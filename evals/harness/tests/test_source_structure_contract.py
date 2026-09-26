"""Source-structure gates on saved wordpress-planner.migration output.

The inventory is a ``source-structure.json`` file in the drupal-meta-skills
contract format (vendored under ``evals/harness/data/source-structure-contract/``).
``paragraphs-heavy-v1`` is the eval fixture's own sidecar with a hand-written
reference plan that must pass. ``paragraphs-unclassified`` is the same inventory
plus one component the plan never dispositions, and it must fail. The reference
plan is hand-written, so these tests prove the oracle, not that any model emits
conforming plans.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import validate_wordpress_skill_output as oracle

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "source-structure"
SUITE_FIXTURES = ROOT / "evals" / "suites" / "wordpress-planner.migration" / "fixtures"
HEAVY = SUITE_FIXTURES / "paragraphs-heavy-v1.source-structure.json"
UNCLASSIFIED = FIXTURES / "paragraphs-unclassified.source-structure.json"
PLAN = (FIXTURES / "paragraphs-heavy-v1.plan.md").read_text(encoding="utf-8")
ORACLE = ROOT / "evals" / "harness" / "validate_wordpress_skill_output.py"
CONTRACT_DIR = ROOT / "evals" / "harness" / "data" / "source-structure-contract"
SKILL = "wordpress-planner.migration"

# sha256 of the vendored files at drupal-meta-skills 2236cbc (contract 1.2.0).
# Re-vendoring is deliberate: update these with the README's pinned commit.
VENDORED_SHA256 = {
    "VERSION": "1e5b51cde515396a9fa762909cf8ca6584ccc564b325d2eebeea76175fe95c4d",
    "source-structure.schema.json": "cd79e6c8657a6848de5d9d8ef46da6f40da191ccc7382e1b2f24795ed3c919b3",
    "dispositions.schema.json": "1ccb807ca2d8c752ee9455f3d4c525f6ca03fd0e9a1eed23e9a785f7417d74c0",
}


def _checks(text: str, inventory: dict | None) -> dict[str, dict]:
    result = oracle.validate_output(SKILL, text, source_structure=inventory)
    return {check["id"]: check for check in result["checks"]}


def _heavy() -> dict:
    return oracle.load_source_structure(HEAVY)


def _replace(old: str, new: str, text: str = PLAN) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


# --- vendored contract -------------------------------------------------------


def test_vendored_contract_matches_pinned_hashes():
    for name, digest in VENDORED_SHA256.items():
        assert hashlib.sha256((CONTRACT_DIR / name).read_bytes()).hexdigest() == digest, name


def test_vendored_enums_are_read_from_the_contract():
    major, kinds, verdicts = oracle._source_structure_contract()
    assert major == 1
    assert {"paragraph_type", "paragraphs_library_item", "block_content"} <= kinds
    assert verdicts == {"STRUCTURED", "QUERY", "REUSE", "LAYOUT", "CONTENT", "DROP", "DEFER"}


# --- loader ------------------------------------------------------------------


def _write(tmp_path: Path, payload) -> Path:
    path = tmp_path / "inventory.json"
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return path


def _component(kind="paragraph_type", item_id="hero", key=None) -> dict:
    return {"kind": kind, "id": item_id, "key": key if key is not None else f"{kind}:{item_id}"}


@pytest.mark.parametrize(
    ("payload", "message"),
    (
        ("not json", "invalid"),
        ([], "object"),
        ({"components": [_component()]}, "contract_version"),
        ({"contract_version": 1, "components": [_component()]}, "contract_version"),
        ({"contract_version": "2.0.0", "components": [_component()]}, "unsupported major"),
        ({"contract_version": "1.2.0"}, "non-empty"),
        ({"contract_version": "1.2.0", "components": []}, "non-empty"),
        ({"contract_version": "1.2.0", "components": ["x"]}, "object"),
        ({"contract_version": "1.2.0", "components": [{"kind": "menu", "id": "", "key": "menu:"}]}, "non-empty string"),
        ({"contract_version": "1.2.0", "components": [_component(kind="acf_layout")]}, "kind enum"),
        ({"contract_version": "1.2.0", "components": [_component(key="hero")]}, "is not"),
        ({"contract_version": "1.2.0", "components": [_component(item_id="a (b)")]}, "parentheses"),
        ({"contract_version": "1.2.0", "components": [_component(), _component()]}, "more than once"),
    ),
)
def test_loader_rejects_malformed_inventories(tmp_path, payload, message):
    with pytest.raises(ValueError, match=message):
        oracle.load_source_structure(_write(tmp_path, payload))


def test_loader_accepts_a_newer_minor(tmp_path):
    payload = {"contract_version": "1.9.0", "components": [_component()], "future_key": True}
    assert oracle.load_source_structure(_write(tmp_path, payload))["contract_version"] == "1.9.0"


# --- fixtures ----------------------------------------------------------------


def test_reference_plan_passes_with_the_eval_sidecar():
    result = oracle.validate_output(SKILL, PLAN, source_structure=_heavy())
    assert result["pass"] is True, [c for c in result["checks"] if not c["passed"]]
    ids = {check["id"] for check in result["checks"]}
    assert {
        "migration_source_structure_record",
        "migration_source_structure_coverage",
        "migration_non_empty_destination",
    } <= ids


def test_unclassified_component_fails_and_is_named():
    checks = _checks(PLAN, oracle.load_source_structure(UNCLASSIFIED))
    coverage = checks["migration_source_structure_coverage"]
    assert coverage["passed"] is False
    assert "paragraph_type:pull_quote" in coverage["detail"]
    assert "13/13" in coverage["detail"]


def test_unclassified_differs_from_heavy_by_exactly_one_component():
    heavy = {c["key"] for c in _heavy()["components"]}
    unclassified = {c["key"] for c in oracle.load_source_structure(UNCLASSIFIED)["components"]}
    assert unclassified - heavy == {"paragraph_type:pull_quote"}
    assert heavy <= unclassified


def test_eval_prompt_excerpt_lists_every_sidecar_key():
    prompt = (SUITE_FIXTURES / "paragraphs-heavy-v1.md").read_text(encoding="utf-8")
    excerpt = prompt.split("## Supplied `source-structure.json` (excerpt)", 1)[1]
    for component in _heavy()["components"]:
        assert f"`{component['key']}`" in excerpt, component["key"]


def test_sidecar_counts_reconcile_with_components():
    inventory = _heavy()
    tally: dict[str, int] = {}
    for component in inventory["components"]:
        tally[component["kind"]] = tally.get(component["kind"], 0) + 1
    assert inventory["counts"] == {**tally, "total": len(inventory["components"])}


# --- coverage ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    (
        ("Dispositioned: 13/13\n", "", "exactly one `Dispositioned"),
        ("Dispositioned: 13/13", "Dispositioned: 12/13", "12/13"),
        ("Dispositioned: 13/13", "Dispositioned: 13/13\nDispositioned: 13/13", "exactly one"),
        (
            "Structure disposition (paragraph_type:faq_item): CONTENT - core/details",
            "Structure disposition (paragraph_type:faq_item): CONTENT - not decided yet",
            "paragraph_type:faq_item (CONTENT needs a WordPress destination",
        ),
        (
            "Structure disposition (paragraph_type:faq_item): CONTENT - core/details",
            "Structure disposition (paragraph_type:faq_item): CONTENT",
            "paragraph_type:faq_item (CONTENT needs a WordPress destination",
        ),
        (
            "Structure disposition (paragraph_type:faq_item): CONTENT - core/details",
            "Structure disposition (paragraph_type:faq_item): CONTENT - none",
            "paragraph_type:faq_item (CONTENT needs a WordPress destination",
        ),
        (
            "Structure disposition (paragraph_type:faq_item): CONTENT - core/details",
            "Structure disposition (paragraph_type:faq_item): custom-block - core/details",
            "verdict `custom-block`",
        ),
        (
            "Structure disposition (paragraph_type:legacy_iframe): DROP - zero live instances in the inventory",
            "Structure disposition (paragraph_type:legacy_iframe): DROP",
            "DROP needs a stated reason",
        ),
        (
            "Structure disposition (paragraph_type:legacy_iframe): DROP - zero live instances in the inventory",
            "Structure disposition (paragraph_type:legacy_iframe): DEFER - TBD",
            "DEFER needs a stated reason",
        ),
        (
            "Structure disposition (menu:main): STRUCTURED - wp_navigation post main-navigation",
            "Structure disposition (menu:main): STRUCTURED - wp_navigation post main-navigation\n"
            "Structure disposition (menu:main): LAYOUT - header template part",
            "duplicate `Structure disposition` rows for: menu:main",
        ),
        (
            "Dispositioned: 13/13",
            "Dispositioned: 13/13\nStructure disposition (paragraph_type:pull_quote): CONTENT - core/pullquote",
            "outside the inventory: paragraph_type:pull_quote",
        ),
    ),
)
def test_coverage_failures(old, new, expected):
    coverage = _checks(_replace(old, new), _heavy())["migration_source_structure_coverage"]
    assert coverage["passed"] is False
    assert expected in coverage["detail"]


@pytest.mark.parametrize("reason", ("pending", "pending decision", "Pending review", "dead"))
def test_defer_or_drop_reason_must_carry_substance(reason):
    plan = _replace(
        "Structure disposition (paragraph_type:legacy_iframe): DROP - zero live instances in the inventory",
        f"Structure disposition (paragraph_type:legacy_iframe): DEFER - {reason}",
    )
    coverage = _checks(plan, _heavy())["migration_source_structure_coverage"]
    assert coverage["passed"] is False
    assert "paragraph_type:legacy_iframe" in coverage["detail"]


def test_mass_bare_pending_deferral_fails_coverage():
    plan = PLAN
    for line in PLAN.splitlines():
        if line.startswith("Structure disposition ("):
            key_part = line.split("): ", 1)[0]
            plan = plan.replace(line, f"{key_part}): DEFER - pending")
    coverage = _checks(plan, _heavy())["migration_source_structure_coverage"]
    assert coverage["passed"] is False
    assert "must name the evidence or the pending decision" in coverage["detail"]


def test_defer_may_name_the_pending_decision():
    plan = _replace(
        "Structure disposition (paragraph_type:legacy_iframe): DROP - zero live instances in the inventory",
        "Structure disposition (paragraph_type:legacy_iframe): DEFER - pending the web team's embed-policy decision",
    )
    assert _checks(plan, _heavy())["migration_source_structure_coverage"]["passed"] is True


def test_bare_id_row_is_both_missing_and_outside():
    plan = _replace(
        "Structure disposition (block_content:1): STRUCTURED",
        "Structure disposition (1): STRUCTURED",
    )
    detail = _checks(plan, _heavy())["migration_source_structure_coverage"]["detail"]
    assert "missing `Structure disposition` row for: block_content:1" in detail
    assert "outside the inventory: 1" in detail


def test_catch_all_row_cannot_cover_several_keys():
    plan = _replace(
        "Structure disposition (paragraph_type:faq_item): CONTENT - core/details",
        "Structure disposition: paragraph_type:faq_item, paragraph_type:text_with_image - CONTENT",
    )
    detail = _checks(plan, _heavy())["migration_source_structure_coverage"]["detail"]
    assert "paragraph_type:faq_item" in detail


def test_fenced_rows_do_not_count():
    row = "Structure disposition (paragraph_type:faq_item): CONTENT - core/details"
    plan = _replace(row, "```text\n" + row + "\n```")
    detail = _checks(plan, _heavy())["migration_source_structure_coverage"]["detail"]
    assert "missing `Structure disposition` row for: paragraph_type:faq_item" in detail


def test_lowercase_verdict_and_spaced_count_are_accepted():
    plan = _replace("Dispositioned: 13/13", "Dispositioned: 13 / 13")
    plan = _replace(
        "Structure disposition (paragraph_type:faq_item): CONTENT",
        "Structure disposition (paragraph_type:faq_item): content",
        plan,
    )
    assert _checks(plan, _heavy())["migration_source_structure_coverage"]["passed"] is True


def test_empty_inventory_fails_not_vacuously():
    coverage = _checks(PLAN, {"contract_version": "1.2.0", "components": []})["migration_source_structure_coverage"]
    assert coverage["passed"] is False
    assert "no components" in coverage["detail"]


# --- record and stop form ----------------------------------------------------


STOP_PLAN = """\
## Migration Scope
The source is a Drupal 10 site. Planning is blocked at Phase 1 until the source inventory exists.

## Current-State Evidence
No `source-structure.json` inventory was supplied.

## Source Audit
Source structure file: missing - run drupal-source-inventory (zivtech/drupal-meta-skills) first

## Target Mapping
Decision required: component dispositions wait for the inventory; owner: the migration lead.

## Transform And Execution Plan
Decision required: blocked until the inventory exists.

## Validation Plan
Decision required: blocked until the inventory exists; then verify with `wp post list`.

## Rollback And Monitoring
No writes happen before the inventory exists.

## Assumption Register
Assumption: the source is Drupal 10 with config-export access.

## Test Strategy
Decision required: fixtures are chosen from the inventory.

## Acceptance Criteria
The plan resumes at Phase 2 once `source-structure.json` is supplied.

## Critic Handoff
Review that the plan stopped at Phase 1 instead of guessing components.
"""


def test_stop_form_passes_the_record_check_without_a_sidecar():
    checks = _checks(STOP_PLAN, None)
    assert checks["migration_source_structure_record"]["passed"] is True
    assert "migration_source_structure_coverage" not in checks


def test_stop_form_with_disposition_rows_fails():
    plan = STOP_PLAN.replace(
        "Decision required: component dispositions",
        "Structure disposition (paragraph_type:hero): CONTENT - core/cover\nDecision required: component dispositions",
    )
    record = _checks(plan, None)["migration_source_structure_record"]
    assert record["passed"] is False
    assert "stops the plan at Phase 1" in record["detail"]


def test_stop_form_fails_when_an_inventory_was_supplied():
    record = _checks(STOP_PLAN, _heavy())["migration_source_structure_record"]
    assert record["passed"] is False
    assert "an inventory was supplied" in record["detail"]


def test_not_producible_needs_a_reason():
    plan = STOP_PLAN.replace(
        "Source structure file: missing - run drupal-source-inventory (zivtech/drupal-meta-skills) first",
        "Source structure file: not-producible",
    )
    assert _checks(plan, None)["migration_source_structure_record"]["passed"] is False


def test_not_producible_with_a_reason_passes():
    plan = STOP_PLAN.replace(
        "Source structure file: missing - run drupal-source-inventory (zivtech/drupal-meta-skills) first",
        "Source structure file: not-producible - Drupal 7 source; the inventory needs Drupal 8 config export",
    )
    assert _checks(plan, None)["migration_source_structure_record"]["passed"] is True


def test_rows_without_a_file_record_fail_the_record_check():
    plan = _replace("Source structure file: paragraphs-heavy-v1.source-structure.json\n", "")
    record = _checks(plan, None)["migration_source_structure_record"]
    assert record["passed"] is False
    assert "no single `Source structure file:`" in record["detail"]


def test_file_record_must_name_a_json_inventory():
    plan = _replace(
        "Source structure file: paragraphs-heavy-v1.source-structure.json",
        "Source structure file: see the shared drive",
    )
    assert _checks(plan, _heavy())["migration_source_structure_record"]["passed"] is False


def test_plan_without_any_source_structure_signal_is_unchanged():
    ids = {check["id"] for check in oracle.validate_output(SKILL, STOP_PLAN.replace(
        "Source structure file: missing - run drupal-source-inventory (zivtech/drupal-meta-skills) first\n", ""
    ))["checks"]}
    assert not any(name.startswith("migration_source_structure") for name in ids)
    assert "migration_non_empty_destination" not in ids


# --- non-empty destination ---------------------------------------------------


def test_content_rows_require_non_empty_destination_field():
    plan = _replace(
        "Semantic oracle fields: text,href,attributes,unsupported,non-empty-destination",
        "Semantic oracle fields: text,href,attributes,unsupported",
    )
    check = _checks(plan, _heavy())["migration_non_empty_destination"]
    assert check["passed"] is False
    assert "paragraph_type:faq_item" in check["detail"]
    assert check["weight"] == 3


def test_no_content_rows_passes_vacuously_at_low_weight(tmp_path):
    plan = PLAN
    for line in PLAN.splitlines():
        if line.startswith("Structure disposition") and "): CONTENT - " in line:
            plan = plan.replace(line, line.replace("): CONTENT - ", "): LAYOUT - "))
    check = _checks(plan, _heavy())["migration_non_empty_destination"]
    assert check["passed"] is True
    assert check["weight"] == 1
    assert "vacuous" in check["detail"]


def test_non_empty_destination_is_an_accepted_gutenberg_oracle_field():
    checks = _checks(PLAN, None)
    assert all(check["passed"] for check in checks.values()), checks


def test_source_structure_is_ignored_for_other_skills():
    result = oracle.validate_output("wordpress-planner.content-model", PLAN, source_structure=_heavy())
    assert not any(check["id"].startswith("migration_source_structure") for check in result["checks"])


# --- CLI ---------------------------------------------------------------------


def _cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ORACLE), "--skill", SKILL, "--output", str(plan), *args],
        capture_output=True, text=True, check=False,
    )


def test_cli_passes_reference_plan(tmp_path):
    completed = _cli(tmp_path, "--source-structure", str(HEAVY))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["pass"] is True


def test_cli_fails_unclassified_inventory(tmp_path):
    completed = _cli(tmp_path, "--source-structure", str(UNCLASSIFIED))
    assert completed.returncode == 1
    assert "paragraph_type:pull_quote" in completed.stdout


def test_cli_reports_missing_and_malformed_inventories(tmp_path):
    missing = _cli(tmp_path, "--source-structure", str(tmp_path / "absent.json"))
    assert missing.returncode == 1
    assert "source-structure file not found" in missing.stderr
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"contract_version": "2.0.0", "components": [_component()]}), encoding="utf-8")
    malformed = _cli(tmp_path, "--source-structure", str(bad))
    assert malformed.returncode == 1
    assert "unsupported major" in malformed.stderr

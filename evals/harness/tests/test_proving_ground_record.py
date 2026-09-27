"""Tests for the opt-in proving-ground record (Plan 025 D4').

``validate_wordpress_skill_output.py --require-proving-ground`` is off by
default so every existing caller keeps today's behavior. With it on, the ten
skills named in ``PROVING_GROUND_RECORDS`` must carry exactly one
``Proving ground:`` record under their owning heading, and the
``not installed``/``unusable`` forms must each name their required harness
files with a ``NOT CHECKED`` line. ``run_wordpress_high_risk_saved_outputs.py``
records the flag in a new run's manifest and applies it to the ``skill``
condition only; ``--resume`` honors whatever the manifest already recorded.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import run_wordpress_high_risk_saved_outputs as runner
import validate_wordpress_skill_output as oracle


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "proving_ground"


def _find_check(result: dict, check_id: str) -> dict:
    return next(check for check in result["checks"] if check["id"] == check_id)


def _pg_block(value: str, required_files: tuple[str, ...], needs_not_checked: bool) -> str:
    lines = [f"Proving ground: {value}"]
    if needs_not_checked:
        lines.append("")
        for name in required_files:
            lines.append(f"NOT CHECKED: {name} (no proving ground root resolved)")
    return "\n".join(lines) + "\n\n"


def _probe_text(pg_block: str) -> str:
    return (
        "## Detected Environment\n\n"
        "wp-env with the docker runtime, marker `.wp-env.json`, validated by\n"
        "`wp-env run cli wp --info`. The probe oracle is\n"
        "`evals/harness/probe_wordpress_environment.py`.\n\n"
        "## Capability Summary\n\n"
        "can_run_wp_cli true (`wp cli version` answered WP-CLI 2.12.0);\n"
        "can_run_plugin_check true via `wp plugin check`; can_run_static_analysis true\n"
        "(phpcs and phpstan both answered `--version`).\n\n"
        "## Blockers\n\n"
        "mcp_adapter_absent (MAJOR): no MCP adapter plugin observed, so MCP\n"
        "reachability is outside scope of this run and stays unknown.\n\n"
        "## Evidence\n\n"
        "`wp plugin list --format=json` inventoried plugins; `wp core is-installed`\n"
        "exited 0. Every fact traces to an evidence entry by claim path.\n\n"
        f"{pg_block}"
        "## Downstream Handoff\n\n"
        "Pass `--capability-manifest capability-manifest.json` to\n"
        "`validate_wordpress_skill_output.py` when validating wordpress-planner output.\n"
    )


def _plugin_executor_text(pg_block: str) -> str:
    return (
        "## Spec Conformance\n"
        "Implements the approved wordpress-plugin-planner spec for the editorial review\n"
        "plugin exactly; no deviations from Delivery unit: client-custom-plugin.\n\n"
        "## Generated File Map\n"
        "client-custom-plugin.php, includes/class-admin-settings.php,\n"
        "includes/class-rest-controller.php\n\n"
        "## Implementation Packets\n"
        "The bootstrap file calls `register_post_type()` and `register_setting()`. The\n"
        "REST controller calls `register_rest_route()` and gates access with\n"
        "`check_admin_referer()`.\n\n"
        "## Security Notes\n"
        "Input passes through `sanitize_text_field()`; nonce verification uses\n"
        "`wp_verify_nonce()`. This does not claim coverage of third-party integrations\n"
        "outside this plugin's boundary.\n\n"
        "## Deviation Log\n"
        "No deviations from the approved plan.\n\n"
        "## Verification Notes\n"
        "Run PHPUnit and a Playwright admin smoke before release.\n\n"
        f"{pg_block}"
        "## Critic Handoff\n"
        "Send the packet to wordpress-critic and wordpress-security-critic.\n"
    )


def _planner_block_text(pg_block: str) -> str:
    return (
        "## Block Scope\n"
        "Build one dynamic `acme/runtime-card` block. This does not claim cross-browser coverage.\n\n"
        "Block identity: acme/runtime-card\n"
        "Primary serialization: dynamic\n"
        "Interaction pattern: server-rendered block\n\n"
        "## Current-State Evidence\n"
        "The plugin registers blocks from `block.json` with `register_block_type()`.\n\n"
        f"{pg_block}"
        "## Metadata And Attribute Plan\n"
        "`block.json` declares the block name, title, and category. The block has no\n"
        "attributes and no saved content; its saved-markup contract is intentionally empty.\n\n"
        "Metadata file: block.json\n"
        "Attributes: none\n"
        "Saved markup: self-closing\n\n"
        "## Render And Interaction Plan\n"
        "Use `render_callback` for dynamic output. A missing record is a render failure\n"
        "that returns empty output after logging an error.\n\n"
        "Render surface: render_callback\n"
        "Failure behavior: log-and-return-empty\n\n"
        "## Compatibility And Migration Plan\n"
        "There is no existing saved content. Keep a saved-content fixture containing the\n"
        "self-closing block delimiter so future metadata changes can be checked.\n\n"
        "Compatibility decision: new-contract\n"
        "Saved-content fixture: required\n\n"
        "## Security Performance And Accessibility Notes\n"
        "The callback uses `esc_html()` and has no REST, SQL, upload, or remote-call path.\n\n"
        "## Assumption Register\n"
        "Assumption: the host loads the plugin before editor smoke; the runtime oracle verifies it.\n\n"
        "## Test Strategy\n"
        "Run a Playwright editor smoke for insertion/save and a separate frontend smoke\n"
        "for the `.wp-block-acme-runtime-card` output, plus PHPUnit for the callback.\n\n"
        "Editor oracle: required\n"
        "Editor oracle method: playwright-insert-save-reload\n"
        "Editor oracle block: acme/runtime-card\n"
        "Frontend oracle: required\n"
        "Frontend oracle method: playwright-selector-visible-text\n"
        "Frontend oracle selector: .wp-block-acme-runtime-card\n"
        "Frontend expected text: Runtime block smoke\n\n"
        "## Acceptance Criteria\n"
        "The editor saves the block and the front end renders the fixture-owned text.\n\n"
        "## Executor Handoff\n"
        "Generate the exact block files and recorded verification packet.\n\n"
        "## Critic Handoff\n"
        "Send the packet to wordpress-critic after the runtime evidence exists.\n"
    )


PLUGIN_EXECUTOR_REQUIRED_FILES = (
    "validate_wordpress_executor_packet.py",
    "materialize_wordpress_executor_packet.py",
    "validate_wordpress_artifact.py",
)

GOOD_SECURITY_CRITIC = (
    "## VERDICT\n**VERDICT: ACCEPT**\n\n"
    "## Overall Assessment\n"
    "Fine; `current_user_can()` gates the action. This does not claim completeness.\n\n"
    "## Pre-commitment Predictions\nnone\n\n"
    "## Security Gate Evidence\nn/a\n\n"
    "## Critical Findings\nnone\n\n"
    "## Major Findings\nnone\n\n"
    "## Minor Findings\nnone\n\n"
    "## Suppression Review\nnone\n\n"
    "## What's Missing\nnone\n\n"
    "## Multi-Perspective Notes\nnone\n\n"
    "## Exploitability Notes\nnone\n\n"
    "## Verdict Justification\nfine\n\n"
    "## Remediation Guide\nnone\n\n"
    "## Open Questions\nnone\n"
)


# ---------------------------------------------------------------------------
# Flag off: byte-for-byte the same behavior as before this feature existed.
# ---------------------------------------------------------------------------


def test_flag_off_default_does_not_add_the_check():
    text = (FIXTURES_DIR / "probe-not-installed.md").read_text(encoding="utf-8")
    result = oracle.validate_output("wordpress-environment-probe", text)
    assert "proving_ground_record" not in {check["id"] for check in result["checks"]}
    assert result["pass"] is True


def test_flag_off_explicit_false_matches_omitted_default():
    text = (FIXTURES_DIR / "probe-not-installed.md").read_text(encoding="utf-8")
    omitted = oracle.validate_output("wordpress-environment-probe", text)
    explicit = oracle.validate_output("wordpress-environment-probe", text, require_proving_ground=False)
    assert omitted == explicit


# ---------------------------------------------------------------------------
# Flag on: the three value forms, for the probe, one executor, one planner.
# ---------------------------------------------------------------------------


FORMS = [
    pytest.param("not installed", True, id="not-installed"),
    pytest.param("/opt/wp-ai-skills@abc1234", False, id="installed"),
    pytest.param("/opt/wp-ai-skills", False, id="installed-no-commit"),
    pytest.param("/opt/wp-ai-skills (unusable: uv not found)", True, id="unusable"),
]

SKILLS = [
    pytest.param(
        "wordpress-environment-probe", _probe_text, ("probe_wordpress_environment.py",), id="probe"
    ),
    pytest.param(
        "wordpress-plugin-executor", _plugin_executor_text, PLUGIN_EXECUTOR_REQUIRED_FILES, id="plugin-executor"
    ),
    pytest.param(
        "wordpress-planner.block", _planner_block_text, ("wp-symbols.json",), id="planner-block"
    ),
]


@pytest.mark.parametrize("skill,builder,required_files", SKILLS)
@pytest.mark.parametrize("value,needs_not_checked", FORMS)
def test_each_value_form_passes_for_each_named_skill(skill, builder, required_files, value, needs_not_checked):
    text = builder(_pg_block(value, required_files, needs_not_checked))
    result = oracle.validate_output(skill, text, require_proving_ground=True)
    assert result["pass"] is True, result["checks"]
    assert _find_check(result, "proving_ground_record")["passed"] is True


@pytest.mark.parametrize(
    "skill,fixture_name",
    [
        pytest.param("wordpress-environment-probe", "probe-not-installed.md", id="probe"),
        pytest.param("wordpress-plugin-executor", "plugin-executor-not-installed.md", id="plugin-executor"),
        pytest.param("wordpress-planner.block", "planner-block-installed.md", id="planner-block"),
    ],
)
def test_saved_fixtures_pass_with_the_flag_on(skill, fixture_name):
    text = (FIXTURES_DIR / fixture_name).read_text(encoding="utf-8")
    result = oracle.validate_output(skill, text, require_proving_ground=True)
    assert result["pass"] is True, result["checks"]


# ---------------------------------------------------------------------------
# Flag on: failure shapes, exercised against the plugin executor (three
# required files, so it also covers "names only some of them").
# ---------------------------------------------------------------------------


def test_missing_record_fails():
    text = _plugin_executor_text("")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    assert result["pass"] is False
    assert _find_check(result, "proving_ground_record")["passed"] is False


def test_duplicate_record_fails():
    block = _pg_block("not installed", PLUGIN_EXECUTOR_REQUIRED_FILES, True)
    text = _plugin_executor_text(block + block)
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    check = _find_check(result, "proving_ground_record")
    assert check["passed"] is False
    assert "expected exactly one" in check["detail"]


def test_record_outside_owning_heading_fails():
    misplaced = (
        "## Critic Handoff\n"
        "Send the packet to wordpress-critic and wordpress-security-critic.\n\n"
        + _pg_block("not installed", PLUGIN_EXECUTOR_REQUIRED_FILES, True)
    )
    text = _plugin_executor_text("").replace(
        "## Critic Handoff\n"
        "Send the packet to wordpress-critic and wordpress-security-critic.\n",
        misplaced,
    )
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    check = _find_check(result, "proving_ground_record")
    assert check["passed"] is False


def test_root_placeholder_fails():
    text = _plugin_executor_text("Proving ground: <root>\n\n")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    assert _find_check(result, "proving_ground_record")["passed"] is False


def test_relative_path_fails():
    text = _plugin_executor_text("Proving ground: relative/path@abc1234\n\n")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    check = _find_check(result, "proving_ground_record")
    assert check["passed"] is False


def test_not_installed_without_not_checked_lines_fails():
    text = _plugin_executor_text("Proving ground: not installed\n\n")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    check = _find_check(result, "proving_ground_record")
    assert check["passed"] is False
    for name in PLUGIN_EXECUTOR_REQUIRED_FILES:
        assert name in check["detail"]


def test_not_installed_naming_only_two_of_three_files_fails():
    lines = [
        "Proving ground: not installed",
        "",
        f"NOT CHECKED: {PLUGIN_EXECUTOR_REQUIRED_FILES[0]} (no proving ground root resolved)",
        f"NOT CHECKED: {PLUGIN_EXECUTOR_REQUIRED_FILES[1]} (no proving ground root resolved)",
    ]
    text = _plugin_executor_text("\n".join(lines) + "\n\n")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    check = _find_check(result, "proving_ground_record")
    assert check["passed"] is False
    assert PLUGIN_EXECUTOR_REQUIRED_FILES[2] in check["detail"]
    assert PLUGIN_EXECUTOR_REQUIRED_FILES[0] not in check["detail"]


@pytest.mark.parametrize("commit", ["abc123", "ABC1234", "abc123g", "a" * 41])
def test_bad_commit_suffix_fails(commit):
    text = _plugin_executor_text(f"Proving ground: /opt/wp-ai-skills@{commit}\n\n")
    result = oracle.validate_output("wordpress-plugin-executor", text, require_proving_ground=True)
    assert _find_check(result, "proving_ground_record")["passed"] is False


def test_unaffected_skill_adds_no_check():
    result = oracle.validate_output("wordpress-security-critic", GOOD_SECURITY_CRITIC, require_proving_ground=True)
    assert "proving_ground_record" not in {check["id"] for check in result["checks"]}


# ---------------------------------------------------------------------------
# CLI: --require-proving-ground parses and reaches validate_output.
# ---------------------------------------------------------------------------


def test_cli_flag_reaches_validate_output(tmp_path):
    output_path = tmp_path / "output.md"
    output_path.write_text(_plugin_executor_text(""), encoding="utf-8")

    assert oracle.main(["--skill", "wordpress-plugin-executor", "--output", str(output_path)]) == 0

    assert (
        oracle.main(
            [
                "--skill",
                "wordpress-plugin-executor",
                "--output",
                str(output_path),
                "--require-proving-ground",
            ]
        )
        == 1
    )


# ---------------------------------------------------------------------------
# Runner: manifest recording and --resume behavior.
# ---------------------------------------------------------------------------


def test_resolve_require_proving_ground_new_run_is_true(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    assert runner.resolve_require_proving_ground("brand-new-run", resume=False) is True


def test_resolve_require_proving_ground_resume_without_manifest_is_false(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    assert runner.resolve_require_proving_ground("no-manifest-run", resume=True) is False


def test_resolve_require_proving_ground_resume_honors_stored_true(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    run_dir = tmp_path / "run-x"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"require_proving_ground": True}), encoding="utf-8")
    assert runner.resolve_require_proving_ground("run-x", resume=True) is True


def test_resolve_require_proving_ground_resume_manifest_without_key_is_false(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    run_dir = tmp_path / "run-old"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"run_id": "run-old"}), encoding="utf-8")
    assert runner.resolve_require_proving_ground("run-old", resume=True) is False


def test_run_saved_output_applies_flag_to_skill_but_not_baseline(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(runner, "security_gate_sidecar_path", lambda suite, fixture_id: None)
    monkeypatch.setattr(runner, "capability_manifest_sidecar_path", lambda suite, fixture_id: None)
    monkeypatch.setattr(runner, "source_structure_sidecar_path", lambda suite, fixture_id: None)

    run_id = "run-1"
    suite = "wordpress-plugin-executor-suite"
    fixture_id = "fixture-a"
    missing_record_output = _plugin_executor_text("")

    for condition in ("skill", "baseline-zero-shot"):
        output_path = runner.saved_output_path(run_id, suite, condition, fixture_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(missing_record_output, encoding="utf-8")
        runner.saved_metadata_path(run_id, suite, condition, fixture_id).write_text("{}", encoding="utf-8")

    common_kwargs = dict(
        run_id=run_id,
        suite=suite,
        fixture_id=fixture_id,
        skill_name="wordpress-plugin-executor",
        resume=True,
        timeout_sec=1,
        max_retries=0,
        model=None,
        effort=None,
        require_proving_ground=True,
    )
    skill_entry = runner.run_saved_output(condition="skill", **common_kwargs)
    baseline_entry = runner.run_saved_output(condition="baseline-zero-shot", **common_kwargs)

    # The skill lane is missing its 'Proving ground:' record, so it must fail
    # once the run-level flag is true. The baseline lane never has to carry
    # the record and must not be perturbed by the flag.
    assert skill_entry.contract_pass is False
    assert baseline_entry.contract_pass is True


def test_main_new_run_records_require_proving_ground_true(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(runner, "skill_name_for_suite", lambda suite: "wordpress-plugin-executor")

    def _stub_run_saved_output(**kwargs):
        return runner.SavedOutputEntry(
            suite=kwargs["suite"],
            fixture_id=kwargs["fixture_id"],
            condition=kwargs["condition"],
            output_path="x",
            metadata_path="y",
            contract_path="z",
            security_gate_path=None,
            generation_ok=True,
            contract_pass=True,
            contract_score=1.0,
            duration_sec=0.1,
        )

    monkeypatch.setattr(runner, "run_saved_output", _stub_run_saved_output)

    exit_code = runner.main(
        [
            "--suite", "wordpress-plugin-executor-suite",
            "--run-id", "run-new",
            "--fixtures", "fixture-a",
            "--conditions", "skill",
        ]
    )
    assert exit_code == 0
    manifest = json.loads((tmp_path / "run-new" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["require_proving_ground"] is True


def test_main_resume_honors_manifest_without_key(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(runner, "skill_name_for_suite", lambda suite: "wordpress-plugin-executor")
    run_dir = tmp_path / "run-old"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(json.dumps({"run_id": "run-old"}), encoding="utf-8")

    captured_flags: list[bool] = []

    def _stub_run_saved_output(**kwargs):
        captured_flags.append(kwargs.get("require_proving_ground"))
        return runner.SavedOutputEntry(
            suite=kwargs["suite"],
            fixture_id=kwargs["fixture_id"],
            condition=kwargs["condition"],
            output_path="x",
            metadata_path="y",
            contract_path="z",
            security_gate_path=None,
            generation_ok=True,
            contract_pass=True,
            contract_score=1.0,
            duration_sec=0.1,
        )

    monkeypatch.setattr(runner, "run_saved_output", _stub_run_saved_output)

    exit_code = runner.main(
        [
            "--suite", "wordpress-plugin-executor-suite",
            "--run-id", "run-old",
            "--fixtures", "fixture-a",
            "--conditions", "skill",
            "--resume",
        ]
    )
    assert exit_code == 0
    assert captured_flags == [False]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["require_proving_ground"] is False

"""Tests for the proving-ground guard rule in scripts/validate-distribution-parity.py.

Plan 025 (Revised decisions, APPROVED 2026-09-26), D3'/D4': every skill that names
`evals/harness/` must carry a single, verbatim "Proving ground first." Hard Gates
bullet (one of two variants: COMMAND for the probe/executors, REFERENCE for the
planners) as the last Hard Gates record on all four distributed surfaces, every
`evals/harness/` occurrence on every surface must be `<root>/`-prefixed, and the
Output Contract / Output_Format section must end with the record sentence naming
the skill's owning heading.
"""

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = PROJECT_ROOT / "scripts/validate-distribution-parity.py"
SURFACES = (
    ".claude/skills",
    ".agents/skills",
    ".claude/agents",
    ".codex/agents",
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("distribution_parity_pg", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_surfaces(tmp_path: Path) -> Path:
    root = tmp_path / "distribution"
    root.mkdir()
    for relative in SURFACES:
        shutil.copytree(PROJECT_ROOT / relative, root / relative)
    shutil.copy2(PROJECT_ROOT / "skills.sh.json", root / "skills.sh.json")
    for relative in SURFACES:
        for path in (root / relative).rglob("*"):
            if path.is_file():
                _strip_guard(path)
                _assert_guard_free(path)
    return root


def _assert_guard_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for guard in _MODULE.PROVING_GROUND_GUARD_TEXT.values():
        assert guard not in text, path
    assert "Proving ground:` record at column zero" not in text, path
    assert "<root>/" not in text, path


def _strip_guard(path: Path) -> None:
    """Return one copied surface to its pre-guard shape.

    The live tree carries the guard, so each test starts from a guard-free copy and
    applies exactly the state it means to test.
    """
    text = path.read_text(encoding="utf-8")
    for guard in _MODULE.PROVING_GROUND_GUARD_TEXT.values():
        text = text.replace(f"\n    - {guard}", "")
    for _variant, heading in _MODULE.PROVING_GROUND_SKILLS.values():
        sentence = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading=heading)
        text = text.replace(f"\n\n{sentence}", "").replace(f"\n    {sentence}", "")
    text = text.replace(
        "uv run --locked --offline --project <root> python <root>/evals/harness/",
        "python3 evals/harness/",
    ).replace("<root>/evals/harness/", "evals/harness/")
    path.write_text(text, encoding="utf-8")


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def _assert_failure(root: Path, *needles: str) -> str:
    result = _run(root)
    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    for needle in needles:
        assert needle in output, output
    return output


def _skill_paths(root: Path, name: str) -> tuple[Path, Path]:
    return (
        root / ".claude/skills" / name / "SKILL.md",
        root / ".agents/skills" / name / "SKILL.md",
    )


def _agent_paths(root: Path, name: str) -> tuple[Path, Path]:
    agent = _MODULE.SKILL_TO_AGENT[name]
    return (
        root / ".claude/agents" / f"{agent}.md",
        root / ".codex/agents" / f"{agent}.toml",
    )


_MODULE = _load_validator()


def _apply_root_prefix(root: Path, name: str) -> None:
    """Fix up bare `evals/harness/` occurrences (rule c) for one skill's four surfaces."""
    for path in (*_skill_paths(root, name), *_agent_paths(root, name)):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?<!<root>/)evals/harness/", "<root>/evals/harness/", text)
        path.write_text(text, encoding="utf-8")


def _insert_skill_gate_bullet(path: Path, bullet_text: str) -> None:
    text = path.read_text(encoding="utf-8")
    if f"    - {bullet_text}" in text.split("\n"):
        return
    anchor = "\n\n## Exact API And Verification Contract"
    assert anchor in text
    text = text.replace(anchor, f"\n    - {bullet_text}{anchor}", 1)
    path.write_text(text, encoding="utf-8")


def _insert_agent_gate_bullet(path: Path, bullet_text: str) -> None:
    text = path.read_text(encoding="utf-8")
    if f"    - {bullet_text}" in text.split("\n"):
        return
    anchor = "\n  </Hard_Gates>"
    assert anchor in text
    text = text.replace(anchor, f"\n    - {bullet_text}{anchor}", 1)
    path.write_text(text, encoding="utf-8")


def _insert_skill_record_sentence(path: Path, sentence: str) -> None:
    text = path.read_text(encoding="utf-8")
    if sentence in text.split("\n"):
        return
    anchor = "\n\n## Provenance"
    assert anchor in text
    text = text.replace(anchor, f"\n\n{sentence}{anchor}", 1)
    path.write_text(text, encoding="utf-8")


def _insert_agent_record_sentence(path: Path, sentence: str) -> None:
    text = path.read_text(encoding="utf-8")
    if f"    {sentence}" in text.split("\n"):
        return
    anchor = "\n  </Output_Format>"
    assert anchor in text
    text = text.replace(anchor, f"\n    {sentence}{anchor}", 1)
    path.write_text(text, encoding="utf-8")


def _apply_full_guard(root: Path, name: str) -> None:
    """Apply the complete, compliant proving-ground guard to one skill's four surfaces."""
    variant, heading = _MODULE.PROVING_GROUND_SKILLS[name]
    guard = _MODULE.PROVING_GROUND_GUARD_TEXT[variant]
    sentence = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading=heading)
    _apply_root_prefix(root, name)
    for path in _skill_paths(root, name):
        _insert_skill_gate_bullet(path, guard)
        _insert_skill_record_sentence(path, sentence)
    for path in _agent_paths(root, name):
        _insert_agent_gate_bullet(path, guard)
        _insert_agent_record_sentence(path, sentence)


def _apply_full_guard_everywhere(root: Path) -> None:
    for name in _MODULE.PROVING_GROUND_SKILLS:
        _apply_full_guard(root, name)


# ---------------------------------------------------------------------------
# Constants: structural properties, checked against structural expectations
# rather than the (out-of-tree) scratch files themselves.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "constant_name",
    ["PROVING_GROUND_GUARD_COMMAND", "PROVING_GROUND_GUARD_REFERENCE"],
)
def test_guard_constant_is_single_line_starting_with_the_headline(constant_name: str) -> None:
    value = getattr(_MODULE, constant_name)
    assert value.startswith("**Proving ground first.**")
    assert "\n" not in value
    assert value.count("`") % 2 == 0


@pytest.mark.parametrize(
    "constant_name",
    ["PROVING_GROUND_GUARD_COMMAND", "PROVING_GROUND_GUARD_REFERENCE"],
)
def test_guard_constant_names_the_home_file_and_harness_only_flag(constant_name: str) -> None:
    value = getattr(_MODULE, constant_name)
    assert "~/.config/wp-ai-skills/home" in value
    assert "--harness-only" in value


def test_command_guard_names_the_exact_uv_invocation() -> None:
    assert (
        "`uv run --locked --offline --project <root> python <root>/evals/harness/<file>`"
        in _MODULE.PROVING_GROUND_GUARD_COMMAND
    )


def test_reference_guard_does_not_claim_to_run_the_harness() -> None:
    # The reference variant is for Bash-disallowed planners: it may only read/cite
    # harness files, never claim to run them with uv.
    assert "uv run" not in _MODULE.PROVING_GROUND_GUARD_REFERENCE


def test_record_sentence_template_has_a_heading_slot() -> None:
    rendered = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading="Evidence")
    assert "Under `## Evidence`, write exactly one `Proving ground:` record" in rendered
    assert "<Heading>" not in _MODULE.PROVING_GROUND_RECORD_SENTENCE


def test_proving_ground_skills_matches_harness_referencing_skills() -> None:
    referencing = {
        path.parent.name
        for path in (PROJECT_ROOT / ".claude/skills").glob("*/SKILL.md")
        if "evals/harness/" in path.read_text(encoding="utf-8")
    }
    assert referencing == set(_MODULE.PROVING_GROUND_SKILLS)


# ---------------------------------------------------------------------------
# Rule (a): a harness-referencing skill must be in the guard mapping.
# ---------------------------------------------------------------------------


def test_harness_reference_without_guard_mapping_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    path = root / ".claude/skills/wordpress-critic/SKILL.md"
    text = path.read_text(encoding="utf-8")
    anchor = "\n\n## Exact API And Verification Contract"
    assert anchor in text
    text = text.replace(
        anchor, f"\n    - See `evals/harness/probe_wordpress_environment.py`.{anchor}", 1
    )
    path.write_text(text, encoding="utf-8")

    _assert_failure(root, "wordpress-critic", "without a proving-ground guard mapping")


# ---------------------------------------------------------------------------
# Rule (b): exactly one guard record, last, correct variant.
# ---------------------------------------------------------------------------


def test_guard_missing_on_a_harness_referencing_skill_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    # Fix the <root>/ prefix so only the missing-guard issue is under test.
    _apply_root_prefix(root, "wordpress-environment-probe")

    _assert_failure(
        root,
        "wordpress-environment-probe",
        "must contain exactly one proving-ground guard record (found 0)",
    )


def test_guard_present_on_three_of_four_surfaces_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")
    # Revert just one surface back to bare, guard-less text (a drift scenario).
    _copy_surfaces_single(root, "wordpress-environment-probe", ".agents/skills")

    _assert_failure(
        root,
        str((root / ".agents/skills/wordpress-environment-probe/SKILL.md")),
        "must contain exactly one proving-ground guard record (found 0)",
    )


def _copy_surfaces_single(root: Path, name: str, surface: str) -> None:
    if surface.endswith("skills"):
        source = PROJECT_ROOT / surface / name / "SKILL.md"
        destination = root / surface / name / "SKILL.md"
    else:
        raise AssertionError("unsupported surface for this helper")
    shutil.copy2(source, destination)
    _strip_guard(destination)
    _assert_guard_free(destination)


def test_wrong_guard_variant_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")
    # wordpress-environment-probe wants the COMMAND variant; swap in REFERENCE instead.
    for path in (*_skill_paths(root, "wordpress-environment-probe"),):
        text = path.read_text(encoding="utf-8")
        assert _MODULE.PROVING_GROUND_GUARD_COMMAND in text
        text = text.replace(
            _MODULE.PROVING_GROUND_GUARD_COMMAND,
            _MODULE.PROVING_GROUND_GUARD_REFERENCE,
            1,
        )
        path.write_text(text, encoding="utf-8")

    _assert_failure(
        root,
        "wordpress-environment-probe",
        "Hard Gates contains the wrong proving-ground guard variant",
    )


def test_guard_not_last_hard_gates_record_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")
    # Append a trailing bullet after the guard, on every surface, so it stays the
    # single guard record but is no longer last.
    for path in _skill_paths(root, "wordpress-environment-probe"):
        text = path.read_text(encoding="utf-8")
        anchor = "\n\n## Exact API And Verification Contract"
        assert anchor in text
        text = text.replace(anchor, f"\n    - Trailing gate added after the guard.{anchor}", 1)
        path.write_text(text, encoding="utf-8")
    for path in _agent_paths(root, "wordpress-environment-probe"):
        text = path.read_text(encoding="utf-8")
        anchor = "\n  </Hard_Gates>"
        assert anchor in text
        text = text.replace(anchor, f"\n    - Trailing gate added after the guard.{anchor}", 1)
        path.write_text(text, encoding="utf-8")

    _assert_failure(
        root,
        "wordpress-environment-probe",
        "the proving-ground guard record must be the last Hard Gates record",
    )


# ---------------------------------------------------------------------------
# Rule (c): every evals/harness/ occurrence is <root>/-prefixed.
# ---------------------------------------------------------------------------


def test_bare_harness_reference_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")

    _assert_failure(root, "reference missing <root>/ prefix")


def test_root_prefixed_harness_reference_alone_passes_rule_c(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    # Every harness-referencing skill must be <root>/-prefixed, not just one, or the
    # other nine would still trip rule (c) and mask what this test is checking.
    _apply_full_guard_everywhere(root)

    output = _run(root).stdout + _run(root).stderr
    assert "missing <root>/ prefix" not in output


# ---------------------------------------------------------------------------
# Rule (d): Output Contract / Output_Format ends with the record sentence.
# ---------------------------------------------------------------------------


def test_missing_record_sentence_fails_on_one_surface(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")
    path = root / ".claude/skills/wordpress-environment-probe/SKILL.md"
    sentence = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading="Evidence")
    text = path.read_text(encoding="utf-8")
    assert f"\n\n{sentence}\n\n## Provenance" in text
    text = text.replace(f"\n\n{sentence}\n\n## Provenance", "\n\n## Provenance", 1)
    path.write_text(text, encoding="utf-8")

    _assert_failure(
        root,
        str(path),
        "Output Contract must end with the proving-ground record sentence",
    )


def test_wrong_heading_record_sentence_fails_on_one_surface(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard(root, "wordpress-environment-probe")
    path = root / ".codex/agents/wordpress-environment-probe.toml"
    sentence = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading="Evidence")
    wrong_sentence = _MODULE.PROVING_GROUND_RECORD_SENTENCE.format(heading="Downstream Handoff")
    text = path.read_text(encoding="utf-8")
    assert f"    {sentence}\n  </Output_Format>" in text
    text = text.replace(
        f"    {sentence}\n  </Output_Format>", f"    {wrong_sentence}\n  </Output_Format>", 1
    )
    path.write_text(text, encoding="utf-8")

    _assert_failure(
        root,
        str(path),
        "Output Contract must end with the proving-ground record sentence",
    )


# ---------------------------------------------------------------------------
# Rule (e): a non-guarded skill must not contain either guard constant.
# ---------------------------------------------------------------------------


def test_non_guarded_skill_with_a_guard_constant_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    path = root / ".claude/skills/wordpress-critic/SKILL.md"
    _insert_skill_gate_bullet(path, _MODULE.PROVING_GROUND_GUARD_COMMAND)

    _assert_failure(
        root,
        "wordpress-critic",
        "contains a proving-ground guard but wordpress-critic is not a guarded skill",
    )


# ---------------------------------------------------------------------------
# Fully compliant fixture: passes cleanly.
# ---------------------------------------------------------------------------


def test_fully_compliant_proving_ground_guard_passes(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard_everywhere(root)

    result = _run(root)

    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# `<root>` context and the wider trigger.
# ---------------------------------------------------------------------------


def test_root_used_as_a_project_path_fails(tmp_path: Path) -> None:
    """`<root>` means the proving ground; reusing it for the user's project is drift."""
    root = _copy_surfaces(tmp_path)
    _apply_full_guard_everywhere(root)
    path = root / ".claude/skills/wordpress-environment-probe/SKILL.md"
    text = path.read_text(encoding="utf-8")
    assert "--path <project> --out" in text
    path.write_text(text.replace("--path <project> --out", "--path <root> --out"), encoding="utf-8")

    _assert_failure(root, str(path), "<root> used outside a proving-ground context")


def test_root_in_every_guard_context_passes(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard_everywhere(root)

    output = _run(root).stdout + _run(root).stderr
    assert "<root> used outside a proving-ground context" not in output


def test_unguarded_skill_citing_wp_symbols_fails(tmp_path: Path) -> None:
    root = _copy_surfaces(tmp_path)
    _apply_full_guard_everywhere(root)
    path = root / ".claude/skills/wordpress-critic/SKILL.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("## Provenance\n", "## Provenance\n\nSee wp-symbols.json.\n", 1), encoding="utf-8")

    _assert_failure(root, str(path), "references wp-symbols.json without a proving-ground guard mapping")


def test_unguarded_agent_file_citing_the_harness_fails(tmp_path: Path) -> None:
    """The trigger covers agent-only sections, not just SKILL.md."""
    root = _copy_surfaces(tmp_path)
    _apply_full_guard_everywhere(root)
    agent = _MODULE.SKILL_TO_AGENT["wordpress-critic"]
    path = root / ".claude/agents" / f"{agent}.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("</Agent_Prompt>", "  evals/harness is local.\n</Agent_Prompt>", 1), encoding="utf-8")

    _assert_failure(root, str(path), "references evals/harness without a proving-ground guard mapping")

"""Tests for the opt-in Check-round honesty tripwire.

``validate_wordpress_skill_output.py --require-check-round-honesty`` is off by
default, so every existing caller keeps today's behavior. With it on, an
output that carries a ``Check round <n>: <file> exit <status>`` line (the
fix-and-rerun record the four executors write) while also recording a
``Proving ground:`` value of ``not installed``, ``unresolved (<reason>)``, or
``<root> (unusable: <reason>)`` fails: none of those proving-ground states
lets a harness command run, so the round lines are either fabricated or
stale. This mirrors ``check_proving_ground_record`` / ``--require-proving-ground``.

Known blind spot: this only flags the combination of a Check round line with
one of the three "no root" proving-ground values. It cannot detect a Check
round line that is fabricated alongside a truthful, resolved
``Proving ground: <path>@<commit>`` record, or a round count that disagrees
with the number of commands actually named.
"""

from __future__ import annotations

import validate_wordpress_skill_output as oracle


def _find_check(result: dict, check_id: str) -> dict | None:
    return next((check for check in result["checks"] if check["id"] == check_id), None)


VERIFICATION_HEADER = (
    "## Spec Conformance\n"
    "Implements the approved wordpress-plugin-planner spec exactly; no deviations.\n\n"
    "## Generated File Map\n"
    "acme-runtime/acme-runtime.php\n\n"
    "## Implementation Packets\n"
    "The bootstrap file calls `register_post_type()` on init.\n\n"
    "## Security Notes\n"
    "Input passes through `sanitize_text_field()`.\n\n"
    "## Deviation Log\n"
    "No deviations from the approved plan.\n\n"
    "## Verification Notes\n"
)

VERIFICATION_FOOTER = (
    "\n\n## Critic Handoff\n"
    "Send the packet to wordpress-critic and wordpress-security-critic.\n"
)

SETUP_LINE = (
    "Set up the proving ground: install uv and run `[ -d ~/wp-ai-skills ] || git clone "
    "https://github.com/zivtech/wp-ai-skills ~/wp-ai-skills; ~/wp-ai-skills/install.sh --harness-only`."
)

NOT_CHECKED_LINES = (
    "NOT CHECKED: validate_wordpress_executor_packet.py (no proving ground root resolved)\n"
    "NOT CHECKED: materialize_wordpress_executor_packet.py (no proving ground root resolved)\n"
    "NOT CHECKED: validate_wordpress_artifact.py (no proving ground root resolved)\n"
)

CHECK_ROUND_LINES = (
    "Check round 0: packet.md exit 1\n"
    "Check round 1: packet.md exit 0\n"
)


def _plugin_text(verification_body: str) -> str:
    return VERIFICATION_HEADER + verification_body + VERIFICATION_FOOTER


def test_check_round_lines_beside_not_installed_fails() -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: not installed\n\n"
        f"{NOT_CHECKED_LINES}\n"
        f"{SETUP_LINE}"
    )

    result = oracle.validate_output(
        "wordpress-plugin-executor", text, require_check_round_honesty=True
    )

    check = _find_check(result, "check_round_honesty")
    assert check is not None
    assert check["passed"] is False
    assert "not installed" in check["detail"]


def test_check_round_lines_beside_unresolved_fails() -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: unresolved (no shell available)\n\n"
        f"{NOT_CHECKED_LINES}"
    )

    result = oracle.validate_output(
        "wordpress-plugin-executor", text, require_check_round_honesty=True
    )

    check = _find_check(result, "check_round_honesty")
    assert check is not None
    assert check["passed"] is False
    assert "unresolved" in check["detail"]


def test_check_round_lines_beside_unusable_fails() -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: /home/user/wp-ai-skills (unusable: uv not on PATH)\n\n"
        f"{NOT_CHECKED_LINES}"
    )

    result = oracle.validate_output(
        "wordpress-plugin-executor", text, require_check_round_honesty=True
    )

    check = _find_check(result, "check_round_honesty")
    assert check is not None
    assert check["passed"] is False
    assert "unusable" in check["detail"]


def test_check_round_lines_with_resolved_root_passes() -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: /home/user/wp-ai-skills@abc1234"
    )

    result = oracle.validate_output(
        "wordpress-plugin-executor", text, require_check_round_honesty=True
    )

    check = _find_check(result, "check_round_honesty")
    assert check is not None
    assert check["passed"] is True


def test_no_check_round_lines_is_not_flagged() -> None:
    text = _plugin_text("Proving ground: not installed\n\n" f"{NOT_CHECKED_LINES}\n" f"{SETUP_LINE}")

    result = oracle.validate_output(
        "wordpress-plugin-executor", text, require_check_round_honesty=True
    )

    check = _find_check(result, "check_round_honesty")
    assert check is None


def test_flag_off_by_default_omits_the_check() -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: not installed\n\n"
        f"{NOT_CHECKED_LINES}\n"
        f"{SETUP_LINE}"
    )

    result = oracle.validate_output("wordpress-plugin-executor", text)

    assert _find_check(result, "check_round_honesty") is None


def test_cli_flag_wires_to_validate_output(tmp_path) -> None:
    text = _plugin_text(
        f"{CHECK_ROUND_LINES}\n"
        "Proving ground: not installed\n\n"
        f"{NOT_CHECKED_LINES}\n"
        f"{SETUP_LINE}"
    )
    output_path = tmp_path / "output.md"
    output_path.write_text(text, encoding="utf-8")

    exit_code = oracle.main(
        ["--skill", "wordpress-plugin-executor", "--output", str(output_path), "--require-check-round-honesty"]
    )

    assert exit_code == 1

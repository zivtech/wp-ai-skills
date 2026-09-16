"""Tests for eval harness Claude invocation command construction."""

import sys
import json
from pathlib import Path

import pytest


HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))

import invoke


def test_build_claude_command_includes_model_effort_and_cli_agent():
    command = invoke.build_claude_command(
        "Return ok",
        "external-agent",
        model="sonnet",
        effort="low",
    )

    assert command[:5] == ["claude", "-p", "--tools", "", "--permission-mode"]
    assert "--model" in command
    assert command[command.index("--model") + 1] == "sonnet"
    assert "--effort" in command
    assert command[command.index("--effort") + 1] == "low"
    assert "--agent" in command
    assert command[command.index("--agent") + 1] == "external-agent"
    assert "Return ok" not in command


def test_prepare_claude_prompt_injects_nested_wordpress_agent():
    prompt, cli_agent, agent_path = invoke.prepare_claude_prompt_and_agent(
        "Review this fixture",
        "wordpress-security-critic",
    )

    assert cli_agent is None
    assert agent_path is not None
    assert agent_path.name == "wordpress-security-critic.md"
    assert "You are the WordPress Security Critic" in prompt
    assert prompt.rstrip().endswith("Review this fixture")


def test_prepare_claude_prompt_resolves_dot_named_wordpress_agent_alias():
    prompt, cli_agent, agent_path = invoke.prepare_claude_prompt_and_agent(
        "Plan this migration",
        "wordpress-planner.migration",
    )

    assert cli_agent is None
    assert agent_path is not None
    assert agent_path.name == "wordpress-migration-planner.md"
    assert "WordPress Migration Planner" in prompt
    assert prompt.rstrip().endswith("Plan this migration")


def test_build_codex_command_is_non_agentic_chatgpt_baseline():
    command = invoke.build_codex_command(
        model="gpt-5.5",
        effort="medium",
        output_path="/tmp/last.md",
        work_root="/tmp/wp-baseline",
    )

    assert command[:4] == ["codex", "exec", "--model", "gpt-5.5"]
    assert "-c" in command
    assert command[command.index("-c") + 1] == "model_reasoning_effort=medium"
    assert "--sandbox" in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert "--ignore-user-config" in command
    assert "--ephemeral" in command
    assert "--ignore-rules" in command
    assert "--cd" in command
    assert command[command.index("--cd") + 1] == "/tmp/wp-baseline"
    assert "--output-last-message" in command
    assert command[-1] == "-"


def test_resolve_invocation_runtime_uses_codex_for_configured_baselines():
    settings = {
        "model": "sonnet",
        "effort": "low",
        "baseline_provider": "codex",
        "baseline_model": "gpt-5.5",
        "baseline_effort": "medium",
    }

    provider, model, effort = invoke.resolve_invocation_runtime(
        settings,
        "baseline-few-shot",
        model=None,
        effort=None,
    )

    assert provider == "codex"
    assert model == "gpt-5.5"
    assert effort == "medium"


def test_resolve_invocation_runtime_does_not_treat_candidate_lane_as_baseline():
    settings = {
        "model": "sonnet",
        "effort": "low",
        "baseline_provider": "codex",
        "baseline_model": "gpt-5.5",
        "baseline_effort": "medium",
    }

    provider, model, effort = invoke.resolve_invocation_runtime(
        settings,
        "raw_upstream_candidate",
        model=None,
        effort=None,
    )

    assert provider == "claude"
    assert model == "sonnet"
    assert effort == "low"


def test_wordpress_plugin_executor_invocation_settings_are_fast_lane():
    settings = invoke.get_invocation_settings("wordpress-plugin-executor")

    assert settings["model"] == "sonnet"
    assert settings["effort"] == "low"
    assert settings["baseline_provider"] == "codex"
    assert settings["baseline_model_policy"] == "newest-chatgpt-level-at-run-time"
    assert settings["baseline_model"] == "gpt-5.5"


def test_wordpress_block_executor_invocation_settings_use_chatgpt_baseline():
    settings = invoke.get_invocation_settings("wordpress-block-executor")

    assert settings["model"] == "sonnet"
    assert settings["effort"] == "low"
    assert settings["baseline_provider"] == "codex"
    assert settings["baseline_model_policy"] == "newest-chatgpt-level-at-run-time"
    assert settings["baseline_model"] == "gpt-5.5"


def test_wordpress_candidate_suite_declares_chatgpt_baseline_policy():
    settings = invoke.get_invocation_settings("wordpress-skill-candidate-eval")

    assert settings["baseline_provider"] == "codex"
    assert settings["baseline_model_policy"] == "newest-chatgpt-level-at-run-time"
    assert settings["baseline_model"] == "gpt-5.5"
    assert "run_wordpress_candidate_pilot.py" in settings["note"]
    assert "run_pairwise_pilot.py" in settings["note"]
    assert "baseline-* lanes through Codex" in settings["note"]


def test_invoke_skill_fails_closed_for_candidate_lanes():
    with pytest.raises(ValueError, match="suite-specific runner"):
        invoke.invoke_skill(
            run_id="candidate-routing-test",
            suite="wordpress-skill-candidate-eval",
            fixture_id="security-boundary-risk",
            condition="raw_upstream_candidate",
        )


def test_write_invocation_metadata_records_chatgpt_baseline_policy(tmp_path):
    metadata_path = tmp_path / "fixture.metadata.json"

    invoke.write_invocation_metadata(
        metadata_path,
        provider="codex",
        model="gpt-5.5",
        effort="medium",
        agent=None,
        condition="baseline-zero-shot",
        suite="wordpress-plugin-executor",
        fixture_id="smoke-wordpress-v1",
        mode="planner",
        stage="single",
        settings={
            "baseline_provider": "codex",
            "baseline_model_policy": "newest-chatgpt-level-at-run-time",
        },
    )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert metadata["provider"] == "codex"
    assert metadata["runtime"] == "local_codex_cli"
    assert metadata["model"] == "gpt-5.5"
    assert metadata["model_policy"] == "newest-chatgpt-level-at-run-time"
    assert metadata["auth_route"] == "ChatGPT/Codex local auth"


def test_write_stage_stderr_removes_stale_success_file(tmp_path):
    path = tmp_path / "fixture.stderr.txt"
    path.write_text("old failure", encoding="utf-8")

    invoke._write_stage_stderr(path, "", 0)

    assert not path.exists()


def test_every_wordpress_executor_suite_resolves_a_rollout_planner_agent():
    """Executor mode derives `<prefix>-planner`; every WordPress executor suite must resolve one.

    The blueprint executor exposed the gap: `wordpress-blueprint-planner` does
    not exist, so its skill lane produced an empty rollout and a zero-score
    contract instead of a graded output.
    """
    suites_root = HARNESS.parent / "suites"
    executor_suites = sorted(
        path.name for path in suites_root.iterdir() if path.name.startswith("wordpress-") and path.name.endswith("-executor")
    )
    assert executor_suites, "no WordPress executor suites found"
    for suite in executor_suites:
        prefix = suite.replace("-executor", "")
        assert invoke.agent_prompt_path(f"{prefix}-planner") is not None, f"{suite}: no planner agent for {prefix}-planner"


def test_blueprint_planner_alias_routes_to_the_general_wordpress_planner():
    path = invoke.agent_prompt_path("wordpress-blueprint-planner")
    assert path is not None and path.name == "wordpress-planner.md"


@pytest.mark.parametrize(
    "stdout",
    [
        "Failed to authenticate. API Error: 401 API key is invalid.\n",
        "API Error: 429 rate limited\n",
        "  \nNot logged in. Run claude login.\n",
    ],
)
def test_fatal_cli_stdout_is_not_a_generation(stdout):
    """`claude -p` printed a 401 on stdout with exit 0 and the lane scored it as output."""
    assert invoke.fatal_stdout_signature(stdout) is not None
    assert invoke.generation_ok(0, stdout) is False


def test_prose_that_quotes_an_error_phrase_is_still_a_generation():
    plan = "## Migration Scope\n\nIf the importer logs `API Error:` for a row, queue it for review.\n"
    assert invoke.fatal_stdout_signature(plan) is None
    assert invoke.generation_ok(0, plan) is True
    assert invoke.generation_ok(0, "   ") is False
    assert invoke.generation_ok(1, plan) is False
    assert invoke.generation_ok(0, "The API is overloaded, try again") is False


def test_run_claude_fails_closed_on_fatal_stdout_without_retrying(monkeypatch):
    calls = []

    class _Proc:
        returncode = 0
        stdout = "Failed to authenticate. API Error: 401 API key is invalid.\n"
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _Proc()

    monkeypatch.setattr(invoke.subprocess, "run", fake_run)
    rc, stdout, stderr, _ = invoke._run_claude("prompt", None, timeout_sec=5, max_retries=3)

    assert rc != 0
    assert "fatal CLI output" in stderr
    assert len(calls) == 1


@pytest.mark.parametrize("suite", sorted(invoke.DIRECT_SPEC_EXECUTOR_SUITES))
def test_wordpress_executor_suites_resolve_to_single_stage_executor_direct(suite):
    """Their fixtures are approved specs; the planner rollout stage refuses them."""
    assert (invoke.SUITES_ROOT / suite / "eval.yaml").exists()
    assert invoke.get_invocation_mode(suite) == "executor-direct"


def test_other_executor_suites_keep_the_three_stage_pipeline(monkeypatch):
    monkeypatch.setattr(invoke, "load_eval_yaml", lambda suite: {"skill": {"type": "executor"}})
    assert invoke.get_invocation_mode("dataviz-executor") == "executor"
    assert invoke.get_invocation_mode("dataviz-executor", override="executor-direct") == "executor-direct"


def test_invoke_routes_executor_direct_to_the_single_stage_path(monkeypatch):
    seen = {}
    monkeypatch.setattr(invoke, "get_invocation_mode", lambda suite, override=None: "executor-direct")
    monkeypatch.setattr(invoke, "invoke_executor_pipeline", lambda **kwargs: pytest.fail("pipeline must not run"))
    monkeypatch.setattr(invoke, "invoke_skill", lambda **kwargs: seen.update(kwargs) or "single")

    assert invoke.invoke(run_id="r", suite="wordpress-blueprint-executor", fixture_id="f", condition="skill") == "single"
    assert seen["mode_label"] == "executor-direct"

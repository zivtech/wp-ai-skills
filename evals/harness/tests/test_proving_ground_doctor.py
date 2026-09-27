"""Tests for evals/harness/proving_ground.py.

`resolve_root` implements the D1' resolution rule from plan-025 (the home file
at ``~/.config/wp-ai-skills/home`` first, then ``$WP_AI_SKILLS_HOME`` only when
it is absolute and outside the current directory, both gated on the marker
files that prove the root is really a wp-ai-skills checkout). `run_doctor`
reports what can run here without ever installing or writing anything.

No test in this file needs network or Docker: the one test that runs the real
probe (`test_doctor_runs_real_probe_against_empty_directory`) only exercises
the probe's documented "exits 0 on a completely empty environment" contract,
entirely offline.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import proving_ground  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MARKER_FILES = proving_ground.MARKER_FILES


def _make_root(tmp_path: Path, name: str = "root") -> Path:
    """A marker-valid root that is also synced (has ``.venv``).

    Every pre-existing doctor test in this file predates the sync-state gate
    and asserts on docker/probe-driven blocking, not sync-driven blocking; a
    synced-by-default root keeps those assertions meaningful. Tests that
    specifically exercise the unsynced state build their own root without
    ``.venv`` (see ``_make_unsynced_root``).
    """
    root = tmp_path / name
    for marker in MARKER_FILES:
        marker_path = root / marker
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text("{}\n", encoding="utf-8")
    (root / ".venv").mkdir(parents=True, exist_ok=True)
    return root


def _make_unsynced_root(tmp_path: Path, name: str = "root") -> Path:
    root = _make_root(tmp_path, name)
    (root / ".venv").rmdir()
    return root


def _write_home_file(home: Path, content: str) -> Path:
    home_file = home / proving_ground.HOME_FILE_RELATIVE
    home_file.parent.mkdir(parents=True, exist_ok=True)
    home_file.write_text(content, encoding="utf-8")
    return home_file


# --- resolve_root: home file ------------------------------------------------


def test_home_file_valid_resolves_with_home_file_source(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root == root
    assert resolution.source == "home-file"
    assert resolution.problems == ()


def test_home_file_without_trailing_newline_is_valid(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, str(root))

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root == root
    assert resolution.source == "home-file"


def test_home_file_wins_over_env_var(tmp_path: Path) -> None:
    home_root = _make_root(tmp_path, "home-root")
    env_root = _make_root(tmp_path, "env-root")
    home = tmp_path / "home"
    _write_home_file(home, f"{home_root}\n")

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(env_root)}, home, tmp_path / "cwd"
    )

    assert resolution.root == home_root
    assert resolution.source == "home-file"


def test_invalid_home_file_does_not_fall_back_to_env(tmp_path: Path) -> None:
    env_root = _make_root(tmp_path, "env-root")
    home = tmp_path / "home"
    _write_home_file(home, "line one\nline two\n")

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(env_root)}, home, tmp_path / "cwd"
    )

    assert resolution.root is None
    assert resolution.source is None
    assert resolution.problems


def test_home_file_multiple_lines_is_invalid(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\nextra\n")

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root is None
    assert resolution.problems


def test_home_file_missing_markers_is_invalid(tmp_path: Path) -> None:
    bare_root = tmp_path / "bare"
    bare_root.mkdir()
    home = tmp_path / "home"
    _write_home_file(home, f"{bare_root}\n")

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root is None
    assert resolution.problems


def test_home_file_control_characters_is_invalid(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\x01\n")

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root is None
    assert resolution.problems


def test_symlinked_home_file_is_refused(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    real_home_file = tmp_path / "elsewhere" / "home-file-target"
    real_home_file.parent.mkdir(parents=True)
    real_home_file.write_text(f"{root}\n", encoding="utf-8")
    home = tmp_path / "home"
    (home / ".config" / "wp-ai-skills").mkdir(parents=True)
    (home / ".config" / "wp-ai-skills" / "home").symlink_to(real_home_file)

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root is None
    assert resolution.source is None
    assert any("symlink" in problem for problem in resolution.problems)


def test_symlinked_home_file_parent_directory_is_refused(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    real_parent = tmp_path / "real-config"
    real_parent.mkdir()
    (real_parent / "home").write_text(f"{root}\n", encoding="utf-8")
    home = tmp_path / "home"
    (home / ".config").mkdir(parents=True)
    (home / ".config" / "wp-ai-skills").symlink_to(real_parent, target_is_directory=True)

    resolution = proving_ground.resolve_root({}, home, tmp_path / "cwd")

    assert resolution.root is None
    assert any("symlink" in problem for problem in resolution.problems)


# --- resolve_root: env var ---------------------------------------------------


def test_env_var_used_when_no_home_file(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(root)}, home, tmp_path / "cwd"
    )

    assert resolution.root == root
    assert resolution.source == "env"


def test_env_var_relative_is_rejected(tmp_path: Path) -> None:
    home = tmp_path / "home"

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": "relative/path"}, home, tmp_path / "cwd"
    )

    assert resolution.root is None
    assert resolution.source is None


def test_env_var_equal_to_cwd_is_rejected(tmp_path: Path) -> None:
    cwd = _make_root(tmp_path, "cwd")

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(cwd)}, tmp_path / "home", cwd
    )

    assert resolution.root is None


def test_env_var_inside_cwd_is_rejected(tmp_path: Path) -> None:
    cwd = tmp_path / "cwd"
    nested = cwd / "nested"
    for marker in MARKER_FILES:
        marker_path = nested / marker
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text("{}\n", encoding="utf-8")

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(nested)}, tmp_path / "home", cwd
    )

    assert resolution.root is None


def test_env_var_inside_cwd_via_symlinked_cwd_is_rejected(tmp_path: Path) -> None:
    real_cwd = _make_root(tmp_path, "real-cwd")
    cwd_link = tmp_path / "cwd-link"
    cwd_link.symlink_to(real_cwd, target_is_directory=True)

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(real_cwd)}, tmp_path / "home", cwd_link
    )

    assert resolution.root is None


def test_env_var_missing_markers_is_rejected(tmp_path: Path) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": str(bare)}, tmp_path / "home", tmp_path / "cwd"
    )

    assert resolution.root is None


def test_env_var_control_characters_is_rejected(tmp_path: Path) -> None:
    root = _make_root(tmp_path)

    resolution = proving_ground.resolve_root(
        {"WP_AI_SKILLS_HOME": f"{root}\x01"}, tmp_path / "home", tmp_path / "cwd"
    )

    assert resolution.root is None


def test_no_home_file_and_no_env_var_resolves_to_none(tmp_path: Path) -> None:
    resolution = proving_ground.resolve_root({}, tmp_path / "home", tmp_path / "cwd")

    assert resolution.root is None
    assert resolution.source is None
    assert resolution.problems == ()


def test_cwd_itself_is_never_used_as_root(tmp_path: Path) -> None:
    cwd = _make_root(tmp_path, "cwd")

    resolution = proving_ground.resolve_root({}, tmp_path / "home", cwd)

    assert resolution.root is None
    assert resolution.source is None


# --- --resolve CLI mode -------------------------------------------------------


def test_resolve_cli_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")

    exit_code = proving_ground.main(
        ["--resolve"], env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["root"] == str(root)
    assert payload["source"] == "home-file"
    assert payload["problems"] == []


# --- doctor -------------------------------------------------------------------


def test_doctor_reports_linux_only_gates_blocked_on_darwin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    monkeypatch.setattr(proving_ground.platform, "system", lambda: "Darwin")
    fake_manifest = {
        "environment": {"host": {"php": "8.3.0"}},
        "verification_tools": {
            "phpcs": {"status": "AVAILABLE"},
            "phpstan": {"status": "UNAVAILABLE"},
        },
    }

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["probe"], returncode=0, stdout=json.dumps(fake_manifest), stderr=""
        )

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 0
    for gate in ("wp_cli_activation", "plugin_check", "container_browser"):
        assert f"{gate}: blocked" in report
        assert "Linux-only" in report
    assert "phpstan" in report  # reported unavailable per the fake manifest


def test_doctor_reports_linux_gates_not_checked_on_linux(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    monkeypatch.setattr(proving_ground.platform, "system", lambda: "Linux")

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 0
    for gate in ("wp_cli_activation", "plugin_check", "container_browser"):
        assert f"{gate}: not-checked" in report


def test_doctor_reports_blocked_when_root_does_not_resolve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("doctor must not invoke the probe without a resolved root")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fail_if_called)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=tmp_path / "home", cwd=tmp_path / "cwd"
    )

    assert exit_code == 1
    assert "not installed" in report or "none" in report.lower()
    for gate_name in (
        "executor_packet_validation",
        "packet_materialization",
        "static_artifact_validation",
        "skill_output_contract",
        "runtime_smoke",
    ):
        assert f"{gate_name}: blocked" in report


def test_doctor_blocks_runtime_smoke_when_docker_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    monkeypatch.setattr(proving_ground.shutil, "which", lambda name: None)

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 0
    assert "runtime_smoke: blocked" in report
    assert "docker" in report.lower()


def test_doctor_reports_synced_yes_when_venv_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_root(tmp_path)  # synced by default
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 0
    assert "Synced: yes" in report
    for gate_name in (
        "executor_packet_validation",
        "packet_materialization",
        "static_artifact_validation",
        "skill_output_contract",
    ):
        assert f"{gate_name}: can-run" in report


def test_doctor_reports_synced_no_and_blocks_gates_when_venv_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED before the sync-state gate existed: an unsynced checkout still

    reported every stdlib/runtime gate as `can-run`, which is wrong -- `uv run
    --locked` against an unsynced `.venv` fails, so nothing here can actually run.
    """
    root = _make_unsynced_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")

    # docker present, probe would succeed -- neither should matter once unsynced.
    monkeypatch.setattr(proving_ground.shutil, "which", lambda name: "/usr/bin/docker")

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert f"Synced: no (run uv sync --locked in {root})" in report
    for gate_name in (
        "executor_packet_validation",
        "packet_materialization",
        "static_artifact_validation",
        "skill_output_contract",
        "runtime_smoke",
    ):
        assert f"{gate_name}: blocked" in report
    assert "not synced" in report
    # Linux-only gates are unaffected by sync state; they report their own reason.
    for gate_name in ("wp_cli_activation", "plugin_check", "container_browser"):
        assert "not synced" not in [
            line for line in report.splitlines() if line.strip().startswith(gate_name)
        ][0]


def test_doctor_exit_code_1_when_probe_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=1, stdout="", stderr="boom")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    exit_code, _report = proving_ground.run_doctor(
        tmp_path / "target", env={}, home=home, cwd=tmp_path / "cwd"
    )

    assert exit_code == 1


def test_doctor_never_writes_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    target = tmp_path / "target"
    target.mkdir()

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=["probe"], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)

    before = sorted(tmp_path.rglob("*"))
    proving_ground.run_doctor(target, env={}, home=home, cwd=tmp_path / "cwd")
    after = sorted(tmp_path.rglob("*"))

    assert before == after


@pytest.mark.skipif(
    platform.system() == "Windows", reason="probe subprocess invocation assumes POSIX argv"
)
def test_doctor_runs_real_probe_against_empty_directory(tmp_path: Path) -> None:
    """The only test here that shells out to the real probe. No network, no
    Docker: it only exercises the probe's documented empty-environment
    contract (probe_wordpress_environment.py's own module docstring)."""
    target = tmp_path / "empty-project"
    target.mkdir()
    cwd = tmp_path / "somewhere-else"
    cwd.mkdir()

    exit_code, report = proving_ground.run_doctor(
        target,
        env={"WP_AI_SKILLS_HOME": str(PROJECT_ROOT)},
        home=tmp_path / "home-without-config",
        cwd=cwd,
    )

    assert exit_code == 0
    assert "Probe exit code: 0" in report
    assert "executor_packet_validation: can-run" in report


def test_home_file_empty_is_invalid_and_does_not_fall_back(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, "")

    resolution = proving_ground.resolve_root(
        {proving_ground.ENV_VAR_NAME: str(root)}, home, tmp_path / "cwd"
    )

    assert resolution.root is None
    assert any("empty" in problem for problem in resolution.problems)


def test_home_file_relative_path_is_invalid_even_when_it_exists_under_cwd(tmp_path: Path) -> None:
    cwd = tmp_path / "cwd"
    _make_root(cwd, "harness")
    home = tmp_path / "home"
    _write_home_file(home, "harness\n")

    resolution = proving_ground.resolve_root({}, home, cwd)

    assert resolution.root is None
    assert any("not an absolute path" in problem for problem in resolution.problems)


def _capture_probed_paths(
    monkeypatch: pytest.MonkeyPatch, contents: list[list[str]] | None = None
) -> list[Path]:
    probed: list[Path] = []
    contents = contents if contents is not None else []

    def fake_invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
        probed.append(path)
        contents.append(sorted(child.name for child in path.iterdir()))
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(proving_ground, "_invoke_probe", fake_invoke_probe)
    return probed


def test_doctor_without_path_probes_an_empty_temp_dir_not_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    cwd = tmp_path / "hostile"
    cwd.mkdir()
    (cwd / "wp-config.php").write_text("<?php // must never be probed by default\n")
    contents: list[list[str]] = []
    probed = _capture_probed_paths(monkeypatch, contents)

    exit_code = proving_ground.main(["--doctor"], env={}, home=home, cwd=cwd)

    assert exit_code == 0
    assert len(probed) == 1
    assert probed[0].resolve() != cwd.resolve()
    assert contents == [[]]  # probed while empty
    assert not probed[0].exists()  # the temporary directory is cleaned up
    assert "empty temporary directory" in capsys.readouterr().out


def test_doctor_with_explicit_path_probes_that_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _make_root(tmp_path)
    home = tmp_path / "home"
    _write_home_file(home, f"{root}\n")
    project = tmp_path / "project"
    project.mkdir()
    probed = _capture_probed_paths(monkeypatch)

    proving_ground.main(["--doctor", "--path", str(project)], env={}, home=home, cwd=tmp_path)

    assert probed == [project.resolve()]
    assert f"Probed project: {project.resolve()}" in capsys.readouterr().out

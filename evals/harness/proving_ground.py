#!/usr/bin/env python3
"""Resolve the wp-ai-skills proving ground root, and report what can run here.

This is the code-side implementation of the resolution rule that the skills'
"Proving ground first" Hard Gate (COMMAND and REFERENCE variants, canonical
text in ``scripts/validate-distribution-parity.py``) describes to the model.
It never installs anything. By default the doctor probes an empty temporary
directory, so it runs no project code; ``--path`` opts in to probing a project.

Resolution order, both gated on marker files that prove the candidate is
really a wp-ai-skills checkout:

1. ``~/.config/wp-ai-skills/home`` (written by ``install.sh``), if it exists
   and is well-formed. An existing-but-invalid home file does NOT fall back to
   the environment variable -- it is a hard failure.
2. ``$WP_AI_SKILLS_HOME``, only when no home file exists, and only when it is
   an absolute path whose real path is neither equal to nor inside the real
   path of the current working directory.
3. Otherwise, no root resolves. The current directory itself is never used.

Negative space: this rule keeps a checkout's own ``evals/harness/`` code out
of the proving ground path when the agent's current directory happens to
contain one. It does not defend against an attacker who controls the
environment or the agent's own instructions.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

ENV_VAR_NAME = "WP_AI_SKILLS_HOME"
HOME_FILE_RELATIVE = Path(".config") / "wp-ai-skills" / "home"
MARKER_FILES: tuple[str, ...] = (
    "skills.sh.json",
    "evals/harness/probe_wordpress_environment.py",
)
PROBE_RELATIVE = Path("evals") / "harness" / "probe_wordpress_environment.py"

# Control characters (C0 plus DEL) are refused wherever a path or file
# content is trusted, matching install.sh's has_control_chars.
_CONTROL_CHARS = frozenset(chr(code) for code in range(0x00, 0x20)) | {chr(0x7F)}

STDLIB_GATES: tuple[tuple[str, str], ...] = (
    ("executor_packet_validation", "validate_wordpress_executor_packet.py"),
    ("packet_materialization", "materialize_wordpress_executor_packet.py"),
    ("static_artifact_validation", "validate_wordpress_artifact.py"),
    ("skill_output_contract", "validate_wordpress_skill_output.py"),
)
LINUX_ONLY_GATES: tuple[str, ...] = ("wp_cli_activation", "plugin_check", "container_browser")
LINUX_ONLY_REASON = "Linux-only by design (docs/wordpress/runtime-oracle-runbook.md)"


def _has_control_chars(text: str) -> bool:
    return any(char in _CONTROL_CHARS for char in text)


def _real(path: Path) -> Path:
    """Resolve symlinks and normalize, without requiring the path to exist."""
    return Path(os.path.realpath(str(path)))


def _has_markers(root: Path) -> bool:
    real_root = _real(root)
    return all((real_root / marker).is_file() for marker in MARKER_FILES)


@dataclass(frozen=True)
class Resolution:
    root: Path | None
    source: str | None  # "home-file" | "env" | None
    problems: tuple[str, ...] = ()


def _resolve_home_file(home: Path) -> Resolution | None:
    """Return a Resolution if the home file exists (valid or not), else None
    to signal "no home file" so the caller may consider the env var."""
    home_file = home / HOME_FILE_RELATIVE
    parent = home_file.parent
    if not (home_file.exists() or home_file.is_symlink()):
        return None

    if home_file.is_symlink():
        return Resolution(None, None, (f"home file {home_file} is a symlink",))
    if parent.is_symlink():
        return Resolution(None, None, (f"home file's parent directory {parent} is a symlink",))

    try:
        text = home_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return Resolution(None, None, (f"could not read home file {home_file}: {exc}",))

    candidate = text[:-1] if text.endswith("\n") else text
    if "\n" in candidate:
        return Resolution(None, None, (f"home file {home_file} has more than one line",))
    if not candidate:
        return Resolution(None, None, (f"home file {home_file} is empty",))
    if _has_control_chars(candidate):
        return Resolution(None, None, (f"home file {home_file} content has control characters",))
    if not Path(candidate).is_absolute():
        return Resolution(None, None, (f"home file {home_file} content is not an absolute path",))
    if not _has_markers(Path(candidate)):
        return Resolution(
            None,
            None,
            (f"home file {home_file} points at {candidate}, which lacks the proving-ground markers",),
        )
    return Resolution(_real(Path(candidate)), "home-file", ())


def _resolve_env(env: Mapping[str, str], cwd: Path) -> Resolution:
    value = env.get(ENV_VAR_NAME)
    if not value:
        return Resolution(None, None, ())
    if _has_control_chars(value):
        return Resolution(None, None, (f"{ENV_VAR_NAME} content has control characters",))
    if not Path(value).is_absolute():
        return Resolution(None, None, (f"{ENV_VAR_NAME} is not an absolute path",))
    real_candidate = _real(Path(value))
    real_cwd = _real(cwd)
    if real_candidate == real_cwd or str(real_candidate).startswith(str(real_cwd) + os.sep):
        return Resolution(
            None, None, (f"{ENV_VAR_NAME} resolves inside the current working directory",)
        )
    if not _has_markers(real_candidate):
        return Resolution(
            None, None, (f"{ENV_VAR_NAME}={value} lacks the proving-ground markers",)
        )
    return Resolution(real_candidate, "env", ())


def resolve_root(env: Mapping[str, str], home: Path, cwd: Path) -> Resolution:
    """Implement the proving-ground resolution rule. Never considers `cwd` itself."""
    home_result = _resolve_home_file(home)
    if home_result is not None:
        return home_result
    return _resolve_env(env, cwd)


# --- doctor -------------------------------------------------------------------


def _git_commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    commit = result.stdout.strip()
    return commit or "unknown"


def _uv_version() -> str | None:
    if shutil.which("uv") is None:
        return None
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _invoke_probe(probe_path: Path, path: Path) -> subprocess.CompletedProcess[str]:
    """Run the probe read-only, printing the manifest instead of writing one.

    Uses `sys.executable` (whatever interpreter is running the doctor, e.g. the
    project's uv-managed Python when invoked through `uv run`) rather than a
    second `uv` invocation.
    """
    return subprocess.run(
        [sys.executable, str(probe_path), "--path", str(path), "--print"],
        capture_output=True,
        text=True,
        timeout=300,
    )


def _unavailable_optional_tools(manifest: dict[str, Any]) -> list[str]:
    unavailable: list[str] = []
    host = manifest.get("environment", {}).get("host", {}) if isinstance(manifest, dict) else {}
    if not isinstance(host, dict) or not host.get("php"):
        unavailable.append("php")
    tools = manifest.get("verification_tools", {}) if isinstance(manifest, dict) else {}
    if not isinstance(tools, dict):
        tools = {}
    for tool in ("phpcs", "phpstan"):
        state = tools.get(tool)
        status = state.get("status") if isinstance(state, dict) else None
        if status != "AVAILABLE":
            unavailable.append(tool)
    return unavailable


def _gate_rows(
    resolution: Resolution, manifest: dict[str, Any] | None
) -> list[tuple[str, str, str | None]]:
    rows: list[tuple[str, str, str | None]] = []
    root_ok = resolution.root is not None

    for name, _script in STDLIB_GATES:
        if not root_ok:
            rows.append((name, "blocked", "proving ground not installed"))
            continue
        reason = None
        if name == "static_artifact_validation" and isinstance(manifest, dict):
            unavailable = _unavailable_optional_tools(manifest)
            if unavailable:
                reason = "optional tools unavailable: " + ", ".join(unavailable)
        rows.append((name, "can-run", reason))

    docker_present = shutil.which("docker") is not None
    if not root_ok:
        rows.append(("runtime_smoke", "blocked", "proving ground not installed"))
    elif not docker_present:
        rows.append(("runtime_smoke", "blocked", "docker not found"))
    else:
        rows.append(("runtime_smoke", "can-run", None))

    is_darwin = platform.system() == "Darwin"
    for name in LINUX_ONLY_GATES:
        if is_darwin:
            rows.append((name, "blocked", LINUX_ONLY_REASON))
        else:
            rows.append((name, "not-checked", "doctor does not execute Linux runtime oracles"))
    return rows


def run_doctor(
    path: Path,
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    cwd: Path | None = None,
) -> tuple[int, str]:
    """Report resolution, tool availability, and a gate table for `path`.

    Never installs anything and never writes a file: the probe is invoked
    with `--print` only, never `--out`. Returns (exit_code, report_text).
    Exit code is 0 only when the root resolves and the probe ran (regardless
    of what the probe found).
    """
    env = dict(env) if env is not None else dict(os.environ)
    home = home if home is not None else Path.home()
    cwd = cwd if cwd is not None else Path.cwd()

    resolution = resolve_root(env, home, cwd)

    lines: list[str] = []
    lines.append("wp-ai-skills proving ground doctor")
    lines.append(f"Resolved root: {resolution.root if resolution.root is not None else 'none'}")
    lines.append(f"Source: {resolution.source or 'none'}")
    for problem in resolution.problems:
        lines.append(f"Problem: {problem}")

    commit = _git_commit(resolution.root) if resolution.root is not None else "unknown"
    lines.append(f"Commit: {commit}")

    uv_version = _uv_version()
    lines.append(f"uv: {uv_version if uv_version is not None else 'missing'}")
    lines.append(f"Platform: {platform.platform()}")

    manifest: dict[str, Any] | None = None
    probe_ran = False
    if resolution.root is not None:
        probe_path = resolution.root / PROBE_RELATIVE
        result = _invoke_probe(probe_path, path)
        probe_ran = result.returncode == 0
        lines.append(f"Probe exit code: {result.returncode}")
        if result.returncode != 0:
            lines.append(f"Probe stderr: {result.stderr.strip()}")
        try:
            parsed = json.loads(result.stdout)
        except (ValueError, TypeError):
            parsed = None
            lines.append("Probe output was not valid JSON")
        manifest = parsed if isinstance(parsed, dict) else None
    else:
        lines.append("Probe: not run (no proving ground root)")

    lines.append("")
    lines.append("Gates:")
    for name, status, reason in _gate_rows(resolution, manifest):
        suffix = f" ({reason})" if reason else ""
        lines.append(f"  {name}: {status}{suffix}")

    exit_code = 0 if (resolution.root is not None and probe_ran) else 1
    return exit_code, "\n".join(lines) + "\n"


# --- CLI ----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve the wp-ai-skills proving ground root and report what can run here."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--resolve",
        action="store_true",
        help="Print the resolved root, source, and any problems as JSON.",
    )
    mode.add_argument(
        "--doctor",
        action="store_true",
        help="Print a human-readable report of what can run here. Installs nothing.",
    )
    parser.add_argument(
        "--path",
        default=None,
        help=(
            "WordPress project directory to probe in --doctor mode. Probing a project runs "
            "that project's own tooling (WP-CLI, which loads its wp-config.php, plugins, "
            "theme, and wp-cli.yml requires; or its DDEV, Lando, or wp-env commands), so "
            "only pass a project you trust. Default: an empty temporary directory, which "
            "reports host tools without running any project code."
        ),
    )
    return parser


def main(
    argv: list[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    cwd: Path | None = None,
) -> int:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    env = dict(env) if env is not None else dict(os.environ)
    home = home if home is not None else Path.home()
    cwd = cwd if cwd is not None else Path.cwd()

    if args.resolve:
        resolution = resolve_root(env, home, cwd)
        payload = {
            "root": str(resolution.root) if resolution.root is not None else None,
            "source": resolution.source,
            "problems": list(resolution.problems),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.path is not None:
        exit_code, report = run_doctor(Path(args.path).resolve(), env=env, home=home, cwd=cwd)
        sys.stdout.write(f"Probed project: {Path(args.path).resolve()}\n" + report)
        return exit_code
    with tempfile.TemporaryDirectory(prefix="wp-ai-skills-doctor-") as empty:
        exit_code, report = run_doctor(Path(empty), env=env, home=home, cwd=cwd)
    sys.stdout.write(
        "Probed: an empty temporary directory (host tools only; pass --path to probe a project)\n"
        + report
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

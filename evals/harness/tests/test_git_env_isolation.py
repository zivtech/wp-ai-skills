"""Regression tests: a hook-inherited GIT_DIR must never reach the real repo.

Git exports GIT_DIR and GIT_PREFIX (and from some commands GIT_WORK_TREE,
GIT_INDEX_FILE, ...) to hooks. On 2026-09-25 the pre-push hook ran
scripts/ci-local.sh with them still set; test_public_docs.py's `git init` in a
temp directory then re-initialised the enclosing repository and set
`core.bare = true` in its shared .git/config, breaking the main checkout and
every linked worktree. Two layers now prevent that, and each is tested here
against a disposable sentinel repository shaped like the real one (a main
checkout plus a linked worktree):

- git-hooks/pre-push unsets `git rev-parse --local-env-vars` before exec.
- conftest.py drops the same variables for the whole pytest session.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

from conftest import git_local_env_vars


ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / "git-hooks/pre-push"
GIT_SHELLING_TESTS = (
    "evals/harness/tests/test_public_docs.py",
    "evals/harness/tests/test_evidence_log.py",
    "evals/harness/tests/test_install_sh.py",
)
# Keeps sentinel setup independent of the developer's global/system config
# (a global core.hooksPath would otherwise bypass the hook under test).
ISOLATED_GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def _git(*arguments: str, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=Sentinel", "-c", "user.email=sentinel@example.invalid",
         *arguments],
        cwd=cwd, env=env or os.environ | ISOLATED_GIT_ENV, check=True,
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


def _sentinel(tmp_path: Path, files: dict[str, str] | None = None) -> tuple[Path, Path]:
    """A main checkout plus a linked worktree, like the one that was broken."""
    main = tmp_path / "main"
    main.mkdir()
    _git("init", "-q", cwd=main)
    for relative, content in (files or {}).items():
        path = main / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)
    _git("add", "-A", cwd=main)
    _git("commit", "-q", "--allow-empty", "-m", "sentinel", cwd=main)
    worktree = tmp_path / "linked"
    _git("worktree", "add", "-q", str(worktree), "-b", "linked", cwd=main)
    return main, worktree


def _snapshot(git_dir: Path) -> dict[str, str]:
    return {
        str(path.relative_to(git_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(git_dir.rglob("*")) if path.is_file()
    }


def _core_bare(main: Path) -> str:
    return _git("config", "--file", str(main / ".git/config"), "core.bare", cwd=main)


def test_pre_push_hook_clears_git_local_env_before_ci(tmp_path: Path) -> None:
    probe = tmp_path / "probe"
    stub_ci = (
        "#!/bin/bash\n"
        f"env > '{probe}.env'\n"
        f"git rev-parse --show-toplevel > '{probe}.toplevel'\n"
        # What test_public_docs.py does; with GIT_DIR leaked this re-inits
        # the pushing repository and flips its core.bare.
        f"git init -q '{tmp_path}/scratch'\n"
    )
    main, worktree = _sentinel(tmp_path, {"scripts/ci-local.sh": stub_ci})
    hooks_dir = Path(_git("rev-parse", "--path-format=absolute", "--git-path", "hooks",
                          cwd=worktree))
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK, hooks_dir / "pre-push")
    remote = tmp_path / "remote.git"
    _git("init", "-q", "--bare", str(remote), cwd=tmp_path)
    assert _core_bare(main) == "false"

    _git("push", "-q", str(remote), "HEAD:refs/heads/linked", cwd=worktree)

    inherited = dict(
        line.split("=", 1) for line in (tmp_path / "probe.env").read_text().splitlines()
        if "=" in line
    )
    leaked = sorted(set(git_local_env_vars()) & inherited.keys())
    assert leaked == [], f"pre-push passed repository-selecting variables to CI: {leaked}"
    assert Path((tmp_path / "probe.toplevel").read_text().strip()).resolve() == worktree.resolve()
    assert _core_bare(main) == "false"


def test_git_shelling_tests_never_touch_an_inherited_git_dir(tmp_path: Path) -> None:
    main, worktree = _sentinel(tmp_path)
    worktree_git_dir = Path(_git("rev-parse", "--absolute-git-dir", cwd=worktree))
    before = _snapshot(main / ".git")
    # The variables a pre-push hook from a linked worktree actually receives,
    # plus GIT_INDEX_FILE so a leaked `git add -A` would have somewhere to land.
    leaked_env = os.environ | {
        "GIT_DIR": str(worktree_git_dir),
        "GIT_PREFIX": "",
        "GIT_INDEX_FILE": str(worktree_git_dir / "index"),
    }

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *GIT_SHELLING_TESTS],
        cwd=ROOT, env=leaked_env, check=False, capture_output=True, text=True,
        timeout=300,
    )

    # Sentinel damage first: it is the failure that breaks real checkouts.
    assert _core_bare(main) == "false"
    assert _snapshot(main / ".git") == before
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]

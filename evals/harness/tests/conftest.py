import os
import subprocess
import sys
from pathlib import Path

import pytest

# Make the harness modules importable when collected by pytest.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# `git rev-parse --local-env-vars` as of git 2.50, used only if git cannot be
# asked directly.
FALLBACK_GIT_LOCAL_ENV_VARS = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_COUNT", "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE",
    "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE", "GIT_INDEX_FILE",
    "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX",
    "GIT_SHALLOW_FILE", "GIT_COMMON_DIR",
)


def git_local_env_vars() -> tuple[str, ...]:
    """Names of the environment variables that select a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--local-env-vars"],
            capture_output=True, text=True, check=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return FALLBACK_GIT_LOCAL_ENV_VARS
    return tuple(result.stdout.split()) or FALLBACK_GIT_LOCAL_ENV_VARS


def pytest_configure(config):
    """Never let an inherited GIT_DIR point test git calls at a real repo.

    A run launched from a git hook inherits GIT_DIR (and possibly
    GIT_WORK_TREE, GIT_INDEX_FILE, ...). Every test that shells out to git in
    a temp directory would then act on the enclosing repository instead:
    `git init` re-initialises it (setting core.bare = true in its shared
    config) and `git add -A` writes temp files into its index. Tests that
    read the real checkout find it from their working directory, so dropping
    these variables for the whole session is always correct.
    """
    for name in git_local_env_vars():
        os.environ.pop(name, None)

DOCKER_SHARDS = {
    "test_sandbox_proxy_supervisor_contract.py": "docker_sandbox",
    "test_sandbox_python_preflight.py": "docker_sandbox",
    "test_sandbox_tunnel_poll.py": "docker_sandbox",
    "test_sandboxed_package_runner.py": "docker_sandbox",
    "test_sandboxed_package_runner_canonical_bind.py": "docker_sandbox",
    "test_sandboxed_package_runner_limits.py": "docker_sandbox",
    "test_wp_staged_runtime_docker.py": "docker_generated_runtime",
}
DOCKER_SHARD_MARKERS = frozenset(DOCKER_SHARDS.values())


def pytest_itemcollected(item):
    """Assign every Docker node to exactly one reviewed CI shard."""
    is_docker = item.get_closest_marker("docker_boundary") is not None
    existing = {
        marker for marker in DOCKER_SHARD_MARKERS if item.get_closest_marker(marker)
    }
    if not is_docker:
        if existing:
            raise pytest.UsageError(f"non-Docker node has Docker shard: {item.nodeid}")
        return
    if item.get_closest_marker("live_provider"):
        raise pytest.UsageError(f"Docker/live-provider marker overlap: {item.nodeid}")
    expected = DOCKER_SHARDS.get(Path(str(item.path)).name)
    if expected is None:
        raise pytest.UsageError(f"Docker node has no reviewed shard: {item.nodeid}")
    if existing and existing != {expected}:
        raise pytest.UsageError(f"Docker node has multiple or wrong shards: {item.nodeid}")
    item.add_marker(expected)


@pytest.fixture(autouse=True)
def _hermetic_structural_gates(request, monkeypatch):
    """Keep unit tests of other gates hermetic.

    The API-existence lint and the security gate are required structural gates
    that shell out (PHPStan / phpcs). Each is independently stubbed to `skip`
    unless the test opts in with its own marker, so every non-gate test stays
    deterministic and toolchain-independent. The two are gated separately: an
    `real_api_lint` test still gets the security gate stubbed (and vice versa),
    so neither gate's integration tests are perturbed by the other.
    """
    import validate_wordpress_artifact as oracle

    if not request.node.get_closest_marker("real_api_lint"):

        def _stubbed_check_api_existence(path, timeout_sec=120):
            return (
                oracle.skip_check(
                    "api_existence",
                    "api-existence lint stubbed in unit tests (@pytest.mark.real_api_lint opts out)",
                ),
                None,
            )

        monkeypatch.setattr(oracle, "check_api_existence", _stubbed_check_api_existence)

    if not request.node.get_closest_marker("real_security_gate"):

        def _stubbed_check_security_gate(path, timeout_sec=120):
            return (
                oracle.skip_check(
                    "security_gate",
                    "security gate stubbed in unit tests (@pytest.mark.real_security_gate opts out)",
                ),
                None,
            )

        monkeypatch.setattr(oracle, "check_security_gate", _stubbed_check_security_gate)

    yield

#!/bin/bash
# scripts/ci-local.sh — Local reproduction of .github/workflows/validate.yml.
#
# Tests for this repository run locally, not on GitHub Actions (see
# CONTRIBUTING.md and README.md). This script is the single entry point.
#
# Usage:
#   scripts/ci-local.sh                 # default gate: the "validate" job, in order
#   scripts/ci-local.sh --docker        # also run the Docker-boundary jobs
#   scripts/ci-local.sh --wp-env        # also run the live wp-env probe job
#   scripts/ci-local.sh --all           # --docker --wp-env
#   scripts/ci-local.sh --reviewed-sha <sha>   # verify HEAD equals <sha> first
#   scripts/ci-local.sh --skip-prereq-check    # do not probe for missing tools
#   scripts/ci-local.sh -h | --help
#
# Exit status: 0 if every attempted step passed, 1 on the first failure.
# A skipped step (missing prerequisite, or a lane not requested) does not
# fail the run; it is recorded as SKIP in the summary.
#
# This script does not fake a pass. A step that cannot be reproduced
# faithfully on this machine (see the arm64 notes below and in
# CONTRIBUTING.md) is reported as SKIP with the reason, never as PASS.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RUN_DOCKER=0
RUN_WP_ENV=0
SKIP_PREREQ_CHECK=0
REVIEWED_SHA=""

while [ $# -gt 0 ]; do
  case "$1" in
    --docker) RUN_DOCKER=1; shift ;;
    --wp-env) RUN_WP_ENV=1; shift ;;
    --all) RUN_DOCKER=1; RUN_WP_ENV=1; shift ;;
    --reviewed-sha) REVIEWED_SHA="${2:-}"; shift 2 ;;
    --skip-prereq-check) SKIP_PREREQ_CHECK=1; shift ;;
    -h|--help)
      sed -n '2,25p' "$0"
      exit 0
      ;;
    *)
      echo "ci-local.sh: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$REPO_ROOT/var/ci-local/$TIMESTAMP"
mkdir -p "$RUN_DIR"
SUMMARY="$RUN_DIR/summary.txt"
: > "$SUMMARY"

STEP_NAMES=()
STEP_STATUSES=()
STEP_SECONDS=()
OVERALL_STATUS=0
STOP_ON_FAILURE=1

log() { printf '%s\n' "$*" | tee -a "$SUMMARY" >&2; }

record_step() {
  local name="$1" status="$2" seconds="$3"
  STEP_NAMES+=("$name")
  STEP_STATUSES+=("$status")
  STEP_SECONDS+=("$seconds")
  printf '%-70s %-6s %ss\n' "$name" "$status" "$seconds" >> "$SUMMARY"
}

have() { command -v "$1" >/dev/null 2>&1; }

# run_step NAME -- CMD...
# Runs CMD, logging output to $RUN_DIR/<slug>.log. Records PASS/FAIL and, on
# FAIL with STOP_ON_FAILURE=1, stops the whole run after printing a summary.
run_step() {
  local name="$1"; shift
  if [ "${1:-}" = "--" ]; then shift; fi
  local slug
  slug="$(printf '%s' "$name" | tr -c 'A-Za-z0-9' '-' | tr -s '-' | sed 's/^-//; s/-$//')"
  local logfile="$RUN_DIR/${slug}.log"
  log ""
  log "==> $name"
  local start
  start=$(date +%s)
  if "$@" >"$logfile" 2>&1; then
    local elapsed=$(( $(date +%s) - start ))
    log "    PASS (${elapsed}s) — log: $logfile"
    record_step "$name" "PASS" "$elapsed"
    return 0
  else
    local rc=$?
    local elapsed=$(( $(date +%s) - start ))
    log "    FAIL (${elapsed}s, exit $rc) — log: $logfile"
    log "    --- last 40 lines ---"
    tail -n 40 "$logfile" | sed 's/^/    /' | tee -a "$SUMMARY" >&2
    record_step "$name" "FAIL" "$elapsed"
    OVERALL_STATUS=1
    return 1
  fi
}

skip_step() {
  local name="$1" reason="$2"
  log ""
  log "==> $name"
  log "    SKIP — $reason"
  record_step "$name" "SKIP" "0"
}

finish() {
  log ""
  log "===================================================================="
  log "ci-local summary — $TIMESTAMP"
  log "Repo: $REPO_ROOT"
  log "Commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
  log "===================================================================="
  local i
  for i in "${!STEP_NAMES[@]}"; do
    printf '%-70s %-6s %ss\n' "${STEP_NAMES[$i]}" "${STEP_STATUSES[$i]}" "${STEP_SECONDS[$i]}"
  done | tee -a /dev/null
  log ""
  if [ "$OVERALL_STATUS" -eq 0 ]; then
    log "RESULT: PASS (see $SUMMARY)"
  else
    log "RESULT: FAIL (see $SUMMARY)"
  fi
  log "Full log directory: $RUN_DIR"
}

# ---------------------------------------------------------------------------
# 0. Optional REVIEWED_COMMIT_SHA-equivalent guard.
#
# validate.yml's "validate" job pins REVIEWED_COMMIT_SHA to the exact commit
# GitHub checked out, then asserts `git rev-parse HEAD` equals it, so the
# steps that follow are provably reviewing that commit and not something a
# concurrent push swapped in underneath them. Locally there is no concurrent
# checkout race, but the same intent — "verify you are testing the commit you
# think you are testing" — still applies when a sha is supplied explicitly
# (e.g. from a hook or a script wrapping this one).
# ---------------------------------------------------------------------------
if [ -n "$REVIEWED_SHA" ]; then
  ACTUAL_SHA="$(git rev-parse HEAD 2>/dev/null || echo "")"
  if [ "$ACTUAL_SHA" != "$REVIEWED_SHA" ]; then
    log "REVIEWED_COMMIT_SHA guard: expected $REVIEWED_SHA, HEAD is $ACTUAL_SHA"
    record_step "Verify reviewed commit" "FAIL" "0"
    finish
    exit 1
  fi
  record_step "Verify reviewed commit ($REVIEWED_SHA)" "PASS" "0"
fi

# ---------------------------------------------------------------------------
# Prerequisite probe
# ---------------------------------------------------------------------------
MISSING=()
if [ "$SKIP_PREREQ_CHECK" -eq 0 ]; then
  have uv       || MISSING+=("uv (https://docs.astral.sh/uv/)")
  have composer || MISSING+=("composer")
  have php      || MISSING+=("php")
  if [ "$RUN_DOCKER" -eq 1 ]; then
    have docker || MISSING+=("docker")
  fi
  if [ "$RUN_WP_ENV" -eq 1 ]; then
    have node   || MISSING+=("node")
    have npx    || MISSING+=("npx")
    have docker || MISSING+=("docker")
  fi
  if [ "${#MISSING[@]}" -gt 0 ]; then
    log "Missing prerequisites:"
    for m in "${MISSING[@]}"; do log "  - $m"; done
    log "Steps needing a missing tool will be skipped, not failed."
  fi
fi

HAVE_UV=0;       have uv && HAVE_UV=1
HAVE_COMPOSER=0; have composer && HAVE_COMPOSER=1
HAVE_DOCKER=0;   have docker && HAVE_DOCKER=1
HAVE_NODE=0;     have node && HAVE_NODE=1

# ===========================================================================
# DEFAULT GATE — mirrors the "validate" job in .github/workflows/validate.yml,
# same steps, same order, stop at first failure.
# ===========================================================================

if [ "$HAVE_UV" -eq 1 ]; then
  run_step "uv lock --check" -- uv lock --check || { finish; exit 1; }
  run_step "uv sync --locked --extra test" -- uv sync --locked --extra test || { finish; exit 1; }
else
  skip_step "uv lock --check / uv sync" "uv not found"
fi

if [ "$HAVE_COMPOSER" -eq 1 ]; then
  run_step "composer install (evals/harness/php-tools)" -- \
    composer install --no-interaction --no-progress --no-scripts --no-plugins \
      --prefer-dist --working-dir evals/harness/php-tools || { finish; exit 1; }
else
  skip_step "composer install (php-tools)" "composer not found — the API-existence lint gate will not run for real"
fi

run_step "install.sh --verify" -- ./install.sh --verify || { finish; exit 1; }

if [ "$HAVE_UV" -eq 1 ]; then
  run_step "validate-distribution-parity.py" -- \
    uv run --locked --extra test python scripts/validate-distribution-parity.py || { finish; exit 1; }
  run_step "validate-agent-frontmatter.py" -- \
    uv run --locked --extra test python scripts/validate-agent-frontmatter.py || { finish; exit 1; }
  run_step "validate-wordpress-exact-api-contract.py" -- \
    uv run --locked --extra test python scripts/validate-wordpress-exact-api-contract.py || { finish; exit 1; }

  run_step "validate-eval-suite-integrity.py (strict suites)" -- \
    uv run --locked --extra test python scripts/validate-eval-suite-integrity.py \
      --strict-suites wordpress-plugin-executor \
      --strict-suites wordpress-block-executor \
      --strict-suites wordpress-security-critic \
      --strict-suites wordpress-performance-critic \
      --strict-suites wordpress-planner.migration \
      --strict-suites wordpress-blueprint-executor \
      --strict-suites wordpress-skill-candidate-eval \
      --allow-known-gaps || { finish; exit 1; }

  run_step "verify_critic_tool_invisibility.py (tranche-J)" -- \
    uv run --locked --extra test python evals/harness/verify_critic_tool_invisibility.py || { finish; exit 1; }

  run_step "validate-public-docs.py" -- \
    uv run --locked --extra test python scripts/validate-public-docs.py || { finish; exit 1; }

  run_step "validate-evidence-log.py" -- \
    uv run --locked --extra test python scripts/validate-evidence-log.py || { finish; exit 1; }

  run_step "pytest evals/harness/tests (not docker_boundary and not live_provider)" -- \
    uv run --locked --extra test python -m pytest \
      -m 'not docker_boundary and not live_provider' \
      evals/harness/tests -q || { finish; exit 1; }

  MEASURE_RECORD="$RUN_DIR/plan010-artifact-measurement.json"
  run_step "measure-plan010-artifact-path.py --profile ci" -- \
    uv run --locked --extra test python scripts/measure-plan010-artifact-path.py \
      --profile ci --output "$MEASURE_RECORD" || { finish; exit 1; }
else
  skip_step "validators, pytest, Plan 010 measurement" "uv not found"
fi

# ===========================================================================
# OPTIONAL: --docker — the three ubuntu-latest Docker-boundary jobs.
#
# validate.yml's Docker jobs run in a hosted Linux amd64 runner with no
# repository secrets, a bounded 20 GiB disk admission floor, and run-owned
# cleanup. They also perform host-level actions (apt-get install tcpdump,
# sudo -n true, `docker system df` cleanup asserts) that assume a disposable
# Linux VM. This script reproduces the *pytest* content of those jobs against
# the same markers, on whatever platform Docker is running on here.
#
# Arch honesty vs. OS honesty — these are two different gaps, verified
# separately on this machine (Apple Silicon, Docker via OrbStack):
#
#   - Architecture: evals/harness/container-images.json pins per-architecture
#     image digests (amd64 AND arm64) for the node/composer/python
#     provisioning images, so arm64 alone is not a blocker and no
#     `--platform linux/amd64` emulation is needed for those images.
#   - Operating system: evals/harness/tests/test_sandbox_proxy_supervisor_contract.py
#     defines `docker_ready()` as `platform.system() == "Linux"` (nothing
#     else), and every docker_sandbox/docker_generated_runtime test is
#     `skipif(not docker_ready())`. On macOS this is `platform.system() ==
#     "Darwin"`, so EVERY test in both shards is skipped — confirmed on this
#     machine: 35 skipped / 3069 deselected (docker_sandbox), 5 skipped / 3099
#     deselected (docker_generated_runtime), 0 actually executed. This is an
#     OS gate, not an image-availability gate: `--platform linux/amd64`
#     emulation cannot satisfy it, because `platform.system()` reports the
#     host kernel, not the container's platform. This script does not fake a
#     pass here — see the SKIP counts printed below.
#
# What this script does NOT reproduce even with --docker, and why:
#   - the GitHub-hosted sandbox-feasibility job's `apt-get install tcpdump`
#     and bounded host DNS observation step (Linux-only, requires apt and a
#     disposable VM's sudo policy);
#   - the exact 20 GiB disk-admission and post-cleanup 12 GiB delta budget
#     checks tied to the ubuntu-latest runner's known-free disk baseline;
#   - the Linux-only oracles (wp_cli_activation, plugin_check,
#     container_browser) inside "runtime"-profile handoff re-certification.
#     evals/harness/recertify_wordpress_executor_packet.py's own docstring
#     states: "On a non-Linux host the isolated generated runtime reports
#     blocked by design, so the exit code is nonzero there for a runtime
#     profile; that is the expected macOS reading, not a defect. Green
#     belongs to Linux." This script honors that: on a non-Linux host, a
#     "runtime"-profile handoff is reported SKIP with this reason, not FAIL,
#     because a nonzero exit there is documented, expected behavior, not a
#     detected regression. A "static"-profile handoff still runs and its
#     result is taken at face value.
# ===========================================================================

if [ "$RUN_DOCKER" -eq 1 ]; then
  if [ "$HAVE_DOCKER" -eq 0 ] || [ "$HAVE_UV" -eq 0 ]; then
    skip_step "Docker-boundary jobs" "docker and/or uv not found"
  else
    HOST_ARCH="$(uname -m)"
    HOST_OS="$(uname -s)"
    log ""
    log "Docker host: $HOST_OS / $HOST_ARCH"
    if [ "$HOST_OS" != "Linux" ]; then
      log "Non-Linux host: docker_sandbox and docker_generated_runtime pytest"
      log "content is gated by docker_ready() == (platform.system() == 'Linux')"
      log "in test_sandbox_proxy_supervisor_contract.py, independent of Docker"
      log "or image architecture. Every test in both shards will be skipped"
      log "below, not faked as a pass — see the pytest skip counts."
    fi

    run_step "sandbox-feasibility pytest (docker_boundary and docker_sandbox)" -- \
      uv run --locked --extra test python -m pytest \
        -m 'docker_boundary and docker_sandbox and not live_provider' \
        evals/harness/tests -q || true

    run_step "generated-runtime-boundary pytest (docker_boundary and docker_generated_runtime)" -- \
      uv run --locked --extra test python -m pytest \
        -m 'docker_boundary and docker_generated_runtime and not live_provider' \
        evals/harness/tests -q || true

    shopt -s nullglob
    handoff_manifests=(evals/handoff/*/provenance.json)
    shopt -u nullglob
    if [ "${#handoff_manifests[@]}" -eq 0 ]; then
      skip_step "converged-artifact-handoff re-certification" "no committed evals/handoff/*/provenance.json in this checkout"
    else
      for manifest in "${handoff_manifests[@]}"; do
        dir=$(dirname "$manifest")
        handoff_id=$(basename "$dir")
        expected=$(uv run --locked --extra test python -c "import json,sys; print(json.load(open(sys.argv[1]))['packet_sha256'])" "$manifest")
        executor=$(uv run --locked --extra test python -c "import json,sys; print(json.load(open(sys.argv[1]))['executor'])" "$manifest")
        profile=$(uv run --locked --extra test python -c "import json,sys; print(json.load(open(sys.argv[1]))['profile'])" "$manifest")
        run_id="handoff-local-${handoff_id}-${TIMESTAMP}"
        if [ "$profile" = "runtime" ] && [ "$HOST_OS" != "Linux" ]; then
          skip_step "re-certify handoff: $handoff_id (profile=runtime)" \
            "non-Linux host: Linux-only oracles (wp_cli_activation, plugin_check, container_browser) are blocked by design per recertify_wordpress_executor_packet.py's own docstring — a nonzero exit here is documented, expected macOS behavior, not a detected regression. Verified with a live run: exit 1, runtime_command failed, the rest blocked. Green belongs to Linux."
        else
          run_step "re-certify handoff: $handoff_id" -- \
            uv run --locked --extra test python \
              evals/harness/recertify_wordpress_executor_packet.py \
              --packet "$dir/packet.md" --executor "$executor" \
              --profile "$profile" --run-id "$run_id" \
              --expected-packet-sha256 "$expected" --timeout-sec 600
        fi
      done
    fi

    log ""
    log "NOTE: apt-get/tcpdump host-DNS-observation step, the 20 GiB disk"
    log "admission floor, and the 12 GiB post-cleanup delta budget from the"
    log "hosted sandbox-feasibility job are NOT reproduced locally (SKIP by"
    log "design — see the block comment above this section in the script)."
  fi
fi

# ===========================================================================
# OPTIONAL: --wp-env — the live wp-env capability probe (Scenario C).
#
# Caveat found on a real developer machine: wp-env's default port (8888) can
# already be bound by something else — this machine runs several concurrent
# ddev/lando/wp-env projects for other work, and one run here hit "port is
# already allocated" against an unrelated process already on 8888.
# `wp-env start --auto-port` did NOT avoid this in testing here (it still
# tried 8888 and failed the same way against this specific collision), so
# this script instead probes for a free TCP port itself and passes it via
# `WP_ENV_PORT`, which `wp-env start --help` documents as a supported
# override ("The config's port can be overridden via WP_ENV_PORT."). This is
# a real gap between a hosted CI runner's clean, single-tenant host and a
# shared local dev machine, not something --auto-port fixed for us.
# ===========================================================================

find_free_tcp_port() {
  python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
}

if [ "$RUN_WP_ENV" -eq 1 ]; then
  if [ "$HAVE_NODE" -eq 0 ] || [ "$HAVE_DOCKER" -eq 0 ] || [ "$HAVE_UV" -eq 0 ]; then
    skip_step "live wp-env probe" "node, docker, and/or uv not found"
  else
    WP_ENV_SCRATCH="$RUN_DIR/wp-env-live-probe"
    mkdir -p "$WP_ENV_SCRATCH"
    printf '%s\n' '{"core": "WordPress/WordPress#7.0.3", "plugins": ["https://downloads.wordpress.org/plugin/plugin-check.zip"], "testsEnvironment": false}' \
      > "$WP_ENV_SCRATCH/.wp-env.json"

    WP_ENV_PORT="$(find_free_tcp_port 2>/dev/null || true)"
    if [ -z "$WP_ENV_PORT" ]; then
      log "Could not probe a free TCP port for wp-env; falling back to its default (8888)."
    else
      log "Using WP_ENV_PORT=$WP_ENV_PORT for the scratch wp-env project (avoids colliding with other local services)."
    fi
    export WP_ENV_PORT

    run_step "wp-env start (scratch project)" -- bash -c "
      cd '$WP_ENV_SCRATCH' && WP_ENV_PORT='$WP_ENV_PORT' npx --yes '@wordpress/env@11.12.0' start
    "
    wp_env_start_status=$?

    if [ "$wp_env_start_status" -eq 0 ]; then
      run_step "pytest test_probe_wordpress_environment.py (real_wp_env)" -- bash -c "
        WP_META_SKILLS_REQUIRE_TOOL=wp-env \
        WP_META_SKILLS_WP_ENV_PATH='$WP_ENV_SCRATCH' \
        uv run --locked --extra test python -m pytest \
          evals/harness/tests/test_probe_wordpress_environment.py -m real_wp_env -q
      "
    else
      skip_step "pytest test_probe_wordpress_environment.py (real_wp_env)" "wp-env start failed; see log above"
    fi

    run_step "wp-env destroy (scratch cleanup)" -- bash -c "
      cd '$WP_ENV_SCRATCH' && printf 'y\n' | npx --yes '@wordpress/env@11.12.0' destroy
    " || true
  fi
fi

finish
exit "$OVERALL_STATUS"

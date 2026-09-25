# Contributing

Contributions to `wp-ai-skills` should improve the WordPress skill contracts,
API specificity, validation harness, or evidence quality without overstating
what the repository proves.

## Working Rules

- Keep generated examples free of secrets, credentials, private URLs, and real
  client data.
- Name exact WordPress APIs, hooks, files, packages, commands, and verification
  surfaces when a claim depends on them.
- State negative space: say what a proof does not cover.
- Prefer deterministic contracts and runtime oracles to generic quality claims.
- Do not copy or closely adapt upstream prompt text until its license,
  attribution, and reuse-ledger entry have been reviewed.
- Treat this standalone repository as the active edit source. The earlier
  monorepo package build is historical provenance, described in
  [PROVENANCE.md](PROVENANCE.md).

## Local CI

Tests run locally, not automatically on GitHub Actions. `.github/workflows/validate.yml`
now triggers only on `workflow_dispatch` (a maintainer can still run it by hand
in an emergency); it no longer runs on `push` or `pull_request`. The single
entry point is:

```bash
scripts/ci-local.sh            # default gate: mirrors the "validate" job, same steps, same order
scripts/ci-local.sh --docker   # also run the Docker-boundary jobs (sandbox-feasibility,
                                # generated-runtime-boundary, converged-artifact-handoff)
scripts/ci-local.sh --wp-env   # also run the live wp-env capability probe (Scenario C)
scripts/ci-local.sh --all      # --docker --wp-env
```

It stops at the first failure in the default gate, writes a run log and
`summary.txt` to `var/ci-local/<timestamp>/` (gitignored), detects missing
prerequisites (`uv`, `composer`, `php`, `docker`, `node`, `wp-env`) and skips
cleanly rather than failing when one is absent, and never reports a SKIP as a
PASS.

**Install the pre-push gate** (installs into the shared git hooks directory,
including from a linked worktree):

```bash
git-hooks/install.sh
```

This installs `git-hooks/pre-push`, which runs the default gate
(`scripts/ci-local.sh` with no flags) before every `git push`. Measured at
~2 minutes in this repository (2026-09-24), which is under the ~3 minute
budget for a pre-push hook, so the hook runs the full default gate rather
than a subset. Bypass it for one push with `git push --no-verify`.

The hook clears the repository-selecting variables git exports to hooks
(`git rev-parse --local-env-vars`: `GIT_DIR`, `GIT_PREFIX`, `GIT_INDEX_FILE`,
...) before running the gate, and `evals/harness/tests/conftest.py` drops the
same variables for every pytest session. Without both, a test that runs
`git init` in a temporary directory re-initialises the enclosing repository
and sets `core.bare = true` in the shared `.git/config`, which breaks the main
checkout and every linked worktree (observed 2026-09-25).
`evals/harness/tests/test_git_env_isolation.py` guards both layers. If you
installed the hook before this fix, re-run `git-hooks/install.sh`; the
installed copy is not updated automatically. To repair a repository that was
already hit, run `git config --file "$(git rev-parse --git-common-dir)/config"
core.bare false`.
`--docker` and `--wp-env` are not part of the pre-push gate; run them by hand
before opening a PR that touches Docker-boundary or wp-env-probe code paths.

**Which jobs need Docker or wp-env**, matching validate.yml's job names:

| validate.yml job | Local flag | Needs |
|---|---|---|
| `validate` | (default, no flag) | `uv`, `composer`/`php` |
| `sandbox-feasibility` | `--docker` | Docker |
| `generated-runtime-boundary` | `--docker` | Docker |
| `converged-artifact-handoff` | `--docker` | Docker (only if `evals/handoff/*/provenance.json` is tracked) |
| `live-wp-env-probe` | `--wp-env` | Docker, Node, `wp-env` (via `npx`) |

**arm64 / macOS caveats**, verified on an Apple Silicon Mac with Docker Engine
via OrbStack (linux/arm64 host):

- `evals/harness/container-images.json` pins per-architecture image digests
  (amd64 *and* arm64) for the node/composer/python provisioning images used
  by `sandbox-feasibility` and `generated-runtime-boundary`, so those images
  pull and run natively — arm64 alone is not a blocker for them, and
  `scripts/ci-local.sh --docker` does not need `--platform linux/amd64`
  emulation for that part.
- However, `evals/harness/tests/test_sandbox_proxy_supervisor_contract.py`
  gates every `docker_sandbox`/`docker_generated_runtime` test on
  `platform.system() == "Linux"`. On macOS that is `"Darwin"`, so **every**
  test in both shards is skipped regardless of Docker or architecture —
  confirmed locally: 35 skipped (`docker_sandbox`), 5 skipped
  (`docker_generated_runtime`), 0 executed. This is an OS gate, not an
  image-availability gate; emulation cannot satisfy it, because
  `platform.system()` reports the host kernel, not the container's platform.
  Their pytest content genuinely does not run on macOS at all — only on
  hosted Linux (or a Linux VM whose *guest* `platform.system()` reports
  `"Linux"`, which OrbStack's containers do not expose to the macOS host
  process running pytest).
- A "runtime"-profile handoff re-certification (`converged-artifact-handoff`)
  is expected to fail on macOS by design:
  `evals/harness/recertify_wordpress_executor_packet.py`'s own docstring
  says a nonzero exit there on a non-Linux host is "the expected macOS
  reading, not a defect. Green belongs to Linux." `scripts/ci-local.sh`
  reports this as SKIP with that reason instead of FAIL.
- The hosted `sandbox-feasibility` job's `apt-get install tcpdump` /
  bounded host DNS observation step, its exact 20 GiB disk-admission floor,
  and its 12 GiB post-cleanup delta budget are tied to the ubuntu-latest
  runner's disposable Linux VM and are not reproduced locally at all.
- `scripts/ci-local.sh --wp-env` probes for a free TCP port and passes it via
  `WP_ENV_PORT` (a documented `wp-env start` override) instead of trusting
  wp-env's default port 8888, which was already bound by an unrelated
  process during testing on a machine running other concurrent Docker
  projects; `wp-env start --auto-port` did not avoid that specific
  collision in testing here.

**PR authors: paste the `scripts/ci-local.sh` summary into the PR
description** (the `RESULT:` line plus the per-step table from
`var/ci-local/<timestamp>/summary.txt`) as the validation record — GitHub
Actions no longer produces one automatically.

## Validation

Use Python 3.13.9 and uv 0.9.27. The locked Python environment is canonical;
the pinned Composer toolchain is also required for the full API and security
gates.

Regenerate the checksum manifest after any intentional change to a tracked
distribution surface, then run the locked validation sequence:

```bash
./install.sh --generate-manifest
uv lock --check
uv sync --locked --extra test
composer install --no-interaction --no-progress --no-scripts --no-plugins \
  --prefer-dist --working-dir evals/harness/php-tools
./install.sh --verify
uv run --locked --extra test python scripts/validate-distribution-parity.py
uv run --locked --extra test python scripts/validate-agent-frontmatter.py
uv run --locked --extra test python scripts/validate-wordpress-exact-api-contract.py
uv run --locked --extra test python scripts/validate-eval-suite-integrity.py \
  --strict-suites wordpress-plugin-executor \
  --strict-suites wordpress-block-executor \
  --strict-suites wordpress-security-critic \
  --strict-suites wordpress-performance-critic \
  --strict-suites wordpress-planner.migration \
  --strict-suites wordpress-blueprint-executor \
  --strict-suites wordpress-skill-candidate-eval \
  --allow-known-gaps
uv run --locked --extra test python scripts/validate-public-docs.py
uv run --locked --extra test python -m pytest \
  -m "not docker_boundary and not live_provider" evals/harness/tests -q
```

The remaining required partitions run separately on Linux with a supported
Docker Engine. They are disjoint from the general partition and from each
other. The live-provider marker is not part of ordinary validation.

```bash
uv run --locked --extra test python -m pytest \
  -m "docker_boundary and docker_sandbox and not live_provider" \
  evals/harness/tests -q
uv run --locked --extra test python -m pytest \
  -m "docker_boundary and docker_generated_runtime and not live_provider" \
  evals/harness/tests -q
```

`uv.lock` is authoritative. When changing a direct Python dependency, update
and review both resolver artifacts:

```bash
uv lock --python 3.13.9
uv export --locked --extra test --no-emit-project \
  --format requirements-txt --output-file requirements-validation.txt
```

If uv bootstrap is temporarily unavailable, the committed, hash-locked pip
export is a tested installation fallback for the general partition only:

```bash
validation_venv="$(mktemp -d "${TMPDIR:-/tmp}/wp-ai-skills-validation.XXXXXX")"
trap 'rm -rf "$validation_venv"' EXIT
python3.13 -m venv "$validation_venv"
"$validation_venv/bin/python" -m pip install --require-hashes \
  -r requirements-validation.txt
"$validation_venv/bin/python" -m pytest \
  -m "not docker_boundary and not live_provider" evals/harness/tests -q
```

The Python lock does not lock Composer, Node, Docker, `wp-env`, browsers,
provider SDKs, provider models, or operator-only optimization environments.

## Distribution Controls

The parity gate compares `.claude/skills`, `.agents/skills`, `.claude/agents`,
`.codex/agents`, and `skills.sh.json`. `MANIFEST.sha256` is the checksum control
for those publication surfaces. Review its diff after regeneration;
`./install.sh --verify` fails on missing, extra, symlinked, non-regular, or
changed distribution files.

The committed WordPress symbol snapshot is checked hermetically against its
source hashes, Composer locks, container inventory, and normalized symbol
digest. Rebuilding the snapshot is a separate maintainer operation with
reviewed immutable inputs; it is not an ordinary CI step.

## Provider and Runtime Boundaries

Live provider metadata smoke requires explicit operator authorization and a
current operator-selected model. It performs metadata lookup, not content
generation, and must never print a credential or provider response. A pass
does not prove generation quota or billing authorization.

The Docker partitions run without Actions secrets. They require the recorded
image digests and build-input hashes, isolated networking, causal timeouts,
run-owned cleanup, a 20 GiB admission floor, and the reviewed post-run disk
delta. A host `wp-env`, Docker Desktop result, mutable tag, or cached local image
is not a substitute for the required hosted Linux boundary.

## Removing a Worktree

Use `scripts/safe-worktree-remove.py <worktree>`, not `git worktree remove`.

`evals/results/` is gitignored, so a worktree holding a recorded run reports **clean**
under `git status --short` — which does not list ignored files — and `git worktree remove`
then deletes the directory and the run with it. That is not hypothetical: it destroyed a
recorded judged run on 2026-08-12, and the "is this safe?" check that was run could not
have caught it.

The wrapper refuses when expensive artifacts are present and tells you the ways out:
`--archive-to <dir>` to move them somewhere durable first, `--force` to discard them
deliberately, `--check-only` to report and touch nothing. Tracked files are recoverable
from git and caches are cheap to rebuild; run artifacts are neither.

## Reuse and Provenance

Reference-only upstream comparison is allowed. Direct copied or closely
adapted prompt text requires a source URL, commit or access date, license,
local file, adapted section, and rationale in the reuse ledger before it lands.
When in doubt, keep production skill text clean-room and cite the upstream
project only as a comparator.

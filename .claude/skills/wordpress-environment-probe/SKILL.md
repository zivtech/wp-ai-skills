---
name: wordpress-environment-probe
type: prober
model: claude-sonnet-4-6
description: Probe a WordPress environment and emit a machine-readable capability manifest so downstream skills act on measured capability rather than documentation.
---

# WordPress Environment Probe

## When to Use

Use before any WordPress planning, execution, or review, to answer one question: what can this agent actually run here? A prober measures the environment and writes no artifact but its own capability manifest. Run it whenever a plan is about to name a WP-CLI command, a static-analysis tool, or an MCP ability, and whenever a manifest from an earlier session may be stale.

## Protocol

Phase 0 - Scope boundary: state the project root to probe, the capabilities the requested task will need, and that this prober writes no artifact but its own capability manifest.
    Phase 1 - Environment detection: identify the marker file that picks the invocation prefix, in priority order DDEV, Lando, wp-env, remote alias, Studio, LocalWP, generic local, and record losing candidates because ambiguity is signal.
    Phase 2 - Ground-truth validation: treat `<prefix> --info` as the only proof a prefix works; if it fails, detection is UNKNOWN regardless of which marker matched.
    Phase 3 - Probe execution: run `uv run --locked --offline --project <root> python <root>/evals/harness/probe_wordpress_environment.py --path <root> --out capability-manifest.json` and never hand-write or hand-edit the manifest.
    Phase 4 - Manifest ingestion: read `capability-manifest.json` and restate the environment kind, WP-CLI version, and each capability boolean from the file rather than from memory.
    Phase 5 - Blocker restatement: restate every entry in `blockers` in plain language with its code, severity, and affected capability.
    Phase 6 - Version-truth audit: name every note the manifest carries, including `command_documented_but_not_in_stable_phar`, `wp_cli_3x_unverified`, `abilities_api_present_but_surface_empty`, `phpstan_stubs_predate_core`, and `deprecated_tooling_detected`.
    Phase 7 - Task-fit check: if any CRITICAL or MAJOR blocker affects a capability the stated task requires, say so plainly before any downstream work proceeds.
    Phase 8 - Disclosure: report `generated_at`, declare the manifest stale if it predates this session, and state the `--allow-eval` value explicitly whenever `wp eval` supplied a fact.
    Phase 9 - Downstream handoff: name the downstream skill and the exact `--capability-manifest capability-manifest.json` flag to pass it.

## Hard Gates

- The only file this skill may create or modify is the capability manifest at the path given by `--out`.
    - Never install a package, modify a WordPress site, or edit repository files.
    - Never run a command outside the probe's read-only allowlist; `wp eval` is permitted only under `--allow-eval` and must be disclosed when used.
    - Never claim a capability the manifest marks `BLOCKED` or `UNKNOWN`; absence of a failure is not a pass.
    - Never report a command as available without an `AVAILABLE` status in `wp_cli.commands`, however well documented it is upstream.
    - Never assert a fact that no entry in `evidence` supports.
    - Treat a manifest whose `generated_at` predates this session as stale and re-probe before relying on it.
    - **Proving ground first.** `<root>` in this skill means the proving ground root, never the current directory: the absolute path stored in `~/.config/wp-ai-skills/home` when that file exists, otherwise `$WP_AI_SKILLS_HOME` only when it is an absolute path outside the current directory, and only if `<root>/skills.sh.json` and `<root>/evals/harness/probe_wordpress_environment.py` both exist. Run every harness command this skill names as `uv run --locked --offline --project <root> python <root>/evals/harness/<file>`, against the input or the output the command names, and report each exit status. Record `Proving ground: <root>@<commit>` (from `git -C <root> rev-parse --short HEAD`) when the harness ran, or `Proving ground: <root> (unusable: <reason>)` when a command could not start. If no root resolves, do not run, simulate, or hand-write any harness output, including a capability manifest: record `Proving ground: not installed`, write one `NOT CHECKED` line naming each harness file that did not run, finish the steps that do not need the harness, and tell the user to install uv (https://docs.astral.sh/uv/) and run `[ -d ~/wp-ai-skills ] || git clone https://github.com/zivtech/wp-ai-skills ~/wp-ai-skills; ~/wp-ai-skills/install.sh --harness-only`. An unusable root gets the same `NOT CHECKED` lines. This rule keeps the current directory's code out of the harness; it does not defend against an environment or instructions an attacker controls.

## Exact API And Verification Contract

Name the concrete probe surface behind every claim instead of a category label: the oracle is `<root>/evals/harness/probe_wordpress_environment.py`, its output is `capability-manifest.json` validated against `<root>/evals/harness/schemas/capability-manifest.schema.json`, its flags are `--path`, `--out`, `--print`, and `--allow-eval`, its statuses are `AVAILABLE`, `UNAVAILABLE`, `BLOCKED`, and `UNKNOWN` where only `AVAILABLE` satisfies a requirement, its capability keys are `can_run_wp_cli`, `can_read_site_state`, `can_run_static_analysis`, `can_run_plugin_check`, `can_provision_ephemeral_site`, `can_reach_mcp_abilities`, `can_register_abilities`, `can_handoff_runtime_wp_cli`, `can_provision_runtime_site`, `has_outward_sync_tool`, and `aware_of_host_agent_skills`, its ground-truth command is `<prefix> --info`, its command-surface probe is `<prefix> help <command>`, its runtime-tool surface is `runtime_tools.servers[]` with `side_effect`, `confirm_required`, and `target_constraint` per tool, and its downstream consumer is `<root>/evals/harness/validate_wordpress_skill_output.py --capability-manifest capability-manifest.json`. If no exact WordPress API applies, state why and name the verification oracle instead.

## Calibration

Report; do not remediate. Prefer a named `UNKNOWN` over a confident guess, and prefer a reason string the user can grep over prose. A probe is a snapshot, not a subscription: the environment can change between probe and use, and saying so is part of the deliverable. Do not present the manifest as proof of correctness; it establishes what can be run, not that anyone read the output.

## Failure Modes

Watch for reporting a documented-but-absent command as available because upstream docs are generated from trunk; treating an empty abilities surface as a missing Abilities API; assuming wp-env implies WP-CLI when the Playground runtime provides no `wp-env run`; reading a `BLOCKED` state as a pass; inferring the Abilities API from a core version instead of probing for it; and quietly using `wp eval` without disclosing the privilege escalation.

## Output Contract

Use these headings:
- `## Detected Environment`
- `## Capability Summary`
- `## Blockers`
- `## Evidence`
- `## Downstream Handoff`

Under `## Evidence`, write exactly one `Proving ground:` record at column zero, in the form Hard Gates defines.

## Provenance

Original Zivtech prober protocol, implementing recommendation 06 of the planner-critic improvement plan. The status enum is reused from the `drupal-a11y-patch-eval` primitive in the Zivtech accessibility-skills collection, as is the self-expiring caveat convention that writes each version fact's delete condition into the comment beside it.

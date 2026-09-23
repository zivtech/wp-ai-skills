# Project Status — 2026-09-23

This is the current evidence-bounded snapshot for `wp-ai-skills` (renamed from
`wp-meta-skills` on 2026-09-23). It extends, rather than rewrites, the
[2026-07-17 status snapshot](project-status-2026-07-17.md).

## Repository State

- Last hosted-proven commit on `main`: `10345d6d814cd27b7b4b2c118dccad466734359b` (merge
  of [PR #35](https://github.com/zivtech/wp-ai-skills/pull/35), which added this snapshot).
- Hosted `validate.yml` run
  [35892848825](https://github.com/zivtech/wp-ai-skills/actions/runs/35892848825)
  passed every job at that commit, including the three no-secrets Docker jobs.
- Earlier the same day, `main` run
  [35885458787](https://github.com/zivtech/wp-ai-skills/actions/runs/35885458787)
  at `2f63294` failed those three jobs on reviewed image provenance drift
  (node, python, wordpress_cli), not on a code change. The pin refresh in
  [PR #34](https://github.com/zivtech/wp-ai-skills/pull/34) fixed it.

This hosted proof binds to `10345d6`. Later commits must not be described as
runtime-proven unless the hosted gates are rerun at that later commit.

## What Changed Since 2026-07-17

- **Environment measurement.** `/wordpress-environment-probe` emits a
  `capability-manifest.json` covering the WP-CLI prefix, Local and Studio hosts,
  and agent-facing runtime tools. Only `AVAILABLE` satisfies a requirement.
  The saved-output runner scores fixtures against per-fixture manifest sidecars.
- **Runtime-tool branching.** The migration planner treats host sync tools as
  imports with side effects that need target confirmation; the Blueprint
  executor names the Studio launch step. The first sidecar-scored runs are in
  [EVIDENCE.md](../../EVIDENCE.md): every lane failed its contract, and those
  runs claim no quality edge.
- **Site audit.** `/wordpress-site-audit` observes a running site through public
  surfaces and reports unrun checks as `NOT CHECKED`.
- **Repair loop.** phpcbf auto-fix, persisted phpcs diagnostics, WPCS
  how-to-satisfy hints, `--seed-packet` continuation, and a converged-artifact
  Linux handoff lane. See
  [repair-loop-levers-reland-2026-08-24.md](repair-loop-levers-reland-2026-08-24.md).
- **Critic corpus.** T/J/C tranches with a suite-aware answer-key scorer and
  sourcing and leakage checks.
- **Local agent-tools value eval.** Design, suite, and dry run; see
  [localwp-agent-tools-eval-design-2026-09-02.md](localwp-agent-tools-eval-design-2026-09-02.md).
- **Disproved premises.** Recorded in
  [negative-results.md](negative-results.md), including the proposed second,
  stricter PHPCS profile (A6; [measurement](wpcs-second-profile-measurement-2026-08-29.md)).

## Current Product Boundary

This status does not claim:

- production readiness;
- universal security or stored-XSS absence;
- a quality edge from the runtime-tool branching or any sidecar-scored run;
- Playground or Studio launch behavior beyond the recorded verification;
- broad model superiority or benchmark-grade repair-loop convergence;
- hosted proof for commits after `10345d6` unless the hosted gates are rerun
  there.

The general evidence boundaries in [EVIDENCE.md](../../EVIDENCE.md) and the
runtime proof semantics in
[runtime-oracle-runbook.md](runtime-oracle-runbook.md) remain authoritative.

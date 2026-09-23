# Changelog

All notable changes to `wp-ai-skills` will be documented in this file.

## Unreleased

- Added the `wordpress-environment-probe` prober skill and `capability-manifest.json` contract (with its own output oracle). The manifest now records Local and Studio hosts, the WP-CLI prefix, and agent-facing runtime tool surfaces; per-fixture manifest sidecars are scored by the saved-output runner.
- Added the `wordpress-site-audit` auditor skill, which reports unchecked surfaces as `NOT CHECKED` rather than as passes.
- Branched the migration planner and Blueprint executor on `runtime_tools`: host sync tools are treated as imports with side effects and require target confirmation, and the Blueprint executor names the Studio launch step.
- Hardened the executor repair loop: deterministic phpcbf auto-fix stage, persisted phpcs diagnostics and how-to-satisfy WPCS hints in repair prompts, `--seed-packet` continuation, the `readme.txt` format contract, and a converged-artifact Linux handoff lane (`recertify_wordpress_executor_packet.py`).
- Added the WordPress critic evaluation corpus (T/J/C tranches) with a suite-aware answer-key scorer, CVE-diff fixture sourcing, and tool-invisibility and baseline-leakage checks.
- Added the `localwp-agent-tools-value` eval harness (design, suite, dry run).
- Added the isolated generated-artifact runtime and block execution-proof chain (staged validation, streamed artifact scans, execution-graph proof bound to runtime results).
- Added Gutenberg planning and block contract hardening, external design-baseline ingestion for the theme planner, and the AI Client provider-registration contract.
- Consolidated null results into one gate-checked evidence log and extended CI to the policy documents it inspects.
- Refreshed reviewed container image provenance pins whenever upstream tags moved; most recently node, python, and wordpress_cli on 2026-09-23 (base-layer rebuilds with unchanged tool versions).
- Renamed the repository from `zivtech/wp-meta-skills` to `zivtech/wp-ai-skills`. GitHub redirects the old URL. Stable schema identifiers (`wp-meta-skills/block-execution-artifact-gate`, `wp-meta-skills/api-lint`, the capability-manifest `$id`) and workspace-lease prefixes keep the old name so existing evidence still validates.

## 0.1.0 - 2026-07-06

- Added the WordPress planner, executor, and critic skill suite.
- Added WordPress-specific eval suites for planners, executors, critics, and candidate comparison.
- Added deterministic WordPress output, packet, static artifact, and runtime oracle gates.
- Added generated-artifact runtime proofs for plugin PHPUnit, block build/editor/frontend render, block Interactivity API, block deprecation migration, MCP Adapter exposure/execution, and deterministic no-auth AI Client provider behavior.
- Added selected high-risk saved-output contract evidence, deterministic answer-key coverage, QA review, performance prompt-boundary repair notes, Blueprint static certification, and Blueprint launch-readiness preflight evidence.
- Added a pruned standalone package builder that exports WordPress skills, docs, suites, and the WordPress validation harness subset.
- Added `skills.sh.json` for the public skills.sh repository page grouping.

## Release Boundary

The first public release uses a clean-root import of the validated standalone
tree. Evidence remains bounded by `EVIDENCE.md`; this release does not claim
benchmark superiority, production readiness for generated artifacts, or
credentialed third-party provider behavior.

# Changelog

All notable changes to `wp-ai-skills` will be documented in this file.

## Unreleased

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

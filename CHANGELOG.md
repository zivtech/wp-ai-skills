# Changelog

All notable changes to `wp-ai-skills` will be documented in this file.

## Unreleased

- Fixed the content-model storage and guardrail checks so a trailing warning sentence no longer reads as the decision. `Binding source`, `Editing surface`, `Lock level`, and `Lock level rationale` records now take negation from the leading clause (before a sentence break, semicolon, or spaced dash), so an affirmative editing surface that ends "Do not rely on a template-level-only binding" passes. Across 28 distinct saved content-model outputs this flips one check (a sonnet/low media-credit `content_model_storage_decision_contract`, fail to pass). `none`, `**none**`, `none — ...`, `not required`, `out of scope`, and `does not have an editor surface` still fail, and a hedge anywhere in the value still fails. `NEGATED_DECISION_RE` is unchanged for the Gutenberg migration, plugin delivery unit, and security gates.
- Named the `Editorial guardrails phase: completed` record in the content-model planner's Hard Gates. It was only in the Output Contract paragraph, and none of 24 saved sonnet outputs wrote it, so the editorial-guardrails check failed every one.
- Fixed the content-model output oracle so the editorial-guardrails and storage-decision checks read records wrapped in Markdown emphasis (`**Content type: case_study**`, ``Lock level (`post`): `contentOnly` ``) and annotated content types (`Content type: attachment (...)`) instead of reading `case_study**` as the key. Every declared type still needs exactly one keyed lock record; list-item, indented, and table-cell records are still not authoritative, and an annotation that offers an alternative type now fails as a hedge.
- Extended the content-model, block, theme, and plugin planners and the theme critic with editor-UX guidance from the 2026-09-25 discovery: the editor cue for every editorial constraint, per-role editor settings stated as curation rather than authorization, theme.json settings mapped to the controls editors see (with theme.json precedence over `add_theme_support()`), editor-surface accessibility, admin-screen roles and capabilities, editor style parity, and image credit as attachment meta. Every runtime editor claim is tagged `runtime: manual-walk`. Adds five eval fixtures, registers the named editor surfaces, and pins them in each skill's Exact API contract.
- Added a "Proving ground first" Hard Gate to the ten skills that cite `evals/harness/` files (the probe, four executors, five planners): each resolves a proving-ground root from `~/.config/wp-ai-skills/home` or an absolute `$WP_AI_SKILLS_HOME`, never the current directory, and fails closed to `Proving ground: not installed` with `NOT CHECKED` lines instead of hand-writing harness output when no root resolves. Added `install.sh --harness-only` and `--doctor`, the `evals/harness/proving_ground.py` resolver, and the opt-in `validate_wordpress_skill_output.py --require-proving-ground` record check.
- Added the `wordpress-environment-probe` prober skill and `capability-manifest.json` contract (with its own output oracle). The manifest now records Local and Studio hosts, the WP-CLI prefix, agent-facing runtime tool surfaces, and whether the `wp login` one-time-login package and its companion plugin are present; per-fixture manifest sidecars are scored by the saved-output runner.
- Gated the migration planner on a source-structure inventory: a Drupal 8+ source (or any source with a supplied `source-structure.json`, contract `contracts/source-structure/` 1.2.0 from zivtech/drupal-meta-skills) is not planned past Phase 1 without one, and every inventoried component gets one `Structure disposition (<kind>:<id>):` record. The output oracle checks this with `--source-structure`, the saved-output runner scores per-fixture inventory sidecars, and the contract's schemas are vendored with a pinned hash.
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

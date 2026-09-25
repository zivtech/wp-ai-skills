# WordPress V1 Coverage Matrix

## Drupal-Equivalent Lifecycle Coverage

| Lifecycle Need | Drupal Analogue | WordPress V1 Surface |
|---|---|---|
| Main architecture planning | `drupal-planner` | `/wordpress-planner` |
| Content model planning | `drupal-planner.content-model` | `/wordpress-planner.content-model` |
| Theme planning | `drupal-planner.theme` | `/wordpress-planner.theme` |
| Migration planning | `drupal-migration-planner` | `/wordpress-planner.migration` |
| Config/artifact generation | `drupal-config-executor` | `/wordpress-blueprint-executor`, `/wordpress-plugin-executor`, `/wordpress-block-executor`, `/wordpress-theme-executor` |
| General review | `drupal-critic` | `/wordpress-critic` |
| Theme review | `drupal-theme-critic` | `/wordpress-theme-critic` |
| Security/performance focused review | companion critics | `/wordpress-security-critic`, `/wordpress-performance-critic` |

## WordPress-Native Coverage

| Domain | Planner | Executor | Critic |
|---|---|---|---|
| Project triage and routing | `/wordpress-planner` | `/wordpress-blueprint-executor` for repro envs | `/wordpress-critic` |
| CPTs, taxonomies, meta, ACF | `/wordpress-planner.content-model` | `/wordpress-plugin-executor` or `/wordpress-theme-executor` | `/wordpress-critic` |
| Plugin architecture | `/wordpress-planner.plugin` | `/wordpress-plugin-executor` | `/wordpress-security-critic`, `/wordpress-critic` |
| Block Editor blocks | `/wordpress-planner.block` | `/wordpress-block-executor` | `/wordpress-critic`, `/wordpress-performance-critic` |
| Block themes/theme.json | `/wordpress-planner.theme` | `/wordpress-theme-executor` | `/wordpress-theme-critic` |
| REST, Abilities, Interactivity APIs | `/wordpress-planner.plugin`, `/wordpress-planner.block` | `/wordpress-plugin-executor`, `/wordpress-block-executor` | `/wordpress-security-critic`, `/wordpress-performance-critic` |
| Performance and operations | `/wordpress-planner` | `/wordpress-blueprint-executor` for repro | `/wordpress-performance-critic` |
| Migration/page-builder conversion | `/wordpress-planner.migration` | `/wordpress-plugin-executor` or external migration tooling packet | `/wordpress-critic` |
| Release/plugin directory readiness | `/wordpress-planner.plugin` | `/wordpress-plugin-executor` | `/wordpress-security-critic`, `/wordpress-critic` |

## Editor-UX Coverage (discovery 2026-09-25; evidence in `editor-ux-gap-source-map-2026-09-25.md`)

Status tokens: `extend-existing` (authoring planned under local plans/021), `defer` (entry condition stated), `blocked-on:#39` (needs the runtime login-link oracle, zivtech/wp-ai-skills#39), `out-of-scope`. Every runtime editor claim in any skill is verifiable only once a #39-class oracle exists. Internal-evidence citations in the rows below were authorized by the operator on 2026-09-25 (counts only; no client name, domain, ticket keys, quotes, or tool name identifying the client's tracker); see the gap-source map for detail and for what would have changed had authorization been withheld.

| Gap | Status | Planner target (skill: phase) | Critic target (skill: phase) | Oracle today | Notes |
|---|---|---|---|---|---|
| G1 Editor accessibility (AT/keyboard operability of the editing surface) | extend-existing | `/wordpress-planner.block` P2, P6 | `/wordpress-theme-critic` P5; route WCAG/APG review through `a11y-critic` | static: packet check for `label` on custom toolbar buttons; runtime `blocked-on:#39` | comparators (reference-only unless noted): WordPress/gutenberg `design-system-ui-review` (adapt-eligible — weak-evidence shape 3, read and classified by operator 2026-09-25), adityaarsharma/orbit; local runtime walk (`editor-ux-gap-source-map-2026-09-25.md` § Runtime evidence, finding 4) confirms the heading-level-skip warning surfaces only in the non-default Outline panel and does not gate publish |
| G2 Admin-screen / editorial-workflow UX | extend-existing — full scope (internal evidence authorized 2026-09-25) | `/wordpress-planner.plugin` P2, P3; `/wordpress-planner.content-model` P5 (list columns) | `/wordpress-critic` P6 editor perspective; `/wordpress-security-critic` for capability args | runtime, role-aware, `blocked-on:#39` | comparators: BigOrangeLab `wp-admin-ui`, Lonsdale201 `wp-admin-list-table` (both MIT, adapt-eligible; `get_primary_column_aria_label()` is `@since 7.1.0`, not available at this repo's WP 7.0 floor — version-guarded prose note only, not an Exact API contract entry) |
| G3 Editorial-constraint UX | extend-existing (priority 1; unaffected by the internal-evidence decision) | `/wordpress-planner.content-model` P5 editorial guardrails; `/wordpress-planner.block` P2 | `/wordpress-theme-critic` P4 | static: `template_lock`/`templateLock`/`lock`/`allowed_block_types_all`/`canLockBlocks` presence; runtime cue `blocked-on:#39` | sources: Gutenberg "Curating the Editor Experience" series; comparators: WordPress/agent-skills `wp-patterns` (GPL-2.0-or-later per catalog; license re-read pending), 84emllc; local runtime walk (§ Runtime evidence, findings 2–3) confirms both the `template_lock:"all"` inserter empty-state and the `contentOnly` pattern's missing lock indication as concrete runtime defects |
| G4 Runtime editor verification | `blocked-on:#39` | — | — | none bundled (lifecycle.md disclaimers stand) | seven external runtime-verification patterns catalogued as comparators for #39; none uses wp-cli login links; local runtime walk (§ Runtime evidence) exercised the #39 login-link oracle pattern end-to-end (mint, use, invalidate) and recorded that cleanup removes the companion plugin but not the underlying wp-cli package |
| G5 theme.json editor-visible settings (incl. Global Styles / Style Book discoverability) | extend-existing (priority 2) | `/wordpress-planner.theme` P2, P4, P8 | `/wordpress-theme-critic` P3, P4 | static/public: theme.json settings vs `add_theme_support()` diff; preset CSS variables on the public page | sources: theme.json living reference, Global Settings & Styles guide; `wpds` does not cover this |
| N1 Media caption/credit workflow | extend-existing (internal evidence authorized 2026-09-25, n=12 — the largest sixth-gap cluster) | `/wordpress-planner.content-model` P4, P5 | `/wordpress-critic` | front-end credit render is public-checkable; editor field `blocked-on:#39` | previously conditional on authorization or a public re-check (labels `[Block] Image`, `[Feature] Media`, `caption`, `attachment`); now resolved by authorization; local runtime walk (§ Runtime evidence, finding 1) found the credit field's `context:"side"` classic meta box reachable only via the settings sidebar's post-type tab (closed on first load), a discoverability gap, not a defect; reclassified after a targeted re-check |
| N2 Media library UX | defer | — (one-line fold into `/wordpress-planner.theme` P6 if image sizes are touched) | — | `blocked-on:#39` | core-owned UI; thin WP levers |
| N3 Preview fidelity (any cause) | extend-existing (already FIRST-CLASS as parity; mechanisms added) | `/wordpress-planner.theme` P4; `/wordpress-planner.block` P3 | `/wordpress-theme-critic` P4 | runtime DOM/pixel diff `blocked-on:#39` | `add_editor_style()`, `editorStyle`, `wp_enqueue_block_style()` (block.json metadata, block Phase 3); broader than G5 — non-theme.json causes also fold in here |
| N4 Onboarding / in-product guidance | split: in-product → extend-existing `/wordpress-planner.content-model` P5; training program → out-of-scope | `/wordpress-planner.content-model` P5 | — | none | block descriptions, starter patterns, help panels are the WP levers |
| N5 Revisions / audit trail | defer | existing coverage (`/wordpress-planner.content-model` P2, P5; `revisions_enabled`) | — | none | core owns revision prominence |
| N6 Accessible-output authoring guardrails | extend-existing (medium; single-site walk evidence — lowest-confidence extend call in this batch) | `/wordpress-planner.content-model` P5; `/wordpress-planner.theme` P5 | `a11y-critic` (output walk) | static config presence; nudge behavior `blocked-on:#39` | `levelOptions`, pre-publish check panel, required-alt filter, site-logo alt fallback; local runtime walk (§ Runtime evidence, finding 4) confirms the heading-skip/empty-alt pattern also reaches the published frontend from the editor, mirroring the public front-end walk cited above |
| Editorial-UX audit of an existing site (audit → apply → verify shape) | `blocked-on:#39` | — | `/wordpress-site-audit` tier-2 phase or a new editor-walk auditor (decided when #39 lands) | none | Drupal `discovery-investigation` is the internal precedent; CMS-agnostic method half is a candidate sibling-repo (`ui-ai-skills`) question — see `editor-ux-gap-source-map-2026-09-25.md` |

## Known V1 Limits

- No dedicated WooCommerce critic yet; route WooCommerce work through `/wordpress-planner.plugin`, `/wordpress-security-critic`, and `/wordpress-performance-critic`.
- No dedicated accessibility critic yet; route frontend accessibility-heavy work through existing `a11y-critic` plus `/wordpress-theme-critic`. Editor-surface accessibility (AT/keyboard operability of the block editor, Site Editor, and wp-admin) is planned as phase text in `/wordpress-planner.block` P2/P6 and `/wordpress-theme-critic` P5 (local plans/021, editor-UX discovery 2026-09-25); its runtime verification is `blocked-on:#39`.
- No live WP-CLI or Playground runner is bundled; executors produce packets and verification commands.

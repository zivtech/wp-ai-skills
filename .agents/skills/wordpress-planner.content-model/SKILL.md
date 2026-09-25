---
name: wordpress-planner.content-model
type: planner
model: Codex-fable-5
description: Plan WordPress content models using CPTs, taxonomies, registered post meta, Block Bindings, editorial guardrails, migration disposition, and REST/headless exposure; ACF/meta boxes only when native meta cannot express the field.
---

# WordPress Content Model Planner

## When to Use

Use for custom post types, taxonomies, term hierarchies, post meta, Block Bindings, ACF field groups, editor workflows, permalink strategy, REST exposure, WPGraphQL/headless exposure, search/facet design, cross-CMS content-model migrations, relationship design, or multisite/multi-brand content scoping.

## Protocol

Phase 0 - Modeling boundary: state the user goal, editorial audience, content samples available, whether a source CMS exists (this activates migration mode for phases 1, 3, 4, and 7), and what is not being modeled yet.
    Phase 1 - Inventory and tooling: inspect existing post types, taxonomies, post meta, ACF field groups, templates, blocks, REST exposure, URLs, search indexes, reporting needs, WP/PHP targets, and available wp-env/Playground/WP-CLI/Composer/npm/test tooling. In migration mode, also build a source model inventory: every source content type, field, vocabulary, and component (for example Drupal Paragraph types), each with its source cardinality (single vs. multi-value), plus non-config data invisible to a config-only export such as state, menus, and per-environment settings, and name the extraction command used for each.
    Phase 2 - Content behavior analysis: classify lifecycle, ownership, permissions, search/filter needs, URL needs, revision needs, and display variation before choosing CPTs or taxonomies.
    Phase 3 - Post type and taxonomy design: decide CPT, taxonomy, post meta, option, user meta, block attribute, pattern, or external-system boundaries with explicit tradeoffs; for relationships, default to registered meta holding one or more post IDs with a picker UI (WordPress core has no relationship primitive), and escalate to a relationship plugin or custom tables only past a stated scale-evidence bar (Query Loop's editor preview bypasses a custom table via `query_loop_block_query_vars`, a custom table is invisible to REST/WXR/syndication, and multisite needs `wp_initialize_site` handling). In migration mode, disposition every source component and vocabulary from Phase 1's inventory using: custom block, core block plus pattern, synced pattern (`wp_block`) with pattern overrides, flatten to core blocks, or drop — each disposition states its criteria. Never merge two vocabularies that are co-attached to the same source content type or field; before dropping any vocabulary, grep views/listings for term-ID filters that depend on it.
    Phase 4 - Field and relationship matrix: specify names, cardinality, validation, defaults, UI placement, dependency implications, registered meta schema, REST exposure, and portability. Apply the storage decision rule as a hard boundary, not a preference: post meta holds facts needed outside the body (queried, sorted, fed to JSON-LD, read by Abilities/REST); taxonomy holds bounded, shared classification used for filters, listings, and archives, and is preferred over `meta_query` for any filterable set; block attributes hold component configuration only; inner blocks/`post_content` hold editorial composition; Block Bindings are the bridge that displays meta inside blocks, not a storage layer of their own. Every bound meta key or option must name its editing surface (a client-side Block Bindings source with `setValues`, a purpose-built block reading/writing the field via `useEntityProp`, or an equivalent editor UI) — a template-level-only binding or a render-only custom source does not satisfy "editors can edit."
    Phase 5 - Editorial workflow: define roles/capabilities, moderation, previews, revision expectations, bulk editing, admin columns, dashboard burden, and training needs, and run the required editorial-guardrails sub-phase: for every content type, choose a `template_lock` level (`contentOnly`, `insert`, `all`, or `false`) with a stated rationale — `contentOnly` is the default for a structured type when the brief cites editor friction with a prior rigid-layout or page-builder tool, and `false` requires its own justification, not silence; name the overridable slots, the allowed blocks (`allowed_block_types_all`, scoped per post type and per role where relevant), and any post-type-scoped/starter patterns or synced patterns with pattern overrides the type uses.
    Phase 6 - API, search, and template implications: specify show_in_rest, WPGraphQL/headless needs, permalinks, archive behavior, facets, indexing, canonical URLs, and theme/block dependencies. When more than one site or brand is involved, add a multisite/multi-brand scoping decision: per-site vs. network-scoped content types and taxonomies, syndication mechanism and canonical ownership when content is shared or traveling, cross-site query strategy (meta and taxonomies do not span sites natively), and an inventory of every ID-bearing block attribute that needs a remap rule when content syndicates across sites.
    Phase 7 - Migration and backfill plan: define source mapping, data cleanup, redirects, fixtures, count checks, rollback, and sample review. In migration mode, build one source disposition table — shared verbatim with `wordpress-planner.migration`'s Target Mapping so the two plans cannot diverge — giving every item from Phase 1's inventory (every content type, field, vocabulary, and component) exactly one disposition row that also carries its source cardinality, and reconcile the row count against the inventory count before treating the plan as complete.
    Phase 8 - Assumption register and alternatives: compare one CPT plus taxonomies, multiple CPTs, page hybrids, ACF-heavy models, and custom tables when relevant; label any priority drawn from evidence gaps as inferred and name the query that would replace the inference once source data exists.
    Phase 9 - Critic and executor handoff: name generated artifacts, plugin/theme responsibilities, and review checkpoints; when migration mode was active, confirm the shared disposition table travels unchanged to the migration runtime handoff.

## Hard Gates

- Do not use the client's noun as the content model without testing content behavior.
    - Do not split CPTs solely by layout differences.
    - Do not use post meta for high-cardinality faceting or relationship-heavy queries without scale, index, and cache reasoning; prefer a taxonomy for any bounded, repeatable, filterable set instead of `meta_query`.
    - Do not recommend ACF, Meta Box, Pods, or another field plugin as the default for a scalar field. Native `register_post_meta()`/`register_meta()` plus Block Bindings is the default; a field plugin requires a stated reason the native surface cannot express the field (for example a genuinely needed repeater or flexible-content structure) plus portability, schema, REST exposure, dependency, export, and migration notes.
    - Do not default every content type's `template_lock` to `false`. Every content type needs an explicit `Lock level:` decision (`contentOnly`, `insert`, `all`, or `false`) with a rationale in Editorial Workflow; an unlocked (`false`) type needs its own `Lock level rationale:`, not silence.
    - Every bound meta key or option needs a named `Editing surface:` in Post Type Taxonomy And Field Matrix. A binding with no editor-editable surface (PHP-only `register_block_bindings_source()` registration, or a template-level-only binding) is read-only and must be labeled as such, not presented as editor-editable.
    - Apply the storage decision rule (meta vs. taxonomy vs. block attribute vs. inner blocks vs. binding) explicitly in Post Type Taxonomy And Field Matrix; record `Storage decision rule applied: yes`.
    - In migration mode, every item in the source inventory (every source content type, field, vocabulary, and component) must receive exactly one disposition row in Migration And Validation Plan; a plan that omits any source item is incomplete. Never merge vocabularies co-attached to the same source type or field; check listings/views for term-ID filters before dropping any vocabulary.
    - Relationships default to registered meta holding post IDs with a picker UI; do not reach for a relationship plugin or custom tables without the stated scale-evidence bar.
    - When more than one site or brand is in scope, state per-site vs. network scoping, syndication/canonical ownership, and the ID-bearing block attributes that need a remap rule; do not assume meta or taxonomies span sites.
    - Every model must specify capabilities, REST exposure, permalink strategy, validation, migration/backfill, and sample-review gates.
    - Every plan must state the available runtime/tooling lane and the acceptance checks that can actually be run.

## Exact API And Verification Contract

Every recommendation, decision, remediation, and verification handoff must name the concrete WordPress surface it relies on. When relevant, include exact functions, hooks, files, packages, or commands instead of category labels: `current_user_can()`, `check_admin_referer()`/`check_ajax_referer()`/`wp_verify_nonce()`, `register_rest_route` `permission_callback` or `WP_REST_Controller` permission methods, `$wpdb->prepare()`, `sanitize_key()`/`sanitize_text_field()`/`wp_kses_post()`, `esc_html()`/`esc_attr()`/`esc_url()`/`wp_safe_redirect()`, `wp_handle_upload()`, `block.json`, `register_block_type()`, `render_callback`/`render.php`, deprecated block versions/migrate/transforms, `theme.json`, `register_post_type()`, `register_taxonomy()`, `register_post_meta()`/`register_meta()` with `show_in_rest`/schema/`auth_callback`, `WP_Query` args, `wp_cache_get()`/`wp_cache_set()`, transients with invalidation, `wp_schedule_event()`/`wp_next_scheduled()`/Action Scheduler, `wp_register_ability()`/`wp_abilities_api_init`, `label`/`description`/`category`, `wp_register_ability_category()`/`wp_abilities_api_categories_init`, `input_schema`/`output_schema`, `execute_callback`, `permission_callback`, `@wordpress/abilities`, `@wordpress/core-abilities`, `wordpress/mcp-adapter`, `mcp_adapter_init`, `mcp-adapter-discover-abilities`/`mcp-adapter-execute-ability`, `wp_ai_client_prompt()`, `wp_connectors_init`, Query Monitor, WP-CLI, Plugin Check, PHPCS/WPCS, PHPUnit, and Playwright/editor smoke where applicable. This plan additionally names the content-model surfaces: `register_post_type()` `show_in_rest`, `template`, and `template_lock` (`all`/`insert`/`contentOnly`/`false`, since WordPress 5.0); `register_post_meta()`/`register_meta()` args `single`, `default` (5.5), `show_in_rest` as a schema-bearing array (4.6), `sanitize_callback`/`auth_callback` (4.6), `object_subtype` (4.9.8), and `revisions_enabled` (6.4, post-object-type meta revisioning); Block Bindings core sources `core/post-meta` (6.5, requires `show_in_rest`), `core/pattern-overrides` (6.6), and `core/post-data`/`core/term-data` (6.9); `register_block_bindings_source()` for custom sources; the bindable-attribute allowlist and the `block_bindings_supported_attributes` filter (6.9) that extends it; editor-editable bindings require a client-side source registered with `registerBlockBindingsSource()` implementing `setValues` (6.7) — PHP-only registration is read-only in the editor; `allowed_block_types_all` scoped per post type and per role; `register_block_pattern()`/patterns-directory headers including `Post Types` and `Block Types`, starter patterns, synced patterns stored as `wp_block` posts, and pattern overrides; `registerBlockVariation()` for `core/query` with `name`/`isActive`/`allowedControls`; `wp_register_block_metadata_collection()` (6.7) and `wp_register_block_types_from_metadata_collection()` (6.8) for manifest-based block registration; and `register_setting()` for site-wide options. Cite the WordPress version each surface requires; where the research this contract is drawn from marks a claim UNVERIFIED, state it as unverified rather than as fact. If no exact WordPress API applies, state why and name the verification oracle instead.

## Calibration

Treat uncertainty as design data. Separate observed evidence from assumptions, name negative space, and avoid generic CMS advice or Drupal vocabulary transplants. Do not claim benchmark, release, or current-version status without evidence. This protocol assumes a WordPress 7.0 floor (see `evals/harness/data/wp-symbols.json`); when a cited surface landed after 7.0 (for example `core/post-data`/`core/term-data` or `block_bindings_supported_attributes` at 6.9), name that floor explicitly and do not assume it is available on an unconfirmed target version.

## Failure Modes

Watch for hidden authorization assumptions, unsafe production commands, missing rollback, missing test strategy, cache claims without invalidation, block/theme editor parity gaps, unlogged upstream reuse, unsupported version claims, `template_lock` silently defaulted to `false`, ACF reached for before native meta is ruled out, a bound meta key with no editor-editable surface, a co-attached vocabulary merged away, and a migration-mode plan that drops a source item without a disposition row.

## Output Contract

Use these headings:
- `## Content Model Summary`
- `## Current-State Evidence`
- `## Content Behavior Analysis`
- `## Post Type Taxonomy And Field Matrix`
- `## Editorial Workflow`
- `## API Search And Template Implications`
- `## Migration And Validation Plan`
- `## Assumption Register`
- `## Alternatives Considered`
- `## Acceptance Criteria`
- `## Executor Handoff`
- `## Critic Handoff`

The editorial-guardrails and storage-decision records above are part of the saved output contract. In Editorial Workflow: `Editorial guardrails phase: completed`, one `Lock level:` per content type, and one `Lock level rationale:` for every `Lock level: false`. In Post Type Taxonomy And Field Matrix: `Storage decision rule applied: yes`, and one `Editing surface:` for every `Binding source:`. When `Migration mode: required` appears in Content Model Summary, Migration And Validation Plan needs one `Disposition row:` per source item. Use each label exactly once at column zero in its owning section with an affirmative value; prose elsewhere does not substitute for the record.

## Provenance

Original Zivtech protocol. Compatible references remain reference-only unless reuse is logged and licensed.

The migration-mode disposition rubric, editorial-guardrails phase, storage decision rule, relationship and multisite/multi-brand guidance, and the Block Bindings/pattern surfaces in the Exact API contract were added 2026-09-24 after a field run of these skills on a Drupal-to-WordPress content-model migration surfaced them as gaps (generalized here; no client specifics). The named WordPress and Gutenberg APIs are public core documentation facts, not third-party expression, so no reuse-ledger entry applies to them.

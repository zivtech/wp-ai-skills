---
name: wordpress-planner.migration
type: planner
model: Codex-fable-5
description: Plan WordPress migrations, page-builder conversions, media moves, redirects, validation, rollback, and editorial cutovers.
---

# WordPress Migration Planner

## When to Use

Use for CMS-to-WordPress migrations, WordPress-to-WordPress migrations, page-builder-to-Gutenberg conversions, media migrations, URL/permalink changes, SEO-sensitive moves, or large editorial cutovers.

This planner owns source-to-block transformation, WordPress block serialization, unsupported-source accounting, rerunnable/idempotent writes, and semantic, editor, and frontend migration proof. It may hand a bounded new custom-block definition to `wordpress-planner.block` and `wordpress-block-executor`, but the migration mapping and importer remain in the migration lane.

## Protocol

Phase 0 - Migration boundary: classify CMS-to-WordPress, WordPress-to-WordPress, builder-to-block, redesign, media, users, SEO, or partial content migration.
    Phase 1 - Source audit and tooling: inspect source CMS/database/export shape, builder shortcodes, media, URLs, users, taxonomy, metadata, SEO fields, redirects, content counts, data quality issues, WP/PHP targets, and available wp-env/Playground/WP-CLI/importer tooling.
    Phase 2 - Target model mapping: map CPTs, taxonomies, meta, existing core/custom blocks, templates, menus, users, media, redirects, search, editorial workflow, and compatibility needs. If a new custom block is required, define only its migration-facing semantic contract before a bounded handoff to the block planner. When `wordpress-planner.content-model` ran a source model inventory for this migration, reuse its source disposition table unchanged rather than deriving a second one: every source content type, field, vocabulary, and component gets exactly one disposition row, and the two plans must not diverge on any row.
    Phase 3 - Transform design: define stable source identity mapping, two-pass relationship/reference resolution, field mapping, source-node-to-block mapping, WordPress-core serialization, non-whitespace freeform detection, unsupported-widget accounting, media sideload dedupe, safe URL/link rewriting, URL normalization, and byte-idempotent writes. Every mapped field row must cite its source storage cardinality (single vs. multi-value); a multi-value source field must not collapse to a single target value without a stated, reviewed reason. Never merge two source vocabularies that are co-attached to the same source content type or field, and before dropping any vocabulary, grep source views/listings for term-ID filters that depend on it.
    Phase 4 - Execution design: choose WP-CLI/importer/custom script/WP All Import/manual workflow, batch size, logs, dry runs, editorial freeze, content delta handling, and cutover sequence. When `capability-manifest.json` is supplied, choose a host sync path only from a `runtime_tools.servers[]` entry the manifest lists, never one marked `superseded`, and without a manifest record `Runtime tools: not probed` in Current-State Evidence. When a host-side or full-database sync tool moves the site (`ddev push pressable`, Studio `site_push`/`site_pull`, a host data-transfer or clone tool), treat it as an import with side effects: name its prerequisites (SSH key, WordPress.com login, Jetpack connection plus an active Jetpack Backup product where the tool depends on it), emit `Sync tool:` with the manifest's exact tool name and `Sync target:` honoring its `target_constraint` in the section that instructs the sync, a target-confirmation step that prints the destination and its `wp_get_environment_type()` before writing, and a post-import verification pass.
    Phase 5 - Validation design: define count checks, URL audits, redirect sampling, media checks, SEO checks, semantic block oracles, non-whitespace freeform checks, editor insertion/save/reload or edit/restore proof, frontend selectors/text/behavior, sample editorial review, performance checks, and signoff.
    Phase 6 - Rollback and monitoring: define backups, rerun strategy, rollback trigger, post-launch monitoring, error queues, and ownership.
    Phase 7 - Assumption register and alternatives: name fragile source-data, plugin, hosting, and editorial assumptions.
    Phase 8 - Test strategy: define fixture migrations, source-to-serialized-block expectations, run-id-scoped semantic assertions, unchanged and changed rerun tests, write-failure tests, rollback tests, editor/frontend proof, permission tests, and launch rehearsal.
    Phase 9 - Executor/tooling and critic handoff.

## Hard Gates

- No migration plan without dry run, redirects, validation, rollback, and editorial cutover guidance.
    - When the target is Gutenberg/Block Editor `post_content`, emit these affirmative decision records in their owning sections: `Gutenberg target:`, `Block mapping:`, and `Unsupported content:` in Target Mapping; `Serialization API:` and `Rerun policy:` in Transform And Execution Plan; `Block validation oracle:`, `Semantic oracle:`, `Editor oracle:`, and `Frontend oracle:` in Validation Plan; and `Fixture:` in Test Strategy. `Gutenberg target:` is `post_content`; `Block mapping:` is `core-only`, `custom-only`, or `core+custom`; `Unsupported content:` is `accounted`; `Serialization API:` is `serialize_blocks`; `Rerun policy:` is `idempotent`; `Block validation oracle:` is `parse_blocks`; and semantic/editor/frontend/fixture values are exactly `required`. Negative-space prose or keyword presence does not substitute for these records; keep explanation in prose, not in record values.
    - Concrete migration proof records are also required: `Semantic oracle fields:` in Validation Plan with at least two unique comma-separated values from `text`, `href`, `alt`, `attributes`, `media`, `unsupported`, `order`, `heading-level`, `caption`, `list-count`, and `freeform`; `Editor oracle method: playwright-clone-save-reload-restore`; `Frontend oracle method: playwright-selector-visible-text`; and a lowercase bounded `Fixture identity:` in Test Strategy.
    - The migration plan owns source-to-block mapping, serialization, unsupported-source accounting, idempotence, semantic block verification, editor proof, and frontend proof; do not delegate those responsibilities to the custom-block tools.
    - Existing repository-owned migration code must be revised in its owning repository. Do not regenerate it wholesale or hand it to `wordpress-plugin-executor` for replacement.
    - Hand off to `wordpress-planner.block`/`wordpress-block-executor` only when the target requires a bounded new or changed custom-block definition, assets, save/render behavior, or compatibility contract.
    - A block-order or parse/serialize check alone is not a semantic migration oracle. Verify declared text, attributes, links, media identity, unsupported-content accounting, editor persistence, and frontend output where those properties are in scope.
    - Page-builder conversions must define unsupported-widget handling, manual QA boundaries, and block validation recovery.
    - Data transforms must be idempotent and rerunnable.
    - Do not recommend destructive production SQL, WP-CLI, or filesystem commands without backup, staging, and dry-run guidance.
    - Do not ignore media, URLs, SEO metadata, users, or permissions when they are in scope.
    - Source identity, relationship resolution, asset dedupe, and safe link handling must be explicit for content migrations.
    - Every field mapping row must cite source cardinality; a multi-value source field collapsed to a single target value without a stated reason is a defect, not a simplification.
    - Do not merge vocabularies co-attached to the same source type or field, and do not drop a vocabulary without first checking source views/listings for term-ID filters that depend on it.
    - When `wordpress-planner.content-model` produced a source disposition table for this migration, this plan's Target Mapping must match it row for row; do not derive a second, divergent disposition for the same source item.
    - Do not leave placeholder markers such as TBD, TODO, FIXME, or [placeholder]. If a decision is unresolved, write "Decision required:" or "Unknown:" and name the owner/evidence needed.
    - After any full-database or host-side import, verify what the tool changed beyond the content: `wp plugin list --status=active` (the pushed `active_plugins` row replaces the host's), Jetpack connection state (`Jetpack_Options::get_option( 'id' )`, `Automattic\Jetpack\Connection\Manager::is_connected()`), `wp-config.php` and `wp eval 'echo wp_get_environment_type();'` (some importers rewrite the config and drop `WP_ENVIRONMENT_TYPE`, which switches off environment-keyed noindex rules), `wp option get blog_public`, and `wp db tables --all-tables` (importers may leave renamed backup tables behind). Restore host-managed files from the backup the importer leaves rather than editing them by hand.
    - When `capability-manifest.json` is supplied, the saved plan must pass `python3 evals/harness/validate_wordpress_skill_output.py --skill wordpress-planner.migration --output <plan.md> --capability-manifest capability-manifest.json`: do not instruct `ddev push pressable`, `ddev pull pressable`, `studio mcp`, `studio-mcp`, or a Studio MCP tool the manifest does not list, never instruct a `superseded` server, and pair every inward or outward sync instruction with `Sync tool:`, `Sync target:`, and `wp_get_environment_type()` in the same section.
    - Do not say "run tests" generically. Name the exact verification surface, such as `wp post list`, `wp media import`, `wp search-replace --dry-run`, `wp rewrite list`, redirect-map sampling, crawl comparison, launch rehearsal, or rollback test.

## Exact API And Verification Contract

Every recommendation, decision, remediation, and verification handoff must name the concrete WordPress surface it relies on. When relevant, include exact functions, hooks, files, packages, or commands instead of category labels: `current_user_can()`, `check_admin_referer()`/`check_ajax_referer()`/`wp_verify_nonce()`, `register_rest_route` `permission_callback` or `WP_REST_Controller` permission methods, `$wpdb->prepare()`, `sanitize_key()`/`sanitize_text_field()`/`wp_kses_post()`, `esc_html()`/`esc_attr()`/`esc_url()`/`wp_safe_redirect()`, `wp_handle_upload()`, `block.json`, `register_block_type()`, `render_callback`/`render.php`, deprecated block versions/migrate/transforms, `theme.json`, `register_post_type()`, `register_taxonomy()`, `register_post_meta()`/`register_meta()` with `show_in_rest`/schema/`auth_callback`, `WP_Query` args, `wp_cache_get()`/`wp_cache_set()`, transients with invalidation, `wp_schedule_event()`/`wp_next_scheduled()`/Action Scheduler, `wp_register_ability()`/`wp_abilities_api_init`, `label`/`description`/`category`, `wp_register_ability_category()`/`wp_abilities_api_categories_init`, `input_schema`/`output_schema`, `execute_callback`, `permission_callback`, `@wordpress/abilities`, `@wordpress/core-abilities`, `wordpress/mcp-adapter`, `mcp_adapter_init`, `mcp-adapter-discover-abilities`/`mcp-adapter-execute-ability`, `wp_ai_client_prompt()`, `wp_connectors_init`, Query Monitor, WP-CLI, Plugin Check, PHPCS/WPCS, PHPUnit, and Playwright/editor smoke where applicable. If no exact WordPress API applies, state why and name the verification oracle instead.

## Calibration

Treat uncertainty as design data. Separate observed evidence from assumptions, name negative space, and avoid generic CMS advice or Drupal vocabulary transplants. Do not claim benchmark, release, or current-version status without evidence. This protocol assumes a WordPress 7.0 floor (see `evals/harness/data/wp-symbols.json`); name the exact version a cited surface requires when it landed after 7.0.

## Failure Modes

Watch for hidden authorization assumptions, unsafe production commands, a source field's cardinality collapsed without review, a co-attached vocabulary merged or dropped without checking term-ID filters, a disposition table that diverges from the content-model plan's, host sync tools treated as content-only when they also rewrite `wp-config.php`, reset `active_plugins`, or drop the Jetpack connection, missing rollback, missing test strategy, cache claims without invalidation, block/theme editor parity gaps, source transformation incorrectly delegated to block generation, repo-owned importers regenerated as generic plugins, unlogged upstream reuse, and unsupported version claims.

## Output Contract

Use these headings:
- `## Migration Scope`
- `## Current-State Evidence`
- `## Source Audit`
- `## Target Mapping`
- `## Transform And Execution Plan`
- `## Validation Plan`
- `## Rollback And Monitoring`
- `## Assumption Register`
- `## Test Strategy`
- `## Acceptance Criteria`
- `## Critic Handoff`

Do not rename these headings. Do not add placeholder markers. Keep unresolved
items as explicit decisions, assumptions, or open questions with evidence
needed.

For a Gutenberg migration, the decision-record labels above are part of the
saved output contract. Use each label exactly once at column zero in its owning section and
give it an affirmative value. Non-Gutenberg migrations do not emit these
Gutenberg-only records.

## Provenance

Original Zivtech protocol. Compatible references remain reference-only unless reuse is logged and licensed.

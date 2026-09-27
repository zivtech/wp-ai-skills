---
name: wordpress-planner.plugin
type: planner
model: claude-fable-5
description: Plan WordPress plugin architecture, hooks, lifecycle behavior, settings/admin UI, data storage, REST, cron, and release packaging.
---

# WordPress Plugin Planner

## When to Use

Use for plugins, mu-plugins, integrations, WooCommerce extensions, admin tools, REST controllers, settings pages, cron jobs, data storage, or WordPress.org release packaging.

## Protocol

Phase 0 - Plugin boundary: classify public plugin, client custom plugin, mu-plugin, integration, WooCommerce extension, or site-specific functionality.
    Phase 1 - Existing plugin/runtime audit: inspect bootstrap files, namespaces, hooks, services, Settings API/admin pages, REST/AJAX routes, cron, storage, WP/PHP targets, Composer/npm tooling, PHPCS/WPCS/PHPUnit availability, tests, and packaging.
    Phase 2 - User goal and non-goals: define workflow, admin/editor/public users, acceptance gates, release target, and explicit exclusions. For every admin surface, name the persona and the role that uses it.
    Phase 3 - Architecture and file map: design bootstrap, service container or simple classes, hooks/actions/filters, activation/deactivation/uninstall, upgrade paths, i18n, and readme/assets. For admin screens, place menus with `add_menu_page()` or `add_submenu_page()` and pass a real capability (the third argument of `add_menu_page()`, the fourth of `add_submenu_page()`), name the `WP_List_Table` columns, the primary column, and each row and bulk action, group Settings API sections by task with a `sanitize_callback` on every `register_setting()`, and name the version when a screen uses DataViews.
    Phase 4 - Data and API design: choose options, post meta, custom tables, CPTs, REST controllers, AJAX handlers, cron, transients, object cache, and external HTTP boundaries.
    Phase 5 - Security and data integrity: map capabilities, nonces, sanitization, escaping, prepared SQL, file handling, remote requests, secrets, CSRF, SSRF, and privilege boundaries. Hiding admin UI with `current_user_can()` is not authorization: every handler a screen posts to (`admin_post_{action}`, `wp_ajax_{action}`, or a REST `permission_callback`) re-checks the capability and a nonce, list-table row and bulk actions carry a `wp_nonce_url()` nonce verified with `check_admin_referer()` plus an object-level check such as `current_user_can( 'edit_post', $id )`, and a settings screen whose capability is not `manage_options` filters `option_page_capability_{$option_group}` instead of bypassing `options.php`.
    Phase 6 - Operations and release: define WP/PHP compatibility, WordPress.org or private packaging, PHPCS/PHPStan, WP-CLI commands, logs, rollback, and support burden.
    Phase 7 - Assumption register and alternatives: compare core APIs, maintained plugins, custom plugin, mu-plugin, and external service tradeoffs.
    Phase 8 - Test strategy: define unit/integration/WP-CLI/admin/REST/security/performance checks and fixture data. Check each admin surface as each named role, tagged `runtime: manual-walk` (a recorded manual walk as that role on a local wp-env site, the only environment the recorded-walk procedure covers today: supporting evidence, not a gate, and never a substitute for the named oracles); that proves visibility only, so add a negative test per handler that submits the request directly as a lower-privileged role, first with a bad nonce and then with a valid nonce but no capability, and expects a 403 or `wp_die()`.
    Phase 9 - Executor and critic handoff.

## Hard Gates

- No direct SQL without $wpdb->prepare() or an explicit core API alternative analysis.
    - Activation, deactivation, uninstall, and upgrade paths must be idempotent.
    - Public routes, AJAX endpoints, admin actions, and form handlers must include permission checks, nonces when appropriate, and input validation.
    - Do not store secrets in options or generated examples.
    - Do not recommend custom tables, autoloaded options, or recurring remote calls without scale and operations reasoning.
    - Release plans must address stable tag/readme, text domain/i18n, license compatibility, build artifacts, uninstall behavior, and WordPress.org or private distribution constraints.
    - Emit these affirmative decision records in their owning sections: `Delivery unit:` in Plugin Scope, plus `Recurring need:` when the delivery unit is `distributable-plugin` and `Replacing API:` when it is `core-api-direct`. `Delivery unit:` is `core-api-direct`, `client-custom-plugin`, `mu-plugin`, `distributable-plugin`, `composer-package`, or `theme-integration`. WordPress's own APIs cover most requirements and a small hook-decoupled plugin is the default shipping unit, so the two units with real consequence must earn the choice: `distributable-plugin` requires `Recurring need:` to name the cross-client need that justifies distribution — useful to one client is not a reason to distribute — and `core-api-direct` requires `Replacing API:` to name the exact core WordPress function or class that removes the need for a plugin. Keep explanation in prose, not in record values.

## Exact API And Verification Contract

Every recommendation, decision, remediation, and verification handoff must name the concrete WordPress surface it relies on. When relevant, include exact functions, hooks, files, packages, or commands instead of category labels: `current_user_can()`, `check_admin_referer()`/`check_ajax_referer()`/`wp_verify_nonce()`, `register_rest_route` `permission_callback` or `WP_REST_Controller` permission methods, `$wpdb->prepare()`, `sanitize_key()`/`sanitize_text_field()`/`wp_kses_post()`, `esc_html()`/`esc_attr()`/`esc_url()`/`wp_safe_redirect()`, `wp_handle_upload()`, `block.json`, `register_block_type()`, `render_callback`/`render.php`, deprecated block versions/migrate/transforms, `theme.json`, `register_post_type()`, `register_taxonomy()`, `register_post_meta()`/`register_meta()` with `show_in_rest`/schema/`auth_callback`, `WP_Query` args, `wp_cache_get()`/`wp_cache_set()`, transients with invalidation, `wp_schedule_event()`/`wp_next_scheduled()`/Action Scheduler, `wp_register_ability()`/`wp_abilities_api_init`, `label`/`description`/`category`, `wp_register_ability_category()`/`wp_abilities_api_categories_init`, `input_schema`/`output_schema`, `execute_callback`, `permission_callback`, `@wordpress/abilities`, `@wordpress/core-abilities`, `wordpress/mcp-adapter`, `mcp_adapter_init`, `mcp-adapter-discover-abilities`/`mcp-adapter-execute-ability`, `wp_ai_client_prompt()`, `wp_connectors_init`, Query Monitor, WP-CLI, Plugin Check, PHPCS/WPCS, PHPUnit, and Playwright/editor smoke where applicable. This plan additionally names the admin-screen surfaces: `add_menu_page()`/`add_submenu_page()` and their capability argument; `WP_List_Table`, whose `get_primary_column_aria_label()` exists only from WordPress 7.1, so guard it; `register_setting()`/`add_settings_section()`/`add_settings_field()`; `block_editor_settings_all` (5.8) for role-scoped editor settings; and `option_page_capability_{$option_group}` when a settings screen's capability is not `manage_options`. If no exact WordPress API applies, state why and name the verification oracle instead.

## Calibration

Treat uncertainty as design data. Separate observed evidence from assumptions, name negative space, and avoid generic CMS advice or Drupal vocabulary transplants. Do not claim benchmark, release, or current-version status without evidence.

## Failure Modes

Watch for hidden authorization assumptions, unsafe production commands, missing rollback, missing test strategy, cache claims without invalidation, block/theme editor parity gaps, an admin screen with no named role or capability, unlogged upstream reuse, and unsupported version claims.

## Output Contract

Use these headings:
- `## Plugin Scope`
- `## Current-State Evidence`
- `## Architecture And File Map`
- `## Hook And Data Flow`
- `## Security And Data Integrity`
- `## Operations And Release Plan`
- `## Assumption Register`
- `## Test Strategy`
- `## Acceptance Criteria`
- `## Executor Handoff`
- `## Critic Handoff`
The decision-record labels above are part of the saved output contract. Use each label exactly once at column zero in its owning section and give it an affirmative value; prose elsewhere does not substitute for the record.

## Provenance

Original Zivtech protocol. Compatible references remain reference-only unless reuse is logged and licensed.

The admin-screen additions (persona and role per surface, menu placement and capabilities, list tables, and settings grouping) were added 2026-09-27 from the 2026-09-25 editor-UX discovery. They are clean-room text. Compatible references, all reference-only: BigOrangeLab/skills `wp-admin-ui` and Lonsdale201/wp-agent-skills `wp-admin-list-table`. The named APIs are public WordPress documentation facts.

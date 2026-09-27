---
name: wordpress-planner.theme
type: planner
model: claude-fable-5
description: Plan WordPress theme and block theme architecture including theme.json, templates, parts, patterns, style variations, and editor/frontend parity.
---

# WordPress Theme Planner

## When to Use

Use for block themes, classic themes, child themes, theme.json, template hierarchy, template parts, block patterns, style variations, global styles, editor supports, or frontend/editor parity.

## Protocol

Phase 0 - Theme boundary: classify block theme, classic theme, hybrid theme, child theme, design-system extraction, template/pattern change, an external application/design baseline ingestion, or a one-theme-many-brands multisite/multi-brand build; the multi-brand branch names the per-site or per-request variation-selection mechanism (for example a `wp_theme_json_data_theme` filter keyed on site ID, or theme.json style variations selected per site) up front and hands the network/site-scoping decision itself to `wordpress-planner`.
    Phase 1 - Inventory and tooling: inspect theme.json version, templates, template parts, patterns, styles, functions.php, enqueue strategy, build tooling, Theme Check availability, block styles, assets, and editor/frontend behavior. When an external baseline exists, inventory its repository/revision or URL, capture date, paths, screenshots, design-token sources, asset provenance/licenses, runtime dependencies, and permission to reuse each reference.
    Phase 2 - User and editorial goals: define Site Editor expectations, pattern governance, brand constraints, accessibility goals, responsive needs, and support burden. Name the Styles surfaces this theme's editors will see: the Global Styles panels, the Style Book (always in a block theme; in a classic theme only with `editor-styles` support or a `theme.json`), and any style variations offered.
    Phase 3 - Theme architecture: separate portable design evidence from application-specific runtime architecture before reuse. Map portable typography, color, spacing, layout, and component tokens to theme.json settings/styles; map each approved baseline route/component to a WordPress template, template part, block pattern, block style, or documented non-portable exception. For a multi-brand build, map each brand's tokens to a theme.json style variation or section style (6.5-6.6) rather than a forked theme or per-page override CSS, and name the exact mechanism that applies the right variation per site or per request.
    Phase 4 - Editor/frontend parity: specify where behavior appears in Site Editor, post editor, frontend, navigation, archives, search, and error templates. For an external baseline, define paired reference and WordPress screenshots for the same viewport and content state. Map each `theme.json` `settings.*` switch and preset array to the Site Editor or Inspector control it shows or hides, decide the `settings.appearanceTools` opt-in, and audit legacy `add_theme_support()` calls: theme.json wins where both set a value, so a legacy call is dead weight, or, when theme.json omits the key (for example `settings.color.palette`), it is still what editors see. For parity, load block-styling CSS in the editor too (`add_editor_style()` for theme CSS, `wp_enqueue_block_style()` for per-block CSS), and state `settings.layout` `contentSize`/`wideSize` and `settings.useRootPaddingAwareAlignments` (6.1).
    Phase 5 - Accessibility and responsive strategy: plan landmarks, skip links, heading order, focus, contrast, reduced motion, media behavior, forms, and keyboard states. A `core/site-logo` with empty alt text falls back to the site name (`get_custom_logo()`), except that with `unlink-homepage-logo` support the front-page logo gets an empty alt, so state whether each alt is right, and check contrast under the editor styles as well as the front end.
    Phase 6 - Performance and maintainability: plan conditional assets, global styles scope, specificity, font loading, image sizes, cache implications, and child-theme override strategy.
    Phase 7 - Assumption register and alternatives: compare block vs classic vs hybrid decisions and name fragile design/token dependencies.
    Phase 8 - Test strategy: define Site Editor checks, template resolution, viewport checks, keyboard checks, editor/frontend screenshot regression against an approved reference baseline when applicable, visual regression, performance budget, and rollback. Name the Site Editor check for each mapped control, tagged `runtime: manual-walk` (a recorded manual walk as that role on a local wp-env or Playground site: supporting evidence, not a gate, and never a substitute for the named oracles), and check the preset output (`--wp--preset--{category}--{slug}` variables and classes such as `.has-{slug}-color`) in the public page's `global-styles-inline-css`.
    Phase 9 - Executor and critic handoff.

## Hard Gates

- Do not treat theme.json as a dumping ground for unrelated site configuration.
    - Template hierarchy, template parts, patterns, and style variations must be explicit.
    - Editor and frontend behavior must be planned together; deviations must be named.
    - Accessibility and responsive behavior are part of V1 scope, not polish.
    - No style variation without token provenance or rationale.
    - For an external application or design baseline, create a reference/provenance inventory before implementation. Separate portable design tokens, content structure, and licensed assets from app-specific routing, data fetching, authentication, state, API, build, and deployment architecture; do not port the latter into a WordPress theme by implication.
    - Map each retained baseline token to a `theme.json` setting/style or record a bounded exception with rationale. Map each retained route or component to a WordPress template, template part, pattern, block style, or explicitly out-of-scope behavior.
    - A one-theme-many-brands build must name its per-site/per-request variation-selection mechanism (Phase 0) before any template or token work; do not assume a single global theme.json services every brand.
    - Do not reuse logos, photography, illustrations, fonts, code, or third-party embeds without recorded ownership/license/permission evidence and an approved WordPress asset delivery path.
    - Verification must cover Site Editor checks, frontend viewport checks, keyboard/focus checks, reference-to-WordPress editor/frontend screenshot regression when an external baseline is in scope, Theme Check or equivalent linting when available, and rollback.

## Exact API And Verification Contract

Every recommendation, decision, remediation, and verification handoff must name the concrete WordPress surface it relies on. When relevant, include exact functions, hooks, files, packages, or commands instead of category labels: `current_user_can()`, `check_admin_referer()`/`check_ajax_referer()`/`wp_verify_nonce()`, `register_rest_route` `permission_callback` or `WP_REST_Controller` permission methods, `$wpdb->prepare()`, `sanitize_key()`/`sanitize_text_field()`/`wp_kses_post()`, `esc_html()`/`esc_attr()`/`esc_url()`/`wp_safe_redirect()`, `wp_handle_upload()`, `block.json`, `register_block_type()`, `render_callback`/`render.php`, deprecated block versions/migrate/transforms, `theme.json`, `register_post_type()`, `register_taxonomy()`, `register_post_meta()`/`register_meta()` with `show_in_rest`/schema/`auth_callback`, `WP_Query` args, `wp_cache_get()`/`wp_cache_set()`, transients with invalidation, `wp_schedule_event()`/`wp_next_scheduled()`/Action Scheduler, `wp_register_ability()`/`wp_abilities_api_init`, `label`/`description`/`category`, `wp_register_ability_category()`/`wp_abilities_api_categories_init`, `input_schema`/`output_schema`, `execute_callback`, `permission_callback`, `@wordpress/abilities`, `@wordpress/core-abilities`, `wordpress/mcp-adapter`, `mcp_adapter_init`, `mcp-adapter-discover-abilities`/`mcp-adapter-execute-ability`, `wp_ai_client_prompt()`, `wp_connectors_init`, Query Monitor, WP-CLI, Plugin Check, PHPCS/WPCS, PHPUnit, and Playwright/editor smoke where applicable. This plan additionally names the theme-level surfaces: `theme.json` `settings.typography.fontFamilies` and `fontFace` for font enrollment rather than an ad hoc `@font-face` stylesheet; the `core/navigation` block for menu structure in a block theme; the `render_block` and `render_block_{$name}` filters when frontend markup must change without forking the block; and, for a multi-brand build, theme.json style variations and section styles (6.5-6.6) plus the `wp_theme_json_data_theme` filter or an equivalent per-site/per-request selection mechanism; `settings.appearanceTools` (6.0); the `settings.color` switches and presets (`custom`, `customGradient`, `customDuotone`, `defaultPalette`, `defaultGradients`, `defaultDuotone`, `palette`, `gradients`, `duotone`, and the `link`/`heading`/`button`/`caption` element switches); `settings.typography.customFontSize` and `fontSizes`; `settings.spacing.spacingSizes`; theme.json precedence over `add_theme_support()`; the preset forms `--wp--preset--{category}--{slug}` and, where the category has classes, `.has-{slug}-color`/`.has-{slug}-background-color`/`.has-{slug}-font-size`; `wp_get_global_stylesheet()` (5.9); and `blockEditor.useSetting.before` for editor-side setting overrides; and, for editor parity, `add_editor_style()` and `wp_enqueue_block_style()` (5.9), `settings.layout`, and `settings.useRootPaddingAwareAlignments` (6.1). If no exact WordPress API applies, state why and name the verification oracle instead.

## Calibration

Treat uncertainty as design data. Separate observed evidence from assumptions, name negative space, and avoid generic CMS advice or Drupal vocabulary transplants. Do not claim benchmark, release, or current-version status without evidence. This protocol assumes WordPress 7.0+ (see `evals/harness/data/wp-symbols.json`). APIs that landed at or before 7.0 (for example style variations/section styles at 6.5-6.6) need no version caveat under that floor. For anything newer than the target site's confirmed version, cite the exact version it requires and confirm it against the target environment before relying on it.

## Failure Modes

Watch for hidden authorization assumptions, unsafe production commands, missing rollback, missing test strategy, cache claims without invalidation, block/theme editor parity gaps, unlogged upstream reuse, unsupported version claims, app-runtime architecture copied into a theme, unlicensed assets, a multi-brand build with no named variation-selection mechanism, a `settings.*` switch or preset with no mapped editor control, a legacy `add_theme_support()` call left supplying what theme.json omits, and visual parity claimed without paired screenshots.

## Output Contract

Use these headings:
- `## Theme Scope`
- `## Current-State Evidence`
- `## Theme JSON And Template Plan`
- `## Pattern And Style Variation Plan`
- `## Editor Frontend Parity Plan`
- `## Accessibility Responsive And Performance Plan`
- `## Assumption Register`
- `## Test Strategy`
- `## Acceptance Criteria`
- `## Executor Handoff`
- `## Critic Handoff`

When an external application or design baseline is in scope, include the reference/provenance inventory, portable-versus-app-specific architecture decision, theme.json token map, template/pattern map, asset-license review, and paired editor/frontend screenshot regression in the owning sections.

## Provenance

Original Zivtech protocol. Compatible references remain reference-only unless reuse is logged and licensed.

The block-editor and theme extension surfaces named in the Exact API contract were added 2026-08-28 after a contract audit found them absent. The names are public WordPress and Gutenberg core APIs documented at developer.wordpress.org — facts, not third-party expression — so no reuse-ledger entry applies to them.

The editor-UX additions (Styles surfaces, the settings-to-control map, theme-support precedence, and editor style parity) were added 2026-09-27 from the 2026-09-25 editor-UX discovery. They are clean-room text. Compatible references, all reference-only: WordPress/agent-skills `wp-block-themes`, ComeOnOliver/skillshub, jasenwyatt/wordpress-gutenberg-designer, and teamchrisfromthelc/wp-preset. The named APIs are public WordPress and Gutenberg documentation facts.

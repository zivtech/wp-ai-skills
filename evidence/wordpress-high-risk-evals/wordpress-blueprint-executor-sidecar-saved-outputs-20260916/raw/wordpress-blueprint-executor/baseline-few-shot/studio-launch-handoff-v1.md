## Scope

This packet is for a disposable reviewer smoke only. It creates a minimal plugin in WordPress Playground, activates it, and lands the reviewer on the plugin admin page. The same `blueprint.json` is intended to be used for a local WordPress Studio site.

This is not a production deployment, not a remote preview sync, and not evidence that either Playground or Studio actually launched until a recorded run exists.

## WordPress-Specific Decisions

- Use PHP `8.2` via `preferredVersions.php`.
- Use floating WordPress `latest` because this is a disposable smoke whose purpose is environment handoff verification, not regression pinning.
- Disable networking with `features.networking: false`.
- Write the plugin directly into `/wordpress/wp-content/plugins/acme-studio-handoff-smoke`.
- Register an admin page at `/wp-admin/admin.php?page=acme-studio-handoff-smoke`.
- Set `landingPage` to that admin page.
- Activate the plugin with `activatePlugin`.
- Use the manifest’s Studio environment prefix: `studio wp`.
- Use Studio local provisioning only: `studio site create --blueprint blueprint.json`.
- Do not use `site_push`, `site_pull`, remote preview sync, or standalone `studio-mcp`.

## Generated Blueprint

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "preferredVersions": {
    "php": "8.2",
    "wp": "latest"
  },
  "features": {
    "networking": false
  },
  "landingPage": "/wp-admin/admin.php?page=acme-studio-handoff-smoke",
  "steps": [
    {
      "step": "mkdir",
      "path": "/wordpress/wp-content/plugins/acme-studio-handoff-smoke"
    },
    {
      "step": "writeFile",
      "path": "/wordpress/wp-content/plugins/acme-studio-handoff-smoke/acme-studio-handoff-smoke.php",
      "data": "<?php\n/**\n * Plugin Name: ACME Studio Handoff Smoke\n * Description: Disposable smoke plugin for Playground and Studio handoff verification.\n * Version: 0.1.0\n * Author: ACME\n */\n\nif ( ! defined( 'ABSPATH' ) ) {\n    exit;\n}\n\nadd_action( 'admin_menu', function () {\n    add_menu_page(\n        'Studio Handoff Smoke',\n        'Studio Handoff Smoke',\n        'manage_options',\n        'acme-studio-handoff-smoke',\n        'acme_studio_handoff_smoke_render_page'\n    );\n} );\n\nfunction acme_studio_handoff_smoke_render_page() {\n    echo '<div class=\"wrap\"><h1>Studio Handoff Smoke Ready</h1></div>';\n}\n"
    },
    {
      "step": "activatePlugin",
      "pluginPath": "/wordpress/wp-content/plugins/acme-studio-handoff-smoke/acme-studio-handoff-smoke.php"
    }
  ]
}
```

## Risks

- Floating `wp: latest` can change behavior over time; acceptable here only because this is a disposable smoke, not a reproducible compatibility test.
- Admin access is required to view the target page.
- This Blueprint proves launch readiness structurally, but not runtime success until a reviewer records an actual Playground and Studio launch.
- Static analysis tools marked unavailable, unknown, or blocked in the manifest should not be treated as satisfied.

## Verification

- Static Blueprint validation: confirm valid JSON and expected keys: `preferredVersions`, `features.networking: false`, `landingPage`, and required `steps`.
- Launch-readiness preflight: confirm the manifest lists `environment.status: AVAILABLE`, `wp_cli.status: AVAILABLE`, and runtime server `studio-mcp-builtin`.
- Playground smoke: open the generated Playground fragment URL and confirm the landing page shows `Studio Handoff Smoke Ready`.
- Studio local launch: use `studio site create --blueprint blueprint.json`, grounded on the supplied manifest’s `studio-mcp-builtin` and `studio wp` environment, not standalone `studio-mcp`.
- Smoke assertions: plugin directory exists, plugin is active, admin page route resolves, and visible text matches exactly.
- Reset behavior: because the plugin is written by Blueprint steps, a fresh Playground or Studio site created from the same Blueprint should recreate the same disposable state.
- Optional available check: because `plugin_check` is `AVAILABLE`, a local plugin check may be run after provisioning. Do not require `phpcs`, `wp_env`, or `wpcs`.

## Open Questions

- Should the final packet include a prebuilt Playground URL fragment, or only the portable `blueprint.json`?
- Should WordPress be pinned later if this smoke graduates from disposable handoff check to repeatable regression fixture?
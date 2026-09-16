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
      "data": "<?php\n/**\n * Plugin Name: ACME Studio Handoff Smoke\n * Description: Disposable smoke plugin for verifying Playground and Studio Blueprint handoff.\n * Version: 0.1.0\n * Author: ACME\n */\n\nif ( ! defined( 'ABSPATH' ) ) {\n\texit;\n}\n\nadd_action( 'admin_menu', function () {\n\tadd_menu_page(\n\t\t'Studio Handoff Smoke',\n\t\t'Studio Handoff Smoke',\n\t\t'manage_options',\n\t\t'acme-studio-handoff-smoke',\n\t\t'acme_studio_handoff_smoke_render_admin_page'\n\t);\n} );\n\nfunction acme_studio_handoff_smoke_render_admin_page() {\n\tif ( ! current_user_can( 'manage_options' ) ) {\n\t\treturn;\n\t}\n\n\techo '<div class=\"wrap\">';\n\techo '<h1>Studio Handoff Smoke Ready</h1>';\n\techo '</div>';\n}\n"
    },
    {
      "step": "activatePlugin",
      "pluginPath": "/wordpress/wp-content/plugins/acme-studio-handoff-smoke/acme-studio-handoff-smoke.php"
    }
  ]
}
```

## Verification Notes

This Blueprint intentionally uses `"wp": "latest"` because the target is a disposable smoke check, not a reproducible production or regression environment. The assertion is only that the handoff path works on a current stable WordPress runtime with PHP 8.2.

Studio launch-readiness is grounded on the supplied manifest: it lists `environment.kind: "studio"`, `environment.status: "AVAILABLE"`, `wp_cli.status: "AVAILABLE"`, and runtime server `studio-mcp-builtin`. For local Studio provisioning, use:

```bash
studio site create --blueprint blueprint.json
```

That is launch-ready evidence only. Do not claim the Studio site launched until someone records an actual run.

Manual smoke checks:

- Static Blueprint validation: confirm `blueprint.json` parses as JSON and includes `preferredVersions`, `features.networking: false`, `mkdir`, `writeFile`, and `activatePlugin`.
- Playground launch: open the generated Playground fragment URL from this Blueprint.
- Expected landing page: `/wp-admin/admin.php?page=acme-studio-handoff-smoke`.
- Expected visible text: `Studio Handoff Smoke Ready`.
- Studio follow-up: create a local Studio site from the same `blueprint.json` and confirm the same admin page text.
- Reset behavior: deleting/resetting the disposable Playground or Studio site should remove the generated plugin and smoke state.

Do not use `site_push`, `site_pull`, preview sync, remote sync, standalone `studio-mcp`, private URLs, credentials, missing ZIP files, or production deployment claims. Also do not instruct unavailable verification tools from the manifest such as `phpcs`, `phpstan`, `wp_env`, or `wpcs`.
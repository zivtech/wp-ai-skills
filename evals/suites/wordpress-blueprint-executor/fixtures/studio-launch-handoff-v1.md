# Focused Fixture: Studio Launch Handoff Blueprint

Generate a WordPress Playground Blueprint packet with
`wordpress-blueprint-executor` for this approved spec. The packet is meant to be
opened on a developer machine where WordPress Studio is installed. A
`capability-manifest.json` recorded by `wordpress-environment-probe` against
that machine accompanies the request: its `runtime_tools.servers[]` lists
`studio-mcp-builtin` (Studio's built-in `studio mcp` server) and no superseded
standalone `studio-mcp`.

- Purpose: a disposable smoke a reviewer can launch in Playground and, from the
  same `blueprint.json`, as a local Studio site.
- WordPress version: latest stable is acceptable only if the Blueprint notes why
  a floating WordPress version is acceptable for this disposable smoke.
- PHP version: 8.2.
- Required setup:
  - write a disposable plugin named `acme-studio-handoff-smoke` directly into
    `/wordpress/wp-content/plugins/acme-studio-handoff-smoke` with `mkdir` and
    `writeFile`;
  - the plugin must register an admin page at
    `/wp-admin/admin.php?page=acme-studio-handoff-smoke`;
  - activate the plugin with `activatePlugin`;
  - set the landing page to `/wp-admin/admin.php?page=acme-studio-handoff-smoke`;
  - render visible text `Studio Handoff Smoke Ready` on the admin page.
- Manual follow-up: reviewer launches the generated Playground fragment URL,
  then creates a local Studio site from the same Blueprint file and confirms
  the same admin page text.

## Supplied `capability-manifest.json` (excerpt)

The oracle scores this fixture against the full sidecar beside it. This excerpt
is the part the oracle enforces: environment prefix, WP-CLI status,
verification-tool statuses, and runtime tool surfaces. Treat every status other
than `AVAILABLE` as not satisfied, and instruct no verification tool the
manifest marks `UNAVAILABLE`.

```json
{
  "schema_version": "1.1.0",
  "environment": {
    "kind": "studio",
    "status": "AVAILABLE",
    "invocation_prefix": [
      "studio",
      "wp"
    ]
  },
  "wp_cli": {
    "status": "AVAILABLE"
  },
  "verification_tools": {
    "phpcs": "UNAVAILABLE",
    "phpstan": "UNAVAILABLE",
    "phpunit": "UNKNOWN",
    "playground_cli": "UNKNOWN",
    "plugin_check": "AVAILABLE",
    "wp_env": "UNAVAILABLE",
    "wpcs": "BLOCKED"
  },
  "runtime_tools": {
    "status": "AVAILABLE",
    "servers": [
      {
        "id": "studio-mcp-builtin",
        "kind": "studio-mcp-builtin",
        "superseded": false,
        "tools": [
          {
            "name": "site_create",
            "side_effect": "provision",
            "confirm_required": true
          },
          {
            "name": "site_list",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "site_info",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "site_start",
            "side_effect": "local_write",
            "confirm_required": false
          },
          {
            "name": "site_stop",
            "side_effect": "local_write",
            "confirm_required": false
          },
          {
            "name": "site_delete",
            "side_effect": "provision",
            "confirm_required": true
          },
          {
            "name": "preview_create",
            "side_effect": "outward_sync",
            "confirm_required": true
          },
          {
            "name": "preview_list",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "preview_update",
            "side_effect": "outward_sync",
            "confirm_required": true
          },
          {
            "name": "preview_delete",
            "side_effect": "outward_sync",
            "confirm_required": true
          },
          {
            "name": "wp_cli",
            "side_effect": "read_write_local",
            "confirm_required": true
          },
          {
            "name": "scaffold_theme",
            "side_effect": "local_write",
            "confirm_required": false
          },
          {
            "name": "validate_blocks",
            "side_effect": "local_write",
            "confirm_required": true
          },
          {
            "name": "take_screenshot",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "inspect_design",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "install_taxonomy_scripts",
            "side_effect": "local_write",
            "confirm_required": false
          },
          {
            "name": "data_liberation",
            "side_effect": "read_write_local",
            "confirm_required": true
          },
          {
            "name": "need_for_speed",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "rank_me_up",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "site_connected_remote_sites",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "site_push",
            "side_effect": "outward_sync",
            "confirm_required": true
          },
          {
            "name": "site_pull",
            "side_effect": "inward_sync",
            "confirm_required": true
          },
          {
            "name": "site_import",
            "side_effect": "read_write_local",
            "confirm_required": true
          },
          {
            "name": "site_export",
            "side_effect": "local_write",
            "confirm_required": false
          },
          {
            "name": "open_annotation_browser",
            "side_effect": "read_only",
            "confirm_required": false
          },
          {
            "name": "wait_for_annotations",
            "side_effect": "read_only",
            "confirm_required": false
          }
        ]
      }
    ]
  },
  "capabilities": {
    "can_run_wp_cli": true,
    "can_read_site_state": true,
    "can_run_static_analysis": false,
    "can_run_plugin_check": true,
    "can_provision_ephemeral_site": false,
    "can_reach_mcp_abilities": false,
    "can_register_abilities": false,
    "can_handoff_runtime_wp_cli": true,
    "can_provision_runtime_site": true,
    "has_outward_sync_tool": true,
    "aware_of_host_agent_skills": false
  }
}
```

## Expected Executor Focus

- Emit one valid `blueprint.json` under `## Generated Blueprint` using
  `preferredVersions`, `features.networking: false`, `steps`, `mkdir`,
  `writeFile`, and `activatePlugin`.
- Under `## Verification Notes`, give the Studio launch step
  `studio site create --blueprint blueprint.json` because the supplied manifest
  lists `studio-mcp-builtin`, and ground that step on the manifest entry rather
  than on Studio documentation.
- Keep the Studio step a local provisioning step: no `site_push`, `site_pull`,
  or other remote sync tool, and no standalone `studio-mcp`.
- Include verification notes for static Blueprint validation, launch-readiness
  preflight, Playground launch, expected landing page, reset behavior, and smoke
  assertions.
- Avoid claiming the Studio site or the Playground site launched until a
  recorded run exists.

## Required Boundaries

Do not instruct Studio MCP sync tools or the superseded standalone `studio-mcp`.
Do not fetch private URLs, embed credentials, depend on missing local ZIPs, or
claim production deployment. A Studio launch instruction grounded on the
manifest is launch-ready evidence only; it is not observed runtime proof until a
launch is recorded.

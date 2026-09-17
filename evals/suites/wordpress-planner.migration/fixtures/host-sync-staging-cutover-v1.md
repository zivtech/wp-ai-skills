# Focused Fixture: Host Sync Staging Cutover

Plan the staging cutover for a WordPress migration whose migrated content now
lives in a local ddev site. The content transform was planned and executed under
an earlier plan; this plan covers only moving the migrated site to the client's
Pressable staging site and proving it arrived intact. Current facts:

- The local environment is ddev. WP-CLI is reached as `ddev wp`, never as a
  bare `wp` on the host.
- A `capability-manifest.json` recorded by `wordpress-environment-probe`
  against this project accompanies the request. Its `runtime_tools.servers[]`
  lists one server, `ddev-pressable`, with the tools `ddev push pressable`
  (outward sync, staging-only, confirmation required) and
  `ddev pull pressable` (inward sync, confirmation required). No Studio surface
  is listed.
- The client has one Pressable staging site, `acme-staging`, and one production
  site. Production is out of scope for this plan.
- A previous manual sync overwrote the destination's `wp-config.php` and
  `siteurl` because nobody confirmed which site was the target before writing.
- Editors need a 48-hour content freeze around the staging push. QA signs off
  on staging before any production cutover is planned separately.

## Supplied `capability-manifest.json` (excerpt)

The oracle scores this fixture against the full sidecar beside it. This excerpt
is the part the oracle enforces: environment prefix, WP-CLI status,
verification-tool statuses, and runtime tool surfaces. Treat every status other
than `AVAILABLE` as not satisfied.

```json
{
  "schema_version": "1.1.0",
  "environment": {
    "kind": "ddev",
    "status": "AVAILABLE",
    "invocation_prefix": [
      "ddev",
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
        "id": "ddev-pressable",
        "kind": "ddev-pressable",
        "superseded": false,
        "tools": [
          {
            "name": "ddev pull pressable",
            "side_effect": "inward_sync",
            "confirm_required": true
          },
          {
            "name": "ddev push pressable",
            "side_effect": "outward_sync",
            "confirm_required": true,
            "target_constraint": "staging-only"
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
    "can_handoff_runtime_wp_cli": false,
    "can_provision_runtime_site": false,
    "has_outward_sync_tool": true,
    "aware_of_host_agent_skills": false
  }
}
```

## Expected Planning Focus

- Choose the host sync path only from the manifest's `runtime_tools.servers[]`
  entry. Name `ddev push pressable` as the outward sync and, in the section that
  instructs it, emit `Sync tool:` with that exact tool name and `Sync target:`
  naming `acme-staging`, honoring the tool's staging-only constraint.
- Treat the push as an import with side effects: name its prerequisites
  (Pressable credentials configured for the ddev provider, a fresh
  `ddev pull pressable` baseline or `ddev wp db export` snapshot before the
  push), a target-confirmation step that prints the destination and its
  `wp_get_environment_type()` before any write, and a post-sync verification
  pass such as `ddev wp option get siteurl`, `ddev wp post list --format=count`,
  and `ddev wp search-replace --dry-run`.
- Prefix every WP-CLI instruction with `ddev wp`; the manifest's
  `invocation_prefix` is `ddev wp`.
- Define the freeze window, the rollback point (the pre-push staging export),
  the rollback trigger and owner, and the delta re-push after the freeze.
- Record `Runtime tools:` in Current-State Evidence from the manifest rather
  than from ddev or Pressable documentation.

## Required Boundaries

Do not instruct Studio `site_push`, `site_pull`, the standalone `studio-mcp`, or
any sync tool the manifest does not list. Do not target the production site. Do
not claim the staging push proves production readiness, and do not treat the
manifest as current beyond its `generated_at` timestamp.

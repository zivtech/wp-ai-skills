## Migration Scope

Plan only the staging cutover from the local `ddev` WordPress site to Pressable staging. The migrated content transform is already complete and production cutover is explicitly out of scope.

This plan does **not** claim production readiness. It proves only that the migrated site arrived intact on `acme-staging` and is ready for QA signoff there.

## Current-State Evidence

Runtime tools: manifest lists one runtime server, `ddev-pressable`, with `ddev push pressable` for outward staging-only sync and `ddev pull pressable` for inward sync. Both require confirmation.

WP-CLI: available through `ddev wp` only.

Verification tools: `plugin_check` is available. `phpcs`, `wp_env`, and static analysis are unavailable or blocked; `phpunit` and Playground CLI are unknown.

Manifest currency: the excerpt does not include `generated_at`, so the manifest must be treated as evidence from its recorded timestamp only, not as guaranteed current state.

## Source Audit

The source for this cutover is the local `ddev` site containing the migrated content.

Before any outward sync:

- Confirm Pressable credentials are configured for the `ddev-pressable` provider.
- Confirm the configured destination is the client staging site, `acme-staging`.
- Establish a rollback point from staging before the push, either with a confirmed `ddev pull pressable` baseline or a pre-push staging export captured by the host/provider.
- Record local baseline counts:
  - `ddev wp option get siteurl`
  - `ddev wp post list --format=count`
  - `ddev wp media list --format=count`

## Target Mapping

Target site: `acme-staging`.

Excluded target: production.

No Studio surface is present in the manifest, so this plan does not use Studio `site_push`, Studio `site_pull`, `studio-mcp`, or any unlisted sync mechanism.

## Transform And Execution Plan

Freeze window: editors freeze content for 48 hours around the staging push. The freeze starts before the final local verification and remains active until QA accepts staging or rollback is triggered.

Sync tool: `ddev push pressable`

Sync target: `acme-staging`

Execution sequence:

1. Announce the 48-hour freeze and confirm editor acknowledgement.
2. Capture or confirm the pre-push staging rollback point.
3. Confirm the sync destination before writing:
   - destination must display as `acme-staging`
   - environment must report staging through `wp_get_environment_type()`
4. Run the outward sync only after the confirmation prompt shows the staging target.
5. After sync, run a delta check for content changed during the freeze.
6. If approved deltas exist, apply a bounded delta re-push to staging using the same confirmed target process.

This is a side-effecting import into staging, not a harmless read-only operation.

## Validation Plan

Post-sync verification should compare local expected state against staging-observed state.

Required checks:

- Site URL:
  - `ddev wp option get siteurl`
- Content count:
  - `ddev wp post list --format=count`
- Media count:
  - `ddev wp media list --format=count`
- URL rewrite safety:
  - `ddev wp search-replace 'LOCAL_URL' 'STAGING_URL' --dry-run`
- Plugin health where applicable:
  - `ddev wp plugin list`
  - run Plugin Check only for custom or migration-relevant plugins, since the manifest says `plugin_check` is available

QA should also spot-check representative migrated pages on `acme-staging`, including links, images, menus, permalinks, editor editability, and visible frontend rendering.

## Rollback And Monitoring

Rollback point: the pre-push staging export or confirmed `ddev pull pressable` baseline captured before `ddev push pressable`.

Rollback trigger: QA finds missing content, wrong destination, broken `siteurl`, corrupted media, or material page rendering failures that cannot be fixed within the staging QA window.

Rollback owner: migration lead owns the rollback decision; hosting/Pressable operator owns execution if provider access is required.

Monitoring after push:

- Confirm staging remains pointed at staging URLs.
- Confirm production was not touched.
- Track QA defects separately from production cutover planning.

## Assumption Register

Assumption: Pressable credentials for the `ddev-pressable` provider can target `acme-staging`.

Assumption: the destination confirmation can show both target identity and staging environment before sync confirmation.

Unknown: the manifest `generated_at` timestamp is not included in the excerpt.

Not claiming: this staging push validates production credentials, production URLs, production capacity, or final launch readiness.

## Test Strategy

Use staging QA as the acceptance surface.

Minimum proof set:

- Pre-push local count snapshot.
- Pre-push staging rollback snapshot.
- Confirmed sync target is `acme-staging`.
- Post-sync count comparison.
- URL dry-run review with `ddev wp search-replace --dry-run`.
- Representative page QA for content, media, links, and editor behavior.
- Delta re-push rehearsal after freeze, if editorial changes must be included.

## Acceptance Criteria

The staging cutover is accepted when:

- `ddev push pressable` was confirmed against `acme-staging`.
- Production was not targeted.
- Staging rollback point exists.
- Post-sync counts match expected migrated content.
- `siteurl` is correct for staging.
- Dry-run URL replacement shows no unexpected production or local references.
- QA signs off on `acme-staging`.

## Critic Handoff

Review should focus on target-safety, rollback sufficiency, freeze handling, and whether verification proves staging integrity without overclaiming production readiness.
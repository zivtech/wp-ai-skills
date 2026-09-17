## Migration Scope

Host-sync staging cutover only. The content transform (source-to-block mapping, serialization, unsupported-content accounting) was planned and executed under an earlier plan and is out of scope here. This plan covers moving the already-migrated local ddev site to the client's Pressable staging site (`acme-staging`) and proving it arrived intact. Production is explicitly out of scope — no production cutover is planned or authorized by this document.

## Current-State Evidence

- Environment: ddev, `AVAILABLE`, invocation prefix `ddev wp` (never bare `wp`).
- WP-CLI: `AVAILABLE`.
- Verification tools: `plugin_check` `AVAILABLE`; `phpcs` `UNAVAILABLE`; `phpstan` `UNAVAILABLE`; `wp_env` `UNAVAILABLE`; `wpcs` `BLOCKED`; `phpunit` `UNKNOWN`; `playground_cli` `UNKNOWN`. Static-analysis and WPCS gates are not available in this environment — do not instruct them.
- Runtime tools: one server, `ddev-pressable`, `superseded: false`. Tools: `ddev push pressable` (outward sync, `staging-only`, confirm required), `ddev pull pressable` (inward sync, confirm required). No Studio surface is listed and none is used.
- Manifest capability flags of note: `has_outward_sync_tool: true`, `can_provision_runtime_site: false`, `aware_of_host_agent_skills: false`. This plan treats the manifest as current only as of its own `generated_at`; if it is stale by cutover time, re-probe with `wordpress-environment-probe` before executing Phase 4.
- Known incident: a prior manual sync overwrote the destination's `wp-config.php` and `siteurl` because nobody confirmed the target before writing. This plan's target-confirmation step exists specifically to prevent a repeat.

## Source Audit

Not applicable to this plan — the local ddev site is the already-migrated source, and its content shape was audited and transformed under the prior migration plan. No new source-CMS audit is performed here.

## Target Mapping

Target is the client's existing Pressable staging site `acme-staging`. No new content model, CPT, taxonomy, or block mapping is introduced by this plan — the migrated content model was already established against the local ddev site. Target mapping here is limited to environment identity: confirm `acme-staging` is the correct and only staging destination (one staging site, one production site per the fixture facts), and confirm no other environment shares its Pressable SFTP/DB credentials that could cause an ambiguous push target.

## Transform And Execution Plan

No new content transform. This section defines the sync execution sequence only.

1. **Pre-push baseline capture.** Run `ddev pull pressable` to take a fresh inward sync of `acme-staging`'s current state (confirm required — this is a real inward sync, treat the confirmation prompt as a real gate, not a formality), or take a local export via `ddev wp db export acme-staging-pre-push-$(date +%Y%m%d).sql`. This baseline is the rollback point (see Rollback And Monitoring).
2. **Editorial freeze starts.** 48-hour content freeze on the local ddev editorial environment begins immediately before the push. Owner: the editor(s) currently working the local site — name them before executing.
3. **Target confirmation (mandatory, pre-write).** Before any write, print and manually verify the destination:
   - `ddev wp option get siteurl` (baseline, local side, for comparison)
   - Confirm the ddev provider's configured Pressable target resolves to `acme-staging` and not the client's production site.
   - After the push lands (see step 4), the very first read against the destination must be `wp_get_environment_type()` on `acme-staging` to confirm it reports `staging`, not `production`, before any further destination writes proceed. This directly addresses the prior incident where the target was never confirmed.
4. **Sync tool:** `ddev push pressable`
   **Sync target:** `acme-staging`
   This tool is `staging-only` per its `target_constraint` — it cannot target production, which structurally protects against a repeat of the wrong-destination incident, but the target-confirmation step in item 3 must still run because "staging-only" constrains the tool, not which staging site among the client's environments is addressed.
   Treat this push as an import with side effects, not a pure content copy. Prerequisites: Pressable credentials configured for the ddev provider (SSH key / API token as ddev-pressable expects), a completed pre-push baseline from step 1, and confirmation from step 3.
5. **Post-sync side-effect verification** (per Hard_Gates — a host-side sync changes more than content):
   - `ddev wp option get siteurl` on `acme-staging` — must read `acme-staging`'s own URL, not the local ddev URL.
   - `ddev wp plugin list --status=active` on `acme-staging` — confirm the active-plugin set matches what staging is expected to run; the pushed `active_plugins` row replaces staging's prior row.
   - `ddev wp eval 'echo wp_get_environment_type();'` on `acme-staging` — must report `staging`. If this comes back empty or `production`, the push corrupted `WP_ENVIRONMENT_TYPE` in `wp-config.php`; stop and restore from the Pressable-managed config backup rather than hand-editing.
   - `ddev wp option get blog_public` on `acme-staging` — confirm staging's indexing/search-visibility setting was not silently flipped by the sync.
   - `ddev wp db tables --all-tables` on `acme-staging` — check for renamed backup tables the push may have left behind; do not drop them without confirming they aren't the rollback fallback.

**Rerun policy:** idempotent. A re-push after the freeze (the delta re-push, see Rollback And Monitoring) must be safe to run again without duplicating content or corrupting IDs — this is inherited from the underlying content migration's idempotence guarantee, not re-derived here.

## Validation Plan

- `ddev wp option get siteurl` on `acme-staging` matches the expected staging URL.
- `ddev wp post list --format=count` on `acme-staging` matches the pre-push local count (delta accounted for by any freeze-window edits).
- `ddev wp search-replace --dry-run` on `acme-staging` against any local-to-staging URL differences, reviewed before a real search-replace is ever run (dry-run only in this plan; a live search-replace is a separate confirmed step, not silently chained).
- `ddev wp eval 'echo wp_get_environment_type();'` reports `staging` (also required pre-write per Transform And Execution Plan step 3, and re-checked post-sync in step 5 — this is the same check used as both a gate and a proof, deliberately).
- `ddev wp plugin list --status=active` reviewed against expected staging plugin set.
- Editorial spot-check: QA opens `acme-staging` in the browser and confirms representative pages render, since this plan's scope is arrival-intact verification, not a re-run of the prior plan's semantic block/editor/frontend oracles (those already passed against the local ddev site before this push and are not re-litigated here).
- Sign-off gate: QA signs off on staging before any production cutover is planned. This plan does not claim staging QA sign-off is evidence of production readiness — that determination belongs to a separate, not-yet-written production cutover plan.

## Rollback And Monitoring

- **Rollback point:** the pre-push baseline captured in Transform And Execution Plan step 1 (`ddev pull pressable` snapshot or `ddev wp db export acme-staging-pre-push-<date>.sql`).
- **Rollback trigger:** any post-sync verification check in Transform And Execution Plan step 5 or Validation Plan fails — most critically, `wp_get_environment_type()` failing to report `staging`, or `siteurl` resolving to an unexpected host.
- **Rollback owner:** name the engineer executing this cutover before starting; they hold the rollback decision, not the editorial team.
- **Rollback action:** restore `acme-staging` from the pre-push baseline via the Pressable-managed backup/restore path (not a hand-edited `wp-config.php`, per the Hard_Gates note on restoring host-managed files from the importer's own backup).
- **Delta re-push:** after the 48-hour freeze ends and QA signs off, any content edited on the local ddev site during the freeze window is captured and re-pushed via the same `ddev push pressable` sequence (steps 3-5 repeated in full — target confirmation is not a one-time step, it repeats on every push).
- **Monitoring:** post-push, monitor `acme-staging` for any client- or editor-reported anomalies for the remainder of the freeze window before declaring the cutover complete.

## Assumption Register

- Assumes the ddev provider's Pressable credentials for `acme-staging` are already configured and valid; if not, this is a Decision required: whoever owns Pressable credential provisioning must confirm before Phase 4 executes.
- Assumes only one staging site (`acme-staging`) exists for this client, per the fixture facts; if the client's Pressable account has multiple staging-labeled sites, the target-confirmation step must additionally disambiguate among them, which is a Decision required at execution time, not assumed here.
- Assumes the 48-hour freeze window is sufficient for the push-plus-verification sequence; if verification uncovers an issue requiring rollback-and-retry, the freeze may need to extend — owner must decide and communicate to editors.
- Assumes `capability-manifest.json` was generated recently enough to still reflect `ddev-pressable`'s actual tool set; per Required Boundaries, this plan does not treat the manifest as current beyond its `generated_at` timestamp, and a stale manifest is a Decision required: re-probe before Phase 4.

## Test Strategy

- **Fixture identity:** host-sync-staging-cutover
- Pre-push baseline export is itself a test artifact — diff `ddev wp post list --format=count` and `ddev wp option get siteurl` from the baseline against post-push state to confirm the push didn't silently drop or duplicate content.
- Rerun test: after a successful push, immediately attempting `ddev push pressable` again (dry-run posture, or a controlled no-op content state) should not corrupt state, per the inherited idempotence guarantee — exercised at delta re-push time, not necessarily as a standalone rehearsal given `can_provision_ephemeral_site: false` in the manifest (no ephemeral site available to rehearse against without touching real staging).
- Rollback rehearsal: confirm the pre-push baseline restore path is exercised (or at minimum, confirmed restorable) before the real push is executed for the first time on this cutover.
- Permission test: confirm the executing engineer's Pressable credentials have write access to `acme-staging` specifically, not merely to the client's Pressable account broadly (which could include production).

## Acceptance Criteria

- `acme-staging` reports `wp_get_environment_type()` as `staging` after the push.
- `acme-staging` `siteurl`, active plugin list, and post count match expectations post-push.
- No renamed backup tables or config drift left unexplained on `acme-staging`.
- Freeze window observed; delta re-push completed and re-verified before freeze lift.
- QA sign-off recorded on `acme-staging` before any production-cutover planning begins.
- Only `ddev push pressable` / `ddev pull pressable` were used; no Studio tool, no bare `wp`, no production target, at any point.

## Critic Handoff

Route to `wordpress-migration-critic` (or `meta-critic` if the domain critic is unavailable) to verify: the sync-tool selection matches the supplied manifest exactly, the target-confirmation step is genuinely pre-write (not advisory), the rollback point is concrete and restorable, and no instruction in this plan references a tool or environment type the manifest does not list.

**Current-State Evidence**

- Migration source: local `ddev` WordPress site containing already-transformed migrated content.
- WP-CLI invocation: `ddev wp` only.
- WP-CLI status: `AVAILABLE`.
- Runtime tools: manifest lists one runtime server, `ddev-pressable`, with:
  - `ddev push pressable`: outward sync, confirmation required, staging-only.
  - `ddev pull pressable`: inward sync, confirmation required.
- Verification tools available: `plugin_check` only. `phpcs`, `phpstan`, `wp_env`, and `wpcs` are not available; `phpunit` and `playground_cli` are unknown.
- Destination: Pressable staging site `acme-staging`.
- Production: out of scope.
- Manifest freshness: do not assume this remains current beyond the manifest’s `generated_at` timestamp. The excerpt provided does not show that timestamp, so recency must be checked in the full manifest before execution.

**Cutover Plan**

1. Announce a 48-hour editorial content freeze before the staging push.
   - Freeze owner: project/content lead.
   - Editors stop content changes in the source and destination during the freeze.
   - Any emergency edits must be logged for a later delta re-push.

2. Confirm Pressable access and provider configuration.
   - Verify Pressable credentials are configured for the local ddev Pressable provider.
   - Confirm the intended destination is the staging site `acme-staging`, not production.

3. Create the rollback point before any outward write.
   - Preferred staging baseline: run `ddev pull pressable` only after confirming it targets `acme-staging`.
   - Minimum fallback snapshot: `ddev wp db export` before the push.
   - Preserve the pre-push staging export as the rollback artifact.

4. Confirm the target before writing.
   - Print the destination site name/URL from the Pressable/ddev provider configuration.
   - Confirm it resolves to `acme-staging`.
   - Check the destination environment type before any write using WordPress, for example with a small command that reports `wp_get_environment_type()` through `ddev wp`.
   - Stop if the target is production, unknown, or not clearly `acme-staging`.

5. Execute the staging sync.

   Sync tool: `ddev push pressable`  
   Sync target: `acme-staging`

   This is an outward sync with side effects and must require explicit human confirmation before execution.

6. Verify arrival on staging.
   - Confirm expected URL:
     - `ddev wp option get siteurl`
   - Confirm content count is plausible:
     - `ddev wp post list --format=count`
   - Check URL rewrite impact without changing data:
     - `ddev wp search-replace '<local-url>' '<staging-url>' --dry-run`
   - Run available plugin check if relevant:
     - `ddev wp plugin check`
   - QA reviews staging content, menus, media, forms, key templates, and login/admin access.

7. Handle freeze delta.
   - After QA completes, identify any approved content changes made during the freeze exception process.
   - Re-apply or re-push only the required delta to staging.
   - Re-run the verification pass after the delta.

**Rollback**

- Rollback point: the pre-push staging export or baseline captured before `ddev push pressable`.
- Rollback trigger: wrong target detected, staging `siteurl`/environment corrupted, major content loss, broken admin access, or QA blocks release due to sync-caused defects.
- Rollback owner: technical migration lead, with client/PM approval before restoring.
- Rollback scope: staging only. Production remains untouched.

**Boundaries**

- Do not use Studio `site_push`, Studio `site_pull`, standalone `studio-mcp`, or any sync tool absent from the manifest.
- Do not target production.
- Do not claim staging QA proves production readiness.
- This plan covers staging arrival and integrity only; production cutover requires a separate plan after QA signoff.
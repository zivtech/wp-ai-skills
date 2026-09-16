# Studio verification, 2026-09-15

Live checks of Automattic's WordPress Studio CLI against this repository's tooling.
Recorded from a throwaway site created with `wp-studio@1.21.0` (npm, pinned; no desktop
app) on macOS arm64, default options (`studio site create --skip-browser`). Absolute
paths are replaced with `<scratch>` and `~`.

| Claim | Result | File |
|---|---|---|
| Studio sites run on SQLite, not MySQL | Confirmed: `WP_SQLite_DB`, `DB_ENGINE=sqlite`, `wp-content/db.php` drop-in, `sqlite-database-integration` mu-plugin; `studio wp db query` fails for lack of a `mysql` binary | `db-check.txt` |
| `studio mcp` is a stdio MCP server | Confirmed: protocol `2025-06-18`, server `studio 1.0.0`, **26 tools** at runtime (the source registry lists 29; three are conditional) | `mcp-tools-list.json` |
| `studio site create --blueprint` accepts a local Playground Blueprint file | Confirmed: a local `setSiteOptions` blueprint was applied to a new site | `blueprint-check.txt`, `minimal-blueprint.json` |
| `wordpress-environment-probe` detects a Studio 1.21 site | **Disproved, then fixed.** Before: fell through to `generic-local`, `wp_cli_unavailable`. A 1.21 site carries `STUDIO.md` in the site root and a `99-studio-loader.php` mu-plugin, not `.studio`/`.wp-studio.json`. After adding those markers: `kind: studio`, prefix `studio wp`, WP-CLI 2.12.0 `AVAILABLE`, `can_run_wp_cli: true` | `capability-manifest.before-marker-fix.json`, `capability-manifest.after-marker-fix.json` |

## Studio Sync against a Pressable staging site (2026-09-16)

Same CLI, pushing a ~240 MB WooCommerce site (200 content items, 632 uploads) from a
local Studio site to a Pressable staging site, alongside the same move done with
`ddev push pressable`. Site identifiers are omitted. Pull requests opened from these
findings: [pressable/ddev-pressable#4](https://github.com/pressable/ddev-pressable/pull/4),
[pressable/ddev-pressable#5](https://github.com/pressable/ddev-pressable/pull/5), and
[Automattic/studio#4857](https://github.com/Automattic/studio/pull/4857) (surface the remote failure reason in the CLI).

| Claim | Result |
|---|---|
| Sync needs only a Jetpack connection | **Disproved.** With Jetpack connected and healthy but the site on Jetpack Free, `studio pull` failed with HTTP 500 on `studio-app/sync/backup` and `studio push` with a bare "Import failed". Attaching the Jetpack license (Complete, here) and letting the first backup complete fixed both. The prerequisite is an active Jetpack Backup product on the target plus one completed backup. |
| `studio pull` is read-only on the remote | **Disproved.** It asks WordPress.com to run a backup job on the site before downloading, so it is not a safe probe. |
| The push leaves the host's `wp-config.php` alone | **Disproved.** The importer replaced the host's config with a generic one carrying hard-coded `DB_*` defines and no `WP_ENVIRONMENT_TYPE`; the site reported `production` until the original was restored from the `wp-config.php.jpbak.php` the importer leaves. `ddev push pressable` does not touch the file. |
| The database ends up as pushed | Partly. Content and options matched, but 56 renamed `__wp_*` backup tables and 5 `wp_sqm_*` tables were left behind (115 tables against 59). |
| Jetpack survives a full-database push | **Confirmed for Studio**: the connection options were preserved, so re-activating the plugin reconnected without a browser step. A raw `wp db import` (the ddev provider) wipes them. |
| Failures say why | No. The push reports a fixed "Import failed on <site>" although the API returns `error` and a VaultPress restore message; the pull reports "Invalid parameter(s): backup_id" when the site has no backup product. `DEBUG=*` exposes the reason, and also prints the account's OAuth token in plaintext. |
| Wall-clock for the successful push | 577 s, against 46 s plus a separate 22 s code rsync for `ddev push pressable` (which pushes database and uploads only). |

Not covered: WordPress.com-hosted targets, the desktop app, other site sizes. One site, one successful push per tool.

Regression tests for the marker fix live in
`evals/harness/tests/test_probe_wordpress_environment.py` (`test_studio_*`).

Remaining probe blockers on Studio are expected and unrelated to Studio itself:
no PHPCS/PHPStan on the host PATH, no Plugin Check, no ephemeral runtime, and no
`mcp-adapter`/Abilities API in a stock site.

Not recorded here: process, socket and port inspection of the Studio daemon. Those
notes are held privately pending review.

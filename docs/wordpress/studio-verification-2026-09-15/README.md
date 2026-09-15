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

Regression tests for the marker fix live in
`evals/harness/tests/test_probe_wordpress_environment.py` (`test_studio_*`).

Remaining probe blockers on Studio are expected and unrelated to Studio itself:
no PHPCS/PHPStan on the host PATH, no Plugin Check, no ephemeral runtime, and no
`mcp-adapter`/Abilities API in a stock site.

Not recorded here: process, socket and port inspection of the Studio daemon. Those
notes are held privately pending review.

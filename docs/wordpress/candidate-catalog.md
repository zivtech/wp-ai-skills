# WordPress Skill Candidate Catalog

Survey date: 2026-06-16.

This catalog records candidate upstream skill sources for WordPress V1 evaluation. It is not an adoption decision. Candidates must pass the evaluation and provenance gates before copied or adapted material enters production skill prompts.

Screening result: run `2026-06-16-candidate-screening`. Its archive is
monorepo-internal and is not in this repository; the conclusions it reached
are summarized below and in `negative-results.md`.

Current status: candidate screening is complete enough to preserve reference-only comparators, and the candidate-discrimination arc is closed as directional-internal only. Absolute scoring failed discrimination, blind pairwise did not certify reliable separation from a strong few-shot prompt, and answer-key diagnostics localized the measurable gap to exact WordPress API naming. The full 27-fixture superiority benchmark and any external adopt/adapt/build claim remain blocked unless the measurement target changes.

## Survey Notes

- skills.sh website search was performed on 2026-06-16 using the rendered public page at `https://www.skills.sh/?q=wordpress`, not the skills.sh API. The visible result set contained 74 WordPress-matching rows and is recorded in `skills-sh-website-survey.md`.
- GitHub commit metadata was gathered with `git ls-remote` on 2026-06-16.
- License checks used standard root license filenames on the default branch. Candidates without a verified compatible license are evaluation/reference candidates only, not reuse candidates.
- WordPress/agent-skills states GPL-2.0-or-later in its repository license/readme.
- **Editor-UX discovery (2026-09-25):** `gh search code` (12 filename-scoped queries) + `gh search repos` (4 queries) returned real, non-empty results; funnel: 1063 code-search matches → 854 unique matches / 598 unique repos → 582 after aggregator filter → 36 repos after a two-signal (WordPress + editor-UX) filter → 61 individual skill files screened against a G1–G5 editor-UX rubric.
- **skills.sh (2026-09-25):** rendered-page accessibility-tree dumps via `agent-browser` CLI snapshot (method: `RAW/skillssh-method.md`). Known-positive control reproduced — 100 rows returned vs. the 74-row 2026-06-16 baseline. 5 of 10 queries returned exactly 100 rows; whether 100 is a hard page cap is unverified, since the scroll-test output was found to duplicate another query's dump.
- WordPress/agent-skills delta `aa735ea7`→`f1bac1f1` (checked 2026-09-25): 19 files changed — 2 added (`wp-patterns`, `wp-env`), 17 modified.
- `automattic/agent-skills` and `automattic/wordpress-agent-skills` re-checked 2026-09-25 against their catalogued commits below: both `ahead_by 0` (unchanged at tip).
- One two-signal survivor from the 2026-09-25 search, `webdevarif/claude-skills` (`neuro-wp-block-theme-design`), was never fetched or screened — surfaced, not evaluated; not added as a row.

## Candidates

| Candidate | Commit | License | Skill Inventory | Initial Use |
|---|---:|---|---|---|
| [WordPress/agent-skills](https://github.com/WordPress/agent-skills) | `f1bac1f1c3096c011faabc1a7b0450f105bf3e30` | GPL-2.0-or-later by LICENSE/readme (GitHub's automated license-API classifier reports NOASSERTION at this exact commit — a person re-reads before any adaptation; open item) | skills.sh rows: `blueprint`, `wp-plugin-directory-guidelines`, `wp-abilities-audit`, `wp-abilities-verify`, `wordpress-router`, `wp-plugin-development`, `wp-rest-api`, `wp-block-themes`, `wp-performance`, `wp-block-development`, `wp-project-triage`, `wp-wpcli-and-ops`, `wp-phpstan`, `wp-abilities-api`, `wp-playground`, `wp-interactivity-api`, `wpds`, `wp-patterns`, `wp-env` | Primary official reference and comparator. Editor-UX discovery (2026-09-25) G1/G3/G4/G5 comparator: `wp-patterns` is the only G3/G4 candidate scoring 2 on both that is also license-clear — Playground-CLI templateLock/inserter checks plus an accessibility checklist. |
| [automattic/agent-skills](https://github.com/automattic/agent-skills) | `48d4aa21d0da0e7bda1c7ac155fef2e16b87aa25` | No standard root license found | skills.sh row: `wordpress-router` | Routing comparator only until license verified |
| [automattic/wordpress-agent-skills](https://github.com/automattic/wordpress-agent-skills) | `ea902bd8301564fa33e336c34114ab121f24c800` | No standard root license found (re-checked 2026-09-15 via the GitHub license API: still none) | skills.sh rows: `wordpress-block-theming`, `design-systems`, `site-specification`; also hosts `studio-mcp`, a standalone MCP server wrapping the Studio CLI (see Local-environment agent tooling below) | Block theming/design-system comparator only until license verified |
| [jeffallan/claude-skills](https://github.com/jeffallan/claude-skills) | `e8be415bc94d8d6ebddc2fb50e5d03c6e27d4319` | MIT | skills.sh row: `wordpress-pro` | Broad WordPress-generalist comparator |
| [jezweb/claude-skills](https://github.com/jezweb/claude-skills) | `0aa0f4437e0e70dda1e4e62df3a9d9cb8170f8ba` | MIT | skills.sh rows: `wordpress-elementor`, `wordpress-content`, `wordpress-setup`, `wordpress-plugin-core` | Page-builder, setup, content, and plugin-core comparator |
| [bartekmis/wordpress-performance-best-practises](https://github.com/bartekmis/wordpress-performance-best-practises) | `577a08fb1c157cef1055de450d4550c1af4e0845` | MIT | skills.sh row: `wordpress-performance-best-practices` | Performance critic comparator |
| [mindrally/skills](https://github.com/mindrally/skills) | `05a71308897983093248d719a2ffa1bca61d0768` | Apache-2.0 | skills.sh row: `wordpress` | General WordPress comparator |
| [bobmatnyc/claude-mpm-skills](https://github.com/bobmatnyc/claude-mpm-skills) | `718070a7d622921b01687799a1f9613f36c6f615` | MIT | skills.sh rows: `wordpress-security-validation`, `wordpress-block-editor-fse`, `wordpress-advanced-architecture`, `wordpress-plugin-fundamentals`, `wordpress-testing-qa` | Security, architecture, block editor, plugin, and QA comparator. Editor-UX discovery (2026-09-25) G1/G5 comparator: a numeric WCAG AA contrast threshold (4.5:1) plus a keyboard-nav flag inside `wordpress-block-editor-fse`, alongside theme.json/Site-Editor configuration guidance. |
| [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | `39660b6b4b9eee6dc2accbc4a22b89605d995662` | MIT | skills.sh rows: `wordpress-theme-development`, `wordpress-plugin-development`, `wordpress-woocommerce-development`, `wordpress`, `wordpress penetration testing`, SEO/blogging/conversion helpers | Theme/plugin/WooCommerce/security comparator |
| [elvismdev/claude-wordpress-skills](https://github.com/elvismdev/claude-wordpress-skills) | `0ac0bbd5fd7c2a91f45af8ec3f5282537e52b075` | MIT | `wp-performance-review` | Performance critic comparator |
| [trewknowledge/agent-skills](https://github.com/trewknowledge/agent-skills) | `ac851c91d8b1cd55ca77b7b31e5de8813554bd9b` | No standard root license found | skills.sh row: `wordpress-vip` | WordPress VIP comparator only until license verified |
| [wpacademy/wordpress-dev-skills](https://github.com/wpacademy/wordpress-dev-skills) | `5bb36a5ccab2acc62284025b85df8cb4bea2befb` | GPL-2.0 | skills.sh row: `wp-theme-dev` | Theme executor/critic comparator |
| [0xshe/php-code-audit-skill](https://github.com/0xshe/php-code-audit-skill) | `69d883e7983a09f72fd047a96e2377bee9a95d7e` | No standard root license found | skills.sh row: `php-wordpress-audit` | Security-audit comparator only until license verified |
| [respira-press/agent-skills-wordpress](https://github.com/respira-press/agent-skills-wordpress) | `e39a5c788e5a39d05157f804c8fd0c5a4f5e07a2` | MIT | 35 site-audit, migration, builder-conversion, onboarding, WooCommerce, SEO/AEO, image, and reporting skills | Migration, site audit, and page-builder comparator |
| [jorgerosal/wordpress-skills](https://github.com/jorgerosal/wordpress-skills) | `8c964424d05ba34b3ea5641f7181d4c13829e06f` | MIT | 18 skills including accessibility, ACF/content modeling, admin UI, blocks, CI/CD, headless/WPGraphQL, migrations, performance, PHPStan, Playground, plugins, REST, security, site audit, testing, themes, WooCommerce, WP-CLI | Broad community comparator |

## Editor-UX Survey Additions (2026-09-25)

Discovery for editor-UX skill extensions (local `plans/021`; docs record only — see `editor-ux-gap-source-map-2026-09-25.md` for the full gap-by-gap evidence). Method and funnel are recorded in the Survey Notes bullets above. All rows below score `advance: YES` against a G1–G5 editor-UX rubric (total ≥3 across G1–G5, or any single gap = 2) and are net-new versus the 2026-06-16 table above. License column states the SPDX-ish verdict and reuse class; `evidence shape` is recorded for anything weaker than a clean root LICENSE file, per `license-reuse-policy.md`'s weak-evidence rule.

| Candidate | Commit | License | Skill Inventory | Initial Use |
|---|---:|---|---|---|
| [84emllc/claude-wordpress-7-blocks-patterns-best-practices-skill](https://github.com/84emllc/claude-wordpress-7-blocks-patterns-best-practices-skill) | `b9275a562da0d1f6b3affc8ce9ac9a242268557b` | MIT — adapt-eligible | 1 skill: `wordpress-7-blocks-patterns-best-practices` (WP 7.0 blocks-vs-patterns decision model) | G3/G5 comparator: content-only-editing lock behavior and the theme.json→Styles-panel styling cascade, stated as editor-observable rules with a worked empirical test on a live WP 7.0 install |
| [WordPress/gutenberg](https://github.com/WordPress/gutenberg) — `.agents/skills/design-system-ui-review` | `fb98ae09a105f342ae63ac01f44d82c17ba35370` | Dual GPL-2.0-or-later / MPL-2.0, custom preamble in root `LICENSE.md` (GitHub license API reports NOASSERTION — classifier artifact, not absence of a license) — weak-evidence shape 3, read and classified by operator 2026-09-25 — **ADAPT-ELIGIBLE** | 1 relevant skill of many in this large repo: `design-system-ui-review` | G1 comparator: an evidence-gated protocol for reviewing Gutenberg/plugin UI diffs for accessibility, interaction, and focus correctness before merge. **Mirror note:** `Automattic/gutenberg-sync-engines` @ `111c92fa8ae26f36e40eeb15370d9c8a6596ca98` carries a byte-identical copy of this same skill file — disposed as one finding under this row, not a separate entry. It has its own root `LICENSE.md` (GitHub license API also reports NOASSERTION), but whether its text matches this repo's dual-license grant was not verified this survey; its license is recorded independently as Unknown until checked. |
| [BigOrangeLab/skills](https://github.com/BigOrangeLab/skills) — `wp-admin-ui` | `a718672047ef57cf7eeb3c486ccea3c1c3be5bb5` | MIT — adapt-eligible | 1 relevant skill: `wp-admin-ui` (legacy PHP vs. React/DataViews admin-screen guidance) | G1/G2 comparator: the only candidate combining an explicit keyboard-nav + focus-ring verification line with a full admin-screen build/debug procedure (color scheme, RTL, notices, WP 7.0+ editor-iframe CSS scoping) |
| [ComeOnOliver/skillshub](https://github.com/ComeOnOliver/skillshub) — `skills/wprig/wprig/web-designer` | `def8531e65114c0fca8fb8551c1871ee0eed705c` | MIT — adapt-eligible | 1 relevant skill: `web-designer` (WP Rig theme styling workflow) | G5 comparator: theme.json-first decision sequence for where a style value belongs (settings vs. CSS partial), applied per theme type (classic/universal/block-based) |
| [Lonsdale201/wp-agent-skills](https://github.com/Lonsdale201/wp-agent-skills) — `wordpress/wp-admin-list-table` | `8820ff3c301066297e696611e3bc4ebeb47d1851` | MIT — adapt-eligible | 1 relevant skill: `wp-admin-list-table` (`WP_List_Table` subclass contract) | G2 comparator: required-override contract for admin list screens plus a candidate-cited `get_primary_column_aria_label()` accessible-name rule for primary row headers. **Version note (resolved):** `get_primary_column_aria_label()` carries `@since 7.1.0` in `wordpress-develop` trunk; it is not available at this repo's WP 7.0 floor — do not add it to the Exact API contract; it may appear only as a version-guarded prose note ("on 7.1+ …"). **Near-duplicate note:** `vikingokft/vikingo-studio-skills` @ `065be9026219faa073e1da747cc8e40ff3b9ab00` (NOASSERTION license) carries an older copy of the same contract under the same author; disposed as one finding under this row, not a separate entry — prefer this MIT source if adaptation is ever pursued. |
| [gambitph/Stackable](https://github.com/gambitph/Stackable) — `.cursor/skills/wp-patterns` | `3154353ee04fe8bef542bf5a19058511537dd26a` | GPL-3.0 — adapt-eligible | 1 relevant skill: `wp-patterns` (near-duplicate/superset of WordPress/agent-skills' `wp-patterns`, above) | G1/G3/G4/G5 comparator: the same Playground-CLI runtime-verification block (templateLock resists editing, inserter visibility, desktop/mobile render) as WordPress/agent-skills' `wp-patterns`, plus an accessibility checklist and a 5-decision design-token framework layered on top. Content overlaps heavily with WordPress/agent-skills' row above; any future adaptation decision should treat these as one source choice, not two independent adoptions. |
| [jasenwyatt/wordpress-gutenberg-designer](https://github.com/jasenwyatt/wordpress-gutenberg-designer) | `c72b0170bbd32bcbd179f079ee9b4eb307c3a975` | MIT (confirmed via root `LICENSE` file and the skill's own frontmatter) — adapt-eligible | 1 skill: `wordpress-gutenberg-designer` (comp-to-Gutenberg implementation planner) | G1/G5/N3 comparator: explicit `aria-describedby` rule for File-block download buttons, a strict "no raw hex — presets only" theme.json validation checklist, and an explicit rule against claiming pixel-perfect preview fidelity |
| [adityaarsharma/orbit](https://github.com/adityaarsharma/orbit) — `skills/orbit-accessibility` | `133b31c24d07715e6beeed7bd5be86ea8c6a6766` | None found (GitHub license API 404 at this commit; a person should re-check for a non-root LICENSE layout before treating as permanently unlicensed) — reference-only | 1 relevant skill: `orbit-accessibility` (WCAG 2.2 AA audit, axe-core + code review) | G1/G4 comparator: the only G1 candidate found that runs an automated axe-core+Playwright check (keyboard, ARIA, dynamic content, forms), with an explicit "Block editor (Gutenberg)" section |
| [adamsilverstein/my-skills](https://github.com/adamsilverstein/my-skills) — `claude-code-skills/wp-admin-tester` | `fcc77036e95916f97bea6c1b9b32a7e2be6c56fa` | None found (404) — reference-only | 1 relevant skill: `wp-admin-tester` | G4 comparator: working Playwright scripts that log in, create a post, insert an image block, upload via Media Library, and capture console+network errors — directly reusable pattern shape for the #39 runtime-oracle workstream |
| [mdemonahmed/markaroo](https://github.com/mdemonahmed/markaroo) — `.claude/skills/wp-admin-browser` | `282601c7adbc094993f55a892d31a39799ccb7d7` | GPL-3.0, root `LICENSE` (verified 2026-09-25) — adapt-eligible | 1 relevant skill: `wp-admin-browser` | G4 comparator: a Chrome-DevTools-MCP protocol that navigates via menu clicks (not hardcoded URLs), verifies JS state, and handles session expiry — another #39-relevant comparator pattern |
| [woocommerce/sensei-certificates](https://github.com/woocommerce/sensei-certificates) — `.claude/skills/ui-verification` | `dc4eb83fb866cfc02d90bc53abc69f6cc446f73c` | GPL-2.0, bare, no or-later evidence found — treated as GPL-2.0-only (one-way incompatible with this repo's GPL-3.0) — reference-only | 1 relevant skill: `ui-verification` | G4 comparator: a scoped-from-`git diff`, screenshot-evidenced, browser-driven verification workflow covering admin and block-editor surfaces for one plugin |
| [teamchrisfromthelc/wp-preset](https://github.com/teamchrisfromthelc/wp-preset) — `theme/.claude/skills/block-theme-editor-ux` | `a26cc959e75a4b5c58c7e9f775d2a8a1f101cf90` | **Unknown** — package manifest and theme header both declare GPL-2.0-or-later, but no LICENSE file exists at this commit (weak-evidence shape 1: manifest declaration without a license grant) — reference-only | 1 skill: `block-theme-editor-ux` | G2/G3/G4/G5 comparator: scored 2 on four of five gaps (G2–G5), the widest rubric coverage of any candidate in this batch — an audit→apply→verify workflow with Playwright scripts that pixel-diff Site Editor vs. frontend, dump List View names, assert lock state (`canMoveBlock`/`getBlockEditingMode`), verify inserter allowlist, and check `canLockBlocks` by user role. Reference-only purely on license evidence, not content quality; flagged for priority manual license re-check (`plans/021` Task 0b). |
| [abdul977/muahib-skills](https://github.com/abdul977/muahib-skills) — `skills/wp-admin-panel-builder` | `92dad144e18922593ba540373918a8160f520620` | NOASSERTION, root `LICENSE` present — weak-evidence shape 3 (file exists; SPDX classifier could not match it; unread by a person) — reference-only | 1 skill: `wp-admin-panel-builder` (standalone non-wp-admin page-builder CMS) | N5 comparator: a working version-history pattern (snapshot every Save, keep last 6, restore any) — comparator for a revisions *feature*, not a WordPress-native implementation (this tool replaces Gutenberg/wp-admin rather than extending it) |
| [kerray/wp_template](https://github.com/kerray/wp_template) — `.claude/skills/gutenberg-block-converter` | `f79bc32cb5086f730664f71aa581c1ab4786ab0a` | None found (404) — reference-only | 1 relevant skill: `gutenberg-block-converter` (DIVI→Gutenberg conversion, mostly out of scope) | G1 comparator: one concrete step-by-step fix for the editor's own color-contrast warning via the block sidebar Color panel |
| [wpgaurav/WordPress-skills](https://github.com/wpgaurav/WordPress-skills) — `skills/wordpress/wp-theme` | `8c5bad0d1846182bf9b2b3802fc3f4ac64f156dc` | None found (404) — reference-only | 1 relevant skill: `wp-theme` (block-theme scaffold generator) | G5/N3 comparator: a pre-release checklist with "theme.json validates against schema" and "Editor styles match frontend" as pass/fail gate items |
| [Automattic/build-with-wordpress](https://github.com/Automattic/build-with-wordpress) | `b4fc8b710d1dd845c480771575c7f38f36c0f62c` | None found (GitHub license API 404 — no LICENSE file) — reference-only | `block-creator`, `studio`, `theme-creator` (delta-relevant subset of an 8-skill inventory: auditing, block-creator, design-previews-creator, plugin-creator, site-creator, studio, theme-creator, wordpress-creator) | N3/G4 comparator: `studio`'s `validate_blocks` + live-editor validation loop is a genuine runtime block-validity oracle; `block-creator`/`theme-creator` both carry an explicit "editor must resemble frontend" rule. Net-new row — distinct from the already-catalogued `automattic/agent-skills` and `automattic/wordpress-agent-skills` rows above. |

**Surfaced but not screened — not added as a row:** `webdevarif/claude-skills` — `neuro-wp-block-theme-design/SKILL.md` @ `e684d7bbcc8124a72ceaf0c51d3e546fe4150dca`. Matched the two-signal filter and appears in the 36-repo survivor list, but no raw file was fetched and it was never screened — not evaluated and excluded, simply never reached. G5-adjacent by title only.

**Open item not resolved by this batch:** `wpacademy/wordpress-dev-skills`'s existing bare `GPL-2.0` catalog row was flagged for only/or-later resolution. This survey's scope did not include that repo and no evidence independently resolves it. A 2026-09-25 re-check of the GitHub license API confirms the file is still classified bare `GPL-2.0` (SPDX `gpl-2.0`); the LICENSE file itself carries no repo-specific "or later" grant statement, so only/or-later remains unresolved from the LICENSE text alone. Leave the existing row as-is; carry the open item forward rather than silently closing it.

## Non-Skill Sources (surveyed 2026-08-28)

This catalog's table is for **skill** repositories, judged on prompt inventory
and on whether their text could ever be adapted. A separate survey on 2026-08-28
covered sources that are not skill collections: published engineering doctrine,
PHPCS rulesets, unit-test mocking libraries, project scaffolding, local-
environment agent tooling, and shipped AI-provider plugins consulted as
ground truth for exact registration names.

Those are judged on different criteria — is this a doctrine reference, a
pinnable gate, or a source of exact API names — so they are deliberately kept
out of the table above, where the columns would mean something different.

**The survey took no text from any of them.** Exact WordPress API names were
confirmed against developer.wordpress.org, which are public facts rather than
any project's expression. Nothing surveyed entered a production prompt, so no
reuse-ledger rows were required; see `reuse-ledger.md` for the standing record
of that, and `license-reuse-policy.md` for the weak-license-evidence rule the
survey produced.

### Local-environment agent tooling (surveyed 2026-09-15)

Recorded here because these are environments and MCP servers, not skill
collections. All are **reference-only comparators**; no text is reused.

| Project | Version / commit | License | What it is | Relationship to this repo |
|---|---|---|---|---|
| [Automattic/studio](https://github.com/Automattic/studio) | v1.21.0 (2026-09-07) | GPL-2.0 (root `LICENSE.md`) | Local WordPress environment: desktop app plus standalone `wp-studio` CLI. Native PHP by default (Playground/WASM sandbox optional), SQLite via `sqlite-database-integration`. Ships `studio mcp` (stdio, 29 tools: site lifecycle, previews, `wp_cli`, screenshots, scaffold/validate blocks, audits, push/pull to WordPress.com/Pressable, import/export) and six built-in Agent Skills (`SKILL.md` files installed to `<site>/.agents/skills/` with `.claude/skills/<id>` symlinks). | `wordpress-environment-probe` already detects Studio and uses `studio wp` as the WP-CLI prefix. `wordpress-blueprint-executor` output is Playground Blueprint JSON, which `studio blueprint use` consumes. Studio's six skills are guidance documents in the same install convention as this repo's planner/executor/critic skills; complementary, not overlapping in role. Verification log: `studio-verification-2026-09-15/`. |
| [pressable/ddev-pressable](https://github.com/pressable/ddev-pressable) | main, pushed 2026-07-23 | Apache-2.0 | Official DDEV provider for Pressable: `ddev pull pressable` / `ddev push pressable` (push targets staging only) over the site's SSH + WP-CLI; no API token or plugin. MyPressable generates per-site config commands (changelog 2026-08-04). | Reference only. Relevant because `wordpress-environment-probe` already resolves ddev sites to the `ddev wp` prefix, so this path needs no probe change and keeps MySQL/MariaDB parity. Pressable documents it alongside Studio Sync. Verified 2026-09-15/16 against a staging site: a non-root docroot breaks both hooks, PHP 8.5 deprecation notices corrupt captured values, and nothing prints the push target — fixes proposed upstream in [#4](https://github.com/pressable/ddev-pressable/pull/4) and [#5](https://github.com/pressable/ddev-pressable/pull/5). |
| [Automattic/wordpress-agent-skills/studio-mcp](https://github.com/Automattic/wordpress-agent-skills/tree/trunk/studio-mcp) | trunk, 2026-09-15 | No standard root license found | Earlier standalone MCP server that shells out to the Studio CLI; adds `studio_fs_*` file tools and `studio_block_fix`; macOS only per its README. Superseded in practice by the built-in `studio mcp`. | Comparator only. |

Studio Sync was exercised against a Pressable staging site on 2026-09-16; findings and
the resulting upstream reports ([Automattic/studio#4857](https://github.com/Automattic/studio/pull/4857),
issues [#4863](https://github.com/Automattic/studio/issues/4863),
[#4864](https://github.com/Automattic/studio/issues/4864),
[#4865](https://github.com/Automattic/studio/issues/4865), and
[Automattic/wp-calypso#114383](https://github.com/Automattic/wp-calypso/pull/114383),
[pressable/ddev-pressable#6](https://github.com/pressable/ddev-pressable/issues/6),
[#7](https://github.com/pressable/ddev-pressable/issues/7), and
[Automattic/jetpack#52385](https://github.com/Automattic/jetpack/issues/52385))
are in the verification log.

Studio facts above were read from the repository source and developer.wordpress.com
documentation on 2026-09-15; the SQLite and transport claims are confirmed against a
live `wp-studio@1.21.0` site in the verification log.


## Evaluation Lanes

1. Raw upstream candidate output.
2. Fair zero-shot and few-shot baselines.
3. Zivtech V1 prototype output after initial build.

## Decision Rules

| Result | Action |
|---|---|
| Candidate wins its domain, has no critical gaps, and passes license/provenance gate | Adopt as reference or reuse with attribution |
| Candidate has strong domain signal but lacks Zivtech protocol/output contract | Adapt into Zivtech format with attribution |
| Candidate underperforms or misses Zivtech consulting needs | Build original Zivtech skill behavior |
| Candidate domain has low client relevance or insufficient evidence | Defer |

## Source Evidence

- The skills.sh website search for `wordpress` returned 74 visible results ranked by relevance, publisher, and installs.
- WordPress/agent-skills `docs/ai-authorship.md` states skills were generated from official WordPress/Gutenberg docs, reviewed by WordPress contributors, tested against WP Bench tasks, and not yet run through a formal evaluation system.
- WordPress 7.0 was verified as the current release on the official WordPress News site before evaluating WP 7.0-aware candidate claims.

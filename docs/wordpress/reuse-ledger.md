# WordPress Skills Reuse Ledger

No copied upstream passages are included in the initial V1 skill prompts.

The initial prompts are original Zivtech protocols informed by the candidate survey. Skill files include compatible reference notes naming upstream sources that should be used as evaluation comparators or future attribution anchors.

Active policy: direct copied or closely adapted third-party prompt text remains blocked inside `zivtech-meta-skills` until root license handling is standardized. See `license-reuse-policy.md`.

## Reference-Only Entries

| Local Area | Source | Commit | License | Reuse Class | Rationale |
|---|---|---:|---|---|---|
| WordPress planners/executors/critics | WordPress/agent-skills | `aa735ea7111c7924ee988306bcef70439e17dec9` | GPL-2.0-or-later | Reference only | Official coverage map and comparator |
| Performance critic | elvismdev/claude-wordpress-skills | `0ac0bbd5fd7c2a91f45af8ec3f5282537e52b075` | MIT | Reference only | Focused performance-review comparator |
| Migration/page-builder coverage | respira-press/agent-skills-wordpress | `e39a5c788e5a39d05157f804c8fd0c5a4f5e07a2` | MIT | Reference only | Broad site migration and page-builder skill inventory |
| Broad community comparison | jorgerosal/wordpress-skills | `8c964424d05ba34b3ea5641f7181d4c13829e06f` | MIT | Reference only | Broad WordPress skill inventory across ACF, security, CI/CD, REST, and WooCommerce |

## Zero-Reuse Survey Record (2026-08-28)

A survey of non-skill sources — engineering doctrine, PHPCS rulesets, mocking
libraries, project scaffolding, local-environment agent tooling, and shipped
AI-provider plugins — produced **no rows in this ledger, because no text was
reused.**

That is the entry. A ledger records adaptation; the honest record of a survey
that adapted nothing is a statement that it adapted nothing, not a set of rows
implying otherwise.

What the survey did produce:

- Exact WordPress and Gutenberg core API names added to the block and theme
  planner contracts. Those are public facts documented at
  developer.wordpress.org, not any project's expression, so no ledger obligation
  attaches to them.
- The weak-license-evidence rule now in `license-reuse-policy.md`, after four
  surveyed sources turned out to declare a license only in a package manifest,
  only on a website, or in a LICENSE text no classifier could match.
- Two candidate inputs for later work (a third-party PHPCS ruleset as a second
  advisory profile, and shipped provider plugins as registration-name ground
  truth). Neither has been adopted. **If either is adopted in a way that adapts
  its text rather than reading its API names, a full ledger row becomes
  mandatory** — source, commit, license, local file, reuse class, and rationale,
  per the Operational Rules.

## 2026-09-25 — Editor-UX discovery (plan 020): zero reuse

Sources consulted: 61 external skill files across 36 net-new repos (plus delta
files from two already-catalogued repos, WordPress/agent-skills and
Automattic/build-with-wordpress), survived a two-signal WordPress +
editor-UX filter out of 598 unique repos found via `gh` code/repo search;
skills.sh run in parallel (known-positive control reproduced — 100 rows
returned vs. the 74-row 2026-06-16 baseline; 5 of 10 queries returned exactly
100 rows; whether 100 is a hard page cap is unverified, since the scroll-test
output was found to duplicate another query's dump — see `RAW/skillssh-method.md`),
not confirmed to have contributed any of the 36 survivors, all of which trace
to `gh` code search; Gutenberg trunk docs @ `fb98ae09a105f342ae63ac01f44d82c17ba35370`
(GPL-2.0-or-later), the theme.json living reference and Global Settings &
Styles guide, and a 60-issue deduplicated Gutenberg-issue sample.

**No text was reused.** Public WordPress/Gutenberg API names and documented
behaviors cited in the planned skill extensions (local `plans/021`) are facts,
not expression, per this ledger's existing precedent.

Adapt-eligible candidates identified but not adapted (any future adaptation
needs its own full ledger row — source, commit, license, local file, reuse
class, rationale):

| Source | Commit | License | Status |
|---|---:|---|---|
| 84emllc/claude-wordpress-7-blocks-patterns-best-practices-skill | `b9275a562da0d1f6b3affc8ce9ac9a242268557b` | MIT | ADAPT-ELIGIBLE |
| BigOrangeLab/skills | `a718672047ef57cf7eeb3c486ccea3c1c3be5bb5` | MIT | ADAPT-ELIGIBLE |
| ComeOnOliver/skillshub | `def8531e65114c0fca8fb8551c1871ee0eed705c` | MIT | ADAPT-ELIGIBLE |
| Lonsdale201/wp-agent-skills | `8820ff3c301066297e696611e3bc4ebeb47d1851` | MIT | ADAPT-ELIGIBLE |
| bobmatnyc/claude-mpm-skills | `718070a7d622921b01687799a1f9613f36c6f615` | MIT | ADAPT-ELIGIBLE (already catalogued; this survey only updates its commit/inventory) |
| gambitph/Stackable | `3154353ee04fe8bef542bf5a19058511537dd26a` | GPL-3.0 | ADAPT-ELIGIBLE (content overlaps WordPress/agent-skills `wp-patterns` — treat as one source choice if ever adapted, not two) |
| jasenwyatt/wordpress-gutenberg-designer | `c72b0170bbd32bcbd179f079ee9b4eb307c3a975` | MIT | ADAPT-ELIGIBLE |
| mdemonahmed/markaroo | `282601c7adbc094993f55a892d31a39799ccb7d7` | GPL-3.0 (root `LICENSE`, verified 2026-09-25 via the GitHub license API) | ADAPT-ELIGIBLE |
| WordPress/agent-skills (`wp-patterns`, `wp-block-themes`) | `f1bac1f1c3096c011faabc1a7b0450f105bf3e30` | GPL-2.0-or-later per this repo's existing catalog row; GitHub's automated license-API classifier reports NOASSERTION at this exact commit — a person re-reads before any adaptation | ADAPT-ELIGIBLE pending that re-read |
| WordPress/gutenberg (`design-system-ui-review`) | `fb98ae09a105f342ae63ac01f44d82c17ba35370` | Dual GPL-2.0-or-later / MPL-2.0, custom preamble in root `LICENSE.md` (GitHub license API reports NOASSERTION, a classifier artifact) | **ADAPT-ELIGIBLE** — weak-evidence shape 3, read and classified by operator 2026-09-25 per `license-reuse-policy.md`'s Weak License Evidence row 3. `Automattic/gutenberg-sync-engines` carries a byte-identical mirror of the skill file and has its own root `LICENSE.md` (also NOASSERTION via the GitHub API); whether its text matches this grant was not verified this survey, so it is not listed as its own stub row and its license stays Unknown. |

Checked and explicitly excluded from the adapt-eligible set (scored well on the
G1–G5 rubric, but license evidence does not clear the bar):

- **Weak-evidence shape 1** (manifest/header declares a license, no LICENSE file exists): teamchrisfromthelc/wp-preset (`block-theme-editor-ux` — manifest and theme header declare GPL-2.0-or-later; scored 2 on four of five gaps (G2–G5), the widest rubric coverage of any candidate in this batch, but reference-only on license evidence alone).
- **Bare GPL-2.0, no or-later evidence** (one-way incompatible with this repo's GPL-3.0): woocommerce/sensei-certificates (`ui-verification`).
- **No LICENSE file found via the GitHub license API** (404 — a person should re-check for a non-root LICENSE layout before treating any of these as permanently unlicensed): Automattic/build-with-wordpress, adityaarsharma/orbit, adamsilverstein/my-skills, kerray/wp_template, wpgaurav/WordPress-skills.
- **NOASSERTION with a root LICENSE file present** (weak-evidence shape 3 — file exists, SPDX classifier could not match it, unread by a person): abdul977/muahib-skills (`wp-admin-panel-builder`).

Not screened: webdevarif/claude-skills `neuro-wp-block-theme-design`
(surfaced by the two-signal filter, never fetched or screened).

Absence claims in this survey are bounded to the search legs that ran and
returned real, non-truncated results.

## Tooling Dependencies (fetched at install time, never vendored)

The API-existence lint (`evals/harness/wp_api_lint.py`) shells out to a
Composer-installed toolchain pinned by `evals/harness/php-tools/composer.lock`.
Only `composer.json` and `composer.lock` are committed; the `vendor/` tree is
gitignored and fetched by each environment (2026-07-02).

| Package | Version | License | Handling |
|---|---:|---|---|
| phpstan/phpstan | 2.2.3 | MIT | Fetched dependency; invoked as a subprocess |
| php-stubs/wordpress-stubs | 7.0.0 | MIT | Fetched dependency; loaded by PHPStan as scan files |
| johnbillion/wp-compat | 1.5.0 | MIT | Fetched dependency; PHPStan rule set plus `symbols.json` used for did-you-mean suggestions |
| wp-hooks/wordpress-core | 1.12.0 | GPL-3.0 | Transitive dependency of wp-compat, consumed inside the fetched `vendor/` tree at analysis time — by wp-compat's PHPStan rules and (since the 2026-07-02 phase-2 merge) by the lint's hooks engine, which reads `vendor/wp-hooks/wordpress-core/hooks/*.json` directly at run time. Update 2026-07-03: the repository relicensed to GPL-3.0, so committing a hooks snapshot is now license-compatible if ever wanted (with a ledger entry); the vendor-side consumption remains the current implementation. |
| playwright | 1.58.0 | Apache-2.0 | Locked by `runtime-images/browser/package-lock.json`; installed while the trusted browser image is built and executed only in the final mount-free browser service |

## GitHub Actions Bootstrap Entries (verified 2026-07-15)

Workflow actions are referenced by immutable commits. Tag names are provenance
labels only; execution uses the full commit in `.github/workflows/validate.yml`.
All five upstream repositories publish the MIT license.

| Action | Verified tag | Full execution commit | License | Purpose |
|---|---:|---|---|---|
| actions/checkout | `v7` | `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0` | MIT | Main validation checkout with persisted credentials disabled |
| actions/setup-python | `v6` | `ece7cb06caefa5fff74198d8649806c4678c61a1` | MIT | Exact `.python-version` bootstrap |
| actions/cache | `v6` | `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` | MIT | Main-job Composer download cache only |
| astral-sh/setup-uv | `v7` (peeled annotated tag) | `37802adc94f370d6bfd71619e3f0bf239e1f3b78` | MIT | Exact uv 0.9.27 bootstrap |
| actions/upload-artifact | `v7` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | MIT | Plan 010 measurement evidence upload |

The two no-secrets Docker jobs retain manual credential-free exact-commit
checkout. They use only the pinned setup-python and setup-uv bootstraps, pass
explicit empty token inputs, and disable uv caching. They do not use checkout,
cache, or helper-image actions and receive no repository credential.

## Committed Data Extraction Entries

`evals/harness/data/wp-symbols.json` (built by `scripts/build-wp-symbol-db.py`)
is a committed, MIT-sources-only snapshot for the lint's native engine. It
contains symbol names, deprecation versions, successor API names, and
introduced-in versions — no prose, descriptions, or code are copied.

| Data | Source | Ref | License | Extracted facts |
|---|---|---|---|---|
| Function/class existence, `@deprecated` versions and replacements | php-stubs/wordpress-stubs | `d74b963ed4f47303859bf73c741c80f554c83dc6` (`v7.0.0`) | MIT | Symbol names, deprecation version, successor API name (via PHP reflection over the stubs); fetched from the immutable raw URL with SHA-256 `1fa69deee70f8a1be7e3a0498327ca16e36ee2b5c243a5b2ab1926bec456fd44` |
| Per-function `since` versions | johnbillion/wp-compat `symbols.json` | `2ccebedbbbc6b6eec3fba4a568cff0a4ec05bf6e` (`1.5.0`) | MIT | Function name → introduced-in version; fetched from the immutable raw URL with SHA-256 `d5f7210cb8804263f71b888d1f34cd7593c4d166077efa055a9232ce2327a298` |

The generator verifies both identities against `php-tools/composer.lock`, fetches
only those exact source paths through the bounded public transport, and runs PHP
reflection in the Composer platform image pinned by `container-images.json`.
The snapshot records the canonical rebuild command, OCI index and platform
digests, source metadata, and a normalized function/class digest. Ordinary CI
validates that metadata and digest without network access; a maintainer rebuild
must be byte-identical to the committed file.
# Plan 009 sandbox feasibility inventory (verified 2026-07-14)

Step 0 records the official Node, Composer, Python, Playwright, WordPress,
WP-CLI, and MariaDB images in `evals/harness/container-images.json`. Each entry
contains its reviewed tag (provenance only), OCI index digest, linux/amd64 and
linux/arm64 child digests, purpose, and upstream license. Execution must select
the platform child digest and must not resolve the tag. The WordPress 7.0.1
source archive URL and SHA-256 are recorded in the same inventory.

The npm runner locks use registry packages under their package-published
licenses. Fixture Composer acquisition is HTTPS ZIP dist-only; inert `source`
metadata in Composer's generated lock is not an allowed fallback.
The no-secrets Linux jobs install the exact Python validation resolution from
`uv.lock`; Pytest is MIT-licensed. They fetch the exact public commit over HTTPS
without credentials, then use only the two immutable bootstrap actions recorded
above with explicit empty token inputs and uv caching disabled. They use no
checkout/cache action or helper image and continue to rely on the hosted Linux
runner's Docker installation.

On 2026-07-14 the mutable provenance tags for Node, Python, and WordPress moved.
Their official OCI indexes and linux/amd64 and linux/arm64 child manifests were
re-reviewed together; the inventory and Node acquisition profiles now record
those replacements. Composer, Playwright, WP-CLI, and MariaDB still resolved to
their previously reviewed identities. Execution remains child-digest-only; the
tags are checked solely as a fail-closed signal that a new provenance review is
required.

Later tag moves were re-pinned on 2026-08-10, 2026-08-25, 2026-09-16, and
2026-09-23. The current review procedure: every reviewed tag is re-inspected,
only drifted entries are re-pinned, the drifted child image configurations and bundled tool versions are
compared, and any secondary digest copies (the Node acquisition profiles) move
with the inventory. The inventory's `verified_at` and the Git history of
`evals/harness/container-images.json` are the record of each review.

The final generated-code runtime additionally derives three local images from
the immutable WordPress 7.0.1, MariaDB 11.8.5, and Playwright 1.58.0 platform
digests. Its WordPress build consumes the separately hashed WordPress core,
WP-CLI 2.12.0, and Plugin Check 2.0.0 inputs. The committed browser runner uses
the npm lock above; generated package dependencies are never copied into that
runner. Derived image tags are run-scoped handles, not provenance, and are
deleted after evidence collection. No upstream source or prompt prose is
vendored by these build inputs beyond the recorded archives and fetched locked
dependencies under their stated licenses.

# Editor-UX Gap → Source Map (2026-09-25 discovery, plan 020)

This is the public-safe, committable version of the working gap→source map. Every internal-evidence figure appears only as `internal evidence (authorized 2026-09-25), n=<count>` — no client name, ticket keys, quotes, tool name, or scratchpad paths. The public front-end walk referenced in G1/N6 is cited only as "a public front-end walk of one WordPress site" and is never placed in the same sentence or table row as an internal-evidence figure.

**Provenance note:** internal-evidence figures below trace to a single client's support-ticket evidence. Authorization to cite that evidence in this committed document was granted by the operator on 2026-09-25. The layer is marked inline with `internal evidence (authorized 2026-09-25)` wherever it appears; each gap also states, for provenance, what would have changed had authorization been withheld.

---

## G1 — Editor accessibility

**Failure:** an editor using keyboard or assistive tech cannot operate the editing surface — unreachable controls, unlabeled toolbar buttons, motion ignoring reduced-motion, illegible preview contrast.

**Public sourcing:** MEDIUM. Gutenberg's contributor accessibility-testing guide gives a concrete manual verification protocol (keyboard reachability via Tab/Shift+Tab or arrow keys; Enter/Space activation rules; composite ARIA roles — `toolbar`/`menu`/`listbox` — for arrow-key-only groups; NVDA+Firefox and VoiceOver+Safari as the two most representative screen-reader combinations, with exact inspection shortcuts). The accessibility how-to guide adds landmark-region guidance (all editor content should sit inside a landmark region) and points to the `navigateRegions` package for cross-region keyboard navigation. No ARIA-attribute-level static-check API list was sourced from documentation — that remains a clean-room authoring task.

**Public issues:** 8 numbered Gutenberg issues, each matching a distinct clause of the failure statement (unreachable controls, focus-ring visibility, disabled-state distinguishability, reduced-motion, high-contrast-mode legibility, empty-link announcement).

**External comparators (reference-only unless noted):** WordPress/gutenberg's own UI-review skill (adapt-eligible — weak-evidence shape 3, read and classified by operator 2026-09-25; see the candidate-catalog additions); a WCAG 2.2 AA audit skill with an explicit Block Editor section, verified via axe-core+Playwright — the only comparator that runs a real automated check rather than stating a checklist.

**Internal evidence (authorized 2026-09-25):** n=1 (contrast) — weak, not load-bearing for this gap's disposition.

**Disposition:** extend-existing · **Targets:** `/wordpress-planner.block` P2, P6; `/wordpress-theme-critic` P5 · **Oracle:** static partial (packet check that custom toolbar buttons carry a `label`); runtime AT/keyboard operability `blocked-on:#39` · **Comparators (reference-only unless noted above):** WordPress/gutenberg `design-system-ui-review`, adityaarsharma/orbit `orbit-accessibility` · **If internal evidence had not been authorized:** no change (n=1 was never load-bearing).

---

## G2 — Admin-screen / editorial-workflow UX

**Failure:** an editor's daily wp-admin work is slow or confusing — cluttered screens, listing columns that hide what they need, scattered settings, UI shown to roles that cannot act on it.

**Public sourcing:** THIN — the weakest developer-documentation leg in this map. No classic wp-admin mechanism (meta boxes, admin columns, Settings API grouping, dashboard widgets) was sourced by any fetch. The one sourced mechanism is Block/Site-Editor-scoped, not classic-admin: a filter that gates Editor UI visibility by capability check, plus four related data hooks that can restore capability to Administrators after a global restriction — a real, sourced answer to "UI shown to roles that cannot act on it," but for the editing surface, not the admin screens this gap centers on.

**Public issues:** 2 (admin list-screen UX, DataViews-based screens).

**External comparators:** an admin-UI build/debug skill with an explicit keyboard-nav and focus-ring verification line (MIT, adapt-eligible); an admin list-table skill with a `WP_List_Table` required-override contract and a candidate-cited accessible-name rule for primary row headers, version-dated by the candidate to a later WordPress release than this repo's floor (resolved: `@since 7.1.0`, above this repo's WP 7.0 floor) (MIT, adapt-eligible).

**Internal evidence (authorized 2026-09-25):** n=13, plus a role/permission-confusion cluster of n=5 and a set of role-specific failure patterns that an admin-only (non-role-aware) walkthrough would systematically miss. This evidence layer carries G2's disposition almost entirely.

**Disposition:** extend-existing — **full scope** (internal evidence authorized 2026-09-25) · **Targets:** `/wordpress-planner.plugin` P2, P3; `/wordpress-planner.content-model` P5 (list-column prompt) · **Oracle:** runtime, role-aware, `blocked-on:#39`; static partial is presence-only (capability-argument greps) · **Comparators:** the two MIT candidates above · **If internal evidence had not been authorized:** this would have been the largest swing in this map — scope would narrow to the sourced role-conditional-visibility slice only (the Editor-UI capability filter and its restore hooks); the admin-screen information-architecture half (columns, settings grouping, dashboard widgets) would become defer, entry condition a successful fetch of WordPress's own design-handbook material or a second evidence set; priority would drop from 2nd to last (5th) of the five audited gaps.

---

## G3 — Editorial-constraint UX

**Failure:** an editor hits an invisible wall — blocks absent from the inserter with no explanation, regions that will not edit, actions failing without feedback.

**Public sourcing:** VERY STRONG. A full how-to-guide series ("Curating the Editor Experience") answers not just which APIs exist but how an editor *experiences and is told about* each constraint: content-only editing hides non-content blocks from list view and canvas, shows a flat content list in the block Inspector, and exposes a "Modify" toolbar link the editor can use to reach full design tools; blocks locked by theme/pattern authors are unlockable by editors by default unless a settings flag (administrators-only by default) says otherwise; inserter allow/deny lists; a heading-level curation attribute; toggles for code editing, responsive editing, and block-state editing; a client-side filter that can restrict a setting per block location, neighboring block, or the current user's role; a server-side filter that can strip block supports entirely; starter-pattern prioritization by block type, post type, or template type. The public leg alone documents every constraint-communication mechanism the rubric asks for.

**Public issues:** 3, matching the "invisible wall" failure statement directly.

**External comparators:** WordPress/agent-skills' pattern-verification skill, which runs a real WordPress-Playground-CLI check that a locked template actually resists editing and that inserter visibility matches expectation (license re-read pending, otherwise adapt-eligible per this repo's catalog); a near-duplicate/superset comparator with the same runtime-verification block plus a design-token framework (GPL-3.0, adapt-eligible); a role-aware Playwright comparator asserting lock state and inserter allowlists by role (reference-only, license evidence weak).

**Internal evidence (authorized 2026-09-25):** n=38 — the largest single evidence bucket of any gap in this discovery, including a "can't find the control" sub-pattern and an "optional feature not discoverable" sub-pattern. Not load-bearing for this gap's priority — the public leg alone already clears the bar.

**Disposition:** extend-existing, **priority 1** · **Targets:** `/wordpress-planner.content-model` P5 editorial-guardrails sub-phase; `/wordpress-planner.block` P2; `/wordpress-theme-critic` P4 · **Oracle:** static — real and deterministic (presence/values of the lock- and allow-list-related settings named above); runtime "the editor actually sees the cue" is `blocked-on:#39`, though an ephemeral-environment login path exists as a complement, not a replacement · **Comparators:** the three named above · **If internal evidence had not been authorized:** no change.

---

## G4 — Runtime editor verification

**Failure:** nothing proves what an editor actually sees or can do.

**Public sourcing:** seven external comparators carry genuine login→act→verify runtime protocols against a real WordPress editor session (cookie-based login, interactive form-fill, or a browser-automation MCP), spanning post creation, image insertion, media upload, and console/network error capture. None matches the exact mechanism proposed for this repo's own runtime-oracle dependency (a CLI-generated login link); all are comparator evidence that the pattern class — scripted login plus role-aware runtime checks — is a common ecosystem shape.

**Internal evidence (authorized 2026-09-25):** n=0 — correctly so; this gap is not persona-observable from a support-ticket stream.

**Disposition:** defer — `blocked-on:zivtech/wp-ai-skills#39` · **Targets:** none now; on landing, a WordPress-environment capability probe should report login-link capability and available roles, and executor verification commands should gain a role parameter · **Oracle:** it is the oracle · **Comparators (reference-only):** all seven runtime-protocol candidates, catalogued as comparators for the #39 workstream · **If internal evidence had not been authorized:** no change.

---

## G5 — theme.json editor-visible settings

**Failure:** an editor's design controls do not match what the theme promises — tokens missing from Site Editor panels, restrictions failing to hide options, preset labels wrong.

**Public sourcing:** STRONG — the largest single rating change in this discovery, after a documentation fetch that had originally 404'd was recovered. The theme.json living reference gives the full settings schema: a single boolean bundle that turns on a named set of UI controls; a boolean that can hide block-visibility controls entirely while still honoring saved attributes; the full boolean property list controlling exactly which color-related Global Styles/Inspector controls appear, plus the preset arrays that populate the pickers. The companion Global Settings & Styles guide gives the exact `add_theme_support()` ⇔ `theme.json` setting equivalence table — the precise diagnostic for "a restriction failed to hide an option" (a boolean that didn't take, or a legacy call a newer theme.json setting should have superseded but didn't) — and the exact preset-naming contract (a CSS custom property pattern and a class pattern) that a skill would check preset labels against.

**Public issues:** 6, including the most-discussed issue in the entire sampled corpus (engagement in the high double digits) concerning Style Book discoverability for classic themes.

**External comparators:** a theme-styling skill with a theme-type-aware decision sequence for where a style value belongs (MIT, adapt-eligible); WordPress/agent-skills' block-themes skill, which includes a Site-Editor-reflects-changes verification step; a presets-only validation checklist (MIT, adapt-eligible); a pixel-diff Site-Editor-vs-frontend comparator with role-aware lock-state checks — the only candidate in the survey combining pixel-diffing with role-aware lock-state checks in one skill (license evidence weak, reference-only).

**Confirmed:** the repo's already-catalogued `wpds` skill and its companion pattern-authoring doc do not cover this settings→UI-control mapping — no overlap with a clean-room G5 extension.

**Internal evidence (authorized 2026-09-25):** n=1, self-flagged borderline — weak, not load-bearing.

**Disposition:** extend-existing, priority 2 · **Targets:** `/wordpress-planner.theme` P2, P4, P8; `/wordpress-theme-critic` P3, P4 · **Oracle:** the only gap in this map whose oracle is fully static and login-free (parse theme.json settings, diff against `add_theme_support()` calls, check expected preset CSS variables/classes on the public front end); runtime "control renders with the right label in the Site Editor" is `blocked-on:#39` · **Comparators:** the four named above · **If internal evidence had not been authorized:** no change.

---

## Sixth-gap candidates (persona-checklist completeness check)

A 7-stage, 30-item editor-persona journey checklist (draft → edit → constrained editing → media → review → publish → admin housekeeping, plus a cross-cutting AT/keyboard pass) was built from the public Gutenberg-issue corpus and the internal-evidence layer. It touches every one of G1–G5 with at least one item. **Verdict: the five-gap list is not complete against the persona.** Seven distinct clusters surfaced that do not map cleanly onto G1–G5; none were dropped silently.

| Candidate | Public evidence | Internal evidence | Disposition |
|---|---|---|---|
| N1 — Media caption/credit workflow | None in the sampled corpus (search-scope gap — the sample was a11y/feedback-labeled only, not a confirmed absence) | internal evidence (authorized 2026-09-25), n=12 — the largest sixth-gap cluster found by either leg | Extend-existing (`/wordpress-planner.content-model` P4/P5) — internal evidence authorized 2026-09-25; previously the most layer-sensitive call in this discovery, now resolved |
| N2 — Media library UX (findability, crop persistence) | 3 adjacent issues (media-editor modal iteration) | internal evidence (authorized 2026-09-25), n=3 | Defer — mostly core-owned UI; fold one line into `/wordpress-planner.theme` P6 if image sizes are touched |
| N3 — Preview fidelity (any cause) | 2 issues + 5 converging external comparators | internal evidence (authorized 2026-09-25), n=2 | Extend-existing — already FIRST-CLASS as editor/frontend parity; add mechanism names and an oracle; kept as its own coverage-matrix row since it is broader than G5 (non-theme.json causes also apply) |
| N4 — Onboarding / in-product guidance | 1 adjacent issue | internal evidence (authorized 2026-09-25), n=3 | Split — in-product-guidance slice extends `/wordpress-planner.content-model` P5 (small, prose-only); the training-program half is out-of-scope for this repo |
| N5 — Revisions / audit-trail visibility | 2 issues | internal evidence (authorized 2026-09-25), n=1 | Defer — existing coverage (`revisions_enabled` and related fields already named in `/wordpress-planner.content-model`) is adequate for what a skill controls; core owns revision prominence |
| N6 — Accessible-output authoring guardrails (new; derived from a public front-end walk) | A public front-end walk of one WordPress site found empty `alt` text on 5 of 14 in-body images with a positive control (sibling images in the same block type had well-written alt — indicating a workflow/nudge gap, not a capability gap), two independent heading-level-skip instances, and a site logo with blank alt and no fallback | none | Extend-existing, medium priority (`/wordpress-planner.content-model` P5; `/wordpress-planner.theme` P5) — lowest-confidence extend call in this discovery: single site, single team; the positive control is what keeps it above defer rather than a training-only explanation |
| Real-time-collaboration accessibility | 4 issues, one a formal tracking issue | none (scope/timing gap in the evidence window, not disconfirming) | Defer, recorded as a G1 sub-case — a core-feature bug, not a client-facing build lever |
| Global Styles / Style Book discoverability | Strong by engagement (2 of the highest-engagement issues in the sampled corpus) | none | Extend-existing as a G5 sub-case (`/wordpress-planner.theme` P2) |
| Content duplication/clone | none | internal evidence (authorized 2026-09-25), n=1 | Defer — too thin on a single leg |
| Print-adjacent workflow | none | internal evidence (authorized 2026-09-25), n=1 | Out of scope — borderline frontend-rendering concern, excluded by this discovery's negative space |

**A gap in the checklist method itself, recorded rather than hidden:** the "what editors are told the UI does" documentation-mismatch signal and a set of formal usability-test reports both failed to fetch (navigation-chrome-only pages, no article content recovered); this is a method limitation, not evidence that documentation mismatches don't occur.

---

## Summary — sourcing strength by gap

| Gap | Public sourcing | Internal evidence | Combined |
|---|---|---|---|
| G1 — Editor accessibility | MEDIUM | weak, authorized 2026-09-25 | Improved from the plan's original thin expectation; still no static-check API enumeration |
| G2 — Admin-screen UX | THIN | moderate-strong, authorized 2026-09-25 — carries the gap | Internal evidence is doing most of the evidentiary work; public leg alone would not clear the extend bar |
| G3 — Editorial-constraint UX | VERY STRONG | largest bucket of any gap, authorized 2026-09-25, not load-bearing | Public leg alone documents every constraint-communication mechanism in the rubric |
| G4 — Runtime verification | Complete (comparator survey; blocked on #39) | none, correctly | Complete as a dependency record |
| G5 — theme.json settings | STRONG | weak, authorized 2026-09-25 | Public sourcing solid on its own; internal thin |

---

## Runtime evidence: local role-based editor walk (2026-09-25)

This is a separate evidence layer from the internal (client-ticket) evidence
cited above: a throwaway local `wp-env` site, not client data, run to test
whether a runtime walk finds defects a static/source review would miss.

**Method:** `wp-env` 11.12.0 stood up a throwaway local site (WordPress
7.1.2, Twenty Twenty-Five) with a synthetic scenario mu-plugin exercising
G3 (a `template_lock:"all"` CPT and a `templateLock:"contentOnly"` pattern),
N1 (a classic meta box surfacing registered post meta), G2 (a
capability-gated Settings page and list-table column), and G1/N6 (seed
content with a heading-level skip and a missing-alt image). One-time login
links (`wp login as <ID>`, the #39 tooling pattern via
`aaemnnosttv/wp-cli-login-command`) authenticated as Editor (the primary
role walked), Author, and Contributor, with a single Administrator spot
check used only to determine whether a defect was role-specific.
`agent-browser` drove accessibility-tree and keyboard passes against the
block editor and wp-admin screens. This is n=1 site, one walker, synthetic
content — directional runtime evidence, not a quality-comparison claim (see
Evaluation Boundary).

**Findings table:**

| # | Finding | Acting role | Gap | Origin | Severity | Static-catchable by an existing skill? |
|---|---|---|---|---|---|---|
| 1 | A classic meta box (`context:"side"`) for a registered post meta field renders only inside the settings sidebar's post-type tab (Gutenberg mounts side boxes as `extraSidebarPanels`), not in the "Meta Boxes" area below the canvas that holds `normal`/`advanced` boxes. The sidebar is closed on first load, so the credit field has no visible entry point until the editor opens Settings on the post tab. | Editor; also checked as Administrator | N1, G2 | Resolved as a discoverability gap, not a defect. The first walk and a first reproduction both reported the box as permanently `display:none` and attributed it to core. A targeted check with the sidebar open on the Exhibit tab showed the field on screen with its stored value; `.edit-post-meta-boxes-area.is-side` exists only in that state. | MINOR (discoverability) | No |
| 2 | On a fully template-locked CPT (`template_lock:"all"`), opening the Block Inserter shows a real, accessibly-exposed panel whose Blocks tab reads only "No results found." — no copy anywhere explains the template is locked. | Editor | G3 | CORE-WP (Gutenberg's inserter has no dedicated empty-state message for a fully locked template) | MAJOR | Partly — a reviewer could flag the risk abstractly; the literal "No results found." text needed a live run to surface. |
| 3 | On a `templateLock:"contentOnly"`-locked pattern, the inner Heading/Paragraph blocks give no icon, label, tooltip, or menu item indicating the structure is locked; the documented "Modify" escape-hatch link did not appear for this pattern instance in this build. | Editor | G3 | CORE-WP (Gutenberg's Lock UI doesn't reflect `templateLock`; the "Modify" affordance was absent/version-gated here) | MAJOR | Partly — the abstract risk (two non-overlapping lock mechanisms) is flaggable in review; the concrete absence of any in-UI explanation needed a live run. |
| 4 | A heading-level skip (H2→H4) is correctly detected and labeled in Document Overview, but only under the non-default "Outline" tab, with no inline warning and no publish-time gate; the skip and the post's empty `alt=""` on a non-decorative image both reached the published frontend unchanged. This mirrors the public front-end walk already cited under G1/N6. | Editor | G1 / N6 | CORE-WP (the Outline checker is correct; no publish-time gate exists) | MAJOR (discoverability of the in-editor warning); CRITICAL (the published empty `alt` reaching real visitors) | Partly — a content/a11y-aware static review of the seeded HTML could catch the heading skip and empty alt directly; it could not know whether the editor UI surfaces a warning without running the editor. |
| 5 | Contributor role: the Image block placeholder text promises "Drag and drop an image, upload, or choose from your library," but the only control rendered is "Insert from URL" — Contributor lacks `upload_files`, so the instructional copy overstates what the role can do. | Contributor | NEW (role-clarity, adjacent to G2 — the #39 role-specificity pattern) | CORE-WP (Gutenberg's `MediaPlaceholder` conditionally hides Upload/Library by capability but doesn't adjust the instructional copy) | MAJOR | No — this needs authenticating as a lower-privileged role and cross-referencing rendered copy against role capabilities; it isn't visible from source alone. |

**Positive controls (behaved correctly by role, not findings):** Publish vs.
"Submit for Review" button text switched correctly between Author and
Contributor; the Exhibits list rendered read-only (no edit link/row
actions) for Contributor on posts it doesn't own.

**What only a runtime walk found:** findings 1, 2, 3, and 5 all required
live DOM/role evidence: where a side meta box actually mounts, literal
empty-state copy, an absent lock-status affordance, and capability-mismatched
placeholder text.

**Method caveat:** runtime walks can be confidently wrong about UI state. Finding 1
was misclassified twice, as a hidden control and then as a core defect, because neither
pass opened the settings sidebar. A walk must record the editor chrome state
(sidebar open or closed, active tab, panel preferences) before it reports a control
missing, and must re-check the claim in every chrome state. None of the five existing wp-ai-skills phase reviewers
(`wordpress-critic`, `wordpress-theme-critic`, `wordpress-security-critic`,
`wordpress-performance-critic`, `wordpress-site-audit`) execute the block
editor or authenticate as a lower-privileged role; all five are source/spec/
public-surface reviewers as currently written.

**Oracle note for #39:** the walk's own cleanup step is a useful data point
for the eventual #39 oracle runbook — `wp plugin deactivate`/`delete
wp-cli-login-server` removes the companion plugin but leaves the underlying
`aaemnnosttv/wp-cli-login-command` WP-CLI package installed (`wp package
uninstall aaemnnosttv/wp-cli-login-command` handles that explicitly; for a
fully throwaway environment, `wp-env destroy` is the simpler equivalent).
Verified cleanup result for this walk: a post-cleanup `wp plugin list`
confirms `wp-cli-login-server` is absent, leaving only `hello` (inactive)
and the walk's own `editor-walk-scenarios` (must-use).

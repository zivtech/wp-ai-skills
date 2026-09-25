# Fixture: migration-mode-component-heavy

Scenario: a cultural-institution site is migrating from a legacy component-based
CMS to WordPress. This activates migration mode.

Synthetic source inventory (no client data), with manifest ids in backticks:

- Content types: `event` (recurring, multiple date sets per event), `story`
  (single-author narrative), `exhibit` (references related `story` and
  `person` items).
- Vocabularies: `event_type` and `audience` are both attached to `event`;
  `topic` is attached to both `story` and `exhibit`.
- Reusable page-building components ("paragraph"-style, embeddable inside any
  content type): `hero_component`, `grid_list_component`,
  `accordion_component`, `featured_object_component` (appears identically on
  many pages and should stay in sync when edited from one place),
  `quote_component`, `map_component`.
- A per-item "exclude from public listings" flag stored as a taxonomy term
  reference rather than a boolean field.
- A non-node surface: `site_footer_block`, a block placed in every page's
  footer region containing the institution's address, hours, and social
  links (facts, not layout) — this is not attached to any single content
  type; it lives outside any node, the way a placed/reusable region block or
  a menu does in many source CMSs.

The candidate output must run this planner's migration mode: build a source
model inventory for every item above (including the non-node
`site_footer_block`), and give each one exactly one keyed
`Disposition row (<item-id>): <token> - <rationale>` record in Migration And
Validation Plan, addressed by its manifest id above. It must cite `event`'s
and `exhibit`'s field cardinality (recurring dates and related-item
references are multi-value, not single), and choose a component disposition
token (`custom-block` / `pattern` / `synced-pattern-with-overrides` /
`core-blocks` / `drop`) with a stated rationale for each of the six
reusable components. For `site_footer_block`, apply the rule that facts
embedded inside a site-wide block become a site setting/option bound into
the owning template part rather than literal text in the part — the expected
disposition token is `site-option` (or `template-part` if it justifies why
the facts stay unbound). It must not merge `event_type` and `audience`
(co-attached to `event`) or `topic` and any other vocabulary attached to the
same type. It must run the editorial-guardrails phase — a
`Content type: <post_type>` declaration plus a keyed
`Lock level (<post_type>): ...` decision, and a keyed
`Lock level rationale (<post_type>): ...` for every `false`, for each of
`event`/`story`/`exhibit` — and the storage decision rule (a keyed
`Editing surface (<meta_key>): ...` for every `Binding source (<meta_key>): ...`).
It must not claim benchmark, release, or current-version status without
evidence, and must name the downstream planner/executor/critic handoff.

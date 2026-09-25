# Fixture: migration-mode-component-heavy

Scenario: a cultural-institution site is migrating from a legacy component-based
CMS to WordPress. This activates migration mode.

Synthetic source inventory (no client data):

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

The candidate output must run this planner's migration mode: build a source
model inventory for every item above, give each one exactly one disposition
row in Migration And Validation Plan, cite `event`'s and `exhibit`'s field
cardinality (recurring dates and related-item references are multi-value,
not single), and choose a component disposition (custom block / core block
plus pattern / synced pattern with overrides / flatten to core blocks / drop)
with a stated criterion for each of the six components. It must not merge
`event_type` and `audience` (co-attached to `event`) or `topic` and any other
vocabulary attached to the same type. It must run the editorial-guardrails
phase (a `Lock level` decision per content type) and the storage decision
rule (an `Editing surface` for anything bound into a block). It must not
claim benchmark, release, or current-version status without evidence, and
must name the downstream planner/executor/critic handoff.

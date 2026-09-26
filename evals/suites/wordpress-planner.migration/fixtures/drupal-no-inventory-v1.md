# Focused Fixture: Drupal Source Without An Inventory

Plan a migration of an invented regional transit agency's Drupal 10 site into
WordPress. Pages are built from Paragraphs, and the site has config export
access. No `source-structure.json` inventory has been produced, and none is
supplied. The requester asks for a full migration plan anyway.

## Expected Planning Focus

- Apply the Phase 1 source-structure gate: the source is Drupal 8 or later with
  config export, so the plan must not plan past Phase 1 without the inventory.
- Record `Source structure file: missing - <reason>` in Source Audit and tell
  the user to run the `drupal-source-inventory` skill (zivtech/drupal-meta-skills)
  first.
- Keep every required heading, but leave Target Mapping and later sections as
  explicit `Decision required:` items. Do not invent components or emit
  `Structure disposition` rows.
- Do not claim a Gutenberg transformation that has not been planned.

# Focused Fixture: Paragraphs-Heavy Source With A Supplied Inventory

Plan a migration of an invented water utility's Drupal 10 site into Gutenberg
blocks in `post_content`. Pages are built from Paragraphs. The
`drupal-source-inventory` skill already ran, and its `source-structure.json`
(contract `contracts/source-structure/` 1.2.0, zivtech/drupal-meta-skills) is
supplied as `paragraphs-heavy-v1.source-structure.json`.

## Supplied `source-structure.json` (excerpt)

Every component, keyed by its contract `key` (`{kind}:{id}`):

| Key | Label | Fields (role) | Live instances |
|---|---|---|---|
| `node_bundle:service_page` | Service Page | body (PROSE), field_sections (REF) | n/a |
| `node_bundle:outage_notice` | Outage Notice | field_outage_start (FACT), field_affected_streets (FACT, multi-value), field_sections (REF) | n/a |
| `paragraph_type:hero_banner` | Hero Banner | field_heading (PROSE), field_image (MEDIA), field_dark_theme (PRESENTATION) | 140 |
| `paragraph_type:rate_table` | Rate Table | field_tier_name (PROSE), field_rate_per_kgal (FACT, reviewed), field_effective_date (FACT, reviewed) | 36 |
| `paragraph_type:faq_item` | FAQ Item | field_question (PROSE), field_answer (PROSE) | 410 |
| `paragraph_type:text_with_image` | Text With Image | field_text (PROSE), field_image (MEDIA), field_image_left (PRESENTATION) | 520 |
| `paragraph_type:service_area_list` | Service Area List | field_listing (CONFIG, embeds a View) | 18 |
| `paragraph_type:callout_band` | Callout Band | field_style (PRESENTATION), field_text (PROSE) | 95 |
| `paragraph_type:legacy_iframe` | Legacy Iframe | field_src (CONFIG) | 0 |
| `paragraphs_library_item:1` | Storm Preparation Checklist | reused by 9 hosts | 1 |
| `block_content:1` | Footer Contact (main) | address and phone facts | n/a |
| `placement:footer_contact_main` | Footer Contact placement | footer region | n/a |
| `menu:main` | Main navigation | | n/a |

The library item and the block_content entity share the bare id `1`.

## Expected Planning Focus

- Record `Source structure file:` in Source Audit.
- In Target Mapping, give every component exactly one
  `Structure disposition (<kind>:<id>): <VERDICT> - <WordPress destination>`
  record, using the contract's verdicts (STRUCTURED, QUERY, REUSE, LAYOUT,
  CONTENT, DROP, DEFER), plus `Dispositioned: 13/13`. DROP and DEFER rows give a
  reason instead of a destination.
- Keep the reviewed rate facts queryable instead of flattening them into markup.
- Add `non-empty-destination` to `Semantic oracle fields:` for components that
  land as CONTENT, and name how empty `post_content` is detected.
- Satisfy the Gutenberg migration records, idempotent reruns, rollback, and
  editor/frontend proof.

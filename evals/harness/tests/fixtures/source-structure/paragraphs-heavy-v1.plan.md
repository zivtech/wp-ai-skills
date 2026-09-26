## Migration Scope
Migrate an invented water utility's Drupal 10 site, whose pages are built from
Paragraphs, into Gutenberg blocks in `post_content`. This plan does not prove
production cutover readiness.

## Current-State Evidence
The source inventory was produced by `drupal-source-inventory` and supplied as
`paragraphs-heavy-v1.source-structure.json` (contract 1.2.0). A disposable
wp-env fixture exists for import rehearsals.

## Source Audit
Source structure file: paragraphs-heavy-v1.source-structure.json

The inventory lists 13 components across two node bundles, seven paragraph
types, one Paragraphs Library item, one block_content entity, one placement,
and one menu. `legacy_iframe` has zero live instances. The library item and
the block_content entity share the bare id `1`, so every row below is keyed by
`{kind}:{id}`.

## Target Mapping
Map source Paragraphs to core blocks in `post_content`; rate facts move to
registered post meta; record every unsupported source node.

Gutenberg target: post_content
Block mapping: core+custom
Unsupported content: accounted

Dispositioned: 13/13
Structure disposition (node_bundle:service_page): CONTENT - page post type, body and sections serialized into post_content
Structure disposition (node_bundle:outage_notice): STRUCTURED - outage_notice custom post type with registered meta outage_start and affected_streets
Structure disposition (paragraph_type:hero_banner): CONTENT - core/cover with core/heading
Structure disposition (paragraph_type:rate_table): STRUCTURED - rate_tier meta via register_post_meta(), rendered by a bound core/table
Structure disposition (paragraph_type:faq_item): CONTENT - core/details
Structure disposition (paragraph_type:text_with_image): CONTENT - core/media-text
Structure disposition (paragraph_type:service_area_list): QUERY - core/query filtered by the service_area taxonomy
Structure disposition (paragraph_type:callout_band): LAYOUT - core/group block style callout-band
Structure disposition (paragraph_type:legacy_iframe): DROP - zero live instances in the inventory
Structure disposition (paragraphs_library_item:1): REUSE - synced pattern storm-preparation-checklist
Structure disposition (block_content:1): STRUCTURED - site options bound into the footer template part
Structure disposition (placement:footer_contact_main): LAYOUT - footer template part
Structure disposition (menu:main): STRUCTURED - wp_navigation post main-navigation

## Transform And Execution Plan
Use WordPress block serialization, stable source identity, and an idempotent,
rerunnable two-pass import.

Serialization API: serialize_blocks
Rerun policy: idempotent

## Validation Plan
Use `parse_blocks()` for block validation, a semantic oracle for expected text
and href values, a Playwright editor smoke, and a separate frontend smoke.
Every item whose source component is dispositioned CONTENT must import
non-empty `post_content`; check with `wp post list --post_type=page --field=ID`
and `wp post get <id> --field=post_content`.

Block validation oracle: parse_blocks
Semantic oracle: required
Semantic oracle fields: text,href,attributes,unsupported,non-empty-destination
Editor oracle: required
Editor oracle method: playwright-clone-save-reload-restore
Frontend oracle: required
Frontend oracle method: playwright-selector-visible-text

## Rollback And Monitoring
Keep run-scoped before-images and execute a rollback test in wp-env.

## Assumption Register
Assumption: the inventory's role assignments marked reviewed are correct.

## Test Strategy
Use the supplied inventory as the canonical source fixture, plus one
malformed-paragraph negative fixture.

Fixture: required
Fixture identity: paragraphs-heavy-v1

## Acceptance Criteria
Every inventoried component has exactly one structure disposition, and every
unsupported node is accounted for.

## Critic Handoff
Review serialization, idempotence, destination coverage, editor evidence, and
rollback evidence.

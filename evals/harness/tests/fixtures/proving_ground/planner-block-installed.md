## Block Scope
Build one dynamic `acme/runtime-card` block. This does not claim cross-browser coverage.

Block identity: acme/runtime-card
Primary serialization: dynamic
Interaction pattern: server-rendered block

## Current-State Evidence
The plugin registers blocks from `block.json` with `register_block_type()`.

Proving ground: /home/ci/wp-ai-skills@abc1234

## Metadata And Attribute Plan
`block.json` declares the block name, title, and category. The block has no
attributes and no saved content; its saved-markup contract is intentionally empty.

Metadata file: block.json
Attributes: none
Saved markup: self-closing

## Render And Interaction Plan
Use `render_callback` for dynamic output. A missing record is a render failure
that returns empty output after logging an error.

Render surface: render_callback
Failure behavior: log-and-return-empty

## Compatibility And Migration Plan
There is no existing saved content. Keep a saved-content fixture containing the
self-closing block delimiter so future metadata changes can be checked.

Compatibility decision: new-contract
Saved-content fixture: required

## Security Performance And Accessibility Notes
The callback uses `esc_html()` and has no REST, SQL, upload, or remote-call path.

## Assumption Register
Assumption: the host loads the plugin before editor smoke; the runtime oracle verifies it.

## Test Strategy
Run a Playwright editor smoke for insertion/save and a separate frontend smoke
for the `.wp-block-acme-runtime-card` output, plus PHPUnit for the callback.

Editor oracle: required
Editor oracle method: playwright-insert-save-reload
Editor oracle block: acme/runtime-card
Frontend oracle: required
Frontend oracle method: playwright-selector-visible-text
Frontend oracle selector: .wp-block-acme-runtime-card
Frontend expected text: Runtime block smoke

## Acceptance Criteria
The editor saves the block and the front end renders the fixture-owned text.

## Executor Handoff
Generate the exact block files and recorded verification packet.

## Critic Handoff
Send the packet to wordpress-critic after the runtime evidence exists.

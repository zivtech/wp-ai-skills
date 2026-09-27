# Request: plan the editor-accessibility fix for an existing block

Plan this block change now and write the complete saved output. The scenario, the code excerpt, and the expectations below are the brief; treat them as the request, not as a description of a test.

Scenario: extend an existing repository-owned custom block, `acme/callout-card`
(an invented block, not tied to any real project). The block already ships
and is in editorial use; this change only touches its editor UI, not its
saved markup or attributes.

**Existing `edit.js` excerpt (invented, for this fixture only):**

```js
import { BlockControls, InspectorControls } from '@wordpress/block-editor';
import { ToolbarGroup, ToolbarButton, PanelBody, Icon } from '@wordpress/components';
import { pin, rotateLeft } from '@wordpress/icons';

export default function Edit( { attributes, setAttributes } ) {
	return (
		<>
			<BlockControls>
				<ToolbarGroup>
					<ToolbarButton icon={ pin } onClick={ () => setAttributes( { pinned: ! attributes.pinned } ) } />
					<ToolbarButton icon={ rotateLeft } onClick={ () => setAttributes( { flipped: false } ) } />
				</ToolbarGroup>
			</BlockControls>
			<InspectorControls>
				<PanelBody>
					<p>Callout options go here.</p>
				</PanelBody>
			</InspectorControls>
		</>
	);
}
```

The two `ToolbarButton` elements are icon-only and carry no `label` or
`title`, and the `PanelBody` carries no `title`. The requested change is to
plan the fix for this specific editor-accessibility gap in the existing
block, not to redesign the block's functionality or its saved markup.

The candidate output must name each missing accessible name concretely: a
`label` (or `title`, since `ToolbarButton` accepts either) for the pin
toggle button, a `label`/`title` for the flip-reset button, and a `title`
for the `PanelBody`. It must plan for keyboard reachability of these
controls (Tab/Shift+Tab reaching each one, Enter/Space activating it) and
for reduced motion in the editor preview via `useReducedMotion` from
`@wordpress/compose` if the block has any editor-preview animation. It must
name a keyboard and screen-reader pass over this specific toolbar and panel,
tagged `runtime: manual-walk`, rather than asserting the fix is complete
from the static edit alone. It must not propose changing the block's saved
markup, attributes, or `render.php` to fix this, since the defect is
entirely in the editor-only controls shown above.

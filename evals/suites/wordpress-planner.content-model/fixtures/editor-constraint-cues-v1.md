# Fixture: editor-constraint-cues-v1

Scenario: an invented regional civic-trust organization is moving two content
types onto WordPress. No client, site, or ticket is real; every name below is
invented for this fixture.

- `case_study` is a structured content type: editors fill in a fixed set of
  sections (summary, outcome, partner list) inside a layout the organization
  does not want editors to rearrange. The brief cites repeated editor
  complaints on the prior page-builder tool, where editors dragged sections
  into a broken order.
- `field_note` is a free-form content type: editors compose short narrative
  updates with whatever mix of paragraphs, images, and pull-quotes fits the
  story. The brief explicitly wants full composition freedom here.
- Two editor roles interact with these types differently: `staff_editor`
  (in-house, trained on the block editor) and `contributor` (occasional
  outside contributors filing `field_note` drafts for staff review).

The candidate output must run the editorial-guardrails sub-phase for both
content types: declare `Content type: case_study` and
`Content type: field_note`, then give each its own keyed lock-level decision
(`case_study` should land on `contentOnly` given the prior page-builder
friction cited above; `field_note` should land on `false` with its own
keyed rationale, since silence or a rationale borrowed from `case_study` is
not sufficient). For each locked constraint, it must name the concrete cue
the editor actually sees for that constraint (not just the underlying
mechanism) and say where the constraint's rationale is recorded so a future
editor can find out why the section is locked. It must decide, per role, not
per content type, whether `canLockBlocks` stays on for `staff_editor` versus
`contributor`, and which `block_editor_settings_all` switches apply to which
role. Because `case_study`'s summary section constrains editors to a single
heading level, the plan must curate that heading level with `levelOptions`.
Every named constraint cue must be confirmed as the role that would actually
encounter it, tagged `runtime: manual-walk`, not left as a static claim
alone. The output must not default `field_note`'s lock level to `false`
without its own stated rationale, and must not describe a block's simple
absence from the inserter as self-explanatory to an editor who has not been
told why.

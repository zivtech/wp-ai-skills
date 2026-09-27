# Request: plan photographer credit, caption, and alt text for images

Plan this content model now and write the complete saved output. The scenario and the expectations below are the brief; treat them as the request, not as a description of a test.

Scenario: an invented regional newsroom-style publisher wants photographer
credit alongside every published image. No client, site, or ticket is real;
every name below is invented for this fixture.

- Every published photo needs a visible photographer credit line displayed
  directly under the image on the front end, separate from the image's
  caption text.
- Images also carry a caption (a short editorial description of what is
  shown) and alt text (for screen readers), both already in use today.
- Some images appear inside galleries, where each individual photo in the
  gallery needs its own caption.
- An editor on the current team has been typing the photographer's name
  directly into the caption field (for example "Photo: J. Alvarez") as a
  workaround, and leadership wants a model that stops that workaround from
  being necessary.

The candidate output must model photographer credit as attachment meta,
registered for the `attachment` object type with REST exposure, and name a
concrete editing surface for it (not a template-level-only or render-only
surface). It must keep the caption as the existing core image caption
mechanism rather than folding credit text into it, and must state explicitly
that a credit typed into the caption field is the failure mode being
designed against. It must address gallery images individually: each photo
in a gallery keeps its own caption. Finally, it must give one explicit
statement of where each of the three fields — alt text, caption, and
credit — is set by an editor and where each one renders on the front end,
so the three do not blur together into one field in the plan.

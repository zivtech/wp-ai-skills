# Output-Contract Oracle: Unbounded Raw-HTML Stripping (2026-09-27)

`evals/harness/validate_wordpress_skill_output.py` decides which text is
authoritative before it looks for headings, decision records, verification
oracles, and negative-space language. Part of that pass blanks raw HTML a
reader would never see rendered: comments, CDATA, processing instructions,
declarations, and raw-text elements such as `<script>`. Until 2026-09-27 that
pass ran as plain regexes over the whole document, before and independently of
the fenced-code pass, and every pattern ran to its closing delimiter *or the end
of the document*.

## What went wrong

A WordPress PHP file omits the closing `?>` tag; that is the coding standard,
not an omission. Executor packets embed each generated file in a fenced code
block, so the first `<?php` in a packet matched the processing-instruction
pattern `<\?.*?(?:\?>|$)` and, with no `?>` anywhere, blanked everything from
that point to the end of the document. Every heading after the first PHP file
was gone before `required_output_headings` ran, and the text that
`verification_specificity` and `negative_space` read was gone with it.

The same class of defect hid a second shape: a raw-text element name inside a
backtick code span (`` `<script>` `` in critic prose) matched the raw-text
element pattern and blanked the document up to the next literal `</script>`,
which in the recorded security-critic output was 115 lines later.

## Measurement before the change

Corpus: every saved output the oracle is applied to in this repository, 65
documents in three groups.

| Group | Documents | Contain `<?php` | `<?php` with no `?>` |
|---|---:|---:|---:|
| `evidence/**/raw/**` with a recorded `*.contract.json` | 52 | 4 | 3 |
| `evals/suites/*-executor/examples/*.materializable-packet.md` | 12 | 9 | 6 |
| `evals/handoff/*/packet.md` | 1 | 1 | 1 |

Counterfactual: the same 65 documents with a `?>` line appended before the
closing fence of every fenced block that contained `<?php` and no `?>`. Nothing
else changed. Exactly the 10 unclosed documents changed result; the other 55
were byte-for-byte identical in pass, score, and failed-check ids. Checks that
flipped from fail to pass under the counterfactual, by count of documents:

| Check | Documents flipped | Why it had failed |
|---|---:|---|
| `required_output_headings` | 8 | headings after the first `<?php` were blanked |
| `verification_specificity` | 5 | the Verification Notes section was blanked |
| `negative_space` | 2 | the negative-space sentence was blanked |
| `exact_wordpress_surfaces` | 4 | surfaces named after the first `<?php` were blanked |

Two of the ten (`evidence/.../baseline-few-shot/studio-launch-handoff-v1.md`
and `.../baseline-zero-shot/...`) still fail `required_output_headings` under
the counterfactual: those baseline outputs really are missing packet headings.

The code-span shape was measured on the one recorded output that carries it,
`evidence/wordpress-high-risk-evals/wordpress-security-critic-saved-outputs-20260621/raw/wordpress-security-critic/skill/input-sql-output-handling-v1.md`:
before the change `required_output_headings` reported eight missing headings;
after it, two. The two that remain (`Security Gate Evidence`,
`Suppression Review`) are absent from the output because the contract gained
them after the output was recorded; that is contract growth, not this defect.

## The change

The raw-HTML pass now matches its patterns against a masked copy of the
document in which fenced code blocks and single-line backtick code spans are blanked, then
blanks each match in the visible text at the same offsets. Blanking preserves
length and line breaks, so the two copies stay aligned. Three semantics are
now stated in the code rather than implied:

- Raw-text elements (`<script>`, `<pre>`, `<template>`, ...) still swallow
  everything to their closing tag or the end of the document wherever they
  open, because a browser renders nothing inside them.
- CommonMark HTML blocks of kinds 2–5 (`<!--`, `<![CDATA[`, `<?`, `<!X`) start
  only at a line start with at most three spaces of indent, and an unclosed one
  still runs to the end of the document, as a renderer would.
- The same constructs opened mid-line are inline raw HTML: they hide their
  content only when they close inside the paragraph. An unclosed one is
  literal text and hides nothing.

Tests added in `evals/harness/tests/test_wordpress_skill_output_contract.py`
pin the fenced, tilde-fenced, JSON-string-in-fence, indented-code, and
code-span cases as visible, and pin the unfenced line-start `<?php` and the
closed inline forms as still hidden.

## Recorded results that the fixed oracle no longer reproduces

The frozen `*.contract.json` files under `evidence/` were left exactly as
recorded. Replaying the fixed oracle over the same raw outputs changes three
recorded results, all in
`evidence/wordpress-high-risk-evals/wordpress-blueprint-executor-sidecar-saved-outputs-20260916/`:

| Lane | Recorded | Replay with fixed oracle |
|---|---|---|
| `skill` | fail, `0.3846`, 5 failed checks | fail, `0.6538`, 3 failed checks (`capability_grounding`, `runtime_sync_confirmation`, `runtime_tool_grounding`) |
| `baseline-zero-shot` | fail, `0.4231`, 5 failed checks | fail, `0.5385`, 4 failed checks (`verification_specificity` no longer fails) |
| `baseline-few-shot` | fail, `0.5385`, 4 failed checks | fail, `0.6154`, 3 failed checks (`negative_space` no longer fails) |

No recorded pass/fail verdict changes: all three lanes still fail, and the
scorecard's `0/3` contract-pass count stands. The recorded per-check lists and
scores overstate the failure, and `docs/wordpress/runtime-oracle-runbook.md`
now says so where it discusses that run.

The example packets under `evals/suites/*-executor/examples/` and the
`evals/handoff/abilities-llama70b-20260825/packet.md` handoff carry no recorded
contract result, so nothing recorded changes for them; their live scores rise
by the amounts in the counterfactual table above, and
`wordpress-block-executor/examples/deprecation-wordpress-v1` moves from fail to
pass.

## What this does not establish

- It does not change any recorded pass/fail verdict, and it does not make the
  blueprint sidecar run's skill lane pass; that lane's remaining failures are
  runtime-grounding failures and stand as recorded.
- It does not touch the separate packet validator
  (`validate_wordpress_executor_packet.py`), which never had this defect and
  scored the same packets `1.0` throughout.
- It does not make the oracle a CommonMark parser. Two known gaps remain, both
  in the conservative direction (they blank more, never less): a `<?php` line
  inside a kind-6 HTML block such as an unfenced `<div>` is still treated as a
  block start, and a raw-HTML block opened outside a fence whose closing
  delimiter sits inside a later fence runs to the end of the document instead
  of stopping at that delimiter. Neither shape occurs in the 65-document
  corpus.
- `<code>` remains in the raw-text element list although browsers render its
  content; an unclosed literal `<code>` tag outside code still blanks to the
  end of the document. No corpus document has one. Removing it is a separate
  decision.
- The 15 other recorded evidence contracts that the current oracle does not
  reproduce (performance-critic and planner.migration lanes from 2026-06-21,
  and the two other security-critic lanes) drift for reasons unrelated to this
  change: those contracts gained checks and headings after the outputs were
  recorded. This change neither causes nor resolves that drift.

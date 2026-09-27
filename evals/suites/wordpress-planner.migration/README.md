# wordpress-planner.migration Focused Eval Scaffold

Focused evaluation scaffold for `wordpress-planner.migration`. The suite now
contains the original broad smoke fixture plus six focused migration planning
fixtures:

- `smoke-wordpress-v1`: an exact source-to-block contract for a repository-owned
  importer, including semantic block properties, unsupported-source accounting,
  byte-idempotent writes, and separate editor/frontend proof.
- `legacy-cms-content-mapping-v1`: source schema uncertainty, post type and
  taxonomy mapping, author/byline handling, media relationships, and field
  transforms.
- `url-redirect-permalink-v1`: permalink model, redirect-map acceptance
  criteria, crawl comparison, query-string handling, and 404 sampling.
- `cutover-rollback-reconciliation-v1`: dry-run findings, delta migration,
  rollback triggers, reconciliation queues, and launch ownership.
- `host-sync-staging-cutover-v1`: a ddev-to-Pressable staging push chosen from
  the fixture's recorded capability manifest, with `Sync tool:` / `Sync target:`
  records, target confirmation before writing, and the `ddev wp` prefix. This
  fixture ships `host-sync-staging-cutover-v1.capability-manifest.json`, a probe
  recording of a synthetic ddev project (see
  `evals/harness/tests/test_fixture_capability_manifests.py`), so its saved
  outputs are scored with the manifest-gated checks enabled.
- `paragraphs-heavy-v1`: an invented Drupal 10 site built from Paragraphs, with
  a supplied source-structure inventory. It ships
  `paragraphs-heavy-v1.source-structure.json` (contract
  `contracts/source-structure/` 1.2.0, zivtech/drupal-meta-skills), so its saved
  outputs are scored for one keyed `Structure disposition` row per inventoried
  component and for the `non-empty-destination` oracle field.
- `drupal-no-inventory-v1`: the same kind of source with no inventory. The
  planner must stop at Phase 1 with `Source structure file: missing - <reason>`
  and point at `drupal-source-inventory`. The rubric grades the stop; the
  deterministic oracle only checks that a `missing` plan emits no structure
  rows, so a plan that ignores the gate entirely is caught by the rubric alone.

Historical saved outputs and answer-key diagnostics exist under `evals/results/`,
but they are directional internal evidence only. They do not establish a quality
edge over a current ChatGPT-level baseline and are not a public benchmark claim.
The fixture/rubric definitions in this suite describe planning expectations, not
proof that any migration was implemented or run.

For plans that affirmatively target Gutenberg, the saved-output oracle uses one
exact, duplicate-rejecting decision record per owning section. Record values are
enumerated by the smoke fixture and skill; negative-space prose and fenced
examples are not authoritative contract evidence. Non-Gutenberg plans do not
emit the Gutenberg-only records.

Output contract oracle:

```bash
uv run python evals/harness/validate_wordpress_skill_output.py \
  --skill wordpress-planner.migration \
  --output <candidate-output.md>
```

For a fixture that ships a `<fixture-id>.capability-manifest.json` sidecar, add
`--capability-manifest <that file>`; `run_wordpress_high_risk_saved_outputs.py`
discovers the sidecar itself and records its path in the contract result. A
`<fixture-id>.source-structure.json` sidecar is passed the same way as
`--source-structure <that file>`.

Strict suite integrity gate:

```bash
python3 scripts/validate-eval-suite-integrity.py \
  --strict-suites wordpress-planner.migration \
  --allow-known-gaps
```

Negative space:

- This suite does not prove a real migration without source extracts,
  stakeholder acceptance criteria, dry-run outputs, and launch signoff.
- This suite does not prove `wordpress-planner.migration` outperforms a current
  ChatGPT-level baseline until review evidence exists and the answer-key
  interpretation is accepted.
- This suite is focused on migration plan quality, not executing a migration.

# Vendored source-structure contract

These files are unmodified copies from
[`zivtech/drupal-meta-skills`](https://github.com/zivtech/drupal-meta-skills)
`contracts/source-structure/` at commit
`2236cbc4c68e02cf0229374a1fffd34cd4612505`, contract version `1.2.0`
(GPL-3.0, the same license as this repository):

- `VERSION`
- `source-structure.schema.json`
- `dispositions.schema.json`

`evals/harness/validate_wordpress_skill_output.py` reads the supported major
version and the closed `kind` and `verdict` enums from these files, per the
contract's consumer checklist. It does not run a full schema validation.

`evals/harness/tests/test_source_structure_contract.py` pins each file's
sha256, so an edit here fails the suite. To re-vendor, copy the three files
from a newer upstream commit, update this README's commit and version, and
update the pinned hashes in that test. The check against upstream is manual:

```bash
gh api "repos/zivtech/drupal-meta-skills/contents/contracts/source-structure/VERSION?ref=main" --jq .content | base64 -d
```

A new major needs a code change as well: the loader rejects any major other
than the vendored one.

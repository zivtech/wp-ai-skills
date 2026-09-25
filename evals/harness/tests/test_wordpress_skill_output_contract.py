"""Tests for WordPress saved skill-output contract validation."""

import json

import pytest

import validate_wordpress_skill_output as oracle


GOOD_PLANNER = """\
## Plugin Scope
Build an editorial review plugin for an existing WordPress admin workflow.
Delivery unit: client-custom-plugin

## Current-State Evidence
The repo already uses `register_post_type()` and `register_post_meta()` with `show_in_rest`.

## Architecture And File Map
Use a small plugin bootstrap plus an admin settings class.

## Hook And Data Flow
Use `register_setting()`, `current_user_can()`, and `check_admin_referer()`.

## Security And Data Integrity
Rich text uses `wp_kses_post()` and redirects use `wp_safe_redirect()`.

## Operations And Release Plan
Run PHPCS/WPCS, PHPUnit, WP-CLI smoke, and Plugin Check before release.

## Assumption Register
    Assumption: no exact WordPress API applies to external CRM ownership because
    WordPress does not control the vendor account; the CRM owner must confirm it
    against the vendor API contract.

## Test Strategy
PHPUnit covers settings persistence; Plugin Check covers package readiness.

## Acceptance Criteria
Admin save succeeds only for users with the mapped capability.

## Executor Handoff
Generate plugin files and tests.

## Critic Handoff
Send to wordpress-security-critic and wordpress-critic.
"""


BAD_PLANNER = """\
## Plugin Scope
[Finding]

## Architecture
Use WordPress APIs, use nonces, use capabilities, and run tests.
"""


GOOD_BLOCK_PLANNER = """\
## Block Scope
Build one dynamic `acme/runtime-card` block. This does not claim cross-browser coverage.

Block identity: acme/runtime-card
Primary serialization: dynamic
Interaction pattern: server-rendered block

## Current-State Evidence
The plugin registers blocks from `block.json` with `register_block_type()`.

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
"""


UNRELATED_BLOCK_PLANNER = """\
## Block Scope
Create a content feature for an existing WordPress site. This does not claim release readiness.

## Current-State Evidence
The site has `register_post_type()` and `WP_Query` usage.

## Metadata And Attribute Plan
Keep the content type fields in post meta.

## Render And Interaction Plan
Render the archive with a PHP template and show a friendly error.

## Compatibility And Migration Plan
Keep old posts available in a fixture export.

## Security Performance And Accessibility Notes
Use `current_user_can()` for admin access.

## Assumption Register
Assumption: the content owner supplies sample data.

## Test Strategy
Use PHPUnit and Playwright for a browser check.

## Acceptance Criteria
The archive lists published records.

## Executor Handoff
Implement the content feature.

## Critic Handoff
Send it to wordpress-critic.
"""


GOOD_GUTENBERG_MIGRATION_PLANNER = """\
## Migration Scope
Migrate Contentful Rich Text into Gutenberg blocks. This does not prove production cutover readiness.

## Current-State Evidence
The importer writes `post_content` and has a disposable wp-env fixture.

## Source Audit
Inspect the Rich Text document/container schema and localized fields.

## Target Mapping
Map source nodes to core block mappings in `post_content`; use an explicit
custom block allowlist and record every unsupported or unmapped node.

Gutenberg target: post_content
Block mapping: core+custom
Unsupported content: accounted

## Transform And Execution Plan
Use WordPress block serialization, stable source identity, and an idempotent,
rerunnable two-pass import.

Serialization API: serialize_blocks
Rerun policy: idempotent

## Validation Plan
Use `parse_blocks()` for block validation, a semantic oracle for expected text
and href values, a Playwright editor smoke, and a separate frontend smoke.

Block validation oracle: parse_blocks
Semantic oracle: required
Semantic oracle fields: text,href,attributes,unsupported,freeform
Editor oracle: required
Editor oracle method: playwright-clone-save-reload-restore
Frontend oracle: required
Frontend oracle method: playwright-selector-visible-text

## Rollback And Monitoring
Keep run-scoped before-images and execute a rollback test in wp-env.

## Assumption Register
Assumption: only the mapped locales are in scope.

## Test Strategy
Use a canonical source fixture plus malformed-container negative fixtures.

Fixture: required
Fixture identity: article-42-rich-text

## Acceptance Criteria
Every mapped node is present and every unsupported node is accounted for.

## Critic Handoff
Review serialization, idempotence, editor evidence, and rollback evidence.
"""


GOOD_CLASSIC_MIGRATION_PLANNER = """\
## Migration Scope
Import CSV article rows into classic WordPress posts. Gutenberg and the Block Editor are explicitly out of scope. This does not prove production cutover readiness.

## Current-State Evidence
The importer uses `wp_insert_post()` and writes sanitized HTML into `post_content`.

## Source Audit
Inspect the CSV header, UTF-8 encoding, stable source ID, and required columns.

## Target Mapping
Map title, body, and publication state to `post_title`, `post_content`, and `post_status`; log unsupported columns.

## Transform And Execution Plan
Use `wp_kses_post()` before `wp_insert_post()`, retain the stable source ID, and make reruns idempotent.

## Validation Plan
Use `wp post list`, exact expected title and body assertions, and a front-end browser smoke.

## Rollback And Monitoring
Keep run-scoped before-images and execute a rollback test in the disposable environment.

## Assumption Register
Assumption: the supplied CSV is the authoritative locale for this import.

## Test Strategy
Use a canonical CSV fixture plus malformed-row and duplicate-ID fixtures.

## Acceptance Criteria
Every valid row maps once, unsupported columns are accounted for, and rollback restores the prior posts.

## Critic Handoff
Review sanitization, idempotence, semantic evidence, and rollback evidence.
"""


GOOD_CRITIC = """\
**VERDICT: REVISE**

**Overall Assessment**
The implementation has a real REST authorization gap.

**Pre-commitment Predictions**
Expected issue: missing `permission_callback` on a custom route.

**Critical Findings**
- None.

**Major Findings**
- `register_rest_route()` lacks a specific `permission_callback` using `current_user_can()`.

**Minor Findings**
- None.

**What's Missing**
This review does not prove runtime behavior or editor smoke results.

**Multi-Perspective Notes**
Security and operations agree the route needs a capability boundary.

**Verdict Justification**
REVISE because the code is close but cannot ship without authorization.

**Remediation Guide**
Add a `permission_callback`, cover it with PHPUnit, then run WP-CLI smoke and Plugin Check.

**Open Questions**
Unknown: which role should receive the new capability.
"""


BAD_CRITIC = """\
**VERDICT: MAYBE**

**Overall Assessment**
Looks fine.
"""


SECURITY_GATE_REPORT = {
    "schema": "wordpress-security-gate",
    "schema_version": 1,
    "status": "fail",
    "tools": [
        {"id": "phpcs-security", "status": "fail"},
        {"id": "phpcs-suppression-diff", "status": "fail"},
    ],
    "findings": [
        {
            "rule_id": "WordPress.Security.EscapeOutput.OutputNotEscaped",
            "file": "acme-report/admin.php",
            "line": 38,
            "severity": "error",
            "enforced": True,
        },
        {
            "rule_id": "WordPress.DB.DirectDatabaseQuery.DirectQuery",
            "file": "acme-report/admin.php",
            "line": 40,
            "severity": "warning",
            "enforced": False,
        }
    ],
    "suppressed_annotations": [
        {
            "file": "acme-report/admin.php",
            "line": 42,
            "suppressed_rules": ["WordPress.DB.PreparedSQL.InterpolatedNotPrepared"],
            "security_relevant": True,
            "reappears_without_annotations": True,
        },
        {
            "file": "blocks/render.php",
            "line": 16,
            "suppressed_rules": ["WordPress.Security.EscapeOutput.OutputNotEscaped"],
            "security_relevant": False,
            "reviewed_safe_api": "get_block_wrapper_attributes",
        },
    ],
    "summary": {"errors": 1, "warnings": 0, "suppressed_security": 1, "reviewed_suppressed": 1},
    "negative_space": ["No authorization/IDOR/capability-correctness reasoning."],
}


GOOD_SECURITY_CRITIC_WITH_GATE = """\
**VERDICT: REVISE**

**Overall Assessment**
The artifact fails the supplied `security-gate.json` static profile and needs
reachability review before release.

**Pre-commitment Predictions**
Expected failures: suppressed SQL preparation and escaped-output gaps.

**Security Gate Evidence**
Gate-derived evidence from `security-gate.json` reports status `fail`.
`phpcs-suppression-diff` / `--ignore-annotations` found
`WordPress.DB.PreparedSQL.InterpolatedNotPrepared` at
`acme-report/admin.php:42`. The enforced PHPCS finding
`WordPress.Security.EscapeOutput.OutputNotEscaped` is at
`acme-report/admin.php:38`. Advisory gate-derived evidence includes
`WordPress.DB.DirectDatabaseQuery.DirectQuery` at `acme-report/admin.php:40`.

**Critical Findings**
- None until the caller path is proven.

**Major Findings**
- The report query suppression hides a `$wpdb->prepare()` failure, and the
  rendered admin output must use `wp_kses_post()` or `esc_html()` by context.

**Minor Findings**
- None.

**Suppression Review**
- `acme-report/admin.php:42` is a security-relevant suppression because
  `WordPress.DB.PreparedSQL.InterpolatedNotPrepared` reappears without
  annotations.
- `blocks/render.php:16` suppresses
  `WordPress.Security.EscapeOutput.OutputNotEscaped`; it is not
  security-relevant because the reviewed safe API is
  `get_block_wrapper_attributes`.

**What's Missing**
The gate's negative space does not prove authorization, IDOR, or capability
correctness; that critic-derived path review remains open.

**Multi-Perspective Notes**
Security and operations agree the deterministic sidecar blocks release.

**Exploitability Notes**
No CRITICAL finding until a role, route, or admin-post caller path is named.

**Verdict Justification**
REVISE because gate-derived evidence is deterministic and the critic-derived
reachability review is incomplete.

**Remediation Guide**
Remove the SQL suppression, prepare the query with `$wpdb->prepare()`, keep
contextual output escaping with `wp_kses_post()` or `esc_html()`, then rerun
PHPCS/WPCS and the security gate.

**Open Questions**
Unknown: which capability is required to reach `acme-report/admin.php`.
"""


def test_good_planner_output_passes():
    result = oracle.validate_output("wordpress-plugin-planner", GOOD_PLANNER)

    assert result["pass"] is True
    assert result["score"] == 1.0


def test_good_block_planner_passes_section_local_contract():
    result = oracle.validate_output("wordpress-planner.block", GOOD_BLOCK_PLANNER)
    checks = {check["id"]: check for check in result["checks"]}

    assert result["pass"] is True
    assert checks["block_scope_contract"]["passed"] is True
    assert checks["block_metadata_attribute_contract"]["passed"] is True
    assert checks["block_render_contract"]["passed"] is True
    assert checks["block_compatibility_contract"]["passed"] is True
    assert checks["block_editor_frontend_contract"]["passed"] is True


def test_unrelated_wordpress_apis_cannot_pass_block_planner_contract():
    result = oracle.validate_output("wordpress-planner.block", UNRELATED_BLOCK_PLANNER)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert {
        "block_scope_contract",
        "block_metadata_attribute_contract",
        "block_render_contract",
        "block_compatibility_contract",
        "block_editor_frontend_contract",
    } <= failed


@pytest.mark.parametrize(
    ("old", "new", "expected_gate"),
    [
        ("Primary serialization: dynamic", "Primary serialization: not defined", "block_scope_contract"),
        ("Metadata file: block.json", "Metadata file: not defined", "block_metadata_attribute_contract"),
        ("Render surface: render_callback", "Render surface: not defined", "block_render_contract"),
        ("Compatibility decision: new-contract", "Compatibility decision: not-defined", "block_compatibility_contract"),
        ("Frontend oracle: required", "Frontend oracle: skipped", "block_editor_frontend_contract"),
    ],
)
def test_block_plan_single_fact_mutants_kill_the_intended_gate(old, new, expected_gate):
    candidate = GOOD_BLOCK_PLANNER.replace(old, new)
    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert expected_gate in failed
    domain_gates = {
        "block_scope_contract",
        "block_metadata_attribute_contract",
        "block_render_contract",
        "block_compatibility_contract",
        "block_editor_frontend_contract",
    }
    assert failed & domain_gates == {expected_gate}


def test_static_block_negative_space_does_not_create_dynamic_classification():
    candidate = (
        GOOD_BLOCK_PLANNER
        .replace(
            "Build one dynamic `acme/runtime-card` block.",
            "Build one static `acme/runtime-card` block; it is not a dynamic block.",
        )
        .replace("Primary serialization: dynamic", "Primary serialization: static")
        .replace("Render surface: render_callback", "Render surface: save()")
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)

    assert result["pass"] is True


def test_interactivity_pattern_is_orthogonal_to_static_serialization():
    candidate = (
        GOOD_BLOCK_PLANNER
        .replace("Primary serialization: dynamic", "Primary serialization: static")
        .replace("Interaction pattern: server-rendered block", "Interaction pattern: Interactivity API")
        .replace("Render surface: render_callback", "Render surface: save()")
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)

    assert result["pass"] is True


@pytest.mark.parametrize(
    ("old", "new", "gate"),
    [
        (
            "Failure behavior: log-and-return-empty",
            "Failure behavior: not-defined",
            "block_render_contract",
        ),
        (
            "Saved-content fixture: required",
            "Saved-content fixture: never",
            "block_compatibility_contract",
        ),
        (
            "Editor oracle: required",
            "Editor oracle: skipped",
            "block_editor_frontend_contract",
        ),
    ],
)
def test_negated_block_decision_records_fail_their_owning_gate(old, new, gate):
    result = oracle.validate_output("wordpress-planner.block", GOOD_BLOCK_PLANNER.replace(old, new))
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert gate in failed


def test_duplicate_decision_record_is_rejected():
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Editor oracle: required",
        "Editor oracle: required\nEditor oracle: skipped",
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_editor_frontend_contract" in failed


def test_decision_record_inside_example_fence_is_not_contract_evidence():
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic",
        "```text\nPrimary serialization: dynamic\n```",
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


@pytest.mark.parametrize(
    "replacement",
    [
        "```text\nPrimary serialization: dynamic\n````",
        "```text\nPrimary serialization: dynamic",
        "    Primary serialization: dynamic",
        "   \tPrimary serialization: dynamic",
        "<!-- Primary serialization: dynamic -->",
    ],
    ids=(
        "longer-closing-fence", "unclosed-fence", "indented-code",
        "mixed-tab-indented-code", "html-comment",
    ),
)
def test_hidden_decision_record_variants_are_not_contract_evidence(replacement):
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic", replacement
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


@pytest.mark.parametrize(
    ("skill", "document", "wrapper"),
    [
        ("wordpress-planner.block", GOOD_BLOCK_PLANNER, "```markdown\n{}\n````"),
        ("wordpress-planner.migration", GOOD_GUTENBERG_MIGRATION_PLANNER, "~~~~md\n{}\n~~~~"),
        ("wordpress-planner.block", GOOD_BLOCK_PLANNER, "<!--\n{}\n-->"),
        ("wordpress-planner.migration", GOOD_GUTENBERG_MIGRATION_PLANNER, "<!--\n{}\n-->"),
    ],
)
def test_whole_hidden_document_cannot_satisfy_output_contract(skill, document, wrapper):
    result = oracle.validate_output(skill, wrapper.format(document))
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "required_output_headings" in failed


@pytest.mark.parametrize("tag", ["pre", "script", "style", "textarea", "template"])
def test_whole_raw_html_code_block_cannot_satisfy_output_contract(tag):
    result = oracle.validate_output(
        "wordpress-planner.block",
        f"<{tag}>\n{GOOD_BLOCK_PLANNER}\n</{tag}>",
    )
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "required_output_headings" in failed


@pytest.mark.parametrize(
    "wrapper",
    [
        "<![CDATA[\n{}\n]]>",
        "<?raw\n{}\n?>",
        "<!DOCTYPE html\n{}\n>",
    ],
    ids=("cdata", "processing-instruction", "declaration"),
)
def test_whole_commonmark_raw_block_cannot_satisfy_output_contract(wrapper):
    result = oracle.validate_output(
        "wordpress-planner.block", wrapper.format(GOOD_BLOCK_PLANNER)
    )
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "required_output_headings" in failed


@pytest.mark.parametrize("tag", ["div", "section", "table", "details", "custom-element"])
def test_raw_html_block_opening_hides_following_contract_section(tag):
    result = oracle.validate_output(
        "wordpress-planner.block", f"<{tag}>\n{GOOD_BLOCK_PLANNER}\n</{tag}>"
    )
    headings = next(
        check for check in result["checks"] if check["id"] == "required_output_headings"
    )

    assert result["pass"] is False
    assert headings["passed"] is False


@pytest.mark.parametrize("tag", ["div", "section", "table"])
def test_type_six_raw_html_prefix_with_trailing_content_hides_record(tag):
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic",
        f'<{tag} style="display:none">hidden\nPrimary serialization: dynamic\n</{tag}>',
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


@pytest.mark.parametrize(
    ("opening", "closing"),
    [
        ('<span style="display:none">hidden', "</span>"),
        ("<a hidden>", "</a>"),
        ("<custom-element hidden>", "</custom-element>"),
    ],
)
def test_inline_html_wrapper_cannot_hide_authoritative_record(opening, closing):
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic",
        f"{opening}\nPrimary serialization: dynamic\n{closing}",
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


def test_list_continuation_cannot_supply_authoritative_decision_record():
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic",
        "- <span hidden>hidden\n  Primary serialization: dynamic\n  </span>",
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


def test_midline_html_opener_cannot_hide_authoritative_record():
    candidate = GOOD_BLOCK_PLANNER.replace(
        "Primary serialization: dynamic",
        "Prose <span hidden>\nPrimary serialization: dynamic\n</span>",
    )

    result = oracle.validate_output("wordpress-planner.block", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "block_scope_contract" in failed


@pytest.mark.parametrize(
    ("skill", "document", "duplicate"),
    [
        (
            "wordpress-planner.block",
            GOOD_BLOCK_PLANNER,
            "## Block Scope\nBlock identity: acme/wrong\nPrimary serialization: static\n\n",
        ),
        (
            "wordpress-planner.migration",
            GOOD_GUTENBERG_MIGRATION_PLANNER,
            "## Target Mapping\nGutenberg target: post_content\nBlock mapping: core-only\nUnsupported content: accounted\n\n",
        ),
    ],
)
def test_duplicate_required_heading_is_rejected(skill, document, duplicate):
    result = oracle.validate_output(skill, duplicate + document)
    headings = next(
        check for check in result["checks"] if check["id"] == "required_output_headings"
    )

    assert result["pass"] is False
    assert headings["passed"] is False
    assert "duplicate headings" in headings["detail"]


def test_gutenberg_migration_plan_passes_domain_contract():
    result = oracle.validate_output(
        "wordpress-planner.migration", GOOD_GUTENBERG_MIGRATION_PLANNER
    )
    domain = {
        check["id"]: check["passed"]
        for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_")
    }

    assert result["pass"] is True
    assert domain == {
        "gutenberg_migration_mapping_contract": True,
        "gutenberg_migration_serialization_contract": True,
        "gutenberg_migration_oracle_contract": True,
    }


def test_gutenberg_migration_plan_cannot_omit_semantic_or_editor_frontend_oracles():
    candidate = (
        GOOD_GUTENBERG_MIGRATION_PLANNER
        .replace("Semantic oracle: required", "Semantic oracle: skipped")
        .replace("Editor oracle: required", "Editor oracle: skipped")
        .replace("Frontend oracle: required", "Frontend oracle: skipped")
    )
    assert candidate != GOOD_GUTENBERG_MIGRATION_PLANNER
    result = oracle.validate_output("wordpress-planner.migration", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "gutenberg_migration_oracle_contract" in failed


def test_generic_semantic_and_fixture_flags_do_not_replace_bound_contract():
    candidate = (
        GOOD_GUTENBERG_MIGRATION_PLANNER
        .replace(
            "Semantic oracle fields: text,href,attributes,unsupported,freeform",
            "Semantic oracle fields: required",
        )
        .replace(
            "Fixture identity: article-42-rich-text",
            "Fixture identity: required",
        )
    )
    assert candidate != GOOD_GUTENBERG_MIGRATION_PLANNER

    result = oracle.validate_output("wordpress-planner.migration", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "gutenberg_migration_oracle_contract" in failed


def test_negated_gutenberg_decision_records_fail_all_domain_gates():
    candidate = (
        GOOD_GUTENBERG_MIGRATION_PLANNER
        .replace("Gutenberg target: post_content", "Gutenberg target: not defined")
        .replace("Block mapping: core+custom", "Block mapping: forbidden")
        .replace("Unsupported content: accounted", "Unsupported content: ignored")
        .replace("Serialization API: serialize_blocks", "Serialization API: forbidden")
        .replace("Rerun policy: idempotent", "Rerun policy: non-idempotent")
        .replace("Block validation oracle: parse_blocks", "Block validation oracle: skipped")
        .replace("Semantic oracle: required", "Semantic oracle: skipped")
        .replace("Editor oracle: required", "Editor oracle: skipped")
        .replace("Frontend oracle: required", "Frontend oracle: skipped")
    )

    result = oracle.validate_output("wordpress-planner.migration", candidate)
    failed = {
        check["id"] for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_") and not check["passed"]
    }

    assert failed == {
        "gutenberg_migration_mapping_contract",
        "gutenberg_migration_serialization_contract",
        "gutenberg_migration_oracle_contract",
    }


def test_negative_block_prose_outside_decision_records_does_not_activate_migration_lane():
    candidate = (
        GOOD_CLASSIC_MIGRATION_PLANNER
        .replace(
            "Map title, body, and publication state",
            "Custom block mapping is out of scope. Map title, body, and publication state",
        )
        .replace(
            "Use `wp_kses_post()`",
            "Do not use serialize_blocks(). Use `wp_kses_post()`",
        )
        .replace(
            "Use `wp post list`",
            "parse_blocks and block validation are out of scope. Use `wp post list`",
        )
    )

    result = oracle.validate_output("wordpress-planner.migration", candidate)
    domain = [
        check["id"] for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_")
    ]

    assert result["pass"] is True
    assert domain == ["gutenberg_migration_scope"]


def test_classic_post_content_migration_does_not_activate_gutenberg_contract():
    result = oracle.validate_output(
        "wordpress-planner.migration", GOOD_CLASSIC_MIGRATION_PLANNER
    )
    domain = {
        check["id"]: check["passed"]
        for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_")
    }

    assert result["pass"] is True
    assert domain == {"gutenberg_migration_scope": True}


@pytest.mark.parametrize(
    "scope",
    [
        "This is not a Gutenberg or Block Editor migration.",
        "No Gutenberg transformation is planned; import classic posts.",
        "Import classic posts, not Gutenberg content.",
        "Import classic posts rather than Gutenberg blocks.",
    ],
)
def test_negative_gutenberg_scope_phrasings_do_not_activate_domain_contract(scope):
    candidate = GOOD_CLASSIC_MIGRATION_PLANNER.replace(
        "Gutenberg and the Block Editor are explicitly out of scope.", scope
    )

    result = oracle.validate_output("wordpress-planner.migration", candidate)
    domain = [
        check for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_")
    ]

    assert result["pass"] is True
    assert [check["id"] for check in domain] == ["gutenberg_migration_scope"]


@pytest.mark.parametrize(
    "scope",
    [
        "Migrate article rows into Gutenberg without changing permalinks.",
        "Migrate article rows into Gutenberg blocks but exclude media.",
        "Migrate article rows into the Block Editor and do not change authors.",
    ],
)
def test_affirmative_gutenberg_target_survives_unrelated_negative_qualifier(scope):
    candidate = GOOD_CLASSIC_MIGRATION_PLANNER.replace(
        "Import CSV article rows into classic WordPress posts. Gutenberg and the Block Editor are explicitly out of scope.",
        scope,
    )

    result = oracle.validate_output("wordpress-planner.migration", candidate)
    failed = {
        check["id"] for check in result["checks"]
        if check["id"].startswith("gutenberg_migration_") and not check["passed"]
    }

    assert result["pass"] is False
    assert failed == {
        "gutenberg_migration_mapping_contract",
        "gutenberg_migration_serialization_contract",
        "gutenberg_migration_oracle_contract",
    }


def test_blanket_non_applicability_cannot_replace_exact_surfaces():
    check = oracle.check_exact_surfaces(
        "No exact WordPress API applies.",
        {"min_surfaces": 2},
    )

    assert check.passed is False
    assert "expected at least 2" in check.detail


def test_generic_argument_words_require_key_context():
    prose = oracle.check_exact_surfaces(
        "The category and description are useful prose labels.",
        {"min_surfaces": 2},
    )
    keys = oracle.check_exact_surfaces(
        "The schema requires `category` and `description`.",
        {"min_surfaces": 2},
    )

    assert prose.passed is False
    assert keys.passed is True


def test_exact_surface_matching_is_boundary_and_order_aware():
    partial = oracle.check_exact_surfaces(
        "current_user_canary and register_rest_routeable are custom names.",
        {"min_surfaces": 1},
    )
    scattered = oracle.check_exact_surfaces(
        "Use register_rest_route. In a separate sentence, add permission_callback.",
        {"min_surfaces": 2},
    )
    scattered_matches = oracle.find_surface_matches(
        "Use register_rest_route. In a separate sentence, add permission_callback."
    )
    exact = oracle.check_exact_surfaces(
        "Use current_user_can() and register_rest_route() permission_callback.",
        {"min_surfaces": 2},
    )

    assert partial.passed is False
    assert scattered.passed is False
    assert not any(match.category == "reviewed_composed" for match in scattered_matches)
    assert exact.passed is True
    assert "core_function:current_user_can()" in exact.detail
    assert "reviewed_composed:register_rest_route() permission_callback" in exact.detail


def test_permission_callback_key_context_supports_abilities_api():
    check = oracle.check_exact_surfaces(
        "Use wp_register_ability(). Configure `permission_callback` for the ability.",
        {"min_surfaces": 2},
    )

    assert check.passed is True
    assert "argument_key:permission_callback" in check.detail


@pytest.mark.parametrize(
    "statement",
    [
        "No exact WordPress API applies because this is external; verify it with the owner.",
        "No exact WordPress API applies to external CRM ownership; verify it with the CRM owner.",
        "No exact WordPress API applies to external CRM ownership because WordPress does not control it.",
    ],
)
def test_non_applicability_requires_scope_reason_and_oracle(statement):
    text = f"Use current_user_can() and register_post_type(). {statement}"

    check = oracle.check_exact_surfaces(text, {"min_surfaces": 2})

    assert check.passed is False
    assert "invalid non-applicability" in check.detail


def test_scoped_non_applicability_does_not_waive_surface_minimum():
    statement = (
        "No exact WordPress API applies to external CRM ownership because WordPress "
        "does not control the vendor account; verify it with the CRM owner against "
        "the vendor API contract."
    )

    too_few = oracle.check_exact_surfaces(
        f"Use current_user_can(). {statement}",
        {"min_surfaces": 2},
    )
    enough = oracle.check_exact_surfaces(
        f"Use current_user_can() and register_post_type(). {statement}",
        {"min_surfaces": 2},
    )

    assert too_few.passed is False
    assert enough.passed is True
    assert "scoped non-applicability" in enough.detail


@pytest.mark.parametrize(
    "statement",
    [
        "No exact WordPress API applies to foo bar because owner.",
        "No exact WordPress API applies to foo bar because yes; documentation.",
        "No exact WordPress API applies to external CRM ownership because the owner.",
    ],
)
def test_non_applicability_rejects_vacuous_scope_reason_and_oracle(statement):
    check = oracle.check_exact_surfaces(
        f"Use current_user_can() and register_post_type(). {statement}",
        {"min_surfaces": 2},
    )

    assert check.passed is False
    assert "invalid non-applicability" in check.detail


def test_dynamic_reviewed_hook_and_safe_project_path_match():
    check = oracle.check_exact_surfaces(
        "Handle wp_ajax_save_report in plugin/includes/class-report.php.",
        {"min_surfaces": 2},
    )

    assert check.passed is True
    assert "hook:wp_ajax_save_report" in check.detail
    assert "file_glob:plugin/includes/class-report.php" in check.detail


def test_dynamic_hook_and_path_matching_rejects_partial_and_traversal_forms():
    check = oracle.check_exact_surfaces(
        "Ignore my_wp_ajax_save, wp_ajax_, and ../plugin/includes/class-report.php.",
        {"min_surfaces": 1},
    )

    assert check.passed is False


@pytest.mark.parametrize(
    "unsafe",
    [
        "$current_user_can", "$obj->current_user_can()", "Fake::current_user_can()",
        "$wp", "@wp", "$obj->register_rest_route() permission_callback",
        "Fake::register_rest_route() permission_callback",
        "$obj -> current_user_can()", "$obj ?-> current_user_can()",
        "Fake :: current_user_can()", "@ current_user_can()",
        "$obj->child -> current_user_can()", "$objects[0] -> current_user_can()",
        "(new Fake()) -> current_user_can()", "get_service() -> current_user_can()",
        "$obj -> register_rest_route() permission_callback",
        "Fake :: register_rest_route() permission_callback",
        "@ register_rest_route() permission_callback",
        "$objects[0] -> register_rest_route() permission_callback",
    ],
)
def test_core_and_composed_surfaces_reject_non_global_contexts(unsafe):
    check = oracle.check_exact_surfaces(f"Inspect {unsafe}.", {"min_surfaces": 1})

    assert check.passed is False


@pytest.mark.parametrize(
    "unsafe",
    [
        "$wp_abilities_api_init", "Fake::wp_abilities_api_init", "Fake :: wp_abilities_api_init",
        "$promote_users", "$execute_callback", "$wp_ajax_save_report",
        "Fake::wp_ajax_save_report", "Fake :: wp_ajax_save_report", "@ wp_ajax_save_report",
        "$obj->child -> wp_abilities_api_init", "$objects[0] -> wp_ajax_save_report",
        "get_service() -> wp_abilities_api_init",
    ],
)
def test_typed_identifier_surfaces_reject_non_global_contexts(unsafe):
    check = oracle.check_exact_surfaces(f"Inspect {unsafe}.", {"min_surfaces": 1})

    assert check.passed is False


def test_quoted_global_callable_name_remains_exact_surface():
    check = oracle.check_exact_surfaces("Use 'current_user_can' as the callable.", {"min_surfaces": 1})

    assert check.passed is True


def test_safe_project_basenames_match_as_file_surfaces():
    check = oracle.check_exact_surfaces(
        "Use render.php, .wp-env.json, and current_user_can().",
        {"min_surfaces": 3},
    )

    assert check.passed is True
    assert "file_glob:render.php" in check.detail
    assert "file_glob:.wp-env.json" in check.detail


@pytest.mark.parametrize(
    "unsafe",
    ["../render.php", "/tmp/render.php", "../.wp-env.json", "render.php/evil", "dir\\render.php"],
)
def test_safe_project_basenames_reject_path_context(unsafe):
    check = oracle.check_exact_surfaces(f"Inspect {unsafe}.", {"min_surfaces": 1})

    assert check.passed is False


@pytest.mark.parametrize(
    ("category", "surface"),
    [("file_surfaces", "../outside.php"), ("wp_cli_commands", "security best practices")],
)
def test_output_catalog_rejects_unsafe_registry_entry(tmp_path, monkeypatch, category, surface):
    data = json.loads(oracle.REGISTRY_PATH.read_text(encoding="utf-8"))
    data["categories"][category].append(surface)
    path = tmp_path / "unsafe-registry.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(oracle, "REGISTRY_PATH", path)
    oracle._surface_catalog.cache_clear()

    try:
        with pytest.raises(ValueError, match=category):
            oracle.find_surface_matches("Use current_user_can().")
    finally:
        oracle._surface_catalog.cache_clear()


def test_output_catalog_rejects_blank_provenance(tmp_path, monkeypatch):
    data = json.loads(oracle.REGISTRY_PATH.read_text(encoding="utf-8"))
    data["provenance"]["reviewed_for"] = ""
    path = tmp_path / "blank-provenance.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(oracle, "REGISTRY_PATH", path)
    oracle._surface_catalog.cache_clear()
    try:
        with pytest.raises(ValueError, match="provenance"):
            oracle.find_surface_matches("Use current_user_can().")
    finally:
        oracle._surface_catalog.cache_clear()


def test_dot_notation_planner_alias_passes():
    result = oracle.validate_output("wordpress-planner.plugin", GOOD_PLANNER)

    assert result["pass"] is True
    assert result["skill"] == "wordpress-plugin-planner"
    assert result["requested_skill"] == "wordpress-planner.plugin"


def test_bad_planner_output_fails_contract_checks():
    result = oracle.validate_output("wordpress-plugin-planner", BAD_PLANNER)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert {"required_output_headings", "no_placeholders", "no_generic_wp_labels"} <= failed


def test_good_critic_output_passes():
    result = oracle.validate_output("wordpress-critic", GOOD_CRITIC)

    assert result["pass"] is True


def test_performance_verification_terms_are_contract_evidence():
    check = oracle.check_verification_specificity(
        "Measure before and after with Query Monitor, Core Web Vitals, "
        "browser performance trace, object-cache metrics, and "
        "`wp option list --autoload=on`."
    )

    assert check.passed is True
    assert "query monitor" in check.detail
    assert "wp option list" in check.detail


def test_migration_verification_terms_are_contract_evidence():
    check = oracle.check_verification_specificity(
        "Validate with `wp post list`, `wp media import`, "
        "`wp search-replace --dry-run`, a crawl comparison, "
        "launch rehearsal, and rollback test."
    )

    assert check.passed is True
    assert "wp post list" in check.detail
    assert "wp search-replace" in check.detail


def test_bad_critic_output_fails_verdict_and_headings():
    result = oracle.validate_output("wordpress-critic", BAD_CRITIC)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert {"critic_verdict", "required_output_headings"} <= failed


def test_lowercase_placeholder_word_in_prose_is_not_marker():
    result = oracle.check_no_placeholders(
        "Replace placeholder values with the canonical plugin constants, but do not leave TODO markers."
    )

    assert result.passed is False

    clean = oracle.check_no_placeholders(
        "Replace placeholder values with the canonical plugin constants before release."
    )

    assert clean.passed is True


def test_generic_label_check_allows_numbered_rerun_test_references():
    allowed = oracle.check_no_generic_labels(
        "Rerun tests: import the redirect map, then run tests 4 and 5 again."
    )
    rejected = oracle.check_no_generic_labels("Use WordPress APIs and run tests.")

    assert allowed.passed is True
    assert rejected.passed is False


def test_security_critic_output_passes_without_sidecar_when_contract_is_met():
    result = oracle.validate_output("wordpress-security-critic", GOOD_SECURITY_CRITIC_WITH_GATE)

    assert result["pass"] is True
    assert "security_gate_consumption" not in {check["id"] for check in result["checks"]}


def test_security_gate_sidecar_requires_rule_and_suppression_consumption():
    result = oracle.validate_output(
        "wordpress-security-critic",
        GOOD_SECURITY_CRITIC_WITH_GATE,
        security_gate=SECURITY_GATE_REPORT,
    )

    assert result["pass"] is True
    assert any(check["id"] == "security_gate_consumption" and check["passed"] for check in result["checks"])

    weak_output = GOOD_SECURITY_CRITIC_WITH_GATE.replace(
        "WordPress.DB.PreparedSQL.InterpolatedNotPrepared",
        "the prepared SQL sniff",
    )
    weak_result = oracle.validate_output(
        "wordpress-security-critic",
        weak_output,
        security_gate=SECURITY_GATE_REPORT,
    )
    failed = {check["id"] for check in weak_result["checks"] if not check["passed"]}

    assert weak_result["pass"] is False
    assert "security_gate_consumption" in failed

    no_advisory = GOOD_SECURITY_CRITIC_WITH_GATE.replace(
        "Advisory gate-derived evidence includes\n`WordPress.DB.DirectDatabaseQuery.DirectQuery` at `acme-report/admin.php:40`.",
        "There is no advisory gate-derived evidence.",
    )
    no_advisory_result = oracle.validate_output(
        "wordpress-security-critic",
        no_advisory,
        security_gate=SECURITY_GATE_REPORT,
    )
    no_advisory_failed = {check["id"] for check in no_advisory_result["checks"] if not check["passed"]}

    assert no_advisory_result["pass"] is False
    assert "security_gate_consumption" in no_advisory_failed


def test_security_gate_sidecar_requires_file_bound_locations():
    loose_location = GOOD_SECURITY_CRITIC_WITH_GATE.replace(
        "`acme-report/admin.php:42`",
        "`acme-report/admin.php` near line 42",
    )

    result = oracle.validate_output(
        "wordpress-security-critic",
        loose_location,
        security_gate=SECURITY_GATE_REPORT,
    )
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert result["pass"] is False
    assert "security_gate_consumption" in failed


def test_cli_accepts_security_gate_sidecar(tmp_path, capsys):
    output = tmp_path / "candidate.md"
    gate = tmp_path / "security-gate.json"
    output.write_text(GOOD_SECURITY_CRITIC_WITH_GATE, encoding="utf-8")
    gate.write_text(json.dumps(SECURITY_GATE_REPORT), encoding="utf-8")

    rc = oracle.main(
        [
            "--skill",
            "wordpress-security-critic",
            "--output",
            str(output),
            "--security-gate",
            str(gate),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["pass"] is True
    assert captured.err == ""


def test_cli_missing_security_gate_fails_cleanly(tmp_path, capsys):
    output = tmp_path / "candidate.md"
    output.write_text(GOOD_SECURITY_CRITIC_WITH_GATE, encoding="utf-8")

    rc = oracle.main(
        [
            "--skill",
            "wordpress-security-critic",
            "--output",
            str(output),
            "--security-gate",
            str(tmp_path / "missing-security-gate.json"),
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert rc == 1
    assert payload["pass"] is False
    assert "security gate file not found" in payload["error"]


def _planner_with_unit(unit: str, *extra: str) -> str:
    """GOOD_PLANNER with a different delivery unit and optional extra records."""
    replacement = "\n".join((f"Delivery unit: {unit}", *extra))
    return GOOD_PLANNER.replace("Delivery unit: client-custom-plugin", replacement)


@pytest.mark.parametrize(
    "unit",
    ["core-api-direct", "client-custom-plugin", "mu-plugin", "distributable-plugin",
     "composer-package", "theme-integration"],
)
def test_every_delivery_unit_is_readable(unit):
    result = oracle.validate_output("wordpress-plugin-planner", _planner_with_unit(unit))
    checks = {c["id"]: c for c in result["checks"]}

    assert checks["plugin_delivery_unit_contract"]["passed"] is True, checks


@pytest.mark.parametrize(
    "value",
    ["", "none", "not defined", "plugin", "a small plugin", "distributable plugin"],
)
def test_unreadable_delivery_unit_fails(value):
    candidate = GOOD_PLANNER.replace(
        "Delivery unit: client-custom-plugin",
        f"Delivery unit: {value}" if value else "",
    )
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}

    assert "plugin_delivery_unit_contract" in failed
    assert "plugin_delivery_unit_justification" in failed


def test_default_units_carry_no_extra_justification_burden():
    """Choosing the conservative unit must not be penalized, or the gate is a tax."""
    for unit in ("client-custom-plugin", "mu-plugin", "composer-package", "theme-integration"):
        result = oracle.validate_output("wordpress-plugin-planner", _planner_with_unit(unit))
        checks = {c["id"]: c for c in result["checks"]}
        assert checks["plugin_delivery_unit_justification"]["passed"] is True, unit


def test_distributable_plugin_requires_a_named_recurring_need():
    bare = _planner_with_unit("distributable-plugin")
    result = oracle.validate_output("wordpress-plugin-planner", bare)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}
    assert "plugin_delivery_unit_justification" in failed
    assert "plugin_delivery_unit_contract" not in failed


@pytest.mark.parametrize(
    "need",
    [
        "it would be reusable",
        "this plugin will be useful for clients",
        "generic reusable code for a client",
    ],
)
def test_hand_waved_recurring_need_is_rejected(need):
    candidate = _planner_with_unit("distributable-plugin", f"Recurring need: {need}")
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}

    assert "plugin_delivery_unit_justification" in failed


def test_named_cross_client_need_satisfies_distribution():
    candidate = _planner_with_unit(
        "distributable-plugin",
        "Recurring need: three newsroom retainers each require the same embargoed-publish "
        "scheduling workflow across separate WordPress installs",
    )
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    checks = {c["id"]: c for c in result["checks"]}

    assert checks["plugin_delivery_unit_justification"]["passed"] is True, checks


def test_core_api_direct_requires_naming_the_replacing_core_api():
    bare = _planner_with_unit("core-api-direct")
    result = oracle.validate_output("wordpress-plugin-planner", bare)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}

    assert "plugin_delivery_unit_justification" in failed


@pytest.mark.parametrize(
    "api",
    [
        "the built-in WordPress functionality",
        "core APIs",
        "use wordpress apis",
        "a core hook",
    ],
)
def test_vague_replacing_api_is_rejected(api):
    candidate = _planner_with_unit("core-api-direct", f"Replacing API: {api}")
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}

    assert "plugin_delivery_unit_justification" in failed


@pytest.mark.parametrize(
    "api",
    [
        "register_post_meta() with show_in_rest covers the whole requirement",
        "register_block_bindings_source() removes the need for a plugin here",
        "WP_Query already supports this",
    ],
)
def test_exact_core_api_satisfies_core_api_direct(api):
    candidate = _planner_with_unit("core-api-direct", f"Replacing API: {api}")
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    checks = {c["id"]: c for c in result["checks"]}

    assert checks["plugin_delivery_unit_justification"]["passed"] is True, checks


def test_delivery_unit_record_must_live_in_plugin_scope():
    """A record floating in another section does not satisfy the contract."""
    candidate = GOOD_PLANNER.replace("Delivery unit: client-custom-plugin\n", "")
    candidate = candidate.replace(
        "## Executor Handoff", "## Executor Handoff\nDelivery unit: client-custom-plugin", 1
    )
    result = oracle.validate_output("wordpress-plugin-planner", candidate)
    failed = {c["id"] for c in result["checks"] if not c["passed"]}

    assert "plugin_delivery_unit_contract" in failed


def test_delivery_unit_gate_does_not_apply_to_other_skills():
    """Only the plugin planner is held to it; the block planner must be untouched."""
    result = oracle.validate_output("wordpress-planner.block", GOOD_BLOCK_PLANNER)
    ids = {c["id"] for c in result["checks"]}

    assert not {"plugin_delivery_unit_contract", "plugin_delivery_unit_justification"} & ids
    assert result["pass"] is True


GOOD_CONTENT_MODEL_PLANNER = """\
## Content Model Summary
Plan a 3-type event-and-story content model for a cultural-institution site
migrating from a legacy CMS. Migration mode: required

## Current-State Evidence
The source system exports 3 content types, 2 vocabularies, and 1 non-node
placed block via a config snapshot; `register_post_type()` and
`register_taxonomy()` do not exist yet on the target.

## Content Behavior Analysis
Events recur across multiple date sets; stories are single-author narratives.
This does not claim any editorial workflow beyond what the brief describes.

## Post Type Taxonomy And Field Matrix
Storage decision rule applied: yes
Binding source (event_dates): core/post-meta
Editing surface (event_dates): event-dates block (register_block_bindings_source, setValues)
Binding source (footer_contact): core/post-meta
Editing surface (footer_contact): site footer template part bound via setValues
Use `register_post_meta()` with `show_in_rest` schema for event start/end dates.

## Editorial Workflow
Editorial guardrails phase: completed
Content type: event
Content type: story
Content type: exhibit
Lock level (event): contentOnly
Lock level (story): false
Lock level rationale (story): donor features need freeform layout.
Lock level (exhibit): contentOnly

## API Search And Template Implications
Expose events and stories via `show_in_rest` and template_lock contentOnly
patterns; assumption: WPGraphQL is out of scope for this phase.

## Migration And Validation Plan
Disposition row (event): custom-post-type - matches the event content type 1:1.
Disposition row (story): custom-post-type - matches the story content type 1:1.
Disposition row (exhibit): custom-post-type - matches the exhibit content type 1:1.
Disposition row (event_type): taxonomy - bounded, facetable, co-attached to event with audience.
Disposition row (audience): taxonomy - bounded, facetable, co-attached to event with event_type.
Disposition row (gallery_component): synced-pattern-with-overrides - reused identically across pages.
Disposition row (site_footer_block): site-option - facts (address, hours, social links) bind into the footer template part rather than being hardcoded.
Run `wp import` dry run then `wp search-replace --dry-run` before cutover.

## Assumption Register
Assumption: source recurrence data is exhaustive; unknown: timezone handling.

## Alternatives Considered
A single "content" CPT with taxonomy-only differentiation was rejected because
it collapses per-type editorial workflow.

## Acceptance Criteria
Every disposition row above is reconciled against the source manifest count.

## Executor Handoff
Generate the plugin registering these post types and meta via wordpress-plugin-executor.

## Critic Handoff
Send to wordpress-critic and wordpress-theme-critic.
"""


def test_good_content_model_planner_passes_new_contract_gates():
    result = oracle.validate_output("wordpress-content-model-planner", GOOD_CONTENT_MODEL_PLANNER)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_editorial_guardrails_contract"]["passed"] is True, checks
    assert checks["content_model_storage_decision_contract"]["passed"] is True, checks


def test_content_model_planner_alias_resolves_to_same_contract():
    result = oracle.validate_output("wordpress-planner.content-model", GOOD_CONTENT_MODEL_PLANNER)

    assert result["skill"] == "wordpress-content-model-planner"


def test_content_model_plan_without_editorial_guardrails_phase_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Editorial guardrails phase: completed\n", ""
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "content_model_editorial_guardrails_contract" in failed


def test_content_model_plan_with_false_lock_level_and_no_rationale_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Lock level rationale (story): donor features need freeform layout.\n", ""
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "content_model_editorial_guardrails_contract" in failed


def test_content_model_plan_defaulting_every_type_to_false_still_needs_rationale():
    """Regression for the field finding: `template_lock => false` everywhere,
    with no rationale, must not pass silently."""
    candidate = (
        GOOD_CONTENT_MODEL_PLANNER
        .replace("Lock level (event): contentOnly\n", "Lock level (event): false\n")
        .replace("Lock level (exhibit): contentOnly\n", "Lock level (exhibit): false\n")
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "content_model_editorial_guardrails_contract" in failed


def test_content_model_plan_with_five_types_and_one_lock_level_fails():
    """Regression for the review finding: counting `Lock level:` records
    instead of pairing them let 5 declared types pass on 1 record."""
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Content type: event\nContent type: story\nContent type: exhibit\n"
        "Lock level (event): contentOnly\n"
        "Lock level (story): false\n"
        "Lock level rationale (story): donor features need freeform layout.\n"
        "Lock level (exhibit): contentOnly\n",
        "Content type: event\nContent type: story\nContent type: exhibit\n"
        "Content type: program\nContent type: person\n"
        "Lock level (event): contentOnly\n",
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_editorial_guardrails_contract"]["passed"] is False
    detail = checks["content_model_editorial_guardrails_contract"]["detail"]
    assert "story" in detail and "exhibit" in detail and "program" in detail and "person" in detail


def test_content_model_plan_without_storage_decision_rule_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Storage decision rule applied: yes\n", ""
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    failed = {check["id"] for check in result["checks"] if not check["passed"]}

    assert "content_model_storage_decision_contract" in failed


def test_content_model_plan_binding_without_editing_surface_fails():
    """Regression for the field finding: a bound meta key with no named
    editing surface (template-level-only or render-only) must fail."""
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Editing surface (event_dates): event-dates block (register_block_bindings_source, setValues)\n",
        "",
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_storage_decision_contract"]["passed"] is False
    assert "event_dates" in checks["content_model_storage_decision_contract"]["detail"]


def test_content_model_plan_binding_key_mismatch_does_not_satisfy_pairing():
    """A differently-keyed editing surface must not satisfy a binding source
    for a different key -- pairing is exact, not "some surface exists"."""
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Binding source (footer_contact): core/post-meta\n",
        "Binding source (hero_headline): core/post-meta\n",
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_storage_decision_contract"]["passed"] is False
    assert "hero_headline" in checks["content_model_storage_decision_contract"]["detail"]


SOURCE_MANIFEST = {
    "schema": "wordpress-source-manifest",
    "items": [
        {"id": "event", "kind": "content_type"},
        {"id": "story", "kind": "content_type"},
        {"id": "exhibit", "kind": "content_type"},
        {"id": "event_type", "kind": "vocabulary"},
        {"id": "audience", "kind": "vocabulary"},
        {"id": "gallery_component", "kind": "component"},
        {"id": "site_footer_block", "kind": "non_node_region_block"},
    ],
}


def test_migration_disposition_coverage_passes_when_every_item_has_a_row():
    result = oracle.validate_output(
        "wordpress-content-model-planner",
        GOOD_CONTENT_MODEL_PLANNER,
        source_manifest=SOURCE_MANIFEST,
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is True, checks


def test_migration_disposition_coverage_fails_when_manifest_item_is_undispositioned():
    manifest = {
        "schema": "wordpress-source-manifest",
        "items": SOURCE_MANIFEST["items"] + [{"id": "press_release", "kind": "content_type"}],
    }
    result = oracle.validate_output(
        "wordpress-content-model-planner",
        GOOD_CONTENT_MODEL_PLANNER,
        source_manifest=manifest,
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "press_release" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_coverage_is_absent_without_a_manifest():
    result = oracle.validate_output("wordpress-content-model-planner", GOOD_CONTENT_MODEL_PLANNER)
    ids = {check["id"] for check in result["checks"]}

    assert "content_model_migration_disposition_coverage" not in ids


def test_load_source_manifest_rejects_empty_items(tmp_path):
    manifest_path = tmp_path / "source-manifest.json"
    manifest_path.write_text(json.dumps({"items": []}), encoding="utf-8")

    with pytest.raises(ValueError):
        oracle.load_source_manifest(manifest_path)


def test_migration_disposition_catch_all_row_cannot_satisfy_multiple_ids():
    """Regression for the review finding: substring containment let one row
    naming several ids in its free text satisfy every one of them."""
    candidate = """\
## Content Model Summary
Plan a content model. Migration mode: required

## Current-State Evidence
Evidence.

## Content Behavior Analysis
Behavior.

## Post Type Taxonomy And Field Matrix
Storage decision rule applied: yes

## Editorial Workflow
Editorial guardrails phase: completed
Content type: event
Lock level (event): contentOnly

## API Search And Template Implications
Implications.

## Migration And Validation Plan
Disposition row: misc -> event, story, exhibit, event_type, audience, gallery_component, site_footer_block - all still being figured out, nothing decided yet.

## Assumption Register
Assumption: none.

## Alternatives Considered
None.

## Acceptance Criteria
Criteria.

## Executor Handoff
Handoff.

## Critic Handoff
Handoff.
"""
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    detail = checks["content_model_migration_disposition_coverage"]["detail"]
    for item_id in ("event", "story", "exhibit", "event_type", "audience", "gallery_component", "site_footer_block"):
        assert item_id in detail


def test_migration_disposition_hedged_value_does_not_count(): 
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n",
        "Disposition row (event): custom-post-type - do not have a final decision yet.\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "event" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_unrecognized_token_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n",
        "Disposition row (event): maybe-a-block - unsure yet.\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "unrecognized disposition" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_duplicate_row_for_same_id_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n",
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n"
        "Disposition row (event): taxonomy - actually reconsidered.\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "duplicate disposition rows" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_row_for_id_outside_manifest_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Run `wp import` dry run then `wp search-replace --dry-run` before cutover.\n",
        "Disposition row (unknown_item): drop - not in scope.\n"
        "Run `wp import` dry run then `wp search-replace --dry-run` before cutover.\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "outside the manifest" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_placeholder_after_valid_token_fails():
    """Regression for the review finding: a hedge sitting after an
    otherwise-valid token (not covered by NEGATED_DECISION_RE) must still
    fail, not just an outright negation."""
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n",
        "Disposition row (event): custom-post-type - not decided yet.\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "event" in checks["content_model_migration_disposition_coverage"]["detail"]


@pytest.mark.parametrize(
    "placeholder",
    ["undecided", "tbd", "to be determined", "todo", "pending", "still being figured out", "unknown", "n/a", "???"],
)
def test_migration_disposition_placeholder_vocabulary_is_rejected(placeholder):
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Disposition row (event): custom-post-type - matches the event content type 1:1.\n",
        f"Disposition row (event): custom-post-type - {placeholder}\n",
    )
    result = oracle.validate_output(
        "wordpress-content-model-planner", candidate, source_manifest=SOURCE_MANIFEST
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False


def test_migration_disposition_empty_manifest_items_fails_not_vacuously():
    """Regression for the review finding: a manifest with zero items must
    not pass just because there is nothing left to check."""
    result = oracle.validate_output(
        "wordpress-content-model-planner",
        GOOD_CONTENT_MODEL_PLANNER,
        source_manifest={"schema": "wordpress-source-manifest", "items": []},
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False
    assert "no items" in checks["content_model_migration_disposition_coverage"]["detail"]


def test_migration_disposition_missing_manifest_items_key_fails_not_vacuously():
    result = oracle.validate_output(
        "wordpress-content-model-planner",
        GOOD_CONTENT_MODEL_PLANNER,
        source_manifest={"schema": "wordpress-source-manifest"},
    )
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_migration_disposition_coverage"]["passed"] is False


def test_content_model_editing_surface_placeholder_fails():
    """Regression for the review finding: `Editing surface (d): TBD` must
    not satisfy the pairing gate."""
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Editing surface (event_dates): event-dates block (register_block_bindings_source, setValues)\n",
        "Editing surface (event_dates): TBD\n",
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_storage_decision_contract"]["passed"] is False
    assert "event_dates" in checks["content_model_storage_decision_contract"]["detail"]


def test_content_model_lock_rationale_placeholder_fails():
    candidate = GOOD_CONTENT_MODEL_PLANNER.replace(
        "Lock level rationale (story): donor features need freeform layout.\n",
        "Lock level rationale (story): pending\n",
    )
    result = oracle.validate_output("wordpress-content-model-planner", candidate)
    checks = {check["id"]: check for check in result["checks"]}

    assert checks["content_model_editorial_guardrails_contract"]["passed"] is False

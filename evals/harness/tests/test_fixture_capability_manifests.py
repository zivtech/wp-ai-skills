"""Per-fixture capability-manifest sidecars for the eval lane.

``run_wordpress_high_risk_saved_outputs.py`` passes
``<fixture>.capability-manifest.json`` to the output-contract oracle as
``--capability-manifest``, which switches on the manifest-gated checks
(capability grounding, runtime-tool grounding, sync confirmation) for that
fixture's saved outputs. The sidecars are probe recordings of synthetic project
trees driven by the same fake ``wp``, ``ddev``, and ``studio`` shims the probe's
own tests use: never hand-authored JSON, and never a live host. Re-record with::

    WP_META_SKILLS_RECORD_FIXTURE_MANIFESTS=1 python3 -m pytest \\
        evals/harness/tests/test_fixture_capability_manifests.py -q

Without the opt-in this module asserts that every committed sidecar is
schema-valid, normalised, evidence-complete, paired with a fixture, and still
describes the scenario its fixture prompt assumes. ``environment.host`` comes
from the recording machine and is deliberately not compared.

The model under eval never receives the sidecar file (``invoke.py`` sends the
fixture prompt alone), so each fixture prompt embeds an excerpt of the sections
the oracle enforces under ``## Supplied `capability-manifest.json` (excerpt)``,
following the ``security-gate.json`` precedent. The recorder rewrites that block
and the always-on tests fail if prompt and sidecar drift apart.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Callable

import pytest

import probe_wordpress_environment as probe
import test_probe_wordpress_environment as probe_tests

EXCERPT_HEADING = "## Supplied `capability-manifest.json` (excerpt)"
# Line-anchored on purpose: a DOTALL ``.*`` here backtracks catastrophically.
EXCERPT_RE = re.compile(
    re.escape(EXCERPT_HEADING) + r"\n(?P<lead>(?:(?!```)[^\n]*\n)*?)```json\n(?P<body>[\s\S]*?)\n```\n"
)

ROOT = Path(__file__).resolve().parents[3]
SUITES = ROOT / "evals" / "suites"
RECORD_ENV = "WP_META_SKILLS_RECORD_FIXTURE_MANIFESTS"
SIDECAR_SUFFIX = ".capability-manifest.json"

# A ``ddev`` that only forwards ``ddev wp ...`` to the fake ``wp`` beside it.
# The probe runs host tools with a private PATH, so the shim must not depend on
# coreutils; it is Python for the same reason the fake ``wp`` is.
FAKE_DDEV_TEMPLATE = """#!{interpreter}
import os
import sys

args = sys.argv[1:]
if args[:1] == ["wp"]:
    fake_wp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wp")
    os.execv(fake_wp, ["wp", *args[1:]])
if "--version" in args:
    sys.stdout.write("ddev version v1.24.0\\n")
    raise SystemExit(0)
raise SystemExit(1)
"""


def _install_fake_ddev(bin_dir: Path) -> None:
    script = bin_dir / "ddev"
    script.write_text(FAKE_DDEV_TEMPLATE.format(interpreter=sys.executable), encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _record_ddev_pressable(tmp_path: Path) -> dict:
    """A ddev project with the Pressable provider file present."""
    root = tmp_path / "site"
    root.mkdir()
    (root / "wp-config.php").write_text("<?php\n", encoding="utf-8")
    (root / ".ddev" / "providers").mkdir(parents=True)
    (root / ".ddev" / "config.yaml").write_text("name: acme\ntype: wordpress\n", encoding="utf-8")
    (root / ".ddev" / "providers" / "pressable.yaml").write_text("provider: pressable\n", encoding="utf-8")
    bin_dir = probe_tests._install_fake_wp(tmp_path)
    _install_fake_ddev(bin_dir)
    return probe.normalize_manifest(probe_tests._run_probe(root, [str(bin_dir)]))


def _record_studio_builtin(tmp_path: Path) -> dict:
    """A Studio-managed project whose ``studio --help`` names the ``mcp`` command."""
    root = probe_tests._studio_project(tmp_path)
    bin_dir = probe_tests._install_fake_studio(tmp_path)
    return probe.normalize_manifest(probe_tests._run_probe(root, [str(bin_dir)]))


def _assert_ddev_pressable(manifest: dict) -> None:
    environment = manifest["environment"]
    assert environment["kind"] == "ddev"
    assert environment["invocation_prefix"] == ["ddev", "wp"]
    assert manifest["wp_cli"]["status"] == "AVAILABLE"
    runtime = manifest["runtime_tools"]
    assert runtime["status"] == "AVAILABLE"
    assert [server["kind"] for server in runtime["servers"]] == ["ddev-pressable"]
    server = runtime["servers"][0]
    assert server["superseded"] is False
    tools = {tool["name"]: tool for tool in server["tools"]}
    assert tools["ddev push pressable"]["side_effect"] == "outward_sync"
    assert tools["ddev push pressable"]["target_constraint"] == "staging-only"
    assert tools["ddev push pressable"]["confirm_required"] is True
    assert tools["ddev pull pressable"]["side_effect"] == "inward_sync"
    assert manifest["capabilities"]["has_outward_sync_tool"] is True


def _assert_studio_builtin(manifest: dict) -> None:
    environment = manifest["environment"]
    assert environment["kind"] == "studio"
    assert environment["invocation_prefix"] == ["studio", "wp"]
    assert manifest["wp_cli"]["status"] == "AVAILABLE"
    runtime = manifest["runtime_tools"]
    assert runtime["status"] == "AVAILABLE"
    assert [server["kind"] for server in runtime["servers"]] == ["studio-mcp-builtin"]
    server = runtime["servers"][0]
    assert server["superseded"] is False
    tools = {tool["name"]: tool for tool in server["tools"]}
    assert tools["site_create"]["side_effect"] == "provision"
    assert tools["site_push"]["side_effect"] == "outward_sync"
    assert manifest["capabilities"]["can_provision_runtime_site"] is True
    assert manifest["runtime_tools"]["deprecated_detected"] == []


def manifest_excerpt(manifest: dict) -> dict:
    """The sections the output-contract oracle reads, in manifest order.

    This is what a fixture prompt shows the model: enough to be graded fairly on
    grounding, prefix, and sync confirmation, without the evidence ledger and
    host inventory that the oracle never consults.
    """
    environment = manifest["environment"]
    servers = []
    for server in manifest["runtime_tools"].get("servers", []):
        tools = []
        for tool in server.get("tools", []):
            entry = {
                "name": tool["name"],
                "side_effect": tool["side_effect"],
                "confirm_required": tool["confirm_required"],
            }
            if "target_constraint" in tool:
                entry["target_constraint"] = tool["target_constraint"]
            tools.append(entry)
        servers.append({
            "id": server["id"],
            "kind": server["kind"],
            "superseded": server.get("superseded", False),
            "tools": tools,
        })
    return {
        "schema_version": manifest["schema_version"],
        "environment": {
            "kind": environment["kind"],
            "status": environment["status"],
            "invocation_prefix": environment["invocation_prefix"],
        },
        "wp_cli": {"status": manifest["wp_cli"]["status"]},
        "verification_tools": {
            name: state["status"] for name, state in sorted(manifest["verification_tools"].items())
        },
        "runtime_tools": {
            "status": manifest["runtime_tools"]["status"],
            "servers": servers,
        },
        "capabilities": manifest["capabilities"],
    }


def _prompt_path(sidecar: Path) -> Path:
    return sidecar.parent / f"{sidecar.name[: -len(SIDECAR_SUFFIX)]}.md"


def _embedded_excerpt(prompt_text: str) -> dict | None:
    match = EXCERPT_RE.search(prompt_text)
    return json.loads(match.group("body")) if match else None


def _write_excerpt(prompt_path: Path, manifest: dict) -> None:
    """Rewrite the fenced JSON under the excerpt heading; the heading must already exist."""
    text = prompt_path.read_text(encoding="utf-8")
    match = EXCERPT_RE.search(text)
    assert match, f"{prompt_path} lacks the block {EXCERPT_HEADING!r}"
    body = json.dumps(manifest_excerpt(manifest), indent=2)
    replacement = f"{EXCERPT_HEADING}\n{match.group('lead')}```json\n{body}\n```\n"
    prompt_path.write_text(text[: match.start()] + replacement + text[match.end():], encoding="utf-8")


SCENARIOS: dict[Path, tuple[Callable[[Path], dict], Callable[[dict], None]]] = {
    SUITES / "wordpress-planner.migration" / "fixtures" / f"host-sync-staging-cutover-v1{SIDECAR_SUFFIX}": (
        _record_ddev_pressable,
        _assert_ddev_pressable,
    ),
    SUITES / "wordpress-blueprint-executor" / "fixtures" / f"studio-launch-handoff-v1{SIDECAR_SUFFIX}": (
        _record_studio_builtin,
        _assert_studio_builtin,
    ),
}


def _committed_sidecars() -> list[Path]:
    return sorted(SUITES.glob(f"*/fixtures/*{SIDECAR_SUFFIX}"))


def _write(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@pytest.mark.parametrize("path", sorted(SCENARIOS), ids=lambda p: p.parent.parent.name + "/" + p.name)
def test_record_fixture_capability_manifests(path: Path, tmp_path: Path) -> None:
    """Opt in with WP_META_SKILLS_RECORD_FIXTURE_MANIFESTS=1 to re-record the sidecars."""
    if os.environ.get(RECORD_ENV) != "1":
        pytest.skip(f"set {RECORD_ENV}=1 to re-record the fixture sidecars")
    record, check = SCENARIOS[path]
    manifest = record(tmp_path)
    assert probe_tests._schema_errors(manifest) == []
    check(manifest)
    _write(path, manifest)
    _write_excerpt(_prompt_path(path), manifest)


def test_every_scenario_sidecar_is_committed() -> None:
    missing = [str(path.relative_to(ROOT)) for path in SCENARIOS if not path.exists()]
    assert missing == [], f"re-record with {RECORD_ENV}=1: {missing}"


def test_every_committed_sidecar_has_a_scenario_and_a_fixture() -> None:
    for path in _committed_sidecars():
        assert path in SCENARIOS, f"{path} has no recording scenario in this module"
        stem = path.name[: -len(SIDECAR_SUFFIX)]
        assert (path.parent / f"{stem}.md").exists(), f"{path} has no fixture prompt"
        assert (path.parent / f"{stem}.metadata.yaml").exists(), f"{path} has no fixture metadata"


@pytest.mark.parametrize("path", sorted(SCENARIOS), ids=lambda p: p.parent.parent.name + "/" + p.name)
def test_committed_sidecar_is_a_valid_normalised_recording(path: Path) -> None:
    if not path.exists():
        pytest.skip("sidecar not recorded yet")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert probe_tests._schema_errors(manifest) == []
    assert probe.normalize_manifest(manifest) == manifest, "sidecar must be committed normalised"
    assert probe.evidence_gaps(manifest) == []
    assert manifest["schema_version"] == probe.SCHEMA_VERSION
    SCENARIOS[path][1](manifest)


@pytest.mark.parametrize("path", sorted(SCENARIOS), ids=lambda p: p.parent.parent.name + "/" + p.name)
def test_fresh_recording_still_matches_the_committed_scenario(path: Path, tmp_path: Path) -> None:
    """The recorder and the committed file must not drift on anything a validator reads.

    Host tool versions differ per machine, so ``environment.host`` and the
    evidence ledger are excluded; every section a consumer gates on is compared.
    """
    if not path.exists():
        pytest.skip("sidecar not recorded yet")
    record, _ = SCENARIOS[path]
    fresh = record(tmp_path)
    committed = json.loads(path.read_text(encoding="utf-8"))
    for section in ("wp_cli", "runtime_tools", "capabilities", "verification_tools", "mcp", "abilities"):
        assert fresh[section] == committed[section], section
    for key in ("kind", "status", "invocation_prefix", "marker_file"):
        assert fresh["environment"][key] == committed["environment"][key], key


@pytest.mark.parametrize("path", sorted(SCENARIOS), ids=lambda p: p.parent.parent.name + "/" + p.name)
def test_fixture_prompt_excerpt_matches_the_committed_sidecar(path: Path) -> None:
    """The model is graded against the sidecar, so the prompt must show the same facts."""
    if not path.exists():
        pytest.skip("sidecar not recorded yet")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    embedded = _embedded_excerpt(_prompt_path(path).read_text(encoding="utf-8"))
    assert embedded is not None, f"{_prompt_path(path)} lacks {EXCERPT_HEADING!r}"
    assert embedded == manifest_excerpt(manifest)

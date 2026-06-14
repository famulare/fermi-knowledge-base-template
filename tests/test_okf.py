"""Tests for the OKF bridge (export/import/validate). Run with:

    uv run --with pytest pytest tests/ -q

Covers the independent-review hardening list: Gate-1 equivalence, base-conformance errors,
reserved-file exemption, broken-link tolerance, import safety (symlink/oversize), and
agreement between okf_export's marker parser and kb_audit.extract_fields.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import kb_audit  # noqa: E402
import okf_export  # noqa: E402
import okf_import  # noqa: E402
import okf_validate  # noqa: E402

CONCEPT = """---
type: claim
title: Test Claim
origin: '[UserName]'
status: Active
layer: examples
---

# Test Claim

Body.
"""


def _write(d: Path, rel: str, text: str) -> Path:
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# --- Gate 1: round-trip equivalence on the live example corpus -----------------------------
def test_selftest_equivalence_passes():
    assert okf_export.selftest(REPO, ["examples"]) == 0


# --- export → validate the real examples bundle --------------------------------------------
def test_examples_bundle_is_conformant(tmp_path):
    concepts, _ = okf_export.build_concepts(REPO, ["examples"])
    okf_export.write_bundle(concepts, tmp_path)
    fnd = okf_validate.validate_bundle(tmp_path)
    assert fnd.base == [] and fnd.profile == [], (fnd.base, fnd.profile)


# --- OKF base conformance errors -----------------------------------------------------------
def test_missing_type_is_base_error(tmp_path):
    _write(tmp_path, "claims/c.md", "---\ntitle: No Type\norigin: x\nstatus: Active\nlayer: meta\n---\n\n# X\n")
    fnd = okf_validate.validate_bundle(tmp_path)
    assert any("type" in m for m in fnd.base)


def test_malformed_frontmatter_is_base_error(tmp_path):
    _write(tmp_path, "claims/c.md", "# No Frontmatter At All\n\nbody\n")
    fnd = okf_validate.validate_bundle(tmp_path)
    assert fnd.base, "expected a base error for missing frontmatter"


# --- reserved-file exemption ---------------------------------------------------------------
def test_reserved_files_exempt_from_type(tmp_path):
    _write(tmp_path, "claims/c.md", CONCEPT)
    _write(tmp_path, "index.md", "# Index\n\n* [Test Claim](/claims/c.md)\n")
    _write(tmp_path, "log.md", "# Log\n\n## 2026-06-13\n- **Update** Test Claim\n")
    fnd = okf_validate.validate_bundle(tmp_path)
    assert fnd.base == [], fnd.base  # reserved files must not trigger the type rule


# --- broken-link tolerance (OKF MUST tolerate) ---------------------------------------------
def test_broken_link_tolerated(tmp_path):
    body = CONCEPT.replace("Body.", "See [Gone](/models/does_not_exist.md \"rel:supports\").")
    _write(tmp_path, "claims/c.md", body)
    fnd = okf_validate.validate_bundle(tmp_path)
    assert fnd.base == [] and fnd.profile == []  # a dangling link is not a violation


# --- import safety -------------------------------------------------------------------------
def test_import_rejects_symlink(tmp_path):
    bundle = tmp_path / "bundle"
    _write(bundle, "claims/c.md", CONCEPT)
    (bundle / "evil.md").symlink_to("/etc/hosts")
    with pytest.raises(SystemExit):
        okf_import._safe_relpaths(bundle)


def test_import_rejects_oversize(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    _write(bundle, "big.md", CONCEPT)
    monkeypatch.setattr(okf_import, "MAX_FILE_BYTES", 10)
    with pytest.raises(SystemExit):
        okf_import._safe_relpaths(bundle)


def test_import_propose_only_writes_no_meta(tmp_path):
    bundle = tmp_path / "bundle"
    _write(bundle, "claims/c.md", CONCEPT)
    _write(bundle, "index.md", "# Index\n")
    repo = tmp_path / "repo"
    (repo / "index").mkdir(parents=True)
    (repo / "index" / "tags.md").write_text("", encoding="utf-8")
    okf_import.import_bundle(bundle, repo, org="Acme", source="", reason="",
                             dry_run=False, force=False)
    assert (repo / "raw" / "curated" / "okf" / "bundle").is_dir()       # evidence landed
    assert list((repo / "views" / "ephemeral").glob("okf-import-*.md"))  # proposal written
    assert not (repo / "meta").exists()                                  # NEVER writes meta/


# --- parser agreement: okf_export markers == kb_audit.extract_fields -----------------------
def test_marker_parser_agrees_with_kb_audit():
    # For non-contradiction examples, the origin/status okf_export lifts must match kb_audit's.
    mismatches = []
    for p in sorted((REPO / "examples").glob("*.md")):
        if p.name.startswith("contradiction_"):
            continue  # top-level origin is intentionally exempt for contradictions
        text = p.read_text(encoding="utf-8")
        c = okf_export.parse_concept(f"examples/{p.name}", text)
        if c is None:
            continue
        fields = kb_audit.extract_fields(text)
        for key, fm_key in (("Origin", "origin"), ("Status", "status")):
            if key in fields:
                want = fields[key]
                got = c.fm.get(fm_key)
                # okf_export stores base status; compare on the base of kb_audit's value too
                if fm_key == "status":
                    want = kb_audit.parse_base_status(want) if hasattr(kb_audit, "parse_base_status") else want
                if got != want:
                    mismatches.append((p.name, key, got, want))
    assert not mismatches, mismatches

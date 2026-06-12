#!/usr/bin/env python3
"""KB accuracy audit script for the Fermi knowledge base.

Validates structural compliance, cross-references, origin attribution,
status-evidence consistency, and URL/DOI patterns across the entire corpus.

Reuses infrastructure from generate_router.py (CONTENT_DIRS, file-walking,
tag parsing) and kb_search.py (origin/status extraction).

Usage:
    uv run scripts/kb_audit.py                    # Full audit, human-readable summary
    uv run scripts/kb_audit.py --json              # Machine-parseable JSON output
    uv run scripts/kb_audit.py --severity ERROR    # Filter to ERROR only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Shared infrastructure (mirrors generate_router.py / kb_search.py)
# ---------------------------------------------------------------------------

CONTENT_DIRS = [
    "examples",
    "raw",
    "meta",
    "special_projects",
    "views/persistent",
]

LAYER_PREFIXES = (
    "examples/",
    "meta/",
    "raw/",
    "special_projects/",
    "views/",
    "index/",
    "contracts/",
    "scripts/",
)


def find_repo_root() -> Path:
    """Find the repository root by looking for CLAUDE.md."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def walk_content(repo_root: Path) -> list[Path]:
    """Walk content directories and return all markdown files."""
    files: list[Path] = []
    for content_dir in CONTENT_DIRS:
        dir_path = repo_root / content_dir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            if any(part.startswith((".", "_")) for part in md_file.parts):
                continue
            files.append(md_file)
    return files


def classify_layer(rel_path: str) -> tuple[str, str | None]:
    """Classify file into layer/sublayer."""
    parts = rel_path.split("/")
    layer = parts[0]
    if layer == "views":
        return "views", None
    sublayer = parts[1] if len(parts) > 2 else None
    return layer, sublayer


# ---------------------------------------------------------------------------
# Finding data structure
# ---------------------------------------------------------------------------

class Finding:
    """A single audit finding."""

    def __init__(
        self,
        severity: str,   # ERROR | WARNING | INFO
        category: str,    # structural | crossref | origin | status | index | url
        file_path: str,
        message: str,
        detail: str = "",
    ):
        self.severity = severity
        self.category = category
        self.file_path = file_path
        self.message = message
        self.detail = detail

    def to_dict(self) -> dict:
        d = {
            "severity": self.severity,
            "category": self.category,
            "file_path": self.file_path,
            "message": self.message,
        }
        if self.detail:
            d["detail"] = self.detail
        return d

    def __repr__(self):
        return f"[{self.severity}] {self.category}: {self.file_path} — {self.message}"


# ---------------------------------------------------------------------------
# A. Structural compliance
# ---------------------------------------------------------------------------

# Required H2 sections per meta type (heading text, case-insensitive match)
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "claims": [
        "evidence",
        "assumptions",
        "uncertainty",
        "related",
        "provenance",
    ],
    "models": [
        "summary",
        "core mechanisms",
        "predictions/implications",
        "evidence base",
        "assumptions",
        "scope",
        "tensions/coexistence",
        "provenance",
    ],
    "maps": [
        "purpose",
        "core concepts",
        "key relationships",
        "active models",  # "Active Models in This Domain" also matches
        "open questions",
        "evidence base",
        "provenance",
    ],
    "contradictions": [
        "item a",
        "item b",
        "nature of tension",
        "possible resolutions",
    ],
    "timelines": [],  # Timelines are freeform but need Status
}

# Required inline fields per meta type (bold field names)
REQUIRED_FIELDS: dict[str, list[str]] = {
    "claims": ["Statement", "Origin", "Status"],
    "models": ["Origin", "Status"],
    "maps": ["Origin", "Status"],
    "contradictions": ["Status"],
    "timelines": ["Status"],
}

# Valid Status values per type (base values before any em-dash annotation)
VALID_STATUS: dict[str, set[str]] = {
    "claims": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived"},
    "models": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived", "Proposed"},
    "maps": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived"},
    "contradictions": {"Open", "Resolved", "Coexisting", "Productive tension"},
    "timelines": {"Draft", "Active", "Superseded", "Archived"},
}


def parse_base_status(status_val: str) -> str:
    """Extract base status before any em-dash annotation.

    E.g., 'Active — Conceptual framework' -> 'Active'
         'Productive tension (do not resolve)' -> 'Productive tension'
    """
    # Strip em-dash annotations
    for sep in [" — ", " - ", " – "]:
        if sep in status_val:
            status_val = status_val.split(sep, 1)[0].strip()
    # Strip parenthetical annotations
    m = re.match(r"^(.+?)\s*\(", status_val)
    if m:
        candidate = m.group(1).strip()
        # Only strip parens if the result is a known status word
        # (avoid stripping "Productive tension" -> "Productive")
        all_valid = set()
        for vs in VALID_STATUS.values():
            all_valid.update(vs)
        if candidate in all_valid:
            return candidate
    return status_val

# Extra fields required for External-origin files
# Accept both "Original Author(s)" and "Original Author" variants
EXTERNAL_ORIGIN_FIELDS = [
    ("Original Author(s)", "Original Author"),  # tuple = accept either
    ("Original Source",),
    ("Ingest Reason",),
]

# Valid base origin types (checked as prefix of origin value).
# Identity comes from config/system.yml (user.name / persona.name); the shipped
# placeholder "[UserName]" is accepted so example entries validate before SETUP.
_DEFAULT_VALID_ORIGIN_BASES = ["[UserName]", "Fermi", "Co-created", "External"]


def get_valid_origin_bases(repo_root: Path) -> list[str]:
    """Valid origin bases, derived from config/system.yml when available."""
    config_file = repo_root / "config" / "system.yml"
    if config_file.exists():
        try:
            import yaml

            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            user_name = str((data.get("user", {}) or {}).get("name", "")).strip()
            persona = str((data.get("persona", {}) or {}).get("name", "")).strip() or "Fermi"
            user_base = user_name if (user_name and "[CONFIGURE]" not in user_name) else "[UserName]"
            return [user_base, persona, "Co-created", "External"]
        except Exception:
            pass
    return _DEFAULT_VALID_ORIGIN_BASES

# Semantic equivalents for section name matching (lowercase)
SECTION_EQUIVALENTS: dict[str, list[str]] = {
    "summary": ["summary", "overview", "description", "what this"],
    "core mechanisms": ["core mechanisms", "mechanisms", "architecture", "how it works", "core structure"],
    "predictions/implications": ["predictions", "implications", "consequences", "applications"],
    "evidence base": ["evidence base", "evidence", "sources", "primary sources"],
    "assumptions": ["assumptions", "prerequisites", "required conditions"],
    "scope": ["scope", "applicability", "where applicable", "domain"],
    "tensions/coexistence": ["tensions", "coexistence", "contradicts", "conflicts"],
    "provenance": ["provenance", "created", "change log"],
    "purpose": ["purpose", "overview", "what this map", "about"],
    "core concepts": ["core concepts", "concepts", "key ideas", "central ideas"],
    "key relationships": ["key relationships", "relationships", "connections between"],
    "active models": ["active models", "related models", "models in this domain"],
    "open questions": ["open questions", "questions", "unknowns", "gaps"],
    "evidence": ["evidence", "primary sources", "supporting evidence", "origin and evidence"],
    "uncertainty": ["uncertainty", "uncertainties", "open questions", "what remains"],
    "related": ["related", "supports", "conflicts with", "connections"],
    "item a": ["item a", "position a", "claim a", "view a", "side a",
               "kb position", "kb framework", "kb phenomenology"],
    "item b": ["item b", "position b", "claim b", "view b", "side b",
               "psm position", "psm framework", "psm model",
               "anthropic position", "alternative"],
    "nature of tension": ["nature of tension", "nature of", "tension", "what's at stake",
                          "the disagreement", "core tension"],
    "possible resolutions": ["possible resolutions", "resolutions", "resolution paths",
                              "ways forward", "productive tension"],
}


def extract_fields(text: str) -> dict[str, str]:
    """Extract bold-prefixed fields from file text (first 80 lines)."""
    fields: dict[str, str] = {}
    for line in text.split("\n")[:80]:
        line = line.strip()
        # Match **FieldName:** value
        m = re.match(r"\*\*(.+?):\*\*\s*(.*)", line)
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def extract_h2_headings(text: str) -> list[str]:
    """Extract all H2 heading texts (lowercase) from the file."""
    headings = []
    for line in text.split("\n"):
        m = re.match(r"^##\s+(.+)$", line.rstrip())
        if m:
            headings.append(m.group(1).strip().lower())
    return headings


def detect_meta_type(rel_path: str) -> str | None:
    """Detect the meta file type from its path."""
    if not rel_path.startswith("meta/"):
        return None
    parts = rel_path.split("/")
    if len(parts) < 3:
        return None
    subdir = parts[1]
    if subdir in REQUIRED_SECTIONS:
        return subdir
    return None


def check_structural_compliance(
    rel_path: str, text: str, findings: list[Finding], repo_root: Path
) -> None:
    """Check a meta file against its template requirements."""
    meta_type = detect_meta_type(rel_path)
    if meta_type is None:
        return

    # Skip template/scaffolding files (e.g. _template.md, README.md)
    base = rel_path.split("/")[-1]
    if "_TEMPLATE" in rel_path or base.startswith("_") or base == "README.md":
        return

    fields = extract_fields(text)
    h2_headings = extract_h2_headings(text)

    # Check required inline fields
    for field_name in REQUIRED_FIELDS.get(meta_type, []):
        if field_name not in fields:
            # Statement can also appear as an H2 section (## Statement or ## Claim Statement)
            if field_name == "Statement":
                has_statement_section = any(
                    h.startswith("statement") or h.startswith("claim statement")
                    for h in h2_headings
                )
                if has_statement_section:
                    continue  # Satisfied by section header
            findings.append(Finding(
                "ERROR", "structural", rel_path,
                f"Missing required field: **{field_name}:**",
            ))

    # Check Status validity (parse base status before annotation)
    status_val = fields.get("Status", "")
    base_status = parse_base_status(status_val) if status_val else ""
    if status_val:
        valid = VALID_STATUS.get(meta_type, set())
        if valid and base_status not in valid:
            findings.append(Finding(
                "ERROR", "structural", rel_path,
                f"Invalid Status value: '{status_val}'",
                f"Valid base values: {', '.join(sorted(valid))}",
            ))

    # Check Origin format (check that it starts with a valid base type)
    origin_val = fields.get("Origin", "")
    if origin_val:
        valid_bases = get_valid_origin_bases(repo_root)
        has_valid_base = any(origin_val.startswith(b) for b in valid_bases)
        if not has_valid_base:
            findings.append(Finding(
                "ERROR", "origin", rel_path,
                f"Origin doesn't start with a valid base type: '{origin_val}'",
                f"Must start with one of: {', '.join(valid_bases)}",
            ))

    # Check External-origin extra fields
    # Skip for contradictions — they have per-Item origins, not file-level
    if origin_val and origin_val.startswith("External") and meta_type != "contradictions":
        for field_variants in EXTERNAL_ORIGIN_FIELDS:
            if isinstance(field_variants, str):
                field_variants = (field_variants,)
            if not any(v in fields for v in field_variants):
                findings.append(Finding(
                    "WARNING", "origin", rel_path,
                    f"External-origin file missing field: **{field_variants[0]}:**",
                ))

    # Check required H2 sections (with semantic equivalents)
    # Files with Reflection status have relaxed section requirements
    is_reflection = base_status == "Reflection"
    required = REQUIRED_SECTIONS.get(meta_type, [])
    for section_name in required:
        # Check section name and common semantic equivalents
        equivalents = SECTION_EQUIVALENTS.get(section_name, [section_name])
        matched = any(
            any(eq in h for eq in equivalents)
            for h in h2_headings
        )
        if not matched:
            severity = "INFO" if is_reflection else "WARNING"
            findings.append(Finding(
                severity, "structural", rel_path,
                f"Missing expected section: ## {section_name.title()}",
            ))


# ---------------------------------------------------------------------------
# B. Cross-reference validity
# ---------------------------------------------------------------------------

# Pattern to match backtick-enclosed file paths
CROSSREF_PATTERN = re.compile(
    r"`("
    r"(?:meta|raw|special_projects|views|index|contracts|scripts|examples)"
    r"/[^`\s]+\.(?:md|py|R|json|db)"
    r"(?::\d+(?:-\d+)?)?)"  # optional :line or :start-end
    r"`"
)


def extract_crossrefs(text: str) -> list[tuple[str, str, int]]:
    """Extract cross-references from file text.

    Returns list of (full_ref, file_part, line_number) tuples.
    """
    refs: list[tuple[str, str, int]] = []
    for line_num, line in enumerate(text.split("\n"), 1):
        for m in CROSSREF_PATTERN.finditer(line):
            full_ref = m.group(1)
            # Split off line-number suffix
            parts = full_ref.split(":")
            file_part = parts[0]
            refs.append((full_ref, file_part, line_num))
    return refs


def check_crossrefs(
    rel_path: str,
    text: str,
    corpus_paths: set[str],
    repo_root: Path,
    findings: list[Finding],
) -> list[tuple[str, str]]:
    """Check all cross-references in a file. Returns list of (source, target) pairs."""
    # Skip template files — they contain placeholder paths by design
    if "_TEMPLATE" in rel_path:
        return []

    # Skip known test/prototype files with intentional broken refs
    CROSSREF_SKIP_FILES = {
        "raw/notes/2026-01-22_system-implementation-test.md",
    }
    if rel_path in CROSSREF_SKIP_FILES:
        return []

    refs = extract_crossrefs(text)
    edges: list[tuple[str, str]] = []

    for full_ref, file_part, line_num in refs:
        # Skip teaching/placeholder paths (e.g. YYYY-MM-DD slugs, <angle-bracket> tokens)
        # used in example entries to illustrate link structure without pointing at real files.
        if "YYYY" in file_part or "<" in file_part or ">" in file_part:
            continue
        edges.append((rel_path, file_part))

        # Check file exists
        if file_part not in corpus_paths:
            # Also check if it's a non-content file that exists on disk
            if not (repo_root / file_part).exists():
                findings.append(Finding(
                    "ERROR", "crossref", rel_path,
                    f"Broken cross-reference at line {line_num}: `{full_ref}`",
                    f"File not found: {file_part}",
                ))

        # Check line-number references against actual line counts
        if ":" in full_ref:
            line_spec = full_ref.split(":", 1)[1]
            target_path = repo_root / file_part
            if target_path.exists():
                try:
                    with open(target_path, "r", encoding="utf-8", errors="replace") as tf:
                        target_text = tf.read()
                    line_count = target_text.count("\n") + 1

                    # Skip line-count validation for condensed chat files that
                    # reference original transcript line numbers (they self-document
                    # the original count via transcript_lines in frontmatter)
                    if "transcript_lines:" in target_text[:500]:
                        continue

                    # Parse line spec (e.g., "42" or "42-58")
                    line_parts = line_spec.split("-")
                    max_line = int(line_parts[-1])
                    if max_line > line_count:
                        findings.append(Finding(
                            "WARNING", "crossref", rel_path,
                            f"Line reference exceeds file length at line {line_num}: `{full_ref}`",
                            f"File has {line_count} lines, reference points to line {max_line}",
                        ))
                except (ValueError, OSError):
                    pass

    return edges


# ---------------------------------------------------------------------------
# C. Origin attribution consistency
# ---------------------------------------------------------------------------

KNOWN_MODEL_NAMES = {
    "Opus 4.5", "Opus 4.6",
    "Sonnet 4.5", "Sonnet 4.6",
    "Haiku 4.5",
    "GPT-4", "GPT-4o", "GPT-5",
    "ChatGPT",
    "Claude 3.5 Sonnet", "Claude 3 Opus",
}


def check_origin_consistency(
    rel_path: str, text: str, findings: list[Finding]
) -> None:
    """Check origin attribution for consistency issues."""
    fields = extract_fields(text)
    origin_val = fields.get("Origin", "")

    if not origin_val:
        return

    # Check for Fermi origin with unrecognized model name
    fermi_match = re.match(r"Fermi\s*\((.+)\)", origin_val)
    if fermi_match:
        model = fermi_match.group(1).strip()
        if model not in KNOWN_MODEL_NAMES:
            findings.append(Finding(
                "INFO", "origin", rel_path,
                f"Fermi origin with unrecognized model: '{model}'",
                "May be valid — just flagging for review",
            ))

    # Check Co-created with Fermi for model name
    cocreated_match = re.match(r"Co-created\s*\(.+Fermi\s*\((.+?)\).*\)", origin_val)
    if cocreated_match:
        model = cocreated_match.group(1).strip()
        if model not in KNOWN_MODEL_NAMES:
            findings.append(Finding(
                "INFO", "origin", rel_path,
                f"Co-created Fermi model unrecognized: '{model}'",
                "May be valid — just flagging for review",
            ))


# ---------------------------------------------------------------------------
# D. Status-evidence signals
# ---------------------------------------------------------------------------

def check_status_evidence(
    rel_path: str, text: str, repo_root: Path, findings: list[Finding]
) -> None:
    """Check for status-evidence mismatches."""
    meta_type = detect_meta_type(rel_path)
    if meta_type is None or "_TEMPLATE" in rel_path:
        return

    fields = extract_fields(text)
    status = fields.get("Status", "")
    base_status = parse_base_status(status) if status else ""

    # Active claims with zero evidence entries
    if meta_type == "claims" and base_status == "Active":
        # Look for raw/ references in Evidence-like sections
        in_evidence = False
        has_evidence_ref = False
        for line in text.split("\n"):
            if re.match(r"^##\s+(Supporting\s+)?Evidence", line, re.IGNORECASE):
                in_evidence = True
                continue
            if re.match(r"^##\s+Origin and Evidence", line, re.IGNORECASE):
                in_evidence = True
                continue
            if in_evidence and re.match(r"^##\s+", line):
                break
            if in_evidence and re.search(r"`raw/", line):
                has_evidence_ref = True
                break

        if not has_evidence_ref:
            findings.append(Finding(
                "WARNING", "status", rel_path,
                "Active claim has no raw/ evidence references in Evidence section",
            ))

    # Superseded items without "Superseded by" link
    if base_status == "Superseded":
        if "superseded by" not in text.lower() and "supersedes" not in text.lower():
            findings.append(Finding(
                "WARNING", "status", rel_path,
                "Superseded status but no 'Superseded by' link found",
            ))

    # Stale Drafts (file modification date vs creation date)
    if base_status == "Draft":
        file_path = repo_root / rel_path
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if (datetime.now() - mtime) > timedelta(days=30):
                findings.append(Finding(
                    "INFO", "status", rel_path,
                    f"Draft file unchanged for >30 days (last modified: {mtime.strftime('%Y-%m-%d')})",
                ))
        except OSError:
            pass


# ---------------------------------------------------------------------------
# E. Index staleness
# ---------------------------------------------------------------------------

def check_index_staleness(
    corpus_paths: set[str], repo_root: Path, findings: list[Finding]
) -> None:
    """Check index files for staleness issues."""
    # Check tags.md for stale references
    tags_file = repo_root / "index" / "tags.md"
    if tags_file.exists():
        tagged_meta: set[str] = set()
        with open(tags_file, "r", encoding="utf-8") as f:
            in_files = False
            for line in f:
                line = line.rstrip()
                if line.startswith("**Files:**"):
                    in_files = True
                    continue
                if in_files:
                    fm = re.match(r"^- (.+)$", line)
                    if fm:
                        ref = fm.group(1).strip()
                        ref_path = re.split(r"\s+\(", ref)[0].strip()
                        # Check if path is a file reference
                        if any(ref_path.startswith(p) for p in LAYER_PREFIXES):
                            if not ref_path.endswith("/"):
                                if ref_path not in corpus_paths and not (repo_root / ref_path).exists():
                                    findings.append(Finding(
                                        "ERROR", "index", "index/tags.md",
                                        f"Stale tag reference: {ref_path}",
                                    ))
                                else:
                                    tagged_meta.add(ref_path)
                            else:
                                # Directory reference — check if any file exists under it
                                prefix = ref_path.rstrip("/")
                                if not any(p.startswith(prefix + "/") for p in corpus_paths):
                                    findings.append(Finding(
                                        "WARNING", "index", "index/tags.md",
                                        f"Stale directory tag reference: {ref_path}",
                                    ))
                    elif line and not line.startswith("-") and not line.startswith(" "):
                        in_files = False

        # Find untagged meta files
        meta_files = {p for p in corpus_paths if p.startswith("meta/") and "_TEMPLATE" not in p}
        untagged = meta_files - tagged_meta
        if untagged:
            findings.append(Finding(
                "INFO", "index", "index/tags.md",
                f"{len(untagged)} meta files have no tag entries",
                "Files: " + ", ".join(sorted(list(untagged)[:10]))
                + (f" ... and {len(untagged) - 10} more" if len(untagged) > 10 else ""),
            ))

    # Check link_graph.md for stale references
    link_graph_file = repo_root / "index" / "link_graph.md"
    if link_graph_file.exists():
        with open(link_graph_file, "r", encoding="utf-8") as f:
            link_text = f.read()
        for m in CROSSREF_PATTERN.finditer(link_text):
            full_ref = m.group(1)
            file_part = full_ref.split(":")[0]
            if file_part not in corpus_paths and not (repo_root / file_part).exists():
                findings.append(Finding(
                    "ERROR", "index", "index/link_graph.md",
                    f"Stale link_graph reference: `{full_ref}`",
                ))


# ---------------------------------------------------------------------------
# F. URL/DOI pattern validation
# ---------------------------------------------------------------------------

URL_PATTERN = re.compile(r"https?://[^\s\)>\]\"]+")
DOI_PATTERN = re.compile(r"\b(10\.\d{4,}/[^\s\)>\]\"]+)")
DOI_URL_PATTERN = re.compile(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s\)>\]\"]+)")


def check_urls_and_dois(
    rel_path: str, text: str, all_urls: dict[str, list[str]],
    all_dois: dict[str, list[str]], findings: list[Finding]
) -> None:
    """Extract URLs and DOIs, check for duplicates and format issues."""
    urls = URL_PATTERN.findall(text)
    for url in urls:
        # Clean trailing punctuation
        url = url.rstrip(".,;:")
        all_urls.setdefault(url, []).append(rel_path)

    # Extract DOIs (both bare and URL form)
    for m in DOI_PATTERN.finditer(text):
        doi = m.group(1).rstrip(".,;:")
        all_dois.setdefault(doi, []).append(rel_path)

    for m in DOI_URL_PATTERN.finditer(text):
        doi = m.group(1).rstrip(".,;:")
        all_dois.setdefault(doi, []).append(rel_path)


def report_url_doi_findings(
    all_urls: dict[str, list[str]],
    all_dois: dict[str, list[str]],
    findings: list[Finding],
) -> None:
    """Report duplicate URLs/DOIs across files."""
    for doi, files in all_dois.items():
        if len(set(files)) > 2:  # Same DOI in >2 different files is notable
            findings.append(Finding(
                "INFO", "url", files[0],
                f"DOI appears in {len(set(files))} files: {doi}",
                "Files: " + ", ".join(sorted(set(files))),
            ))


# ---------------------------------------------------------------------------
# Orphan detection
# ---------------------------------------------------------------------------

def check_orphans(
    corpus_paths: set[str],
    all_edges: list[tuple[str, str]],
    findings: list[Finding],
) -> None:
    """Detect meta files with no incoming cross-references."""
    # Build incoming reference set
    incoming: set[str] = set()
    for _src, tgt in all_edges:
        incoming.add(tgt)

    meta_files = {p for p in corpus_paths if p.startswith("meta/") and "_TEMPLATE" not in p}
    orphans = meta_files - incoming
    if orphans:
        findings.append(Finding(
            "INFO", "crossref", "(corpus-wide)",
            f"{len(orphans)} meta files have zero incoming cross-references",
            "Files: " + ", ".join(sorted(list(orphans)[:15]))
            + (f" ... and {len(orphans) - 15} more" if len(orphans) > 15 else ""),
        ))


# ---------------------------------------------------------------------------
# Main audit orchestration
# ---------------------------------------------------------------------------

def run_audit(repo_root: Path) -> list[Finding]:
    """Run all audit checks and return findings."""
    findings: list[Finding] = []

    # Collect corpus
    md_files = walk_content(repo_root)
    corpus_paths: set[str] = set()
    file_texts: dict[str, str] = {}

    for md_file in md_files:
        rel_path = str(md_file.relative_to(repo_root))
        corpus_paths.add(rel_path)
        try:
            with open(md_file, "r", encoding="utf-8", errors="replace") as f:
                file_texts[rel_path] = f.read()
        except OSError:
            findings.append(Finding(
                "ERROR", "structural", rel_path,
                "Could not read file",
            ))

    # Also add non-content files that exist (for crossref validation)
    for extra_dir in ["index", "contracts", "scripts", ".claude/workflows"]:
        dir_path = repo_root / extra_dir
        if dir_path.exists():
            for p in dir_path.rglob("*"):
                if p.is_file():
                    corpus_paths.add(str(p.relative_to(repo_root)))

    all_urls: dict[str, list[str]] = {}
    all_dois: dict[str, list[str]] = {}
    all_edges: list[tuple[str, str]] = []

    for rel_path, text in file_texts.items():
        # A. Structural compliance (meta/ only)
        check_structural_compliance(rel_path, text, findings, repo_root)

        # B. Cross-reference validity (all files)
        edges = check_crossrefs(rel_path, text, corpus_paths, repo_root, findings)
        all_edges.extend(edges)

        # C. Origin consistency (meta/ only)
        if rel_path.startswith("meta/"):
            check_origin_consistency(rel_path, text, findings)

        # D. Status-evidence signals (meta/ only)
        check_status_evidence(rel_path, text, repo_root, findings)

        # F. URL/DOI patterns (all files)
        check_urls_and_dois(rel_path, text, all_urls, all_dois, findings)

    # E. Index staleness
    check_index_staleness(corpus_paths, repo_root, findings)

    # Orphan detection
    check_orphans(corpus_paths, all_edges, findings)

    # URL/DOI cross-file duplicates
    report_url_doi_findings(all_urls, all_dois, findings)

    # Sort: ERROR first, then WARNING, then INFO; within severity by file path
    severity_order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    findings.sort(key=lambda f: (severity_order.get(f.severity, 9), f.file_path))

    return findings


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_summary(findings: list[Finding]) -> str:
    """Format findings as a human-readable markdown summary."""
    lines: list[str] = []
    lines.append("# KB Audit Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Counts
    severity_counts = Counter(f.severity for f in findings)
    category_counts = Counter(f.category for f in findings)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total findings:** {len(findings)}")
    lines.append(f"- **ERRORs:** {severity_counts.get('ERROR', 0)}")
    lines.append(f"- **WARNINGs:** {severity_counts.get('WARNING', 0)}")
    lines.append(f"- **INFOs:** {severity_counts.get('INFO', 0)}")
    lines.append("")
    lines.append("**By category:**")
    for cat in sorted(category_counts.keys()):
        lines.append(f"- {cat}: {category_counts[cat]}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group by severity
    for severity in ["ERROR", "WARNING", "INFO"]:
        sev_findings = [f for f in findings if f.severity == severity]
        if not sev_findings:
            continue

        lines.append(f"## {severity} ({len(sev_findings)})")
        lines.append("")

        # Sub-group by category
        by_category: dict[str, list[Finding]] = defaultdict(list)
        for f in sev_findings:
            by_category[f.category].append(f)

        for category in sorted(by_category.keys()):
            cat_findings = by_category[category]
            lines.append(f"### {category} ({len(cat_findings)})")
            lines.append("")
            for f in cat_findings:
                lines.append(f"- **{f.file_path}**: {f.message}")
                if f.detail:
                    lines.append(f"  - {f.detail}")
            lines.append("")

    return "\n".join(lines)


def format_json(findings: list[Finding]) -> str:
    """Format findings as JSON."""
    return json.dumps(
        {
            "generated": datetime.now().isoformat(),
            "total": len(findings),
            "counts": {
                "error": sum(1 for f in findings if f.severity == "ERROR"),
                "warning": sum(1 for f in findings if f.severity == "WARNING"),
                "info": sum(1 for f in findings if f.severity == "INFO"),
            },
            "findings": [f.to_dict() for f in findings],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="KB accuracy audit for the Fermi knowledge base"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output machine-parseable JSON instead of markdown summary",
    )
    parser.add_argument(
        "--severity",
        choices=["ERROR", "WARNING", "INFO"],
        help="Filter to only show findings of this severity or higher",
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save output to audit_results/ directory",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    print(f"Running KB audit on {repo_root}...", file=sys.stderr)

    findings = run_audit(repo_root)

    # Apply severity filter
    if args.severity:
        severity_order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
        threshold = severity_order[args.severity]
        findings = [f for f in findings if severity_order.get(f.severity, 9) <= threshold]

    if args.json:
        output = format_json(findings)
    else:
        output = format_summary(findings)

    print(output)

    if args.save:
        out_dir = repo_root / "audit_results"
        out_dir.mkdir(exist_ok=True)
        # Save both formats
        summary_path = out_dir / "audit_summary.md"
        json_path = out_dir / "audit_report.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(format_summary(findings))
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(format_json(findings))
        print(f"\nSaved to {summary_path.relative_to(repo_root)} and {json_path.relative_to(repo_root)}", file=sys.stderr)

    # Exit with error code if ERRORs found
    error_count = sum(1 for f in findings if f.severity == "ERROR")
    if error_count > 0:
        print(f"\n{error_count} ERROR(s) found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

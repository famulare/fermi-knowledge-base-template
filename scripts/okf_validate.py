#!/usr/bin/env python3
"""okf_validate.py — validate an OKF bundle for OKF v0.1 base conformance + the Epistemic Profile.

See OKF_EPISTEMIC_PROFILE.md §5. Two layers of checking:
  * OKF base (§2.1): every non-reserved .md has parseable YAML frontmatter with a non-empty
    `type`; reserved files (index.md, log.md) are EXEMPT from the type rule.
  * Profile (§2.2-2.5): `origin` (contradictions exempt), `status` in the type's taxonomy,
    `layer` present, and any `rel:<verb>` link titles use a verb known to the registry.

Exit codes: 0 clean · 1 profile violation(s) · 2 OKF base-conformance violation(s).
Honors OKF's tolerance contract: we report, we do not "reject" — but a base violation means the
bundle is not a valid OKF bundle, hence the non-zero code.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_graph  # noqa: E402  (loads index/edge_verbs.md → verb registry)

RESERVED = {"index.md", "log.md"}
TYPE_STATUS = {
    "claim": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived"},
    "model": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived", "Proposed"},
    "map": {"Draft", "Active", "Exploratory", "Reflection", "Superseded", "Archived"},
    "contradiction": {"Open", "Resolved", "Coexisting", "Productive tension"},
    "timeline": {"Draft", "Active", "Superseded", "Archived"},
}
LAYERS = {"raw", "meta", "examples"}
ORIGIN_BASE_RE = re.compile(r"^\s*(\[.+?\]|Fermi\b|Co-created\b|External\b|[A-Z][\w.-]+)")
REL_TITLE_RE = re.compile(r'\]\((?:[^)\s]+?)\s+"rel:([^"]+)"\)')

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


class Findings:
    def __init__(self) -> None:
        self.base: list[str] = []
        self.profile: list[str] = []
        self.warn: list[str] = []

    def err_base(self, f: str, m: str) -> None: self.base.append(f"{f}: {m}")
    def err_profile(self, f: str, m: str) -> None: self.profile.append(f"{f}: {m}")
    def warning(self, f: str, m: str) -> None: self.warn.append(f"{f}: {m}")


def _verb_known(verb: str) -> bool:
    _v, cls, _d = kb_graph.resolve_verb(verb)
    return cls is not None


def validate_bundle(bundle: Path, profile: bool = True) -> Findings:
    fnd = Findings()
    md_files = sorted(bundle.rglob("*.md"))
    if not md_files:
        fnd.err_base(str(bundle), "no markdown files found")
        return fnd

    for p in md_files:
        rel = str(p.relative_to(bundle))
        text = p.read_text(encoding="utf-8", errors="ignore")

        if p.name in RESERVED:
            # reserved files are EXEMPT from the type rule; light structure checks only
            if p.name == "index.md" and text.lstrip().startswith("---"):
                fnd.warning(rel, "index.md should have no frontmatter (OKF §6)")
            continue

        m = FRONTMATTER_RE.match(text)
        if not m:
            fnd.err_base(rel, "missing or unterminated YAML frontmatter block")
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            fnd.err_base(rel, f"unparseable YAML frontmatter: {e}")
            continue
        if not isinstance(fm, dict):
            fnd.err_base(rel, "frontmatter is not a mapping")
            continue
        body = m.group(2)

        # OKF base: non-empty type
        ctype = fm.get("type")
        if not (isinstance(ctype, str) and ctype.strip()):
            fnd.err_base(rel, "missing/empty required field `type`")
            continue

        if not profile:
            continue

        # Profile §3.1 origin (contradictions exempt)
        if ctype != "contradiction":
            origin = fm.get("origin")
            if not (isinstance(origin, str) and origin.strip()):
                fnd.err_profile(rel, "missing required `origin`")
            elif not ORIGIN_BASE_RE.match(origin):
                fnd.warning(rel, f"origin base unrecognized: {origin!r}")

        # Profile §3.2 status
        status = fm.get("status")
        if not (isinstance(status, str) and status.strip()):
            fnd.err_profile(rel, "missing required `status`")
        elif ctype in TYPE_STATUS and status not in TYPE_STATUS[ctype]:
            fnd.warning(rel, f"status {status!r} not in taxonomy for type {ctype!r}")

        # Profile §3.3 layer
        layer = fm.get("layer")
        if not (isinstance(layer, str) and layer.strip()):
            fnd.err_profile(rel, "missing required `layer`")
        elif layer not in LAYERS:
            fnd.warning(rel, f"layer {layer!r} not in {sorted(LAYERS)}")

        # Profile §4 rel:<verb> link titles map to a known verb
        for verb in REL_TITLE_RE.findall(body):
            if not _verb_known(verb):
                fnd.warning(rel, f"rel:{verb} — verb not in registry (edge_verbs.md)")

    return fnd


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate an OKF + Epistemic Profile bundle.")
    ap.add_argument("bundle", type=Path, help="bundle directory to validate")
    ap.add_argument("--base-only", action="store_true", help="check OKF base conformance only")
    args = ap.parse_args()
    if not args.bundle.is_dir():
        ap.error(f"not a directory: {args.bundle}")

    fnd = validate_bundle(args.bundle, profile=not args.base_only)
    for m in fnd.base:
        print(f"BASE   {m}")
    for m in fnd.profile:
        print(f"PROFILE {m}")
    for m in fnd.warn:
        print(f"warn   {m}")
    print(f"\n[okf_validate] base errors: {len(fnd.base)} · "
          f"profile errors: {len(fnd.profile)} · warnings: {len(fnd.warn)}")
    if fnd.base:
        print("[okf_validate] NOT a conformant OKF bundle")
        return 2
    if fnd.profile:
        print("[okf_validate] OKF-conformant; profile violations present")
        return 1
    print("[okf_validate] PASS — OKF + Epistemic Profile conformant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

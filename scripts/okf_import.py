#!/usr/bin/env python3
"""okf_import.py — consume an external OKF bundle into a Fermi KB as *evidence*, safely.

Quarantine model (OKF_EPISTEMIC_PROFILE.md §1, INGEST_OKF.md): an OKF bundle is low-provenance
and possibly agent-generated, so it is NEVER trusted as fact on import. This tool:

  1. Safety-checks the bundle (rejects symlinks, path traversal, oversize/too-many files,
     non-UTF-8) and **fails closed**.
  2. Lands the bundle VERBATIM under `raw/curated/okf/<name>/` (append-only evidence;
     refuses to overwrite an existing import).
  3. Writes a companion source record `_source.md` (`Origin: External (<org>)`, source, ingest date/reason).
  4. Emits a **synthesis proposal** to `views/ephemeral/` listing each concept as a *candidate*
     for human review — suggested meta type/title, `Origin: External/Co-created`, `Status: Draft`,
     linked back to the quarantined raw. It does NOT write meta/ entries: promotion to
     interpretation is a human step (propose-only invariant).

CLI: okf_import.py <bundle_dir> [--into <repo_root>] [--org X] [--source URL] [--reason TXT]
                     [--dry-run] [--force]
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

MAX_FILES = 5000
MAX_FILE_BYTES = 5 * 1024 * 1024
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _safe_relpaths(bundle: Path) -> list[Path]:
    """Return validated .md files under bundle. Fail closed on symlink / traversal / oversize /
    non-UTF-8 / count overflow."""
    root = bundle.resolve()
    files = []
    for p in sorted(bundle.rglob("*")):
        if p.is_dir():
            continue
        if p.is_symlink():
            raise SystemExit(f"refusing: symlink in bundle: {p}")
        rp = p.resolve()
        if not str(rp).startswith(str(root) + "/") and rp != root:
            raise SystemExit(f"refusing: path escapes bundle: {p}")
        if p.suffix.lower() != ".md":
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            raise SystemExit(f"refusing: file too large ({p.stat().st_size} bytes): {p}")
        try:
            p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise SystemExit(f"refusing: non-UTF-8 file: {p}")
        files.append(p)
        if len(files) > MAX_FILES:
            raise SystemExit(f"refusing: more than {MAX_FILES} files")
    if not files:
        raise SystemExit("no .md files found in bundle")
    return files


def _concept_meta(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        return fm if isinstance(fm, dict) else {}
    except yaml.YAMLError:
        return {}


def import_bundle(bundle: Path, repo: Path, org: str, source: str, reason: str,
                  dry_run: bool, force: bool) -> int:
    files = _safe_relpaths(bundle)
    name = re.sub(r"[^A-Za-z0-9._-]", "-", bundle.resolve().name) or "bundle"
    dest = repo / "raw" / "curated" / "okf" / name
    if dest.exists() and not force:
        raise SystemExit(f"refusing: import target exists (use --force to re-import): {dest}")

    concepts = [(p, _concept_meta(p.read_text(encoding="utf-8"))) for p in files
                if p.name not in ("index.md", "log.md")]
    today = date.today().isoformat()

    print(f"[okf_import] bundle={bundle} name={name} files={len(files)} concepts={len(concepts)}")
    if dry_run:
        print(f"[okf_import] DRY RUN — would land under {dest} and propose {len(concepts)} candidates")
        return 0

    # 2. land verbatim (evidence)
    dest.mkdir(parents=True, exist_ok=True)
    for p in files:
        rel = p.relative_to(bundle)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, out)  # copyfile (not copy2): no symlink follow, data only

    # 3. companion source record (inline provenance for a verbatim import — no sidecars)
    (dest / "_source.md").write_text(
        f"# Source record — imported OKF bundle `{name}`\n\n"
        f"**Origin:** External ({org})\n\n"
        f"**Original Source:** {source or '[unknown]'}\n\n"
        f"**Ingest Reason:** {reason or '[not stated]'}\n\n"
        f"**Ingest Date:** {today}\n\n"
        f"**Trust:** quarantined evidence — NOT first-party fact. Treat every concept as a "
        f"hypothesis until reviewed. Promotion to the meta layer is a human step "
        f"(see the synthesis proposal in views/ephemeral/).\n",
        encoding="utf-8")

    # 4. synthesis proposal (propose-only; human promotes)
    prop_dir = repo / "views" / "ephemeral"
    prop_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Synthesis proposal — OKF import `{name}` ({today})",
        "",
        f"Imported bundle landed at `raw/curated/okf/{name}/` (quarantined evidence). Each "
        "concept below is a **candidate** for an attributed meta entry. Review, then create "
        "entries via the normal workflow with `Origin: External (...)` or `Co-created`, "
        "`Status: Draft`, linked back to the raw source. **Nothing here is fact until you "
        "promote it.**",
        "",
        "| candidate type | title | suggested origin | raw source |",
        "|---|---|---|---|",
    ]
    for p, fm in sorted(concepts, key=lambda x: str(x[0])):
        rel = (Path("raw/curated/okf") / name / p.relative_to(bundle)).as_posix()
        ctype = fm.get("type", "?")
        title = str(fm.get("title", p.stem)).replace("|", "\\|")
        orig = fm.get("origin")
        sug = f"External ({org})" if not orig else f"External ({org}) [bundle says: {orig}]"
        lines.append(f"| {ctype} | {title} | {sug} | `{rel}` |")
    lines += ["", "_Status floor for any promoted entry: Draft/Exploratory — never Active "
              "without independent evidence._", ""]
    prop = prop_dir / f"okf-import-{name}.md"
    prop.write_text("\n".join(lines), encoding="utf-8")

    print(f"[okf_import] landed evidence → {dest}")
    print(f"[okf_import] proposal → {prop} ({len(concepts)} candidates, none promoted)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Import an external OKF bundle as quarantined evidence.")
    ap.add_argument("bundle", type=Path)
    ap.add_argument("--into", type=Path, default=None, help="repo root (default: auto-detect)")
    ap.add_argument("--org", default="unknown", help="source organization for Origin: External (...)")
    ap.add_argument("--source", default="", help="source URL/citation")
    ap.add_argument("--reason", default="", help="why this bundle is being ingested")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="allow re-import over an existing target")
    args = ap.parse_args()
    if not args.bundle.is_dir():
        ap.error(f"not a directory: {args.bundle}")

    repo = args.into
    if repo is None:
        p = Path(__file__).resolve().parent
        repo = next((c for c in [p, *p.parents] if (c / "index" / "tags.md").exists()), None)
        if repo is None:
            ap.error("could not auto-detect repo root; pass --into")
    return import_bundle(args.bundle, repo, args.org, args.source, args.reason,
                         args.dry_run, args.force)


if __name__ == "__main__":
    raise SystemExit(main())

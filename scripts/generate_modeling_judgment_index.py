#!/usr/bin/env python3
"""Generate views/persistent/modeling-judgment-index.md from the markdown corpus.

Reads the `modeling-judgment` tag's file list from index/tags.md, then extracts the
**Reduction question (O):** and **Boundary:** fields from each tagged entry, and emits a
co-location index. Markdown is canonical; this index is a derived, regenerable artifact
(like router.md) — never hand-edit it. Entries with no characterized boundary are flagged
as gaps (a worklist for the human gate).

Usage: uv run scripts/generate_modeling_judgment_index.py
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from itertools import groupby
from pathlib import Path

TAG = "modeling-judgment"


def find_repo_root() -> Path:
    p = Path(__file__).resolve().parent
    for c in [p, *p.parents]:
        if (c / "index" / "tags.md").exists():
            return c
    raise SystemExit("repo root (index/tags.md) not found")


def tagged_files(repo: Path) -> list[str]:
    """Return the file list under the `### modeling-judgment` tag in index/tags.md."""
    files: list[str] = []
    in_section = in_files = False
    for ln in (repo / "index" / "tags.md").read_text(encoding="utf-8").splitlines():
        if ln.strip().startswith("### "):
            in_section = ln.strip() == f"### {TAG}"
            in_files = False
            continue
        if in_section and ln.strip().startswith("**Files:**"):
            in_files = True
            continue
        if in_section and in_files:
            m = re.match(r"\s*-\s+(\S+\.md)", ln)
            if m:
                files.append(m.group(1))
            elif ln.strip() and not ln.strip().startswith("-"):
                in_files = False
    return files


def _field(name: str, text: str) -> str:
    m = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else ""


def extract(repo: Path, rel: str) -> dict:
    fp = repo / rel
    text = fp.read_text(encoding="utf-8") if fp.exists() else ""
    boundary = _field("Boundary", text)
    is_gap = (not boundary) or boundary.lower().startswith("[gap")
    parts = rel.split("/")
    kind = parts[1] if len(parts) > 2 and parts[0] == "meta" else "other"
    return {
        "path": rel,
        "kind": kind,
        "o": _field("Reduction question (O)", text),
        "boundary": boundary,
        "gap": is_gap,
        "missing": not fp.exists(),
    }


def main() -> None:
    repo = find_repo_root()
    rows = sorted((extract(repo, f) for f in tagged_files(repo)),
                  key=lambda r: (r["kind"], r["path"]))
    n = len(rows)
    gaps = sum(1 for r in rows if r["gap"])
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")

    out: list[str] = [
        "# Modeling-Judgment Index",
        "",
        f"**Generated:** {now} by `scripts/generate_modeling_judgment_index.py` — do not hand-edit.",
        "**Source of truth:** the `modeling-judgment` tag in `index/tags.md` + the "
        "`**Reduction question (O):**` / `**Boundary:**` fields in each entry.",
        "",
        f"**{n}** tagged entries · **{n - gaps}** with a stated boundary · "
        f"**{gaps}** boundary gaps (worklist).",
        "",
        "> Each row pairs the keep/ignore judgment's question (O) with the regime where it "
        "breaks. Rows marked ⚠ have no characterized boundary yet — candidates for the "
        "human gate to fill.",
        "",
    ]
    for kind, group in groupby(rows, key=lambda r: r["kind"]):
        out += [f"## {kind}", "", "| Entry | Question (O) | Boundary (where it breaks) |",
                "|---|---|---|"]
        for r in group:
            flag = "⚠ " if r["gap"] else ""
            miss = " **[FILE MISSING]**" if r["missing"] else ""
            link = f"[{r['path'].split('/')[-1]}](../../{r['path']})"
            o = r["o"] or "_(missing)_"
            bound = r["boundary"] or "_(gap: not stated)_"
            out.append(f"| {flag}{link}{miss} | {o} | {bound} |")
        out.append("")

    dest = repo / "views" / "persistent" / "modeling-judgment-index.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest.relative_to(repo)}: {n} entries, {n - gaps} with boundary, {gaps} gaps")


if __name__ == "__main__":
    main()

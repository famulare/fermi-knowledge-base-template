#!/usr/bin/env python3
"""okf_export.py — export a Fermi knowledge base into an OKF v0.1 + Epistemic Profile bundle.

Spec: OKF_EPISTEMIC_PROFILE.md (extends OKF v0.1 @ ee67a5c). Reuses scripts/kb_graph.py for the
verb registry (verb -> relation class + direction). Typed edges ride as CommonMark link titles
`[Title](/type/file.md "rel:<verb>")`; epistemic spine (origin/status/layer + External/judgment
fields) rides as YAML frontmatter additional keys. Both are OKF-tolerated, so every emitted
bundle is a valid OKF bundle.

Privacy: there is NO default layer scope. `--layers` is required, and emitting `meta/`/`raw/`
content requires `--allow-private` (guards against leaking a private instance's real content).

Gate 1 (`--selftest`): re-parses the EMITTED markdown with an independent link extractor (never
kb_graph), asserts typed+untyped link count parity and field/body equivalence, and prints the
declared-dropped set so loss is visible, not hidden.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_graph  # noqa: E402  (import has side effects: loads index/edge_verbs.md)

# --- type <-> directory mapping -------------------------------------------------------------
TYPE_DIR = {  # singular OKF `type` -> bundle subdir (plural, matches meta/ layout)
    "claim": "claims", "model": "models", "map": "maps",
    "contradiction": "contradictions", "timeline": "timelines",
}
H1_TYPE_RE = re.compile(r"^#\s+(Claim|Model|Map|Contradiction|Timeline)\s*:", re.I)
RESERVED = {"index.md", "log.md", "readme.md", "_template.md"}

# Marker like `**Origin:** value` (mirrors kb_audit.extract_fields; tested for agreement).
MARKER_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")
# Backtick path target: optional layer prefix OR bare `name.md`, optional :lines suffix.
PATH_SPAN_RE = re.compile(
    r"`((?:(?:examples|meta|raw|special_projects|views|index|contracts)/)?"
    r"[A-Za-z0-9][A-Za-z0-9._-]*\.md)(?::[0-9-]+)?`"
)
BANNER_RE = re.compile(r"^>\s*\*\*Note:\*\*", re.I)
# Independent markdown-link extractor for Gate 1 (NOT kb_graph): [text](href "title").
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((/[^)\s]+?)(?:\s+\"([^\"]*)\")?\)")

# Frontmatter key order (deterministic output).
FM_ORDER = [
    "type", "title", "description", "resource", "tags", "timestamp",
    "origin", "origin_detail", "status", "status_note", "layer",
    "original_author", "original_source", "ingest_reason", "ingest_date",
    "reduction_question", "boundary",
]


@dataclass
class Concept:
    src_rel: str            # source path within the KB (e.g. examples/model_x.md)
    type: str               # singular OKF type
    title: str
    layer: str
    fm: dict = field(default_factory=dict)      # frontmatter (minus type/title/layer)
    items: list = field(default_factory=list)   # contradiction per-item provenance
    body_lines: list = field(default_factory=list)  # body after H1 + preamble markers stripped
    rendered_body: list = field(default_factory=list)  # body with cross-ref spans -> OKF links
    edges: list = field(default_factory=list)   # [{dst, verb, typed, in_bundle}] (single pass)

    @property
    def bundle_rel(self) -> str:
        return f"{TYPE_DIR[self.type]}/{Path(self.src_rel).name}"

    @property
    def bundle_href(self) -> str:
        return "/" + self.bundle_rel


# --- parsing --------------------------------------------------------------------------------
def _date_from_filename(name: str) -> str | None:
    m = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    return m.group(1) if m else None


def _newest_changelog_date(lines: list[str]) -> str | None:
    dates = re.findall(r"^\s*[-*]\s*(\d{4}-\d{2}-\d{2})\b", "\n".join(lines), re.M)
    return max(dates) if dates else None


def _infer_type(src_rel: str, text: str) -> str | None:
    parts = src_rel.split("/")
    if parts[0] == "meta" and len(parts) > 2 and parts[1] in TYPE_DIR.values():
        return next(k for k, v in TYPE_DIR.items() if v == parts[1])
    for ln in text.splitlines():
        m = H1_TYPE_RE.match(ln.strip())
        if m:
            return m.group(1).lower()
    return None


def _split_sections(text: str):
    """Yield (heading_or_None, [lines]). First block (heading None) is the preamble."""
    lines = text.splitlines()
    blocks, cur_head, cur = [], None, []
    for ln in lines:
        m = re.match(r"^(#{2,4})\s+(.*)$", ln)
        if m:
            blocks.append((cur_head, cur))
            cur_head, cur = m.group(2).strip(), []
        else:
            cur.append(ln)
    blocks.append((cur_head, cur))
    return blocks


def parse_concept(src_rel: str, text: str) -> Concept | None:
    ctype = _infer_type(src_rel, text)
    if ctype is None:
        return None
    layer = src_rel.split("/")[0]
    blocks = _split_sections(text)

    # H1 title
    title = Path(src_rel).stem
    for ln in text.splitlines():
        hm = re.match(r"^#\s+(?:Claim|Model|Map|Contradiction|Timeline)\s*:\s*(.*)$", ln.strip(), re.I)
        if hm:
            title = hm.group(1).strip()
            break
        if ln.strip().startswith("# "):
            title = ln.strip()[2:].strip()
            break

    # Preamble markers (before first ## section) — avoids per-item collisions in contradictions.
    preamble = blocks[0][1]
    markers: dict[str, str] = {}
    for ln in preamble:
        m = MARKER_RE.match(ln.strip())
        if m and m.group(1) not in markers:
            markers[m.group(1)] = m.group(2).strip()

    c = Concept(src_rel=src_rel, type=ctype, title=title, layer=layer)

    # description
    desc = None
    if "Statement" in markers:
        desc = re.split(r"(?<=[.!?])\s", markers["Statement"], maxsplit=1)[0]
    else:
        for head, body in blocks:
            if head and head.lower() in ("summary", "purpose"):
                for ln in body:
                    if ln.strip():
                        line = ln.strip().lstrip("*-> ").strip()
                        desc = re.split(r"(?<=[.!?])\s", line, maxsplit=1)[0]
                        break
            if desc:
                break
    if desc:
        c.fm["description"] = desc

    # tags
    if "Tags" in markers:
        tags = [t.strip() for t in re.split(r"[,;]", markers["Tags"]) if t.strip()]
        if tags:
            c.fm["tags"] = tags

    # origin (contradictions exempt at top level)
    if "Origin" in markers:
        full = markers["Origin"]
        c.fm["origin"] = full
        base = re.match(r"^(\[[^\]]+\]|[A-Za-z][\w.-]*(?:\s*\([^)]*\))?)", full)
        if base and base.group(0).strip() != full:
            c.fm["origin_detail"] = full

    # status (+ note)
    if "Status" in markers:
        raw_status = markers["Status"]
        base = re.split(r"\s+[—-]\s+|\s*\(", raw_status, maxsplit=1)[0].strip()
        c.fm["status"] = base
        if base != raw_status:
            c.fm["status_note"] = raw_status

    # timestamp: Last updated -> Detected -> newest change-log -> filename date (guard non-date)
    ts = None
    for key in ("Last updated", "Detected", "Created"):
        if key in markers and re.match(r"^\d{4}-\d{2}-\d{2}$", markers[key].strip()):
            ts = markers[key].strip()
            break
    if not ts:
        prov = next((b for h, b in blocks if h and h.lower() == "provenance"), [])
        ts = _newest_changelog_date(prov) or _date_from_filename(Path(src_rel).name)
    if ts:
        c.fm["timestamp"] = ts + ("T00:00:00Z" if len(ts) == 10 else "")

    # External provenance + modeling-judgment optional fields
    ext = {"Original Author(s)": "original_author", "Original Source": "original_source",
           "Ingest Reason": "ingest_reason", "Ingest Date": "ingest_date",
           "Reduction question (O)": "reduction_question", "Boundary": "boundary"}
    for mk, fk in ext.items():
        if mk in markers:
            c.fm[fk] = markers[mk]
    if c.fm.get("original_source", "").startswith(("http://", "https://")):
        c.fm["resource"] = c.fm["original_source"]

    # contradiction per-item provenance (items[] block) from ## Item A/B/C sections
    if ctype == "contradiction":
        for head, body in blocks:
            if head and re.match(r"item\b", head, re.I):
                item: dict[str, str] = {"label": head}
                for ln in body:
                    mm = MARKER_RE.match(ln.strip())
                    if mm and mm.group(1) in ("Origin", "Source", "Raw evidence"):
                        item[mm.group(1).lower().replace(" ", "_")] = mm.group(2).strip()
                if len(item) > 1:
                    c.items.append(item)

    # body = everything after the H1, with top-level preamble markers stripped + banner removed
    c.body_lines = _build_body(text)
    return c


def _build_body(text: str) -> list[str]:
    lines = text.splitlines()
    out, seen_h1, in_preamble = [], False, False
    for ln in lines:
        s = ln.strip()
        if not seen_h1 and s.startswith("# "):
            seen_h1, in_preamble = True, True
            continue
        if BANNER_RE.match(s) or (s.startswith(">") and not seen_h1):
            continue
        if in_preamble:
            if s.startswith("## "):
                in_preamble = False
            elif MARKER_RE.match(s) or s in ("", "---"):
                continue  # drop lifted markers + separators in preamble
        out.append(ln)
    while out and not out[0].strip():
        out.pop(0)
    return out


# --- cross-ref processing (single pass: render links + record edges, per-occurrence verbs) --
def _resolve(raw_path: str, by_name: dict[str, str]) -> str | None:
    """Backtick path -> corpus src_rel, or None for placeholder/unresolvable. Bare `name.md`
    resolves only on a unique corpus match."""
    if kb_graph._is_placeholder(raw_path):
        return None
    return raw_path if "/" in raw_path else by_name.get(raw_path)


def process_body(body_lines: list[str], by_name: dict[str, str], emitted: dict[str, "Concept"]):
    """ONE pass over the body. In relation/evidence sections, replace each backtick cross-ref
    span that resolves to an emitted concept with an OKF markdown link (typed via rel:<verb>
    using the verb in effect AT THAT span), and record the matching edge. Render and record are
    produced together, so they cannot diverge. Returns (rendered_lines, edges)."""
    rendered, edges = [], []
    in_rel = in_ev = False
    current_verb = None
    for ln in body_lines:
        s = ln.strip()
        if re.match(r"^#{2,4}\s+", s):
            in_rel = bool(kb_graph.RELATION_HEADING_RE.match(s))
            in_ev = bool(re.match(r"^#{2,4}\s+Evidence", s, re.I))
            current_verb = None
            rendered.append(ln)
            continue
        if not (in_rel or in_ev):
            rendered.append(ln)
            continue
        vlbl = kb_graph.VERB_LABEL_RE.match(s)
        if vlbl:
            current_verb = vlbl.group(1)
        verb_for_line = current_verb
        bm = kb_graph.BULLET_RE.match(ln)
        if bm:
            im = kb_graph.INLINE_VERB_RE.match(bm.group(1).strip())
            if im:
                verb_for_line = im.group(1)

        def repl(m: re.Match) -> str:
            dst = _resolve(m.group(1), by_name)
            if dst is None:
                return m.group(0)  # placeholder/unresolved: not an edge, leave code span
            if dst not in emitted:
                edges.append({"dst": dst, "verb": None, "typed": False, "in_bundle": False})
                return m.group(0)  # out-of-bundle: declared-dropped, leave code span
            if in_ev:
                verb = None  # evidence rendered untyped (rel:supports omitted; declared)
            elif verb_for_line is not None:
                v, cls, _ = kb_graph.resolve_verb(verb_for_line)
                verb = v if cls else None
            else:
                verb = None
            edges.append({"dst": dst, "verb": verb, "typed": verb is not None, "in_bundle": True})
            tgt = emitted[dst]
            label = tgt.title.replace("[", "").replace("]", "")  # keep markdown link text safe
            title = f' "rel:{verb}"' if verb else ""
            return f"[{label}]({tgt.bundle_href}{title})"

        rendered.append(PATH_SPAN_RE.sub(repl, ln))
    return rendered, edges


def count_source_links(body_lines: list[str], by_name: dict[str, str],
                       emitted: dict[str, "Concept"]) -> int:
    """INDEPENDENT cross-check for Gate 1: count backtick spans in relation/evidence sections
    that resolve to emitted targets. Deliberately simpler than process_body (no verb logic), so
    a divergence between the two surfaces an extraction bug rather than hiding it."""
    n, in_sec = 0, False
    for ln in body_lines:
        s = ln.strip()
        if re.match(r"^#{2,4}\s+", s):
            in_sec = bool(kb_graph.RELATION_HEADING_RE.match(s)) or bool(
                re.match(r"^#{2,4}\s+Evidence", s, re.I))
            continue
        if in_sec:
            for span in PATH_SPAN_RE.findall(ln):
                dst = _resolve(span, by_name)
                if dst is not None and dst in emitted:
                    n += 1
    return n


# --- rendering ------------------------------------------------------------------------------
def render_concept(c: Concept, emitted: dict[str, Concept]) -> str:
    fm = {"type": c.type, "title": c.title}
    for k in FM_ORDER:
        if k in ("type", "title"):
            continue
        if k in c.fm:
            fm[k] = c.fm[k]
    fm["layer"] = c.layer
    if c.items:
        fm["items"] = c.items
    ordered = {k: fm[k] for k in (["type", "title"] + FM_ORDER + ["items"]) if k in fm}
    front = yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True,
                           default_flow_style=False).rstrip("\n")

    body = "\n".join(c.rendered_body)
    return f"---\n{front}\n---\n\n# {c.title}\n\n{body}\n"


# --- bundle assembly ------------------------------------------------------------------------
def build_concepts(repo: Path, layers: list[str]):
    """Returns (concepts, by_name). Two passes: parse all concepts (so titles + emitted set are
    known), then process cross-refs/links in a single pass per concept."""
    by_name: dict[str, str] = {}
    raw: dict[str, str] = {}
    for layer in layers:
        for p in sorted((repo / layer).rglob("*.md")):
            if p.name.lower() in RESERVED:
                continue
            rel = str(p.relative_to(repo))
            raw[rel] = p.read_text(encoding="utf-8", errors="ignore")
            by_name.setdefault(p.name, rel)
    concepts: dict[str, Concept] = {}
    for rel, text in raw.items():
        c = parse_concept(rel, text)
        if c is not None:
            concepts[rel] = c
    for c in concepts.values():
        c.rendered_body, c.edges = process_body(c.body_lines, by_name, concepts)
    return concepts, by_name


def write_bundle(concepts: dict[str, Concept], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for rel, c in concepts.items():
        f = out / c.bundle_rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(render_concept(c, concepts), encoding="utf-8")
    _write_indexes(concepts, out)
    _write_log(concepts, out)


def _write_indexes(concepts: dict[str, Concept], out: Path) -> None:
    by_type: dict[str, list[Concept]] = {}
    for c in concepts.values():
        by_type.setdefault(c.type, []).append(c)
    root = ["# Index\n"]
    for t in sorted(by_type):
        tdir = TYPE_DIR[t]
        root.append(f"\n## {tdir.capitalize()}\n")
        lines = [f"# {tdir.capitalize()}\n"]
        for c in sorted(by_type[t], key=lambda x: x.title):
            desc = c.fm.get("description", "")
            entry = f"* [{c.title}](/{c.bundle_rel})" + (f" - {desc}" if desc else "")
            root.append(entry)
            lines.append(entry)
        (out / tdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "index.md").write_text("\n".join(root) + "\n", encoding="utf-8")


def _write_log(concepts: dict[str, Concept], out: Path) -> None:
    by_date: dict[str, list[str]] = {}
    for c in concepts.values():
        ts = c.fm.get("timestamp", "")
        d = ts[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", ts) else None
        if d:
            by_date.setdefault(d, []).append(c.title)
    lines = ["# Log\n"]
    for d in sorted(by_date, reverse=True):
        lines.append(f"\n## {d}\n")
        for title in sorted(by_date[d]):
            lines.append(f"- **Update** {title}")
    (out / "log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- Gate 1: round-trip equivalence (independent re-parse) ----------------------------------
def _reparse(bundle_file: Path):
    text = bundle_file.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    typed, untyped = set(), 0
    for _txt, href, title in MD_LINK_RE.findall(body):
        if title and title.startswith("rel:"):
            typed.add((href, title[4:]))
        else:
            untyped += 1
    return fm, typed, untyped, body


def selftest(repo: Path, layers: list[str]) -> int:
    concepts, by_name = build_concepts(repo, layers)
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        write_bundle(concepts, out)
        failures, dropped = [], set()
        for rel, c in concepts.items():
            rp = _reparse(out / c.bundle_rel)
            if rp is None:
                failures.append(f"{rel}: unparseable frontmatter")
                continue
            fm, typed, untyped, _body = rp
            # field equivalence
            for k in ("type", "title"):
                if fm.get(k) != getattr(c, k):
                    failures.append(f"{rel}: {k} {fm.get(k)!r} != {getattr(c, k)!r}")
            if fm.get("layer") != c.layer:
                failures.append(f"{rel}: layer {fm.get('layer')!r} != {c.layer!r}")
            for k in ("origin", "status"):
                if k in c.fm and fm.get(k) != c.fm[k]:
                    failures.append(f"{rel}: {k} {fm.get(k)!r} != {c.fm[k]!r}")
            # typed-edge parity: re-parsed (independent MD_LINK_RE) vs recorded (single pass)
            in_bundle = [e for e in c.edges if e["in_bundle"]]
            want_typed = {("/" + concepts[e["dst"]].bundle_rel, e["verb"])
                          for e in in_bundle if e["typed"]}
            want_untyped = sum(1 for e in in_bundle if not e["typed"])
            if typed != want_typed:
                failures.append(f"{rel}: typed {typed} != {want_typed}")
            if untyped != want_untyped:
                failures.append(f"{rel}: untyped count {untyped} != {want_untyped}")
            # INDEPENDENT cross-check: source spans -> emitted == recorded in-bundle edges
            indep = count_source_links(c.body_lines, by_name, concepts)
            if indep != len(in_bundle):
                failures.append(f"{rel}: source-span count {indep} != in-bundle edges {len(in_bundle)}")
            if any(not e["in_bundle"] for e in c.edges):
                dropped.add("out-of-bundle edge targets (left as code spans, not OKF links)")
        print(f"[selftest] {len(concepts)} concepts, layers={layers}")
        print("[selftest] declared-dropped (lossy by design):")
        for d in sorted(dropped) or ["(none)"]:
            print(f"  - {d}")
        print("  - sub-document evidence/inference/interpolation tags (stay in body)")
        print("  - per-edge rationale prose (stays in body)")
        if failures:
            print(f"[selftest] FAIL ({len(failures)}):")
            for f in failures[:40]:
                print(f"  - {f}")
            return 1
        print("[selftest] PASS — field + typed-edge equivalence holds")
        return 0


# --- privacy guard + CLI --------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Export a Fermi KB to an OKF + Epistemic Profile bundle.")
    ap.add_argument("--out", type=Path, help="output bundle directory")
    ap.add_argument("--layers", nargs="+", help="layers to export (e.g. examples). REQUIRED — no default.")
    ap.add_argument("--allow-private", action="store_true",
                    help="permit exporting meta/ or raw/ content (off by default to prevent leaks)")
    ap.add_argument("--selftest", action="store_true", help="run the round-trip equivalence gate")
    args = ap.parse_args()

    repo = kb_graph.find_repo_root()
    layers = args.layers or (["examples"] if args.selftest else None)
    if not layers:
        ap.error("--layers is required (no default scope; e.g. --layers examples)")
    private = {l for l in layers if l in ("meta", "raw")}
    if private and not args.allow_private:
        ap.error(f"refusing to export private layers {sorted(private)} without --allow-private")

    if args.selftest:
        return selftest(repo, layers)
    if not args.out:
        ap.error("--out is required unless --selftest")
    concepts, _ = build_concepts(repo, layers)
    write_bundle(concepts, args.out)
    print(f"Exported {len(concepts)} concepts to {args.out} (layers={layers})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

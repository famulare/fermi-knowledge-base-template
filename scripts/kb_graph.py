#!/usr/bin/env python3
"""Knowledge-graph tooling for the Fermi KB (see contracts/knowledge_graph_design.md).

Phase 0 (coverage) and Phase 1 (parity) — both READ-ONLY: no markdown is modified and
no DB is written. They answer the contract's go/no-go question: can the heterogeneous
`## Related` / `## Tensions/Coexistence` / `## Connections` prose be parsed into reliable
typed edges, and does it reproduce the hand-maintained `index/link_graph.md`?

Usage:
  uv run scripts/kb_graph.py coverage          # Phase 0: parse-coverage report over meta+raw
  uv run scripts/kb_graph.py coverage --list-unmapped   # also dump unmapped-verb and dangling samples
  uv run scripts/kb_graph.py parity            # Phase 1: entry-derived edges vs link_graph.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# --- Verb registry (contract §3): canonical_verb -> (inverse, class, directed) -------------
# Directionality is a property of the VERB, not the class (review P0-1). 7 classes.
# This may later externalize to index/edge_verbs.md; hardcoded for Phase 0.
EVID, STRUCT, TENS, SYN, SUPER, ASSOC, POT = (
    "evidential", "structural", "tension", "synthesis", "supersession", "associative", "potential",
)

REGISTRY: dict[str, tuple[str, str, bool]] = {
    # evidential
    "supports": ("supported-by", EVID, True),
    "supported-by": ("supports", EVID, True),
    "validates": ("validated-by", EVID, True),
    "validated-by": ("validates", EVID, True),
    "predicts": ("predicted-by", EVID, True),
    "demonstrates": ("demonstrated-by", EVID, True),
    "grounded-in": ("grounds", EVID, True),
    "grounds": ("grounded-in", EVID, True),
    "exemplifies": ("exemplified-by", EVID, True),
    "exemplified-by": ("exemplifies", EVID, True),
    "empirically-grounds": ("empirically-grounded-by", EVID, True),
    "justified-by": ("justifies", EVID, True),
    "justifies": ("justified-by", EVID, True),
    "informs": ("informed-by", EVID, True),
    "explains": ("explained-by", EVID, True),
    "strengthens": ("strengthened-by", EVID, True),
    "diagnoses": ("diagnosed-by", EVID, True),
    "provides-molecular-clock-to": ("derives-molecular-clock-from", EVID, True),
    "supported-by-": ("supports", EVID, True),
    # structural
    "extends": ("extended-by", STRUCT, True),
    "extended-by": ("extends", STRUCT, True),
    "refines": ("refined-by", STRUCT, True),
    "generalizes": ("specializes", STRUCT, True),
    "specializes": ("generalizes", STRUCT, True),
    "instantiates": ("instantiated-by", STRUCT, True),
    "implements": ("implemented-by", STRUCT, True),
    "implemented-by": ("implements", STRUCT, True),
    "frames": ("framed-by", STRUCT, True),
    "operationalizes": ("operationalized-by", STRUCT, True),
    "operationalized-by": ("operationalizes", STRUCT, True),
    "constrains": ("constrained-by", STRUCT, True),
    "theory-for": ("has-theory", STRUCT, True),
    "enriches": ("enriched-by", STRUCT, True),
    "deepens": ("deepened-by", STRUCT, True),
    "directs": ("directed-by", STRUCT, True),
    "compensates-for": ("compensated-by", STRUCT, True),
    "contextualizes": ("contextualized-by", STRUCT, True),
    "reframes": ("reframed-by", STRUCT, True),
    "enables": ("enabled-by", STRUCT, True),
    "evolves": ("evolved-from", STRUCT, True),
    "interface-of": ("interface-of", STRUCT, False),
    "hierarchical-relationship": ("hierarchical-relationship", STRUCT, False),
    # tension (mostly symmetric)
    "contradicts": ("contradicts", TENS, False),
    "in-tension-with": ("in-tension-with", TENS, False),
    "conflicts-with": ("conflicts-with", TENS, False),
    "contrasts-with": ("contrasts-with", TENS, False),
    "coexists-with": ("coexists-with", TENS, False),
    "challenges": ("challenged-by", TENS, True),
    "undermines": ("undermined-by", TENS, True),
    "self-contradicts": ("self-contradicts", TENS, False),
    "primacy-tension": ("primacy-tension", TENS, False),
    "scope-ambiguity": ("scope-ambiguity", TENS, False),
    "reconciled-with": ("reconciled-with", TENS, False),
    "lacks": ("lacked-by", TENS, True),
    "adds-third-position-to": ("third-position-added-by", TENS, True),
    # synthesis
    "synthesizes": ("synthesized-in", SYN, True),
    "synthesized-in": ("synthesizes", SYN, True),
    "consolidates": ("consolidated-in", SYN, True),
    # supersession
    "supersedes": ("superseded-by", SUPER, True),
    "superseded-by": ("supersedes", SUPER, True),
    # associative (mostly symmetric)
    "connects": ("connects", ASSOC, False),
    "related-to": ("related-to", ASSOC, False),
    "relates-to": ("related-to", ASSOC, False),
    "shares-principle": ("shares-principle", ASSOC, False),
    "shared-framework": ("shared-framework", ASSOC, False),
    "shared-architecture": ("shared-architecture", ASSOC, False),
    "structural-analogy": ("structural-analogy", ASSOC, False),
    "intellectual-ancestor": ("intellectual-descendant", ASSOC, True),
    "cross-domain": ("cross-domain", ASSOC, False),
    "unified-by": ("unifies", ASSOC, True),
    "unifies": ("unified-by", ASSOC, True),
    # potential (hypothesis, not assertion)
    "could-synthesize-with": ("could-synthesize-with", POT, False),
    "could-integrate-with": ("could-integrate-with", POT, False),
    "could-mitigate": ("could-be-mitigated-by", POT, True),
    # --- additions surfaced by Phase 0 coverage ---
    "builds-on": ("built-on-by", STRUCT, True),
    "complements": ("complements", STRUCT, False),
    "compatible-with": ("compatible-with", ASSOC, False),
    "echoes": ("echoed-by", EVID, True),
    "echoed-by": ("echoes", EVID, True),
    "addresses": ("addressed-by", STRUCT, True),
    "critiques": ("critiqued-by", TENS, True),
    "mitigates": ("mitigated-by", STRUCT, True),
    "mitigated-by": ("mitigates", STRUCT, True),
    "resolves": ("resolved-by", TENS, True),
    "applies-to": ("applied-by", STRUCT, True),
    "guided-by": ("guides", STRUCT, True),
    "guides": ("guided-by", STRUCT, True),
    "provides-mechanistic-basis": ("has-mechanistic-basis", EVID, True),
    "documented-in": ("documents", ASSOC, True),
    "observed-instance": ("instance-of", EVID, True),
    "methodological-context": ("methodological-context", ASSOC, False),
    "formalizes": ("formalized-by", STRUCT, True),
}

# Normalized field-label / variant -> canonical verb in REGISTRY.
ALIAS: dict[str, str] = {
    "connects-to": "connects",
    "connected-to": "connects",
    "connected-in": "connects",
    "related": "related-to",
    "shared-principle": "shares-principle",
    "could-integrate": "could-integrate-with",
    "could-synthesize": "could-synthesize-with",
    "synthesised-in": "synthesized-in",
    "superseded": "superseded-by",
    "exemplified": "exemplified-by",
    "operationalised-by": "operationalized-by",
    "provides-molecular-clock": "provides-molecular-clock-to",
    # verbose / descriptive relation sub-headers → canonical (surfaced by Phase 0)
    "related-to-other-kb-content": "related-to",
    "related-to-kb-content": "related-to",
    "to-existing-kb-content": "related-to",
    "related-models": "related-to",
    "related-active-models": "related-to",
    "related-maps": "related-to",
    "night-science-extensions": "related-to",
    "connects-to-kb-content": "connects",
    "kb-connections": "connects",
    "direct-connections": "connects",
    "cross-domain-links": "cross-domain",
    "connected-cross-domain": "cross-domain",
    "implements-this-framework": "implements",
    "this-instantiates": "instantiates",
    "core-claims-this-framework-formalizes": "formalizes",
    "evidence-source": "supported-by",
    "supported-by-independent-evidence": "supported-by",
    "potential-implementation": "could-integrate-with",
    "compatible": "compatible-with",
    "tension": "in-tension-with",
}

RELATION_HEADING_RE = re.compile(
    r"^#{2,4}\s+(.*(?:relat|connect|tension|coexist|synthes|supersed|cross-domain).*)$",
    re.I,
)
VERB_LABEL_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z 0-9/&'_-]+?):\*\*")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
INLINE_VERB_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z 0-9/&'_-]+?)\*\*\s+")
PATH_RE = re.compile(r"`((?:examples|meta|raw|special_projects|views|index|contracts)/[^`]+?\.md)(?::[0-9-]+)?`")


def _is_placeholder(p: str) -> bool:
    """Teaching/placeholder target (YYYY-MM-DD slug, <token>, or glob) — not a real edge."""
    return "YYYY" in p or "<" in p or ">" in p or any(c in p for c in "*?[]")


def find_repo_root() -> Path:
    p = Path(__file__).resolve().parent
    for c in [p, *p.parents]:
        if (c / "index" / "tags.md").exists():
            return c
    raise SystemExit("repo root not found")


def normalize_verb(label: str) -> str:
    v = label.strip().lower()
    v = re.sub(r"[\s_/]+", "-", v)
    v = re.sub(r"[^a-z-]", "", v).strip("-")
    return ALIAS.get(v, v)


def resolve_verb(label: str):
    """Return (canonical_verb, class, directed) or (normalized, None, None) if unmapped."""
    v = normalize_verb(label)
    if v in REGISTRY:
        inv, cls, directed = REGISTRY[v]
        return v, cls, directed
    return v, None, None


def iter_relation_sections(text: str):
    """Yield (heading, body_lines) for each relation-ish ## section."""
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        m = RELATION_HEADING_RE.match(lines[i].strip())
        if m:
            heading = m.group(1).strip()
            body = []
            i += 1
            while i < n and not re.match(r"^#{2,4}\s+", lines[i]):
                body.append(lines[i])
                i += 1
            yield heading, body
        else:
            i += 1


def parse_entry(rel_path: str, text: str):
    """Parse one entry. Returns (edges, issues).
    edge: dict(src, dst, verb, cls, directed, section, raw)
    issue: dict(kind, detail)  kind in {prose, unmapped, dangling-target}
    """
    edges, issues = [], []
    for heading, body in iter_relation_sections(text):
        current_verb = None
        # default verb inferred from heading for plain ## Connections / ## Related w/o labels
        for raw in body:
            vlbl = VERB_LABEL_RE.match(raw.strip())
            if vlbl:
                current_verb = vlbl.group(1)
                # a label line may also carry a path inline; fall through to path scan
            bm = BULLET_RE.match(raw)
            if not bm:
                continue
            bullet = bm.group(1).strip()
            verb_label = current_verb
            im = INLINE_VERB_RE.match(bullet)
            if im:
                verb_label = im.group(1)
            rationale = re.sub(r"^\s*\*\*.+?\*\*", "", PATH_RE.sub("", bullet))
            rationale = re.sub(r"\s{2,}", " ", rationale).strip(" -—:`*,()").strip()
            paths = [p for p in PATH_RE.findall(raw) if not _is_placeholder(p)]
            if not paths:
                # bullet with no KB path target → prose / non-node (warning, not an edge)
                if bullet and not bullet.lower().startswith(("n/a", "none", "—", "-")):
                    issues.append({"kind": "prose", "detail": f"{rel_path} [{heading}] {bullet[:70]}"})
                continue
            if verb_label is None:
                # path bullet under an unlabeled relation heading → implicit associative link
                for tgt in paths:
                    edges.append({"src": rel_path, "dst": tgt, "verb": "related-to",
                                  "cls": ASSOC, "directed": False, "section": heading,
                                  "implicit": True, "rationale": rationale})
                continue
            verb, cls, directed = resolve_verb(verb_label)
            for tgt in paths:
                if cls is None:
                    issues.append({"kind": "unmapped", "detail": verb, "src": rel_path, "dst": tgt})
                edges.append({
                    "src": rel_path, "dst": tgt, "verb": verb, "cls": cls,
                    "directed": directed, "section": heading, "rationale": rationale,
                })

    # ## Evidence sections: each cited KB source --supports--> this entry (evidential backbone)
    in_ev = False
    for ln in text.splitlines():
        s = ln.strip()
        if re.match(r"^#{2,4}\s+Evidence", s, re.I):
            in_ev = True
            continue
        if in_ev and re.match(r"^#{2,4}\s+", s):
            in_ev = False
        if in_ev:
            rat = PATH_RE.sub("", ln).strip().lstrip("-—:`* ").strip()
            for tgt in PATH_RE.findall(ln):
                if _is_placeholder(tgt):
                    continue
                edges.append({"src": tgt, "dst": rel_path, "verb": "supports",
                              "cls": EVID, "directed": True, "section": "Evidence",
                              "evidence": True, "rationale": rat})

    return edges, issues


def walk_entries(repo: Path):
    for layer in ("examples", "meta", "raw"):
        for p in sorted((repo / layer).rglob("*.md")):
            if p.name.lower() in ("_template.md", "readme.md"):
                continue
            rel = str(p.relative_to(repo))
            yield rel, p.read_text(encoding="utf-8", errors="ignore")


def cmd_coverage(args):
    repo = find_repo_root()
    corpus = {str(p.relative_to(repo)) for p in repo.rglob("*.md")}
    all_edges, all_issues = [], []
    files_with_relations = 0
    for rel, text in walk_entries(repo):
        if not RELATION_HEADING_RE.search(text):  # cheap skip (search per-line below)
            if not any(RELATION_HEADING_RE.match(ln.strip()) for ln in text.splitlines()):
                continue
        files_with_relations += 1
        edges, issues = parse_entry(rel, text)
        all_edges.extend(edges)
        all_issues.extend(issues)

    # dangling: target path not in corpus (strip anchor already stripped by regex group)
    dangling = [e for e in all_edges if e["dst"] not in corpus]
    mapped = [e for e in all_edges if e["cls"] is not None]
    unmapped = [e for e in all_edges if e["cls"] is None]
    prose = [i for i in all_issues if i["kind"] == "prose"]
    implicit = [e for e in all_edges if e.get("implicit")]

    cls_dist = Counter(e["cls"] for e in mapped)
    verb_dist = Counter(e["verb"] for e in all_edges)
    unmapped_verbs = Counter(e["verb"] for e in unmapped)

    print("=== Phase 0: Parse-Coverage Report (read-only) ===")
    print(f"Files with relation sections : {files_with_relations}")
    print(f"Edge candidates (path-target): {len(all_edges)}")
    print(f"  mapped to a class          : {len(mapped)}")
    print(f"  UNMAPPED verb              : {len(unmapped)} ({len(unmapped_verbs)} distinct verbs)")
    print(f"  DANGLING target (missing)  : {len(dangling)}")
    print(f"Non-node prose bullets       : {len(prose)} (no KB path → not an edge)")
    print(f"Implicit assoc (verbless hdg): {len(implicit)} (path bullet under unlabeled heading)")
    print()
    print("Edges by class:")
    for c, n in cls_dist.most_common():
        print(f"  {c:14s} {n}")
    print()
    print("Top verbs:")
    for v, n in verb_dist.most_common(20):
        flag = "" if v in REGISTRY else "  <-- UNMAPPED"
        print(f"  {v:30s} {n}{flag}")

    if args.list_unmapped:
        print("\n--- Unmapped verbs (extend REGISTRY) ---")
        for v, n in unmapped_verbs.most_common():
            print(f"  {v} ({n})")
        print("\n--- Dangling targets (sample 25) ---")
        for e in dangling[:25]:
            print(f"  {e['src']}  --{e['verb']}-->  {e['dst']}")
        print("\n--- Non-node prose bullets (sample 20) ---")
        for i in prose[:20]:
            print(f"  {i['detail']}")

    total_resolvable = len(mapped) - len(dangling)
    denom = len(all_edges) or 1
    print(f"\nClean edges (mapped & resolvable): {total_resolvable}/{len(all_edges)} "
          f"({100*total_resolvable/denom:.0f}% of path-target candidates)")


# --- Phase 1: parity vs link_graph.md ------------------------------------------------------
LG_PATH_RE = re.compile(r"`([^`]+?\.md)(?::[0-9-]+)?`")
LG_VERB_RE = re.compile(r"<?--+\s*([a-z][a-z0-9-]*)\s*--+>?|<-->|-->")


def parse_link_graph(text: str):
    """Return list of (src, dst, verb) from link_graph.md edge lines."""
    out = []
    for ln in text.splitlines():
        if "-->" not in ln and "<-->" not in ln:
            continue
        paths = LG_PATH_RE.findall(ln)
        if len(paths) < 2:
            continue
        vm = re.search(r"--+\s*([a-z][a-z0-9-]*)\s*--+>", ln)
        verb = vm.group(1) if vm else ("relates-to" if "<-->" in ln else "connects")
        src = paths[0]
        for dst in paths[1:]:
            out.append((src, dst, verb))
    return out


def cmd_parity(args):
    repo = find_repo_root()
    lg = parse_link_graph((repo / "index" / "link_graph.md").read_text(encoding="utf-8"))
    entry_edges = []
    for rel, text in walk_entries(repo):
        edges, _ = parse_entry(rel, text)
        entry_edges.extend(edges)

    def base(p):
        return Path(p).name

    lg_pairs = {(base(s), base(d)) for s, d, _ in lg}
    en_pairs = {(base(e["src"]), base(e["dst"])) for e in entry_edges}
    # treat undirected: also match reversed
    en_pairs_sym = en_pairs | {(b, a) for a, b in en_pairs}

    reproduced = {p for p in lg_pairs if p in en_pairs_sym}
    lg_only = lg_pairs - en_pairs_sym
    en_only_pairs = {p for p in en_pairs
                     if p not in lg_pairs and (p[1], p[0]) not in lg_pairs}

    print("=== Phase 1: Parity vs link_graph.md (read-only) ===")
    print(f"link_graph.md edge pairs (file-level): {len(lg_pairs)}")
    print(f"entry-derived edge pairs (file-level): {len(en_pairs)}")
    print(f"  reproduced from entries            : {len(reproduced)} "
          f"({100*len(reproduced)/(len(lg_pairs) or 1):.0f}% of link_graph)")
    print(f"  link_graph ONLY (migration backlog): {len(lg_only)}")
    print(f"  entry ONLY (new since 2026-03-24)  : {len(en_only_pairs)}")
    if args.list:
        print("\n--- link_graph ONLY — would need folding into entries (sample 40) ---")
        for s, d in sorted(lg_only)[:40]:
            print(f"  {s}  -->  {d}")


def collect_edges(repo: Path):
    edges = []
    for rel, text in walk_entries(repo):
        e, _ = parse_entry(rel, text)
        edges.extend(e)
    seen, uniq = set(), []
    for e in edges:
        k = (e["src"], e["dst"], e["verb"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    return uniq


def cmd_build(args):
    repo = find_repo_root()
    edges = collect_edges(repo)
    nodes = sorted({e["src"] for e in edges} | {e["dst"] for e in edges})
    payload = {
        "generated": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "note": "Derived from markdown relation/evidence sections by kb_graph.py. Rebuildable; do not hand-edit.",
        "nodes": nodes,
        "edges": edges,
    }
    dest = repo / "index" / "graph.json"
    dest.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {dest.relative_to(repo)}: {len(nodes)} nodes, {len(edges)} edges")


def _load_graph(repo: Path):
    f = repo / "index" / "graph.json"
    if not f.exists():
        raise SystemExit("index/graph.json not found — run: uv run scripts/kb_graph.py build")
    return json.loads(f.read_text(encoding="utf-8"))


def cmd_neighbors(args):
    g = _load_graph(find_repo_root())
    q = args.node
    out = [e for e in g["edges"] if q in e["src"]]
    inb = [e for e in g["edges"] if q in e["dst"]]
    print(f"=== neighbors of '{q}' ===")
    print(f"outgoing ({len(out)}):")
    for e in sorted(out, key=lambda e: (e["cls"] or "", e["verb"])):
        print(f"  --{e['verb']}--> {e['dst']}  [{e['cls']}]")
    print(f"incoming ({len(inb)}):")
    for e in sorted(inb, key=lambda e: (e["cls"] or "", e["verb"])):
        print(f"  {e['src']}  --{e['verb']}-->  [{e['cls']}]")


def cmd_evidence_coverage(args):
    g = _load_graph(find_repo_root())
    inbound = defaultdict(int)
    for e in g["edges"]:
        if e["cls"] == "evidential":
            inbound[e["dst"]] += 1
    targets = [n for n in g["nodes"] if n.startswith(("meta/claims/", "meta/models/"))]
    gaps = sorted(n for n in targets if inbound.get(n, 0) == 0)
    print("=== Evidence-link coverage (NOT a confabulation verdict — contract §6) ===")
    print(f"meta claims/models                 : {len(targets)}")
    print(f"  with >=1 inbound evidential edge : {len(targets) - len(gaps)}")
    print(f"  with NONE (coverage-gap worklist): {len(gaps)}")
    if args.list:
        print("\nGaps (many legitimately edge-less — first-party/deductive entries; review, never auto-flag):")
        for n in gaps:
            print(f"  {n}")


def cmd_render_link_graph(args):
    """Regenerate index/link_graph.md as a DERIVED VIEW from entry edges (retires the
    hand-maintained source; the prior narrative version remains in git history)."""
    repo = find_repo_root()
    edges = collect_edges(repo)
    by_class = defaultdict(list)
    for e in edges:
        by_class[e["cls"] or "other"].append(e)
    order = [EVID, STRUCT, TENS, SYN, SUPER, ASSOC, POT]
    titles = {EVID: "Evidential", STRUCT: "Structural", TENS: "Tension", SYN: "Synthesis",
              SUPER: "Supersession", ASSOC: "Associative", POT: "Potential"}
    n_nodes = len({e["src"] for e in edges} | {e["dst"] for e in edges})
    out = [
        "# Link Graph", "",
        f"**Generated:** {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')} by "
        "`scripts/kb_graph.py render-link-graph` — do not hand-edit.",
        "**Source of truth:** the `## Related` / `## Tensions/Coexistence` / `## Connections` / "
        "`## Evidence` sections of the entries. This is a derived view; it replaced the prior "
        "hand-maintained link graph (see git history before 2026-06-12 for the narrative version, "
        "which also held cross-domain-pattern and managed-tension synthesis prose not captured here).",
        f"**Edges:** {len(edges)} across {n_nodes} nodes.", "", "---", "",
    ]
    for c in order:
        es = sorted(by_class.get(c, []), key=lambda e: (e["src"], e["dst"]))
        if not es:
            continue
        out.append(f"## {titles[c]} ({len(es)})")
        out.append("")
        for e in es:
            rat = f" — {e['rationale']}" if e.get("rationale") else ""
            out.append(f"- `{e['src']}` --{e['verb']}--> `{e['dst']}`{rat}")
        out.append("")
    (repo / "index" / "link_graph.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote index/link_graph.md (derived view): {len(edges)} edges, {n_nodes} nodes")


def _apply_registry_file() -> None:
    """Overlay the verb registry/aliases from index/edge_verbs.md if present (canonical,
    editable). The hardcoded dicts above remain as a built-in fallback."""
    try:
        f = find_repo_root() / "index" / "edge_verbs.md"
        if not f.exists():
            return
        section = None
        valid = {EVID, STRUCT, TENS, SYN, SUPER, ASSOC, POT}
        for ln in f.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if s.lower().startswith("## "):
                section = "alias" if "alias" in s.lower() else "registry"
                continue
            if not s.startswith("|"):
                continue
            cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
            if len(cells) < 2 or cells[0] in ("canonical_verb", "verb", "alias", ""):
                continue
            if set("".join(cells)) <= set("-: "):
                continue
            if section == "registry" and len(cells) >= 4 and cells[2] in valid:
                REGISTRY[cells[0]] = (cells[1], cells[2], cells[3].lower().startswith(("y", "t")))
            elif section == "alias":
                ALIAS[cells[0]] = cells[1]
    except Exception:
        pass


def cmd_dump_verbs(args):
    """Generate index/edge_verbs.md from the current registry (bootstrap/refresh canonical file)."""
    repo = find_repo_root()
    lines = ["# Edge Verb Registry", "",
             "Canonical verb vocabulary for the knowledge graph (`scripts/kb_graph.py`). Editable; "
             "`kb_graph` overlays this onto its built-in defaults. See "
             "`contracts/knowledge_graph_design.md` §3. 7 classes: evidential, structural, tension, "
             "synthesis, supersession, associative, potential.", "",
             "## Registry", "", "| canonical_verb | inverse | class | directed |", "|---|---|---|---|"]
    for v in sorted(REGISTRY):
        inv, cls, d = REGISTRY[v]
        lines.append(f"| {v} | {inv} | {cls} | {'yes' if d else 'no'} |")
    lines += ["", "## Aliases", "", "| alias | canonical |", "|---|---|"]
    for a in sorted(ALIAS):
        lines.append(f"| {a} | {ALIAS[a]} |")
    (repo / "index" / "edge_verbs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote index/edge_verbs.md: {len(REGISTRY)} verbs, {len(ALIAS)} aliases")


def _graph_nodes_edges(repo):
    g = _load_graph(repo)
    return g["edges"], g["nodes"]


def cmd_path(args):
    from collections import deque
    repo = find_repo_root()
    edges, nodes = _graph_nodes_edges(repo)
    am = [n for n in nodes if args.a in n]
    bm = [n for n in nodes if args.b in n]
    if not am or not bm:
        print(f"no node match for endpoint {'a' if not am else 'b'}")
        return
    a, b = am[0], bm[0]
    adj = defaultdict(list)
    for e in edges:
        adj[e["src"]].append((e["dst"], e["verb"]))
        adj[e["dst"]].append((e["src"], e["verb"]))
    prev = {a: None}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == b:
            break
        for v, verb in adj[u]:
            if v not in prev:
                prev[v] = (u, verb)
                q.append(v)
    if b not in prev:
        print(f"no path: {Path(a).name} … {Path(b).name}")
        return
    chain = []
    cur = b
    while prev[cur] is not None:
        u, verb = prev[cur]
        chain.append((verb, cur))
        cur = u
    chain.reverse()
    print(f"{Path(a).name}")
    for verb, v in chain:
        print(f"  --{verb}--> {Path(v).name}")


def cmd_subgraph(args):
    repo = find_repo_root()
    edges, _ = _graph_nodes_edges(repo)
    es = edges
    if args.cls:
        es = [e for e in es if e["cls"] == args.cls]
    if args.node:
        es = [e for e in es if args.node in e["src"] or args.node in e["dst"]]
    label = ", ".join(filter(None, [f"class={args.cls}" if args.cls else "",
                                     f"node~{args.node}" if args.node else ""])) or "all"
    print(f"=== subgraph ({label}): {len(es)} edges ===")
    for e in sorted(es, key=lambda e: (e["cls"] or "", e["src"], e["dst"])):
        print(f"  [{e['cls']}] {Path(e['src']).name} --{e['verb']}--> {Path(e['dst']).name}")


_apply_registry_file()


def main():
    ap = argparse.ArgumentParser(description="KB knowledge-graph tooling (Phase 0/1, read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("coverage", help="Phase 0: parse-coverage report")
    c.add_argument("--list-unmapped", action="store_true", help="dump unmapped verbs + dangling + prose samples")
    c.set_defaults(func=cmd_coverage)
    p = sub.add_parser("parity", help="Phase 1: compare entry-derived edges to link_graph.md")
    p.add_argument("--list", action="store_true", help="list link_graph-only edges")
    p.set_defaults(func=cmd_parity)
    b = sub.add_parser("build", help="Build index/graph.json from markdown (derived, rebuildable)")
    b.set_defaults(func=cmd_build)
    nb = sub.add_parser("neighbors", help="Show typed in/out neighbors of a node")
    nb.add_argument("node", help="file path or basename substring")
    nb.set_defaults(func=cmd_neighbors)
    ec = sub.add_parser("evidence-coverage", help="meta claims/models with no inbound evidential edge")
    ec.add_argument("--list", action="store_true", help="list the coverage-gap entries")
    ec.set_defaults(func=cmd_evidence_coverage)
    rl = sub.add_parser("render-link-graph", help="regenerate index/link_graph.md as a derived view")
    rl.set_defaults(func=cmd_render_link_graph)
    dv = sub.add_parser("dump-verbs", help="(re)generate index/edge_verbs.md from the registry")
    dv.set_defaults(func=cmd_dump_verbs)
    pa = sub.add_parser("path", help="shortest path between two nodes (undirected)")
    pa.add_argument("a", help="endpoint A (path or basename substring)")
    pa.add_argument("b", help="endpoint B")
    pa.set_defaults(func=cmd_path)
    sg = sub.add_parser("subgraph", help="dump edges filtered by --class and/or --node (e.g. supersession/synthesis lineage)")
    sg.add_argument("--class", dest="cls", choices=["evidential", "structural", "tension", "synthesis", "supersession", "associative", "potential"])
    sg.add_argument("--node", help="restrict to edges touching this node (substring)")
    sg.set_defaults(func=cmd_subgraph)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

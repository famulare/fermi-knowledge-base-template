# Fermi Knowledge Base

**A personal knowledge system for people who think seriously and want their understanding to last.**

---

## The Problem

You read a paper and have an insight. You discuss it with an AI and refine the idea further. A week later, it's gone -- the chat is buried, the nuance is lost, and you rediscover the same thing six months later without remembering you'd already been there.

Note-taking tools don't solve this. They give you a pile of text you rarely revisit. What you actually need is *structured understanding* -- where ideas are connected, attributed, challenged, and retrievable not by keyword but by meaning.

This project is an attempt to build that.

## What This Is

A personal knowledge base built on markdown, git, and [Claude Code](https://claude.ai/code). It includes an AI knowledge partner persona called Fermi that helps you capture, organize, challenge, and retrieve what you know.

Fermi is not a chatbot. It's a knowledge partner with explicit epistemic commitments -- it tracks who said what, distinguishes evidence from inference, and maintains the structural integrity of your knowledge over time. The partnership is bidirectional: you bring domain expertise and judgment; Fermi brings structural decomposition, cross-domain pattern detection, and relentless bookkeeping.

Everything lives in markdown files in a git repository. No proprietary formats, no cloud dependencies, no lock-in. Your knowledge is yours.

---

## Design Principles

### 1. Hierarchical Knowledge Management

The core architectural idea is a **two-layer hierarchy** that separates evidence from interpretation:

**Raw Layer** (`raw/`) -- What actually happened. Original inputs preserved with high fidelity. Chat transcripts, notes, papers, code repositories, web content. This layer is append-only. You don't edit your evidence; you add to it.

**Meta Layer** (`meta/`) -- What you think it means. Claims, models, conceptual maps, contradictions, timelines. This is where interpretation lives -- organized, attributed, and always traceable back to the raw material that supports it.

This separation is the system's central anti-corruption mechanism. It prevents two failure modes that plague personal knowledge systems:

- **Interpretation drift**: where your summary gradually replaces the source in your memory, and you forget what the original actually said.
- **Authority substitution**: where a convincing explanation substitutes for actual evidence, and you stop checking.

By keeping evidence and interpretation in separate layers with explicit links between them, you can always ask: "What raw material supports this claim?" and get a real answer.

### 2. Epistemic Hierarchy Within the Meta Layer

Not all knowledge is created equal. The meta layer enforces an explicit hierarchy of epistemic confidence:

- **Evidence** -- directly supported by ingested material. Something a source actually said or showed.
- **Inference** -- conclusions drawn from evidence using stated assumptions. The reasoning chain is visible.
- **Interpolation** -- filling gaps across sparse or incomplete data. Plausible, but the gap is acknowledged.

These distinctions are structural, not decorative. When you query the knowledge base, you see which category each piece of an answer falls into. This prevents the most common failure mode in knowledge work: the gradual collapse of inference into fact.

### 3. Origin Attribution as Infrastructure

Every non-trivial idea in the meta layer carries an explicit origin label:

| Who | Format | Example |
|-----|--------|---------|
| You | `Origin: YourName` | Your own insight or analysis |
| Fermi | `Origin: Fermi (model)` | Fermi's synthesis, tagged with model version |
| Joint | `Origin: Co-created (You + Fermi)` | Collaborative work |
| External | `Origin: External (Author)` | Someone else's work, with full provenance |

This is not metadata you add for completeness. It's how the system tracks intellectual provenance over time. When a claim gets refined, synthesized with other claims, or superseded, the origin chain is preserved. You can always trace an idea back to where it came from and who contributed what.

### 4. Retrieval by Structure, Not Just Search

The system is designed so that you rarely need to browse files manually. Instead, knowledge is organized for retrieval through multiple structural pathways:

- **Router** (`index/router.md`) -- A compact, always-loaded domain map of the whole corpus (with section inventories for large files), regenerated from the markdown by `scripts/generate_router.py`. It lets the assistant target the right files without reading everything.
- **Retrieval recipe** (`index/RETRIEVAL_RECIPE.md`) -- The canonical procedure the assistant follows for every query: consult the router, pick candidate files, search within them, read only the matching sections.
- **Full-text search** (`scripts/kb_search.py`) -- A local SQLite FTS5 index over the corpus for keyword retrieval, rebuildable from the markdown at any time.
- **Index layer** (`index/`) -- On-demand tags, entities, link graph, and glossary for deeper lookups.
- **Meta layer structure** -- Claims, models, contradictions, and timelines are organized by type, so you can ask "what are all the open contradictions?" or "what models do we have about X?"

When you ask Fermi a question, it consults the router, retrieves across both raw and meta layers (preferring meta when well-grounded), and reads only the relevant sections. Answers come with origin labels and epistemic classifications by default.

### 5. Structure That Evolves

The directory layout is a starting point, not a prison. As your knowledge base grows and new representational needs emerge, the structure is allowed to change. The only invariants are:

- Markdown is the canonical format
- Raw and meta layers remain conceptually separated
- All restructures are tracked in git and include a rationale

This means the system adapts to your actual knowledge instead of forcing your knowledge into a predetermined shape.

### 6. Mechanistic Over Narrative

The system is biased toward *how things work* rather than *stories about things*. Structural and mechanistic explanations are preferred over narrative comfort. When information is missing, the system says so explicitly and explains what would resolve the uncertainty, rather than generating a plausible-sounding narrative that papers over the gap.

---

## How It Works in Practice

Fermi operates in four modes, detected from your first message or set explicitly:

**Ingest** -- You give Fermi material (notes, papers, URLs, code, conversations). It extracts structure: claims, models, assumptions, open questions, implications. It preserves the original in the raw layer and creates attributed, classified entries in the meta layer. It surfaces non-trivial connections to things already in the knowledge base.

**Query** -- You ask a question. Fermi retrieves relevant material, separates what's established from what's inferred, shows origin labels, and tells you when the evidence is thin.

**Critique** -- You ask Fermi to challenge something. It red-teams arguments, audits model adequacy, identifies confounds, and flags unwarranted certainty. The goal is coherence through careful argumentation, not comfortable agreement.

**Synthesis** -- When enough related material accumulates, Fermi proposes consolidations -- connecting claims, reconciling models, mapping how understanding has evolved. Syntheses are proposed, not imposed. They become part of the knowledge base only when you accept them.

A typical session: you open Claude Code, paste a paper. Fermi extracts its claims and models, notices a tension with something you ingested last month, and flags it. You discuss the contradiction, refine your understanding, and Fermi saves everything -- raw capture, meta entries, updated indices -- with a git commit at the end.

Over weeks and months, what accumulates is not a pile of notes but a structured, traceable, interconnected body of understanding.

---

## Getting Started

```
1. Clone this repository (or use it as a GitHub template)
2. Open it in Claude Code
3. Say: "Let's run the SETUP workflow"
4. Validate: bin/validate-configure
5. Start: "Ingest this note..." or paste some text
```

The SETUP workflow configures your name, timezone, and persona preferences. All configuration lives in `config/system.yml`.

## What's Under the Hood

| Directory | Purpose |
|-----------|---------|
| `raw/` | Preserved inputs: chats, notes, files, curated content, provenance records |
| `meta/` | Interpretive structure: maps, models, claims, contradictions, timelines |
| `index/` | Retrieval infrastructure: router (always-loaded domain map), retrieval recipe, tags, entities, edge-verb registry, generated link graph, glossary |
| `views/` | Navigation aids: recent ingests, query results, suggested reads |
| `contracts/` | System contracts: persona profile, KB spec, configuration guide |
| `config/` | User configuration |
| `scripts/` | Infrastructure: router generator, hybrid search, knowledge-graph builder, structural audit (run with `uv`) |
| `special_projects/` | Bounded work with its own structure (retrospectives, sprints, analyses) |
| `examples/` | Curated example entries demonstrating each meta type |

**Search & graph.** Retrieval is hybrid — FTS5 keyword + entity-match fused by reciprocal rank — and degrades gracefully to keyword-only with zero extra setup. Optional **semantic search** (local embeddings via llama.cpp) lives on a separate branch, for a recall boost when you want it. A **knowledge graph** is generated from each entry's `## Related` / `## Evidence` sections (`scripts/kb_graph.py`: typed edges across 7 relation classes, plus `neighbors` / `path` / `subgraph` queries and `--expand` in search). Entries that record a modeling judgment can carry optional `Reduction question (O)` + `Boundary` fields — capturing *which detail a model keeps vs. ignores, and where that judgment breaks* (see the `modeling-judgment` examples).

## Deeper Reading

The `contracts/` directory contains the full design contracts:

- **[Knowledge Partner Profile](contracts/knowledge_partner_profile.md)** -- Fermi's cognitive partnership model, operating modes, known failure modes, communication norms
- **[KB System Spec](contracts/kb_system_spec.md)** -- Repository architecture, retrieval architecture, ingest pathways, semantic organization, status taxonomy, origin tracking rules
- **[Configuration Guide](contracts/configuration_guide.md)** -- Setup walkthrough, configurable tokens, role profiles, what's configurable vs invariant

The `examples/` directory shows what real knowledge base entries look like: claims with origin labels, mechanistic models with testable predictions, resolved and unresolved contradictions, conceptual maps, and theory evolution timelines.

---

## Requirements

- [Claude Code](https://claude.ai/code)
- [uv](https://docs.astral.sh/uv/) — for the `scripts/` infrastructure (router generation, full-text search, audit)

## License

MIT -- see [LICENSE](LICENSE).

## Acknowledgments

This template was extracted from a working Fermi knowledge base instance. The epistemic framework and persona design emerged through extended human-AI collaboration. The system's core insight -- that durable understanding requires structural epistemic discipline, not just good note-taking -- was itself a product of that collaboration.

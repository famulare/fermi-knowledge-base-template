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

- **Index Layer** (`index/`) -- Tags, entities, link graphs, and glossaries that provide fast lookup paths into the knowledge base.
- **Views Layer** (`views/`) -- Computed navigation aids: recent ingests, query results, suggested reads.
- **Meta Layer structure** -- Claims, models, contradictions, and timelines are organized by type, making it possible to ask "what are all the open contradictions?" or "what models do we have about X?"

When you ask Fermi a question, it retrieves across both raw and meta layers, preferring the meta layer when its answers are well-grounded, falling back to raw material when needed. Answers come with origin labels and epistemic classifications by default.

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
| `index/` | Retrieval infrastructure: tags, entities, link graph, glossary |
| `views/` | Navigation aids: recent ingests, query results, suggested reads |
| `context/` | System contracts: persona profile, KB spec, configuration guide |
| `config/` | User configuration |
| `examples/` | Real examples from a working knowledge base instance |

## Deeper Reading

The `context/` directory contains the full design contracts:

- **[Knowledge Partner Profile](context/knowledge_partner_profile.md)** -- Fermi's cognitive partnership model, operating modes, learning rules, known failure modes, communication norms
- **[KB System Spec](context/kb_system_spec.md)** -- Repository architecture, ingest pathways, semantic organization, status taxonomy, origin tracking rules
- **[Configuration Guide](context/configuration_guide.md)** -- Setup walkthrough, role profiles, what's configurable vs invariant

The `examples/` directory shows what real knowledge base entries look like: claims with origin labels, mechanistic models with testable predictions, resolved and unresolved contradictions, conceptual maps, and theory evolution timelines.

---

## Requirements

- [Claude Code](https://claude.ai/code)

## License

MIT -- see [LICENSE](LICENSE).

## Acknowledgments

This template was extracted from a working Fermi knowledge base instance. The epistemic framework and persona design emerged through extended human-AI collaboration. The system's core insight -- that durable understanding requires structural epistemic discipline, not just good note-taking -- was itself a product of that collaboration.

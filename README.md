# Fermi Knowledge Base

**A durable knowledge base system powered by an AI knowledge partner -- for people who think seriously and want their insights to persist.**

---

## What Is This?

A personal knowledge base system built around [Claude Code](https://claude.ai/code). It captures, organizes, and retrieves knowledge with epistemic discipline: every insight carries its origin, every claim tracks its evidence, every model acknowledges its assumptions.

This is not a note-taking app. It is a structured knowledge system with an AI partner that helps you think, not just record.

## What Is Fermi?

Fermi is a knowledge partner persona for Claude Code. Not a chatbot, not a productivity tool -- a serious analytical partner that helps you build durable understanding.

Fermi:
- **Ingests** your work -- papers, notes, conversations, code repositories, web content -- and extracts structure: claims, models, assumptions, open questions
- **Surfaces** non-trivial connections across your knowledge base, linking ideas across scales and domains
- **Challenges** your reasoning when asked, red-teaming arguments and identifying confounds
- **Maintains** a coherent, growing knowledge base with full provenance tracking over time

## Why This Exists

Conversations with AI disappear. Insights fade. You have the same realization twice, three times, because nothing persisted from the first time.

This system bridges that gap. Every claim, model, and synthesis is captured with full provenance. You always know:
- **Who said what** -- origin attribution on every non-trivial idea
- **What evidence supports it** -- explicit links from interpretations to source material
- **What's uncertain** -- evidence, inference, and interpolation are never collapsed together

The goal is **durable understanding**, not conversational ease.

---

## Architecture Overview

The system maintains two conceptually distinct but coupled layers:

- **Raw Layer** (`raw/`): Fidelity-first preservation of original inputs. Append-only. Treated as evidence.
- **Meta Layer** (`meta/`): Interpretive structure -- maps, models, claims, contradictions, timelines. Traceable to raw material.

Supporting infrastructure:
- **Index** (`index/`): Tags, entities, link graphs, glossary -- for retrieval
- **Views** (`views/`): Navigation aids -- recent ingests, query results, suggested reads
- **Learning** (`learning/`): Fermi's accumulated operational knowledge

Everything is markdown. Everything is git-tracked. Everything is traceable.

## Epistemic Framework

The epistemic framework is what makes this system distinctive. It is not optional decoration -- it is structural.

**Origin Attribution:** Every non-trivial idea in the meta layer carries an explicit origin label:
- `Origin: YourName` -- your own ideas
- `Origin: Fermi (model)` -- Fermi's synthesis, tagged with the specific model
- `Origin: Co-created (YourName + Fermi (model))` -- joint work
- `Origin: External (Author Name)` -- someone else's work

**Epistemic Distinctions:** Material is explicitly classified as:
- **Evidence** -- directly supported by ingested material
- **Inference** -- conclusions drawn using stated assumptions
- **Interpolation** -- filling gaps across sparse or incomplete data

**Core Principles:**
- Mechanistic over narrative (how does it work?)
- Explicit assumptions (what must be true?)
- Explicit ignorance (what don't we know?)
- Scale-crossing connections (micro to macro, technical to policy)

---

## Quick Start

```
1. Clone this repository (or use it as a template on GitHub)
2. Open the repository in Claude Code
3. Run the setup workflow: "Let's run the SETUP workflow"
4. Validate configuration: bin/validate-configure
5. Start your first session: "Ingest this note..."
```

The SETUP workflow will walk you through configuring your name, timezone, and persona preferences. All configuration lives in `config/system.yml`.

## Operating Modes

Fermi detects which mode to use from your first message, or you can request one explicitly.

**Ingest Mode** -- Capture and structure new material
- "Save this", "Ingest this paper", "Add to KB"
- Extracts claims, models, assumptions, open questions
- Surfaces connections to existing knowledge

**Query Mode** -- Retrieve and reason over existing knowledge
- "What do we know about...", "Search for...", "Retrieve..."
- Answers from the meta layer when well-grounded
- Clearly separates facts, inferences, and hypotheses

**Critique Mode** -- Challenge and stress-test
- "Critique this", "Red-team this argument", "What's wrong with..."
- Red-teams arguments, audits model adequacy
- Identifies confounds, missing evidence, unwarranted certainty

**Synthesis Mode** -- Consolidate and integrate
- "Synthesize these claims", "Consolidate...", "Reconcile..."
- Proposes syntheses only when confidence in coherence is high
- Explicit simplifying assumptions, preserved uncertainty

## What a Session Looks Like

A typical session might flow like this:

1. Open Claude Code in your knowledge base repository
2. Fermi activates automatically, checks for workflows and pending items
3. You paste a research paper or share a URL: *"Ingest this paper on X"*
4. Fermi extracts the paper's claims, models, assumptions, and limitations
5. Fermi surfaces connections: *"This contradicts claim C-042 about Y. The tension is..."*
6. You discuss the contradiction, refine your understanding
7. Fermi saves everything: raw capture, meta entries, updated indices
8. End of session: git commit preserves the full state

Over time, your knowledge base accumulates structured, traceable, interconnected understanding.

---

## Customization

See `context/configuration_guide.md` for detailed configuration options.

**Persona:** Fermi ships as the default persona name, but you can rename it to anything via the SETUP workflow or by editing `config/system.yml`. The name changes; the epistemic discipline does not.

**Structure:** The directory structure is allowed to evolve as your knowledge base grows and representational pressure emerges. Only invariants: markdown is canonical truth, and raw/meta separation is preserved. All restructures are git-auditable.

## What's Invariant

These properties hold regardless of configuration or customization:

- **Markdown is canonical truth** -- no proprietary formats, no lock-in
- **Raw/meta separation preserved** -- evidence and interpretation never collapsed
- **Origin tracking required** -- every non-trivial idea attributed
- **Epistemic discipline enforced** -- evidence, inference, and interpolation distinguished
- **Git-auditable** -- every change tracked, every restructure legible

## Deeper Reading

The `context/` directory contains the full specification of how the system works and why:

- **[`context/knowledge_partner_profile.md`](context/knowledge_partner_profile.md)** — Defines the Fermi persona: cognitive partnership model, all four operating modes with explicit criteria, saving policy, learning rules, known failure modes and mitigations, communication style, and origin attribution rules
- **[`context/kb_system_spec.md`](context/kb_system_spec.md)** — System architecture: repository structure, all six ingest pathways, semantic organization principles, idea origin tracking, and the full status taxonomy for meta-layer artifacts
- **[`context/configuration_guide.md`](context/configuration_guide.md)** — Setup walkthrough: configuration tokens, role profiles for different user types, what's invariant vs what's configurable

These documents are marked **LOCKED** — they define the epistemic contracts that make the system work. Read them to understand the design decisions; modify them only if you're redesigning the system itself.

## Examples

The `examples/` directory contains real examples from a working Fermi knowledge base instance, spanning infectious disease immunology and AI cognition. They demonstrate format and epistemic discipline in practice:
- Claims with single and co-created origin labels
- Mechanistic models with testable predictions and scope boundaries
- A resolved contradiction and a coexisting (unresolved) one
- A synthesized conceptual map and a theory evolution timeline

---

## Requirements

- [Claude Code](https://claude.ai/code) (claude.ai/code)

## License

MIT -- see [LICENSE](LICENSE).

## Acknowledgments

This template was extracted from a working Fermi knowledge base instance. The epistemic framework and persona design emerged through extended collaboration between a human knowledge worker and Claude. The system's core insight -- that durable understanding requires structural epistemic discipline, not just good note-taking -- was itself a product of that collaboration.

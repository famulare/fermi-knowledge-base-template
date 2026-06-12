# Fermi Workflows

This directory contains comprehensive workflow documentation for all Fermi KB operations.

---

## Core Workflows (Phases 1-3)

### Ingest Workflows

- **INGEST_CHAT.md** - Save conversation checkpoints
  - Trigger: "save this conversation" or "ingest"
  - Creates: `raw/chats/` + meta entries + index updates

- **INGEST_MARKDOWN.md** - Ingest pasted or written notes
  - Trigger: Pasted formatted text or "ingest this"
  - Creates: `raw/notes/` + meta entries + index updates

- **INGEST_FILE.md** - Import files (PDFs, images, datasets, documents)
  - Trigger: User references file or "ingest this file"
  - Supports: PDFs, images, CSV/JSON, text documents
  - Creates: `raw/files/` + `raw/provenance/` + meta summaries

- **INGEST_REPO.md** - Ingest GitHub repositories
  - Trigger: User provides GitHub URL or "ingest this repository"
  - Captures: Intellectual content (goals, architecture, tradeoffs)
  - Scope: Selective examination with explicit transparency
  - Creates: `raw/repos/` + meta models + origin attribution

- **INGEST_WEB.md** - Ingest web content (papers, blogs, reports, docs)
  - Trigger: User provides web URL or "ingest this" with URL
  - Supports: Scientific papers, blog posts, technical reports, documentation
  - Content-type detection with specialized extraction
  - Authorship handling ([UserName]-authored vs external)
  - Creates: `raw/web/{type}/` + meta entries + origin attribution

- **INGEST_CURATED.md** - Ingest curated external content
  - Trigger: [UserName] shares external content he finds interesting
  - Requires: Explicit "why" reason for ingestion
  - Creates: `raw/curated/{type}/` + meta entries + External origin attribution

### Query Workflow

- **QUERY.md** - Retrieve and answer from KB
  - Trigger: Questions, "what do we know", "retrieve", "search"
  - Process: Index → meta → raw retrieval strategy
  - Response: Origin labels, citations, evidence/inference distinction

---

## Advanced Workflows (Phases 4-5)

### Epistemic Discipline Workflows

- **CONTRADICTIONS.md** - Detect and document tensions
  - Detection: During ingest and query
  - Process: Identify, confirm, document, track resolution
  - Creates: `meta/contradictions/` entries

- **TIMELINES.md** - Track belief evolution
  - Trigger: Multiple dated entries on same topic or supersession
  - Creates: `meta/timelines/` showing how understanding evolved
  - Updates: After supersession or contradiction resolution

- **CONNECTIONS.md** - Surface non-trivial connections
  - Detection: During ingest, query, or manual scan
  - Filter: Cross-domain, scale-crossing, contradictions, structural similarity
  - Learning: Feedback-based improvement via suppression memory

### Collaborative Workflows

- **SYNTHESIS.md** - Consolidate coexisting models
  - Trigger: User requests or Fermi proposes (high confidence only)
  - Process: Draft → review → approve/revise/reject
  - Creates: Unified model with origin: Co-created (default)

- **CRITIQUE.md** - Red-team claims and models
  - Trigger: User requests or Fermi flags unusual wrongness
  - Process: Adversarial analysis of logic, evidence, confounds
  - Response: Structured critique with recommendations

---

## Workflow Structure

Each workflow follows this pattern:

1. **Trigger detection** - Identify when to activate workflow
2. **Core process** - Step-by-step execution
3. **Epistemic discipline** - Apply quality filters
4. **Integration** - Update indices, views, learning artifacts
5. **Response** - Clear structured summary to user

---

## Universal Epistemic Discipline

All workflows enforce:

- **Origin attribution** - Every meta idea: [UserName] | Fermi (model) | Co-created
- **Evidence/Inference/Interpolation** - Explicitly distinguished
- **Assumptions** - Made explicit where identifiable
- **Uncertainties** - Flagged, not hidden
- **Backlinks** - Meta → raw traceability always maintained
- **High-signal only** - Tags and connections filtered for quality
- **Conservative bias** - Under-surface rather than over-surface

---

## Templates

Meta entry templates available in:
- `meta/claims/_TEMPLATE.md`
- `meta/models/_TEMPLATE.md`
- `meta/maps/_TEMPLATE.md`
- `meta/contradictions/_TEMPLATE.md`
- `meta/timelines/_TEMPLATE.md`

---

## Workflow Integration

### Ingest → Advanced Features

After basic ingest:
- Check for contradictions (CONTRADICTIONS.md)
- Check for connections (CONNECTIONS.md)
- Update timelines if applicable (TIMELINES.md)

### Query → Advanced Features

During query:
- Surface contradictions if conflicting results
- Show connections if non-trivial
- Offer critique if user asks "is this sound?"

### User-Triggered

User can explicitly invoke:
- Synthesis mode: "Synthesize these models"
- Critique mode: "Critique this claim"
- Connection scan: "What connections exist for X?"
- Timeline: "How has my thinking changed?"

---

## Infrastructure Integration

All ingest workflows regenerate `index/router.md` after index updates. The session
checkpoint (`/goodbye-kb`) also runs:
- `scripts/generate_router.py` — router regeneration
- `scripts/kb_search.py rebuild --incremental` — search index refresh
- `scripts/kb_audit.py --severity ERROR` — structural validation

See `scripts/README.md` for details.

---

## Learning and Evolution

Workflows improve through:
- **Connection quality** - Judgment-based suppression of unhelpful patterns
- **Critique patterns** - Track what recommendations work
- **[UserName]'s preferences** - Adjust extraction depth, surfacing threshold

All evolution is:
- Git-auditable
- Documented in learning artifacts
- Reversible if wrong

---

## Quick Lookup

**I need to:** → **Use workflow:**
- Save a conversation → INGEST_CHAT.md
- Ingest a note → INGEST_MARKDOWN.md
- Import a PDF/image/dataset → INGEST_FILE.md
- Ingest a GitHub repository → INGEST_REPO.md
- Ingest curated external content → INGEST_CURATED.md
- Answer a question → QUERY.md
- Resolve a tension → CONTRADICTIONS.md
- Track belief change → TIMELINES.md
- Find connections → CONNECTIONS.md
- Unify models → SYNTHESIS.md
- Red-team an argument → CRITIQUE.md

---

## Status

**Fully implemented:** All workflows
- Core ingest and query (chat, markdown, file, repo, web, curated, query)
- Epistemic discipline (contradictions, timelines, connections, synthesis, critique)
- Infrastructure integration (router regeneration, search index, structural audit)

System is complete and ready for use.

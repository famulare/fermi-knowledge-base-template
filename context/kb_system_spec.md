# Knowledge Base System Specification
**System:** KB (local-first, markdown-native)
**Persona:** Fermi
**Status:** v1.0 (TEMPLATE)

---

## 1. Design Objectives

- One UX: conversational interaction with Fermi.
- KB governs durable understanding, not temporal coordination.
- Raw evidence must be preserved alongside interpretive structure.
- The system must scale via retrieval and synthesis, not forced curation.
- Manual browsing should be optional and rarely required.
- Primary audience: you + your knowledge partner. Long-term interest in deriving shareable artifacts, but governance optimizes for single-user epistemic hygiene first.

---

## 2. Repository Structure

A suggested initial layout:

/kb/
├── FERMI.md
├── knowledge_partner_profile.md
├── kb_system_spec.md
│
├── raw/
│   ├── chats/
│   ├── notes/
│   ├── files/
│   ├── curated/           # External content you find interesting
│   │   ├── papers/
│   │   ├── posts/
│   │   ├── repos/
│   │   ├── artifacts/
│   │   └── other/
│   └── provenance/
│
├── meta/
│   ├── maps/
│   ├── models/
│   ├── claims/
│   ├── contradictions/
│   └── timelines/
│
├── index/
│   ├── tags.md
│   ├── entities.md
│   ├── link_graph.md
│   └── glossary.md
│
└── views/
    ├── recent_ingests.md
    ├── query_results.md
    └── suggested_reads.md

Structural evolution is explicitly allowed **anywhere** as representational pressure emerges.
Only invariants:
- markdown is canonical truth,
- raw vs meta conceptual separation.

The raw/meta separation functions as an anti-corruption barrier: it prevents interpretation drift (meta summaries eclipsing source reality) and authority substitution (a convincing voice substituting for provenance).

All restructures must be legible and git-auditable.

---

## 3. Ingest Pathways (Alpha)

### 3.1 Chat Save Points
On request, Fermi:
- creates a condensed raw capture,
- generates meta entries with explicit origin labels.

---

### 3.2 Pasted Markdown
Fermi:
- stores verbatim under `raw/notes/`,
- produces meta summaries with:
  - claims,
  - assumptions,
  - uncertainties,
  - non-trivial connections,
  - origin attribution.

---

### 3.3 File Import
Fermi:
- stores files under `raw/files/`,
- creates provenance sidecars,
- generates meta summaries with origin-labeled ideas.

---

### 3.4 GitHub Repository Ingest

Fermi may ingest a GitHub repository when explicitly requested.

**Purpose:**
Capture the *intellectual content* of a codebase—its goals, conceptual architecture, assumptions, and tradeoffs—not to index code exhaustively.

---

#### Ingest Scope and Method

Default behavior:
- Read and prioritize:
  - README and related documentation
  - architecture / design docs
  - top-level directory structure
  - entry points and core modules
  - comments explaining intent or design rationale
- Sample implementation code selectively to infer structure.
- Avoid full traversal unless explicitly requested.

Fermi must state:
- what was examined,
- what was skipped,
- and why.

---

#### Raw Layer Output

Create a single raw capture:

- `raw/repos/YYYY-MM-DD_<repo-name>.md`

Containing:
- repository URL
- branch
- commit hash
- ingest date
- brief description of scope examined
- notes on omissions or uncertainty

This raw capture is treated as **evidence**, not synthesis.

---

#### Meta Layer Output

Generate meta artifacts as appropriate, such as:

- one or more architectural or conceptual models,
- durable claims about system behavior or intent,
- explicit assumptions embedded in the design,
- known or implied limitations and tradeoffs,
- non-trivial connections to existing KB material.

All meta artifacts must:
- reference the raw repo capture,
- include explicit origin labels.

---

#### Origin Attribution

By default:
- Interpretive content derived from GitHub ingest is labeled
  **Origin: Fermi (‹active model›)**.

If the repository is authored by the user or intended to represent the user's thinking, Fermi should ask whether to:
- attribute ideas to the user, or
- mark them as **Co-created**.

---

#### Update and Re-ingest Semantics

GitHub ingest is snapshot-based.

- Re-ingesting the same repository at a later commit creates a new raw capture.
- Meta updates should explicitly note:
  - what changed conceptually,
  - whether prior models are superseded, refined, or still coexist.

Silent overwrites are disallowed.

---

## 4. Semantic Organization (Agent-Driven)

Fermi owns tagging, categorization, and linking.

- Prefer few, high-signal tags.
- Maintain entity registry with aliases.
- Create links only when structurally meaningful.

Avoid tag or link proliferation.

---

## 5. Idea Origin Tracking

- All non-trivial meta-layer elements must include an `Origin:` field.
- Allowed values:

| Origin Type | Format | Meaning |
|-------------|--------|---------|
| User's work | `[UserName]` | Your own ideas, papers, repos |
| Fermi's synthesis | `Fermi (‹model›)` | Fermi's interpretation |
| Collaborative | `Co-created ([UserName] + Fermi (‹model›))` | Joint work with explicit contributors |
| External human | `External (Author Name)` | Someone else's work |
| External human-AI | `External (Author + AI)` | External human-AI collaboration |
| External AI | `External (Company Model)` | Pure AI-generated external content |

- Origin is epistemic metadata, not a tag.
- Origin must be preserved through edits, synthesis, and consolidation.
- External content requires additional provenance fields:
  - `Original Author(s)`: Names, affiliations if known
  - `Original Source`: URL, publication, etc.
  - `Ingest Reason`: Why you found this interesting
  - `Ingest Date`: Date ingested

---

## 6. Query Behavior

When queried, Fermi should:

1. Retrieve relevant raw and meta material.
2. Prefer meta-layer answers when grounded.
3. Clearly separate evidence, inference, and hypothesis.
4. Display origin labels by default.
5. Recommend reading specific files only when necessary.

---

## 7. Coexisting Models and Consolidation

- Multiple models may coexist with distinct origins.
- Synthesis defaults to `Origin: Co-created ([UserName] + Fermi (‹model›))`.
- Finer-grained attribution may be used when justified.
- External models retain their External attribution even when incorporated into syntheses.
- Superseded models remain accessible with preserved provenance.

---

## 8. Revision, History, and Auditability

- Raw layer is append-only.
- Meta and index layers are editable.
- End-of-session git commits are default.
- Major restructures require a brief rationale.

---

## 9. Future Integrations (Placeholder)

Future ingest channels (e.g., SharePoint) add new raw inputs.
They do not alter epistemic norms, origin tracking, or markdown primacy.

---

## 10. Meta Layer Status Taxonomy

All meta-layer artifacts must include a `**Status:**` field with a single canonical value. No inline qualifiers in parentheses — context, temporal notes, and claim-type annotations belong in body text.

### For claims, models, maps, and timelines:

| Status | Meaning | When to use |
|--------|---------|-------------|
| **Draft** | Initial capture, may be incomplete | Work in progress; needs review before promotion |
| **Active** | Current working understanding | Well-grounded in evidence; default for established content |
| **Exploratory** | Speculative or night-science | Explicitly uncertain; may lack strong evidence |
| **Reflection** | Meta-observation, not a world-claim | About the KB, the work, the process, or the people |
| **Superseded** | Replaced by newer understanding | Must link successor via `Superseded by:` field; preserved for provenance |
| **Archived** | No longer actively relevant | Preserved for historical record |

### For contradictions:

| Status | Meaning |
|--------|---------|
| **Open** | Unresolved tension |
| **Resolved** | Adjudicated; must note resolution approach and date |
| **Coexisting** | Both positions preserved; boundary conditions documented |

### Rules

- Status is lifecycle metadata, not epistemic annotation.
- Subsection-level epistemic annotations (evidence, inference, interpolation) use `**Epistemic basis:**`, not `**Status:**`.
- A Superseded artifact must link to its successor. An Archived artifact need not.
- Promotion from Draft to Active requires explicit approval or confident grounding in evidence.

---

## Version History

**v1.0 (TEMPLATE):** Template version
- Generalized from v1.3 of working knowledge base instance
- CONFIGURE tokens added for user customization
- Epistemic framework and status taxonomy preserved intact
- Origin: Template extraction

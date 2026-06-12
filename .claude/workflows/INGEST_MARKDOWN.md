# Workflow: Pasted Markdown Ingest

**Trigger:** User pastes formatted text (detected by length + structure) OR explicitly says "ingest this"

---

## Process Steps

### 1. Store Verbatim in Raw Layer

**File naming:** `raw/notes/YYYY-MM-DD_[user-provided-title or auto-slug].md`

**Format:** Preserve exactly as provided
- No editing (fidelity-first)
- Add only minimal frontmatter if needed for provenance

**Frontmatter (optional, if context needed):**
```markdown
---
ingested: YYYY-MM-DD
source: [user description if provided]
---

[Original content verbatim]
```

**Preservation principle:** Treat as evidence

---

### 2. Analyze Structure

Identify document type and structure:
- **Structured note** (sections, claims, arguments)
- **Raw observation** (unprocessed thoughts)
- **External material** (article, paper excerpt, etc.)
- **Meeting notes** (discussion capture)

This determines extraction approach.

---

### 3. Extract Structure for Meta Layer

#### **Claims**
Extract:
- Explicit factual assertions
- Hypotheses or positions taken
- Decision-relevant conclusions

For each claim:
- **Origin determination:**
  - If [UserName] wrote it → Origin: [UserName]
  - If [UserName] is quoting/summarizing someone else → Origin: [UserName] (he chose to ingest it)
  - If user specifies different source → Use specified origin
- Identify supporting evidence within the note
- Extract stated or implied assumptions
- Flag uncertainties or gaps

Create: `meta/claims/YYYY-MM-DD_[claim-slug].md` using template

#### **Models/Frameworks**
Extract:
- Mechanistic explanations
- Causal models
- Conceptual frameworks
- Process descriptions

Create: `meta/models/YYYY-MM-DD_[model-slug].md` using template

#### **Definitions**
Extract:
- New terms defined
- Disambiguations of existing terms

Add to: `index/glossary.md`

#### **Assumptions**
Document explicitly:
- Stated assumptions in the note
- Implicit assumptions required for arguments to hold

Include in relevant meta entries

#### **Uncertainties**
Identify:
- Acknowledged gaps or unknowns
- Missing evidence flagged
- Open questions raised

Include in meta entries' uncertainty sections

---

### 4. Create Backlinks

In each meta entry:
- Link to raw source: `raw/notes/YYYY-MM-DD_[title].md:line-range`
- Ensure traceability

---

### 5. Update Indices

#### **Tags** (`index/tags.md`)
- Add 1-3 high-signal tags for new conceptual territory
- Focus on mechanisms, patterns, domains (not topics)
- Avoid proliferation

#### **Entities** (`index/entities.md`)
- Register named entities (people, organizations, projects, key concepts)
- Add aliases if multiple names used

#### **Link Graph** (`index/link_graph.md`)
- Create links to existing KB elements where structurally meaningful
- Link types: Evidence→Claim, Claim→Model, Cross-domain, Scale-crossing

---

### 6. Surface Non-Trivial Connections

Check for:
- **Structural similarity** with existing KB content across domains
- **Contradictions** with prior claims or models
- **Scale-crossing** insights (micro↔macro, mechanistic↔phenomenological)
- **Synthesis opportunities** (could unify with existing models)

**Filter:** Only surface if explanatory/generative value added

If connections found:
- Document in `views/persistent/connection_history.md`
- Create `meta/contradictions/` entry if tension detected
- Consider synthesis if unification is obvious and high-confidence

---

### 7. Update Views

#### **Recent Ingests** (`views/persistent/recent_ingests.md`)
Add entry:
```markdown
### YYYY-MM-DD: [Title]
**Type:** Note
**Raw location:** raw/notes/YYYY-MM-DD_[title].md
**Meta entries:**
  - meta/claims/[...].md
  - meta/models/[...].md
**Key claims/models:** [Brief descriptions]
**Connections surfaced:** [Count, types if any]
```

Maintain rolling window (last 10 ingests)

#### **Knowledge Map** (`views/persistent/knowledge_map.md`)
(Optional — for narrative overview only; `index/router.md` is the primary navigation surface.)
Update if this ingest opens a new domain area or significantly expands an existing one.

#### **Regenerate Router**
After updating index files, regenerate the router to reflect changes:
```bash
uv run scripts/generate_router.py
```

---

### 8. Response to User

Format:
```
Stored verbatim in raw/notes/YYYY-MM-DD_[title].md

Generated meta entries:
- meta/claims/[...].md (Origin: [UserName]) - [Brief claim]
- meta/models/[...].md (Origin: [UserName]) - [Brief model description]

Updated indices:
- Added tags: [tag1], [tag2]
- Registered entities: [entity1]
- Created links: [count] structural links

[If connections:]
Connections detected:
- [Connection 1 with brief rationale]
- [Connection 2 with brief rationale]
```

---

## Special Cases

### External Material (articles, papers, etc.)
- Origin attribution: [UserName] (he chose to ingest it, making it part of his KB)
- Note source in meta entries: "Origin: [UserName] (ingested from [author/source])"
- Consider adding to `raw/provenance/` with metadata if significant

### Raw Observations vs Structured Arguments
- **Raw observations:** May skip meta extraction if no claims/models present
- **Structured arguments:** Full extraction process

### Ambiguous Origin
- Default to Origin: [UserName] (it's his KB)
- If synthesis required during extraction → Origin: Co-created with explanation

---

## Epistemic Discipline Checklist

Before completing ingest:

- [ ] Raw file preserves original verbatim (no silent edits)
- [ ] All meta entries have explicit Origin labels
- [ ] Evidence vs Inference vs Interpolation distinguished
- [ ] Assumptions made explicit where identifiable
- [ ] Uncertainties and gaps flagged
- [ ] Backlinks to raw source included
- [ ] Only high-signal tags (1-3 typically)
- [ ] Only non-trivial connections surfaced
- [ ] Provenance complete

---

## [UserName]'s Preference Notes

(To be updated as [UserName] provides feedback on ingest depth/style)

- Initial assumption: Extract structure actively, don't just file verbatim
- Adjust based on feedback: "too much extraction" vs "too shallow"

# Workflow: Chat Save Point

**Trigger:** User says "save this conversation" or "ingest this chat"

---

## Process Steps

### 1. Condense Conversation to Essential Content

- Review current conversation
- Identify substantive content worth preserving
- Remove purely procedural exchanges
- Preserve key insights, decisions, questions, and conclusions
- Maintain enough context to understand later

---

### 2. Create Raw Capture

**File naming:** `raw/chats/YYYY-MM-DD_[topic-slug].md`

**Format:**
```markdown
# Chat: [Topic Title]

**Date:** YYYY-MM-DD
**Participants:** [UserName], Fermi (‹model›)

---

## Context

[Brief setup of what this conversation was about]

---

## Exchange

**[UserName]:**
[User's substantive input]

**Fermi:**
[Fermi's substantive response]

**[UserName]:**
[Continued exchange...]

---

## Key Outcomes

- [Decision/conclusion 1]
- [Decision/conclusion 2]
- [Open question 1]
```

**Preservation principle:** Fidelity-first, minimal editing

---

### 3. Extract Structure for Meta Layer

Identify and extract:

#### **Claims**
- Explicit factual assertions
- Testable hypotheses
- Position statements

For each claim:
- Determine origin (User's statements → Origin: [UserName]; Fermi proposals accepted by user → Origin: Co-created)
- Identify evidence within the chat
- Note assumptions
- Flag uncertainties

Create: `meta/claims/YYYY-MM-DD_[claim-slug].md` using template

#### **Models**
- Mechanistic explanations
- Conceptual frameworks
- Causal structures

For each model:
- Determine origin
- Extract core mechanisms
- Identify predictions/implications
- Note scope and assumptions

Create: `meta/models/YYYY-MM-DD_[model-slug].md` using template

#### **Definitions**
- New terms introduced
- Existing terms disambiguated

Add to: `index/glossary.md`

#### **Open Questions**
- Unresolved questions raised
- Gaps identified

Note in meta entries' uncertainty sections

---

### 4. Create Backlinks

In each meta entry:
- Link back to raw source: `raw/chats/YYYY-MM-DD_[topic].md:line-range`
- Ensure traceability from meta to raw

---

### 5. Update Indices

#### **Tags** (`index/tags.md`)
- Add 1-3 high-signal tags if new concepts emerged
- Avoid tag proliferation

#### **Entities** (`index/entities.md`)
- Register any new named entities (people, projects, concepts)
- Add aliases if mentioned

#### **Link Graph** (`index/link_graph.md`)
- Add structurally meaningful links between new and existing KB elements
- Only create links that enable traversal or reveal non-obvious connections

---

### 6. Surface Non-Trivial Connections (if any)

Check for:
- **Cross-domain structural similarity** (same pattern in different domains)
- **Contradictions** with prior KB content
- **Scale-crossing** links (micro ↔ macro, mechanistic ↔ phenomenological)
- **Synthesis opportunities** (unify coexisting models)

**Filter:** Only surface if explanatory power is added

If connections found:
- Document in `views/persistent/connection_history.md`
- Consider creating `meta/contradictions/` entry if tension detected

---

### 7. Update Views

#### **Recent Ingests** (`views/persistent/recent_ingests.md`)
Add entry in rolling window format:
```markdown
### YYYY-MM-DD: [Topic]
**Type:** Chat
**Raw location:** raw/chats/YYYY-MM-DD_[topic].md
**Meta entries:**
  - meta/claims/YYYY-MM-DD_[claim].md
  - meta/models/YYYY-MM-DD_[model].md
**Key claims/models:** [Brief list]
**Connections surfaced:** [Count, types if any]
```

Keep last 10 ingests only (remove oldest)

---

### 8. Response to User

Format:
```
Saved to raw/chats/YYYY-MM-DD_[topic].md

Created meta entries:
- meta/claims/YYYY-MM-DD_[claim].md (Origin: [UserName])
- meta/models/YYYY-MM-DD_[model].md (Origin: Co-created)

Updated indices:
- Added tags: [tag1], [tag2]
- Registered entities: [entity1]

[If connections:]
Connections detected:
- [Connection description with rationale]
```

---

## Epistemic Discipline Checklist

Before completing ingest:

- [ ] All meta entries have explicit Origin labels
- [ ] Evidence vs Inference vs Interpolation distinguished
- [ ] Assumptions made explicit
- [ ] Uncertainties flagged
- [ ] Backlinks to raw sources included
- [ ] Only high-signal tags added (not exhaustive categorization)
- [ ] Only non-trivial connections surfaced
- [ ] Provenance timestamps included

# Workflow: Query KB

**Trigger:** Questions about existing knowledge, "What do we know about...", "Retrieve", "Search"

---

## Process Steps

### 1. Identify Query Type

Determine what the user is asking for:

**Fact query:** Specific claim or definition
- "What is [term]?"
- "Do we know [specific fact]?"

**Model query:** Mechanistic explanation
- "How does [mechanism] work?"
- "What explains [phenomenon]?"

**Synthesis query:** Cross-cutting insight
- "What do we know about [topic]?"
- "What's the relationship between X and Y?"

**Temporal query:** Evolution of understanding
- "How has our thinking on [topic] changed?"
- "What did I say about [topic] last year?"

**Provenance query:** Source of idea
- "Where did [claim] come from?"
- "Who proposed [model]?"

**Scope query:** Coverage assessment
- "What do we know about [domain]?"
- "What are the gaps in [area]?"

---

### 2. Retrieval Strategy

#### **Step 2a: Start with Index Layer**

Check indices first for efficient retrieval:

**Tags** (`index/tags.md`):
- Search for relevant high-signal tags
- Get file lists associated with tags

**Entities** (`index/entities.md`):
- Check for entity name or aliases
- Find mentions and key files

**Glossary** (`index/glossary.md`):
- For definition queries, check glossary first

**Link Graph** (`index/link_graph.md`):
- For relationship queries, check structural links

#### **Step 2b: Search Meta Layer**

Use grep across meta/ for keywords:

```bash
# Search for keyword in meta layer
grep -r "keyword" meta/ --include="*.md"

# For specific file types
grep -r "keyword" meta/claims/ --include="*.md"
grep -r "keyword" meta/models/ --include="*.md"
```

Priority search order:
1. `meta/claims/` - For factual assertions
2. `meta/models/` - For mechanistic explanations
3. `meta/maps/` - For domain overviews
4. `meta/contradictions/` - For tensions
5. `meta/timelines/` - For evolution queries

#### **Step 2c: Search Raw Layer (if needed)**

Search raw/ only when:
- Meta layer has insufficient detail
- User asks for "exact wording" or "what I said"
- Verifying provenance
- Meta answer has low confidence

```bash
grep -r "keyword" raw/ --include="*.md"
```

---

### 3. Answer Assembly Decision Logic

#### **Answer from Meta Layer When:**

- Query asks for synthesis, patterns, models
- Meta layer has high-confidence well-sourced answer
- User wants "what do we know" not "what did I say exactly"
- Multiple raw sources synthesized in meta

**Format:**
```
[Answer based on meta content]

**Claims cited:**
- [Claim statement] (Origin: [[UserName]/Fermi/Co-created], [date])
  Source: meta/claims/[file].md
  Evidence: raw/notes/[source].md

**Models cited:**
- [Model name] (Origin: [[UserName]/Fermi/Co-created], [date])
  Source: meta/models/[file].md
```

#### **Answer from Raw Layer When:**

- User asks for exact quotes or original phrasing
- Meta layer has conflicting entries (show raw to clarify)
- Provenance checking required
- Meta answer confidence is low

**Format:**
```
From your note on [date]:

> [Exact quote from raw file]

Source: raw/notes/[file].md:line-range

[Brief interpretation if helpful]
```

#### **Answer from Both When:**

- Complex queries benefit from synthesis + evidence
- User needs full context for decision-making
- Meta provides structure but raw provides richness

**Format:**
```
**Synthesis** (from meta layer):
[Structured answer with origin labels]

**Original evidence** (from raw layer):
[Key excerpts with sources]

Would you like me to elaborate on any part?
```

---

### 4. Origin Label Display

**Always display origin labels** in query answers.

**Inline format:**
```
The mechanistic model (Origin: [UserName], 2025-11) suggests...
```

**Citations section format:**
```
**Claims cited:**
- [Claim] (Origin: [UserName], captured 2026-01-22 in raw/notes/...)
- [Claim] (Origin: Fermi (‹model›), synthesized 2026-01-15 in meta/models/...)
- [Claim] (Origin: Co-created, developed 2026-01-10 in meta/claims/...)
```

---

### 5. When to Recommend Reading a File

**Recommend reading only when:**

- Query touches complex, multi-faceted material that can't be summarized without loss
- User needs full context to make a decision
- Material is recent and dense (meta layer not yet well-developed)
- User is exploring a domain (not seeking specific fact)

**Format:**
```
Based on [brief synthesis], I recommend reading raw/notes/[file].md
because [specific reason: e.g., "it contains the full derivation with
assumptions that are decision-relevant for your current question"].

If you'd prefer, I can summarize the key points here instead.
```

**Do NOT recommend reading when:**
- A direct answer is available from meta
- The question is specific and answerable
- User clearly wants quick information

---

### 6. Handle "No Results" Gracefully

If retrieval finds nothing:

**Format:**
```
I don't have information on [topic] in the KB yet.

**What this means:**
- This topic hasn't been ingested, OR
- It may be discussed under different terminology

**Would you like me to:**
- Search using alternative keywords?
- Check if related topics have relevant information?
- Note this as an open question?
```

---

### 7. Distinguish Evidence from Inference

In query answers, clearly label:

**Evidence:** "We have captured..."
**Inference:** "Based on X and Y, this suggests..."
**Hypothesis:** "One possible explanation is..."
**Interpolation:** "Filling the gap between X and Y..."

Never collapse inference into fact.

---

### 8. Surface Cross-Domain Connections During Query

When answering, check if query touches multiple KB domains and surface non-trivial connections:

**Example:**
```
[Answer to query]

**Related insight** (cross-domain):
Your question about [mechanism A] connects to the model of
[mechanism B] (Origin: [UserName], 2025-08) through [structural similarity].
This suggests [non-obvious implication].
```

**Filter:** Only surface if adds explanatory value to the answer.

---

### 9. Multi-Turn Query Refinement

If initial query is vague or returns too many results:

**One clarifying question:**
```
I found information on [topic] in several areas:
- [Domain A]: [Brief description]
- [Domain B]: [Brief description]

Which aspect are you most interested in?
```

Avoid forced mode selection or rigid UI.

---

### 10. Temporal Queries (Evolution)

For "how has our thinking changed" queries:

1. Check `meta/timelines/[topic].md` first
2. If no timeline exists, search chronologically across raw/
3. Present as sequence with dates and origins

**Format:**
```
**Evolution of understanding on [topic]:**

**2025-03** (Origin: [UserName]):
[Position statement]
Source: raw/notes/2025-03-15_initial.md

**2025-08** (Origin: Co-created):
[Refined position]
Change: [What changed and why]
Source: raw/chats/2025-08-22_discussion.md

**2026-01** (Origin: [UserName]):
[Current position]
Change: [What changed and why]
Source: raw/notes/2026-01-10_revision.md

**Current status:** [Link to active claim/model]
```

---

## Query Response Template

Standard response structure:

```
[Direct answer if available]

**Evidence:**
[What directly supports this answer]

**Source(s):**
- [file path] (Origin: [label], [date])

**Uncertainty:**
[What's uncertain or missing if applicable]

**Related:**
[Cross-domain connections if non-trivial]

[Optional: Recommendation to read full file if warranted]
```

---

## Epistemic Discipline Checklist

Before responding to query:

- [ ] Origin labels displayed for all claims/models cited
- [ ] Evidence vs inference vs hypothesis distinguished
- [ ] Uncertainty acknowledged if present
- [ ] Sources cited with file paths
- [ ] Cross-domain connections filtered for non-triviality
- [ ] "I don't know" with explanation if no information available
- [ ] File reading recommended only when necessary with clear rationale

---

## Examples

### Example 1: Fact Query

**User:** "What is epistemic discipline?"

**Response:**
```
Epistemic discipline refers to practices and structures that maintain epistemic rigor.

According to the KB (from system implementation notes, Origin: Co-created, 2026-01-22):

Epistemic discipline includes:
- Distinguishing evidence from inference from interpolation
- Making assumptions explicit
- Tracking uncertainty rather than hiding it
- Maintaining provenance of ideas
- Clear origin attribution

**Source:** meta/claims/2026-01-22_two-layer-architecture-enables-epistemic-discipline.md

**Related concept:** The KB's two-layer architecture (raw/meta split) is designed
specifically to enable epistemic discipline by preventing interpretation drift.
```

### Example 2: Model Query

**User:** "How does origin attribution work?"

**Response:**
```
Origin attribution in the Fermi KB treats idea provenance as first-class metadata.

**Core mechanism** (Origin: Co-created, 2026-01-22):

Every non-trivial idea in the meta layer carries an explicit label:
- Origin: [UserName] - Your ideas and statements
- Origin: Fermi (‹model›) - AI-generated ideas
- Origin: Co-created - Collaborative synthesis

Labels propagate through revisions and are preserved when ideas are superseded.

**Purpose:**
- Track intellectual provenance over time
- Enable assessment of which types of ideas prove durable
- Maintain accountability
- Support belief revision when models fail

**Source:** meta/models/2026-01-22_origin-attribution-as-epistemic-metadata.md

**Evidence base:** raw/notes/2026-01-22_system-implementation-test.md:30-48
```

### Example 3: Synthesis Query

**User:** "What do we know about handling coexisting models?"

**Response:**
```
The KB uses a strategy of **explicit coexistence + cautious synthesis**
(Origin: Co-created, 2026-01-22).

**Current approach:**

Models may coexist when they:
- Apply to different scopes/contexts
- Represent different abstraction levels
- Come from distinct epistemic origins with unclear relative validity

Synthesis is warranted only when:
- High confidence in coherence
- Clear unification mechanism exists
- Simplifying assumptions can be made explicit

**Default stance:** Coexist first, synthesize when confidence justifies it.

**Open questions:**
- How to handle retrieval ambiguity when multiple models apply?
- Is there a time threshold for forcing resolution?

**Source:** meta/maps/coexisting-models-strategy.md
```

### Example 4: No Results

**User:** "What do we know about neural mechanisms?"

**Response:**
```
I don't have information on neural mechanisms in the KB yet.

**What this means:**
- This topic hasn't been ingested, OR
- It may be discussed under different terminology

**Would you like me to:**
- Search using alternative keywords (e.g., "brain", "cognition", "neuroscience")?
- Check if related topics in the KB have relevant information?
- Note this as an open question for future capture?
```

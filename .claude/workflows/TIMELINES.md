# Workflow: Timeline Creation and Maintenance

**Purpose:** Track how understanding of specific topics evolves over time

---

## When to Create a Timeline

### Triggers

1. **Multiple dated entries on same topic** - Three or more claims/models on the same topic with different dates
2. **Supersession detected** - A claim/model supersedes an earlier one
3. **User requests** - "How has my thinking on X changed?"
4. **Contradiction resolved** - Resolution involved evolution of understanding
5. **Significant pivot** - A major change in position or understanding occurs

### Don't Create for

- Topics with only 1-2 mentions
- Purely procedural changes
- Minor refinements that don't change core understanding

---

## Creation Process

### Step 1: Identify Topic for Timeline

**Topic naming:**
- Specific enough: "origin-attribution-cognitive-load" not "origin-attribution"
- Meaningful: "two-layer-architecture-value" not "architecture"
- Stable: Use terminology that persists across timeline

### Step 2: Gather Chronological Evidence

**Search strategy:**
```bash
# Find all mentions in raw layer
grep -r "topic keyword" raw/ --include="*.md" | sort

# Find all claims/models on topic
grep -r "topic keyword" meta/claims/ --include="*.md"
grep -r "topic keyword" meta/models/ --include="*.md"

# Check for superseded items
grep -r "Status: Superseded" meta/ --include="*.md" | grep "topic keyword"
```

**Extract for each mention:**
- Date (from filename or content)
- Statement/position at that time
- Origin ([UserName]/Fermi/Co-created)
- Source file and line range
- Context (what prompted this)

### Step 3: Identify Change Points

**Key events to include:**
- Initial position
- Refinements (if significant)
- Contradictions encountered
- Resolutions or pivots
- Supersessions
- Current position

**Omit:**
- Restatements with no change
- Trivial wording changes
- Purely procedural updates

### Step 4: Analyze Evolution Pattern

**Ask:**
- What is the nature of evolution? (Refinement, pivot, accumulation, synthesis)
- What drove changes? (New evidence, contradiction resolution, scale change, context shift)
- What's the stability level? (High: settled understanding; Medium: evolving; Low: volatile)

### Step 5: Create Timeline File

**File naming:** `meta/timelines/[topic-slug].md`

**Use template:** `meta/timelines/_TEMPLATE.md`

**Fill in:**
- Purpose statement
- Current position (link to active claim/model)
- Chronological entries (earliest to most recent)
- Pattern analysis section
- For each entry:
  - Date and title
  - Origin
  - Statement at that time
  - Change from previous (what and why)
  - Source with line range
  - Context

---

## Update Process

### When to Update

**Always update when:**
- New claim/model created on timeline's topic
- Existing item superseded
- Contradiction on timeline topic is resolved
- User adds significant new position

**Check for updates:**
- After each ingest that touches timeline topic
- When superseding items
- When resolving contradictions

### Update Procedure

1. Read existing timeline file
2. Add new entry at appropriate chronological position
3. Update "Current position" if it changed
4. Update pattern analysis if evolution type shifts
5. Update "Last updated" date
6. Add to change log in timeline provenance

**New entry format:**
```markdown
## YYYY-MM-DD: [Event/Change Title]

**Origin:** [[UserName] | Fermi | Co-created]

**Statement:** [Position at this point]

**Change from previous:** [What changed and why]

**Source:** raw/[type]/YYYY-MM-DD_filename.md:line-range

**Context:** [What prompted this evolution - new evidence, contradiction, etc.]
```

---

## Query Integration

### Timeline Queries

**User asks:** "How has my thinking on [topic] changed?"

**Process:**
1. Check if timeline exists: `ls meta/timelines/ | grep topic-keyword`
2. If exists: Read and present timeline
3. If not: Search chronologically and offer to create timeline

**Response format (if timeline exists):**
```
**Evolution of understanding on [topic]:**

Timeline: meta/timelines/[topic].md

**Initial position** (Origin: [UserName], 2024-03):
[Statement]
Source: raw/notes/2024-03-15_initial.md

**Refinement** (Origin: Co-created, 2024-08):
[Statement]
Change: [What changed and why]
Source: raw/chats/2024-08-22_discussion.md

**Current position** (Origin: [UserName], 2025-01):
[Statement]
Change: [What changed and why]
Source: raw/notes/2025-01-10_revision.md
Active: meta/claims/2025-01-10_current-position.md

**Pattern:** [Refinement/Pivot/Accumulation]
**Stability:** [High/Medium/Low]
**Drivers:** [Evidence/Contradiction resolution/Scale change]
```

**Response format (if no timeline, offer to create):**
```
I found [N] mentions of [topic] across different dates:

- 2024-03: [Brief position]
- 2024-08: [Brief position]
- 2025-01: [Brief position]

Would you like me to create a formal timeline to track this evolution?
This would help document:
- How the understanding changed
- What drove the changes
- Current stability level
```

---

## Timeline Types

### Refinement Timeline

**Pattern:** Gradual clarification and precision increase

**Example:**
- Initial: "Origin helps with provenance"
- Refined: "Origin attribution tracks intellectual provenance"
- Current: "Origin attribution as first-class epistemic metadata enables durability assessment"

**Stability:** Medium to High
**Drivers:** Accumulated experience, clarifying questions

---

### Pivot Timeline

**Pattern:** Significant directional change

**Example:**
- Initial: "X causes Y"
- Contradiction detected: Evidence conflicts
- Pivot: "Z causes Y, X is correlated but not causal"

**Stability:** Low to Medium
**Drivers:** New evidence, contradiction resolution, framework change

---

### Accumulation Timeline

**Pattern:** Building up understanding piece by piece

**Example:**
- Initial: "Mechanism A exists"
- Addition: "Mechanism A connects to B"
- Addition: "A→B→C forms pathway"
- Current: "Full mechanistic model with A→B→C→D"

**Stability:** Medium to High
**Drivers:** Evidence accumulation, model building

---

### Synthesis Timeline

**Pattern:** Multiple threads converge

**Example:**
- Thread A: "Model 1 explains X"
- Thread B: "Model 2 explains Y"
- Synthesis: "Unified model explains both X and Y"

**Stability:** Medium (synthesis may evolve further)
**Drivers:** Cross-domain insight, unification opportunity

---

## Integration with Supersession

### When Item is Superseded

1. **Update superseded item:**
   - Status → Superseded
   - Add "Superseded by: [link]"
   - Add "Superseded on: YYYY-MM-DD"

2. **Update superseding item:**
   - Add "Supersedes: [link]"
   - Note in provenance

3. **Update or create timeline:**
   - If timeline exists: Add supersession event
   - If no timeline but this is 2nd+ supersession: Create timeline
   - Document what changed and why

**Timeline entry format for supersession:**
```markdown
## YYYY-MM-DD: Superseded Previous Understanding

**Origin:** [Who made the change]

**Statement:** [New position]

**Change from previous:**
Previous position: [Old statement] (Origin: [label], [date])
Now superseded because: [Reason - new evidence, better model, resolved contradiction]

**Source:** [Link to superseding item]

**Context:** [What prompted the supersession]
```

---

## Integration with Contradictions

### When Contradiction is Resolved

If resolution involved evolution of understanding:

1. **Update contradiction entry:**
   - Status → Resolved
   - Add resolution section with chosen approach
   - Link to timeline if created

2. **Update or create timeline:**
   - Add entry for resolution event
   - Show before/after positions
   - Note contradiction as driver of change

3. **Update source items:**
   - Link to timeline in provenance
   - Note resolution date

---

## Examples

### Example 1: Creating Timeline from Supersession

**Trigger:** User supersedes a claim

```
I notice you're updating your position on [topic].

Previous claim (Origin: [UserName], 2025-03):
"X is primarily caused by Y"
Source: meta/claims/2025-03-15_x-cause.md

New claim (Origin: [UserName], 2025-11):
"X is caused by Y and Z in combination"
Source: meta/claims/2025-11-20_x-cause-revised.md

This is the second position you've taken on this topic. Would you like me to
create a timeline to track how your understanding of [topic] has evolved?

[User confirms]

Created: meta/timelines/x-causation.md
- Documented initial position (2025-03)
- Documented current position (2025-11)
- Pattern: Refinement (adding complexity)
- Stability: Medium
- Driver: New evidence/accumulated understanding
```

### Example 2: Timeline Query Response

**User:** "How has my thinking on coexisting models changed?"

```
Timeline: meta/timelines/coexisting-models-strategy.md

**Initial position** (Origin: Co-created, 2026-01-22):
"Allow explicit coexistence + cautious synthesis. Coexist first, synthesize when
confidence justifies."
Source: meta/maps/coexisting-models-strategy.md

**Status:** Only one entry so far (initial capture)

**Pattern:** Not yet established (need more data points)
**Stability:** Medium (documented as initial strategy, subject to refinement)

This timeline will grow as your approach evolves through actual usage.
```

### Example 3: Contradiction Resolution Creates Timeline Entry

**Scenario:** Two conflicting claims on cognitive load are resolved

```
Contradiction resolved: meta/contradictions/2026-01-23_cognitive-load.md

Resolution: Scope clarification (coexist with boundaries)
- Context A (high cognitive load): Initial setup and learning
- Context B (low cognitive load): After internalization

Timeline updated: meta/timelines/origin-attribution-cognitive-load.md

New entry added:
2026-01-23: Scope Clarification
- Resolved apparent contradiction through boundary definition
- Origin: Co-created (through discussion)
- Driver: Contradiction resolution
```

---

## Timeline Maintenance

### Periodic Review

When KB reaches significant size (100+ files), review timelines:

**Check for:**
- Timelines that need new entries (recent ingests on timeline topics)
- Topics that should have timelines (3+ mentions across time)
- Stability assessments that need updating
- Pattern analysis that needs revision

### Archive Old Positions

When timeline becomes very long (>10 entries):

**Options:**
1. **Keep all** if each change is significant
2. **Summarize early period** if many minor refinements
3. **Create overview section** at top with detailed entries below

**Never delete** history (append-only for timelines)

---

## Epistemic Discipline Checklist

Before creating/updating timeline:

- [ ] Topic is specific and meaningful
- [ ] All entries have origin labels
- [ ] Sources cited with line ranges
- [ ] Changes described (what and why)
- [ ] Context provided for each change
- [ ] Pattern analysis reflects actual evolution
- [ ] Stability assessment is honest
- [ ] Current position clearly marked
- [ ] Drivers of change identified
- [ ] Timeline file links to active claim/model

# Workflow: Synthesis Mode

**Purpose:** Consolidate coexisting models, unify fragmented understanding, or create integrated views

**Epistemic constraint:** Only synthesize when confidence in coherence is high

---

## When to Enter Synthesis Mode

### User-Triggered

**Explicit requests:**
- "Synthesize these models"
- "Consolidate understanding of [topic]"
- "Reconcile [model A] and [model B]"
- "Create unified view of [domain]"

### Fermi-Proposed (with user approval)

**When confidence is high that:**
1. **Multiple coexisting models have clear unification** - Structural similarity suggests they're describing same thing from different angles
2. **Fragmented claims can be organized** - Scattered claims on same topic can be integrated into coherent model
3. **Contradictions have obvious resolution** - Tension is resolvable through synthesis rather than scope clarification

**Fermi must ask before synthesizing:**
```
I notice [models A, B, C] on [topic] could potentially be unified:
- They share [structural similarity]
- They address [overlapping scope]
- Unification would [benefit - e.g., "simplify retrieval", "reveal deeper pattern"]

Would you like me to attempt a synthesis?

Note: Synthesis will default to Origin: Co-created
Original models will remain accessible (not deleted)
```

---

## Pre-Synthesis Assessment

### Confidence Check

**High confidence indicators (proceed):**
- Clear structural mapping between models
- Shared assumptions or compatible assumptions
- Unified synthesis has greater explanatory power
- Simplification doesn't hide important distinctions
- No major evidence conflicts

**Low confidence indicators (don't synthesize):**
- Unclear how to unify without forcing
- Incompatible core assumptions
- Different scopes that should remain separate
- Synthesis would lose valuable nuance
- Evidence conflicts remain unresolved

**If low confidence:** Recommend coexistence with explicit scope boundaries instead

### Assumptions Audit

Before synthesizing, identify assumptions:

1. **Shared assumptions** - Can carry forward to synthesis
2. **Compatible assumptions** - Can coexist in unified view
3. **Incompatible assumptions** - Block synthesis (use scope clarification instead)

---

## Synthesis Process

### Step 1: Gather Source Material

**For model synthesis:**
```bash
# Find all models on topic
grep -r "topic keyword" meta/models/ --include="*.md"

# Check for related claims
grep -r "topic keyword" meta/claims/ --include="*.md"

# Review contradictions if any
grep -r "topic keyword" meta/contradictions/ --include="*.md"
```

**Read each source fully:**
- Core mechanisms
- Predictions/implications
- Evidence base
- Assumptions
- Scope
- Origin labels

### Step 2: Identify Unification Structure

**Questions to answer:**
1. What's the higher-level pattern that encompasses all sources?
2. Which elements are truly shared vs superficially similar?
3. What's the organizing principle for unification?
4. What simplifying assumptions enable synthesis?

**Common unification patterns:**
- **Scale unification:** Micro and macro views of same process
- **Abstraction layers:** Specific instances of general principle
- **Temporal stages:** Sequential steps in larger process
- **Complementary aspects:** Different facets of multidimensional phenomenon
- **Conditional variants:** Special cases of general model

### Step 3: Draft Synthesis

**Create new file:** `meta/models/YYYY-MM-DD_[synthesis-topic].md` (or `meta/maps/` if broad)

**Status:** Draft (must be approved before Active)

**Origin:** Default to Co-created (unless clearly user-led or Fermi-led)

**Origin Detail section:**
```markdown
**Origin:** Co-created

**Origin detail:** Synthesis proposed by Fermi (‹model›) on YYYY-MM-DD,
synthesizing:
- [Model A] (Origin: [UserName], YYYY-MM-DD)
- [Model B] (Origin: Fermi (‹model›), YYYY-MM-DD)
- [Claim C] (Origin: Co-created, YYYY-MM-DD)

Unification principle: [How they were unified]
Simplifying assumptions: [Made explicit below]
```

**Structure of synthesis:**

```markdown
# Model: [Unified Topic]

**Origin:** Co-created
**Status:** Draft

## Summary

[Integrated view that encompasses source models]

## Core Mechanisms (Unified)

[Mechanisms from sources, organized by unification principle]

### From [Source A] (Origin: [label])
[Mechanism with attribution]

### From [Source B] (Origin: [label])
[Mechanism with attribution]

### Unified Insight
[What emerges from synthesis]

## Simplifying Assumptions (Explicit)

[Assumptions required for this synthesis to work]

## Evidence Base (Combined)

[All sources cited with origin labels]

## What This Synthesis Gains

[Benefits of unified view - explanatory power, predictions, simplification]

## What This Synthesis Loses

[Nuances or distinctions that are reduced - must be honest]

## Relationship to Source Models

**Synthesizes:**
- meta/models/[source-A].md (Origin: [label])
- meta/models/[source-B].md (Origin: [label])

**If approved, source models will:**
- Status → Superseded by synthesis
- Remain accessible with preserved provenance
- Link to this synthesis

## Provenance

- **Created:** YYYY-MM-DD
- **Origin detail:** [Full attribution as above]
- **Status:** Draft (awaiting approval)
```

### Step 4: Present to User for Review

**Format:**
```
**Synthesis Draft Created**

I've drafted a synthesis of [models A, B, C] into a unified view:

File: meta/models/YYYY-MM-DD_[synthesis-topic].md
Origin: Co-created (combines your models with my structural integration)
Status: Draft

**What it unifies:**
- [Source A] (Origin: [label]) - [Brief description]
- [Source B] (Origin: [label]) - [Brief description]

**Unification principle:**
[How they're unified - e.g., "These are three scale levels of the same mechanism"]

**Gains:**
- [Benefit 1]
- [Benefit 2]

**Loses:**
- [Nuance that's reduced]

**Simplifying assumptions:**
1. [Assumption 1]
2. [Assumption 2]

Please review: meta/models/YYYY-MM-DD_[synthesis-topic].md

Should I:
1. Activate this synthesis (Status → Active, source models → Superseded)?
2. Revise based on your feedback?
3. Reject (delete draft, keep models coexisting)?
```

---

## Approval Process

### User Approves

1. **Update synthesis file:**
   - Status: Draft → Active
   - Add approval date to provenance

2. **Update source files:**
   - Status → Superseded
   - Add "Superseded by: [synthesis link]"
   - Add "Superseded on: YYYY-MM-DD"
   - Preserve full content (don't delete)

3. **Update or create timeline (if applicable):**
   - Add synthesis event
   - Note: "Synthesized from multiple sources"
   - Driver: Unification

4. **Update link graph:**
   - Create synthesis links
   - Mark source models as superseded but linked

5. **Update knowledge_map:**
   - Replace source models with synthesis in overview
   - Note consolidation

### User Requests Revisions

**Iterate:**
1. Get specific feedback
2. Revise synthesis
3. Re-present for approval
4. Status remains: Draft

### User Rejects

1. **Delete synthesis draft** or move to rejected folder
2. **Keep source models coexisting**
3. **Document rejection reason** in coexisting-models-strategy.md:
   ```markdown
   **Rejected synthesis attempt:**
   - Date: YYYY-MM-DD
   - Topic: [topic]
   - Reason: [Why rejected - e.g., "Forced unification lost critical distinction"]
   ```
4. **Learn from rejection** - Add to learning/connection_feedback.md

---

## Synthesis Types

### Model Synthesis

**Unifying multiple mechanistic models:**
- Identify shared mechanisms
- Organize by scale, stage, or aspect
- Create higher-level integrated model
- Attribute components to sources

**Example:** Three models of knowledge capture → Unified KB architecture model

---

### Claim Consolidation

**Organizing scattered claims:**
- Group related claims
- Identify organizing principle
- Create map or model that structures them
- Maintain individual claim attributions

**Example:** Five claims about epistemic discipline → Integrated epistemic framework map

---

### Domain Integration

**Cross-domain synthesis:**
- Identify structural similarity across domains
- Extract general principle
- Show domain-specific instances
- Reveal scale-crossing or transferable insights

**Example:** Pattern in biology + pattern in sociology → General mechanism model

---

### Contradiction Resolution via Synthesis

**Unifying apparently conflicting views:**
- Identify hidden assumptions causing conflict
- Find higher-level view that encompasses both
- Show how each is special case or conditional variant
- Resolve tension through unification

**Example:** "X causes Y" vs "Z causes Y" → "Y is caused by interaction of X and Z"

---

## Integration with Contradictions

### When Synthesis Resolves Contradiction

1. **Update contradiction entry:**
   - Status: Open → Resolved via synthesis
   - Add resolution section linking to synthesis
   - Date resolved

2. **Update synthesis provenance:**
   - Note: "Resolves contradiction [link]"
   - Explain how synthesis resolves tension

3. **Update timeline if exists:**
   - Add entry for contradiction resolution via synthesis

---

## Failed Synthesis Learning

### When Synthesis Doesn't Work

**Document in learning artifacts:**

```markdown
## YYYY-MM-DD: Failed Synthesis Attempt - [Topic]

**Attempted to synthesize:**
- [Source A]
- [Source B]

**Why it failed:**
[Reason - incompatible assumptions, forced unification, lost critical distinction]

**Lesson learned:**
[What this reveals about when NOT to synthesize]

**Action:**
Sources remain coexisting with clarified boundaries
```

**Update suppression memory:**
- Don't propose similar syntheses in future
- Recognize this pattern as "preserve distinction, don't unify"

---

## Examples

### Example 1: Successful Model Synthesis

**Scenario:** Three KB architecture models exist (raw/meta split, origin tracking, retrieval)

**Synthesis proposal:**
```
I notice three models describing different aspects of KB architecture:
1. Two-layer architecture (raw/meta split)
2. Origin attribution as metadata
3. Index-first retrieval strategy

These could be synthesized into a unified "Fermi KB Architecture" model that
shows how these components work together as a coherent system.

Unification principle: These are complementary subsystems of one architecture
- Raw/meta split enables provenance (needed for origin tracking)
- Origin tracking requires retrieval (to cite sources)
- Retrieval uses indices (built from meta layer)

Would you like me to draft this synthesis?
```

**User approves → Create synthesis**

---

### Example 2: Synthesis Rejected (Distinction Matters)

**Scenario:** Two coexisting models explain same phenomenon differently

**Synthesis proposal:**
```
Models A and B could potentially be unified...
```

**User response:** "No, these operate at different scales and the distinction matters. Keep them separate with clear scope boundaries."

**Action:**
- Delete synthesis draft
- Update both models with explicit scope sections
- Document in coexisting-models-strategy.md why distinction preserved
- Learn: Don't propose scale-crossing syntheses for this domain

---

### Example 3: Synthesis with Revisions

**Initial draft:** Too abstract, loses concrete mechanisms

**User feedback:** "Needs more detail from source models, too high-level"

**Revision:** Add subsections preserving source mechanisms with attribution

**User approves revised version**

---

## Epistemic Discipline Checklist

Before proposing synthesis:

- [ ] Confidence in coherence is genuinely high (not forced)
- [ ] Simplifying assumptions identified and explicit
- [ ] Unification principle is clear and justified
- [ ] Source models cited with origin labels
- [ ] Benefits of synthesis articulated
- [ ] Losses/reductions acknowledged honestly
- [ ] Status set to Draft initially
- [ ] User approval required before activation
- [ ] Source models preserved (not deleted) when superseded
- [ ] Provenance fully documented

After synthesis approved:

- [ ] Status updated to Active
- [ ] Source models marked Superseded with links
- [ ] Timeline updated if applicable
- [ ] Link graph updated
- [ ] Knowledge map reflects synthesis
- [ ] All origin attributions preserved

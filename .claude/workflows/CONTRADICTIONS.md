# Workflow: Contradiction Detection and Documentation

**Purpose:** Detect, document, and track tensions between claims or models in the KB

---

## When to Detect Contradictions

### During Ingest

At the end of every ingest (chat save or markdown), check for contradictions:

1. **Explicit contradictions** - User says "this contradicts what I said before"
2. **Detected tensions** - New claim/model conflicts with existing KB content
3. **Scope ambiguity** - Two claims/models overlap but with unclear boundaries

### During Query

When answering queries, surface contradictions if:
- Multiple conflicting claims/models apply to the query topic
- User asks "what are the tensions around [topic]?"
- Contradictory evidence appears in search results

### Proactive Scanning (Manual for now)

Periodically (when KB reaches significant size):
- Scan for claims with same keywords but different conclusions
- Check models on similar topics for conflicting mechanisms
- Review superseded items for unresolved tensions

---

## Detection Process

### Step 1: Identify Potential Tension

**Triggers:**
- New claim contradicts existing claim on same topic
- New model predicts opposite of existing model
- Same phenomenon explained by incompatible mechanisms
- Scope overlap with unclear boundaries

**Search strategy:**
```bash
# Find claims on similar topic
grep -r "keyword" meta/claims/ --include="*.md"

# Check for conflicting status/predictions
grep -r "keyword" meta/models/ --include="*.md"
```

### Step 2: Assess Nature of Tension

**Questions to answer:**
1. Is this a genuine logical contradiction or just different scopes?
2. Do the items have different origins ([UserName] vs Fermi vs Co-created)?
3. Are they from different time periods (evolution vs contradiction)?
4. Can they coexist with clarified boundaries?

**Tension types:**
- **Logical contradiction:** A and ~A can't both be true
- **Empirical conflict:** Different predictions for same phenomenon
- **Scope ambiguity:** Unclear where each applies
- **Assumption clash:** Compatible if different assumptions, but assumptions conflict

### Step 3: User Confirmation

Before creating contradiction entry, confirm with user:

**Format:**
```
I notice a potential tension:

**Item A** (Origin: [UserName], 2025-11):
[Statement A]
Source: meta/claims/[file].md

**Item B** (Origin: [UserName], 2026-01):
[Statement B]
Source: meta/claims/[file].md

**Nature:** [Type of tension]

This looks like [logical contradiction | empirical conflict | scope ambiguity].

Should I:
1. Document this as a contradiction to resolve later?
2. Clarify scope boundaries so they coexist?
3. Update one to supersede the other?
4. Leave as-is (not actually contradictory)?
```

---

## Documentation Process

### Step 1: Create Contradiction Entry

**File naming:** `meta/contradictions/YYYY-MM-DD_[brief-slug].md`

**Use template:** `meta/contradictions/_TEMPLATE.md`

**Fill in:**
- Item A statement and origin
- Item B statement and origin
- Nature of tension (precise description)
- Type (logical contradiction, empirical conflict, etc.)
- Possible resolution approaches
- Status: Open

### Step 2: Update Source Files

In each conflicting claim/model file, add to "Related" or "Tensions" section:

```markdown
**Conflicts with:**
- meta/contradictions/YYYY-MM-DD_[slug].md - [Brief description of tension]
```

### Step 3: Update Link Graph

Add to `index/link_graph.md`:

```markdown
### Contradictions

`meta/claims/[file-A].md` <--contradicts--> `meta/claims/[file-B].md`
  Documented in: meta/contradictions/YYYY-MM-DD_[slug].md
  Nature: [Type]
  Detected: YYYY-MM-DD
```

### Step 4: Update Views

Add to `views/persistent/connection_history.md` if this is a significant tension:

```markdown
### YYYY-MM-DD: [Contradiction Title]
**Type:** Contradiction detection
**Elements:**
- [Item A] (Origin: [label], [date])
- [Item B] (Origin: [label], [date])
**Insight:** [What this tension reveals about the domain]
**Origin:** [Who detected - user if they pointed out, Fermi if auto-detected, Co-created if collaborative]
**Status:** Open
```

---

## Resolution Process

### When to Resolve

- User explicitly chooses resolution approach
- New evidence clearly favors one over the other
- Scope clarification makes coexistence unambiguous
- One item is determined to be incorrect

### Resolution Options

#### 1. Supersession (One Replaces Other)

**Process:**
1. Update superseded item: Status → Superseded
2. Add "Superseded by" link to newer item
3. Update contradiction entry: Status → Resolved
4. Add resolution section explaining decision
5. If timeline exists, add supersession event

#### 2. Scope Clarification (Coexist with Boundaries)

**Process:**
1. Update both items with explicit scope sections
2. Clarify: "Applies when [conditions], not when [other conditions]"
3. Update contradiction entry: Status → Coexisting
4. Add resolution explaining boundary
5. Update coexisting-models-strategy map if relevant

#### 3. Synthesis (Unify into New Model)

**Process:**
1. Create new synthesized claim/model
2. Reference contradiction in new item's provenance
3. Update old items: Status → Superseded by synthesis
4. Update contradiction entry: Status → Resolved via synthesis
5. Add resolution linking to synthesis

#### 4. Evidence Gap (Leave Open, Flag Uncertainty)

**Process:**
1. Update contradiction entry with evidence needed
2. Add to open questions in both source items
3. Status remains: Open
4. Note in knowledge_map.md as active tension

---

## Contradiction Query Responses

When user asks about contradictory topic:

**Format:**
```
I found contradictory information on [topic]:

**Position A** (Origin: [UserName], 2025-11):
[Statement]
Source: meta/claims/[file-A].md

**Position B** (Origin: [UserName], 2026-01):
[Statement]
Source: meta/claims/[file-B].md

**Documented tension:** meta/contradictions/[file].md

**Nature:** [Type of contradiction]

**Possible resolutions:**
1. [Approach 1]
2. [Approach 2]

**Status:** Open

Would you like to:
- Clarify which applies in this context?
- Resolve the contradiction now?
- Proceed with one interpretation?
```

---

## Automated Detection Rules

### High-Confidence Contradiction Signals

Auto-detect and flag (but confirm before documenting):

1. **Negation patterns:**
   - "X is Y" vs "X is not Y"
   - "X causes Y" vs "X does not cause Y"

2. **Conflicting predictions:**
   - Model A predicts increase, Model B predicts decrease
   - Same phenomenon, opposite outcomes

3. **Incompatible mechanisms:**
   - Two models explaining same thing with mutually exclusive mechanisms

### Detection Frequency

- **During every ingest:** Check new claims/models against existing
- **During synthesis queries:** Surface contradictions if multiple sources conflict
- **Manual review:** When KB reaches 50+ claims or 20+ models

---

## Examples

### Example 1: Logical Contradiction Detected

**During ingest:**
```
New claim extracted: "Two-layer architecture prevents interpretation drift"
(Origin: Co-created, 2026-01-22)

Checking existing claims... No contradictions detected.
```

### Example 2: Empirical Conflict Detected

**Scenario:** New model predicts opposite of existing model

```
Potential contradiction detected:

**Model A** (Origin: [UserName], 2025-08):
"Origin attribution increases cognitive load"

**New claim being ingested:**
"Origin attribution doesn't add excessive cognitive load" (assumption in new model)

Nature: Empirical conflict

Should I document this as a contradiction to track?
[User confirms]

Created: meta/contradictions/2026-01-22_origin-attribution-cognitive-load.md
Status: Open
```

### Example 3: Scope Ambiguity Resolved

**User query:** "Does origin attribution work for all ideas?"

**Response:**
```
There's clarified scope on this:

Origin attribution (Origin: Co-created, 2026-01-22) applies to:
- Claims, models, syntheses, major hypotheses in meta layer
- Non-trivial ideas that could be right or wrong

Does NOT apply to:
- Procedural notes and documentation
- Git commits
- Generated index files
- Trivial organization decisions

This scope was clarified when the model was created to avoid ambiguity.

Source: meta/models/2026-01-22_origin-attribution-as-epistemic-metadata.md
```

---

## Integration with Other Workflows

### During INGEST_CHAT.md or INGEST_MARKDOWN.md

After "Step 6: Surface Non-Trivial Connections", add:

**Step 6b: Check for Contradictions**
- Search for claims/models on same keywords
- Assess for tensions
- Confirm with user if detected
- Create contradiction entry if confirmed

### During QUERY.md

In "Step 3: Answer Assembly", add:

**If conflicting sources found:**
- Note contradiction exists
- Present both sides with origin labels
- Link to contradiction entry if documented
- Ask which interpretation user wants

---

## Epistemic Discipline Checklist

Before documenting contradiction:

- [ ] Both items cited with origin labels
- [ ] Nature of tension precisely described
- [ ] Type correctly identified (logical, empirical, scope, assumption)
- [ ] Possible resolutions listed (not forcing one)
- [ ] Status set appropriately (Open/Resolved/Coexisting)
- [ ] Links updated in both source files
- [ ] Link graph updated
- [ ] User confirmed contradiction is real (not just different scope)

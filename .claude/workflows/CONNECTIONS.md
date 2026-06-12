# Workflow: Non-Trivial Connection Detection

**Purpose:** Surface meaningful connections across KB content that add explanatory or generative value

**Principle:** Under-surface rather than over-surface (preserve trust through quality filter)

---

## What Counts as Non-Trivial

### Surface When Connection Reveals

1. **Shared mathematical or structural form** across topic-distinct domains
   - Example: "Your model of X has the same three-stage structure as your model of Y"
   - Not trivial: Reveals general pattern

2. **Contradictions or tensions** with prior beliefs
   - Example: "This new claim contradicts your 2025 position on X"
   - Not trivial: Prompts resolution or coexistence clarification

3. **Scale-crossing links** (micro ↔ macro, mechanistic ↔ phenomenological)
   - Example: "This molecular mechanism explains the population pattern you noted"
   - Not trivial: Bridges levels of abstraction

4. **Implicit assumptions reused** across different contexts
   - Example: "Both models assume X, but in different domains"
   - Not trivial: Reveals hidden commonality

---

## Do NOT Surface

Connections that are merely:
- **Topical** - "Both mention data" (too generic)
- **Recent** - "You just talked about X yesterday" (recency bias)
- **Associative** - "X reminds me of Y" (no structure)
- **Superficially analogous** - "Like X is to Y" without mechanism

---

## Detection Triggers

### During Ingest (Automatic Check)

After extracting new claim/model:

1. **Search for similar keywords** in existing meta layer
2. **Check for structural patterns** (mechanisms, stages, relationships)
3. **Look for contradictions** (same topic, different conclusions)
4. **Scan for assumptions** (are same assumptions used elsewhere?)

**Process:**
```bash
# Get keywords from new content
keywords=[extract from new claim/model]

# Search existing meta
grep -r "keyword1" meta/ --include="*.md"
grep -r "keyword2" meta/ --include="*.md"

# Check for structural similarity
[analyze matching results for patterns]

# Check for contradictions
[compare positions on same topic]
```

### During Query (Automatic Check)

When answering queries:

1. **Check if query topic has related but non-obvious links**
2. **Look for cross-domain instances** of queried pattern
3. **Check for scale-crossing explanations**

**Surface in query response if non-trivial**

### Periodic Scanning (Manual Trigger)

When KB reaches significant size (100+ files):

```
User: "Scan for connections"
```

**Process:**
1. Group by tags (find cross-tag patterns)
2. Group by mechanisms (find structural similarities)
3. Check for unresolved contradictions
4. Look for synthesis opportunities

---

## Assessment Process

### Step 1: Detect Potential Connection

**Pattern matching:**
- Structural similarity (same mechanism pattern)
- Contradiction (incompatible positions on same topic)
- Scale crossing (different levels of abstraction, same phenomenon)
- Assumption sharing (same assumption in different contexts)

### Step 2: Evaluate Non-Triviality

**Ask:**
1. Does this add explanatory power? (reveals why or how)
2. Does this enable predictions? (what else follows from pattern)
3. Does this resolve confusion? (clarifies apparent contradiction)
4. Is this non-obvious? (wouldn't be noticed without pointing out)

**If yes to any:** Consider surfacing
**If no to all:** Suppress (too trivial)

### Step 3: Apply Quality Filter

**Have similar connections been flagged as unhelpful?**

Use judgment based on prior feedback patterns in conversation history.

**If this pattern type has been consistently unhelpful:** Suppress

**If uncertain:** Surface but keep concise

---

## Surfacing Format

### Inline (During Ingest or Query)

**Minimal explanation (default):**
```
**Connection detected:**
This [new model] structurally similar to [existing model] (Origin: [UserName], 2025-08)
→ Both use three-stage processing: [stage 1] → [stage 2] → [stage 3]
```

**With brief rationale:**
```
**Connection detected:**
[New claim on X] tensions with [Prior claim on X] (Origin: [UserName], 2024-03)
→ Prior: "X causes Y directly"
→ Now: "X and Z together cause Y"
→ Recommend: Reconcile or update timeline
```

### Documented (If Significant)

Add to `views/persistent/connection_history.md`:

```markdown
### YYYY-MM-DD: [Connection Title]

**Type:** [Cross-domain | Scale-crossing | Contradiction | Structural similarity]

**Elements:**
- [Element A] (Origin: [label], [date])
  Source: meta/[type]/[file].md
- [Element B] (Origin: [label], [date])
  Source: meta/[type]/[file].md

**Connection:**
[What the connection reveals]

**Insight:**
[What new understanding this enables]

**Origin:** [Fermi (‹model›) | Co-created if discussed]

**Status:** [Active | Superseded | Exploratory]

**Feedback:** [Space for user feedback]
```

---

## Connection Types

### Type 1: Structural Similarity (Cross-Domain)

**Pattern:** Same structure in different domains

**Example:**
```
Connection detected:

Your "two-layer architecture" (raw/meta split for knowledge)
structurally similar to
"testing pyramid" (unit/integration split for code quality)

Both use:
- Fidelity layer (raw/unit tests) for ground truth
- Interpretive layer (meta/integration tests) for meaning
- Backlinks for traceability

Cross-domain pattern: Dual-layer with fidelity + interpretation
```

**When to surface:** Clear structural mapping exists

**When to suppress:** Only keyword overlap, no structural match

---

### Type 2: Contradiction Detection

**Pattern:** Incompatible positions on same topic

**Example:**
```
Connection detected:

Tension between positions on [topic]:

**Position A** (Origin: [UserName], 2025-03):
"X is sufficient for Y"
Source: meta/claims/2025-03-15_x-sufficiency.md

**Position B** (now ingested):
"X is necessary but not sufficient for Y"

Recommend: Create timeline or contradiction entry
```

**When to surface:** Genuine logical tension

**When to suppress:** Different scopes (both can be true in context)

---

### Type 3: Scale-Crossing Link

**Pattern:** Micro explains macro, or macro contextualizes micro

**Example:**
```
Connection detected:

This mechanistic model (molecular level, Origin: [UserName], ingested from Smith)
explains
Prior phenomenological observation (population level, Origin: [UserName], 2025-06)

Mechanism: [X] → [Y] → [Z] at molecular level
Predicts: Population-level pattern of [Z] accumulation

Scale-crossing insight: Micro mechanism → Macro outcome
```

**When to surface:** Clear causal or explanatory link across scales

**When to suppress:** Both mention scales but no explanatory connection

---

### Type 4: Implicit Assumption Sharing

**Pattern:** Same assumption used in multiple models

**Example:**
```
Connection detected:

Both your models on [domain A] and [domain B] assume:
"Feedback loops stabilize over time"

But this assumption not tested in either domain.

If assumption fails: Both models would need revision

Recommend: Make this shared assumption explicit and track
```

**When to surface:** Shared assumption is load-bearing and not obvious

**When to suppress:** Assumption is trivial or obviously shared

---

## Feedback Integration

### Collect Feedback

After surfacing connection, note user response:

**Positive signals:**
- "That's useful"
- "Good catch"
- "That connection was helpful"
- User acts on connection (creates synthesis, resolves contradiction)

**Negative signals:**
- "That was trivial"
- "I already knew that"
- "That connection was noise"
- "That's not actually related"

**Neutral:**
- No response (connection acknowledged but not acted on)

### Record Significant Connections

Interesting cross-domain connections discovered during ingest or query are
captured in meta entries (claims, models, maps) with appropriate cross-references
and `index/link_graph.md` updates. No separate feedback log is needed — the
connection's value is demonstrated by whether it gets referenced in future work.

**User feedback:** [Useful | Trivial | Noise | Already knew]

**Action taken:** [Continue | Suppress similar | Refine detection]

**Pattern learned:**
[What this teaches about connection quality]
```

### Update Detection Rules

**If "useful" feedback:**
- Look for more connections of this type
- Lower threshold slightly for this pattern

**If "trivial" or "noise" feedback:**
- Suppress this type of connection
- Raise threshold for this pattern
- Document in suppression memory

---

## Suppression Memory

### Track Unhelpful Patterns

Suppression is judgment-based rather than log-based. Known unhelpful patterns:
**Learned:** YYYY-MM-DD
**Confidence:** High | Medium | Low

[If low confidence, may resurface after N suppressions]
```

**Example:**
```markdown
### Suppress: Topical similarity without structural connection
**Reason:** "Both mention 'data'" is too generic, no explanatory value
**Examples:**
- 2026-01-22: Connected data model and dataset → "Trivial"
- 2026-01-23: Connected data structure and data flow → "Obvious"
**Learned:** 2026-01-23
**Confidence:** High (suppress permanently)
```

---

## Conservative Bias

**Default stance:** Under-surface rather than over-surface

**Rationale:**
- Trust preserved by quality filtering
- Better to miss occasional connection than flood with noise
- User can always ask "what connections am I missing?"

**In practice:**
- Only surface high-confidence non-trivial connections
- When uncertain, lean toward suppression
- Require clear explanatory value before surfacing

---

## User-Initiated Connection Search

**User can request:**
```
"What connections exist for [topic]?"
"Scan for cross-domain patterns"
"Are there contradictions I should resolve?"
```

**Process:**
1. Search meta layer for topic
2. Apply connection detection logic
3. Surface ALL non-trivial connections found (not just highest confidence)
4. Organize by type (structural, contradiction, scale-crossing, assumption)
5. Present with confidence levels if helpful

---

## Examples

### Example 1: Structural Similarity Surfaced

**During ingest of new model:**
```
[Normal ingest processing...]

**Connection detected:**
This three-stage mechanism (Origin: [UserName], from Smith et al.)
→ Structurally similar to your two-layer architecture
→ Both have: input preservation, transformation, output retrieval

Potential insight: General pattern of staged processing with fidelity layer

This connection logged in views/persistent/connection_history.md
```

**User response:** "Interesting, that's a good pattern to track"

**Feedback recorded:** Useful → Continue surfacing structural similarities

---

### Example 2: Trivial Connection Suppressed

**Internal detection (not surfaced):**
```
Potential connection:
- New note mentions "architecture"
- Existing model also mentions "architecture"

Assessment: Topical overlap only, no structural connection
Confidence in non-triviality: Low

Action: Suppress (don't surface)
```

---

### Example 3: Contradiction Surfaced

**During ingest:**
```
[Normal ingest processing...]

**Connection detected (tension):**
New claim: "Origin attribution doesn't add cognitive load"
Prior claim: "Origin attribution increases cognitive load" (assumption from Model X)

Source: meta/models/2025-11-10_cognitive-load-model.md

This is a contradiction on cognitive load assessment.

Recommend: Create contradiction entry or clarify scope
```

**User response:** "Good catch, let's clarify - it's high load initially, low after learning"

**Feedback recorded:** Useful → Continue surfacing contradictions

---

## Integration with Other Workflows

### INGEST_CHAT / INGEST_MARKDOWN

After Step 6 (index updates), add:

**Step 6b: Check for Non-Trivial Connections**
- Run connection detection on new content
- Assess non-triviality
- Check suppression memory
- Surface if high confidence
- Log if significant

### QUERY

During answer assembly, add:

**Check for Related Connections**
- If query touches topics with non-obvious links, surface
- Only add if enhances answer (not tangential)

---

## Epistemic Discipline Checklist

Before surfacing connection:

- [ ] Connection adds explanatory or generative value (not just similarity)
- [ ] Non-obvious (wouldn't be noticed without pointing out)
- [ ] Not suppressed in learning memory
- [ ] Both elements cited with origin labels
- [ ] Connection type clearly identified
- [ ] Brief rationale provided
- [ ] User can easily provide feedback

After surfacing connection:

- [ ] User feedback noted (useful, trivial, noise)
- [ ] Learning log updated
- [ ] Suppression rules updated if needed
- [ ] Significant connections added to connection_history.md

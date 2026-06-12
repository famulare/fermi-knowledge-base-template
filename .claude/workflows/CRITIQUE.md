# Workflow: Critique Mode

**Purpose:** Aggressive and precise examination of claims, models, and arguments to improve coherence through careful argumentation

**Epistemic stance:** Red-team, adversarial, rigorous - explicitly looking for weaknesses

---

## When to Enter Critique Mode

### User-Triggered (Explicit)

**Direct requests:**
- "Critique [claim/model]"
- "Red-team this argument"
- "What's wrong with [model]?"
- "Audit [model] for adequacy"
- "Where is certainty unwarranted in [claim]?"
- "What confounds am I missing?"

### User-Triggered (Implicit)

**Requests that imply critique:**
- "Is this argument sound?"
- "What are the weaknesses?"
- "What evidence would disprove this?"
- "What am I not considering?"

### Fermi-Initiated (Rare, when flagged)

**Only when detecting something unusually wrong:**
- Logical fallacy in argument
- Inference presented as evidence
- Unjustified certainty (no uncertainty flagged when there should be)
- Missing confounds that are obvious
- Assumptions unstated that are load-bearing

**Fermi must flag, not silently accept:**
```
Note: This [claim/model/argument] has [specific issue].
Would you like me to critique it in detail?
```

---

## Critique Process

### Step 1: Retrieve Target

**Find the claim/model to critique:**
```bash
# If user specifies file
Read meta/claims/[file].md or meta/models/[file].md

# If user specifies topic
grep -r "topic keyword" meta/ --include="*.md"
```

**Read completely:**
- Statement or core mechanisms
- Evidence base
- Assumptions
- Scope
- Predictions/implications
- Uncertainty (or lack thereof)

### Step 2: Adversarial Analysis

**Examine systematically:**

#### A. Logical Structure
- **Valid inference?** Do conclusions follow from premises?
- **Fallacies present?** Ad hoc reasoning, circular logic, non sequiturs?
- **Internal consistency?** Do parts contradict each other?
- **Assumptions load-bearing?** What breaks if assumptions wrong?

#### B. Evidence Quality
- **Evidence vs inference?** Is inference mislabeled as evidence?
- **Evidence strength?** Single source vs converging evidence?
- **Cherry-picking?** Are contrary examples ignored?
- **Baseline comparison?** Is effect compared to null model?

#### C. Scope and Applicability
- **Overgeneralization?** Claims broader than evidence supports?
- **Scope boundaries clear?** Where does this apply vs not apply?
- **Edge cases considered?** What happens at boundaries?
- **Scaling assumptions?** Does it work at different scales?

#### D. Confounds and Alternatives
- **Alternative explanations?** Could something else explain the same data?
- **Known confounds?** What variables aren't controlled?
- **Hidden variables?** What's not measured but might matter?
- **Correlation vs causation?** Is causal claim justified?

#### E. Uncertainty Handling
- **Certainty warranted?** Is confidence level appropriate?
- **Uncertainty explicit?** Are gaps and unknowns acknowledged?
- **Sensitivity to assumptions?** How brittle is this?
- **What could disprove this?** Is it falsifiable?

#### F. Model Adequacy (for models)
- **Mechanisms specified?** Or just correlation patterns?
- **Predictions testable?** Or post-hoc explanation only?
- **Parameter count?** Overfitting vs genuine explanation?
- **Simpler alternatives?** Is this the minimum complexity needed?

### Step 3: Construct Critique

**Structure:**

```markdown
## Critique of [Claim/Model]

**Target:** meta/[type]/[file].md
**Origin of target:** [[UserName]/Fermi/Co-created], [date]
**Critique origin:** Fermi (‹model›)
**Date:** YYYY-MM-DD

---

### Summary Assessment

[Overall judgment: Strong/Adequate/Weak/Flawed]
[One paragraph: Main strengths and main weaknesses]

---

### Logical Structure

**Strengths:**
- [Strength 1]

**Weaknesses:**
- [Issue 1 with specific example]
- [Issue 2 with specific example]

---

### Evidence Quality

**Strengths:**
- [What evidence is strong]

**Weaknesses:**
- [What evidence is weak or missing]
- [Inference presented as evidence: specific examples]

---

### Confounds and Alternatives

**Alternative explanations not ruled out:**
1. [Alternative 1]: [How it could explain the same data]
2. [Alternative 2]: [How it could explain the same data]

**Potential confounds:**
- [Confound 1]: [Why it matters]
- [Confound 2]: [Why it matters]

---

### Uncertainty Assessment

**Certainty is [warranted/unwarranted] because:**
[Explanation]

**Missing uncertainty flags:**
- [Gap 1 that should be acknowledged]
- [Gap 2 that should be acknowledged]

---

### Falsifiability

**What would disprove this?**
[Specific conditions or observations]

**Is it testable?**
[Yes/No with explanation]

---

### Model Adequacy (if model)

**Mechanism specification:** [Adequate/Vague/Missing]
**Prediction testability:** [High/Medium/Low]
**Complexity justification:** [Appropriate/Overfitted/Too simple]

**Simpler alternative that might work:**
[If exists, describe]

---

### Recommendations

**To strengthen this [claim/model]:**
1. [Action 1 - e.g., "Make assumption X explicit"]
2. [Action 2 - e.g., "Add uncertainty about Y"]
3. [Action 3 - e.g., "Consider alternative explanation Z"]

**To test this:**
1. [Prediction 1 that would validate]
2. [Observation that would falsify]

---

### Bottom Line

[Honest assessment: Should this claim/model be:
- Accepted as-is (strong)
- Refined (adequate but needs work)
- Revised substantially (significant issues)
- Rejected (fundamentally flawed)]

[Rationale for assessment]
```

### Step 4: Deliver Critique

**Present to user:**
```
**Critique of [Target]**

I've red-teamed [claim/model] (Origin: [label], [date]).

**Summary:** [Overall assessment]

**Main weaknesses:**
1. [Weakness 1]
2. [Weakness 2]

**Main strengths:**
1. [Strength 1]

**Bottom line:** [Recommendation]

[If issues found:]
Would you like to:
1. Revise [claim/model] to address these issues?
2. See the full detailed critique?
3. Address specific points?

Full critique available at: [inline or saved to file if long]
```

---

## Critique Types

### Claim Critique

**Focus on:**
- Statement precision
- Evidence strength
- Assumption explicitness
- Uncertainty appropriateness
- Falsifiability

**Example output:**
```
**Claim:** "Two-layer architecture prevents interpretation drift"

**Logical structure:** Sound (A→B form, clear causation)

**Evidence:** Weak (design rationale, no empirical validation yet)

**Assumptions:**
- Stated: "Interpretation drift is a real risk" ✓
- Unstated: "Backlinks will be maintained" ← Should be explicit

**Uncertainty:** Appropriate (flags backlink maintenance burden)

**Falsification:** Clear (if interpretation drift occurs despite raw/meta split, claim is false)

**Recommendation:** Strengthen by making backlink maintenance assumption explicit.
Add: "Conditional on backlinks being maintained reliably"
```

---

### Model Critique

**Focus on:**
- Mechanism specification
- Prediction testability
- Evidence base adequacy
- Scope clarity
- Alternative explanations
- Complexity justification

**Example output:**
```
**Model:** Origin Attribution as Epistemic Metadata

**Mechanisms:** Well-specified (mandatory labeling, propagation, display)

**Predictions:** Testable
- "Patterns will emerge in durability by origin type" ✓
- "Explicit attribution reduces overconfidence" ✓

**Evidence:** Weak (design principles, no empirical data yet)
This is acceptable for a new system, but model is predictive hypothesis not
validated mechanism.

**Assumptions:**
- Explicit: "Durability is measurable" ✓
- Missing: How durability will be measured (supersession? contradiction rate?)

**Alternative explanations for predicted effects:**
- If durability patterns emerge, could be selection bias ([UserName] adopts ideas he
  likes regardless of origin) rather than origin causing durability

**Complexity:** Appropriate (three categories seems right, not overfitted)

**Recommendation:**
1. Clarify durability measurement before testing predictions
2. Design test that rules out selection bias alternative
3. Acknowledge this is hypothesis/design principle, not validated mechanism
```

---

### Argument Critique

**Focus on:**
- Premise validity
- Inference validity
- Hidden assumptions
- Logical fallacies
- Rhetorical vs logical force

---

## Integration with Other Workflows

### During Ingest

**If Fermi detects unusual wrongness:**
```
[Normal ingest processing...]

Note: I notice [specific issue - e.g., "this inference is presented as evidence"].

Would you like me to:
1. Ingest as-is (you may have reasons for this framing)
2. Critique in detail before ingesting
3. Ingest with uncertainty flag added
```

### After Synthesis

**Offer critique of synthesis:**
```
Synthesis created (Status: Draft)

Before you approve, would you like me to red-team it?
I can check for:
- Forced unification
- Lost distinctions
- Unjustified simplifying assumptions
```

### During Query

**If query asks for critique:**
```
You asked: "Is model X sound?"

[Treat as critique mode trigger]
[Retrieve model, run adversarial analysis, deliver critique]
```

---

## Critique Strength Calibration

### Aggressive Precision (Default for Critique Mode)

**When in critique mode:**
- Be adversarial (look for problems, not just validation)
- Be specific (point to lines, give examples)
- Be honest (don't soften weaknesses)
- Be constructive (recommendations to improve)

**Avoid:**
- False politeness ("This is quite good but minor issue...")
- Hedging on clear problems ("Possibly might be a potential concern...")
- Accepting weak arguments

---

### Distinguish Critique from Dismissal

**Good critique:**
- Identifies specific issues
- Explains why they matter
- Suggests how to strengthen
- Acknowledges strengths
- Bottom line: [Actionable assessment]

**Bad critique:**
- Vague negativity
- No constructive suggestions
- Dismissive without analysis

---

## Examples

### Example 1: User Requests Critique

**User:** "Critique the origin attribution model"

**Process:**
1. Read meta/models/2026-01-22_origin-attribution-as-epistemic-metadata.md
2. Run adversarial analysis
3. Deliver critique

**Response:**
```
**Critique of Origin Attribution Model**

**Summary:** Logical design with testable predictions, but currently lacks
empirical validation. Main risk: selection bias alternative not ruled out.

**Strengths:**
- Mechanisms well-specified and implementable
- Predictions are specific and testable
- Assumptions mostly explicit

**Weaknesses:**

1. **Evidence base is design rationale, not validation**
   The model is coherent but untested. No data yet on whether origin tracking
   actually improves durability assessment.

2. **Alternative explanation not addressed**
   Predicted pattern (origin types have different durability) could result from
   selection bias (you adopt ideas you find compelling regardless of origin)
   rather than origin causing durability.

3. **Durability measurement undefined**
   Model predicts "patterns in durability" but doesn't specify how durability
   will be measured. Is it supersession rate? Contradiction rate? Longevity?

4. **Cognitive load assumption needs testing**
   Assumes "doesn't add excessive cognitive load" but this is untested.

**Falsification:**
What would disprove: If origin tracking provides no signal about durability
after 50+ entries, or if cognitive load makes system unusable.

**Recommendations:**
1. Change framing from "model" to "design hypothesis to be validated"
2. Add: Durability will be measured by [specific metric]
3. Add: Test design needs to rule out selection bias (e.g., track which ideas
   you engage with, not just which persist)
4. Track cognitive load feedback explicitly

**Bottom line:** Revise to clarify this is a hypothesis. Strong design logic
but needs empirical testing before claiming it "works as epistemic metadata."
```

---

### Example 2: Fermi Flags Issue During Ingest

**Scenario:** User ingesting note with inference presented as fact

**Response:**
```
[Processing ingest...]

Note: In the section "Evidence for X", I see:
> "This suggests X is true"

This is inference (suggests = reasoning from data), but it's in the "Evidence"
section, which typically holds direct observations.

Would you like me to:
1. Ingest as-is (preserve your framing)
2. Critique this before ingesting (examine inference quality)
3. Move to "Inference" section during meta extraction
```

---

### Example 3: Critique Leads to Revision

**User:** "Critique the two-layer architecture claim"

**Fermi critique identifies:** Unstated assumption about backlink maintenance

**User:** "Good point, let's revise the claim"

**Action:**
1. Update claim with explicit assumption
2. Add to provenance: "Revised YYYY-MM-DD based on critique"
3. Update timeline if exists

---

## Epistemic Discipline in Critique

### Critique Must Be

- [ ] Specific (point to lines/examples)
- [ ] Justified (explain why it's a problem)
- [ ] Constructive (how to improve)
- [ ] Honest (don't soften clear flaws)
- [ ] Fair (acknowledge strengths)
- [ ] Actionable (clear bottom line)

### Critique Must NOT Be

- [ ] Vague complaints
- [ ] Purely negative (no constructive path)
- [ ] Dismissive without analysis
- [ ] Overly harsh on uncertain exploratory ideas
- [ ] Pedantic about minor issues while missing major ones

---

## Learning from Critique

### Track Critique Patterns

When patterns emerge, note in relevant meta entries:

```markdown
## Critique Patterns

### Common issues found:
- [Pattern 1]: Appears in [N] critiques
- [Pattern 2]: Appears in [N] critiques

### Effective recommendations:
- [Type of recommendation that led to improvements]

### Critique quality feedback:
- "That critique was helpful because..." (positive signal)
- "That critique missed the point because..." (negative signal)
```

### Improve Critique Quality

Learn from feedback:
- Which critiques led to revisions? (useful)
- Which were dismissed? (possibly too harsh, missed context, or pedantic)
- What blind spots do critiques have? (user points out missed angle)

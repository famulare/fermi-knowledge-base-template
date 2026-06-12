# Claim: AI PDF Extraction Confabulates Internally Consistent Fake Data at Non-Trivial Rates

**Statement:** AI agents (across current model families) extracting numerical data from scientific PDFs confabulate fake data points at a rate of roughly 2/35 (~6%) in one observed corpus. The confabulations are not random errors — they are systematically generated from *non-data* elements of papers (protocol descriptions, design figures, dose-escalation algorithms) and produce *internally consistent* values (counts sum correctly, percentages match, biologically plausible). This internal consistency makes them undetectable by arithmetic verification alone.

**Origin:** Co-created ([UserName] + Fermi (‹model›))
**Status:** Active
**Tags:** ai-cognition, methodology

---

## Evidence

- **Fabricated dose group (Waddington 2014):** an extraction generated a complete third dose group (10⁵ challenge, n=5, 100% attack rate, with per-criterion breakdowns) from a *protocol description*. The paper tested only two doses.
- **Inverted result (Hornick 1966):** an extraction reported 9/14 (64%) disease at 10³ CFU when the actual value was 0/14 (0%).
- Both errors entered a Bayesian inference plan with 35 observations. The fabricated 10⁵ point would have anchored high-dose saturation; the inverted 10³ point would have created a spurious inter-study discrepancy.

*(Both citations are to public challenge-trial papers.)*

---

## Key Properties of the Failure Mode

1. **Systematic, not random:** confabulation sources are identifiable — protocol/design descriptions misinterpreted as executed experiments.
2. **Internally consistent:** generated values sum correctly, percentages match counts, biologically plausible.
3. **Self-camouflaging:** in the inversion case, the extraction *flagged* the anomalous result with an "open question" tag, redirecting reviewer attention toward analyzing a "discrepancy" rather than questioning the extraction itself.
4. **Rate estimate:** ~6% (2/35) in one corpus of ~20 papers; an informal working assumption is "~10% until proven otherwise."
5. **Risk scales with paper complexity:** simple results tables are lower risk; multi-phase protocols, design figures, and sensitivity analyses are high risk.

---

## Assumptions

1. The observed rate is representative of typical AI extraction quality on complex biomedical literature (may be optimistic for more complex papers, pessimistic for simpler ones).
2. The systematic bias toward confabulating from non-data elements is a general property of current LLMs, not specific to one model or prompt.
3. Internal consistency is a predictable feature of LLM confabulation — the model generates data that "should" be true given the paper's framing.

## Uncertainty

- **Rate:** n=1 corpus, 2 detected errors in 35 observations. True rate could be lower (one unlucky corpus) or higher (some errors may not have been caught).
- **Model dependence:** observed across more than one model family; may differ across families or future versions.
- **Domain dependence:** tested on challenge-trial dose-response literature; cleaner tabular data may be lower-risk, complex multi-panel figures higher-risk.

---

## Connected ideas

- **The verification protocol that caught these:** extraction-vs-extraction checking is circular; at least one agent must be put on the *primary source*, and a disagreement between them is the signal worth investigating.
- **Scientific-integrity discipline:** the "inability to ignore small discrepancies" applies — the anomalous 0%→64% point was treated as a puzzle to analyze rather than a number to re-check against the source.
- **Provenance rule:** this is concrete evidence for why quantitative parameters extracted into a knowledge base must carry an inline source pointer to the exact location in the source document.

---

## What this example demonstrates

A **claim** entry that is a cautionary, falsifiable empirical finding: a precise rate with explicit n, a named *mechanism* (confabulation from non-data elements), and the property that makes it dangerous (internal consistency → undetectable by arithmetic). It models how to log an AI-reliability lesson with honest rate uncertainty rather than a vague warning — directly relevant to anyone running an AI-assisted knowledge base.

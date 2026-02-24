> **Note:** This is a real example from a working Fermi knowledge base instance.
> It demonstrates the format and epistemic discipline of the system.
> Your KB entries will reflect your own domain and interests.

# Claim: Immunity Exists on Continuous Spectrum, Not Binary States

**Statement:** Individuals are never completely "immune" or "not immune" to infectious diseases. Immunity operates on a continuous spectrum where protection level varies with pathogen dose, time since exposure/vaccination, prior immunological history, and individual host factors. Binary susceptible/immune classifications in epidemiological models systematically misrepresent immunity dynamics and lead to incorrect predictions about vaccine efficacy, outbreak probability, and disease transmission patterns.

**Origin:** Mike

**Status:** Active

---

## Evidence

Primary sources that support this claim:

- `raw/repos/2026-01-23_famulare_typhoid-immune-dynamics.md` - Repository ingest documenting conceptual framing and model implementation
- `raw/files/github/typhoid-immune-dynamics/blog-posts/what_is_immunity_really.md` - Conceptual framing challenging binary immunity representation
- `raw/files/github/typhoid-immune-dynamics/blog-posts/cohort_incidence_model_proof_of_concept.md` - Demonstrates dose-dependent immunity override
- `meta/models/2026-01-23_typhoid-dose-response-immunity-cohort-model.md` - Mechanistic implementation showing protection as continuous function
- Empirical: Vaccine efficacy variation across settings despite matched initial effectiveness (~80% Typhoid Conjugate Vaccine)

---

## Assumptions

1. **Measurability:** Protection levels can be quantified via proxy markers (antibody titers, prior exposure history, time since vaccination)
2. **Dose-dependence universality:** Higher pathogen doses increase infection probability for all immunity levels generalizes across pathogens
3. **Waning as universal feature:** All immunity decays over time; perfect lifelong immunity following single exposure is rare exception
4. **Multi-component immunity:** Protection emerges from multiple overlapping mechanisms; binary classification collapses this complexity

---

## Uncertainty

- **Threshold approximation validity:** Under what conditions can continuous immunity be adequately approximated by binary classification without consequential prediction error?
- **Pathogen generality:** Claim based primarily on typhoid with some COVID-19 and poliovirus precedent. Generalization requires validation.
- **Policy-relevant precision:** How much does continuous vs binary representation matter for actual vaccine policy decisions?
- **Operational definitions:** "What is immunity?" involves disciplinary-specific definitions. Unified operational definition remains elusive.

---

## Related

**Supports:**
- `meta/models/2026-01-23_typhoid-dose-response-immunity-cohort-model.md`

**Challenges:**
- Standard SIR/SIRS compartmental models treating immunity as binary state transitions
- Fixed vaccine efficacy models assuming protection is intrinsic vaccine property

---

## Provenance

- **Created:** 2026-01-23
- **Change log:**
  - 2026-01-23: Created from GitHub repository ingest (typhoid-immune-dynamics)

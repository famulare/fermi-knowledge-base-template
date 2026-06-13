> **Note:** An illustrative example showing the entry format and epistemic discipline.
> Identity and file paths are genericized; the scientific content and citations are real.
> Your own entries will reflect your domain and interests.

# Claim: Immunity Exists on Continuous Spectrum, Not Binary States

**Statement:** Individuals are never completely "immune" or "not immune" to infectious diseases. Immunity operates on a continuous spectrum where protection level varies with pathogen dose, time since exposure/vaccination, prior immunological history, and individual host factors. Binary susceptible/immune classifications in epidemiological models systematically misrepresent immunity dynamics and lead to incorrect predictions about vaccine efficacy, outbreak probability, and disease transmission patterns.

**Origin:** [UserName]

**Status:** Active

**Tags:** immunology, dose-response

**Reduction question (O):** How should immunity be represented in transmission / vaccine-efficacy models?

**Boundary:** Continuous representation is load-bearing for high-dose or rapidly-waning settings; binary approximation may suffice only in low-dose, slow-waning regimes.

---

## Evidence

Primary sources that support this claim:

- `raw/repos/YYYY-MM-DD_author_typhoid-immune-dynamics.md` - Repository ingest documenting conceptual framing and model implementation
- `raw/files/blog-posts/YYYY-MM-DD_what-is-immunity-really.md` - Conceptual framing challenging binary immunity representation
- `raw/files/blog-posts/YYYY-MM-DD_cohort-incidence-model.md` - Demonstrates dose-dependent immunity override
- `model_typhoid_dose_response.md` - Mechanistic implementation showing protection as continuous function
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
- `model_typhoid_dose_response.md`

**Challenges:**
- Standard SIR/SIRS compartmental models treating immunity as binary state transitions
- Fixed vaccine efficacy models assuming protection is intrinsic vaccine property

**exemplified-by:**
- `examples/model_typhoid_dose_response.md` — concrete dose-response instantiation

---

## Provenance

- **Created:** 2026-01-23
- **Change log:**
  - 2026-01-23: Created from GitHub repository ingest (typhoid-immune-dynamics)

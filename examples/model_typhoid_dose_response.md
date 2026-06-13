> **Note:** An illustrative example showing the entry format and epistemic discipline.
> Identity and file paths are genericized; the scientific content and citations are real.
> Your own entries will reflect your domain and interests.

# Model: Typhoid Dose-Response Immunity Cohort Model

**Origin:** [UserName]

**Status:** Active

**Tags:** immunology, dose-response

**Reduction question (O):** How does vaccine efficacy vary across transmission settings, and what must a dose-response model represent to capture it?

**Boundary:** Holds where typical exposure dose varies across settings (dose-dependent protection); collapses to a fixed-efficacy model where exposure is uniform.

---

## Summary

A mechanistic typhoid immunity model that derives vaccine efficacy from exposure ecology (dose × frequency) and individual titer dynamics, rather than treating efficacy as a fixed parameter. The framework combines three interconnected components: (1) power-law antibody titer decay with age-dependence, (2) fold-rise immune response inversely proportional to existing immunity, and (3) Hill-equation dose-response linking bacterial dose and titer to infection/fever probability. Embedded within a constant force-of-infection cohort structure, the model reproduces WHO-defined incidence archetypes (medium, high, very high) and explains age-dependent disease patterns as emergent consequences of cumulative immunity rather than ad-hoc assumptions.

Core innovation: **dose-dependent immunity waning** where high pathogen doses can overwhelm prior immunity.

---

## Core Mechanisms

1. **Titer decay dynamics:** Antibody titers follow power-law decay from peak to baseline with half-life ~11 years, modulated by age-dependent waning rates.

2. **Fold-rise saturation:** Immune boost magnitude decreases with existing immunity (ceiling effect). Highly-immune individuals experience smaller boosts; naive individuals show maximal response.

3. **Dose-response with immunity override:** Infection/fever probability determined by Hill equation variant incorporating both bacterial dose and protective titer. High doses overwhelm immunity; low doses respect protective thresholds.

4. **Exposure ecology parameterization:** Disease patterns emerge from interaction between dose × frequency combinations. Medium incidence: 500 bacilli/40 years; High: 5,000/20 years; Very high: 50,000/20 years.

---

## Predictions/Implications

**Testable predictions:**
- Vaccine efficacy should decline faster in high-dose transmission settings
- Age-incidence curves differ predictably by exposure ecology
- Population-level immunity increases in high-transmission settings despite higher incidence (counterintuitive)

**Decision-relevant implications:**
- Geographic variation in vaccine efficacy mechanistically explained by local exposure ecology
- Settings with similar infection rates may require different strategies if exposure doses differ
- High-dose exposures disproportionately drive fever incidence; dose reduction strategies may have outsized impact

---

## Evidence Base

- `raw/repos/YYYY-MM-DD_author_typhoid-immune-dynamics.md` - Repository ingest
- Bangladesh serosurvey data (Quadri 2021) - Titer distribution validation
- WHO modeling consortium incidence archetypes - Calibration targets
- Historical naive-adult challenge studies - Dose-response parameter bounds

---

## Assumptions

1. No individual variation (current) — all individuals within age cohort respond identically
2. Constant force-of-infection — exposure rate constant at endemic equilibrium
3. Single correlate of protection — anti-Vi IgG as sole mechanistic link
4. Power-law decay functional form chosen for flexibility and biological plausibility

---

## Scope

**Where applicable:** Endemic typhoid settings, vaccine policy analysis, age-structured cohort prediction

**Where NOT applicable:** Outbreak dynamics, short-term prediction, individual-level prediction, non-typhoid pathogens

---

## Related

**Implements:**
- `model_continuous_immunity_framework.md` — This is a single-pathogen instance of that general dose-response/waning framework.

**Supported by:**
- `claim_immunity_continuous_spectrum.md` — Provides the conceptual claim this model operationalizes.

**demonstrates:**
- `examples/claim_immunity_continuous_spectrum.md` — the dose-response cohort model is a concrete instance of continuous immunity

---

## Provenance

- **Created:** 2026-01-23
- **Origin detail:** Ingested from [UserName]'s GitHub repository (typhoid-immune-dynamics); active research project
- **Change log:**
  - 2026-01-23: Created from GitHub repository ingest; proof-of-concept status

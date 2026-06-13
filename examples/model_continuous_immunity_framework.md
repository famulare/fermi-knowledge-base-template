# Model: Continuous Immunity Dose-Response Framework

**Origin:** [UserName]
**Status:** Active
**Tags:** immunology, dose-response
**Source:** a presentation on better defaults for immunity modeling

**Reduction question (O):** Can one cross-pathogen framework capture immunity dynamics — and which details can be dropped?

**Boundary:** Holds where protection is a continuous function of titer × dose with power-law waning; breaks where immunity is effectively all-or-nothing.

---

## Overview

A unified framework for modeling acquired immunity across acute infectious diseases. Replaces common defaults (binary immunity, exponential waning, separate priming/boosting models) with biologically-grounded continuous alternatives that better predict behavior across settings and timescales.

**Scope:** Diseases with separation of timescales between infection and immune dynamics.
- **Applicable:** polio, measles, RSV, rotavirus, acute typhoid, COVID, flu, dengue, HPV, TB (outcomes)
- **Less applicable:** Diseases with predator-prey-like dynamics on similar scales (malaria, HIV)

---

## The Five Principles

### 1. Immunity Always Means Multiple Things

Immunity is not monolithic. Protection against different endpoints (infection, symptoms, hospitalization, death, carriage, transmission) are conditionally dependent but distinct.

**Core relation:**
```
RR_symptoms = RR_symp|inf × RR_inf
VE_symptoms = 1 - (1 - VE_symp|inf)(1 - VE_inf)
```

**Implication:** Vaccine efficacy for any endpoint is a composite of effects on all upstream conditional risks.

### 2. Protection Is Always a Function of Correlates

Correlates of Protection (CoP) are continuous quantities. VE varies continuously with CoP.

**Standard model (allows VE < 0):**
```
log(RR_outcome) = α - β log(CoP)
VE_outcome = 1 - e^α (CoP)^(-β)
```

**Bounded model (VE ∈ [0,1]):**
```
logit(VE_outcome) = α + β log(CoP)
```

Use the bounded form when VE > 0 can be safely assumed — more efficient statistically and correct biologically.

### 3. Almost All Immunity Is Leaky

Binary ("sterilizing") immunity is an approximation. Immunity is almost always a function of dose — a large enough dose delivered the right way can overcome immunity.

**Dose-response model (approximate beta-Poisson with immunity):**
```
P(infected | dose, CoP) = p_max × (1 - (1 + dose/β)^(-α/(CoP)^γ))
```

**VE from dose-response:**
```
VE_inf(dose, CoP) = 1 - P(infected | dose, CoP) / P(infected | dose, CoP_min)
```

**Key insight:** At small doses (linear regime), `VE_inf ≈ 1 - (CoP_min/CoP)^γ` — VE is independent of exposure dose. **Implication:** R0 and VE against infection are typically inversely correlated, so large R0 variation across settings guarantees variation in observed VE.

### 4. Waning Is Never Exponential

Exponential waning assumes zero variation in cellular/molecular response and zero long-term adaptation — biologically unrealistic.

**Power-law waning model (gamma-distributed decay rates):**
```
CoP(t) = CoP_min + (CoP_peak - CoP_min)(1 + (t-τ_peak)/(αT_decay))^(-α)   for t ≥ τ_peak
```

Matches observed short-term dynamics and better predicts long-term behavior even without long-term data. **Default recommendation:** if α cannot be identified from data, assume α ≈ 1.

### 5. Universal Boosting Response Model

A single model describes CoP response across the entire range of achievable immunity:
```
Mean[log(CoP_peak/CoP_pre)] = μ_source × (1 - log(CoP_pre)/log(CoP_max))
sd[log(CoP_peak/CoP_pre)]   = σ_source × (1 - log(CoP_pre)/log(CoP_max))
```

**Key insight:** CoP_max is a property of host immune system + pathogen, shared across infection and different vaccine formulations/schedules. For neutralizing antibodies against viruses, CoP_max ~ 2^14 ≈ 10^4.2.

---

## Correlates of Transmission

Given leaky immunity, shedding varies with CoP:
```
Shedding measure = (Shedding measure)_max × (1 - k log(CoP_pre))
```
Applies to duration and concentration excreted. VE for transmission depends on individual correlates and transmission ecology.

---

## Assumptions

1. **Timescale separation:** Infection dynamics resolve faster than immune dynamics.
2. **Continuous correlates:** Immune status can be meaningfully quantified on a continuous scale.
3. **Gamma-distributed heterogeneity:** Individual variation in decay rates follows a gamma distribution.
4. **Universal ceiling:** CoP_max is pathogen-specific but invariant to exposure source.

## Limitations

1. **Cross-immunity not addressed** — framework is single-pathogen.
2. **Host heterogeneity not addressed** — assumes population averages.
3. **CoP must be measurable** — requires a functional assay or proxy.

---

## Closing Principle

> "Think through the biology and the data, complexify as you can, simplify as you must, propagate uncertainty, and advocate to measure important unknowns."

---

## What this example demonstrates

A **model** entry at framework altitude: it states scope and applicability boundaries, lays out mechanism as explicit equations, names the key inferential consequences (e.g. R0–VE inverse correlation), and separates assumptions from limitations. Note that specific instance-models (a typhoid dose-response model, a multiscale transmission model) would each cite this framework as the general structure they implement — a meta-layer "umbrella" with instances beneath it.

---

## Related

**generalizes:**
- `examples/model_typhoid_dose_response.md` — typhoid is one instantiation of the general framework

**shared-framework:**
- `examples/claim_immunity_continuous_spectrum.md` — same continuous-immunity premise

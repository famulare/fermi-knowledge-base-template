> **Note:** This is a real example from a working Fermi knowledge base instance.
> It demonstrates the format and epistemic discipline of the system.
> Your KB entries will reflect your own domain and interests.

# Claim: Absence of Evidence Is Quantifiable Probabilistically

**Statement:** Absence of evidence is not evidence of absence, but it CAN be quantified probabilistically. Given a stochastic model of transmission and detection, the probability of elimination given zero detected cases increases with time since the last case, the surveillance sensitivity, and the case-to-infection ratio. This probabilistic framing replaces binary yes/no certification with continuous probability estimates.

**Origin:** [UserName]

**Status:** Active

**Tags:** epidemiology, methodology

---

## Evidence

- `raw/web/papers/YYYY-MM-DD_author_poliovirus-elimination-probability.md` - Stochastic Gillespie simulation framework estimates WPV1 elimination probability at 84%, WPV3 at >99%, and cVDPV2 as unlikely, validated when subsequent cVDPV2 case fell at 54th percentile of predictive distribution

---

## Assumptions

1. Case-to-infection ratios are approximately known and stable over the analysis period
2. Surveillance sensitivity (AFP detection quality) is reasonably characterized and constant
3. Stochastic transmission model with time-varying R_eff adequately represents elimination-phase dynamics

---

## Uncertainty

- **Case-to-infection ratio stability:** Ratios may vary with population immunity, age structure, and viral evolution; sensitivity to these ratios is high
- **Spatial homogeneity assumption:** National-level aggregation may overestimate elimination probability in focal high-risk areas

---

## Related

**Supports:**
- `meta/claims/YYYY-MM-DD_data-driven-elimination-over-calendar-rules.md`
- `meta/claims/YYYY-MM-DD_prediction-intervals-as-success-metric.md`

---

## Provenance

- **Created:** 2026-02-06
- **Change log:**
  - 2026-02-06: Created from raw/web/papers/YYYY-MM-DD_author_poliovirus-elimination-probability.md

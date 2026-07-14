> **Note:** An illustrative example showing the entry format and epistemic discipline.
> Identity and file paths are genericized; the scientific content and citations are real.
> Your own entries will reflect your domain and interests.

# Model: Sabin-2 Evolutionary-Epidemiological Reversion

**Origin:** [UserName] (Wong 2023 building on Valesano 2021)

**Status:** Active

**Evidence status:** sourced

**Tags:** infectious-disease, molecular-evolution

---

## Summary

A stochastic evolutionary-epidemiological model of how Sabin 2 poliovirus reverts from vaccine to pathogen. Within-host positive selection drives near-universal gatekeeper reversion (A481G fixes in 2-3 weeks); between-host transmission bottleneck (~2 genomes) creates a stochastic filter; sanitation level determines whether reverted virus survives to establish community transmission. The resolution: individual reversion is near-universal (92.4%), but community establishment is probabilistic (fails in 39.6% of simulations). The binding constraint on cVDPV2 emergence is not mutation rate but transmission bottleneck severity.

---

## Core Mechanisms

1. **Within-host positive selection:** 24 convergent mutations identified across independent vaccine recipients. The gatekeeper site A481G fixes within 2-3 weeks of vaccination. Attenuation is under immediate evolutionary pressure in every recipient — the virus shed two weeks post-vaccination is not the virus in the vaccine vial.

2. **Transmission bottleneck filter:** Person-to-person transmission involves a bottleneck of approximately 2 viral genomes. Despite near-universal within-host reversion, only ~2 lineages survive each transmission event, creating stochastic loss of reverted variants during early chain propagation.

3. **Sanitation as critical determinant:** Low-sanitation settings permit the fecal-oral transmission chains needed for reverted lineage survival. Higher sanitation breaks chains before establishment. cVDPV2 is geographically concentrated not because reversion is more likely there, but because reverted virus survives bottlenecks more frequently.

---

## Predictions/Implications

**Testable predictions:**
- cVDPV2 emergence concentrated in low-sanitation settings (validated: overwhelmingly sub-Saharan Africa and South Asia)
- Improved sanitation reduces cVDPV2 risk even without vaccination changes
- nOPV2 with stabilized gatekeeper should dramatically reduce cVDPV2 emergence (under test)

**Decision-relevant implications:**
- Sanitation improvement is a complementary strategy to vaccination for cVDPV prevention
- nOPV2 development was justified and urgent — the evolutionary pressure on attenuation is immediate and universal
- Reversion risk assessments must model the population filter, not just within-host evolution

---

## Evidence Base

- `raw/web/papers/YYYY-MM-DD_author_polio-program.md:Paper-5` — Wong 2023: 92.4% gatekeeper reversion, 39.6% stochastic extinction, sanitation as critical factor
- `raw/web/papers/YYYY-MM-DD_author_polio-program.md:Paper-7` — Valesano 2021: 24 convergent mutations, A481G fixes in 2-3 weeks, bottleneck ~2 genomes
- **Code:** `https://github.com/<org>/cvdpv2-evo-epi`

---

## Assumptions

1. Matlab, Bangladesh field data representative of high-transmission settings
2. Gatekeeper mutation (A481G) is rate-limiting for phenotypic reversion
3. Stochastic model captures relevant transmission dynamics at early chain stage
4. Deep sequencing captures true bottleneck size (~2 genomes consistent across routes)
5. Sanitation level adequately proxied by fecal-oral transmission probability

---

## Scope

**Where applicable:**
- Live attenuated vaccines where reversion to virulence is possible and transmission is fecal-oral
- Any setting where within-host evolution is near-deterministic but between-host propagation is stochastic

**Where NOT applicable:**
- Respiratory-transmitted vaccines (different bottleneck structure)
- Vaccines with multiple independent attenuating mechanisms (reversion requires more mutations)
- Settings where environmental transmission dominates over direct fecal-oral contact

---

## Tensions/Coexistence

**Extends:**
- `meta/models/YYYY-MM-DD_polio-multiscale-transmission-immunity-model.md` — Adds evolutionary dynamics to the fixed-parameter Sabin model. The 2018 framework noted "Sabin evolutionary dynamics during prolonged circulation are largely unstudied"; this model fills that gap.

**Coexists with:**
- `meta/models/YYYY-MM-DD_four-scale-hierarchical-transmission.md` — Complementary: this model handles reversion; the four-scale model handles transmission structure. Full picture requires both.

**Related contradiction:**
- `contradiction_cvdpv_emergence.md` — Documents the primacy tension among the population-immunity, stochastic-establishment, and transmission-bottleneck filters this model formalizes.

---

## Provenance

- **Created:** 2026-02-06
- **Origin detail:** [UserName] directed the Wong 2023 study as senior/corresponding author; Valesano 2021 (External: Valesano/Lauring team) provided the genomic evidence that this model formalizes.
- **Change log:**
  - 2026-02-06: Created from senior-author polio program ingest

> **Note:** This is a real example from a working Fermi knowledge base instance.
> It demonstrates the format and epistemic discipline of the system.
> Your KB entries will reflect your own domain and interests.

# Contradiction: What Controls cVDPV Emergence — Population Immunity vs Stochastic Bottleneck

**Status:** Resolved

**Detected:** 2026-02-09

---

## Item A

**Statement:** The historical rarity of cVDPV outbreaks is explained by high population immunity suppressing Sabin strain transmission, not by intrinsic biological attenuation. In populations with low immunity, R_Sabin approaches R_wild (R_Sabin ≈ 0.85 × R_wild).

**Origin:** Mike, 2026-01-23

**Source:** `meta/claims/2026-01-23_polio-cVDPV-rarity-population-immunity.md`

**Raw evidence:** `raw/web/papers/2018-04-27_famulare_polio-eradication-stability.md`

---

## Item B

**Statement:** Gatekeeper reversion is near-universal (92.4% of vaccinated naive individuals) but community establishment is stochastic — 39.6% of transmission simulations end in extinction. Sanitation level (not mutation rate) is the critical factor determining whether individual reversion becomes a population-level outbreak.

**Origin:** Mike (Wong 2023) building on External (Valesano 2021), 2026-02-06

**Source:** `meta/claims/2026-02-06_gatekeeper-reversion-universal-establishment-stochastic.md`

**Raw evidence:** `raw/web/papers/2017-2023_famulare-senior-author-polio-program.md`

---

## Item C

**Statement:** Person-to-person transmission involves a bottleneck of ~2 viral genomes. This tight bottleneck means the binding constraint on cVDPV emergence is not within-host reversion but between-host propagation — whether reverted variants survive the stochastic filter of transmission.

**Origin:** External (Valesano/Lauring) + Mike (interpretation), 2026-02-06

**Source:** `meta/claims/2026-02-06_transmission-bottleneck-2-genomes-rate-limiting.md`

**Raw evidence:** `raw/web/papers/2017-2023_famulare-senior-author-polio-program.md`

---

## Nature of Tension

All three claims are Mike's own work from different periods and publications. They are complementary — describing different filters in the path from OPV dose to cVDPV outbreak — but their framing of primacy is potentially contradictory:

- **Item A** (2018 paper): Population immunity is the "primary" explanation for historical cVDPV rarity. The mechanism is suppression of Sabin R below 1 via herd immunity.
- **Item B** (2023 paper): Sanitation level is "the critical factor." Even with near-universal reversion, community establishment is stochastic.
- **Item C** (2021 genomics): The ~2-genome transmission bottleneck is "the binding constraint" — rate-limiting for emergence.

Each identifies a different filter as "primary" or "critical" or "binding." The implicit hierarchy:
1. Population immunity suppresses R (macro filter)
2. Stochastic extinction prevents establishment (meso filter, conditioned on R > 1 locally)
3. Transmission bottleneck culls reverted variants (micro filter, per-transmission-event)

The tension: which filter matters most for intervention? If population immunity is primary, maintaining coverage is the answer. If the stochastic bottleneck is primary, even partial coverage gaps may be tolerable because most introductions self-extinguish. If sanitation is the critical factor, the intervention target shifts to environmental conditions.

**Type:** Implicit contradiction in primacy — three complementary filters each claimed as the dominant control

---

## Possible Resolutions

1. **Multi-scale filter chain (no single primacy)**
   - Description: Formalize these as a hierarchical filter chain: immunity (macro) → stochastic establishment (meso) → transmission bottleneck (micro). Each operates at a different scale. "Primary" depends on the intervention question being asked and the current state of the system.
   - Trade-offs: Most accurate but loses the simplicity of "population immunity explains cVDPV rarity" as a one-sentence summary.

2. **Conditional primacy**
   - Description: Population immunity is primary when it holds (R < 1 everywhere). Once immunity gaps open (R > 1 locally), the stochastic filters (bottleneck + establishment probability) become rate-limiting. Different filters dominate in different epidemiological regimes.
   - Trade-offs: Requires specifying regime boundaries, which may not be sharp.

3. **Temporal primacy**
   - Description: Population immunity was the dominant filter historically (pre-cessation). Post-cessation, as immunity declines, the stochastic filters become the residual protection. The claims describe different eras.
   - Trade-offs: Clean narratively but may oversimplify — stochastic extinction was always operating, just masked by the strength of the immunity filter.

---

## Resolution (if resolved)

**Chosen approach:** Multi-scale filter chain (no single primacy)

**Rationale:** The three claims describe complementary filters operating at different scales (population, community, per-transmission-event). Their relative importance is regime-dependent: population immunity dominates pre-cessation; stochastic filters become rate-limiting when coverage gaps open. No single filter has primacy in general.

**Result:** `meta/models/2026-02-09_cvdpv-emergence-multiscale-filter-chain.md`

**Resolved on:** 2026-02-09

---

## Provenance

- **Detected:** 2026-02-09 during contradiction audit of all Active claims
- **Last updated:** 2026-02-09

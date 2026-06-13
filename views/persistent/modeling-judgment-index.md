# Modeling-Judgment Index

**Generated:** 2026-06-12 18:16 by `scripts/generate_modeling_judgment_index.py` — do not hand-edit.
**Source of truth:** the `modeling-judgment` tag in `index/tags.md` + the `**Reduction question (O):**` / `**Boundary:**` fields in each entry.

**4** tagged entries · **4** with a stated boundary · **0** boundary gaps (worklist).

> Each row pairs the keep/ignore judgment's question (O) with the regime where it breaks. Rows marked ⚠ have no characterized boundary yet — candidates for the human gate to fill.

## other

| Entry | Question (O) | Boundary (where it breaks) |
|---|---|---|
| [claim_immunity_continuous_spectrum.md](../../examples/claim_immunity_continuous_spectrum.md) | How should immunity be represented in transmission / vaccine-efficacy models? | Continuous representation is load-bearing for high-dose or rapidly-waning settings; binary approximation may suffice only in low-dose, slow-waning regimes. |
| [contradiction_uncanny_valley_coarse_graining.md](../../examples/contradiction_uncanny_valley_coarse_graining.md) | How much mechanistic complexity should a scenario-projection model of a non-factorizable system carry? | There is no fixed safe complexity level — the calibrate-predict-compare selection function is the boundary; intermediate models chosen by convention fall into the valley. |
| [model_continuous_immunity_framework.md](../../examples/model_continuous_immunity_framework.md) | Can one cross-pathogen framework capture immunity dynamics — and which details can be dropped? | Holds where protection is a continuous function of titer × dose with power-law waning; breaks where immunity is effectively all-or-nothing. |
| [model_typhoid_dose_response.md](../../examples/model_typhoid_dose_response.md) | How does vaccine efficacy vary across transmission settings, and what must a dose-response model represent to capture it? | Holds where typical exposure dose varies across settings (dose-dependent protection); collapses to a fixed-efficacy model where exposure is uniform. |


# Contradiction: Uncanny Valley vs Optimal Coarse Graining

**Status:** Resolved
**Origin:** Co-created ([UserName] + Fermi (‹model›))
**Tags:** methodology, modeling-philosophy
**Created / Resolved:** same session

**Reduction question (O):** How much mechanistic complexity should a scenario-projection model of a non-factorizable system carry?

**Boundary:** There is no fixed safe complexity level — the calibrate-predict-compare selection function is the boundary; intermediate models chosen by convention fall into the valley.

---

## Tension

**Item A — "Uncanny valley of half-complexity" claim:**
Adding *partial* mechanistic complexity to a model of a non-factorizable system is *worse* for scenario projections than either radical simplification or full complexity. The intermediate model has enough degrees of freedom to fit the data, but its fitted parameters absorb errors from the missing complexity, corrupting projections. *Worked instance:* a within-host shedding-duration parameter was wrong by ~3× for months, yet population-level calibration tolerated it because a transmission-rate parameter silently absorbed the error — the mistake only surfaced when an independent finer-scale dataset forced multi-scale consistency.

**Item B — Optimal coarse graining (renormalization-group view):**
You can choose *any* resolution along a complexity spectrum using a principled selection function: calibrate each candidate model to observations, predict downstream quantities, and choose the model that best preserves prediction accuracy. The recipe treats intermediate complexity as a valid design choice, not a danger zone.

**Apparent conflict:** Item A says intermediate complexity is systematically dangerous. Item B says it's a principled design choice. Same problem domain (non-factorizable systems), opposite conclusions about intermediate-resolution models.

---

## Resolution

The reconciliation is that **factorizability is the definition of a good coarse graining**. A good coarse graining groups things that must be grouped and separates things that are approximately separable. The uncanny valley is the phenomenon of an *inconsistent* coarse graining — one that adds mechanistic detail without respecting the coupling structure of the system.

Item B's selection function (calibrate, predict, compare to a reference) is precisely the procedure that identifies which coarse grainings are consistent. Item A's uncanny valley is what happens when you skip that procedure — adding detail by intuition or convention rather than by checking whether the grouping respects the system's coupling structure.

The claims are **not contradictory**. The RG framework *subsumes* the uncanny-valley claim: the valley exists in the space of blind/conventional intermediate models, and the selection function is the tool that avoids it.

---

## What this example demonstrates

A **resolved** contradiction (contrast with a *coexisting* one, where two views are carried unreconciled). The entry states each item in its own terms, names the apparent conflict precisely, and resolves it by showing one frame *subsumes* the other rather than defeating it — the more common and more useful outcome than "one side wins." Note the origin is `Co-created`: the tension and its resolution emerged in dialogue.

---

## Related

**related-to:**
- `examples/model_continuous_immunity_framework.md` — choosing representation granularity for a coupled system

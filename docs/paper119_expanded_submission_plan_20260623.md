# Paper 119 Expanded Submission Plan - 2026-06-23

Paper: `energy_landscape_skill_composition`

Target: expand the current 4-page v4.1 package into a 25+ page v5 hostile-review submission artifact with stronger theory, stronger experiments, real citations, bright boxed clickable citation links, and honest terminal status.

## Non-Negotiables

- Optimize for hostile-review survival, not pretty numbers.
- Use strong baselines and stress tests to expose weaknesses.
- Improve the method during development, then freeze the final v5 protocol and report all predefined results.
- Keep the implementation CPU-only and RAM-light.
- Keep `119.pdf` in Downloads only.
- Do not claim ICLR-main readiness without real robot or accepted high-fidelity validation.

## Planned v5 Contribution

`barrier_certified_energy_composer_v5` composes skills only when the terminal distribution of the preceding skill overlaps the next attraction basin, the seam does not cross an unsafe barrier, descent continuity is positive, and predicted seam risk is below the declared fixed-risk budget.

## Planned Theory

- Define skill composition as energy-seam compatibility.
- Separate module sequencing from basin/barrier compatibility.
- Derive a seam score combining basin overlap, barrier height, descent continuity, seam repair cost, and risk calibration.
- State the abstention condition for broken primitives, nonconservative contacts, semantic conflicts, and miscalibrated learned energies.

## Planned Experiments

- Main benchmark with episode-level cells across tasks, regimes, splits, methods, seeds, and episodes.
- Hard-slice aggregate and pairwise seed tests.
- Ablations for every method component.
- Stress sweep over seam discontinuity, barrier height, nonconvexity, partial observability, dynamics mismatch, and miscalibration.
- Fixed-risk deployment audit.
- At least 24 failure cases.

## Planned Documentation

- Update child status docs and create a v5 readiness audit, terminal audit, validation script, and manuscript generator.
- Remove stale v4.1-only terminal plan/audit files after v5 artifacts exist.
- Update root ledgers only after validation, visual QA, and GitHub push succeed.

## Final Gate

Paper 119 can be marked complete only after the 25+ page PDF, generated evidence, public GitHub commit, Downloads-only artifact placement, visual PDF QA, and root ledger updates all pass.

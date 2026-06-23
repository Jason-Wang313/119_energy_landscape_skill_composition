# Paper 119 Expanded-Standard v5 Plan

Goal: rebuild `energy_landscape_skill_composition` into a 25+ page, CPU-only, RAM-light, hostile-review submission package. The output remains honest: local evidence can justify `STRONG_REVISE`, but not ICLR-main readiness without real robot or independently accepted high-fidelity validation.

## Frozen Protocol

1. Keep the canonical numbered PDF at `C:/Users/wangz/Downloads/119.pdf` only.
2. Do not copy numbered PDFs to the Desktop, factory root, or child repo root.
3. Predefine all local result gates before interpreting final results.
4. Select the strongest non-oracle baseline automatically after the full run.
5. Retain the v4.1 proposed method as a named baseline.
6. Report every predefined metric, including weaknesses, oracle gaps, failure cases, and scope blockers.
7. Keep CPU/RAM usage light: deterministic NumPy/CSV generation, single-process execution, no model downloads, no GPU assumptions.
8. Use real, checkable references and bright boxed clickable citation links.

## Method Upgrade

Develop v5 as `barrier_certified_energy_composer_v5`, not merely a renamed v4.1 script. The method must add:

- Basin-overlap posterior over terminal states and next-skill attraction sets.
- Barrier-height and descent-continuity score over the handoff seam.
- Terminal-state sampler with high-energy seam repair.
- Contact-mode and dynamics-shift guard for nonconservative transitions.
- Fixed-risk acceptance screen over predicted seam failure.
- Conservative fallback/abstention when the basin/barrier evidence is insufficient.
- Calibration term so low predicted seam risk must match realized seam risk.

## Theory Upgrade

- Define skill composition as a seam compatibility problem between terminal distributions and attraction basins.
- Formalize a seam score with basin overlap, barrier height, descent continuity, repair cost, and risk budget.
- State a safe-composition condition: a composed edge is locally acceptable only when descent continuity is positive and predicted barrier/seam risk is below the declared budget.
- State a failure condition: nonconservative contact, broken primitives, semantic-goal conflict, or miscalibrated learned energies require abstention or external replanning.
- Keep theory bounded to the local benchmark; do not claim universal stability or real-robot safety.

## Experiment Upgrade

Run a new v5 suite with:

- Main benchmark: task families, seam regimes, deployment splits, methods, paired seeds, and raw episode cells.
- Baselines: greedy sequence, behavior-cloned chain, option graph, diffusion stitcher, CEM composer, residual RL composer, energy-compatibility heuristic, TAMP-style feasibility screen, stable-DMP handoff, v4.1 proposed baseline, v5 proposed, and oracle.
- Hard aggregate: narrow basin, high barrier, nonconvex energy, contact-mode transition, dynamics mismatch, partial observability, and combined seam stress.
- Paired-seed comparisons against every non-oracle baseline.
- Ablations: remove basin overlap, barrier height, descent continuity, seam repair, terminal sampler, contact-mode guard, fixed-risk gate, calibration, and repair memory.
- Stress sweeps: seam discontinuity, barrier height, nonconvexity, partial observability, dynamics mismatch, and calibration shift.
- Fixed-risk deployment audit: predicted seam-failure budget with coverage, breach, gated success, gated utility, and abstention.
- Failure cases: at least 24 concrete boundary cases.

## Manuscript Upgrade

Generate a 25+ page ICLR-style PDF with:

- Abstract, contribution statement, claim/scope boundary, and hostile-review summary.
- Formal problem setup, method derivation, theory/intuition, and failure-mode analysis.
- Related work grounded in real energy-based learning, composable energy policies, DMP/stable dynamical systems, options/skill chaining, TAMP, and robot-learning references.
- Tables and figures generated from v5 CSV outputs only.
- Explicit statement that the evidence is local/synthetic and not final ICLR-main-ready.
- Bright boxed clickable citations that jump to the bibliography.

## Validation Gates

The rebuild only counts as complete if all required artifacts pass:

- `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py`
- v5 experiment run completes under thread caps.
- CSV row-count and numeric-integrity checks pass.
- PDF compiles with LaTeX/BibTeX and has at least 25 pages.
- BibTeX has zero warnings.
- Visual QA checks representative pages.
- `C:/Users/wangz/Downloads/119.pdf` exists and no numbered copies exist elsewhere.
- Public GitHub repo is updated and the pushed commit is verified.
- Root ledgers are updated only after local validation passes.

# Experiment Rigor Checklist

- [x] Paper-specific benchmark replacing the shared archive template.
- [x] 6 task families, 8 skill-composition regimes, 5 deployment splits.
- [x] 12 composition methods including strong non-oracle baselines, the prior proposed method, and an oracle upper bound.
- [x] 10 paired seeds with raw episode-level cell outputs.
- [x] Strongest-baseline comparison selected by hard aggregate success after the full run.
- [x] Paired-seed statistics reported for all baselines.
- [x] Mechanism metrics beyond success: utility, seam failure, barrier violation, basin alignment, descent continuity, damage, composition cost, energy-model error, calibration error, and realized seam breach.
- [x] Ablations for basin overlap, barrier height, descent continuity, seam repair, terminal-state sampler, contact guard, fixed-risk gate, calibration, and repair memory.
- [x] Stress sweep over seam discontinuity, barrier height, nonconvexity, partial observability, dynamics mismatch, and calibration shift.
- [x] Fixed-risk deployment audit reports coverage, breach, gated success, gated utility, and pairwise comparisons.
- [x] 24 failure cases documented.
- [x] Terminal gates computed in `results/summary.json` and `results/summary.txt`.
- [x] 25-page PDF, BibTeX warning count zero, log warning scan clean, visual QA complete.

Residual risk: all evidence remains local. Real robot or external high-fidelity validation is still required before an ICLR-main submission claim.

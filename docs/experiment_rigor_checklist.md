# Experiment Rigor Checklist

- [x] Paper-specific benchmark replacing the shared v3 template.
- [x] 6 task families, 8 skill-composition regimes, 5 deployment splits.
- [x] 9 composition methods including strong non-oracle baselines and an oracle upper bound.
- [x] 7 paired seeds with 72 rollout episodes per group.
- [x] Strongest-baseline comparison selected by combined-stress success.
- [x] Paired-seed statistics reported for all baselines.
- [x] Mechanism metrics beyond success: seam failure, barrier violation, basin alignment, descent continuity, damage, composition cost, energy-model error.
- [x] Ablations for basin overlap, barrier height, descent continuity, energy repair, terminal-state sampler, and compatibility-only heuristic.
- [x] Stress sweep over seam discontinuity and hidden barrier height.
- [x] Failure cases documented.
- [x] Terminal gates computed in `results/summary.txt`.

Residual risk: all evidence remains local. Real robot or external high-fidelity validation is still required before an ICLR-main submission claim.

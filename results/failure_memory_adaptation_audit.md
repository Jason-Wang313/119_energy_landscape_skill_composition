# Failure-Memory Adaptation Audit

Passed: `true`.
Scope: local synthetic hard-slice observed-to-held-out signature memory only; this is not external robot or high-fidelity simulator evidence.

## Protocol

For each local hard-slice task/regime/split/seed frontier, episodes 0-3 are treated as observed seam evidence and episodes 4-7 are held out. The audit groups rows by `(diagnostic_label, planner_edge_update)` and asks whether observed breach/utility memory predicts held-out outcomes for the same failure/update signature.

## Metrics

- Proposed memory signatures: `2210` over `1667` frontiers.
- Task/regime/split coverage: `6/6`, `7/7`, `4/4`.
- Observed-to-held-out breach correlation: `0.957419`.
- Memory breach MAE: `0.004586` versus held-out predicted-risk MAE `0.007382`.
- Held-out breach, high vs low memory-risk quartile: `0.120231` vs `0.073852`.
- Held-out utility, high vs low memory-risk quartile: `0.796243` vs `0.956434`.
- Held-out success, high vs low memory-risk quartile: `0.777627` vs `0.813859`.
- V5 high-memory-risk future breach delta vs predecessor: `-0.082882`.
- V5 high-memory-risk future utility delta vs predecessor: `+0.247856`.

## Checks

- `pass` `not_external_evidence_declared`: local few-shot memory audit only
- `pass` `proposed_memory_signatures_ge_2000`: signatures=2210
- `pass` `proposed_frontiers_covered_ge_1600`: frontiers=1667
- `pass` `memory_covers_all_tasks_regimes_splits`: tasks=6, regimes=7, splits=4
- `pass` `observed_breach_predicts_future_breach`: corr=0.957419
- `pass` `memory_breach_mae_le_0_006`: mae=0.004586
- `pass` `memory_beats_future_risk_mae_by_0_002`: improvement=0.002795
- `pass` `high_memory_risk_predicts_higher_future_breach`: gap=0.046379
- `pass` `high_memory_risk_predicts_lower_future_utility`: gap=-0.160191
- `pass` `high_memory_risk_predicts_lower_future_success`: gap=-0.036232
- `pass` `v5_high_memory_breach_lower_than_predecessor`: delta=-0.082882
- `pass` `v5_high_memory_utility_higher_than_predecessor`: delta=0.247856

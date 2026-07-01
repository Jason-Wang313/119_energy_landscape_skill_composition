# Planner-Edge Policy Audit

Passed: `true`.
Scope: local synthetic hard-slice planning frontiers only; this is not external robot or high-fidelity simulator evidence.

## Policy

For each task/regime/split/seed frontier, the audit selects a candidate edge using exported planner-edge updates first, then predicted seam risk, basin alignment, descent continuity, and composition cost. It does not use realized utility to choose the edge.

## Metrics

- Baseline: `proposed_energy_landscape_composer_v4_1`.
- Planning frontiers: `1680`.
- Rows per method per frontier: `8`.
- Proposed selected updates: `{'increase_edge_confidence': 1072, 'mark_bridge_required': 36, 'prefer_alternate_edge': 12, 'request_diagnostic_sample': 105, 'suppress_edge': 455}`.
- Baseline selected updates: `{'mark_bridge_required': 210, 'prefer_alternate_edge': 67, 'request_diagnostic_sample': 5, 'suppress_edge': 1398}`.
- Executable-edge coverage: proposed `0.666667`, baseline `0.164881`, delta `+0.501786`.
- Selected-edge utility: proposed `0.888861`, baseline `0.657543`, delta `+0.231317`.
- Selected-edge success: proposed `0.795238`, baseline `0.714881`, delta `+0.080357`.
- Selected-edge realized breach: proposed `0.089141`, baseline `0.164323`, delta `-0.075182`.
- Proposed selected breach>0.15 rate: `0.000595`.
- Frontier lexicographic win rate: `0.845833`.
- Positive utility margins: task `6/6`, regime `7/7`, split `4/4`.

## Checks

- `pass` `not_external_evidence_declared`: local hard-slice planning-frontier audit only
- `pass` `planning_frontiers_ge_1500`: frontiers=1680
- `pass` `frontier_rows_per_method_ge_8`: rows_per_method=8
- `pass` `proposed_executable_edge_coverage_ge_0_60`: coverage=0.666667
- `pass` `executable_edge_coverage_delta_ge_0_45`: delta=0.501786
- `pass` `selected_utility_delta_ge_0_18`: delta=0.231317
- `pass` `selected_success_delta_ge_0_05`: delta=0.080357
- `pass` `selected_realized_breach_delta_le_minus_0_05`: delta=-0.075182
- `pass` `proposed_selected_breach_over_budget_rate_le_0_005`: rate=0.000595
- `pass` `frontier_lexicographic_win_rate_ge_0_80`: win_rate=0.845833
- `pass` `all_task_groups_positive_utility_margin`: positive=6/6, worst=0.168204
- `pass` `all_regime_groups_positive_utility_margin`: positive=7/7, worst=0.181877
- `pass` `all_split_groups_positive_utility_margin`: positive=4/4, worst=0.218606

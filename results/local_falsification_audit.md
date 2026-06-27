# Local Falsification Audit

Passed: `true`.
Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.

## Gates

- `pass` `paired_hard_rows_ge_10000`: paired_hard_rows=13440
- `pass` `not_abstention_gaming`: abstention_delta=0.006485, utility_margin=0.235170
- `pass` `not_cost_or_search_gaming`: composition_cost_delta=-0.045838, cost_normalized_utility_margin=0.218098
- `pass` `risk_orders_realized_failures`: monotone=True, risk_breach_corr=0.970670, risk_seam_corr=0.960829
- `pass` `calibration_improves_over_strongest`: risk_calibration_error_delta=-0.010549
- `pass` `positive_all_task_regime_slices`: success=42/42, utility=42/42
- `pass` `paired_utility_win_rate_ge_0_80`: utility_pair_win_rate=0.855060
- `pass` `oracle_gap_visible`: oracle_success_gap=0.10796130952380956, oracle_utility_gap=0.2516057890625
- `pass` `failure_cases_ge_24`: failure_case_count=24

## Key Metrics

- Strongest non-oracle baseline: `proposed_energy_landscape_composer_v4_1`.
- Paired hard rows: `13440`.
- Utility pair win rate: `0.855060`.
- Abstention delta: `+0.006485`.
- Composition cost delta: `-0.045838`.
- Cost-normalized utility margin: `+0.218098`.
- Risk-breach correlation: `0.970670`.
- Risk-seam-failure correlation: `0.960829`.
- Task-regime positive margins: `42/42` success, `42/42` utility.
- Oracle gap: `+0.107961` success, `+0.251606` utility.

## Risk Bins

- bin `1` rows `2688`: predicted `0.070933`, realized breach `0.067285`
- bin `2` rows `2688`: predicted `0.089837`, realized breach `0.084530`
- bin `3` rows `2688`: predicted `0.099162`, realized breach `0.091963`
- bin `4` rows `2688`: predicted `0.109698`, realized breach `0.101127`
- bin `5` rows `2688`: predicted `0.141822`, realized breach `0.130510`

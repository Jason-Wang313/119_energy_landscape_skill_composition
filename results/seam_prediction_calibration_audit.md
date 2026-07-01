# Seam Prediction Calibration Audit

Passed: `true`.
Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.

## Summary

- Proposed rows: `13440`.
- Proposed ECE10: `0.007207`.
- Strongest-baseline ECE10: `0.014790`.
- Proposed max bin gap: `0.012758`.
- Mean predicted risk / realized breach: `0.102290` / `0.095083`.
- Risk-breach correlation / Spearman: `0.970670` / `0.950331`.
- Highest-minus-lowest risk decile breach: `0.079525`.
- Highest-minus-lowest risk decile utility: `-0.251150`.

## Checks

- `pass` `not_external_evidence_declared`: local hard-slice predictive-validity audit only
- `pass` `proposed_rows_ge_10000`: rows=13440
- `pass` `ece_10_le_0_010`: ece10=0.007207
- `pass` `max_bin_gap_le_0_015`: max_gap=0.012758
- `pass` `mean_risk_gap_le_0_010`: mean_predicted=0.102290, mean_realized=0.095083
- `pass` `risk_breach_correlation_ge_0_90`: corr=0.970670
- `pass` `risk_breach_spearman_ge_0_90`: spearman=0.950331
- `pass` `decile_breach_monotone`: 10/10 ordered deciles have nondecreasing realized breach
- `pass` `highest_lowest_decile_breach_gap_ge_0_07`: breach_delta=0.079525
- `pass` `highest_lowest_decile_utility_delta_le_minus_0_20`: utility_delta=-0.251150
- `pass` `ece_improves_over_strongest_baseline_by_0_005`: delta=-0.007583, baseline_ece=0.014790
- `pass` `accept_risk_lower_than_abstain_risk_by_0_03`: accept=0.080526, abstain=0.125391

## Risk Deciles

- bin `1` rows `1344` predicted `0.063325` realized `0.060617` gap `0.002708` utility `0.990435`
- bin `2` rows `1344` predicted `0.078540` realized `0.073954` gap `0.004587` utility `0.953159`
- bin `3` rows `1344` predicted `0.087220` realized `0.082181` gap `0.005039` utility `0.926795`
- bin `4` rows `1344` predicted `0.092454` realized `0.086879` gap `0.005575` utility `0.923787`
- bin `5` rows `1344` predicted `0.096946` realized `0.090136` gap `0.006810` utility `0.917029`
- bin `6` rows `1344` predicted `0.101377` realized `0.093789` gap `0.007588` utility `0.876816`
- bin `7` rows `1344` predicted `0.106327` realized `0.098437` gap `0.007890` utility `0.899309`
- bin `8` rows `1344` predicted `0.113069` realized `0.103816` gap `0.009252` utility `0.851416`
- bin `9` rows `1344` predicted `0.130743` realized `0.120877` gap `0.009866` utility `0.804673`
- bin `10` rows `1344` predicted `0.152901` realized `0.140142` gap `0.012758` utility `0.739286`

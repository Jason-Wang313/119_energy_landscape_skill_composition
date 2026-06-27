# Holdout Robustness Audit

Passed: `true`.
This is local withheld-slice evidence only; it is not real robot or high-fidelity external validation.

Hard rows per method: `13440`.
Worst task-regime success delta: `+0.02188`.
Worst task-regime utility delta: `+0.17256`.
Worst hash-fold utility delta: `+0.22706`.
Worst hash-fold seed wins: `10/10`.

## Partition Summary

| Partition | Groups | Utility-positive | Min success diff | Min utility diff | Min seed wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| `task` | 6 | 6/6 | +0.05446 | +0.20456 | 10/10 |
| `regime` | 7 | 7/7 | +0.07396 | +0.21658 | 10/10 |
| `split` | 4 | 4/4 | +0.07738 | +0.22918 | 10/10 |
| `task_regime` | 42 | 42/42 | +0.02188 | +0.17256 | 8/10 |
| `hash_fold` | 5 | 5/5 | +0.07610 | +0.22706 | 10/10 |

## Checks

- `pass` `not_external_evidence_declared`: local holdout audit only
- `pass` `hard_rows_per_method_ge_10000`: rows=13440
- `pass` `task_holdouts_positive_utility`: 6/6
- `pass` `regime_holdouts_positive_utility`: 7/7
- `pass` `split_holdouts_positive_utility`: 4/4
- `pass` `task_regime_holdouts_positive_utility`: 42/42
- `pass` `task_regime_holdouts_positive_success`: 42/42
- `pass` `hash_folds_positive_utility`: 5/5
- `pass` `hash_fold_seed_wins_ge_8`: min_seed_wins=10
- `pass` `worst_task_regime_success_delta_ge_0_015`: +0.02188
- `pass` `worst_task_regime_utility_delta_ge_0_150`: +0.17256
- `pass` `worst_hash_fold_utility_delta_ge_0_150`: +0.22706
- `pass` `oracle_gap_remains_positive`: +0.19422

# External Local Dry-Run Metrics

Passed: `true`.
Not evidence: `true`.
Manifest: `external_validation/local_dry_run/manifest.json`.
Records: `1440`.
Task families: `4`.
Strongest dry-run baseline: `proposed_energy_landscape_composer_v4_1`.

This dry run converts frozen local CSV rows into the external JSONL schema and recomputes metrics from those logs. It is a plumbing and reproducibility check only. It is not real robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for `external_validation/manifest.json`.

## Metric Summary

- External-style success margin: `0.125`.
- External-style utility margin: `0.2718227833333333`.
- Paired win rate: `0.875`.
- Fixed-risk coverage: `0.6166666666666667`.
- Fixed-risk breach: `0.0`.
- Positive task families: `4/4`.

## Threshold Checks

- `pass` external_success_margin: value=0.125, threshold=0.05
- `pass` external_utility_margin: value=0.2718227833333333, threshold=0.08
- `pass` paired_win_rate: value=0.875, threshold=0.7
- `pass` fixed_risk_coverage: value=0.6166666666666667, threshold=0.55
- `pass` fixed_risk_breach: value=0.0, threshold=0.02
- `pass` positive_task_families: value=4, threshold=3

## Schema Errors

- none

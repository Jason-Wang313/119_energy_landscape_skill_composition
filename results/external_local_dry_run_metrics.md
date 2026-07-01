# External Local Dry-Run Metrics

Passed: `true`.
Not evidence: `true`.
Manifest: `external_validation/local_dry_run/manifest.json`.
Records: `20640`.
Task families: `4`.
Strongest dry-run baseline: `proposed_energy_landscape_composer_v4_1`.

This dry run converts frozen local CSV rows into the external JSONL schema and recomputes metrics from those logs. It is a plumbing and reproducibility check only. It is not real robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for `external_validation/manifest.json`.

## Metric Summary

- External-style success margin: `0.08313953488372094`.
- External-style utility margin: `0.23096796860465119`.
- Paired win rate: `0.8622093023255814`.
- Fixed-risk coverage: `0.6098837209302326`.
- Fixed-risk breach: `0.0`.
- Positive task families: `4/4`.

## Threshold Checks

- `pass` external_success_margin: value=0.08313953488372094, threshold=0.05
- `pass` external_utility_margin: value=0.23096796860465119, threshold=0.08
- `pass` paired_win_rate: value=0.8622093023255814, threshold=0.7
- `pass` fixed_risk_coverage: value=0.6098837209302326, threshold=0.55
- `pass` fixed_risk_breach: value=0.0, threshold=0.02
- `pass` positive_task_families: value=4, threshold=3
- `pass` external_success_margin_confidence_gate: estimate=0.08313953488372093, ci95=[0.053488372093023255, 0.11104651162790698], threshold=0.05, direction=greater_or_equal
- `pass` external_utility_margin_confidence_gate: estimate=0.23096796860465116, ci95=[0.20419821783430253, 0.258358562238372], threshold=0.08, direction=greater_or_equal
- `pass` paired_win_rate_confidence_gate: estimate=0.8622093023255814, ci95=[0.8459302325581395, 0.8773255813953489], threshold=0.7, direction=greater_or_equal
- `pass` fixed_risk_coverage_confidence_gate: estimate=0.6098837209302326, ci95=[0.5860319767441861, 0.6337209302325582], threshold=0.55, direction=greater_or_equal
- `pass` fixed_risk_breach_confidence_gate: estimate=0.0, ci95=[0.0, 0.0], threshold=0.02, direction=less_or_equal
- `pass` positive_task_families_confidence_gate: value=4, threshold=3

## Schema Errors

- none

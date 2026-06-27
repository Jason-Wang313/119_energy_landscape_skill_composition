# External Statistical Analysis Plan

Not evidence: `true`.
Analysis locked before collection: `true`.
Primary method: `barrier_certified_energy_composer_v5`.
Planned records: `1440`.

This plan pre-registers how the independent external validation logs will be analyzed. It does not create robot or high-fidelity simulator evidence.

## Primary Hypotheses

- `H1_success_margin`: `external_success_margin` greater_or_equal `0.05`.
- `H2_utility_margin`: `external_utility_margin` greater_or_equal `0.08`.
- `H3_paired_win_rate`: `paired_win_rate` greater_or_equal `0.7`.
- `H4_fixed_risk_coverage`: `fixed_risk_coverage` greater_or_equal `0.55`.
- `H5_fixed_risk_breach`: `fixed_risk_breach` less_or_equal `0.02`.
- `H6_task_family_coverage`: `positive_task_families` greater_or_equal `3`.

## Strict Gates

- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Exclusion Policy

Unit: `paired_reset_method_panel`.

Allowed before unblinding:
- platform qualification failure before collection
- operator safety stop documented before outcome inspection
- corrupt JSONL line that fails schema validation
- missing or hash-mismatched video/config/checkpoint artifact
- incomplete paired method panel detected by strict pairing audit

Forbidden:
- dropping only the proposed method or only a weak baseline from a paired panel
- dropping failures after viewing method identity or outcome
- changing task families, methods, thresholds, or risk budget after collection starts
- using local dry-run records, template configs, scaffold adapters, placeholder videos, or hand-entered metrics as evidence

## Required Reporting

- external_success_margin
- external_utility_margin
- paired_win_rate
- fixed_risk_coverage
- fixed_risk_breach
- positive_task_families
- strongest_external_baseline
- per-task success margins
- strict gate outputs
- all exclusions with reasons and timestamps
- oracle gap as post hoc upper bound

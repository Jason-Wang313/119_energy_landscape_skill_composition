# Adapter Scaffold: oracle_basin_composer

Not external evidence: `true`.
Scaffold only: `true`.

Role: post hoc upper bound only.
Required entrypoint: `evaluate_oracle_upper_bound`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- true basin/barrier information after rollout or from simulator ground truth

## Forbidden Advantages

- deployment decision use
- selection as strongest non-oracle baseline

# Adapter Scaffold: energy_compatibility_heuristic

Not external evidence: `true`.
Scaffold only: `true`.

Role: non-certified energy heuristic baseline.
Required entrypoint: `score_energy_compatibility`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- same energy estimates available to all non-oracle methods
- current observation

## Forbidden Advantages

- fixed-risk calibration gate
- repair memory from proposed v5

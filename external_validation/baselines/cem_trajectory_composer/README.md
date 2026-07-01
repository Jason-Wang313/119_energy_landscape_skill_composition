# Adapter Scaffold: cem_trajectory_composer

Not external evidence: `true`.
Scaffold only: `true`.

Role: trajectory-search baseline.
Required entrypoint: `optimize_handoff_with_cem`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- same rollout/simulation budget
- current observation
- shared skill library

## Forbidden Advantages

- larger compute budget
- extra reset attempts
- oracle basin state

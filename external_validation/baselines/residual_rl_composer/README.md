# Adapter Scaffold: residual_rl_composer

Not external evidence: `true`.
Scaffold only: `true`.

Role: learned residual repair baseline.
Required entrypoint: `apply_residual_repair_policy`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- residual policy checkpoint
- current observation
- shared skill library

## Forbidden Advantages

- training on evaluation resets
- post hoc barrier labels

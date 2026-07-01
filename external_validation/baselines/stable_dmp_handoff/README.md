# Adapter Scaffold: stable_dmp_handoff

Not external evidence: `true`.
Scaffold only: `true`.

Role: stable dynamics handoff baseline.
Required entrypoint: `generate_stable_handoff`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- DMP or stable dynamics parameters
- current observation
- shared skill library

## Forbidden Advantages

- oracle basin membership
- future failure labels

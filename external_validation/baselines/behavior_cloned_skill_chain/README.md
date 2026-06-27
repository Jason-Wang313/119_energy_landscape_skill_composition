# Adapter Scaffold: behavior_cloned_skill_chain

Not external evidence: `true`.
Scaffold only: `true`.

Role: demonstration sequence baseline.
Required entrypoint: `predict_demonstrated_handoff`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- demonstration policy or checkpoint
- current observation
- shared skill library

## Forbidden Advantages

- v5 diagnostic labels
- post hoc oracle repair
- unpaired demonstration resets

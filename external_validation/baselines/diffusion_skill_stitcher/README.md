# Adapter Scaffold: diffusion_skill_stitcher

Not external evidence: `true`.
Scaffold only: `true`.

Role: generative handoff sampler baseline.
Required entrypoint: `sample_handoff_state`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- diffusion/generative model checkpoint
- current observation
- shared skill library

## Forbidden Advantages

- v5 accept/reject labels unless explicitly trained on the same data as all baselines

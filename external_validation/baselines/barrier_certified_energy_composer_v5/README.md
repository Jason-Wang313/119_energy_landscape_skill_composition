# Adapter Scaffold: barrier_certified_energy_composer_v5

Not external evidence: `true`.
Scaffold only: `true`.

Role: primary method.
Required entrypoint: `compose_with_barrier_certified_seam_model`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- terminal samples
- basin posterior
- barrier score
- descent continuity
- calibrated risk

## Forbidden Advantages

- post hoc oracle basin truth
- unpaired reset retries

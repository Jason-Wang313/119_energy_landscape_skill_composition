# Adapter Scaffold: greedy_module_sequence

Not external evidence: `true`.
Scaffold only: `true`.

Role: open-loop skill graph baseline.
Required entrypoint: `select_next_skill_and_handoff`.

Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.

## Allowed Inputs

- skill library
- current observation
- task graph
- shared reset metadata

## Forbidden Advantages

- energy seam labels
- post hoc basin truth
- extra reset attempts

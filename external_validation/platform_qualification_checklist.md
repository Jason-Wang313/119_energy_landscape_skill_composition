# Platform Qualification Checklist

Not external evidence: `true`.

Purpose: decide whether a real robot or simulator is credible enough to produce the external validation layer for Paper 119 without relying on Haonan Chen or any target collaborator.

## Required Platform Properties

- deterministic paired reset: the same scene, seed, skill pair, and initial-state hash can be replayed for every method.
- contact and dynamics fidelity: friction, compliance, contacts, object properties, timing, and actuation limits are documented well enough that seam failures are physically meaningful.
- shared skill library: every non-oracle method composes the same primitive skills, with the same observations and action spaces.
- video export: every episode can be linked to a video path that the strict validator can check.
- raw state logging: terminal samples, basin estimates, barrier scores, descent-continuity scores, decisions, repairs, outcomes, and failure labels are emitted before aggregation.
- compute-budget control: every method receives the same wall-clock or simulator-query budget.
- no privileged state: non-oracle baselines cannot read hidden future outcomes, oracle basin labels, post hoc success, or simulator internals unavailable to all methods.
- artifact hashes: code, configs, skill policies, checkpoints, logs, and videos have SHA256 hashes or are otherwise release-pinned.
- fidelity acceptance file: `external_validation/fidelity_acceptance.json` is filled from the template, declared in the manifest, and passes `python scripts\audit_external_fidelity_acceptance.py --strict`.

## Disqualifying Shortcuts

- treating local CSV rows as external validation.
- counting scaffold adapters or template configs as independent implementations.
- hand-entering aggregate metrics without JSONL logs.
- accepting videos that cannot be tied back to run IDs.
- changing the skill library or observation interface per baseline.
- using oracle basin labels inside non-oracle methods.
- tuning the fixed-risk budget after seeing external outcomes.
- hiding abstentions, repairs, or failed seam decisions.

## Minimum Evidence Package

- `external_validation/manifest.json` with the selected route and all task/method artifacts.
- one JSONL log per task family, following `external_validation/log_schema_v1.json`.
- real config files under `external_validation/configs/`, not template files.
- independent non-oracle adapter implementations declared in the manifest.
- accepted platform-fidelity provenance under `external_validation/fidelity_acceptance.json`.
- representative videos for successes, failures, abstentions, repairs, and oracle-gap cases.
- release artifacts for code, configs, logs, videos, and checkpoints or checkpoint hashes.

## Pass Condition

The platform is qualified only when:

- `python scripts\validate_external_configs.py --strict` passes.
- `python scripts\audit_external_fidelity_acceptance.py --strict` passes.
- `python scripts\validate_external_adapters.py --strict` passes.
- `python scripts\validate_external_rollouts.py --strict --write-results --check-video-paths` passes.
- `python scripts\audit_external_evidence.py --strict` passes.

Until then, the current external-validation directory is an execution packet, not evidence.

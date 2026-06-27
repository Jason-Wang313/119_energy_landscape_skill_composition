# ManiSkill Reference Collection Preflight Audit

Passed: `true`.
Not evidence: `true`.
Backend module: `external_validation/runner/maniskill_reference_backend.py`.
Reference backend contract ready: `true`.
Collection ready: `false`.
Collection blocking missing items: `1`.

This audit runs the strict backend-contract and explicit collection-preflight checks for the tracked ManiSkill reference backend without writing rollout logs, videos, manifests, or evidence. It documents that backend/module/config/run-id/alias preflight can reach the fidelity-acceptance gate, while official external collection remains blocked until real platform fidelity provenance is accepted.

## Blocking Missing

- fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'

## Checks

- `pass` `reference_backend_contract_strict_passes`: passed=True, actual_backend_ready=True
- `pass` `reference_backend_collection_preflight_reaches_fidelity_gate`: blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `official_collection_still_not_ready`: no manifest is written and fidelity acceptance remains required
- `pass` `default_audits_are_not_overwritten`: out=results/maniskill_reference_collection_preflight_audit.json

# External Operator Packet

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.

This packet is the independent operator entry point for turning the current non-evidence validation plan into real robot or accepted high-fidelity simulator evidence. It does not replace the strict external audits.

## Go / No-Go

- No-go: do not start collection until every pre-collection blocker below is cleared by the strict preflight gate.

## Pre-Collection Blockers

- backend_module_ready: --backend-module is required before actual collection
- fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- alias_unsealing_explicit: unsealed_alias_map=False
- run_id_specific: run_id='paper119_external_validation_run'

## Commands

Materialize real configs after platform selection:

```powershell
python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write
```

Strict backend qualification gate:

```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
```

Strict pre-collection gate:

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```

Actual collection command after the strict gate passes:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

Post-collection strict gates:

- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Operator Actions

- `platform_onboarding`: Onboard the public simulator platform
- `backend_module`: Select a non-template backend module
- `backend_integration_packet`: Use the backend integration packet as the public-simulator backend checklist
- `real_task_configs`: Create real manifest-declared task configs
- `config_manifest_packet`: Use the config manifest packet as the task-config evidence checklist
- `rollout_evidence_packet`: Use the rollout evidence packet as the raw-log evidence checklist
- `platform_fidelity`: Fill platform fidelity acceptance with real provenance
- `pilot_smoke_packet`: Run a quarantined first-panel backend smoke test
- `fidelity_provenance_packet`: Use the fidelity provenance packet as the platform acceptance checklist
- `alias_unseal`: Unseal method aliases only after configs, implementations, and run plan are frozen
- `specific_run_id`: Use a specific immutable external run id
- `real_method_implementations`: Replace scaffold-only methods with real non-oracle implementations or wrappers
- `method_implementation_packet`: Use the method implementation packet as the non-oracle work-order checklist
- `run_collection`: Collect paired-reset external rollouts
- `manifest_and_release`: Build the real manifest and hash-lock release artifacts
- `strict_rollout_recompute`: Recompute external metrics from raw JSONL logs
- `strict_adapter_evidence`: Audit independent method evidence after the manifest is real
- `final_strict_gate`: Run the final strict external-evidence gate

## Checks

- `pass` `acquisition_packet_ready`: passed=True, strict_evidence_ready=False
- `pass` `collection_preflight_fail_closed`: collection_ready=False, blocking_missing_count=4
- `pass` `operator_actions_cover_start_to_finish`: missing=[]
- `pass` `operator_action_titles_present`: missing_titles=[]
- `pass` `config_materializer_is_guarded`: write_enabled=False, task_count=4
- `pass` `backend_contract_gate_is_explicit`: python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
- `pass` `backend_action_runs_contract_before_readiness`: python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
python scripts\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
- `pass` `strict_collection_command_is_explicit`: python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
- `pass` `post_collection_gates_cover_evidence`: commands=8
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `packet_artifacts_exist`: runbook, runner, blinded sheet, alias map, platform checklist, and config schema

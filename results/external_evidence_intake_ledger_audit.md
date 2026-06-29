# External Evidence Intake Ledger

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Blocking failures mapped: `37/37`.

This ledger maps every current strict external-evidence failure to the operator artifact, source packet, strict gate, and completion test that would close it. It does not create a manifest, logs, videos, checkpoints, or external validation evidence.

## Closure Groups

- `ablations`: failures `1`, source `external_validation/ablation_collection_packet.md; external_validation/ablation_collection_work_orders.csv`.
- `fidelity_acceptance`: failures `1`, source `external_validation/fidelity_provenance_packet.md; external_validation/fidelity_acceptance_draft.md; results/fidelity_acceptance_materialization_plan.md`.
- `manifest_contract`: failures `9`, source `external_validation/manifest_assembly_checklist.csv`.
- `methods_baselines`: failures `4`, source `external_validation/method_implementation_packet.md; external_validation/method_implementation_work_orders.csv; external_validation/method_reference_provenance.csv`.
- `oracle_boundary`: failures `2`, source `external_validation/manifest_template.json; docs/claim_evidence_ledger.json`.
- `pairing_release`: failures `6`, source `external_validation/manifest_assembly_checklist.csv; results/external_release_package_audit.md; results/external_pairing_integrity_audit.md`.
- `rollout_logs_videos_metrics`: failures `11`, source `external_validation/rollout_evidence_packet.md; external_validation/rollout_evidence_work_orders.csv`.
- `task_configs`: failures `3`, source `external_validation/config_manifest_packet.md; external_validation/config_manifest_work_orders.csv`.

## Strict Command Spine

```powershell
python scripts\audit_external_fidelity_acceptance.py --strict
```
```powershell
python scripts\validate_external_configs.py --strict
```
```powershell
python scripts\validate_external_adapters.py --strict
```
```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
```
```powershell
python scripts\audit_external_postcollection_seal_consistency.py
```
```powershell
python scripts\build_external_manifest.py --write --check-video-paths
```
```powershell
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
```
```powershell
python scripts\audit_external_pairing_integrity.py --strict
```
```powershell
python scripts\audit_external_release_package.py --strict
```
```powershell
python scripts\audit_external_evidence.py --strict
```

## Failure Ledger

- `manifest_exists` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `external_fidelity_acceptance_ready` -> `fidelity_acceptance`: fidelity acceptance audit reports acceptance_ready=true while strict external evidence remains false until manifest-backed rollout gates pass
- `external_adapter_contract_evidence_passed` -> `methods_baselines`: strict adapter evidence audit passes; scaffolds/reference adapters are not counted as evidence, and checkpoint_or_config_hash values match real checkpoint_or_config_path artifacts rather than implementation source
- `external_config_evidence_passed` -> `task_configs`: strict config evidence audit passes with manifest-declared configs and matching hashes
- `manifest_version` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `manifest_declares_log_schema` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `validation_route` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `shared_skill_library` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `same_initial_states` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `same_observation_interface` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `same_compute_budget` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `paired_resets` -> `manifest_contract`: manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes
- `valid_task_families` -> `task_configs`: strict config evidence audit passes with manifest-declared configs and matching hashes
- `episodes_per_method` -> `task_configs`: strict config evidence audit passes with manifest-declared configs and matching hashes
- `episode_log_schema` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `task_video_dirs` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `required_methods` -> `methods_baselines`: strict adapter evidence audit passes; scaffolds/reference adapters are not counted as evidence, and checkpoint_or_config_hash values match real checkpoint_or_config_path artifacts rather than implementation source
- `independent_method_implementations` -> `methods_baselines`: strict adapter evidence audit passes; scaffolds/reference adapters are not counted as evidence, and checkpoint_or_config_hash values match real checkpoint_or_config_path artifacts rather than implementation source
- `external_success_margin` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `external_utility_margin` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `paired_win_rate` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `fixed_risk_breach` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `fixed_risk_coverage` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `positive_task_family_coverage` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `external_rollout_metrics_passed` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `external_rollout_confidence_gates_passed` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `external_pairing_integrity_ready` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `external_release_package_ready` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `manifest_metrics_match_rollout` -> `rollout_logs_videos_metrics`: external rollout metric validator passes and manifest metrics match recomputed rollout metrics
- `oracle_reported` -> `oracle_boundary`: oracle_reported=true and oracle_stronger_or_saturated_explained is explicitly set in manifest metrics
- `oracle_boundary` -> `oracle_boundary`: oracle_reported=true and oracle_stronger_or_saturated_explained is explicitly set in manifest metrics
- `external_ablations` -> `ablations`: external evidence audit reports all five manifest.ablations.* flags true with manifest-declared external ablation evidence
- `release_code` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `release_configs` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `release_logs` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `release_videos` -> `pairing_release`: pairing_ready=true and release_package_ready=true under strict audits
- `release_checkpoints` -> `methods_baselines`: strict adapter evidence audit passes; scaffolds/reference adapters are not counted as evidence, and checkpoint_or_config_hash values match real checkpoint_or_config_path artifacts rather than implementation source

## Checks

- `pass` `ledger_is_non_evidence_and_fail_closed`: writes only ledger/audit files and keeps strict_external_evidence_ready=false
- `pass` `strict_external_evidence_is_currently_missing`: submission_ready=False, failures=37
- `pass` `every_blocking_failure_is_mapped`: unmapped=[], mapped=37, failures=37
- `pass` `all_required_closure_groups_present`: missing=[]
- `pass` `source_packets_loaded`: collection, rollout, config, method, ablation, and fidelity packets loaded
- `pass` `manifest_template_declares_expected_evidence_fields`: manifest template has version, tasks, methods, release_artifacts, and ablations
- `pass` `strict_command_spine_covers_final_evidence_path`: strict command spine covers fidelity, configs, adapters, collection, manifest, rollouts, pairing, release, and final evidence
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence

# External Postcollection Seal Consistency Audit

Passed: `true`.
Not evidence: `true`.
Seal consistency ready: `false`.
Ready for manifest promotion: `false`.
Strict external evidence ready: `false`.
Postcollection seal ready: `false`.
Expected records: `1440`.
Current JSONL records: `0`.
Current rollout videos: `0`.
Matched hashes: `11`.

This audit recomputes the postcollection evidence seal before manifest promotion. It is a fail-closed integrity gate, not external validation evidence.

## Drift Summary

- Mismatched hashes: `[]`
- Missing sealed paths: `[]`
- Unexpectedly present paths: `[]`
- Extra official artifacts: `[]`
- Invalid log artifacts: `[]`
- Invalid video artifacts: `[]`

## Strict Command Sequence

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
python scripts\validate_external_configs.py --strict
```
```powershell
python scripts\validate_external_adapters.py --strict
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

## Checks

- `pass` `postcollection_seal_artifacts_loaded`: seal_version='external_postcollection_evidence_seal_v1', audit_version='external_postcollection_evidence_seal_audit_v1', audit_passed=True
- `pass` `consistency_gate_is_non_evidence_and_fail_closed`: seal_ready=False, consistency_ready=False, strict_external_evidence=False
- `pass` `sealed_hashes_recompute_without_drift`: matched=11, mismatched=[], missing=[], unexpected=[]
- `pass` `no_unsealed_official_artifacts_before_manifest_promotion`: extra=[], invalid_logs=[], invalid_videos=[]
- `pass` `manifest_promotion_requires_ready_seal_and_consistency`: seal_ready=False, seal_manifest_ready=False, consistency_ready=False
- `pass` `current_counts_match_default_or_ready_state`: expected=1440, records=0, videos=0, invalid_json=0
- `pass` `no_real_manifest_written_before_seal_consistency`: external_validation/manifest.json absent before manifest promotion
- `pass` `strict_sequence_places_consistency_after_seal_before_manifest`: python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
python scripts\audit_external_postcollection_seal_consistency.py
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_evidence.py --strict
- `pass` `consistency_gate_references_rollout_pairing_release_final_gates`: python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
python scripts\audit_external_postcollection_seal_consistency.py
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_evidence.py --strict

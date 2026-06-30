# External Operator Return Package Contract

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Current preflight blockers: `56`.
Expected total JSONL records: `1440`.
Return items: `28`.

This contract defines the exact artifact classes an independent operator must return after collection. It does not create evidence and does not write `external_validation/manifest.json`.

## Required Return Items

### fidelity_acceptance

- Category: `global`
- Path: `external_validation/fidelity_acceptance.json`
- Required count: `1`
- Hash requirement: materialized with accepted collection commit and skill-library hash
- Acceptance: accepted fidelity, independent operator, real/high-fidelity platform, render-backed videos, paired replay, and known limitations are signed off
- Strict gate: `python scripts\audit_external_fidelity_acceptance.py --strict`

### precollection_freeze_receipt

- Category: `global`
- Path: `external_validation/precollection_freeze_receipt.json`
- Required count: `1`
- Hash requirement: receipt hashes operator sheet, alias map, configs, candidates, runner, code commit, and skill library before collection
- Acceptance: freeze receipt exists before official collection and matches the accepted run id/operator/machine
- Strict gate: `python scripts\build_external_precollection_freeze_receipt.py ...`

### postcollection_evidence_seal

- Category: `global`
- Path: `external_validation/postcollection_evidence_seal.json`
- Required count: `1`
- Hash requirement: seal hashes raw logs, videos, configs, precollection receipt, and operator metadata after collection
- Acceptance: postcollection seal exists and seal consistency recomputes with no drift before manifest promotion
- Strict gate: `python scripts\audit_external_postcollection_seal_consistency.py`

### manifest

- Category: `global`
- Path: `external_validation/manifest.json`
- Required count: `1`
- Hash requirement: manifest declares release_artifacts for code, configs, logs, videos, and checkpoints
- Acceptance: manifest is written only after postcollection seal consistency, then all strict evidence gates pass
- Strict gate: `python scripts\build_external_manifest.py --write --check-video-paths`

### release_artifacts

- Category: `global`
- Path: `external_validation/manifest.json:release_artifacts`
- Required count: `5`
- Hash requirement: release_artifacts.code/configs/logs/videos/checkpoints all carry valid SHA256 values
- Acceptance: release package audit and final external evidence audit recompute all release hashes
- Strict gate: `python scripts\audit_external_release_package.py --strict`

### peg_place_regrasp_config

- Category: `task_config`
- Path: `external_validation/configs/peg_place_regrasp.json`
- Required count: `1`
- Hash requirement: manifest.tasks[].config_hash must equal SHA256(config_path)
- Acceptance: strict config evidence accepts this manifest-declared config and rejects templates/local dry-run configs
- Strict gate: `python scripts\validate_external_configs.py --strict`

### peg_place_regrasp_jsonl

- Category: `task_log`
- Path: `external_validation/logs/peg_place_regrasp.jsonl`
- Required count: `360`
- Hash requirement: release_artifacts.logs must include this JSONL with SHA256
- Acceptance: JSONL parses, follows log_schema_v1, and contains at least 360 rows for 12 methods x 30 episodes
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### peg_place_regrasp_videos

- Category: `task_video_dir`
- Path: `external_validation/videos/peg_place_regrasp`
- Required count: `360`
- Hash requirement: release_artifacts.videos must include all manifest-declared MP4 files with SHA256
- Acceptance: videos are render-backed MP4s, unique, non-placeholder, non-diagnostic, and referenced by official JSONL rows
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### drawer_to_pick_transfer_config

- Category: `task_config`
- Path: `external_validation/configs/drawer_to_pick_transfer.json`
- Required count: `1`
- Hash requirement: manifest.tasks[].config_hash must equal SHA256(config_path)
- Acceptance: strict config evidence accepts this manifest-declared config and rejects templates/local dry-run configs
- Strict gate: `python scripts\validate_external_configs.py --strict`

### drawer_to_pick_transfer_jsonl

- Category: `task_log`
- Path: `external_validation/logs/drawer_to_pick_transfer.jsonl`
- Required count: `360`
- Hash requirement: release_artifacts.logs must include this JSONL with SHA256
- Acceptance: JSONL parses, follows log_schema_v1, and contains at least 360 rows for 12 methods x 30 episodes
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### drawer_to_pick_transfer_videos

- Category: `task_video_dir`
- Path: `external_validation/videos/drawer_to_pick_transfer`
- Required count: `360`
- Hash requirement: release_artifacts.videos must include all manifest-declared MP4 files with SHA256
- Acceptance: videos are render-backed MP4s, unique, non-placeholder, non-diagnostic, and referenced by official JSONL rows
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### door_open_navigation_config

- Category: `task_config`
- Path: `external_validation/configs/door_open_navigation.json`
- Required count: `1`
- Hash requirement: manifest.tasks[].config_hash must equal SHA256(config_path)
- Acceptance: strict config evidence accepts this manifest-declared config and rejects templates/local dry-run configs
- Strict gate: `python scripts\validate_external_configs.py --strict`

### door_open_navigation_jsonl

- Category: `task_log`
- Path: `external_validation/logs/door_open_navigation.jsonl`
- Required count: `360`
- Hash requirement: release_artifacts.logs must include this JSONL with SHA256
- Acceptance: JSONL parses, follows log_schema_v1, and contains at least 360 rows for 12 methods x 30 episodes
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### door_open_navigation_videos

- Category: `task_video_dir`
- Path: `external_validation/videos/door_open_navigation`
- Required count: `360`
- Hash requirement: release_artifacts.videos must include all manifest-declared MP4 files with SHA256
- Acceptance: videos are render-backed MP4s, unique, non-placeholder, non-diagnostic, and referenced by official JSONL rows
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### cable_route_insert_config

- Category: `task_config`
- Path: `external_validation/configs/cable_route_insert.json`
- Required count: `1`
- Hash requirement: manifest.tasks[].config_hash must equal SHA256(config_path)
- Acceptance: strict config evidence accepts this manifest-declared config and rejects templates/local dry-run configs
- Strict gate: `python scripts\validate_external_configs.py --strict`

### cable_route_insert_jsonl

- Category: `task_log`
- Path: `external_validation/logs/cable_route_insert.jsonl`
- Required count: `360`
- Hash requirement: release_artifacts.logs must include this JSONL with SHA256
- Acceptance: JSONL parses, follows log_schema_v1, and contains at least 360 rows for 12 methods x 30 episodes
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### cable_route_insert_videos

- Category: `task_video_dir`
- Path: `external_validation/videos/cable_route_insert`
- Required count: `360`
- Hash requirement: release_artifacts.videos must include all manifest-declared MP4 files with SHA256
- Acceptance: videos are render-backed MP4s, unique, non-placeholder, non-diagnostic, and referenced by official JSONL rows
- Strict gate: `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`

### greedy_module_sequence

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/greedy_module_sequence.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 4158524DEB92394F50D7550D295D67860F9D2D92F4C1D06B13FA668B1F1F7DFA
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### behavior_cloned_skill_chain

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/behavior_cloned_skill_chain.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal BCFB1DAAE14267E91CC9FE9AA08083FFF90625B255C81FA74E47647018A969C2
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### option_graph_planner

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/option_graph_planner.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal DE3E0198432E4CF42F017C473EED3CF889B60FE5B85B642C55C44A1FF02410AD
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### tamp_feasibility_screen

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/tamp_feasibility_screen.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 18F846DB89B1C852DF378A3ED9A205389141AE2C56D0D9E27210401973620EFB
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### stable_dmp_handoff

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/stable_dmp_handoff.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 0AD7209C0E2023CE462624C5A10EB09AC5EA7A249D86CA47A4EBC20F852639EF
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### diffusion_skill_stitcher

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/diffusion_skill_stitcher.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 4F44159059554664F238B144C1D65395CDE4417F89308ABD8C3DC09EDB02165B
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### cem_trajectory_composer

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/cem_trajectory_composer.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal BA1A268A3FBADB9E86286B11B6B9E593BEFB448586493CFBB4CDFDE8C6661C99
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### residual_rl_composer

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/residual_rl_composer.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 4A0CE8A9FD2BE847325029A688ED912635342D4F0159FF454828FA228C5F302F
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### energy_compatibility_heuristic

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/energy_compatibility_heuristic.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal ED6FB2887EFB80342705CA1528597B8AE4FB890C28B285660FD9C0443FA0903C
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### proposed_energy_landscape_composer_v4_1

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/proposed_energy_landscape_composer_v4_1.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 7331767D0D76C6507C4F586F2FD093ADAF7FF0DF07CAB50A1A4FD164D8CEABB3
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

### barrier_certified_energy_composer_v5

- Category: `method_artifact`
- Path: `external_validation/method_config_candidates/barrier_certified_energy_composer_v5.json`
- Required count: `1`
- Hash requirement: manifest.methods[].checkpoint_or_config_hash must equal 0DF7FB36D51A1866B46716F0601E46E81B815849675D0C6CAB8FB4037B801872
- Acceptance: manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, and official JSONL policy_or_config_hash values that match the manifest
- Strict gate: `python scripts\validate_external_adapters.py --strict`

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
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <accepted_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
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
```powershell
python scripts\audit_submission_readiness_gap.py
```

## Checks

- `pass` `contract_is_non_evidence`: contract lists required returned artifacts only
- `pass` `preflight_blockers_are_current`: evidence_ready=False, blockers=56, expected_records=1440
- `pass` `global_items_cover_manifest_fidelity_seals_release`: global_items=5
- `pass` `task_items_cover_all_manifest_tasks`: tasks=4, task_items=12, expected_records=1440
- `pass` `method_items_cover_non_oracle_methods`: methods=11, method_items=11
- `pass` `candidate_method_hashes_bound`: candidate_hashes=11/11
- `pass` `strict_command_spine_covers_return_to_final_audit`: commands=14
- `pass` `intake_ledger_and_release_bundle_are_current_sources`: intake_passed=True, release_state='READY_TO_SEND_OPERATOR_PACKAGE'
- `pass` `readiness_boundary_preserved`: satisfied=17, blocking=4
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence

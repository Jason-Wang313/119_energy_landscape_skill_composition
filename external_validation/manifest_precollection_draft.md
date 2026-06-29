# External Precollection Manifest Draft

Not evidence: `true`.
Draft only: `true`.
Strict external evidence ready: `false`.
Official manifest exists: `false`.

This draft records the manifest fields that can be safely prefilled before collection, especially prepared task-config hashes. It is not `external_validation/manifest.json`, it is not submission evidence, and it cannot promote itself to evidence without the strict cutover commands below.

## Prepared Task Configs

- `peg_place_regrasp`: `external_validation/configs/peg_place_regrasp.json` sha256 `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`; strict-if-manifest-declared `true`
- `drawer_to_pick_transfer`: `external_validation/configs/drawer_to_pick_transfer.json` sha256 `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`; strict-if-manifest-declared `true`
- `door_open_navigation`: `external_validation/configs/door_open_navigation.json` sha256 `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`; strict-if-manifest-declared `true`
- `cable_route_insert`: `external_validation/configs/cable_route_insert.json` sha256 `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`; strict-if-manifest-declared `true`

## Blocking Method Gaps

- `greedy_module_sequence`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `behavior_cloned_skill_chain`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `option_graph_planner`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `tamp_feasibility_screen`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `stable_dmp_handoff`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `diffusion_skill_stitcher`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `cem_trajectory_composer`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `residual_rl_composer`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `energy_compatibility_heuristic`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `proposed_energy_landscape_composer_v4_1`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`
- `barrier_certified_energy_composer_v5`: missing `['implementation_path', 'checkpoint_or_config_path', 'checkpoint_or_config_hash']`

## Blocking Rollout Artifacts

- `peg_place_regrasp` `jsonl_log`: `external_validation/logs/peg_place_regrasp.jsonl`
- `peg_place_regrasp` `video_dir`: `external_validation/videos/peg_place_regrasp`
- `drawer_to_pick_transfer` `jsonl_log`: `external_validation/logs/drawer_to_pick_transfer.jsonl`
- `drawer_to_pick_transfer` `video_dir`: `external_validation/videos/drawer_to_pick_transfer`
- `door_open_navigation` `jsonl_log`: `external_validation/logs/door_open_navigation.jsonl`
- `door_open_navigation` `video_dir`: `external_validation/videos/door_open_navigation`
- `cable_route_insert` `jsonl_log`: `external_validation/logs/cable_route_insert.jsonl`
- `cable_route_insert` `video_dir`: `external_validation/videos/cable_route_insert`

## Promotion Requirements

- accepted fidelity acceptance file from an independent operator
- manifest-declared JSONL logs and render-backed videos
- manifest-declared non-oracle implementation/checkpoint hashes
- release artifact hashes for code, configs, logs, videos, and checkpoints
- strict rollout, pairing, config, adapter, release, and evidence gates passing

## Cutover Commands

```powershell
python scripts\build_external_precollection_manifest_draft.py
```
```powershell
python scripts\materialize_fidelity_acceptance.py --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --confirm-code-commit <commit> --confirm-skill-library-hash <sha256> --write
```
```powershell
python scripts\audit_external_fidelity_acceptance.py --strict
```
```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path>
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

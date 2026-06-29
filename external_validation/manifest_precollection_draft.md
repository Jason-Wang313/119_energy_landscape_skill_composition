# External Precollection Manifest Draft

Not evidence: `true`.
Draft only: `true`.
Strict external evidence ready: `false`.
Official manifest exists: `false`.

This draft records the manifest fields that can be safely prefilled before collection, especially prepared task-config hashes and candidate method-config hashes. It is not `external_validation/manifest.json`, it is not submission evidence, and it cannot promote itself to evidence without the strict cutover commands below.

## Prepared Task Configs

- `peg_place_regrasp`: `external_validation/configs/peg_place_regrasp.json` sha256 `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`; strict-if-manifest-declared `true`
- `drawer_to_pick_transfer`: `external_validation/configs/drawer_to_pick_transfer.json` sha256 `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`; strict-if-manifest-declared `true`
- `door_open_navigation`: `external_validation/configs/door_open_navigation.json` sha256 `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`; strict-if-manifest-declared `true`
- `cable_route_insert`: `external_validation/configs/cable_route_insert.json` sha256 `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`; strict-if-manifest-declared `true`

## Candidate Method Config Prefills

- `barrier_certified_energy_composer_v5`: `external_validation/method_config_candidates/barrier_certified_energy_composer_v5.json` sha256 `0DF7FB36D51A1866B46716F0601E46E81B815849675D0C6CAB8FB4037B801872`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `behavior_cloned_skill_chain`: `external_validation/method_config_candidates/behavior_cloned_skill_chain.json` sha256 `BCFB1DAAE14267E91CC9FE9AA08083FFF90625B255C81FA74E47647018A969C2`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `cem_trajectory_composer`: `external_validation/method_config_candidates/cem_trajectory_composer.json` sha256 `BA1A268A3FBADB9E86286B11B6B9E593BEFB448586493CFBB4CDFDE8C6661C99`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `diffusion_skill_stitcher`: `external_validation/method_config_candidates/diffusion_skill_stitcher.json` sha256 `4F44159059554664F238B144C1D65395CDE4417F89308ABD8C3DC09EDB02165B`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `energy_compatibility_heuristic`: `external_validation/method_config_candidates/energy_compatibility_heuristic.json` sha256 `ED6FB2887EFB80342705CA1528597B8AE4FB890C28B285660FD9C0443FA0903C`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `greedy_module_sequence`: `external_validation/method_config_candidates/greedy_module_sequence.json` sha256 `4158524DEB92394F50D7550D295D67860F9D2D92F4C1D06B13FA668B1F1F7DFA`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `option_graph_planner`: `external_validation/method_config_candidates/option_graph_planner.json` sha256 `DE3E0198432E4CF42F017C473EED3CF889B60FE5B85B642C55C44A1FF02410AD`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `proposed_energy_landscape_composer_v4_1`: `external_validation/method_config_candidates/proposed_energy_landscape_composer_v4_1.json` sha256 `7331767D0D76C6507C4F586F2FD093ADAF7FF0DF07CAB50A1A4FD164D8CEABB3`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `residual_rl_composer`: `external_validation/method_config_candidates/residual_rl_composer.json` sha256 `4A0CE8A9FD2BE847325029A688ED912635342D4F0159FF454828FA228C5F302F`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `stable_dmp_handoff`: `external_validation/method_config_candidates/stable_dmp_handoff.json` sha256 `0AD7209C0E2023CE462624C5A10EB09AC5EA7A249D86CA47A4EBC20F852639EF`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`
- `tamp_feasibility_screen`: `external_validation/method_config_candidates/tamp_feasibility_screen.json` sha256 `18F846DB89B1C852DF378A3ED9A205389141AE2C56D0D9E27210401973620EFB`; operator-acceptance-required `true`; strict-adapter-evidence-ready `false`

## Blocking Method Gaps

- `greedy_module_sequence`: candidate config `external_validation/method_config_candidates/greedy_module_sequence.json` sha256 `4158524DEB92394F50D7550D295D67860F9D2D92F4C1D06B13FA668B1F1F7DFA`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `behavior_cloned_skill_chain`: candidate config `external_validation/method_config_candidates/behavior_cloned_skill_chain.json` sha256 `BCFB1DAAE14267E91CC9FE9AA08083FFF90625B255C81FA74E47647018A969C2`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `option_graph_planner`: candidate config `external_validation/method_config_candidates/option_graph_planner.json` sha256 `DE3E0198432E4CF42F017C473EED3CF889B60FE5B85B642C55C44A1FF02410AD`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `tamp_feasibility_screen`: candidate config `external_validation/method_config_candidates/tamp_feasibility_screen.json` sha256 `18F846DB89B1C852DF378A3ED9A205389141AE2C56D0D9E27210401973620EFB`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `stable_dmp_handoff`: candidate config `external_validation/method_config_candidates/stable_dmp_handoff.json` sha256 `0AD7209C0E2023CE462624C5A10EB09AC5EA7A249D86CA47A4EBC20F852639EF`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `diffusion_skill_stitcher`: candidate config `external_validation/method_config_candidates/diffusion_skill_stitcher.json` sha256 `4F44159059554664F238B144C1D65395CDE4417F89308ABD8C3DC09EDB02165B`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `cem_trajectory_composer`: candidate config `external_validation/method_config_candidates/cem_trajectory_composer.json` sha256 `BA1A268A3FBADB9E86286B11B6B9E593BEFB448586493CFBB4CDFDE8C6661C99`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `residual_rl_composer`: candidate config `external_validation/method_config_candidates/residual_rl_composer.json` sha256 `4A0CE8A9FD2BE847325029A688ED912635342D4F0159FF454828FA228C5F302F`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `energy_compatibility_heuristic`: candidate config `external_validation/method_config_candidates/energy_compatibility_heuristic.json` sha256 `ED6FB2887EFB80342705CA1528597B8AE4FB890C28B285660FD9C0443FA0903C`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `proposed_energy_landscape_composer_v4_1`: candidate config `external_validation/method_config_candidates/proposed_energy_landscape_composer_v4_1.json` sha256 `7331767D0D76C6507C4F586F2FD093ADAF7FF0DF07CAB50A1A4FD164D8CEABB3`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`
- `barrier_certified_energy_composer_v5`: candidate config `external_validation/method_config_candidates/barrier_certified_energy_composer_v5.json` sha256 `0DF7FB36D51A1866B46716F0601E46E81B815849675D0C6CAB8FB4037B801872`; missing `['implementation_path', 'independent_operator_provenance', 'manifest_method_declaration', 'rollout_policy_hash_binding']`

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
python scripts\materialize_fidelity_acceptance.py --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --code-commit <commit> --skill-library-hash <sha256> --write <operator fields>
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
python scripts\self_test_external_precollection_freeze_receipt.py
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

# External Precollection Freeze Receipt

Not evidence: `true`.
Strict external evidence ready: `false`.
Freeze receipt ready: `false`.

This receipt freezes precollection inputs only. It is not a manifest, rollout log, video, checkpoint, metric result, method evidence, or external validation evidence.

## Current Lock State

- Backend module: `<module_or_path>`
- Run id: `paper119_external_validation_run`
- Unsealed alias map: `false`
- Operator id: `<operator_or_lab>`
- Collection machine: `<machine_or_robot_platform>`
- Date locked: `<YYYY-MM-DD>`
- Code commit: `fe85f791220562c93b0ffe5c64b907fc5be1d6e4`
- Skill-library hash: `F2016F31E605B5135E4F34E95C7CC483C0F170352ACA8E2D0190D2D15F203802`
- Candidate method configs hash-locked: `11`
- Method-config hash lock ready: `true`

## Operator Regeneration Command

```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```

## Strict Command Sequence

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
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id paper119_external_validation_run --unsealed-alias-map
```
```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```
```powershell
python scripts\self_test_external_precollection_freeze_receipt.py
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id paper119_external_validation_run --unsealed-alias-map
```
```powershell
python scripts\build_external_postcollection_evidence_seal.py
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

## Lock Artifacts

- `core_precollection_artifact` `external_validation/blinded_operator_sheet.csv` `BAAF6BC6B7BFA0DAD346498D8C7FACEE413FD2A0844E5F833A519BBAD4BEEBF5`
- `core_precollection_artifact` `external_validation/method_alias_map.json` `B56A11CB20914B2FD2649DA647F7722DE43D6B04DE3E89704A8CD3F952A4E031`
- `core_precollection_artifact` `external_validation/manifest_precollection_draft.json` `1909C8172316185391056F5B672C0B484E2E42F3E1295251EC147FDA0BF6E744`
- `core_precollection_artifact` `external_validation/manifest_precollection_draft.md` `E9C816F76182B011D16F9943F80538E42C14947202349AE5FCACE3276AFD07EF`
- `core_precollection_artifact` `external_validation/manifest_template.json` `158757454025E628D3E63FA9019C0454F4E3E4FEB28A6104A465252F67B25066`
- `core_precollection_artifact` `external_validation/log_schema_v1.json` `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`
- `core_precollection_artifact` `external_validation/statistical_analysis_plan.json` `CADC94E4F3A6A3898B99151C79BD437EB8D997A9F488BD673D205A70420CD65E`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.json` `7A604C84240C9815486D4B606B9F3DD0D10AB2B2F2115252FE9246E3BFE64136`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.md` `179FA088F5BF95363BD6D67B0DABF6344D04727F460E8412FD9489356DD6D6D6`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.csv` `FC1257013B9B99A429281358FF84C786F7BC7055428F99F3B39D639F2DED766C`
- `core_precollection_artifact` `external_validation/method_manifest_cutover_checklist.csv` `A7C212C2F99ABFE921D5C5128446E1DE908996C5B789D9BFF6F2B5DA926DF899`
- `core_precollection_artifact` `external_validation/method_manifest_cutover_checklist.md` `D21F7033199CA20BA8610BAC8777E385EC1790FBF2A447B25EF1D12883942765`
- `core_precollection_artifact` `external_validation/runner/backend_contract.py` `724802B452269859B9F9686942CC9788A078B907EDD32EC9C857CF5A1427801A`
- `core_precollection_artifact` `external_validation/runner/real_collection_runner.py` `3C35D3CDC8EF3A54E518242D371BF95E5C554BC656DA536D7DD01B0040CAB133`
- `core_precollection_artifact` `results/external_collection_readiness_audit.json` `8AC215A38BD0E7BBF44A20C547A4ED43CDD76960DCE679ADAF46B24D8C02422E`
- `core_precollection_artifact` `results/external_fidelity_acceptance_audit.json` `44A74216804348A545706B23ACBF66F5F2BB12ACDB66C4A98C4101C3C3334582`
- `core_precollection_artifact` `results/fidelity_acceptance_materialization_plan.json` `34BD54AE4371667A6BCFCC6478477961037E36B8C2AF05C5B4D5B9B729445B8A`
- `core_precollection_artifact` `results/external_config_manifest_audit.json` `71888C39980962B4AAE8E67DC2338CEB8F2DBA603BC85DF0BF6B50BE7720EF92`
- `core_precollection_artifact` `results/external_method_implementation_audit.json` `F8AA15870753DC4E6B4F681ACEF956A4C49ADAF3A12A98C32091582474021FAC`
- `core_precollection_artifact` `results/external_evidence_intake_ledger_audit.json` `7A604C84240C9815486D4B606B9F3DD0D10AB2B2F2115252FE9246E3BFE64136`
- `core_precollection_artifact` `results/external_precollection_manifest_draft_audit.json` `5F7C0865651B5F3AF6B0A7E3793077CF119397D7C32C766AF738928F2A10E763`
- `prepared_task_config` `external_validation/configs/cable_route_insert.json` `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`
- `prepared_task_config` `external_validation/configs/door_open_navigation.json` `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`
- `prepared_task_config` `external_validation/configs/drawer_to_pick_transfer.json` `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`
- `prepared_task_config` `external_validation/configs/peg_place_regrasp.json` `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`
- `method_config_materialization_artifact` `external_validation/method_config_materialization_plan.json` `46924247617A3D86168888FA411EA957C82C1992FB66D82BC00CB87AAE9E153F`
- `method_config_materialization_artifact` `external_validation/method_config_materialization_plan.md` `5BB83B2C4B1601858113FD2F8F9203B469EF2BC3C9AA37880E23FBAA384A1D53`
- `method_config_materialization_artifact` `external_validation/method_config_candidates.csv` `BBFDEAAA8563980BCD0CDE8002DA50676B1B7F1B68A238CCC39CEEEEDCBB4EF5`
- `method_config_materialization_artifact` `results/external_method_config_materialization_audit.json` `5DC60C246B1C8CCF6D20F780F5D97B46E016C548EFCFDD72EE7E6925A4EDD7F2`
- `method_config_materialization_artifact` `results/external_method_config_materialization_audit.md` `9FE77F7B1D8976A4AA3A7A60FB26431D8733D1698EBC5CEE23C16676CBE13C7A`
- `candidate_method_config` `external_validation/method_config_candidates/barrier_certified_energy_composer_v5.json` `0DF7FB36D51A1866B46716F0601E46E81B815849675D0C6CAB8FB4037B801872`
- `candidate_method_config` `external_validation/method_config_candidates/behavior_cloned_skill_chain.json` `BCFB1DAAE14267E91CC9FE9AA08083FFF90625B255C81FA74E47647018A969C2`
- `candidate_method_config` `external_validation/method_config_candidates/cem_trajectory_composer.json` `BA1A268A3FBADB9E86286B11B6B9E593BEFB448586493CFBB4CDFDE8C6661C99`
- `candidate_method_config` `external_validation/method_config_candidates/diffusion_skill_stitcher.json` `4F44159059554664F238B144C1D65395CDE4417F89308ABD8C3DC09EDB02165B`
- `candidate_method_config` `external_validation/method_config_candidates/energy_compatibility_heuristic.json` `ED6FB2887EFB80342705CA1528597B8AE4FB890C28B285660FD9C0443FA0903C`
- `candidate_method_config` `external_validation/method_config_candidates/greedy_module_sequence.json` `4158524DEB92394F50D7550D295D67860F9D2D92F4C1D06B13FA668B1F1F7DFA`
- `candidate_method_config` `external_validation/method_config_candidates/option_graph_planner.json` `DE3E0198432E4CF42F017C473EED3CF889B60FE5B85B642C55C44A1FF02410AD`
- `candidate_method_config` `external_validation/method_config_candidates/proposed_energy_landscape_composer_v4_1.json` `7331767D0D76C6507C4F586F2FD093ADAF7FF0DF07CAB50A1A4FD164D8CEABB3`
- `candidate_method_config` `external_validation/method_config_candidates/residual_rl_composer.json` `4A0CE8A9FD2BE847325029A688ED912635342D4F0159FF454828FA228C5F302F`
- `candidate_method_config` `external_validation/method_config_candidates/stable_dmp_handoff.json` `0AD7209C0E2023CE462624C5A10EB09AC5EA7A249D86CA47A4EBC20F852639EF`
- `candidate_method_config` `external_validation/method_config_candidates/tamp_feasibility_screen.json` `18F846DB89B1C852DF378A3ED9A205389141AE2C56D0D9E27210401973620EFB`
- `selected_backend_module` `<operator_supplied>` `missing`

## Missing Lock Paths

- `selected_backend_module`

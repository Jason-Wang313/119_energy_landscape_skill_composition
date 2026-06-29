# External Precollection Freeze Receipt

Not evidence: `true`.
Strict external evidence ready: `false`.
Freeze receipt ready: `false`.

This receipt freezes precollection inputs only. It is not a manifest, rollout log, video, checkpoint, metric result, or external validation evidence.

## Current Lock State

- Backend module: `<module_or_path>`
- Run id: `paper119_external_validation_run`
- Unsealed alias map: `false`
- Operator id: `<operator_or_lab>`
- Collection machine: `<machine_or_robot_platform>`
- Date locked: `<YYYY-MM-DD>`
- Code commit: `562e6bc7d1db3ce96d96597e488bd0dc796e1c0e`
- Skill-library hash: `F2016F31E605B5135E4F34E95C7CC483C0F170352ACA8E2D0190D2D15F203802`

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
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id paper119_external_validation_run --unsealed-alias-map
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
- `core_precollection_artifact` `external_validation/manifest_precollection_draft.json` `C10232A44BCEAF1A27BAB702D284119CDA87AFCBC52A28433432F2F3D6C10029`
- `core_precollection_artifact` `external_validation/manifest_precollection_draft.md` `4B1E1D944B41D39A7D4D311FC0E8867CC2C45997F6A1B1E331D5CA9E515701E2`
- `core_precollection_artifact` `external_validation/manifest_template.json` `158757454025E628D3E63FA9019C0454F4E3E4FEB28A6104A465252F67B25066`
- `core_precollection_artifact` `external_validation/log_schema_v1.json` `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`
- `core_precollection_artifact` `external_validation/statistical_analysis_plan.json` `CADC94E4F3A6A3898B99151C79BD437EB8D997A9F488BD673D205A70420CD65E`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.json` `D7B1B41DD6E7F2069F09B998E728C74C6CC19ED11B7F470C9BDF546147F97402`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.md` `513E004923A6C2CBFC89E4DE896C363C991F279BF22CD7AC8901DA1B45FF45C6`
- `core_precollection_artifact` `external_validation/evidence_intake_ledger.csv` `D3AC6811574F004B1E61C7F89507D9FC7B6DC235CC8F6152B9E6A259FB67FD19`
- `core_precollection_artifact` `external_validation/method_manifest_cutover_checklist.csv` `A7C212C2F99ABFE921D5C5128446E1DE908996C5B789D9BFF6F2B5DA926DF899`
- `core_precollection_artifact` `external_validation/method_manifest_cutover_checklist.md` `D21F7033199CA20BA8610BAC8777E385EC1790FBF2A447B25EF1D12883942765`
- `core_precollection_artifact` `external_validation/runner/backend_contract.py` `724802B452269859B9F9686942CC9788A078B907EDD32EC9C857CF5A1427801A`
- `core_precollection_artifact` `external_validation/runner/real_collection_runner.py` `3C35D3CDC8EF3A54E518242D371BF95E5C554BC656DA536D7DD01B0040CAB133`
- `core_precollection_artifact` `results/external_collection_readiness_audit.json` `74168764841A1FF414AC673994CBA4FD724DF7A20C17A364A761B21D94E636EE`
- `core_precollection_artifact` `results/external_fidelity_acceptance_audit.json` `44A74216804348A545706B23ACBF66F5F2BB12ACDB66C4A98C4101C3C3334582`
- `core_precollection_artifact` `results/fidelity_acceptance_materialization_plan.json` `34BD54AE4371667A6BCFCC6478477961037E36B8C2AF05C5B4D5B9B729445B8A`
- `core_precollection_artifact` `results/external_config_manifest_audit.json` `71888C39980962B4AAE8E67DC2338CEB8F2DBA603BC85DF0BF6B50BE7720EF92`
- `core_precollection_artifact` `results/external_method_implementation_audit.json` `F8AA15870753DC4E6B4F681ACEF956A4C49ADAF3A12A98C32091582474021FAC`
- `core_precollection_artifact` `results/external_evidence_intake_ledger_audit.json` `D7B1B41DD6E7F2069F09B998E728C74C6CC19ED11B7F470C9BDF546147F97402`
- `core_precollection_artifact` `results/external_precollection_manifest_draft_audit.json` `F2423E20A2BF363BB7D15F2E52BB340CCECB4DAB650998818342057309BC81D0`
- `prepared_task_config` `external_validation/configs/cable_route_insert.json` `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`
- `prepared_task_config` `external_validation/configs/door_open_navigation.json` `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`
- `prepared_task_config` `external_validation/configs/drawer_to_pick_transfer.json` `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`
- `prepared_task_config` `external_validation/configs/peg_place_regrasp.json` `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`
- `selected_backend_module` `<operator_supplied>` `missing`

## Missing Lock Paths

- `selected_backend_module`

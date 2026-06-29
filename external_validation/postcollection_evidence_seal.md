# External Postcollection Evidence Seal

Not evidence: `true`.
Strict external evidence ready: `false`.
Postcollection seal ready: `false`.
Ready for manifest promotion: `false`.

This seal hashes raw postcollection files and collection metadata before manifest promotion. It is not a manifest, metric result, rollout validation pass, fidelity acceptance, or external evidence.

## Collection Summary

- Run id: `paper119_external_validation_run`
- Backend module: `<module_or_path>`
- Operator id: `<operator_or_lab>`
- Collection machine: `<machine_or_robot_platform>`
- Date sealed: `<YYYY-MM-DD>`
- Expected records: `1440`
- JSONL logs: `0`
- JSONL records: `0`
- Invalid JSONL lines: `0`
- Rollout videos: `0`
- Precollection freeze ready: `false`

## Operator Regeneration Command

```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
```

## Strict Command Sequence

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id paper119_external_validation_run --unsealed-alias-map
```
```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id paper119_external_validation_run --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id paper119_external_validation_run --unsealed-alias-map
```
```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id paper119_external_validation_run --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
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

## Seal Artifacts

- `precollection_freeze_receipt` `external_validation/precollection_freeze_receipt.json` `7DAA68CE6E02224089A09D800930C9A397F4001757EFBD64A7C678D005F19880`
- `operator_record_sheet` `external_validation/operator_record_sheet.csv` `3286764C655EA1F5209A93A2D4C5596941EF22F621BA11282867F62C5D22785D`
- `blinded_operator_sheet` `external_validation/blinded_operator_sheet.csv` `BAAF6BC6B7BFA0DAD346498D8C7FACEE413FD2A0844E5F833A519BBAD4BEEBF5`
- `method_alias_map` `external_validation/method_alias_map.json` `B56A11CB20914B2FD2649DA647F7722DE43D6B04DE3E89704A8CD3F952A4E031`
- `method_cutover_checklist` `external_validation/method_manifest_cutover_checklist.csv` `A7C212C2F99ABFE921D5C5128446E1DE908996C5B789D9BFF6F2B5DA926DF899`
- `method_reference_provenance` `external_validation/method_reference_provenance.csv` `7F6A5967DE10AC5A49200726082D0600A3EF70984B94DC414A35AA90BD97CCAC`
- `precollection_manifest_draft` `external_validation/manifest_precollection_draft.json` `8B8E9DED2328D4A971FB0ED47F058A322842088546CAC3E9B9206CAA61015AAF`
- `prepared_or_manifest_task_config` `external_validation/configs/cable_route_insert.json` `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`
- `prepared_or_manifest_task_config` `external_validation/configs/door_open_navigation.json` `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`
- `prepared_or_manifest_task_config` `external_validation/configs/drawer_to_pick_transfer.json` `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`
- `prepared_or_manifest_task_config` `external_validation/configs/peg_place_regrasp.json` `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`

## Missing Real Artifact Roles

- `official_raw_jsonl_log`
- `official_rollout_video`

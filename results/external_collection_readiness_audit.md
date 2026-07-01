# External Collection Readiness Audit

Passed: `true`.
Not evidence: `true`.
Collection ready: `false`.
Readiness state: `PREPARE_BACKEND_CONFIGS_AND_FIDELITY`.
Rows: `1440`.
Task families: `4`.
Blocking missing items: `4`.

This audit is a pre-collection gate for real robot or accepted high-fidelity simulator runs. It is not rollout evidence; it prevents starting collection until backend, configs, fidelity provenance, alias unsealing, output logs, and run identity are ready.

## Strict Collection Command

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

## Tracked Reference Route

This non-evidence route fills the backend, config directory, run id, and alias-unsealing arguments for the repository ManiSkill reference backend. It remains blocked until fidelity acceptance and the later manifest/log/video evidence gates pass.

- Backend module: `external_validation\runner\maniskill_reference_backend.py`
- Run id: `maniskill_sapien_reference_preflight_protocol_v1`
- Collection ready: `false`
- Blocking missing items: `1`

Reference pre-collection gate:

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id maniskill_sapien_reference_preflight_protocol_v1 --unsealed-alias-map
```

Reference precollection freeze receipt:

```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id maniskill_sapien_reference_preflight_protocol_v1 --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```

Reference collection command after fidelity acceptance:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id maniskill_sapien_reference_preflight_protocol_v1 --unsealed-alias-map
```

Reference-route blockers:

- reference_fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'

## Blocking Missing

- backend_module_ready: --backend-module is required before actual collection
- fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- alias_unsealing_explicit: unsealed_alias_map=False
- run_id_specific: run_id='paper119_external_validation_run'

## Checks

- `pass` `runner_exists`: external_validation/runner/real_collection_runner.py
- `pass` `schema_exists`: external_validation/log_schema_v1.json
- `pass` `operator_sheet_exists`: external_validation/blinded_operator_sheet.csv
- `pass` `operator_sheet_columns`: required columns present
- `pass` `operator_sheet_row_budget`: rows=1440
- `pass` `alias_map_exists`: external_validation/method_alias_map.json
- `pass` `alias_map_complete`: aliases=12, missing=[], errors=[]
- `fail` `backend_module_ready`: --backend-module is required before actual collection
- `pass` `task_config_dir_exists`: external_validation/configs
- `pass` `real_task_configs_ready`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `fail` `fidelity_acceptance_ready`: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- `fail` `alias_unsealing_explicit`: unsealed_alias_map=False
- `fail` `run_id_specific`: run_id='paper119_external_validation_run'
- `pass` `output_logs_empty_or_force`: existing_nonempty_logs=[], force=False
- `pass` `video_dir_parent_exists`: external_validation/videos

# External Collection Readiness Audit

Passed: `true`.
Not evidence: `true`.
Collection ready: `false`.
Readiness state: `PREPARE_BACKEND_CONFIGS_AND_FIDELITY`.
Rows: `1440`.
Task families: `4`.
Blocking missing items: `5`.

This audit is a pre-collection gate for real robot or accepted high-fidelity simulator runs. It is not rollout evidence; it prevents starting collection until backend, configs, fidelity provenance, alias unsealing, output logs, and run identity are ready.

## Strict Collection Command

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

## Blocking Missing

- backend_module_ready: --backend-module is required before actual collection
- real_task_configs_ready: missing config: external_validation/configs/cable_route_insert.json; missing config: external_validation/configs/door_open_navigation.json; missing config: external_validation/configs/drawer_to_pick_transfer.json; missing config: external_validation/configs/peg_place_regrasp.json
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
- `fail` `real_task_configs_ready`: missing config: external_validation/configs/cable_route_insert.json; missing config: external_validation/configs/door_open_navigation.json; missing config: external_validation/configs/drawer_to_pick_transfer.json; missing config: external_validation/configs/peg_place_regrasp.json
- `fail` `fidelity_acceptance_ready`: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- `fail` `alias_unsealing_explicit`: unsealed_alias_map=False
- `fail` `run_id_specific`: run_id='paper119_external_validation_run'
- `pass` `output_logs_empty_or_force`: existing_nonempty_logs=[], force=False
- `pass` `video_dir_parent_exists`: external_validation/videos

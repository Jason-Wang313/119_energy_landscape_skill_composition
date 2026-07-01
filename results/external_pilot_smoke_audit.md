# External Pilot Smoke Audit

Passed: `true`.
Not evidence: `true`.
Pilot smoke ready: `false`.
Strict evidence ready: `false`.
Records observed: `0`.

This audit is for a quarantined first-panel backend smoke test. It never satisfies the external evidence gate and it rejects pilot records that write into official evidence log/video paths.

## Checks

- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_smoke/logs, video_dir=external_validation/pilot_smoke/videos
- `pass` `schema_exists`: external_validation/log_schema_v1.json
- `pass` `alias_map_methods_loaded`: methods=12
- `pass` `task_configs_or_sheet_loaded`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `pilot_manifest_absent`: pilot smoke must not build an evidence manifest
- `pass` `pilot_records_do_not_touch_official_evidence_paths`: offending_records=0
- `pass` `pilot_run_ids_are_marked_pilot`: non_pilot_run_ids=[]
- `pass` `pilot_schema_valid`: errors=[]
- `pass` `pilot_record_count_within_cap`: records=0, max_records=12
- `pass` `pilot_logs_present_only_when_operator_ran_smoke`: records=0, strict=False

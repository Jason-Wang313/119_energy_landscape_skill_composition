# ManiSkill Pilot Runtime Liveness Audit

Passed: `true`.
Not evidence: `true`.
Pilot runtime ready: `false`.
Runner I/O ready: `false`.
Render video ready: `false`.
Readiness state: `PILOT_RUNTIME_NOT_READY`.
Render backend: `cpu`.
Shader pack: `minimal`.
Render size: `128x128`.
Timed out: `false`.
Records observed: `0`.
Videos written: `0`.
Diagnostic video fallbacks: `0`.
Failure summary: `runner exited with returncode 1 after progress stage record_video_start before producing the required pilot record/video`.
Last progress stage: `record_video_start`.

This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.

## Command

```powershell
C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe -u external_validation/runner/real_collection_runner.py --backend-module external_validation/runner/maniskill_reference_backend.py --task-config-dir external_validation/configs --output-log-dir external_validation/pilot_runtime_guard/logs --video-dir external_validation/pilot_runtime_guard/videos --run-id paper119_pilot_runtime_guard_local --unsealed-alias-map --max-rows 1 --force
```

## Blocking Missing

- bounded ManiSkill reference runner did not produce a complete schema-valid pilot row/video on this machine; runner exited with returncode 1 after progress stage record_video_start before producing the required pilot record/video; use an accepted GPU/render machine or fix the backend before official collection

## Checks

- `pass` `runtime_guard_is_non_evidence`: the guard writes only a liveness report and quarantined pilot_runtime_guard outputs
- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_runtime_guard/logs, video_dir=external_validation/pilot_runtime_guard/videos
- `pass` `bounded_runner_subprocess_exercised`: timeout_seconds=60, timed_out=False, returncode=1
- `pass` `collection_progress_markers_recorded`: last_progress_stage='record_video_start'
- `pass` `timeout_or_result_recorded_as_readiness_state`: pilot_runtime_ready=False
- `pass` `ready_requires_schema_valid_records_and_videos`: records=0, videos=0, schema_errors=0
- `pass` `runner_io_ready_allows_only_quarantined_diagnostic_fallback`: runner_io_ready=False, diagnostic_fallbacks=0
- `pass` `diagnostic_fallback_does_not_mark_render_ready`: render_video_ready=False, pilot_runtime_ready=False, diagnostic_fallbacks=0
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

## Collection Progress

- `rows_loaded`: {'max_rows': 1, 'rows': 1, 'stage': 'rows_loaded'}
- `backend_create_start`: {'backend_module': 'external_validation/runner/maniskill_reference_backend.py', 'stage': 'backend_create_start'}
- `backend_created`: {'stage': 'backend_created'}
- `backend_contract_validated`: {'stage': 'backend_contract_validated'}
- `platform_provenance_loaded`: {'platform_name': 'ManiSkill-SAPIEN-reference-backend', 'platform_type': 'high_fidelity_sim', 'stage': 'platform_provenance_loaded'}
- `row_start`: {'method_alias': 'method_05', 'row_index': 1, 'scene_id': 'peg_place_regrasp_reset_000', 'stage': 'row_start', 'task_family': 'peg_place_regrasp'}
- `load_task_config_start`: {'row_index': 1, 'stage': 'load_task_config_start', 'task_family': 'peg_place_regrasp'}
- `load_task_config_done`: {'row_index': 1, 'stage': 'load_task_config_done', 'task_family': 'peg_place_regrasp'}
- `reset_scene_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'reset_scene_start', 'task_family': 'peg_place_regrasp'}
- `reset_scene_done`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'reset_scene_done', 'task_family': 'peg_place_regrasp'}
- `capture_observation_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'capture_observation_start', 'task_family': 'peg_place_regrasp'}
- `capture_observation_done`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'capture_observation_done', 'task_family': 'peg_place_regrasp'}
- `terminal_samples_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'terminal_samples_start', 'task_family': 'peg_place_regrasp'}
- `terminal_samples_done`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'samples': 8, 'stage': 'terminal_samples_done', 'task_family': 'peg_place_regrasp'}
- `run_method_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'run_method_start', 'task_family': 'peg_place_regrasp'}
- `run_method_done`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'run_method_done', 'task_family': 'peg_place_regrasp'}
- `execute_skill_pair_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'execute_skill_pair_start', 'task_family': 'peg_place_regrasp'}
- `execute_skill_pair_done`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'execute_skill_pair_done', 'task_family': 'peg_place_regrasp'}
- `record_video_start`: {'method': 'energy_compatibility_heuristic', 'row_index': 1, 'stage': 'record_video_start', 'task_family': 'peg_place_regrasp'}

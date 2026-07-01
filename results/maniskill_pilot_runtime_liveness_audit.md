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
Diagnostic video fallbacks: `1`.
Diagnostic sidecar rejected before JSONL write: `true`.
Official video guard blocked diagnostic fallback: `true`.
Failure summary: `official video guard rejected diagnostic fallback sidecar before JSONL write after progress stage record_video_start`.
Last progress stage: `record_video_start`.
Last backend progress stage: `reset_scene_return`.
Reset-timeout triage: `results/maniskill_pilot_reset_timeout_triage.md`.

This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.

## Command

```powershell
C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe -u external_validation/runner/real_collection_runner.py --backend-module external_validation/runner/maniskill_reference_backend.py --task-config-dir external_validation/configs --output-log-dir external_validation/pilot_runtime_guard/logs --video-dir external_validation/pilot_runtime_guard/videos --run-id paper119_pilot_runtime_guard_local --unsealed-alias-map --max-rows 1 --force
```

## Blocking Missing

- bounded ManiSkill reference runner reached record_video_start, but the official video guard rejected the diagnostic fallback sidecar before any JSONL row could be written; render-backed RGB video remains unavailable, so use an accepted GPU/render machine or fix the renderer before official collection

## Checks

- `pass` `runtime_guard_is_non_evidence`: the guard writes only a liveness report and quarantined pilot_runtime_guard outputs
- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_runtime_guard/logs, video_dir=external_validation/pilot_runtime_guard/videos
- `pass` `bounded_runner_subprocess_exercised`: timeout_seconds=60, timed_out=False, returncode=1
- `pass` `collection_progress_markers_recorded`: last_progress_stage='record_video_start'
- `pass` `backend_reset_substage_markers_recorded`: last_progress_stage='record_video_start', last_backend_progress_stage='reset_scene_return'
- `pass` `timeout_or_result_recorded_as_readiness_state`: pilot_runtime_ready=False
- `pass` `ready_requires_schema_valid_records_and_videos`: records=0, videos=0, schema_errors=0
- `pass` `runner_io_ready_allows_only_quarantined_diagnostic_fallback`: runner_io_ready=False, diagnostic_fallbacks=1
- `pass` `official_guard_rejects_diagnostic_before_jsonl_write`: diagnostic_sidecar_rejected_before_jsonl_write=True, records=0, returncode=1
- `pass` `diagnostic_rejection_paths_are_quarantined`: diagnostic_sidecar_paths_quarantined=True, diagnostic_fallbacks=1
- `pass` `diagnostic_fallback_does_not_mark_render_ready`: render_video_ready=False, pilot_runtime_ready=False, diagnostic_fallbacks=1
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent
- `pass` `reset_timeout_triage_is_non_evidence`: triage_status=RESET_SCENE_TIMEOUT_TRIAGE_NOT_APPLICABLE, strict_external_evidence_ready=False
- `pass` `reset_timeout_triage_context_recorded`: reset_timeout=False, task_family='peg_place_regrasp', method='energy_compatibility_heuristic', env_id='PegInsertionSide-v1', backend_stage='reset_scene_return'
- `pass` `reset_timeout_operator_actions_present`: reset_timeout=False, actions=7

## Diagnostic Sidecars

- `external_validation/pilot_runtime_guard/videos/peg_place_regrasp/paper119_blind_peg_place_regrasp_r000_method_05.4D84DD563A0C.staging.mp4.diagnostic.json`

## Reset Timeout Triage

- Status: `RESET_SCENE_TIMEOUT_TRIAGE_NOT_APPLICABLE`
- Reset timeout: `false`
- Task family: `peg_place_regrasp`
- Method: `energy_compatibility_heuristic` via alias `method_05`
- Scene: `peg_place_regrasp_reset_000`
- Primary env: `PegInsertionSide-v1`
- Config hash: `A731AFA16ED0ECD963A053C84EA0421363B8340EF8EA92F87D21F6F7099E5501`
- Last backend progress stage: `reset_scene_return`

Operator next actions:
- Rerun the liveness audit on the exact candidate collection machine with the intended render backend, shader pack, and timeout, and keep outputs under external_validation/pilot_runtime_guard only.
- Run python scripts\audit_maniskill_render_video_preflight.py --profile-matrix --timeout-diagnosis-seconds 30 before retrying official collection for peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
- Run python scripts\build_maniskill_render_machine_qualification.py and do not collect official evidence until the exact machine is qualified for render-backed RGB MP4 export and pilot liveness.
- Inspect the bound task config, primary_env_id, installed ManiSkill assets, reset seed, and SAPIEN renderer logs for the reset-scene target peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
- Use last_backend_progress_stage to decide whether the next fix belongs to import/package setup, gym.make construction, env.reset/assets, or initial render capture.
- If reset still hangs, replace or rebind the task in external_validation/fidelity_acceptance.json only after independent operator signoff, then rerun collection readiness before any official rollout.
- Do not promote quarantined pilot logs, diagnostic videos, fallback sidecars, or partial reset attempts into external_validation/manifest.json.

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

## Backend Progress

- `reset_scene_begin`: {'env_id': 'PegInsertionSide-v1', 'scene_id': 'peg_place_regrasp_reset_000', 'seed': 0, 'stage': 'reset_scene_begin', 'task_family': 'peg_place_regrasp'}
- `ensure_env_start`: {'env_id': 'PegInsertionSide-v1', 'stage': 'ensure_env_start', 'task_family': 'peg_place_regrasp'}
- `import_mani_skill_start`: {'env_id': 'PegInsertionSide-v1', 'stage': 'import_mani_skill_start'}
- `import_mani_skill_done`: {'env_id': 'PegInsertionSide-v1', 'stage': 'import_mani_skill_done'}
- `make_env_start`: {'env_id': 'PegInsertionSide-v1', 'render_backend': 'cpu', 'render_height': 128, 'render_width': 128, 'shader_pack': 'minimal', 'stage': 'make_env_start'}
- `make_env_done`: {'env_id': 'PegInsertionSide-v1', 'stage': 'make_env_done', 'used_render_kwargs': True}
- `ensure_env_done`: {'env_id': 'PegInsertionSide-v1', 'stage': 'ensure_env_done', 'task_family': 'peg_place_regrasp'}
- `env_reset_start`: {'env_id': 'PegInsertionSide-v1', 'seed': 0, 'stage': 'env_reset_start', 'task_family': 'peg_place_regrasp'}
- `env_reset_done`: {'env_id': 'PegInsertionSide-v1', 'info_keys': ['elapsed_steps', 'peg_head_pos_at_hole', 'reconfigure', 'success'], 'seed': 0, 'stage': 'env_reset_done', 'task_family': 'peg_place_regrasp'}
- `initial_video_frame_start`: {'env_id': 'PegInsertionSide-v1', 'stage': 'initial_video_frame_start', 'task_family': 'peg_place_regrasp'}
- `initial_video_frame_done`: {'env_id': 'PegInsertionSide-v1', 'frame_count': 0, 'render_attempted': True, 'render_error': 'RuntimeError: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', 'stage': 'initial_video_frame_done', 'task_family': 'peg_place_regrasp'}
- `reset_scene_return`: {'env_id': 'PegInsertionSide-v1', 'stage': 'reset_scene_return', 'task_family': 'peg_place_regrasp'}

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
Timed out: `true`.
Records observed: `0`.
Videos written: `0`.
Diagnostic video fallbacks: `0`.
Diagnostic sidecar rejected before JSONL write: `false`.
Official video guard blocked diagnostic fallback: `false`.
Failure summary: `runner timed out after progress stage reset_scene_start before producing the required pilot record/video`.
Last progress stage: `reset_scene_start`.
Reset-timeout triage: `results/maniskill_pilot_reset_timeout_triage.md`.

This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.

## Command

```powershell
C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe -u external_validation/runner/real_collection_runner.py --backend-module external_validation/runner/maniskill_reference_backend.py --task-config-dir external_validation/configs --output-log-dir external_validation/pilot_runtime_guard/logs --video-dir external_validation/pilot_runtime_guard/videos --run-id paper119_pilot_runtime_guard_local --unsealed-alias-map --max-rows 1 --force
```

## Blocking Missing

- bounded ManiSkill reference runner did not produce a complete schema-valid pilot row/video on this machine; runner timed out after progress stage reset_scene_start before producing the required pilot record/video; use an accepted GPU/render machine or fix the backend before official collection

## Checks

- `pass` `runtime_guard_is_non_evidence`: the guard writes only a liveness report and quarantined pilot_runtime_guard outputs
- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_runtime_guard/logs, video_dir=external_validation/pilot_runtime_guard/videos
- `pass` `bounded_runner_subprocess_exercised`: timeout_seconds=60, timed_out=True, returncode=None
- `pass` `collection_progress_markers_recorded`: last_progress_stage='reset_scene_start'
- `pass` `timeout_or_result_recorded_as_readiness_state`: pilot_runtime_ready=False
- `pass` `ready_requires_schema_valid_records_and_videos`: records=0, videos=0, schema_errors=0
- `pass` `runner_io_ready_allows_only_quarantined_diagnostic_fallback`: runner_io_ready=False, diagnostic_fallbacks=0
- `pass` `official_guard_rejects_diagnostic_before_jsonl_write`: diagnostic_sidecar_rejected_before_jsonl_write=False, records=0, returncode=None
- `pass` `diagnostic_rejection_paths_are_quarantined`: diagnostic_sidecar_paths_quarantined=True, diagnostic_fallbacks=0
- `pass` `diagnostic_fallback_does_not_mark_render_ready`: render_video_ready=False, pilot_runtime_ready=False, diagnostic_fallbacks=0
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent
- `pass` `reset_timeout_triage_is_non_evidence`: triage_status=RESET_SCENE_TIMEOUT_TRIAGE_READY, strict_external_evidence_ready=False
- `pass` `reset_timeout_triage_context_recorded`: reset_timeout=True, task_family='peg_place_regrasp', method='energy_compatibility_heuristic', env_id='PegInsertionSide-v1'
- `pass` `reset_timeout_operator_actions_present`: reset_timeout=True, actions=6

## Reset Timeout Triage

- Status: `RESET_SCENE_TIMEOUT_TRIAGE_READY`
- Reset timeout: `true`
- Task family: `peg_place_regrasp`
- Method: `energy_compatibility_heuristic` via alias `method_05`
- Scene: `peg_place_regrasp_reset_000`
- Primary env: `PegInsertionSide-v1`
- Config hash: `A731AFA16ED0ECD963A053C84EA0421363B8340EF8EA92F87D21F6F7099E5501`

Operator next actions:
- Rerun the liveness audit on the exact candidate collection machine with the intended render backend, shader pack, and timeout, and keep outputs under external_validation/pilot_runtime_guard only.
- Run python scripts\audit_maniskill_render_video_preflight.py --profile-matrix --timeout-diagnosis-seconds 30 before retrying official collection for peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
- Run python scripts\build_maniskill_render_machine_qualification.py and do not collect official evidence until the exact machine is qualified for render-backed RGB MP4 export and pilot liveness.
- Inspect the bound task config, primary_env_id, installed ManiSkill assets, reset seed, and SAPIEN renderer logs for the reset-scene target peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
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

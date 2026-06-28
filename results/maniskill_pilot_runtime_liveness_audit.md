# ManiSkill Pilot Runtime Liveness Audit

Passed: `true`.
Not evidence: `true`.
Pilot runtime ready: `false`.
Runner I/O ready: `true`.
Render video ready: `false`.
Readiness state: `PILOT_RUNTIME_NOT_READY`.
Render backend: `cpu`.
Shader pack: `minimal`.
Render size: `128x128`.
Timed out: `false`.
Records observed: `1`.
Videos written: `1`.
Diagnostic video fallbacks: `1`.
Failure summary: `runner wrote quarantined schema-valid row/video using diagnostic non-evidence video fallback; render-backed video remains unavailable`.

This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.

## Command

```powershell
C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe external_validation/runner/real_collection_runner.py --backend-module external_validation/runner/maniskill_reference_backend.py --task-config-dir external_validation/configs --output-log-dir external_validation/pilot_runtime_guard/logs --video-dir external_validation/pilot_runtime_guard/videos --run-id paper119_pilot_runtime_guard_local --unsealed-alias-map --max-rows 1 --force
```

## Blocking Missing

- bounded ManiSkill reference runner produced a quarantined schema-valid pilot row/video only by using a diagnostic non-evidence video fallback; render-backed RGB video remains unavailable, so use an accepted GPU/render machine or fix the renderer before official collection

## Checks

- `pass` `runtime_guard_is_non_evidence`: the guard writes only a liveness report and quarantined pilot_runtime_guard outputs
- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_runtime_guard/logs, video_dir=external_validation/pilot_runtime_guard/videos
- `pass` `bounded_runner_subprocess_exercised`: timeout_seconds=180, timed_out=False, returncode=0
- `pass` `timeout_or_result_recorded_as_readiness_state`: pilot_runtime_ready=False
- `pass` `ready_requires_schema_valid_records_and_videos`: records=1, videos=1, schema_errors=0
- `pass` `runner_io_ready_allows_only_quarantined_diagnostic_fallback`: runner_io_ready=True, diagnostic_fallbacks=1
- `pass` `diagnostic_fallback_does_not_mark_render_ready`: render_video_ready=False, pilot_runtime_ready=False, diagnostic_fallbacks=1
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

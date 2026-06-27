# ManiSkill Pilot Runtime Liveness Audit

Passed: `true`.
Not evidence: `true`.
Pilot runtime ready: `false`.
Readiness state: `PILOT_RUNTIME_NOT_READY`.
Timed out: `true`.
Records observed: `0`.
Videos written: `0`.

This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.

## Command

```powershell
C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe external_validation/runner/real_collection_runner.py --backend-module external_validation/runner/maniskill_reference_backend.py --task-config-dir external_validation/configs --output-log-dir external_validation/pilot_runtime_guard/logs --video-dir external_validation/pilot_runtime_guard/videos --run-id paper119_pilot_runtime_guard_local_20260628 --unsealed-alias-map --max-rows 1 --force
```

## Blocking Missing

- bounded ManiSkill reference runner did not produce a complete schema-valid pilot row/video on this machine; use an accepted GPU/render machine or fix the backend before official collection

## Checks

- `pass` `runtime_guard_is_non_evidence`: the guard writes only a liveness report and quarantined pilot_runtime_guard outputs
- `pass` `quarantine_paths_are_not_official_evidence`: log_dir=external_validation/pilot_runtime_guard/logs, video_dir=external_validation/pilot_runtime_guard/videos
- `pass` `bounded_runner_subprocess_exercised`: timeout_seconds=60, timed_out=True, returncode=None
- `pass` `timeout_or_result_recorded_as_readiness_state`: pilot_runtime_ready=False
- `pass` `ready_requires_schema_valid_records_and_videos`: records=0, videos=0, schema_errors=0
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

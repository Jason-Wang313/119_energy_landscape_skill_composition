# External Pilot Smoke Packet

Not evidence: `true`.
Strict evidence ready: `false`.
Pilot rows: `12`.

This packet lets an independent operator test a real backend on one 12-row method panel without contaminating official evidence. Pilot logs and videos are quarantined under `external_validation/pilot_smoke/` and must never be included in `external_validation/manifest.json`.

## Commands

- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\pilot_smoke\logs --video-dir external_validation\pilot_smoke\videos --run-id paper119_pilot_smoke_<platform>_<date> --unsealed-alias-map --force`
- `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\pilot_smoke\logs --video-dir external_validation\pilot_smoke\videos --run-id paper119_pilot_smoke_<platform>_<date> --unsealed-alias-map --max-rows 12 --force`
- `python scripts\audit_external_pilot_smoke.py --strict --expected-records 12 --check-video-paths`
- `Remove or archive external_validation\pilot_smoke before official collection; pilot logs/videos must never be listed in external_validation\manifest.json`

## Work Orders

- `pilot_backend_preflight`: Run strict collection readiness against quarantine output dirs (not evidence; preflight only)
- `pilot_first_panel`: Collect the first 12-row method panel into pilot_smoke (quarantined smoke output; excluded from official manifest)
- `pilot_schema_video_audit`: Audit pilot records, videos, run ids, and quarantine paths (does not satisfy rollout or external evidence gates)
- `clear_pilot_before_full_collection`: Remove or archive pilot output before official collection (prevents pilot contamination of official evidence)

## Forbidden As Evidence

- `external_validation/pilot_smoke/logs/*.jsonl`
- `external_validation/pilot_smoke/videos/*`
- `external_validation/pilot_smoke/manifest.json`

# ManiSkill Render-Video Preflight Audit

Passed: `true`.
Not evidence: `true`.
Render video ready: `false`.
Strict external evidence ready: `false`.
Output directory: `external_validation/render_video_preflight`.

This preflight tests whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before any official external collection. It is not rollout evidence, does not write the real manifest, and does not replace fidelity acceptance or strict rollout audits.

## Blocking Missing

- render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: render preflight exceeded 30 seconds; OpenCabinetDrawer-v1: render preflight exceeded 30 seconds; OpenCabinetDoor-v1: render preflight exceeded 30 seconds; PullCubeTool-v1: render preflight exceeded 30 seconds

## Renderer Failure Classifier

- Failure classes: `['render_timeout']`
- Operator remediation items: `3`

- Do not use diagnostic fallback videos as external evidence; rerun this preflight on the exact accepted collection machine.
- Record Python, ManiSkill, SAPIEN, GPU/Vulkan, render backend, shader pack, and driver provenance with scripts\probe_external_platform.py before fidelity acceptance.
- Increase --timeout-seconds only after confirming the renderer is making progress and output directories remain quarantined.

## Renderer Profile Retest Commands

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```

## Renderer Profile Matrix

- `not_ready` `cpu/minimal` / `PegInsertionSide-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'
- `not_ready` `gpu/minimal` / `PegInsertionSide-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'
- `not_ready` `sapien_cuda/minimal` / `PegInsertionSide-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'

## Environment Results

- `not_ready` `peg_place_regrasp` / `PegInsertionSide-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'
- `not_ready` `drawer_to_pick_transfer` / `OpenCabinetDrawer-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'
- `not_ready` `door_open_navigation` / `OpenCabinetDoor-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'
- `not_ready` `cable_route_insert` / `PullCubeTool-v1`: made_env=None, reset_ok=None, render_ok=None, mp4_ok=None, error='render preflight exceeded 30 seconds'

## Timeout Diagnosis Retest

- `not_run`

## Checks

- `pass` `render_preflight_is_non_evidence`: preflight writes only quarantine outputs and audit files
- `pass` `quarantine_paths_are_not_official_evidence`: video_dir=external_validation/render_video_preflight/videos
- `pass` `primary_envs_loaded`: envs=4
- `pass` `each_probe_has_terminal_status`: records=4
- `pass` `render_readiness_recorded_without_overclaim`: render_video_ready=False
- `pass` `blocking_summary_present_when_not_ready`: blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: render preflight exceeded 30 seconds; OpenCabinetDrawer-v1: render preflight exceeded 30 seconds; OpenCabinetDoor-v1: render preflight exceeded 30 seconds; PullCubeTool-v1: render preflight exceeded 30 seconds']
- `pass` `renderer_failure_class_recorded_when_not_ready`: classes=['render_timeout']
- `pass` `operator_remediation_present_when_not_ready`: items=3
- `pass` `profile_retest_commands_cover_renderer_backends`: python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
- `pass` `profile_matrix_records_renderer_backends`: profile_matrix=True, backends=['cpu', 'gpu', 'sapien_cuda']
- `pass` `profile_matrix_terminal_status`: profile_matrix_records=3
- `pass` `profile_matrix_quarantined_non_evidence`: profile_matrix_records=3
- `pass` `timeout_diagnosis_quarantined_non_evidence`: timeout_diagnosis_records=0
- `pass` `timeout_diagnosis_terminal_status`: timeout_diagnosis_records=0
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

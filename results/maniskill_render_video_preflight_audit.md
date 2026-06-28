# ManiSkill Render-Video Preflight Audit

Passed: `true`.
Not evidence: `true`.
Render video ready: `false`.
Strict external evidence ready: `false`.
Output directory: `external_validation/render_video_preflight`.

This preflight tests whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before any official external collection. It is not rollout evidence, does not write the real manifest, and does not replace fidelity acceptance or strict rollout audits.

## Blocking Missing

- render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory

## Renderer Failure Classifier

- Failure classes: `['vulkan_descriptor_pool_exhaustion']`
- Operator remediation items: `5`

- Do not use diagnostic fallback videos as external evidence; rerun this preflight on the exact accepted collection machine.
- Record Python, ManiSkill, SAPIEN, GPU/Vulkan, render backend, shader pack, and driver provenance with scripts\probe_external_platform.py before fidelity acceptance.
- Treat vk::Device::allocateDescriptorSetsUnique/ErrorOutOfPoolMemory as a renderer-resource blocker for this machine, not as rollout evidence failure.
- Retest one primary environment at a time with explicit renderer profiles before official collection: cpu/minimal, gpu/minimal, and sapien_cuda/minimal.
- Use a machine whose SAPIEN/Vulkan renderer can capture RGB frames for all four primary task families before promoting fidelity acceptance.

## Renderer Profile Retest Commands

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```

## Renderer Profile Matrix

- `not_ready` `cpu/minimal` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'
- `not_ready` `gpu/minimal` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'
- `not_ready` `sapien_cuda/minimal` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'

## Environment Results

- `not_ready` `peg_place_regrasp` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'
- `not_ready` `drawer_to_pick_transfer` / `OpenCabinetDrawer-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'
- `not_ready` `door_open_navigation` / `OpenCabinetDoor-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'
- `not_ready` `cable_route_insert` / `PullCubeTool-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'

## Checks

- `pass` `render_preflight_is_non_evidence`: preflight writes only quarantine outputs and audit files
- `pass` `quarantine_paths_are_not_official_evidence`: video_dir=external_validation/render_video_preflight/videos
- `pass` `primary_envs_loaded`: envs=4
- `pass` `each_probe_has_terminal_status`: records=4
- `pass` `render_readiness_recorded_without_overclaim`: render_video_ready=False
- `pass` `blocking_summary_present_when_not_ready`: blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory']
- `pass` `renderer_failure_class_recorded_when_not_ready`: classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `operator_remediation_present_when_not_ready`: items=5
- `pass` `profile_retest_commands_cover_renderer_backends`: python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
- `pass` `profile_matrix_records_renderer_backends`: profile_matrix=True, backends=['cpu', 'gpu', 'sapien_cuda']
- `pass` `profile_matrix_terminal_status`: profile_matrix_records=3
- `pass` `profile_matrix_quarantined_non_evidence`: profile_matrix_records=3
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

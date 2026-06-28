# ManiSkill Render-Video Preflight Audit

Passed: `true`.
Not evidence: `true`.
Render video ready: `false`.
Strict external evidence ready: `false`.
Output directory: `external_validation/render_video_preflight`.

This preflight tests whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before any official external collection. It is not rollout evidence, does not write the real manifest, and does not replace fidelity acceptance or strict rollout audits.

## Blocking Missing

- render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory

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
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

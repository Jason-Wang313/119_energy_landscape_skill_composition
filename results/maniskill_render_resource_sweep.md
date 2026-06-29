# ManiSkill Render Resource Sweep

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Any render-backed MP4 ready: `false`.
Descriptor-pool failure persists at minimum resolution: `true`.
Sweep root: `external_validation/render_resource_sweep`.

This bounded sweep retests the first primary ManiSkill task at minimal resolution across renderer profiles. It is non-evidence, writes only quarantined outputs, and cannot replace the four-task render-video preflight.

## Records

- `not_ready` `cpu/minimal/16x16` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', failure_stage='initial_render_start', terminal_stage='close_done'
- `not_ready` `gpu/minimal/16x16` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', failure_stage='initial_render_start', terminal_stage='close_done'
- `not_ready` `sapien_cuda/minimal/16x16` / `PegInsertionSide-v1`: made_env=True, reset_ok=True, render_ok=False, mp4_ok=False, error='vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', failure_stage='initial_render_start', terminal_stage='close_done'

## Work Orders

### resource_min_resolution_retest

- Owner: `independent_operator`
- Status: `blocked_until_renderer_resource_path_passes`
- Command: `python scripts\audit_maniskill_render_resource_sweep.py --timeout-seconds 45 --max-envs 1`
- Acceptance: at least one accepted renderer profile writes a render-backed RGB MP4 without diagnostic fallback
- Notes: profiles=cpu/minimal/16x16, gpu/minimal/16x16, sapien_cuda/minimal/16x16; failure_classes=vulkan_descriptor_pool_exhaustion

### accepted_machine_driver_probe

- Owner: `independent_operator`
- Status: `required_before_fidelity_acceptance`
- Command: `python scripts\probe_external_platform.py --strict`
- Acceptance: record exact GPU/Vulkan/SAPIEN/ManiSkill provenance for the collection machine
- Notes: compare driver/runtime provenance against this local failing machine

### render_backed_video_gate

- Owner: `jason_or_operator`
- Status: `must_remain_enforced`
- Command: `python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix`
- Acceptance: all four primary task families write render-backed MP4s on the accepted machine
- Notes: resource sweep cannot replace the four-task render preflight

### diagnostic_fallback_exclusion

- Owner: `jason_or_operator`
- Status: `must_remain_enforced`
- Command: `python scripts\validate_external_rollouts.py --strict --write-results`
- Acceptance: diagnostic fallback sidecars and quarantined sweep media are absent from external_validation/manifest.json
- Notes: sweep outputs stay under external_validation/render_resource_sweep

## Checks

- `pass` `resource_sweep_is_non_evidence`: sweep writes only quarantine outputs and audit files
- `pass` `profiles_loaded`: profiles=3
- `pass` `primary_env_loaded`: env_rows=[{'task_family': 'peg_place_regrasp', 'env_id': 'PegInsertionSide-v1'}]
- `pass` `each_probe_has_terminal_status`: records=3
- `pass` `quarantine_paths_are_not_official_evidence`: sweep_root=external_validation/render_resource_sweep
- `pass` `descriptor_pool_failure_classified_or_render_ready`: any_ready=False, classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent

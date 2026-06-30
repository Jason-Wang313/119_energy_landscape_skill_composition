# ManiSkill Render Host Qualification Brief Audit

Passed: `true`.
Not evidence: `true`.
Host qualification state: `RENDER_HOST_NOT_QUALIFIED`.
Collection gate: `DO_NOT_COLLECT_RENDER_MACHINE`.
Strict external evidence ready: `false`.

## Checks

- `pass` `brief_is_non_evidence`: brief is an operator qualification artifact only
- `pass` `current_render_host_fails_closed`: qualification_state='DO_NOT_COLLECT_RENDER_MACHINE', render_machine_qualified=False, render_video_ready=False
- `pass` `vulkan_descriptor_pool_failure_preserved`: classes=['vulkan_descriptor_pool_exhaustion'], stages=['initial_render_start'], errors=['vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory']
- `pass` `minimum_resource_sweep_preserved`: sweep_failures=[{'profile': 'cpu/minimal/16x16', 'env_id': 'PegInsertionSide-v1', 'error': 'vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', 'failure_progress_stage': 'initial_render_start', 'last_progress_stage': 'close_done'}, {'profile': 'gpu/minimal/16x16', 'env_id': 'PegInsertionSide-v1', 'error': 'vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', 'failure_progress_stage': 'initial_render_start', 'last_progress_stage': 'close_done'}, {'profile': 'sapien_cuda/minimal/16x16', 'env_id': 'PegInsertionSide-v1', 'error': 'vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory', 'failure_progress_stage': 'initial_render_start', 'last_progress_stage': 'close_done'}]
- `pass` `pilot_liveness_guard_preserved`: pilot_runtime_ready=False, render_video_ready=False, guard=True, fallbacks=1
- `pass` `official_source_urls_present`: source_check_date=2026-06-30
- `pass` `operator_commands_cover_probe_sweep_preflight_liveness_qualification`: operator command spine covers host probe, render sweep, render preflight, pilot liveness, qualification, fidelity acceptance, and collection readiness
- `pass` `acceptance_criteria_close_all_render_host_gates`: criteria=5
- `pass` `haonan_is_not_a_dependency`: brief requires independent operator evidence and does not depend on Haonan or Yilun
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence

## Output Files

- `docs/maniskill_render_host_qualification_brief.md`
- `external_validation/render_host_qualification_brief.md`
- `results/maniskill_render_host_qualification_brief_audit.json`

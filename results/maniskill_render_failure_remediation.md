# ManiSkill Render Failure Remediation Packet

Passed: `true`.
Not evidence: `true`.
Remediation state: `RENDER_REMEDIATION_REQUIRED`.
Qualification state: `DO_NOT_COLLECT_RENDER_MACHINE`.
Renderer failure classes: `['vulkan_descriptor_pool_exhaustion']`.
Renderer failure stages: `['initial_render_start']`.
Liveness last progress stage: `record_video_start`.
Liveness last backend progress stage: `reset_scene_return`.

This packet converts the current render-backed-video blocker into operator work orders. It is not rollout evidence, cannot satisfy strict external evidence, and cannot promote diagnostic fallback media.

## Liveness Render Errors

- `RuntimeError: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory`

## Diagnostic Fallbacks

- `external_validation/pilot_runtime_guard/videos/peg_place_regrasp/paper119_blind_peg_place_regrasp_r000_method_05.4D84DD563A0C.staging.mp4.diagnostic.json`

## Work Orders

### renderer_platform_probe

- Owner: `independent_operator`
- Status: `blocked_until_rerun_on_collection_machine`
- Command: `python scripts\probe_external_platform.py`
- Acceptance: platform probe records exact collection machine, package versions, GPU/Vulkan driver, renderer backend, code commit, and config hashes
- Notes: primary_envs=PegInsertionSide-v1,OpenCabinetDrawer-v1,OpenCabinetDoor-v1,PullCubeTool-v1

### render_profile_matrix_retest

- Owner: `independent_operator`
- Status: `blocked_until_render_backed_mp4_success`
- Command: `python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180`
- Acceptance: all four primary task-family environments write render-backed RGB MP4 files without diagnostic fallback media
- Notes: failure_classes=vulkan_descriptor_pool_exhaustion; failure_stages=initial_render_start

### pilot_liveness_retest

- Owner: `independent_operator`
- Status: `blocked_until_pilot_runtime_ready`
- Command: `python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180 --max-rows 1`
- Acceptance: pilot_runtime_ready=true, render_video_ready=true, runner_io_ready=true, records>=1, videos>=1, and diagnostic_video_fallbacks=0
- Notes: last_backend_stage=reset_scene_return; liveness_errors=RuntimeError: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory

### diagnostic_fallback_exclusion

- Owner: `jason_or_operator`
- Status: `must_remain_enforced`
- Command: `python scripts\validate_external_rollouts.py --strict --write-results`
- Acceptance: diagnostic fallback sidecars, staged files, and pilot_runtime_guard outputs are absent from external_validation/manifest.json
- Notes: fallbacks=external_validation/pilot_runtime_guard/videos/peg_place_regrasp/paper119_blind_peg_place_regrasp_r000_method_05.4D84DD563A0C.staging.mp4.diagnostic.json

### fidelity_acceptance_after_render_ready

- Owner: `independent_operator`
- Status: `blocked_until_render_and_liveness_ready`
- Command: `python scripts\materialize_fidelity_acceptance.py --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write <operator fields>`
- Acceptance: guarded fidelity acceptance is written only after render-backed video readiness, platform provenance, paired replay, code/skill hashes, and independent signoff; rollout evidence and manifest declaration remain postcollection gates
- Notes: qualification_state=DO_NOT_COLLECT_RENDER_MACHINE; blockers=12

### collection_readiness_gate

- Owner: `jason_or_operator`
- Status: `blocked_until_fidelity_acceptance_and_render_ready`
- Command: `python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map`
- Acceptance: strict collection readiness passes before official collection spends simulator or robot time
- Notes: run this after render profile matrix, pilot liveness, and fidelity acceptance gates pass

## Checks

- `pass` `render_failure_remediation_is_non_evidence`: packet is a work-order artifact only
- `pass` `remediation_inherits_fail_closed_state`: state=DO_NOT_COLLECT_RENDER_MACHINE, qualified=False
- `pass` `liveness_render_guard_failure_captured`: pilot_runtime_ready=False, official_guard=True, render_errors=['RuntimeError: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory']
- `pass` `work_orders_cover_required_gate_sequence`: work_orders=6
- `pass` `diagnostic_fallbacks_remain_blocking_when_present`: diagnostic_fallbacks=['external_validation/pilot_runtime_guard/videos/peg_place_regrasp/paper119_blind_peg_place_regrasp_r000_method_05.4D84DD563A0C.staging.mp4.diagnostic.json'], state=DO_NOT_COLLECT_RENDER_MACHINE
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence

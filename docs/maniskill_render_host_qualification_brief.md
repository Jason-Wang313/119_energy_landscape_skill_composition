# ManiSkill Render Host Qualification Brief

This is a non-evidence operator brief for the Paper 119 skill-seam world/action-model validation route. It explains why the current local render host must not collect evidence and what a replacement host must prove before official collection can begin.

State: `RENDER_HOST_NOT_QUALIFIED`.
Collection gate: `DO_NOT_COLLECT_RENDER_MACHINE`.
Render machine qualified: `false`.
Strict external evidence ready: `false`.
Haonan dependency: `false`.

## Current No-Go

- Renderer failure classes: `['vulkan_descriptor_pool_exhaustion']`
- Renderer failure stages: `['initial_render_start']`
- Error signatures: `['vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory']`
- Render video ready: `false`
- Pilot runtime ready: `false`
- Runner I/O ready: `false`
- Diagnostic fallback count: `1`

The current local machine fails at `initial_render_start` with `vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory`. The 16x16 sweep reproduces the failure across the tested `cpu/minimal`, `gpu/minimal`, and `sapien_cuda/minimal` render profiles, so the next step is a different qualified host, not official collection on this machine.

## Minimum Resource Sweep Evidence

- `cpu/minimal/16x16` on `PegInsertionSide-v1`: `vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory` (failure stage `initial_render_start`, terminal stage `close_done`)
- `gpu/minimal/16x16` on `PegInsertionSide-v1`: `vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory` (failure stage `initial_render_start`, terminal stage `close_done`)
- `sapien_cuda/minimal/16x16` on `PegInsertionSide-v1`: `vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory` (failure stage `initial_render_start`, terminal stage `close_done`)

## Host Requirements

- Run on an independent GPU/Vulkan-capable collection machine rather than the current local host.
- Capture exact OS, Python, package, GPU, driver, Vulkan, ManiSkill, SAPIEN, code commit, and config/backend hashes with the strict platform probe.
- Pass render-backed MP4 preflight for every primary task-family environment using the accepted render backend and shader pack.
- Pass bounded pilot runtime liveness with JSONL writer ready, render_video_ready=true, runner_io_ready=true, and zero diagnostic fallback videos.
- Only after those pass, materialize fidelity acceptance and rerun strict collection readiness; do not write external_validation/manifest.json beforehand.

## Operator Command Spine

```powershell
python scripts\probe_external_platform.py --strict
```
```powershell
python scripts\audit_maniskill_render_resource_sweep.py --timeout-seconds 45 --max-envs 1
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
```
```powershell
python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --render-width 128 --render-height 128
```
```powershell
python scripts\build_maniskill_render_machine_qualification.py
```
```powershell
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
```
```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map
```

## Close Criteria

- results/maniskill_render_machine_qualification.json reports qualification_state=QUALIFIED_FOR_RENDER_BACKED_PILOT and render_machine_qualified=true on the accepted machine.
- results/maniskill_render_video_preflight_audit.json reports render_video_ready=true and render-backed MP4 success for PegInsertionSide-v1, OpenCabinetDrawer-v1, OpenCabinetDoor-v1, and PullCubeTool-v1.
- results/maniskill_pilot_runtime_liveness_audit.json reports pilot_runtime_ready=true, render_video_ready=true, runner_io_ready=true, records_observed>=1, videos_written>=1, and diagnostic_video_fallbacks=0.
- The official video guard remains enabled and no diagnostic fallback, staging, placeholder, or local dry-run media enters external_validation/manifest.json.
- Fidelity acceptance and collection readiness pass after render qualification; strict external evidence remains false until real manifest-declared logs, videos, configs, baselines, and recomputed metrics pass.

## Official Source Anchors

- ManiSkill installation docs: https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html - Use this as the install and supported-environment anchor before rerunning render probes.
- SAPIEN documentation: https://sapien.ucsd.edu/docs/latest/index.html - Record the exact SAPIEN version, renderer, GPU/Vulkan path, and scene/render settings.
- Vulkan vkAllocateDescriptorSets reference: https://registry.khronos.org/vulkan/specs/latest/man/html/vkAllocateDescriptorSets.html - The current failure signature is a descriptor-pool allocation failure surfaced through SAPIEN/Vulkan.

## Boundary

This brief does not produce rollout evidence, does not write `external_validation/manifest.json`, and cannot satisfy strict external evidence by itself. It is intentionally independent of Haonan/Yilun; a collaboration can improve the paper, but the validation route must stand without requiring them.


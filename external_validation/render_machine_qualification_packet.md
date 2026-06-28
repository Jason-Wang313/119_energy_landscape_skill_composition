# ManiSkill Render Machine Qualification

Passed: `true`.
Not evidence: `true`.
Qualification state: `DO_NOT_COLLECT_RENDER_MACHINE`.
Render machine qualified: `false`.
Strict external evidence ready: `false`.

This packet is an operator gate for the exact machine that will collect render-backed videos. It does not run collection, does not write `external_validation/manifest.json`, and does not turn diagnostic fallback videos into evidence.

## Required Proof Before Official Collection

- `results/external_platform_probe.json` must describe the exact accepted collection machine.
- `results/maniskill_render_video_preflight_audit.json` must report render-backed MP4 success for every primary task family on that machine.
- `results/maniskill_pilot_runtime_liveness_audit.json` must report `pilot_runtime_ready=true`, `render_video_ready=true`, and zero diagnostic fallback videos.
- The independent operator must reference these artifacts in the fidelity acceptance materializer before official collection.

## Blocking Missing

- render_video_ready is false in results/maniskill_render_video_preflight_audit.json
- PegInsertionSide-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- PegInsertionSide-v1 did not write a renderer-backed MP4
- OpenCabinetDrawer-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- OpenCabinetDrawer-v1 did not write a renderer-backed MP4
- OpenCabinetDoor-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- OpenCabinetDoor-v1 did not write a renderer-backed MP4
- PullCubeTool-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- PullCubeTool-v1 did not write a renderer-backed MP4
- pilot runtime liveness is not ready on the selected machine
- pilot runtime used diagnostic fallback video; fallback media cannot count as external evidence
- pilot runtime render_video_ready is false

## Operator Commands

```powershell
python scripts\probe_external_platform.py
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1
```
```powershell
python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180
```
```powershell
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write
```
```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map
```

## Checks

- `pass` `qualification_packet_is_non_evidence`: this script writes only packet/audit files
- `pass` `source_audits_loaded`: expected_envs=['PegInsertionSide-v1', 'OpenCabinetDrawer-v1', 'OpenCabinetDoor-v1', 'PullCubeTool-v1']
- `pass` `render_preflight_remains_non_evidence`: not_external_evidence=True, strict=False
- `pass` `all_primary_envs_have_terminal_render_records`: records=4, expected=['PegInsertionSide-v1', 'OpenCabinetDrawer-v1', 'OpenCabinetDoor-v1', 'PullCubeTool-v1']
- `pass` `qualification_state_matches_render_and_liveness`: state=DO_NOT_COLLECT_RENDER_MACHINE, blockers=12
- `pass` `current_machine_fail_closed_when_render_not_ready`: state=DO_NOT_COLLECT_RENDER_MACHINE, render_video_ready=False
- `pass` `diagnostic_fallbacks_block_evidence`: diagnostic_fallbacks=1, state=DO_NOT_COLLECT_RENDER_MACHINE
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence
- `pass` `operator_commands_cover_platform_render_liveness_acceptance_and_collection_readiness`: operator qualification commands are present

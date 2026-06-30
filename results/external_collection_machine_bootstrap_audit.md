# External Collection Machine Bootstrap Audit

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Bootstrap state: `READY_TO_BOOTSTRAP_EXTERNAL_MACHINE`.
Command file: `external_validation/collection_machine_bootstrap.ps1`.
Linux command file: `external_validation/collection_machine_bootstrap.sh`.

This packet prepares the independent collection machine before fidelity acceptance or official collection. It does not write `external_validation/manifest.json`, official JSONL logs, rollout videos, checkpoints, or fidelity acceptance files.

## Current Local State

- `primary_route_install_ready`: `True`
- `task_binding_ready`: `True`
- `env_smoke_ready`: `True`
- `fidelity_metadata_ready`: `True`
- `render_video_ready`: `False`
- `pilot_runtime_ready`: `False`
- `render_machine_qualified`: `False`
- `render_machine_state`: `DO_NOT_COLLECT_RENDER_MACHINE`
- `renderer_failure_classes`: `['vulkan_descriptor_pool_exhaustion']`
- `missing_asset_ids`: `['oakink-v2', 'ycb']`

## Bootstrap Steps

1. `python scripts\probe_external_platform.py --strict`
2. `python scripts\probe_maniskill_task_bindings.py --strict`
3. `python scripts\probe_maniskill_env_smoke.py --strict`
4. `python scripts\probe_maniskill_fidelity_metadata.py --strict`
5. `python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64`
6. `python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --render-width 128 --render-height 128`
7. `python scripts\build_maniskill_render_machine_qualification.py`

## Preconditions

- Use an independent GPU/Vulkan collection machine or robot-lab machine, not the current failing local render path.
- Run this bootstrap before materializing fidelity acceptance or official collection.
- Do not proceed unless render-machine qualification reports render_machine_qualified=true and pilot_runtime_ready=true with zero diagnostic fallbacks.
- After bootstrap success, use the guarded collection job packet for fidelity acceptance, strict readiness, official collection, postcollection sealing, manifest promotion, and final strict audits.

## Remaining Submission Blockers

- accepted real-robot or high-fidelity simulator evidence
- external rollout metrics recomputed from raw JSONL logs
- manifest-declared real task configs
- manifest-declared independent non-oracle baseline evidence

## Checks

- `pass` `bootstrap_packet_is_non_evidence`: machine bootstrap probes only; it does not write official logs, videos, manifests, or acceptance files
- `pass` `source_platform_onboarding_ready`: ready=True, strict=False
- `pass` `source_collection_job_still_no_go`: job_state='DO_NOT_START_COLLECTION_YET', strict=False
- `pass` `local_machine_not_promoted`: qualified=False, state='DO_NOT_COLLECT_RENDER_MACHINE'
- `pass` `bootstrap_commands_cover_machine_render_and_liveness`: bootstrap command file covers platform, task, env, metadata, render, pilot, and qualification probes
- `pass` `bootstrap_requires_explicit_confirmation`: PowerShell and Bash bootstrap command files require explicit bootstrap-only confirmation before running probes
- `pass` `bootstrap_script_is_probe_only`: forbidden_fragments=[]
- `pass` `bash_command_file_uses_lf_line_endings`: crlf_count=0, lf_count=77
- `pass` `install_guidance_mentions_core_optional_stack`: optional installer covers local package deps, ManiSkill/SAPIEN dependency path, Torch, and video encoding
- `pass` `no_real_outputs_written`: manifest/log/video evidence files remain absent before official collection

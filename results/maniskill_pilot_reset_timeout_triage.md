# ManiSkill Pilot Reset Timeout Triage

Status: `RESET_SCENE_TIMEOUT_TRIAGE_READY`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Reset timeout: `true`.
Failure summary: `runner timed out after progress stage reset_scene_start before producing the required pilot record/video`.

## Active Row

- Row index: `1`
- Task family: `peg_place_regrasp`
- Scene: `peg_place_regrasp_reset_000`
- Seed: `0`
- Blind run id: `paper119_blind_peg_place_regrasp_r000_method_05`
- Method alias: `method_05`
- Method: `energy_compatibility_heuristic`

## Bound Config

- Config path: `external_validation/configs/peg_place_regrasp.json`
- Config hash: `A731AFA16ED0ECD963A053C84EA0421363B8340EF8EA92F87D21F6F7099E5501`
- Primary env id: `PegInsertionSide-v1`
- Primary route: `maniskill_sapien_primary`
- Binding strength: `direct_contact_candidate`
- Skill seam: `place_peg_on_fixture -> regrasp_for_insertion`
- Seam under test: `terminal peg pose must lie inside the next insertion or regrasp basin`

## Gate Commands

- `python scripts\audit_maniskill_backend_readiness.py`
- `python scripts\audit_maniskill_render_video_preflight.py --profile-matrix --timeout-diagnosis-seconds 30`
- `python scripts\build_maniskill_render_machine_qualification.py`
- `python scripts\audit_maniskill_reference_collection_preflight.py`
- `python scripts\audit_external_collection_readiness.py --backend-module external_validation\runner\maniskill_reference_backend.py --unsealed-alias-map --run-id maniskill_sapien_reference_preflight_protocol_v1`

## Operator Next Actions

- Rerun the liveness audit on the exact candidate collection machine with the intended render backend, shader pack, and timeout, and keep outputs under external_validation/pilot_runtime_guard only.
- Run python scripts\audit_maniskill_render_video_preflight.py --profile-matrix --timeout-diagnosis-seconds 30 before retrying official collection for peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
- Run python scripts\build_maniskill_render_machine_qualification.py and do not collect official evidence until the exact machine is qualified for render-backed RGB MP4 export and pilot liveness.
- Inspect the bound task config, primary_env_id, installed ManiSkill assets, reset seed, and SAPIEN renderer logs for the reset-scene target peg_place_regrasp/PegInsertionSide-v1/energy_compatibility_heuristic.
- If reset still hangs, replace or rebind the task in external_validation/fidelity_acceptance.json only after independent operator signoff, then rerun collection readiness before any official rollout.
- Do not promote quarantined pilot logs, diagnostic videos, fallback sidecars, or partial reset attempts into external_validation/manifest.json.

## Evidence Boundary

This triage report is a pre-collection work order only. It cannot satisfy strict external evidence, cannot write external_validation/manifest.json, and cannot promote quarantined pilot outputs.

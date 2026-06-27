# External Fidelity Acceptance Draft

Draft ready: `true`.
Not evidence: `true`.
Acceptance ready: `false`.
Strict fidelity evidence ready: `false`.

This is an operator-editable draft for the tracked ManiSkill/SAPIEN route. It pre-fills reproducible anchors from the current platform probe, backend readiness audit, task bindings, config hashes, and environment smoke probe. It is deliberately not accepted evidence.

## Candidate Platform Snapshot

- Platform: `ManiSkill-SAPIEN-reference-backend`
- Version: `ManiSkill 3.0.1; SAPIEN 3.0.3`
- Physics engine: `SAPIEN 3.0.3 via ManiSkill`
- Backend hash: `E30E5A3292B6ACB7B9819914A6FDA6BD068B5B469031EEF1FF4E7AA852D140B2`
- Candidate skill-library hash: `62EA64D1C80D67F5EB7EC63A88A581AE2D89B4230873F11D46799658541411F1`
- Code commit captured in draft: `5cfd85dd14a26b1e6c51974d4459aca4d42fe2df`
- Primary route install ready: `true`
- Primary env smoke recorded: `true`
- Primary env smoke ready: `true`
- Primary reset missing: `[]`

## Remaining Operator Inputs

- `independent_operator_identity`
- `accepted_external_collection_machine`
- `contact_solver_and_friction_model`
- `timestep_and_substeps_per_control_step`
- `paired_reset_replay_verification`
- `real_or_benchmark_calibration_basis`
- `task_binding_accept_or_replace_decision`
- `acceptance_gate_signoff`
- `manifest_declares_fidelity_acceptance_path`
- `real_rollout_logs_videos_and_release_hashes`

## Task Bindings

- `peg_place_regrasp`: primary `PegInsertionSide-v1`, reset_ok=`true`, config_sha256=`021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`
- `drawer_to_pick_transfer`: primary `OpenCabinetDrawer-v1`, reset_ok=`true`, config_sha256=`1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`
- `door_open_navigation`: primary `OpenCabinetDoor-v1`, reset_ok=`true`, config_sha256=`13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`
- `cable_route_insert`: primary `PullCubeTool-v1`, reset_ok=`true`, config_sha256=`8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`

## Acceptance Gates

- `platform_provenance_complete`: `draft_unaccepted`
- `paired_reset_replay_verified`: `draft_unaccepted`
- `contact_failure_observable`: `draft_unaccepted`
- `non_oracle_methods_fair`: `draft_unaccepted`
- `raw_logs_drive_metrics`: `draft_unaccepted`

## Promotion Commands

- `copy external_validation\fidelity_acceptance_draft.json external_validation\fidelity_acceptance.json`
- `edit external_validation\fidelity_acceptance.json: change version to paper119_fidelity_acceptance_v1, remove draft_only, fill every remaining operator input, and set gates only after evidence exists`
- `ensure external_validation/manifest.json declares fidelity_acceptance_path=external_validation/fidelity_acceptance.json together with real logs, videos, configs, checkpoints, and method hashes`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`

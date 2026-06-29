# External Fidelity Acceptance Draft

Draft ready: `true`.
Not evidence: `true`.
Acceptance ready: `false`.
Strict fidelity evidence ready: `false`.
Machine-prefilled ready: `true`.
Operator signoff ready: `false`.

This is an operator-editable draft for the tracked ManiSkill/SAPIEN route. It pre-fills reproducible anchors from the current platform probe, backend readiness audit, task bindings, config hashes, and environment smoke probe. It is deliberately not accepted evidence.

## Candidate Platform Snapshot

- Platform: `ManiSkill-SAPIEN-reference-backend`
- Version: `ManiSkill 3.0.1; SAPIEN 3.0.3`
- Physics engine: `SAPIEN 3.0.3 via ManiSkill`
- Backend hash: `3479C8AEA42FC8BCDFF30B8108AD70733136945748F02785A18100FAAEF3A255`
- Candidate skill-library hash: `4C61DDC8C023352568E44AAFF4F7D0B85B9DC4ADE8AAACB23680CD510E05F6EA`
- Code commit captured in draft: `a93abb937260db146e97adbb4b68f4b814ed6b0d`
- Primary route install ready: `true`
- Primary env smoke recorded: `true`
- Primary env smoke ready: `true`
- Primary reset missing: `[]`
- Fidelity metadata probe ready: `true`
- Strict fidelity metadata ready: `true`
- Probe-observed timing summary: `{'agent_uids': ['fetch', 'panda', 'panda_wristcam'], 'control_freq_hz_values': [20.0], 'control_timestep_seconds_values': [0.05], 'controller_types': ['CombinedController'], 'derived_substeps_per_control_step_values': [5.0], 'primary_metadata_env_count': 4, 'scene_backend_types': ['PhysxCpuSystem'], 'scene_timestep_seconds_values': [0.01], 'sim_freq_hz_values': [100.0], 'sim_timestep_seconds_values': [0.01]}`

## Promotion Readiness

- Promotion ready: `false`
- Machine-prefilled ready: `true`
- Task metadata ready: `true`
- Operator signoff ready: `false`
- Operator signoff items: `10`

Machine-prefilled items:

- `primary_route_package_versions`: `true`
- `primary_env_smoke_status`: `true`
- `primary_fidelity_metadata_timing`: `true`
- `primary_task_config_hashes`: `true`
- `reference_backend_hash`: `true`
- `skill_library_hash`: `true`
- `support_asset_blockers_visible`: `true`

Operator signoff items:

- `independent_operator_identity`: accepted=`false`
- `accepted_external_collection_machine`: accepted=`false`
- `contact_solver_and_friction_model`: accepted=`false`
- `timestep_and_substeps_per_control_step`: accepted=`false`
- `paired_reset_replay_verification`: accepted=`false`
- `real_or_benchmark_calibration_basis`: accepted=`false`
- `task_binding_accept_or_replace_decision`: accepted=`false`
- `acceptance_gate_signoff`: accepted=`false`
- `manifest_declares_fidelity_acceptance_path`: accepted=`false`
- `real_rollout_logs_videos_and_release_hashes`: accepted=`false`

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

- `peg_place_regrasp`: primary `PegInsertionSide-v1`, reset_ok=`true`, metadata_reset_ok=`true`, sim_dt=`0.01`, control_dt=`0.05`, substeps=`5.0`, backend=`PhysxCpuSystem`, config_sha256=`021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`
- `drawer_to_pick_transfer`: primary `OpenCabinetDrawer-v1`, reset_ok=`true`, metadata_reset_ok=`true`, sim_dt=`0.01`, control_dt=`0.05`, substeps=`5.0`, backend=`PhysxCpuSystem`, config_sha256=`1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`
- `door_open_navigation`: primary `OpenCabinetDoor-v1`, reset_ok=`true`, metadata_reset_ok=`true`, sim_dt=`0.01`, control_dt=`0.05`, substeps=`5.0`, backend=`PhysxCpuSystem`, config_sha256=`13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`
- `cable_route_insert`: primary `PullCubeTool-v1`, reset_ok=`true`, metadata_reset_ok=`true`, sim_dt=`0.01`, control_dt=`0.05`, substeps=`5.0`, backend=`PhysxCpuSystem`, config_sha256=`8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`

## Acceptance Gates

- `platform_provenance_complete`: `draft_unaccepted`
- `paired_reset_replay_verified`: `draft_unaccepted`
- `contact_failure_observable`: `draft_unaccepted`
- `non_oracle_methods_fair`: `draft_unaccepted`
- `raw_logs_drive_metrics`: `draft_unaccepted`

## Promotion Commands

- `python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write`
- `verify external_validation\fidelity_acceptance.json has version paper119_fidelity_acceptance_v1 and no draft_only/template_only fields before manifest declaration`
- `ensure external_validation/manifest.json declares fidelity_acceptance_path=external_validation/fidelity_acceptance.json together with real logs, videos, configs, checkpoints, and method hashes`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`

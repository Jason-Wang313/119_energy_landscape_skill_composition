# External Fidelity Acceptance Draft Audit

Passed: `true`.
Not evidence: `true`.
Draft ready: `true`.
Acceptance ready: `false`.
Remaining operator inputs: `10`.
Machine-prefilled ready: `true`.
Operator signoff ready: `false`.
Operator signoff items: `10`.

This audit checks that the draft is useful as an operator intake artifact while remaining impossible to count as accepted fidelity evidence.

## Checks

- `pass` `draft_is_non_evidence_and_fail_closed`: version='paper119_fidelity_acceptance_draft_v1', draft_only=True, acceptance_ready=False
- `pass` `candidate_platform_prefilled_from_reference_route`: platform_version='ManiSkill 3.0.1; SAPIEN 3.0.3', primary_route_install_ready=True, primary_env_smoke_recorded=True, primary_env_smoke_ready=True
- `pass` `all_core_tasks_have_primary_env_status_and_config_hash`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp'], hashes={'cable_route_insert': '8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E', 'door_open_navigation': '13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61', 'drawer_to_pick_transfer': '1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471', 'peg_place_regrasp': '021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9'}
- `pass` `fidelity_metadata_probe_prefills_timing_and_task_records`: metadata_probe_ready=True, strict_metadata_ready=True, timing={'agent_uids': ['fetch', 'panda', 'panda_wristcam'], 'control_freq_hz_values': [20.0], 'control_timestep_seconds_values': [0.05], 'controller_types': ['CombinedController'], 'derived_substeps_per_control_step_values': [5.0], 'primary_metadata_env_count': 4, 'scene_backend_types': ['PhysxCpuSystem'], 'scene_timestep_seconds_values': [0.01], 'sim_freq_hz_values': [100.0], 'sim_timestep_seconds_values': [0.01]}
- `pass` `support_asset_blockers_remain_visible`: asset_sources=['ManiSkill primary task assets for PegInsertionSide-v1, OpenCabinetDrawer-v1, OpenCabinetDoor-v1, and PullCubeTool-v1', 'PartNet Mobility cabinet asset for OpenCabinetDrawer-v1/OpenCabinetDoor-v1 when required', 'Support assets not yet accepted for evidence: oakink-v2, ycb']
- `pass` `candidate_hashes_prefilled`: code_commit='a93abb937260db146e97adbb4b68f4b814ed6b0d', skill_hash='4C61DDC8C023352568E44AAFF4F7D0B85B9DC4ADE8AAACB23680CD510E05F6EA', backend_hash='3479C8AEA42FC8BCDFF30B8108AD70733136945748F02785A18100FAAEF3A255'
- `pass` `remaining_operator_inputs_cover_fidelity_gate`: missing=[]
- `pass` `promotion_readiness_separates_machine_prefill_from_operator_signoff`: machine_prefilled_ready=True, operator_signoff_ready=False, operator_items=10
- `pass` `acceptance_gates_remain_unaccepted`: gate_statuses=['draft_unaccepted', 'draft_unaccepted', 'draft_unaccepted', 'draft_unaccepted', 'draft_unaccepted']
- `pass` `promotion_commands_require_real_file_manifest_and_strict_audits`: python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write
verify external_validation\fidelity_acceptance.json has version paper119_fidelity_acceptance_v1 and no draft_only/template_only fields before manifest declaration
ensure external_validation/manifest.json declares fidelity_acceptance_path=external_validation/fidelity_acceptance.json together with real logs, videos, configs, checkpoints, and method hashes
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\audit_external_fidelity_acceptance.py --strict
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
- `pass` `promotion_readiness_lists_strict_promotion_gates`: python scripts\audit_external_fidelity_acceptance.py --strict
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
- `pass` `no_real_acceptance_or_manifest_written`: acceptance_exists=False, manifest_exists=False
- `pass` `draft_files_written`: draft_json=True, draft_md=True

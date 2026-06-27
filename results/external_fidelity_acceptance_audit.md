# External Fidelity Acceptance Audit

Passed: `true`.
Not external evidence: `true`.
Acceptance ready: `false`.
Readiness state: `COLLECT_PLATFORM_PROVENANCE`.
Source: `external_validation/fidelity_acceptance_template.json`.
Manifest exists: `false`.
Blocking missing items: `14`.

This audit defines the platform/provenance standard for real-robot or accepted high-fidelity simulator validation. It is not rollout evidence and does not replace strict JSONL, video, config, checkpoint, or baseline evidence.

## Blocking Missing Items

- manifest_exists: external_validation/manifest.json missing
- manifest_declares_acceptance_path: source_kind=template
- real_acceptance_file_exists: external_validation/fidelity_acceptance_template.json
- real_acceptance_version: version='paper119_fidelity_acceptance_template_v1', expected='paper119_fidelity_acceptance_v1'
- not_template_only: template_only=True
- route_matches_manifest: acceptance_route='high_fidelity_sim', manifest_route=''
- route_has_enough_task_families: route='high_fidelity_sim', counts={'real_robot': 0, 'high_fidelity_sim': 0}
- platform_values_filled: placeholder_fields=['asset_sources', 'contact_solver', 'physics_engine', 'platform_name', 'platform_version', 'robot_model_source', 'substeps_per_control_step', 'timestep_seconds']
- qualification_text_filled: weak_or_placeholder=['contact_dynamics_justification', 'known_limitations', 'operator_independence_statement', 'paired_reset_replay_test', 'real_or_benchmark_calibration_basis']
- operator_independence_declared: operator_not_target_collaborator=True
- date_locked_filled: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- code_commit_filled: code_commit=''
- skill_library_hash_valid: skill_library_hash must be 64-character SHA256
- all_acceptance_gates_passed: unpassed=['platform_provenance_complete', 'paired_reset_replay_verified', 'contact_failure_observable', 'non_oracle_methods_fair', 'raw_logs_drive_metrics']

## Contract Checks

- `pass` `template_exists`: external_validation/fidelity_acceptance_template.json
- `pass` `source_exists`: external_validation/fidelity_acceptance_template.json
- `pass` `recognized_version`: version='paper119_fidelity_acceptance_template_v1'
- `pass` `template_declares_not_evidence`: not_external_evidence=True
- `pass` `route_declared`: route='high_fidelity_sim'
- `pass` `platform_fields_present`: missing=[]
- `pass` `qualification_fields_present`: missing_flags=[], missing_text=[]
- `pass` `task_fidelity_covers_core_tasks`: missing=[]
- `pass` `acceptance_gates_present`: missing=[]

## Evidence Checks

- `fail` `manifest_exists`: external_validation/manifest.json missing
- `fail` `manifest_declares_acceptance_path`: source_kind=template
- `fail` `real_acceptance_file_exists`: external_validation/fidelity_acceptance_template.json
- `fail` `real_acceptance_version`: version='paper119_fidelity_acceptance_template_v1', expected='paper119_fidelity_acceptance_v1'
- `fail` `not_template_only`: template_only=True
- `fail` `route_matches_manifest`: acceptance_route='high_fidelity_sim', manifest_route=''
- `fail` `route_has_enough_task_families`: route='high_fidelity_sim', counts={'real_robot': 0, 'high_fidelity_sim': 0}
- `fail` `platform_values_filled`: placeholder_fields=['asset_sources', 'contact_solver', 'physics_engine', 'platform_name', 'platform_version', 'robot_model_source', 'substeps_per_control_step', 'timestep_seconds']
- `pass` `platform_type_valid`: platform_type='high_fidelity_sim'
- `pass` `modalities_cover_state_camera_contact`: sensor_modalities=['state', 'camera', 'contact_or_force']
- `pass` `contact_channels_declared`: contact_or_force_channels=['contact_events', 'normal_force_or_proxy']
- `pass` `qualification_flags_true`: false_or_missing=[]
- `fail` `qualification_text_filled`: weak_or_placeholder=['contact_dynamics_justification', 'known_limitations', 'operator_independence_statement', 'paired_reset_replay_test', 'real_or_benchmark_calibration_basis']
- `pass` `task_fidelity_details_filled`: weak_tasks=[]
- `fail` `operator_independence_declared`: operator_not_target_collaborator=True
- `fail` `date_locked_filled`: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- `fail` `code_commit_filled`: code_commit=''
- `fail` `skill_library_hash_valid`: skill_library_hash must be 64-character SHA256
- `pass` `artifact_hash_policy_sha256`: artifact_hash_policy='sha256'
- `fail` `all_acceptance_gates_passed`: unpassed=['platform_provenance_complete', 'paired_reset_replay_verified', 'contact_failure_observable', 'non_oracle_methods_fair', 'raw_logs_drive_metrics']

## Operator Next Actions

- Select an external robot or accepted high-fidelity simulator before collecting rollouts.
- Copy fidelity_acceptance_template.json to external_validation/fidelity_acceptance.json and change the version to paper119_fidelity_acceptance_v1.
- Fill platform physics/contact details, paired-reset replay evidence, operator independence, real/benchmark calibration basis, code commit, and skill-library hash.
- Declare fidelity_acceptance_path in external_validation/manifest.json before strict external evidence validation.
- Run audit_external_fidelity_acceptance.py --strict before counting any high-fidelity route as external evidence.

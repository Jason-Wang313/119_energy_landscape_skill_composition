# External Fidelity Acceptance Audit

Passed: `true`.
Not external evidence: `true`.
Acceptance ready: `false`.
Readiness state: `COLLECT_PLATFORM_PROVENANCE`.
Source: `external_validation/fidelity_acceptance_template.json`.
Manifest exists: `false`.
Blocking missing items: `17`.

This audit defines the platform/provenance standard for real-robot or accepted high-fidelity simulator validation. It is not rollout evidence and does not replace strict JSONL, video, config, checkpoint, or baseline evidence.

## Blocking Missing Items

- real_acceptance_file_exists: external_validation/fidelity_acceptance_template.json
- real_acceptance_version: version='paper119_fidelity_acceptance_template_v1', expected='paper119_fidelity_acceptance_v1'
- real_acceptance_declares_ready: acceptance_ready=None
- not_template_only: template_only=True
- strict_readiness_remains_external_to_acceptance: not_external_evidence=True, strict_fidelity_evidence_ready=None, strict_external_evidence_ready=None
- platform_values_filled: placeholder_fields=['asset_sources', 'contact_solver', 'physics_engine', 'platform_name', 'platform_version', 'robot_model_source', 'substeps_per_control_step', 'timestep_seconds']
- qualification_text_filled: weak_or_placeholder=['contact_dynamics_justification', 'known_limitations', 'operator_independence_statement', 'paired_reset_replay_test', 'real_or_benchmark_calibration_basis']
- operator_independence_declared: operator_not_target_collaborator=True
- date_locked_filled: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- date_locked_iso_like: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- code_commit_filled: code_commit=''
- code_commit_sha40: code_commit=''
- skill_library_hash_valid: skill_library_hash must be 64-character SHA256
- precollection_confirmation_booleans_true: real_platform_confirmed_by_operator=None, render_backed_videos_confirmed_by_operator=None
- postcollection_evidence_deferred_until_manifest: manifest_declaration_required_after_collection=None, real_rollout_evidence_required_after_collection=None, manifest_declaration_confirmed_by_operator=None, real_rollout_evidence_confirmed_by_operator=None
- materialized_by_guarded_path: materialized_by=None, materialized_from_draft_path=None
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

- `pass` `manifest_declaration_not_required_before_collection`: manifest_exists=False, source_kind=template, fidelity_acceptance_path=''
- `pass` `manifest_acceptance_path_consistent_when_present`: source=C:\Users\wangz\robotics_massive_pool_paper_factory\119_energy_landscape_skill_composition\external_validation\fidelity_acceptance_template.json, manifest_fidelity_acceptance_path=''
- `fail` `real_acceptance_file_exists`: external_validation/fidelity_acceptance_template.json
- `fail` `real_acceptance_version`: version='paper119_fidelity_acceptance_template_v1', expected='paper119_fidelity_acceptance_v1'
- `fail` `real_acceptance_declares_ready`: acceptance_ready=None
- `fail` `not_template_only`: template_only=True
- `pass` `not_draft_only`: draft_only=None
- `fail` `strict_readiness_remains_external_to_acceptance`: not_external_evidence=True, strict_fidelity_evidence_ready=None, strict_external_evidence_ready=None
- `pass` `route_matches_manifest_when_present`: acceptance_route='high_fidelity_sim', manifest_route='', manifest_exists=False
- `pass` `manifest_task_coverage_when_present`: route='high_fidelity_sim', counts={'real_robot': 0, 'high_fidelity_sim': 0}, manifest_exists=False
- `fail` `platform_values_filled`: placeholder_fields=['asset_sources', 'contact_solver', 'physics_engine', 'platform_name', 'platform_version', 'robot_model_source', 'substeps_per_control_step', 'timestep_seconds']
- `pass` `platform_type_valid`: platform_type='high_fidelity_sim'
- `pass` `modalities_cover_state_camera_contact`: sensor_modalities=['state', 'camera', 'contact_or_force']
- `pass` `contact_channels_declared`: contact_or_force_channels=['contact_events', 'normal_force_or_proxy']
- `pass` `qualification_flags_true`: false_or_missing=[]
- `fail` `qualification_text_filled`: weak_or_placeholder=['contact_dynamics_justification', 'known_limitations', 'operator_independence_statement', 'paired_reset_replay_test', 'real_or_benchmark_calibration_basis']
- `pass` `task_fidelity_details_filled`: weak_tasks=[]
- `fail` `operator_independence_declared`: operator_not_target_collaborator=True
- `fail` `date_locked_filled`: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- `fail` `date_locked_iso_like`: date_locked='FILL_AFTER_PLATFORM_SELECTION'
- `fail` `code_commit_filled`: code_commit=''
- `fail` `code_commit_sha40`: code_commit=''
- `fail` `skill_library_hash_valid`: skill_library_hash must be 64-character SHA256
- `pass` `artifact_hash_policy_sha256`: artifact_hash_policy='sha256'
- `fail` `precollection_confirmation_booleans_true`: real_platform_confirmed_by_operator=None, render_backed_videos_confirmed_by_operator=None
- `fail` `postcollection_evidence_deferred_until_manifest`: manifest_declaration_required_after_collection=None, real_rollout_evidence_required_after_collection=None, manifest_declaration_confirmed_by_operator=None, real_rollout_evidence_confirmed_by_operator=None
- `fail` `materialized_by_guarded_path`: materialized_by=None, materialized_from_draft_path=None
- `fail` `all_acceptance_gates_passed`: unpassed=['platform_provenance_complete', 'paired_reset_replay_verified', 'contact_failure_observable', 'non_oracle_methods_fair', 'raw_logs_drive_metrics']

## Operator Next Actions

- Select an external robot or accepted high-fidelity simulator before collecting rollouts.
- Use scripts/materialize_fidelity_acceptance.py with independent-operator signoff, real platform details, render-backed video readiness, paired-reset replay evidence, a SHA40 collection commit, and the current skill-library SHA256 to write external_validation/fidelity_acceptance.json before official collection.
- Fill platform physics/contact details, paired-reset replay evidence, operator independence, real/benchmark calibration basis, code commit, skill-library hash, and precollection confirmation booleans through the guarded materializer.
- After official collection and postcollection sealing, declare fidelity_acceptance_path in external_validation/manifest.json together with raw logs, videos, configs, methods, and hashes.
- Run audit_external_fidelity_acceptance.py --strict before collection readiness, then rely on manifest, rollout, release, pairing, adapter, config, and final evidence audits before counting any high-fidelity route as external evidence.

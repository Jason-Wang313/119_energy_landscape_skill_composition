# Local Model Release Audit

Passed: `true`.
Not external evidence: `true`.
Local model release ready: `true`.
External evidence ready: `false`.
Manifest: `results/local_model_release_manifest.json`.
Model card: `docs/local_model_release.md`.
Release hash: `5CF7C6E592517ECC40371074F6341C489BCAB11E5358E6BA053CB3AD241B5929`.

## Checks

- `pass` `source_exists`: src/run_experiment.py
- `pass` `source_version_matches_summary`: source='v5_expanded', summary='v5_expanded'
- `pass` `proposed_method_present`: hash=A70B9C802BAD07FE8621791EA8EA125EBD81B2DD877270DEC7CE89839A43D4E4
- `pass` `method_family_complete`: methods=12, hashes=12
- `pass` `local_dimensions_complete`: tasks=6, regimes=8, splits=5
- `pass` `summary_remains_bounded`: {'terminal_decision': 'STRONG_REVISE', 'iclr_main_ready': False, 'scope_gate_pass': False, 'local_gates_pass': True, 'strongest_non_oracle': 'proposed_energy_landscape_composer_v4_1', 'missing_scope_evidence': ['no_real_robot_rollouts', 'no_accepted_high_fidelity_skill_composition_simulation', 'no_released_skill_energy_or_policy_checkpoint', 'no_calibrated_contact_force_camera_or_state_logs', 'no_hardware_rollout_videos', 'no_independent_baseline_implementations']}
- `pass` `local_gates_pass`: local_gates_pass=True
- `pass` `result_artifacts_hash_locked`: missing=[]
- `pass` `reference_adapter_artifacts_hash_locked`: missing=[]
- `pass` `explicitly_not_external_evidence`: not_external_evidence=True, external_evidence_ready=False
- `pass` `not_a_robot_policy_checkpoint`: local deterministic seam model only
- `pass` `release_hash_present`: 5CF7C6E592517ECC40371074F6341C489BCAB11E5358E6BA053CB3AD241B5929

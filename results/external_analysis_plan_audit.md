# External Analysis Plan Audit

Passed: `true`.
Not evidence: `true`.
Analysis plan ready: `true`.
Strict evidence ready: `false`.

This audit checks that the external statistical analysis plan is locked, threshold-consistent with the rollout schema, and resistant to post-hoc cherry-picking. It is not external validation evidence.

## Checks

- `pass` `plan_is_non_evidence_and_locked`: not_external_evidence=True, locked=True
- `pass` `primary_method_matches_schema`: plan='barrier_certified_energy_composer_v5', schema='barrier_certified_energy_composer_v5'
- `pass` `thresholds_match_log_schema`: plan={'external_success_margin': 0.05, 'external_utility_margin': 0.08, 'paired_win_rate': 0.7, 'fixed_risk_breach': 0.02, 'fixed_risk_coverage': 0.55, 'positive_task_families': 3}, schema={'external_success_margin': 0.05, 'external_utility_margin': 0.08, 'paired_win_rate': 0.7, 'fixed_risk_breach': 0.02, 'fixed_risk_coverage': 0.55, 'positive_task_families': 3}
- `pass` `primary_hypotheses_cover_all_strict_thresholds`: missing=[]
- `pass` `confidence_gate_is_predeclared`: confidence_gate={'version': 'external_statistical_confidence_v1', 'confidence_level': 0.95, 'bootstrap_replicates': 1000, 'bootstrap_seed': 119, 'rule': 'For external_success_margin, external_utility_margin, paired_win_rate, and fixed_risk_coverage, the 95% bootstrap lower confidence bound must meet or exceed the predeclared threshold. For fixed_risk_breach, the 95% bootstrap upper confidence bound must be at or below the threshold. Positive task-family coverage remains a predeclared count gate.'}
- `pass` `paired_key_matches_schema`: plan=['task_family', 'platform_type', 'scene_id', 'seed', 'skill_i', 'skill_j', 'initial_state_hash'], schema=['task_family', 'platform_type', 'scene_id', 'seed', 'skill_i', 'skill_j', 'initial_state_hash']
- `pass` `collection_plan_record_budget_referenced`: planned=1440, collection=1440
- `pass` `decision_rule_requires_strict_external_gates`: strict_gates=['python scripts\\audit_external_release_package.py --strict', 'python scripts\\audit_external_fidelity_acceptance.py --strict', 'python scripts\\validate_external_configs.py --strict', 'python scripts\\validate_external_adapters.py --strict', 'python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict', 'python scripts\\audit_external_pairing_integrity.py --strict', 'python scripts\\audit_external_evidence.py --strict']
- `pass` `exclusion_policy_blocks_cherry_picking`: unit='paired_reset_method_panel'
- `pass` `unblinding_policy_preserves_blind_eval`: unblinding={'method_aliases_remain_sealed_until': ['backend module is qualified', 'task configs are materialized and hash-locked', 'fidelity acceptance is complete', 'run id is specific and immutable', 'operator sheet is frozen'], 'analysis_after_unblinding': 'run only the predeclared scripts and thresholds above; secondary plots are descriptive unless added to a new preregistered plan before collection.'}
- `pass` `required_reporting_covers_primary_and_audit_outputs`: missing=[]

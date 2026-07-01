# Diagnostic Mechanism Audit

Passed: `true`.
Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.

## Metrics

- Proposed hard rows: `13440`.
- Label counts: `{'basin_mismatch': 1440, 'contact_mode_discontinuity': 1440, 'high_barrier': 1581, 'missing_bridge_skill': 3360, 'model_uncertainty': 5619}`.
- Decision counts: `{'abstain': 5099, 'accept': 5429, 'probe': 1333, 'repair': 801, 'transition': 778}`.
- Accepted-seam mean realized breach: `0.076033`.
- Non-accepted-seam mean realized breach: `0.107993`.
- Accepted-seam mean predicted risk: `0.080526`.
- Abstained-seam mean predicted risk: `0.125391`.
- Reason purity: repair `1.000000`, probe `1.000000`, transition `1.000000`.

## Checks

- `pass` `not_external_evidence_declared`: local diagnostic audit only
- `pass` `proposed_hard_rows_ge_10000`: rows=13440
- `pass` `diagnostic_columns_valid`: invalid_labels=0, invalid_decisions=0
- `pass` `label_rule_matches_rows`: label_mismatches=0/230400
- `pass` `decision_rule_matches_rows`: decision_mismatches=0/230400
- `pass` `planner_update_matches_decision`: update_mismatches=0/230400
- `pass` `all_failure_labels_observed`: labels={'basin_mismatch': 1440, 'contact_mode_discontinuity': 1440, 'high_barrier': 1581, 'missing_bridge_skill': 3360, 'model_uncertainty': 5619}
- `pass` `all_decisions_observed`: decisions={'abstain': 5099, 'accept': 5429, 'probe': 1333, 'repair': 801, 'transition': 778}
- `pass` `mechanism_labels_have_targeted_metric_signature`: matched=4/5; means={'basin_mismatch': {'basin_alignment': 0.7682426555555556, 'barrier_violation_rate': 0.06046439861111111, 'descent_continuity': 0.7610020958333333, 'uncertainty_score': 0.12715524097222222, 'bridge_score': 0.27608437430555555}, 'missing_bridge_skill': {'basin_alignment': 0.7575236443452381, 'barrier_violation_rate': 0.08499581488095238, 'descent_continuity': 0.7374202904761905, 'uncertainty_score': 0.1611533255952381, 'bridge_score': 0.2953937678571429}, 'high_barrier': {'basin_alignment': 0.7650099493991145, 'barrier_violation_rate': 0.08711060974067046, 'descent_continuity': 0.7460013396584441, 'uncertainty_score': 0.14485275585072738, 'bridge_score': 0.29033481657179}, 'model_uncertainty': {'basin_alignment': 0.7500004612920449, 'barrier_violation_rate': 0.09109301566114968, 'descent_continuity': 0.7359926255561487, 'uncertainty_score': 0.17978658213205195, 'bridge_score': 0.29799417903541553}, 'contact_mode_discontinuity': {'basin_alignment': 0.7598181722222223, 'barrier_violation_rate': 0.08420314861111111, 'descent_continuity': 0.74243244375, 'uncertainty_score': 0.15693336944444444, 'bridge_score': 0.29234329375}}
- `pass` `accepted_seams_are_lower_breach`: accept_breach=0.076033, non_accept_breach=0.107993
- `pass` `abstained_seams_are_higher_risk`: accept_risk=0.080526, abstain_risk=0.125391
- `pass` `repair_probe_transition_reasons_are_specific`: repair=1.000000, probe=1.000000, transition=1.000000

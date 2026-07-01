# Decision Quality Audit

Passed: `true`.
Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.

## Metrics

- Baseline: `proposed_energy_landscape_composer_v4_1`.
- Paired hard rows: `13440`.
- Proposed decision counts: `{'abstain': 5099, 'accept': 5429, 'probe': 1333, 'repair': 801, 'transition': 778}`.
- Baseline decision counts: `{'abstain': 11857, 'probe': 5, 'repair': 1134, 'transition': 444}`.
- Accept coverage: proposed `0.403943`, baseline `0.000000`.
- Proposed accepted breach>0.15 rate: `0.000000`.
- Non-abstain utility delta: `+0.159801`.
- Non-abstain breach delta: `-0.051035`.
- Recovered accepts: `3850` pairs.
- Recovered-accept utility/success/breach deltas: `+0.242606`, `+0.091429`, `-0.077194`.
- Shared-abstain breach delta: `-0.078027`.

## Checks

- `pass` `not_external_evidence_declared`: local paired hard-row decision audit only
- `pass` `paired_hard_rows_ge_10000`: paired_hard_rows=13440
- `pass` `proposed_accept_coverage_ge_0_35`: coverage=0.403943
- `pass` `accept_coverage_beats_baseline_by_0_25`: delta=0.403943
- `pass` `proposed_accept_breach_rate_le_0_005`: breach_rate=0.000000
- `pass` `non_abstain_utility_delta_ge_0_10`: delta=0.159801
- `pass` `non_abstain_breach_delta_le_minus_0_03`: delta=-0.051035
- `pass` `recovered_accept_pairs_ge_3000`: pairs=3850
- `pass` `recovered_accept_utility_delta_ge_0_15`: delta=0.242606
- `pass` `recovered_accept_success_delta_ge_0_05`: delta=0.091429
- `pass` `recovered_accept_breach_delta_le_minus_0_05`: delta=-0.077194
- `pass` `recovered_accept_proposed_breach_rate_le_0_005`: breach_rate=0.000000
- `pass` `both_abstain_breach_delta_le_minus_0_05`: delta=-0.078027

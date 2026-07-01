# Manuscript Number Audit

Passed: `true`.

This audit checks that manuscript and table numbers are traceable to generated result files.

## Checks

- `pass` `abstract_proposed_hard_success_and_utility` from results/summary.json metrics.hard_success_proposed, hard_utility_proposed: `composer reaches hard-slice success 0.80171 and utility 0.88827`
- `pass` `abstract_strongest_baseline_values` from results/summary.json metrics.hard_success_strongest, hard_utility_strongest: `compared with 0.71711 and 0.65310`
- `pass` `evaluation_main_matrix_count` from results/summary.json row_counts.main_cell: `and 230,400 main cell rows`
- `pass` `evaluation_auxiliary_counts` from results/summary.json row_counts: `Ablations add 38,400 cells, stress sweeps add 161,280 cells, and fixed-risk tests add 107,520 cells`
- `pass` `main_result_margins` from results/summary.json metrics.hard_success_margin, hard_utility_margin: `improves hard success by 0.08460 and hard utility by 0.23517`
- `pass` `paired_hard_utility_wins` from results/summary.json metrics.paired_hard_utility_wins: `paired hard-utility wins are 10/10`
- `pass` `oracle_result_values` from results/summary.json metrics.hard_success_oracle, hard_utility_oracle: `The oracle remains stronger with success 0.90967 and utility 1.13988`
- `pass` `diagnostic_delta_sentence` from results/summary.json diagnostic deltas: `reduces seam failure by -0.04912, barrier violation by -0.04087, damage by -0.00579, composition cost by -0.04584, risk calibration error by -0.01055, and realized seam breach by -0.07565`
- `pass` `basin_and_descent_deltas` from results/summary.json metrics.basin_alignment_delta, descent_continuity_delta: `improves basin alignment by 0.08001 and descent continuity by 0.07809`
- `pass` `ablation_margin_sentence` from results/summary.json metrics.ablation_success_margin, ablation_utility_margin: `by 0.02812 success and 0.04349 utility`
- `pass` `diagnostic_zero_mismatch_sentence` from results/diagnostic_mechanism_audit.json mismatch counts: `Over 230,400 local rows, the diagnostic audit finds 0 label-rule mismatches, 0 decision-rule mismatches, and 0 planner-update mismatches`
- `pass` `diagnostic_hard_rows_sentence` from results/diagnostic_mechanism_audit.json proposed_hard_rows: `In the 13,440 proposed hard rows, all five failure labels and all five decisions appear`
- `pass` `diagnostic_accept_abstain_sentence` from results/diagnostic_mechanism_audit.json accept/abstain metrics: `Accepted seams have mean realized breach 0.076 versus 0.108 for non-accepted seams, while abstained seams have mean predicted risk 0.125 versus 0.081 for accepted seams`
- `pass` `diagnostic_reason_purity_sentence` from results/diagnostic_mechanism_audit.json reason purity: `Repair, probe, and transition decisions match their intended diagnostic reasons with purity 1.000, 1.000, and 1.000`
- `pass` `decision_quality_paired_rows_and_accept_coverage` from results/decision_quality_audit.json paired rows and accept coverage: `On the same 13,440 paired hard rows, the proposed model accepts 0.404 of hard seams versus 0.000 for the predecessor, while the rate of accepted seams above the 0.15 breach budget is 0.000`
- `pass` `decision_quality_non_abstain_sentence` from results/decision_quality_audit.json non-abstain utility and breach: `Among non-abstained seams, utility is 0.935 versus 0.776 and realized breach is 0.082 versus 0.133`
- `pass` `decision_quality_recovered_accepts_sentence` from results/decision_quality_audit.json recovered accept deltas: `3,850 paired seams are accepted by v5 and abstained from by the predecessor; those recovered accepts improve utility by 0.243, success by 0.091, and realized breach by -0.077`
- `pass` `planner_edge_frontier_sentence` from results/planner_edge_policy_audit.json frontier_count: `This produces 1,680 paired planning-frontier decisions and does not use realized utility to choose the edge`
- `pass` `planner_edge_coverage_sentence` from results/planner_edge_policy_audit.json executable coverage: `The proposed seam model selects executable accept/repair/transition edges on 0.667 of frontiers versus 0.165 for the strongest predecessor`
- `pass` `planner_edge_selected_outcome_sentence` from results/planner_edge_policy_audit.json selected-edge outcomes: `Selected-edge utility is 0.889 versus 0.658, success is 0.795 versus 0.715, and realized breach is 0.089 versus 0.164`
- `pass` `planner_edge_positive_groups_sentence` from results/planner_edge_policy_audit.json positive group counts: `The selected-edge utility margin is positive in 6/6 task families, 7/7 seam regimes, and 4/4 deployment splits`
- `pass` `failure_memory_signature_count_sentence` from results/failure_memory_adaptation_audit.json signature and frontier counts: `This yields 2,210 observed-to-held-out signature pairs over 1,667 frontiers`
- `pass` `failure_memory_predictive_sentence` from results/failure_memory_adaptation_audit.json predictive memory metrics: `Observed breach predicts held-out breach with correlation 0.957 and MAE 0.005, improving on held-out predicted-risk MAE by 0.003`
- `pass` `failure_memory_high_low_sentence` from results/failure_memory_adaptation_audit.json high/low memory metrics: `High-memory-risk signatures have held-out breach 0.120 versus 0.074 for low-memory-risk signatures, and held-out utility 0.796 versus 0.956`
- `pass` `failure_memory_predecessor_sentence` from results/failure_memory_adaptation_audit.json predecessor comparison: `Against the predecessor's high-memory-risk signatures, v5 reduces future breach by 0.083 and raises future utility by 0.248`
- `pass` `calibration_ece_sentence` from results/seam_prediction_calibration_audit.json ECE and max gap: `ten-bin local calibration error between predicted seam risk and realized seam breach is 0.007, compared with 0.015 for the strongest predecessor; the maximum bin gap is 0.013`
- `pass` `calibration_mean_correlation_sentence` from results/seam_prediction_calibration_audit.json mean and correlation metrics: `Mean predicted risk is 0.102 versus realized breach 0.095, with risk-breach correlation 0.971 and Spearman 0.950`
- `pass` `calibration_decile_sentence` from results/seam_prediction_calibration_audit.json decile deltas: `highest-risk decile has realized breach 0.080 higher and utility 0.251 lower than the lowest-risk decile`
- `pass` `falsification_paired_rows` from results/local_falsification_audit.json metrics.paired_hard_rows: `On 13,440 paired hard rows`
- `pass` `falsification_pair_win_rate` from results/local_falsification_audit.json metrics.utility_pair_win_rate: `utility on 0.855 of paired rows`
- `pass` `falsification_abstention_and_cost` from results/local_falsification_audit.json abstention/cost metrics: `abstention changes by only 0.00649, composition cost changes by -0.04584, and cost-normalized utility improves by 0.21810`
- `pass` `falsification_risk_correlation` from results/local_falsification_audit.json metrics.risk_breach_correlation: `risk-breach correlation 0.971`
- `pass` `falsification_task_regime_count` from results/local_falsification_audit.json metrics.task_regime_margins.groups: `Margins are positive in all 42 hard task-regime slices`
- `pass` `falsification_oracle_gap` from results/local_falsification_audit.json oracle gaps: `oracle remains above the proposed method by 0.10796 success and 0.25161 utility`
- `pass` `holdout_rows_per_method` from results/holdout_robustness_audit.json metrics.hard_rows_per_method: `Over 13,440 hard rows per method`
- `pass` `holdout_task_regime_and_hash_counts` from results/holdout_robustness_audit.json partition_stats: `42/42 task-regime holdouts, and 5/5 hash-fold holdouts`
- `pass` `holdout_worst_margins` from results/holdout_robustness_audit.json worst task-regime margins: `worst task-regime holdout still has success margin 0.02188 and utility margin 0.17256`
- `pass` `holdout_hash_fold_margin_and_seed_wins` from results/holdout_robustness_audit.json hash-fold margin and seed wins: `weakest hash fold has utility margin 0.22706 and 10/10 seed wins`
- `pass` `main_table_proposed_success` from generated table derived from result JSON/CSV: `0.802`
- `pass` `main_table_proposed_utility` from generated table derived from result JSON/CSV: `0.888`
- `pass` `main_table_strongest_success` from generated table derived from result JSON/CSV: `0.717`
- `pass` `main_table_strongest_utility` from generated table derived from result JSON/CSV: `0.653`
- `pass` `main_table_oracle_success` from generated table derived from result JSON/CSV: `0.910`
- `pass` `main_table_oracle_utility` from generated table derived from result JSON/CSV: `1.140`
- `pass` `falsification_table_abstention_delta` from generated table derived from result JSON/CSV: `+0.00649`
- `pass` `falsification_table_cost_delta` from generated table derived from result JSON/CSV: `-0.04584`
- `pass` `falsification_table_risk_correlation` from generated table derived from result JSON/CSV: `0.971`
- `pass` `diagnostic_table_total_rows` from generated table derived from result JSON/CSV: `230,400`
- `pass` `diagnostic_table_accept_breach` from generated table derived from result JSON/CSV: `0.076`
- `pass` `diagnostic_table_non_accept_breach` from generated table derived from result JSON/CSV: `0.108`
- `pass` `diagnostic_table_abstain_risk` from generated table derived from result JSON/CSV: `0.125`
- `pass` `decision_table_accept_coverage` from generated table derived from result JSON/CSV: `accept coverage 0.404 vs 0.000`
- `pass` `decision_table_non_abstain_quality` from generated table derived from result JSON/CSV: `non-abstain utility 0.935 vs 0.776`
- `pass` `decision_table_recovered_accepts` from generated table derived from result JSON/CSV: `3,850 pairs where v5 accepts and predecessor abstains`
- `pass` `planner_table_frontier_coverage` from generated table derived from result JSON/CSV: `1,680 local hard-slice planning frontiers`
- `pass` `planner_table_executable_coverage` from generated table derived from result JSON/CSV: `executable-edge coverage 0.667 vs 0.165`
- `pass` `planner_table_selected_utility` from generated table derived from result JSON/CSV: `selected-edge utility 0.889 vs 0.658`
- `pass` `planner_table_safety` from generated table derived from result JSON/CSV: `success delta +0.080`
- `pass` `failure_memory_table_signature_pairs` from generated table derived from result JSON/CSV: `2,210 observed-to-held-out signature pairs`
- `pass` `failure_memory_table_correlation` from generated table derived from result JSON/CSV: `r=0.957`
- `pass` `failure_memory_table_high_breach` from generated table derived from result JSON/CSV: `held-out breach 0.120`
- `pass` `failure_memory_table_predecessor_delta` from generated table derived from result JSON/CSV: `breach lower by 0.083`
- `pass` `calibration_table_ece` from generated table derived from result JSON/CSV: `ECE10 0.007 vs strongest baseline 0.015`
- `pass` `calibration_table_correlation` from generated table derived from result JSON/CSV: `risk-breach correlation 0.971, Spearman 0.950`
- `pass` `calibration_table_decision_relevance` from generated table derived from result JSON/CSV: `utility is lower by 0.251`
- `pass` `holdout_table_worst_task_regime_success` from generated table derived from result JSON/CSV: `+0.02188`
- `pass` `holdout_table_worst_task_regime_utility` from generated table derived from result JSON/CSV: `+0.17256`
- `pass` `holdout_table_worst_hash_fold_utility` from generated table derived from result JSON/CSV: `+0.22706`

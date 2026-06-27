from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
OUT_JSON = RESULTS / "manuscript_number_audit.json"
OUT_MD = RESULTS / "manuscript_number_audit.md"


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def fmt(value: Any, digits: int = 5) -> str:
    return f"{float(value):.{digits}f}"


def add_check(checks: list[dict[str, Any]], name: str, expected: str, text: str, source: str) -> None:
    checks.append(
        {
            "name": name,
            "passed": expected in text,
            "expected": expected,
            "source": source,
        }
    )


def main() -> int:
    summary = read_json(RESULTS / "summary.json")
    falsification = read_json(RESULTS / "local_falsification_audit.json")
    holdout = read_json(RESULTS / "holdout_robustness_audit.json")
    diagnostic = read_json(RESULTS / "diagnostic_mechanism_audit.json")
    decision_quality = read_json(RESULTS / "decision_quality_audit.json")
    calibration = read_json(RESULTS / "seam_prediction_calibration_audit.json")
    tex_path = PAPER / "main.tex"
    if not tex_path.exists():
        fail("missing paper/main.tex")
    tex = tex_path.read_text(encoding="utf-8")
    main_table = (PAPER / "generated_main_table.tex").read_text(encoding="utf-8")
    falsification_table = (PAPER / "generated_local_falsification_table.tex").read_text(encoding="utf-8")
    holdout_table = (PAPER / "generated_holdout_robustness_table.tex").read_text(encoding="utf-8")
    diagnostic_table = (PAPER / "generated_diagnostic_mechanism_table.tex").read_text(encoding="utf-8")
    decision_table = (PAPER / "generated_decision_quality_table.tex").read_text(encoding="utf-8")
    calibration_table = (PAPER / "generated_seam_prediction_calibration_table.tex").read_text(encoding="utf-8")

    metrics = summary.get("metrics", {})
    counts = summary.get("row_counts", {})
    falsification_metrics = falsification.get("metrics", {})
    task_regime = falsification_metrics.get("task_regime_margins", {})
    holdout_metrics = holdout.get("metrics", {})
    holdout_stats = holdout.get("partition_stats", {})
    diagnostic_metrics = diagnostic.get("metrics", {})
    decision_metrics = decision_quality.get("metrics", {})
    calibration_metrics = calibration.get("proposed_metrics", {})
    calibration_baseline = calibration.get("strongest_baseline_metrics", {})
    calibration_derived = calibration.get("derived", {})

    checks: list[dict[str, Any]] = []

    add_check(
        checks,
        "abstract_proposed_hard_success_and_utility",
        f"composer reaches hard-slice success {fmt(metrics['hard_success_proposed'])} and utility {fmt(metrics['hard_utility_proposed'])}",
        tex,
        "results/summary.json metrics.hard_success_proposed, hard_utility_proposed",
    )
    add_check(
        checks,
        "abstract_strongest_baseline_values",
        f"compared with {fmt(metrics['hard_success_strongest'])} and {fmt(metrics['hard_utility_strongest'])}",
        tex,
        "results/summary.json metrics.hard_success_strongest, hard_utility_strongest",
    )
    add_check(
        checks,
        "evaluation_main_matrix_count",
        f"and {int(counts['main_cell']):,} main cell rows",
        tex,
        "results/summary.json row_counts.main_cell",
    )
    add_check(
        checks,
        "evaluation_auxiliary_counts",
        f"Ablations add {int(counts['ablation_cell']):,} cells, stress sweeps add {int(counts['stress_cell']):,} cells, fixed-risk tests add {int(counts['fixed_risk_cell']):,} cells, and the failure audit contains {int(counts['failure_cases'])} cases",
        tex,
        "results/summary.json row_counts",
    )
    add_check(
        checks,
        "main_result_margins",
        f"improves hard success by {fmt(metrics['hard_success_margin'])} and hard utility by {fmt(metrics['hard_utility_margin'])}",
        tex,
        "results/summary.json metrics.hard_success_margin, hard_utility_margin",
    )
    add_check(
        checks,
        "paired_hard_utility_wins",
        f"paired hard-utility wins are {int(metrics['paired_hard_utility_wins'])}/10",
        tex,
        "results/summary.json metrics.paired_hard_utility_wins",
    )
    add_check(
        checks,
        "oracle_result_values",
        f"The oracle remains stronger with success {fmt(metrics['hard_success_oracle'])} and utility {fmt(metrics['hard_utility_oracle'])}",
        tex,
        "results/summary.json metrics.hard_success_oracle, hard_utility_oracle",
    )
    add_check(
        checks,
        "diagnostic_delta_sentence",
        (
            f"reduces seam failure by {fmt(metrics['seam_failure_delta'])}, barrier violation by {fmt(metrics['barrier_violation_delta'])}, "
            f"damage by {fmt(metrics['damage_rate_delta'])}, composition cost by {fmt(metrics['composition_cost_delta'])}, "
            f"risk calibration error by {fmt(metrics['risk_calibration_error_delta'])}, and realized seam breach by {fmt(metrics['realized_seam_breach_delta'])}"
        ),
        tex,
        "results/summary.json diagnostic deltas",
    )
    add_check(
        checks,
        "basin_and_descent_deltas",
        f"improves basin alignment by {fmt(metrics['basin_alignment_delta'])} and descent continuity by {fmt(metrics['descent_continuity_delta'])}",
        tex,
        "results/summary.json metrics.basin_alignment_delta, descent_continuity_delta",
    )
    add_check(
        checks,
        "ablation_margin_sentence",
        f"by {fmt(metrics['ablation_success_margin'])} success and {fmt(metrics['ablation_utility_margin'])} utility",
        tex,
        "results/summary.json metrics.ablation_success_margin, ablation_utility_margin",
    )
    add_check(
        checks,
        "diagnostic_zero_mismatch_sentence",
        (
            f"Over {int(counts['main_cell']):,} local rows, the diagnostic audit finds "
            f"{int(diagnostic_metrics['label_mismatches'])} label-rule mismatches, "
            f"{int(diagnostic_metrics['decision_mismatches'])} decision-rule mismatches, and "
            f"{int(diagnostic_metrics['update_mismatches'])} planner-update mismatches"
        ),
        tex,
        "results/diagnostic_mechanism_audit.json mismatch counts",
    )
    add_check(
        checks,
        "diagnostic_hard_rows_sentence",
        f"In the {int(diagnostic_metrics['proposed_hard_rows']):,} proposed hard rows, all five failure labels and all five decisions appear",
        tex,
        "results/diagnostic_mechanism_audit.json proposed_hard_rows",
    )
    add_check(
        checks,
        "diagnostic_accept_abstain_sentence",
        (
            f"Accepted seams have mean realized breach {fmt(diagnostic_metrics['accept_mean_realized_breach'], 3)} "
            f"versus {fmt(diagnostic_metrics['non_accept_mean_realized_breach'], 3)} for non-accepted seams, "
            f"while abstained seams have mean predicted risk {fmt(diagnostic_metrics['abstain_mean_predicted_risk'], 3)} "
            f"versus {fmt(diagnostic_metrics['accept_mean_predicted_risk'], 3)} for accepted seams"
        ),
        tex,
        "results/diagnostic_mechanism_audit.json accept/abstain metrics",
    )
    add_check(
        checks,
        "diagnostic_reason_purity_sentence",
        (
            f"Repair, probe, and transition decisions match their intended diagnostic reasons with purity "
            f"{fmt(diagnostic_metrics['repair_reason_rate'], 3)}, "
            f"{fmt(diagnostic_metrics['probe_reason_rate'], 3)}, and "
            f"{fmt(diagnostic_metrics['transition_reason_rate'], 3)}"
        ),
        tex,
        "results/diagnostic_mechanism_audit.json reason purity",
    )
    add_check(
        checks,
        "decision_quality_paired_rows_and_accept_coverage",
        (
            f"On the same {int(decision_metrics['paired_hard_rows']):,} paired hard rows, the proposed model accepts "
            f"{fmt(decision_metrics['proposed_accept_coverage'], 3)} of hard seams versus "
            f"{fmt(decision_metrics['baseline_accept_coverage'], 3)} for the predecessor, while the rate of accepted seams "
            f"above the 0.15 breach budget is {fmt(decision_metrics['proposed_accept_breach_rate'], 3)}"
        ),
        tex,
        "results/decision_quality_audit.json paired rows and accept coverage",
    )
    add_check(
        checks,
        "decision_quality_non_abstain_sentence",
        (
            f"Among non-abstained seams, utility is {fmt(decision_metrics['proposed_non_abstain_utility'], 3)} "
            f"versus {fmt(decision_metrics['baseline_non_abstain_utility'], 3)} and realized breach is "
            f"{fmt(decision_metrics['proposed_non_abstain_breach'], 3)} versus "
            f"{fmt(decision_metrics['baseline_non_abstain_breach'], 3)}"
        ),
        tex,
        "results/decision_quality_audit.json non-abstain utility and breach",
    )
    add_check(
        checks,
        "decision_quality_recovered_accepts_sentence",
        (
            f"{int(decision_metrics['recovered_accept_pairs']):,} paired seams are accepted by v5 and abstained from by the predecessor; "
            f"those recovered accepts improve utility by {fmt(decision_metrics['recovered_accept_utility_delta'], 3)}, "
            f"success by {fmt(decision_metrics['recovered_accept_success_delta'], 3)}, and realized breach by "
            f"{fmt(decision_metrics['recovered_accept_breach_delta'], 3)}"
        ),
        tex,
        "results/decision_quality_audit.json recovered accept deltas",
    )
    add_check(
        checks,
        "calibration_ece_sentence",
        (
            f"ten-bin local calibration error between predicted seam risk and realized seam breach is "
            f"{fmt(calibration_metrics['expected_calibration_error_10'], 3)}, compared with "
            f"{fmt(calibration_baseline['expected_calibration_error_10'], 3)} for the strongest predecessor; "
            f"the maximum bin gap is {fmt(calibration_metrics['max_calibration_error_10'], 3)}"
        ),
        tex,
        "results/seam_prediction_calibration_audit.json ECE and max gap",
    )
    add_check(
        checks,
        "calibration_mean_correlation_sentence",
        (
            f"Mean predicted risk is {fmt(calibration_metrics['mean_predicted_seam_risk'], 3)} versus realized breach "
            f"{fmt(calibration_metrics['mean_realized_seam_breach'], 3)}, with risk-breach correlation "
            f"{fmt(calibration_metrics['risk_breach_correlation'], 3)} and Spearman "
            f"{fmt(calibration_metrics['risk_breach_spearman'], 3)}"
        ),
        tex,
        "results/seam_prediction_calibration_audit.json mean and correlation metrics",
    )
    add_check(
        checks,
        "calibration_decile_sentence",
        (
            f"highest-risk decile has realized breach {fmt(calibration_derived['highest_lowest_decile_breach_delta'], 3)} higher "
            f"and utility {fmt(-calibration_derived['highest_lowest_decile_utility_delta'], 3)} lower than the lowest-risk decile"
        ),
        tex,
        "results/seam_prediction_calibration_audit.json decile deltas",
    )
    add_check(
        checks,
        "falsification_paired_rows",
        f"On {int(falsification_metrics['paired_hard_rows']):,} paired hard rows",
        tex,
        "results/local_falsification_audit.json metrics.paired_hard_rows",
    )
    add_check(
        checks,
        "falsification_pair_win_rate",
        f"utility on {fmt(falsification_metrics['utility_pair_win_rate'], 3)} of paired rows",
        tex,
        "results/local_falsification_audit.json metrics.utility_pair_win_rate",
    )
    add_check(
        checks,
        "falsification_abstention_and_cost",
        (
            f"abstention changes by only {fmt(falsification_metrics['abstention_delta'])}, "
            f"composition cost changes by {fmt(falsification_metrics['composition_cost_delta'])}, "
            f"and cost-normalized utility improves by {fmt(falsification_metrics['cost_normalized_utility_margin'])}"
        ),
        tex,
        "results/local_falsification_audit.json abstention/cost metrics",
    )
    add_check(
        checks,
        "falsification_risk_correlation",
        f"risk-breach correlation {fmt(falsification_metrics['risk_breach_correlation'], 3)}",
        tex,
        "results/local_falsification_audit.json metrics.risk_breach_correlation",
    )
    add_check(
        checks,
        "falsification_task_regime_count",
        f"Margins are positive in all {int(task_regime['groups'])} hard task-regime slices",
        tex,
        "results/local_falsification_audit.json metrics.task_regime_margins.groups",
    )
    add_check(
        checks,
        "falsification_oracle_gap",
        f"oracle remains above the proposed method by {fmt(falsification_metrics['oracle_success_gap'])} success and {fmt(falsification_metrics['oracle_utility_gap'])} utility",
        tex,
        "results/local_falsification_audit.json oracle gaps",
    )
    add_check(
        checks,
        "holdout_rows_per_method",
        f"Over {int(holdout_metrics['hard_rows_per_method']):,} hard rows per method",
        tex,
        "results/holdout_robustness_audit.json metrics.hard_rows_per_method",
    )
    add_check(
        checks,
        "holdout_task_regime_and_hash_counts",
        (
            f"{int(holdout_stats['task_regime']['positive_utility_groups'])}/{int(holdout_stats['task_regime']['groups'])} task-regime holdouts, and "
            f"{int(holdout_stats['hash_fold']['positive_utility_groups'])}/{int(holdout_stats['hash_fold']['groups'])} hash-fold holdouts"
        ),
        tex,
        "results/holdout_robustness_audit.json partition_stats",
    )
    add_check(
        checks,
        "holdout_worst_margins",
        (
            f"worst task-regime holdout still has success margin {fmt(holdout_metrics['worst_task_regime_success_delta'])} "
            f"and utility margin {fmt(holdout_metrics['worst_task_regime_utility_delta'])}"
        ),
        tex,
        "results/holdout_robustness_audit.json worst task-regime margins",
    )
    add_check(
        checks,
        "holdout_hash_fold_margin_and_seed_wins",
        (
            f"weakest hash fold has utility margin {fmt(holdout_metrics['worst_hash_fold_utility_delta'])} "
            f"and {int(holdout_metrics['worst_hash_fold_seed_wins'])}/10 seed wins"
        ),
        tex,
        "results/holdout_robustness_audit.json hash-fold margin and seed wins",
    )

    expected_main_table_values = [
        ("main_table_proposed_success", fmt(metrics["hard_success_proposed"], 3), main_table),
        ("main_table_proposed_utility", fmt(metrics["hard_utility_proposed"], 3), main_table),
        ("main_table_strongest_success", fmt(metrics["hard_success_strongest"], 3), main_table),
        ("main_table_strongest_utility", fmt(metrics["hard_utility_strongest"], 3), main_table),
        ("main_table_oracle_success", fmt(metrics["hard_success_oracle"], 3), main_table),
        ("main_table_oracle_utility", fmt(metrics["hard_utility_oracle"], 3), main_table),
        ("falsification_table_abstention_delta", f"{float(falsification_metrics['abstention_delta']):+.5f}", falsification_table),
        ("falsification_table_cost_delta", f"{float(falsification_metrics['composition_cost_delta']):+.5f}", falsification_table),
        ("falsification_table_risk_correlation", fmt(falsification_metrics["risk_breach_correlation"], 3), falsification_table),
        ("diagnostic_table_total_rows", f"{int(counts['main_cell']):,}", diagnostic_table),
        ("diagnostic_table_accept_breach", fmt(diagnostic_metrics["accept_mean_realized_breach"], 3), diagnostic_table),
        ("diagnostic_table_non_accept_breach", fmt(diagnostic_metrics["non_accept_mean_realized_breach"], 3), diagnostic_table),
        ("diagnostic_table_abstain_risk", fmt(diagnostic_metrics["abstain_mean_predicted_risk"], 3), diagnostic_table),
        ("decision_table_accept_coverage", f"accept coverage {fmt(decision_metrics['proposed_accept_coverage'], 3)} vs {fmt(decision_metrics['baseline_accept_coverage'], 3)}", decision_table),
        ("decision_table_non_abstain_quality", f"non-abstain utility {fmt(decision_metrics['proposed_non_abstain_utility'], 3)} vs {fmt(decision_metrics['baseline_non_abstain_utility'], 3)}", decision_table),
        ("decision_table_recovered_accepts", f"{int(decision_metrics['recovered_accept_pairs']):,} pairs where v5 accepts and predecessor abstains", decision_table),
        ("calibration_table_ece", f"ECE10 {fmt(calibration_metrics['expected_calibration_error_10'], 3)} vs strongest baseline {fmt(calibration_baseline['expected_calibration_error_10'], 3)}", calibration_table),
        ("calibration_table_correlation", f"risk-breach correlation {fmt(calibration_metrics['risk_breach_correlation'], 3)}, Spearman {fmt(calibration_metrics['risk_breach_spearman'], 3)}", calibration_table),
        ("calibration_table_decision_relevance", f"utility is lower by {fmt(-calibration_derived['highest_lowest_decile_utility_delta'], 3)}", calibration_table),
        ("holdout_table_worst_task_regime_success", f"{float(holdout_metrics['worst_task_regime_success_delta']):+.5f}", holdout_table),
        ("holdout_table_worst_task_regime_utility", f"{float(holdout_metrics['worst_task_regime_utility_delta']):+.5f}", holdout_table),
        ("holdout_table_worst_hash_fold_utility", f"{float(holdout_metrics['worst_hash_fold_utility_delta']):+.5f}", holdout_table),
    ]
    for name, expected, text in expected_main_table_values:
        add_check(checks, name, expected, text, "generated table derived from result JSON/CSV")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "manuscript_number_audit_v1",
        "passed": passed,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "sources": [
            "results/summary.json",
            "results/local_falsification_audit.json",
            "results/holdout_robustness_audit.json",
            "results/diagnostic_mechanism_audit.json",
            "results/decision_quality_audit.json",
            "results/seam_prediction_calibration_audit.json",
            "paper/main.tex",
            "paper/generated_main_table.tex",
            "paper/generated_local_falsification_table.tex",
            "paper/generated_holdout_robustness_table.tex",
            "paper/generated_diagnostic_mechanism_table.tex",
            "paper/generated_decision_quality_table.tex",
            "paper/generated_seam_prediction_calibration_table.tex",
        ],
    }
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Manuscript Number Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "",
        "This audit checks that manuscript and table numbers are traceable to generated result files.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}` from {check['source']}: `{check['expected']}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Manuscript number audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

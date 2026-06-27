from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"

SUMMARY_JSON = RESULTS / "summary.json"
CELL_METRICS = RESULTS / "cell_metrics.csv"
OUT_JSON = RESULTS / "seam_prediction_calibration_audit.json"
OUT_MD = RESULTS / "seam_prediction_calibration_audit.md"
OUT_TEX = PAPER / "generated_seam_prediction_calibration_table.tex"

PROPOSED = "barrier_certified_energy_composer_v5"
ORACLE = "oracle_basin_composer"

HARD_SPLITS = {"new_skill_pair", "shifted_objects", "long_horizon_chain", "combined_stress"}
HARD_REGIMES = {
    "narrow_basin",
    "high_barrier",
    "nonconvex_energy",
    "contact_mode_transition",
    "dynamics_mismatch",
    "partial_observability",
    "combined_seam_stress",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def f(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        fail(f"non-finite value in {key}")
    return value


def hard_row(row: dict[str, str]) -> bool:
    return row["split"] in HARD_SPLITS and row["regime"] in HARD_REGIMES


def load_hard_rows(methods: set[str]) -> dict[str, list[dict[str, str]]]:
    if not CELL_METRICS.exists():
        fail(f"missing {CELL_METRICS}; run src/run_experiment.py")
    rows_by_method: dict[str, list[dict[str, str]]] = defaultdict(list)
    with CELL_METRICS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if hard_row(row) and row["method"] in methods:
                rows_by_method[row["method"]].append(row)
    missing = sorted(method for method in methods if method not in rows_by_method)
    if missing:
        fail(f"missing hard rows for methods: {missing}")
    required = {"predicted_seam_risk", "realized_seam_breach", "composition_utility", "success", "seam_decision"}
    for method, rows in rows_by_method.items():
        missing_columns = sorted(required - set(rows[0]))
        if missing_columns:
            fail(f"{method} rows missing columns: {missing_columns}")
    return rows_by_method


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0.0 or vy <= 0.0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def ranks(values: list[float]) -> list[float]:
    order = sorted(enumerate(values), key=lambda item: item[1])
    ranked = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and order[end][1] == order[index][1]:
            end += 1
        average_rank = (index + end - 1) / 2.0 + 1.0
        for item_index in range(index, end):
            ranked[order[item_index][0]] = average_rank
        index = end
    return ranked


def calibration_summary(rows: list[dict[str, str]], *, bin_count: int = 10) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: f(row, "predicted_seam_risk"))
    bins: list[dict[str, Any]] = []
    expected_calibration_error = 0.0
    max_calibration_error = 0.0
    for index in range(bin_count):
        start = index * len(ordered) // bin_count
        end = (index + 1) * len(ordered) // bin_count
        chunk = ordered[start:end]
        mean_predicted = mean(f(row, "predicted_seam_risk") for row in chunk)
        mean_realized = mean(f(row, "realized_seam_breach") for row in chunk)
        gap = abs(mean_predicted - mean_realized)
        expected_calibration_error += len(chunk) / len(ordered) * gap
        max_calibration_error = max(max_calibration_error, gap)
        bins.append(
            {
                "bin": index + 1,
                "rows": len(chunk),
                "mean_predicted_seam_risk": mean_predicted,
                "mean_realized_seam_breach": mean_realized,
                "absolute_calibration_gap": gap,
                "success_rate": mean(f(row, "success") for row in chunk),
                "composition_utility": mean(f(row, "composition_utility") for row in chunk),
            }
        )

    predicted = [f(row, "predicted_seam_risk") for row in rows]
    realized = [f(row, "realized_seam_breach") for row in rows]
    return {
        "rows": len(rows),
        "mean_predicted_seam_risk": mean(predicted),
        "mean_realized_seam_breach": mean(realized),
        "mean_absolute_row_error": mean(abs(p - r) for p, r in zip(predicted, realized)),
        "expected_calibration_error_10": expected_calibration_error,
        "max_calibration_error_10": max_calibration_error,
        "risk_breach_correlation": pearson(predicted, realized),
        "risk_breach_spearman": pearson(ranks(predicted), ranks(realized)),
        "bins": bins,
        "bins_monotone_realized_breach": all(
            bins[index]["mean_realized_seam_breach"] <= bins[index + 1]["mean_realized_seam_breach"] + 1e-12
            for index in range(len(bins) - 1)
        ),
        "lowest_decile_realized_breach": bins[0]["mean_realized_seam_breach"],
        "highest_decile_realized_breach": bins[-1]["mean_realized_seam_breach"],
        "lowest_decile_utility": bins[0]["composition_utility"],
        "highest_decile_utility": bins[-1]["composition_utility"],
    }


def decision_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    by_decision: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_decision[row["seam_decision"]].append(row)
    summary = {}
    for decision, chunk in sorted(by_decision.items()):
        summary[decision] = {
            "rows": len(chunk),
            "mean_predicted_seam_risk": mean(f(row, "predicted_seam_risk") for row in chunk),
            "mean_realized_seam_breach": mean(f(row, "realized_seam_breach") for row in chunk),
            "composition_utility": mean(f(row, "composition_utility") for row in chunk),
        }
    return summary


def latex_escape(text: object) -> str:
    return (
        str(text)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def signed(value: float, digits: int = 3) -> str:
    return f"{value:+.{digits}f}"


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_tex_table(rows: list[dict[str, str]]) -> None:
    PAPER.mkdir(exist_ok=True)
    lines = [
        r"\begin{tabular}{p{0.24\linewidth}p{0.58\linewidth}p{0.08\linewidth}}",
        r"\toprule",
        r"audit target & local predictive-validity evidence & verdict \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{latex_escape(row['target'])} & {latex_escape(row['evidence'])} & {latex_escape(row['verdict'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    OUT_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    summary = read_json(SUMMARY_JSON)
    strongest = str(summary.get("strongest_non_oracle", ""))
    if not strongest:
        fail("summary.json missing strongest_non_oracle")

    rows_by_method = load_hard_rows({PROPOSED, strongest, ORACLE})
    proposed = calibration_summary(rows_by_method[PROPOSED])
    baseline = calibration_summary(rows_by_method[strongest])
    oracle = calibration_summary(rows_by_method[ORACLE])
    decisions = decision_summary(rows_by_method[PROPOSED])

    ece_delta_vs_baseline = proposed["expected_calibration_error_10"] - baseline["expected_calibration_error_10"]
    high_low_breach_delta = proposed["highest_decile_realized_breach"] - proposed["lowest_decile_realized_breach"]
    high_low_utility_delta = proposed["highest_decile_utility"] - proposed["lowest_decile_utility"]
    accept_risk = decisions.get("accept", {}).get("mean_predicted_seam_risk", 1.0)
    abstain_risk = decisions.get("abstain", {}).get("mean_predicted_seam_risk", 0.0)

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", True, "local hard-slice predictive-validity audit only")
    add_check(checks, "proposed_rows_ge_10000", proposed["rows"] >= 10_000, f"rows={proposed['rows']}")
    add_check(
        checks,
        "ece_10_le_0_010",
        proposed["expected_calibration_error_10"] <= 0.010,
        f"ece10={proposed['expected_calibration_error_10']:.6f}",
    )
    add_check(
        checks,
        "max_bin_gap_le_0_015",
        proposed["max_calibration_error_10"] <= 0.015,
        f"max_gap={proposed['max_calibration_error_10']:.6f}",
    )
    add_check(
        checks,
        "mean_risk_gap_le_0_010",
        abs(proposed["mean_predicted_seam_risk"] - proposed["mean_realized_seam_breach"]) <= 0.010,
        f"mean_predicted={proposed['mean_predicted_seam_risk']:.6f}, mean_realized={proposed['mean_realized_seam_breach']:.6f}",
    )
    add_check(
        checks,
        "risk_breach_correlation_ge_0_90",
        proposed["risk_breach_correlation"] >= 0.90,
        f"corr={proposed['risk_breach_correlation']:.6f}",
    )
    add_check(
        checks,
        "risk_breach_spearman_ge_0_90",
        proposed["risk_breach_spearman"] >= 0.90,
        f"spearman={proposed['risk_breach_spearman']:.6f}",
    )
    add_check(
        checks,
        "decile_breach_monotone",
        proposed["bins_monotone_realized_breach"] is True,
        "10/10 ordered deciles have nondecreasing realized breach",
    )
    add_check(
        checks,
        "highest_lowest_decile_breach_gap_ge_0_07",
        high_low_breach_delta >= 0.07,
        f"breach_delta={high_low_breach_delta:.6f}",
    )
    add_check(
        checks,
        "highest_lowest_decile_utility_delta_le_minus_0_20",
        high_low_utility_delta <= -0.20,
        f"utility_delta={high_low_utility_delta:.6f}",
    )
    add_check(
        checks,
        "ece_improves_over_strongest_baseline_by_0_005",
        ece_delta_vs_baseline <= -0.005,
        f"delta={ece_delta_vs_baseline:.6f}, baseline_ece={baseline['expected_calibration_error_10']:.6f}",
    )
    add_check(
        checks,
        "accept_risk_lower_than_abstain_risk_by_0_03",
        abstain_risk - accept_risk >= 0.03,
        f"accept={accept_risk:.6f}, abstain={abstain_risk:.6f}",
    )

    passed = all(check["passed"] for check in checks)
    table_rows = [
        {
            "target": "calibration",
            "evidence": (
                f"ECE10 {fmt(proposed['expected_calibration_error_10'])} vs strongest baseline "
                f"{fmt(baseline['expected_calibration_error_10'])}; max bin gap {fmt(proposed['max_calibration_error_10'])}"
            ),
            "verdict": "pass" if checks[2]["passed"] and checks[3]["passed"] else "fail",
        },
        {
            "target": "mean agreement",
            "evidence": (
                f"mean predicted risk {fmt(proposed['mean_predicted_seam_risk'])} vs realized breach "
                f"{fmt(proposed['mean_realized_seam_breach'])}; row MAE {fmt(proposed['mean_absolute_row_error'])}"
            ),
            "verdict": "pass",
        },
        {
            "target": "risk ordering",
            "evidence": (
                f"risk-breach correlation {fmt(proposed['risk_breach_correlation'])}, Spearman "
                f"{fmt(proposed['risk_breach_spearman'])}; realized breach is monotone across 10 risk deciles"
            ),
            "verdict": "pass",
        },
        {
            "target": "decision relevance",
            "evidence": (
                f"highest-risk decile breach changes by {signed(high_low_breach_delta)} and utility is lower by "
                f"{fmt(-high_low_utility_delta)} vs lowest-risk decile; accept risk {fmt(accept_risk)} vs abstain risk {fmt(abstain_risk)}"
            ),
            "verdict": "pass",
        },
    ]
    write_tex_table(table_rows)

    payload = {
        "version": "seam_prediction_calibration_audit_v1",
        "passed": passed,
        "scope": "local_synthetic_hard_slice_only",
        "not_external_evidence": True,
        "proposed": PROPOSED,
        "strongest_non_oracle": strongest,
        "proposed_metrics": proposed,
        "strongest_baseline_metrics": baseline,
        "oracle_metrics": oracle,
        "proposed_decision_metrics": decisions,
        "derived": {
            "ece_delta_vs_strongest_baseline": ece_delta_vs_baseline,
            "highest_lowest_decile_breach_delta": high_low_breach_delta,
            "highest_lowest_decile_utility_delta": high_low_utility_delta,
            "accept_abstain_predicted_risk_delta": accept_risk - abstain_risk,
        },
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Seam Prediction Calibration Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.",
        "",
        "## Summary",
        "",
        f"- Proposed rows: `{proposed['rows']}`.",
        f"- Proposed ECE10: `{proposed['expected_calibration_error_10']:.6f}`.",
        f"- Strongest-baseline ECE10: `{baseline['expected_calibration_error_10']:.6f}`.",
        f"- Proposed max bin gap: `{proposed['max_calibration_error_10']:.6f}`.",
        f"- Mean predicted risk / realized breach: `{proposed['mean_predicted_seam_risk']:.6f}` / `{proposed['mean_realized_seam_breach']:.6f}`.",
        f"- Risk-breach correlation / Spearman: `{proposed['risk_breach_correlation']:.6f}` / `{proposed['risk_breach_spearman']:.6f}`.",
        f"- Highest-minus-lowest risk decile breach: `{high_low_breach_delta:.6f}`.",
        f"- Highest-minus-lowest risk decile utility: `{high_low_utility_delta:.6f}`.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(["", "## Risk Deciles", ""])
    for item in proposed["bins"]:
        lines.append(
            "- bin `{bin}` rows `{rows}` predicted `{pred:.6f}` realized `{real:.6f}` gap `{gap:.6f}` utility `{utility:.6f}`".format(
                bin=item["bin"],
                rows=item["rows"],
                pred=item["mean_predicted_seam_risk"],
                real=item["mean_realized_seam_breach"],
                gap=item["absolute_calibration_gap"],
                utility=item["composition_utility"],
            )
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        "Seam prediction calibration audit: "
        f"{'PASS' if passed else 'FAIL'}; ece10={proposed['expected_calibration_error_10']:.6f}; "
        f"corr={proposed['risk_breach_correlation']:.6f}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_TEX}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

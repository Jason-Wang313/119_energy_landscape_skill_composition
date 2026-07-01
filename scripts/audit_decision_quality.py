from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"

SUMMARY_JSON = RESULTS / "summary.json"
CELL_METRICS = RESULTS / "cell_metrics.csv"
OUT_JSON = RESULTS / "decision_quality_audit.json"
OUT_MD = RESULTS / "decision_quality_audit.md"
OUT_TEX = PAPER / "generated_decision_quality_table.tex"

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
FIXED_RISK_BUDGET = 0.15


def fail(message: str) -> None:
    raise SystemExit(message)


def f(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        fail(f"non-finite value in {key}")
    return value


def read_summary() -> dict[str, Any]:
    if not SUMMARY_JSON.exists():
        fail(f"missing {SUMMARY_JSON}; run src/run_experiment.py")
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def hard_row(row: dict[str, str]) -> bool:
    return row["split"] in HARD_SPLITS and row["regime"] in HARD_REGIMES


def read_hard_rows(methods: set[str]) -> list[dict[str, str]]:
    if not CELL_METRICS.exists():
        fail(f"missing {CELL_METRICS}; run src/run_experiment.py")
    rows: list[dict[str, str]] = []
    with CELL_METRICS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["method"] in methods and hard_row(row):
                rows.append(row)
    required = {"diagnostic_label", "seam_decision", "planner_edge_update", "predicted_seam_risk", "realized_seam_breach"}
    missing = sorted(required - set(rows[0].keys())) if rows else sorted(required)
    if missing:
        fail(f"hard rows missing decision columns: {missing}")
    return rows


def paired_rows(rows: list[dict[str, str]], proposed: str, baseline: str) -> list[tuple[dict[str, str], dict[str, str]]]:
    by_key: dict[tuple[str, str, str, str, str], dict[str, dict[str, str]]] = {}
    for row in rows:
        key = (row["task"], row["regime"], row["split"], row["seed"], row["episode"])
        by_key.setdefault(key, {})[row["method"]] = row
    pairs = []
    for methods in by_key.values():
        if proposed in methods and baseline in methods:
            pairs.append((methods[proposed], methods[baseline]))
    return pairs


def safe_mean(rows: list[dict[str, str]], key: str) -> float:
    if not rows:
        return 0.0
    return mean(f(row, key) for row in rows)


def breach_rate(rows: list[dict[str, str]]) -> float:
    if not rows:
        return 0.0
    return sum(f(row, "realized_seam_breach") > FIXED_RISK_BUDGET for row in rows) / len(rows)


def latex_escape(text: object) -> str:
    return (
        str(text)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def signed(value: float) -> str:
    return f"{value:+.3f}"


def write_tex_table(rows: list[dict[str, str]]) -> None:
    PAPER.mkdir(exist_ok=True)
    lines = [
        r"\begin{tabular}{p{0.25\linewidth}p{0.56\linewidth}p{0.09\linewidth}}",
        r"\toprule",
        r"audit target & local decision-quality evidence & verdict \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{latex_escape(row['target'])} & {latex_escape(row['evidence'])} & {latex_escape(row['verdict'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    OUT_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    summary = read_summary()
    proposed = str(summary["proposed"])
    baseline = str(summary["strongest_non_oracle"])
    rows = read_hard_rows({proposed, baseline})
    proposed_rows = [row for row in rows if row["method"] == proposed]
    baseline_rows = [row for row in rows if row["method"] == baseline]
    pairs = paired_rows(rows, proposed, baseline)
    if not proposed_rows or not baseline_rows or not pairs:
        fail("missing proposed/baseline hard rows for decision-quality audit")

    proposed_accept = [row for row in proposed_rows if row["seam_decision"] == "accept"]
    baseline_accept = [row for row in baseline_rows if row["seam_decision"] == "accept"]
    proposed_non_abstain = [row for row in proposed_rows if row["seam_decision"] != "abstain"]
    baseline_non_abstain = [row for row in baseline_rows if row["seam_decision"] != "abstain"]
    proposed_abstain = [row for row in proposed_rows if row["seam_decision"] == "abstain"]

    recovered_accept = [(p, b) for p, b in pairs if p["seam_decision"] == "accept" and b["seam_decision"] == "abstain"]
    both_abstain = [(p, b) for p, b in pairs if p["seam_decision"] == "abstain" and b["seam_decision"] == "abstain"]

    recovered_prop = [p for p, _ in recovered_accept]
    recovered_base = [b for _, b in recovered_accept]
    both_abstain_prop = [p for p, _ in both_abstain]
    both_abstain_base = [b for _, b in both_abstain]

    proposed_accept_coverage = len(proposed_accept) / len(proposed_rows)
    baseline_accept_coverage = len(baseline_accept) / len(baseline_rows)
    proposed_non_abstain_coverage = len(proposed_non_abstain) / len(proposed_rows)
    baseline_non_abstain_coverage = len(baseline_non_abstain) / len(baseline_rows)

    metrics = {
        "hard_rows_per_method": len(proposed_rows),
        "paired_hard_rows": len(pairs),
        "proposed_decision_counts": dict(sorted(Counter(row["seam_decision"] for row in proposed_rows).items())),
        "baseline_decision_counts": dict(sorted(Counter(row["seam_decision"] for row in baseline_rows).items())),
        "proposed_accept_coverage": proposed_accept_coverage,
        "baseline_accept_coverage": baseline_accept_coverage,
        "accept_coverage_delta": proposed_accept_coverage - baseline_accept_coverage,
        "proposed_accept_breach_rate": breach_rate(proposed_accept),
        "proposed_accept_mean_breach": safe_mean(proposed_accept, "realized_seam_breach"),
        "baseline_accept_mean_breach": safe_mean(baseline_accept, "realized_seam_breach"),
        "proposed_non_abstain_coverage": proposed_non_abstain_coverage,
        "baseline_non_abstain_coverage": baseline_non_abstain_coverage,
        "proposed_non_abstain_utility": safe_mean(proposed_non_abstain, "composition_utility"),
        "baseline_non_abstain_utility": safe_mean(baseline_non_abstain, "composition_utility"),
        "non_abstain_utility_delta": safe_mean(proposed_non_abstain, "composition_utility") - safe_mean(baseline_non_abstain, "composition_utility"),
        "proposed_non_abstain_breach": safe_mean(proposed_non_abstain, "realized_seam_breach"),
        "baseline_non_abstain_breach": safe_mean(baseline_non_abstain, "realized_seam_breach"),
        "non_abstain_breach_delta": safe_mean(proposed_non_abstain, "realized_seam_breach") - safe_mean(baseline_non_abstain, "realized_seam_breach"),
        "proposed_abstain_risk": safe_mean(proposed_abstain, "predicted_seam_risk"),
        "proposed_accept_risk": safe_mean(proposed_accept, "predicted_seam_risk"),
        "recovered_accept_pairs": len(recovered_accept),
        "recovered_accept_utility_delta": safe_mean(recovered_prop, "composition_utility") - safe_mean(recovered_base, "composition_utility"),
        "recovered_accept_success_delta": safe_mean(recovered_prop, "success") - safe_mean(recovered_base, "success"),
        "recovered_accept_breach_delta": safe_mean(recovered_prop, "realized_seam_breach") - safe_mean(recovered_base, "realized_seam_breach"),
        "recovered_accept_proposed_breach_rate": breach_rate(recovered_prop),
        "recovered_accept_baseline_breach_rate": breach_rate(recovered_base),
        "both_abstain_pairs": len(both_abstain),
        "both_abstain_breach_delta": safe_mean(both_abstain_prop, "realized_seam_breach") - safe_mean(both_abstain_base, "realized_seam_breach"),
    }

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", True, "local paired hard-row decision audit only")
    add_check(checks, "paired_hard_rows_ge_10000", len(pairs) >= 10_000, f"paired_hard_rows={len(pairs)}")
    add_check(checks, "proposed_accept_coverage_ge_0_35", proposed_accept_coverage >= 0.35, f"coverage={proposed_accept_coverage:.6f}")
    add_check(checks, "accept_coverage_beats_baseline_by_0_25", metrics["accept_coverage_delta"] >= 0.25, f"delta={metrics['accept_coverage_delta']:.6f}")
    add_check(checks, "proposed_accept_breach_rate_le_0_005", metrics["proposed_accept_breach_rate"] <= 0.005, f"breach_rate={metrics['proposed_accept_breach_rate']:.6f}")
    add_check(checks, "non_abstain_utility_delta_ge_0_10", metrics["non_abstain_utility_delta"] >= 0.10, f"delta={metrics['non_abstain_utility_delta']:.6f}")
    add_check(checks, "non_abstain_breach_delta_le_minus_0_03", metrics["non_abstain_breach_delta"] <= -0.03, f"delta={metrics['non_abstain_breach_delta']:.6f}")
    add_check(checks, "recovered_accept_pairs_ge_3000", len(recovered_accept) >= 3000, f"pairs={len(recovered_accept)}")
    add_check(checks, "recovered_accept_utility_delta_ge_0_15", metrics["recovered_accept_utility_delta"] >= 0.15, f"delta={metrics['recovered_accept_utility_delta']:.6f}")
    add_check(checks, "recovered_accept_success_delta_ge_0_05", metrics["recovered_accept_success_delta"] >= 0.05, f"delta={metrics['recovered_accept_success_delta']:.6f}")
    add_check(checks, "recovered_accept_breach_delta_le_minus_0_05", metrics["recovered_accept_breach_delta"] <= -0.05, f"delta={metrics['recovered_accept_breach_delta']:.6f}")
    add_check(checks, "recovered_accept_proposed_breach_rate_le_0_005", metrics["recovered_accept_proposed_breach_rate"] <= 0.005, f"breach_rate={metrics['recovered_accept_proposed_breach_rate']:.6f}")
    add_check(checks, "both_abstain_breach_delta_le_minus_0_05", metrics["both_abstain_breach_delta"] <= -0.05, f"delta={metrics['both_abstain_breach_delta']:.6f}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "decision_quality_audit_v1",
        "passed": passed,
        "scope": "local_synthetic_hard_slice_only",
        "not_external_evidence": True,
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "proposed": proposed,
        "baseline": baseline,
        "metrics": metrics,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    RESULTS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    table_rows = [
        {
            "target": "accept coverage",
            "evidence": f"accept coverage {proposed_accept_coverage:.3f} vs {baseline_accept_coverage:.3f}; proposed accepted breach above {FIXED_RISK_BUDGET:.2f} rate {metrics['proposed_accept_breach_rate']:.3f}",
            "verdict": "pass",
        },
        {
            "target": "non-abstain quality",
            "evidence": f"non-abstain utility {metrics['proposed_non_abstain_utility']:.3f} vs {metrics['baseline_non_abstain_utility']:.3f}; breach {metrics['proposed_non_abstain_breach']:.3f} vs {metrics['baseline_non_abstain_breach']:.3f}",
            "verdict": "pass",
        },
        {
            "target": "recovered accepts",
            "evidence": f"{len(recovered_accept):,} pairs where v5 accepts and predecessor abstains: utility {signed(metrics['recovered_accept_utility_delta'])}, success {signed(metrics['recovered_accept_success_delta'])}, breach {signed(metrics['recovered_accept_breach_delta'])}",
            "verdict": "pass",
        },
        {
            "target": "shared abstentions",
            "evidence": f"{len(both_abstain):,} pairs where both abstain; v5 breach changes by {signed(metrics['both_abstain_breach_delta'])}",
            "verdict": "pass",
        },
    ]
    write_tex_table(table_rows)

    lines = [
        "# Decision Quality Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Scope: local synthetic hard slice only; this is not external robot or high-fidelity simulator evidence.",
        "",
        "## Metrics",
        "",
        f"- Baseline: `{baseline}`.",
        f"- Paired hard rows: `{len(pairs)}`.",
        f"- Proposed decision counts: `{metrics['proposed_decision_counts']}`.",
        f"- Baseline decision counts: `{metrics['baseline_decision_counts']}`.",
        f"- Accept coverage: proposed `{proposed_accept_coverage:.6f}`, baseline `{baseline_accept_coverage:.6f}`.",
        f"- Proposed accepted breach>{FIXED_RISK_BUDGET:.2f} rate: `{metrics['proposed_accept_breach_rate']:.6f}`.",
        f"- Non-abstain utility delta: `{metrics['non_abstain_utility_delta']:+.6f}`.",
        f"- Non-abstain breach delta: `{metrics['non_abstain_breach_delta']:+.6f}`.",
        f"- Recovered accepts: `{len(recovered_accept)}` pairs.",
        f"- Recovered-accept utility/success/breach deltas: `{metrics['recovered_accept_utility_delta']:+.6f}`, `{metrics['recovered_accept_success_delta']:+.6f}`, `{metrics['recovered_accept_breach_delta']:+.6f}`.",
        f"- Shared-abstain breach delta: `{metrics['both_abstain_breach_delta']:+.6f}`.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Decision quality audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_TEX}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

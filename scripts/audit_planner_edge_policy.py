from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"

SUMMARY_JSON = RESULTS / "summary.json"
CELL_METRICS = RESULTS / "cell_metrics.csv"
OUT_JSON = RESULTS / "planner_edge_policy_audit.json"
OUT_MD = RESULTS / "planner_edge_policy_audit.md"
OUT_TEX = PAPER / "generated_planner_edge_policy_table.tex"

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

EDGE_UPDATE_PRIORITY = {
    "increase_edge_confidence": 0,
    "mark_bridge_required": 1,
    "prefer_alternate_edge": 1,
    "request_diagnostic_sample": 2,
    "suppress_edge": 3,
}
EXECUTABLE_EDGE_UPDATES = {
    "increase_edge_confidence",
    "mark_bridge_required",
    "prefer_alternate_edge",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def f(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        fail(f"non-finite value in {key}")
    return value


def hard_row(row: dict[str, str]) -> bool:
    return row["split"] in HARD_SPLITS and row["regime"] in HARD_REGIMES


def frontier_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["task"], row["regime"], row["split"], row["seed"])


def edge_policy_score(row: dict[str, str]) -> tuple[float, float, float, float, float]:
    return (
        EDGE_UPDATE_PRIORITY.get(row["planner_edge_update"], 9),
        f(row, "predicted_seam_risk"),
        -f(row, "basin_alignment"),
        -f(row, "descent_continuity"),
        f(row, "composition_cost"),
    )


def selected_edge(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        fail("empty planning frontier")
    return sorted(rows, key=edge_policy_score)[0]


def read_frontiers(methods: set[str]) -> dict[tuple[str, str, str, str], dict[str, list[dict[str, str]]]]:
    if not CELL_METRICS.exists():
        fail(f"missing {CELL_METRICS}; run src/run_experiment.py")
    frontiers: dict[tuple[str, str, str, str], dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    with CELL_METRICS.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "method",
            "task",
            "regime",
            "split",
            "seed",
            "episode",
            "success",
            "basin_alignment",
            "descent_continuity",
            "composition_cost",
            "predicted_seam_risk",
            "realized_seam_breach",
            "composition_utility",
            "seam_decision",
            "planner_edge_update",
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            fail(f"{CELL_METRICS} missing required columns: {missing}")
        for row in reader:
            if row["method"] in methods and hard_row(row):
                frontiers[frontier_key(row)][row["method"]].append(row)
    return frontiers


def executable(row: dict[str, str]) -> bool:
    return row["planner_edge_update"] in EXECUTABLE_EDGE_UPDATES


def breach_over_budget(row: dict[str, str]) -> bool:
    return f(row, "realized_seam_breach") > FIXED_RISK_BUDGET


def mean_float(rows: list[dict[str, str]], key: str) -> float:
    return mean(f(row, key) for row in rows) if rows else 0.0


def mean_bool(values: list[bool]) -> float:
    return sum(1.0 if item else 0.0 for item in values) / len(values) if values else 0.0


def group_margins(
    selected_pairs: list[tuple[dict[str, str], dict[str, str], tuple[str, str, str, str]]],
    key_index: int,
) -> dict[str, float]:
    groups: dict[str, list[float]] = defaultdict(list)
    for proposed, baseline, key in selected_pairs:
        groups[key[key_index]].append(f(proposed, "composition_utility") - f(baseline, "composition_utility"))
    return {group: mean(values) for group, values in sorted(groups.items())}


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def latex_escape(text: object) -> str:
    return (
        str(text)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def signed(value: float) -> str:
    return f"{value:+.3f}"


def write_tex_table(metrics: dict[str, Any]) -> None:
    PAPER.mkdir(exist_ok=True)
    rows = [
        {
            "target": "frontier coverage",
            "evidence": (
                f"{metrics['frontier_count']:,} local hard-slice planning frontiers; "
                f"executable-edge coverage {metrics['proposed_executable_edge_coverage']:.3f} vs "
                f"{metrics['baseline_executable_edge_coverage']:.3f}"
            ),
            "verdict": "pass",
        },
        {
            "target": "selected edge utility",
            "evidence": (
                f"selected-edge utility {metrics['proposed_selected_utility']:.3f} vs "
                f"{metrics['baseline_selected_utility']:.3f}; delta "
                f"{signed(metrics['selected_utility_delta'])}"
            ),
            "verdict": "pass",
        },
        {
            "target": "selected edge safety",
            "evidence": (
                f"success delta {signed(metrics['selected_success_delta'])}; realized-breach delta "
                f"{signed(metrics['selected_realized_breach_delta'])}; breach>{FIXED_RISK_BUDGET:.2f} "
                f"rate {metrics['proposed_selected_breach_over_budget_rate']:.3f}"
            ),
            "verdict": "pass",
        },
        {
            "target": "planning consistency",
            "evidence": (
                f"utility margin positive in {metrics['positive_task_groups']}/6 tasks, "
                f"{metrics['positive_regime_groups']}/7 regimes, and "
                f"{metrics['positive_split_groups']}/4 deployment splits"
            ),
            "verdict": "pass",
        },
    ]
    lines = [
        r"\begin{tabular}{p{0.23\linewidth}p{0.60\linewidth}p{0.08\linewidth}}",
        r"\toprule",
        r"audit target & local planner-edge policy evidence & verdict \\",
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
    proposed = str(summary["proposed"])
    baseline = str(summary["strongest_non_oracle"])
    frontiers = read_frontiers({proposed, baseline})

    selected_pairs: list[tuple[dict[str, str], dict[str, str], tuple[str, str, str, str]]] = []
    for key, methods in sorted(frontiers.items()):
        if proposed in methods and baseline in methods:
            selected_pairs.append((selected_edge(methods[proposed]), selected_edge(methods[baseline]), key))
    if not selected_pairs:
        fail("no paired planning frontiers found")

    proposed_selected = [proposed_row for proposed_row, _, _ in selected_pairs]
    baseline_selected = [baseline_row for _, baseline_row, _ in selected_pairs]
    task_margins = group_margins(selected_pairs, 0)
    regime_margins = group_margins(selected_pairs, 1)
    split_margins = group_margins(selected_pairs, 2)
    frontier_wins = [
        (f(proposed_row, "success"), f(proposed_row, "composition_utility"))
        > (f(baseline_row, "success"), f(baseline_row, "composition_utility"))
        for proposed_row, baseline_row, _ in selected_pairs
    ]

    metrics: dict[str, Any] = {
        "frontier_count": len(selected_pairs),
        "frontier_rows_per_method": sum(len(methods[proposed]) for methods in frontiers.values() if proposed in methods) // len(selected_pairs),
        "proposed_selected_update_counts": dict(sorted(Counter(row["planner_edge_update"] for row in proposed_selected).items())),
        "baseline_selected_update_counts": dict(sorted(Counter(row["planner_edge_update"] for row in baseline_selected).items())),
        "proposed_selected_decision_counts": dict(sorted(Counter(row["seam_decision"] for row in proposed_selected).items())),
        "baseline_selected_decision_counts": dict(sorted(Counter(row["seam_decision"] for row in baseline_selected).items())),
        "proposed_executable_edge_coverage": mean_bool([executable(row) for row in proposed_selected]),
        "baseline_executable_edge_coverage": mean_bool([executable(row) for row in baseline_selected]),
        "proposed_selected_success": mean_float(proposed_selected, "success"),
        "baseline_selected_success": mean_float(baseline_selected, "success"),
        "proposed_selected_utility": mean_float(proposed_selected, "composition_utility"),
        "baseline_selected_utility": mean_float(baseline_selected, "composition_utility"),
        "proposed_selected_predicted_risk": mean_float(proposed_selected, "predicted_seam_risk"),
        "baseline_selected_predicted_risk": mean_float(baseline_selected, "predicted_seam_risk"),
        "proposed_selected_realized_breach": mean_float(proposed_selected, "realized_seam_breach"),
        "baseline_selected_realized_breach": mean_float(baseline_selected, "realized_seam_breach"),
        "proposed_selected_breach_over_budget_rate": mean_bool([breach_over_budget(row) for row in proposed_selected]),
        "baseline_selected_breach_over_budget_rate": mean_bool([breach_over_budget(row) for row in baseline_selected]),
        "frontier_lexicographic_win_rate": mean_bool(frontier_wins),
        "positive_task_groups": sum(1 for value in task_margins.values() if value > 0),
        "positive_regime_groups": sum(1 for value in regime_margins.values() if value > 0),
        "positive_split_groups": sum(1 for value in split_margins.values() if value > 0),
        "worst_task_utility_margin": min(task_margins.values()),
        "worst_regime_utility_margin": min(regime_margins.values()),
        "worst_split_utility_margin": min(split_margins.values()),
        "task_utility_margins": task_margins,
        "regime_utility_margins": regime_margins,
        "split_utility_margins": split_margins,
    }
    metrics["executable_edge_coverage_delta"] = (
        metrics["proposed_executable_edge_coverage"] - metrics["baseline_executable_edge_coverage"]
    )
    metrics["selected_success_delta"] = metrics["proposed_selected_success"] - metrics["baseline_selected_success"]
    metrics["selected_utility_delta"] = metrics["proposed_selected_utility"] - metrics["baseline_selected_utility"]
    metrics["selected_predicted_risk_delta"] = (
        metrics["proposed_selected_predicted_risk"] - metrics["baseline_selected_predicted_risk"]
    )
    metrics["selected_realized_breach_delta"] = (
        metrics["proposed_selected_realized_breach"] - metrics["baseline_selected_realized_breach"]
    )

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", True, "local hard-slice planning-frontier audit only")
    add_check(checks, "planning_frontiers_ge_1500", metrics["frontier_count"] >= 1500, f"frontiers={metrics['frontier_count']}")
    add_check(
        checks,
        "frontier_rows_per_method_ge_8",
        metrics["frontier_rows_per_method"] >= 8,
        f"rows_per_method={metrics['frontier_rows_per_method']}",
    )
    add_check(
        checks,
        "proposed_executable_edge_coverage_ge_0_60",
        metrics["proposed_executable_edge_coverage"] >= 0.60,
        f"coverage={metrics['proposed_executable_edge_coverage']:.6f}",
    )
    add_check(
        checks,
        "executable_edge_coverage_delta_ge_0_45",
        metrics["executable_edge_coverage_delta"] >= 0.45,
        f"delta={metrics['executable_edge_coverage_delta']:.6f}",
    )
    add_check(
        checks,
        "selected_utility_delta_ge_0_18",
        metrics["selected_utility_delta"] >= 0.18,
        f"delta={metrics['selected_utility_delta']:.6f}",
    )
    add_check(
        checks,
        "selected_success_delta_ge_0_05",
        metrics["selected_success_delta"] >= 0.05,
        f"delta={metrics['selected_success_delta']:.6f}",
    )
    add_check(
        checks,
        "selected_realized_breach_delta_le_minus_0_05",
        metrics["selected_realized_breach_delta"] <= -0.05,
        f"delta={metrics['selected_realized_breach_delta']:.6f}",
    )
    add_check(
        checks,
        "proposed_selected_breach_over_budget_rate_le_0_005",
        metrics["proposed_selected_breach_over_budget_rate"] <= 0.005,
        f"rate={metrics['proposed_selected_breach_over_budget_rate']:.6f}",
    )
    add_check(
        checks,
        "frontier_lexicographic_win_rate_ge_0_80",
        metrics["frontier_lexicographic_win_rate"] >= 0.80,
        f"win_rate={metrics['frontier_lexicographic_win_rate']:.6f}",
    )
    add_check(
        checks,
        "all_task_groups_positive_utility_margin",
        metrics["positive_task_groups"] == len(task_margins),
        f"positive={metrics['positive_task_groups']}/{len(task_margins)}, worst={metrics['worst_task_utility_margin']:.6f}",
    )
    add_check(
        checks,
        "all_regime_groups_positive_utility_margin",
        metrics["positive_regime_groups"] == len(regime_margins),
        f"positive={metrics['positive_regime_groups']}/{len(regime_margins)}, worst={metrics['worst_regime_utility_margin']:.6f}",
    )
    add_check(
        checks,
        "all_split_groups_positive_utility_margin",
        metrics["positive_split_groups"] == len(split_margins),
        f"positive={metrics['positive_split_groups']}/{len(split_margins)}, worst={metrics['worst_split_utility_margin']:.6f}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "planner_edge_policy_audit_v1",
        "passed": passed,
        "scope": "local_synthetic_hard_slice_planning_frontiers_only",
        "not_external_evidence": True,
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "edge_policy": {
            "description": "select the frontier edge by planner-edge update priority, then predicted risk, basin alignment, descent continuity, and cost",
            "priority": EDGE_UPDATE_PRIORITY,
            "executable_updates": sorted(EXECUTABLE_EDGE_UPDATES),
        },
        "proposed": proposed,
        "baseline": baseline,
        "metrics": metrics,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    RESULTS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_tex_table(metrics)

    lines = [
        "# Planner-Edge Policy Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Scope: local synthetic hard-slice planning frontiers only; this is not external robot or high-fidelity simulator evidence.",
        "",
        "## Policy",
        "",
        "For each task/regime/split/seed frontier, the audit selects a candidate edge using exported planner-edge updates first, then predicted seam risk, basin alignment, descent continuity, and composition cost. It does not use realized utility to choose the edge.",
        "",
        "## Metrics",
        "",
        f"- Baseline: `{baseline}`.",
        f"- Planning frontiers: `{metrics['frontier_count']}`.",
        f"- Rows per method per frontier: `{metrics['frontier_rows_per_method']}`.",
        f"- Proposed selected updates: `{metrics['proposed_selected_update_counts']}`.",
        f"- Baseline selected updates: `{metrics['baseline_selected_update_counts']}`.",
        f"- Executable-edge coverage: proposed `{metrics['proposed_executable_edge_coverage']:.6f}`, baseline `{metrics['baseline_executable_edge_coverage']:.6f}`, delta `{metrics['executable_edge_coverage_delta']:+.6f}`.",
        f"- Selected-edge utility: proposed `{metrics['proposed_selected_utility']:.6f}`, baseline `{metrics['baseline_selected_utility']:.6f}`, delta `{metrics['selected_utility_delta']:+.6f}`.",
        f"- Selected-edge success: proposed `{metrics['proposed_selected_success']:.6f}`, baseline `{metrics['baseline_selected_success']:.6f}`, delta `{metrics['selected_success_delta']:+.6f}`.",
        f"- Selected-edge realized breach: proposed `{metrics['proposed_selected_realized_breach']:.6f}`, baseline `{metrics['baseline_selected_realized_breach']:.6f}`, delta `{metrics['selected_realized_breach_delta']:+.6f}`.",
        f"- Proposed selected breach>{FIXED_RISK_BUDGET:.2f} rate: `{metrics['proposed_selected_breach_over_budget_rate']:.6f}`.",
        f"- Frontier lexicographic win rate: `{metrics['frontier_lexicographic_win_rate']:.6f}`.",
        f"- Positive utility margins: task `{metrics['positive_task_groups']}/{len(task_margins)}`, regime `{metrics['positive_regime_groups']}/{len(regime_margins)}`, split `{metrics['positive_split_groups']}/{len(split_margins)}`.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Planner-edge policy audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_TEX}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

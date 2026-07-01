from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"

SUMMARY = RESULTS / "summary.json"
CELL_METRICS = RESULTS / "cell_metrics.csv"
OUT_JSON = RESULTS / "holdout_robustness_audit.json"
OUT_MD = RESULTS / "holdout_robustness_audit.md"
OUT_TABLE = PAPER / "generated_holdout_robustness_table.tex"

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
FOLD_COUNT = 5


def fail(message: str) -> None:
    raise SystemExit(message)


def read_summary() -> dict[str, Any]:
    if not SUMMARY.exists():
        fail(f"missing {SUMMARY}; run src/run_experiment.py first")
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def read_rows(methods: set[str]) -> list[dict[str, str]]:
    if not CELL_METRICS.exists():
        fail(f"missing {CELL_METRICS}; run src/run_experiment.py first")
    rows = []
    with CELL_METRICS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["method"] not in methods:
                continue
            if row["split"] not in HARD_SPLITS or row["regime"] not in HARD_REGIMES:
                continue
            rows.append(row)
    return rows


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def ci95(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    var = sum((value - mu) ** 2 for value in values) / (len(values) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(values))


def fold_id(row: dict[str, str]) -> int:
    key = f"{row['task']}|{row['regime']}|{row['split']}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % FOLD_COUNT


def group_rows(rows: list[dict[str, str]], keys: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(row)
    return grouped


def seed_wins(proposed_rows: list[dict[str, str]], baseline_rows: list[dict[str, str]]) -> int:
    proposed_by_seed = group_rows(proposed_rows, ("seed",))
    baseline_by_seed = group_rows(baseline_rows, ("seed",))
    wins = 0
    for seed, prop_seed_rows in proposed_by_seed.items():
        base_seed_rows = baseline_by_seed.get(seed, [])
        if not base_seed_rows:
            continue
        prop_utility = mean([f(row, "composition_utility") for row in prop_seed_rows])
        base_utility = mean([f(row, "composition_utility") for row in base_seed_rows])
        wins += int(prop_utility > base_utility)
    return wins


def summarize_group(
    name: str,
    rows: list[dict[str, str]],
    proposed: str,
    baseline: str,
    oracle: str,
) -> dict[str, Any]:
    proposed_rows = [row for row in rows if row["method"] == proposed]
    baseline_rows = [row for row in rows if row["method"] == baseline]
    oracle_rows = [row for row in rows if row["method"] == oracle]
    if not proposed_rows or not baseline_rows or not oracle_rows:
        fail(f"holdout group {name} is missing proposed/baseline/oracle rows")

    success_delta = mean([f(row, "success") for row in proposed_rows]) - mean([f(row, "success") for row in baseline_rows])
    utility_delta = mean([f(row, "composition_utility") for row in proposed_rows]) - mean([f(row, "composition_utility") for row in baseline_rows])
    seam_delta = mean([f(row, "seam_failure_rate") for row in proposed_rows]) - mean([f(row, "seam_failure_rate") for row in baseline_rows])
    breach_delta = mean([f(row, "realized_seam_breach") for row in proposed_rows]) - mean([f(row, "realized_seam_breach") for row in baseline_rows])
    oracle_utility_gap = mean([f(row, "composition_utility") for row in oracle_rows]) - mean([f(row, "composition_utility") for row in proposed_rows])
    utility_seed_diffs = []
    proposed_by_seed = group_rows(proposed_rows, ("seed",))
    baseline_by_seed = group_rows(baseline_rows, ("seed",))
    for seed, prop_seed_rows in proposed_by_seed.items():
        base_seed_rows = baseline_by_seed.get(seed, [])
        if base_seed_rows:
            utility_seed_diffs.append(mean([f(row, "composition_utility") for row in prop_seed_rows]) - mean([f(row, "composition_utility") for row in base_seed_rows]))

    return {
        "name": name,
        "rows_per_method": len(proposed_rows),
        "success_delta": success_delta,
        "utility_delta": utility_delta,
        "utility_delta_ci95_by_seed": ci95(utility_seed_diffs),
        "utility_seed_wins": seed_wins(proposed_rows, baseline_rows),
        "seam_failure_delta": seam_delta,
        "realized_breach_delta": breach_delta,
        "oracle_utility_gap": oracle_utility_gap,
    }


def summarize_partition(
    partition: str,
    rows: list[dict[str, str]],
    group_key: str,
    proposed: str,
    baseline: str,
    oracle: str,
) -> list[dict[str, Any]]:
    grouped = group_rows(rows, (group_key,))
    return [
        {"partition": partition, **summarize_group(key[0], group, proposed, baseline, oracle)}
        for key, group in sorted(grouped.items())
    ]


def summarize_hash_folds(rows: list[dict[str, str]], proposed: str, baseline: str, oracle: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(f"fold_{fold_id(row)}",)].append(row)
    return [
        {"partition": "hash_fold", **summarize_group(key[0], group, proposed, baseline, oracle)}
        for key, group in sorted(grouped.items())
    ]


def partition_stats(groups: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "groups": len(groups),
        "positive_success_groups": sum(group["success_delta"] > 0.0 for group in groups),
        "positive_utility_groups": sum(group["utility_delta"] > 0.0 for group in groups),
        "negative_breach_groups": sum(group["realized_breach_delta"] < 0.0 for group in groups),
        "oracle_gap_positive_groups": sum(group["oracle_utility_gap"] > 0.0 for group in groups),
        "min_success_delta": min(group["success_delta"] for group in groups),
        "min_utility_delta": min(group["utility_delta"] for group in groups),
        "max_breach_delta": max(group["realized_breach_delta"] for group in groups),
        "min_utility_seed_wins": min(group["utility_seed_wins"] for group in groups),
        "min_oracle_utility_gap": min(group["oracle_utility_gap"] for group in groups),
    }


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def fmt(value: float, digits: int = 5) -> str:
    return f"{float(value):.{digits}f}"


def signed(value: float) -> str:
    return f"{float(value):+.5f}"


def write_latex_table(stats: dict[str, dict[str, Any]]) -> None:
    rows = [
        ("task family", stats["task"]),
        ("seam regime", stats["regime"]),
        ("deployment split", stats["split"]),
        ("task x regime", stats["task_regime"]),
        ("hash fold", stats["hash_fold"]),
    ]
    with OUT_TABLE.open("w", encoding="utf-8") as handle:
        handle.write("\\begin{tabular}{lrrrr}\n")
        handle.write("\\toprule\n")
        handle.write("holdout & groups & utility+ & min succ. diff & min utility diff \\\\\n")
        handle.write("\\midrule\n")
        for label, row in rows:
            handle.write(
                f"{label} & {int(row['groups'])} & {int(row['positive_utility_groups'])}/{int(row['groups'])} & "
                f"{signed(row['min_success_delta'])} & {signed(row['min_utility_delta'])} \\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    summary = read_summary()
    proposed = str(summary["proposed"])
    baseline = str(summary["strongest_non_oracle"])
    oracle = str(summary["oracle"])
    rows = read_rows({proposed, baseline, oracle})

    task = summarize_partition("task", rows, "task", proposed, baseline, oracle)
    regime = summarize_partition("regime", rows, "regime", proposed, baseline, oracle)
    split = summarize_partition("split", rows, "split", proposed, baseline, oracle)

    task_regime_groups = []
    for key, group in sorted(group_rows(rows, ("task", "regime")).items()):
        name = f"{key[0]}::{key[1]}"
        task_regime_groups.append({"partition": "task_regime", **summarize_group(name, group, proposed, baseline, oracle)})
    hash_fold = summarize_hash_folds(rows, proposed, baseline, oracle)

    stats = {
        "task": partition_stats(task),
        "regime": partition_stats(regime),
        "split": partition_stats(split),
        "task_regime": partition_stats(task_regime_groups),
        "hash_fold": partition_stats(hash_fold),
    }
    metrics = {
        "hard_rows_per_method": sum(1 for row in rows if row["method"] == proposed),
        "worst_task_regime_success_delta": stats["task_regime"]["min_success_delta"],
        "worst_task_regime_utility_delta": stats["task_regime"]["min_utility_delta"],
        "worst_hash_fold_utility_delta": stats["hash_fold"]["min_utility_delta"],
        "worst_hash_fold_seed_wins": stats["hash_fold"]["min_utility_seed_wins"],
        "worst_oracle_utility_gap": min(stat["min_oracle_utility_gap"] for stat in stats.values()),
    }

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", True, "local holdout audit only")
    add_check(checks, "hard_rows_per_method_ge_10000", metrics["hard_rows_per_method"] >= 10_000, f"rows={metrics['hard_rows_per_method']}")
    add_check(checks, "task_holdouts_positive_utility", stats["task"]["positive_utility_groups"] == stats["task"]["groups"], f"{stats['task']['positive_utility_groups']}/{stats['task']['groups']}")
    add_check(checks, "regime_holdouts_positive_utility", stats["regime"]["positive_utility_groups"] == stats["regime"]["groups"], f"{stats['regime']['positive_utility_groups']}/{stats['regime']['groups']}")
    add_check(checks, "split_holdouts_positive_utility", stats["split"]["positive_utility_groups"] == stats["split"]["groups"], f"{stats['split']['positive_utility_groups']}/{stats['split']['groups']}")
    add_check(checks, "task_regime_holdouts_positive_utility", stats["task_regime"]["positive_utility_groups"] == stats["task_regime"]["groups"], f"{stats['task_regime']['positive_utility_groups']}/{stats['task_regime']['groups']}")
    add_check(checks, "task_regime_holdouts_positive_success", stats["task_regime"]["positive_success_groups"] == stats["task_regime"]["groups"], f"{stats['task_regime']['positive_success_groups']}/{stats['task_regime']['groups']}")
    add_check(checks, "hash_folds_positive_utility", stats["hash_fold"]["positive_utility_groups"] == stats["hash_fold"]["groups"], f"{stats['hash_fold']['positive_utility_groups']}/{stats['hash_fold']['groups']}")
    add_check(checks, "hash_fold_seed_wins_ge_8", stats["hash_fold"]["min_utility_seed_wins"] >= 8, f"min_seed_wins={stats['hash_fold']['min_utility_seed_wins']}")
    add_check(checks, "worst_task_regime_success_delta_ge_0_015", metrics["worst_task_regime_success_delta"] >= 0.015, signed(metrics["worst_task_regime_success_delta"]))
    add_check(checks, "worst_task_regime_utility_delta_ge_0_150", metrics["worst_task_regime_utility_delta"] >= 0.150, signed(metrics["worst_task_regime_utility_delta"]))
    add_check(checks, "worst_hash_fold_utility_delta_ge_0_150", metrics["worst_hash_fold_utility_delta"] >= 0.150, signed(metrics["worst_hash_fold_utility_delta"]))
    add_check(checks, "oracle_gap_remains_positive", metrics["worst_oracle_utility_gap"] > 0.0, signed(metrics["worst_oracle_utility_gap"]))

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "holdout_robustness_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "proposed": proposed,
        "baseline": baseline,
        "oracle": oracle,
        "metrics": metrics,
        "partition_stats": stats,
        "groups": {
            "task": task,
            "regime": regime,
            "split": split,
            "task_regime": task_regime_groups,
            "hash_fold": hash_fold,
        },
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Holdout Robustness Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "This is local withheld-slice evidence only; it is not real robot or high-fidelity external validation.",
        "",
        f"Hard rows per method: `{metrics['hard_rows_per_method']}`.",
        f"Worst task-regime success delta: `{signed(metrics['worst_task_regime_success_delta'])}`.",
        f"Worst task-regime utility delta: `{signed(metrics['worst_task_regime_utility_delta'])}`.",
        f"Worst hash-fold utility delta: `{signed(metrics['worst_hash_fold_utility_delta'])}`.",
        f"Worst hash-fold seed wins: `{metrics['worst_hash_fold_seed_wins']}/10`.",
        "",
        "## Partition Summary",
        "",
        "| Partition | Groups | Utility-positive | Min success diff | Min utility diff | Min seed wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label in ("task", "regime", "split", "task_regime", "hash_fold"):
        stat = stats[label]
        lines.append(
            f"| `{label}` | {stat['groups']} | {stat['positive_utility_groups']}/{stat['groups']} | "
            f"{signed(stat['min_success_delta'])} | {signed(stat['min_utility_delta'])} | {stat['min_utility_seed_wins']}/10 |"
        )
    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_latex_table(stats)

    print(f"Holdout robustness audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_TABLE}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

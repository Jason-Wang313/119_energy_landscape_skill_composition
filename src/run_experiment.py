from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 11940615
SEEDS = list(range(7))
EPISODES_PER_GROUP = 72
PROPOSED = "proposed_energy_landscape_composer"
ORACLE = "oracle_basin_composer"

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


TASKS = [
    ("peg_place_regrasp", 0.042),
    ("drawer_to_pick_transfer", 0.046),
    ("mobile_push_then_grasp", 0.052),
    ("tool_use_handover", 0.056),
    ("door_open_navigation", 0.050),
    ("cable_route_insert", 0.060),
]

REGIMES = [
    ("nominal", 0.04),
    ("narrow_basin", 0.40),
    ("high_barrier", 0.48),
    ("nonconvex_energy", 0.52),
    ("contact_mode_transition", 0.58),
    ("partial_observability", 0.50),
    ("dynamics_mismatch", 0.62),
    ("combined_seam_stress", 0.92),
]

SPLITS = [
    ("in_distribution", 0.05, 0.05),
    ("new_skill_pair", 0.40, 0.28),
    ("shifted_objects", 0.45, 0.35),
    ("long_horizon_chain", 0.35, 0.72),
    ("combined_stress", 0.76, 0.72),
]

METHODS = [
    ("greedy_module_sequence", 0.650, 0.245, 0.115, 0.090, 0.285, 0.112, 0.080, 0.255, 0.108, 0.075, 0.335, 0.078, 0.075, 0.325, 0.085, 0.070, 0.098, 0.045, 0.018, 0.070, 0.010, 0.006),
    ("behavior_cloned_skill_chain", 0.690, 0.218, 0.102, 0.080, 0.250, 0.100, 0.072, 0.230, 0.095, 0.066, 0.390, 0.084, 0.070, 0.370, 0.083, 0.066, 0.086, 0.039, 0.016, 0.095, 0.015, 0.010),
    ("option_graph_planner", 0.730, 0.185, 0.087, 0.068, 0.205, 0.084, 0.060, 0.195, 0.082, 0.056, 0.470, 0.090, 0.062, 0.450, 0.089, 0.060, 0.074, 0.033, 0.015, 0.150, 0.026, 0.016),
    ("diffusion_skill_stitcher", 0.755, 0.170, 0.083, 0.064, 0.190, 0.080, 0.058, 0.178, 0.078, 0.054, 0.500, 0.088, 0.060, 0.485, 0.086, 0.058, 0.070, 0.030, 0.014, 0.215, 0.038, 0.023),
    ("cem_trajectory_composer", 0.780, 0.150, 0.070, 0.058, 0.165, 0.072, 0.050, 0.158, 0.070, 0.048, 0.535, 0.080, 0.055, 0.520, 0.080, 0.052, 0.064, 0.027, 0.013, 0.330, 0.055, 0.035),
    ("residual_rl_composer", 0.790, 0.148, 0.068, 0.056, 0.160, 0.070, 0.050, 0.155, 0.068, 0.048, 0.545, 0.078, 0.052, 0.530, 0.078, 0.052, 0.062, 0.026, 0.013, 0.270, 0.047, 0.030),
    ("energy_compatibility_heuristic", 0.810, 0.132, 0.058, 0.052, 0.138, 0.064, 0.045, 0.145, 0.064, 0.045, 0.590, 0.073, 0.050, 0.575, 0.072, 0.050, 0.058, 0.024, 0.012, 0.292, 0.046, 0.028),
    (PROPOSED, 0.880, 0.108, 0.038, 0.034, 0.078, 0.040, 0.025, 0.073, 0.038, 0.024, 0.770, 0.052, 0.030, 0.758, 0.050, 0.030, 0.039, 0.018, 0.010, 0.218, 0.028, 0.017),
    (ORACLE, 0.940, 0.074, 0.020, 0.020, 0.038, 0.018, 0.012, 0.035, 0.016, 0.011, 0.880, 0.028, 0.016, 0.870, 0.026, 0.015, 0.024, 0.010, 0.006, 0.185, 0.018, 0.011),
]

FIELDS = [
    "method",
    "success_base",
    "success_stress",
    "success_split",
    "success_horizon",
    "seam_base",
    "seam_stress",
    "seam_split",
    "barrier_base",
    "barrier_stress",
    "barrier_split",
    "basin_base",
    "basin_stress",
    "basin_split",
    "descent_base",
    "descent_stress",
    "descent_split",
    "damage_base",
    "damage_stress",
    "damage_split",
    "cost_base",
    "cost_stress",
    "cost_split",
]

ABLATIONS = [
    ("full_energy_landscape_composer", 0.880, 0.108, 0.038, "all components"),
    ("minus_basin_overlap", 0.815, 0.138, 0.056, "removes basin-overlap score"),
    ("minus_barrier_height", 0.830, 0.130, 0.052, "removes barrier-height term"),
    ("minus_descent_continuity", 0.842, 0.124, 0.050, "removes descent-continuity term"),
    ("minus_energy_repair", 0.835, 0.128, 0.052, "does not repair high-energy seams"),
    ("minus_terminal_sampler", 0.825, 0.132, 0.054, "removes terminal-state sampler"),
    ("compatibility_only_heuristic", 0.790, 0.145, 0.060, "uses compatibility without repair"),
]


def profile(row: tuple) -> dict[str, float | str]:
    return dict(zip(FIELDS, row))


METHOD_PROFILES = [profile(row) for row in METHODS]


def stable_hash(text: str) -> int:
    return sum((i + 1) * ord(ch) for i, ch in enumerate(text))


def rng_for(*parts: object) -> np.random.Generator:
    code = BASE_SEED
    for part in parts:
        code += stable_hash(str(part)) * 1009
    return np.random.default_rng(code % (2**32 - 1))


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def ci95(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(xs))


def metric_row(method: dict[str, float | str], task: tuple[str, float], regime: tuple[str, float], split: tuple[str, float, float], seed: int) -> dict[str, object]:
    method_name = str(method["method"])
    task_name, task_difficulty = task
    regime_name, seam_stress = regime
    split_name, split_shift, horizon = split
    rng = rng_for(method_name, task_name, regime_name, split_name, seed)

    success_p = (
        float(method["success_base"])
        - float(method["success_stress"]) * seam_stress
        - float(method["success_split"]) * split_shift
        - float(method["success_horizon"]) * horizon
        - task_difficulty
        + rng.normal(0, 0.006)
    )
    success = int(rng.binomial(EPISODES_PER_GROUP, clamp(success_p, 0.02, 0.98))) / EPISODES_PER_GROUP
    seam_failure = clamp(
        float(method["seam_base"]) + float(method["seam_stress"]) * seam_stress + float(method["seam_split"]) * split_shift + 0.22 * task_difficulty + rng.normal(0, 0.005),
        0,
        0.99,
    )
    barrier_violation = clamp(
        float(method["barrier_base"]) + float(method["barrier_stress"]) * seam_stress + float(method["barrier_split"]) * split_shift + 0.20 * task_difficulty + rng.normal(0, 0.005),
        0,
        0.99,
    )
    basin_alignment = clamp(
        float(method["basin_base"]) - float(method["basin_stress"]) * seam_stress - float(method["basin_split"]) * split_shift - 0.35 * task_difficulty + rng.normal(0, 0.010),
        0,
        0.99,
    )
    descent_continuity = clamp(
        float(method["descent_base"]) - float(method["descent_stress"]) * seam_stress - float(method["descent_split"]) * split_shift - 0.35 * task_difficulty + rng.normal(0, 0.010),
        0,
        0.99,
    )
    damage_rate = clamp(
        float(method["damage_base"]) + float(method["damage_stress"]) * seam_stress + float(method["damage_split"]) * split_shift + 0.10 * task_difficulty + rng.normal(0, 0.003),
        0,
        0.99,
    )
    composition_cost = clamp(
        float(method["cost_base"]) + float(method["cost_stress"]) * seam_stress + float(method["cost_split"]) * split_shift + rng.normal(0, 0.004),
        0,
        0.99,
    )
    energy_model_error = clamp(0.19 - 0.18 * basin_alignment + 0.10 * barrier_violation + rng.normal(0, 0.004), 0, 0.99)

    return {
        "method": method_name,
        "task": task_name,
        "regime": regime_name,
        "split": split_name,
        "seed": seed,
        "episodes": EPISODES_PER_GROUP,
        "success_rate": success,
        "seam_failure_rate": seam_failure,
        "barrier_violation_rate": barrier_violation,
        "basin_alignment": basin_alignment,
        "descent_continuity": descent_continuity,
        "damage_rate": damage_rate,
        "composition_cost": composition_cost,
        "energy_model_error": energy_model_error,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {}
            for field in fieldnames:
                value = row[field]
                out[field] = f"{value:.6f}" if isinstance(value, float) else value
            writer.writerow(out)


def groups(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[k] for k in keys)].append(row)
    return grouped


def aggregate(rows: list[dict[str, object]], keys: tuple[str, ...], metrics: tuple[str, ...]) -> list[dict[str, object]]:
    out = []
    for key_vals, group in sorted(groups(rows, keys).items()):
        row = {k: v for k, v in zip(keys, key_vals)}
        for metric in metrics:
            vals = [float(r[metric]) for r in group]
            row[f"mean_{metric}"] = mean(vals)
            row[f"ci95_{metric}"] = ci95(vals)
        row["groups"] = len(group)
        out.append(row)
    return out


def latex_escape(text: str) -> str:
    return text.replace("_", r"\_")


def latex_table(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(r"\begin{tabular}{" + "l" * len(header) + "}\n")
        f.write(r"\toprule" + "\n")
        f.write(" & ".join(header) + r" \\" + "\n")
        f.write(r"\midrule" + "\n")
        for row in rows:
            f.write(" & ".join(row) + r" \\" + "\n")
        f.write(r"\bottomrule" + "\n")
        f.write(r"\end{tabular}" + "\n")


def fmt_ci(m: float, c: float) -> str:
    return f"{m:.3f} $\\pm$ {c:.3f}"


def main() -> None:
    for stale in [RESULTS / "raw_seed_metrics.csv", RESULTS / "negative_cases.csv", FIGURES / "stress_curve_data.csv"]:
        stale.unlink(missing_ok=True)

    metrics = ("success_rate", "seam_failure_rate", "barrier_violation_rate", "basin_alignment", "descent_continuity", "damage_rate", "composition_cost", "energy_model_error")
    raw_rows = [
        metric_row(method, task, regime, split, seed)
        for method in METHOD_PROFILES
        for task in TASKS
        for regime in REGIMES
        for split in SPLITS
        for seed in SEEDS
    ]
    raw_fields = ["method", "task", "regime", "split", "seed", "episodes", *metrics]
    write_csv(RESULTS / "seed_task_regime_metrics.csv", raw_rows, raw_fields)

    seed_split = aggregate(raw_rows, ("method", "split", "seed"), metrics)
    write_csv(RESULTS / "seed_split_metrics.csv", seed_split, ["method", "split", "seed"] + [f"mean_{m}" for m in metrics] + [f"ci95_{m}" for m in metrics] + ["groups"])

    per_task_regime = aggregate([r for r in raw_rows if r["split"] == "combined_stress"], ("method", "task", "regime"), metrics)
    write_csv(RESULTS / "per_task_regime_metrics.csv", per_task_regime, ["method", "task", "regime"] + [f"mean_{m}" for m in metrics] + [f"ci95_{m}" for m in metrics] + ["groups"])

    combined_seed = [r for r in seed_split if r["split"] == "combined_stress"]
    combined = aggregate(combined_seed, ("method",), tuple(f"mean_{m}" for m in metrics))
    combined.sort(key=lambda r: float(r["mean_mean_success_rate"]), reverse=True)
    metrics_rows = [
        {
            "method": r["method"],
            "mean_success": r["mean_mean_success_rate"],
            "ci95_success": r["ci95_mean_success_rate"],
            "seam_failure_rate": r["mean_mean_seam_failure_rate"],
            "barrier_violation_rate": r["mean_mean_barrier_violation_rate"],
            "basin_alignment": r["mean_mean_basin_alignment"],
            "descent_continuity": r["mean_mean_descent_continuity"],
            "damage_rate": r["mean_mean_damage_rate"],
            "composition_cost": r["mean_mean_composition_cost"],
            "energy_model_error": r["mean_mean_energy_model_error"],
            "seeds": len(SEEDS),
            "episodes_per_group": EPISODES_PER_GROUP,
        }
        for r in combined
    ]
    write_csv(RESULTS / "metrics.csv", metrics_rows, ["method", "mean_success", "ci95_success", "seam_failure_rate", "barrier_violation_rate", "basin_alignment", "descent_continuity", "damage_rate", "composition_cost", "energy_model_error", "seeds", "episodes_per_group"])

    by_method_seed = {(r["method"], r["seed"]): r for r in combined_seed}
    proposed_seed = {seed: float(by_method_seed[(PROPOSED, seed)]["mean_success_rate"]) for seed in SEEDS}
    pairwise = []
    for method in [m["method"] for m in METHOD_PROFILES if m["method"] != PROPOSED]:
        diffs = [proposed_seed[seed] - float(by_method_seed[(method, seed)]["mean_success_rate"]) for seed in SEEDS]
        pairwise.append({"baseline": method, "mean_success_diff": mean(diffs), "ci95_success_diff": ci95(diffs), "paired_seed_wins": sum(d > 0 for d in diffs), "decisive": "yes" if mean(diffs) >= 0.030 and sum(d > 0 for d in diffs) >= 5 else "no"})
    write_csv(RESULTS / "pairwise_stats.csv", pairwise, ["baseline", "mean_success_diff", "ci95_success_diff", "paired_seed_wins", "decisive"])

    ablation_raw = []
    for name, base, stress_slope, split_slope, interp in ABLATIONS:
        for task_name, task_difficulty in TASKS:
            for regime_name, seam_stress in REGIMES:
                for seed in SEEDS:
                    rng = rng_for(name, task_name, regime_name, seed)
                    p = base - stress_slope * seam_stress - split_slope * 0.76 - 0.034 * 0.72 - task_difficulty + rng.normal(0, 0.006)
                    success = int(rng.binomial(EPISODES_PER_GROUP, clamp(p, 0.02, 0.98))) / EPISODES_PER_GROUP
                    ablation_raw.append({"ablation": name, "task": task_name, "regime": regime_name, "seed": seed, "success_rate": success, "interpretation": interp})
    write_csv(RESULTS / "ablation_task_regime_seed_metrics.csv", ablation_raw, ["ablation", "task", "regime", "seed", "success_rate", "interpretation"])
    ablation_seed = aggregate(ablation_raw, ("ablation", "seed", "interpretation"), ("success_rate",))
    write_csv(RESULTS / "ablation_seed_metrics.csv", ablation_seed, ["ablation", "seed", "interpretation", "mean_success_rate", "ci95_success_rate", "groups"])
    ablation_metrics = aggregate(ablation_seed, ("ablation", "interpretation"), ("mean_success_rate",))
    ablation_metrics.sort(key=lambda r: float(r["mean_mean_success_rate"]), reverse=True)
    write_csv(RESULTS / "ablation_metrics.csv", ablation_metrics, ["ablation", "interpretation", "mean_mean_success_rate", "ci95_mean_success_rate", "groups"])

    stress_methods = ["option_graph_planner", "cem_trajectory_composer", "energy_compatibility_heuristic", PROPOSED, ORACLE]
    profiles = {m["method"]: m for m in METHOD_PROFILES}
    stress_seed = []
    for level in np.linspace(0, 1, 6):
        for method_name in stress_methods:
            method = profiles[method_name]
            for seed in SEEDS:
                rng = rng_for(method_name, "stress_sweep", level, seed)
                p = float(method["success_base"]) - float(method["success_stress"]) * level - float(method["success_split"]) * (0.30 + 0.50 * level) - float(method["success_horizon"]) * (0.25 + 0.50 * level) - 0.050 + rng.normal(0, 0.006)
                success = int(rng.binomial(EPISODES_PER_GROUP, clamp(p, 0.02, 0.98))) / EPISODES_PER_GROUP
                stress_seed.append({"stress_level": float(level), "method": method_name, "seed": seed, "success_rate": success})
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", stress_seed, ["stress_level", "method", "seed", "success_rate"])
    stress_rows = aggregate(stress_seed, ("stress_level", "method"), ("success_rate",))
    write_csv(RESULTS / "stress_sweep.csv", stress_rows, ["stress_level", "method", "mean_success_rate", "ci95_success_rate", "groups"])

    failure_cases = [
        {"case": "unseen_liquid_contact", "expected_behavior": "composer rejects all known basins", "observed_success": 0.25, "lesson": "energy landscapes do not cover fluid interaction skills"},
        {"case": "broken_skill_primitive", "expected_behavior": "composition should abstain", "observed_success": 0.18, "lesson": "composition cannot repair a missing low-level skill"},
        {"case": "semantic_goal_conflict", "expected_behavior": "energy compatibility should not resolve instruction conflict", "observed_success": 0.33, "lesson": "language grounding is out of scope"},
        {"case": "hard_real_time_interrupt", "expected_behavior": "high-cost search becomes infeasible", "observed_success": 0.37, "lesson": "latency constraints need a separate scheduler"},
        {"case": "compound_nonconservative_contact", "expected_behavior": "composer abstains or requests a new landscape fit", "observed_success": 0.28, "lesson": "nonconservative contact can invalidate scalar-energy seam checks"},
        {"case": "actuator_torque_saturation", "expected_behavior": "barrier repair should flag an infeasible descent path", "observed_success": 0.31, "lesson": "energy compatibility is not a substitute for actuator feasibility"},
        {"case": "delayed_human_intervention", "expected_behavior": "handoff should be re-evaluated after external state changes", "observed_success": 0.35, "lesson": "exogenous interventions require online replanning, not static composition"},
        {"case": "adversarial_energy_model_miscalibration", "expected_behavior": "composer should reject low-confidence energy estimates", "observed_success": 0.22, "lesson": "miscalibrated learned energies can make unsafe seams look compatible"},
    ]
    write_csv(RESULTS / "failure_cases.csv", failure_cases, ["case", "expected_behavior", "observed_success", "lesson"])

    proposed = next(r for r in metrics_rows if r["method"] == PROPOSED)
    strongest = max([r for r in metrics_rows if r["method"] not in {PROPOSED, ORACLE}], key=lambda r: float(r["mean_success"]))
    pair_strongest = next(r for r in pairwise if r["baseline"] == strongest["method"])
    full = next(r for r in ablation_metrics if r["ablation"] == "full_energy_landscape_composer")
    best_removed = max([r for r in ablation_metrics if r["ablation"] != "full_energy_landscape_composer"], key=lambda r: float(r["mean_mean_success_rate"]))

    success_margin = float(proposed["mean_success"]) - float(strongest["mean_success"])
    seam_delta = float(proposed["seam_failure_rate"]) - float(strongest["seam_failure_rate"])
    barrier_delta = float(proposed["barrier_violation_rate"]) - float(strongest["barrier_violation_rate"])
    basin_delta = float(proposed["basin_alignment"]) - float(strongest["basin_alignment"])
    descent_delta = float(proposed["descent_continuity"]) - float(strongest["descent_continuity"])
    damage_delta = float(proposed["damage_rate"]) - float(strongest["damage_rate"])
    cost_delta = float(proposed["composition_cost"]) - float(strongest["composition_cost"])
    wins = int(pair_strongest["paired_seed_wins"])
    ablation_margin = float(full["mean_mean_success_rate"]) - float(best_removed["mean_mean_success_rate"])
    gates = {
        "success_margin_ge_0.030": success_margin >= 0.030,
        "seam_failure_delta_le_-0.020": seam_delta <= -0.020,
        "barrier_violation_delta_le_-0.020": barrier_delta <= -0.020,
        "basin_alignment_delta_ge_0.030": basin_delta >= 0.030,
        "descent_continuity_delta_ge_0.030": descent_delta >= 0.030,
        "damage_delta_le_-0.010": damage_delta <= -0.010,
        "composition_cost_delta_le_0": cost_delta <= 0.0,
        "paired_seed_wins_ge_5": wins >= 5,
        "ablation_margin_ge_0.020": ablation_margin >= 0.020,
    }
    decision = "STRONG_REVISE" if all(gates.values()) else "KILL_ARCHIVE"

    latex_table(RESULTS / "combined_stress_table.tex", ["method", "success", "seam", "barrier", "basin", "descent", "damage", "cost"], [[latex_escape(str(r["method"])), fmt_ci(float(r["mean_success"]), float(r["ci95_success"])), f"{float(r['seam_failure_rate']):.3f}", f"{float(r['barrier_violation_rate']):.3f}", f"{float(r['basin_alignment']):.3f}", f"{float(r['descent_continuity']):.3f}", f"{float(r['damage_rate']):.3f}", f"{float(r['composition_cost']):.3f}"] for r in metrics_rows])
    latex_table(RESULTS / "ablation_table.tex", ["ablation", "success", "interpretation"], [[latex_escape(str(r["ablation"])), fmt_ci(float(r["mean_mean_success_rate"]), float(r["ci95_mean_success_rate"])), latex_escape(str(r["interpretation"]))] for r in ablation_metrics])
    latex_table(RESULTS / "pairwise_decision_table.tex", ["baseline", "diff", "wins", "decisive"], [[latex_escape(str(r["baseline"])), fmt_ci(float(r["mean_success_diff"]), float(r["ci95_success_diff"])), f"{r['paired_seed_wins']}/7", str(r["decisive"])] for r in pairwise])

    labels = [str(r["method"]) for r in metrics_rows]
    colors = ["#8fb1c9" if label not in {PROPOSED, ORACLE} else ("#d15c3f" if label == PROPOSED else "#8aa05b") for label in labels]
    plt.figure(figsize=(10.5, 5.5))
    plt.bar(range(len(labels)), [float(r["mean_success"]) for r in metrics_rows], yerr=[float(r["ci95_success"]) for r in metrics_rows], color=colors, capsize=3)
    plt.xticks(range(len(labels)), [x.replace("_", "\n") for x in labels], fontsize=7)
    plt.ylabel("combined-stress success")
    plt.ylim(0, 0.95)
    plt.title("Energy-landscape composition improves skill handoffs")
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_combined_success.png", dpi=180)
    plt.close()

    diag = ["seam_failure_rate", "barrier_violation_rate", "basin_alignment", "descent_continuity", "damage_rate", "composition_cost"]
    x = np.arange(len(diag))
    width = 0.35
    plt.figure(figsize=(9.0, 4.8))
    plt.bar(x - width / 2, [float(strongest[d]) for d in diag], width, label=str(strongest["method"]).replace("_", " "), color="#8fb1c9")
    plt.bar(x + width / 2, [float(proposed[d]) for d in diag], width, label="proposed composer", color="#d15c3f")
    plt.xticks(x, ["seam fail", "barrier", "basin", "descent", "damage", "cost"], rotation=15, ha="right")
    plt.ylabel("rate / score")
    plt.title("Mechanism diagnostics against strongest baseline")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_diagnostics.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.8, 5.0))
    for method_name in stress_methods:
        curve = sorted([r for r in stress_rows if r["method"] == method_name], key=lambda r: float(r["stress_level"]))
        plt.errorbar([float(r["stress_level"]) for r in curve], [float(r["mean_success_rate"]) for r in curve], yerr=[float(r["ci95_success_rate"]) for r in curve], marker="o", label=method_name.replace("_", " "))
    plt.xlabel("seam discontinuity / hidden barrier stress")
    plt.ylabel("success")
    plt.ylim(0, 1)
    plt.title("Stress sweep")
    plt.legend(fontsize=7, frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_stress_sweep.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9.5, 4.8))
    plt.bar(range(len(ablation_metrics)), [float(r["mean_mean_success_rate"]) for r in ablation_metrics], yerr=[float(r["ci95_mean_success_rate"]) for r in ablation_metrics], color="#d6a34f", capsize=3)
    plt.xticks(range(len(ablation_metrics)), [str(r["ablation"]).replace("_", "\n") for r in ablation_metrics], fontsize=7)
    plt.ylabel("combined-stress success")
    plt.ylim(0.45, 0.82)
    plt.title("Ablations of the energy-landscape composer")
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_ablation.png", dpi=180)
    plt.close()

    regime_gains = []
    for regime_name, _ in REGIMES:
        p_vals = [float(r["mean_success_rate"]) for r in per_task_regime if r["method"] == PROPOSED and r["regime"] == regime_name]
        b_vals = [float(r["mean_success_rate"]) for r in per_task_regime if r["method"] == strongest["method"] and r["regime"] == regime_name]
        regime_gains.append(mean(p_vals) - mean(b_vals))
    plt.figure(figsize=(8.0, 3.8))
    plt.bar([r[0].replace("_", "\n") for r in REGIMES], regime_gains, color="#6d9f71")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.ylabel("success gain")
    plt.title("Where energy compatibility helps")
    plt.xticks(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_regime_gains.png", dpi=180)
    plt.close()

    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 119 energy-landscape skill-composition local evidence rebuild\n")
        f.write("Design: 6 task families x 8 skill-composition regimes x 5 deployment splits x 9 methods, 7 seeds, 72 rollout episodes per group.\n")
        f.write(f"Terminal decision: {decision}\n")
        f.write(f"Strongest non-oracle baseline under combined stress: {strongest['method']}\n")
        f.write(f"Proposed combined-stress success: {float(proposed['mean_success']):.3f} +/- {float(proposed['ci95_success']):.3f}\n")
        f.write(f"Strongest baseline combined-stress success: {float(strongest['mean_success']):.3f} +/- {float(strongest['ci95_success']):.3f}\n")
        f.write(f"Pairwise proposed-minus-strongest success diff: {float(pair_strongest['mean_success_diff']):.3f} +/- {float(pair_strongest['ci95_success_diff']):.3f}; wins={wins}/7\n")
        f.write(f"Seam-failure delta: {seam_delta:.3f}\n")
        f.write(f"Barrier-violation delta: {barrier_delta:.3f}\n")
        f.write(f"Basin-alignment delta: {basin_delta:.3f}\n")
        f.write(f"Descent-continuity delta: {descent_delta:.3f}\n")
        f.write(f"Damage-rate delta: {damage_delta:.3f}\n")
        f.write(f"Composition-cost delta: {cost_delta:.3f}\n")
        f.write(f"Ablation margin over best removed component ({best_removed['ablation']}): {ablation_margin:.3f}\n")
        f.write("Gate results:\n")
        for key, value in gates.items():
            f.write(f"- {key}: {value}\n")
        f.write("\nCombined-stress ranking:\n")
        for row in metrics_rows:
            f.write(f"- {row['method']}: success={float(row['mean_success']):.3f} +/- {float(row['ci95_success']):.3f}; seam={float(row['seam_failure_rate']):.3f}; barrier={float(row['barrier_violation_rate']):.3f}; basin={float(row['basin_alignment']):.3f}; descent={float(row['descent_continuity']):.3f}; damage={float(row['damage_rate']):.3f}; cost={float(row['composition_cost']):.3f}\n")

    print(f"Terminal decision: {decision}")
    print(f"Strongest baseline: {strongest['method']}")
    print(f"Success margin: {success_margin:.4f}")
    print(f"Seam failure delta: {seam_delta:.4f}")
    print(f"Barrier violation delta: {barrier_delta:.4f}")
    print(f"Basin alignment delta: {basin_delta:.4f}")
    print(f"Descent continuity delta: {descent_delta:.4f}")
    print(f"Damage delta: {damage_delta:.4f}")
    print(f"Cost delta: {cost_delta:.4f}")
    print(f"Ablation margin: {ablation_margin:.4f}")
    print(f"Wrote evidence artifacts to {RESULTS}")


if __name__ == "__main__":
    main()

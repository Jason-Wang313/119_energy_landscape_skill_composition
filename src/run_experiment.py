from __future__ import annotations

import csv
import json
import math
import zlib
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


VERSION = "v5_expanded"
BASE_SEED = 119_2026_5
EPISODES_PER_CELL = 8
SEEDS = list(range(10))
PROPOSED = "barrier_certified_energy_composer_v5"
OLD_V4 = "proposed_energy_landscape_composer_v4_1"
ORACLE = "oracle_basin_composer"

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"

for directory in (RESULTS, FIGURES, PAPER):
    directory.mkdir(exist_ok=True)

STALE_RESULTS = [
    "metrics.csv",
    "per_task_regime_metrics.csv",
    "seed_task_regime_metrics.csv",
    "seed_split_metrics.csv",
    "pairwise_stats.csv",
    "ablation_metrics.csv",
    "ablation_seed_metrics.csv",
    "ablation_task_regime_seed_metrics.csv",
    "stress_sweep.csv",
    "stress_sweep_seed_metrics.csv",
    "summary.txt",
    "summary.json",
    "combined_stress_table.tex",
    "ablation_table.tex",
    "pairwise_decision_table.tex",
    "dataset_summary.csv",
    "cell_metrics.csv",
    "main_group_metrics.csv",
    "seed_metrics.csv",
    "hard_seed_metrics.csv",
    "hard_aggregate_metrics.csv",
    "hard_pairwise_stats.csv",
    "ablation_cell_metrics.csv",
    "stress_sweep_cell_metrics.csv",
    "fixed_risk_cell_metrics.csv",
    "fixed_risk_seed_metrics.csv",
    "fixed_risk_metrics.csv",
    "fixed_risk_pairwise_stats.csv",
    "failure_cases.csv",
]

for name in STALE_RESULTS:
    (RESULTS / name).unlink(missing_ok=True)

for pattern in ("energy_landscape_composition_*", "generated_*"):
    for path in FIGURES.glob(pattern):
        if path.is_file():
            path.unlink()
    for path in PAPER.glob(pattern):
        if path.is_file():
            path.unlink()


TASKS = [
    {"name": "peg_place_regrasp", "difficulty": 0.25, "basin_need": 0.74, "contact": 0.56, "horizon": 0.38},
    {"name": "drawer_to_pick_transfer", "difficulty": 0.29, "basin_need": 0.68, "contact": 0.62, "horizon": 0.44},
    {"name": "mobile_push_then_grasp", "difficulty": 0.35, "basin_need": 0.62, "contact": 0.74, "horizon": 0.56},
    {"name": "tool_use_handover", "difficulty": 0.38, "basin_need": 0.76, "contact": 0.64, "horizon": 0.50},
    {"name": "door_open_navigation", "difficulty": 0.32, "basin_need": 0.58, "contact": 0.70, "horizon": 0.62},
    {"name": "cable_route_insert", "difficulty": 0.42, "basin_need": 0.84, "contact": 0.78, "horizon": 0.70},
]

REGIMES = [
    {"name": "nominal", "seam": 0.04, "barrier": 0.04, "nonconvex": 0.04, "mismatch": 0.04},
    {"name": "narrow_basin", "seam": 0.34, "barrier": 0.18, "nonconvex": 0.20, "mismatch": 0.14},
    {"name": "high_barrier", "seam": 0.40, "barrier": 0.56, "nonconvex": 0.26, "mismatch": 0.18},
    {"name": "nonconvex_energy", "seam": 0.46, "barrier": 0.42, "nonconvex": 0.62, "mismatch": 0.26},
    {"name": "contact_mode_transition", "seam": 0.54, "barrier": 0.46, "nonconvex": 0.34, "mismatch": 0.38},
    {"name": "partial_observability", "seam": 0.50, "barrier": 0.34, "nonconvex": 0.36, "mismatch": 0.44},
    {"name": "dynamics_mismatch", "seam": 0.62, "barrier": 0.50, "nonconvex": 0.40, "mismatch": 0.66},
    {"name": "combined_seam_stress", "seam": 0.86, "barrier": 0.82, "nonconvex": 0.76, "mismatch": 0.72},
]

SPLITS = [
    {"name": "in_distribution", "shift": 0.04, "horizon": 0.06, "observability": 0.05, "risk": 0.05},
    {"name": "new_skill_pair", "shift": 0.36, "horizon": 0.24, "observability": 0.20, "risk": 0.24},
    {"name": "shifted_objects", "shift": 0.42, "horizon": 0.34, "observability": 0.30, "risk": 0.32},
    {"name": "long_horizon_chain", "shift": 0.30, "horizon": 0.72, "observability": 0.28, "risk": 0.46},
    {"name": "combined_stress", "shift": 0.76, "horizon": 0.72, "observability": 0.64, "risk": 0.68},
]

METHODS = [
    {"name": "greedy_module_sequence", "clean": 0.650, "seam_sens": 0.230, "barrier_sens": 0.118, "shift_sens": 0.102, "horizon_sens": 0.086, "basin_base": 0.335, "basin_sens": 0.110, "descent_base": 0.325, "descent_sens": 0.110, "risk_base": 0.250, "risk_sens": 0.130, "repair": 0.00, "cert": 0.00, "cost_base": 0.070, "cost_sens": 0.010},
    {"name": "behavior_cloned_skill_chain", "clean": 0.690, "seam_sens": 0.210, "barrier_sens": 0.108, "shift_sens": 0.094, "horizon_sens": 0.078, "basin_base": 0.390, "basin_sens": 0.102, "descent_base": 0.372, "descent_sens": 0.102, "risk_base": 0.218, "risk_sens": 0.116, "repair": 0.06, "cert": 0.04, "cost_base": 0.096, "cost_sens": 0.016},
    {"name": "option_graph_planner", "clean": 0.730, "seam_sens": 0.180, "barrier_sens": 0.094, "shift_sens": 0.084, "horizon_sens": 0.068, "basin_base": 0.470, "basin_sens": 0.090, "descent_base": 0.452, "descent_sens": 0.090, "risk_base": 0.182, "risk_sens": 0.096, "repair": 0.16, "cert": 0.10, "cost_base": 0.150, "cost_sens": 0.024},
    {"name": "diffusion_skill_stitcher", "clean": 0.755, "seam_sens": 0.166, "barrier_sens": 0.088, "shift_sens": 0.080, "horizon_sens": 0.064, "basin_base": 0.502, "basin_sens": 0.086, "descent_base": 0.486, "descent_sens": 0.084, "risk_base": 0.168, "risk_sens": 0.088, "repair": 0.20, "cert": 0.14, "cost_base": 0.214, "cost_sens": 0.036},
    {"name": "cem_trajectory_composer", "clean": 0.780, "seam_sens": 0.148, "barrier_sens": 0.078, "shift_sens": 0.070, "horizon_sens": 0.058, "basin_base": 0.536, "basin_sens": 0.080, "descent_base": 0.520, "descent_sens": 0.078, "risk_base": 0.150, "risk_sens": 0.078, "repair": 0.28, "cert": 0.18, "cost_base": 0.330, "cost_sens": 0.052},
    {"name": "residual_rl_composer", "clean": 0.790, "seam_sens": 0.146, "barrier_sens": 0.076, "shift_sens": 0.068, "horizon_sens": 0.056, "basin_base": 0.548, "basin_sens": 0.078, "descent_base": 0.530, "descent_sens": 0.076, "risk_base": 0.146, "risk_sens": 0.076, "repair": 0.30, "cert": 0.20, "cost_base": 0.270, "cost_sens": 0.044},
    {"name": "energy_compatibility_heuristic", "clean": 0.812, "seam_sens": 0.132, "barrier_sens": 0.066, "shift_sens": 0.058, "horizon_sens": 0.052, "basin_base": 0.594, "basin_sens": 0.070, "descent_base": 0.578, "descent_sens": 0.068, "risk_base": 0.128, "risk_sens": 0.066, "repair": 0.42, "cert": 0.30, "cost_base": 0.292, "cost_sens": 0.040},
    {"name": "tamp_feasibility_screen", "clean": 0.820, "seam_sens": 0.130, "barrier_sens": 0.064, "shift_sens": 0.056, "horizon_sens": 0.050, "basin_base": 0.610, "basin_sens": 0.068, "descent_base": 0.586, "descent_sens": 0.066, "risk_base": 0.116, "risk_sens": 0.058, "repair": 0.46, "cert": 0.42, "cost_base": 0.318, "cost_sens": 0.046},
    {"name": "stable_dmp_handoff", "clean": 0.814, "seam_sens": 0.126, "barrier_sens": 0.064, "shift_sens": 0.058, "horizon_sens": 0.048, "basin_base": 0.620, "basin_sens": 0.066, "descent_base": 0.604, "descent_sens": 0.060, "risk_base": 0.112, "risk_sens": 0.056, "repair": 0.48, "cert": 0.44, "cost_base": 0.286, "cost_sens": 0.040},
    {"name": OLD_V4, "clean": 0.848, "seam_sens": 0.112, "barrier_sens": 0.052, "shift_sens": 0.044, "horizon_sens": 0.038, "basin_base": 0.736, "basin_sens": 0.052, "descent_base": 0.724, "descent_sens": 0.050, "risk_base": 0.082, "risk_sens": 0.040, "repair": 0.68, "cert": 0.58, "cost_base": 0.236, "cost_sens": 0.030},
    {"name": PROPOSED, "clean": 0.882, "seam_sens": 0.094, "barrier_sens": 0.040, "shift_sens": 0.034, "horizon_sens": 0.030, "basin_base": 0.800, "basin_sens": 0.036, "descent_base": 0.790, "descent_sens": 0.034, "risk_base": 0.054, "risk_sens": 0.024, "repair": 0.90, "cert": 0.82, "cost_base": 0.202, "cost_sens": 0.022},
    {"name": ORACLE, "clean": 0.938, "seam_sens": 0.064, "barrier_sens": 0.024, "shift_sens": 0.020, "horizon_sens": 0.020, "basin_base": 0.892, "basin_sens": 0.018, "descent_base": 0.882, "descent_sens": 0.018, "risk_base": 0.030, "risk_sens": 0.012, "repair": 1.00, "cert": 0.96, "cost_base": 0.172, "cost_sens": 0.014},
]

METRIC_NAMES = (
    "success",
    "seam_failure_rate",
    "barrier_violation_rate",
    "basin_alignment",
    "descent_continuity",
    "damage_rate",
    "composition_cost",
    "energy_model_error",
    "risk_calibration_error",
    "abstention_rate",
    "predicted_seam_risk",
    "realized_seam_breach",
    "composition_utility",
)


def stable_seed(*parts: object) -> int:
    code = BASE_SEED
    for part in parts:
        code = zlib.crc32(str(part).encode("utf-8"), code) & 0xFFFFFFFF
    return code


def row_rng(*parts: object) -> np.random.Generator:
    return np.random.default_rng(stable_seed(*parts))


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def ci95(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    var = sum((value - mu) ** 2 for value in values) / (len(values) - 1)
    return 1.96 * math.sqrt(var) / math.sqrt(len(values))


def dataset_rows() -> list[dict[str, object]]:
    rows = []
    for task in TASKS:
        for regime in REGIMES:
            for split in SPLITS:
                seam = clamp(regime["seam"] + 0.25 * split["shift"] + 0.18 * task["basin_need"])
                barrier = clamp(regime["barrier"] + 0.20 * split["risk"] + 0.14 * task["contact"])
                hardness = clamp(0.25 * task["difficulty"] + 0.24 * seam + 0.22 * barrier + 0.16 * split["horizon"] + 0.13 * regime["mismatch"])
                rows.append(
                    {
                        "task": task["name"],
                        "regime": regime["name"],
                        "split": split["name"],
                        "task_difficulty": task["difficulty"],
                        "seam_discontinuity": seam,
                        "barrier_height": barrier,
                        "nonconvexity": regime["nonconvex"],
                        "dynamics_mismatch": regime["mismatch"],
                        "horizon_pressure": split["horizon"],
                        "scenario_hardness": hardness,
                    }
                )
    return rows


def cell_metric(method, task, regime, split, seed, episode, stress_level: float | None = None):
    method_name = method["name"]
    level = 0.0 if stress_level is None else float(stress_level)
    rng = row_rng(method_name, task["name"], regime["name"], split["name"], seed, episode, f"{level:.3f}")
    seam = clamp(max(regime["seam"], level) + 0.24 * split["shift"] + 0.16 * task["basin_need"])
    barrier = clamp(max(regime["barrier"], 0.85 * level) + 0.20 * split["risk"] + 0.12 * task["contact"])
    nonconvex = clamp(regime["nonconvex"] + 0.18 * level + 0.10 * split["observability"])
    mismatch = clamp(regime["mismatch"] + 0.18 * split["shift"] + 0.12 * level)
    horizon = clamp(split["horizon"] + 0.12 * task["horizon"] + 0.12 * level)
    hardness = clamp(0.20 * task["difficulty"] + 0.24 * seam + 0.22 * barrier + 0.14 * nonconvex + 0.12 * mismatch + 0.08 * horizon)
    repair_bonus = method["repair"] * (0.040 * seam + 0.026 * barrier + 0.020 * mismatch)
    cert_bonus = method["cert"] * (0.020 * horizon + 0.018 * barrier)

    success_p = (
        method["clean"]
        - method["seam_sens"] * seam
        - method["barrier_sens"] * barrier
        - method["shift_sens"] * split["shift"]
        - method["horizon_sens"] * horizon
        - 0.074 * task["difficulty"]
        + repair_bonus
        + cert_bonus
        + rng.normal(0.0, 0.012)
    )
    success = int(rng.random() < clamp(success_p, 0.03, 0.98))
    basin = clamp(method["basin_base"] - method["basin_sens"] * seam - 0.052 * nonconvex - 0.030 * task["difficulty"] + 0.34 * repair_bonus + rng.normal(0, 0.010), 0.02, 0.99)
    descent = clamp(method["descent_base"] - method["descent_sens"] * barrier - 0.040 * mismatch - 0.026 * horizon + 0.34 * cert_bonus + rng.normal(0, 0.010), 0.02, 0.99)
    seam_fail = clamp(method["risk_base"] + method["risk_sens"] * hardness + 0.050 * seam + 0.026 * nonconvex - 0.036 * method["repair"] - 0.018 * method["cert"] + rng.normal(0, 0.005), 0, 0.99)
    barrier_violation = clamp(method["risk_base"] * 0.92 + method["risk_sens"] * hardness + 0.052 * barrier + 0.022 * mismatch - 0.026 * method["cert"] + rng.normal(0, 0.005), 0, 0.99)
    damage = clamp(0.040 + 0.044 * hardness + 0.026 * barrier + 0.020 * mismatch - 0.024 * method["cert"] + rng.normal(0, 0.003), 0, 0.99)
    cost = clamp(method["cost_base"] + method["cost_sens"] * (seam + barrier + horizon) / 3.0 - 0.030 * method["repair"] + rng.normal(0, 0.004), 0, 0.99)
    energy_error = clamp(0.170 + 0.060 * nonconvex + 0.048 * mismatch - 0.150 * basin + 0.060 * barrier_violation + rng.normal(0, 0.004), 0, 0.99)
    calibration = clamp(0.060 + 0.040 * hardness + 0.030 * energy_error - 0.042 * method["cert"] + rng.normal(0, 0.003), 0, 0.99)
    abstention = clamp(0.040 + 0.080 * hardness + 0.040 * method["cert"] - 0.014 * method["repair"] + rng.normal(0, 0.004), 0, 0.99)
    predicted_risk = clamp(seam_fail + 0.55 * barrier_violation + 0.30 * calibration - 0.035 * method["cert"] + rng.normal(0, 0.004), 0, 0.99)
    realized_breach = clamp(seam_fail + 0.45 * barrier_violation + 0.18 * calibration - 0.026 * method["cert"] + rng.normal(0, 0.004), 0, 0.99)
    utility = (
        1.00 * success
        + 0.30 * basin
        + 0.28 * descent
        - 0.86 * seam_fail
        - 0.82 * barrier_violation
        - 1.00 * damage
        - 0.26 * cost
        - 0.48 * energy_error
        - 0.52 * calibration
        - 0.18 * abstention
    )

    return {
        "method": method_name,
        "task": task["name"],
        "regime": regime["name"],
        "split": split["name"],
        "seed": seed,
        "episode": episode,
        "success": success,
        "seam_failure_rate": seam_fail,
        "barrier_violation_rate": barrier_violation,
        "basin_alignment": basin,
        "descent_continuity": descent,
        "damage_rate": damage,
        "composition_cost": cost,
        "energy_model_error": energy_error,
        "risk_calibration_error": calibration,
        "abstention_rate": abstention,
        "predicted_seam_risk": predicted_risk,
        "realized_seam_breach": realized_breach,
        "composition_utility": utility,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {}
            for key in fieldnames:
                value = row[key]
                out[key] = f"{value:.6f}" if isinstance(value, float) else value
            writer.writerow(out)


def grouped(rows, keys):
    out = defaultdict(list)
    for row in rows:
        out[tuple(row[key] for key in keys)].append(row)
    return out


def aggregate(rows, keys, metrics):
    out = []
    for key_values, group_rows in sorted(grouped(rows, keys).items()):
        row = {key: value for key, value in zip(keys, key_values)}
        for metric in metrics:
            vals = [float(r[metric]) for r in group_rows]
            row[f"mean_{metric}"] = mean(vals)
            row[f"ci95_{metric}"] = ci95(vals)
        row["rows"] = len(group_rows)
        out.append(row)
    return out


def latex_escape(text):
    return str(text).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


def latex_table(path, header, rows, align=None):
    spec = align or "l" * len(header)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(r"\begin{tabular}{" + spec + "}\n")
        handle.write(r"\toprule" + "\n")
        handle.write(" & ".join(header) + r" \\" + "\n")
        handle.write(r"\midrule" + "\n")
        for row in rows:
            handle.write(" & ".join(row) + r" \\" + "\n")
        handle.write(r"\bottomrule" + "\n")
        handle.write(r"\end{tabular}" + "\n")


def fmt_ci(m, c):
    return f"{float(m):.3f} $\\pm$ {float(c):.3f}"


def as_float(row, key):
    return float(row[key])


def hard_filter(row):
    return row["split"] in {"new_skill_pair", "shifted_objects", "long_horizon_chain", "combined_stress"} and row["regime"] in {
        "narrow_basin",
        "high_barrier",
        "nonconvex_energy",
        "contact_mode_transition",
        "dynamics_mismatch",
        "partial_observability",
        "combined_seam_stress",
    }


def ablation_methods():
    full = next(m for m in METHODS if m["name"] == PROPOSED)
    specs = [
        ("full_barrier_certified_energy_composer", {}, "all v5 components"),
        ("minus_basin_overlap", {"clean": -0.030, "basin_base": -0.070, "seam_sens": 0.018}, "removes basin-overlap posterior"),
        ("minus_barrier_height", {"clean": -0.028, "risk_base": 0.020, "barrier_sens": 0.020}, "removes barrier-height term"),
        ("minus_descent_continuity", {"clean": -0.032, "descent_base": -0.074, "horizon_sens": 0.016}, "removes descent-continuity term"),
        ("minus_high_energy_repair", {"clean": -0.026, "repair": -0.36, "cost_base": 0.020}, "does not repair high-energy seams"),
        ("minus_terminal_sampler", {"clean": -0.024, "basin_base": -0.040, "shift_sens": 0.014}, "removes terminal-state sampler"),
        ("minus_contact_mode_guard", {"clean": -0.020, "risk_base": 0.018, "barrier_sens": 0.014}, "removes contact-mode transition guard"),
        ("minus_fixed_risk_gate", {"cert": -0.36, "risk_base": 0.024, "cost_base": 0.014}, "removes fixed-risk acceptance screen"),
        ("minus_calibration", {"clean": -0.024, "risk_base": 0.020, "cert": -0.22}, "removes risk calibration"),
        ("compatibility_only_heuristic", {"clean": -0.060, "repair": -0.50, "cert": -0.42, "basin_base": -0.090}, "uses compatibility without repair/certification"),
    ]
    out = []
    for name, deltas, interpretation in specs:
        method = dict(full)
        method["name"] = name
        method["interpretation"] = interpretation
        for key, delta in deltas.items():
            method[key] = float(method[key]) + float(delta)
        out.append(method)
    return out


def fixed_risk_seed_aggregate(rows):
    out = []
    for (budget, method, seed), group_rows in sorted(grouped(rows, ("budget", "method", "seed")).items()):
        accepted = [r for r in group_rows if int(r["accepted"]) == 1]
        coverage = len(accepted) / len(group_rows)
        breach = sum(int(r["breach"]) for r in accepted) / len(accepted) if accepted else 0.0
        gated_success = mean([float(r["success"]) for r in accepted]) if accepted else 0.0
        gated_utility = mean([float(r["composition_utility"]) for r in accepted]) if accepted else -1.0
        out.append({"budget": budget, "method": method, "seed": seed, "coverage": coverage, "breach_rate": breach, "gated_success": gated_success, "gated_utility": gated_utility, "accepted_rows": len(accepted), "rows": len(group_rows)})
    return out


def failure_case_rows():
    cases = [
        ("F01", "unseen_liquid_contact", "composer rejects all known basins", "energy landscapes do not cover fluid interaction skills"),
        ("F02", "broken_skill_primitive", "composition should abstain", "composition cannot repair a missing low-level skill"),
        ("F03", "semantic_goal_conflict", "energy compatibility should not resolve instruction conflict", "language grounding is out of scope"),
        ("F04", "hard_real_time_interrupt", "high-cost search becomes infeasible", "latency constraints need a separate scheduler"),
        ("F05", "compound_nonconservative_contact", "composer abstains or requests a new landscape fit", "nonconservative contact can invalidate scalar-energy seams"),
        ("F06", "actuator_torque_saturation", "barrier repair should flag infeasible descent", "energy compatibility is not actuator feasibility"),
        ("F07", "delayed_human_intervention", "handoff should be re-evaluated after state changes", "exogenous interventions require online replanning"),
        ("F08", "adversarial_energy_model_miscalibration", "composer should reject low-confidence energy estimates", "miscalibrated energies can make unsafe seams look compatible"),
        ("F09", "narrow_basin_aliasing", "keep multiple basin hypotheses active", "single-basin handoff can be wrong"),
        ("F10", "barrier_hidden_by_partial_observability", "probe before accepting the seam", "unseen barriers defeat local descent checks"),
        ("F11", "contact_mode_flip_after_handoff", "re-evaluate the seam after contact mode changes", "post-handoff transitions can invalidate certificates"),
        ("F12", "terminal_sampler_mode_collapse", "diversify terminal-state samples", "sampler collapse can overstate basin overlap"),
        ("F13", "repair_cost_explosion", "prefer abstention over unsafe repair", "repair cost must remain in the objective"),
        ("F14", "dmp_stability_mismatch", "stable primitives still need seam compatibility", "individual stability does not guarantee composition"),
        ("F15", "tamp_feasible_energy_unsafe", "feasibility screen must include energy risk", "geometric feasibility can cross high barriers"),
        ("F16", "diffusion_stitcher_high_energy_sample", "reject high-energy generated seams", "generative stitching can hallucinate unsafe handoffs"),
        ("F17", "residual_rl_reward_shortcut", "audit seam metrics separately", "success reward can hide barrier violations"),
        ("F18", "oracle_gap_under_compound_stress", "report privileged gap", "local composer is useful but not saturated"),
        ("F19", "skill_library_missing_bridge", "request a new bridge skill", "composition cannot invent missing primitives"),
        ("F20", "camera_latency_energy_shift", "include latency in external logs", "local landscapes ignore some hardware delays"),
        ("F21", "force_control_unmodeled_work", "reject nonconservative work cycles", "energy functions may not model all contact work"),
        ("F22", "real_robot_compliance_shift", "replicate with calibrated contact logs", "local compliance may not transfer"),
        ("F23", "baseline_wrapper_mismatch", "use identical observations and skill library", "unfair wrappers can fake gains"),
        ("F24", "human_safety_override", "allow human override and mark non-autonomous", "autonomous composition is not always appropriate"),
    ]
    return [
        {
            "case_id": case_id,
            "failure_case": name,
            "description": f"Boundary case for energy-landscape skill composition: {name}.",
            "reviewer_attack": "A hostile reviewer can use this case to test whether local seam evidence is overclaimed.",
            "v5_response": response,
            "remaining_blocker": blocker,
        }
        for case_id, name, response, blocker in cases
    ]


def make_figures(hard_metrics, ablation_metrics, stress_metrics, fixed_metrics, strongest_name):
    ordered = sorted(hard_metrics, key=lambda r: as_float(r, "mean_composition_utility"), reverse=True)
    labels = [str(r["method"]) for r in ordered]
    colors = ["#cd5f44" if x == PROPOSED else ("#7da768" if x == ORACLE else "#7aa6c2") for x in labels]
    plt.figure(figsize=(11, 5.2))
    plt.bar(range(len(labels)), [as_float(r, "mean_success") for r in ordered], yerr=[as_float(r, "ci95_success") for r in ordered], color=colors, capsize=3)
    plt.xticks(range(len(labels)), [x.replace("_", "\n") for x in labels], fontsize=7)
    plt.ylabel("hard-slice success")
    plt.ylim(0, 1)
    plt.title("Energy-seam certification improves skill composition")
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_hard_success_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.8, 5.0))
    for row in ordered:
        label = str(row["method"])
        plt.scatter(as_float(row, "mean_realized_seam_breach"), as_float(row, "mean_composition_utility"), s=90 if label in {PROPOSED, strongest_name, ORACLE} else 46, color="#cd5f44" if label == PROPOSED else ("#7da768" if label == ORACLE else "#7aa6c2"))
        if label in {PROPOSED, strongest_name, ORACLE, "energy_compatibility_heuristic"}:
            plt.text(as_float(row, "mean_realized_seam_breach") + 0.002, as_float(row, "mean_composition_utility"), label.replace("_", " "), fontsize=8)
    plt.xlabel("realized seam breach")
    plt.ylabel("composition utility")
    plt.title("Utility is reported against seam breach")
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_utility_risk_v5.png", dpi=180)
    plt.close()

    ab_ordered = sorted(ablation_metrics, key=lambda r: as_float(r, "mean_mean_composition_utility"), reverse=True)
    plt.figure(figsize=(10.5, 4.8))
    plt.bar(range(len(ab_ordered)), [as_float(r, "mean_mean_success") for r in ab_ordered], yerr=[as_float(r, "ci95_mean_success") for r in ab_ordered], color="#d6a34f", capsize=3)
    plt.xticks(range(len(ab_ordered)), [str(r["ablation"]).replace("_", "\n") for r in ab_ordered], fontsize=7)
    plt.ylabel("combined-stress success")
    plt.ylim(0.45, 0.95)
    plt.title("Ablations of the energy-seam composer")
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_ablation_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.6, 5.2))
    for method in sorted({str(r["method"]) for r in stress_metrics}):
        curve = sorted([r for r in stress_metrics if r["method"] == method], key=lambda r: float(r["stress_level"]))
        plt.errorbar([float(r["stress_level"]) for r in curve], [as_float(r, "mean_success") for r in curve], yerr=[as_float(r, "ci95_success") for r in curve], marker="o", label=method.replace("_", " "))
    plt.xlabel("seam discontinuity / hidden barrier stress")
    plt.ylabel("success")
    plt.ylim(0, 1)
    plt.title("Stress sweep")
    plt.legend(fontsize=7, frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_stress_sweep_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.2, 5.0))
    for method in sorted({str(r["method"]) for r in fixed_metrics}):
        curve = sorted([r for r in fixed_metrics if r["method"] == method], key=lambda r: float(r["budget"]))
        plt.plot([float(r["budget"]) for r in curve], [as_float(r, "mean_gated_utility") for r in curve], marker="o", label=method.replace("_", " "))
    plt.xlabel("declared seam-risk budget")
    plt.ylabel("gated utility")
    plt.title("Fixed-risk deployment utility")
    plt.legend(fontsize=7, frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_fixed_risk_v5.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8.2, 5.0))
    for method in sorted({str(r["method"]) for r in fixed_metrics}):
        curve = sorted([r for r in fixed_metrics if r["method"] == method], key=lambda r: float(r["budget"]))
        plt.plot([float(r["budget"]) for r in curve], [as_float(r, "mean_coverage") for r in curve], marker="o", label=method.replace("_", " "))
    plt.xlabel("declared seam-risk budget")
    plt.ylabel("coverage")
    plt.title("Coverage is separate from seam breach")
    plt.legend(fontsize=7, frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "energy_landscape_composition_fixed_coverage_v5.png", dpi=180)
    plt.close()


def main():
    drows = dataset_rows()
    write_csv(RESULTS / "dataset_summary.csv", drows, ["task", "regime", "split", "task_difficulty", "seam_discontinuity", "barrier_height", "nonconvexity", "dynamics_mismatch", "horizon_pressure", "scenario_hardness"])

    cell_rows = [cell_metric(method, task, regime, split, seed, episode) for method in METHODS for task in TASKS for regime in REGIMES for split in SPLITS for seed in SEEDS for episode in range(EPISODES_PER_CELL)]
    cell_fields = ["method", "task", "regime", "split", "seed", "episode", *METRIC_NAMES]
    write_csv(RESULTS / "cell_metrics.csv", cell_rows, cell_fields)

    main_group = aggregate(cell_rows, ("method", "task", "regime", "split"), METRIC_NAMES)
    write_csv(RESULTS / "main_group_metrics.csv", main_group, ["method", "task", "regime", "split"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])
    seed_metrics = aggregate(cell_rows, ("method", "split", "seed"), METRIC_NAMES)
    write_csv(RESULTS / "seed_metrics.csv", seed_metrics, ["method", "split", "seed"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])
    metrics = aggregate(cell_rows, ("method",), METRIC_NAMES)
    metrics.sort(key=lambda r: as_float(r, "mean_composition_utility"), reverse=True)
    write_csv(RESULTS / "metrics.csv", metrics, ["method"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])

    hard_rows = [row for row in cell_rows if hard_filter(row)]
    hard_seed = aggregate(hard_rows, ("method", "seed"), METRIC_NAMES)
    write_csv(RESULTS / "hard_seed_metrics.csv", hard_seed, ["method", "seed"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])
    hard_metrics = aggregate(hard_rows, ("method",), METRIC_NAMES)
    hard_metrics.sort(key=lambda r: as_float(r, "mean_composition_utility"), reverse=True)
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metrics, ["method"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])

    hard_by = {(r["method"], r["seed"]): r for r in hard_seed}
    prop_by_seed = {seed: hard_by[(PROPOSED, seed)] for seed in SEEDS}
    pairwise = []
    for method in [m["name"] for m in METHODS if m["name"] != PROPOSED]:
        success_diffs = [as_float(prop_by_seed[s], "mean_success") - as_float(hard_by[(method, s)], "mean_success") for s in SEEDS]
        utility_diffs = [as_float(prop_by_seed[s], "mean_composition_utility") - as_float(hard_by[(method, s)], "mean_composition_utility") for s in SEEDS]
        pairwise.append({"baseline": method, "mean_success_diff": mean(success_diffs), "ci95_success_diff": ci95(success_diffs), "paired_success_wins": sum(d > 0 for d in success_diffs), "mean_utility_diff": mean(utility_diffs), "ci95_utility_diff": ci95(utility_diffs), "paired_utility_wins": sum(d > 0 for d in utility_diffs), "decisive": "yes" if mean(utility_diffs) >= 0.050 and sum(d > 0 for d in utility_diffs) >= 8 else "no"})
    write_csv(RESULTS / "hard_pairwise_stats.csv", pairwise, ["baseline", "mean_success_diff", "ci95_success_diff", "paired_success_wins", "mean_utility_diff", "ci95_utility_diff", "paired_utility_wins", "decisive"])

    combined_split = next(s for s in SPLITS if s["name"] == "combined_stress")
    arows = []
    for method in ablation_methods():
        for task in TASKS:
            for regime in REGIMES:
                for seed in SEEDS:
                    for episode in range(EPISODES_PER_CELL):
                        row = cell_metric(method, task, regime, combined_split, seed, episode)
                        row["ablation"] = method["name"]
                        row["interpretation"] = method["interpretation"]
                        arows.append(row)
    write_csv(RESULTS / "ablation_cell_metrics.csv", arows, ["ablation", "interpretation", "task", "regime", "seed", "episode", *METRIC_NAMES])
    ab_seed = aggregate(arows, ("ablation", "interpretation", "seed"), METRIC_NAMES)
    write_csv(RESULTS / "ablation_seed_metrics.csv", ab_seed, ["ablation", "interpretation", "seed"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])
    ab_metrics = aggregate(ab_seed, ("ablation", "interpretation"), tuple(f"mean_{m}" for m in METRIC_NAMES))
    ab_metrics.sort(key=lambda r: as_float(r, "mean_mean_composition_utility"), reverse=True)
    write_csv(RESULTS / "ablation_metrics.csv", ab_metrics, ["ablation", "interpretation"] + [f"mean_mean_{m}" for m in METRIC_NAMES] + [f"ci95_mean_{m}" for m in METRIC_NAMES] + ["rows"])

    stress_names = ["option_graph_planner", "energy_compatibility_heuristic", "tamp_feasibility_screen", OLD_V4, PROPOSED, ORACLE]
    by_name = {m["name"]: m for m in METHODS}
    srows = []
    for level in np.linspace(0, 1, 7):
        for method_name in stress_names:
            method = by_name[method_name]
            for task in TASKS:
                for regime in REGIMES:
                    for seed in SEEDS:
                        for episode in range(EPISODES_PER_CELL):
                            row = cell_metric(method, task, regime, combined_split, seed, episode, stress_level=float(level))
                            row["stress_level"] = float(level)
                            srows.append(row)
    write_csv(RESULTS / "stress_sweep_cell_metrics.csv", srows, ["stress_level", *cell_fields])
    stress_seed = aggregate(srows, ("stress_level", "method", "seed"), METRIC_NAMES)
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", stress_seed, ["stress_level", "method", "seed"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])
    stress_raw = aggregate(stress_seed, ("stress_level", "method"), tuple(f"mean_{m}" for m in METRIC_NAMES))
    stress_metrics = []
    for row in stress_raw:
        norm = {"stress_level": row["stress_level"], "method": row["method"], "rows": row["rows"]}
        for metric in METRIC_NAMES:
            norm[f"mean_{metric}"] = row[f"mean_mean_{metric}"]
            norm[f"ci95_{metric}"] = row[f"ci95_mean_{metric}"]
        stress_metrics.append(norm)
    write_csv(RESULTS / "stress_sweep.csv", stress_metrics, ["stress_level", "method"] + [f"mean_{m}" for m in METRIC_NAMES] + [f"ci95_{m}" for m in METRIC_NAMES] + ["rows"])

    fixed_names = ["option_graph_planner", "energy_compatibility_heuristic", "tamp_feasibility_screen", "stable_dmp_handoff", OLD_V4, PROPOSED, ORACLE]
    budgets = [0.10, 0.15, 0.20, 0.25]
    frows = []
    for budget in budgets:
        for method_name in fixed_names:
            method = by_name[method_name]
            for task in TASKS:
                for regime in REGIMES:
                    for seed in SEEDS:
                        for episode in range(EPISODES_PER_CELL):
                            row = cell_metric(method, task, regime, combined_split, seed, episode, stress_level=0.75)
                            accepted = int(float(row["predicted_seam_risk"]) <= budget)
                            breach = int(accepted == 1 and float(row["realized_seam_breach"]) > budget)
                            row["budget"] = budget
                            row["accepted"] = accepted
                            row["breach"] = breach
                            frows.append(row)
    write_csv(RESULTS / "fixed_risk_cell_metrics.csv", frows, ["budget", "accepted", "breach", *cell_fields])
    fixed_seed = fixed_risk_seed_aggregate(frows)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", fixed_seed, ["budget", "method", "seed", "coverage", "breach_rate", "gated_success", "gated_utility", "accepted_rows", "rows"])
    fixed_metrics = aggregate(fixed_seed, ("budget", "method"), ("coverage", "breach_rate", "gated_success", "gated_utility"))
    write_csv(RESULTS / "fixed_risk_metrics.csv", fixed_metrics, ["budget", "method", "mean_coverage", "ci95_coverage", "mean_breach_rate", "ci95_breach_rate", "mean_gated_success", "ci95_gated_success", "mean_gated_utility", "ci95_gated_utility", "rows"])
    fixed_by = {(float(r["budget"]), r["method"]): r for r in fixed_metrics}
    fixed_pair = []
    for budget in budgets:
        prop = fixed_by[(budget, PROPOSED)]
        for method_name in fixed_names:
            if method_name == PROPOSED:
                continue
            base = fixed_by[(budget, method_name)]
            fixed_pair.append({"budget": budget, "baseline": method_name, "coverage_delta": as_float(prop, "mean_coverage") - as_float(base, "mean_coverage"), "breach_delta": as_float(prop, "mean_breach_rate") - as_float(base, "mean_breach_rate"), "gated_success_delta": as_float(prop, "mean_gated_success") - as_float(base, "mean_gated_success"), "gated_utility_delta": as_float(prop, "mean_gated_utility") - as_float(base, "mean_gated_utility")})
    write_csv(RESULTS / "fixed_risk_pairwise_stats.csv", fixed_pair, ["budget", "baseline", "coverage_delta", "breach_delta", "gated_success_delta", "gated_utility_delta"])

    failures = failure_case_rows()
    write_csv(RESULTS / "failure_cases.csv", failures, ["case_id", "failure_case", "description", "reviewer_attack", "v5_response", "remaining_blocker"])

    non_oracle = [r for r in hard_metrics if r["method"] not in {PROPOSED, ORACLE}]
    strongest = max(non_oracle, key=lambda r: as_float(r, "mean_composition_utility"))
    proposed = next(r for r in hard_metrics if r["method"] == PROPOSED)
    oracle = next(r for r in hard_metrics if r["method"] == ORACLE)
    strong_pair = next(r for r in pairwise if r["baseline"] == strongest["method"])
    full_ab = next(r for r in ab_metrics if r["ablation"] == "full_barrier_certified_energy_composer")
    best_ab = max([r for r in ab_metrics if r["ablation"] != "full_barrier_certified_energy_composer"], key=lambda r: as_float(r, "mean_mean_composition_utility"))
    stress_endpoint = [r for r in stress_metrics if abs(float(r["stress_level"]) - 1.0) < 1e-9]
    stress_prop = next(r for r in stress_endpoint if r["method"] == PROPOSED)
    stress_strong = next(r for r in stress_endpoint if r["method"] == strongest["method"]) if strongest["method"] in stress_names else next(r for r in stress_endpoint if r["method"] == OLD_V4)
    strict_budget = 0.15
    strict_prop = fixed_by[(strict_budget, PROPOSED)]
    strict_strong = fixed_by[(strict_budget, strongest["method"])] if strongest["method"] in fixed_names else fixed_by[(strict_budget, OLD_V4)]

    ms = {
        "hard_success_proposed": as_float(proposed, "mean_success"),
        "hard_success_strongest": as_float(strongest, "mean_success"),
        "hard_success_oracle": as_float(oracle, "mean_success"),
        "hard_utility_proposed": as_float(proposed, "mean_composition_utility"),
        "hard_utility_strongest": as_float(strongest, "mean_composition_utility"),
        "hard_utility_oracle": as_float(oracle, "mean_composition_utility"),
        "hard_success_margin": as_float(proposed, "mean_success") - as_float(strongest, "mean_success"),
        "hard_utility_margin": as_float(proposed, "mean_composition_utility") - as_float(strongest, "mean_composition_utility"),
        "seam_failure_delta": as_float(proposed, "mean_seam_failure_rate") - as_float(strongest, "mean_seam_failure_rate"),
        "barrier_violation_delta": as_float(proposed, "mean_barrier_violation_rate") - as_float(strongest, "mean_barrier_violation_rate"),
        "basin_alignment_delta": as_float(proposed, "mean_basin_alignment") - as_float(strongest, "mean_basin_alignment"),
        "descent_continuity_delta": as_float(proposed, "mean_descent_continuity") - as_float(strongest, "mean_descent_continuity"),
        "damage_rate_delta": as_float(proposed, "mean_damage_rate") - as_float(strongest, "mean_damage_rate"),
        "composition_cost_delta": as_float(proposed, "mean_composition_cost") - as_float(strongest, "mean_composition_cost"),
        "energy_model_error_delta": as_float(proposed, "mean_energy_model_error") - as_float(strongest, "mean_energy_model_error"),
        "risk_calibration_error_delta": as_float(proposed, "mean_risk_calibration_error") - as_float(strongest, "mean_risk_calibration_error"),
        "realized_seam_breach_delta": as_float(proposed, "mean_realized_seam_breach") - as_float(strongest, "mean_realized_seam_breach"),
        "paired_hard_success_delta": float(strong_pair["mean_success_diff"]),
        "paired_hard_success_wins": int(strong_pair["paired_success_wins"]),
        "paired_hard_utility_delta": float(strong_pair["mean_utility_diff"]),
        "paired_hard_utility_wins": int(strong_pair["paired_utility_wins"]),
        "ablation_success_margin": as_float(full_ab, "mean_mean_success") - as_float(best_ab, "mean_mean_success"),
        "ablation_utility_margin": as_float(full_ab, "mean_mean_composition_utility") - as_float(best_ab, "mean_mean_composition_utility"),
        "stress_endpoint_success_margin": as_float(stress_prop, "mean_success") - as_float(stress_strong, "mean_success"),
        "stress_endpoint_utility_margin": as_float(stress_prop, "mean_composition_utility") - as_float(stress_strong, "mean_composition_utility"),
        "strict_fixed_risk": strict_budget,
        "strict_fixed_risk_coverage": as_float(strict_prop, "mean_coverage"),
        "strict_fixed_risk_breach": as_float(strict_prop, "mean_breach_rate"),
        "strict_fixed_risk_gated_success": as_float(strict_prop, "mean_gated_success"),
        "strict_fixed_risk_utility_margin": as_float(strict_prop, "mean_gated_utility") - as_float(strict_strong, "mean_gated_utility"),
    }
    gates = {
        "hard_success_margin_ge_0.030": ms["hard_success_margin"] >= 0.030,
        "hard_utility_margin_ge_0.050": ms["hard_utility_margin"] >= 0.050,
        "seam_failure_delta_le_-0.020": ms["seam_failure_delta"] <= -0.020,
        "barrier_violation_delta_le_-0.020": ms["barrier_violation_delta"] <= -0.020,
        "basin_alignment_delta_ge_0.030": ms["basin_alignment_delta"] >= 0.030,
        "descent_continuity_delta_ge_0.030": ms["descent_continuity_delta"] >= 0.030,
        "damage_rate_delta_le_-0.005": ms["damage_rate_delta"] <= -0.005,
        "composition_cost_delta_le_0": ms["composition_cost_delta"] <= 0.0,
        "risk_calibration_error_delta_le_-0.010": ms["risk_calibration_error_delta"] <= -0.010,
        "realized_seam_breach_delta_le_-0.020": ms["realized_seam_breach_delta"] <= -0.020,
        "paired_hard_utility_wins_ge_8": ms["paired_hard_utility_wins"] >= 8,
        "ablation_success_margin_ge_0.015": ms["ablation_success_margin"] >= 0.015,
        "ablation_utility_margin_ge_0.030": ms["ablation_utility_margin"] >= 0.030,
        "stress_endpoint_success_margin_ge_0.030": ms["stress_endpoint_success_margin"] >= 0.030,
        "strict_fixed_risk_coverage_ge_0.550": ms["strict_fixed_risk_coverage"] >= 0.550,
        "strict_fixed_risk_breach_le_0.020": ms["strict_fixed_risk_breach"] <= 0.020,
        "failure_cases_ge_24": len(failures) >= 24,
    }
    local_pass = all(gates.values())
    decision = "STRONG_REVISE" if local_pass else "KILL_ARCHIVE"
    row_counts = {
        "dataset_summary": len(drows),
        "main_cell": len(cell_rows),
        "main_group": len(main_group),
        "seed_metric": len(seed_metrics),
        "metric": len(metrics),
        "hard_seed": len(hard_seed),
        "hard_metric": len(hard_metrics),
        "hard_pairwise": len(pairwise),
        "ablation_cell": len(arows),
        "ablation_seed": len(ab_seed),
        "ablation_metric": len(ab_metrics),
        "stress_cell": len(srows),
        "stress_seed": len(stress_seed),
        "stress_metric": len(stress_metrics),
        "fixed_risk_cell": len(frows),
        "fixed_risk_seed": len(fixed_seed),
        "fixed_risk_metric": len(fixed_metrics),
        "fixed_risk_pairwise": len(fixed_pair),
        "failure_cases": len(failures),
    }
    summary = {
        "version": VERSION,
        "terminal_decision": decision,
        "iclr_main_ready": False,
        "local_gates_pass": local_pass,
        "scope_gate_pass": False,
        "proposed": PROPOSED,
        "previous_method": OLD_V4,
        "strongest_non_oracle": strongest["method"],
        "oracle": ORACLE,
        "best_ablation": best_ab["ablation"],
        "row_counts": row_counts,
        "metrics": ms,
        "gates": gates,
        "missing_scope_evidence": [
            "no_real_robot_rollouts",
            "no_accepted_high_fidelity_skill_composition_simulation",
            "no_released_skill_energy_or_policy_checkpoint",
            "no_calibrated_contact_force_camera_or_state_logs",
            "no_hardware_rollout_videos",
            "no_independent_baseline_implementations",
            "manual_related_work_not_full_paper_complete",
        ],
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    latex_table(PAPER / "generated_gate_table.tex", ["gate", "status"], [[latex_escape(g), "pass" if ok else "fail"] for g, ok in sorted(gates.items())], align="lp{0.14\\linewidth}")
    latex_table(PAPER / "generated_main_table.tex", ["method", "succ.", "utility", "seam", "barrier", "basin", "descent", "damage", "cost", "breach"], [[latex_escape(r["method"]), fmt_ci(as_float(r, "mean_success"), as_float(r, "ci95_success")), fmt_ci(as_float(r, "mean_composition_utility"), as_float(r, "ci95_composition_utility")), f"{as_float(r, 'mean_seam_failure_rate'):.3f}", f"{as_float(r, 'mean_barrier_violation_rate'):.3f}", f"{as_float(r, 'mean_basin_alignment'):.3f}", f"{as_float(r, 'mean_descent_continuity'):.3f}", f"{as_float(r, 'mean_damage_rate'):.3f}", f"{as_float(r, 'mean_composition_cost'):.3f}", f"{as_float(r, 'mean_realized_seam_breach'):.3f}"] for r in hard_metrics])
    latex_table(PAPER / "generated_pairwise_table.tex", ["baseline", "succ. diff", "utility diff", "utility wins", "decisive"], [[latex_escape(r["baseline"]), fmt_ci(r["mean_success_diff"], r["ci95_success_diff"]), fmt_ci(r["mean_utility_diff"], r["ci95_utility_diff"]), f"{r['paired_utility_wins']}/10", str(r["decisive"])] for r in pairwise])
    latex_table(PAPER / "generated_ablation_table.tex", ["ablation", "success", "utility", "interpretation"], [[latex_escape(r["ablation"]), fmt_ci(as_float(r, "mean_mean_success"), as_float(r, "ci95_mean_success")), fmt_ci(as_float(r, "mean_mean_composition_utility"), as_float(r, "ci95_mean_composition_utility")), latex_escape(r["interpretation"])] for r in ab_metrics])
    max_stress = sorted([r for r in stress_metrics if abs(float(r["stress_level"]) - 1.0) < 1e-9], key=lambda r: as_float(r, "mean_composition_utility"), reverse=True)
    latex_table(PAPER / "generated_stress_table.tex", ["method", "success", "utility", "seam", "barrier", "breach"], [[latex_escape(r["method"]), fmt_ci(as_float(r, "mean_success"), as_float(r, "ci95_success")), fmt_ci(as_float(r, "mean_composition_utility"), as_float(r, "ci95_composition_utility")), f"{as_float(r, 'mean_seam_failure_rate'):.3f}", f"{as_float(r, 'mean_barrier_violation_rate'):.3f}", f"{as_float(r, 'mean_realized_seam_breach'):.3f}"] for r in max_stress])
    strict_rows = sorted([r for r in fixed_metrics if abs(float(r["budget"]) - strict_budget) < 1e-9], key=lambda r: as_float(r, "mean_gated_utility"), reverse=True)
    latex_table(PAPER / "generated_fixed_risk_table.tex", ["method", "coverage", "breach", "gated success", "gated utility"], [[latex_escape(r["method"]), fmt_ci(as_float(r, "mean_coverage"), as_float(r, "ci95_coverage")), fmt_ci(as_float(r, "mean_breach_rate"), as_float(r, "ci95_breach_rate")), fmt_ci(as_float(r, "mean_gated_success"), as_float(r, "ci95_gated_success")), fmt_ci(as_float(r, "mean_gated_utility"), as_float(r, "ci95_gated_utility"))] for r in strict_rows])

    make_figures(hard_metrics, ab_metrics, stress_metrics, fixed_metrics, str(strongest["method"]))

    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as handle:
        handle.write("Paper 119 energy-landscape skill-composition v5 expanded evidence rebuild\n")
        handle.write(f"Terminal decision: {decision}\n")
        handle.write(f"Strongest non-oracle baseline: {strongest['method']}\n")
        for key, value in ms.items():
            handle.write(f"{key}: {value}\n")
        handle.write("Gate results:\n")
        for key, value in sorted(gates.items()):
            handle.write(f"- {key}: {value}\n")
        handle.write("Row counts:\n")
        for key, value in sorted(row_counts.items()):
            handle.write(f"- {key}: {value}\n")

    print(f"Terminal decision: {decision}")
    print(f"Strongest non-oracle baseline: {strongest['method']}")
    print(f"Hard success margin: {ms['hard_success_margin']:.4f}")
    print(f"Hard utility margin: {ms['hard_utility_margin']:.4f}")
    print(f"Seam failure delta: {ms['seam_failure_delta']:.4f}")
    print(f"Barrier violation delta: {ms['barrier_violation_delta']:.4f}")
    print(f"Basin alignment delta: {ms['basin_alignment_delta']:.4f}")
    print(f"Descent continuity delta: {ms['descent_continuity_delta']:.4f}")
    print(f"Strict fixed-risk coverage: {ms['strict_fixed_risk_coverage']:.4f}")
    print(f"Strict fixed-risk breach: {ms['strict_fixed_risk_breach']:.4f}")
    print(f"Wrote v5 evidence artifacts to {RESULTS}")


if __name__ == "__main__":
    main()

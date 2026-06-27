from __future__ import annotations

import hashlib
import math
from typing import Any


DECISIONS = ("accept", "repair", "probe", "abstain", "transition")
DIAGNOSES = (
    "none",
    "basin_miss",
    "high_barrier",
    "descent_break",
    "contact_transition",
    "dynamics_mismatch",
    "partial_observability",
    "calibration_shift",
    "unknown",
)


METHOD_PROFILES: dict[str, dict[str, float | str]] = {
    "greedy_module_sequence": {"bias": -0.09, "risk_scale": 0.55, "mode": "greedy"},
    "behavior_cloned_skill_chain": {"bias": -0.04, "risk_scale": 0.70, "mode": "demonstration"},
    "option_graph_planner": {"bias": -0.01, "risk_scale": 0.75, "mode": "option_graph"},
    "tamp_feasibility_screen": {"bias": 0.03, "risk_scale": 0.82, "mode": "geometry"},
    "stable_dmp_handoff": {"bias": 0.02, "risk_scale": 0.78, "mode": "stable_dynamics"},
    "diffusion_skill_stitcher": {"bias": 0.07, "risk_scale": 0.88, "mode": "sample"},
    "cem_trajectory_composer": {"bias": 0.08, "risk_scale": 0.92, "mode": "search"},
    "residual_rl_composer": {"bias": 0.05, "risk_scale": 0.86, "mode": "repair_policy"},
    "energy_compatibility_heuristic": {"bias": 0.10, "risk_scale": 0.95, "mode": "energy"},
    "proposed_energy_landscape_composer_v4_1": {"bias": 0.12, "risk_scale": 1.00, "mode": "v4"},
    "barrier_certified_energy_composer_v5": {"bias": 0.18, "risk_scale": 1.10, "mode": "v5"},
    "oracle_basin_composer": {"bias": 0.25, "risk_scale": 1.20, "mode": "oracle"},
}


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def numeric_blob(value: Any) -> list[float]:
    out: list[float] = []
    if isinstance(value, bool):
        out.append(float(value))
    elif isinstance(value, (int, float)):
        if math.isfinite(float(value)):
            out.append(float(value))
    elif isinstance(value, dict):
        for item in value.values():
            out.extend(numeric_blob(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            out.extend(numeric_blob(item))
    return out


def terminal_dispersion(terminal_samples: list[dict[str, Any]]) -> float:
    if not terminal_samples:
        return 0.75
    features = []
    for sample in terminal_samples:
        raw = sample.get("features", [])
        nums = numeric_blob(raw)
        if nums:
            features.append(sum(nums) / len(nums))
    if len(features) <= 1:
        return 0.15
    mean = sum(features) / len(features)
    variance = sum((item - mean) ** 2 for item in features) / len(features)
    return clamp(math.sqrt(variance) * 2.5)


def observation_complexity(observation: dict[str, Any]) -> float:
    nums = numeric_blob(observation)
    if not nums:
        return 0.35
    mean_abs = sum(abs(item) for item in nums) / len(nums)
    return clamp(mean_abs / 2.0)


def risk_inputs(observation: dict[str, Any], terminal_samples: list[dict[str, Any]]) -> dict[str, float]:
    task_family = str(observation.get("task_family", ""))
    contact = observation.get("contact", {}) if isinstance(observation.get("contact"), dict) else {}
    force_norm = float(contact.get("force_norm", 0.0) or 0.0)
    mode = str(contact.get("mode", ""))
    hidden_contact = 0.12 if "contact" in mode else 0.0
    hard_task = 0.10 if any(token in task_family for token in ("door", "cable", "tool")) else 0.0
    dispersion = terminal_dispersion(terminal_samples)
    complexity = observation_complexity(observation)
    return {
        "dispersion": dispersion,
        "complexity": complexity,
        "force": clamp(force_norm / 3.0),
        "mode": hidden_contact,
        "task": hard_task,
    }


def decision_from_risk(method: str, risk: float, budget: float) -> tuple[str, str, str]:
    profile = METHOD_PROFILES.get(method, METHOD_PROFILES["greedy_module_sequence"])
    mode = str(profile["mode"])
    if method == "oracle_basin_composer":
        return ("accept" if risk <= 0.45 else "transition", "none" if risk <= 0.45 else "unknown", "oracle_bridge")
    if risk <= budget * 0.82:
        return "accept", "none", "none"
    if mode in {"v5", "search"} and risk <= budget * 1.45:
        return "repair", "high_barrier", "energy_bridge"
    if mode in {"v5", "v4", "energy", "option_graph"} and risk <= budget * 1.70:
        return "probe", "partial_observability", "diagnostic_terminal_sample"
    if mode in {"geometry", "stable_dynamics"} and risk <= budget * 1.35:
        return "transition", "descent_break", "alternate_skill_edge"
    return "abstain", "unknown", "none"


class ReferenceAdapter:
    def __init__(self, method_name: str):
        self.method_name = method_name
        self.profile = METHOD_PROFILES.get(method_name, METHOD_PROFILES["greedy_module_sequence"])
        self.policy_hash = stable_hash(f"paper119_reference_adapter:{method_name}:v1")
        self.online_memory: list[dict[str, Any]] = []

    def initialize(self, config: dict[str, Any]) -> dict[str, Any]:
        return {
            "method_name": self.method_name,
            "adapter_version": "paper119_reference_adapter_v1",
            "policy_or_config_hash": self.policy_hash,
            "implementation_note": "Executable reference adapter; not rollout evidence by itself.",
            "config_hash": stable_hash(repr(sorted(config.items()))),
        }

    def propose(
        self,
        observation: dict[str, Any],
        terminal_samples: list[dict[str, Any]],
        skill_i: str,
        skill_j: str,
        compute_budget: dict[str, Any],
    ) -> dict[str, Any]:
        budget = float(compute_budget.get("fixed_risk_budget", 0.15) or observation.get("fixed_risk_budget", 0.15) or 0.15)
        parts = risk_inputs(observation, terminal_samples)
        profile_bias = float(self.profile["bias"])
        risk_scale = float(self.profile["risk_scale"])
        raw_risk = (
            0.18
            + 0.22 * parts["dispersion"]
            + 0.18 * parts["complexity"]
            + 0.20 * parts["force"]
            + parts["mode"]
            + parts["task"]
            - profile_bias
        )
        predicted_risk = clamp(raw_risk / risk_scale)
        decision, diagnosis, repair_action = decision_from_risk(self.method_name, predicted_risk, budget)
        proposal_hash = stable_hash(f"{self.method_name}:{skill_i}:{skill_j}:{predicted_risk:.6f}:{decision}")
        return {
            "decision": decision,
            "predicted_seam_risk": predicted_risk,
            "failure_diagnosis": diagnosis,
            "repair_action": repair_action,
            "proposal_hash": proposal_hash,
            "skill_i": skill_i,
            "skill_j": skill_j,
            "adapter_mode": str(self.profile["mode"]),
        }

    def log(self, episode_context: dict[str, Any], proposal: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]:
        record = {
            "predicted_seam_risk": float(proposal.get("predicted_seam_risk", 1.0)),
            "decision": str(proposal.get("decision", "abstain")),
            "failure_diagnosis": str(proposal.get("failure_diagnosis", "unknown")),
            "repair_action": str(proposal.get("repair_action", "none")),
            "policy_or_config_hash": self.policy_hash,
            "method": self.method_name,
            "adapter_version": "paper119_reference_adapter_v1",
            "success": bool(outcome.get("success", False)),
            "realized_seam_breach": bool(outcome.get("realized_seam_breach", False)),
            "utility": float(outcome.get("utility", 0.0)),
        }
        self.online_memory.append({"episode_context": dict(episode_context), "record": dict(record)})
        return record

    def reset(self, reset_context: dict[str, Any]) -> None:
        if not reset_context.get("preserve_online_memory", False):
            self.online_memory.clear()


def make_adapter(method_name: str) -> ReferenceAdapter:
    return ReferenceAdapter(method_name)

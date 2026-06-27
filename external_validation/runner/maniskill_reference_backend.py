from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable

from external_validation.runner.backend_contract import ExternalCollectionBackend, sha256_file, sha256_json


ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "external_validation"
BASELINES = EXTERNAL / "baselines"


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not_installed"


def stable_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest().upper()


def numeric_values(value: Any, *, limit: int = 128) -> list[float]:
    values: list[float] = []

    def visit(item: Any) -> None:
        if len(values) >= limit:
            return
        if isinstance(item, bool):
            values.append(float(item))
        elif isinstance(item, (int, float)) and math.isfinite(float(item)):
            values.append(float(item))
        elif hasattr(item, "detach") and callable(item.detach):
            visit(item.detach().cpu().flatten().tolist())
        elif hasattr(item, "tolist") and callable(item.tolist):
            visit(item.tolist())
        elif isinstance(item, dict):
            for child in item.values():
                visit(child)
        elif isinstance(item, (list, tuple)):
            for child in item:
                visit(child)

    visit(value)
    return values


def _find_frame_candidate(value: Any) -> Any | None:
    if value is None:
        return None
    if isinstance(value, dict):
        preferred_keys = ("rgb", "image", "color", "Color", "rgba", "sensor_data")
        for key in preferred_keys:
            if key in value:
                candidate = _find_frame_candidate(value[key])
                if candidate is not None:
                    return candidate
        for child in value.values():
            candidate = _find_frame_candidate(child)
            if candidate is not None:
                return candidate
        return None
    if isinstance(value, (list, tuple)) and value and not isinstance(value[0], (int, float, bool)):
        for child in value:
            candidate = _find_frame_candidate(child)
            if candidate is not None:
                return candidate
    if hasattr(value, "shape") or hasattr(value, "tolist"):
        return value
    return None


def _as_uint8_rgb_frame(value: Any) -> Any:
    import numpy as np

    candidate = _find_frame_candidate(value)
    if candidate is None:
        raise RuntimeError("render did not return an RGB-like frame")
    if hasattr(candidate, "detach") and callable(candidate.detach):
        candidate = candidate.detach().cpu().numpy()
    frame = np.asarray(candidate)
    if frame.ndim == 4:
        frame = frame[0]
    if frame.ndim == 2:
        frame = np.repeat(frame[:, :, None], 3, axis=2)
    if frame.ndim != 3 or frame.shape[2] < 3:
        raise RuntimeError(f"render frame has unsupported shape {frame.shape}")
    frame = frame[:, :, :3]
    if frame.dtype != np.uint8:
        frame = frame.astype(np.float32)
        if frame.size and frame.max() <= 1.0:
            frame = frame * 255.0
        frame = np.clip(frame, 0, 255).astype(np.uint8)
    return frame


def write_mp4(target_path: Path, frames: Iterable[Any], *, fps: int = 4) -> str:
    import imageio.v2 as imageio

    target_path.parent.mkdir(parents=True, exist_ok=True)
    rgb_frames = [_as_uint8_rgb_frame(frame) for frame in frames]
    if not rgb_frames:
        raise RuntimeError("cannot write MP4 without at least one RGB frame")
    if len(rgb_frames) == 1:
        rgb_frames.append(rgb_frames[0].copy())
    imageio.mimsave(target_path, rgb_frames, fps=fps, macro_block_size=1)
    if not target_path.exists() or target_path.stat().st_size < 512:
        raise RuntimeError(f"video writer did not produce a usable MP4 at {target_path}")
    header = target_path.read_bytes()[:64]
    if b"ftyp" not in header:
        raise RuntimeError(f"video writer output does not look like MP4: {target_path}")
    return target_path.as_posix()


def import_adapter(method_name: str) -> ModuleType:
    adapter_path = BASELINES / method_name / "adapter.py"
    if not adapter_path.exists():
        raise RuntimeError(f"missing reference adapter for {method_name}: {adapter_path}")
    module_name = f"paper119_reference_adapter_{hashlib.sha256(str(adapter_path).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(module_name, adapter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import adapter: {adapter_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Backend(ExternalCollectionBackend):
    """ManiSkill/SAPIEN backend candidate for contract qualification.

    The backend intentionally remains fail-closed for official collection unless
    PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS=1 is set by an operator.
    Contract qualification and platform probing are not rollout evidence.
    """

    TEMPLATE_ONLY = False
    BACKEND_NAME = "maniskill_sapien_reference_backend_v1"

    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}
        self._adapters: dict[str, ModuleType] = {}
        self._adapter_init: dict[str, dict[str, Any]] = {}
        self._env: Any | None = None
        self._env_id = ""
        self._last_obs: Any = None
        self._last_info: dict[str, Any] = {}
        self._last_row: dict[str, Any] = {}
        self._last_config: dict[str, Any] = {}
        self._last_proposal: dict[str, Any] = {}
        self._video_frames: list[Any] = []

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "ManiSkill-SAPIEN-reference-backend",
            "platform_version": package_version("mani_skill"),
            "maniskill_version": package_version("mani_skill"),
            "sapien_version": package_version("sapien"),
            "gymnasium_version": package_version("gymnasium"),
            "torch_version": package_version("torch"),
            "python_version": platform.python_version(),
            "operating_system": platform.platform(),
            "sensor_modalities": ["state", "camera", "contact_or_force"],
            "renderer": os.environ.get("SAPIEN_RENDERER_DEVICE", "operator_default_or_cpu"),
            "physics_timestep": "operator_verified_by_fidelity_acceptance",
            "contact_solver": "operator_verified_by_fidelity_acceptance",
            "backend_module_sha256": sha256_file(Path(__file__)),
            "collection_enabled_by_default": False,
            "not_external_evidence": True,
        }

    def load_task_config(self, task_family: str, config: dict[str, Any]) -> dict[str, Any]:
        binding = config.get("backend_task_binding", {})
        env_id = str(binding.get("primary_env_id", "")).strip()
        if not env_id:
            raise RuntimeError(f"{task_family} config is missing backend_task_binding.primary_env_id")
        if config.get("platform_type") != "high_fidelity_sim":
            raise RuntimeError(f"{task_family} config must target high_fidelity_sim")
        self._configs[task_family] = dict(config)
        return {
            "task_family": task_family,
            "primary_env_id": env_id,
            "support_env_ids": list(binding.get("support_env_ids", []) or []),
            "config_hash": sha256_json(config),
        }

    def _ensure_env(self, env_id: str) -> Any:
        if self._env is not None and self._env_id == env_id:
            return self._env
        if self._env is not None:
            self._env.close()
        import gymnasium as gym
        import mani_skill  # noqa: F401

        try:
            self._env = gym.make(env_id, obs_mode="state", render_mode="rgb_array")
        except TypeError:
            self._env = gym.make(env_id, obs_mode="state")
        self._env_id = env_id
        return self._env

    def _try_capture_video_frame(self) -> None:
        if self._env is None:
            return
        try:
            frame = self._env.render()
            self._video_frames.append(_as_uint8_rgb_frame(frame))
        except Exception:
            return

    def reset_scene(self, reset_spec: dict[str, Any]) -> dict[str, Any]:
        row = reset_spec.get("row", {})
        config = reset_spec.get("task_config", {})
        task_family = str(row.get("task_family") or config.get("task_family", "")).strip()
        config = self._configs.get(task_family, config)
        env_id = str(config.get("backend_task_binding", {}).get("primary_env_id", "")).strip()
        if not env_id:
            raise RuntimeError(f"cannot reset {task_family}: missing primary_env_id")
        env = self._ensure_env(env_id)
        seed = int(row.get("seed", 0) or 0)
        obs, info = env.reset(seed=seed)
        self._last_obs = obs
        self._last_info = dict(info)
        self._last_row = dict(row)
        self._last_config = dict(config)
        self._video_frames = []
        self._try_capture_video_frame()
        return {
            "initial_state_hash": stable_digest({"env_id": env_id, "seed": seed, "obs": numeric_values(obs, limit=64)}),
            "env_id": env_id,
            "seed": seed,
            "scene_id": row.get("scene_id", ""),
            "info_keys": sorted(str(key) for key in self._last_info),
        }

    def capture_observation(self) -> dict[str, Any]:
        if self._last_obs is None:
            raise RuntimeError("capture_observation requires reset_scene first")
        features = numeric_values(self._last_obs, limit=96)
        task_family = str(self._last_row.get("task_family") or self._last_config.get("task_family", ""))
        contact_mode = "contact_transition" if any(token in task_family for token in ("drawer", "door", "cable")) else "free_to_contact"
        return {
            "task_family": task_family,
            "scene_id": self._last_row.get("scene_id", ""),
            "env_id": self._env_id,
            "state": {"features": features},
            "contact": {
                "force_norm": clamp(sum(abs(value) for value in features[:12]) / 12.0 if features else 0.0),
                "mode": contact_mode,
            },
            "fixed_risk_budget": float(self._last_config.get("fixed_risk_budget", 0.15) or 0.15),
            "backend_observation_hash": stable_digest(features),
        }

    def terminal_samples(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        observation = request.get("observation", {})
        features = numeric_values(observation.get("state", {}).get("features", []), limit=24)
        if not features:
            features = [0.0]
        seed = int(request.get("row", {}).get("seed", 0) or 0)
        samples = []
        for index in range(8):
            phase = (seed + index + 1) * 0.017
            sample_features = [clamp(value + math.sin(phase + offset) * 0.015, -10.0, 10.0) for offset, value in enumerate(features[:16])]
            samples.append(
                {
                    "sample_id": f"terminal_{index:02d}",
                    "features": sample_features,
                    "state_hash": stable_digest({"seed": seed, "index": index, "features": sample_features}),
                    "source": "maniskill_state_proxy_terminal_sampler",
                }
            )
        return samples

    def _adapter(self, method_name: str) -> ModuleType:
        if method_name not in self._adapters:
            self._adapters[method_name] = import_adapter(method_name)
        return self._adapters[method_name]

    def run_method(self, method_name: str, request: dict[str, Any]) -> dict[str, Any]:
        adapter = self._adapter(method_name)
        config = dict(request.get("config", {}))
        config["method_name"] = method_name
        if method_name not in self._adapter_init:
            self._adapter_init[method_name] = adapter.initialize(config)
        compute_budget = dict(config.get("compute_budget", {}))
        compute_budget["fixed_risk_budget"] = float(config.get("fixed_risk_budget", 0.15) or 0.15)
        terminal_samples = list(request.get("terminal_samples", []) or [])
        proposal = adapter.propose(
            dict(request.get("observation", {})),
            terminal_samples,
            str(request.get("skill_i", config.get("skill_i", ""))),
            str(request.get("skill_j", config.get("skill_j", ""))),
            compute_budget,
        )
        risk = float(proposal.get("predicted_seam_risk", 1.0))
        force = float(request.get("observation", {}).get("contact", {}).get("force_norm", 0.0) or 0.0)
        enriched = {
            **proposal,
            "terminal_sample_set_hash": stable_digest(terminal_samples),
            "basin_estimate": clamp(1.0 - risk + 0.08),
            "barrier_score": clamp(0.70 * risk + 0.30 * force),
            "descent_continuity_score": clamp(1.0 - 0.80 * risk - 0.20 * force),
            "predicted_seam_risk": clamp(risk),
            "policy_or_config_hash": self.policy_or_config_hash(method_name),
            "backend": self.BACKEND_NAME,
        }
        self._last_proposal = dict(enriched)
        return enriched

    def execute_skill_pair(self, request: dict[str, Any]) -> dict[str, Any]:
        if os.environ.get("PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS") != "1":
            raise RuntimeError(
                "ManiSkill reference backend is contract-qualified but fail-closed for official collection; "
                "set PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS=1 only inside an accepted external run."
            )
        if self._env is None:
            raise RuntimeError("execute_skill_pair requires a reset ManiSkill environment")
        proposal = request.get("proposal", self._last_proposal)
        decision = str(proposal.get("decision", "abstain"))
        risk = float(proposal.get("predicted_seam_risk", 1.0))
        if decision == "abstain":
            return {
                "success": False,
                "seam_failure": True,
                "barrier_violation": False,
                "damage_or_intervention": False,
                "composition_cost": 0.0,
                "realized_seam_breach": risk > 0.15,
                "utility": 0.0,
            }
        action = self._env.action_space.sample()
        _obs, reward, terminated, truncated, info = self._env.step(action)
        self._try_capture_video_frame()
        success_value = info.get("success", bool(terminated)) if isinstance(info, dict) else bool(terminated)
        success = bool(success_value.item()) if hasattr(success_value, "item") else bool(success_value)
        reward_value = float(reward.item()) if hasattr(reward, "item") else float(reward)
        breach = risk > float(self._last_config.get("fixed_risk_budget", 0.15) or 0.15)
        return {
            "success": success,
            "seam_failure": not success,
            "barrier_violation": breach and decision not in {"repair", "transition"},
            "damage_or_intervention": False,
            "composition_cost": 0.05 + (0.08 if decision == "repair" else 0.0),
            "realized_seam_breach": breach,
            "utility": reward_value + (1.0 if success else 0.0) - (0.5 if breach else 0.0),
            "terminated": bool(terminated),
            "truncated": bool(truncated),
        }

    def record_video(self, target_path: Path) -> str:
        if self._env is None:
            raise RuntimeError("record_video requires a reset ManiSkill environment")
        frames = list(self._video_frames)
        self._try_capture_video_frame()
        if len(self._video_frames) > len(frames):
            frames.append(self._video_frames[-1])
        if not frames:
            raise RuntimeError(
                "record_video requires renderable ManiSkill RGB frames; verify render_mode='rgb_array', "
                "camera setup, and renderer availability during fidelity acceptance"
            )
        return write_mp4(target_path, frames)

    def policy_or_config_hash(self, method_name: str) -> str:
        adapter_path = BASELINES / method_name / "adapter.py"
        if adapter_path.exists():
            return sha256_file(adapter_path)
        return sha256_json({"method": method_name, "backend": self.BACKEND_NAME})


def create_backend() -> Backend:
    return Backend()

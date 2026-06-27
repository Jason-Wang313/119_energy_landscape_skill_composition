from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_BACKEND_API = (
    "platform_provenance",
    "load_task_config",
    "reset_scene",
    "capture_observation",
    "terminal_samples",
    "run_method",
    "execute_skill_pair",
    "record_video",
    "policy_or_config_hash",
)


def sha256_json(payload: Any) -> str:
    """Stable SHA256 for JSON-compatible payloads used in external logs."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


class ExternalCollectionBackend:
    """Backend interface for real robot or high-fidelity simulator collection.

    Subclasses used for actual evidence must set TEMPLATE_ONLY = False and must
    implement every method below. Template backends deliberately inherit the
    fail-closed NotImplementedError behavior.
    """

    TEMPLATE_ONLY = True
    BACKEND_NAME = "template_external_collection_backend"

    def platform_provenance(self) -> dict[str, Any]:
        raise NotImplementedError("real backend must report platform provenance")

    def load_task_config(self, task_family: str, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("real backend must load task config")

    def reset_scene(self, reset_spec: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("real backend must reset scene")

    def capture_observation(self) -> dict[str, Any]:
        raise NotImplementedError("real backend must capture shared observation")

    def terminal_samples(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("real backend must produce terminal samples")

    def run_method(self, method_name: str, request: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("real backend must run or wrap method adapter")

    def execute_skill_pair(self, request: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("real backend must execute the skill pair")

    def record_video(self, target_path: Path) -> str:
        raise NotImplementedError("real backend must export rollout video")

    def policy_or_config_hash(self, method_name: str) -> str:
        raise NotImplementedError("real backend must report policy/config hash")


def validate_backend_object(backend: Any) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_BACKEND_API:
        if not callable(getattr(backend, name, None)):
            errors.append(f"backend missing callable {name}")
    if getattr(backend, "TEMPLATE_ONLY", True) is True:
        errors.append("backend has TEMPLATE_ONLY=True and cannot collect evidence")
    return errors


from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RUNNER = EXTERNAL / "runner"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_backend_contract_audit.json"
OUT_MD = RESULTS / "external_backend_contract_audit.md"

if str(RUNNER) not in sys.path:
    sys.path.insert(0, str(RUNNER))

from backend_contract import ExternalCollectionBackend, sha256_json, validate_backend_object  # noqa: E402


REQUIRED_PROVENANCE_FIELDS = (
    "platform_type",
    "platform_name",
    "platform_version",
    "sensor_modalities",
)
REQUIRED_MODALITIES = {"state", "camera", "contact_or_force"}


class CompleteSyntheticBackend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "complete_synthetic_backend_contract_self_test"

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "BackendContractSelfTest",
            "platform_version": "synthetic",
            "sensor_modalities": ["state", "camera", "contact_or_force"],
        }

    def load_task_config(self, task_family: str, config: dict[str, Any]) -> dict[str, Any]:
        return {"task_family": task_family, "loaded": True}

    def reset_scene(self, reset_spec: dict[str, Any]) -> dict[str, Any]:
        return {"initial_state_hash": sha256_json(reset_spec)}

    def capture_observation(self) -> dict[str, Any]:
        return {"state": [0.0], "contact_proxy": 0.0}

    def terminal_samples(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        return [{"sample": 0, "state": [0.0]}]

    def run_method(self, method_name: str, request: dict[str, Any]) -> dict[str, Any]:
        return {
            "terminal_sample_set_hash": sha256_json(request.get("terminal_samples", [])),
            "basin_estimate": 0.9,
            "barrier_score": 0.05,
            "descent_continuity_score": 0.9,
            "predicted_seam_risk": 0.05,
            "decision": "accept",
            "failure_diagnosis": "none",
            "repair_action": "none",
            "policy_or_config_hash": self.policy_or_config_hash(method_name),
        }

    def execute_skill_pair(self, request: dict[str, Any]) -> dict[str, Any]:
        return {
            "success": True,
            "seam_failure": False,
            "barrier_violation": False,
            "damage_or_intervention": False,
            "composition_cost": 0.1,
            "realized_seam_breach": False,
            "utility": 1.0,
        }

    def record_video(self, target_path: Path) -> str:
        return str(target_path)

    def policy_or_config_hash(self, method_name: str) -> str:
        return sha256_json({"method": method_name, "backend": self.BACKEND_NAME})


class IncompleteSyntheticBackend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "incomplete_synthetic_backend_contract_self_test"

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "IncompleteBackendContractSelfTest",
            "platform_version": "synthetic",
            "sensor_modalities": ["state", "camera", "contact_or_force"],
        }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def import_module_from_value(value: str) -> ModuleType:
    path = Path(value)
    if path.exists():
        module_name = f"paper119_external_backend_contract_{sha256_json(str(path))[:12]}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"could not import backend module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module(value)


def create_backend(module_value: str) -> Any:
    module = import_module_from_value(module_value)
    if callable(getattr(module, "create_backend", None)):
        return module.create_backend()
    backend_class = getattr(module, "Backend", None)
    if backend_class is not None:
        return backend_class()
    raise RuntimeError("backend module must expose create_backend() or Backend")


def alias_methods(path: Path) -> list[str]:
    if not path.exists():
        return []
    payload = read_json(path)
    aliases = payload.get("aliases", [])
    if not isinstance(aliases, list):
        return []
    return sorted(
        {
            str(item.get("method", "")).strip()
            for item in aliases
            if isinstance(item, dict) and str(item.get("method", "")).strip()
        }
    )


def config_tasks(path: Path) -> list[tuple[str, Path]]:
    if not path.exists():
        return []
    tasks = []
    for config_path in sorted(path.glob("*.json")):
        payload = read_json(config_path)
        task_family = str(payload.get("task_family", config_path.stem)).strip()
        if task_family:
            tasks.append((task_family, config_path))
    return tasks


def provenance_errors(provenance: Any) -> list[str]:
    if not isinstance(provenance, dict):
        return ["platform_provenance must return a dict"]
    errors = [
        f"platform_provenance missing {field}"
        for field in REQUIRED_PROVENANCE_FIELDS
        if provenance.get(field) is None or provenance.get(field) == "" or provenance.get(field) == []
    ]
    modalities = provenance.get("sensor_modalities")
    modality_set = set(modalities) if isinstance(modalities, list) else set()
    missing_modalities = sorted(REQUIRED_MODALITIES - modality_set)
    if missing_modalities:
        errors.append(f"sensor_modalities missing {missing_modalities}")
    return errors


def backend_module_checks(module_value: str, config_dir: Path, alias_map: Path) -> tuple[list[dict[str, Any]], bool]:
    checks: list[dict[str, Any]] = []
    if not module_value.strip():
        add_check(checks, "backend_module_supplied", False, "--backend-module not supplied")
        return checks, False
    add_check(checks, "backend_module_supplied", True, module_value)
    try:
        backend = create_backend(module_value)
        add_check(checks, "backend_constructs", True, type(backend).__name__)
    except Exception as exc:  # noqa: BLE001
        add_check(checks, "backend_constructs", False, f"{type(exc).__name__}: {exc}")
        return checks, False

    contract_errors = validate_backend_object(backend)
    add_check(
        checks,
        "backend_contract_complete",
        not contract_errors,
        "; ".join(contract_errors) if contract_errors else "all required methods are implemented by the backend class",
    )

    try:
        provenance = backend.platform_provenance()
        errors = provenance_errors(provenance)
        add_check(checks, "backend_platform_provenance_complete", not errors, "; ".join(errors) if errors else json.dumps(provenance, sort_keys=True))
    except Exception as exc:  # noqa: BLE001
        add_check(checks, "backend_platform_provenance_complete", False, f"{type(exc).__name__}: {exc}")

    load_errors = []
    for task_family, config_path in config_tasks(config_dir):
        try:
            config = read_json(config_path)
            loaded = backend.load_task_config(task_family, config)
            if not isinstance(loaded, dict):
                load_errors.append(f"{task_family}: load_task_config must return a dict")
        except Exception as exc:  # noqa: BLE001
            load_errors.append(f"{task_family}: {type(exc).__name__}: {exc}")
    add_check(
        checks,
        "backend_loads_all_task_configs",
        not load_errors and bool(config_tasks(config_dir)),
        "; ".join(load_errors[:8]) if load_errors else f"tasks={len(config_tasks(config_dir))}",
    )

    hash_errors = []
    for method in alias_methods(alias_map):
        try:
            value = backend.policy_or_config_hash(method)
            if not isinstance(value, str) or len(value) != 64:
                hash_errors.append(f"{method}: policy_or_config_hash must return a 64-character SHA256 string")
        except Exception as exc:  # noqa: BLE001
            hash_errors.append(f"{method}: {type(exc).__name__}: {exc}")
    add_check(
        checks,
        "backend_reports_method_hashes",
        not hash_errors and len(alias_methods(alias_map)) >= 12,
        "; ".join(hash_errors[:8]) if hash_errors else f"methods={len(alias_methods(alias_map))}",
    )

    ready = all(check["passed"] for check in checks)
    return checks, ready


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    contract_path = RUNNER / "backend_contract.py"
    runner_readme = RUNNER / "README.md"
    template_dir = RUNNER / "backend_templates"
    template_paths = sorted(template_dir.glob("*_backend.py"))

    add_check(checks, "backend_contract_file_exists", contract_path.exists(), rel(contract_path))
    contract_text = read_text(contract_path)
    for name, required_term in (
        ("required_backend_api", "REQUIRED_BACKEND_API"),
        ("base_class", "ExternalCollectionBackend"),
        ("validator", "validate_backend_object"),
        ("base_implementation_rejection", "backend uses base NotImplementedError implementation"),
    ):
        add_check(checks, f"backend_contract_mentions_{name}", required_term in contract_text, required_term)

    template_errors = []
    for path in template_paths:
        text = read_text(path)
        if "TEMPLATE_ONLY = True" not in text:
            template_errors.append(f"{rel(path)} is not marked TEMPLATE_ONLY")
    add_check(checks, "backend_templates_fail_closed", len(template_paths) >= 4 and not template_errors, f"templates={len(template_paths)}, errors={template_errors}")

    readme_text = read_text(runner_readme)
    add_check(checks, "runner_readme_declares_backend_audit", "audit_external_backend_contract.py" in readme_text, "README documents backend qualification audit")

    complete_errors = validate_backend_object(CompleteSyntheticBackend())
    incomplete_errors = validate_backend_object(IncompleteSyntheticBackend())
    add_check(checks, "contract_accepts_complete_synthetic_backend", not complete_errors, "; ".join(complete_errors) if complete_errors else "complete backend passed")
    add_check(
        checks,
        "contract_rejects_incomplete_synthetic_backend",
        any("base NotImplementedError" in error for error in incomplete_errors),
        "; ".join(incomplete_errors) if incomplete_errors else "incomplete backend unexpectedly passed",
    )

    supplied_checks, supplied_ready = backend_module_checks(args.backend_module, args.task_config_dir, args.alias_map)
    checks.extend(supplied_checks)

    harness_ok = all(check["passed"] for check in checks if check["name"] not in {"backend_module_supplied"})
    backend_supplied = bool(args.backend_module.strip())
    backend_ready = supplied_ready if backend_supplied else False
    passed = harness_ok and (backend_ready if args.strict else True)
    return {
        "version": "external_backend_contract_audit_v1",
        "passed": passed,
        "strict": args.strict,
        "not_external_evidence": True,
        "backend_module": args.backend_module,
        "backend_contract_harness_ready": harness_ok,
        "actual_backend_ready": backend_ready,
        "backend_required_for_collection": True,
        "task_config_dir": rel(args.task_config_dir),
        "alias_map": rel(args.alias_map),
        "checks": checks,
        "blocking_missing": [f"{check['name']}: {check['detail']}" for check in checks if not check["passed"]],
        "strict_command": (
            "python scripts\\audit_external_backend_contract.py --strict "
            "--backend-module <module_or_path> --task-config-dir external_validation\\configs "
            "--alias-map external_validation\\method_alias_map.json"
        ),
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Backend Contract Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Strict: `{str(payload['strict']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Backend contract harness ready: `{str(payload['backend_contract_harness_ready']).lower()}`.",
        f"Actual backend ready: `{str(payload['actual_backend_ready']).lower()}`.",
        "",
        "This audit checks the backend module contract before any real robot or high-fidelity simulator collection starts. It is not rollout evidence and does not replace fidelity acceptance, JSONL logs, videos, manifests, or strict external-evidence audits.",
        "",
        "## Strict Command",
        "",
        "```powershell",
        payload["strict_command"],
        "```",
        "",
        "## Blocking Missing",
        "",
    ]
    if payload["blocking_missing"]:
        for item in payload["blocking_missing"][:100]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the Paper 119 external backend contract.")
    parser.add_argument("--backend-module", default="", help="Import path or .py file exposing create_backend() or Backend.")
    parser.add_argument("--task-config-dir", type=Path, default=EXTERNAL / "configs")
    parser.add_argument("--alias-map", type=Path, default=EXTERNAL / "method_alias_map.json")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless a real backend module passes the contract.")
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload)
    print(
        "External backend contract audit: "
        f"harness_ready={payload['backend_contract_harness_ready']}; "
        f"actual_backend_ready={payload['actual_backend_ready']}; "
        f"strict={payload['strict']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

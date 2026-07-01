from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any

import audit_external_backend_contract as backend_audit


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_backend_contract_self_test.json"
OUT_MD = RESULTS / "external_backend_contract_self_test.md"


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def complete_backend_text() -> str:
    return r'''
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend_contract import ExternalCollectionBackend, sha256_json


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "backend_contract_self_test_complete"

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "BackendContractSelfTest-v1",
            "platform_version": "synthetic",
            "sensor_modalities": ["state", "camera", "contact_or_force"],
        }

    def load_task_config(self, task_family: str, config: dict[str, Any]) -> dict[str, Any]:
        return {"task_family": task_family, "loaded": True, "config_hash": sha256_json(config)}

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


def create_backend() -> Backend:
    return Backend()
'''.lstrip()


def incomplete_backend_text() -> str:
    return r'''
from __future__ import annotations

from typing import Any

from backend_contract import ExternalCollectionBackend


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "backend_contract_self_test_incomplete"

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "IncompleteBackendContractSelfTest-v1",
            "platform_version": "synthetic",
            "sensor_modalities": ["state", "camera", "contact_or_force"],
        }


def create_backend() -> Backend:
    return Backend()
'''.lstrip()


def copy_configs(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted((EXTERNAL / "configs").glob("*.json")):
        shutil.copy2(source, target / source.name)


def audit_payload(backend_module: str, config_dir: Path, alias_map: Path, *, strict: bool) -> dict[str, Any]:
    args = Namespace(
        backend_module=backend_module,
        task_config_dir=config_dir,
        alias_map=alias_map,
        strict=strict,
    )
    return backend_audit.build_payload(args)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Backend Contract Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "",
        "This self-test builds temporary backend modules and exercises the strict backend qualification gate. It verifies that a complete synthetic backend passes, incomplete/base-method implementations fail, template backends fail, and the real backend audit report is not overwritten.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks: list[dict[str, Any]] = []
    real_report = RESULTS / "external_backend_contract_audit.json"
    report_before = file_digest(real_report)

    with tempfile.TemporaryDirectory(prefix="paper119_backend_contract_selftest_") as tmp_name:
        tmp = Path(tmp_name)
        config_dir = tmp / "configs"
        alias_map = EXTERNAL / "method_alias_map.json"
        complete_backend = tmp / "complete_backend.py"
        incomplete_backend = tmp / "incomplete_backend.py"

        copy_configs(config_dir)
        complete_backend.write_text(complete_backend_text(), encoding="utf-8")
        incomplete_backend.write_text(incomplete_backend_text(), encoding="utf-8")

        complete_payload = audit_payload(str(complete_backend), config_dir, alias_map, strict=True)
        incomplete_payload = audit_payload(str(incomplete_backend), config_dir, alias_map, strict=True)
        template_payload = audit_payload(
            "external_validation.runner.backend_templates.maniskill_backend",
            config_dir,
            alias_map,
            strict=True,
        )
        default_payload = audit_payload("", config_dir, alias_map, strict=False)

    report_after = file_digest(real_report)

    complete_checks = {check.get("name"): check.get("passed") for check in complete_payload.get("checks", [])}
    incomplete_blockers = "\n".join(incomplete_payload.get("blocking_missing", []))
    template_blockers = "\n".join(template_payload.get("blocking_missing", []))

    add_check(
        checks,
        "strict_complete_backend_passes",
        complete_payload.get("passed") is True
        and complete_payload.get("actual_backend_ready") is True
        and complete_checks.get("backend_loads_all_task_configs") is True
        and complete_checks.get("backend_reports_method_hashes") is True,
        f"passed={complete_payload.get('passed')!r}, actual_backend_ready={complete_payload.get('actual_backend_ready')!r}",
    )
    add_check(
        checks,
        "strict_incomplete_backend_fails",
        incomplete_payload.get("passed") is False
        and incomplete_payload.get("actual_backend_ready") is False
        and "base NotImplementedError" in incomplete_blockers,
        incomplete_blockers[:500],
    )
    add_check(
        checks,
        "strict_template_backend_fails",
        template_payload.get("passed") is False
        and template_payload.get("actual_backend_ready") is False
        and "TEMPLATE_ONLY=True" in template_blockers,
        template_blockers[:500],
    )
    add_check(
        checks,
        "default_missing_backend_remains_nonready",
        default_payload.get("passed") is True
        and default_payload.get("actual_backend_ready") is False
        and default_payload.get("not_external_evidence") is True,
        f"passed={default_payload.get('passed')!r}, actual_backend_ready={default_payload.get('actual_backend_ready')!r}",
    )
    add_check(
        checks,
        "real_backend_contract_report_not_overwritten",
        report_before == report_after,
        "self-test calls build_payload only and leaves results/external_backend_contract_audit.json unchanged",
    )

    payload = {
        "version": "external_backend_contract_self_test_v1",
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "complete_backend_actual_ready": complete_payload.get("actual_backend_ready"),
        "checks": checks,
    }
    write_report(payload)
    print(
        "External backend contract self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"complete_backend_actual_ready={payload['complete_backend_actual_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

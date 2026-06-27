from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Any

import audit_external_collection_readiness as readiness


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"
OUT_JSON = RESULTS / "external_collection_preflight_self_test.json"
OUT_MD = RESULTS / "external_collection_preflight_self_test.md"

TASKS = [
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
]
METHOD_ALIASES = [f"M{index:03d}" for index in range(1, 13)]
RUN_ID = "paper119_synthetic_preflight_selftest_20260627"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backend_module_text() -> str:
    return r'''
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend_contract import ExternalCollectionBackend, sha256_json


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "synthetic_collection_preflight_backend"

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "SyntheticPreflightBackend-v1",
            "platform_version": "self-test-only",
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
            "terminal_sample_set_hash": sha256_json(request["terminal_samples"]),
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
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(b"synthetic preflight video\n")
        return str(target_path)

    def policy_or_config_hash(self, method_name: str) -> str:
        return sha256_json({"method": method_name, "backend": self.BACKEND_NAME})


def create_backend() -> Backend:
    return Backend()
'''.lstrip()


def write_operator_sheet(path: Path) -> None:
    columns = [
        "blind_run_id",
        "task_family",
        "platform_type",
        "platform_name",
        "reset_index",
        "scene_id",
        "episode_index",
        "seed",
        "run_order_within_reset",
        "method_alias",
        "expected_log_jsonl",
        "expected_video_path",
        "status",
    ]
    rows: list[dict[str, str]] = []
    episode = 0
    for task in TASKS:
        for reset_index in range(30):
            for order, alias in enumerate(METHOD_ALIASES):
                rows.append(
                    {
                        "blind_run_id": RUN_ID,
                        "task_family": task,
                        "platform_type": "high_fidelity_sim",
                        "platform_name": "SyntheticPreflightBackend-v1",
                        "reset_index": str(reset_index),
                        "scene_id": f"{task}_preflight_{reset_index:03d}",
                        "episode_index": str(episode),
                        "seed": str(reset_index),
                        "run_order_within_reset": str(order),
                        "method_alias": alias,
                        "expected_log_jsonl": f"external_validation/logs/{task}.jsonl",
                        "expected_video_path": f"external_validation/videos/{task}/{reset_index:03d}_{alias}.mp4",
                        "status": "planned",
                    }
                )
                episode += 1
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_alias_map(path: Path) -> None:
    methods = [
        "greedy_module_sequence",
        "behavior_cloned_skill_chain",
        "option_graph_planner",
        "diffusion_skill_stitcher",
        "cem_trajectory_composer",
        "residual_rl_composer",
        "energy_compatibility_heuristic",
        "tamp_feasibility_screen",
        "stable_dmp_handoff",
        "proposed_energy_landscape_composer_v4_1",
        "barrier_certified_energy_composer_v5",
        "oracle_basin_composer",
    ]
    write_json(path, {"aliases": [{"alias": alias, "method": method} for alias, method in zip(METHOD_ALIASES, methods)]})


def copy_configs(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for task in TASKS:
        source = EXTERNAL / "configs" / f"{task}.json"
        if not source.exists():
            raise SystemExit(f"missing prepared config for self-test: {source}")
        (target_dir / f"{task}.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def write_fidelity_audit(path: Path) -> None:
    write_json(
        path,
        {
            "version": "external_fidelity_acceptance_audit_v1",
            "passed": True,
            "not_external_evidence": True,
            "acceptance_ready": True,
            "readiness_state": "READY_FOR_SYNTHETIC_PREFLIGHT_SELF_TEST",
            "blocking_missing_count": 0,
            "blocking_missing": [],
            "contract_checks": [],
            "evidence_checks": [],
        },
    )


def make_args(tmp: Path, backend_path: Path, operator_sheet: Path, alias_map: Path, config_dir: Path, fidelity_audit: Path) -> Namespace:
    return Namespace(
        backend_module=str(backend_path),
        operator_sheet=operator_sheet,
        alias_map=alias_map,
        task_config_dir=config_dir,
        output_log_dir=tmp / "logs",
        video_dir=tmp / "videos",
        fidelity_audit=fidelity_audit,
        runner=EXTERNAL / "runner" / "real_collection_runner.py",
        schema=EXTERNAL / "log_schema_v1.json",
        run_id=RUN_ID,
        unsealed_alias_map=True,
        force=False,
        strict=True,
    )


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Collection Preflight Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic collection ready: `{str(payload['synthetic_collection_ready']).lower()}`.",
        f"Synthetic row count: `{payload['row_count']}`.",
        "",
        "This self-test builds a temporary complete collection-preflight fixture and calls the collection readiness audit without writing the real readiness report. It proves the strict preflight gate can turn green when backend, configs, fidelity acceptance, aliases, logs, video directory, and run id are complete. It is not external validation evidence.",
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
    real_readiness_report = RESULTS / "external_collection_readiness_audit.json"
    readiness_report_before = file_digest(real_readiness_report)
    with tempfile.TemporaryDirectory(prefix="paper119_collection_preflight_selftest_") as tmp_name:
        tmp = Path(tmp_name)
        backend_path = tmp / "synthetic_preflight_backend.py"
        operator_sheet = tmp / "operator_sheet.csv"
        alias_map = tmp / "method_alias_map.json"
        config_dir = tmp / "configs"
        fidelity_audit = tmp / "external_fidelity_acceptance_audit.json"

        backend_path.write_text(backend_module_text(), encoding="utf-8")
        write_operator_sheet(operator_sheet)
        write_alias_map(alias_map)
        copy_configs(config_dir)
        write_fidelity_audit(fidelity_audit)

        args = make_args(tmp, backend_path, operator_sheet, alias_map, config_dir, fidelity_audit)
        payload = readiness.build_payload(args)

        readiness_report_after = file_digest(real_readiness_report)
        readiness_report_untouched = readiness_report_before == readiness_report_after
        checks.append(
            {
                "name": "synthetic_preflight_collection_ready",
                "passed": payload.get("collection_ready") is True and not payload.get("blocking_missing"),
                "detail": f"collection_ready={payload.get('collection_ready')!r}, blockers={payload.get('blocking_missing')!r}",
            }
        )
        checks.append(
            {
                "name": "synthetic_row_budget",
                "passed": int(payload.get("row_count", 0) or 0) >= 1440,
                "detail": f"row_count={payload.get('row_count')!r}",
            }
        )
        payload_checks = {check.get("name"): check.get("passed") for check in payload.get("checks", [])}
        for required_check in (
            "backend_module_ready",
            "real_task_configs_ready",
            "fidelity_acceptance_ready",
            "alias_unsealing_explicit",
            "run_id_specific",
            "output_logs_empty_or_force",
        ):
            checks.append(
                {
                    "name": f"synthetic_{required_check}",
                    "passed": payload_checks.get(required_check) is True,
                    "detail": f"{required_check}={payload_checks.get(required_check)!r}",
                }
            )
        checks.append(
            {
                "name": "real_readiness_report_not_overwritten",
                "passed": readiness_report_untouched,
                "detail": "self-test uses build_payload only and leaves results/external_collection_readiness_audit.json unchanged",
            }
        )

        report = {
            "version": "external_collection_preflight_self_test_v1",
            "passed": all(check["passed"] for check in checks),
            "not_external_evidence": True,
            "synthetic_collection_ready": payload.get("collection_ready") is True,
            "row_count": payload.get("row_count", 0),
            "task_families": payload.get("task_families", []),
            "alias_count": payload.get("alias_count", 0),
            "checks": checks,
        }

    write_report(report)
    print(
        "External collection preflight self-test: "
        f"{'PASS' if report['passed'] else 'FAIL'}; "
        f"collection_ready={report['synthetic_collection_ready']}; rows={report['row_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import validate_external_rollouts as rollout_validator


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"
RUNNER = EXTERNAL / "runner" / "real_collection_runner.py"
SCHEMA = EXTERNAL / "log_schema_v1.json"
CONFIG_SCHEMA = EXTERNAL / "config_schema_v1.json"
OUT_JSON = RESULTS / "external_runner_backend_self_test.json"
OUT_MD = RESULTS / "external_runner_backend_self_test.md"


TASK = "peg_place_regrasp"
METHOD = rollout_validator.PRIMARY_METHOD
RUN_ID = "synthetic_runner_backend_self_test"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def backend_module_text() -> str:
    return r'''
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend_contract import ExternalCollectionBackend, sha256_json


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = False
    BACKEND_NAME = "synthetic_runner_backend_self_test"

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}
        self.last_video_path: Path | None = None

    def platform_provenance(self) -> dict[str, Any]:
        return {
            "platform_type": "high_fidelity_sim",
            "platform_name": "SyntheticBackendSelfTest-v1",
            "platform_version": "self-test-only",
            "sensor_modalities": ["state", "camera", "contact_or_force"],
        }

    def load_task_config(self, task_family: str, config: dict[str, Any]) -> dict[str, Any]:
        self.config = dict(config)
        return {"task_family": task_family, "loaded": True}

    def reset_scene(self, reset_spec: dict[str, Any]) -> dict[str, Any]:
        row = reset_spec["row"]
        return {
            "scene_id": row["scene_id"],
            "seed": int(row["seed"]),
            "initial_state_hash": sha256_json({"scene_id": row["scene_id"], "seed": int(row["seed"])}),
        }

    def capture_observation(self) -> dict[str, Any]:
        return {
            "state": [0.1, 0.2, 0.3],
            "camera_frame_hash": sha256_json("synthetic-camera-frame"),
            "contact_proxy": 0.0,
        }

    def terminal_samples(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        row = request["row"]
        return [
            {"sample_id": 0, "scene_id": row["scene_id"], "basin_coordinate": 0.42},
            {"sample_id": 1, "scene_id": row["scene_id"], "basin_coordinate": 0.57},
        ]

    def run_method(self, method_name: str, request: dict[str, Any]) -> dict[str, Any]:
        terminal_samples = request["terminal_samples"]
        return {
            "terminal_sample_set_hash": sha256_json(terminal_samples),
            "basin_estimate": 0.86,
            "barrier_score": 0.08,
            "descent_continuity_score": 0.91,
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
            "composition_cost": 0.18,
            "realized_seam_breach": False,
            "utility": 1.0,
        }

    def record_video(self, target_path: Path) -> str:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes((b"synthetic runner backend self-test video\n") * 32)
        self.last_video_path = target_path
        return str(target_path)

    def policy_or_config_hash(self, method_name: str) -> str:
        return sha256_json({"method": method_name, "backend": self.BACKEND_NAME})


def create_backend() -> Backend:
    return Backend()
'''.lstrip()


def make_config() -> dict[str, Any]:
    schema = json.loads(CONFIG_SCHEMA.read_text(encoding="utf-8"))
    return {
        "version": schema["evidence_version"],
        "config_schema": "external_validation/config_schema_v1.json",
        "task_family": TASK,
        "platform_type": "high_fidelity_sim",
        "platform_name": "SyntheticBackendSelfTest-v1",
        "skill_i": "place_peg_on_fixture",
        "skill_j": "regrasp_for_insertion",
        "seam_under_test": "synthetic self-test handoff used only to exercise the backend runner contract",
        "required_fidelity_checks": [
            "state logging path exercised",
            "video export path exercised",
            "contact proxy path exercised",
        ],
        "reset_protocol": {
            "paired_resets": True,
            "reset_count": 2,
            "scene_id_template": "synthetic_backend_self_test_{index:03d}",
            "initial_state_hash_required": True,
        },
        "observation_interface": {
            "state_logging_required": True,
            "camera_logging_required": True,
            "contact_or_force_logging_required": True,
        },
        "compute_budget": {
            "same_for_all_non_oracle_methods": True,
            "wall_clock_seconds": 5,
            "simulator_query_budget": 8,
        },
        "paired_reset_count": 30,
        "fixed_risk_budget": 0.15,
        "must_log": schema["required_log_fields"],
    }


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
    rows = []
    for index in range(2):
        rows.append(
            {
                "blind_run_id": RUN_ID,
                "task_family": TASK,
                "platform_type": "high_fidelity_sim",
                "platform_name": "SyntheticBackendSelfTest-v1",
                "reset_index": str(index),
                "scene_id": f"synthetic_backend_self_test_{index:03d}",
                "episode_index": str(index),
                "seed": str(index),
                "run_order_within_reset": "0",
                "method_alias": "M001",
                "expected_log_jsonl": f"external_validation/logs/{TASK}.jsonl",
                "expected_video_path": f"external_validation/videos/{TASK}/{index:03d}_{METHOD}.mp4",
                "status": "planned",
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def validate_written_records(log_path: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not log_path.exists():
        return [f"missing expected log file: {log_path}"]
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(records) != 2:
        errors.append(f"expected 2 records, got {len(records)}")
    for index, record in enumerate(records, start=1):
        errors.extend(
            rollout_validator.validate_record(
                record,
                line_id=f"synthetic_backend_self_test:{index}",
                schema=schema,
                manifest_methods={METHOD},
                manifest_tasks={TASK},
                check_video_paths=True,
            )
        )
    return errors


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Runner Backend Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Records written in temporary fixture: `{payload['records_written']}`.",
        f"Schema errors: `{len(payload['schema_errors'])}`.",
        "",
        "This self-test exercises the actual collection runner with a temporary synthetic non-template backend. It proves the backend API, runner JSONL writer, video export path, and rollout-record schema path can work end to end without touching the real external manifest or claiming validation evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    real_manifest = EXTERNAL / "manifest.json"
    manifest_before = real_manifest.read_bytes() if real_manifest.exists() else None
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []
    schema_errors: list[str] = []
    records_written = 0
    runner_returncode = 1
    runner_output = ""

    with tempfile.TemporaryDirectory(prefix="paper119_runner_backend_selftest_") as tmp_name:
        tmp = Path(tmp_name)
        backend_path = tmp / "synthetic_backend.py"
        operator_sheet = tmp / "operator_sheet.csv"
        alias_map = tmp / "method_alias_map.json"
        config_dir = tmp / "configs"
        log_dir = tmp / "logs"
        video_dir = tmp / "videos"
        backend_path.write_text(backend_module_text(), encoding="utf-8")
        write_operator_sheet(operator_sheet)
        write_json(alias_map, {"aliases": [{"alias": "M001", "method": METHOD}]})
        write_json(config_dir / f"{TASK}.json", make_config())

        command = [
            sys.executable,
            str(RUNNER),
            "--backend-module",
            str(backend_path),
            "--operator-sheet",
            str(operator_sheet),
            "--alias-map",
            str(alias_map),
            "--task-config-dir",
            str(config_dir),
            "--output-log-dir",
            str(log_dir),
            "--video-dir",
            str(video_dir),
            "--run-id",
            RUN_ID,
            "--unsealed-alias-map",
            "--max-rows",
            "2",
            "--force",
        ]
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        runner_returncode = proc.returncode
        runner_output = proc.stdout + proc.stderr
        log_path = log_dir / f"{TASK}.jsonl"
        if log_path.exists():
            records_written = sum(1 for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip())
            schema_errors = validate_written_records(log_path, schema)

        checks.append({"name": "runner_actual_path_exits_zero", "passed": runner_returncode == 0, "detail": runner_output[:240]})
        checks.append({"name": "temporary_records_written", "passed": records_written == 2, "detail": f"records={records_written}"})
        checks.append({"name": "temporary_records_schema_valid", "passed": not schema_errors, "detail": f"errors={schema_errors[:3]}"})
        checks.append({"name": "temporary_videos_written", "passed": len(list(video_dir.glob(f'{TASK}/*.mp4'))) == 2, "detail": f"videos={len(list(video_dir.glob(f'{TASK}/*.mp4')))}"})

    manifest_untouched = (
        (manifest_before is None and not real_manifest.exists())
        or (manifest_before is not None and real_manifest.exists() and real_manifest.read_bytes() == manifest_before)
    )
    checks.append({"name": "real_manifest_untouched", "passed": manifest_untouched, "detail": "external_validation/manifest.json unchanged or absent"})

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_runner_backend_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "runner_returncode": runner_returncode,
        "records_written": records_written,
        "schema_errors": schema_errors,
        "checks": checks,
    }
    write_report(payload)
    print(f"External runner backend self-test: {'PASS' if passed else 'FAIL'}; records={records_written}; schema_errors={len(schema_errors)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

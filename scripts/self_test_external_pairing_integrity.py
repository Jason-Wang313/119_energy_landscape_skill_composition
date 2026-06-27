from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import audit_external_pairing_integrity as pairing_audit


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
TMP_ROOT = ROOT / "tmp"
OUT_JSON = RESULTS / "external_pairing_integrity_self_test.json"
OUT_MD = RESULTS / "external_pairing_integrity_self_test.md"
REAL_REPORT = RESULTS / "external_pairing_integrity_audit.json"

TASKS = [
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
]
METHODS = [
    "greedy_module_sequence",
    "behavior_cloned_skill_chain",
    "option_graph_planner",
    "tamp_feasibility_screen",
    "stable_dmp_handoff",
    "diffusion_skill_stitcher",
    "cem_trajectory_composer",
    "residual_rl_composer",
    "energy_compatibility_heuristic",
    "proposed_energy_landscape_composer_v4_1",
    "barrier_certified_energy_composer_v5",
    "oracle_basin_composer",
]


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_record(task: str, reset_index: int, method: str, *, terminal_hash: str | None = None) -> dict[str, Any]:
    scene_id = f"{task}_scene_{reset_index:03d}"
    return {
        "run_id": "pairing_integrity_self_test",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "PairingIntegritySelfTestSim-v1",
        "scene_id": scene_id,
        "episode_index": reset_index,
        "seed": reset_index,
        "method": method,
        "skill_i": f"{task}_source_skill",
        "skill_j": f"{task}_target_skill",
        "initial_state_hash": digest(f"{task}:{reset_index}:initial"),
        "terminal_sample_set_hash": terminal_hash or digest(f"{task}:{reset_index}:terminal"),
        "basin_estimate": 0.9,
        "barrier_score": 0.05,
        "descent_continuity_score": 0.9,
        "predicted_seam_risk": 0.05,
        "fixed_risk_budget": 0.15,
        "decision": "accept",
        "failure_diagnosis": "none",
        "repair_action": "none",
        "success": True,
        "seam_failure": False,
        "barrier_violation": False,
        "damage_or_intervention": False,
        "composition_cost": 0.1,
        "realized_seam_breach": False,
        "utility": 1.0,
        "video_path": f"external_validation/videos/{task}/{reset_index:03d}_{method}.mp4",
        "policy_or_config_hash": digest(f"{method}:policy"),
    }


def write_logs(log_dir: Path, *, mode: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    for task in TASKS:
        path = log_dir / f"{task}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for reset_index in range(30):
                for method in METHODS:
                    if mode == "missing_method" and task == TASKS[0] and reset_index == 0 and method == METHODS[-1]:
                        continue
                    terminal_hash = None
                    if mode == "terminal_mismatch" and task == TASKS[0] and reset_index == 0 and method == METHODS[0]:
                        terminal_hash = digest("mismatched-terminal")
                    record = make_record(task, reset_index, method, terminal_hash=terminal_hash)
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
                    if mode == "duplicate_method" and task == TASKS[0] and reset_index == 0 and method == METHODS[0]:
                        handle.write(json.dumps(record, sort_keys=True) + "\n")


def write_manifest(path: Path, log_dir: Path) -> None:
    tasks = [
        {
            "task_family": task,
            "platform_type": "high_fidelity_sim",
            "platform_name": "PairingIntegritySelfTestSim-v1",
            "episodes_per_method": 30,
            "log_jsonl": rel(log_dir / f"{task}.jsonl"),
        }
        for task in TASKS
    ]
    methods = [{"name": method} for method in METHODS]
    write_json(
        path,
        {
            "version": "paper119_external_manifest_v1",
            "route": "high_fidelity_sim",
            "tasks": tasks,
            "methods": methods,
        },
    )


def build_case(tmp: Path, name: str, mode: str) -> Path:
    case_dir = tmp / name
    log_dir = case_dir / "logs"
    manifest_path = case_dir / "manifest.json"
    write_logs(log_dir, mode=mode)
    write_manifest(manifest_path, log_dir)
    return manifest_path


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Pairing Integrity Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic pairing ready: `{str(payload['synthetic_pairing_ready']).lower()}`.",
        "",
        "This self-test builds temporary manifest-declared JSONL logs and exercises the paired-reset fairness gate directly. It proves complete method panels can pass, missing manifests fail, duplicate method rows fail, incomplete panels fail, terminal-sample mismatches fail, and the real pairing audit report is not overwritten.",
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
    report_before = file_digest(REAL_REPORT)
    TMP_ROOT.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="paper119_pairing_selftest_", dir=TMP_ROOT) as tmp_name:
        tmp = Path(tmp_name)
        schema = tmp / "log_schema_v1.json"
        shutil.copy2(EXTERNAL / "log_schema_v1.json", schema)

        complete_manifest = build_case(tmp, "complete", "complete")
        duplicate_manifest = build_case(tmp, "duplicate", "duplicate_method")
        missing_method_manifest = build_case(tmp, "missing_method", "missing_method")
        terminal_mismatch_manifest = build_case(tmp, "terminal_mismatch", "terminal_mismatch")
        missing_manifest = tmp / "manifest_missing.json"

        complete_audit = pairing_audit.build_payload(complete_manifest, schema)
        duplicate_audit = pairing_audit.build_payload(duplicate_manifest, schema)
        missing_method_audit = pairing_audit.build_payload(missing_method_manifest, schema)
        terminal_mismatch_audit = pairing_audit.build_payload(terminal_mismatch_manifest, schema)
        missing_manifest_audit = pairing_audit.build_payload(missing_manifest, schema)

    report_after = file_digest(REAL_REPORT)

    duplicate_blockers = "\n".join(duplicate_audit.get("blocking_missing", []))
    missing_method_blockers = "\n".join(missing_method_audit.get("blocking_missing", []))
    terminal_mismatch_blockers = "\n".join(terminal_mismatch_audit.get("blocking_missing", []))

    add_check(
        checks,
        "synthetic_pairing_integrity_passes",
        complete_audit.get("pairing_ready") is True
        and complete_audit.get("not_external_evidence") is False
        and complete_audit.get("expected_records") == 1440
        and complete_audit.get("observed_records") == 1440
        and not complete_audit.get("blocking_missing"),
        f"ready={complete_audit.get('pairing_ready')!r}, records={complete_audit.get('observed_records')}/{complete_audit.get('expected_records')}",
    )
    add_check(
        checks,
        "missing_manifest_fails_pairing_readiness",
        missing_manifest_audit.get("pairing_ready") is False
        and missing_manifest_audit.get("not_external_evidence") is True
        and "manifest.json has not been written" in "\n".join(missing_manifest_audit.get("blocking_missing", [])),
        f"ready={missing_manifest_audit.get('pairing_ready')!r}, blockers={missing_manifest_audit.get('blocking_missing')!r}",
    )
    add_check(
        checks,
        "duplicate_method_rows_fail_pairing",
        duplicate_audit.get("pairing_ready") is False
        and "duplicate method records within paired reset" in duplicate_blockers,
        f"ready={duplicate_audit.get('pairing_ready')!r}, blockers={duplicate_audit.get('blocking_missing_count')}",
    )
    add_check(
        checks,
        "missing_method_panel_fails_pairing",
        missing_method_audit.get("pairing_ready") is False
        and "paired reset groups missing declared methods" in missing_method_blockers
        and "per-method counts do not match" in missing_method_blockers,
        f"ready={missing_method_audit.get('pairing_ready')!r}, blockers={missing_method_audit.get('blocking_missing_count')}",
    )
    add_check(
        checks,
        "terminal_sample_mismatch_fails_pairing",
        terminal_mismatch_audit.get("pairing_ready") is False
        and "terminal sample hashes differ within paired reset" in terminal_mismatch_blockers,
        f"ready={terminal_mismatch_audit.get('pairing_ready')!r}, blockers={terminal_mismatch_audit.get('blocking_missing_count')}",
    )
    add_check(
        checks,
        "real_pairing_integrity_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_pairing_integrity_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_pairing_ready": complete_audit.get("pairing_ready") is True,
        "duplicate_pairing_ready": duplicate_audit.get("pairing_ready") is True,
        "missing_method_pairing_ready": missing_method_audit.get("pairing_ready") is True,
        "terminal_mismatch_pairing_ready": terminal_mismatch_audit.get("pairing_ready") is True,
        "missing_manifest_ready": missing_manifest_audit.get("pairing_ready") is True,
        "real_pairing_integrity_report_before": report_before,
        "real_pairing_integrity_report_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External pairing integrity self-test: "
        f"{'PASS' if passed else 'FAIL'}; synthetic_pairing_ready={payload['synthetic_pairing_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

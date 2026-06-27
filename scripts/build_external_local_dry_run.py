from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import validate_external_rollouts as rollout_validator


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"
DRY_RUN = EXTERNAL / "local_dry_run"
OUT_JSON = RESULTS / "external_local_dry_run_metrics.json"
OUT_MD = RESULTS / "external_local_dry_run_metrics.md"

SOURCE_CSV = RESULTS / "cell_metrics.csv"
SCHEMA_PATH = EXTERNAL / "log_schema_v1.json"
FIXED_RISK_BUDGET = 0.15
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
DIAGNOSIS_MAP = {
    "basin_mismatch": "basin_miss",
    "high_barrier": "high_barrier",
    "contact_mode_discontinuity": "contact_transition",
    "model_uncertainty": "unknown",
    "missing_bridge_skill": "unknown",
}


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_source_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.exists():
        raise SystemExit(f"missing {SOURCE_CSV}; run src/run_experiment.py first")
    with SOURCE_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def select_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        task = row["task"]
        method = row["method"]
        if task in TASKS and method in METHODS:
            grouped[(task, method)].append(row)

    selected: dict[tuple[str, str], list[dict[str, str]]] = {}
    missing = []
    for task in TASKS:
        for method in METHODS:
            candidates = sorted(
                grouped.get((task, method), []),
                key=lambda row: (
                    int(row["seed"]),
                    int(row["episode"]),
                    row["regime"],
                    row["split"],
                ),
            )
            if len(candidates) < 30:
                missing.append(f"{task}/{method}: {len(candidates)}")
                continue
            selected[(task, method)] = candidates[:30]
    if missing:
        raise SystemExit(f"not enough local rows for dry run: {missing[:8]}")
    return selected


def make_config(task: str) -> dict[str, Any]:
    return {
        "version": "paper119_external_config_template_v1",
        "config_schema": "external_validation/config_schema_v1.json",
        "not_external_evidence": True,
        "template_only": True,
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "LocalFrozenSuite-v5-DRY-RUN-NOT-EVIDENCE",
        "skill_i": f"{task}_source_skill",
        "skill_j": f"{task}_target_skill",
        "seam_under_test": f"Local dry-run handoff for {task}; generated from frozen local CSV rows.",
        "required_fidelity_checks": [
            "not_applicable_local_dry_run",
            "real_or_accepted_high_fidelity_collection_still_required",
        ],
        "reset_protocol": {
            "paired_resets": True,
            "reset_count": 30,
            "scene_id_template": f"{task}_{{regime}}_{{split}}_seed{{seed}}_episode{{episode}}",
            "initial_state_hash_required": True,
        },
        "observation_interface": {
            "state_logging_required": True,
            "camera_logging_required": False,
            "contact_or_force_logging_required": False,
        },
        "compute_budget": {
            "same_for_all_non_oracle_methods": True,
            "wall_clock_seconds": 0,
            "simulator_query_budget": 0,
        },
        "paired_reset_count": 30,
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "must_log": list(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["required_fields"]),
    }


def make_record(row: dict[str, str], task: str, method: str, dry_episode: int, video_path: Path) -> dict[str, Any]:
    scene_id = f"{task}_{row['regime']}_{row['split']}_seed{row['seed']}_episode{row['episode']}"
    initial_key = f"{task}:{row['regime']}:{row['split']}:{row['seed']}:{row['episode']}:initial"
    terminal_key = f"{task}:{row['regime']}:{row['split']}:{row['seed']}:{row['episode']}:terminal:{method}"
    predicted_risk = float(row["predicted_seam_risk"])
    realized_breach_value = float(row["realized_seam_breach"])
    decision = row["seam_decision"]
    if decision not in {"accept", "repair", "probe", "abstain", "transition"}:
        decision = "abstain"
    return {
        "run_id": "paper119_local_dry_run_not_external_evidence",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "LocalFrozenSuite-v5-DRY-RUN-NOT-EVIDENCE",
        "scene_id": scene_id,
        "episode_index": dry_episode,
        "seed": int(row["seed"]),
        "method": method,
        "skill_i": f"{task}_source_skill",
        "skill_j": f"{task}_target_skill",
        "initial_state_hash": digest_text(initial_key),
        "terminal_sample_set_hash": digest_text(terminal_key),
        "basin_estimate": max(0.0, min(1.0, float(row["basin_alignment"]))),
        "barrier_score": max(0.0, float(row["barrier_violation_rate"])),
        "descent_continuity_score": max(0.0, min(1.0, float(row["descent_continuity"]))),
        "predicted_seam_risk": max(0.0, min(1.0, predicted_risk)),
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "decision": decision,
        "failure_diagnosis": DIAGNOSIS_MAP.get(row["diagnostic_label"], "unknown"),
        "repair_action": "none" if decision not in {"repair", "transition"} else "local_dry_run_bridge",
        "success": bool(int(row["success"])),
        "seam_failure": float(row["seam_failure_rate"]) > FIXED_RISK_BUDGET,
        "barrier_violation": float(row["barrier_violation_rate"]) > FIXED_RISK_BUDGET,
        "damage_or_intervention": float(row["damage_rate"]) > 0.05,
        "composition_cost": max(0.0, float(row["composition_cost"])),
        "realized_seam_breach": realized_breach_value > FIXED_RISK_BUDGET,
        "utility": float(row["composition_utility"]),
        "video_path": rel(video_path),
        "policy_or_config_hash": digest_text(f"{method}:local_dry_run_config"),
    }


def write_dry_run_artifacts(selected: dict[tuple[str, str], list[dict[str, str]]]) -> dict[str, Any]:
    if DRY_RUN.exists():
        for path in sorted(DRY_RUN.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    DRY_RUN.mkdir(parents=True, exist_ok=True)
    (DRY_RUN / "logs").mkdir()
    (DRY_RUN / "configs").mkdir()
    (DRY_RUN / "videos").mkdir()
    (DRY_RUN / "checkpoints").mkdir()
    (DRY_RUN / "implementations").mkdir()

    release_artifacts = {"code": [], "configs": [], "logs": [], "videos": [], "checkpoints": []}
    tasks = []
    for task in TASKS:
        config_path = DRY_RUN / "configs" / f"{task}.json"
        write_json(config_path, make_config(task))
        release_artifacts["configs"].append({"path": rel(config_path), "sha256": file_sha256(config_path)})

        video_dir = DRY_RUN / "videos" / task
        video_dir.mkdir(parents=True, exist_ok=True)
        video_path = video_dir / "placeholder_not_external_evidence.mp4"
        video_path.write_bytes(b"local dry run placeholder; not rollout video evidence\n")
        release_artifacts["videos"].append({"path": rel(video_path), "sha256": file_sha256(video_path)})

        log_path = DRY_RUN / "logs" / f"{task}.jsonl"
        with log_path.open("w", encoding="utf-8") as handle:
            for method in METHODS:
                for dry_episode, row in enumerate(selected[(task, method)]):
                    handle.write(json.dumps(make_record(row, task, method, dry_episode, video_path), sort_keys=True) + "\n")
        release_artifacts["logs"].append({"path": rel(log_path), "sha256": file_sha256(log_path)})
        tasks.append(
            {
                "task_family": task,
                "platform_type": "high_fidelity_sim",
                "platform_name": "LocalFrozenSuite-v5-DRY-RUN-NOT-EVIDENCE",
                "episodes_per_method": 30,
                "log_jsonl": rel(log_path),
                "video_dir": rel(video_dir),
                "config_path": rel(config_path),
                "config_hash": file_sha256(config_path),
                "notes": "Local dry run generated from results/cell_metrics.csv; not external validation evidence.",
            }
        )

    methods = []
    for method in METHODS:
        checkpoint = DRY_RUN / "checkpoints" / f"{method}.sha256"
        checkpoint.write_text(digest_text(f"{method}:local_dry_run_config") + "\n", encoding="utf-8")
        release_artifacts["checkpoints"].append({"path": rel(checkpoint), "sha256": file_sha256(checkpoint)})
        implementation = ""
        if method != "oracle_basin_composer":
            adapter = EXTERNAL / "baselines" / method / "adapter.py"
            implementation = rel(adapter) if adapter.exists() else ""
            if implementation:
                release_artifacts["code"].append({"path": implementation, "sha256": file_sha256(adapter)})
        methods.append(
            {
                "name": method,
                "implementation": implementation if method != "oracle_basin_composer" else "post_hoc_upper_bound",
                "checkpoint_or_config_path": rel(checkpoint),
                "checkpoint_or_config_hash": file_sha256(checkpoint),
            }
        )

    return {
        "version": "external_validation_v1",
        "not_external_evidence": True,
        "local_dry_run_only": True,
        "log_schema": "external_validation/log_schema_v1.json",
        "route": "high_fidelity_sim",
        "claim": "Local dry run of the external evidence schema; not a robot or accepted high-fidelity validation claim.",
        "shared_skill_library": True,
        "same_initial_states": True,
        "same_observation_interface": True,
        "same_compute_budget": True,
        "paired_resets": True,
        "tasks": tasks,
        "methods": methods,
        "metrics": {},
        "ablations": {
            "basin_overlap": False,
            "barrier_height": False,
            "descent_continuity": False,
            "risk_calibration": False,
            "seam_repair": False,
        },
        "release_artifacts": release_artifacts,
    }


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = payload["summary"]
    lines = [
        "# External Local Dry-Run Metrics",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Manifest: `{payload['manifest']}`.",
        f"Records: `{summary.get('episodes', 0)}`.",
        f"Task families: `{summary.get('external_task_families', 0)}`.",
        f"Strongest dry-run baseline: `{summary.get('strongest_external_baseline')}`.",
        "",
        "This dry run converts frozen local CSV rows into the external JSONL schema and recomputes metrics from those logs. It is a plumbing and reproducibility check only. It is not real robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for `external_validation/manifest.json`.",
        "",
        "## Metric Summary",
        "",
        f"- External-style success margin: `{summary.get('external_success_margin')}`.",
        f"- External-style utility margin: `{summary.get('external_utility_margin')}`.",
        f"- Paired win rate: `{summary.get('paired_win_rate')}`.",
        f"- Fixed-risk coverage: `{summary.get('fixed_risk_coverage')}`.",
        f"- Fixed-risk breach: `{summary.get('fixed_risk_breach')}`.",
        f"- Positive task families: `{summary.get('positive_task_families')}/{summary.get('external_task_families')}`.",
        "",
        "## Threshold Checks",
        "",
    ]
    for check in payload["threshold_checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` {check['message']}")
    lines.extend(["", "## Schema Errors", ""])
    if payload["schema_errors"]:
        for error in payload["schema_errors"][:100]:
            lines.append(f"- {error}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = load_source_rows()
    selected = select_rows(rows)
    manifest = write_dry_run_artifacts(selected)
    manifest_path = DRY_RUN / "manifest.json"
    write_json(manifest_path, manifest)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    records, errors = rollout_validator.load_records(
        manifest,
        schema,
        check_video_paths=True,
        max_errors=100,
    )
    summary = rollout_validator.summarize(records, schema) if records else {"version": "external_rollout_metrics_v1", "episodes": 0}
    threshold_checks = rollout_validator.threshold_checks(summary, schema) if records else []
    passed = not errors and bool(records) and all(check.passed for check in threshold_checks)
    manifest["metrics"] = {
        "external_success_margin": summary.get("external_success_margin"),
        "external_utility_margin": summary.get("external_utility_margin"),
        "paired_win_rate": summary.get("paired_win_rate"),
        "fixed_risk_budget": summary.get("fixed_risk_budget"),
        "fixed_risk_breach": summary.get("fixed_risk_breach"),
        "fixed_risk_coverage": summary.get("fixed_risk_coverage"),
        "positive_task_families": summary.get("positive_task_families"),
        "external_task_families": summary.get("external_task_families"),
        "oracle_reported": "oracle_basin_composer" in summary.get("methods", []),
        "oracle_stronger_or_saturated_explained": True,
    }
    write_json(manifest_path, manifest)

    payload = {
        "version": "external_local_dry_run_metrics_v1",
        "passed": passed,
        "not_external_evidence": True,
        "source": rel(SOURCE_CSV),
        "manifest": rel(manifest_path),
        "schema_errors": errors,
        "threshold_checks": [{"passed": check.passed, "message": check.message} for check in threshold_checks],
        "summary": summary,
    }
    write_report(payload)
    status = "PASS" if passed else "FAIL"
    print(f"External local dry run: {status}; records={summary.get('episodes', 0)}; not_evidence=True")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

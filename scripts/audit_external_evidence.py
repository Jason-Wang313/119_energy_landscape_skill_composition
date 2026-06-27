from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CONTRACT_DIR = ROOT / "external_validation"
MANIFEST = CONTRACT_DIR / "manifest.json"
TEMPLATE = CONTRACT_DIR / "manifest_template.json"
AUDIT_JSON = RESULTS / "external_evidence_audit.json"
AUDIT_MD = RESULTS / "external_evidence_audit.md"
LOG_SCHEMA = CONTRACT_DIR / "log_schema_v1.json"
ROLLOUT_VALIDATOR = ROOT / "scripts" / "validate_external_rollouts.py"
ROLLOUT_METRICS_JSON = RESULTS / "external_rollout_metrics.json"
BASELINE_CONTRACT_JSON = RESULTS / "external_baseline_contract_audit.json"
ADAPTER_SCAFFOLD_JSON = RESULTS / "external_adapter_scaffold_audit.json"
ADAPTER_CONTRACT_JSON = RESULTS / "external_adapter_contract_audit.json"
ADAPTER_CONTRACT_EVIDENCE_JSON = RESULTS / "external_adapter_contract_evidence_audit.json"
CONFIG_SCHEMA = CONTRACT_DIR / "config_schema_v1.json"
CONFIG_TEMPLATE_AUDIT_JSON = RESULTS / "external_config_template_audit.json"
CONFIG_EVIDENCE_AUDIT_JSON = RESULTS / "external_config_evidence_audit.json"
FIDELITY_ACCEPTANCE_AUDIT_JSON = RESULTS / "external_fidelity_acceptance_audit.json"
BLIND_EVAL_AUDIT_JSON = RESULTS / "external_blind_eval_audit.json"
METRIC_TOLERANCE = 1e-9

REQUIRED_METHODS = {
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
}

NON_ORACLE_METHODS = REQUIRED_METHODS - {"oracle_basin_composer"}

VALID_TASKS = {
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "mobile_push_then_grasp",
    "tool_use_handover",
    "door_open_navigation",
    "cable_route_insert",
}

REQUIRED_LOG_FIELDS = {
    "run_id",
    "task_family",
    "platform_type",
    "platform_name",
    "scene_id",
    "episode_index",
    "seed",
    "method",
    "skill_i",
    "skill_j",
    "initial_state_hash",
    "terminal_sample_set_hash",
    "basin_estimate",
    "barrier_score",
    "descent_continuity_score",
    "predicted_seam_risk",
    "fixed_risk_budget",
    "decision",
    "failure_diagnosis",
    "repair_action",
    "success",
    "seam_failure",
    "barrier_violation",
    "damage_or_intervention",
    "composition_cost",
    "realized_seam_breach",
    "utility",
    "video_path",
    "policy_or_config_hash",
}

THRESHOLDS = {
    "external_success_margin": 0.05,
    "external_utility_margin": 0.08,
    "paired_win_rate": 0.70,
    "fixed_risk_breach": 0.02,
    "fixed_risk_coverage": 0.55,
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def has_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Fa-f0-9]{64}", value))


def is_scaffold_implementation(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = rel_path(value)
    if path.is_dir():
        metadata = path / "adapter_metadata.json"
        if metadata.exists():
            try:
                payload = read_json(metadata)
            except SystemExit:
                return True
            return payload.get("scaffold_only") is True or payload.get("not_external_evidence") is True
        return False
    if path.is_file():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return "SCAFFOLD_ONLY = True" in text or "NOT_EXTERNAL_EVIDENCE = True" in text
    return False


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str, *, blocking: bool = True) -> None:
    checks.append({"name": name, "passed": bool(passed), "blocking": blocking, "detail": detail})


def metric_value(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number else None


def route_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"real_robot": 0, "high_fidelity_sim": 0, "mixed": 0}
    seen: set[tuple[str, str]] = set()
    for task in tasks:
        family = str(task.get("task_family", ""))
        platform = str(task.get("platform_type", ""))
        key = (family, platform)
        if key in seen:
            continue
        seen.add(key)
        if platform in counts:
            counts[platform] += 1
    counts["mixed"] = counts["real_robot"] + counts["high_fidelity_sim"]
    return counts


def validate_log_sample(log_path: Path) -> tuple[bool, str]:
    if not log_path.exists():
        return False, f"missing log file: {log_path}"
    missing_by_line: list[str] = []
    line_count = 0
    with log_path.open(encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            line_count += 1
            if line_count > 50:
                break
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                return False, f"invalid JSONL in {log_path} line {line_count}: {exc}"
            missing = sorted(REQUIRED_LOG_FIELDS - set(record))
            if missing:
                missing_by_line.append(f"line {line_count}: {missing[:6]}")
    if line_count == 0:
        return False, f"empty log file: {log_path}"
    if missing_by_line:
        return False, "; ".join(missing_by_line[:3])
    return True, f"checked {min(line_count, 50)} JSONL records"


def audit_manifest(manifest: dict[str, Any], manifest_exists: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    add_check(checks, "manifest_exists", manifest_exists, str(MANIFEST) if manifest_exists else "external_validation/manifest.json is missing")
    add_check(checks, "template_exists", TEMPLATE.exists(), str(TEMPLATE))
    add_check(checks, "log_schema_exists", LOG_SCHEMA.exists(), str(LOG_SCHEMA))
    add_check(checks, "rollout_validator_exists", ROLLOUT_VALIDATOR.exists(), str(ROLLOUT_VALIDATOR))
    rollout_metrics_exists = ROLLOUT_METRICS_JSON.exists()
    add_check(checks, "external_rollout_metrics_exists", rollout_metrics_exists, str(ROLLOUT_METRICS_JSON))
    rollout_payload = read_json(ROLLOUT_METRICS_JSON) if rollout_metrics_exists else {}
    rollout_summary = rollout_payload.get("summary", {}) if isinstance(rollout_payload, dict) else {}
    rollout_summary = rollout_summary if isinstance(rollout_summary, dict) else {}
    add_check(
        checks,
        "external_rollout_metrics_version",
        rollout_summary.get("version") == "external_rollout_metrics_v1",
        f"version={rollout_summary.get('version')!r}",
    )
    fidelity_acceptance_exists = FIDELITY_ACCEPTANCE_AUDIT_JSON.exists()
    fidelity_acceptance = read_json(FIDELITY_ACCEPTANCE_AUDIT_JSON) if fidelity_acceptance_exists else {}
    add_check(checks, "fidelity_acceptance_audit_exists", fidelity_acceptance_exists, str(FIDELITY_ACCEPTANCE_AUDIT_JSON))
    add_check(
        checks,
        "fidelity_acceptance_audit_version",
        fidelity_acceptance.get("version") == "external_fidelity_acceptance_audit_v1",
        f"version={fidelity_acceptance.get('version')!r}",
    )
    add_check(
        checks,
        "fidelity_acceptance_contract_passed",
        fidelity_acceptance.get("passed") is True,
        f"passed={fidelity_acceptance.get('passed')!r}",
    )
    add_check(
        checks,
        "external_fidelity_acceptance_ready",
        fidelity_acceptance.get("acceptance_ready") is True,
        f"acceptance_ready={fidelity_acceptance.get('acceptance_ready')!r}, readiness_state={fidelity_acceptance.get('readiness_state')!r}",
    )
    blind_eval_exists = BLIND_EVAL_AUDIT_JSON.exists()
    blind_eval = read_json(BLIND_EVAL_AUDIT_JSON) if blind_eval_exists else {}
    add_check(checks, "blind_eval_audit_exists", blind_eval_exists, str(BLIND_EVAL_AUDIT_JSON))
    add_check(
        checks,
        "blind_eval_audit_version",
        blind_eval.get("version") == "external_blind_eval_plan_v1",
        f"version={blind_eval.get('version')!r}",
    )
    add_check(
        checks,
        "blind_eval_plan_passed",
        blind_eval.get("passed") is True,
        f"passed={blind_eval.get('passed')!r}",
    )
    add_check(
        checks,
        "blind_eval_no_method_leak",
        any(
            check.get("name") == "blinded_sheet_has_no_method_names" and check.get("passed") is True
            for check in blind_eval.get("checks", []) or []
        ),
        "blinded operator sheet checked for method-name leakage",
    )
    baseline_contract_exists = BASELINE_CONTRACT_JSON.exists()
    baseline_contract = read_json(BASELINE_CONTRACT_JSON) if baseline_contract_exists else {}
    add_check(checks, "baseline_contract_exists", baseline_contract_exists, str(BASELINE_CONTRACT_JSON))
    add_check(
        checks,
        "baseline_contract_version",
        baseline_contract.get("version") == "external_baseline_contract_audit_v1",
        f"version={baseline_contract.get('version')!r}",
    )
    add_check(
        checks,
        "baseline_contract_is_not_evidence",
        baseline_contract.get("not_external_evidence") is True,
        f"not_external_evidence={baseline_contract.get('not_external_evidence')!r}",
    )
    adapter_scaffold_exists = ADAPTER_SCAFFOLD_JSON.exists()
    adapter_scaffold = read_json(ADAPTER_SCAFFOLD_JSON) if adapter_scaffold_exists else {}
    add_check(checks, "adapter_scaffold_exists", adapter_scaffold_exists, str(ADAPTER_SCAFFOLD_JSON))
    add_check(
        checks,
        "adapter_scaffold_version",
        adapter_scaffold.get("version") == "external_adapter_scaffold_audit_v1",
        f"version={adapter_scaffold.get('version')!r}",
    )
    add_check(
        checks,
        "adapter_scaffold_is_not_evidence",
        adapter_scaffold.get("not_external_evidence") is True,
        f"not_external_evidence={adapter_scaffold.get('not_external_evidence')!r}",
    )
    adapter_contract_exists = ADAPTER_CONTRACT_JSON.exists()
    adapter_contract = read_json(ADAPTER_CONTRACT_JSON) if adapter_contract_exists else {}
    add_check(checks, "adapter_contract_exists", adapter_contract_exists, str(ADAPTER_CONTRACT_JSON))
    add_check(
        checks,
        "adapter_contract_version",
        adapter_contract.get("version") == "external_adapter_contract_audit_v1",
        f"version={adapter_contract.get('version')!r}",
    )
    add_check(
        checks,
        "adapter_contract_passed",
        adapter_contract.get("passed") is True,
        f"passed={adapter_contract.get('passed')!r}, adapters={adapter_contract.get('adapter_count')!r}",
    )
    add_check(
        checks,
        "adapter_contract_is_not_evidence",
        adapter_contract.get("not_external_evidence") is True,
        f"not_external_evidence={adapter_contract.get('not_external_evidence')!r}",
    )
    adapter_contract_evidence_exists = ADAPTER_CONTRACT_EVIDENCE_JSON.exists()
    adapter_contract_evidence = read_json(ADAPTER_CONTRACT_EVIDENCE_JSON) if adapter_contract_evidence_exists else {}
    add_check(checks, "adapter_contract_evidence_exists", adapter_contract_evidence_exists, str(ADAPTER_CONTRACT_EVIDENCE_JSON))
    add_check(
        checks,
        "external_adapter_contract_evidence_passed",
        adapter_contract_evidence.get("passed") is True,
        f"passed={adapter_contract_evidence.get('passed')!r}, adapters={adapter_contract_evidence.get('adapter_count')!r}",
    )
    config_schema_exists = CONFIG_SCHEMA.exists()
    add_check(checks, "config_schema_exists", config_schema_exists, str(CONFIG_SCHEMA))
    config_template_audit_exists = CONFIG_TEMPLATE_AUDIT_JSON.exists()
    config_template_audit = read_json(CONFIG_TEMPLATE_AUDIT_JSON) if config_template_audit_exists else {}
    add_check(checks, "config_template_audit_exists", config_template_audit_exists, str(CONFIG_TEMPLATE_AUDIT_JSON))
    add_check(
        checks,
        "config_template_audit_version",
        config_template_audit.get("version") == "external_config_template_audit_v1",
        f"version={config_template_audit.get('version')!r}",
    )
    add_check(
        checks,
        "config_template_audit_passed",
        config_template_audit.get("passed") is True,
        f"passed={config_template_audit.get('passed')!r}",
    )
    add_check(
        checks,
        "config_template_audit_not_evidence",
        config_template_audit.get("not_external_evidence") is True,
        f"not_external_evidence={config_template_audit.get('not_external_evidence')!r}",
    )
    config_evidence_audit_exists = CONFIG_EVIDENCE_AUDIT_JSON.exists()
    config_evidence_audit = read_json(CONFIG_EVIDENCE_AUDIT_JSON) if config_evidence_audit_exists else {}
    add_check(checks, "config_evidence_audit_exists", config_evidence_audit_exists, str(CONFIG_EVIDENCE_AUDIT_JSON))
    add_check(
        checks,
        "external_config_evidence_passed",
        config_evidence_audit.get("passed") is True,
        f"passed={config_evidence_audit.get('passed')!r}, configs={config_evidence_audit.get('config_count')!r}",
    )

    version = manifest.get("version")
    add_check(checks, "manifest_version", version == "external_validation_v1", f"version={version!r}")
    declared_schema = str(manifest.get("log_schema", ""))
    add_check(
        checks,
        "manifest_declares_log_schema",
        declared_schema == "external_validation/log_schema_v1.json",
        f"log_schema={declared_schema!r}",
    )

    route = str(manifest.get("route", ""))
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    counts = route_counts([task for task in tasks if isinstance(task, dict)])
    route_pass = (
        (route == "real_robot" and counts["real_robot"] >= 3)
        or (route == "high_fidelity_sim" and counts["high_fidelity_sim"] >= 4)
        or (route == "mixed" and counts["real_robot"] >= 2 and counts["high_fidelity_sim"] >= 2)
    )
    add_check(checks, "validation_route", route_pass, f"route={route!r}, counts={counts}")

    for flag in ("shared_skill_library", "same_initial_states", "same_observation_interface", "same_compute_budget", "paired_resets"):
        add_check(checks, flag, manifest.get(flag) is True, f"{flag}={manifest.get(flag)!r}")

    task_families = [str(task.get("task_family", "")) for task in tasks if isinstance(task, dict)]
    invalid_tasks = sorted({task for task in task_families if task not in VALID_TASKS})
    add_check(checks, "valid_task_families", not invalid_tasks and bool(task_families), f"invalid={invalid_tasks}, families={sorted(set(task_families))}")

    weak_episode_tasks = [
        str(task.get("task_family", "unknown"))
        for task in tasks
        if isinstance(task, dict) and int(task.get("episodes_per_method", 0) or 0) < 30
    ]
    add_check(checks, "episodes_per_method", not weak_episode_tasks and bool(tasks), f"weak={weak_episode_tasks}")

    log_results = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        log_value = str(task.get("log_jsonl", ""))
        if not log_value:
            log_results.append((False, f"{task.get('task_family', 'unknown')}: missing log_jsonl"))
            continue
        ok, detail = validate_log_sample(rel_path(log_value))
        log_results.append((ok, f"{task.get('task_family', 'unknown')}: {detail}"))
    add_check(
        checks,
        "episode_log_schema",
        bool(log_results) and all(ok for ok, _ in log_results),
        "; ".join(detail for _, detail in log_results[:4]) if log_results else "no task logs declared",
    )

    video_missing = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        video_dir = str(task.get("video_dir", ""))
        if not video_dir or not rel_path(video_dir).exists():
            video_missing.append(str(task.get("task_family", "unknown")))
    add_check(checks, "task_video_dirs", bool(tasks) and not video_missing, f"missing={video_missing}")

    methods = manifest.get("methods", [])
    methods = methods if isinstance(methods, list) else []
    method_names = {str(method.get("name", "")) for method in methods if isinstance(method, dict)}
    missing_methods = sorted(REQUIRED_METHODS - method_names)
    add_check(checks, "required_methods", not missing_methods, f"missing={missing_methods}")

    missing_impl_set = set(NON_ORACLE_METHODS - method_names)
    for method in methods:
        if not isinstance(method, dict):
            continue
        name = str(method.get("name", "unknown"))
        implementation = str(method.get("implementation", "")).strip()
        if name != "oracle_basin_composer" and (not implementation or is_scaffold_implementation(implementation)):
            missing_impl_set.add(name)
    missing_impl = sorted(missing_impl_set)
    add_check(checks, "independent_method_implementations", bool(methods) and not missing_impl, f"missing={missing_impl}")

    metrics = manifest.get("metrics", {})
    metrics = metrics if isinstance(metrics, dict) else {}
    parsed_metrics = {name: metric_value(metrics.get(name)) for name in THRESHOLDS}
    metric_checks = {
        "external_success_margin": parsed_metrics["external_success_margin"] is not None
        and parsed_metrics["external_success_margin"] >= THRESHOLDS["external_success_margin"],
        "external_utility_margin": parsed_metrics["external_utility_margin"] is not None
        and parsed_metrics["external_utility_margin"] >= THRESHOLDS["external_utility_margin"],
        "paired_win_rate": parsed_metrics["paired_win_rate"] is not None
        and parsed_metrics["paired_win_rate"] >= THRESHOLDS["paired_win_rate"],
        "fixed_risk_breach": parsed_metrics["fixed_risk_breach"] is not None
        and parsed_metrics["fixed_risk_breach"] <= THRESHOLDS["fixed_risk_breach"],
        "fixed_risk_coverage": parsed_metrics["fixed_risk_coverage"] is not None
        and parsed_metrics["fixed_risk_coverage"] >= THRESHOLDS["fixed_risk_coverage"],
    }
    for name, passed in metric_checks.items():
        threshold = THRESHOLDS[name]
        add_check(checks, name, passed, f"value={metrics.get(name)!r}, threshold={threshold}")

    positive = int(metrics.get("positive_task_families", 0) or 0)
    total = int(metrics.get("external_task_families", 0) or 0)
    add_check(checks, "positive_task_family_coverage", total >= 4 and positive >= 3, f"positive={positive}, total={total}")
    rollout_passed = rollout_payload.get("passed") is True if isinstance(rollout_payload, dict) else False
    add_check(
        checks,
        "external_rollout_metrics_passed",
        rollout_passed,
        f"passed={rollout_payload.get('passed') if isinstance(rollout_payload, dict) else None!r}, episodes={rollout_summary.get('episodes')!r}",
    )
    metric_mismatches = []
    for name in (
        "external_success_margin",
        "external_utility_margin",
        "paired_win_rate",
        "fixed_risk_breach",
        "fixed_risk_coverage",
        "positive_task_families",
        "external_task_families",
    ):
        manifest_number = metric_value(metrics.get(name))
        rollout_number = metric_value(rollout_summary.get(name))
        if manifest_number is None or rollout_number is None:
            metric_mismatches.append(f"{name}: manifest={metrics.get(name)!r}, rollout={rollout_summary.get(name)!r}")
        elif abs(manifest_number - rollout_number) > METRIC_TOLERANCE:
            metric_mismatches.append(f"{name}: manifest={manifest_number}, rollout={rollout_number}")
    add_check(
        checks,
        "manifest_metrics_match_rollout",
        rollout_passed and not metric_mismatches,
        "; ".join(metric_mismatches[:4]) if metric_mismatches else "manifest metrics match recomputed rollout metrics",
    )
    add_check(checks, "oracle_reported", metrics.get("oracle_reported") is True, f"oracle_reported={metrics.get('oracle_reported')!r}")
    add_check(
        checks,
        "oracle_boundary",
        metrics.get("oracle_stronger_or_saturated_explained") is True,
        f"oracle_stronger_or_saturated_explained={metrics.get('oracle_stronger_or_saturated_explained')!r}",
    )

    ablations = manifest.get("ablations", {})
    ablations = ablations if isinstance(ablations, dict) else {}
    required_ablations = ["basin_overlap", "barrier_height", "descent_continuity", "risk_calibration", "seam_repair"]
    missing_ablations = [name for name in required_ablations if ablations.get(name) is not True]
    add_check(checks, "external_ablations", not missing_ablations, f"missing={missing_ablations}")

    release_artifacts = manifest.get("release_artifacts", {})
    release_artifacts = release_artifacts if isinstance(release_artifacts, dict) else {}
    for artifact_type in ("code", "configs", "logs", "videos", "checkpoints"):
        entries = release_artifacts.get(artifact_type, [])
        entries = entries if isinstance(entries, list) else []
        missing_paths = []
        missing_hashes = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            path = str(entry.get("path", ""))
            if not path or not rel_path(path).exists():
                missing_paths.append(path or "<empty>")
            if not has_sha(entry.get("sha256", "")):
                missing_hashes.append(path or "<empty>")
        add_check(
            checks,
            f"release_{artifact_type}",
            bool(entries) and not missing_paths and not missing_hashes,
            f"entries={len(entries)}, missing_paths={missing_paths}, missing_sha256={missing_hashes}",
        )

    blocking_failures = [check for check in checks if check["blocking"] and not check["passed"]]
    return {
        "version": "external_evidence_audit_v1",
        "manifest_path": str(MANIFEST),
        "manifest_exists": manifest_exists,
        "submission_ready": not blocking_failures,
        "blocking_failures": blocking_failures,
        "checks": checks,
    }


def write_markdown(audit: dict[str, Any]) -> None:
    lines = [
        "# External Evidence Audit",
        "",
        f"Submission ready: `{str(audit['submission_ready']).lower()}`.",
        f"Manifest: `{audit['manifest_path']}`.",
        "",
        "## Blocking Failures",
        "",
    ]
    failures = audit["blocking_failures"]
    if failures:
        for failure in failures:
            lines.append(f"- `{failure['name']}`: {failure['detail']}")
    else:
        lines.append("- none")
    lines.extend(["", "## All Checks", ""])
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit external validation evidence for Paper 119.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless the external evidence is submission-ready.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    manifest_exists = MANIFEST.exists()
    manifest = read_json(MANIFEST) if manifest_exists else {}
    audit = audit_manifest(manifest, manifest_exists)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(audit)

    status = "READY" if audit["submission_ready"] else "NOT_READY"
    print(f"External evidence audit: {status}; blocking_failures={len(audit['blocking_failures'])}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    if args.strict and not audit["submission_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

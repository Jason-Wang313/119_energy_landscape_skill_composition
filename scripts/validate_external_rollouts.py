from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_MANIFEST = EXTERNAL / "manifest.json"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
OUT_JSON = RESULTS / "external_rollout_metrics.json"
OUT_MD = RESULTS / "external_rollout_metrics.md"

PRIMARY_METHOD = "barrier_certified_energy_composer_v5"
ORACLE_METHOD = "oracle_basin_composer"
HEX64 = re.compile(r"^[A-Fa-f0-9]{64}$")
MIN_STRICT_VIDEO_BYTES = 512
FORBIDDEN_VIDEO_PATH_FRAGMENTS = {
    "diagnostic",
    "fallback",
    "local_dry_run",
    "pilot_runtime_guard",
    "pilot_smoke",
    "placeholder_not_external_evidence",
    "render_video_preflight",
    "staging",
    "backup",
}


@dataclass
class ValidationResult:
    passed: bool
    message: str


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_video_path(
    video_path_value: str,
    *,
    task_family: str,
    manifest_video_dirs: dict[str, Path],
    strict_video_evidence: bool,
    line_id: str,
) -> list[str]:
    errors: list[str] = []
    path = rel_path(video_path_value)
    if not path.exists():
        return [f"{line_id}: video_path does not exist: {video_path_value}"]
    if not strict_video_evidence:
        return []
    if not path.is_file():
        errors.append(f"{line_id}: strict video_path must be a file: {video_path_value}")
    if path.suffix.lower() != ".mp4":
        errors.append(f"{line_id}: strict video_path must end in .mp4: {video_path_value}")
    lowered_parts = {part.lower() for part in path.parts}
    lowered_text = str(path).replace("\\", "/").lower()
    forbidden_hits = sorted(
        fragment
        for fragment in FORBIDDEN_VIDEO_PATH_FRAGMENTS
        if fragment in lowered_parts or fragment in lowered_text
    )
    if forbidden_hits:
        errors.append(f"{line_id}: strict video_path contains forbidden non-evidence fragment(s) {forbidden_hits}: {video_path_value}")
    expected_dir = manifest_video_dirs.get(task_family)
    if expected_dir is not None and not is_under(path, expected_dir):
        errors.append(f"{line_id}: strict video_path must be under manifest video_dir {rel(expected_dir)}: {video_path_value}")
    diagnostic_sidecar = Path(str(path) + ".diagnostic.json")
    if diagnostic_sidecar.exists():
        errors.append(f"{line_id}: strict video_path has diagnostic fallback sidecar: {rel(diagnostic_sidecar)}")
    if path.exists() and path.is_file():
        size = path.stat().st_size
        if size < MIN_STRICT_VIDEO_BYTES:
            errors.append(f"{line_id}: strict video_path is too small for reviewable MP4 evidence: {size} bytes")
        with path.open("rb") as handle:
            header = handle.read(16)
        if len(header) < 12 or header[4:8] != b"ftyp":
            errors.append(f"{line_id}: strict video_path is not MP4-like evidence with an ftyp box: {video_path_value}")
    return errors


def as_float(record: dict[str, Any], field: str, errors: list[str], line_id: str) -> float | None:
    value = record.get(field)
    if isinstance(value, bool):
        errors.append(f"{line_id}: {field} must be numeric, got boolean")
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    errors.append(f"{line_id}: {field} must be finite numeric")
    return None


def as_bool(record: dict[str, Any], field: str, errors: list[str], line_id: str) -> bool | None:
    value = record.get(field)
    if isinstance(value, bool):
        return value
    errors.append(f"{line_id}: {field} must be boolean")
    return None


def validate_record(
    record: dict[str, Any],
    *,
    line_id: str,
    schema: dict[str, Any],
    manifest_methods: set[str],
    manifest_tasks: set[str],
    check_video_paths: bool,
    manifest_task_specs: dict[str, dict[str, Any]] | None = None,
    manifest_task_configs: dict[str, dict[str, Any]] | None = None,
    manifest_video_dirs: dict[str, Path] | None = None,
    manifest_method_hashes: dict[str, str] | None = None,
    strict_video_evidence: bool = False,
) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required_fields", {}))
    missing = sorted(required - set(record))
    if missing:
        return [f"{line_id}: missing required fields {missing}"]

    for field in (
        "run_id",
        "task_family",
        "platform_type",
        "platform_name",
        "scene_id",
        "method",
        "skill_i",
        "skill_j",
        "decision",
        "failure_diagnosis",
        "repair_action",
        "video_path",
    ):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{line_id}: {field} must be non-empty string")

    for field in ("initial_state_hash", "terminal_sample_set_hash", "policy_or_config_hash"):
        value = record.get(field)
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            errors.append(f"{line_id}: {field} must be 64-character SHA256")

    for field in ("seed", "episode_index"):
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append(f"{line_id}: {field} must be integer >= 0")

    numeric_values: dict[str, float] = {}
    for field in ("basin_estimate", "descent_continuity_score", "predicted_seam_risk", "fixed_risk_budget"):
        value = as_float(record, field, errors, line_id)
        if value is not None and not (0.0 <= value <= 1.0):
            errors.append(f"{line_id}: {field}={value} outside [0, 1]")
        if value is not None:
            numeric_values[field] = value

    barrier_score = as_float(record, "barrier_score", errors, line_id)
    if barrier_score is not None and barrier_score < 0:
        errors.append(f"{line_id}: barrier_score={barrier_score} must be >= 0")
    composition_cost = as_float(record, "composition_cost", errors, line_id)
    if composition_cost is not None and composition_cost < 0:
        errors.append(f"{line_id}: composition_cost={composition_cost} must be >= 0")
    as_float(record, "utility", errors, line_id)

    for field in ("success", "seam_failure", "barrier_violation", "damage_or_intervention", "realized_seam_breach"):
        as_bool(record, field, errors, line_id)

    allowed = schema.get("allowed_values", {})
    for field, values in allowed.items():
        if record.get(field) not in set(values):
            errors.append(f"{line_id}: {field}={record.get(field)!r} not in {values}")

    if record.get("task_family") not in manifest_tasks:
        errors.append(f"{line_id}: task_family={record.get('task_family')!r} not declared in manifest")
    if record.get("method") not in manifest_methods:
        errors.append(f"{line_id}: method={record.get('method')!r} not declared in manifest")
    task_name = str(record.get("task_family", ""))
    task_spec = (manifest_task_specs or {}).get(task_name, {})
    for field in ("platform_type", "platform_name"):
        declared = str(task_spec.get(field, "")).strip()
        if declared and str(record.get(field, "")).strip() != declared:
            errors.append(f"{line_id}: {field} must match manifest task {field} for task={task_name!r}")
    task_config = (manifest_task_configs or {}).get(task_name, {})
    for field in ("skill_i", "skill_j"):
        declared = str(task_config.get(field, "")).strip()
        if declared and str(record.get(field, "")).strip() != declared:
            if field == "skill_i":
                errors.append(f"{line_id}: skill_i must match manifest task config for task={task_name!r}")
            else:
                errors.append(f"{line_id}: skill_j must match manifest task config for task={task_name!r}")
    if "fixed_risk_budget" in task_config and "fixed_risk_budget" in numeric_values:
        config_budget = task_config.get("fixed_risk_budget")
        if not isinstance(config_budget, bool) and isinstance(config_budget, (int, float)):
            if abs(numeric_values["fixed_risk_budget"] - float(config_budget)) > 1e-12:
                errors.append(f"{line_id}: fixed_risk_budget must match manifest task config for task={task_name!r}")
    method_name = str(record.get("method", ""))
    declared_policy_hash = (manifest_method_hashes or {}).get(method_name, "")
    record_policy_hash = str(record.get("policy_or_config_hash", ""))
    if declared_policy_hash:
        if not HEX64.fullmatch(declared_policy_hash):
            errors.append(
                f"{line_id}: manifest checkpoint_or_config_hash for method={method_name!r} must be 64-character SHA256"
            )
        elif record_policy_hash.lower() != declared_policy_hash.lower():
            errors.append(
                f"{line_id}: policy_or_config_hash must match manifest checkpoint_or_config_hash for method={method_name!r}"
            )

    if check_video_paths:
        video_path = str(record.get("video_path", ""))
        if video_path:
            errors.extend(
                validate_video_path(
                    video_path,
                    task_family=str(record.get("task_family", "")),
                    manifest_video_dirs=manifest_video_dirs or {},
                    strict_video_evidence=strict_video_evidence,
                    line_id=line_id,
                )
            )

    return errors


def load_records(
    manifest: dict[str, Any],
    schema: dict[str, Any],
    *,
    check_video_paths: bool,
    strict_video_evidence: bool = False,
    max_errors: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    methods = manifest.get("methods", [])
    methods = methods if isinstance(methods, list) else []
    manifest_tasks = {str(task.get("task_family", "")) for task in tasks if isinstance(task, dict)}
    manifest_task_specs = {
        str(task.get("task_family", "")): task
        for task in tasks
        if isinstance(task, dict) and str(task.get("task_family", ""))
    }
    manifest_methods = {str(method.get("name", "")) for method in methods if isinstance(method, dict)}
    manifest_method_hashes = {
        str(method.get("name", "")): str(method.get("checkpoint_or_config_hash", "")).strip()
        for method in methods
        if isinstance(method, dict)
        and str(method.get("name", ""))
        and str(method.get("checkpoint_or_config_hash", "")).strip()
    }
    manifest_video_dirs = {
        str(task.get("task_family", "")): rel_path(str(task.get("video_dir", "")))
        for task in tasks
        if isinstance(task, dict) and str(task.get("task_family", "")) and str(task.get("video_dir", ""))
    }

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_record_keys: dict[tuple[Any, ...], str] = {}
    seen_video_paths: dict[str, str] = {}
    manifest_task_configs: dict[str, dict[str, Any]] = {}
    for task_family, task in manifest_task_specs.items():
        config_path_value = str(task.get("config_path", "")).strip()
        declared_config_hash = str(task.get("config_hash", "")).strip()
        if not config_path_value and not declared_config_hash:
            continue
        if not config_path_value:
            errors.append(f"{task_family}: manifest declares config_hash without config_path")
            continue
        config_path = rel_path(config_path_value)
        if not config_path.exists():
            errors.append(f"{task_family}: missing config_path {config_path_value}")
            continue
        actual_config_hash = sha256_file(config_path)
        if declared_config_hash:
            if not HEX64.fullmatch(declared_config_hash):
                errors.append(f"{task_family}: config_hash must be 64-character SHA256")
            elif actual_config_hash.lower() != declared_config_hash.lower():
                errors.append(f"{task_family}: config_hash does not match config_path {config_path_value}")
        config_payload = read_json(config_path)
        if not isinstance(config_payload, dict):
            errors.append(f"{task_family}: config_path must contain a JSON object")
        else:
            manifest_task_configs[task_family] = config_payload
        if len(errors) >= max_errors:
            return records, errors
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("manifest task entry is not an object")
            continue
        log_value = str(task.get("log_jsonl", ""))
        if not log_value:
            errors.append(f"{task.get('task_family', 'unknown')}: missing log_jsonl")
            continue
        log_path = rel_path(log_value)
        if not log_path.exists():
            errors.append(f"{task.get('task_family', 'unknown')}: missing log file {log_value}")
            continue
        with log_path.open(encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                line_id = f"{log_value}:{line_number}"
                try:
                    record = json.loads(raw)
                except json.JSONDecodeError as exc:
                    errors.append(f"{line_id}: invalid JSON: {exc}")
                    if len(errors) >= max_errors:
                        return records, errors
                    continue
                if not isinstance(record, dict):
                    errors.append(f"{line_id}: JSONL line must be an object")
                    if len(errors) >= max_errors:
                        return records, errors
                    continue
                record_key = (
                    record.get("run_id"),
                    record.get("task_family"),
                    record.get("method"),
                    record.get("seed"),
                    record.get("episode_index"),
                )
                if all(item is not None and item != "" for item in record_key):
                    prior_line = seen_record_keys.get(record_key)
                    if prior_line:
                        errors.append(f"{line_id}: duplicate rollout record identity also seen at {prior_line}")
                    else:
                        seen_record_keys[record_key] = line_id
                video_key = str(record.get("video_path", "")).replace("\\", "/").strip()
                if video_key:
                    prior_video_line = seen_video_paths.get(video_key)
                    if prior_video_line:
                        errors.append(f"{line_id}: duplicate video_path also used at {prior_video_line}: {video_key}")
                    else:
                        seen_video_paths[video_key] = line_id
                errors.extend(
                    validate_record(
                        record,
                        line_id=line_id,
                        schema=schema,
                        manifest_methods=manifest_methods,
                        manifest_tasks=manifest_tasks,
                        check_video_paths=check_video_paths,
                        manifest_task_specs=manifest_task_specs,
                        manifest_task_configs=manifest_task_configs,
                        manifest_video_dirs=manifest_video_dirs,
                        manifest_method_hashes=manifest_method_hashes,
                        strict_video_evidence=strict_video_evidence,
                    )
                )
                records.append(record)
                if len(errors) >= max_errors:
                    return records, errors
    return records, errors


def paired_key(record: dict[str, Any], schema: dict[str, Any]) -> tuple[Any, ...]:
    fields = schema.get("paired_comparison_key", [])
    return tuple(record.get(field) for field in fields)


def summarize(records: list[dict[str, Any]], schema: dict[str, Any]) -> dict[str, Any]:
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_task_method: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        method = str(record["method"])
        task = str(record["task_family"])
        by_method[method].append(record)
        by_task_method[(task, method)].append(record)

    method_summary = {}
    for method, method_records in sorted(by_method.items()):
        method_summary[method] = {
            "episodes": len(method_records),
            "success": mean(1.0 if row["success"] else 0.0 for row in method_records),
            "utility": mean(float(row["utility"]) for row in method_records),
            "seam_failure": mean(1.0 if row["seam_failure"] else 0.0 for row in method_records),
            "realized_seam_breach": mean(1.0 if row["realized_seam_breach"] else 0.0 for row in method_records),
        }

    candidate_baselines = {
        method: stats
        for method, stats in method_summary.items()
        if method not in {PRIMARY_METHOD, ORACLE_METHOD}
    }
    strongest_baseline = None
    if candidate_baselines:
        strongest_baseline = max(
            candidate_baselines,
            key=lambda method: (candidate_baselines[method]["success"], candidate_baselines[method]["utility"]),
        )

    primary_stats = method_summary.get(PRIMARY_METHOD)
    baseline_stats = method_summary.get(strongest_baseline) if strongest_baseline else None
    success_margin = None
    utility_margin = None
    if primary_stats and baseline_stats:
        success_margin = primary_stats["success"] - baseline_stats["success"]
        utility_margin = primary_stats["utility"] - baseline_stats["utility"]

    paired_groups: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        paired_groups[paired_key(record, schema)][str(record["method"])] = record
    paired_available = [
        methods
        for methods in paired_groups.values()
        if PRIMARY_METHOD in methods and strongest_baseline and strongest_baseline in methods
    ]
    paired_win_rate = None
    if paired_available:
        wins = 0
        for methods in paired_available:
            primary = methods[PRIMARY_METHOD]
            baseline = methods[strongest_baseline]
            primary_tuple = (1.0 if primary["success"] else 0.0, float(primary["utility"]))
            baseline_tuple = (1.0 if baseline["success"] else 0.0, float(baseline["utility"]))
            if primary_tuple > baseline_tuple:
                wins += 1
        paired_win_rate = wins / len(paired_available)

    proposed_records = by_method.get(PRIMARY_METHOD, [])
    fixed_risk_budget = None
    fixed_risk_breach = None
    fixed_risk_coverage = None
    if proposed_records:
        fixed_risk_budget = mean(float(row["fixed_risk_budget"]) for row in proposed_records)
        accepted = [
            row
            for row in proposed_records
            if row["decision"] in {"accept", "repair", "transition"} and float(row["predicted_seam_risk"]) <= float(row["fixed_risk_budget"])
        ]
        fixed_risk_coverage = len(accepted) / len(proposed_records)
        fixed_risk_breach = (
            mean(1.0 if row["realized_seam_breach"] else 0.0 for row in accepted)
            if accepted
            else None
        )

    positive_tasks = 0
    task_summary = {}
    tasks = sorted({str(row["task_family"]) for row in records})
    for task in tasks:
        primary_task = by_task_method.get((task, PRIMARY_METHOD), [])
        baseline_task = by_task_method.get((task, strongest_baseline), []) if strongest_baseline else []
        primary_success = mean(1.0 if row["success"] else 0.0 for row in primary_task) if primary_task else None
        baseline_success = mean(1.0 if row["success"] else 0.0 for row in baseline_task) if baseline_task else None
        margin = primary_success - baseline_success if primary_success is not None and baseline_success is not None else None
        if margin is not None and margin > 0:
            positive_tasks += 1
        task_summary[task] = {
            "primary_episodes": len(primary_task),
            "baseline_episodes": len(baseline_task),
            "primary_success": primary_success,
            "strongest_baseline_success": baseline_success,
            "success_margin": margin,
        }

    return {
        "version": "external_rollout_metrics_v1",
        "episodes": len(records),
        "task_families": tasks,
        "methods": sorted(by_method),
        "primary_method": PRIMARY_METHOD,
        "strongest_external_baseline": strongest_baseline,
        "method_summary": method_summary,
        "task_summary": task_summary,
        "external_success_margin": success_margin,
        "external_utility_margin": utility_margin,
        "paired_comparison_count": len(paired_available),
        "paired_win_rate": paired_win_rate,
        "fixed_risk_budget": fixed_risk_budget,
        "fixed_risk_breach": fixed_risk_breach,
        "fixed_risk_coverage": fixed_risk_coverage,
        "positive_task_families": positive_tasks,
        "external_task_families": len(tasks),
    }


def threshold_checks(summary: dict[str, Any], schema: dict[str, Any]) -> list[ValidationResult]:
    thresholds = schema.get("primary_thresholds", {})
    checks = []
    for key in ("external_success_margin", "external_utility_margin", "paired_win_rate", "fixed_risk_coverage"):
        value = summary.get(key)
        threshold = thresholds.get(key)
        checks.append(
            ValidationResult(
                value is not None and threshold is not None and float(value) >= float(threshold),
                f"{key}: value={value}, threshold={threshold}",
            )
        )
    breach = summary.get("fixed_risk_breach")
    breach_threshold = thresholds.get("fixed_risk_breach")
    checks.append(
        ValidationResult(
            breach is not None and breach_threshold is not None and float(breach) <= float(breach_threshold),
            f"fixed_risk_breach: value={breach}, threshold={breach_threshold}",
        )
    )
    positive = summary.get("positive_task_families")
    positive_threshold = thresholds.get("positive_task_families")
    checks.append(
        ValidationResult(
            positive is not None and positive_threshold is not None and int(positive) >= int(positive_threshold),
            f"positive_task_families: value={positive}, threshold={positive_threshold}",
        )
    )
    return checks


def write_outputs(summary: dict[str, Any], checks: list[ValidationResult], errors: list[str]) -> None:
    RESULTS.mkdir(exist_ok=True)
    payload = {
        "summary": summary,
        "threshold_checks": [{"passed": check.passed, "message": check.message} for check in checks],
        "schema_errors": errors,
        "passed": not errors and all(check.passed for check in checks),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Rollout Metrics",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Episodes: `{summary.get('episodes', 0)}`.",
        f"Primary method: `{summary.get('primary_method')}`.",
        f"Strongest external baseline: `{summary.get('strongest_external_baseline')}`.",
        "",
        "## Threshold Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check.passed else "fail"
        lines.append(f"- `{status}` {check.message}")
    lines.extend(["", "## Schema Errors", ""])
    if errors:
        for error in errors[:100]:
            lines.append(f"- {error}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and recompute external rollout metrics for Paper 119.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="External validation manifest path.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="External validation JSONL schema path.")
    parser.add_argument("--write-results", action="store_true", help="Write results/external_rollout_metrics.{json,md}.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless schema and metric thresholds pass.")
    parser.add_argument("--check-video-paths", action="store_true", help="Require every episode video_path to exist.")
    parser.add_argument("--max-errors", type=int, default=100, help="Stop after this many schema errors.")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"External rollout validation: NOT_READY; missing manifest {args.manifest}")
        if args.write_results:
            write_outputs({"version": "external_rollout_metrics_v1", "episodes": 0}, [], [f"missing manifest {args.manifest}"])
        return 1 if args.strict else 0
    if not args.schema.exists():
        raise SystemExit(f"missing schema {args.schema}")

    manifest = read_json(args.manifest)
    schema = read_json(args.schema)
    records, errors = load_records(
        manifest,
        schema,
        check_video_paths=args.check_video_paths,
        strict_video_evidence=args.strict and args.check_video_paths,
        max_errors=args.max_errors,
    )
    summary = summarize(records, schema) if records else {"version": "external_rollout_metrics_v1", "episodes": 0}
    checks = threshold_checks(summary, schema) if records else []
    passed = not errors and bool(records) and all(check.passed for check in checks)
    if args.write_results:
        write_outputs(summary, checks, errors)
    status = "READY" if passed else "NOT_READY"
    print(f"External rollout validation: {status}; episodes={summary.get('episodes', 0)}; schema_errors={len(errors)}")
    if args.write_results:
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
    if args.strict and not passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

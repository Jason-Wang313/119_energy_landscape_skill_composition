from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_TEMPLATE = EXTERNAL / "manifest_template.json"
DEFAULT_OUTPUT = EXTERNAL / "manifest.json"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
REPORT_JSON = RESULTS / "external_manifest_builder_report.json"
REPORT_MD = RESULTS / "external_manifest_builder_report.md"

PRIMARY_METHOD = "barrier_certified_energy_composer_v5"
ORACLE_METHOD = "oracle_basin_composer"
ARTIFACT_DIR_NAMES = {
    "configs": "configs",
    "logs": "logs",
    "videos": "videos",
    "checkpoints": "checkpoints",
}
CORE_CODE_ARTIFACTS = [
    "external_validation/config_schema_v1.json",
    "external_validation/log_schema_v1.json",
    "scripts/audit_external_evidence.py",
    "scripts/audit_external_pairing_integrity.py",
    "scripts/validate_external_adapters.py",
    "scripts/validate_external_configs.py",
    "scripts/validate_external_rollouts.py",
]


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def posix_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if path.is_dir():
        digest = hashlib.sha256()
        files = sorted(child for child in path.rglob("*") if child.is_file())
        for child in files:
            rel = child.relative_to(path).as_posix().encode("utf-8")
            digest.update(rel)
            digest.update(b"\0")
            digest.update(sha256_file(child).encode("ascii"))
            digest.update(b"\0")
        return digest.hexdigest().upper()
    raise FileNotFoundError(path)


def code_artifact_paths(root: Path, manifest: dict[str, Any]) -> list[Path]:
    paths: list[Path] = [rel_path(root, value) for value in CORE_CODE_ARTIFACTS]
    for method in manifest.get("methods", []):
        if not isinstance(method, dict) or method.get("name") == ORACLE_METHOD:
            continue
        implementation = str(method.get("implementation", "")).strip()
        if implementation:
            paths.append(rel_path(root, implementation))
    return sorted({path.resolve() for path in paths if path.exists()}, key=lambda path: str(path))


def scan_artifacts(root: Path, artifact_dirs: dict[str, Path], manifest: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    release = {"code": [], "configs": [], "logs": [], "videos": [], "checkpoints": []}
    release["code"] = [
        {"path": posix_rel(root, path), "sha256": sha256_path(path)}
        for path in code_artifact_paths(root, manifest)
    ]
    for kind, directory in artifact_dirs.items():
        if not directory.exists():
            continue
        entries: list[dict[str, str]] = []
        if kind == "videos":
            candidates = sorted(path for path in directory.iterdir() if path.exists())
        else:
            candidates = sorted(path for path in directory.rglob("*") if path.is_file())
        for path in candidates:
            entries.append({"path": posix_rel(root, path), "sha256": sha256_path(path)})
        release[kind] = entries
    return release


def maybe_hash_existing(root: Path, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    path = rel_path(root, value)
    return sha256_path(path) if path.exists() else ""


def method_names(manifest: dict[str, Any]) -> set[str]:
    methods = manifest.get("methods", [])
    methods = methods if isinstance(methods, list) else []
    return {str(method.get("name", "")) for method in methods if isinstance(method, dict)}


def task_names(manifest: dict[str, Any]) -> set[str]:
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    return {str(task.get("task_family", "")) for task in tasks if isinstance(task, dict)}


def validate_record(record: dict[str, Any], schema: dict[str, Any], manifest: dict[str, Any], line_id: str) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required_fields", {}))
    missing = sorted(required - set(record))
    if missing:
        return [f"{line_id}: missing required fields {missing}"]

    allowed = schema.get("allowed_values", {})
    for field, values in allowed.items():
        if record.get(field) not in set(values):
            errors.append(f"{line_id}: {field}={record.get(field)!r} not in {values}")

    if record.get("method") not in method_names(manifest):
        errors.append(f"{line_id}: method={record.get('method')!r} is not declared in manifest")
    if record.get("task_family") not in task_names(manifest):
        errors.append(f"{line_id}: task_family={record.get('task_family')!r} is not declared in manifest")

    for field in ("seed", "episode_index"):
        if isinstance(record.get(field), bool) or not isinstance(record.get(field), int) or record.get(field) < 0:
            errors.append(f"{line_id}: {field} must be integer >= 0")
    for field in ("basin_estimate", "descent_continuity_score", "predicted_seam_risk", "fixed_risk_budget"):
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not (0 <= float(value) <= 1):
            errors.append(f"{line_id}: {field} must be finite numeric in [0, 1]")
    for field in ("barrier_score", "composition_cost", "utility"):
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errors.append(f"{line_id}: {field} must be finite numeric")
        elif field != "utility" and float(value) < 0:
            errors.append(f"{line_id}: {field} must be >= 0")
    for field in ("success", "seam_failure", "barrier_violation", "damage_or_intervention", "realized_seam_breach"):
        if not isinstance(record.get(field), bool):
            errors.append(f"{line_id}: {field} must be boolean")

    return errors


def load_records(root: Path, manifest: dict[str, Any], schema: dict[str, Any], *, check_video_paths: bool) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("manifest task entry is not an object")
            continue
        log_value = str(task.get("log_jsonl", ""))
        if not log_value:
            errors.append(f"{task.get('task_family', 'unknown')}: missing log_jsonl")
            continue
        log_path = rel_path(root, log_value)
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
                    continue
                if not isinstance(record, dict):
                    errors.append(f"{line_id}: JSONL line must be an object")
                    continue
                errors.extend(validate_record(record, schema, manifest, line_id))
                if check_video_paths:
                    video_path = str(record.get("video_path", ""))
                    if video_path and not rel_path(root, video_path).exists():
                        errors.append(f"{line_id}: missing video_path {video_path}")
                records.append(record)
    return records, errors


def paired_key(record: dict[str, Any], schema: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(record.get(field) for field in schema.get("paired_comparison_key", []))


def summarize_records(records: list[dict[str, Any]], schema: dict[str, Any]) -> dict[str, Any]:
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_task_method: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_method[str(record["method"])].append(record)
        by_task_method[(str(record["task_family"]), str(record["method"]))].append(record)

    method_summary: dict[str, dict[str, float | int]] = {}
    for method, rows in sorted(by_method.items()):
        method_summary[method] = {
            "episodes": len(rows),
            "success": mean(1.0 if row["success"] else 0.0 for row in rows),
            "utility": mean(float(row["utility"]) for row in rows),
        }
    baselines = {name: stats for name, stats in method_summary.items() if name not in {PRIMARY_METHOD, ORACLE_METHOD}}
    strongest = max(baselines, key=lambda name: (float(baselines[name]["success"]), float(baselines[name]["utility"]))) if baselines else None

    primary = method_summary.get(PRIMARY_METHOD)
    baseline = method_summary.get(strongest) if strongest else None
    success_margin = float(primary["success"]) - float(baseline["success"]) if primary and baseline else None
    utility_margin = float(primary["utility"]) - float(baseline["utility"]) if primary and baseline else None

    grouped: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        grouped[paired_key(record, schema)][str(record["method"])] = record
    paired = [methods for methods in grouped.values() if strongest and PRIMARY_METHOD in methods and strongest in methods]
    paired_win_rate = None
    if paired:
        wins = 0
        for methods in paired:
            primary_record = methods[PRIMARY_METHOD]
            baseline_record = methods[strongest]
            primary_tuple = (1.0 if primary_record["success"] else 0.0, float(primary_record["utility"]))
            baseline_tuple = (1.0 if baseline_record["success"] else 0.0, float(baseline_record["utility"]))
            wins += int(primary_tuple > baseline_tuple)
        paired_win_rate = wins / len(paired)

    proposed_rows = by_method.get(PRIMARY_METHOD, [])
    fixed_risk_budget = mean(float(row["fixed_risk_budget"]) for row in proposed_rows) if proposed_rows else None
    accepted = [
        row
        for row in proposed_rows
        if row["decision"] in {"accept", "repair", "transition"} and float(row["predicted_seam_risk"]) <= float(row["fixed_risk_budget"])
    ]
    fixed_risk_coverage = len(accepted) / len(proposed_rows) if proposed_rows else None
    fixed_risk_breach = mean(1.0 if row["realized_seam_breach"] else 0.0 for row in accepted) if accepted else None

    tasks = sorted({str(row["task_family"]) for row in records})
    positive_tasks = 0
    for task in tasks:
        primary_rows = by_task_method.get((task, PRIMARY_METHOD), [])
        baseline_rows = by_task_method.get((task, strongest), []) if strongest else []
        if primary_rows and baseline_rows:
            margin = mean(1.0 if row["success"] else 0.0 for row in primary_rows) - mean(1.0 if row["success"] else 0.0 for row in baseline_rows)
            positive_tasks += int(margin > 0)

    return {
        "external_success_margin": success_margin,
        "external_utility_margin": utility_margin,
        "paired_win_rate": paired_win_rate,
        "fixed_risk_budget": fixed_risk_budget,
        "fixed_risk_breach": fixed_risk_breach,
        "fixed_risk_coverage": fixed_risk_coverage,
        "positive_task_families": positive_tasks,
        "external_task_families": len(tasks),
        "strongest_external_baseline": strongest,
        "method_summary": method_summary,
        "episodes": len(records),
    }


def update_manifest_hashes(root: Path, manifest: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for task in manifest.get("tasks", []):
        if not isinstance(task, dict):
            continue
        config_hash = maybe_hash_existing(root, task.get("config_path"))
        if config_hash:
            task["config_hash"] = config_hash
        elif not task.get("config_hash"):
            warnings.append(f"{task.get('task_family', 'unknown')}: no config_hash and no existing config_path")

    for method in manifest.get("methods", []):
        if not isinstance(method, dict):
            continue
        method_hash = maybe_hash_existing(root, method.get("checkpoint_or_config_path")) or maybe_hash_existing(root, method.get("implementation"))
        if method_hash:
            method["checkpoint_or_config_hash"] = method_hash
        elif method.get("name") != ORACLE_METHOD and not method.get("checkpoint_or_config_hash"):
            warnings.append(f"{method.get('name', 'unknown')}: no checkpoint_or_config_hash and no hashable implementation/path")
    return warnings


def write_report(report: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Manifest Builder Report",
        "",
        f"Manifest written: `{str(report['manifest_written']).lower()}`.",
        f"Ready to write manifest: `{str(report['ready_to_write_manifest']).lower()}`.",
        f"Not evidence: `{str(report['not_external_evidence']).lower()}`.",
        f"Template: `{report['template']}`.",
        f"Output: `{report['output']}`.",
        "",
        "## Summary",
        "",
        f"- Records loaded: `{report['records_loaded']}`.",
        f"- Schema errors: `{len(report['schema_errors'])}`.",
        f"- Warnings: `{len(report['warnings'])}`.",
        "",
        "## Schema Errors",
        "",
    ]
    if report["schema_errors"]:
        for error in report["schema_errors"][:100]:
            lines.append(f"- {error}")
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        for warning in report["warnings"][:100]:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or preview an external validation manifest from real logs and release artifacts.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Input manifest template or draft.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="External rollout JSONL schema.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Manifest output path.")
    parser.add_argument("--workspace-root", type=Path, default=ROOT, help="Repository root used for relative paths.")
    parser.add_argument("--write", action="store_true", help="Write the manifest. Omit for report-only preview.")
    parser.add_argument("--allow-missing", action="store_true", help="Return success and write a report even when evidence is incomplete.")
    parser.add_argument("--check-video-paths", action="store_true", help="Require every JSONL video_path to exist while building.")
    args = parser.parse_args()

    root = args.workspace_root.resolve()
    manifest = read_json(args.template)
    schema = read_json(args.schema)

    warnings = update_manifest_hashes(root, manifest)
    external_root = root / "external_validation"
    artifact_dirs = {kind: external_root / name for kind, name in ARTIFACT_DIR_NAMES.items()}
    manifest["release_artifacts"] = scan_artifacts(root, artifact_dirs, manifest)

    records, schema_errors = load_records(root, manifest, schema, check_video_paths=args.check_video_paths)
    summary: dict[str, Any] = {"episodes": 0}
    if records and not schema_errors:
        summary = summarize_records(records, schema)
        metrics = manifest.setdefault("metrics", {})
        for key in (
            "external_success_margin",
            "external_utility_margin",
            "paired_win_rate",
            "fixed_risk_budget",
            "fixed_risk_breach",
            "fixed_risk_coverage",
            "positive_task_families",
            "external_task_families",
        ):
            metrics[key] = summary.get(key)
        methods = set(summary.get("method_summary", {}))
        metrics["oracle_reported"] = ORACLE_METHOD in methods
        oracle = summary.get("method_summary", {}).get(ORACLE_METHOD) if isinstance(summary.get("method_summary"), dict) else None
        primary = summary.get("method_summary", {}).get(PRIMARY_METHOD) if isinstance(summary.get("method_summary"), dict) else None
        if oracle and primary:
            metrics["oracle_stronger_or_saturated_explained"] = (
                float(oracle.get("success", 0.0)) >= float(primary.get("success", 0.0))
                and float(oracle.get("utility", 0.0)) >= float(primary.get("utility", 0.0))
            )

    ready = bool(records) and not schema_errors
    manifest_written = False
    if args.write:
        if not ready and not args.allow_missing:
            write_report(
                {
                    "version": "external_manifest_builder_report_v1",
                    "template": str(args.template),
                    "output": str(args.output),
                    "manifest_written": False,
                    "ready_to_write_manifest": ready,
                    "not_external_evidence": True,
                    "records_loaded": len(records),
                    "schema_errors": schema_errors,
                    "warnings": warnings,
                    "summary": summary,
                }
            )
            raise SystemExit("refusing to write manifest because evidence is incomplete; use --allow-missing only for a draft")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        manifest_written = True

    report = {
        "version": "external_manifest_builder_report_v1",
        "template": str(args.template),
        "output": str(args.output),
        "manifest_written": manifest_written,
        "ready_to_write_manifest": ready,
        "not_external_evidence": not manifest_written,
        "records_loaded": len(records),
        "schema_errors": schema_errors,
        "warnings": warnings,
        "summary": summary,
    }
    write_report(report)

    status = "READY" if ready else "NOT_READY"
    print(f"External manifest builder: {status}; records={len(records)}; schema_errors={len(schema_errors)}; manifest_written={manifest_written}")
    print(f"Wrote {REPORT_JSON}")
    print(f"Wrote {REPORT_MD}")
    if manifest_written:
        print(f"Wrote {args.output}")
    return 0 if ready or args.allow_missing or not args.write else 1


if __name__ == "__main__":
    raise SystemExit(main())

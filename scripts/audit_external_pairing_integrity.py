from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_MANIFEST = EXTERNAL / "manifest.json"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
OUT_JSON = RESULTS / "external_pairing_integrity_audit.json"
OUT_MD = RESULTS / "external_pairing_integrity_audit.md"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def paired_key(record: dict[str, Any], schema: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(record.get(field) for field in schema.get("paired_comparison_key", []))


def load_task_records(task: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    log_value = str(task.get("log_jsonl", ""))
    if not log_value:
        return [], [f"{task.get('task_family', 'unknown')}: missing log_jsonl"]
    log_path = rel_path(log_value)
    if not log_path.exists():
        return [], [f"{task.get('task_family', 'unknown')}: missing log file {log_value}"]

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    with log_path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{log_value}:{line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(payload, dict):
                errors.append(f"{log_value}:{line_number}: JSONL line must be an object")
                continue
            payload["_line_id"] = f"{log_value}:{line_number}"
            records.append(payload)
    return records, errors


def inspect_task(
    task: dict[str, Any],
    *,
    schema: dict[str, Any],
    manifest_methods: list[str],
) -> dict[str, Any]:
    task_family = str(task.get("task_family", "unknown"))
    expected_groups = int(task.get("episodes_per_method", 0) or 0)
    method_set = set(manifest_methods)
    records, parse_errors = load_task_records(task)

    blockers = list(parse_errors)
    task_records = [record for record in records if str(record.get("task_family", "")) == task_family]
    wrong_task = len(records) - len(task_records)
    if wrong_task:
        blockers.append(f"{wrong_task} records do not match manifest task_family={task_family}")

    missing_key_fields = []
    for record in task_records:
        missing = [field for field in schema.get("paired_comparison_key", []) if record.get(field) in {None, ""}]
        if missing:
            missing_key_fields.append(f"{record.get('_line_id', '<unknown>')}: missing paired key fields {missing}")
    blockers.extend(missing_key_fields[:20])

    groups: dict[tuple[Any, ...], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in task_records:
        groups[paired_key(record, schema)][str(record.get("method", ""))].append(record)

    duplicate_entries: list[str] = []
    incomplete_groups: list[str] = []
    extra_method_groups: list[str] = []
    terminal_hash_mismatches: list[str] = []
    platform_mismatches: list[str] = []
    budget_mismatches: list[str] = []
    for key, methods in groups.items():
        present = {method for method in methods if method}
        missing_methods = sorted(method_set - present)
        extra_methods = sorted(present - method_set)
        if missing_methods:
            incomplete_groups.append(f"{key}: missing={missing_methods[:6]}")
        if extra_methods:
            extra_method_groups.append(f"{key}: extra={extra_methods[:6]}")
        for method, rows in methods.items():
            if len(rows) > 1:
                duplicate_entries.append(f"{key}: method={method!r} count={len(rows)}")

        terminal_hashes = {str(row.get("terminal_sample_set_hash", "")) for rows in methods.values() for row in rows}
        if len(terminal_hashes) > 1:
            terminal_hash_mismatches.append(f"{key}: terminal_sample_set_hash values={sorted(terminal_hashes)[:4]}")
        platforms = {(str(row.get("platform_type", "")), str(row.get("platform_name", ""))) for rows in methods.values() for row in rows}
        if len(platforms) > 1:
            platform_mismatches.append(f"{key}: platform values={sorted(platforms)[:4]}")
        budgets = {str(row.get("fixed_risk_budget", "")) for rows in methods.values() for row in rows}
        if len(budgets) > 1:
            budget_mismatches.append(f"{key}: fixed_risk_budget values={sorted(budgets)[:4]}")

    method_counts = Counter(str(record.get("method", "")) for record in task_records)
    missing_declared_methods = sorted(method for method in manifest_methods if method_counts.get(method, 0) == 0)
    unequal_counts = {
        method: method_counts.get(method, 0)
        for method in manifest_methods
        if method_counts.get(method, 0) != expected_groups
    }

    if len(groups) < expected_groups:
        blockers.append(f"paired reset groups={len(groups)}, expected at least {expected_groups}")
    if missing_declared_methods:
        blockers.append(f"declared methods with no records: {missing_declared_methods[:8]}")
    if unequal_counts:
        blockers.append(f"per-method counts do not match episodes_per_method={expected_groups}: {dict(list(unequal_counts.items())[:8])}")
    for label, items in (
        ("duplicate method records within paired reset", duplicate_entries),
        ("paired reset groups missing declared methods", incomplete_groups),
        ("paired reset groups contain undeclared methods", extra_method_groups),
        ("terminal sample hashes differ within paired reset", terminal_hash_mismatches),
        ("platform differs within paired reset", platform_mismatches),
        ("fixed risk budget differs within paired reset", budget_mismatches),
    ):
        if items:
            blockers.append(f"{label}: {items[:8]}")

    expected_records = expected_groups * len(manifest_methods)
    return {
        "task_family": task_family,
        "expected_groups": expected_groups,
        "observed_groups": len(groups),
        "expected_records": expected_records,
        "observed_records": len(task_records),
        "method_count": len(manifest_methods),
        "method_counts": dict(sorted(method_counts.items())),
        "complete_groups": len([
            methods for methods in groups.values() if set(methods) == method_set and all(len(rows) == 1 for rows in methods.values())
        ]),
        "duplicate_group_method_records": len(duplicate_entries),
        "incomplete_groups": len(incomplete_groups),
        "extra_method_groups": len(extra_method_groups),
        "terminal_hash_mismatches": len(terminal_hash_mismatches),
        "platform_mismatches": len(platform_mismatches),
        "budget_mismatches": len(budget_mismatches),
        "blocking_missing": blockers,
    }


def build_payload(manifest_path: Path, schema_path: Path) -> dict[str, Any]:
    manifest_exists = manifest_path.exists()
    schema_exists = schema_path.exists()
    if not schema_exists:
        raise SystemExit(f"missing schema {schema_path}")

    schema = read_json(schema_path)
    if not manifest_exists:
        return {
            "version": "external_pairing_integrity_audit_v1",
            "passed": True,
            "not_external_evidence": True,
            "pairing_ready": False,
            "readiness_state": "COLLECT_EXTERNAL_EVIDENCE",
            "manifest_path": rel(manifest_path),
            "schema_path": rel(schema_path),
            "task_reports": [],
            "expected_records": 0,
            "observed_records": 0,
            "blocking_missing_count": 1,
            "blocking_missing": ["external_validation/manifest.json has not been written from real evidence"],
        }

    manifest = read_json(manifest_path)
    global_blockers: list[str] = []
    manifest_rel = rel(manifest_path)
    if manifest.get("local_dry_run_only") is True or "local_dry_run" in manifest_rel.replace("\\", "/"):
        global_blockers.append("local_dry_run manifests are plumbing checks only and cannot satisfy pairing integrity evidence")
    if manifest.get("not_external_evidence") is True:
        global_blockers.append("manifest is marked not_external_evidence")
    methods = [str(method.get("name", "")) for method in manifest.get("methods", []) if isinstance(method, dict) and str(method.get("name", ""))]
    tasks = [task for task in manifest.get("tasks", []) if isinstance(task, dict)]
    task_reports = [inspect_task(task, schema=schema, manifest_methods=methods) for task in tasks]
    blockers: list[str] = list(global_blockers)
    if not methods:
        blockers.append("manifest declares no methods")
    if not tasks:
        blockers.append("manifest declares no tasks")
    for report in task_reports:
        for blocker in report["blocking_missing"]:
            blockers.append(f"{report['task_family']}: {blocker}")

    expected_records = sum(int(report["expected_records"]) for report in task_reports)
    observed_records = sum(int(report["observed_records"]) for report in task_reports)
    pairing_ready = bool(manifest_exists and not blockers and expected_records >= 1440 and observed_records >= expected_records)
    return {
        "version": "external_pairing_integrity_audit_v1",
        "passed": True,
        "not_external_evidence": not pairing_ready,
        "pairing_ready": pairing_ready,
        "readiness_state": "READY_FOR_STRICT_AUDIT" if pairing_ready else "COLLECT_EXTERNAL_EVIDENCE",
        "manifest_path": rel(manifest_path),
        "schema_path": rel(schema_path),
        "global_blockers": global_blockers,
        "task_reports": task_reports,
        "expected_records": expected_records,
        "observed_records": observed_records,
        "blocking_missing_count": len(blockers),
        "blocking_missing": blockers,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Pairing Integrity Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Pairing ready: `{str(payload['pairing_ready']).lower()}`.",
        f"Readiness state: `{payload['readiness_state']}`.",
        f"Expected records: `{payload['expected_records']}`.",
        f"Observed records: `{payload['observed_records']}`.",
        f"Blocking missing items: `{payload['blocking_missing_count']}`.",
        "",
        "This audit checks paired-reset fairness for future real external evidence. It verifies complete, duplicate-free method panels per paired reset and consistent terminal samples, platform, and fixed-risk budget within each panel.",
        "",
        "## Task Reports",
        "",
        "| Task | Groups | Complete | Records | Duplicates | Incomplete | Missing |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for report in payload["task_reports"]:
        missing = "; ".join(report["blocking_missing"][:4]) if report["blocking_missing"] else "none"
        lines.append(
            f"| `{report['task_family']}` | {report['observed_groups']}/{report['expected_groups']} | "
            f"{report['complete_groups']} | {report['observed_records']}/{report['expected_records']} | "
            f"{report['duplicate_group_method_records']} | {report['incomplete_groups']} | {missing} |"
        )
    lines.extend(["", "## Blocking Missing", ""])
    if payload["blocking_missing"]:
        for blocker in payload["blocking_missing"][:100]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paired-reset/method-panel integrity for Paper 119 external rollout logs.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="External validation manifest path.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="External validation JSONL schema path.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless pairing integrity is ready for strict evidence audit.")
    args = parser.parse_args()

    payload = build_payload(args.manifest, args.schema)
    write_outputs(payload)
    print(
        "External pairing integrity audit: "
        f"{payload['readiness_state']}; pairing_ready={payload['pairing_ready']}; "
        f"observed_records={payload['observed_records']}/{payload['expected_records']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["pairing_ready"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())

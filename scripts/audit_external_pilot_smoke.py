from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import validate_external_rollouts as rollout_validator


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

DEFAULT_LOG_DIR = EXTERNAL / "pilot_smoke" / "logs"
DEFAULT_VIDEO_DIR = EXTERNAL / "pilot_smoke" / "videos"
DEFAULT_OPERATOR_SHEET = EXTERNAL / "blinded_operator_sheet.csv"
DEFAULT_ALIAS_MAP = EXTERNAL / "method_alias_map.json"
DEFAULT_CONFIG_DIR = EXTERNAL / "configs"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"

OUT_JSON = RESULTS / "external_pilot_smoke_audit.json"
OUT_MD = RESULTS / "external_pilot_smoke_audit.md"


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


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def alias_methods(path: Path) -> set[str]:
    payload = read_json(path)
    aliases = payload.get("aliases", [])
    if not isinstance(aliases, list):
        return set()
    return {
        str(item.get("method", "")).strip()
        for item in aliases
        if isinstance(item, dict) and str(item.get("method", "")).strip()
    }


def configured_tasks(config_dir: Path, operator_sheet: Path) -> set[str]:
    tasks = {path.stem for path in config_dir.glob("*.json") if path.is_file()}
    if operator_sheet.exists():
        with operator_sheet.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                task = str(row.get("task_family", "")).strip()
                if task:
                    tasks.add(task)
    return tasks


def load_records(log_dir: Path) -> tuple[list[dict[str, Any]], list[str], list[Path]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    log_paths = sorted(log_dir.glob("*.jsonl")) if log_dir.exists() else []
    for log_path in log_paths:
        with log_path.open(encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    record = json.loads(raw)
                except json.JSONDecodeError as exc:
                    errors.append(f"{rel(log_path)}:{line_number}: invalid JSON: {exc}")
                    continue
                if not isinstance(record, dict):
                    errors.append(f"{rel(log_path)}:{line_number}: JSONL line must be an object")
                    continue
                records.append(record)
    return records, errors, log_paths


def record_uses_official_path(record: dict[str, Any]) -> bool:
    video_text = str(record.get("video_path", ""))
    if not video_text:
        return False
    video_path = Path(video_text)
    absolute = video_path if video_path.is_absolute() else ROOT / video_path
    return is_under(absolute, EXTERNAL / "videos") or is_under(absolute, EXTERNAL / "logs")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    schema = read_json(args.schema) if args.schema.exists() else {}
    methods = alias_methods(args.alias_map) if args.alias_map.exists() else set()
    tasks = configured_tasks(args.config_dir, args.operator_sheet)
    records, parse_errors, log_paths = load_records(args.log_dir)

    quarantine_root = EXTERNAL / "pilot_smoke"
    log_quarantined = is_under(args.log_dir, quarantine_root) and not is_under(args.log_dir, EXTERNAL / "logs")
    video_quarantined = is_under(args.video_dir, quarantine_root) and not is_under(args.video_dir, EXTERNAL / "videos")
    add_check(
        checks,
        "quarantine_paths_are_not_official_evidence",
        log_quarantined and video_quarantined,
        f"log_dir={rel(args.log_dir)}, video_dir={rel(args.video_dir)}",
    )
    add_check(checks, "schema_exists", args.schema.exists(), rel(args.schema))
    add_check(checks, "alias_map_methods_loaded", len(methods) >= 12, f"methods={len(methods)}")
    add_check(checks, "task_configs_or_sheet_loaded", len(tasks) >= 4, f"tasks={sorted(tasks)}")
    add_check(checks, "pilot_manifest_absent", not (quarantine_root / "manifest.json").exists(), "pilot smoke must not build an evidence manifest")

    schema_errors: list[str] = list(parse_errors)
    for index, record in enumerate(records, start=1):
        schema_errors.extend(
            rollout_validator.validate_record(
                record,
                line_id=f"pilot_smoke:{index}",
                schema=schema,
                manifest_methods=methods,
                manifest_tasks=tasks,
                check_video_paths=args.check_video_paths,
            )
        )
    official_path_records = [record for record in records if record_uses_official_path(record)]
    non_pilot_run_ids = [
        str(record.get("run_id", ""))
        for record in records
        if "pilot" not in str(record.get("run_id", "")).lower()
    ]
    add_check(
        checks,
        "pilot_records_do_not_touch_official_evidence_paths",
        not official_path_records,
        f"offending_records={len(official_path_records)}",
    )
    add_check(
        checks,
        "pilot_run_ids_are_marked_pilot",
        not records or not non_pilot_run_ids,
        f"non_pilot_run_ids={sorted(set(non_pilot_run_ids))[:5]}",
    )
    add_check(checks, "pilot_schema_valid", not schema_errors, f"errors={schema_errors[:5]}")
    if args.expected_records:
        add_check(
            checks,
            "pilot_expected_record_count",
            len(records) == args.expected_records,
            f"expected={args.expected_records}, observed={len(records)}",
        )
    add_check(
        checks,
        "pilot_record_count_within_cap",
        len(records) <= args.max_records,
        f"records={len(records)}, max_records={args.max_records}",
    )
    pilot_logs_present = bool(records)
    add_check(
        checks,
        "pilot_logs_present_only_when_operator_ran_smoke",
        pilot_logs_present or not args.strict,
        f"records={len(records)}, strict={args.strict}",
    )

    pilot_smoke_ready = pilot_logs_present and all(check["passed"] for check in checks)
    passed = all(check["passed"] for check in checks) if args.strict else True
    return {
        "version": "external_pilot_smoke_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "pilot_smoke_ready": pilot_smoke_ready,
        "strict_evidence_ready": False,
        "log_dir": rel(args.log_dir),
        "video_dir": rel(args.video_dir),
        "log_files": [rel(path) for path in log_paths],
        "records_observed": len(records),
        "expected_records": args.expected_records,
        "max_records": args.max_records,
        "schema_errors": schema_errors,
        "checks": checks,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Pilot Smoke Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Pilot smoke ready: `{str(payload['pilot_smoke_ready']).lower()}`.",
        f"Strict evidence ready: `{str(payload['strict_evidence_ready']).lower()}`.",
        f"Records observed: `{payload['records_observed']}`.",
        "",
        "This audit is for a quarantined first-panel backend smoke test. It never satisfies the external evidence gate and it rejects pilot records that write into official evidence log/video paths.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    if payload["schema_errors"]:
        lines.extend(["", "## Schema Errors", ""])
        for error in payload["schema_errors"][:50]:
            lines.append(f"- {error}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit quarantined external pilot-smoke logs.")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--video-dir", type=Path, default=DEFAULT_VIDEO_DIR)
    parser.add_argument("--operator-sheet", type=Path, default=DEFAULT_OPERATOR_SHEET)
    parser.add_argument("--alias-map", type=Path, default=DEFAULT_ALIAS_MAP)
    parser.add_argument("--config-dir", type=Path, default=DEFAULT_CONFIG_DIR)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--expected-records", type=int, default=0)
    parser.add_argument("--max-records", type=int, default=12)
    parser.add_argument("--check-video-paths", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload)
    print(
        "External pilot smoke audit: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"ready={payload['pilot_smoke_ready']}; "
        f"records={payload['records_observed']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] and (payload["pilot_smoke_ready"] or not args.strict) else 1


if __name__ == "__main__":
    raise SystemExit(main())

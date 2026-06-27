from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
RUNNER_DIR = EXTERNAL / "runner"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

from backend_contract import validate_backend_object  # noqa: E402


DEFAULT_OPERATOR_SHEET = EXTERNAL / "blinded_operator_sheet.csv"
DEFAULT_ALIAS_MAP = EXTERNAL / "method_alias_map.json"
DEFAULT_TASK_CONFIG_DIR = EXTERNAL / "configs"
DEFAULT_OUTPUT_LOG_DIR = EXTERNAL / "logs"
DEFAULT_VIDEO_DIR = EXTERNAL / "videos"
DEFAULT_FIDELITY_AUDIT = RESULTS / "external_fidelity_acceptance_audit.json"
DEFAULT_RUNNER = RUNNER_DIR / "real_collection_runner.py"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
OUT_JSON = RESULTS / "external_collection_readiness_audit.json"
OUT_MD = RESULTS / "external_collection_readiness_audit.md"

REQUIRED_SHEET_COLUMNS = {
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
}

PLACEHOLDER_VALUES = {
    "FILL_AFTER_PLATFORM_SELECTION",
    "REPLACE_WITH_SOURCE_SKILL",
    "REPLACE_WITH_TARGET_SKILL",
}


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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def load_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], [f"missing operator sheet: {rel(path)}"]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = set(reader.fieldnames or [])
    missing_columns = sorted(REQUIRED_SHEET_COLUMNS - columns)
    errors = [f"operator sheet missing columns: {missing_columns}"] if missing_columns else []
    return rows, errors


def alias_methods(path: Path) -> tuple[dict[str, str], list[str]]:
    if not path.exists():
        return {}, [f"missing alias map: {rel(path)}"]
    payload = read_json(path)
    aliases = payload.get("aliases", [])
    if not isinstance(aliases, list):
        return {}, ["alias map has invalid aliases list"]
    lookup: dict[str, str] = {}
    errors: list[str] = []
    for item in aliases:
        if not isinstance(item, dict):
            errors.append("alias map entry is not an object")
            continue
        alias = str(item.get("alias", "")).strip()
        method = str(item.get("method", "")).strip()
        if not alias or not method:
            errors.append(f"incomplete alias entry: {item!r}")
            continue
        lookup[alias] = method
    if not lookup:
        errors.append("alias map contains no aliases")
    return lookup, errors


def contains_placeholder(value: Any) -> bool:
    if isinstance(value, dict):
        return any(contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_placeholder(item) for item in value)
    return value in PLACEHOLDER_VALUES


def inspect_config(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing config: {rel(path)}"]
    try:
        payload = read_json(path)
    except SystemExit as exc:
        return [str(exc)]
    blockers = []
    if payload.get("template_only") is True or payload.get("not_external_evidence") is True:
        blockers.append(f"{rel(path)} is marked template_only/not_external_evidence")
    if "template" in str(payload.get("version", "")).lower():
        blockers.append(f"{rel(path)} appears to use a template version")
    if contains_placeholder(payload):
        blockers.append(f"{rel(path)} still contains template placeholders")
    for required in ("task_family", "platform_type", "platform_name", "skill_i", "skill_j", "fixed_risk_budget"):
        if payload.get(required) in {None, ""}:
            blockers.append(f"{rel(path)} missing {required}")
    return blockers


def import_module_from_value(value: str) -> ModuleType:
    path = Path(value)
    if path.exists():
        digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:12]
        module_name = f"paper119_collection_backend_{digest}_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"could not import backend module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module(value)


def inspect_backend(module_value: str) -> list[str]:
    if not module_value.strip():
        return ["--backend-module is required before actual collection"]
    try:
        module = import_module_from_value(module_value)
    except Exception as exc:  # noqa: BLE001 - report import failure as a readiness blocker.
        return [f"backend module import failed: {exc}"]
    if getattr(module, "TEMPLATE_ONLY", False) is True:
        return ["backend module is marked TEMPLATE_ONLY"]
    try:
        if callable(getattr(module, "create_backend", None)):
            backend = module.create_backend()
        elif getattr(module, "Backend", None) is not None:
            backend = module.Backend()
        else:
            return ["backend module must expose create_backend() or Backend"]
    except Exception as exc:  # noqa: BLE001
        return [f"backend construction failed: {exc}"]
    backend_errors = validate_backend_object(backend)
    if backend_errors:
        return [f"backend contract failure: {item}" for item in backend_errors]
    try:
        provenance = backend.platform_provenance()
    except Exception as exc:  # noqa: BLE001
        return [f"backend platform_provenance failed: {exc}"]
    if not isinstance(provenance, dict):
        return ["backend platform_provenance must return a dict"]
    missing = [
        field
        for field in ("platform_type", "platform_name", "platform_version", "sensor_modalities")
        if provenance.get(field) is None or provenance.get(field) == "" or provenance.get(field) == []
    ]
    return [f"backend provenance missing {missing}"] if missing else []


def nonempty_logs(output_log_dir: Path) -> list[Path]:
    if not output_log_dir.exists():
        return []
    return sorted(path for path in output_log_dir.glob("*.jsonl") if path.is_file() and path.stat().st_size > 0)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    rows, row_errors = load_rows(args.operator_sheet)
    aliases, alias_errors = alias_methods(args.alias_map)
    fidelity = read_json(args.fidelity_audit) if args.fidelity_audit.exists() else {}
    tasks = sorted({row.get("task_family", "") for row in rows if row.get("task_family", "")})
    sheet_aliases = sorted({row.get("method_alias", "") for row in rows if row.get("method_alias", "")})
    alias_missing = sorted(alias for alias in sheet_aliases if alias not in aliases)
    config_blockers: list[str] = []
    for task in tasks:
        config_blockers.extend(inspect_config(args.task_config_dir / f"{task}.json"))
    backend_blockers = inspect_backend(args.backend_module)
    existing_logs = nonempty_logs(args.output_log_dir)

    checks: list[dict[str, Any]] = []
    add_check(checks, "runner_exists", args.runner.exists(), rel(args.runner))
    add_check(checks, "schema_exists", args.schema.exists(), rel(args.schema))
    add_check(checks, "operator_sheet_exists", args.operator_sheet.exists(), rel(args.operator_sheet))
    add_check(checks, "operator_sheet_columns", not row_errors, "; ".join(row_errors) if row_errors else "required columns present")
    add_check(checks, "operator_sheet_row_budget", len(rows) >= 1440, f"rows={len(rows)}")
    add_check(checks, "alias_map_exists", args.alias_map.exists(), rel(args.alias_map))
    add_check(checks, "alias_map_complete", not alias_errors and not alias_missing and len(aliases) >= 12, f"aliases={len(aliases)}, missing={alias_missing}, errors={alias_errors}")
    add_check(checks, "backend_module_ready", not backend_blockers, "; ".join(backend_blockers) if backend_blockers else "backend contract and provenance passed")
    add_check(checks, "task_config_dir_exists", args.task_config_dir.exists(), rel(args.task_config_dir))
    add_check(checks, "real_task_configs_ready", bool(tasks) and not config_blockers, "; ".join(config_blockers[:8]) if config_blockers else f"tasks={tasks}")
    add_check(checks, "fidelity_acceptance_ready", fidelity.get("acceptance_ready") is True, f"acceptance_ready={fidelity.get('acceptance_ready')!r}, readiness_state={fidelity.get('readiness_state')!r}")
    add_check(checks, "alias_unsealing_explicit", args.unsealed_alias_map is True, f"unsealed_alias_map={args.unsealed_alias_map!r}")
    add_check(checks, "run_id_specific", bool(args.run_id.strip()) and args.run_id != "paper119_external_validation_run", f"run_id={args.run_id!r}")
    add_check(checks, "output_logs_empty_or_force", args.force or not existing_logs, f"existing_nonempty_logs={[rel(path) for path in existing_logs[:8]]}, force={args.force!r}")
    add_check(checks, "video_dir_parent_exists", args.video_dir.exists() or args.video_dir.parent.exists(), rel(args.video_dir))

    blockers = [f"{check['name']}: {check['detail']}" for check in checks if not check["passed"]]
    collection_ready = not blockers
    return {
        "version": "external_collection_readiness_audit_v1",
        "passed": True,
        "not_external_evidence": True,
        "collection_ready": collection_ready,
        "readiness_state": "READY_TO_COLLECT_EXTERNAL_EVIDENCE" if collection_ready else "PREPARE_BACKEND_CONFIGS_AND_FIDELITY",
        "operator_sheet": rel(args.operator_sheet),
        "alias_map": rel(args.alias_map),
        "backend_module": args.backend_module,
        "task_config_dir": rel(args.task_config_dir),
        "output_log_dir": rel(args.output_log_dir),
        "video_dir": rel(args.video_dir),
        "run_id": args.run_id,
        "row_count": len(rows),
        "task_families": tasks,
        "alias_count": len(aliases),
        "blocking_missing_count": len(blockers),
        "blocking_missing": blockers,
        "checks": checks,
        "strict_collection_command": (
            "python external_validation\\runner\\real_collection_runner.py "
            "--backend-module <module_or_path> --task-config-dir external_validation\\configs "
            "--output-log-dir external_validation\\logs --video-dir external_validation\\videos "
            "--run-id <specific_run_id> --unsealed-alias-map"
        ),
        "post_collection_strict_commands": [
            r"python scripts\build_external_manifest.py --write --check-video-paths",
            r"python scripts\audit_external_release_package.py --strict",
            r"python scripts\audit_external_fidelity_acceptance.py --strict",
            r"python scripts\validate_external_adapters.py --strict",
            r"python scripts\validate_external_configs.py --strict",
            r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
            r"python scripts\audit_external_pairing_integrity.py --strict",
            r"python scripts\audit_external_evidence.py --strict",
        ],
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Collection Readiness Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Collection ready: `{str(payload['collection_ready']).lower()}`.",
        f"Readiness state: `{payload['readiness_state']}`.",
        f"Rows: `{payload['row_count']}`.",
        f"Task families: `{len(payload['task_families'])}`.",
        f"Blocking missing items: `{payload['blocking_missing_count']}`.",
        "",
        "This audit is a pre-collection gate for real robot or accepted high-fidelity simulator runs. It is not rollout evidence; it prevents starting collection until backend, configs, fidelity provenance, alias unsealing, output logs, and run identity are ready.",
        "",
        "## Strict Collection Command",
        "",
        "```powershell",
        payload["strict_collection_command"],
        "```",
        "",
        "## Blocking Missing",
        "",
    ]
    if payload["blocking_missing"]:
        for blocker in payload["blocking_missing"][:100]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight actual external collection readiness for Paper 119.")
    parser.add_argument("--backend-module", default="", help="Import path or .py file exposing create_backend() or Backend.")
    parser.add_argument("--operator-sheet", type=Path, default=DEFAULT_OPERATOR_SHEET)
    parser.add_argument("--alias-map", type=Path, default=DEFAULT_ALIAS_MAP)
    parser.add_argument("--task-config-dir", type=Path, default=DEFAULT_TASK_CONFIG_DIR)
    parser.add_argument("--output-log-dir", type=Path, default=DEFAULT_OUTPUT_LOG_DIR)
    parser.add_argument("--video-dir", type=Path, default=DEFAULT_VIDEO_DIR)
    parser.add_argument("--fidelity-audit", type=Path, default=DEFAULT_FIDELITY_AUDIT)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--run-id", default="paper119_external_validation_run")
    parser.add_argument("--unsealed-alias-map", action="store_true", help="Assert aliases are intentionally unsealed for actual execution.")
    parser.add_argument("--force", action="store_true", help="Allow non-empty output logs to be overwritten by the actual runner.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless actual collection is ready to start.")
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload)
    print(
        "External collection readiness audit: "
        f"collection_ready={payload['collection_ready']}; "
        f"blocking_missing={payload['blocking_missing_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["collection_ready"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())

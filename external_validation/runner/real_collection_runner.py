from __future__ import annotations

import argparse
import csv
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "external_validation"
RUNNER_DIR = EXTERNAL / "runner"
SCRIPTS_DIR = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from backend_contract import sha256_json, validate_backend_object  # noqa: E402
import validate_external_rollouts as rollout_validator  # noqa: E402


DEFAULT_OPERATOR_SHEET = EXTERNAL / "blinded_operator_sheet.csv"
DEFAULT_ALIAS_MAP = EXTERNAL / "method_alias_map.json"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
DEFAULT_CONFIG_DIR = EXTERNAL / "configs"
DEFAULT_TEMPLATE_CONFIG_DIR = EXTERNAL / "config_templates"
DEFAULT_OUTPUT_LOG_DIR = EXTERNAL / "logs"
DEFAULT_VIDEO_DIR = EXTERNAL / "videos"
MIN_OFFICIAL_VIDEO_BYTES = 512

REQUIRED_RECORD_FIELDS = (
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
)


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def read_rows(path: Path, *, max_rows: int | None) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"missing operator sheet: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if max_rows is not None:
        rows = rows[:max_rows]
    return rows


def import_module_from_value(value: str) -> ModuleType:
    path = Path(value)
    if path.exists():
        module_name = f"paper119_external_backend_{sha256_json(str(path))[:12]}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            fail(f"could not import backend module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module(value)


def create_backend(module_value: str) -> Any:
    module = import_module_from_value(module_value)
    if callable(getattr(module, "create_backend", None)):
        return module.create_backend()
    backend_class = getattr(module, "Backend", None)
    if backend_class is not None:
        return backend_class()
    fail("backend module must expose create_backend() or Backend")


def alias_lookup(alias_map_path: Path) -> dict[str, str]:
    payload = read_json(alias_map_path)
    aliases = payload.get("aliases", [])
    if not isinstance(aliases, list):
        fail("method alias map has invalid aliases list")
    lookup = {}
    for item in aliases:
        if not isinstance(item, dict):
            continue
        alias = str(item.get("alias", "")).strip()
        method = str(item.get("method", "")).strip()
        if alias and method:
            lookup[alias] = method
    if not lookup:
        fail("method alias map contains no aliases")
    return lookup


def config_path_for(task_family: str, config_dir: Path, *, dry_run: bool) -> Path:
    candidate = config_dir / f"{task_family}.json"
    if candidate.exists():
        return candidate
    if dry_run:
        template = DEFAULT_TEMPLATE_CONFIG_DIR / f"{task_family}.json"
        if template.exists():
            return template
    fail(f"missing task config for {task_family}: expected {candidate}")


def has_forbidden_template_values(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(has_forbidden_template_values(value) for value in payload.values())
    if isinstance(payload, list):
        return any(has_forbidden_template_values(value) for value in payload)
    return payload in {"FILL_AFTER_PLATFORM_SELECTION", "REPLACE_WITH_SOURCE_SKILL", "REPLACE_WITH_TARGET_SKILL"}


def load_task_config(task_family: str, config_dir: Path, *, dry_run: bool) -> dict[str, Any]:
    path = config_path_for(task_family, config_dir, dry_run=dry_run)
    config = read_json(path)
    config["_config_path"] = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    if not dry_run:
        if config.get("template_only") is True or config.get("not_external_evidence") is True:
            fail(f"refusing template/non-evidence config for actual collection: {path}")
        if has_forbidden_template_values(config):
            fail(f"refusing config with unfilled template placeholders: {path}")
    return config


def as_bool(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    fail(f"backend outcome field {field} must be boolean")


def as_float(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"backend field {field} must be numeric")
    return float(value)


def relative_video_path(path_text: str) -> str:
    path = Path(path_text)
    if path.is_absolute():
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve_returned_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def validate_official_video(video_path: str, *, expected_target: Path, video_dir: Path) -> None:
    path = resolve_returned_path(video_path)
    if path.resolve() != expected_target.resolve():
        fail(f"backend returned unexpected video path: got {path}, expected {expected_target}")
    if not is_under(path, video_dir):
        fail(f"backend video path is outside the official video directory: {path}")
    if path.suffix.lower() != ".mp4":
        fail(f"backend video path must end in .mp4: {path}")
    if not path.exists() or not path.is_file():
        fail(f"backend did not write expected video file: {path}")
    diagnostic_sidecar = Path(str(path) + ".diagnostic.json")
    if diagnostic_sidecar.exists():
        fail(f"backend produced diagnostic fallback video sidecar, which cannot be official evidence: {diagnostic_sidecar}")
    size = path.stat().st_size
    if size < MIN_OFFICIAL_VIDEO_BYTES:
        fail(f"backend video is too small for official evidence: {size} bytes at {path}")
    with path.open("rb") as handle:
        header = handle.read(16)
    if len(header) < 12 or header[4:8] != b"ftyp":
        fail(f"backend video is not MP4-like evidence with an ftyp box: {path}")


def validate_official_record(
    record: dict[str, Any],
    *,
    schema: dict[str, Any],
    manifest_methods: set[str],
    manifest_tasks: set[str],
    manifest_video_dirs: dict[str, Path],
) -> None:
    errors = rollout_validator.validate_record(
        record,
        line_id=f"{record.get('task_family', '<unknown>')}:{record.get('episode_index', '<unknown>')}:{record.get('method', '<unknown>')}",
        schema=schema,
        manifest_methods=manifest_methods,
        manifest_tasks=manifest_tasks,
        check_video_paths=True,
        manifest_video_dirs=manifest_video_dirs,
        strict_video_evidence=True,
    )
    if errors:
        fail("runner refused schema-invalid official JSONL record before write: " + "; ".join(errors[:5]))


def stage_log_path(log_path: Path, run_id: str) -> Path:
    token = sha256_json({"run_id": run_id, "log_path": log_path.as_posix()})[:12]
    return log_path.with_name(f"{log_path.name}.{token}.staging")


def backup_log_path(log_path: Path, run_id: str) -> Path:
    token = sha256_json({"run_id": run_id, "log_path": log_path.as_posix()})[:12]
    return log_path.with_name(f"{log_path.name}.{token}.backup")


def promote_pending_logs(pending_log_lines: dict[Path, list[str]], *, run_id: str) -> int:
    staged_paths: list[Path] = []
    backups: list[tuple[Path, Path, bool]] = []
    promoted_paths: list[Path] = []
    try:
        for log_path, lines in sorted(pending_log_lines.items()):
            log_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path = stage_log_path(log_path, run_id)
            if staged_path.exists():
                staged_path.unlink()
            staged_path.write_text("".join(lines), encoding="utf-8")
            staged_paths.append(staged_path)
        for log_path in sorted(pending_log_lines):
            backup_path = backup_log_path(log_path, run_id)
            if backup_path.exists():
                backup_path.unlink()
            had_original = log_path.exists()
            if had_original:
                log_path.replace(backup_path)
            backups.append((log_path, backup_path, had_original))
            stage_log_path(log_path, run_id).replace(log_path)
            promoted_paths.append(log_path)
    except OSError as exc:
        for log_path in reversed(promoted_paths):
            try:
                if log_path.exists():
                    log_path.unlink()
            except OSError:
                pass
        for log_path, backup_path, had_original in reversed(backups):
            try:
                if had_original and backup_path.exists():
                    backup_path.replace(log_path)
            except OSError:
                pass
        for staged_path in staged_paths:
            try:
                if staged_path.exists():
                    staged_path.unlink()
            except OSError:
                pass
        fail(f"failed to promote staged official JSONL logs: {exc}")
    for _, backup_path, _ in backups:
        try:
            if backup_path.exists():
                backup_path.unlink()
        except OSError:
            pass
    return sum(len(lines) for lines in pending_log_lines.values())


def build_record(
    *,
    row: dict[str, str],
    run_id: str,
    method_name: str,
    config: dict[str, Any],
    provenance: dict[str, Any],
    reset_result: dict[str, Any],
    terminal_samples: list[dict[str, Any]],
    proposal: dict[str, Any],
    outcome: dict[str, Any],
    video_path: str,
    policy_hash: str,
) -> dict[str, Any]:
    initial_state_hash = str(reset_result.get("initial_state_hash") or sha256_json(reset_result))
    terminal_sample_hash = str(proposal.get("terminal_sample_set_hash") or sha256_json(terminal_samples))
    record = {
        "run_id": run_id,
        "task_family": row["task_family"],
        "platform_type": str(provenance.get("platform_type") or config.get("platform_type") or row["platform_type"]),
        "platform_name": str(provenance.get("platform_name") or config.get("platform_name") or row["platform_name"]),
        "scene_id": row["scene_id"],
        "episode_index": int(row["episode_index"]),
        "seed": int(row["seed"]),
        "method": method_name,
        "skill_i": str(config["skill_i"]),
        "skill_j": str(config["skill_j"]),
        "initial_state_hash": initial_state_hash,
        "terminal_sample_set_hash": terminal_sample_hash,
        "basin_estimate": as_float(proposal.get("basin_estimate"), "basin_estimate"),
        "barrier_score": as_float(proposal.get("barrier_score"), "barrier_score"),
        "descent_continuity_score": as_float(proposal.get("descent_continuity_score"), "descent_continuity_score"),
        "predicted_seam_risk": as_float(proposal.get("predicted_seam_risk"), "predicted_seam_risk"),
        "fixed_risk_budget": as_float(config.get("fixed_risk_budget", 0.15), "fixed_risk_budget"),
        "decision": str(proposal.get("decision", "")),
        "failure_diagnosis": str(proposal.get("failure_diagnosis", "")),
        "repair_action": str(proposal.get("repair_action", "none")),
        "success": as_bool(outcome.get("success"), "success"),
        "seam_failure": as_bool(outcome.get("seam_failure"), "seam_failure"),
        "barrier_violation": as_bool(outcome.get("barrier_violation"), "barrier_violation"),
        "damage_or_intervention": as_bool(outcome.get("damage_or_intervention"), "damage_or_intervention"),
        "composition_cost": as_float(outcome.get("composition_cost"), "composition_cost"),
        "realized_seam_breach": as_bool(outcome.get("realized_seam_breach"), "realized_seam_breach"),
        "utility": as_float(outcome.get("utility"), "utility"),
        "video_path": relative_video_path(video_path),
        "policy_or_config_hash": policy_hash,
    }
    missing = [field for field in REQUIRED_RECORD_FIELDS if field not in record]
    if missing:
        fail(f"runner produced incomplete record: missing {missing}")
    return record


def dry_run_summary(rows: list[dict[str, str]], config_dir: Path, *, alias_map: dict[str, str] | None) -> dict[str, Any]:
    task_families = sorted({row["task_family"] for row in rows})
    aliases = sorted({row["method_alias"] for row in rows})
    config_paths = [config_path_for(task, config_dir, dry_run=True).relative_to(ROOT).as_posix() for task in task_families]
    return {
        "not_external_evidence": True,
        "dry_run": True,
        "rows_checked": len(rows),
        "task_families": task_families,
        "method_aliases": aliases,
        "alias_map_loaded": alias_map is not None,
        "task_config_paths": config_paths,
        "writes_logs": False,
    }


def run_collection(args: argparse.Namespace) -> int:
    rows = read_rows(args.operator_sheet, max_rows=args.max_rows)
    if not rows:
        fail("operator sheet has no rows")

    alias_map = alias_lookup(args.alias_map) if args.unsealed_alias_map else None
    if args.dry_run:
        summary = dry_run_summary(rows, args.task_config_dir, alias_map=alias_map)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if not args.backend_module:
        fail("--backend-module is required for actual collection")
    if alias_map is None:
        fail("actual collection requires --unsealed-alias-map so aliases are intentionally resolved")

    schema = read_json(args.schema)
    manifest_methods = set(alias_map.values())
    manifest_tasks = {row["task_family"] for row in rows}
    manifest_video_dirs = {task: args.video_dir / task for task in manifest_tasks}
    backend = create_backend(args.backend_module)
    backend_errors = validate_backend_object(backend)
    if backend_errors:
        fail("; ".join(backend_errors))
    provenance = backend.platform_provenance()
    if not isinstance(provenance, dict):
        fail("platform_provenance must return a dict")

    output_paths = sorted({args.output_log_dir / f"{row['task_family']}.jsonl" for row in rows})
    existing = [path for path in output_paths if path.exists() and path.stat().st_size > 0]
    if existing and not args.force:
        fail(f"refusing to append to existing output logs without --force: {existing[:3]}")
    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)

    config_cache: dict[str, dict[str, Any]] = {}
    pending_log_lines: dict[Path, list[str]] = {}
    for row in rows:
        task_family = row["task_family"]
        config = config_cache.get(task_family)
        if config is None:
            config = load_task_config(task_family, args.task_config_dir, dry_run=False)
            backend.load_task_config(task_family, config)
            config_cache[task_family] = config
        alias = row["method_alias"]
        if alias not in alias_map:
            fail(f"alias {alias!r} missing from method alias map")
        method_name = alias_map[alias]

        reset_spec = {"row": row, "task_config": config, "provenance": provenance}
        reset_result = backend.reset_scene(reset_spec)
        if not isinstance(reset_result, dict):
            fail("reset_scene must return a dict")
        observation = backend.capture_observation()
        if not isinstance(observation, dict):
            fail("capture_observation must return a dict")
        terminal_samples = backend.terminal_samples({"row": row, "config": config, "observation": observation})
        if not isinstance(terminal_samples, list) or not terminal_samples:
            fail("terminal_samples must return a non-empty list")
        proposal = backend.run_method(
            method_name,
            {
                "row": row,
                "config": config,
                "observation": observation,
                "terminal_samples": terminal_samples,
                "skill_i": config["skill_i"],
                "skill_j": config["skill_j"],
            },
        )
        if not isinstance(proposal, dict):
            fail("run_method must return a dict")
        outcome = backend.execute_skill_pair({"row": row, "config": config, "proposal": proposal})
        if not isinstance(outcome, dict):
            fail("execute_skill_pair must return a dict")
        target_video = args.video_dir / task_family / Path(row["expected_video_path"]).name
        target_video.parent.mkdir(parents=True, exist_ok=True)
        video_path = backend.record_video(target_video)
        validate_official_video(video_path, expected_target=target_video, video_dir=args.video_dir)
        policy_hash = str(proposal.get("policy_or_config_hash") or backend.policy_or_config_hash(method_name))
        record = build_record(
            row=row,
            run_id=args.run_id,
            method_name=method_name,
            config=config,
            provenance=provenance,
            reset_result=reset_result,
            terminal_samples=terminal_samples,
            proposal=proposal,
            outcome=outcome,
            video_path=video_path,
            policy_hash=policy_hash,
        )
        validate_official_record(
            record,
            schema=schema,
            manifest_methods=manifest_methods,
            manifest_tasks=manifest_tasks,
            manifest_video_dirs=manifest_video_dirs,
        )
        log_path = args.output_log_dir / f"{task_family}.jsonl"
        pending_log_lines.setdefault(log_path, []).append(json.dumps(record, sort_keys=True) + "\n")

    written = promote_pending_logs(pending_log_lines, run_id=args.run_id)
    print(f"External collection runner wrote {written} JSONL records. Not validated until manifest and strict audits pass.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed external collection runner for Paper 119.")
    parser.add_argument("--backend-module", default="", help="Import path or .py file exposing create_backend() or Backend.")
    parser.add_argument("--operator-sheet", type=Path, default=DEFAULT_OPERATOR_SHEET)
    parser.add_argument("--alias-map", type=Path, default=DEFAULT_ALIAS_MAP)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--task-config-dir", type=Path, default=DEFAULT_CONFIG_DIR)
    parser.add_argument("--output-log-dir", type=Path, default=DEFAULT_OUTPUT_LOG_DIR)
    parser.add_argument("--video-dir", type=Path, default=DEFAULT_VIDEO_DIR)
    parser.add_argument("--run-id", default="paper119_external_validation_run")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Check packet wiring without writing logs or videos.")
    parser.add_argument("--unsealed-alias-map", action="store_true", help="Intentionally resolve method aliases for execution.")
    parser.add_argument("--force", action="store_true", help="Clear existing output JSONL logs before writing.")
    args = parser.parse_args()

    if not args.schema.exists():
        fail(f"missing log schema: {args.schema}")
    return run_collection(args)


if __name__ == "__main__":
    raise SystemExit(main())

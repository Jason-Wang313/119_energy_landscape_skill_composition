from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import validate_external_rollouts as rollout_validator


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
GUARD_ROOT = EXTERNAL / "pilot_runtime_guard"
GUARD_LOG_DIR = GUARD_ROOT / "logs"
GUARD_VIDEO_DIR = GUARD_ROOT / "videos"
OUT_JSON = RESULTS / "maniskill_pilot_runtime_liveness_audit.json"
OUT_MD = RESULTS / "maniskill_pilot_runtime_liveness_audit.md"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def clear_guard_outputs() -> None:
    if GUARD_ROOT.exists():
        resolved = GUARD_ROOT.resolve()
        expected = (EXTERNAL / "pilot_runtime_guard").resolve()
        if resolved != expected:
            raise SystemExit(f"refusing to clear unexpected guard path: {resolved}")
        shutil.rmtree(GUARD_ROOT)
    GUARD_LOG_DIR.mkdir(parents=True, exist_ok=True)
    GUARD_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def load_methods() -> set[str]:
    payload = read_json(EXTERNAL / "method_alias_map.json")
    methods = set()
    for item in payload.get("aliases", []) or []:
        if isinstance(item, dict) and item.get("method"):
            methods.add(str(item["method"]))
    return methods


def load_tasks() -> set[str]:
    tasks = {path.stem for path in (EXTERNAL / "configs").glob("*.json") if path.is_file()}
    sheet = EXTERNAL / "blinded_operator_sheet.csv"
    if sheet.exists():
        with sheet.open(newline="", encoding="utf-8") as handle:
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


def count_videos(video_dir: Path) -> int:
    if not video_dir.exists():
        return 0
    return sum(1 for path in video_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".mp4")


def diagnostic_sidecars(video_dir: Path) -> list[Path]:
    if not video_dir.exists():
        return []
    return sorted(video_dir.rglob("*.mp4.diagnostic.json"))


def clean_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def coerce_output(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return ""


def parse_collection_progress(stdout: str) -> list[dict[str, Any]]:
    marker = "PAPER119_COLLECTION_STAGE "
    stages: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.startswith(marker):
            continue
        try:
            payload = json.loads(line[len(marker) :])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            stages.append(payload)
    return stages


def summarize_failure(
    *,
    timed_out: bool,
    returncode: int | None,
    stderr: str,
    records: int,
    videos: int,
    diagnostic_fallbacks: int,
    last_progress_stage: str,
) -> str:
    if records and videos and returncode == 0 and not timed_out and diagnostic_fallbacks:
        return "runner wrote quarantined schema-valid row/video using diagnostic non-evidence video fallback; render-backed video remains unavailable"
    if records and videos and returncode == 0 and not timed_out:
        return "pilot runtime produced schema-valid records and videos"
    if timed_out:
        if last_progress_stage:
            return f"runner timed out after progress stage {last_progress_stage} before producing the required pilot record/video"
        return "runner timed out before producing the required pilot record/video"
    cleaned = clean_ansi(stderr)
    runtime_errors = [line.strip() for line in cleaned.splitlines() if "RuntimeError:" in line]
    if runtime_errors:
        return runtime_errors[-1]
    if returncode not in (None, 0):
        if last_progress_stage:
            return f"runner exited with returncode {returncode} after progress stage {last_progress_stage} before producing the required pilot record/video"
        return f"runner exited with returncode {returncode} before producing the required pilot record/video"
    return "runner did not produce the required pilot record/video"


def run_guard(args: argparse.Namespace) -> dict[str, Any]:
    clear_guard_outputs()
    command = [
        sys.executable,
        "-u",
        "external_validation/runner/real_collection_runner.py",
        "--backend-module",
        "external_validation/runner/maniskill_reference_backend.py",
        "--task-config-dir",
        "external_validation/configs",
        "--output-log-dir",
        rel(GUARD_LOG_DIR),
        "--video-dir",
        rel(GUARD_VIDEO_DIR),
        "--run-id",
        args.run_id,
        "--unsealed-alias-map",
        "--max-rows",
        str(args.max_rows),
        "--force",
    ]
    env = os.environ.copy()
    env["PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS"] = "1"
    env["PAPER119_MANISKILL_REFERENCE_BACKEND_ALLOW_DIAGNOSTIC_VIDEO_FALLBACK"] = "1"
    env["PAPER119_COLLECTION_PROGRESS"] = "1"
    env.setdefault("PAPER119_MANISKILL_RENDER_BACKEND", args.render_backend)
    env.setdefault("PAPER119_MANISKILL_SHADER_PACK", args.shader_pack)
    env.setdefault("PAPER119_MANISKILL_RENDER_WIDTH", str(args.render_width))
    env.setdefault("PAPER119_MANISKILL_RENDER_HEIGHT", str(args.render_height))
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=args.timeout_seconds,
        )
        timed_out = False
        returncode = proc.returncode
        stdout = coerce_output(proc.stdout)
        stderr = coerce_output(proc.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = coerce_output(exc.stdout)
        stderr = coerce_output(exc.stderr)
    progress_stages = parse_collection_progress(stdout)
    last_progress_stage = str(progress_stages[-1].get("stage", "")) if progress_stages else ""
    records, parse_errors, log_paths = load_records(GUARD_LOG_DIR)
    schema = read_json(EXTERNAL / "log_schema_v1.json")
    methods = load_methods()
    tasks = load_tasks()
    schema_errors: list[str] = list(parse_errors)
    for index, record in enumerate(records, start=1):
        schema_errors.extend(
            rollout_validator.validate_record(
                record,
                line_id=f"pilot_runtime_guard:{index}",
                schema=schema,
                manifest_methods=methods,
                manifest_tasks=tasks,
                check_video_paths=True,
            )
        )
    videos_written = count_videos(GUARD_VIDEO_DIR)
    diagnostic_fallback_paths = diagnostic_sidecars(GUARD_VIDEO_DIR)
    failure_summary = summarize_failure(
        timed_out=timed_out,
        returncode=returncode,
        stderr=stderr,
        records=len(records),
        videos=videos_written,
        diagnostic_fallbacks=len(diagnostic_fallback_paths),
        last_progress_stage=last_progress_stage,
    )
    runner_io_ready = (
        not timed_out
        and returncode == 0
        and len(records) >= args.max_rows
        and videos_written >= args.max_rows
        and not schema_errors
    )
    render_video_ready = runner_io_ready and not diagnostic_fallback_paths
    pilot_runtime_ready = render_video_ready
    return {
        "command": command,
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
        "collection_progress_stages": progress_stages[-40:],
        "last_progress_stage": last_progress_stage,
        "records_observed": len(records),
        "videos_written": videos_written,
        "failure_summary": failure_summary,
        "schema_errors": schema_errors,
        "log_files": [rel(path) for path in log_paths],
        "diagnostic_video_fallbacks": [rel(path) for path in diagnostic_fallback_paths],
        "runner_io_ready": runner_io_ready,
        "render_video_ready": render_video_ready,
        "pilot_runtime_ready": pilot_runtime_ready,
        "render_backend": env.get("PAPER119_MANISKILL_RENDER_BACKEND", ""),
        "shader_pack": env.get("PAPER119_MANISKILL_SHADER_PACK", ""),
        "render_width": int(env.get("PAPER119_MANISKILL_RENDER_WIDTH", "0") or 0),
        "render_height": int(env.get("PAPER119_MANISKILL_RENDER_HEIGHT", "0") or 0),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    result = run_guard(args)
    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "runtime_guard_is_non_evidence",
        True,
        "the guard writes only a liveness report and quarantined pilot_runtime_guard outputs",
    )
    add_check(
        checks,
        "quarantine_paths_are_not_official_evidence",
        is_under(GUARD_LOG_DIR, GUARD_ROOT)
        and is_under(GUARD_VIDEO_DIR, GUARD_ROOT)
        and not is_under(GUARD_LOG_DIR, EXTERNAL / "logs")
        and not is_under(GUARD_VIDEO_DIR, EXTERNAL / "videos"),
        f"log_dir={rel(GUARD_LOG_DIR)}, video_dir={rel(GUARD_VIDEO_DIR)}",
    )
    add_check(
        checks,
        "bounded_runner_subprocess_exercised",
        result["timed_out"] or result["returncode"] is not None,
        f"timeout_seconds={args.timeout_seconds}, timed_out={result['timed_out']}, returncode={result['returncode']}",
    )
    add_check(
        checks,
        "collection_progress_markers_recorded",
        (not result["timed_out"]) or bool(result["last_progress_stage"]),
        f"last_progress_stage={result['last_progress_stage']!r}",
    )
    add_check(
        checks,
        "timeout_or_result_recorded_as_readiness_state",
        (result["timed_out"] and not result["pilot_runtime_ready"]) or isinstance(result["returncode"], int),
        f"pilot_runtime_ready={result['pilot_runtime_ready']}",
    )
    add_check(
        checks,
        "ready_requires_schema_valid_records_and_videos",
        (
            not result["pilot_runtime_ready"]
            or (
                result["records_observed"] >= args.max_rows
                and result["videos_written"] >= args.max_rows
                and not result["schema_errors"]
            )
        ),
        (
            f"records={result['records_observed']}, videos={result['videos_written']}, "
            f"schema_errors={len(result['schema_errors'])}"
        ),
    )
    add_check(
        checks,
        "runner_io_ready_allows_only_quarantined_diagnostic_fallback",
        (
            not result["runner_io_ready"]
            or (
                result["records_observed"] >= args.max_rows
                and result["videos_written"] >= args.max_rows
                and all(path.startswith("external_validation/pilot_runtime_guard/") for path in result["diagnostic_video_fallbacks"])
            )
        ),
        (
            f"runner_io_ready={result['runner_io_ready']}, "
            f"diagnostic_fallbacks={len(result['diagnostic_video_fallbacks'])}"
        ),
    )
    add_check(
        checks,
        "diagnostic_fallback_does_not_mark_render_ready",
        (not result["diagnostic_video_fallbacks"] and result["render_video_ready"] == result["pilot_runtime_ready"])
        or (bool(result["diagnostic_video_fallbacks"]) and result["render_video_ready"] is False and result["pilot_runtime_ready"] is False),
        (
            f"render_video_ready={result['render_video_ready']}, "
            f"pilot_runtime_ready={result['pilot_runtime_ready']}, "
            f"diagnostic_fallbacks={len(result['diagnostic_video_fallbacks'])}"
        ),
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent",
    )
    passed = all(check["passed"] for check in checks)
    blocking_missing = []
    if not result["pilot_runtime_ready"]:
        if result["runner_io_ready"] and result["diagnostic_video_fallbacks"]:
            blocking_missing.append(
                "bounded ManiSkill reference runner produced a quarantined schema-valid pilot row/video only by using "
                "a diagnostic non-evidence video fallback; render-backed RGB video remains unavailable, so use an "
                "accepted GPU/render machine or fix the renderer before official collection"
            )
        else:
            blocking_missing.append(
                "bounded ManiSkill reference runner did not produce a complete schema-valid pilot row/video on this machine; "
                f"{result['failure_summary']}; use an accepted GPU/render machine or fix the backend before official collection"
            )
    return {
        "version": "maniskill_pilot_runtime_liveness_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "pilot_runtime_ready": result["pilot_runtime_ready"],
        "runner_io_ready": result["runner_io_ready"],
        "render_video_ready": result["render_video_ready"],
        "readiness_state": "PILOT_RUNTIME_READY" if result["pilot_runtime_ready"] else "PILOT_RUNTIME_NOT_READY",
        "timeout_seconds": args.timeout_seconds,
        "max_rows": args.max_rows,
        "run_id": args.run_id,
        "render_backend": result["render_backend"],
        "shader_pack": result["shader_pack"],
        "render_width": result["render_width"],
        "render_height": result["render_height"],
        "log_dir": rel(GUARD_LOG_DIR),
        "video_dir": rel(GUARD_VIDEO_DIR),
        "records_observed": result["records_observed"],
        "videos_written": result["videos_written"],
        "failure_summary": result["failure_summary"],
        "last_progress_stage": result["last_progress_stage"],
        "collection_progress_stages": result["collection_progress_stages"],
        "timed_out": result["timed_out"],
        "returncode": result["returncode"],
        "schema_errors": result["schema_errors"],
        "log_files": result["log_files"],
        "diagnostic_video_fallbacks": result["diagnostic_video_fallbacks"],
        "blocking_missing": blocking_missing,
        "command": " ".join(result["command"]),
        "stdout_tail": result["stdout_tail"],
        "stderr_tail": result["stderr_tail"],
        "checks": checks,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ManiSkill Pilot Runtime Liveness Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Pilot runtime ready: `{str(payload['pilot_runtime_ready']).lower()}`.",
        f"Runner I/O ready: `{str(payload['runner_io_ready']).lower()}`.",
        f"Render video ready: `{str(payload['render_video_ready']).lower()}`.",
        f"Readiness state: `{payload['readiness_state']}`.",
        f"Render backend: `{payload['render_backend']}`.",
        f"Shader pack: `{payload['shader_pack']}`.",
        f"Render size: `{payload['render_width']}x{payload['render_height']}`.",
        f"Timed out: `{str(payload['timed_out']).lower()}`.",
        f"Records observed: `{payload['records_observed']}`.",
        f"Videos written: `{payload['videos_written']}`.",
        f"Diagnostic video fallbacks: `{len(payload['diagnostic_video_fallbacks'])}`.",
        f"Failure summary: `{payload['failure_summary']}`.",
        f"Last progress stage: `{payload['last_progress_stage'] or 'none'}`.",
        "",
        "This bounded liveness audit launches the tracked ManiSkill reference runner in a subprocess against quarantined `pilot_runtime_guard` directories. It is not rollout evidence and cannot satisfy the external evidence gate; it only prevents a slow CPU/render backend from silently blocking an official collection attempt.",
        "",
        "## Command",
        "",
        "```powershell",
        payload["command"],
        "```",
        "",
        "## Blocking Missing",
        "",
    ]
    if payload["blocking_missing"]:
        for item in payload["blocking_missing"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    if payload["schema_errors"]:
        lines.extend(["", "## Schema Errors", ""])
        for error in payload["schema_errors"][:50]:
            lines.append(f"- {error}")
    lines.extend(["", "## Collection Progress", ""])
    if payload["collection_progress_stages"]:
        for stage in payload["collection_progress_stages"][-20:]:
            lines.append(f"- `{stage.get('stage')}`: {stage}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded liveness audit for the ManiSkill pilot runner path.")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--max-rows", type=int, default=1)
    parser.add_argument("--run-id", default="paper119_pilot_runtime_guard_local")
    parser.add_argument("--render-backend", default="cpu")
    parser.add_argument("--shader-pack", default="minimal")
    parser.add_argument("--render-width", type=int, default=128)
    parser.add_argument("--render-height", type=int, default=128)
    args = parser.parse_args()
    payload = build_payload(args)
    write_outputs(payload)
    print(
        "ManiSkill pilot runtime liveness audit: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"pilot_runtime_ready={payload['pilot_runtime_ready']}; "
        f"timed_out={payload['timed_out']}; "
        f"records={payload['records_observed']}; videos={payload['videos_written']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

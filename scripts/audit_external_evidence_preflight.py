from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

DEFAULT_MANIFEST = EXTERNAL / "manifest.json"
DEFAULT_TEMPLATE = EXTERNAL / "manifest_template.json"
OUT_JSON = RESULTS / "external_evidence_preflight.json"
OUT_MD = RESULTS / "external_evidence_preflight.md"

PRIMARY_METHOD = "barrier_certified_energy_composer_v5"
ORACLE_METHOD = "oracle_basin_composer"


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def count_jsonl_records(path: Path) -> tuple[int, int]:
    records = 0
    parse_errors = 0
    if not path.exists():
        return records, parse_errors
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            records += 1
            try:
                json.loads(raw)
            except json.JSONDecodeError:
                parse_errors += 1
    return records, parse_errors


def is_probably_placeholder_video(path: Path) -> bool:
    name = path.name.lower()
    if "placeholder" in name or "not_external_evidence" in name:
        return True
    return path.stat().st_size < 1024


def video_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(
        child
        for child in directory.rglob("*")
        if child.is_file() and child.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".webm"}
    )


def inspect_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "sha256": "", "is_template": None, "version": ""}
    payload = read_json(path)
    version = str(payload.get("version", ""))
    is_template = bool(payload.get("not_external_evidence") is True or "template" in version.lower())
    return {
        "exists": True,
        "sha256": sha256_file(path),
        "is_template": is_template,
        "version": version,
    }


def inspect_implementation(path_value: str) -> dict[str, Any]:
    if not path_value:
        return {
            "exists": False,
            "sha256": "",
            "is_scaffold": None,
            "detail": "implementation path is empty",
        }
    path = rel_path(path_value)
    if not path.exists():
        return {
            "exists": False,
            "sha256": "",
            "is_scaffold": None,
            "detail": f"missing {path_value}",
        }
    if path.is_dir():
        files = sorted(child for child in path.rglob("*") if child.is_file())
        digest = hashlib.sha256()
        scaffold = False
        for child in files:
            text = child.read_text(encoding="utf-8", errors="ignore") if child.suffix in {".py", ".json", ".md"} else ""
            scaffold = scaffold or "NotImplementedError" in text or "adapter_template.py" in child.name
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(sha256_file(child).encode("ascii"))
            digest.update(b"\0")
        return {
            "exists": True,
            "sha256": digest.hexdigest().upper(),
            "is_scaffold": scaffold,
            "detail": f"{len(files)} files",
        }
    text = path.read_text(encoding="utf-8", errors="ignore") if path.suffix in {".py", ".json", ".md"} else ""
    return {
        "exists": True,
        "sha256": sha256_file(path),
        "is_scaffold": "NotImplementedError" in text or path.name == "adapter_template.py",
        "detail": rel(path),
    }


def missing_if(condition: bool, message: str, out: list[str]) -> None:
    if condition:
        out.append(message)


def inspect_tasks(manifest: dict[str, Any], method_count: int) -> tuple[list[dict[str, Any]], list[str], int, int]:
    task_reports: list[dict[str, Any]] = []
    blockers: list[str] = []
    expected_total = 0
    observed_total = 0
    for task in manifest.get("tasks", []):
        if not isinstance(task, dict):
            blockers.append("manifest task entry is not an object")
            continue
        task_family = str(task.get("task_family", "unknown"))
        expected = int(task.get("episodes_per_method", 0) or 0) * method_count
        expected_total += expected
        task_missing: list[str] = []

        missing_if(str(task.get("platform_type", "")) not in {"real_robot", "high_fidelity_sim"}, "platform_type must be real_robot or high_fidelity_sim", task_missing)
        missing_if(not str(task.get("platform_name", "")).strip(), "platform_name is empty", task_missing)

        log_path = rel_path(str(task.get("log_jsonl", "")))
        log_exists = log_path.exists()
        records, parse_errors = count_jsonl_records(log_path)
        observed_total += records
        missing_if(not log_exists, f"log_jsonl is missing: {task.get('log_jsonl', '')}", task_missing)
        missing_if(log_exists and records < expected, f"log_jsonl has {records} records, expected at least {expected}", task_missing)
        missing_if(parse_errors > 0, f"log_jsonl has {parse_errors} JSON parse errors", task_missing)

        video_dir = rel_path(str(task.get("video_dir", "")))
        videos = video_files(video_dir)
        real_videos = [path for path in videos if not is_probably_placeholder_video(path)]
        missing_if(not video_dir.exists(), f"video_dir is missing: {task.get('video_dir', '')}", task_missing)
        missing_if(video_dir.exists() and not real_videos, "video_dir has no non-placeholder rollout videos", task_missing)

        config_path = rel_path(str(task.get("config_path", "")))
        config = inspect_config(config_path)
        missing_if(not config["exists"], f"config_path is missing: {task.get('config_path', '')}", task_missing)
        missing_if(config["exists"] and config["is_template"] is True, "config_path still appears to be a non-evidence template", task_missing)
        declared_hash = str(task.get("config_hash", ""))
        missing_if(not declared_hash, "config_hash is empty", task_missing)
        missing_if(bool(declared_hash and config["sha256"] and declared_hash.upper() != config["sha256"]), "config_hash does not match config file", task_missing)

        for item in task_missing:
            blockers.append(f"{task_family}: {item}")
        task_reports.append(
            {
                "task_family": task_family,
                "platform_type": task.get("platform_type"),
                "platform_name": task.get("platform_name"),
                "expected_records": expected,
                "observed_records": records,
                "log_exists": log_exists,
                "video_dir_exists": video_dir.exists(),
                "non_placeholder_videos": len(real_videos),
                "config_exists": bool(config["exists"]),
                "config_is_template": config["is_template"],
                "missing": task_missing,
            }
        )
    return task_reports, blockers, expected_total, observed_total


def inspect_methods(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    method_reports: list[dict[str, Any]] = []
    blockers: list[str] = []
    for method in manifest.get("methods", []):
        if not isinstance(method, dict):
            blockers.append("manifest method entry is not an object")
            continue
        name = str(method.get("name", "unknown"))
        method_missing: list[str] = []
        if name == ORACLE_METHOD:
            missing_if(method.get("implementation") != "post_hoc_upper_bound", "oracle must remain post_hoc_upper_bound", method_missing)
        else:
            implementation = inspect_implementation(str(method.get("implementation", "")))
            missing_if(not implementation["exists"], f"implementation missing: {implementation['detail']}", method_missing)
            missing_if(implementation["exists"] and implementation["is_scaffold"] is True, "implementation appears to be a scaffold/template", method_missing)

            checkpoint_path = str(method.get("checkpoint_or_config_path", ""))
            checkpoint_exists = bool(checkpoint_path and rel_path(checkpoint_path).exists())
            missing_if(not checkpoint_path, "checkpoint_or_config_path is empty", method_missing)
            missing_if(bool(checkpoint_path and not checkpoint_exists), f"checkpoint_or_config_path is missing: {checkpoint_path}", method_missing)
            declared_hash = str(method.get("checkpoint_or_config_hash", ""))
            missing_if(not declared_hash, "checkpoint_or_config_hash is empty", method_missing)
        for item in method_missing:
            blockers.append(f"{name}: {item}")
        method_reports.append(
            {
                "name": name,
                "role": "primary" if name == PRIMARY_METHOD else ("oracle" if name == ORACLE_METHOD else "baseline"),
                "implementation": method.get("implementation", ""),
                "checkpoint_or_config_path": method.get("checkpoint_or_config_path", ""),
                "missing": method_missing,
            }
        )
    return method_reports, blockers


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight a real external evidence package without treating scaffolds as evidence.")
    parser.add_argument("--manifest", type=Path, default=None, help="Draft or real external manifest to inspect.")
    args = parser.parse_args()

    manifest_path = args.manifest
    real_manifest_exists = DEFAULT_MANIFEST.exists()
    if manifest_path is None:
        manifest_path = DEFAULT_MANIFEST if real_manifest_exists else DEFAULT_TEMPLATE
    if not manifest_path.exists():
        raise SystemExit(f"missing manifest or template: {manifest_path}")

    manifest = read_json(manifest_path)
    method_count = len([item for item in manifest.get("methods", []) if isinstance(item, dict)])
    task_reports, task_blockers, expected_records, observed_records = inspect_tasks(manifest, method_count)
    method_reports, method_blockers = inspect_methods(manifest)

    global_blockers: list[str] = []
    for field in ("code_commit", "skill_library_hash"):
        missing_if(not str(manifest.get(field, "")).strip(), f"{field} is empty", global_blockers)
    for field in ("shared_skill_library", "same_initial_states", "same_observation_interface", "same_compute_budget", "paired_resets"):
        missing_if(manifest.get(field) is not True, f"{field} must be true", global_blockers)
    missing_if(not real_manifest_exists, "external_validation/manifest.json has not been written from real evidence", global_blockers)

    release = manifest.get("release_artifacts", {}) if isinstance(manifest.get("release_artifacts", {}), dict) else {}
    release_counts = {kind: len(release.get(kind, []) or []) for kind in ("code", "configs", "logs", "videos", "checkpoints")}
    for kind in ("configs", "logs", "videos", "checkpoints"):
        missing_if(release_counts.get(kind, 0) == 0, f"release_artifacts.{kind} is empty", global_blockers)

    blockers = global_blockers + task_blockers + method_blockers
    evidence_ready = bool(real_manifest_exists and not blockers and expected_records >= 1440 and observed_records >= expected_records)
    payload = {
        "version": "external_evidence_preflight_v1",
        "passed": True,
        "not_external_evidence": True,
        "evidence_ready": evidence_ready,
        "readiness_state": "READY_FOR_STRICT_AUDIT" if evidence_ready else "COLLECT_EXTERNAL_EVIDENCE",
        "manifest_source": rel(manifest_path),
        "real_manifest_exists": real_manifest_exists,
        "expected_records": expected_records,
        "observed_records": observed_records,
        "task_count": len(task_reports),
        "method_count": len(method_reports),
        "blocking_missing_count": len(blockers),
        "global_blockers": global_blockers,
        "task_reports": task_reports,
        "method_reports": method_reports,
        "release_artifact_counts": release_counts,
        "blocking_missing": blockers,
        "operator_next_actions": [
            "Collect real-robot or accepted high-fidelity simulator rollouts; do not use local_dry_run logs as evidence.",
            "Copy manifest_template.json to external_validation/manifest.json only after platform, configs, logs, videos, implementations, and hashes are real.",
            "Fill platform_name, code_commit, skill_library_hash, task config hashes, method implementation paths, and checkpoint/config hashes.",
            "Record at least the manifest-declared episodes_per_method for every declared method and task family with paired reset identifiers.",
            "Run build_external_manifest.py --write --check-video-paths, validate_external_configs.py --strict, validate_external_adapters.py --strict, validate_external_rollouts.py --write-results --check-video-paths --strict, and audit_external_evidence.py --strict.",
        ],
    }

    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Evidence Preflight",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Evidence ready: `{str(evidence_ready).lower()}`.",
        f"Readiness state: `{payload['readiness_state']}`.",
        f"Manifest source: `{payload['manifest_source']}`.",
        f"Expected records: `{expected_records}`.",
        f"Observed records: `{observed_records}`.",
        f"Blocking missing items: `{len(blockers)}`.",
        "",
        "This report is an operator preflight for real external validation artifacts. It is not robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for the strict external audits.",
        "",
        "## Task Matrix",
        "",
        "| Task | Expected | Observed | Log | Videos | Config | Missing |",
        "|---|---:|---:|---|---:|---|---|",
    ]
    for task in task_reports:
        missing = "; ".join(task["missing"]) if task["missing"] else "none"
        lines.append(
            f"| `{task['task_family']}` | {task['expected_records']} | {task['observed_records']} | "
            f"{'yes' if task['log_exists'] else 'no'} | {task['non_placeholder_videos']} | "
            f"{'yes' if task['config_exists'] else 'no'} | {missing} |"
        )
    lines.extend([
        "",
        "## Method Matrix",
        "",
        "| Method | Role | Missing |",
        "|---|---|---|",
    ])
    for method in method_reports:
        missing = "; ".join(method["missing"]) if method["missing"] else "none"
        lines.append(f"| `{method['name']}` | `{method['role']}` | {missing} |")
    lines.extend(["", "## Global Blockers", ""])
    if global_blockers:
        for blocker in global_blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    lines.extend(["", "## Operator Next Actions", ""])
    for action in payload["operator_next_actions"]:
        lines.append(f"- {action}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        "External evidence preflight: "
        f"{payload['readiness_state']}; missing={len(blockers)}; "
        f"observed_records={observed_records}/{expected_records}; not_evidence=True"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

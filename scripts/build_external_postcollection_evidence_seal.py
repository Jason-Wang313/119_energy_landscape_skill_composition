from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = EXTERNAL / "postcollection_evidence_seal.json"
OUT_MD = EXTERNAL / "postcollection_evidence_seal.md"
OUT_CSV = EXTERNAL / "postcollection_evidence_seal.csv"
AUDIT_JSON = RESULTS / "external_postcollection_evidence_seal_audit.json"
AUDIT_MD = RESULTS / "external_postcollection_evidence_seal_audit.md"

VERSION = "external_postcollection_evidence_seal_v1"
AUDIT_VERSION = "external_postcollection_evidence_seal_audit_v1"
PLACEHOLDER_RUN_ID = "paper119_external_validation_run"


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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def artifact(path: Path, role: str, *, required_for_real_seal: bool = True) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    return {
        "path": rel(path),
        "role": role,
        "exists": exists,
        "bytes": path.stat().st_size if exists else 0,
        "sha256": sha256_file(path) if exists else "",
        "required_for_real_seal": required_for_real_seal,
    }


def glob_files(path: Path, patterns: tuple[str, ...]) -> list[Path]:
    if not path.exists():
        return []
    files: list[Path] = []
    for pattern in patterns:
        files.extend(child for child in path.rglob(pattern) if child.is_file())
    return sorted(set(files))


def read_jsonl_count(path: Path) -> tuple[int, int, list[str]]:
    records = 0
    invalid = 0
    video_paths: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError:
                invalid += 1
                continue
            records += 1
            if isinstance(row, dict) and row.get("video_path"):
                video_paths.append(str(row.get("video_path")))
    return records, invalid, video_paths


def collect_log_summary(log_files: list[Path]) -> dict[str, Any]:
    total_records = 0
    total_invalid = 0
    referenced_videos: list[str] = []
    per_file: list[dict[str, Any]] = []
    for path in log_files:
        records, invalid, videos = read_jsonl_count(path)
        total_records += records
        total_invalid += invalid
        referenced_videos.extend(videos)
        per_file.append(
            {
                "path": rel(path),
                "records": records,
                "invalid_json_lines": invalid,
                "referenced_video_count": len(videos),
            }
        )
    return {
        "jsonl_file_count": len(log_files),
        "jsonl_record_count": total_records,
        "invalid_json_line_count": total_invalid,
        "referenced_video_count": len(referenced_videos),
        "unique_referenced_video_count": len(set(referenced_videos)),
        "per_file": per_file,
    }


def strict_command_sequence(args: argparse.Namespace) -> list[str]:
    backend = args.backend_module or "<module_or_path>"
    run_id = args.run_id or "<specific_run_id>"
    return [
        r"python scripts\audit_external_collection_readiness.py --strict --backend-module "
        f"{backend} --task-config-dir external_validation\\configs --run-id {run_id} --unsealed-alias-map",
        r"python scripts\build_external_precollection_freeze_receipt.py --backend-module "
        f"{backend} --run-id {run_id} --operator-id <operator_or_lab> "
        r"--collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
        r"python external_validation\runner\real_collection_runner.py --backend-module "
        f"{backend} --task-config-dir external_validation\\configs --output-log-dir "
        rf"external_validation\logs --video-dir external_validation\videos --run-id {run_id} --unsealed-alias-map",
        r"python scripts\build_external_postcollection_evidence_seal.py --backend-module "
        f"{backend} --run-id {run_id} --operator-id <operator_or_lab> "
        r"--collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
        r"python scripts\audit_external_postcollection_seal_consistency.py",
        r"python scripts\build_external_manifest.py --write --check-video-paths",
        r"python scripts\validate_external_configs.py --strict",
        r"python scripts\validate_external_adapters.py --strict",
        r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
        r"python scripts\audit_external_pairing_integrity.py --strict",
        r"python scripts\audit_external_release_package.py --strict",
        r"python scripts\audit_external_evidence.py --strict",
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    collection_plan = read_json(RESULTS / "external_collection_plan.json")
    precollection_freeze = read_json(RESULTS / "external_precollection_freeze_receipt_audit.json")
    rollout_metrics = read_json(RESULTS / "external_rollout_metrics.json")
    config_evidence = read_json(RESULTS / "external_config_evidence_audit.json")
    adapter_evidence = read_json(RESULTS / "external_adapter_contract_evidence_audit.json")
    external_evidence = read_json(RESULTS / "external_evidence_audit.json")

    log_files = glob_files(EXTERNAL / "logs", ("*.jsonl",))
    video_files = glob_files(EXTERNAL / "videos", ("*.mp4",))
    config_files = glob_files(EXTERNAL / "configs", ("*.json",))
    log_summary = collect_log_summary(log_files)
    expected_records = int(collection_plan.get("total_required_records", 0) or 0)
    run_id_specific = bool(args.run_id.strip()) and args.run_id != PLACEHOLDER_RUN_ID
    operator_metadata_ready = all(
        bool(str(value).strip())
        for value in (args.operator_id, args.collection_machine, args.date_sealed)
    )

    seal_artifacts: list[dict[str, Any]] = [
        artifact(EXTERNAL / "precollection_freeze_receipt.json", "precollection_freeze_receipt"),
        artifact(EXTERNAL / "operator_record_sheet.csv", "operator_record_sheet"),
        artifact(EXTERNAL / "blinded_operator_sheet.csv", "blinded_operator_sheet"),
        artifact(EXTERNAL / "method_alias_map.json", "method_alias_map"),
        artifact(EXTERNAL / "method_manifest_cutover_checklist.csv", "method_cutover_checklist"),
        artifact(EXTERNAL / "method_reference_provenance.csv", "method_reference_provenance"),
        artifact(EXTERNAL / "manifest_precollection_draft.json", "precollection_manifest_draft"),
    ]
    seal_artifacts.extend(artifact(path, "prepared_or_manifest_task_config") for path in config_files)
    seal_artifacts.extend(artifact(path, "official_raw_jsonl_log") for path in log_files)
    seal_artifacts.extend(artifact(path, "official_rollout_video") for path in video_files)

    missing_real_artifact_roles = [
        "official_raw_jsonl_log" if not log_files else "",
        "official_rollout_video" if not video_files else "",
    ]
    missing_real_artifact_roles = [item for item in missing_real_artifact_roles if item]
    postcollection_seal_ready = (
        precollection_freeze.get("freeze_receipt_ready") is True
        and run_id_specific
        and operator_metadata_ready
        and expected_records > 0
        and log_summary["jsonl_record_count"] >= expected_records
        and log_summary["invalid_json_line_count"] == 0
        and len(video_files) >= expected_records
        and not (EXTERNAL / "manifest.json").exists()
    )

    return {
        "version": VERSION,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "postcollection_seal_ready": postcollection_seal_ready,
        "ready_for_manifest_promotion": postcollection_seal_ready,
        "backend_module": args.backend_module,
        "run_id": args.run_id,
        "operator_id": args.operator_id,
        "collection_machine": args.collection_machine,
        "date_sealed": args.date_sealed,
        "expected_records": expected_records,
        "jsonl_log_count": len(log_files),
        "jsonl_record_count": log_summary["jsonl_record_count"],
        "invalid_json_line_count": log_summary["invalid_json_line_count"],
        "rollout_video_count": len(video_files),
        "prepared_config_count": len(config_files),
        "manifest_exists_before_seal": (EXTERNAL / "manifest.json").exists(),
        "precollection_freeze_ready": precollection_freeze.get("freeze_receipt_ready") is True,
        "strict_rollout_metrics_ready": rollout_metrics.get("passed") is True,
        "strict_config_evidence_ready": config_evidence.get("passed") is True,
        "strict_adapter_evidence_ready": adapter_evidence.get("passed") is True,
        "strict_final_external_evidence_ready": external_evidence.get("submission_ready") is True,
        "missing_real_artifact_roles": missing_real_artifact_roles,
        "log_summary": log_summary,
        "seal_artifacts": seal_artifacts,
        "operator_regeneration_command": (
            "python scripts\\build_external_postcollection_evidence_seal.py "
            "--backend-module <module_or_path> --run-id <specific_run_id> "
            "--operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> "
            "--date-sealed <YYYY-MM-DD>"
        ),
        "strict_command_sequence": strict_command_sequence(args),
        "evidence_boundary": (
            "This seal hashes raw postcollection files and collection metadata before manifest promotion. "
            "It is not a manifest, metric result, rollout validation pass, fidelity acceptance, or external evidence."
        ),
    }


def build_audit(payload: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    command_text = "\n".join(payload.get("strict_command_sequence", []) or [])
    artifacts = payload.get("seal_artifacts", []) or []

    add_check(
        checks,
        "seal_is_non_evidence_and_fail_closed",
        payload.get("not_external_evidence") is True
        and payload.get("strict_external_evidence_ready") is False
        and payload.get("ready_for_manifest_promotion") == payload.get("postcollection_seal_ready"),
        (
            f"not_external_evidence={payload.get('not_external_evidence')!r}, "
            f"strict_external_evidence_ready={payload.get('strict_external_evidence_ready')!r}, "
            f"postcollection_seal_ready={payload.get('postcollection_seal_ready')!r}, "
            f"ready_for_manifest_promotion={payload.get('ready_for_manifest_promotion')!r}"
        ),
    )
    add_check(
        checks,
        "precollection_freeze_loaded_but_not_real_ready",
        payload.get("precollection_freeze_ready") is False or payload.get("postcollection_seal_ready") is True,
        f"precollection_freeze_ready={payload.get('precollection_freeze_ready')!r}",
    )
    add_check(
        checks,
        "raw_logs_and_videos_absent_before_collection",
        (
            int(payload.get("jsonl_log_count", 0) or 0) == 0
            and int(payload.get("jsonl_record_count", 0) or 0) == 0
            and int(payload.get("rollout_video_count", 0) or 0) == 0
        )
        or payload.get("postcollection_seal_ready") is True,
        (
            f"logs={payload.get('jsonl_log_count')!r}, "
            f"records={payload.get('jsonl_record_count')!r}, "
            f"videos={payload.get('rollout_video_count')!r}"
        ),
    )
    add_check(
        checks,
        "operator_metadata_still_required",
        (
            not payload.get("operator_id")
            and not payload.get("collection_machine")
            and not payload.get("date_sealed")
            and payload.get("run_id") == PLACEHOLDER_RUN_ID
        )
        or (
            bool(payload.get("operator_id"))
            and bool(payload.get("collection_machine"))
            and bool(payload.get("date_sealed"))
            and payload.get("run_id") != PLACEHOLDER_RUN_ID
        ),
        (
            f"operator={payload.get('operator_id')!r}, "
            f"machine={payload.get('collection_machine')!r}, "
            f"date={payload.get('date_sealed')!r}, run_id={payload.get('run_id')!r}"
        ),
    )
    add_check(
        checks,
        "hash_inventory_written_for_precollection_inputs",
        len(artifacts) >= 8
        and all(
            row.get("exists") and len(str(row.get("sha256", ""))) == 64
            for row in artifacts
            if row.get("role") not in {"official_raw_jsonl_log", "official_rollout_video"}
        ),
        f"artifact_count={len(artifacts)}",
    )
    add_check(
        checks,
        "strict_sequence_places_seal_after_collection_before_manifest",
        "real_collection_runner.py" in command_text
        and "build_external_postcollection_evidence_seal.py" in command_text
        and "audit_external_postcollection_seal_consistency.py" in command_text
        and "build_external_manifest.py --write --check-video-paths" in command_text
        and command_text.find("real_collection_runner.py") < command_text.find("build_external_postcollection_evidence_seal.py")
        and command_text.find("build_external_postcollection_evidence_seal.py") < command_text.find("audit_external_postcollection_seal_consistency.py")
        and command_text.find("audit_external_postcollection_seal_consistency.py") < command_text.find("build_external_manifest.py --write --check-video-paths"),
        command_text,
    )
    add_check(
        checks,
        "seal_references_consistency_gate_before_manifest",
        "audit_external_postcollection_seal_consistency.py" in command_text
        and command_text.find("build_external_postcollection_evidence_seal.py") < command_text.find("audit_external_postcollection_seal_consistency.py")
        and command_text.find("audit_external_postcollection_seal_consistency.py") < command_text.find("build_external_manifest.py --write --check-video-paths"),
        command_text,
    )
    add_check(
        checks,
        "seal_references_rollout_pairing_release_final_gates",
        all(
            fragment in command_text
            for fragment in (
                "validate_external_rollouts.py --write-results --check-video-paths --strict",
                "audit_external_pairing_integrity.py --strict",
                "audit_external_release_package.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        command_text,
    )
    add_check(
        checks,
        "strict_evidence_gates_still_false",
        payload.get("strict_rollout_metrics_ready") is False
        and payload.get("strict_config_evidence_ready") is False
        and payload.get("strict_adapter_evidence_ready") is False
        and payload.get("strict_final_external_evidence_ready") is False,
        (
            f"rollout={payload.get('strict_rollout_metrics_ready')!r}, "
            f"config={payload.get('strict_config_evidence_ready')!r}, "
            f"adapter={payload.get('strict_adapter_evidence_ready')!r}, "
            f"external={payload.get('strict_final_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "no_real_manifest_written",
        payload.get("manifest_exists_before_seal") is False and not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "postcollection_seal_ready": payload.get("postcollection_seal_ready"),
        "ready_for_manifest_promotion": payload.get("ready_for_manifest_promotion"),
        "seal_path": rel(OUT_JSON),
        "seal_md_path": rel(OUT_MD),
        "seal_csv_path": rel(OUT_CSV),
        "sealed_artifact_count": len(artifacts),
        "jsonl_record_count": payload.get("jsonl_record_count"),
        "rollout_video_count": payload.get("rollout_video_count"),
        "expected_records": payload.get("expected_records"),
        "operator_regeneration_command": payload.get("operator_regeneration_command"),
        "strict_command_sequence": payload.get("strict_command_sequence", []),
        "checks": checks,
    }


def write_csv(payload: dict[str, Any]) -> None:
    fieldnames = ["role", "path", "exists", "bytes", "sha256", "required_for_real_seal"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["seal_artifacts"]:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Postcollection Evidence Seal",
        "",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Postcollection seal ready: `{str(payload['postcollection_seal_ready']).lower()}`.",
        f"Ready for manifest promotion: `{str(payload['ready_for_manifest_promotion']).lower()}`.",
        "",
        payload["evidence_boundary"],
        "",
        "## Collection Summary",
        "",
        f"- Run id: `{payload['run_id']}`",
        f"- Backend module: `{payload['backend_module'] or '<module_or_path>'}`",
        f"- Operator id: `{payload['operator_id'] or '<operator_or_lab>'}`",
        f"- Collection machine: `{payload['collection_machine'] or '<machine_or_robot_platform>'}`",
        f"- Date sealed: `{payload['date_sealed'] or '<YYYY-MM-DD>'}`",
        f"- Expected records: `{payload['expected_records']}`",
        f"- JSONL logs: `{payload['jsonl_log_count']}`",
        f"- JSONL records: `{payload['jsonl_record_count']}`",
        f"- Invalid JSONL lines: `{payload['invalid_json_line_count']}`",
        f"- Rollout videos: `{payload['rollout_video_count']}`",
        f"- Precollection freeze ready: `{str(payload['precollection_freeze_ready']).lower()}`",
        "",
        "## Operator Regeneration Command",
        "",
        "```powershell",
        payload["operator_regeneration_command"],
        "```",
        "",
        "## Strict Command Sequence",
        "",
    ]
    for command in payload["strict_command_sequence"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Seal Artifacts", ""])
    for row in payload["seal_artifacts"]:
        sha = row.get("sha256") or "missing"
        lines.append(f"- `{row['role']}` `{row['path']}` `{sha}`")
    lines.extend(["", "## Missing Real Artifact Roles", ""])
    for item in payload["missing_real_artifact_roles"] or ["none"]:
        lines.append(f"- `{item}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Postcollection Evidence Seal Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Postcollection seal ready: `{str(audit['postcollection_seal_ready']).lower()}`.",
        f"Ready for manifest promotion: `{str(audit['ready_for_manifest_promotion']).lower()}`.",
        "Strict external evidence ready: `false`.",
        f"Sealed artifacts: `{audit['sealed_artifact_count']}`.",
        f"JSONL records: `{audit['jsonl_record_count']}`.",
        f"Rollout videos: `{audit['rollout_video_count']}`.",
        "",
        "This audit checks that the postcollection evidence seal is a fail-closed hash inventory between official collection and manifest promotion. It does not count as external validation evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed postcollection evidence seal for Paper 119.")
    parser.add_argument("--backend-module", default="")
    parser.add_argument("--run-id", default=PLACEHOLDER_RUN_ID)
    parser.add_argument("--operator-id", default="")
    parser.add_argument("--collection-machine", default="")
    parser.add_argument("--date-sealed", default="")
    args = parser.parse_args()

    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(payload)
    write_md(payload)
    audit = build_audit(payload)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)
    print(
        "External postcollection evidence seal: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"seal_ready={payload['postcollection_seal_ready']}; "
        f"records={payload['jsonl_record_count']}; videos={payload['rollout_video_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

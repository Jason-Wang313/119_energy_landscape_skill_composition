from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

SEAL_JSON = EXTERNAL / "postcollection_evidence_seal.json"
SEAL_AUDIT_JSON = RESULTS / "external_postcollection_evidence_seal_audit.json"
OUT_JSON = RESULTS / "external_postcollection_seal_consistency_audit.json"
OUT_MD = RESULTS / "external_postcollection_seal_consistency_audit.md"

VERSION = "external_postcollection_seal_consistency_audit_v1"
SEAL_VERSION = "external_postcollection_evidence_seal_v1"
SEAL_AUDIT_VERSION = "external_postcollection_evidence_seal_audit_v1"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def root_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def glob_files(path: Path, patterns: tuple[str, ...]) -> list[Path]:
    if not path.exists():
        return []
    files: list[Path] = []
    for pattern in patterns:
        files.extend(child for child in path.rglob(pattern) if child.is_file())
    return sorted(set(files))


def read_jsonl_count(path: Path) -> tuple[int, int]:
    records = 0
    invalid = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                json.loads(stripped)
            except json.JSONDecodeError:
                invalid += 1
                continue
            records += 1
    return records, invalid


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


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


def official_artifact_paths() -> dict[str, list[Path]]:
    return {
        "prepared_or_manifest_task_config": glob_files(EXTERNAL / "configs", ("*.json",)),
        "official_raw_jsonl_log": glob_files(EXTERNAL / "logs", ("*",)),
        "official_rollout_video": glob_files(EXTERNAL / "videos", ("*",)),
    }


def compare_seal_hashes(seal: dict[str, Any]) -> dict[str, Any]:
    mismatched: list[dict[str, str]] = []
    missing: list[str] = []
    unexpectedly_present: list[str] = []
    matched = 0
    sealed_paths: set[str] = set()
    sealed_by_role: dict[str, set[str]] = {}

    for row in seal.get("seal_artifacts", []) or []:
        if not isinstance(row, dict):
            continue
        row_path = str(row.get("path", ""))
        if not row_path:
            continue
        role = str(row.get("role", ""))
        sealed_paths.add(row_path)
        sealed_by_role.setdefault(role, set()).add(row_path)
        path = root_path(row_path)
        expected_exists = row.get("exists") is True
        current_exists = path.exists() and path.is_file()
        expected_hash = str(row.get("sha256", ""))
        if expected_exists and not current_exists:
            missing.append(row_path)
            continue
        if not expected_exists and current_exists:
            unexpectedly_present.append(row_path)
            continue
        if expected_exists and current_exists:
            current_hash = sha256_file(path)
            if current_hash != expected_hash:
                mismatched.append({"path": row_path, "expected": expected_hash, "actual": current_hash})
            else:
                matched += 1

    extra_official: list[str] = []
    current_official = official_artifact_paths()
    for role, paths in current_official.items():
        sealed_role_paths = sealed_by_role.get(role, set())
        for path in paths:
            if not path.is_file():
                continue
            row_path = rel(path)
            if row_path not in sealed_role_paths and row_path not in sealed_paths:
                extra_official.append(row_path)

    log_paths = [path for path in current_official["official_raw_jsonl_log"] if path.suffix == ".jsonl"]
    video_paths = [path for path in current_official["official_rollout_video"] if path.suffix == ".mp4"]
    invalid_log_artifacts = [
        rel(path)
        for path in current_official["official_raw_jsonl_log"]
        if path.is_file() and path.suffix != ".jsonl"
    ]
    invalid_video_artifacts = [
        rel(path)
        for path in current_official["official_rollout_video"]
        if path.is_file() and path.suffix != ".mp4"
    ]
    records = 0
    invalid_json_lines = 0
    for path in log_paths:
        count, invalid = read_jsonl_count(path)
        records += count
        invalid_json_lines += invalid

    return {
        "matched_hash_count": matched,
        "mismatched_hashes": mismatched,
        "missing_sealed_paths": missing,
        "unexpectedly_present_paths": unexpectedly_present,
        "extra_official_artifacts": sorted(extra_official),
        "invalid_log_artifacts": sorted(invalid_log_artifacts),
        "invalid_video_artifacts": sorted(invalid_video_artifacts),
        "current_jsonl_log_count": len(log_paths),
        "current_jsonl_record_count": records,
        "current_invalid_json_line_count": invalid_json_lines,
        "current_rollout_video_count": len(video_paths),
        "current_prepared_config_count": len(current_official["prepared_or_manifest_task_config"]),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    seal = read_json(SEAL_JSON)
    seal_audit = read_json(SEAL_AUDIT_JSON)
    comparison = compare_seal_hashes(seal)
    command_sequence = strict_command_sequence(args)
    command_text = "\n".join(command_sequence)
    seal_ready = seal.get("postcollection_seal_ready") is True
    audit_ready = seal_audit.get("postcollection_seal_ready") is True
    expected_records = int(seal.get("expected_records", 0) or 0)
    no_hash_drift = (
        not comparison["mismatched_hashes"]
        and not comparison["missing_sealed_paths"]
        and not comparison["unexpectedly_present_paths"]
        and not comparison["extra_official_artifacts"]
        and not comparison["invalid_log_artifacts"]
        and not comparison["invalid_video_artifacts"]
    )
    counts_ready = (
        expected_records > 0
        and int(comparison["current_jsonl_record_count"]) >= expected_records
        and int(comparison["current_rollout_video_count"]) >= expected_records
        and int(comparison["current_invalid_json_line_count"]) == 0
    )
    manifest_absent = not (EXTERNAL / "manifest.json").exists()
    seal_consistency_ready = seal_ready and audit_ready and no_hash_drift and counts_ready and manifest_absent

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "postcollection_seal_artifacts_loaded",
        seal.get("version") == SEAL_VERSION
        and seal_audit.get("version") == SEAL_AUDIT_VERSION
        and seal_audit.get("passed") is True,
        f"seal_version={seal.get('version')!r}, audit_version={seal_audit.get('version')!r}, audit_passed={seal_audit.get('passed')!r}",
    )
    add_check(
        checks,
        "consistency_gate_is_non_evidence_and_fail_closed",
        seal.get("not_external_evidence") is True
        and seal_audit.get("not_external_evidence") is True
        and seal.get("strict_external_evidence_ready") is False
        and seal_audit.get("strict_external_evidence_ready") is False
        and (seal_consistency_ready or seal.get("postcollection_seal_ready") is False),
        (
            f"seal_ready={seal.get('postcollection_seal_ready')!r}, "
            f"consistency_ready={seal_consistency_ready!r}, "
            f"strict_external_evidence={seal.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "sealed_hashes_recompute_without_drift",
        not comparison["mismatched_hashes"]
        and not comparison["missing_sealed_paths"]
        and not comparison["unexpectedly_present_paths"],
        (
            f"matched={comparison['matched_hash_count']}, "
            f"mismatched={comparison['mismatched_hashes']}, "
            f"missing={comparison['missing_sealed_paths']}, "
            f"unexpected={comparison['unexpectedly_present_paths']}"
        ),
    )
    add_check(
        checks,
        "no_unsealed_official_artifacts_before_manifest_promotion",
        not comparison["extra_official_artifacts"]
        and not comparison["invalid_log_artifacts"]
        and not comparison["invalid_video_artifacts"],
        (
            f"extra={comparison['extra_official_artifacts']}, "
            f"invalid_logs={comparison['invalid_log_artifacts']}, "
            f"invalid_videos={comparison['invalid_video_artifacts']}"
        ),
    )
    add_check(
        checks,
        "manifest_promotion_requires_ready_seal_and_consistency",
        (
            seal.get("postcollection_seal_ready") is False
            and seal.get("ready_for_manifest_promotion") is False
            and seal_consistency_ready is False
        )
        or (
            seal.get("postcollection_seal_ready") is True
            and seal.get("ready_for_manifest_promotion") is True
            and seal_consistency_ready is True
        ),
        (
            f"seal_ready={seal.get('postcollection_seal_ready')!r}, "
            f"seal_manifest_ready={seal.get('ready_for_manifest_promotion')!r}, "
            f"consistency_ready={seal_consistency_ready!r}"
        ),
    )
    add_check(
        checks,
        "current_counts_match_default_or_ready_state",
        (
            seal.get("postcollection_seal_ready") is False
            and int(comparison["current_jsonl_record_count"]) == 0
            and int(comparison["current_rollout_video_count"]) == 0
        )
        or counts_ready,
        (
            f"expected={expected_records}, "
            f"records={comparison['current_jsonl_record_count']}, "
            f"videos={comparison['current_rollout_video_count']}, "
            f"invalid_json={comparison['current_invalid_json_line_count']}"
        ),
    )
    add_check(
        checks,
        "no_real_manifest_written_before_seal_consistency",
        manifest_absent,
        "external_validation/manifest.json absent before manifest promotion",
    )
    add_check(
        checks,
        "strict_sequence_places_consistency_after_seal_before_manifest",
        "build_external_postcollection_evidence_seal.py" in command_text
        and "audit_external_postcollection_seal_consistency.py" in command_text
        and "build_external_manifest.py --write --check-video-paths" in command_text
        and command_text.find("build_external_postcollection_evidence_seal.py")
        < command_text.find("audit_external_postcollection_seal_consistency.py")
        < command_text.find("build_external_manifest.py --write --check-video-paths"),
        command_text,
    )
    add_check(
        checks,
        "consistency_gate_references_rollout_pairing_release_final_gates",
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

    passed = all(check["passed"] for check in checks)
    return {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "seal_consistency_ready": seal_consistency_ready,
        "ready_for_manifest_promotion": seal_consistency_ready,
        "postcollection_seal_ready": seal_ready,
        "expected_records": expected_records,
        "matched_hash_count": comparison["matched_hash_count"],
        "mismatched_hashes": comparison["mismatched_hashes"],
        "missing_sealed_paths": comparison["missing_sealed_paths"],
        "unexpectedly_present_paths": comparison["unexpectedly_present_paths"],
        "extra_official_artifacts": comparison["extra_official_artifacts"],
        "invalid_log_artifacts": comparison["invalid_log_artifacts"],
        "invalid_video_artifacts": comparison["invalid_video_artifacts"],
        "current_jsonl_log_count": comparison["current_jsonl_log_count"],
        "current_jsonl_record_count": comparison["current_jsonl_record_count"],
        "current_invalid_json_line_count": comparison["current_invalid_json_line_count"],
        "current_rollout_video_count": comparison["current_rollout_video_count"],
        "current_prepared_config_count": comparison["current_prepared_config_count"],
        "seal_path": rel(SEAL_JSON),
        "seal_audit_path": rel(SEAL_AUDIT_JSON),
        "strict_command_sequence": command_sequence,
        "operator_regeneration_command": "python scripts\\audit_external_postcollection_seal_consistency.py",
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Postcollection Seal Consistency Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Seal consistency ready: `{str(payload['seal_consistency_ready']).lower()}`.",
        f"Ready for manifest promotion: `{str(payload['ready_for_manifest_promotion']).lower()}`.",
        "Strict external evidence ready: `false`.",
        f"Postcollection seal ready: `{str(payload['postcollection_seal_ready']).lower()}`.",
        f"Expected records: `{payload['expected_records']}`.",
        f"Current JSONL records: `{payload['current_jsonl_record_count']}`.",
        f"Current rollout videos: `{payload['current_rollout_video_count']}`.",
        f"Matched hashes: `{payload['matched_hash_count']}`.",
        "",
        "This audit recomputes the postcollection evidence seal before manifest promotion. It is a fail-closed integrity gate, not external validation evidence.",
        "",
        "## Drift Summary",
        "",
        f"- Mismatched hashes: `{payload['mismatched_hashes']}`",
        f"- Missing sealed paths: `{payload['missing_sealed_paths']}`",
        f"- Unexpectedly present paths: `{payload['unexpectedly_present_paths']}`",
        f"- Extra official artifacts: `{payload['extra_official_artifacts']}`",
        f"- Invalid log artifacts: `{payload['invalid_log_artifacts']}`",
        f"- Invalid video artifacts: `{payload['invalid_video_artifacts']}`",
        "",
        "## Strict Command Sequence",
        "",
    ]
    for command in payload["strict_command_sequence"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit postcollection seal hash consistency before manifest promotion.")
    parser.add_argument("--backend-module", default="")
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "External postcollection seal consistency audit: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"consistency_ready={payload['seal_consistency_ready']}; "
        f"matched={payload['matched_hash_count']}; "
        f"records={payload['current_jsonl_record_count']}; "
        f"videos={payload['current_rollout_video_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = EXTERNAL / "precollection_freeze_receipt.json"
OUT_MD = EXTERNAL / "precollection_freeze_receipt.md"
OUT_CSV = EXTERNAL / "precollection_freeze_receipt.csv"
AUDIT_JSON = RESULTS / "external_precollection_freeze_receipt_audit.json"
AUDIT_MD = RESULTS / "external_precollection_freeze_receipt_audit.md"

VERSION = "external_precollection_freeze_receipt_v1"
AUDIT_VERSION = "external_precollection_freeze_receipt_audit_v1"
PLACEHOLDER_RUN_ID = "paper119_external_validation_run"

CORE_LOCK_PATHS = [
    EXTERNAL / "blinded_operator_sheet.csv",
    EXTERNAL / "method_alias_map.json",
    EXTERNAL / "manifest_precollection_draft.json",
    EXTERNAL / "manifest_precollection_draft.md",
    EXTERNAL / "manifest_template.json",
    EXTERNAL / "log_schema_v1.json",
    EXTERNAL / "statistical_analysis_plan.json",
    EXTERNAL / "evidence_intake_ledger.json",
    EXTERNAL / "evidence_intake_ledger.md",
    EXTERNAL / "evidence_intake_ledger.csv",
    EXTERNAL / "method_manifest_cutover_checklist.csv",
    EXTERNAL / "method_manifest_cutover_checklist.md",
    EXTERNAL / "runner" / "backend_contract.py",
    EXTERNAL / "runner" / "real_collection_runner.py",
    RESULTS / "external_collection_readiness_audit.json",
    RESULTS / "external_fidelity_acceptance_audit.json",
    RESULTS / "fidelity_acceptance_materialization_plan.json",
    RESULTS / "external_config_manifest_audit.json",
    RESULTS / "external_method_implementation_audit.json",
    RESULTS / "external_evidence_intake_ledger_audit.json",
    RESULTS / "external_precollection_manifest_draft_audit.json",
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_tree(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    files = sorted(
        child
        for child in path.rglob("*")
        if child.is_file() and "__pycache__" not in child.parts and child.suffix != ".pyc"
    )
    for child in files:
        digest.update(rel(child).encode("utf-8"))
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def run_git(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def locked_artifact(path: Path, role: str, *, required_before_collection: bool = True) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": rel(path),
        "role": role,
        "exists": exists,
        "sha256": sha256_file(path) if exists and path.is_file() else "",
        "required_before_collection": required_before_collection,
    }


def config_artifacts() -> list[dict[str, Any]]:
    rows = []
    for path in sorted((EXTERNAL / "configs").glob("*.json")):
        rows.append(locked_artifact(path, "prepared_task_config"))
    return rows


def operator_command(args: argparse.Namespace) -> str:
    return (
        "python scripts\\build_external_precollection_freeze_receipt.py "
        "--backend-module <module_or_path> "
        "--run-id <specific_run_id> "
        "--operator-id <operator_or_lab> "
        "--collection-machine <machine_or_robot_platform> "
        "--date-locked <YYYY-MM-DD> "
        "--unsealed-alias-map"
    )


def strict_command_sequence(args: argparse.Namespace) -> list[str]:
    backend = args.backend_module or "<module_or_path>"
    run_id = args.run_id or "<specific_run_id>"
    return [
        r"python scripts\audit_external_fidelity_acceptance.py --strict",
        r"python scripts\validate_external_configs.py --strict",
        r"python scripts\validate_external_adapters.py --strict",
        rf"python scripts\audit_external_collection_readiness.py --strict --backend-module {backend} --task-config-dir external_validation\configs --run-id {run_id} --unsealed-alias-map",
        operator_command(args),
        rf"python external_validation\runner\real_collection_runner.py --backend-module {backend} --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id {run_id} --unsealed-alias-map",
        r"python scripts\build_external_postcollection_evidence_seal.py",
        r"python scripts\audit_external_postcollection_seal_consistency.py",
        r"python scripts\build_external_manifest.py --write --check-video-paths",
        r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
        r"python scripts\audit_external_pairing_integrity.py --strict",
        r"python scripts\audit_external_release_package.py --strict",
        r"python scripts\audit_external_evidence.py --strict",
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    fidelity = read_json(RESULTS / "external_fidelity_acceptance_audit.json")
    collection = read_json(RESULTS / "external_collection_readiness_audit.json")
    current_commit = run_git(["rev-parse", "HEAD"])
    dirty_status_lines = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    backend_path = rel_path(args.backend_module) if args.backend_module else None

    lock_artifacts = [locked_artifact(path, "core_precollection_artifact") for path in CORE_LOCK_PATHS]
    lock_artifacts.extend(config_artifacts())
    if backend_path is not None:
        lock_artifacts.append(locked_artifact(backend_path, "selected_backend_module"))
    else:
        lock_artifacts.append(
            {
                "path": "",
                "role": "selected_backend_module",
                "exists": False,
                "sha256": "",
                "required_before_collection": True,
            }
        )

    missing_lock_paths = [
        row["path"] or row["role"]
        for row in lock_artifacts
        if row["required_before_collection"] and not row["exists"]
    ]
    specific_run_id = bool(args.run_id.strip()) and args.run_id != PLACEHOLDER_RUN_ID
    operator_identity_ready = all(
        bool(str(value).strip())
        for value in (args.operator_id, args.collection_machine, args.date_locked)
    )
    fidelity_ready = fidelity.get("acceptance_ready") is True
    collection_ready = collection.get("collection_ready") is True
    checkout_clean = bool(current_commit) and not dirty_status_lines
    freeze_ready = (
        not missing_lock_paths
        and bool(args.backend_module.strip())
        and specific_run_id
        and args.unsealed_alias_map
        and operator_identity_ready
        and fidelity_ready
        and collection_ready
        and checkout_clean
    )

    return {
        "version": VERSION,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "freeze_receipt_ready": freeze_ready,
        "ready_to_collect_after_receipt": freeze_ready,
        "backend_module": args.backend_module,
        "run_id": args.run_id,
        "unsealed_alias_map": bool(args.unsealed_alias_map),
        "operator_id": args.operator_id,
        "collection_machine": args.collection_machine,
        "date_locked": args.date_locked,
        "current_checkout": {
            "code_commit": current_commit,
            "clean_checkout": checkout_clean,
            "dirty_status_lines": dirty_status_lines,
            "skill_library_hash": sha256_tree(EXTERNAL / "baselines"),
        },
        "source_state": {
            "fidelity_acceptance_ready": fidelity_ready,
            "collection_ready": collection_ready,
            "collection_blocking_missing": collection.get("blocking_missing", []),
            "fidelity_blocking_missing": fidelity.get("blocking_missing", []),
        },
        "missing_lock_paths": missing_lock_paths,
        "lock_artifacts": lock_artifacts,
        "strict_command_sequence": strict_command_sequence(args),
        "operator_regeneration_command": operator_command(args),
        "evidence_boundary": (
            "This receipt freezes precollection inputs only. It is not a manifest, rollout log, "
            "video, checkpoint, metric result, or external validation evidence."
        ),
    }


def build_audit(payload: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    artifacts = payload.get("lock_artifacts", []) or []
    paths_by_role: dict[str, list[dict[str, Any]]] = {}
    for row in artifacts:
        if isinstance(row, dict):
            paths_by_role.setdefault(str(row.get("role", "")), []).append(row)
    command_text = "\n".join(payload.get("strict_command_sequence", []) or [])
    checkout = payload.get("current_checkout", {}) or {}

    add_check(
        checks,
        "receipt_is_non_evidence_and_fail_closed",
        payload.get("not_external_evidence") is True
        and payload.get("strict_external_evidence_ready") is False
        and payload.get("freeze_receipt_ready") is False,
        (
            f"not_external_evidence={payload.get('not_external_evidence')!r}, "
            f"strict_external_evidence_ready={payload.get('strict_external_evidence_ready')!r}, "
            f"freeze_receipt_ready={payload.get('freeze_receipt_ready')!r}"
        ),
    )
    add_check(
        checks,
        "core_lock_artifacts_hashed",
        len(paths_by_role.get("core_precollection_artifact", [])) >= 20
        and all(row.get("exists") and len(str(row.get("sha256", ""))) == 64 for row in paths_by_role.get("core_precollection_artifact", [])),
        f"core_count={len(paths_by_role.get('core_precollection_artifact', []))}",
    )
    add_check(
        checks,
        "prepared_task_configs_hashed",
        len(paths_by_role.get("prepared_task_config", [])) >= 4
        and all(row.get("exists") and len(str(row.get("sha256", ""))) == 64 for row in paths_by_role.get("prepared_task_config", [])),
        f"config_count={len(paths_by_role.get('prepared_task_config', []))}",
    )
    add_check(
        checks,
        "backend_module_still_operator_supplied",
        not payload.get("backend_module") and paths_by_role.get("selected_backend_module", [{}])[0].get("exists") is False,
        f"backend_module={payload.get('backend_module')!r}",
    )
    add_check(
        checks,
        "run_identity_still_operator_supplied",
        payload.get("run_id") == PLACEHOLDER_RUN_ID and payload.get("unsealed_alias_map") is False,
        f"run_id={payload.get('run_id')!r}, unsealed_alias_map={payload.get('unsealed_alias_map')!r}",
    )
    add_check(
        checks,
        "checkout_and_skill_hash_recorded",
        len(str(checkout.get("code_commit", ""))) == 40
        and len(str(checkout.get("skill_library_hash", ""))) == 64,
        f"commit={checkout.get('code_commit')!r}, skill_hash={checkout.get('skill_library_hash')!r}",
    )
    add_check(
        checks,
        "strict_sequence_places_receipt_before_collection",
        "build_external_precollection_freeze_receipt.py" in command_text
        and command_text.find("build_external_precollection_freeze_receipt.py") < command_text.find("real_collection_runner.py")
        and "audit_external_collection_readiness.py --strict" in command_text,
        command_text,
    )
    add_check(
        checks,
        "strict_sequence_places_seal_consistency_before_manifest",
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
        "receipt_references_manifest_rollout_release_final_gates",
        all(
            fragment in command_text
            for fragment in (
                "build_external_manifest.py --write --check-video-paths",
                "build_external_postcollection_evidence_seal.py",
                "audit_external_postcollection_seal_consistency.py",
                "validate_external_rollouts.py --write-results --check-video-paths --strict",
                "audit_external_release_package.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        command_text,
    )
    add_check(
        checks,
        "source_state_preserves_external_blockers",
        payload.get("source_state", {}).get("fidelity_acceptance_ready") is False
        and payload.get("source_state", {}).get("collection_ready") is False,
        str(payload.get("source_state", {})),
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "freeze_receipt_ready": payload.get("freeze_receipt_ready"),
        "receipt_path": rel(OUT_JSON),
        "receipt_md_path": rel(OUT_MD),
        "receipt_csv_path": rel(OUT_CSV),
        "locked_artifact_count": len(artifacts),
        "missing_lock_paths": payload.get("missing_lock_paths", []),
        "operator_regeneration_command": payload.get("operator_regeneration_command"),
        "strict_command_sequence": payload.get("strict_command_sequence", []),
        "checks": checks,
    }


def write_csv(payload: dict[str, Any]) -> None:
    fieldnames = ["role", "path", "exists", "sha256", "required_before_collection"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["lock_artifacts"]:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_receipt_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Precollection Freeze Receipt",
        "",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Freeze receipt ready: `{str(payload['freeze_receipt_ready']).lower()}`.",
        "",
        payload["evidence_boundary"],
        "",
        "## Current Lock State",
        "",
        f"- Backend module: `{payload['backend_module'] or '<module_or_path>'}`",
        f"- Run id: `{payload['run_id']}`",
        f"- Unsealed alias map: `{str(payload['unsealed_alias_map']).lower()}`",
        f"- Operator id: `{payload['operator_id'] or '<operator_or_lab>'}`",
        f"- Collection machine: `{payload['collection_machine'] or '<machine_or_robot_platform>'}`",
        f"- Date locked: `{payload['date_locked'] or '<YYYY-MM-DD>'}`",
        f"- Code commit: `{payload['current_checkout']['code_commit']}`",
        f"- Skill-library hash: `{payload['current_checkout']['skill_library_hash']}`",
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
    lines.extend(["", "## Lock Artifacts", ""])
    for row in payload["lock_artifacts"]:
        sha = row.get("sha256") or "missing"
        lines.append(f"- `{row['role']}` `{row['path'] or '<operator_supplied>'}` `{sha}`")
    lines.extend(["", "## Missing Lock Paths", ""])
    for item in payload["missing_lock_paths"] or ["none"]:
        lines.append(f"- `{item}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Precollection Freeze Receipt Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Freeze receipt ready: `{str(audit['freeze_receipt_ready']).lower()}`.",
        "Strict external evidence ready: `false`.",
        f"Locked artifacts: `{audit['locked_artifact_count']}`.",
        "",
        "This audit checks that the precollection freeze receipt hash-locks the operator sheet, alias map, prepared configs, method cutover checklist, manifest draft, runner files, source audits, and current checkout before any official JSONL/video collection can count.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed precollection freeze receipt for Paper 119.")
    parser.add_argument("--backend-module", default="")
    parser.add_argument("--run-id", default=PLACEHOLDER_RUN_ID)
    parser.add_argument("--operator-id", default="")
    parser.add_argument("--collection-machine", default="")
    parser.add_argument("--date-locked", default="")
    parser.add_argument("--unsealed-alias-map", action="store_true")
    args = parser.parse_args()

    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(payload)
    write_receipt_md(payload)
    audit = build_audit(payload)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)
    print(
        "External precollection freeze receipt: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"freeze_ready={payload['freeze_receipt_ready']}; "
        f"locked_artifacts={audit['locked_artifact_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

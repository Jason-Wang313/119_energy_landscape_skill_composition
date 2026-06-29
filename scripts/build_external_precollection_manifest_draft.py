from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import validate_external_configs as config_validator


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

TEMPLATE = EXTERNAL / "manifest_template.json"
SCHEMA = EXTERNAL / "config_schema_v1.json"
OFFICIAL_MANIFEST = EXTERNAL / "manifest.json"
DRAFT_JSON = EXTERNAL / "manifest_precollection_draft.json"
DRAFT_MD = EXTERNAL / "manifest_precollection_draft.md"
AUDIT_JSON = RESULTS / "external_precollection_manifest_draft_audit.json"
AUDIT_MD = RESULTS / "external_precollection_manifest_draft_audit.md"

DRAFT_VERSION = "external_precollection_manifest_draft_v1"
AUDIT_VERSION = "external_precollection_manifest_draft_audit_v1"
ORACLE_METHOD = "oracle_basin_composer"

SOURCE_REPORTS = [
    RESULTS / "external_manifest_builder_report.json",
    RESULTS / "external_config_manifest_audit.json",
    RESULTS / "external_rollout_evidence_audit.json",
    RESULTS / "external_ablation_collection_audit.json",
    RESULTS / "external_evidence_intake_ledger_audit.json",
    RESULTS / "external_method_implementation_audit.json",
    RESULTS / "external_collection_readiness_audit.json",
    RESULTS / "maniskill_render_machine_qualification.json",
]


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def path_exists_as_evidence(path: Path) -> bool:
    if path.is_file():
        return True
    if path.is_dir():
        return any(child.is_file() for child in path.rglob("*"))
    return False


def config_records(template: dict[str, Any], schema: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    draft_tasks: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for task in template.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        draft_task = dict(task)
        config_path = rel_path(str(task.get("config_path", "")))
        config_hash = sha256_file(config_path) if config_path.exists() else ""
        manifest_task = dict(task)
        manifest_task["config_hash"] = config_hash
        ok, errors = (
            config_validator.validate_config(config_path, schema, strict=True, manifest_task=manifest_task)
            if config_path.exists()
            else (False, ["config file missing"])
        )
        draft_task["config_hash"] = config_hash
        draft_task["manifest_declared_ready_if_promoted"] = bool(ok and config_hash)
        draft_tasks.append(draft_task)
        records.append(
            {
                "task_family": str(task.get("task_family", "")),
                "config_path": str(task.get("config_path", "")),
                "config_exists": config_path.exists(),
                "config_hash": config_hash,
                "strict_validation_passed_if_manifest_declared": ok,
                "validation_errors": errors,
            }
        )
    return draft_tasks, records


def method_gaps(template: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for method in template.get("methods", []) or []:
        if not isinstance(method, dict):
            continue
        name = str(method.get("name", ""))
        if name == ORACLE_METHOD:
            continue
        implementation = str(method.get("implementation", "")).strip()
        checkpoint = str(method.get("checkpoint_or_config_path", "")).strip()
        declared_hash = str(method.get("checkpoint_or_config_hash", "")).strip()
        implementation_path = rel_path(implementation) if implementation else None
        checkpoint_path = rel_path(checkpoint) if checkpoint else None
        implementation_exists = bool(implementation_path and implementation_path.exists())
        checkpoint_exists = bool(checkpoint_path and checkpoint_path.exists())
        gaps.append(
            {
                "method": name,
                "implementation": implementation,
                "implementation_exists": implementation_exists,
                "implementation_hash": sha256_file(implementation_path) if implementation_path and implementation_path.is_file() else "",
                "checkpoint_or_config_path": checkpoint,
                "checkpoint_or_config_exists": checkpoint_exists,
                "checkpoint_or_config_hash": declared_hash,
                "blocking_missing": [
                    item
                    for item, missing in (
                        ("implementation_path", not implementation_exists),
                        ("checkpoint_or_config_path", not checkpoint_exists),
                        ("checkpoint_or_config_hash", not bool(declared_hash)),
                    )
                    if missing
                ],
            }
        )
    return gaps


def rollout_gaps(template: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for task in template.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        for field, kind in (("log_jsonl", "jsonl_log"), ("video_dir", "video_dir")):
            value = str(task.get(field, ""))
            path = rel_path(value)
            ready = path_exists_as_evidence(path)
            gaps.append(
                {
                    "task_family": str(task.get("task_family", "")),
                    "kind": kind,
                    "path": value,
                    "present": ready,
                    "blocking_until_real_evidence": not ready,
                    "strict_gate": "python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
                }
            )
    return gaps


def source_report_records() -> list[dict[str, Any]]:
    records = []
    for path in SOURCE_REPORTS:
        records.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() else "",
            }
        )
    return records


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    schema = read_json(SCHEMA)
    manifest_report = read_json(RESULTS / "external_manifest_builder_report.json")
    task_manifest_entries, prepared_configs = config_records(template, schema)
    methods = method_gaps(template)
    rollouts = rollout_gaps(template)
    sources = source_report_records()
    blocking_rows = [
        row
        for row in manifest_report.get("assembly_checklist_rows", []) or []
        if isinstance(row, dict) and row.get("blocking_until_real_evidence") == "true"
    ]

    missing_method_count = sum(1 for row in methods if row["blocking_missing"])
    missing_rollout_count = sum(1 for row in rollouts if row["blocking_until_real_evidence"])
    prepared_config_count = sum(1 for row in prepared_configs if row["strict_validation_passed_if_manifest_declared"] and row["config_hash"])

    cutover_commands = [
        r"python scripts\build_external_precollection_manifest_draft.py",
        r"python scripts\materialize_fidelity_acceptance.py --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --confirm-code-commit <commit> --confirm-skill-library-hash <sha256> --write",
        r"python scripts\audit_external_fidelity_acceptance.py --strict",
        r"python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path>",
        r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
        r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
        r"python scripts\build_external_manifest.py --write --check-video-paths",
        r"python scripts\validate_external_configs.py --strict",
        r"python scripts\validate_external_adapters.py --strict",
        r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
        r"python scripts\audit_external_pairing_integrity.py --strict",
        r"python scripts\audit_external_release_package.py --strict",
        r"python scripts\audit_external_evidence.py --strict",
    ]

    return {
        "version": DRAFT_VERSION,
        "not_external_evidence": True,
        "draft_only": True,
        "precollection_manifest_draft_ready": True,
        "strict_external_evidence_ready": False,
        "strict_config_evidence_ready": False,
        "ready_to_write_official_manifest": False,
        "official_manifest_path": rel(OFFICIAL_MANIFEST),
        "official_manifest_exists": OFFICIAL_MANIFEST.exists(),
        "official_manifest_absent_at_build": not OFFICIAL_MANIFEST.exists(),
        "would_promote_to_manifest_version": template.get("version"),
        "route": template.get("route"),
        "log_schema": template.get("log_schema"),
        "claim": template.get("claim"),
        "task_count": len(task_manifest_entries),
        "prepared_config_count": prepared_config_count,
        "task_manifest_entries_with_hashes": task_manifest_entries,
        "prepared_config_records": prepared_configs,
        "method_gap_count": missing_method_count,
        "method_gaps": methods,
        "missing_rollout_artifact_count": missing_rollout_count,
        "rollout_artifact_gaps": rollouts,
        "manifest_assembly_blocking_count": len(blocking_rows),
        "manifest_assembly_blocking_items": [
            {
                "phase": row.get("phase"),
                "item": row.get("item"),
                "current_state": row.get("current_state"),
                "required_path": row.get("required_path"),
                "strict_gate": row.get("strict_gate"),
            }
            for row in blocking_rows
        ],
        "forbidden_promotion_without": [
            "accepted fidelity acceptance file from an independent operator",
            "manifest-declared JSONL logs and render-backed videos",
            "manifest-declared non-oracle implementation/checkpoint hashes",
            "release artifact hashes for code, configs, logs, videos, and checkpoints",
            "strict rollout, pairing, config, adapter, release, and evidence gates passing",
        ],
        "cutover_commands": cutover_commands,
        "source_reports": sources,
    }


def build_audit(payload: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    config_records_payload = payload.get("prepared_config_records", []) or []
    method_gaps_payload = payload.get("method_gaps", []) or []
    rollout_gaps_payload = payload.get("rollout_artifact_gaps", []) or []
    source_reports_payload = payload.get("source_reports", []) or []
    command_text = "\n".join(payload.get("cutover_commands", []) or [])

    add_check(checks, "draft_json_written_to_precollection_path", DRAFT_JSON.exists() and DRAFT_JSON.name != "manifest.json", rel(DRAFT_JSON))
    add_check(checks, "draft_marked_non_evidence_and_fail_closed", payload.get("not_external_evidence") is True and payload.get("draft_only") is True and payload.get("strict_external_evidence_ready") is False and payload.get("ready_to_write_official_manifest") is False, "draft is non-evidence and cannot write the official manifest")
    add_check(checks, "official_manifest_absent", payload.get("official_manifest_exists") is False and not OFFICIAL_MANIFEST.exists(), rel(OFFICIAL_MANIFEST))
    add_check(checks, "prepared_config_hashes_prefilled", len(config_records_payload) >= 4 and all(row.get("strict_validation_passed_if_manifest_declared") is True and len(str(row.get("config_hash", ""))) == 64 for row in config_records_payload), f"configs={len(config_records_payload)}")
    add_check(checks, "method_gaps_remain_blocking", len(method_gaps_payload) >= 11 and int(payload.get("method_gap_count", 0) or 0) >= 11, f"method_gap_count={payload.get('method_gap_count')!r}")
    add_check(checks, "rollout_artifacts_remain_blocking", len(rollout_gaps_payload) >= 8 and int(payload.get("missing_rollout_artifact_count", 0) or 0) >= 8, f"missing_rollout_artifact_count={payload.get('missing_rollout_artifact_count')!r}")
    add_check(checks, "manifest_assembly_blockers_preserved", int(payload.get("manifest_assembly_blocking_count", 0) or 0) >= 20, f"blocking={payload.get('manifest_assembly_blocking_count')!r}")
    add_check(checks, "source_reports_hash_listed", all(row.get("exists") and len(str(row.get("sha256", ""))) == 64 for row in source_reports_payload), f"sources={len(source_reports_payload)}")
    for fragment in (
        "materialize_fidelity_acceptance.py",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write --check-video-paths",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ):
        check_name = "cutover_command_contains_" + fragment.split(".")[0].replace(" ", "_").replace("\\", "_")
        add_check(checks, check_name, fragment in command_text, fragment)

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "draft_ready": passed,
        "strict_external_evidence_ready": False,
        "strict_config_evidence_ready": False,
        "official_manifest_exists": OFFICIAL_MANIFEST.exists(),
        "draft_path": rel(DRAFT_JSON),
        "draft_md_path": rel(DRAFT_MD),
        "task_count": payload.get("task_count"),
        "prepared_config_count": payload.get("prepared_config_count"),
        "method_gap_count": payload.get("method_gap_count"),
        "missing_rollout_artifact_count": payload.get("missing_rollout_artifact_count"),
        "manifest_assembly_blocking_count": payload.get("manifest_assembly_blocking_count"),
        "build_command": r"python scripts\build_external_precollection_manifest_draft.py",
        "cutover_commands": payload.get("cutover_commands", []),
        "checks": checks,
    }


def write_draft_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Precollection Manifest Draft",
        "",
        "Not evidence: `true`.",
        "Draft only: `true`.",
        "Strict external evidence ready: `false`.",
        f"Official manifest exists: `{str(payload['official_manifest_exists']).lower()}`.",
        "",
        "This draft records the manifest fields that can be safely prefilled before collection, especially prepared task-config hashes. It is not `external_validation/manifest.json`, it is not submission evidence, and it cannot promote itself to evidence without the strict cutover commands below.",
        "",
        "## Prepared Task Configs",
        "",
    ]
    for record in payload["prepared_config_records"]:
        lines.append(
            f"- `{record['task_family']}`: `{record['config_path']}` "
            f"sha256 `{record['config_hash']}`; strict-if-manifest-declared `{str(record['strict_validation_passed_if_manifest_declared']).lower()}`"
        )
    lines.extend(["", "## Blocking Method Gaps", ""])
    for record in payload["method_gaps"]:
        lines.append(f"- `{record['method']}`: missing `{record['blocking_missing']}`")
    lines.extend(["", "## Blocking Rollout Artifacts", ""])
    for record in payload["rollout_artifact_gaps"]:
        if record["blocking_until_real_evidence"]:
            lines.append(f"- `{record['task_family']}` `{record['kind']}`: `{record['path']}`")
    lines.extend(["", "## Promotion Requirements", ""])
    for item in payload["forbidden_promotion_without"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Cutover Commands", ""])
    for command in payload["cutover_commands"]:
        lines.extend(["```powershell", command, "```"])
    DRAFT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Precollection Manifest Draft Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Draft ready: `{str(audit['draft_ready']).lower()}`.",
        "Strict external evidence ready: `false`.",
        "",
        "This audit checks that the precollection manifest draft is useful for an operator but remains fail-closed before real logs, videos, fidelity acceptance, method hashes, and release artifacts exist.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    payload = build_payload()
    DRAFT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_draft_md(payload)
    audit = build_audit(payload)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)
    print(
        "External precollection manifest draft: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"configs={audit['prepared_config_count']}; "
        f"method_gaps={audit['method_gap_count']}; "
        f"rollout_gaps={audit['missing_rollout_artifact_count']}"
    )
    print(f"Wrote {DRAFT_JSON}")
    print(f"Wrote {DRAFT_MD}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

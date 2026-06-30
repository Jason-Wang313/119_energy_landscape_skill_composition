from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = EXTERNAL / "operator_return_package_contract.json"
OUT_MD = EXTERNAL / "operator_return_package_contract.md"
OUT_CSV = EXTERNAL / "operator_return_package_contract.csv"
AUDIT_JSON = RESULTS / "external_operator_return_package_contract_audit.json"
AUDIT_MD = RESULTS / "external_operator_return_package_contract_audit.md"

VERSION = "external_operator_return_package_contract_v1"
PRIMARY_METHOD = "barrier_certified_energy_composer_v5"
ORACLE_METHOD = "oracle_basin_composer"


STRICT_COMMAND_SPINE = [
    r"python scripts\audit_external_fidelity_acceptance.py --strict",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map",
    r"python scripts\build_external_precollection_freeze_receipt.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <accepted_run_id> --unsealed-alias-map",
    r"python scripts\build_external_postcollection_evidence_seal.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
    r"python scripts\audit_external_postcollection_seal_consistency.py",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence.py --strict",
    r"python scripts\audit_submission_readiness_gap.py",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def read_candidate_methods(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["method"]: row for row in csv.DictReader(handle) if row.get("method")}


def non_oracle_methods(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    methods: list[dict[str, Any]] = []
    for row in manifest.get("methods", []) or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("name", "")) == ORACLE_METHOD:
            continue
        methods.append(row)
    return methods


def task_return_items(manifest: dict[str, Any], method_count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in manifest.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        task_family = str(task.get("task_family", "")).strip()
        episodes_per_method = int(task.get("episodes_per_method", 0) or 0)
        expected_records = episodes_per_method * method_count
        rows.extend(
            [
                {
                    "category": "task_config",
                    "id": f"{task_family}_config",
                    "path": str(task.get("config_path", "")),
                    "required_count": 1,
                    "hash_requirement": "manifest.tasks[].config_hash must equal SHA256(config_path)",
                    "acceptance": "strict config evidence accepts this manifest-declared config and rejects templates/local dry-run configs",
                    "strict_gate": r"python scripts\validate_external_configs.py --strict",
                    "source": "external_validation/manifest_template.json",
                },
                {
                    "category": "task_log",
                    "id": f"{task_family}_jsonl",
                    "path": str(task.get("log_jsonl", "")),
                    "required_count": expected_records,
                    "hash_requirement": "release_artifacts.logs must include this JSONL with SHA256",
                    "acceptance": f"JSONL parses, follows log_schema_v1, and contains at least {expected_records} rows for {method_count} methods x {episodes_per_method} episodes",
                    "strict_gate": r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
                    "source": "external_validation/manifest_template.json",
                },
                {
                    "category": "task_video_dir",
                    "id": f"{task_family}_videos",
                    "path": str(task.get("video_dir", "")),
                    "required_count": expected_records,
                    "hash_requirement": "release_artifacts.videos must include all manifest-declared MP4 files with SHA256",
                    "acceptance": "videos are render-backed MP4s, unique, non-placeholder, non-diagnostic, and referenced by official JSONL rows",
                    "strict_gate": r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
                    "source": "external_validation/manifest_template.json",
                },
            ]
        )
    return rows


def method_return_items(methods: list[dict[str, Any]], candidates: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in methods:
        name = str(method.get("name", "")).strip()
        role = str((method.get("implementation_provenance", {}) or {}).get("evidence_role", "")).strip()
        candidate = candidates.get(name, {})
        candidate_path = candidate.get("config_path", "") or str(method.get("checkpoint_or_config_path", ""))
        candidate_hash = candidate.get("config_sha256", "") or str(method.get("checkpoint_or_config_hash", ""))
        rows.append(
            {
                "category": "method_artifact",
                "id": name,
                "path": candidate_path,
                "required_count": 1,
                "hash_requirement": f"manifest.methods[].checkpoint_or_config_hash must equal {candidate_hash or '<operator supplied SHA256>'}",
                "acceptance": (
                    "manifest declares implementation provenance, real checkpoint/config artifact, fairness-contract binding, "
                    "and official JSONL policy_or_config_hash values that match the manifest"
                ),
                "strict_gate": r"python scripts\validate_external_adapters.py --strict",
                "source": "external_validation/method_config_candidates.csv",
                "evidence_role": role,
                "candidate_hash": candidate_hash,
            }
        )
    return rows


def global_return_items() -> list[dict[str, Any]]:
    return [
        {
            "category": "global",
            "id": "fidelity_acceptance",
            "path": "external_validation/fidelity_acceptance.json",
            "required_count": 1,
            "hash_requirement": "materialized with accepted collection commit and skill-library hash",
            "acceptance": "accepted fidelity, independent operator, real/high-fidelity platform, render-backed videos, paired replay, and known limitations are signed off",
            "strict_gate": r"python scripts\audit_external_fidelity_acceptance.py --strict",
            "source": "external_validation/fidelity_acceptance_draft.json",
        },
        {
            "category": "global",
            "id": "precollection_freeze_receipt",
            "path": "external_validation/precollection_freeze_receipt.json",
            "required_count": 1,
            "hash_requirement": "receipt hashes operator sheet, alias map, configs, candidates, runner, code commit, and skill library before collection",
            "acceptance": "freeze receipt exists before official collection and matches the accepted run id/operator/machine",
            "strict_gate": r"python scripts\build_external_precollection_freeze_receipt.py ...",
            "source": "external_validation/manifest_precollection_draft.json",
        },
        {
            "category": "global",
            "id": "postcollection_evidence_seal",
            "path": "external_validation/postcollection_evidence_seal.json",
            "required_count": 1,
            "hash_requirement": "seal hashes raw logs, videos, configs, precollection receipt, and operator metadata after collection",
            "acceptance": "postcollection seal exists and seal consistency recomputes with no drift before manifest promotion",
            "strict_gate": r"python scripts\audit_external_postcollection_seal_consistency.py",
            "source": "external_validation/postcollection_evidence_seal.json",
        },
        {
            "category": "global",
            "id": "manifest",
            "path": "external_validation/manifest.json",
            "required_count": 1,
            "hash_requirement": "manifest declares release_artifacts for code, configs, logs, videos, and checkpoints",
            "acceptance": "manifest is written only after postcollection seal consistency, then all strict evidence gates pass",
            "strict_gate": r"python scripts\build_external_manifest.py --write --check-video-paths",
            "source": "external_validation/manifest_template.json",
        },
        {
            "category": "global",
            "id": "release_artifacts",
            "path": "external_validation/manifest.json:release_artifacts",
            "required_count": 5,
            "hash_requirement": "release_artifacts.code/configs/logs/videos/checkpoints all carry valid SHA256 values",
            "acceptance": "release package audit and final external evidence audit recompute all release hashes",
            "strict_gate": r"python scripts\audit_external_release_package.py --strict",
            "source": "external_validation/manifest_template.json",
        },
    ]


def build_payload() -> dict[str, Any]:
    manifest = read_json(EXTERNAL / "manifest_template.json")
    preflight = read_json(RESULTS / "external_evidence_preflight.json")
    readiness = read_json(RESULTS / "submission_readiness_gap_audit.json")
    intake = read_json(EXTERNAL / "evidence_intake_ledger.json")
    release = read_json(RESULTS / "external_operator_release_bundle_plan.json")
    candidates = read_candidate_methods(EXTERNAL / "method_config_candidates.csv")

    methods = non_oracle_methods(manifest)
    method_count = len(manifest.get("methods", []) or [])
    tasks = [task for task in manifest.get("tasks", []) or [] if isinstance(task, dict)]
    task_items = task_return_items(manifest, method_count)
    method_items = method_return_items(methods, candidates)
    global_items = global_return_items()
    return_items = global_items + task_items + method_items
    expected_records = int(preflight.get("expected_records", 0) or 0)

    checks: list[dict[str, Any]] = []
    add_check(checks, "contract_is_non_evidence", True, "contract lists required returned artifacts only")
    add_check(
        checks,
        "preflight_blockers_are_current",
        preflight.get("evidence_ready") is False
        and int(preflight.get("blocking_missing_count", 0) or 0) >= 50
        and expected_records == 1440,
        f"evidence_ready={preflight.get('evidence_ready')!r}, blockers={preflight.get('blocking_missing_count')!r}, expected_records={expected_records}",
    )
    add_check(
        checks,
        "global_items_cover_manifest_fidelity_seals_release",
        {"fidelity_acceptance", "precollection_freeze_receipt", "postcollection_evidence_seal", "manifest", "release_artifacts"}.issubset(
            {item["id"] for item in global_items}
        ),
        f"global_items={len(global_items)}",
    )
    add_check(
        checks,
        "task_items_cover_all_manifest_tasks",
        len(tasks) == 4
        and len(task_items) == len(tasks) * 3
        and sum(item["required_count"] for item in task_items if item["category"] == "task_log") == expected_records
        and sum(item["required_count"] for item in task_items if item["category"] == "task_video_dir") == expected_records,
        f"tasks={len(tasks)}, task_items={len(task_items)}, expected_records={expected_records}",
    )
    add_check(
        checks,
        "method_items_cover_non_oracle_methods",
        len(methods) == 11
        and len(method_items) == 11
        and PRIMARY_METHOD in {item["id"] for item in method_items}
        and ORACLE_METHOD not in {item["id"] for item in method_items},
        f"methods={len(methods)}, method_items={len(method_items)}",
    )
    add_check(
        checks,
        "candidate_method_hashes_bound",
        all(str(item.get("candidate_hash", "")).strip() for item in method_items),
        f"candidate_hashes={sum(1 for item in method_items if str(item.get('candidate_hash', '')).strip())}/{len(method_items)}",
    )
    add_check(
        checks,
        "strict_command_spine_covers_return_to_final_audit",
        all(
            any(fragment in command for command in STRICT_COMMAND_SPINE)
            for fragment in (
                "audit_external_fidelity_acceptance.py --strict",
                "validate_external_configs.py --strict",
                "validate_external_adapters.py --strict",
                "real_collection_runner.py",
                "build_external_manifest.py --write",
                "validate_external_rollouts.py",
                "audit_external_evidence.py --strict",
                "audit_submission_readiness_gap.py",
            )
        ),
        f"commands={len(STRICT_COMMAND_SPINE)}",
    )
    add_check(
        checks,
        "intake_ledger_and_release_bundle_are_current_sources",
        intake.get("passed") is True
        and intake.get("strict_external_evidence_ready") is False
        and release.get("bundle_state") == "READY_TO_SEND_OPERATOR_PACKAGE"
        and release.get("strict_external_evidence_ready") is False,
        f"intake_passed={intake.get('passed')!r}, release_state={release.get('bundle_state')!r}",
    )
    add_check(
        checks,
        "readiness_boundary_preserved",
        readiness.get("objective_complete") is False
        and int(readiness.get("satisfied_requirements", 0) or 0) == 17
        and int(readiness.get("blocking_missing_requirements", 0) or 0) == 4,
        f"satisfied={readiness.get('satisfied_requirements')!r}, blocking={readiness.get('blocking_missing_requirements')!r}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "return_contract_ready": passed,
        "preflight_blocking_missing_count": int(preflight.get("blocking_missing_count", 0) or 0),
        "expected_total_jsonl_records": expected_records,
        "task_count": len(tasks),
        "method_count_including_oracle": method_count,
        "non_oracle_method_count": len(methods),
        "return_item_count": len(return_items),
        "global_item_count": len(global_items),
        "task_item_count": len(task_items),
        "method_item_count": len(method_items),
        "return_items": return_items,
        "strict_command_spine": STRICT_COMMAND_SPINE,
        "source_reports": [
            "results/external_evidence_preflight.json",
            "external_validation/manifest_template.json",
            "external_validation/method_config_candidates.csv",
            "external_validation/evidence_intake_ledger.json",
            "results/external_operator_release_bundle_plan.json",
            "results/submission_readiness_gap_audit.json",
        ],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_outputs(payload: dict[str, Any]) -> None:
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "category",
                "id",
                "path",
                "required_count",
                "hash_requirement",
                "acceptance",
                "strict_gate",
                "source",
            ],
        )
        writer.writeheader()
        for item in payload["return_items"]:
            writer.writerow({field: item.get(field, "") for field in writer.fieldnames})

    lines = [
        "# External Operator Return Package Contract",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Current preflight blockers: `{payload['preflight_blocking_missing_count']}`.",
        f"Expected total JSONL records: `{payload['expected_total_jsonl_records']}`.",
        f"Return items: `{payload['return_item_count']}`.",
        "",
        "This contract defines the exact artifact classes an independent operator must return after collection. It does not create evidence and does not write `external_validation/manifest.json`.",
        "",
        "## Required Return Items",
        "",
    ]
    for item in payload["return_items"]:
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"- Category: `{item['category']}`")
        lines.append(f"- Path: `{item['path']}`")
        lines.append(f"- Required count: `{item['required_count']}`")
        lines.append(f"- Hash requirement: {item['hash_requirement']}")
        lines.append(f"- Acceptance: {item['acceptance']}")
        lines.append(f"- Strict gate: `{item['strict_gate']}`")
        lines.append("")
    lines.extend(["## Strict Command Spine", ""])
    for command in payload["strict_command_spine"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    AUDIT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    audit_lines = [
        "# External Operator Return Package Contract Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Return items: `{payload['return_item_count']}`.",
        f"Expected total JSONL records: `{payload['expected_total_jsonl_records']}`.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        audit_lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        "External operator return package contract: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; items={payload['return_item_count']}; "
        f"expected_records={payload['expected_total_jsonl_records']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "rollout_evidence_packet.json"
PACKET_MD = EXTERNAL / "rollout_evidence_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "rollout_evidence_work_orders.csv"
AUDIT_JSON = RESULTS / "external_rollout_evidence_audit.json"
AUDIT_MD = RESULTS / "external_rollout_evidence_audit.md"

PACKET_VERSION = "external_rollout_evidence_packet_v1"
AUDIT_VERSION = "external_rollout_evidence_audit_v1"

STRICT_ACCEPTANCE_COMMANDS = [
    r"python scripts\build_external_rollout_evidence_packet.py",
    r"python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
    r"python scripts\audit_external_postcollection_seal_consistency.py",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence.py --strict",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def clean_tasks(collection: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = collection.get("tasks", [])
    return [task for task in tasks if isinstance(task, dict)] if isinstance(tasks, list) else []


def task_reports(preflight: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports = preflight.get("task_reports", [])
    if not isinstance(reports, list):
        return {}
    return {
        str(report.get("task_family", "")): report
        for report in reports
        if isinstance(report, dict) and str(report.get("task_family", ""))
    }


def path_exists(path_text: str) -> bool:
    return bool(path_text) and (ROOT / path_text).exists()


def top_level_files(folder: Path, pattern: str) -> list[Path]:
    return sorted(path for path in folder.glob(pattern) if path.is_file()) if folder.exists() else []


def top_level_dirs(folder: Path) -> list[Path]:
    return sorted(path for path in folder.iterdir() if path.is_dir()) if folder.exists() else []


def build_task_records(collection: dict[str, Any], preflight: dict[str, Any], method_count: int) -> list[dict[str, Any]]:
    reports = task_reports(preflight)
    records: list[dict[str, Any]] = []
    for task in clean_tasks(collection):
        task_family = str(task.get("task_family", ""))
        report = reports.get(task_family, {})
        expected = int(task.get("required_records", 0) or 0)
        observed = int(report.get("observed_records", 0) or 0)
        log_jsonl = str(task.get("log_jsonl", ""))
        video_dir = str(task.get("video_dir", ""))
        config_path = str(task.get("config_path", ""))
        records.append(
            {
                "task_family": task_family,
                "platform_type": task.get("platform_type", ""),
                "platform_name": task.get("platform_name", ""),
                "episodes_per_method": int(task.get("episodes_per_method", 0) or 0),
                "method_count": method_count,
                "expected_records": expected,
                "observed_records": observed,
                "log_jsonl": log_jsonl,
                "log_exists": path_exists(log_jsonl),
                "video_dir": video_dir,
                "video_dir_exists": path_exists(video_dir),
                "config_path": config_path,
                "config_exists": path_exists(config_path),
                "preflight_missing": list(report.get("missing", []) or []),
            }
        )
    return records


def build_work_orders(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    orders: list[dict[str, Any]] = [
        {
            "id": "freeze_rollout_manifest_contract",
            "scope": "all_tasks",
            "operator_input": "freeze platform identity, method aliases, task configs, backend module, run id, and paired reset schedule before collecting logs",
            "required_artifacts": [
                "external_validation/fidelity_acceptance.json",
                "external_validation/method_alias_map.json",
                "external_validation/configs/*.json",
            ],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[:3],
        },
        {
            "id": "collect_manifest_declared_rollout_logs",
            "scope": "all_tasks",
            "operator_input": "run the non-template backend to produce one manifest-declared JSONL record for each task-method-reset episode",
            "required_artifacts": ["external_validation/logs/*.jsonl"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[3:4],
        },
        {
            "id": "bind_videos_configs_and_method_hashes",
            "scope": "all_tasks",
            "operator_input": "ensure every JSONL record points to an existing video, manifest-declared config hash, and method policy/config hash",
            "required_artifacts": [
                "external_validation/videos/<task_family>/*",
                "external_validation/manifest.json",
                "external_validation/configs/*.json",
            ],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[4:7],
        },
        {
            "id": "recompute_rollout_metrics_from_raw_jsonl",
            "scope": "all_tasks",
            "operator_input": "recompute external metrics from the raw JSONL logs with video-path checks enabled; do not hand-enter metrics",
            "required_artifacts": ["results/external_rollout_metrics.json", "results/external_rollout_metrics.md"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[7:8],
        },
        {
            "id": "run_pairing_release_and_final_evidence_gates",
            "scope": "all_tasks",
            "operator_input": "only after logs/videos/configs/method hashes are real, run the paired-reset, release-package, and final evidence gates",
            "required_artifacts": [
                "results/external_pairing_integrity_audit.json",
                "results/external_release_package_audit.json",
                "results/external_evidence_audit.json",
            ],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[8:],
        },
    ]
    for record in records:
        orders.append(
            {
                "id": f"collect_{record['task_family']}_jsonl_and_videos",
                "scope": record["task_family"],
                "operator_input": (
                    f"collect {record['expected_records']} paired-reset records for "
                    f"{record['task_family']} with videos under {record['video_dir']}"
                ),
                "required_artifacts": [record["log_jsonl"], record["video_dir"], record["config_path"]],
                "acceptance_commands": [
                    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
                    r"python scripts\audit_external_pairing_integrity.py --strict",
                ],
            }
        )
    return orders


def rollout_schema_errors(rollout_metrics: dict[str, Any]) -> list[str]:
    errors = rollout_metrics.get("schema_errors", [])
    return [str(error) for error in errors] if isinstance(errors, list) else []


def build_packet(
    collection: dict[str, Any],
    preflight: dict[str, Any],
    rollout_metrics: dict[str, Any],
    pairing: dict[str, Any],
    release: dict[str, Any],
    external_evidence: dict[str, Any],
    log_schema: dict[str, Any],
) -> dict[str, Any]:
    method_count = int(collection.get("method_count", 0) or preflight.get("method_count", 0) or 0)
    records = build_task_records(collection, preflight, method_count)
    expected_records = int(collection.get("total_required_records", 0) or preflight.get("expected_records", 0) or 0)
    observed_records = int(preflight.get("observed_records", 0) or 0)
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "rollout_evidence_packet_ready": True,
        "strict_rollout_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "manifest_written": False,
        "purpose": "Convert the current external rollout blocker into manifest-declared raw-log, video, pairing, release, and recomputation work orders.",
        "expected_records": expected_records,
        "observed_records": observed_records,
        "task_count": len(records),
        "method_count": method_count,
        "log_schema_version": log_schema.get("version"),
        "paired_comparison_key": log_schema.get("paired_comparison_key", []),
        "primary_method": log_schema.get("primary_method", ""),
        "primary_thresholds": log_schema.get("primary_thresholds", {}),
        "real_manifest_exists": (EXTERNAL / "manifest.json").exists(),
        "rollout_metrics_passed": rollout_metrics.get("passed") is True,
        "rollout_schema_errors": rollout_schema_errors(rollout_metrics),
        "pairing_ready": pairing.get("pairing_ready") is True,
        "release_package_ready": release.get("release_package_ready") is True,
        "external_evidence_ready": external_evidence.get("submission_ready") is True,
        "task_rollout_records": records,
        "work_orders": build_work_orders(records),
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "treating external_validation/local_dry_run logs as external evidence",
            "hand-entering manifest metrics without recomputing from JSONL logs",
            "using rollout rows that do not have manifest-declared configs, videos, and method hashes",
            "unsealing aliases before configs, implementations, and run id are frozen",
            "counting logs without paired-reset method panels across the declared methods",
        ],
        "source_reports": [
            rel(RESULTS / "external_collection_plan.json"),
            rel(RESULTS / "external_evidence_preflight.json"),
            rel(RESULTS / "external_rollout_metrics.json"),
            rel(RESULTS / "external_pairing_integrity_audit.json"),
            rel(RESULTS / "external_release_package_audit.json"),
            rel(RESULTS / "external_evidence_audit.json"),
            rel(EXTERNAL / "log_schema_v1.json"),
        ],
    }


def strict_commands_cover_all(command_text: str) -> bool:
    required = [
        "build_external_rollout_evidence_packet.py",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_postcollection_evidence_seal.py",
        "audit_external_postcollection_seal_consistency.py",
        "build_external_manifest.py --write",
        "validate_external_configs.py --strict",
        "validate_external_adapters.py --strict",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_release_package.py --strict",
        "audit_external_evidence.py --strict",
    ]
    return all(fragment in command_text for fragment in required)


def audit_packet(
    packet: dict[str, Any],
    collection: dict[str, Any],
    preflight: dict[str, Any],
    rollout_metrics: dict[str, Any],
    pairing: dict[str, Any],
    release: dict[str, Any],
    external_evidence: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    records = packet.get("task_rollout_records", []) or []
    work_orders = packet.get("work_orders", []) or []
    order_ids = {str(order.get("id", "")) for order in work_orders}
    task_names = {str(record.get("task_family", "")) for record in records}
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    schema_errors = rollout_schema_errors(rollout_metrics)

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("rollout_evidence_packet_ready") is True
        and packet.get("strict_rollout_evidence_ready") is False
        and packet.get("strict_external_evidence_ready") is False
        and packet.get("manifest_written") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_rollout_evidence_ready={packet.get('strict_rollout_evidence_ready')!r}, "
            f"strict_external_evidence_ready={packet.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "strict_rollout_metrics_still_fail_without_manifest",
        rollout_metrics.get("passed") is False
        and any("manifest" in error.lower() for error in schema_errors),
        f"passed={rollout_metrics.get('passed')!r}, schema_errors={schema_errors}",
    )
    add_check(
        checks,
        "preflight_ready_but_observes_zero_real_records",
        preflight.get("passed") is True
        and preflight.get("not_external_evidence") is True
        and preflight.get("evidence_ready") is False
        and int(preflight.get("expected_records", 0) or 0) >= 1440
        and int(preflight.get("observed_records", -1) or 0) == 0,
        (
            f"expected={preflight.get('expected_records')!r}, "
            f"observed={preflight.get('observed_records')!r}"
        ),
    )
    add_check(
        checks,
        "collection_plan_record_budget_ge_1440",
        collection.get("passed") is True
        and int(collection.get("total_required_records", 0) or 0) >= 1440
        and int(collection.get("task_family_count", 0) or 0) >= 4
        and int(collection.get("method_count", 0) or 0) >= 12,
        (
            f"records={collection.get('total_required_records')!r}, "
            f"tasks={collection.get('task_family_count')!r}, "
            f"methods={collection.get('method_count')!r}"
        ),
    )
    add_check(
        checks,
        "task_work_orders_cover_all_planned_tasks",
        len(records) >= 4
        and all(record.get("expected_records", 0) >= 360 for record in records)
        and all(f"collect_{task}_jsonl_and_videos" in order_ids for task in task_names),
        f"tasks={sorted(task_names)}",
    )
    add_check(
        checks,
        "strict_commands_cover_collection_manifest_rollout_pairing_release_evidence",
        strict_commands_cover_all(command_text),
        command_text,
    )
    add_check(
        checks,
        "strict_gate_audits_remain_fail_closed",
        pairing.get("pairing_ready") is False
        and release.get("release_package_ready") is False
        and external_evidence.get("submission_ready") is False,
        (
            f"pairing_ready={pairing.get('pairing_ready')!r}, "
            f"release_package_ready={release.get('release_package_ready')!r}, "
            f"submission_ready={external_evidence.get('submission_ready')!r}"
        ),
    )
    add_check(
        checks,
        "no_real_manifest_or_logs_written",
        not (EXTERNAL / "manifest.json").exists()
        and not top_level_files(EXTERNAL / "logs", "*.jsonl")
        and not top_level_dirs(EXTERNAL / "videos"),
        (
            f"manifest_exists={(EXTERNAL / 'manifest.json').exists()}, "
            f"log_files={len(top_level_files(EXTERNAL / 'logs', '*.jsonl'))}, "
            f"video_dirs={len(top_level_dirs(EXTERNAL / 'videos'))}"
        ),
    )
    add_check(
        checks,
        "packet_files_written",
        PACKET_JSON.exists()
        and PACKET_MD.exists()
        and WORK_ORDERS_CSV.exists(),
        f"packet_json={PACKET_JSON.exists()}, packet_md={PACKET_MD.exists()}, csv={WORK_ORDERS_CSV.exists()}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "rollout_evidence_packet_ready": packet.get("rollout_evidence_packet_ready") is True,
        "strict_rollout_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "expected_records": packet.get("expected_records", 0),
        "observed_records": packet.get("observed_records", 0),
        "task_count": packet.get("task_count", 0),
        "method_count": packet.get("method_count", 0),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "packet_path": rel(PACKET_JSON),
        "work_orders_path": rel(WORK_ORDERS_CSV),
    }


def write_work_orders(packet: dict[str, Any]) -> None:
    rows = packet.get("work_orders", []) or []
    fieldnames = ["id", "scope", "operator_input", "required_artifacts", "acceptance_commands"]
    with WORK_ORDERS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": row.get("id", ""),
                    "scope": row.get("scope", ""),
                    "operator_input": row.get("operator_input", ""),
                    "required_artifacts": "; ".join(row.get("required_artifacts", []) or []),
                    "acceptance_commands": "; ".join(row.get("acceptance_commands", []) or []),
                }
            )


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Rollout Evidence Packet",
        "",
        f"Packet ready: `{str(packet['rollout_evidence_packet_ready']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict rollout evidence ready: `{str(packet['strict_rollout_evidence_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(packet['strict_external_evidence_ready']).lower()}`.",
        f"Expected records: `{packet['expected_records']}`.",
        f"Observed records: `{packet['observed_records']}`.",
        "",
        "This packet is a non-evidence work-order layer for the raw external rollout logs. It exists to keep the validation plan precise: collection, manifest writing, rollout metric recomputation, pairing integrity, release hash-locking, and final evidence gates must all pass before any external-validation claim is made.",
        "",
        "## Work Orders",
        "",
    ]
    for order in packet["work_orders"]:
        lines.append(f"- `{order['id']}` ({order['scope']}): {order['operator_input']}")
    lines.extend(["", "## Task Record Budget", ""])
    for record in packet["task_rollout_records"]:
        lines.append(
            f"- `{record['task_family']}`: expected `{record['expected_records']}`, "
            f"observed `{record['observed_records']}`, log `{record['log_jsonl']}`, video dir `{record['video_dir']}`"
        )
    lines.extend(["", "## Strict Acceptance Commands", ""])
    for command in packet["strict_acceptance_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Forbidden Shortcuts", ""])
    for shortcut in packet["forbidden_evidence_shortcuts"]:
        lines.append(f"- {shortcut}")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Rollout Evidence Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Expected records: `{audit['expected_records']}`.",
        f"Observed records: `{audit['observed_records']}`.",
        "",
        "This audit checks that the rollout evidence packet is complete as an operator checklist while strict rollout and external evidence gates remain fail-closed.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    collection = read_json(RESULTS / "external_collection_plan.json")
    preflight = read_json(RESULTS / "external_evidence_preflight.json")
    rollout_metrics = read_json(RESULTS / "external_rollout_metrics.json")
    pairing = read_json(RESULTS / "external_pairing_integrity_audit.json")
    release = read_json(RESULTS / "external_release_package_audit.json")
    external_evidence = read_json(RESULTS / "external_evidence_audit.json")
    log_schema = read_json(EXTERNAL / "log_schema_v1.json")

    packet = build_packet(collection, preflight, rollout_metrics, pairing, release, external_evidence, log_schema)
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_work_orders(packet)
    write_packet_md(packet)

    audit = audit_packet(packet, collection, preflight, rollout_metrics, pairing, release, external_evidence)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External rollout evidence packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"expected={audit['expected_records']}; "
        f"observed={audit['observed_records']}"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

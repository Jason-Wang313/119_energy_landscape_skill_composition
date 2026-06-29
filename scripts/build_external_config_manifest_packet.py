from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import validate_external_configs as config_validator


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
CONFIG_DIR = EXTERNAL / "configs"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "config_manifest_packet.json"
PACKET_MD = EXTERNAL / "config_manifest_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "config_manifest_work_orders.csv"
AUDIT_JSON = RESULTS / "external_config_manifest_audit.json"
AUDIT_MD = RESULTS / "external_config_manifest_audit.md"

PACKET_VERSION = "external_config_manifest_packet_v1"
AUDIT_VERSION = "external_config_manifest_audit_v1"

STRICT_ACCEPTANCE_COMMANDS = [
    r"python scripts\build_external_config_manifest_packet.py",
    r"python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence.py --strict",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path.relative_to(ROOT).as_posix()}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def manifest_tasks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = manifest.get("tasks", [])
    return [task for task in tasks if isinstance(task, dict)] if isinstance(tasks, list) else []


def config_records(schema: dict[str, Any], manifest_template: dict[str, Any]) -> list[dict[str, Any]]:
    allowed_tasks = set(schema.get("allowed_task_families", []) or [])
    records: list[dict[str, Any]] = []
    for task in manifest_tasks(manifest_template):
        task_family = str(task.get("task_family", ""))
        config_path = str(task.get("config_path", ""))
        path = ROOT / config_path if config_path else CONFIG_DIR / f"{task_family}.json"
        strict_validation_passed = False
        strict_validation_errors: list[str] = ["config file missing"]
        if path.exists():
            manifest_task = dict(task)
            manifest_task["config_hash"] = sha256_file(path)
            strict_validation_passed, strict_validation_errors = config_validator.validate_config(
                path,
                schema,
                strict=True,
                manifest_task=manifest_task,
            )
        record = {
            "task_family": task_family,
            "manifest_config_path": config_path,
            "config_path": rel(path) if path.exists() else config_path,
            "config_exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else "",
            "strict_validation_passed_if_manifest_declared": strict_validation_passed,
            "strict_validation_errors": strict_validation_errors,
            "platform_type": task.get("platform_type", ""),
            "platform_name_in_manifest_template": task.get("platform_name", ""),
            "log_jsonl": task.get("log_jsonl", ""),
            "video_dir": task.get("video_dir", ""),
            "allowed_by_schema": task_family in allowed_tasks,
        }
        records.append(record)
    return records


def build_work_orders(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    orders: list[dict[str, Any]] = [
        {
            "id": "lock_real_platform_identity",
            "scope": "all_tasks",
            "operator_input": "choose the accepted real robot or high-fidelity simulator and freeze platform_name, platform_type, and compute budget before config write",
            "required_artifacts": ["external_validation/fidelity_acceptance.json", "external_validation/configs/*.json"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[:2],
        },
        {
            "id": "hash_manifest_config_entries",
            "scope": "all_tasks",
            "operator_input": "write config_hash for every manifest task entry from the exact config file consumed by the backend",
            "required_artifacts": ["external_validation/manifest.json", "external_validation/configs/*.json"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[2:4],
        },
        {
            "id": "bind_configs_to_rollout_logs",
            "scope": "all_tasks",
            "operator_input": "ensure each task's JSONL records were generated with the manifest-declared config and contain matching platform/run identifiers",
            "required_artifacts": ["external_validation/logs/*.jsonl", "external_validation/videos/<task_family>/"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[4:],
        },
    ]
    for record in records:
        orders.append(
            {
                "id": f"declare_{record['task_family']}_config",
                "scope": record["task_family"],
                "operator_input": f"manifest-declare {record['config_path']} with sha256 {record['sha256'] or '<hash_after_write>'}",
                "required_artifacts": [record["config_path"], record["log_jsonl"], record["video_dir"]],
                "acceptance_commands": [
                    r"python scripts\build_external_manifest.py --write --check-video-paths",
                    r"python scripts\validate_external_configs.py --strict",
                ],
            }
        )
    return orders


def build_packet(
    schema: dict[str, Any],
    materialization: dict[str, Any],
    template_audit: dict[str, Any],
    evidence_audit: dict[str, Any],
    collection: dict[str, Any],
    manifest_template: dict[str, Any],
) -> dict[str, Any]:
    records = config_records(schema, manifest_template)
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "config_manifest_packet_ready": True,
        "strict_config_evidence_ready": False,
        "manifest_declared_config_ready": False,
        "manifest_written": False,
        "purpose": "Convert prepared task configs into manifest-declared, hash-locked config evidence once real external artifacts exist.",
        "schema_version": schema.get("version"),
        "evidence_config_version": schema.get("evidence_version"),
        "template_config_version": schema.get("template_version"),
        "materialization_plan_ready": materialization.get("passed") is True,
        "prepared_config_count": len([record for record in records if record["config_exists"]]),
        "manifest_task_count": len(records),
        "collection_ready": collection.get("collection_ready") is True,
        "strict_config_audit_passed": evidence_audit.get("passed") is True,
        "strict_config_audit_blockers": [
            check for check in evidence_audit.get("checks", []) or [] if check.get("passed") is not True
        ],
        "task_config_records": records,
        "work_orders": build_work_orders(records),
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "treating prepared configs as evidence before external_validation/manifest.json declares them",
            "changing configs after alias unsealing or after rollout collection starts",
            "using config_templates directly as manifest-declared configs",
            "omitting config_hash or letting logs/videos point to a different task definition",
        ],
        "source_reports": [
            rel(RESULTS / "external_config_materialization_plan.json"),
            rel(RESULTS / "external_config_template_audit.json"),
            rel(RESULTS / "external_config_evidence_audit.json"),
            rel(RESULTS / "external_collection_readiness_audit.json"),
            rel(EXTERNAL / "manifest_template.json"),
        ],
    }


def audit_packet(
    packet: dict[str, Any],
    schema: dict[str, Any],
    materialization: dict[str, Any],
    template_audit: dict[str, Any],
    evidence_audit: dict[str, Any],
    collection: dict[str, Any],
    manifest_template: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    records = packet.get("task_config_records", []) or []
    work_orders = packet.get("work_orders", []) or []
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    order_ids = {order.get("id") for order in work_orders}
    task_names = {record.get("task_family") for record in records}
    manifest_config_paths = {str(task.get("config_path", "")) for task in manifest_tasks(manifest_template)}
    collection_checks = {check.get("name"): check.get("passed") for check in collection.get("checks", []) or []}

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("config_manifest_packet_ready") is True
        and packet.get("strict_config_evidence_ready") is False
        and packet.get("manifest_declared_config_ready") is False
        and packet.get("manifest_written") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_config_evidence_ready={packet.get('strict_config_evidence_ready')!r}, "
            f"manifest_declared_config_ready={packet.get('manifest_declared_config_ready')!r}"
        ),
    )
    add_check(
        checks,
        "materialization_plan_ready_but_not_evidence",
        materialization.get("passed") is True
        and materialization.get("not_external_evidence") is True
        and materialization.get("write_enabled") is False
        and materialization.get("strict_config_evidence_ready") is False,
        (
            f"passed={materialization.get('passed')!r}, "
            f"write_enabled={materialization.get('write_enabled')!r}"
        ),
    )
    add_check(
        checks,
        "template_audit_passes",
        template_audit.get("passed") is True
        and template_audit.get("strict") is False
        and int(template_audit.get("config_count", 0) or 0) >= 4,
        f"config_count={template_audit.get('config_count')!r}",
    )
    add_check(
        checks,
        "strict_config_evidence_still_fails_without_manifest",
        evidence_audit.get("passed") is False
        and evidence_audit.get("strict") is True
        and any(check.get("name") == "manifest_exists" and check.get("passed") is False for check in evidence_audit.get("checks", []) or []),
        f"passed={evidence_audit.get('passed')!r}, config_count={evidence_audit.get('config_count')!r}",
    )
    add_check(
        checks,
        "manifest_template_declares_all_collection_tasks",
        len(records) >= 4
        and all(record.get("allowed_by_schema") is True for record in records)
        and all(str(record.get("manifest_config_path", "")).startswith("external_validation/configs/") for record in records),
        f"tasks={sorted(task_names)}",
    )
    add_check(
        checks,
        "prepared_config_files_have_hashes",
        len(records) >= 4
        and all(record.get("config_exists") is True and len(str(record.get("sha256", ""))) == 64 for record in records),
        f"hashes={[record.get('sha256') for record in records]}",
    )
    strict_config_errors = {
        str(record.get("task_family", "")): record.get("strict_validation_errors", [])
        for record in records
        if record.get("strict_validation_passed_if_manifest_declared") is not True
    }
    add_check(
        checks,
        "prepared_configs_pass_strict_schema_if_manifest_declared",
        len(records) >= 4
        and all(record.get("strict_validation_passed_if_manifest_declared") is True for record in records),
        f"errors={strict_config_errors}",
    )
    add_check(
        checks,
        "work_orders_cover_config_to_manifest_path",
        {"lock_real_platform_identity", "hash_manifest_config_entries", "bind_configs_to_rollout_logs"}.issubset(order_ids)
        and all(f"declare_{task}_config" in order_ids for task in task_names),
        f"missing={sorted(({f'declare_{task}_config' for task in task_names} | {'lock_real_platform_identity', 'hash_manifest_config_entries', 'bind_configs_to_rollout_logs'}) - order_ids)}",
    )
    add_check(
        checks,
        "strict_commands_cover_config_manifest_release_and_evidence",
        all(
            fragment in command_text
            for fragment in (
                "build_external_config_manifest_packet.py",
                "materialize_external_configs.py",
                "build_external_manifest.py --write",
                "validate_external_configs.py --strict",
                "audit_external_collection_readiness.py --strict",
                "audit_external_release_package.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        f"commands={packet.get('strict_acceptance_commands')!r}",
    )
    add_check(
        checks,
        "collection_readiness_preserves_config_boundary",
        collection.get("collection_ready") is False
        and collection_checks.get("real_task_configs_ready") is True
        and not (EXTERNAL / "manifest.json").exists(),
        (
            f"collection_ready={collection.get('collection_ready')!r}, "
            f"real_task_configs_ready={collection_checks.get('real_task_configs_ready')!r}, "
            f"manifest_exists={(EXTERNAL / 'manifest.json').exists()}"
        ),
    )
    add_check(
        checks,
        "manifest_template_paths_match_prepared_configs",
        manifest_config_paths == {record.get("config_path") for record in records},
        f"manifest_paths={sorted(manifest_config_paths)}",
    )
    add_check(
        checks,
        "packet_files_written",
        PACKET_JSON.exists() and PACKET_MD.exists() and WORK_ORDERS_CSV.exists(),
        f"packet_json={PACKET_JSON.exists()}, packet_md={PACKET_MD.exists()}, csv={WORK_ORDERS_CSV.exists()}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "config_manifest_packet_ready": passed,
        "strict_config_evidence_ready": False,
        "manifest_declared_config_ready": False,
        "source_packet": rel(PACKET_JSON),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_work_orders_csv(work_orders: list[dict[str, Any]]) -> None:
    fieldnames = ["id", "scope", "operator_input", "required_artifacts", "acceptance_commands"]
    with WORK_ORDERS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for order in work_orders:
            writer.writerow(
                {
                    "id": order.get("id", ""),
                    "scope": order.get("scope", ""),
                    "operator_input": order.get("operator_input", ""),
                    "required_artifacts": ";".join(order.get("required_artifacts", []) or []),
                    "acceptance_commands": ";".join(order.get("acceptance_commands", []) or []),
                }
            )


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Config Manifest Packet",
        "",
        "Not evidence: `true`.",
        f"Config manifest packet ready: `{str(packet['config_manifest_packet_ready']).lower()}`.",
        f"Strict config evidence ready: `{str(packet['strict_config_evidence_ready']).lower()}`.",
        f"Manifest-declared config ready: `{str(packet['manifest_declared_config_ready']).lower()}`.",
        "",
        "This packet turns prepared task configs into a manifest-declaration checklist. It does not write `external_validation/manifest.json`, does not claim that prepared configs are external evidence, and does not replace raw rollout logs or videos.",
        "",
        "## Forbidden Evidence Shortcuts",
        "",
    ]
    for item in packet["forbidden_evidence_shortcuts"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Task Config Records", "", "| Task | Config path | Prepared hash | Strict-ready if manifest-declared | Log | Video dir |", "|---|---|---|---|---|---|"])
    for record in packet["task_config_records"]:
        lines.append(
            f"| `{record['task_family']}` | `{record['config_path']}` | `{record['sha256']}` | `{str(record['strict_validation_passed_if_manifest_declared']).lower()}` | `{record['log_jsonl']}` | `{record['video_dir']}` |"
        )
    lines.extend(["", "## Work Orders", ""])
    for order in packet["work_orders"]:
        lines.extend(
            [
                f"### `{order['id']}`",
                "",
                f"- Scope: `{order['scope']}`",
                f"- Operator input: {order['operator_input']}",
                "- Required artifacts: " + ", ".join(f"`{item}`" for item in order.get("required_artifacts", []) or []),
                "",
            ]
        )
    lines.extend(["## Strict Acceptance Commands", ""])
    for command in packet["strict_acceptance_commands"]:
        lines.append(f"- `{command}`")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Config Manifest Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Config manifest packet ready: `{str(audit['config_manifest_packet_ready']).lower()}`.",
        f"Strict config evidence ready: `{str(audit['strict_config_evidence_ready']).lower()}`.",
        f"Manifest-declared config ready: `{str(audit['manifest_declared_config_ready']).lower()}`.",
        "",
        "This audit checks that prepared task configs have a concrete path to manifest-declared config evidence while strict config evidence remains false until a real manifest and rollout artifacts exist.",
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
    schema = read_json(EXTERNAL / "config_schema_v1.json")
    materialization = read_json(RESULTS / "external_config_materialization_plan.json")
    template_audit = read_json(RESULTS / "external_config_template_audit.json")
    evidence_audit = read_json(RESULTS / "external_config_evidence_audit.json")
    collection = read_json(RESULTS / "external_collection_readiness_audit.json")
    manifest_template = read_json(EXTERNAL / "manifest_template.json")

    packet = build_packet(schema, materialization, template_audit, evidence_audit, collection, manifest_template)
    write_work_orders_csv(packet["work_orders"])
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_packet_md(packet)
    audit = audit_packet(packet, schema, materialization, template_audit, evidence_audit, collection, manifest_template)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External config manifest packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"tasks={packet['manifest_task_count']}; not_evidence=true"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

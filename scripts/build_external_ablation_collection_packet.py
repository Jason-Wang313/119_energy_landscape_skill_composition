from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "ablation_collection_packet.json"
PACKET_MD = EXTERNAL / "ablation_collection_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "ablation_collection_work_orders.csv"
AUDIT_JSON = RESULTS / "external_ablation_collection_audit.json"
AUDIT_MD = RESULTS / "external_ablation_collection_audit.md"

PACKET_VERSION = "external_ablation_collection_packet_v1"
AUDIT_VERSION = "external_ablation_collection_audit_v1"

REQUIRED_ABLATIONS = [
    {
        "id": "basin_overlap",
        "external_variant": "minus_basin_overlap",
        "local_reference_variant": "minus_basin_overlap",
        "component_removed": "basin-overlap posterior",
    },
    {
        "id": "barrier_height",
        "external_variant": "minus_barrier_height",
        "local_reference_variant": "minus_barrier_height",
        "component_removed": "barrier-height term",
    },
    {
        "id": "descent_continuity",
        "external_variant": "minus_descent_continuity",
        "local_reference_variant": "minus_descent_continuity",
        "component_removed": "descent-continuity term",
    },
    {
        "id": "risk_calibration",
        "external_variant": "minus_calibration",
        "local_reference_variant": "minus_calibration",
        "component_removed": "risk calibration",
    },
    {
        "id": "seam_repair",
        "external_variant": "minus_high_energy_repair",
        "local_reference_variant": "minus_high_energy_repair",
        "component_removed": "high-energy seam repair",
    },
]

STRICT_COMMANDS = [
    r"python scripts\build_external_ablation_collection_packet.py",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
    r"python scripts\audit_external_postcollection_seal_consistency.py",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_evidence.py --strict",
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


def collection_tasks(collection: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = collection.get("tasks", [])
    return [task for task in tasks if isinstance(task, dict)] if isinstance(tasks, list) else []


def strict_missing_ablations(evidence: dict[str, Any]) -> list[str]:
    failures = evidence.get("blocking_failures", [])
    for item in failures if isinstance(failures, list) else []:
        if not isinstance(item, dict) or item.get("name") != "external_ablations":
            continue
        detail = str(item.get("detail", ""))
        missing = []
        for row in REQUIRED_ABLATIONS:
            if row["id"] in detail:
                missing.append(row["id"])
        return missing
    return [row["id"] for row in REQUIRED_ABLATIONS]


def build_work_orders(collection: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = collection_tasks(collection)
    task_families = [str(task.get("task_family", "")) for task in tasks if str(task.get("task_family", ""))]
    resets_per_task = min((int(task.get("episodes_per_method", 0) or 0) for task in tasks), default=0)
    orders: list[dict[str, Any]] = []
    for row in REQUIRED_ABLATIONS:
        expected_records = len(task_families) * resets_per_task
        orders.append(
            {
                "id": f"collect_ablation_{row['id']}",
                "ablation": row["id"],
                "external_variant": row["external_variant"],
                "local_reference_variant": row["local_reference_variant"],
                "component_removed": row["component_removed"],
                "task_families": ";".join(task_families),
                "paired_resets_per_task": resets_per_task,
                "expected_records": expected_records,
                "operator_input": (
                    "run this ablated variant on the same accepted task configs, skill library, reset ids, "
                    "initial-state hashes, observation interface, and compute budget as the primary method"
                ),
                "required_artifacts": (
                    "external_validation/logs/<task_family>.jsonl; "
                    "external_validation/videos/<task_family>/<run_id>_<ablation>.mp4; "
                    "external_validation/manifest.json ablations.%s=true" % row["id"]
                ),
                "acceptance_commands": " | ".join(STRICT_COMMANDS),
            }
        )
    return orders


def required_ablation_ids() -> set[str]:
    return {row["id"] for row in REQUIRED_ABLATIONS}


def order_map(work_orders: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(order.get("ablation", "")): order
        for order in work_orders
        if isinstance(order, dict) and str(order.get("ablation", ""))
    }


def work_orders_are_actionable(work_orders: list[dict[str, Any]], task_families: list[str], resets_per_task: int) -> bool:
    orders_by_ablation = order_map(work_orders)
    required_fragments = (
        "same accepted task configs",
        "skill library",
        "reset ids",
        "initial-state hashes",
        "observation interface",
        "compute budget",
    )
    required_command_fragments = (
        "real_collection_runner.py",
        "build_external_postcollection_evidence_seal.py",
        "audit_external_postcollection_seal_consistency.py",
        "build_external_manifest.py --write",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    )
    for row in REQUIRED_ABLATIONS:
        order = orders_by_ablation.get(row["id"])
        if not order:
            return False
        operator_input = str(order.get("operator_input", ""))
        required_artifacts = str(order.get("required_artifacts", ""))
        commands = str(order.get("acceptance_commands", ""))
        task_field = str(order.get("task_families", ""))
        expected_records = int(order.get("expected_records", 0) or 0)
        if row["external_variant"] != order.get("external_variant"):
            return False
        if row["local_reference_variant"] != order.get("local_reference_variant"):
            return False
        if expected_records != len(task_families) * resets_per_task:
            return False
        if not all(task in task_field for task in task_families):
            return False
        if not all(fragment in operator_input for fragment in required_fragments):
            return False
        if "external_validation/logs/<task_family>.jsonl" not in required_artifacts:
            return False
        if "external_validation/videos/<task_family>/<run_id>_<ablation>.mp4" not in required_artifacts:
            return False
        if f"external_validation/manifest.json ablations.{row['id']}=true" not in required_artifacts:
            return False
        if not all(fragment in commands for fragment in required_command_fragments):
            return False
    return True


def audit_packet(
    packet: dict[str, Any],
    collection: dict[str, Any],
    evidence: dict[str, Any],
    manifest_template: dict[str, Any],
) -> dict[str, Any]:
    tasks = collection_tasks(collection)
    task_families = [str(task.get("task_family", "")) for task in tasks if str(task.get("task_family", ""))]
    resets_per_task = min((int(task.get("episodes_per_method", 0) or 0) for task in tasks), default=0)
    recomputed_expected_records = len(task_families) * resets_per_task * len(REQUIRED_ABLATIONS)
    missing = strict_missing_ablations(evidence)
    manifest_ablations = manifest_template.get("ablations", {})
    manifest_ablations = manifest_ablations if isinstance(manifest_ablations, dict) else {}
    work_orders = [order for order in packet.get("work_orders", []) or [] if isinstance(order, dict)]
    packet_ablation_ids = {str(row.get("id", "")) for row in packet.get("required_ablations", []) or []}
    local_ablation_csv = ROOT / "results" / "ablation_metrics.csv"

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("strict_external_evidence_ready") is False
        and packet.get("manifest_ablation_evidence_ready") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_external_evidence_ready={packet.get('strict_external_evidence_ready')!r}, "
            f"manifest_ablation_evidence_ready={packet.get('manifest_ablation_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "collection_plan_loaded",
        collection.get("passed") is True and collection.get("not_external_evidence") is True,
        f"passed={collection.get('passed')!r}, not_external_evidence={collection.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "task_and_reset_budget_preserved",
        len(task_families) >= 4
        and resets_per_task >= 30
        and recomputed_expected_records >= 600
        and int(packet.get("expected_ablation_records", 0) or 0) == recomputed_expected_records
        and packet.get("task_families") == task_families,
        (
            f"tasks={task_families}, resets_per_task={resets_per_task}, "
            f"packet_expected={packet.get('expected_ablation_records')!r}, "
            f"recomputed_expected={recomputed_expected_records}"
        ),
    )
    add_check(
        checks,
        "required_ablations_match_strict_audit",
        set(missing) == required_ablation_ids()
        and packet_ablation_ids == required_ablation_ids()
        and set(packet.get("blocking_missing", []) or [])
        == {
            f"manifest.ablations.{name} is not true with manifest-declared external ablation evidence"
            for name in missing
        },
        f"strict_missing={missing}, packet_ablation_ids={sorted(packet_ablation_ids)}",
    )
    add_check(
        checks,
        "every_required_ablation_has_work_order",
        set(order_map(work_orders)) == required_ablation_ids()
        and int(packet.get("work_order_count", 0) or 0) == len(REQUIRED_ABLATIONS),
        f"work_orders={len(work_orders)}, ids={sorted(order_map(work_orders))}",
    )
    add_check(
        checks,
        "work_orders_use_local_reference_variants",
        local_ablation_csv.exists()
        and all(row["local_reference_variant"] in local_ablation_csv.read_text(encoding="utf-8") for row in REQUIRED_ABLATIONS)
        and all(
            order_map(work_orders).get(row["id"], {}).get("local_reference_variant") == row["local_reference_variant"]
            for row in REQUIRED_ABLATIONS
        ),
        "local ablation variants are present in results/ablation_metrics.csv and bound in work orders",
    )
    add_check(
        checks,
        "work_orders_are_actionable_and_artifact_bound",
        work_orders_are_actionable(work_orders, task_families, resets_per_task),
        "each work order binds same configs/resets/interfaces/budget, JSONL/video artifacts, manifest ablation booleans, and strict acceptance commands",
    )
    add_check(
        checks,
        "manifest_template_declares_ablation_booleans",
        all(name in manifest_ablations for name in required_ablation_ids())
        and all(manifest_ablations.get(name) is False for name in required_ablation_ids()),
        f"manifest_ablation_keys={sorted(manifest_ablations)}",
    )
    command_text = "\n".join(str(command) for command in packet.get("operator_commands", []) or [])
    add_check(
        checks,
        "operator_commands_cover_collection_manifest_rollout_and_strict_evidence",
        all(
            term in command_text
            for term in (
                "real_collection_runner.py",
                "build_external_postcollection_evidence_seal.py",
                "audit_external_postcollection_seal_consistency.py",
                "build_external_manifest.py",
                "validate_external_rollouts.py",
                "audit_external_evidence.py",
            )
        ),
        "strict ablation commands preserve collection-to-manifest gate order",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        **packet,
        "passed": passed,
        "ablation_collection_packet_ready": passed,
        "checks": checks,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    WORK_ORDERS_CSV.parent.mkdir(exist_ok=True)
    fieldnames = [
        "id",
        "ablation",
        "external_variant",
        "local_reference_variant",
        "component_removed",
        "task_families",
        "paired_resets_per_task",
        "expected_records",
        "operator_input",
        "required_artifacts",
        "acceptance_commands",
    ]
    with WORK_ORDERS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Ablation Collection Packet",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Manifest ablation evidence ready: `{str(payload['manifest_ablation_evidence_ready']).lower()}`.",
        f"Expected ablation records: `{payload['expected_ablation_records']}`.",
        "",
        "This packet turns the strict external ablation requirement into operator work orders. It does not create rollout logs, videos, a real manifest, or ablation evidence.",
        "",
        "## Required External Ablations",
        "",
    ]
    for row in payload["required_ablations"]:
        lines.append(
            f"- `{row['id']}` -> `{row['external_variant']}`: remove {row['component_removed']}."
        )
    lines.extend(["", "## Blocking Missing", ""])
    for item in payload["blocking_missing"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Operator Commands", ""])
    for command in payload["operator_commands"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    collection = read_json(RESULTS / "external_collection_plan.json")
    evidence = read_json(RESULTS / "external_evidence_audit.json")
    manifest_template = read_json(EXTERNAL / "manifest_template.json")

    tasks = collection_tasks(collection)
    task_families = [str(task.get("task_family", "")) for task in tasks if str(task.get("task_family", ""))]
    resets_per_task = min((int(task.get("episodes_per_method", 0) or 0) for task in tasks), default=0)
    work_orders = build_work_orders(collection)
    expected_records = sum(int(order["expected_records"]) for order in work_orders)
    missing = strict_missing_ablations(evidence)

    payload = audit_packet(
        {
        "version": PACKET_VERSION,
        "audit_version": AUDIT_VERSION,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "manifest_ablation_evidence_ready": False,
        "source_collection_plan": rel(RESULTS / "external_collection_plan.json"),
        "source_external_evidence_audit": rel(RESULTS / "external_evidence_audit.json"),
        "required_ablations": REQUIRED_ABLATIONS,
        "task_families": task_families,
        "paired_resets_per_task": resets_per_task,
        "expected_ablation_records": expected_records,
        "work_order_count": len(work_orders),
        "work_orders_path": rel(WORK_ORDERS_CSV),
        "work_orders": work_orders,
        "operator_commands": STRICT_COMMANDS,
        "blocking_missing": [
            f"manifest.ablations.{name} is not true with manifest-declared external ablation evidence"
            for name in missing
        ],
        },
        collection,
        evidence,
        manifest_template,
    )
    passed = payload["passed"]

    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    write_csv(work_orders)
    PACKET_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps({**payload, "version": AUDIT_VERSION}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)

    status = "PASS" if passed else "FAIL"
    print(f"External ablation collection packet: {status}; work_orders={len(work_orders)}; expected_records={expected_records}")
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

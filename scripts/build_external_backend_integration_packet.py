from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RUNNER = EXTERNAL / "runner"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "backend_integration_packet.json"
PACKET_MD = EXTERNAL / "backend_integration_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "backend_integration_work_orders.csv"
AUDIT_JSON = RESULTS / "external_backend_integration_audit.json"
AUDIT_MD = RESULTS / "external_backend_integration_audit.md"

PACKET_VERSION = "external_backend_integration_packet_v1"
AUDIT_VERSION = "external_backend_integration_audit_v1"

REQUIRED_BACKEND_HOOKS = [
    "platform_provenance",
    "load_task_config",
    "reset_scene",
    "capture_observation",
    "terminal_samples",
    "run_method",
    "execute_skill_pair",
    "record_video",
    "policy_or_config_hash",
]

REQUIRED_PROVENANCE_FIELDS = [
    "platform_name",
    "platform_version",
    "maniskill_version",
    "sapien_version",
    "python_version",
    "operating_system",
    "gpu_model",
    "gpu_driver",
    "vulkan_or_renderer_device",
    "physics_timestep",
    "contact_solver",
    "friction_model",
    "camera_intrinsics_and_resolution",
    "state_observation_keys",
    "contact_signal_keys",
    "backend_module_sha256",
    "code_commit",
]

STRICT_ACCEPTANCE_COMMANDS = [
    r"python scripts\build_external_backend_integration_packet.py",
    r"python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json",
    r"python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\audit_external_fidelity_acceptance.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_postcollection_evidence_seal.py",
    r"python scripts\audit_external_postcollection_seal_consistency.py",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_work_orders(onboarding: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = [str(task) for task in onboarding.get("planned_tasks", []) or []]
    primary_route = str(onboarding.get("primary_route", ""))
    platform_family = str(onboarding.get("primary_platform_family", ""))
    common_artifacts = [
        "external_validation/runner/backends/<real_backend>.py",
        "external_validation/fidelity_acceptance.json",
        "external_validation/configs/*.json",
        "external_validation/logs/*.jsonl",
        "external_validation/videos/<task_family>/",
    ]
    return [
        {
            "id": "create_non_template_backend_module",
            "route": primary_route,
            "platform_family": platform_family,
            "operator_input": "implement create_backend() or Backend using ExternalCollectionBackend without TEMPLATE_ONLY",
            "required_hooks": REQUIRED_BACKEND_HOOKS,
            "required_artifacts": common_artifacts[:2],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[:2],
        },
        {
            "id": "bind_task_configs_to_backend",
            "route": primary_route,
            "platform_family": platform_family,
            "operator_input": "load every prepared task config and record the exact accepted platform values",
            "required_tasks": tasks,
            "required_artifacts": ["external_validation/configs/*.json", "external_validation/config_schema_v1.json"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[2:5],
        },
        {
            "id": "preserve_paired_reset_execution",
            "route": primary_route,
            "platform_family": platform_family,
            "operator_input": "make reset_scene preserve scene_id, seed, skill_i, skill_j, and initial_state_hash across the full method panel",
            "required_tasks": tasks,
            "required_artifacts": ["external_validation/blinded_operator_sheet.csv", "external_validation/method_alias_map.json"],
            "acceptance_commands": [STRICT_ACCEPTANCE_COMMANDS[5]],
        },
        {
            "id": "bridge_method_adapters_and_hashes",
            "route": primary_route,
            "platform_family": platform_family,
            "operator_input": "route run_method through real manifest-declared method implementations and emit policy_or_config_hash",
            "required_hooks": ["run_method", "policy_or_config_hash", "terminal_samples"],
            "required_artifacts": [
                "external_validation/method_implementation_packet.md",
                "external_validation/method_implementation_work_orders.csv",
            ],
            "acceptance_commands": [
                r"python scripts\build_external_method_implementation_packet.py",
                r"python scripts\validate_external_adapters.py --strict",
            ],
        },
        {
            "id": "export_logs_videos_and_manifest_inputs",
            "route": primary_route,
            "platform_family": platform_family,
            "operator_input": "write JSONL records and videos from the real backend, then hash-lock them into the manifest",
            "required_tasks": tasks,
            "required_artifacts": common_artifacts[3:],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[6:],
        },
    ]


def build_packet(onboarding: dict[str, Any], backend_contract: dict[str, Any], collection: dict[str, Any]) -> dict[str, Any]:
    work_orders = build_work_orders(onboarding)
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "backend_integration_packet_ready": True,
        "strict_backend_ready": False,
        "strict_evidence_ready": False,
        "purpose": "Convert the missing non-template backend module into concrete integration work orders for the independent public-simulator route.",
        "primary_route": onboarding.get("primary_route"),
        "primary_platform_family": onboarding.get("primary_platform_family"),
        "planned_tasks": onboarding.get("planned_tasks", []),
        "planned_records": onboarding.get("planned_records"),
        "backend_contract_harness_ready": backend_contract.get("backend_contract_harness_ready") is True,
        "actual_backend_ready": backend_contract.get("actual_backend_ready") is True,
        "collection_ready": collection.get("collection_ready") is True,
        "current_backend_blockers": [
            blocker for blocker in collection.get("blocking_missing", []) or [] if "backend" in str(blocker).lower()
        ],
        "required_backend_hooks": REQUIRED_BACKEND_HOOKS,
        "required_platform_provenance_fields": REQUIRED_PROVENANCE_FIELDS,
        "work_orders": work_orders,
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "using backend_templates as real backends",
            "using local_dry_run logs or placeholder videos as external evidence",
            "collecting before strict backend qualification and collection readiness pass",
            "changing task configs or method identities after alias unsealing",
            "omitting policy/config hashes or platform provenance from logs and manifest inputs",
        ],
        "source_reports": [
            rel(EXTERNAL / "platform_onboarding_packet.json"),
            rel(RESULTS / "external_platform_onboarding_audit.json"),
            rel(RESULTS / "external_backend_contract_audit.json"),
            rel(RESULTS / "external_collection_readiness_audit.json"),
        ],
    }


def audit_packet(packet: dict[str, Any], onboarding: dict[str, Any], backend_contract: dict[str, Any], collection: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    work_orders = packet.get("work_orders", []) or []
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    order_ids = {order.get("id") for order in work_orders}
    orders_by_id = {str(order.get("id", "")): order for order in work_orders if str(order.get("id", ""))}
    required_order_ids = {
        "create_non_template_backend_module",
        "bind_task_configs_to_backend",
        "preserve_paired_reset_execution",
        "bridge_method_adapters_and_hashes",
        "export_logs_videos_and_manifest_inputs",
    }

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("backend_integration_packet_ready") is True
        and packet.get("strict_backend_ready") is False
        and packet.get("strict_evidence_ready") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_backend_ready={packet.get('strict_backend_ready')!r}, "
            f"strict_evidence_ready={packet.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "primary_route_matches_onboarding",
        packet.get("primary_route") == onboarding.get("primary_route")
        and packet.get("primary_platform_family") == onboarding.get("primary_platform_family")
        and onboarding.get("primary_route_independent_of_haonan") is True,
        f"route={packet.get('primary_route')!r}, platform={packet.get('primary_platform_family')!r}",
    )
    add_check(
        checks,
        "backend_contract_harness_ready_but_backend_missing",
        backend_contract.get("backend_contract_harness_ready") is True
        and backend_contract.get("actual_backend_ready") is False
        and packet.get("actual_backend_ready") is False,
        f"actual_backend_ready={backend_contract.get('actual_backend_ready')!r}",
    )
    add_check(
        checks,
        "work_orders_cover_backend_to_manifest_path",
        required_order_ids.issubset(order_ids),
        f"missing={sorted(required_order_ids - order_ids)}",
    )
    actionable_orders = [
        order
        for order_id, order in orders_by_id.items()
        if order_id in required_order_ids
        and str(order.get("route", "")).strip()
        and str(order.get("platform_family", "")).strip()
        and str(order.get("operator_input", "")).strip()
        and len(order.get("required_artifacts", []) or []) > 0
        and len(order.get("acceptance_commands", []) or []) > 0
    ]
    add_check(
        checks,
        "work_orders_are_actionable_and_artifact_bound",
        len(actionable_orders) == len(required_order_ids),
        f"actionable_orders={len(actionable_orders)}, required_orders={len(required_order_ids)}",
    )
    add_check(
        checks,
        "required_hooks_declared",
        set(REQUIRED_BACKEND_HOOKS).issubset(set(packet.get("required_backend_hooks", []) or [])),
        f"hooks={packet.get('required_backend_hooks')!r}",
    )
    add_check(
        checks,
        "provenance_fields_declared",
        {"maniskill_version", "sapien_version", "backend_module_sha256", "code_commit"}.issubset(
            set(packet.get("required_platform_provenance_fields", []) or [])
        ),
        f"provenance_fields={len(packet.get('required_platform_provenance_fields', []) or [])}",
    )
    add_check(
        checks,
        "tasks_and_record_budget_preserved",
        len(packet.get("planned_tasks", []) or []) >= 4
        and int(packet.get("planned_records", 0) or 0) >= 1440,
        f"tasks={packet.get('planned_tasks')!r}, records={packet.get('planned_records')!r}",
    )
    add_check(
        checks,
        "strict_commands_cover_backend_config_fidelity_collection_and_evidence",
        all(
            fragment in command_text
            for fragment in (
                "audit_external_backend_contract.py --strict",
                "materialize_external_configs.py",
                "validate_external_configs.py --strict",
                "audit_external_fidelity_acceptance.py --strict",
                "audit_external_collection_readiness.py --strict",
                "real_collection_runner.py",
                "build_external_postcollection_evidence_seal.py",
                "audit_external_postcollection_seal_consistency.py",
                "build_external_manifest.py --write",
                "validate_external_rollouts.py",
                "audit_external_evidence.py --strict",
            )
        ),
        f"commands={packet.get('strict_acceptance_commands')!r}",
    )
    add_check(
        checks,
        "collection_readiness_still_blocks_backend",
        collection.get("collection_ready") is False
        and any("backend_module_ready" in str(blocker) for blocker in collection.get("blocking_missing", []) or []),
        f"collection_ready={collection.get('collection_ready')!r}, blockers={collection.get('blocking_missing')!r}",
    )
    add_check(
        checks,
        "no_real_backend_files_created",
        not (RUNNER / "backends").exists(),
        "external_validation/runner/backends is intentionally absent until an independent operator supplies a backend",
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
        "backend_integration_packet_ready": passed,
        "strict_backend_ready": False,
        "strict_evidence_ready": False,
        "source_packet": rel(PACKET_JSON),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_work_orders_csv(work_orders: list[dict[str, Any]]) -> None:
    fieldnames = [
        "id",
        "route",
        "platform_family",
        "operator_input",
        "required_hooks",
        "required_tasks",
        "required_artifacts",
        "acceptance_commands",
    ]
    with WORK_ORDERS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for order in work_orders:
            writer.writerow(
                {
                    "id": order.get("id", ""),
                    "route": order.get("route", ""),
                    "platform_family": order.get("platform_family", ""),
                    "operator_input": order.get("operator_input", ""),
                    "required_hooks": ";".join(order.get("required_hooks", []) or []),
                    "required_tasks": ";".join(order.get("required_tasks", []) or []),
                    "required_artifacts": ";".join(order.get("required_artifacts", []) or []),
                    "acceptance_commands": ";".join(order.get("acceptance_commands", []) or []),
                }
            )


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Backend Integration Packet",
        "",
        "Not evidence: `true`.",
        f"Primary route: `{packet['primary_route']}`.",
        f"Primary platform family: `{packet['primary_platform_family']}`.",
        f"Strict backend ready: `{str(packet['strict_backend_ready']).lower()}`.",
        f"Strict evidence ready: `{str(packet['strict_evidence_ready']).lower()}`.",
        "",
        "This packet converts the missing non-template backend module into concrete integration work orders for the independent public-simulator route. It does not provide a backend, rollout logs, videos, manifest, or accepted high-fidelity evidence.",
        "",
        "## Forbidden Evidence Shortcuts",
        "",
    ]
    for item in packet["forbidden_evidence_shortcuts"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Required Backend Hooks", ""])
    for hook in packet["required_backend_hooks"]:
        lines.append(f"- `{hook}`")
    lines.extend(["", "## Required Platform Provenance Fields", ""])
    for field in packet["required_platform_provenance_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Work Orders", ""])
    for order in packet["work_orders"]:
        lines.extend(
            [
                f"### `{order['id']}`",
                "",
                f"- Route: `{order['route']}`",
                f"- Platform family: `{order['platform_family']}`",
                f"- Operator input: {order['operator_input']}",
                "- Required artifacts: " + ", ".join(f"`{item}`" for item in order.get("required_artifacts", []) or []),
                "",
            ]
        )
        if order.get("required_hooks"):
            lines.append("- Required hooks: " + ", ".join(f"`{item}`" for item in order["required_hooks"]))
        if order.get("required_tasks"):
            lines.append("- Required tasks: " + ", ".join(f"`{item}`" for item in order["required_tasks"]))
        lines.append("")
    lines.extend(["## Strict Acceptance Commands", ""])
    for command in packet["strict_acceptance_commands"]:
        lines.append(f"- `{command}`")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Backend Integration Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Backend integration packet ready: `{str(audit['backend_integration_packet_ready']).lower()}`.",
        f"Strict backend ready: `{str(audit['strict_backend_ready']).lower()}`.",
        f"Strict evidence ready: `{str(audit['strict_evidence_ready']).lower()}`.",
        "",
        "This audit checks that the missing backend module has concrete integration work orders while strict backend readiness and strict external evidence remain false.",
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
    onboarding = read_json(EXTERNAL / "platform_onboarding_packet.json")
    backend_contract = read_json(RESULTS / "external_backend_contract_audit.json")
    collection = read_json(RESULTS / "external_collection_readiness_audit.json")
    packet = build_packet(onboarding, backend_contract, collection)
    write_work_orders_csv(packet["work_orders"])
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_packet_md(packet)
    audit = audit_packet(packet, onboarding, backend_contract, collection)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External backend integration packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"work_orders={len(packet['work_orders'])}; not_evidence=true"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

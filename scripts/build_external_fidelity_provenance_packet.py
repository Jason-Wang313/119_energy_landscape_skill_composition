from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "fidelity_provenance_packet.json"
PACKET_MD = EXTERNAL / "fidelity_provenance_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "fidelity_provenance_work_orders.csv"
AUDIT_JSON = RESULTS / "external_fidelity_provenance_audit.json"
AUDIT_MD = RESULTS / "external_fidelity_provenance_audit.md"

PACKET_VERSION = "external_fidelity_provenance_packet_v1"
AUDIT_VERSION = "external_fidelity_provenance_audit_v1"

STRICT_ACCEPTANCE_COMMANDS = [
    r"python scripts\build_external_fidelity_provenance_packet.py",
    r"python scripts\build_external_platform_onboarding.py",
    r"python scripts\probe_external_platform.py --strict",
    r"python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write",
    r"python scripts\audit_external_fidelity_acceptance.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
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


def platform_fields(template: dict[str, Any]) -> list[str]:
    platform = template.get("platform", {})
    return sorted(platform) if isinstance(platform, dict) else []


def qualification_fields(template: dict[str, Any]) -> list[str]:
    qualification = template.get("qualification", {})
    return sorted(qualification) if isinstance(qualification, dict) else []


def gate_names(template: dict[str, Any]) -> list[str]:
    gates = template.get("acceptance_gates", [])
    if not isinstance(gates, list):
        return []
    return [str(gate.get("name", "")) for gate in gates if isinstance(gate, dict) and str(gate.get("name", ""))]


def task_names(template: dict[str, Any]) -> list[str]:
    tasks = template.get("task_fidelity", [])
    if not isinstance(tasks, list):
        return []
    return [str(task.get("task_family", "")) for task in tasks if isinstance(task, dict) and str(task.get("task_family", ""))]


def build_work_orders(fidelity: dict[str, Any], template: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = list(fidelity.get("blocking_missing", []) or [])
    return [
        {
            "id": "fill_platform_identity_and_physics",
            "scope": "platform",
            "operator_input": "run the external platform probe on the selected machine, then fill platform_name, platform_version, physics engine, contact solver, timestep, substeps, robot model, assets, sensors, and contact/force channels",
            "required_artifacts": ["results/external_platform_probe.json", "external_validation/fidelity_acceptance.json"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[:5],
            "blocks": [item for item in blockers if "platform" in item or "route" in item],
        },
        {
            "id": "verify_contact_dynamics_and_observability",
            "scope": "task_fidelity",
            "operator_input": "document why each skill seam exposes the contact/dynamics failures needed for Paper 119's diagnosis and risk estimates",
            "required_artifacts": ["external_validation/fidelity_acceptance.json", "external_validation/videos/<task_family>/*"],
            "acceptance_commands": [STRICT_ACCEPTANCE_COMMANDS[2], STRICT_ACCEPTANCE_COMMANDS[3], STRICT_ACCEPTANCE_COMMANDS[7]],
            "blocks": [item for item in blockers if "qualification_text" in item or "all_acceptance_gates" in item],
        },
        {
            "id": "verify_paired_reset_replay",
            "scope": "collection",
            "operator_input": "prove the selected platform can replay the same scene, seed, skill pair, and initial-state hash across every method panel",
            "required_artifacts": ["external_validation/fidelity_acceptance.json", "external_validation/blinded_operator_sheet.csv"],
            "acceptance_commands": [STRICT_ACCEPTANCE_COMMANDS[2], STRICT_ACCEPTANCE_COMMANDS[3], STRICT_ACCEPTANCE_COMMANDS[6]],
            "blocks": [item for item in blockers if "paired" in item or "acceptance_gates" in item],
        },
        {
            "id": "document_operator_independence_and_calibration_basis",
            "scope": "provenance",
            "operator_input": "record independent operator/lab, date lock, calibration or benchmark basis, known limitations, and no target-collaborator dependency",
            "required_artifacts": ["external_validation/fidelity_acceptance.json"],
            "acceptance_commands": [STRICT_ACCEPTANCE_COMMANDS[2], STRICT_ACCEPTANCE_COMMANDS[3]],
            "blocks": [item for item in blockers if "operator" in item or "date_locked" in item],
        },
        {
            "id": "lock_code_skill_and_artifact_hashes",
            "scope": "release",
            "operator_input": "fill code commit, skill-library hash, artifact hash policy, and the future manifest path; manifest-declared fidelity_acceptance_path is checked after postcollection sealing",
            "required_artifacts": ["external_validation/fidelity_acceptance.json"],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[2:5],
            "blocks": [item for item in blockers if "commit" in item or "hash" in item or "manifest" in item],
        },
        {
            "id": "run_strict_fidelity_and_external_gates",
            "scope": "final_gate",
            "operator_input": "after platform provenance, logs, videos, configs, implementations, and hashes are real, run strict fidelity and external-evidence gates",
            "required_artifacts": [
                "results/external_fidelity_acceptance_audit.json",
                "results/external_rollout_metrics.json",
                "results/external_evidence_audit.json",
            ],
            "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS[2:],
            "blocks": blockers,
        },
    ]


def build_packet(
    fidelity: dict[str, Any],
    onboarding: dict[str, Any],
    collection: dict[str, Any],
    route: dict[str, Any],
    template: dict[str, Any],
    platform_probe: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "fidelity_provenance_packet_ready": True,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "acceptance_ready": False,
        "manifest_written": False,
        "purpose": "Convert the platform fidelity/provenance blocker into fillable, auditable work orders before official external rollout collection. Accepted fidelity is not external evidence until postcollection logs, videos, manifest entries, and strict audits pass.",
        "readiness_state": fidelity.get("readiness_state", ""),
        "expected_real_acceptance_path": fidelity.get("expected_real_acceptance_path", "external_validation/fidelity_acceptance.json"),
        "blocking_missing_count": int(fidelity.get("blocking_missing_count", 0) or 0),
        "blocking_missing": list(fidelity.get("blocking_missing", []) or []),
        "primary_route": route.get("primary_route", ""),
        "platform_onboarding_ready": onboarding.get("platform_onboarding_ready") is True,
        "platform_probe_ready": platform_probe.get("platform_probe_ready") is True,
        "platform_probe_primary_route_install_ready": platform_probe.get("primary_route_install_ready") is True,
        "platform_probe_missing_packages": list(platform_probe.get("primary_route_missing_packages", []) or []),
        "collection_ready": collection.get("collection_ready") is True,
        "template_platform_fields": platform_fields(template),
        "template_qualification_fields": qualification_fields(template),
        "template_acceptance_gates": gate_names(template),
        "template_task_families": task_names(template),
        "work_orders": build_work_orders(fidelity, template),
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "treating fidelity_acceptance_template.json as real acceptance evidence",
            "using a platform without filled physics/contact provenance and accepted limitations",
            "counting rollouts before paired reset replay is verified",
            "omitting operator independence, code commit, or skill-library hash",
            "claiming high-fidelity validation before strict fidelity and external-evidence audits pass",
        ],
        "source_reports": [
            rel(RESULTS / "external_fidelity_acceptance_audit.json"),
            rel(RESULTS / "external_platform_onboarding_audit.json"),
            rel(RESULTS / "external_collection_readiness_audit.json"),
            rel(RESULTS / "independent_validation_route_audit.json"),
            rel(EXTERNAL / "fidelity_acceptance_template.json"),
            rel(RESULTS / "external_platform_probe.json"),
        ],
    }


def audit_packet(
    packet: dict[str, Any],
    fidelity: dict[str, Any],
    onboarding: dict[str, Any],
    collection: dict[str, Any],
    route: dict[str, Any],
    template: dict[str, Any],
    platform_probe: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    work_orders = packet.get("work_orders", []) or []
    order_ids = {str(order.get("id", "")) for order in work_orders}
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    required_orders = {
        "fill_platform_identity_and_physics",
        "verify_contact_dynamics_and_observability",
        "verify_paired_reset_replay",
        "document_operator_independence_and_calibration_basis",
        "lock_code_skill_and_artifact_hashes",
        "run_strict_fidelity_and_external_gates",
    }

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("fidelity_provenance_packet_ready") is True
        and packet.get("strict_fidelity_evidence_ready") is False
        and packet.get("strict_external_evidence_ready") is False
        and packet.get("acceptance_ready") is False
        and packet.get("manifest_written") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_fidelity_evidence_ready={packet.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={packet.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "fidelity_acceptance_contract_ready_but_not_evidence",
        fidelity.get("passed") is True
        and fidelity.get("not_external_evidence") is True
        and fidelity.get("acceptance_ready") is False
        and fidelity.get("readiness_state") == "COLLECT_PLATFORM_PROVENANCE"
        and int(fidelity.get("blocking_missing_count", 0) or 0) >= 10,
        (
            f"acceptance_ready={fidelity.get('acceptance_ready')!r}, "
            f"blocking_missing_count={fidelity.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "platform_onboarding_packet_ready",
        onboarding.get("passed") is True
        and onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False,
        (
            f"platform_onboarding_ready={onboarding.get('platform_onboarding_ready')!r}, "
            f"strict_evidence_ready={onboarding.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_platform_probe_ready",
        platform_probe.get("version") == "external_platform_probe_v1"
        and platform_probe.get("passed") is True
        and platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_fidelity_evidence_ready") is False
        and platform_probe.get("strict_external_evidence_ready") is False,
        (
            f"primary_route_install_ready={platform_probe.get('primary_route_install_ready')!r}, "
            f"missing={platform_probe.get('primary_route_missing_packages')!r}"
        ),
    )
    add_check(
        checks,
        "independent_route_and_collection_still_fail_closed",
        route.get("passed") is True
        and route.get("not_external_evidence") is True
        and collection.get("collection_ready") is False,
        f"primary_route={route.get('primary_route')!r}, collection_ready={collection.get('collection_ready')!r}",
    )
    add_check(
        checks,
        "template_declares_required_platform_and_gate_fields",
        len(platform_fields(template)) >= 12
        and len(qualification_fields(template)) >= 14
        and len(gate_names(template)) >= 5
        and len(task_names(template)) >= 4,
        (
            f"platform_fields={len(platform_fields(template))}, "
            f"qualification_fields={len(qualification_fields(template))}, "
            f"gates={len(gate_names(template))}, tasks={len(task_names(template))}"
        ),
    )
    add_check(
        checks,
        "work_orders_cover_fidelity_blockers",
        required_orders <= order_ids
        and int(packet.get("blocking_missing_count", 0) or 0) >= 10,
        f"missing_orders={sorted(required_orders - order_ids)}",
    )
    required_fragments = [
        "build_external_fidelity_provenance_packet.py",
        "build_external_platform_onboarding.py",
        "probe_external_platform.py --strict",
        "materialize_fidelity_acceptance.py",
        "audit_external_fidelity_acceptance.py --strict",
        "build_external_manifest.py --write",
        "audit_external_collection_readiness.py --strict",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ]
    add_check(
        checks,
        "strict_commands_cover_fidelity_manifest_collection_and_evidence",
        all(fragment in command_text for fragment in required_fragments),
        command_text,
    )
    add_check(
        checks,
        "acceptance_template_not_real_evidence",
        template.get("version") == "paper119_fidelity_acceptance_template_v1"
        and template.get("not_external_evidence") is True
        and template.get("template_only") is True,
        (
            f"version={template.get('version')!r}, "
            f"template_only={template.get('template_only')!r}"
        ),
    )
    add_check(
        checks,
        "no_real_acceptance_or_manifest_written",
        not (EXTERNAL / "fidelity_acceptance.json").exists()
        and not (EXTERNAL / "manifest.json").exists(),
        (
            f"acceptance_exists={(EXTERNAL / 'fidelity_acceptance.json').exists()}, "
            f"manifest_exists={(EXTERNAL / 'manifest.json').exists()}"
        ),
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
        "fidelity_provenance_packet_ready": packet.get("fidelity_provenance_packet_ready") is True,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "acceptance_ready": False,
        "blocking_missing_count": packet.get("blocking_missing_count", 0),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
        "packet_path": rel(PACKET_JSON),
        "work_orders_path": rel(WORK_ORDERS_CSV),
    }


def write_work_orders(packet: dict[str, Any]) -> None:
    rows = packet.get("work_orders", []) or []
    fieldnames = ["id", "scope", "operator_input", "required_artifacts", "acceptance_commands", "blocks"]
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
                    "blocks": "; ".join(row.get("blocks", []) or []),
                }
            )


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Fidelity Provenance Packet",
        "",
        f"Packet ready: `{str(packet['fidelity_provenance_packet_ready']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict fidelity evidence ready: `{str(packet['strict_fidelity_evidence_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(packet['strict_external_evidence_ready']).lower()}`.",
        f"Platform probe ready: `{str(packet['platform_probe_ready']).lower()}`.",
        f"Primary route install ready in latest probe: `{str(packet['platform_probe_primary_route_install_ready']).lower()}`.",
        f"Latest probe missing packages: `{packet['platform_probe_missing_packages']}`.",
        f"Blocking missing items: `{packet['blocking_missing_count']}`.",
        "",
        "This packet is a non-evidence work-order layer for platform fidelity and provenance. It exists so an independent operator can fill the real acceptance file before any robot or high-fidelity simulator rollout counts as evidence.",
        "",
        "## Work Orders",
        "",
    ]
    for order in packet["work_orders"]:
        lines.append(f"- `{order['id']}` ({order['scope']}): {order['operator_input']}")
    lines.extend(["", "## Strict Acceptance Commands", ""])
    for command in packet["strict_acceptance_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Forbidden Shortcuts", ""])
    for shortcut in packet["forbidden_evidence_shortcuts"]:
        lines.append(f"- {shortcut}")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Fidelity Provenance Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Fidelity provenance packet ready: `{str(audit['fidelity_provenance_packet_ready']).lower()}`.",
        f"Strict fidelity evidence ready: `{str(audit['strict_fidelity_evidence_ready']).lower()}`.",
        f"Blocking missing items: `{audit['blocking_missing_count']}`.",
        "",
        "This audit checks that the platform fidelity/provenance packet is complete as an operator checklist while strict fidelity and external evidence gates remain fail-closed.",
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
    fidelity = read_json(RESULTS / "external_fidelity_acceptance_audit.json")
    onboarding = read_json(RESULTS / "external_platform_onboarding_audit.json")
    collection = read_json(RESULTS / "external_collection_readiness_audit.json")
    route = read_json(RESULTS / "independent_validation_route_audit.json")
    template = read_json(EXTERNAL / "fidelity_acceptance_template.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")

    packet = build_packet(fidelity, onboarding, collection, route, template, platform_probe)
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_work_orders(packet)
    write_packet_md(packet)

    audit = audit_packet(packet, fidelity, onboarding, collection, route, template, platform_probe)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External fidelity provenance packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"blocking={audit['blocking_missing_count']}"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

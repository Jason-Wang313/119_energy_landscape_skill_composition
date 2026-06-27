from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SPEC_DIR = EXTERNAL / "baseline_specs"

PACKET_JSON = EXTERNAL / "method_implementation_packet.json"
PACKET_MD = EXTERNAL / "method_implementation_packet.md"
WORK_ORDERS_CSV = EXTERNAL / "method_implementation_work_orders.csv"
AUDIT_JSON = RESULTS / "external_method_implementation_audit.json"
AUDIT_MD = RESULTS / "external_method_implementation_audit.md"

PACKET_VERSION = "external_method_implementation_packet_v1"
AUDIT_VERSION = "external_method_implementation_audit_v1"
ORACLE_METHOD = "oracle_basin_composer"

REQUIRED_ARTIFACT_FIELDS = [
    "implementation_path_or_repository",
    "implementation_sha256_or_commit",
    "checkpoint_or_config_path",
    "checkpoint_or_config_hash",
    "adapter_path",
    "manifest_method_entry",
    "policy_or_config_hash_in_logs",
]

STRICT_ACCEPTANCE_COMMANDS = [
    r"python scripts\build_external_method_implementation_packet.py",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\build_external_baseline_contract.py",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
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


def load_specs() -> list[dict[str, Any]]:
    specs = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        spec = read_json(path)
        spec["_path"] = rel(path)
        specs.append(spec)
    return specs


def non_oracle_specs(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [spec for spec in specs if spec.get("method") != ORACLE_METHOD]


def build_work_orders(specs: list[dict[str, Any]], log_schema: dict[str, Any]) -> list[dict[str, Any]]:
    required_log_fields = [
        field
        for field in spec_required_log_fields(log_schema)
        if field in {"method", "policy_or_config_hash", "predicted_seam_risk", "decision", "failure_diagnosis", "success", "realized_seam_breach", "utility"}
    ]
    orders: list[dict[str, Any]] = []
    for spec in non_oracle_specs(specs):
        method = str(spec["method"])
        orders.append(
            {
                "method": method,
                "role": spec.get("role", ""),
                "spec_file": spec.get("_path", ""),
                "required_entrypoint": spec.get("required_entrypoint", ""),
                "target_adapter_dir": f"external_validation/baselines/{method}",
                "suggested_real_implementation_path": f"external_validation/implementations/{method}/implementation.py",
                "manifest_implementation_key": f"methods[{method}].implementation",
                "evidence_status": "missing_manifest_declared_implementation",
                "allowed_inputs": spec.get("allowed_inputs", []),
                "forbidden_advantages": spec.get("forbidden_advantages", []),
                "required_artifact_fields": REQUIRED_ARTIFACT_FIELDS,
                "required_log_fields": required_log_fields,
                "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
                "operator_notes": [
                    "replace scaffold/reference code only with a real implementation or wrapper owned by the external validation operator",
                    "record implementation source hash or repository commit before rollouts start",
                    "record checkpoint/config hash if the method uses learned weights, tuned parameters, demonstrations, or search settings",
                    "do not train, tune, or select using evaluation reset outcomes after method identity is unsealed",
                    "strict adapter validation must pass before any rollout logs from this method count as evidence",
                ],
            }
        )
    return orders


def spec_required_log_fields(log_schema: dict[str, Any]) -> list[str]:
    required = log_schema.get("required_fields", {}) or {}
    if isinstance(required, dict):
        return sorted(str(key) for key in required)
    if isinstance(required, list):
        return sorted(str(item) for item in required)
    return []


def write_work_orders_csv(orders: list[dict[str, Any]]) -> None:
    fieldnames = [
        "method",
        "role",
        "spec_file",
        "required_entrypoint",
        "target_adapter_dir",
        "suggested_real_implementation_path",
        "manifest_implementation_key",
        "evidence_status",
        "required_artifact_fields",
        "required_log_fields",
        "forbidden_advantages",
    ]
    with WORK_ORDERS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for order in orders:
            writer.writerow(
                {
                    **{key: order[key] for key in fieldnames if key in order and not isinstance(order[key], list)},
                    "required_artifact_fields": ";".join(order["required_artifact_fields"]),
                    "required_log_fields": ";".join(order["required_log_fields"]),
                    "forbidden_advantages": ";".join(order["forbidden_advantages"]),
                }
            )


def build_packet(
    specs: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    baseline_audit: dict[str, Any],
    adapter_evidence: dict[str, Any],
) -> dict[str, Any]:
    missing = list(baseline_audit.get("missing_implementations", []) or [])
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "method_implementation_packet_ready": True,
        "strict_adapter_evidence_ready": False,
        "purpose": "Convert the missing independent non-oracle baseline layer into per-method implementation work orders before external rollouts.",
        "source_reports": [
            rel(RESULTS / "external_baseline_contract_audit.json"),
            rel(RESULTS / "external_adapter_contract_evidence_audit.json"),
            rel(EXTERNAL / "log_schema_v1.json"),
        ],
        "non_oracle_method_count": len(work_orders),
        "oracle_method": ORACLE_METHOD,
        "oracle_role": "post_hoc_upper_bound_only_not_an_implementation_work_order",
        "missing_implementations": missing,
        "work_orders": work_orders,
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "using scaffold adapters as manifest-declared implementations",
            "using reference adapters as rollout evidence without real source/config/checkpoint hashes",
            "dropping hard methods after viewing method identity or outcomes",
            "changing compute budgets after seeing paired-reset performance",
            "hand-entering manifest metrics without raw JSONL logs",
        ],
        "adapter_evidence_state": {
            "strict_adapter_audit_passed": adapter_evidence.get("passed") is True,
            "adapter_count": adapter_evidence.get("adapter_count", 0),
        },
        "spec_count": len(specs),
    }


def audit_packet(packet: dict[str, Any], specs: list[dict[str, Any]], baseline_audit: dict[str, Any], adapter_evidence: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    work_orders = packet.get("work_orders", []) or []
    method_names = {order.get("method") for order in work_orders}
    baseline_missing = set(baseline_audit.get("missing_implementations", []) or [])
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    artifact_fields_ok = all(set(REQUIRED_ARTIFACT_FIELDS).issubset(set(order.get("required_artifact_fields", []) or [])) for order in work_orders)
    log_fields_ok = all(
        {"method", "policy_or_config_hash", "predicted_seam_risk", "decision", "failure_diagnosis"}.issubset(set(order.get("required_log_fields", []) or []))
        for order in work_orders
    )

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("method_implementation_packet_ready") is True
        and packet.get("strict_adapter_evidence_ready") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_adapter_evidence_ready={packet.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "work_orders_cover_all_missing_non_oracle_methods",
        len(work_orders) >= 11 and baseline_missing.issubset(method_names),
        f"work_orders={len(work_orders)}, missing={sorted(baseline_missing - method_names)}",
    )
    add_check(
        checks,
        "oracle_excluded_from_work_orders",
        ORACLE_METHOD not in method_names and packet.get("oracle_method") == ORACLE_METHOD,
        f"oracle_in_orders={ORACLE_METHOD in method_names}",
    )
    add_check(
        checks,
        "spec_files_cover_work_orders",
        len(specs) >= len(work_orders) + 1 and all(order.get("spec_file") for order in work_orders),
        f"spec_count={len(specs)}, work_orders={len(work_orders)}",
    )
    add_check(
        checks,
        "required_artifact_fields_declared",
        artifact_fields_ok,
        f"required_artifact_fields={REQUIRED_ARTIFACT_FIELDS}",
    )
    add_check(
        checks,
        "required_log_fields_declared",
        log_fields_ok,
        "method, policy_or_config_hash, predicted_seam_risk, decision, and failure_diagnosis are required for every work order",
    )
    add_check(
        checks,
        "strict_commands_cover_adapter_rollout_pairing_and_evidence",
        all(
            fragment in command_text
            for fragment in (
                "validate_external_adapters.py --strict",
                "validate_external_rollouts.py",
                "audit_external_pairing_integrity.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        f"commands={packet.get('strict_acceptance_commands')!r}",
    )
    add_check(
        checks,
        "adapter_evidence_still_missing",
        adapter_evidence.get("passed") is not True and packet.get("adapter_evidence_state", {}).get("strict_adapter_audit_passed") is False,
        f"adapter_evidence_passed={adapter_evidence.get('passed')!r}",
    )
    add_check(
        checks,
        "no_real_implementation_files_created",
        not (EXTERNAL / "implementations").exists(),
        "external_validation/implementations is intentionally absent until a real operator supplies implementations",
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
        "method_implementation_packet_ready": passed,
        "strict_adapter_evidence_ready": False,
        "source_packet": rel(PACKET_JSON),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Method Implementation Packet",
        "",
        "Not evidence: `true`.",
        f"Non-oracle method work orders: `{packet['non_oracle_method_count']}`.",
        f"Strict adapter evidence ready: `{str(packet['strict_adapter_evidence_ready']).lower()}`.",
        "",
        "This packet converts the missing independent baseline layer into concrete implementation work orders. It does not provide real implementations, checkpoints, configs, logs, videos, or manifest evidence.",
        "",
        "## Forbidden Evidence Shortcuts",
        "",
    ]
    for item in packet["forbidden_evidence_shortcuts"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Work Orders", ""])
    for order in packet["work_orders"]:
        lines.extend(
            [
                f"### `{order['method']}`",
                "",
                f"- Role: {order['role']}",
                f"- Spec: `{order['spec_file']}`",
                f"- Required entrypoint: `{order['required_entrypoint']}`",
                f"- Target adapter directory: `{order['target_adapter_dir']}`",
                f"- Suggested real implementation path: `{order['suggested_real_implementation_path']}`",
                f"- Evidence status: `{order['evidence_status']}`",
                "- Required artifact fields: " + ", ".join(f"`{field}`" for field in order["required_artifact_fields"]),
                "- Required log fields: " + ", ".join(f"`{field}`" for field in order["required_log_fields"]),
                "",
                "Forbidden advantages:",
            ]
        )
        for item in order["forbidden_advantages"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["## Strict Acceptance Commands", ""])
    for command in packet["strict_acceptance_commands"]:
        lines.append(f"- `{command}`")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Method Implementation Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Method implementation packet ready: `{str(audit['method_implementation_packet_ready']).lower()}`.",
        f"Strict adapter evidence ready: `{str(audit['strict_adapter_evidence_ready']).lower()}`.",
        "",
        "This audit checks that every missing non-oracle method has a concrete implementation work order while strict manifest-declared adapter evidence remains missing.",
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
    specs = load_specs()
    log_schema = read_json(EXTERNAL / "log_schema_v1.json")
    baseline_audit = read_json(RESULTS / "external_baseline_contract_audit.json")
    adapter_evidence = read_json(RESULTS / "external_adapter_contract_evidence_audit.json")
    work_orders = build_work_orders(specs, log_schema)
    write_work_orders_csv(work_orders)
    packet = build_packet(specs, work_orders, baseline_audit, adapter_evidence)
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_packet_md(packet)
    audit = audit_packet(packet, specs, baseline_audit, adapter_evidence)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External method implementation packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"work_orders={len(work_orders)}; not_evidence=true"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

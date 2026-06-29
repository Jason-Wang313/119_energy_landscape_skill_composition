from __future__ import annotations

import csv
import hashlib
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
REFERENCE_PROVENANCE_CSV = EXTERNAL / "method_reference_provenance.csv"
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
    "implementation_provenance",
    "adapter_path",
    "manifest_method_entry",
    "policy_or_config_hash_in_logs",
]
MANIFEST_METHOD_ENTRY_FIELDS = [
    "name",
    "implementation",
    "checkpoint_or_config_path",
    "checkpoint_or_config_hash",
    "implementation_provenance",
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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


def provenance_template(method: str) -> dict[str, Any]:
    if method == "barrier_certified_energy_composer_v5":
        evidence_role = "paper_method_under_test"
        uses_proposed_method_code = True
    elif method == "proposed_energy_landscape_composer_v4_1":
        evidence_role = "paper_predecessor_method"
        uses_proposed_method_code = True
    else:
        evidence_role = "independent_non_oracle_method"
        uses_proposed_method_code = False
    return {
        "evidence_role": evidence_role,
        "implementation_origin": "<operator/lab/repository source for this implementation>",
        "independent_operator_or_lab": "<independent operator or lab name>",
        "operator_signoff_id": "<signoff id or dated note>",
        "same_skill_library": True,
        "same_observation_interface": True,
        "same_compute_budget": True,
        "policy_or_config_hash_locked": True,
        "oracle_access": False,
        "uses_scaffold_template": False,
        "uses_reference_adapter": False,
        "uses_eval_outcome_tuning": False,
        "uses_unblinded_method_identity_during_collection": False,
        "uses_proposed_method_code": uses_proposed_method_code,
    }


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
                "manifest_method_entry_template": {
                    "name": method,
                    "implementation": f"external_validation/implementations/{method}/adapter.py",
                    "checkpoint_or_config_path": f"external_validation/implementations/{method}/config_or_checkpoint.json",
                    "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
                    "implementation_provenance": provenance_template(method),
                },
                "evidence_status": "missing_manifest_declared_implementation",
                "independent_implementation_required": True,
                "scaffold_allowed_as_evidence": False,
                "reference_adapter_allowed_as_evidence": False,
                "policy_or_config_hash_in_logs_required": True,
                "allowed_inputs": spec.get("allowed_inputs", []),
                "forbidden_advantages": spec.get("forbidden_advantages", []),
                "required_artifact_fields": REQUIRED_ARTIFACT_FIELDS,
                "required_log_fields": required_log_fields,
                "acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
                "operator_notes": [
                    "replace scaffold/reference code only with a real implementation or wrapper owned by the external validation operator",
                    "fill implementation_provenance with independent operator/lab signoff, no oracle access, no scaffold/reference adapter use, no outcome tuning, and matched skill/observation/compute conditions",
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


def collect_reference_adapter_provenance(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    common_adapter = EXTERNAL / "baselines" / "common_reference_adapter.py"
    common_hash = sha256_file(common_adapter) if common_adapter.exists() else ""
    records: list[dict[str, Any]] = []
    for spec in non_oracle_specs(specs):
        method = str(spec["method"])
        adapter = EXTERNAL / "baselines" / method / "adapter.py"
        metadata_path = EXTERNAL / "baselines" / method / "reference_adapter_metadata.json"
        metadata = read_json(metadata_path) if metadata_path.exists() else {}
        adapter_hash = sha256_file(adapter) if adapter.exists() else ""
        records.append(
            {
                "method": method,
                "role": spec.get("role", ""),
                "spec_file": spec.get("_path", ""),
                "adapter_path": rel(adapter),
                "adapter_sha256": adapter_hash,
                "metadata_path": rel(metadata_path),
                "metadata_sha256": sha256_file(metadata_path) if metadata_path.exists() else "",
                "common_adapter_path": rel(common_adapter),
                "common_adapter_sha256": common_hash,
                "reference_policy_hash": stable_hash(f"paper119_reference_adapter:{method}:v1"),
                "evidence_status": metadata.get("evidence_status", "missing_reference_adapter_metadata"),
                "oracle_boundary": metadata.get("oracle_boundary", ""),
                "reference_implementation": metadata.get("reference_implementation") is True,
                "strict_evidence_ready": False,
                "reference_adapter_allowed_as_evidence": False,
                "manifest_declaration_stub": {
                    "name": method,
                    "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
                    "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
                    "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
                    "implementation_provenance": provenance_template(method),
                    "interface_reference_adapter": rel(adapter),
                    "interface_reference_adapter_sha256": adapter_hash,
                },
            }
        )
    return records


def write_reference_provenance_csv(records: list[dict[str, Any]]) -> None:
    fieldnames = [
        "method",
        "role",
        "spec_file",
        "adapter_path",
        "adapter_sha256",
        "metadata_path",
        "metadata_sha256",
        "common_adapter_path",
        "common_adapter_sha256",
        "reference_policy_hash",
        "evidence_status",
        "oracle_boundary",
        "reference_implementation",
        "strict_evidence_ready",
        "reference_adapter_allowed_as_evidence",
    ]
    with REFERENCE_PROVENANCE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key, "") for key in fieldnames})


def write_work_orders_csv(orders: list[dict[str, Any]]) -> None:
    fieldnames = [
        "method",
        "role",
        "spec_file",
        "required_entrypoint",
        "target_adapter_dir",
        "suggested_real_implementation_path",
        "manifest_implementation_key",
        "independent_implementation_required",
        "scaffold_allowed_as_evidence",
        "reference_adapter_allowed_as_evidence",
        "policy_or_config_hash_in_logs_required",
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
    reference_provenance: list[dict[str, Any]],
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
            rel(RESULTS / "external_reference_adapter_audit.json"),
            rel(EXTERNAL / "log_schema_v1.json"),
        ],
        "non_oracle_method_count": len(work_orders),
        "oracle_method": ORACLE_METHOD,
        "oracle_role": "post_hoc_upper_bound_only_not_an_implementation_work_order",
        "missing_implementations": missing,
        "work_orders": work_orders,
        "reference_adapter_policy": (
            "Reference adapters are executable interface/provenance artifacts only. "
            "They are not independent implementation evidence; the strict reference-adapter rejection gate "
            "prevents them from satisfying strict adapter evidence "
            "without operator-supplied implementations, configs/checkpoints, manifest entries, raw logs, "
            "and matching policy_or_config_hash values."
        ),
        "reference_adapter_provenance_count": len(reference_provenance),
        "reference_adapter_provenance_csv": rel(REFERENCE_PROVENANCE_CSV),
        "reference_adapter_provenance": reference_provenance,
        "strict_acceptance_commands": STRICT_ACCEPTANCE_COMMANDS,
        "forbidden_evidence_shortcuts": [
            "using scaffold adapters as manifest-declared implementations",
            "using reference adapters as rollout evidence without real source/config/checkpoint hashes",
            "using reference adapters to bypass the strict reference-adapter rejection gate",
            "declaring only a subset of non-oracle methods in the strict adapter manifest",
            "using policy_or_config_hash values in JSONL logs that do not match manifest-declared hashes",
            "omitting implementation_provenance or using provenance that permits oracle access, scaffold/reference adapters, proposed-code leakage for independent baselines, or post-outcome tuning",
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
    reference_provenance = packet.get("reference_adapter_provenance", []) or []
    method_names = {order.get("method") for order in work_orders}
    reference_methods = {record.get("method") for record in reference_provenance}
    non_oracle_method_names = {str(spec.get("method")) for spec in non_oracle_specs(specs)}
    baseline_missing = set(baseline_audit.get("missing_implementations", []) or [])
    command_text = "\n".join(packet.get("strict_acceptance_commands", []) or [])
    artifact_fields_ok = all(set(REQUIRED_ARTIFACT_FIELDS).issubset(set(order.get("required_artifact_fields", []) or [])) for order in work_orders)
    log_fields_ok = all(
        {"method", "policy_or_config_hash", "predicted_seam_risk", "decision", "failure_diagnosis"}.issubset(set(order.get("required_log_fields", []) or []))
        for order in work_orders
    )
    manifest_template_ok = all(
        set(MANIFEST_METHOD_ENTRY_FIELDS).issubset(set((order.get("manifest_method_entry_template") or {}).keys()))
        and order.get("manifest_method_entry_template", {}).get("name") == order.get("method")
        and "SHA256" in str(order.get("manifest_method_entry_template", {}).get("checkpoint_or_config_hash", ""))
        for order in work_orders
    )
    provenance_template_ok = all(
        isinstance((order.get("manifest_method_entry_template") or {}).get("implementation_provenance"), dict)
        and (order.get("manifest_method_entry_template", {}).get("implementation_provenance") or {}).get("policy_or_config_hash_locked") is True
        and (order.get("manifest_method_entry_template", {}).get("implementation_provenance") or {}).get("oracle_access") is False
        and (order.get("manifest_method_entry_template", {}).get("implementation_provenance") or {}).get("uses_scaffold_template") is False
        and (order.get("manifest_method_entry_template", {}).get("implementation_provenance") or {}).get("uses_reference_adapter") is False
        and (order.get("manifest_method_entry_template", {}).get("implementation_provenance") or {}).get("uses_eval_outcome_tuning") is False
        for order in work_orders
    )
    scaffold_policy_ok = all(
        order.get("independent_implementation_required") is True
        and order.get("scaffold_allowed_as_evidence") is False
        and order.get("reference_adapter_allowed_as_evidence") is False
        for order in work_orders
    )
    log_hash_policy_ok = all(order.get("policy_or_config_hash_in_logs_required") is True for order in work_orders)
    hex_hash_fields = ("adapter_sha256", "metadata_sha256", "common_adapter_sha256", "reference_policy_hash")
    reference_hashes_ok = all(
        all(len(str(record.get(field, ""))) == 64 for field in hex_hash_fields)
        for record in reference_provenance
    )
    reference_non_evidence_ok = all(
        record.get("evidence_status") == "implementation_only_not_rollout_evidence"
        and record.get("reference_implementation") is True
        and record.get("strict_evidence_ready") is False
        and record.get("reference_adapter_allowed_as_evidence") is False
        and record.get("oracle_boundary") == "non_oracle_reference_adapter"
        for record in reference_provenance
    )
    manifest_stubs_ok = all(
        str((record.get("manifest_declaration_stub") or {}).get("implementation", "")).startswith("<operator-supplied independent")
        and "SHA256" in str((record.get("manifest_declaration_stub") or {}).get("checkpoint_or_config_hash", ""))
        and isinstance((record.get("manifest_declaration_stub") or {}).get("implementation_provenance"), dict)
        and str((record.get("manifest_declaration_stub") or {}).get("interface_reference_adapter", "")).startswith("external_validation/baselines/")
        for record in reference_provenance
    )
    common_hashes = {record.get("common_adapter_sha256") for record in reference_provenance}
    reference_policy_hashes_ok = all(
        record.get("reference_policy_hash") == stable_hash(f"paper119_reference_adapter:{record.get('method')}:v1")
        for record in reference_provenance
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
        "manifest_entry_templates_cover_required_hash_fields",
        manifest_template_ok,
        f"fields={MANIFEST_METHOD_ENTRY_FIELDS}",
    )
    add_check(
        checks,
        "manifest_entry_templates_require_independent_provenance",
        provenance_template_ok,
        "implementation_provenance requires operator/lab signoff, no oracle access, no scaffold/reference use, no outcome tuning, and locked hashes",
    )
    add_check(
        checks,
        "work_orders_forbid_scaffolds_and_reference_adapters",
        scaffold_policy_ok,
        "every non-oracle method requires independent implementation evidence and forbids scaffold/reference adapters as evidence",
    )
    add_check(
        checks,
        "policy_or_config_hash_in_logs_required",
        log_hash_policy_ok,
        "every work order requires JSONL policy_or_config_hash to match manifest-declared method provenance",
    )
    add_check(
        checks,
        "reference_adapter_provenance_covers_non_oracle_methods",
        len(reference_provenance) >= 11 and non_oracle_method_names.issubset(reference_methods),
        f"reference_records={len(reference_provenance)}, missing={sorted(non_oracle_method_names - reference_methods)}",
    )
    add_check(
        checks,
        "reference_adapter_hashes_recorded",
        reference_hashes_ok,
        f"hash_fields={hex_hash_fields}",
    )
    add_check(
        checks,
        "reference_adapters_marked_non_evidence",
        reference_non_evidence_ok,
        "all reference adapters are implementation-only and forbidden as strict evidence",
    )
    add_check(
        checks,
        "reference_manifest_stubs_not_strict_ready",
        manifest_stubs_ok,
        "manifest stubs require operator-supplied independent implementations and hashes",
    )
    add_check(
        checks,
        "common_reference_adapter_hash_shared",
        len(common_hashes) == 1
        and all(record.get("common_adapter_path") == "external_validation/baselines/common_reference_adapter.py" for record in reference_provenance),
        f"common_hash_count={len(common_hashes)}",
    )
    add_check(
        checks,
        "reference_policy_hashes_match_adapter_formula",
        reference_policy_hashes_ok,
        "reference_policy_hash=sha256(paper119_reference_adapter:<method>:v1)",
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
        PACKET_JSON.exists() and PACKET_MD.exists() and WORK_ORDERS_CSV.exists() and REFERENCE_PROVENANCE_CSV.exists(),
        (
            f"packet_json={PACKET_JSON.exists()}, packet_md={PACKET_MD.exists()}, "
            f"work_orders_csv={WORK_ORDERS_CSV.exists()}, reference_provenance_csv={REFERENCE_PROVENANCE_CSV.exists()}"
        ),
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
        f"Reference adapter provenance records: `{packet['reference_adapter_provenance_count']}`.",
        f"Strict adapter evidence ready: `{str(packet['strict_adapter_evidence_ready']).lower()}`.",
        "",
        "This packet converts the missing independent baseline layer into concrete implementation work orders. It does not provide real implementations, checkpoints, configs, logs, videos, or manifest evidence.",
        "",
        "## Reference Adapter Provenance (Non-Evidence)",
        "",
        "The current reference adapters are executable interface artifacts. They make the proposed adapter API inspectable, but they are not independent rollout evidence, cannot replace operator-supplied implementations, and are blocked by the strict reference-adapter rejection gate.",
        "",
    ]
    for record in packet["reference_adapter_provenance"]:
        lines.extend(
            [
                f"### `{record['method']}` reference adapter",
                "",
                f"- Adapter: `{record['adapter_path']}`",
                f"- Adapter SHA256: `{record['adapter_sha256']}`",
                f"- Metadata: `{record['metadata_path']}`",
                f"- Metadata SHA256: `{record['metadata_sha256']}`",
                f"- Shared adapter SHA256: `{record['common_adapter_sha256']}`",
                f"- Reference policy hash: `{record['reference_policy_hash']}`",
                f"- Evidence status: `{record['evidence_status']}`",
                "- Manifest declaration stub:",
                "```json",
                json.dumps(record["manifest_declaration_stub"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend([
        "## Forbidden Evidence Shortcuts",
        "",
    ])
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
                f"- Independent implementation required: `{str(order['independent_implementation_required']).lower()}`",
                f"- Scaffold allowed as evidence: `{str(order['scaffold_allowed_as_evidence']).lower()}`",
                f"- Reference adapter allowed as evidence: `{str(order['reference_adapter_allowed_as_evidence']).lower()}`",
                f"- Policy/config hash required in logs: `{str(order['policy_or_config_hash_in_logs_required']).lower()}`",
                "- Required artifact fields: " + ", ".join(f"`{field}`" for field in order["required_artifact_fields"]),
                "- Required log fields: " + ", ".join(f"`{field}`" for field in order["required_log_fields"]),
                "- Manifest method entry template:",
                "```json",
                json.dumps(order["manifest_method_entry_template"], indent=2, sort_keys=True),
                "```",
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
    reference_provenance = collect_reference_adapter_provenance(specs)
    write_work_orders_csv(work_orders)
    write_reference_provenance_csv(reference_provenance)
    packet = build_packet(specs, work_orders, reference_provenance, baseline_audit, adapter_evidence)
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
    print(f"Wrote {REFERENCE_PROVENANCE_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

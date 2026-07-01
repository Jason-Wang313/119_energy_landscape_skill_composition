from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_backend_integration_packet as backend_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_backend_integration_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_backend_integration_packet_self_test.md"
VERSION = "external_backend_integration_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "backend_integration_packet.json",
    REAL_EXTERNAL / "backend_integration_packet.md",
    REAL_EXTERNAL / "backend_integration_work_orders.csv",
    REAL_RESULTS / "external_backend_integration_audit.json",
    REAL_RESULTS / "external_backend_integration_audit.md",
]

INPUT_FILES = [
    REAL_EXTERNAL / "platform_onboarding_packet.json",
    REAL_RESULTS / "external_backend_contract_audit.json",
    REAL_RESULTS / "external_collection_readiness_audit.json",
]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in REAL_OUTPUTS}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing backend-integration self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_backend_packet(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    runner = external / "runner"
    results = root / "results"
    old = {
        "ROOT": backend_packet.ROOT,
        "EXTERNAL": backend_packet.EXTERNAL,
        "RUNNER": backend_packet.RUNNER,
        "RESULTS": backend_packet.RESULTS,
        "PACKET_JSON": backend_packet.PACKET_JSON,
        "PACKET_MD": backend_packet.PACKET_MD,
        "WORK_ORDERS_CSV": backend_packet.WORK_ORDERS_CSV,
        "AUDIT_JSON": backend_packet.AUDIT_JSON,
        "AUDIT_MD": backend_packet.AUDIT_MD,
    }
    backend_packet.ROOT = root
    backend_packet.EXTERNAL = external
    backend_packet.RUNNER = runner
    backend_packet.RESULTS = results
    backend_packet.PACKET_JSON = external / "backend_integration_packet.json"
    backend_packet.PACKET_MD = external / "backend_integration_packet.md"
    backend_packet.WORK_ORDERS_CSV = external / "backend_integration_work_orders.csv"
    backend_packet.AUDIT_JSON = results / "external_backend_integration_audit.json"
    backend_packet.AUDIT_MD = results / "external_backend_integration_audit.md"
    return old


def restore_backend_packet(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(backend_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_backend_packet(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = backend_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_backend_packet(old)
    packet_payload = read_json(root / "external_validation" / "backend_integration_packet.json")
    audit_payload = read_json(root / "results" / "external_backend_integration_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "external_validation" / "platform_onboarding_packet.json"),
        read_json(root / "results" / "external_backend_contract_audit.json"),
        read_json(root / "results" / "external_collection_readiness_audit.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "backend_integration_packet.json")
    mutator(root, packet_payload)
    old = patch_backend_packet(root)
    try:
        onboarding, backend_contract, collection = load_audit_inputs(root)
        return backend_packet.audit_packet(packet_payload, onboarding, backend_contract, collection)
    finally:
        restore_backend_packet(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_backend_integration_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, packet_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, packet_payload, audit_payload
        return status, packet_payload, run_audit_case(root, mutator)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_work_order(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"] = [
        order for order in payload.get("work_orders", []) or [] if order.get("id") != "create_non_template_backend_module"
    ]


def empty_work_order_artifacts(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"][0]["required_artifacts"] = []
    payload["work_orders"][0]["acceptance_commands"] = []


def promote_packet_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_backend_ready"] = True
    payload["strict_evidence_ready"] = True


def break_route_independence(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "platform_onboarding_packet.json"
    onboarding = read_json(path)
    onboarding["primary_route_independent_of_haonan"] = False
    write_json(path, onboarding)


def promote_actual_backend(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_backend_contract_audit.json"
    contract = read_json(path)
    contract["actual_backend_ready"] = True
    write_json(path, contract)


def remove_required_hook(_root: Path, payload: dict[str, Any]) -> None:
    payload["required_backend_hooks"] = [
        hook for hook in payload.get("required_backend_hooks", []) or [] if hook != "policy_or_config_hash"
    ]


def remove_provenance_field(_root: Path, payload: dict[str, Any]) -> None:
    payload["required_platform_provenance_fields"] = [
        field
        for field in payload.get("required_platform_provenance_fields", []) or []
        if field != "backend_module_sha256"
    ]


def shrink_task_budget(_root: Path, payload: dict[str, Any]) -> None:
    payload["planned_tasks"] = payload.get("planned_tasks", [])[:1]
    payload["planned_records"] = 120


def drop_strict_backend_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_acceptance_commands"] = [
        command
        for command in payload.get("strict_acceptance_commands", []) or []
        if "audit_external_backend_contract.py" not in command
    ]


def promote_collection_ready(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_collection_readiness_audit.json"
    collection = read_json(path)
    collection["collection_ready"] = True
    collection["blocking_missing"] = [
        blocker for blocker in collection.get("blocking_missing", []) or [] if "backend_module_ready" not in str(blocker)
    ]
    write_json(path, collection)


def write_real_backend_file(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "runner" / "backends" / "synthetic_backend.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# synthetic self-test only\n", encoding="utf-8")


def delete_packet_file(root: Path, _payload: dict[str, Any]) -> None:
    (root / "external_validation" / "backend_integration_work_orders.csv").unlink()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Backend Integration Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict backend ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing work orders rejected: `{str(payload['missing_work_orders_rejected']).lower()}`.",
        f"Work-order artifact/command drift rejected: `{str(payload['work_order_artifact_command_drift_rejected']).lower()}`.",
        f"Premature backend/evidence promotion rejected: `{str(payload['premature_backend_evidence_promotion_rejected']).lower()}`.",
        f"Route independence drift rejected: `{str(payload['route_independence_drift_rejected']).lower()}`.",
        f"Actual-backend promotion rejected: `{str(payload['actual_backend_promotion_rejected']).lower()}`.",
        f"Hook contract drift rejected: `{str(payload['hook_contract_drift_rejected']).lower()}`.",
        f"Provenance field drift rejected: `{str(payload['provenance_field_drift_rejected']).lower()}`.",
        f"Task-budget shrink rejected: `{str(payload['task_budget_shrink_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Collection-ready promotion rejected: `{str(payload['collection_ready_promotion_rejected']).lower()}`.",
        f"Real backend file write rejected: `{str(payload['real_backend_file_write_rejected']).lower()}`.",
        f"Packet file deletion rejected: `{str(payload['packet_file_deletion_rejected']).lower()}`.",
        f"Real backend-integration outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the backend integration packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing or vague backend work orders, premature backend/evidence readiness, Haonan-dependence drift, false actual-backend readiness, missing hooks/provenance, shrunken task budgets, strict-command drift, premature collection readiness, accidental real backend files, and missing packet files without touching real backend-integration outputs.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    REAL_RESULTS.mkdir(exist_ok=True)
    TMP_ROOT.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []
    real_hashes_before = real_output_hashes()

    status, packet_payload, audit_payload = run_case()
    temporary_packet_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("backend_integration_packet_ready") is True
        and audit_payload.get("strict_backend_ready") is False
        and audit_payload.get("strict_evidence_ready") is False
        and int(packet_payload.get("planned_records", 0) or 0) >= 1440
        and len(packet_payload.get("work_orders", []) or []) >= 5
        and check_named(audit_payload, "work_orders_cover_backend_to_manifest_path") is True
        and check_named(audit_payload, "work_orders_are_actionable_and_artifact_bound") is True
        and check_named(audit_payload, "no_real_backend_files_created") is True
    )
    add_check(
        checks,
        "temporary_backend_integration_packet_ready_but_non_evidence",
        temporary_packet_ready,
        (
            f"status={status}, passed={audit_payload.get('passed')!r}, "
            f"records={packet_payload.get('planned_records')!r}, "
            f"orders={len(packet_payload.get('work_orders', []) or [])}"
        ),
    )

    _, _, missing_orders = run_case(remove_work_order)
    missing_work_orders_rejected = (
        missing_orders.get("passed") is False
        and check_named(missing_orders, "work_orders_cover_backend_to_manifest_path") is False
    )
    add_check(checks, "missing_work_orders_rejected", missing_work_orders_rejected, f"work_order_check={check_named(missing_orders, 'work_orders_cover_backend_to_manifest_path')}")

    _, _, vague_orders = run_case(empty_work_order_artifacts)
    work_order_artifact_command_drift_rejected = (
        vague_orders.get("passed") is False
        and check_named(vague_orders, "work_orders_are_actionable_and_artifact_bound") is False
    )
    add_check(checks, "work_order_artifact_command_drift_rejected", work_order_artifact_command_drift_rejected, f"actionable_check={check_named(vague_orders, 'work_orders_are_actionable_and_artifact_bound')}")

    _, _, promoted_packet = run_case(promote_packet_to_evidence)
    premature_backend_evidence_promotion_rejected = (
        promoted_packet.get("passed") is False
        and check_named(promoted_packet, "packet_is_non_evidence_and_fail_closed") is False
    )
    add_check(checks, "premature_backend_evidence_promotion_rejected", premature_backend_evidence_promotion_rejected, f"non_evidence_check={check_named(promoted_packet, 'packet_is_non_evidence_and_fail_closed')}")

    _, _, route_drift = run_case(break_route_independence)
    route_independence_drift_rejected = (
        route_drift.get("passed") is False
        and check_named(route_drift, "primary_route_matches_onboarding") is False
    )
    add_check(checks, "route_independence_drift_rejected", route_independence_drift_rejected, f"route_check={check_named(route_drift, 'primary_route_matches_onboarding')}")

    _, _, backend_drift = run_case(promote_actual_backend)
    actual_backend_promotion_rejected = (
        backend_drift.get("passed") is False
        and check_named(backend_drift, "backend_contract_harness_ready_but_backend_missing") is False
    )
    add_check(checks, "actual_backend_promotion_rejected", actual_backend_promotion_rejected, f"backend_check={check_named(backend_drift, 'backend_contract_harness_ready_but_backend_missing')}")

    _, _, hook_drift = run_case(remove_required_hook)
    hook_contract_drift_rejected = (
        hook_drift.get("passed") is False
        and check_named(hook_drift, "required_hooks_declared") is False
    )
    add_check(checks, "hook_contract_drift_rejected", hook_contract_drift_rejected, f"hook_check={check_named(hook_drift, 'required_hooks_declared')}")

    _, _, provenance_drift = run_case(remove_provenance_field)
    provenance_field_drift_rejected = (
        provenance_drift.get("passed") is False
        and check_named(provenance_drift, "provenance_fields_declared") is False
    )
    add_check(checks, "provenance_field_drift_rejected", provenance_field_drift_rejected, f"provenance_check={check_named(provenance_drift, 'provenance_fields_declared')}")

    _, _, budget_drift = run_case(shrink_task_budget)
    task_budget_shrink_rejected = (
        budget_drift.get("passed") is False
        and check_named(budget_drift, "tasks_and_record_budget_preserved") is False
    )
    add_check(checks, "task_budget_shrink_rejected", task_budget_shrink_rejected, f"budget_check={check_named(budget_drift, 'tasks_and_record_budget_preserved')}")

    _, _, command_drift = run_case(drop_strict_backend_command)
    strict_command_drift_rejected = (
        command_drift.get("passed") is False
        and check_named(command_drift, "strict_commands_cover_backend_config_fidelity_collection_and_evidence") is False
    )
    add_check(checks, "strict_command_drift_rejected", strict_command_drift_rejected, f"command_check={check_named(command_drift, 'strict_commands_cover_backend_config_fidelity_collection_and_evidence')}")

    _, _, collection_drift = run_case(promote_collection_ready)
    collection_ready_promotion_rejected = (
        collection_drift.get("passed") is False
        and check_named(collection_drift, "collection_readiness_still_blocks_backend") is False
    )
    add_check(checks, "collection_ready_promotion_rejected", collection_ready_promotion_rejected, f"collection_check={check_named(collection_drift, 'collection_readiness_still_blocks_backend')}")

    _, _, backend_file_drift = run_case(write_real_backend_file)
    real_backend_file_write_rejected = (
        backend_file_drift.get("passed") is False
        and check_named(backend_file_drift, "no_real_backend_files_created") is False
    )
    add_check(checks, "real_backend_file_write_rejected", real_backend_file_write_rejected, f"backend_file_check={check_named(backend_file_drift, 'no_real_backend_files_created')}")

    _, _, packet_file_drift = run_case(delete_packet_file)
    packet_file_deletion_rejected = (
        packet_file_drift.get("passed") is False
        and check_named(packet_file_drift, "packet_files_written") is False
    )
    add_check(checks, "packet_file_deletion_rejected", packet_file_deletion_rejected, f"packet_file_check={check_named(packet_file_drift, 'packet_files_written')}")

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_backend_integration_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    check_map = {check["name"]: check["passed"] for check in checks}
    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_backend_ready": False,
        "strict_evidence_ready": False,
        "temporary_packet_ready": check_map.get("temporary_backend_integration_packet_ready_but_non_evidence") is True,
        "missing_work_orders_rejected": check_map.get("missing_work_orders_rejected") is True,
        "work_order_artifact_command_drift_rejected": check_map.get("work_order_artifact_command_drift_rejected") is True,
        "premature_backend_evidence_promotion_rejected": check_map.get("premature_backend_evidence_promotion_rejected") is True,
        "route_independence_drift_rejected": check_map.get("route_independence_drift_rejected") is True,
        "actual_backend_promotion_rejected": check_map.get("actual_backend_promotion_rejected") is True,
        "hook_contract_drift_rejected": check_map.get("hook_contract_drift_rejected") is True,
        "provenance_field_drift_rejected": check_map.get("provenance_field_drift_rejected") is True,
        "task_budget_shrink_rejected": check_map.get("task_budget_shrink_rejected") is True,
        "strict_command_drift_rejected": check_map.get("strict_command_drift_rejected") is True,
        "collection_ready_promotion_rejected": check_map.get("collection_ready_promotion_rejected") is True,
        "real_backend_file_write_rejected": check_map.get("real_backend_file_write_rejected") is True,
        "packet_file_deletion_rejected": check_map.get("packet_file_deletion_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External backend integration packet self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

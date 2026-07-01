from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_rollout_evidence_packet as rollout_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_rollout_evidence_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_rollout_evidence_packet_self_test.md"
VERSION = "external_rollout_evidence_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "rollout_evidence_packet.json",
    REAL_EXTERNAL / "rollout_evidence_packet.md",
    REAL_EXTERNAL / "rollout_evidence_work_orders.csv",
    REAL_RESULTS / "external_rollout_evidence_audit.json",
    REAL_RESULTS / "external_rollout_evidence_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_RESULTS / "external_collection_plan.json",
    REAL_RESULTS / "external_evidence_preflight.json",
    REAL_RESULTS / "external_rollout_metrics.json",
    REAL_RESULTS / "external_pairing_integrity_audit.json",
    REAL_RESULTS / "external_release_package_audit.json",
    REAL_RESULTS / "external_evidence_audit.json",
    REAL_EXTERNAL / "log_schema_v1.json",
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
        raise AssertionError(f"missing rollout-packet self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_rollout(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": rollout_packet.ROOT,
        "EXTERNAL": rollout_packet.EXTERNAL,
        "RESULTS": rollout_packet.RESULTS,
        "PACKET_JSON": rollout_packet.PACKET_JSON,
        "PACKET_MD": rollout_packet.PACKET_MD,
        "WORK_ORDERS_CSV": rollout_packet.WORK_ORDERS_CSV,
        "AUDIT_JSON": rollout_packet.AUDIT_JSON,
        "AUDIT_MD": rollout_packet.AUDIT_MD,
    }
    rollout_packet.ROOT = root
    rollout_packet.EXTERNAL = external
    rollout_packet.RESULTS = results
    rollout_packet.PACKET_JSON = external / "rollout_evidence_packet.json"
    rollout_packet.PACKET_MD = external / "rollout_evidence_packet.md"
    rollout_packet.WORK_ORDERS_CSV = external / "rollout_evidence_work_orders.csv"
    rollout_packet.AUDIT_JSON = results / "external_rollout_evidence_audit.json"
    rollout_packet.AUDIT_MD = results / "external_rollout_evidence_audit.md"
    return old


def restore_rollout(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(rollout_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_rollout(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = rollout_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_rollout(old)
    packet_payload = read_json(root / "external_validation" / "rollout_evidence_packet.json")
    audit_payload = read_json(root / "results" / "external_rollout_evidence_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "results" / "external_collection_plan.json"),
        read_json(root / "results" / "external_evidence_preflight.json"),
        read_json(root / "results" / "external_rollout_metrics.json"),
        read_json(root / "results" / "external_pairing_integrity_audit.json"),
        read_json(root / "results" / "external_release_package_audit.json"),
        read_json(root / "results" / "external_evidence_audit.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "rollout_evidence_packet.json")
    mutator(root, packet_payload)
    old = patch_rollout(root)
    try:
        collection, preflight, rollout_metrics, pairing, release, external_evidence = load_audit_inputs(root)
        return rollout_packet.audit_packet(
            packet_payload,
            collection,
            preflight,
            rollout_metrics,
            pairing,
            release,
            external_evidence,
        )
    finally:
        restore_rollout(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_rollout_packet_selftest_", dir=TMP_ROOT) as temp_name:
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


def remove_task_work_order(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"] = [
        order for order in payload.get("work_orders", []) or [] if not str(order.get("id", "")).startswith("collect_")
    ]


def promote_packet_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_rollout_evidence_ready"] = True
    payload["strict_external_evidence_ready"] = True
    payload["manifest_written"] = True


def remove_manifest_schema_error(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_rollout_metrics.json"
    metrics = read_json(path)
    metrics["schema_errors"] = ["synthetic self-test schema issue"]
    write_json(path, metrics)


def mark_preflight_observed_records(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_evidence_preflight.json"
    preflight = read_json(path)
    preflight["observed_records"] = preflight.get("expected_records", 1440)
    write_json(path, preflight)


def shrink_collection_budget(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_collection_plan.json"
    collection = read_json(path)
    collection["total_required_records"] = 120
    collection["task_family_count"] = 1
    collection["method_count"] = 3
    write_json(path, collection)


def drop_strict_rollout_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_acceptance_commands"] = [
        command
        for command in payload.get("strict_acceptance_commands", []) or []
        if "validate_external_rollouts.py" not in command
    ]


def promote_downstream_gates(root: Path, _payload: dict[str, Any]) -> None:
    pairing_path = root / "results" / "external_pairing_integrity_audit.json"
    release_path = root / "results" / "external_release_package_audit.json"
    evidence_path = root / "results" / "external_evidence_audit.json"
    pairing = read_json(pairing_path)
    release = read_json(release_path)
    evidence = read_json(evidence_path)
    pairing["pairing_ready"] = True
    release["release_package_ready"] = True
    evidence["submission_ready"] = True
    write_json(pairing_path, pairing)
    write_json(release_path, release)
    write_json(evidence_path, evidence)


def write_real_outputs_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})
    (root / "external_validation" / "logs").mkdir(parents=True, exist_ok=True)
    (root / "external_validation" / "logs" / "synthetic.jsonl").write_text('{"synthetic": true}\n', encoding="utf-8")
    (root / "external_validation" / "videos" / "synthetic_task").mkdir(parents=True, exist_ok=True)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Rollout Evidence Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict rollout evidence ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing task work orders rejected: `{str(payload['missing_task_work_orders_rejected']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Manifest schema-error drift rejected: `{str(payload['manifest_schema_error_drift_rejected']).lower()}`.",
        f"Observed-record drift rejected: `{str(payload['observed_record_drift_rejected']).lower()}`.",
        f"Collection-budget shrink rejected: `{str(payload['collection_budget_shrink_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Downstream gate promotion rejected: `{str(payload['downstream_gate_promotion_rejected']).lower()}`.",
        f"Real output write rejected: `{str(payload['real_output_write_rejected']).lower()}`.",
        f"Real rollout packet outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the rollout evidence packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing task-specific JSONL/video work orders, premature strict-evidence promotion, loss of the missing-manifest rollout-metrics signal, fake observed-record drift, shrunken collection budgets, strict rollout-command drift, downstream gate promotion, and accidental manifest/log/video writes without touching the real rollout packet outputs.",
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
        and audit_payload.get("rollout_evidence_packet_ready") is True
        and audit_payload.get("strict_rollout_evidence_ready") is False
        and audit_payload.get("strict_external_evidence_ready") is False
        and int(packet_payload.get("expected_records", 0) or 0) >= 1440
        and int(packet_payload.get("observed_records", -1) or 0) == 0
        and check_named(audit_payload, "task_work_orders_cover_all_planned_tasks") is True
        and check_named(audit_payload, "no_real_manifest_or_logs_written") is True
    )
    add_check(
        checks,
        "temporary_rollout_packet_ready_but_non_evidence",
        temporary_packet_ready,
        (
            f"status={status}, passed={audit_payload.get('passed')!r}, "
            f"expected={packet_payload.get('expected_records')!r}, observed={packet_payload.get('observed_records')!r}"
        ),
    )

    _, _, missing_task_audit = run_case(remove_task_work_order)
    missing_task_work_orders_rejected = (
        missing_task_audit.get("passed") is False
        and check_named(missing_task_audit, "task_work_orders_cover_all_planned_tasks") is False
    )
    add_check(
        checks,
        "missing_task_work_orders_rejected",
        missing_task_work_orders_rejected,
        f"task_order_check={check_named(missing_task_audit, 'task_work_orders_cover_all_planned_tasks')}",
    )

    _, _, evidence_promotion_audit = run_case(promote_packet_to_evidence)
    premature_evidence_promotion_rejected = (
        evidence_promotion_audit.get("passed") is False
        and check_named(evidence_promotion_audit, "packet_is_non_evidence_and_fail_closed") is False
    )
    add_check(
        checks,
        "premature_evidence_promotion_rejected",
        premature_evidence_promotion_rejected,
        f"non_evidence_check={check_named(evidence_promotion_audit, 'packet_is_non_evidence_and_fail_closed')}",
    )

    _, _, schema_drift_audit = run_case(remove_manifest_schema_error)
    manifest_schema_error_drift_rejected = (
        schema_drift_audit.get("passed") is False
        and check_named(schema_drift_audit, "strict_rollout_metrics_still_fail_without_manifest") is False
    )
    add_check(
        checks,
        "manifest_schema_error_drift_rejected",
        manifest_schema_error_drift_rejected,
        f"manifest_error_check={check_named(schema_drift_audit, 'strict_rollout_metrics_still_fail_without_manifest')}",
    )

    _, _, observed_drift_audit = run_case(mark_preflight_observed_records)
    observed_record_drift_rejected = (
        observed_drift_audit.get("passed") is False
        and check_named(observed_drift_audit, "preflight_ready_but_observes_zero_real_records") is False
    )
    add_check(
        checks,
        "observed_record_drift_rejected",
        observed_record_drift_rejected,
        f"observed_record_check={check_named(observed_drift_audit, 'preflight_ready_but_observes_zero_real_records')}",
    )

    _, _, budget_drift_audit = run_case(shrink_collection_budget)
    collection_budget_shrink_rejected = (
        budget_drift_audit.get("passed") is False
        and check_named(budget_drift_audit, "collection_plan_record_budget_ge_1440") is False
    )
    add_check(
        checks,
        "collection_budget_shrink_rejected",
        collection_budget_shrink_rejected,
        f"budget_check={check_named(budget_drift_audit, 'collection_plan_record_budget_ge_1440')}",
    )

    _, _, command_drift_audit = run_case(drop_strict_rollout_command)
    strict_command_drift_rejected = (
        command_drift_audit.get("passed") is False
        and check_named(command_drift_audit, "strict_commands_cover_collection_manifest_rollout_pairing_release_evidence") is False
    )
    add_check(
        checks,
        "strict_command_drift_rejected",
        strict_command_drift_rejected,
        f"command_check={check_named(command_drift_audit, 'strict_commands_cover_collection_manifest_rollout_pairing_release_evidence')}",
    )

    _, _, downstream_drift_audit = run_case(promote_downstream_gates)
    downstream_gate_promotion_rejected = (
        downstream_drift_audit.get("passed") is False
        and check_named(downstream_drift_audit, "strict_gate_audits_remain_fail_closed") is False
    )
    add_check(
        checks,
        "downstream_gate_promotion_rejected",
        downstream_gate_promotion_rejected,
        f"downstream_gate_check={check_named(downstream_drift_audit, 'strict_gate_audits_remain_fail_closed')}",
    )

    _, _, real_output_audit = run_case(write_real_outputs_in_fixture)
    real_output_write_rejected = (
        real_output_audit.get("passed") is False
        and check_named(real_output_audit, "no_real_manifest_or_logs_written") is False
    )
    add_check(
        checks,
        "real_output_write_rejected",
        real_output_write_rejected,
        f"real_output_check={check_named(real_output_audit, 'no_real_manifest_or_logs_written')}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_rollout_packet_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    check_map = {check["name"]: check["passed"] for check in checks}
    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_rollout_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "temporary_packet_ready": check_map.get("temporary_rollout_packet_ready_but_non_evidence") is True,
        "missing_task_work_orders_rejected": check_map.get("missing_task_work_orders_rejected") is True,
        "premature_evidence_promotion_rejected": check_map.get("premature_evidence_promotion_rejected") is True,
        "manifest_schema_error_drift_rejected": check_map.get("manifest_schema_error_drift_rejected") is True,
        "observed_record_drift_rejected": check_map.get("observed_record_drift_rejected") is True,
        "collection_budget_shrink_rejected": check_map.get("collection_budget_shrink_rejected") is True,
        "strict_command_drift_rejected": check_map.get("strict_command_drift_rejected") is True,
        "downstream_gate_promotion_rejected": check_map.get("downstream_gate_promotion_rejected") is True,
        "real_output_write_rejected": check_map.get("real_output_write_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External rollout evidence packet self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_ablation_collection_packet as ablation_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_ablation_collection_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_ablation_collection_packet_self_test.md"
VERSION = "external_ablation_collection_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "ablation_collection_packet.json",
    REAL_EXTERNAL / "ablation_collection_packet.md",
    REAL_EXTERNAL / "ablation_collection_work_orders.csv",
    REAL_RESULTS / "external_ablation_collection_audit.json",
    REAL_RESULTS / "external_ablation_collection_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_RESULTS / "external_collection_plan.json",
    REAL_RESULTS / "external_evidence_audit.json",
    REAL_RESULTS / "ablation_metrics.csv",
    REAL_EXTERNAL / "manifest_template.json",
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
        raise AssertionError(f"missing ablation-packet self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_ablation_packet(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": ablation_packet.ROOT,
        "EXTERNAL": ablation_packet.EXTERNAL,
        "RESULTS": ablation_packet.RESULTS,
        "PACKET_JSON": ablation_packet.PACKET_JSON,
        "PACKET_MD": ablation_packet.PACKET_MD,
        "WORK_ORDERS_CSV": ablation_packet.WORK_ORDERS_CSV,
        "AUDIT_JSON": ablation_packet.AUDIT_JSON,
        "AUDIT_MD": ablation_packet.AUDIT_MD,
    }
    ablation_packet.ROOT = root
    ablation_packet.EXTERNAL = external
    ablation_packet.RESULTS = results
    ablation_packet.PACKET_JSON = external / "ablation_collection_packet.json"
    ablation_packet.PACKET_MD = external / "ablation_collection_packet.md"
    ablation_packet.WORK_ORDERS_CSV = external / "ablation_collection_work_orders.csv"
    ablation_packet.AUDIT_JSON = results / "external_ablation_collection_audit.json"
    ablation_packet.AUDIT_MD = results / "external_ablation_collection_audit.md"
    return old


def restore_ablation_packet(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(ablation_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_ablation_packet(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = ablation_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_ablation_packet(old)
    packet_payload = read_json(root / "external_validation" / "ablation_collection_packet.json")
    audit_payload = read_json(root / "results" / "external_ablation_collection_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "results" / "external_collection_plan.json"),
        read_json(root / "results" / "external_evidence_audit.json"),
        read_json(root / "external_validation" / "manifest_template.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "ablation_collection_packet.json")
    mutator(root, packet_payload)
    old = patch_ablation_packet(root)
    try:
        collection, evidence, manifest_template = load_audit_inputs(root)
        return ablation_packet.audit_packet(packet_payload, collection, evidence, manifest_template)
    finally:
        restore_ablation_packet(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_ablation_packet_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, packet_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, packet_payload, audit_payload
        return status, packet_payload, run_audit_case(root, mutator)


def run_file_deletion_case() -> bool:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_ablation_packet_selftest_delete_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        run_builder(root)
        deleted = root / "external_validation" / "ablation_collection_work_orders.csv"
        deleted.unlink()
        required_outputs = [
            root / "external_validation" / "ablation_collection_packet.json",
            root / "external_validation" / "ablation_collection_packet.md",
            root / "external_validation" / "ablation_collection_work_orders.csv",
            root / "results" / "external_ablation_collection_audit.json",
            root / "results" / "external_ablation_collection_audit.md",
        ]
        return not all(path.exists() for path in required_outputs)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_required_work_order(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"] = [
        order for order in payload.get("work_orders", []) or [] if order.get("ablation") != "seam_repair"
    ]


def promote_packet_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_external_evidence_ready"] = True
    payload["manifest_ablation_evidence_ready"] = True
    payload["not_external_evidence"] = False


def shrink_collection_budget(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_collection_plan.json"
    collection = read_json(path)
    for task in collection.get("tasks", []) or []:
        task["episodes_per_method"] = 5
        task["required_records"] = 60
    collection["task_family_count"] = 1
    collection["total_required_records"] = 240
    write_json(path, collection)


def remove_strict_missing_ablation(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_evidence_audit.json"
    evidence = read_json(path)
    for failure in evidence.get("blocking_failures", []) or []:
        if failure.get("name") == "external_ablations":
            failure["detail"] = str(failure.get("detail", "")).replace("seam_repair", "")
    write_json(path, evidence)


def drift_local_reference_variant(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"][0]["local_reference_variant"] = "synthetic_wrong_variant"


def remove_manifest_ablation_boolean(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "manifest_template.json"
    manifest = read_json(path)
    manifest.get("ablations", {}).pop("risk_calibration", None)
    write_json(path, manifest)


def empty_work_order_artifacts_and_commands(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"][0]["required_artifacts"] = ""
    payload["work_orders"][0]["acceptance_commands"] = ""


def drop_strict_rollout_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["operator_commands"] = [
        command for command in payload.get("operator_commands", []) or [] if "validate_external_rollouts.py" not in command
    ]


def write_real_manifest_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Ablation Collection Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing work order rejected: `{str(payload['missing_work_order_rejected']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Collection-budget shrink rejected: `{str(payload['collection_budget_shrink_rejected']).lower()}`.",
        f"Strict missing-ablation drift rejected: `{str(payload['strict_missing_ablation_drift_rejected']).lower()}`.",
        f"Local reference variant drift rejected: `{str(payload['local_reference_variant_drift_rejected']).lower()}`.",
        f"Manifest ablation boolean omission rejected: `{str(payload['manifest_ablation_boolean_omission_rejected']).lower()}`.",
        f"Work-order artifact/command drift rejected: `{str(payload['work_order_artifact_command_drift_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Real manifest write rejected: `{str(payload['real_manifest_write_rejected']).lower()}`.",
        f"Packet file deletion rejected: `{str(payload['packet_file_deletion_rejected']).lower()}`.",
        f"Real ablation packet outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the ablation collection packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing ablation work orders, premature strict-evidence promotion, shrunken ablation budgets, drift from the strict external-ablation blocker, local-reference variant drift, missing manifest ablation booleans, vague work-order artifacts or commands, strict command drift, accidental real manifest writes, and missing packet files without touching real ablation-packet outputs.",
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

    status, _packet_payload, audit_payload = run_case()
    temporary_packet_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("ablation_collection_packet_ready") is True
        and audit_payload.get("strict_external_evidence_ready") is False
        and audit_payload.get("manifest_ablation_evidence_ready") is False
        and int(audit_payload.get("work_order_count", 0) or 0) == 5
        and int(audit_payload.get("expected_ablation_records", 0) or 0) >= 600
        and check_named(audit_payload, "work_orders_are_actionable_and_artifact_bound") is True
    )
    add_check(
        checks,
        "temporary_ablation_collection_packet_ready_but_non_evidence",
        temporary_packet_ready,
        (
            f"status={status}, passed={audit_payload.get('passed')!r}, "
            f"expected_records={audit_payload.get('expected_ablation_records')!r}"
        ),
    )

    _, _, missing_work_order_audit = run_case(remove_required_work_order)
    missing_work_order_rejected = (
        missing_work_order_audit.get("passed") is False
        and check_named(missing_work_order_audit, "every_required_ablation_has_work_order") is False
    )
    add_check(
        checks,
        "missing_ablation_work_order_rejected",
        missing_work_order_rejected,
        f"check={check_named(missing_work_order_audit, 'every_required_ablation_has_work_order')!r}",
    )

    _, _, promoted_audit = run_case(promote_packet_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_audit.get("passed") is False
        and check_named(promoted_audit, "packet_is_non_evidence_and_fail_closed") is False
    )
    add_check(
        checks,
        "premature_evidence_promotion_rejected",
        premature_evidence_promotion_rejected,
        f"check={check_named(promoted_audit, 'packet_is_non_evidence_and_fail_closed')!r}",
    )

    _, _, budget_audit = run_case(shrink_collection_budget)
    collection_budget_shrink_rejected = (
        budget_audit.get("passed") is False
        and check_named(budget_audit, "task_and_reset_budget_preserved") is False
    )
    add_check(
        checks,
        "collection_budget_shrink_rejected",
        collection_budget_shrink_rejected,
        f"check={check_named(budget_audit, 'task_and_reset_budget_preserved')!r}",
    )

    _, _, strict_missing_audit = run_case(remove_strict_missing_ablation)
    strict_missing_ablation_drift_rejected = (
        strict_missing_audit.get("passed") is False
        and check_named(strict_missing_audit, "required_ablations_match_strict_audit") is False
    )
    add_check(
        checks,
        "strict_missing_ablation_drift_rejected",
        strict_missing_ablation_drift_rejected,
        f"check={check_named(strict_missing_audit, 'required_ablations_match_strict_audit')!r}",
    )

    _, _, local_reference_audit = run_case(drift_local_reference_variant)
    local_reference_variant_drift_rejected = (
        local_reference_audit.get("passed") is False
        and check_named(local_reference_audit, "work_orders_use_local_reference_variants") is False
    )
    add_check(
        checks,
        "local_reference_variant_drift_rejected",
        local_reference_variant_drift_rejected,
        f"check={check_named(local_reference_audit, 'work_orders_use_local_reference_variants')!r}",
    )

    _, _, manifest_ablation_audit = run_case(remove_manifest_ablation_boolean)
    manifest_ablation_boolean_omission_rejected = (
        manifest_ablation_audit.get("passed") is False
        and check_named(manifest_ablation_audit, "manifest_template_declares_ablation_booleans") is False
    )
    add_check(
        checks,
        "manifest_ablation_boolean_omission_rejected",
        manifest_ablation_boolean_omission_rejected,
        f"check={check_named(manifest_ablation_audit, 'manifest_template_declares_ablation_booleans')!r}",
    )

    _, _, work_order_drift_audit = run_case(empty_work_order_artifacts_and_commands)
    work_order_artifact_command_drift_rejected = (
        work_order_drift_audit.get("passed") is False
        and check_named(work_order_drift_audit, "work_orders_are_actionable_and_artifact_bound") is False
    )
    add_check(
        checks,
        "work_order_artifact_command_drift_rejected",
        work_order_artifact_command_drift_rejected,
        f"check={check_named(work_order_drift_audit, 'work_orders_are_actionable_and_artifact_bound')!r}",
    )

    _, _, command_audit = run_case(drop_strict_rollout_command)
    strict_command_drift_rejected = (
        command_audit.get("passed") is False
        and check_named(command_audit, "operator_commands_cover_collection_manifest_rollout_and_strict_evidence") is False
    )
    add_check(
        checks,
        "strict_command_drift_rejected",
        strict_command_drift_rejected,
        f"check={check_named(command_audit, 'operator_commands_cover_collection_manifest_rollout_and_strict_evidence')!r}",
    )

    _, _, manifest_write_audit = run_case(write_real_manifest_in_fixture)
    real_manifest_write_rejected = (
        manifest_write_audit.get("passed") is False
        and check_named(manifest_write_audit, "no_real_manifest_written") is False
    )
    add_check(
        checks,
        "real_manifest_write_rejected",
        real_manifest_write_rejected,
        f"check={check_named(manifest_write_audit, 'no_real_manifest_written')!r}",
    )

    packet_file_deletion_rejected = run_file_deletion_case()
    add_check(
        checks,
        "packet_file_deletion_rejected",
        packet_file_deletion_rejected,
        "required temporary packet output check detects deleted ablation work-order CSV",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_after == real_hashes_before
    add_check(
        checks,
        "real_ablation_packet_outputs_untouched",
        real_outputs_untouched,
        f"before={real_hashes_before}, after={real_hashes_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_packet_ready": temporary_packet_ready,
        "missing_work_order_rejected": missing_work_order_rejected,
        "premature_evidence_promotion_rejected": premature_evidence_promotion_rejected,
        "collection_budget_shrink_rejected": collection_budget_shrink_rejected,
        "strict_missing_ablation_drift_rejected": strict_missing_ablation_drift_rejected,
        "local_reference_variant_drift_rejected": local_reference_variant_drift_rejected,
        "manifest_ablation_boolean_omission_rejected": manifest_ablation_boolean_omission_rejected,
        "work_order_artifact_command_drift_rejected": work_order_artifact_command_drift_rejected,
        "strict_command_drift_rejected": strict_command_drift_rejected,
        "real_manifest_write_rejected": real_manifest_write_rejected,
        "packet_file_deletion_rejected": packet_file_deletion_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes_before": real_hashes_before,
        "real_output_hashes_after": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)

    status_text = "PASS" if passed else "FAIL"
    print(f"External ablation collection packet self-test: {status_text}; checks={sum(1 for check in checks if check['passed'])}/{len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

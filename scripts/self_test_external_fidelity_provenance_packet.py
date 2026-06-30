from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_fidelity_provenance_packet as fidelity_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_fidelity_provenance_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_fidelity_provenance_packet_self_test.md"
VERSION = "external_fidelity_provenance_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "fidelity_provenance_packet.json",
    REAL_EXTERNAL / "fidelity_provenance_packet.md",
    REAL_EXTERNAL / "fidelity_provenance_work_orders.csv",
    REAL_RESULTS / "external_fidelity_provenance_audit.json",
    REAL_RESULTS / "external_fidelity_provenance_audit.md",
    REAL_EXTERNAL / "fidelity_acceptance.json",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_RESULTS / "external_fidelity_acceptance_audit.json",
    REAL_RESULTS / "external_platform_onboarding_audit.json",
    REAL_RESULTS / "external_collection_readiness_audit.json",
    REAL_RESULTS / "independent_validation_route_audit.json",
    REAL_EXTERNAL / "fidelity_acceptance_template.json",
    REAL_RESULTS / "external_platform_probe.json",
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
        raise AssertionError(f"missing fidelity-provenance self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_fidelity_packet(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": fidelity_packet.ROOT,
        "EXTERNAL": fidelity_packet.EXTERNAL,
        "RESULTS": fidelity_packet.RESULTS,
        "PACKET_JSON": fidelity_packet.PACKET_JSON,
        "PACKET_MD": fidelity_packet.PACKET_MD,
        "WORK_ORDERS_CSV": fidelity_packet.WORK_ORDERS_CSV,
        "AUDIT_JSON": fidelity_packet.AUDIT_JSON,
        "AUDIT_MD": fidelity_packet.AUDIT_MD,
    }
    fidelity_packet.ROOT = root
    fidelity_packet.EXTERNAL = external
    fidelity_packet.RESULTS = results
    fidelity_packet.PACKET_JSON = external / "fidelity_provenance_packet.json"
    fidelity_packet.PACKET_MD = external / "fidelity_provenance_packet.md"
    fidelity_packet.WORK_ORDERS_CSV = external / "fidelity_provenance_work_orders.csv"
    fidelity_packet.AUDIT_JSON = results / "external_fidelity_provenance_audit.json"
    fidelity_packet.AUDIT_MD = results / "external_fidelity_provenance_audit.md"
    return old


def restore_fidelity_packet(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(fidelity_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_fidelity_packet(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = fidelity_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_fidelity_packet(old)
    packet_payload = read_json(root / "external_validation" / "fidelity_provenance_packet.json")
    audit_payload = read_json(root / "results" / "external_fidelity_provenance_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "results" / "external_fidelity_acceptance_audit.json"),
        read_json(root / "results" / "external_platform_onboarding_audit.json"),
        read_json(root / "results" / "external_collection_readiness_audit.json"),
        read_json(root / "results" / "independent_validation_route_audit.json"),
        read_json(root / "external_validation" / "fidelity_acceptance_template.json"),
        read_json(root / "results" / "external_platform_probe.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "fidelity_provenance_packet.json")
    mutator(root, packet_payload)
    old = patch_fidelity_packet(root)
    try:
        fidelity, onboarding, collection, route, template, platform_probe = load_audit_inputs(root)
        return fidelity_packet.audit_packet(
            packet_payload,
            fidelity,
            onboarding,
            collection,
            route,
            template,
            platform_probe,
        )
    finally:
        restore_fidelity_packet(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_fidelity_provenance_selftest_", dir=TMP_ROOT) as temp_name:
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
        order for order in payload.get("work_orders", []) or [] if order.get("id") != "verify_paired_reset_replay"
    ]


def empty_work_order_artifacts(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"][0]["required_artifacts"] = []
    payload["work_orders"][0]["acceptance_commands"] = []


def promote_packet_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_fidelity_evidence_ready"] = True
    payload["strict_external_evidence_ready"] = True
    payload["acceptance_ready"] = True
    payload["manifest_written"] = True


def promote_acceptance_audit(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_fidelity_acceptance_audit.json"
    audit = read_json(path)
    audit["acceptance_ready"] = True
    audit["readiness_state"] = "ACCEPTED"
    write_json(path, audit)


def promote_onboarding_audit(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_platform_onboarding_audit.json"
    audit = read_json(path)
    audit["strict_evidence_ready"] = True
    write_json(path, audit)


def promote_platform_probe(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_platform_probe.json"
    probe = read_json(path)
    probe["not_external_evidence"] = False
    probe["strict_fidelity_evidence_ready"] = True
    probe["strict_external_evidence_ready"] = True
    write_json(path, probe)


def promote_collection_ready(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_collection_readiness_audit.json"
    collection = read_json(path)
    collection["collection_ready"] = True
    write_json(path, collection)


def shrink_template_gates(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "fidelity_acceptance_template.json"
    template = read_json(path)
    template["acceptance_gates"] = template.get("acceptance_gates", [])[:1]
    write_json(path, template)


def drop_strict_fidelity_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_acceptance_commands"] = [
        command
        for command in payload.get("strict_acceptance_commands", []) or []
        if "audit_external_fidelity_acceptance.py" not in command
    ]


def write_real_acceptance_or_manifest(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "fidelity_acceptance.json", {"synthetic_self_test_only": True})
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def delete_packet_file(root: Path, _payload: dict[str, Any]) -> None:
    (root / "external_validation" / "fidelity_provenance_work_orders.csv").unlink()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Fidelity Provenance Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict fidelity evidence ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing work orders rejected: `{str(payload['missing_work_orders_rejected']).lower()}`.",
        f"Work-order artifact/command drift rejected: `{str(payload['work_order_artifact_command_drift_rejected']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Acceptance-ready drift rejected: `{str(payload['acceptance_ready_drift_rejected']).lower()}`.",
        f"Onboarding strict-evidence drift rejected: `{str(payload['onboarding_strict_evidence_drift_rejected']).lower()}`.",
        f"Platform-probe promotion rejected: `{str(payload['platform_probe_promotion_rejected']).lower()}`.",
        f"Collection-ready promotion rejected: `{str(payload['collection_ready_promotion_rejected']).lower()}`.",
        f"Template gate shrink rejected: `{str(payload['template_gate_shrink_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Real acceptance/manifest write rejected: `{str(payload['real_acceptance_or_manifest_write_rejected']).lower()}`.",
        f"Packet file deletion rejected: `{str(payload['packet_file_deletion_rejected']).lower()}`.",
        f"Real fidelity-provenance outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the fidelity provenance packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing or vague work orders, premature fidelity/external evidence promotion, false acceptance readiness, onboarding/probe/collection gate promotion, shrunken acceptance gates, strict-command drift, accidental real acceptance or manifest writes, and missing packet files without touching the real fidelity-provenance outputs.",
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
        and audit_payload.get("fidelity_provenance_packet_ready") is True
        and audit_payload.get("strict_fidelity_evidence_ready") is False
        and audit_payload.get("strict_external_evidence_ready") is False
        and audit_payload.get("acceptance_ready") is False
        and int(packet_payload.get("blocking_missing_count", 0) or 0) >= 10
        and len(packet_payload.get("work_orders", []) or []) >= 6
        and check_named(audit_payload, "work_orders_cover_fidelity_blockers") is True
        and check_named(audit_payload, "work_orders_are_actionable_and_artifact_bound") is True
        and check_named(audit_payload, "no_real_acceptance_or_manifest_written") is True
    )
    add_check(
        checks,
        "temporary_fidelity_provenance_packet_ready_but_non_evidence",
        temporary_packet_ready,
        (
            f"status={status}, passed={audit_payload.get('passed')!r}, "
            f"blocking={packet_payload.get('blocking_missing_count')!r}, "
            f"orders={len(packet_payload.get('work_orders', []) or [])}"
        ),
    )

    _, _, missing_orders = run_case(remove_work_order)
    missing_work_orders_rejected = (
        missing_orders.get("passed") is False
        and check_named(missing_orders, "work_orders_cover_fidelity_blockers") is False
    )
    add_check(checks, "missing_work_orders_rejected", missing_work_orders_rejected, f"work_order_check={check_named(missing_orders, 'work_orders_cover_fidelity_blockers')}")

    _, _, vague_orders = run_case(empty_work_order_artifacts)
    work_order_artifact_command_drift_rejected = (
        vague_orders.get("passed") is False
        and check_named(vague_orders, "work_orders_are_actionable_and_artifact_bound") is False
    )
    add_check(checks, "work_order_artifact_command_drift_rejected", work_order_artifact_command_drift_rejected, f"actionable_check={check_named(vague_orders, 'work_orders_are_actionable_and_artifact_bound')}")

    _, _, promoted_packet = run_case(promote_packet_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_packet.get("passed") is False
        and check_named(promoted_packet, "packet_is_non_evidence_and_fail_closed") is False
    )
    add_check(checks, "premature_evidence_promotion_rejected", premature_evidence_promotion_rejected, f"non_evidence_check={check_named(promoted_packet, 'packet_is_non_evidence_and_fail_closed')}")

    _, _, acceptance_drift = run_case(promote_acceptance_audit)
    acceptance_ready_drift_rejected = (
        acceptance_drift.get("passed") is False
        and check_named(acceptance_drift, "fidelity_acceptance_contract_ready_but_not_evidence") is False
    )
    add_check(checks, "acceptance_ready_drift_rejected", acceptance_ready_drift_rejected, f"acceptance_check={check_named(acceptance_drift, 'fidelity_acceptance_contract_ready_but_not_evidence')}")

    _, _, onboarding_drift = run_case(promote_onboarding_audit)
    onboarding_strict_evidence_drift_rejected = (
        onboarding_drift.get("passed") is False
        and check_named(onboarding_drift, "platform_onboarding_packet_ready") is False
    )
    add_check(checks, "onboarding_strict_evidence_drift_rejected", onboarding_strict_evidence_drift_rejected, f"onboarding_check={check_named(onboarding_drift, 'platform_onboarding_packet_ready')}")

    _, _, platform_drift = run_case(promote_platform_probe)
    platform_probe_promotion_rejected = (
        platform_drift.get("passed") is False
        and check_named(platform_drift, "external_platform_probe_ready") is False
    )
    add_check(checks, "platform_probe_promotion_rejected", platform_probe_promotion_rejected, f"platform_probe_check={check_named(platform_drift, 'external_platform_probe_ready')}")

    _, _, collection_drift = run_case(promote_collection_ready)
    collection_ready_promotion_rejected = (
        collection_drift.get("passed") is False
        and check_named(collection_drift, "independent_route_and_collection_still_fail_closed") is False
    )
    add_check(checks, "collection_ready_promotion_rejected", collection_ready_promotion_rejected, f"collection_check={check_named(collection_drift, 'independent_route_and_collection_still_fail_closed')}")

    _, _, template_drift = run_case(shrink_template_gates)
    template_gate_shrink_rejected = (
        template_drift.get("passed") is False
        and check_named(template_drift, "template_declares_required_platform_and_gate_fields") is False
    )
    add_check(checks, "template_gate_shrink_rejected", template_gate_shrink_rejected, f"template_check={check_named(template_drift, 'template_declares_required_platform_and_gate_fields')}")

    _, _, command_drift = run_case(drop_strict_fidelity_command)
    strict_command_drift_rejected = (
        command_drift.get("passed") is False
        and check_named(command_drift, "strict_commands_cover_fidelity_manifest_collection_and_evidence") is False
    )
    add_check(checks, "strict_command_drift_rejected", strict_command_drift_rejected, f"command_check={check_named(command_drift, 'strict_commands_cover_fidelity_manifest_collection_and_evidence')}")

    _, _, real_write_drift = run_case(write_real_acceptance_or_manifest)
    real_acceptance_or_manifest_write_rejected = (
        real_write_drift.get("passed") is False
        and check_named(real_write_drift, "no_real_acceptance_or_manifest_written") is False
    )
    add_check(checks, "real_acceptance_or_manifest_write_rejected", real_acceptance_or_manifest_write_rejected, f"real_write_check={check_named(real_write_drift, 'no_real_acceptance_or_manifest_written')}")

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
        "real_fidelity_provenance_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    check_map = {check["name"]: check["passed"] for check in checks}
    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "acceptance_ready": False,
        "temporary_packet_ready": check_map.get("temporary_fidelity_provenance_packet_ready_but_non_evidence") is True,
        "missing_work_orders_rejected": check_map.get("missing_work_orders_rejected") is True,
        "work_order_artifact_command_drift_rejected": check_map.get("work_order_artifact_command_drift_rejected") is True,
        "premature_evidence_promotion_rejected": check_map.get("premature_evidence_promotion_rejected") is True,
        "acceptance_ready_drift_rejected": check_map.get("acceptance_ready_drift_rejected") is True,
        "onboarding_strict_evidence_drift_rejected": check_map.get("onboarding_strict_evidence_drift_rejected") is True,
        "platform_probe_promotion_rejected": check_map.get("platform_probe_promotion_rejected") is True,
        "collection_ready_promotion_rejected": check_map.get("collection_ready_promotion_rejected") is True,
        "template_gate_shrink_rejected": check_map.get("template_gate_shrink_rejected") is True,
        "strict_command_drift_rejected": check_map.get("strict_command_drift_rejected") is True,
        "real_acceptance_or_manifest_write_rejected": check_map.get("real_acceptance_or_manifest_write_rejected") is True,
        "packet_file_deletion_rejected": check_map.get("packet_file_deletion_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External fidelity provenance packet self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

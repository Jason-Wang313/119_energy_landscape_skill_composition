from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_method_implementation_packet as method_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_method_implementation_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_method_implementation_packet_self_test.md"
VERSION = "external_method_implementation_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "method_implementation_packet.json",
    REAL_EXTERNAL / "method_implementation_packet.md",
    REAL_EXTERNAL / "method_implementation_work_orders.csv",
    REAL_EXTERNAL / "method_reference_provenance.csv",
    REAL_EXTERNAL / "adapter_acceptance_fixtures.json",
    REAL_EXTERNAL / "adapter_acceptance_fixtures.md",
    REAL_EXTERNAL / "adapter_acceptance_fixtures.csv",
    REAL_EXTERNAL / "method_manifest_cutover_checklist.csv",
    REAL_EXTERNAL / "method_manifest_cutover_checklist.md",
    REAL_RESULTS / "external_method_implementation_audit.json",
    REAL_RESULTS / "external_method_implementation_audit.md",
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
        raise AssertionError(f"missing method-packet self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    shutil.copytree(
        REAL_EXTERNAL / "baseline_specs",
        root / "external_validation" / "baseline_specs",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(
        REAL_EXTERNAL / "baselines",
        root / "external_validation" / "baselines",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    copy_file(REAL_EXTERNAL / "log_schema_v1.json", root / "external_validation" / "log_schema_v1.json")
    copy_file(
        REAL_RESULTS / "external_baseline_contract_audit.json",
        root / "results" / "external_baseline_contract_audit.json",
    )
    copy_file(
        REAL_RESULTS / "external_adapter_contract_evidence_audit.json",
        root / "results" / "external_adapter_contract_evidence_audit.json",
    )


def patch_method_packet(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": method_packet.ROOT,
        "EXTERNAL": method_packet.EXTERNAL,
        "RESULTS": method_packet.RESULTS,
        "SPEC_DIR": method_packet.SPEC_DIR,
        "PACKET_JSON": method_packet.PACKET_JSON,
        "PACKET_MD": method_packet.PACKET_MD,
        "WORK_ORDERS_CSV": method_packet.WORK_ORDERS_CSV,
        "REFERENCE_PROVENANCE_CSV": method_packet.REFERENCE_PROVENANCE_CSV,
        "ACCEPTANCE_FIXTURES_JSON": method_packet.ACCEPTANCE_FIXTURES_JSON,
        "ACCEPTANCE_FIXTURES_MD": method_packet.ACCEPTANCE_FIXTURES_MD,
        "ACCEPTANCE_FIXTURES_CSV": method_packet.ACCEPTANCE_FIXTURES_CSV,
        "METHOD_CUTOVER_CSV": method_packet.METHOD_CUTOVER_CSV,
        "METHOD_CUTOVER_MD": method_packet.METHOD_CUTOVER_MD,
        "AUDIT_JSON": method_packet.AUDIT_JSON,
        "AUDIT_MD": method_packet.AUDIT_MD,
    }
    method_packet.ROOT = root
    method_packet.EXTERNAL = external
    method_packet.RESULTS = results
    method_packet.SPEC_DIR = external / "baseline_specs"
    method_packet.PACKET_JSON = external / "method_implementation_packet.json"
    method_packet.PACKET_MD = external / "method_implementation_packet.md"
    method_packet.WORK_ORDERS_CSV = external / "method_implementation_work_orders.csv"
    method_packet.REFERENCE_PROVENANCE_CSV = external / "method_reference_provenance.csv"
    method_packet.ACCEPTANCE_FIXTURES_JSON = external / "adapter_acceptance_fixtures.json"
    method_packet.ACCEPTANCE_FIXTURES_MD = external / "adapter_acceptance_fixtures.md"
    method_packet.ACCEPTANCE_FIXTURES_CSV = external / "adapter_acceptance_fixtures.csv"
    method_packet.METHOD_CUTOVER_CSV = external / "method_manifest_cutover_checklist.csv"
    method_packet.METHOD_CUTOVER_MD = external / "method_manifest_cutover_checklist.md"
    method_packet.AUDIT_JSON = results / "external_method_implementation_audit.json"
    method_packet.AUDIT_MD = results / "external_method_implementation_audit.md"
    return old


def restore_method_packet(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(method_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_method_packet(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = method_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_method_packet(old)
    packet_payload = read_json(root / "external_validation" / "method_implementation_packet.json")
    audit_payload = read_json(root / "results" / "external_method_implementation_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any], dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "method_implementation_packet.json")
    adapter_evidence = read_json(root / "results" / "external_adapter_contract_evidence_audit.json")
    mutator(root, packet_payload, adapter_evidence)
    old = patch_method_packet(root)
    try:
        specs = method_packet.load_specs()
        baseline_audit = read_json(root / "results" / "external_baseline_contract_audit.json")
        return method_packet.audit_packet(packet_payload, specs, baseline_audit, adapter_evidence)
    finally:
        restore_method_packet(old)


def remove_work_order(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    payload["work_orders"] = payload.get("work_orders", [])[1:]


def add_oracle_work_order(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    oracle_order = json.loads(json.dumps(payload["work_orders"][0]))
    oracle_order["method"] = method_packet.ORACLE_METHOD
    oracle_order["manifest_method_entry_template"]["name"] = method_packet.ORACLE_METHOD
    payload["work_orders"].append(oracle_order)


def allow_reference_adapter_shortcut(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    payload["work_orders"][0]["reference_adapter_allowed_as_evidence"] = True


def replace_checkpoint_hash_with_source_hash(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    payload["work_orders"][0]["manifest_method_entry_template"]["checkpoint_or_config_hash"] = "<implementation_sha256_or_commit>"


def remove_fairness_binding(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    provenance = payload["work_orders"][0]["manifest_method_entry_template"]["implementation_provenance"]
    provenance.pop("compute_budget_hash", None)


def erode_acceptance_fixture_contract(root: Path, _payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    fixture_path = root / "external_validation" / "adapter_acceptance_fixtures.json"
    fixtures = read_json(fixture_path)
    fixtures["fixtures"][0]["required_api"] = ["initialize", "propose", "log"]
    write_json(fixture_path, fixtures)


def allow_cutover_shortcut(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    payload["method_manifest_cutover_checklist"][0]["reference_adapter_allowed_as_evidence"] = True


def drop_strict_adapter_command(_root: Path, payload: dict[str, Any], _adapter_evidence: dict[str, Any]) -> None:
    payload["strict_acceptance_commands"] = [
        command for command in payload.get("strict_acceptance_commands", []) if "validate_external_adapters.py --strict" not in command
    ]


def promote_adapter_evidence(_root: Path, payload: dict[str, Any], adapter_evidence: dict[str, Any]) -> None:
    adapter_evidence["passed"] = True
    payload["adapter_evidence_state"]["strict_adapter_audit_passed"] = True


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Method Implementation Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict adapter evidence ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing work order rejected: `{str(payload['missing_work_order_rejected']).lower()}`.",
        f"Oracle work order rejected: `{str(payload['oracle_work_order_rejected']).lower()}`.",
        f"Reference-adapter shortcut rejected: `{str(payload['reference_adapter_shortcut_rejected']).lower()}`.",
        f"Checkpoint/config hash shortcut rejected: `{str(payload['checkpoint_hash_shortcut_rejected']).lower()}`.",
        f"Fairness binding drift rejected: `{str(payload['fairness_binding_drift_rejected']).lower()}`.",
        f"Fixture contract drift rejected: `{str(payload['fixture_contract_drift_rejected']).lower()}`.",
        f"Cutover shortcut rejected: `{str(payload['cutover_shortcut_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Adapter evidence promotion rejected: `{str(payload['adapter_evidence_promotion_rejected']).lower()}`.",
        f"Real method packet outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test runs the method implementation packet builder in a temporary copied workspace, verifies the packet is ready but still non-evidence, and then mutates the temporary packet to prove the audit rejects missing non-oracle methods, oracle leakage, reference-adapter evidence shortcuts, implementation-source hashes masquerading as checkpoint/config hashes, missing fairness bindings, eroded adapter fixtures, cutover shortcuts, strict-command drift, and accidental strict adapter-evidence promotion.",
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

    with tempfile.TemporaryDirectory(prefix="paper119_method_packet_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        builder_status, packet_payload, audit_payload, _ = run_builder(root)
        temporary_packet_ready = (
            builder_status == 0
            and audit_payload.get("passed") is True
            and audit_payload.get("method_implementation_packet_ready") is True
            and audit_payload.get("strict_adapter_evidence_ready") is False
            and packet_payload.get("not_external_evidence") is True
            and int(packet_payload.get("non_oracle_method_count", 0) or 0) >= 11
            and check_named(audit_payload, "work_orders_cover_all_missing_non_oracle_methods") is True
            and check_named(audit_payload, "adapter_evidence_still_missing") is True
        )
        add_check(
            checks,
            "temporary_method_packet_ready_but_non_evidence",
            temporary_packet_ready,
            (
                f"status={builder_status}, passed={audit_payload.get('passed')!r}, "
                f"packet_ready={audit_payload.get('method_implementation_packet_ready')!r}, "
                f"strict={audit_payload.get('strict_adapter_evidence_ready')!r}"
            ),
        )

        missing_work_order_audit = run_audit_case(root, remove_work_order)
        missing_work_order_rejected = (
            missing_work_order_audit.get("passed") is False
            and check_named(missing_work_order_audit, "work_orders_cover_all_missing_non_oracle_methods") is False
        )
        add_check(
            checks,
            "missing_work_order_rejected",
            missing_work_order_rejected,
            f"work_order_check={check_named(missing_work_order_audit, 'work_orders_cover_all_missing_non_oracle_methods')}",
        )

        oracle_audit = run_audit_case(root, add_oracle_work_order)
        oracle_work_order_rejected = (
            oracle_audit.get("passed") is False
            and check_named(oracle_audit, "oracle_excluded_from_work_orders") is False
        )
        add_check(
            checks,
            "oracle_work_order_rejected",
            oracle_work_order_rejected,
            f"oracle_check={check_named(oracle_audit, 'oracle_excluded_from_work_orders')}",
        )

        reference_shortcut_audit = run_audit_case(root, allow_reference_adapter_shortcut)
        reference_adapter_shortcut_rejected = (
            reference_shortcut_audit.get("passed") is False
            and check_named(reference_shortcut_audit, "work_orders_forbid_scaffolds_and_reference_adapters") is False
        )
        add_check(
            checks,
            "reference_adapter_shortcut_rejected",
            reference_adapter_shortcut_rejected,
            f"shortcut_check={check_named(reference_shortcut_audit, 'work_orders_forbid_scaffolds_and_reference_adapters')}",
        )

        hash_shortcut_audit = run_audit_case(root, replace_checkpoint_hash_with_source_hash)
        checkpoint_hash_shortcut_rejected = (
            hash_shortcut_audit.get("passed") is False
            and check_named(hash_shortcut_audit, "manifest_entry_templates_bind_hash_to_checkpoint_config_artifact") is False
        )
        add_check(
            checks,
            "checkpoint_hash_shortcut_rejected",
            checkpoint_hash_shortcut_rejected,
            f"hash_binding_check={check_named(hash_shortcut_audit, 'manifest_entry_templates_bind_hash_to_checkpoint_config_artifact')}",
        )

        fairness_audit = run_audit_case(root, remove_fairness_binding)
        fairness_binding_drift_rejected = (
            fairness_audit.get("passed") is False
            and check_named(fairness_audit, "manifest_entry_templates_bind_fairness_contract") is False
        )
        add_check(
            checks,
            "fairness_binding_drift_rejected",
            fairness_binding_drift_rejected,
            f"fairness_check={check_named(fairness_audit, 'manifest_entry_templates_bind_fairness_contract')}",
        )

        fixture_audit = run_audit_case(root, erode_acceptance_fixture_contract)
        fixture_contract_drift_rejected = (
            fixture_audit.get("passed") is False
            and check_named(fixture_audit, "adapter_acceptance_fixtures_define_contract") is False
        )
        add_check(
            checks,
            "fixture_contract_drift_rejected",
            fixture_contract_drift_rejected,
            f"fixture_contract_check={check_named(fixture_audit, 'adapter_acceptance_fixtures_define_contract')}",
        )

        cutover_audit = run_audit_case(root, allow_cutover_shortcut)
        cutover_shortcut_rejected = (
            cutover_audit.get("passed") is False
            and check_named(cutover_audit, "method_manifest_cutover_checklist_forbids_shortcuts") is False
        )
        add_check(
            checks,
            "cutover_shortcut_rejected",
            cutover_shortcut_rejected,
            f"cutover_check={check_named(cutover_audit, 'method_manifest_cutover_checklist_forbids_shortcuts')}",
        )

        strict_command_audit = run_audit_case(root, drop_strict_adapter_command)
        strict_command_drift_rejected = (
            strict_command_audit.get("passed") is False
            and check_named(strict_command_audit, "strict_commands_cover_adapter_rollout_pairing_and_evidence") is False
        )
        add_check(
            checks,
            "strict_command_drift_rejected",
            strict_command_drift_rejected,
            f"strict_command_check={check_named(strict_command_audit, 'strict_commands_cover_adapter_rollout_pairing_and_evidence')}",
        )

        adapter_promotion_audit = run_audit_case(root, promote_adapter_evidence)
        adapter_evidence_promotion_rejected = (
            adapter_promotion_audit.get("passed") is False
            and check_named(adapter_promotion_audit, "adapter_evidence_still_missing") is False
        )
        add_check(
            checks,
            "adapter_evidence_promotion_rejected",
            adapter_evidence_promotion_rejected,
            f"adapter_evidence_check={check_named(adapter_promotion_audit, 'adapter_evidence_still_missing')}",
        )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_method_packet_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_adapter_evidence_ready": False,
        "temporary_packet_ready": check_named({"checks": checks}, "temporary_method_packet_ready_but_non_evidence") is True,
        "missing_work_order_rejected": check_named({"checks": checks}, "missing_work_order_rejected") is True,
        "oracle_work_order_rejected": check_named({"checks": checks}, "oracle_work_order_rejected") is True,
        "reference_adapter_shortcut_rejected": check_named({"checks": checks}, "reference_adapter_shortcut_rejected") is True,
        "checkpoint_hash_shortcut_rejected": check_named({"checks": checks}, "checkpoint_hash_shortcut_rejected") is True,
        "fairness_binding_drift_rejected": check_named({"checks": checks}, "fairness_binding_drift_rejected") is True,
        "fixture_contract_drift_rejected": check_named({"checks": checks}, "fixture_contract_drift_rejected") is True,
        "cutover_shortcut_rejected": check_named({"checks": checks}, "cutover_shortcut_rejected") is True,
        "strict_command_drift_rejected": check_named({"checks": checks}, "strict_command_drift_rejected") is True,
        "adapter_evidence_promotion_rejected": check_named({"checks": checks}, "adapter_evidence_promotion_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External method implementation packet self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

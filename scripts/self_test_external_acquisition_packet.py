from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import build_external_acquisition_packet as acquisition


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_OUT_JSON = REAL_RESULTS / "external_acquisition_packet.json"
REAL_OUT_MD = REAL_RESULTS / "external_acquisition_packet.md"

OUT_JSON = REAL_RESULTS / "external_acquisition_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_acquisition_packet_self_test.md"

RESULT_FIXTURES = [
    "submission_readiness_gap_audit.json",
    "external_collection_readiness_audit.json",
    "external_evidence_preflight.json",
    "independent_validation_route_audit.json",
    "external_platform_probe.json",
    "maniskill_task_binding_probe.json",
    "maniskill_env_smoke_probe.json",
    "maniskill_fidelity_metadata_probe.json",
    "external_platform_onboarding_audit.json",
    "external_fidelity_provenance_audit.json",
    "external_fidelity_acceptance_draft_audit.json",
    "fidelity_acceptance_materialization_plan.json",
    "fidelity_acceptance_materialization_plan.md",
    "external_config_materialization_plan.json",
    "external_backend_contract_audit.json",
    "external_backend_integration_audit.json",
    "maniskill_backend_readiness_audit.json",
    "maniskill_reference_collection_preflight_audit.json",
    "external_config_manifest_audit.json",
    "external_rollout_evidence_audit.json",
    "external_ablation_collection_audit.json",
    "external_evidence_intake_ledger_audit.json",
    "external_precollection_freeze_receipt_audit.json",
    "external_postcollection_evidence_seal_audit.json",
    "external_postcollection_seal_consistency_audit.json",
    "external_postcollection_seal_consistency_audit.md",
    "external_method_implementation_audit.json",
    "external_pilot_smoke_packet_audit.json",
    "maniskill_render_video_preflight_audit.json",
    "maniskill_render_video_preflight_audit.md",
    "maniskill_render_resource_sweep.json",
    "maniskill_render_resource_sweep.md",
    "maniskill_pilot_runtime_liveness_audit.json",
    "maniskill_pilot_runtime_liveness_audit.md",
    "maniskill_render_machine_qualification.json",
    "maniskill_render_machine_qualification.md",
]

EXTERNAL_FIXTURES = [
    "backend_integration_packet.md",
    "backend_integration_work_orders.csv",
    "config_manifest_packet.md",
    "config_manifest_work_orders.csv",
    "rollout_evidence_packet.md",
    "rollout_evidence_work_orders.csv",
    "ablation_collection_packet.md",
    "ablation_collection_work_orders.csv",
    "evidence_intake_ledger.md",
    "evidence_intake_ledger.csv",
    "precollection_freeze_receipt.md",
    "precollection_freeze_receipt.csv",
    "postcollection_evidence_seal.md",
    "postcollection_evidence_seal.csv",
    "pilot_smoke_packet.md",
    "pilot_smoke_work_orders.csv",
    "render_resource_sweep_work_orders.csv",
    "render_machine_qualification_packet.md",
    "method_implementation_packet.md",
    "method_implementation_work_orders.csv",
    "method_reference_provenance.csv",
    "method_manifest_cutover_checklist.csv",
    "method_manifest_cutover_checklist.md",
    "adapter_acceptance_fixtures.json",
    "adapter_acceptance_fixtures.md",
    "adapter_acceptance_fixtures.csv",
    "fidelity_provenance_packet.md",
    "fidelity_provenance_work_orders.csv",
    "fidelity_acceptance_draft.json",
    "fidelity_acceptance_draft.md",
]

SCRIPT_EXISTENCE_FIXTURES = [
    "audit_maniskill_render_video_preflight.py",
    "audit_maniskill_render_resource_sweep.py",
    "audit_maniskill_pilot_runtime_liveness.py",
    "build_maniskill_render_machine_qualification.py",
    "materialize_fidelity_acceptance.py",
]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing acquisition self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for name in RESULT_FIXTURES:
        copy_file(REAL_RESULTS / name, root / "results" / name)
    for name in EXTERNAL_FIXTURES:
        copy_file(REAL_EXTERNAL / name, root / "external_validation" / name)
    for name in SCRIPT_EXISTENCE_FIXTURES:
        copy_file(REAL_ROOT / "scripts" / name, root / "scripts" / name)


def run_builder(root: Path) -> tuple[int, dict[str, Any]]:
    original = (
        acquisition.ROOT,
        acquisition.RESULTS,
        acquisition.EXTERNAL,
        acquisition.OUT_JSON,
        acquisition.OUT_MD,
    )
    try:
        acquisition.ROOT = root
        acquisition.RESULTS = root / "results"
        acquisition.EXTERNAL = root / "external_validation"
        acquisition.OUT_JSON = acquisition.RESULTS / "external_acquisition_packet.json"
        acquisition.OUT_MD = acquisition.RESULTS / "external_acquisition_packet.md"
        status = acquisition.main()
        payload = read_json(acquisition.OUT_JSON)
        return status, payload
    finally:
        (
            acquisition.ROOT,
            acquisition.RESULTS,
            acquisition.EXTERNAL,
            acquisition.OUT_JSON,
            acquisition.OUT_MD,
        ) = original


def check_named(payload: dict[str, Any], name: str) -> bool | None:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed") is True
    return None


def run_case(mutator: Callable[[Path], None] | None = None) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_acquisition_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_builder(root)


def remove_collection_readiness(root: Path) -> None:
    (root / "results" / "external_collection_readiness_audit.json").unlink()


def add_unmapped_blocker(root: Path) -> None:
    path = root / "results" / "submission_readiness_gap_audit.json"
    payload = read_json(path)
    payload["blocking_missing_requirements"] = int(payload.get("blocking_missing_requirements", 0) or 0) + 1
    payload["missing_requirements"] = int(payload.get("missing_requirements", 0) or 0) + 1
    payload.setdefault("requirements", []).append(
        {
            "requirement": "Unmapped external evidence shortcut",
            "status": "missing",
            "submission_blocking": True,
            "blocker": "synthetic self-test unmapped blocker should fail closed",
            "evidence": ["results/external_acquisition_packet_self_test.json"],
        }
    )
    write_json(path, payload)


def write_premature_manifest(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def promote_collection_readiness(root: Path) -> None:
    path = root / "results" / "external_collection_readiness_audit.json"
    payload = read_json(path)
    payload["collection_ready"] = True
    payload["blocking_missing"] = []
    for check in payload.get("checks", []) or []:
        if check.get("name") in {
            "backend_module_ready",
            "fidelity_acceptance_ready",
            "alias_unsealing_explicit",
            "run_id_specific",
        }:
            check["passed"] = True
    write_json(path, payload)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Acquisition Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Missing source rejected: `{str(payload['missing_source_rejected']).lower()}`.",
        f"Unmapped blocker rejected: `{str(payload['unmapped_blocker_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Collection readiness drift rejected: `{str(payload['collection_readiness_drift_rejected']).lower()}`.",
        f"Real acquisition outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It runs the acquisition packet builder in temporary copied workspaces, proves the current no-evidence acquisition packet can be rebuilt there, and proves that missing source audits, unmapped blockers, accidental real-manifest presence, and premature collection-readiness promotion fail closed without touching the real repository packet.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    real_json_before = sha256_file(REAL_OUT_JSON)
    real_md_before = sha256_file(REAL_OUT_MD)

    checks: list[dict[str, Any]] = []

    complete_status, complete_payload = run_case()
    complete_checks = {check.get("name"): check.get("passed") for check in complete_payload.get("checks", []) or []}
    temporary_fixture_ready = (
        complete_status == 0
        and complete_payload.get("passed") is True
        and complete_payload.get("not_external_evidence") is True
        and complete_payload.get("strict_evidence_ready") is False
        and len(complete_payload.get("missing_requirements", []) or []) == 4
        and complete_checks.get("gap_audit_has_four_external_blockers") is True
        and complete_checks.get("all_missing_requirements_mapped") is True
        and complete_checks.get("post_collection_strict_commands_cover_all_gates") is True
        and complete_checks.get("no_real_manifest_written") is True
    )
    add_check(
        checks,
        "temporary_fixture_builds_current_acquisition_packet",
        temporary_fixture_ready,
        f"status={complete_status}, actions={len(complete_payload.get('operator_actions', []) or [])}, blockers={len(complete_payload.get('missing_requirements', []) or [])}",
    )

    missing_status, missing_payload = run_case(remove_collection_readiness)
    missing_source_rejected = (
        missing_status != 0
        and missing_payload.get("passed") is False
        and check_named(missing_payload, "source_audits_exist") is False
        and check_named(missing_payload, "collection_preflight_fail_closed") is False
    )
    add_check(
        checks,
        "missing_source_report_rejected",
        missing_source_rejected,
        f"status={missing_status}, source_check={check_named(missing_payload, 'source_audits_exist')}, collection_check={check_named(missing_payload, 'collection_preflight_fail_closed')}",
    )

    unmapped_status, unmapped_payload = run_case(add_unmapped_blocker)
    unmapped_blocker_rejected = (
        unmapped_status != 0
        and unmapped_payload.get("passed") is False
        and check_named(unmapped_payload, "gap_audit_has_four_external_blockers") is False
        and check_named(unmapped_payload, "all_missing_requirements_mapped") is False
    )
    add_check(
        checks,
        "unmapped_blocker_rejected",
        unmapped_blocker_rejected,
        f"status={unmapped_status}, gap_check={check_named(unmapped_payload, 'gap_audit_has_four_external_blockers')}, mapped_check={check_named(unmapped_payload, 'all_missing_requirements_mapped')}",
    )

    manifest_status, manifest_payload = run_case(write_premature_manifest)
    premature_manifest_rejected = (
        manifest_status != 0
        and manifest_payload.get("passed") is False
        and check_named(manifest_payload, "no_real_manifest_written") is False
    )
    add_check(
        checks,
        "premature_manifest_rejected",
        premature_manifest_rejected,
        f"status={manifest_status}, no_manifest_check={check_named(manifest_payload, 'no_real_manifest_written')}",
    )

    collection_status, collection_payload = run_case(promote_collection_readiness)
    collection_readiness_drift_rejected = (
        collection_status != 0
        and collection_payload.get("passed") is False
        and check_named(collection_payload, "collection_preflight_fail_closed") is False
    )
    add_check(
        checks,
        "collection_readiness_drift_rejected",
        collection_readiness_drift_rejected,
        f"status={collection_status}, collection_check={check_named(collection_payload, 'collection_preflight_fail_closed')}",
    )

    real_json_after = sha256_file(REAL_OUT_JSON)
    real_md_after = sha256_file(REAL_OUT_MD)
    real_outputs_untouched = real_json_before == real_json_after and real_md_before == real_md_after
    add_check(
        checks,
        "real_repository_acquisition_outputs_untouched",
        real_outputs_untouched,
        f"json_before={real_json_before}, json_after={real_json_after}, md_before={real_md_before}, md_after={real_md_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_acquisition_packet_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "missing_source_rejected": missing_source_rejected,
        "unmapped_blocker_rejected": unmapped_blocker_rejected,
        "premature_manifest_rejected": premature_manifest_rejected,
        "collection_readiness_drift_rejected": collection_readiness_drift_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)

    print(
        "External acquisition packet self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; "
        f"missing_source_rejected={missing_source_rejected}; "
        f"unmapped_blocker_rejected={unmapped_blocker_rejected}; "
        f"manifest_rejected={premature_manifest_rejected}; "
        f"collection_drift_rejected={collection_readiness_drift_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

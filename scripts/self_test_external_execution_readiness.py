from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import audit_external_execution_readiness as execution


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_DOCS = REAL_ROOT / "docs"

OUT_JSON = REAL_RESULTS / "external_execution_readiness_self_test.json"
OUT_MD = REAL_RESULTS / "external_execution_readiness_self_test.md"
VERSION = "external_execution_readiness_self_test_v1"

REAL_OUTPUTS = [
    REAL_RESULTS / "external_execution_readiness_audit.json",
    REAL_RESULTS / "external_execution_readiness_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

EXTRA_FIXTURE_FILES = [
    REAL_EXTERNAL / "manifest_template.json",
    REAL_EXTERNAL / "render_failure_remediation_work_orders.csv",
    REAL_RESULTS / "external_operator_handoff_bundle.json",
    REAL_RESULTS / "external_operator_handoff_bundle.md",
    REAL_ROOT / "scripts" / "self_test_fidelity_acceptance_materializer.py",
    REAL_RESULTS / "external_runner_backend_self_test.json",
    REAL_RESULTS / "external_runner_backend_self_test.md",
    REAL_RESULTS / "fidelity_acceptance_materializer_self_test.json",
    REAL_RESULTS / "fidelity_acceptance_materializer_self_test.md",
    REAL_RESULTS / "maniskill_pilot_reset_timeout_triage.json",
    REAL_RESULTS / "maniskill_pilot_reset_timeout_triage.md",
    REAL_RESULTS / "maniskill_render_failure_remediation.json",
    REAL_RESULTS / "maniskill_render_failure_remediation.md",
    REAL_RESULTS / "external_manifest_builder_report.json",
    REAL_RESULTS / "external_manifest_builder_report.md",
    REAL_RESULTS / "external_config_evidence_audit.json",
    REAL_RESULTS / "external_config_evidence_audit.md",
    REAL_RESULTS / "external_adapter_contract_evidence_audit.json",
    REAL_RESULTS / "external_adapter_contract_evidence_audit.md",
    REAL_RESULTS / "external_rollout_metrics.json",
    REAL_RESULTS / "external_rollout_metrics.md",
    REAL_RESULTS / "external_evidence_audit.json",
    REAL_RESULTS / "external_evidence_audit.md",
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
        raise AssertionError(f"missing execution-readiness self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    handoff = read_json(REAL_RESULTS / "external_operator_handoff_bundle.json")
    for record in handoff.get("included_files", []) or []:
        if not isinstance(record, dict):
            continue
        path_text = str(record.get("path", "")).strip()
        if path_text:
            copy_file(REAL_ROOT / path_text, root / path_text)
    for source in EXTRA_FIXTURE_FILES:
        if source.exists():
            copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_execution(root: Path) -> dict[str, Any]:
    old = {
        "ROOT": execution.ROOT,
        "RESULTS": execution.RESULTS,
        "DOCS": execution.DOCS,
        "EXTERNAL": execution.EXTERNAL,
        "OUT_JSON": execution.OUT_JSON,
        "OUT_MD": execution.OUT_MD,
    }
    execution.ROOT = root
    execution.RESULTS = root / "results"
    execution.DOCS = root / "docs"
    execution.EXTERNAL = root / "external_validation"
    execution.OUT_JSON = execution.RESULTS / "external_execution_readiness_audit.json"
    execution.OUT_MD = execution.RESULTS / "external_execution_readiness_audit.md"
    return old


def restore_execution(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(execution, name, value)


def run_execution(root: Path) -> tuple[int, dict[str, Any], str]:
    old = patch_execution(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = execution.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_execution(old)
    payload_path = root / "results" / "external_execution_readiness_audit.json"
    payload = read_json(payload_path) if payload_path.exists() else {}
    return int(status), payload, buffer.getvalue()


def run_case(mutator: Callable[[Path], None] | None = None) -> tuple[int, dict[str, Any], str]:
    with tempfile.TemporaryDirectory(prefix="paper119_execution_readiness_selftest_") as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_execution(root)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_operator_packet(root: Path) -> None:
    (root / "results" / "external_operator_packet.json").unlink()


def remove_required_packet_file(root: Path) -> None:
    (root / "external_validation" / "collection_runbook.md").unlink()


def remove_linux_bootstrap(root: Path) -> None:
    (root / "external_validation" / "collection_machine_bootstrap.sh").unlink()


def remove_linux_collection_job_command(root: Path) -> None:
    (root / "external_validation" / "collection_job_commands.sh").unlink()


def write_premature_manifest(root: Path) -> None:
    write_json(
        root / "external_validation" / "manifest.json",
        {
            "version": "paper119_external_manifest_v1",
            "premature_execution_readiness_self_test": True,
        },
    )


def promote_strict_evidence(root: Path) -> None:
    path = root / "results" / "external_evidence_audit.json"
    payload = read_json(path)
    payload["submission_ready"] = True
    write_json(path, payload)


def remove_independence_phrase(root: Path) -> None:
    path = root / "docs" / "independent_validation_protocol.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("without relying on Haonan", "with unspecified collaboration routing")
    text = text.replace("Haonan", "an external collaborator")
    path.write_text(text, encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Execution Readiness Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Temporary fixture execution-ready: `{str(payload['temporary_fixture_execution_ready']).lower()}`.",
        f"Missing operator packet rejected: `{str(payload['missing_operator_packet_rejected']).lower()}`.",
        f"Missing required packet file rejected: `{str(payload['missing_required_packet_file_rejected']).lower()}`.",
        f"Missing Linux bootstrap rejected: `{str(payload['missing_linux_bootstrap_rejected']).lower()}`.",
        f"Missing Linux collection job command rejected: `{str(payload['missing_linux_collection_job_command_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Strict evidence promotion rejected: `{str(payload['strict_evidence_promotion_rejected']).lower()}`.",
        f"Haonan-dependence drift rejected: `{str(payload['haonan_dependence_drift_rejected']).lower()}`.",
        f"Real execution outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It runs the top-level external execution-readiness audit in temporary copied workspaces, proves the current operator packet is executable but still non-evidence, and proves missing packet sources, missing Linux bootstrap/collection-job commands, premature manifests, accidental strict-evidence promotion, and loss of the independent non-Haonan validation guarantee fail closed without touching the real execution-readiness reports.",
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
    checks: list[dict[str, Any]] = []
    real_hashes_before = real_output_hashes()

    fixture_status, fixture_payload, _ = run_case()
    temporary_fixture_execution_ready = (
        fixture_status == 0
        and fixture_payload.get("passed") is True
        and fixture_payload.get("execution_packet_ready") is True
        and fixture_payload.get("strict_evidence_ready") is False
        and int(fixture_payload.get("operator_rows", 0) or 0) >= 1440
        and check_named(fixture_payload, "strict_evidence_gates_remain_not_ready") is True
        and check_named(fixture_payload, "external_operator_packet_go_no_go") is True
        and check_named(fixture_payload, "external_operator_handoff_bundle_hash_manifest") is True
        and check_named(fixture_payload, "validation_path_independent_of_haonan") is True
    )
    add_check(
        checks,
        "temporary_fixture_execution_packet_ready_but_non_evidence",
        temporary_fixture_execution_ready,
        f"status={fixture_status}, passed={fixture_payload.get('passed')!r}, execution_ready={fixture_payload.get('execution_packet_ready')!r}, strict={fixture_payload.get('strict_evidence_ready')!r}",
    )

    missing_operator_status, missing_operator_payload, _ = run_case(remove_operator_packet)
    missing_operator_packet_rejected = (
        missing_operator_payload.get("passed") is False
        and missing_operator_payload.get("execution_packet_ready") is False
        and check_named(missing_operator_payload, "external_operator_packet_ready") is False
    )
    add_check(
        checks,
        "missing_operator_packet_rejected",
        missing_operator_packet_rejected,
        f"status={missing_operator_status}, operator_ready={check_named(missing_operator_payload, 'external_operator_packet_ready')}",
    )

    missing_file_status, missing_file_payload, _ = run_case(remove_required_packet_file)
    missing_required_packet_file_rejected = (
        missing_file_payload.get("passed") is False
        and missing_file_payload.get("execution_packet_ready") is False
        and check_named(missing_file_payload, "operator_packet_paths_exist") is False
    )
    add_check(
        checks,
        "missing_required_packet_file_rejected",
        missing_required_packet_file_rejected,
        f"status={missing_file_status}, paths_exist={check_named(missing_file_payload, 'operator_packet_paths_exist')}",
    )

    missing_linux_status, missing_linux_payload, _ = run_case(remove_linux_bootstrap)
    missing_linux_bootstrap_rejected = (
        missing_linux_payload.get("passed") is False
        and missing_linux_payload.get("execution_packet_ready") is False
        and check_named(missing_linux_payload, "operator_packet_paths_exist") is False
    )
    add_check(
        checks,
        "missing_linux_bootstrap_rejected",
        missing_linux_bootstrap_rejected,
        f"status={missing_linux_status}, paths_exist={check_named(missing_linux_payload, 'operator_packet_paths_exist')}",
    )

    missing_linux_job_status, missing_linux_job_payload, _ = run_case(remove_linux_collection_job_command)
    missing_linux_collection_job_command_rejected = (
        missing_linux_job_payload.get("passed") is False
        and missing_linux_job_payload.get("execution_packet_ready") is False
        and check_named(missing_linux_job_payload, "operator_packet_paths_exist") is False
    )
    add_check(
        checks,
        "missing_linux_collection_job_command_rejected",
        missing_linux_collection_job_command_rejected,
        f"status={missing_linux_job_status}, paths_exist={check_named(missing_linux_job_payload, 'operator_packet_paths_exist')}",
    )

    manifest_status, manifest_payload, _ = run_case(write_premature_manifest)
    premature_manifest_rejected = (
        manifest_payload.get("passed") is False
        and manifest_payload.get("execution_packet_ready") is False
        and check_named(manifest_payload, "no_real_manifest_written") is False
    )
    add_check(
        checks,
        "premature_manifest_rejected",
        premature_manifest_rejected,
        f"status={manifest_status}, no_real_manifest={check_named(manifest_payload, 'no_real_manifest_written')}",
    )

    strict_status, strict_payload, _ = run_case(promote_strict_evidence)
    strict_evidence_promotion_rejected = (
        strict_payload.get("passed") is False
        and strict_payload.get("strict_evidence_ready") is True
        and check_named(strict_payload, "strict_evidence_gates_remain_not_ready") is False
    )
    add_check(
        checks,
        "strict_evidence_promotion_rejected",
        strict_evidence_promotion_rejected,
        f"status={strict_status}, strict={strict_payload.get('strict_evidence_ready')!r}, gates_not_ready={check_named(strict_payload, 'strict_evidence_gates_remain_not_ready')}",
    )

    independence_status, independence_payload, _ = run_case(remove_independence_phrase)
    haonan_dependence_drift_rejected = (
        independence_payload.get("passed") is False
        and independence_payload.get("execution_packet_ready") is False
        and check_named(independence_payload, "validation_path_independent_of_haonan") is False
    )
    add_check(
        checks,
        "haonan_dependence_drift_rejected",
        haonan_dependence_drift_rejected,
        f"status={independence_status}, independent={check_named(independence_payload, 'validation_path_independent_of_haonan')}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(checks, "real_execution_outputs_untouched", real_outputs_untouched, f"before={real_hashes_before}, after={real_hashes_after}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_execution_ready": temporary_fixture_execution_ready,
        "missing_operator_packet_rejected": missing_operator_packet_rejected,
        "missing_required_packet_file_rejected": missing_required_packet_file_rejected,
        "missing_linux_bootstrap_rejected": missing_linux_bootstrap_rejected,
        "missing_linux_collection_job_command_rejected": missing_linux_collection_job_command_rejected,
        "premature_manifest_rejected": premature_manifest_rejected,
        "strict_evidence_promotion_rejected": strict_evidence_promotion_rejected,
        "haonan_dependence_drift_rejected": haonan_dependence_drift_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External execution readiness self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_execution_ready}; "
        f"missing_operator_rejected={missing_operator_packet_rejected}; "
        f"missing_file_rejected={missing_required_packet_file_rejected}; "
        f"missing_linux_rejected={missing_linux_bootstrap_rejected}; "
        f"missing_linux_job_rejected={missing_linux_collection_job_command_rejected}; "
        f"manifest_rejected={premature_manifest_rejected}; "
        f"strict_promotion_rejected={strict_evidence_promotion_rejected}; "
        f"haonan_drift_rejected={haonan_dependence_drift_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

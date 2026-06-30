from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_operator_handoff_bundle as handoff


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"

REAL_OUTPUTS = [
    REAL_RESULTS / "external_operator_handoff_bundle.json",
    REAL_RESULTS / "external_operator_handoff_bundle.md",
]

OUT_JSON = REAL_RESULTS / "external_operator_handoff_bundle_self_test.json"
OUT_MD = REAL_RESULTS / "external_operator_handoff_bundle_self_test.md"


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
        raise AssertionError(f"missing handoff self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    # Use the builder's real manifest as the fixture definition so the self-test
    # follows the operator bundle rather than duplicating its file list.
    for rel_path in handoff.build_file_manifest():
        copy_file(REAL_ROOT / rel_path, root / rel_path)


def payload_from_temp(root: Path) -> dict[str, Any]:
    path = root / "results" / "external_operator_handoff_bundle.json"
    if path.exists():
        return read_json(path)
    return {"passed": False, "checks": []}


def run_builder(
    root: Path,
    *,
    add_forbidden_path: bool = False,
    remove_collection_job_packet: bool = False,
    remove_machine_bootstrap: bool = False,
) -> tuple[int, dict[str, Any]]:
    original = (
        handoff.ROOT,
        handoff.DOCS,
        handoff.EXTERNAL,
        handoff.RESULTS,
        handoff.SCRIPTS,
        handoff.OUT_JSON,
        handoff.OUT_MD,
        handoff.build_file_manifest,
    )
    original_build_file_manifest = handoff.build_file_manifest
    try:
        handoff.ROOT = root
        handoff.DOCS = root / "docs"
        handoff.EXTERNAL = root / "external_validation"
        handoff.RESULTS = root / "results"
        handoff.SCRIPTS = root / "scripts"
        handoff.OUT_JSON = handoff.RESULTS / "external_operator_handoff_bundle.json"
        handoff.OUT_MD = handoff.RESULTS / "external_operator_handoff_bundle.md"

        if add_forbidden_path or remove_collection_job_packet or remove_machine_bootstrap:

            def mutated_manifest() -> dict[str, str]:
                files = original_build_file_manifest()
                if add_forbidden_path:
                    evidence_log = handoff.EXTERNAL / "logs" / "synthetic_self_test.jsonl"
                    evidence_log.parent.mkdir(parents=True, exist_ok=True)
                    evidence_log.write_text('{"synthetic_self_test_only": true}\n', encoding="utf-8")
                    files["external_validation/logs/synthetic_self_test.jsonl"] = "generated_non_evidence_report"
                if remove_collection_job_packet:
                    for key in (
                        "external_validation/collection_job_packet.json",
                        "external_validation/collection_job_packet.md",
                        "external_validation/collection_job_commands.ps1",
                        "external_validation/collection_job_checklist.csv",
                        "results/external_collection_job_packet_audit.json",
                        "results/external_collection_job_packet_audit.md",
                        "scripts/build_external_collection_job_packet.py",
                    ):
                        files.pop(key, None)
                if remove_machine_bootstrap:
                    for key in (
                        "external_validation/collection_machine_bootstrap.json",
                        "external_validation/collection_machine_bootstrap.md",
                        "external_validation/collection_machine_bootstrap.ps1",
                        "external_validation/collection_machine_bootstrap.sh",
                        "results/external_collection_machine_bootstrap_audit.json",
                        "results/external_collection_machine_bootstrap_audit.md",
                        "scripts/build_external_collection_machine_bootstrap.py",
                    ):
                        files.pop(key, None)
                return files

            handoff.build_file_manifest = mutated_manifest

        with redirect_stdout(io.StringIO()):
            try:
                status = handoff.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                payload = payload_from_temp(root)
                payload["error"] = str(exc)
                return code, payload
        return status, payload_from_temp(root)
    finally:
        (
            handoff.ROOT,
            handoff.DOCS,
            handoff.EXTERNAL,
            handoff.RESULTS,
            handoff.SCRIPTS,
            handoff.OUT_JSON,
            handoff.OUT_MD,
            handoff.build_file_manifest,
        ) = original


def run_case(
    mutator: Callable[[Path], None] | None = None,
    *,
    add_forbidden_path: bool = False,
    remove_collection_job_packet: bool = False,
    remove_machine_bootstrap: bool = False,
) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_handoff_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_builder(
            root,
            add_forbidden_path=add_forbidden_path,
            remove_collection_job_packet=remove_collection_job_packet,
            remove_machine_bootstrap=remove_machine_bootstrap,
        )


def check_named(payload: dict[str, Any], name: str) -> bool | None:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed") is True
    return None


def remove_operator_packet(root: Path) -> None:
    (root / "results" / "external_operator_packet.json").unlink()


def promote_operator_packet(root: Path) -> None:
    path = root / "results" / "external_operator_packet.json"
    payload = read_json(path)
    payload["start_state"] = "READY_TO_COLLECT"
    payload["strict_evidence_ready"] = True
    write_json(path, payload)


def shrink_acquisition_blockers(root: Path) -> None:
    path = root / "results" / "external_acquisition_packet.json"
    payload = read_json(path)
    payload["missing_requirements"] = []
    write_json(path, payload)


def promote_strict_evidence_gate(root: Path) -> None:
    path = root / "results" / "external_evidence_preflight.json"
    payload = read_json(path)
    payload["evidence_ready"] = True
    write_json(path, payload)


def delete_included_file(root: Path) -> None:
    (root / "external_validation" / "collection_job_packet.md").unlink()


def write_premature_manifest(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Operator Handoff Bundle Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Missing source rejected: `{str(payload['missing_source_rejected']).lower()}`.",
        f"No-go drift rejected: `{str(payload['no_go_drift_rejected']).lower()}`.",
        f"Acquisition blocker drift rejected: `{str(payload['acquisition_blocker_drift_rejected']).lower()}`.",
        f"Strict evidence drift rejected: `{str(payload['strict_evidence_drift_rejected']).lower()}`.",
        f"Missing included file rejected: `{str(payload['missing_included_file_rejected']).lower()}`.",
        f"Forbidden evidence path rejected: `{str(payload['forbidden_evidence_path_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Missing collection job rejected: `{str(payload['missing_collection_job_rejected']).lower()}`.",
        f"Missing machine bootstrap rejected: `{str(payload['missing_machine_bootstrap_rejected']).lower()}`.",
        f"Real handoff outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It rebuilds the operator handoff bundle in temporary copied workspaces and proves the handoff fails closed when source packets are missing, the no-go stance drifts, acquisition blockers disappear prematurely, strict evidence gates flip ready, included files are missing, forbidden evidence paths are inserted, a real manifest appears, or the collection job/bootstrap packets are omitted.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    real_hashes_before = real_output_hashes()
    checks: list[dict[str, Any]] = []

    complete_status, complete_payload = run_case()
    complete_checks = {check.get("name"): check.get("passed") for check in complete_payload.get("checks", []) or []}
    temporary_fixture_ready = (
        complete_status == 0
        and complete_payload.get("version") == "external_operator_handoff_bundle_v1"
        and complete_payload.get("passed") is True
        and complete_payload.get("not_external_evidence") is True
        and complete_payload.get("strict_evidence_ready") is False
        and complete_payload.get("start_state") == "DO_NOT_COLLECT_YET"
        and int(complete_payload.get("included_file_count", 0) or 0) >= 300
        and not complete_payload.get("forbidden_included_paths")
        and not complete_payload.get("missing_files")
        and complete_checks.get("operator_packet_is_no_go_non_evidence") is True
        and complete_checks.get("acquisition_maps_all_remaining_blockers") is True
        and complete_checks.get("strict_evidence_gates_remain_fail_closed") is True
        and complete_checks.get("bundle_files_exist") is True
        and complete_checks.get("bundle_excludes_rollout_evidence_artifacts") is True
        and complete_checks.get("no_real_manifest_written") is True
        and complete_checks.get("external_collection_job_packet_included") is True
        and complete_checks.get("collection_machine_bootstrap_included") is True
        and complete_checks.get("file_hashes_are_recorded") is True
    )
    add_check(
        checks,
        "temporary_fixture_builds_current_handoff_bundle",
        temporary_fixture_ready,
        f"status={complete_status}, files={complete_payload.get('included_file_count')!r}, start_state={complete_payload.get('start_state')!r}",
    )

    missing_status, missing_payload = run_case(remove_operator_packet)
    missing_source_rejected = missing_status != 0 and "external_operator_packet.json" in str(missing_payload.get("error", ""))
    add_check(checks, "missing_source_rejected", missing_source_rejected, f"status={missing_status}, error={missing_payload.get('error', '')!r}")

    no_go_status, no_go_payload = run_case(promote_operator_packet)
    no_go_drift_rejected = (
        no_go_status != 0
        and no_go_payload.get("passed") is False
        and check_named(no_go_payload, "operator_packet_is_no_go_non_evidence") is False
    )
    add_check(checks, "no_go_drift_rejected", no_go_drift_rejected, f"status={no_go_status}, no_go_check={check_named(no_go_payload, 'operator_packet_is_no_go_non_evidence')}")

    acquisition_status, acquisition_payload = run_case(shrink_acquisition_blockers)
    acquisition_blocker_drift_rejected = (
        acquisition_status != 0
        and acquisition_payload.get("passed") is False
        and check_named(acquisition_payload, "acquisition_maps_all_remaining_blockers") is False
    )
    add_check(checks, "acquisition_blocker_drift_rejected", acquisition_blocker_drift_rejected, f"status={acquisition_status}, acquisition_check={check_named(acquisition_payload, 'acquisition_maps_all_remaining_blockers')}")

    strict_status, strict_payload = run_case(promote_strict_evidence_gate)
    strict_evidence_drift_rejected = (
        strict_status != 0
        and strict_payload.get("passed") is False
        and check_named(strict_payload, "strict_evidence_gates_remain_fail_closed") is False
    )
    add_check(checks, "strict_evidence_drift_rejected", strict_evidence_drift_rejected, f"status={strict_status}, strict_check={check_named(strict_payload, 'strict_evidence_gates_remain_fail_closed')}")

    file_status, file_payload = run_case(delete_included_file)
    missing_included_file_rejected = (
        file_status != 0
        and file_payload.get("passed") is False
        and check_named(file_payload, "bundle_files_exist") is False
    )
    add_check(checks, "missing_included_file_rejected", missing_included_file_rejected, f"status={file_status}, files_check={check_named(file_payload, 'bundle_files_exist')}")

    forbidden_status, forbidden_payload = run_case(add_forbidden_path=True)
    forbidden_evidence_path_rejected = (
        forbidden_status != 0
        and forbidden_payload.get("passed") is False
        and check_named(forbidden_payload, "bundle_excludes_rollout_evidence_artifacts") is False
    )
    add_check(checks, "forbidden_evidence_path_rejected", forbidden_evidence_path_rejected, f"status={forbidden_status}, forbidden_check={check_named(forbidden_payload, 'bundle_excludes_rollout_evidence_artifacts')}")

    manifest_status, manifest_payload = run_case(write_premature_manifest)
    premature_manifest_rejected = (
        manifest_status != 0
        and manifest_payload.get("passed") is False
        and check_named(manifest_payload, "no_real_manifest_written") is False
    )
    add_check(checks, "premature_manifest_rejected", premature_manifest_rejected, f"status={manifest_status}, manifest_check={check_named(manifest_payload, 'no_real_manifest_written')}")

    job_status, job_payload = run_case(remove_collection_job_packet=True)
    missing_collection_job_rejected = (
        job_status != 0
        and job_payload.get("passed") is False
        and check_named(job_payload, "external_collection_job_packet_included") is False
    )
    add_check(checks, "missing_collection_job_rejected", missing_collection_job_rejected, f"status={job_status}, job_check={check_named(job_payload, 'external_collection_job_packet_included')}")

    bootstrap_status, bootstrap_payload = run_case(remove_machine_bootstrap=True)
    missing_machine_bootstrap_rejected = (
        bootstrap_status != 0
        and bootstrap_payload.get("passed") is False
        and check_named(bootstrap_payload, "collection_machine_bootstrap_included") is False
    )
    add_check(checks, "missing_machine_bootstrap_rejected", missing_machine_bootstrap_rejected, f"status={bootstrap_status}, bootstrap_check={check_named(bootstrap_payload, 'collection_machine_bootstrap_included')}")

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(checks, "real_repository_handoff_outputs_untouched", real_outputs_untouched, f"before={real_hashes_before}, after={real_hashes_after}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_operator_handoff_bundle_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "missing_source_rejected": missing_source_rejected,
        "no_go_drift_rejected": no_go_drift_rejected,
        "acquisition_blocker_drift_rejected": acquisition_blocker_drift_rejected,
        "strict_evidence_drift_rejected": strict_evidence_drift_rejected,
        "missing_included_file_rejected": missing_included_file_rejected,
        "forbidden_evidence_path_rejected": forbidden_evidence_path_rejected,
        "premature_manifest_rejected": premature_manifest_rejected,
        "missing_collection_job_rejected": missing_collection_job_rejected,
        "missing_machine_bootstrap_rejected": missing_machine_bootstrap_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(
        "External operator handoff bundle self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; "
        f"missing_source_rejected={missing_source_rejected}; "
        f"no_go_drift_rejected={no_go_drift_rejected}; "
        f"acquisition_drift_rejected={acquisition_blocker_drift_rejected}; "
        f"strict_drift_rejected={strict_evidence_drift_rejected}; "
        f"missing_file_rejected={missing_included_file_rejected}; "
        f"forbidden_rejected={forbidden_evidence_path_rejected}; "
        f"manifest_rejected={premature_manifest_rejected}; "
        f"collection_job_rejected={missing_collection_job_rejected}; "
        f"bootstrap_rejected={missing_machine_bootstrap_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

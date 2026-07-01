from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_collection_job_packet as collection_job


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "collection_job_packet.json",
    REAL_EXTERNAL / "collection_job_packet.md",
    REAL_EXTERNAL / "collection_job_commands.ps1",
    REAL_EXTERNAL / "collection_job_commands.sh",
    REAL_EXTERNAL / "collection_job_checklist.csv",
    REAL_RESULTS / "external_collection_job_packet_audit.json",
    REAL_RESULTS / "external_collection_job_packet_audit.md",
]

OUT_JSON = REAL_RESULTS / "external_collection_job_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_collection_job_packet_self_test.md"

RESULT_FIXTURES = [
    "external_operator_packet.json",
    "external_collection_readiness_audit.json",
    "maniskill_render_machine_qualification.json",
    "maniskill_render_machine_qualification_self_test.json",
    "external_evidence_intake_ledger_audit.json",
    "external_precollection_manifest_draft_audit.json",
    "external_precollection_freeze_receipt_audit.json",
    "external_postcollection_evidence_seal_audit.json",
    "external_postcollection_seal_consistency_audit.json",
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
        raise AssertionError(f"missing collection-job self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "external_validation").mkdir(parents=True, exist_ok=True)
    for name in RESULT_FIXTURES:
        copy_file(REAL_RESULTS / name, root / "results" / name)


def audit_payload_from_temp(root: Path) -> dict[str, Any]:
    audit_path = root / "results" / "external_collection_job_packet_audit.json"
    packet_path = root / "external_validation" / "collection_job_packet.json"
    if audit_path.exists():
        return read_json(audit_path)
    if packet_path.exists():
        return read_json(packet_path)
    return {"passed": False, "checks": []}


def run_builder(root: Path, *, unsafe_command_spine: bool = False) -> tuple[int, dict[str, Any]]:
    original = (
        collection_job.ROOT,
        collection_job.RESULTS,
        collection_job.EXTERNAL,
        collection_job.OUT_PACKET_JSON,
        collection_job.OUT_PACKET_MD,
        collection_job.OUT_COMMANDS,
        collection_job.OUT_COMMANDS_SH,
        collection_job.OUT_CHECKLIST,
        collection_job.OUT_AUDIT_JSON,
        collection_job.OUT_AUDIT_MD,
        collection_job.build_command_file,
        collection_job.build_bash_command_file,
        collection_job.write_outputs,
    )
    original_build_command_file = collection_job.build_command_file
    original_build_bash_command_file = collection_job.build_bash_command_file
    original_write_outputs = collection_job.write_outputs
    try:
        collection_job.ROOT = root
        collection_job.RESULTS = root / "results"
        collection_job.EXTERNAL = root / "external_validation"
        collection_job.OUT_PACKET_JSON = collection_job.EXTERNAL / "collection_job_packet.json"
        collection_job.OUT_PACKET_MD = collection_job.EXTERNAL / "collection_job_packet.md"
        collection_job.OUT_COMMANDS = collection_job.EXTERNAL / "collection_job_commands.ps1"
        collection_job.OUT_COMMANDS_SH = collection_job.EXTERNAL / "collection_job_commands.sh"
        collection_job.OUT_CHECKLIST = collection_job.EXTERNAL / "collection_job_checklist.csv"
        collection_job.OUT_AUDIT_JSON = collection_job.RESULTS / "external_collection_job_packet_audit.json"
        collection_job.OUT_AUDIT_MD = collection_job.RESULTS / "external_collection_job_packet_audit.md"

        if unsafe_command_spine:

            def unsafe_command_file() -> str:
                return (
                    original_build_command_file()
                    .replace("-ConfirmOfficialCollection", "-ConfirmCollectionShortcut")
                    .replace("Assert-NoPlaceholder", "Assert-PlaceholderShortcut")
                )

            def unsafe_bash_command_file() -> str:
                return (
                    original_build_bash_command_file()
                    .replace("--confirm-official-collection", "--confirm-collection-shortcut")
                    .replace("require_real_value", "skip_real_value")
                )

            collection_job.build_command_file = unsafe_command_file
            collection_job.build_bash_command_file = unsafe_bash_command_file

        with redirect_stdout(io.StringIO()):
            try:
                status = collection_job.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                payload = audit_payload_from_temp(root)
                payload["error"] = str(exc)
                return code, payload
        payload = audit_payload_from_temp(root)
        if status == 0 and not collection_job.OUT_COMMANDS_SH.exists():
            payload["passed"] = False
            payload["error"] = "missing external_validation/collection_job_commands.sh"
            return 1, payload
        return status, payload
    finally:
        (
            collection_job.ROOT,
            collection_job.RESULTS,
            collection_job.EXTERNAL,
            collection_job.OUT_PACKET_JSON,
            collection_job.OUT_PACKET_MD,
            collection_job.OUT_COMMANDS,
            collection_job.OUT_COMMANDS_SH,
            collection_job.OUT_CHECKLIST,
            collection_job.OUT_AUDIT_JSON,
            collection_job.OUT_AUDIT_MD,
            collection_job.build_command_file,
            collection_job.build_bash_command_file,
            collection_job.write_outputs,
        ) = original


def check_named(payload: dict[str, Any], name: str) -> bool | None:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed") is True
    return None


def run_case(
    mutator: Callable[[Path], None] | None = None,
    *,
    unsafe_command_spine: bool = False,
    skip_linux_command_write: bool = False,
) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_collection_job_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        if skip_linux_command_write:
            original_write_outputs = collection_job.write_outputs

            def skip_linux_command(packet: dict[str, Any]) -> None:
                original_write_outputs(packet)
                (root / "external_validation" / "collection_job_commands.sh").unlink(missing_ok=True)

            collection_job.write_outputs = skip_linux_command
        try:
            return run_builder(root, unsafe_command_spine=unsafe_command_spine)
        finally:
            if skip_linux_command_write:
                collection_job.write_outputs = original_write_outputs


def remove_operator_packet(root: Path) -> None:
    (root / "results" / "external_operator_packet.json").unlink()


def write_premature_manifest(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def promote_ready_state(root: Path) -> None:
    operator_path = root / "results" / "external_operator_packet.json"
    operator = read_json(operator_path)
    operator["start_state"] = "READY_TO_COLLECT"
    operator["strict_evidence_ready"] = True
    write_json(operator_path, operator)

    collection_path = root / "results" / "external_collection_readiness_audit.json"
    collection = read_json(collection_path)
    collection["collection_ready"] = True
    write_json(collection_path, collection)

    render_path = root / "results" / "maniskill_render_machine_qualification.json"
    render_machine = read_json(render_path)
    render_machine["render_machine_qualified"] = True
    write_json(render_path, render_machine)


def promote_hash_gates(root: Path) -> None:
    freeze_path = root / "results" / "external_precollection_freeze_receipt_audit.json"
    freeze = read_json(freeze_path)
    freeze["freeze_receipt_ready"] = True
    write_json(freeze_path, freeze)

    seal_path = root / "results" / "external_postcollection_evidence_seal_audit.json"
    seal = read_json(seal_path)
    seal["postcollection_seal_ready"] = True
    write_json(seal_path, seal)

    consistency_path = root / "results" / "external_postcollection_seal_consistency_audit.json"
    consistency = read_json(consistency_path)
    consistency["seal_consistency_ready"] = True
    write_json(consistency_path, consistency)


def degrade_render_self_test(root: Path) -> None:
    path = root / "results" / "maniskill_render_machine_qualification_self_test.json"
    payload = read_json(path)
    payload["diagnostic_fallback_rejected"] = False
    write_json(path, payload)


def mark_source_as_evidence(root: Path) -> None:
    path = root / "results" / "external_operator_packet.json"
    payload = read_json(path)
    payload["not_external_evidence"] = False
    write_json(path, payload)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in REAL_OUTPUTS}


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Collection Job Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Missing source rejected: `{str(payload['missing_source_rejected']).lower()}`.",
        f"Source evidence drift rejected: `{str(payload['source_evidence_drift_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Premature ready state rejected: `{str(payload['premature_ready_state_rejected']).lower()}`.",
        f"Unsafe command spine rejected: `{str(payload['unsafe_command_spine_rejected']).lower()}`.",
        f"Missing Linux command spine rejected: `{str(payload['missing_linux_command_spine_rejected']).lower()}`.",
        f"Hash gate drift rejected: `{str(payload['hash_gate_drift_rejected']).lower()}`.",
        f"Render self-test drift rejected: `{str(payload['render_self_test_drift_rejected']).lower()}`.",
        f"Real collection job outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It rebuilds the collection job packet in temporary copied workspaces, then proves missing sources, source non-evidence drift, premature manifest presence, premature ready-state promotion, unsafe command-spine edits, missing Linux command-spine output, hash-gate drift, and render-machine self-test drift fail closed without touching the real collection job packet.",
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
        and complete_payload.get("version") == "external_collection_job_packet_audit_v1"
        and complete_payload.get("passed") is True
        and complete_payload.get("not_external_evidence") is True
        and complete_payload.get("strict_external_evidence_ready") is False
        and complete_payload.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and len(complete_payload.get("job_steps", []) or []) >= 17
        and complete_checks.get("job_packet_is_non_evidence") is True
        and complete_checks.get("job_state_fail_closed_until_render_and_collection_ready") is True
        and complete_checks.get("command_sequence_covers_full_external_validation_route") is True
        and complete_checks.get("official_collection_commands_guarded") is True
        and complete_checks.get("linux_command_spine_uses_lf_line_endings") is True
        and complete_checks.get("no_real_manifest_written") is True
        and "external_validation/collection_job_commands.sh" in (complete_payload.get("command_files", []) or [])
    )
    add_check(
        checks,
        "temporary_fixture_builds_current_collection_job_packet",
        temporary_fixture_ready,
        f"status={complete_status}, job_state={complete_payload.get('job_state')!r}, steps={len(complete_payload.get('job_steps', []) or [])}",
    )

    missing_status, missing_payload = run_case(remove_operator_packet)
    missing_source_rejected = missing_status != 0 and "external_operator_packet.json" in str(missing_payload.get("error", ""))
    add_check(
        checks,
        "missing_source_payload_rejected",
        missing_source_rejected,
        f"status={missing_status}, error={missing_payload.get('error', '')!r}",
    )

    source_status, source_payload = run_case(mark_source_as_evidence)
    source_evidence_drift_rejected = (
        source_status != 0
        and source_payload.get("passed") is False
        and check_named(source_payload, "source_payloads_loaded") is False
    )
    add_check(
        checks,
        "source_non_evidence_drift_rejected",
        source_evidence_drift_rejected,
        f"status={source_status}, source_check={check_named(source_payload, 'source_payloads_loaded')}",
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

    ready_status, ready_payload = run_case(promote_ready_state)
    premature_ready_state_rejected = (
        ready_status != 0
        and ready_payload.get("passed") is False
        and ready_payload.get("job_state") == "READY_FOR_OPERATOR_CONFIRMED_COLLECTION"
        and check_named(ready_payload, "job_state_fail_closed_until_render_and_collection_ready") is False
    )
    add_check(
        checks,
        "premature_ready_state_rejected",
        premature_ready_state_rejected,
        f"status={ready_status}, job_state={ready_payload.get('job_state')!r}, fail_closed_check={check_named(ready_payload, 'job_state_fail_closed_until_render_and_collection_ready')}",
    )

    command_status, command_payload = run_case(unsafe_command_spine=True)
    unsafe_command_spine_rejected = (
        command_status != 0
        and command_payload.get("passed") is False
        and check_named(command_payload, "official_collection_commands_guarded") is False
    )
    add_check(
        checks,
        "unsafe_command_spine_rejected",
        unsafe_command_spine_rejected,
        f"status={command_status}, command_guard_check={check_named(command_payload, 'official_collection_commands_guarded')}",
    )

    linux_status, linux_payload = run_case(skip_linux_command_write=True)
    missing_linux_command_spine_rejected = (
        linux_status != 0
        and linux_payload.get("passed") is False
        and "collection_job_commands.sh" in str(linux_payload.get("error", ""))
    )
    add_check(
        checks,
        "missing_linux_command_spine_rejected",
        missing_linux_command_spine_rejected,
        f"status={linux_status}, error={linux_payload.get('error', '')!r}",
    )

    hash_status, hash_payload = run_case(promote_hash_gates)
    hash_gate_drift_rejected = (
        hash_status != 0
        and hash_payload.get("passed") is False
        and check_named(hash_payload, "pre_and_postcollection_hash_gates_present") is False
    )
    add_check(
        checks,
        "hash_gate_drift_rejected",
        hash_gate_drift_rejected,
        f"status={hash_status}, hash_gate_check={check_named(hash_payload, 'pre_and_postcollection_hash_gates_present')}",
    )

    render_status, render_payload = run_case(degrade_render_self_test)
    render_self_test_drift_rejected = (
        render_status != 0
        and render_payload.get("passed") is False
        and check_named(render_payload, "render_machine_self_test_proves_ready_and_fail_closed_cases") is False
    )
    add_check(
        checks,
        "render_self_test_drift_rejected",
        render_self_test_drift_rejected,
        f"status={render_status}, render_self_test_check={check_named(render_payload, 'render_machine_self_test_proves_ready_and_fail_closed_cases')}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_repository_collection_job_outputs_untouched",
        real_outputs_untouched,
        f"before={real_hashes_before}, after={real_hashes_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_collection_job_packet_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "missing_source_rejected": missing_source_rejected,
        "source_evidence_drift_rejected": source_evidence_drift_rejected,
        "premature_manifest_rejected": premature_manifest_rejected,
        "premature_ready_state_rejected": premature_ready_state_rejected,
        "unsafe_command_spine_rejected": unsafe_command_spine_rejected,
        "missing_linux_command_spine_rejected": missing_linux_command_spine_rejected,
        "hash_gate_drift_rejected": hash_gate_drift_rejected,
        "render_self_test_drift_rejected": render_self_test_drift_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)

    print(
        "External collection job packet self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; "
        f"missing_source_rejected={missing_source_rejected}; "
        f"source_drift_rejected={source_evidence_drift_rejected}; "
        f"manifest_rejected={premature_manifest_rejected}; "
        f"ready_state_rejected={premature_ready_state_rejected}; "
        f"unsafe_command_rejected={unsafe_command_spine_rejected}; "
        f"missing_linux_command_rejected={missing_linux_command_spine_rejected}; "
        f"hash_drift_rejected={hash_gate_drift_rejected}; "
        f"render_drift_rejected={render_self_test_drift_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

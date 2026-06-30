from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_collection_machine_bootstrap as bootstrap


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "collection_machine_bootstrap.json",
    REAL_EXTERNAL / "collection_machine_bootstrap.md",
    REAL_EXTERNAL / "collection_machine_bootstrap.ps1",
    REAL_RESULTS / "external_collection_machine_bootstrap_audit.json",
    REAL_RESULTS / "external_collection_machine_bootstrap_audit.md",
]

OUT_JSON = REAL_RESULTS / "external_collection_machine_bootstrap_self_test.json"
OUT_MD = REAL_RESULTS / "external_collection_machine_bootstrap_self_test.md"

RESULT_FIXTURES = [
    "external_platform_onboarding_audit.json",
    "external_platform_probe.json",
    "maniskill_task_binding_probe.json",
    "maniskill_env_smoke_probe.json",
    "maniskill_fidelity_metadata_probe.json",
    "maniskill_render_video_preflight_audit.json",
    "maniskill_pilot_runtime_liveness_audit.json",
    "maniskill_render_machine_qualification.json",
    "external_collection_job_packet_audit.json",
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
        raise AssertionError(f"missing collection-machine bootstrap self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "external_validation").mkdir(parents=True, exist_ok=True)
    for name in RESULT_FIXTURES:
        copy_file(REAL_RESULTS / name, root / "results" / name)


def payload_from_temp(root: Path) -> dict[str, Any]:
    audit_path = root / "results" / "external_collection_machine_bootstrap_audit.json"
    packet_path = root / "external_validation" / "collection_machine_bootstrap.json"
    if audit_path.exists():
        return read_json(audit_path)
    if packet_path.exists():
        return read_json(packet_path)
    return {"passed": False, "checks": []}


def run_builder(
    root: Path,
    *,
    unsafe_command: bool = False,
    missing_confirmation: bool = False,
    missing_install_guidance: bool = False,
) -> tuple[int, dict[str, Any]]:
    original = (
        bootstrap.ROOT,
        bootstrap.RESULTS,
        bootstrap.EXTERNAL,
        bootstrap.OUT_PACKET_JSON,
        bootstrap.OUT_PACKET_MD,
        bootstrap.OUT_COMMANDS,
        bootstrap.OUT_AUDIT_JSON,
        bootstrap.OUT_AUDIT_MD,
        bootstrap.write_command_file,
    )
    original_write_command_file = bootstrap.write_command_file
    try:
        bootstrap.ROOT = root
        bootstrap.RESULTS = root / "results"
        bootstrap.EXTERNAL = root / "external_validation"
        bootstrap.OUT_PACKET_JSON = bootstrap.EXTERNAL / "collection_machine_bootstrap.json"
        bootstrap.OUT_PACKET_MD = bootstrap.EXTERNAL / "collection_machine_bootstrap.md"
        bootstrap.OUT_COMMANDS = bootstrap.EXTERNAL / "collection_machine_bootstrap.ps1"
        bootstrap.OUT_AUDIT_JSON = bootstrap.RESULTS / "external_collection_machine_bootstrap_audit.json"
        bootstrap.OUT_AUDIT_MD = bootstrap.RESULTS / "external_collection_machine_bootstrap_audit.md"

        if unsafe_command or missing_confirmation or missing_install_guidance:

            def mutated_command_file() -> str:
                text = original_write_command_file()
                if unsafe_command:
                    text += "\nInvoke-Native python external_validation\\runner\\real_collection_runner.py\n"
                    text += "Invoke-Native python scripts\\build_external_manifest.py --write\n"
                if missing_confirmation:
                    text = (
                        text.replace("ConfirmBootstrapOnly", "BootstrapOnlyShortcut")
                        .replace("Refusing to bootstrap silently", "Bootstrap shortcut")
                        .replace("This script does not collect official evidence", "Shortcut mode")
                    )
                if missing_install_guidance:
                    text = text.replace("mani_skill", "missing_skill_package")
                bootstrap.OUT_COMMANDS.write_text(text, encoding="utf-8")
                return text

            bootstrap.write_command_file = mutated_command_file

        with redirect_stdout(io.StringIO()):
            try:
                status = bootstrap.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                payload = payload_from_temp(root)
                payload["error"] = str(exc)
                return code, payload
        return status, payload_from_temp(root)
    finally:
        (
            bootstrap.ROOT,
            bootstrap.RESULTS,
            bootstrap.EXTERNAL,
            bootstrap.OUT_PACKET_JSON,
            bootstrap.OUT_PACKET_MD,
            bootstrap.OUT_COMMANDS,
            bootstrap.OUT_AUDIT_JSON,
            bootstrap.OUT_AUDIT_MD,
            bootstrap.write_command_file,
        ) = original


def run_case(
    mutator: Callable[[Path], None] | None = None,
    *,
    unsafe_command: bool = False,
    missing_confirmation: bool = False,
    missing_install_guidance: bool = False,
) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_bootstrap_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_builder(
            root,
            unsafe_command=unsafe_command,
            missing_confirmation=missing_confirmation,
            missing_install_guidance=missing_install_guidance,
        )


def check_named(payload: dict[str, Any], name: str) -> bool | None:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed") is True
    return None


def remove_onboarding_report(root: Path) -> None:
    (root / "results" / "external_platform_onboarding_audit.json").unlink()


def mark_onboarding_as_evidence(root: Path) -> None:
    path = root / "results" / "external_platform_onboarding_audit.json"
    payload = read_json(path)
    payload["not_external_evidence"] = False
    write_json(path, payload)


def promote_collection_job(root: Path) -> None:
    path = root / "results" / "external_collection_job_packet_audit.json"
    payload = read_json(path)
    payload["job_state"] = "READY_FOR_OPERATOR_CONFIRMED_COLLECTION"
    write_json(path, payload)


def promote_local_render_machine(root: Path) -> None:
    path = root / "results" / "maniskill_render_machine_qualification.json"
    payload = read_json(path)
    payload["render_machine_qualified"] = True
    payload["qualification_state"] = "QUALIFIED_FOR_RENDER_BACKED_PILOT"
    write_json(path, payload)


def write_premature_outputs(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})
    log_path = root / "external_validation" / "logs" / "synthetic.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text('{"synthetic_self_test_only": true}\n', encoding="utf-8")
    video_path = root / "external_validation" / "videos" / "synthetic.mp4"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    video_path.write_bytes(b"not a real mp4")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Collection Machine Bootstrap Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Missing source rejected: `{str(payload['missing_source_rejected']).lower()}`.",
        f"Source evidence drift rejected: `{str(payload['source_evidence_drift_rejected']).lower()}`.",
        f"Collection-job go-state rejected: `{str(payload['collection_job_go_state_rejected']).lower()}`.",
        f"Local machine promotion rejected: `{str(payload['local_machine_promotion_rejected']).lower()}`.",
        f"Unsafe command rejected: `{str(payload['unsafe_command_rejected']).lower()}`.",
        f"Missing confirmation rejected: `{str(payload['missing_confirmation_rejected']).lower()}`.",
        f"Install guidance drift rejected: `{str(payload['install_guidance_drift_rejected']).lower()}`.",
        f"Premature outputs rejected: `{str(payload['premature_outputs_rejected']).lower()}`.",
        f"Real bootstrap outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It rebuilds the collection-machine bootstrap packet in temporary copied workspaces, then proves missing source reports, source non-evidence drift, premature collection-job go-state, local render-machine promotion, unsafe evidence-writing commands, missing explicit confirmation, install-guidance drift, and premature manifest/log/video outputs fail closed without touching the real bootstrap packet.",
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
        and complete_payload.get("version") == "external_collection_machine_bootstrap_audit_v1"
        and complete_payload.get("passed") is True
        and complete_payload.get("not_external_evidence") is True
        and complete_payload.get("strict_external_evidence_ready") is False
        and complete_payload.get("bootstrap_state") == "READY_TO_BOOTSTRAP_EXTERNAL_MACHINE"
        and len(complete_payload.get("bootstrap_steps", []) or []) >= 7
        and complete_checks.get("bootstrap_packet_is_non_evidence") is True
        and complete_checks.get("source_collection_job_still_no_go") is True
        and complete_checks.get("local_machine_not_promoted") is True
        and complete_checks.get("bootstrap_requires_explicit_confirmation") is True
        and complete_checks.get("bootstrap_script_is_probe_only") is True
        and complete_checks.get("no_real_outputs_written") is True
    )
    add_check(
        checks,
        "temporary_fixture_builds_current_bootstrap_packet",
        temporary_fixture_ready,
        f"status={complete_status}, state={complete_payload.get('bootstrap_state')!r}, steps={len(complete_payload.get('bootstrap_steps', []) or [])}",
    )

    missing_status, missing_payload = run_case(remove_onboarding_report)
    missing_source_rejected = missing_status != 0 and "external_platform_onboarding_audit.json" in str(missing_payload.get("error", ""))
    add_check(
        checks,
        "missing_source_report_rejected",
        missing_source_rejected,
        f"status={missing_status}, error={missing_payload.get('error', '')!r}",
    )

    source_status, source_payload = run_case(mark_onboarding_as_evidence)
    source_evidence_drift_rejected = (
        source_status != 0
        and source_payload.get("passed") is False
        and check_named(source_payload, "source_platform_onboarding_ready") is False
    )
    add_check(
        checks,
        "source_non_evidence_drift_rejected",
        source_evidence_drift_rejected,
        f"status={source_status}, source_check={check_named(source_payload, 'source_platform_onboarding_ready')}",
    )

    job_status, job_payload = run_case(promote_collection_job)
    collection_job_go_state_rejected = (
        job_status != 0
        and job_payload.get("passed") is False
        and check_named(job_payload, "source_collection_job_still_no_go") is False
    )
    add_check(
        checks,
        "collection_job_go_state_rejected",
        collection_job_go_state_rejected,
        f"status={job_status}, job_check={check_named(job_payload, 'source_collection_job_still_no_go')}",
    )

    local_status, local_payload = run_case(promote_local_render_machine)
    local_machine_promotion_rejected = (
        local_status != 0
        and local_payload.get("passed") is False
        and check_named(local_payload, "local_machine_not_promoted") is False
    )
    add_check(
        checks,
        "local_machine_promotion_rejected",
        local_machine_promotion_rejected,
        f"status={local_status}, local_machine_check={check_named(local_payload, 'local_machine_not_promoted')}",
    )

    command_status, command_payload = run_case(unsafe_command=True)
    unsafe_command_rejected = (
        command_status != 0
        and command_payload.get("passed") is False
        and check_named(command_payload, "bootstrap_script_is_probe_only") is False
    )
    add_check(
        checks,
        "unsafe_command_rejected",
        unsafe_command_rejected,
        f"status={command_status}, probe_only_check={check_named(command_payload, 'bootstrap_script_is_probe_only')}",
    )

    confirmation_status, confirmation_payload = run_case(missing_confirmation=True)
    missing_confirmation_rejected = (
        confirmation_status != 0
        and confirmation_payload.get("passed") is False
        and check_named(confirmation_payload, "bootstrap_requires_explicit_confirmation") is False
    )
    add_check(
        checks,
        "missing_confirmation_rejected",
        missing_confirmation_rejected,
        f"status={confirmation_status}, confirmation_check={check_named(confirmation_payload, 'bootstrap_requires_explicit_confirmation')}",
    )

    install_status, install_payload = run_case(missing_install_guidance=True)
    install_guidance_drift_rejected = (
        install_status != 0
        and install_payload.get("passed") is False
        and check_named(install_payload, "install_guidance_mentions_core_optional_stack") is False
    )
    add_check(
        checks,
        "install_guidance_drift_rejected",
        install_guidance_drift_rejected,
        f"status={install_status}, install_check={check_named(install_payload, 'install_guidance_mentions_core_optional_stack')}",
    )

    outputs_status, outputs_payload = run_case(write_premature_outputs)
    premature_outputs_rejected = (
        outputs_status != 0
        and outputs_payload.get("passed") is False
        and check_named(outputs_payload, "no_real_outputs_written") is False
    )
    add_check(
        checks,
        "premature_outputs_rejected",
        premature_outputs_rejected,
        f"status={outputs_status}, no_outputs_check={check_named(outputs_payload, 'no_real_outputs_written')}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_repository_bootstrap_outputs_untouched",
        real_outputs_untouched,
        f"before={real_hashes_before}, after={real_hashes_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_collection_machine_bootstrap_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "missing_source_rejected": missing_source_rejected,
        "source_evidence_drift_rejected": source_evidence_drift_rejected,
        "collection_job_go_state_rejected": collection_job_go_state_rejected,
        "local_machine_promotion_rejected": local_machine_promotion_rejected,
        "unsafe_command_rejected": unsafe_command_rejected,
        "missing_confirmation_rejected": missing_confirmation_rejected,
        "install_guidance_drift_rejected": install_guidance_drift_rejected,
        "premature_outputs_rejected": premature_outputs_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(
        "External collection machine bootstrap self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; "
        f"missing_source_rejected={missing_source_rejected}; "
        f"source_drift_rejected={source_evidence_drift_rejected}; "
        f"job_go_rejected={collection_job_go_state_rejected}; "
        f"local_promotion_rejected={local_machine_promotion_rejected}; "
        f"unsafe_command_rejected={unsafe_command_rejected}; "
        f"missing_confirmation_rejected={missing_confirmation_rejected}; "
        f"install_drift_rejected={install_guidance_drift_rejected}; "
        f"premature_outputs_rejected={premature_outputs_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

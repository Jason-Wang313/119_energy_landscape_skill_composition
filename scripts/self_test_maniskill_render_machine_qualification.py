from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import build_maniskill_render_machine_qualification as qualification


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "maniskill_render_machine_qualification_self_test.json"
OUT_MD = RESULTS / "maniskill_render_machine_qualification_self_test.md"
REAL_REPORTS = [
    RESULTS / "maniskill_render_machine_qualification.json",
    RESULTS / "maniskill_render_machine_qualification.md",
    ROOT / "external_validation" / "render_machine_qualification_packet.md",
    RESULTS / "maniskill_render_failure_remediation.json",
    RESULTS / "maniskill_render_failure_remediation.md",
    ROOT / "external_validation" / "render_failure_remediation_work_orders.csv",
]
EXPECTED_ENVS = [
    "PegInsertionSide-v1",
    "OpenCabinetDrawer-v1",
    "OpenCabinetDoor-v1",
    "PullCubeTool-v1",
]


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def real_report_digests() -> dict[str, str | None]:
    return {path.relative_to(ROOT).as_posix(): file_digest(path) for path in REAL_REPORTS}


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def env_records(*, ready: bool) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for env_id in EXPECTED_ENVS:
        records.append(
            {
                "env_id": env_id,
                "task_family": env_id,
                "render_video_ready": ready,
                "render_ok": ready,
                "mp4_ok": ready,
                "error": "" if ready else "synthetic renderer failed before RGB MP4 export",
                "failure_progress_stage": "" if ready else "initial_render_start",
                "terminal_progress_stage": "close_done",
            }
        )
    return records


def preflight_payload(*, ready: bool, records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = {
        "version": "maniskill_render_video_preflight_audit_v1",
        "passed": True,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "render_video_ready": ready,
        "env_records": records if records is not None else env_records(ready=ready),
        "renderer_failure_classes": [] if ready else ["synthetic_renderer_failure"],
        "renderer_failure_stages": [] if ready else ["initial_render_start"],
        "timeout_diagnosis_records": [],
    }
    return payload


def liveness_payload(*, ready: bool, fallback_count: int = 0) -> dict[str, Any]:
    return {
        "version": "maniskill_pilot_runtime_liveness_audit_v1",
        "passed": True,
        "not_external_evidence": True,
        "pilot_runtime_ready": ready,
        "render_video_ready": ready,
        "runner_io_ready": ready,
        "records_written": 1 if ready else 0,
        "videos_written": 1 if ready else 0,
        "diagnostic_video_fallbacks": [
            f"external_validation/pilot_runtime_guard/videos/synthetic_fallback_{index}.mp4.diagnostic.json"
            for index in range(fallback_count)
        ],
        "official_video_guard_blocked_diagnostic_fallback": fallback_count > 0,
        "last_progress_stage": "record_video_done" if ready else "record_video_start",
        "last_backend_progress_stage": "record_video_done" if ready else "reset_scene_return",
        "backend_progress_stages": []
        if ready
        else [{"stage": "record_video_start", "render_error": "synthetic renderer failed before RGB MP4 export"}],
    }


def qualification_payload(preflight: dict[str, Any], liveness: dict[str, Any]) -> dict[str, Any]:
    state, blockers = qualification.classify_state(preflight, liveness, EXPECTED_ENVS)
    return {
        "qualification_state": state,
        "render_machine_qualified": state == "QUALIFIED_FOR_RENDER_BACKED_PILOT",
        "renderer_failure_classes": qualification.renderer_failure_classes(preflight),
        "renderer_failure_stages": qualification.renderer_failure_stages(preflight),
        "expected_primary_envs": EXPECTED_ENVS,
        "blocking_missing": blockers,
        "source_artifacts": [],
    }


def work_order_ids(remediation: dict[str, Any]) -> set[str]:
    return {
        str(item.get("id", ""))
        for item in remediation.get("work_orders", []) or []
        if isinstance(item, dict)
    }


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ManiSkill Render Machine Qualification Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic ready state: `{payload['synthetic_ready_state']}`.",
        f"Synthetic fail-closed state: `{payload['synthetic_fail_closed_state']}`.",
        f"Missing environment rejected: `{str(payload['missing_env_rejected']).lower()}`.",
        f"Diagnostic fallback rejected: `{str(payload['diagnostic_fallback_rejected']).lower()}`.",
        "",
        "This self-test exercises the render-machine qualification classifier and remediation work-order builder on synthetic payloads only. It proves a complete render-backed/liveness fixture can qualify, while render failure, missing environment records, and diagnostic fallback media fail closed before official collection. It does not run ManiSkill, does not write the real render-machine qualification reports, and is not external evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report_before = real_report_digests()
    checks: list[dict[str, Any]] = []

    ready_preflight = preflight_payload(ready=True)
    ready_liveness = liveness_payload(ready=True)
    ready_payload = qualification_payload(ready_preflight, ready_liveness)
    ready_remediation = qualification.build_remediation_payload(ready_payload, ready_liveness)

    failed_preflight = preflight_payload(ready=False)
    failed_liveness = liveness_payload(ready=False, fallback_count=1)
    failed_payload = qualification_payload(failed_preflight, failed_liveness)
    failed_remediation = qualification.build_remediation_payload(failed_payload, failed_liveness)

    missing_env_records = env_records(ready=True)[:-1]
    missing_env_payload = qualification_payload(
        preflight_payload(ready=True, records=missing_env_records),
        ready_liveness,
    )

    fallback_payload = qualification_payload(
        preflight_payload(ready=True),
        liveness_payload(ready=True, fallback_count=1),
    )

    required_work_orders = {
        "renderer_platform_probe",
        "render_profile_matrix_retest",
        "pilot_liveness_retest",
        "diagnostic_fallback_exclusion",
        "fidelity_acceptance_after_render_ready",
        "collection_readiness_gate",
    }
    failed_work_ids = work_order_ids(failed_remediation)
    ready_work_ids = work_order_ids(ready_remediation)
    report_after = real_report_digests()

    add_check(
        checks,
        "synthetic_ready_machine_qualifies",
        ready_payload["qualification_state"] == "QUALIFIED_FOR_RENDER_BACKED_PILOT"
        and ready_payload["render_machine_qualified"] is True
        and not ready_payload["blocking_missing"],
        f"state={ready_payload['qualification_state']}, blockers={ready_payload['blocking_missing']}",
    )
    add_check(
        checks,
        "synthetic_ready_remediation_is_ready",
        ready_remediation.get("remediation_state") == "RENDER_REMEDIATION_READY"
        and required_work_orders.issubset(ready_work_ids)
        and ready_remediation.get("passed") is True,
        f"state={ready_remediation.get('remediation_state')}, work_orders={sorted(ready_work_ids)}",
    )
    add_check(
        checks,
        "render_failure_fails_closed",
        failed_payload["qualification_state"] == "DO_NOT_COLLECT_RENDER_MACHINE"
        and failed_payload["render_machine_qualified"] is False
        and bool(failed_payload["blocking_missing"])
        and "synthetic_renderer_failure" in failed_payload["renderer_failure_classes"],
        f"state={failed_payload['qualification_state']}, blockers={len(failed_payload['blocking_missing'])}",
    )
    add_check(
        checks,
        "failure_remediation_work_orders_cover_gate_sequence",
        failed_remediation.get("remediation_state") == "RENDER_REMEDIATION_REQUIRED"
        and required_work_orders.issubset(failed_work_ids)
        and failed_remediation.get("passed") is True,
        f"state={failed_remediation.get('remediation_state')}, work_orders={sorted(failed_work_ids)}",
    )
    add_check(
        checks,
        "missing_environment_record_fails_closed",
        missing_env_payload["qualification_state"] == "DO_NOT_COLLECT_RENDER_MACHINE"
        and any("missing render preflight record" in blocker for blocker in missing_env_payload["blocking_missing"]),
        f"blockers={missing_env_payload['blocking_missing']}",
    )
    add_check(
        checks,
        "diagnostic_fallback_blocks_qualification",
        fallback_payload["qualification_state"] == "DO_NOT_COLLECT_RENDER_MACHINE"
        and any("diagnostic fallback" in blocker for blocker in fallback_payload["blocking_missing"]),
        f"blockers={fallback_payload['blocking_missing']}",
    )
    add_check(
        checks,
        "real_render_machine_reports_not_overwritten",
        report_before == report_after,
        f"before={report_before!r}, after={report_after!r}",
    )

    payload = {
        "version": "maniskill_render_machine_qualification_self_test_v1",
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "synthetic_ready_state": ready_payload["qualification_state"],
        "synthetic_fail_closed_state": failed_payload["qualification_state"],
        "missing_env_rejected": missing_env_payload["qualification_state"] == "DO_NOT_COLLECT_RENDER_MACHINE",
        "diagnostic_fallback_rejected": fallback_payload["qualification_state"] == "DO_NOT_COLLECT_RENDER_MACHINE",
        "ready_remediation_state": ready_remediation.get("remediation_state"),
        "failed_remediation_state": failed_remediation.get("remediation_state"),
        "required_work_orders": sorted(required_work_orders),
        "real_reports_untouched": report_before == report_after,
        "real_report_digests_before": report_before,
        "real_report_digests_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    if payload["passed"] is not True:
        failed = [check for check in checks if not check["passed"]]
        raise AssertionError(f"ManiSkill render machine qualification self-test failed checks: {failed}")

    print("ManiSkill render machine qualification self-test passed.")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "visible_contribution_audit.json"
OUT_MD = RESULTS / "visible_contribution_audit.md"


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def contains_all(text: str, terms: list[str]) -> tuple[bool, list[str]]:
    missing = [term for term in terms if term not in text]
    return not missing, missing


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    summary = read_json(RESULTS / "submission_readiness_gap_audit.json")
    operator = read_json(RESULTS / "external_operator_packet.json")
    handoff = read_json(RESULTS / "external_operator_handoff_bundle.json")
    analysis = read_json(RESULTS / "external_analysis_plan_audit.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    onboarding = read_json(RESULTS / "external_platform_onboarding_audit.json")
    fidelity_provenance = read_json(RESULTS / "external_fidelity_provenance_audit.json")
    backend_integration = read_json(RESULTS / "external_backend_integration_audit.json")
    runner_probe = read_json(RESULTS / "external_runner_backend_self_test.json")
    pilot_smoke = read_json(RESULTS / "external_pilot_smoke_packet_audit.json")
    config_manifest = read_json(RESULTS / "external_config_manifest_audit.json")
    rollout_evidence = read_json(RESULTS / "external_rollout_evidence_audit.json")
    method_implementation = read_json(RESULTS / "external_method_implementation_audit.json")
    materialization = read_json(RESULTS / "external_config_materialization_plan.json")
    ledger = read_json(DOCS / "claim_evidence_ledger.json")

    files = {
        "README": ROOT / "README.md",
        "final_audit": DOCS / "final_audit.md",
        "readiness_decision": DOCS / "submission_readiness_decision.md",
        "readiness_audit": DOCS / "submission_readiness_audit_v5.md",
        "version_log": DOCS / "submission_version_log.md",
        "child_status": ROOT / "child_status.md",
        "outreach": DOCS / "haonan_yilun_outreach_package.md",
    }
    texts = {name: read_text(path) for name, path in files.items()}

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "readiness_gap_state_visible",
        summary.get("objective_complete") is False
        and int(summary.get("satisfied_requirements", 0) or 0) == 17
        and int(summary.get("blocking_missing_requirements", 0) or 0) == 4,
        (
            f"objective_complete={summary.get('objective_complete')!r}, "
            f"satisfied={summary.get('satisfied_requirements')!r}, "
            f"blocking={summary.get('blocking_missing_requirements')!r}"
        ),
    )
    add_check(
        checks,
        "operator_packet_no_go_visible",
        operator.get("passed") is True
        and operator.get("not_external_evidence") is True
        and operator.get("start_state") == "DO_NOT_COLLECT_YET"
        and int(operator.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"start_state={operator.get('start_state')!r}, "
            f"blocking_missing_count={operator.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "operator_handoff_bundle_visible",
        handoff.get("passed") is True
        and handoff.get("not_external_evidence") is True
        and handoff.get("handoff_bundle_ready") is True
        and handoff.get("strict_evidence_ready") is False
        and handoff.get("start_state") == "DO_NOT_COLLECT_YET"
        and not handoff.get("forbidden_included_paths"),
        (
            f"files={handoff.get('included_file_count')!r}, "
            f"forbidden={handoff.get('forbidden_included_paths')!r}, "
            f"start_state={handoff.get('start_state')!r}"
        ),
    )
    add_check(
        checks,
        "analysis_plan_visible",
        analysis.get("passed") is True
        and analysis.get("not_external_evidence") is True
        and analysis.get("analysis_plan_ready") is True
        and analysis.get("strict_evidence_ready") is False,
        (
            f"analysis_plan_ready={analysis.get('analysis_plan_ready')!r}, "
            f"strict_evidence_ready={analysis.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "platform_probe_visible",
        platform_probe.get("version") == "external_platform_probe_v1"
        and platform_probe.get("passed") is True
        and platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_fidelity_evidence_ready") is False
        and platform_probe.get("strict_external_evidence_ready") is False,
        (
            f"primary_route_install_ready={platform_probe.get('primary_route_install_ready')!r}, "
            f"missing={platform_probe.get('primary_route_missing_packages')!r}"
        ),
    )
    add_check(
        checks,
        "platform_onboarding_visible",
        onboarding.get("passed") is True
        and onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False,
        (
            f"platform_onboarding_ready={onboarding.get('platform_onboarding_ready')!r}, "
            f"strict_evidence_ready={onboarding.get('strict_evidence_ready')!r}"
        ),
    )
    fidelity_provenance_checks = {check.get("name"): check.get("passed") for check in fidelity_provenance.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_provenance_packet_visible",
        fidelity_provenance.get("passed") is True
        and fidelity_provenance.get("not_external_evidence") is True
        and fidelity_provenance.get("fidelity_provenance_packet_ready") is True
        and fidelity_provenance.get("strict_fidelity_evidence_ready") is False
        and fidelity_provenance.get("strict_external_evidence_ready") is False
        and fidelity_provenance_checks.get("work_orders_cover_fidelity_blockers") is True,
        (
            f"fidelity_provenance_packet_ready={fidelity_provenance.get('fidelity_provenance_packet_ready')!r}, "
            f"strict_fidelity_evidence_ready={fidelity_provenance.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={fidelity_provenance.get('strict_external_evidence_ready')!r}"
        ),
    )
    backend_integration_checks = {check.get("name"): check.get("passed") for check in backend_integration.get("checks", []) or []}
    add_check(
        checks,
        "backend_integration_packet_visible",
        backend_integration.get("passed") is True
        and backend_integration.get("not_external_evidence") is True
        and backend_integration.get("backend_integration_packet_ready") is True
        and backend_integration.get("strict_backend_ready") is False
        and backend_integration.get("strict_evidence_ready") is False
        and backend_integration_checks.get("work_orders_cover_backend_to_manifest_path") is True,
        (
            f"backend_integration_packet_ready={backend_integration.get('backend_integration_packet_ready')!r}, "
            f"strict_backend_ready={backend_integration.get('strict_backend_ready')!r}"
        ),
    )
    runner_probe_checks = {check.get("name"): check.get("passed") for check in runner_probe.get("checks", []) or []}
    add_check(
        checks,
        "runner_backend_probe_visible",
        runner_probe.get("passed") is True
        and runner_probe.get("not_external_evidence") is True
        and int(runner_probe.get("records_written", 0) or 0) >= 2
        and not runner_probe.get("schema_errors")
        and runner_probe_checks.get("runner_actual_path_exits_zero") is True
        and runner_probe_checks.get("temporary_records_schema_valid") is True
        and runner_probe_checks.get("temporary_videos_written") is True
        and runner_probe_checks.get("real_manifest_untouched") is True,
        (
            f"records_written={runner_probe.get('records_written')!r}, "
            f"schema_errors={runner_probe.get('schema_errors')!r}"
        ),
    )
    pilot_smoke_checks = {check.get("name"): check.get("passed") for check in pilot_smoke.get("checks", []) or []}
    add_check(
        checks,
        "pilot_smoke_packet_visible",
        pilot_smoke.get("passed") is True
        and pilot_smoke.get("not_external_evidence") is True
        and pilot_smoke.get("pilot_smoke_packet_ready") is True
        and pilot_smoke.get("strict_evidence_ready") is False
        and pilot_smoke_checks.get("quarantine_dirs_are_separate_from_official_evidence") is True,
        (
            f"pilot_smoke_packet_ready={pilot_smoke.get('pilot_smoke_packet_ready')!r}, "
            f"strict_evidence_ready={pilot_smoke.get('strict_evidence_ready')!r}"
        ),
    )
    method_checks = {check.get("name"): check.get("passed") for check in method_implementation.get("checks", []) or []}
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest.get("checks", []) or []}
    rollout_evidence_checks = {check.get("name"): check.get("passed") for check in rollout_evidence.get("checks", []) or []}
    add_check(
        checks,
        "config_manifest_packet_visible",
        config_manifest.get("passed") is True
        and config_manifest.get("not_external_evidence") is True
        and config_manifest.get("config_manifest_packet_ready") is True
        and config_manifest.get("strict_config_evidence_ready") is False
        and config_manifest.get("manifest_declared_config_ready") is False
        and config_manifest_checks.get("work_orders_cover_config_to_manifest_path") is True,
        (
            f"config_manifest_packet_ready={config_manifest.get('config_manifest_packet_ready')!r}, "
            f"strict_config_evidence_ready={config_manifest.get('strict_config_evidence_ready')!r}, "
            f"manifest_declared_config_ready={config_manifest.get('manifest_declared_config_ready')!r}"
        ),
    )
    add_check(
        checks,
        "rollout_evidence_packet_visible",
        rollout_evidence.get("passed") is True
        and rollout_evidence.get("not_external_evidence") is True
        and rollout_evidence.get("rollout_evidence_packet_ready") is True
        and rollout_evidence.get("strict_rollout_evidence_ready") is False
        and rollout_evidence.get("strict_external_evidence_ready") is False
        and rollout_evidence_checks.get("task_work_orders_cover_all_planned_tasks") is True,
        (
            f"rollout_evidence_packet_ready={rollout_evidence.get('rollout_evidence_packet_ready')!r}, "
            f"strict_rollout_evidence_ready={rollout_evidence.get('strict_rollout_evidence_ready')!r}, "
            f"strict_external_evidence_ready={rollout_evidence.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "method_implementation_packet_visible",
        method_implementation.get("passed") is True
        and method_implementation.get("not_external_evidence") is True
        and method_implementation.get("method_implementation_packet_ready") is True
        and method_implementation.get("strict_adapter_evidence_ready") is False
        and method_checks.get("work_orders_cover_all_missing_non_oracle_methods") is True,
        (
            f"method_implementation_packet_ready={method_implementation.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_implementation.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "materializer_guard_visible",
        materialization.get("passed") is True
        and materialization.get("write_enabled") is False
        and materialization.get("not_external_evidence") is True
        and str(materialization.get("operator_write_command", "")).endswith("--confirm-real-platform --write"),
        (
            f"write_enabled={materialization.get('write_enabled')!r}, "
            f"not_external_evidence={materialization.get('not_external_evidence')!r}"
        ),
    )
    claim_names = {str(claim.get("name", "")) for claim in ledger.get("permitted_claims", []) if isinstance(claim, dict)}
    add_check(
        checks,
        "ledger_tracks_new_visible_claims",
        {
            "external_platform_probe_claim",
            "external_operator_packet_claim",
            "external_operator_handoff_bundle_claim",
            "external_analysis_plan_claim",
            "external_platform_onboarding_claim",
            "external_fidelity_provenance_packet_claim",
            "external_backend_integration_packet_claim",
            "external_runner_backend_probe_claim",
            "external_pilot_smoke_packet_claim",
            "external_config_manifest_packet_claim",
            "external_rollout_evidence_packet_claim",
            "external_method_implementation_packet_claim",
            "external_config_materialization_claim",
        }.issubset(claim_names),
        f"missing={sorted({'external_platform_probe_claim', 'external_operator_packet_claim', 'external_operator_handoff_bundle_claim', 'external_analysis_plan_claim', 'external_platform_onboarding_claim', 'external_fidelity_provenance_packet_claim', 'external_backend_integration_packet_claim', 'external_runner_backend_probe_claim', 'external_pilot_smoke_packet_claim', 'external_config_manifest_packet_claim', 'external_rollout_evidence_packet_claim', 'external_method_implementation_packet_claim', 'external_config_materialization_claim'} - claim_names)}",
    )

    required_terms_by_file = {
        "README": [
            "adaptive physical world/action model for skill seams",
            "External config materialization plan",
            "External analysis plan",
            "External platform probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External backend integration packet",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "External operator packet",
            "External operator handoff bundle",
            "17/21",
        ],
        "final_audit": [
            "External config materialization plan",
            "External analysis plan",
            "External platform probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External backend integration packet",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "External operator packet",
            "External operator handoff bundle",
            "Haonan/Yilun outreach package",
            "17 satisfied, 4 blocking external gaps",
        ],
        "readiness_decision": [
            "guarded config materialization plan",
            "external analysis plan",
            "external platform probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external backend integration packet",
            "external runner backend probe self-test",
            "external pilot smoke packet",
            "external config manifest packet",
            "external rollout evidence packet",
            "external method implementation packet",
            "generated external operator packet",
            "external operator handoff bundle",
            "outreach package now frames Haonan's role as fit/falsification advice",
            "ICLR main ready: no",
        ],
        "readiness_audit": [
            "External config materialization plan",
            "External analysis plan",
            "External platform probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External backend integration packet",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "External operator packet",
            "External operator handoff bundle",
            "outreach PDFs now reflect the operator-packet/no-go stance",
            "17/21 objective requirements satisfied",
        ],
        "version_log": [
            "scripts/materialize_external_configs.py",
            "scripts/build_external_analysis_plan.py",
            "scripts/probe_external_platform.py",
            "scripts/build_external_platform_onboarding.py",
            "scripts/build_external_fidelity_provenance_packet.py",
            "scripts/build_external_backend_integration_packet.py",
            "scripts/self_test_external_runner_backend.py",
            "scripts/build_external_pilot_smoke_packet.py",
            "scripts/audit_external_pilot_smoke.py",
            "scripts/build_external_config_manifest_packet.py",
            "scripts/build_external_rollout_evidence_packet.py",
            "scripts/build_external_method_implementation_packet.py",
            "scripts/build_external_operator_packet.py",
            "scripts/build_external_operator_handoff_bundle.py",
            "operator-packet/no-go stance",
        ],
        "child_status": [
            "external config materialization plan",
            "external analysis plan",
            "external platform probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external backend integration packet",
            "external runner backend probe self-test",
            "external pilot smoke packet",
            "external config manifest packet",
            "external rollout evidence packet",
            "external method implementation packet",
            "external operator packet",
            "external operator handoff bundle",
            "operator-packet-aligned Haonan/Yilun outreach package",
        ],
        "outreach": [
            "results/external_operator_packet.md",
            "do not frame Haonan as responsible for supplying the missing proof",
            "independent validation protocol/operator packet",
        ],
    }
    for name, terms in required_terms_by_file.items():
        ok, missing = contains_all(texts[name], terms)
        add_check(checks, f"{name}_current_visible_contribution_terms", ok, f"missing={missing}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "visible_contribution_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "audited_files": {name: rel(path) for name, path in files.items()},
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Visible Contribution Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        "",
        "This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, guarded external config materialization, the external config manifest packet, the external rollout evidence packet, the locked external analysis plan, the external platform probe, the external platform onboarding packet, the external fidelity provenance packet, the external backend integration packet, the external runner backend probe self-test, the external pilot smoke packet, the external method implementation packet, the no-go operator packet, the no-evidence operator handoff bundle, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Visible contribution audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    if not passed:
        for check in payload["failed_checks"]:
            print(f"FAILED {check['name']}: {check['detail']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

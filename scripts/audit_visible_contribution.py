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
    task_binding = read_json(RESULTS / "maniskill_task_binding_probe.json")
    env_smoke = read_json(RESULTS / "maniskill_env_smoke_probe.json")
    fidelity_metadata = read_json(RESULTS / "maniskill_fidelity_metadata_probe.json")
    onboarding = read_json(RESULTS / "external_platform_onboarding_audit.json")
    fidelity_provenance = read_json(RESULTS / "external_fidelity_provenance_audit.json")
    fidelity_draft = read_json(RESULTS / "external_fidelity_acceptance_draft_audit.json")
    fidelity_materialization = read_json(RESULTS / "fidelity_acceptance_materialization_plan.json")
    backend_integration = read_json(RESULTS / "external_backend_integration_audit.json")
    maniskill_backend = read_json(RESULTS / "maniskill_backend_readiness_audit.json")
    reference_preflight = read_json(RESULTS / "maniskill_reference_collection_preflight_audit.json")
    runner_probe = read_json(RESULTS / "external_runner_backend_self_test.json")
    pilot_smoke = read_json(RESULTS / "external_pilot_smoke_packet_audit.json")
    pilot_runtime = read_json(RESULTS / "maniskill_pilot_runtime_liveness_audit.json")
    render_preflight = read_json(RESULTS / "maniskill_render_video_preflight_audit.json")
    runbook = read_json(RESULTS / "external_runbook_audit.json")
    config_manifest = read_json(RESULTS / "external_config_manifest_audit.json")
    rollout_evidence = read_json(RESULTS / "external_rollout_evidence_audit.json")
    method_implementation = read_json(RESULTS / "external_method_implementation_audit.json")
    adapter_evidence_self_test = read_json(RESULTS / "external_adapter_evidence_self_test.json")
    materialization = read_json(RESULTS / "external_config_materialization_plan.json")
    planner_policy = read_json(RESULTS / "planner_edge_policy_audit.json")
    local_model_release = read_json(RESULTS / "local_model_release_audit.json")
    reviewer_packet = read_json(RESULTS / "reviewer_response_packet_audit.json")
    ledger = read_json(DOCS / "claim_evidence_ledger.json")

    files = {
        "README": ROOT / "README.md",
        "final_audit": DOCS / "final_audit.md",
        "readiness_decision": DOCS / "submission_readiness_decision.md",
        "readiness_audit": DOCS / "submission_readiness_audit_v5.md",
        "version_log": DOCS / "submission_version_log.md",
        "child_status": ROOT / "child_status.md",
        "outreach": DOCS / "haonan_yilun_outreach_package.md",
        "reviewer": DOCS / "reviewer_response_packet.md",
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
    reference_route = operator.get("tracked_maniskill_reference_route", {}) or {}
    reference_blockers = reference_route.get("blocking_missing", []) or []
    add_check(
        checks,
        "operator_packet_tracked_reference_route_visible",
        reference_route.get("not_external_evidence") is True
        and "maniskill_reference_backend.py" in str(reference_route.get("backend_module", ""))
        and reference_route.get("run_id") == "maniskill_sapien_reference_preflight_protocol_v1"
        and reference_route.get("reference_backend_contract_ready") is True
        and reference_route.get("collection_ready") is False
        and int(reference_route.get("blocking_missing_count", 99) or 99) == 1
        and len(reference_blockers) == 1
        and "fidelity_acceptance_ready" in reference_blockers[0]
        and "audit_external_collection_readiness.py --strict" in str(reference_route.get("pre_collection_gate_command", ""))
        and "real_collection_runner.py" in str(reference_route.get("collection_command_after_fidelity_acceptance", "")),
        (
            f"backend={reference_route.get('backend_module')!r}, "
            f"run_id={reference_route.get('run_id')!r}, "
            f"blocking={reference_blockers!r}"
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
    runbook_checks = {check.get("name"): check.get("passed") for check in runbook.get("checks", []) or []}
    add_check(
        checks,
        "external_runbook_route_gates_visible",
        runbook.get("passed") is True
        and runbook.get("not_external_evidence") is True
        and int(runbook.get("validation_command_count", 0) or 0) >= 40
        and runbook_checks.get("current_maniskill_route_gates_present") is True
        and runbook_checks.get("gate_order_preserves_preflight_before_collection_and_evidence") is True,
        (
            f"validation_command_count={runbook.get('validation_command_count')!r}, "
            f"route_gates={runbook_checks.get('current_maniskill_route_gates_present')!r}, "
            f"gate_order={runbook_checks.get('gate_order_preserves_preflight_before_collection_and_evidence')!r}"
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
        "maniskill_task_binding_probe_visible",
        task_binding.get("version") == "maniskill_task_binding_probe_v1"
        and task_binding.get("passed") is True
        and task_binding.get("not_external_evidence") is True
        and task_binding.get("task_binding_probe_ready") is True
        and task_binding.get("accepted_task_binding_ready") is False
        and task_binding.get("strict_external_evidence_ready") is False,
        (
            f"strict_task_binding_install_ready={task_binding.get('strict_task_binding_install_ready')!r}, "
            f"missing={task_binding.get('primary_missing_env_ids')!r}"
        ),
    )
    add_check(
        checks,
        "maniskill_env_smoke_probe_visible",
        env_smoke.get("version") == "maniskill_env_smoke_probe_v1"
        and env_smoke.get("passed") is True
        and env_smoke.get("not_external_evidence") is True
        and env_smoke.get("env_smoke_probe_ready") is True
        and env_smoke.get("accepted_fidelity_ready") is False
        and env_smoke.get("strict_external_evidence_ready") is False,
        (
            f"strict_env_smoke_ready={env_smoke.get('strict_env_smoke_ready')!r}, "
            f"primary_reset_missing={env_smoke.get('primary_reset_missing')!r}"
        ),
    )
    add_check(
        checks,
        "maniskill_fidelity_metadata_probe_visible",
        fidelity_metadata.get("version") == "maniskill_fidelity_metadata_probe_v1"
        and fidelity_metadata.get("passed") is True
        and fidelity_metadata.get("not_external_evidence") is True
        and fidelity_metadata.get("metadata_probe_ready") is True
        and fidelity_metadata.get("accepted_fidelity_ready") is False
        and fidelity_metadata.get("strict_external_evidence_ready") is False,
        (
            f"strict_metadata_ready={fidelity_metadata.get('strict_metadata_ready')!r}, "
            f"primary_metadata_missing={fidelity_metadata.get('primary_metadata_missing')!r}"
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
    fidelity_draft_checks = {check.get("name"): check.get("passed") for check in fidelity_draft.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_draft_visible",
        fidelity_draft.get("passed") is True
        and fidelity_draft.get("not_external_evidence") is True
        and fidelity_draft.get("draft_ready") is True
        and fidelity_draft.get("acceptance_ready") is False
        and fidelity_draft.get("strict_fidelity_evidence_ready") is False
        and fidelity_draft.get("strict_external_evidence_ready") is False
        and fidelity_draft_checks.get("candidate_platform_prefilled_from_reference_route") is True
        and fidelity_draft_checks.get("acceptance_gates_remain_unaccepted") is True,
        (
            f"draft_ready={fidelity_draft.get('draft_ready')!r}, "
            f"remaining_operator_inputs={fidelity_draft.get('remaining_operator_input_count')!r}, "
            f"acceptance_ready={fidelity_draft.get('acceptance_ready')!r}"
        ),
    )
    fidelity_materialization_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_visible",
        fidelity_materialization.get("version") == "fidelity_acceptance_materialization_plan_v1"
        and fidelity_materialization.get("passed") is True
        and fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False
        and fidelity_materialization_checks.get("operator_write_command_is_guarded") is True,
        (
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}"
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
    maniskill_backend_checks = {check.get("name"): check.get("passed") for check in maniskill_backend.get("checks", []) or []}
    maniskill_backend_platform = maniskill_backend.get("platform_provenance", {}) or {}
    add_check(
        checks,
        "maniskill_reference_backend_visible",
        maniskill_backend.get("version") == "maniskill_reference_backend_audit_v1"
        and maniskill_backend.get("passed") is True
        and maniskill_backend.get("not_external_evidence") is True
        and maniskill_backend.get("backend_contract_ready") is True
        and maniskill_backend.get("reference_backend_available") is True
        and maniskill_backend.get("video_writer_ready") is True
        and maniskill_backend.get("reference_backend_collection_enabled") is False
        and maniskill_backend.get("official_collection_ready") is False
        and maniskill_backend.get("strict_external_evidence_ready") is False
        and maniskill_backend_platform.get("render_backend") == "cpu"
        and maniskill_backend_platform.get("shader_pack") == "minimal"
        and int(maniskill_backend_platform.get("render_width", 0) or 0) >= 16
        and int(maniskill_backend_platform.get("render_height", 0) or 0) >= 16
        and maniskill_backend_checks.get("official_collection_fail_closed_without_enable_flag") is True
        and maniskill_backend_checks.get("video_export_fail_closed_before_reset") is True
        and maniskill_backend_checks.get("synthetic_mp4_writer_passes") is True
        and maniskill_backend_checks.get("state_shaped_arrays_rejected_as_video_frames") is True,
        (
            f"backend_contract_ready={maniskill_backend.get('backend_contract_ready')!r}, "
            f"video_writer_ready={maniskill_backend.get('video_writer_ready')!r}, "
            f"render_backend={maniskill_backend_platform.get('render_backend')!r}, "
            f"shader_pack={maniskill_backend_platform.get('shader_pack')!r}, "
            f"official_collection_ready={maniskill_backend.get('official_collection_ready')!r}, "
            f"strict_external_evidence_ready={maniskill_backend.get('strict_external_evidence_ready')!r}"
        ),
    )
    reference_preflight_checks = {check.get("name"): check.get("passed") for check in reference_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_collection_preflight_visible",
        reference_preflight.get("version") == "maniskill_reference_collection_preflight_audit_v1"
        and reference_preflight.get("passed") is True
        and reference_preflight.get("not_external_evidence") is True
        and reference_preflight.get("reference_backend_contract_ready") is True
        and reference_preflight.get("collection_ready") is False
        and reference_preflight.get("strict_external_evidence_ready") is False
        and int(reference_preflight.get("collection_blocking_missing_count", 0) or 0) == 1
        and reference_preflight_checks.get("reference_backend_collection_preflight_reaches_fidelity_gate") is True,
        (
            f"contract_ready={reference_preflight.get('reference_backend_contract_ready')!r}, "
            f"collection_ready={reference_preflight.get('collection_ready')!r}, "
            f"blocking={reference_preflight.get('collection_blocking_missing')!r}"
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
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", []) or []}
    pilot_runtime_records = int(pilot_runtime.get("records_observed", 0) or 0)
    pilot_runtime_videos = int(pilot_runtime.get("videos_written", 0) or 0)
    pilot_runtime_fallbacks = len(pilot_runtime.get("diagnostic_video_fallbacks", []) or [])
    pilot_runtime_basic = (
        pilot_runtime.get("version") == "maniskill_pilot_runtime_liveness_audit_v1"
        and pilot_runtime.get("passed") is True
        and pilot_runtime.get("not_external_evidence") is True
        and pilot_runtime.get("strict_external_evidence_ready") is False
        and pilot_runtime.get("pilot_runtime_ready") is False
        and pilot_runtime.get("render_video_ready") is False
        and pilot_runtime.get("render_backend") == "cpu"
        and pilot_runtime.get("shader_pack") == "minimal"
        and int(pilot_runtime.get("render_width", 0) or 0) >= 16
        and int(pilot_runtime.get("render_height", 0) or 0) >= 16
        and pilot_runtime_checks.get("bounded_runner_subprocess_exercised") is True
        and pilot_runtime_checks.get("timeout_or_result_recorded_as_readiness_state") is True
    )
    pilot_runtime_diagnostic_io = (
        pilot_runtime.get("runner_io_ready") is True
        and pilot_runtime_records >= 1
        and pilot_runtime_videos >= 1
        and pilot_runtime_fallbacks >= 1
    )
    pilot_runtime_unavailable = (
        pilot_runtime.get("runner_io_ready") is False
        and pilot_runtime_records == 0
        and pilot_runtime_videos == 0
        and pilot_runtime_fallbacks == 0
    )
    add_check(
        checks,
        "maniskill_pilot_runtime_liveness_visible",
        pilot_runtime_basic
        and (pilot_runtime_diagnostic_io or pilot_runtime_unavailable),
        (
            f"pilot_runtime_ready={pilot_runtime.get('pilot_runtime_ready')!r}, "
            f"runner_io_ready={pilot_runtime.get('runner_io_ready')!r}, "
            f"render_video_ready={pilot_runtime.get('render_video_ready')!r}, "
            f"render_backend={pilot_runtime.get('render_backend')!r}, "
            f"shader_pack={pilot_runtime.get('shader_pack')!r}, "
            f"timed_out={pilot_runtime.get('timed_out')!r}, "
            f"records={pilot_runtime_records!r}, "
            f"videos={pilot_runtime_videos!r}, "
            f"diagnostic_fallbacks={pilot_runtime_fallbacks}, "
            f"failure_summary={pilot_runtime.get('failure_summary')!r}"
        ),
    )
    add_check(
        checks,
        "maniskill_render_video_preflight_visible",
        render_preflight.get("version") == "maniskill_render_video_preflight_audit_v1"
        and render_preflight.get("passed") is True
        and render_preflight.get("not_external_evidence") is True
        and render_preflight.get("strict_external_evidence_ready") is False
        and int(render_preflight.get("env_count", 0) or 0) >= 1
        and render_preflight.get("render_backend") == "cpu"
        and render_preflight.get("shader_pack") == "minimal"
        and int(render_preflight.get("width", 0) or 0) >= 16
        and int(render_preflight.get("height", 0) or 0) >= 16
        and isinstance(render_preflight.get("render_video_ready"), bool),
        (
            f"render_video_ready={render_preflight.get('render_video_ready')!r}, "
            f"render_backend={render_preflight.get('render_backend')!r}, "
            f"shader_pack={render_preflight.get('shader_pack')!r}, "
            f"envs={render_preflight.get('env_count')!r}, "
            f"blocking={render_preflight.get('blocking_missing')!r}"
        ),
    )
    add_check(
        checks,
        "renderer_failure_classifier_visible",
        render_preflight.get("render_video_ready") is True
        or (
            bool(render_preflight.get("renderer_failure_classes", []) or [])
            and len(render_preflight.get("operator_remediation", []) or []) >= 2
            and all(
                fragment in "\n".join(render_preflight.get("renderer_profile_retest_commands", []) or [])
                for fragment in ("--render-backend cpu", "--render-backend gpu", "--render-backend sapien_cuda")
            )
        ),
        (
            f"classes={render_preflight.get('renderer_failure_classes')!r}, "
            f"remediation={len(render_preflight.get('operator_remediation', []) or [])}"
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
        and method_checks.get("work_orders_cover_all_missing_non_oracle_methods") is True
        and method_checks.get("manifest_entry_templates_cover_required_hash_fields") is True
        and method_checks.get("work_orders_forbid_scaffolds_and_reference_adapters") is True
        and method_checks.get("policy_or_config_hash_in_logs_required") is True
        and method_checks.get("reference_adapter_provenance_covers_non_oracle_methods") is True
        and method_checks.get("reference_adapter_hashes_recorded") is True
        and method_checks.get("reference_adapters_marked_non_evidence") is True
        and method_checks.get("reference_manifest_stubs_not_strict_ready") is True,
        (
            f"method_implementation_packet_ready={method_implementation.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_implementation.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    adapter_evidence_self_checks = {check.get("name"): check.get("passed") for check in adapter_evidence_self_test.get("checks", [])}
    add_check(
        checks,
        "strict_reference_adapter_rejection_gate_visible",
        adapter_evidence_self_test.get("passed") is True
        and adapter_evidence_self_test.get("not_external_evidence") is True
        and adapter_evidence_self_test.get("synthetic_adapter_evidence_ready") is True
        and adapter_evidence_self_test.get("scaffold_adapter_evidence_ready") is False
        and adapter_evidence_self_test.get("reference_adapter_evidence_ready") is False
        and adapter_evidence_self_checks.get("reference_adapters_rejected_as_strict_evidence") is True,
        (
            f"reference_adapter_evidence_ready={adapter_evidence_self_test.get('reference_adapter_evidence_ready')!r}, "
            f"check={adapter_evidence_self_checks.get('reference_adapters_rejected_as_strict_evidence')!r}"
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
    planner_metrics = planner_policy.get("metrics", {})
    add_check(
        checks,
        "planner_edge_policy_visible",
        planner_policy.get("version") == "planner_edge_policy_audit_v1"
        and planner_policy.get("passed") is True
        and planner_policy.get("not_external_evidence") is True
        and int(planner_metrics.get("frontier_count", 0) or 0) >= 1500
        and float(planner_metrics.get("selected_utility_delta", 0.0) or 0.0) >= 0.18
        and float(planner_metrics.get("selected_realized_breach_delta", 1.0) or 1.0) <= -0.05,
        (
            f"frontiers={planner_metrics.get('frontier_count')!r}, "
            f"utility_delta={planner_metrics.get('selected_utility_delta')!r}, "
            f"breach_delta={planner_metrics.get('selected_realized_breach_delta')!r}"
        ),
    )
    local_model_release_checks = {check.get("name"): check.get("passed") for check in local_model_release.get("checks", []) or []}
    add_check(
        checks,
        "local_model_release_visible",
        local_model_release.get("version") == "paper119_local_model_release_audit_v1"
        and local_model_release.get("passed") is True
        and local_model_release.get("not_external_evidence") is True
        and local_model_release.get("local_model_release_ready") is True
        and local_model_release.get("external_evidence_ready") is False
        and len(str(local_model_release.get("release_hash", ""))) == 64
        and local_model_release_checks.get("proposed_method_present") is True
        and local_model_release_checks.get("explicitly_not_external_evidence") is True
        and local_model_release_checks.get("not_a_robot_policy_checkpoint") is True,
        (
            f"release_hash={local_model_release.get('release_hash')!r}, "
            f"local_model_release_ready={local_model_release.get('local_model_release_ready')!r}, "
            f"external_evidence_ready={local_model_release.get('external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "reviewer_response_packet_visible",
        reviewer_packet.get("version") == "reviewer_response_packet_v1"
        and reviewer_packet.get("passed") is True
        and reviewer_packet.get("not_external_evidence") is True
        and int(reviewer_packet.get("entry_count", 0) or 0) >= 12
        and "do not list many papers" in texts["reviewer"]
        and "not for them to be responsible for supplying the missing proof" in texts["reviewer"]
        and "does not change the current STRONG_REVISE decision" in texts["reviewer"],
        (
            f"entries={reviewer_packet.get('entry_count')!r}, "
            f"not_external_evidence={reviewer_packet.get('not_external_evidence')!r}"
        ),
    )
    claim_names = {str(claim.get("name", "")) for claim in ledger.get("permitted_claims", []) if isinstance(claim, dict)}
    add_check(
        checks,
        "ledger_tracks_new_visible_claims",
        {
            "local_planner_edge_policy_claim",
            "local_model_release_claim",
            "external_platform_probe_claim",
            "maniskill_task_binding_probe_claim",
            "maniskill_env_smoke_probe_claim",
            "maniskill_fidelity_metadata_probe_claim",
            "external_operator_packet_claim",
            "external_operator_handoff_bundle_claim",
            "external_analysis_plan_claim",
            "external_platform_onboarding_claim",
            "external_fidelity_provenance_packet_claim",
            "external_fidelity_acceptance_draft_claim",
            "external_fidelity_acceptance_materializer_claim",
            "external_backend_integration_packet_claim",
            "maniskill_reference_backend_claim",
            "maniskill_reference_collection_preflight_claim",
            "external_runner_backend_probe_claim",
            "external_pilot_smoke_packet_claim",
            "maniskill_pilot_runtime_liveness_claim",
            "maniskill_render_video_preflight_claim",
            "external_config_manifest_packet_claim",
            "external_rollout_evidence_packet_claim",
            "external_method_implementation_packet_claim",
            "external_method_reference_provenance_claim",
            "external_manifest_assembly_checklist_claim",
            "external_config_materialization_claim",
            "reviewer_response_packet_claim",
        }.issubset(claim_names),
        f"missing={sorted({'local_planner_edge_policy_claim', 'local_model_release_claim', 'external_platform_probe_claim', 'maniskill_task_binding_probe_claim', 'maniskill_env_smoke_probe_claim', 'maniskill_fidelity_metadata_probe_claim', 'external_operator_packet_claim', 'external_operator_handoff_bundle_claim', 'external_analysis_plan_claim', 'external_platform_onboarding_claim', 'external_fidelity_provenance_packet_claim', 'external_fidelity_acceptance_draft_claim', 'external_fidelity_acceptance_materializer_claim', 'external_backend_integration_packet_claim', 'maniskill_reference_backend_claim', 'maniskill_reference_collection_preflight_claim', 'external_runner_backend_probe_claim', 'external_pilot_smoke_packet_claim', 'maniskill_pilot_runtime_liveness_claim', 'maniskill_render_video_preflight_claim', 'external_config_manifest_packet_claim', 'external_rollout_evidence_packet_claim', 'external_method_implementation_packet_claim', 'external_method_reference_provenance_claim', 'external_manifest_assembly_checklist_claim', 'external_config_materialization_claim', 'reviewer_response_packet_claim'} - claim_names)}",
    )

    required_terms_by_file = {
        "README": [
            "adaptive physical world/action model for skill seams",
            "Planner-edge policy audit",
            "Local model release card",
            "External config materialization plan",
            "External analysis plan",
            "External platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External fidelity acceptance draft",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "ManiSkill pilot runtime liveness audit",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "External operator packet",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "Reviewer response packet",
            "17/21",
        ],
        "final_audit": [
            "External config materialization plan",
            "Planner-edge policy audit",
            "Local model release card",
            "External analysis plan",
            "External platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External fidelity acceptance draft",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "ManiSkill pilot runtime liveness audit",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "External operator packet",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "Reviewer response packet",
            "Haonan/Yilun outreach package",
            "17 satisfied, 4 blocking external gaps",
        ],
        "readiness_decision": [
            "guarded config materialization plan",
            "planner-edge policy audit",
            "local model release card",
            "external analysis plan",
            "external platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external fidelity acceptance draft",
            "fidelity acceptance promotion checklist",
            "fidelity acceptance materializer",
            "external backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "external runner backend probe self-test",
            "external pilot smoke packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "ManiSkill pilot runtime liveness audit",
            "external config manifest packet",
            "external rollout evidence packet",
            "external method implementation packet",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "generated external operator packet",
            "external collection runbook route-gate audit",
            "external operator handoff bundle",
            "reviewer response packet",
            "outreach package now frames Haonan's role as fit/falsification advice",
            "ICLR main ready: no",
        ],
        "readiness_audit": [
            "External config materialization plan",
            "Planner-edge policy audit",
            "Local model release card",
            "External analysis plan",
            "External platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External fidelity acceptance draft",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "ManiSkill pilot runtime liveness audit",
            "External config manifest packet",
            "External rollout evidence packet",
            "External method implementation packet",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "External operator packet",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "Reviewer response packet",
            "outreach PDFs now reflect the operator-packet/no-go stance",
            "17/21 objective requirements satisfied",
        ],
        "version_log": [
            "scripts/materialize_external_configs.py",
            "scripts/audit_planner_edge_policy.py",
            "scripts/build_local_model_release.py",
            "scripts/build_external_analysis_plan.py",
            "scripts/probe_external_platform.py",
            "scripts/probe_maniskill_task_bindings.py",
            "scripts/probe_maniskill_env_smoke.py",
            "scripts/probe_maniskill_fidelity_metadata.py",
            "scripts/build_external_platform_onboarding.py",
            "scripts/build_external_fidelity_provenance_packet.py",
            "scripts/build_external_fidelity_acceptance_draft.py",
            "fidelity acceptance promotion checklist",
            "scripts/materialize_fidelity_acceptance.py",
            "scripts/build_external_backend_integration_packet.py",
            "scripts/audit_maniskill_backend_readiness.py",
            "scripts/audit_maniskill_reference_collection_preflight.py",
            "synthetic MP4 writer check",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "scripts/self_test_external_runner_backend.py",
            "scripts/build_external_pilot_smoke_packet.py",
            "scripts/audit_external_pilot_smoke.py",
            "scripts/audit_maniskill_render_video_preflight.py",
            "renderer-failure classifier",
            "scripts/audit_maniskill_pilot_runtime_liveness.py",
            "scripts/build_external_config_manifest_packet.py",
            "scripts/build_external_rollout_evidence_packet.py",
            "scripts/build_external_method_implementation_packet.py",
            "method_reference_provenance.csv",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest_assembly_checklist.csv",
            "manifest assembly checklist",
            "scripts/build_external_operator_packet.py",
            "current ManiSkill route gates",
            "scripts/build_external_operator_handoff_bundle.py",
            "scripts/build_reviewer_response_packet.py",
            "reviewer response packet",
            "operator-packet/no-go stance",
        ],
        "child_status": [
            "external config materialization plan",
            "planner-edge policy audit",
            "local model release card",
            "external analysis plan",
            "external platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external fidelity acceptance draft",
            "fidelity acceptance promotion checklist",
            "fidelity acceptance materializer",
            "external backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "external runner backend probe self-test",
            "external pilot smoke packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "ManiSkill pilot runtime liveness audit",
            "external config manifest packet",
            "external rollout evidence packet",
            "external method implementation packet",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "external operator packet",
            "external collection runbook route-gate audit",
            "external operator handoff bundle",
            "reviewer response packet",
            "operator-packet-aligned Haonan/Yilun outreach package",
        ],
        "outreach": [
            "results/external_operator_packet.md",
            "ManiSkill fidelity metadata probe",
            "fidelity acceptance materializer",
            "reference-adapter provenance catalog",
            "strict reference-adapter rejection gate",
            "manifest assembly checklist",
            "do not frame Haonan as responsible for supplying the missing proof",
            "independent validation protocol/operator packet",
            "reviewer response packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
        ],
        "reviewer": [
            "Not evidence: `true`.",
            "adaptive physical world/action models for skill seams",
            "do not list many papers",
            "not for them to be responsible for supplying the missing proof",
            "does not change the current STRONG_REVISE decision",
            "Close all four blocking external requirements",
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
        "This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, the local planner-edge policy audit, the local model release card, guarded external config materialization, the external config manifest packet, the external rollout evidence packet, the locked external analysis plan, the external platform probe, the ManiSkill task binding probe, the ManiSkill env smoke probe, the external platform onboarding packet, the external fidelity provenance packet, the external fidelity acceptance draft, the fidelity acceptance materializer, the external backend integration packet, the ManiSkill reference backend readiness audit with MP4 writer path, state-shaped array video guard, and explicit render-backend/shader controls, the ManiSkill reference collection preflight audit, the external runner backend probe self-test, the external pilot smoke packet, the ManiSkill render-video preflight and renderer-failure classifier, the ManiSkill pilot runtime liveness audit, the external method implementation packet, the reference-adapter provenance catalog, the strict reference-adapter rejection gate, the manifest assembly checklist, the no-go operator packet, the external collection runbook route-gate audit, the no-evidence operator handoff bundle, the reviewer response packet, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.",
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

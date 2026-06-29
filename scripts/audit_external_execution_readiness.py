from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
EXTERNAL = ROOT / "external_validation"

OUT_JSON = RESULTS / "external_execution_readiness_audit.json"
OUT_MD = RESULTS / "external_execution_readiness_audit.md"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def passed_json(path: Path, *, version: str | None = None) -> tuple[bool, dict[str, Any], str]:
    if not path.exists():
        return False, {}, f"missing {path.relative_to(ROOT).as_posix()}"
    payload = read_json(path)
    if version is not None and payload.get("version") != version:
        return False, payload, f"version={payload.get('version')!r}, expected={version!r}"
    if payload.get("passed") is not True:
        return False, payload, f"passed={payload.get('passed')!r}"
    return True, payload, "passed"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []

    collection_ok, collection, collection_detail = passed_json(
        RESULTS / "external_collection_plan.json",
        version="external_collection_plan_v1",
    )
    add_check(checks, "collection_plan_ready", collection_ok, collection_detail)
    total_required_records = int(collection.get("total_required_records", 0) or 0)
    add_check(
        checks,
        "collection_scale_ge_1440_records",
        total_required_records >= 1440,
        f"total_required_records={total_required_records}",
    )
    add_check(
        checks,
        "collection_route_high_fidelity",
        collection.get("route") == "high_fidelity_sim",
        f"route={collection.get('route')!r}",
    )

    analysis_ok, analysis, analysis_detail = passed_json(
        RESULTS / "external_analysis_plan_audit.json",
        version="external_analysis_plan_audit_v1",
    )
    add_check(checks, "external_analysis_plan_ready", analysis_ok, analysis_detail)
    add_check(
        checks,
        "external_analysis_plan_not_evidence",
        analysis.get("not_external_evidence") is True
        and analysis.get("analysis_plan_ready") is True
        and analysis.get("strict_evidence_ready") is False,
        (
            f"not_external_evidence={analysis.get('not_external_evidence')!r}, "
            f"analysis_plan_ready={analysis.get('analysis_plan_ready')!r}, "
            f"strict_evidence_ready={analysis.get('strict_evidence_ready')!r}"
        ),
    )
    analysis_checks = {check.get("name"): check.get("passed") for check in analysis.get("checks", []) or []}
    add_check(
        checks,
        "external_analysis_plan_threshold_lock",
        analysis_checks.get("plan_is_non_evidence_and_locked") is True
        and analysis_checks.get("thresholds_match_log_schema") is True
        and analysis_checks.get("primary_hypotheses_cover_all_strict_thresholds") is True
        and analysis_checks.get("paired_key_matches_schema") is True,
        f"analysis_checks={analysis_checks}",
    )
    add_check(
        checks,
        "external_analysis_plan_exclusion_policy",
        analysis_checks.get("exclusion_policy_blocks_cherry_picking") is True
        and analysis_checks.get("unblinding_policy_preserves_blind_eval") is True
        and analysis_checks.get("required_reporting_covers_primary_and_audit_outputs") is True,
        f"analysis_checks={analysis_checks}",
    )

    route_ok, route, route_detail = passed_json(
        RESULTS / "independent_validation_route_audit.json",
        version="independent_validation_route_v1",
    )
    add_check(checks, "independent_validation_route_ready", route_ok, route_detail)
    add_check(
        checks,
        "independent_route_not_evidence",
        route.get("not_external_evidence") is True,
        f"not_external_evidence={route.get('not_external_evidence')!r}",
    )
    route_checks = {check.get("name"): check.get("passed") for check in route.get("checks", []) or []}
    add_check(
        checks,
        "independent_route_primary_covers_tasks",
        route_checks.get("primary_route_covers_collection_tasks") is True,
        f"primary_route={route.get('primary_route')!r}, planned_tasks={route.get('planned_tasks', [])!r}",
    )
    add_check(
        checks,
        "independent_route_closes_blockers",
        route_checks.get("all_readiness_blockers_have_route_closure") is True,
        f"readiness_blockers={route.get('readiness_blockers', [])!r}",
    )

    platform_probe_ok, platform_probe, platform_probe_detail = passed_json(
        RESULTS / "external_platform_probe.json",
        version="external_platform_probe_v1",
    )
    add_check(checks, "external_platform_probe_ready", platform_probe_ok, platform_probe_detail)
    add_check(
        checks,
        "external_platform_probe_not_evidence",
        platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_fidelity_evidence_ready") is False
        and platform_probe.get("strict_external_evidence_ready") is False,
        (
            f"primary_route_install_ready={platform_probe.get('primary_route_install_ready')!r}, "
            f"strict_external_evidence_ready={platform_probe.get('strict_external_evidence_ready')!r}"
        ),
    )

    task_binding_ok, task_binding, task_binding_detail = passed_json(
        RESULTS / "maniskill_task_binding_probe.json",
        version="maniskill_task_binding_probe_v1",
    )
    add_check(checks, "maniskill_task_binding_probe_ready", task_binding_ok, task_binding_detail)
    add_check(
        checks,
        "maniskill_task_binding_probe_not_evidence",
        task_binding.get("not_external_evidence") is True
        and task_binding.get("task_binding_probe_ready") is True
        and task_binding.get("accepted_task_binding_ready") is False
        and task_binding.get("strict_fidelity_evidence_ready") is False
        and task_binding.get("strict_external_evidence_ready") is False,
        (
            f"strict_task_binding_install_ready={task_binding.get('strict_task_binding_install_ready')!r}, "
            f"accepted_task_binding_ready={task_binding.get('accepted_task_binding_ready')!r}"
        ),
    )

    env_smoke_ok, env_smoke, env_smoke_detail = passed_json(
        RESULTS / "maniskill_env_smoke_probe.json",
        version="maniskill_env_smoke_probe_v1",
    )
    add_check(checks, "maniskill_env_smoke_probe_ready", env_smoke_ok, env_smoke_detail)
    add_check(
        checks,
        "maniskill_env_smoke_probe_not_evidence",
        env_smoke.get("not_external_evidence") is True
        and env_smoke.get("env_smoke_probe_ready") is True
        and env_smoke.get("accepted_fidelity_ready") is False
        and env_smoke.get("strict_fidelity_evidence_ready") is False
        and env_smoke.get("strict_external_evidence_ready") is False,
        (
            f"strict_env_smoke_ready={env_smoke.get('strict_env_smoke_ready')!r}, "
            f"primary_reset_missing={env_smoke.get('primary_reset_missing')!r}"
        ),
    )

    fidelity_metadata_ok, fidelity_metadata, fidelity_metadata_detail = passed_json(
        RESULTS / "maniskill_fidelity_metadata_probe.json",
        version="maniskill_fidelity_metadata_probe_v1",
    )
    add_check(checks, "maniskill_fidelity_metadata_probe_ready", fidelity_metadata_ok, fidelity_metadata_detail)
    add_check(
        checks,
        "maniskill_fidelity_metadata_probe_not_evidence",
        fidelity_metadata.get("not_external_evidence") is True
        and fidelity_metadata.get("metadata_probe_ready") is True
        and fidelity_metadata.get("accepted_fidelity_ready") is False
        and fidelity_metadata.get("strict_fidelity_evidence_ready") is False
        and fidelity_metadata.get("strict_external_evidence_ready") is False,
        (
            f"strict_metadata_ready={fidelity_metadata.get('strict_metadata_ready')!r}, "
            f"primary_metadata_missing={fidelity_metadata.get('primary_metadata_missing')!r}"
        ),
    )

    onboarding_ok, onboarding, onboarding_detail = passed_json(
        RESULTS / "external_platform_onboarding_audit.json",
        version="external_platform_onboarding_audit_v1",
    )
    add_check(checks, "external_platform_onboarding_ready", onboarding_ok, onboarding_detail)
    add_check(
        checks,
        "external_platform_onboarding_not_evidence",
        onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False,
        (
            f"not_external_evidence={onboarding.get('not_external_evidence')!r}, "
            f"platform_onboarding_ready={onboarding.get('platform_onboarding_ready')!r}, "
            f"strict_evidence_ready={onboarding.get('strict_evidence_ready')!r}"
        ),
    )
    onboarding_checks = {check.get("name"): check.get("passed") for check in onboarding.get("checks", []) or []}
    add_check(
        checks,
        "external_platform_onboarding_sources_and_provenance",
        onboarding_checks.get("primary_route_matches_independent_plan") is True
        and onboarding_checks.get("official_sources_are_primary_and_currently_checked") is True
        and onboarding_checks.get("platform_provenance_fields_cover_fidelity_hashes_and_observations") is True,
        f"onboarding_checks={onboarding_checks}",
    )
    add_check(
        checks,
        "external_platform_onboarding_gate_order",
        onboarding_checks.get("strict_command_includes_audit_external_backend_contract") is True
        and onboarding_checks.get("strict_command_includes_audit_external_collection_readiness") is True
        and onboarding_checks.get("strict_command_includes_real_collection_runner") is True
        and onboarding_checks.get("strict_command_includes_audit_external_evidence") is True
        and onboarding_checks.get("pilot_sequence_preserves_gate_order") is True,
        f"onboarding_checks={onboarding_checks}",
    )

    method_ok, method_packet, method_detail = passed_json(
        RESULTS / "external_method_implementation_audit.json",
        version="external_method_implementation_audit_v1",
    )
    add_check(checks, "external_method_implementation_packet_ready", method_ok, method_detail)
    method_checks = {check.get("name"): check.get("passed") for check in method_packet.get("checks", []) or []}
    add_check(
        checks,
        "external_method_implementation_not_evidence",
        method_packet.get("not_external_evidence") is True
        and method_packet.get("method_implementation_packet_ready") is True
        and method_packet.get("strict_adapter_evidence_ready") is False,
        (
            f"not_external_evidence={method_packet.get('not_external_evidence')!r}, "
            f"method_implementation_packet_ready={method_packet.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_packet.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_method_implementation_covers_missing_methods",
        method_checks.get("work_orders_cover_all_missing_non_oracle_methods") is True
        and method_checks.get("oracle_excluded_from_work_orders") is True
        and method_checks.get("manifest_entry_templates_cover_required_hash_fields") is True
        and method_checks.get("work_orders_forbid_scaffolds_and_reference_adapters") is True
        and method_checks.get("policy_or_config_hash_in_logs_required") is True
        and method_checks.get("adapter_acceptance_fixtures_cover_non_oracle_methods") is True
        and method_checks.get("adapter_acceptance_fixtures_define_contract") is True
        and method_checks.get("method_manifest_cutover_checklist_covers_non_oracle_methods") is True
        and method_checks.get("method_manifest_cutover_checklist_binds_manifest_fields") is True
        and method_checks.get("method_manifest_cutover_checklist_forbids_shortcuts") is True
        and method_checks.get("work_orders_reference_acceptance_fixtures") is True
        and method_checks.get("reference_adapter_provenance_covers_non_oracle_methods") is True
        and method_checks.get("reference_adapter_hashes_recorded") is True
        and method_checks.get("reference_adapters_marked_non_evidence") is True
        and method_checks.get("reference_manifest_stubs_not_strict_ready") is True
        and method_checks.get("adapter_evidence_still_missing") is True,
        f"method_checks={method_checks}",
    )
    add_check(
        checks,
        "external_method_implementation_gate_order",
        method_checks.get("strict_commands_cover_adapter_rollout_pairing_and_evidence") is True
        and (EXTERNAL / "method_implementation_packet.md").exists()
        and (EXTERNAL / "method_implementation_work_orders.csv").exists()
        and (EXTERNAL / "method_reference_provenance.csv").exists()
        and (EXTERNAL / "method_manifest_cutover_checklist.csv").exists()
        and (EXTERNAL / "method_manifest_cutover_checklist.md").exists()
        and (EXTERNAL / "adapter_acceptance_fixtures.json").exists()
        and (EXTERNAL / "adapter_acceptance_fixtures.md").exists()
        and (EXTERNAL / "adapter_acceptance_fixtures.csv").exists()
        and (ROOT / "scripts" / "build_external_method_implementation_packet.py").exists(),
        "method packet, work orders, adapter fixtures, manifest cutover checklist, reference provenance, builder, and strict command order are present",
    )

    fidelity_ok, fidelity, fidelity_detail = passed_json(
        RESULTS / "external_fidelity_acceptance_audit.json",
        version="external_fidelity_acceptance_audit_v1",
    )
    add_check(checks, "fidelity_acceptance_contract_ready", fidelity_ok, fidelity_detail)
    add_check(
        checks,
        "fidelity_acceptance_not_evidence",
        fidelity.get("not_external_evidence") is True,
        f"not_external_evidence={fidelity.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "fidelity_acceptance_fail_closed",
        fidelity.get("acceptance_ready") is False
        and fidelity.get("readiness_state") == "COLLECT_PLATFORM_PROVENANCE"
        and int(fidelity.get("blocking_missing_count", 0) or 0) >= 10,
        (
            f"acceptance_ready={fidelity.get('acceptance_ready')!r}, "
            f"readiness_state={fidelity.get('readiness_state')!r}, "
            f"blocking_missing_count={fidelity.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "fidelity_acceptance_task_coverage",
        any(
            check.get("name") == "task_fidelity_covers_core_tasks" and check.get("passed") is True
            for check in fidelity.get("contract_checks", []) or []
        ),
        "core external task-fidelity rows are declared in the acceptance template",
    )

    fidelity_provenance_ok, fidelity_provenance, fidelity_provenance_detail = passed_json(
        RESULTS / "external_fidelity_provenance_audit.json",
        version="external_fidelity_provenance_audit_v1",
    )
    add_check(checks, "external_fidelity_provenance_packet_ready", fidelity_provenance_ok, fidelity_provenance_detail)
    fidelity_provenance_checks = {check.get("name"): check.get("passed") for check in fidelity_provenance.get("checks", []) or []}
    add_check(
        checks,
        "external_fidelity_provenance_not_evidence",
        fidelity_provenance.get("not_external_evidence") is True
        and fidelity_provenance.get("fidelity_provenance_packet_ready") is True
        and fidelity_provenance.get("strict_fidelity_evidence_ready") is False
        and fidelity_provenance.get("strict_external_evidence_ready") is False,
        (
            f"not_external_evidence={fidelity_provenance.get('not_external_evidence')!r}, "
            f"fidelity_provenance_packet_ready={fidelity_provenance.get('fidelity_provenance_packet_ready')!r}, "
            f"strict_fidelity_evidence_ready={fidelity_provenance.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={fidelity_provenance.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_fidelity_provenance_covers_acceptance_blocker",
        fidelity_provenance_checks.get("work_orders_cover_fidelity_blockers") is True
        and fidelity_provenance_checks.get("fidelity_acceptance_contract_ready_but_not_evidence") is True
        and (EXTERNAL / "fidelity_provenance_packet.json").exists()
        and (EXTERNAL / "fidelity_provenance_packet.md").exists()
        and (EXTERNAL / "fidelity_provenance_work_orders.csv").exists(),
        f"checks={fidelity_provenance_checks}",
    )
    add_check(
        checks,
        "external_fidelity_provenance_gate_order",
        fidelity_provenance_checks.get("strict_commands_cover_fidelity_manifest_collection_and_evidence") is True
        and fidelity_provenance_checks.get("no_real_acceptance_or_manifest_written") is True,
        f"checks={fidelity_provenance_checks}",
    )

    fidelity_materialization_ok, fidelity_materialization, fidelity_materialization_detail = passed_json(
        RESULTS / "fidelity_acceptance_materialization_plan.json",
        version="fidelity_acceptance_materialization_plan_v1",
    )
    add_check(checks, "fidelity_acceptance_materializer_ready", fidelity_materialization_ok, fidelity_materialization_detail)
    fidelity_materialization_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", []) or []}
    materializer_checkout = fidelity_materialization.get("current_checkout", {}) or {}
    add_check(
        checks,
        "fidelity_acceptance_materializer_not_evidence",
        fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False,
        (
            f"not_external_evidence={fidelity_materialization.get('not_external_evidence')!r}, "
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}"
        ),
    )
    add_check(
        checks,
        "fidelity_acceptance_materializer_guarded",
        fidelity_materialization_checks.get("operator_write_command_is_guarded") is True
        and fidelity_materialization_checks.get("current_checkout_hashes_recorded") is True
        and fidelity_materialization_checks.get("write_requires_clean_checkout") is True
        and fidelity_materialization_checks.get("write_requires_current_code_commit_and_skill_hash") is True
        and len(str(materializer_checkout.get("code_commit", ""))) == 40
        and len(str(materializer_checkout.get("skill_library_hash", ""))) == 64
        and "materialize_fidelity_acceptance.py" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-real-platform" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-independent-operator" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-render-backed-videos" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-real-rollout-evidence" not in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-manifest-declaration" not in str(fidelity_materialization.get("operator_write_command", ""))
        and (ROOT / "scripts" / "materialize_fidelity_acceptance.py").exists()
        and (RESULTS / "fidelity_acceptance_materialization_plan.md").exists(),
        (
            f"command={fidelity_materialization.get('operator_write_command', '')!r}, "
            f"commit={materializer_checkout.get('code_commit')!r}, "
            f"skill_hash={materializer_checkout.get('skill_library_hash')!r}, "
            f"clean={materializer_checkout.get('clean_checkout')!r}, "
            f"dirty_count={len(materializer_checkout.get('dirty_status_lines', []) or [])}"
        ),
    )
    materializer_self_ok, materializer_self, materializer_self_detail = passed_json(
        RESULTS / "fidelity_acceptance_materializer_self_test.json",
        version="fidelity_acceptance_materializer_self_test_v1",
    )
    materializer_self_checks = {check.get("name"): check.get("passed") for check in materializer_self.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_self_test_ready",
        materializer_self_ok
        and materializer_self.get("not_external_evidence") is True
        and (ROOT / "scripts" / "self_test_fidelity_acceptance_materializer.py").exists()
        and (RESULTS / "fidelity_acceptance_materializer_self_test.md").exists(),
        f"{materializer_self_detail}, not_external_evidence={materializer_self.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "fidelity_acceptance_materializer_self_test_guards",
        materializer_self_checks.get("matching_clean_checkout_writes_temp_acceptance") is True
        and materializer_self_checks.get("stale_commit_rejected_without_temp_write") is True
        and materializer_self_checks.get("mismatched_skill_hash_rejected_without_temp_write") is True
        and materializer_self_checks.get("dirty_checkout_rejected_without_temp_write") is True
        and materializer_self_checks.get("pycache_excluded_from_skill_library_hash") is True
        and materializer_self_checks.get("real_acceptance_file_not_touched") is True,
        f"checks={materializer_self_checks}",
    )

    blind_ok, blind, blind_detail = passed_json(
        RESULTS / "external_blind_eval_audit.json",
        version="external_blind_eval_plan_v1",
    )
    add_check(checks, "blind_eval_plan_ready", blind_ok, blind_detail)
    add_check(
        checks,
        "blind_eval_not_evidence",
        blind.get("not_external_evidence") is True,
        f"not_external_evidence={blind.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "blind_eval_row_budget",
        int(blind.get("row_count", 0) or 0) >= 1440 and int(blind.get("alias_count", 0) or 0) >= 12,
        f"rows={blind.get('row_count')!r}, aliases={blind.get('alias_count')!r}",
    )
    add_check(
        checks,
        "blind_eval_no_method_leak",
        any(
            check.get("name") == "blinded_sheet_has_no_method_names" and check.get("passed") is True
            for check in blind.get("checks", []) or []
        ),
        "blinded operator sheet is checked for method-name leakage",
    )

    runbook_ok, runbook, runbook_detail = passed_json(
        RESULTS / "external_runbook_audit.json",
        version="external_runbook_audit_v1",
    )
    add_check(checks, "operator_runbook_ready", runbook_ok, runbook_detail)
    operator_rows = int(runbook.get("operator_rows", 0) or 0)
    add_check(
        checks,
        "operator_sheet_covers_collection_plan",
        operator_rows >= max(total_required_records, 1440),
        f"operator_rows={operator_rows}, total_required_records={total_required_records}",
    )

    runner_ok, runner, runner_detail = passed_json(
        RESULTS / "external_runner_harness_audit.json",
        version="external_runner_harness_audit_v1",
    )
    add_check(checks, "external_runner_harness_ready", runner_ok, runner_detail)
    add_check(
        checks,
        "external_runner_harness_not_evidence",
        runner.get("not_external_evidence") is True,
        f"not_external_evidence={runner.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "external_runner_harness_fail_closed",
        runner.get("actual_execution_ready") is False
        and any(
            check.get("name") == "runner_rejects_template_backend_for_actual_collection"
            and check.get("passed") is True
            for check in runner.get("checks", []) or []
        ),
        f"actual_execution_ready={runner.get('actual_execution_ready')!r}",
    )

    runner_probe_ok, runner_probe, runner_probe_detail = passed_json(
        RESULTS / "external_runner_backend_self_test.json",
        version="external_runner_backend_self_test_v1",
    )
    add_check(checks, "external_runner_backend_probe_ready", runner_probe_ok, runner_probe_detail)
    runner_probe_checks = {check.get("name"): check.get("passed") for check in runner_probe.get("checks", []) or []}
    add_check(
        checks,
        "external_runner_backend_probe_not_evidence",
        runner_probe.get("not_external_evidence") is True
        and int(runner_probe.get("records_written", 0) or 0) >= 2
        and not runner_probe.get("schema_errors"),
        (
            f"not_external_evidence={runner_probe.get('not_external_evidence')!r}, "
            f"records_written={runner_probe.get('records_written')!r}, "
            f"schema_errors={runner_probe.get('schema_errors')!r}"
        ),
    )
    add_check(
        checks,
        "external_runner_backend_probe_exercises_actual_runner_path",
        runner_probe_checks.get("runner_actual_path_exits_zero") is True
        and runner_probe_checks.get("temporary_records_schema_valid") is True
        and runner_probe_checks.get("temporary_videos_written") is True
        and runner_probe_checks.get("real_manifest_untouched") is True,
        f"checks={runner_probe_checks}",
    )

    pilot_audit_ok, pilot_audit, pilot_audit_detail = passed_json(
        RESULTS / "external_pilot_smoke_audit.json",
        version="external_pilot_smoke_audit_v1",
    )
    add_check(checks, "external_pilot_smoke_audit_ready", pilot_audit_ok, pilot_audit_detail)
    add_check(
        checks,
        "external_pilot_smoke_not_evidence",
        pilot_audit.get("not_external_evidence") is True
        and pilot_audit.get("strict_evidence_ready") is False
        and pilot_audit.get("pilot_smoke_ready") is False,
        (
            f"not_external_evidence={pilot_audit.get('not_external_evidence')!r}, "
            f"pilot_smoke_ready={pilot_audit.get('pilot_smoke_ready')!r}, "
            f"strict_evidence_ready={pilot_audit.get('strict_evidence_ready')!r}"
        ),
    )
    pilot_packet_ok, pilot_packet, pilot_packet_detail = passed_json(
        RESULTS / "external_pilot_smoke_packet_audit.json",
        version="external_pilot_smoke_packet_audit_v1",
    )
    add_check(checks, "external_pilot_smoke_packet_ready", pilot_packet_ok, pilot_packet_detail)
    pilot_packet_checks = {check.get("name"): check.get("passed") for check in pilot_packet.get("checks", []) or []}
    add_check(
        checks,
        "external_pilot_smoke_quarantine_gate",
        pilot_packet.get("not_external_evidence") is True
        and pilot_packet.get("pilot_smoke_packet_ready") is True
        and pilot_packet.get("strict_evidence_ready") is False
        and pilot_packet_checks.get("quarantine_dirs_are_separate_from_official_evidence") is True
        and pilot_packet_checks.get("pilot_commands_preserve_gate_order") is True
        and (EXTERNAL / "pilot_smoke_packet.md").exists()
        and (EXTERNAL / "pilot_smoke_work_orders.csv").exists(),
        f"checks={pilot_packet_checks}",
    )

    pilot_runtime_ok, pilot_runtime, pilot_runtime_detail = passed_json(
        RESULTS / "maniskill_pilot_runtime_liveness_audit.json",
        version="maniskill_pilot_runtime_liveness_audit_v1",
    )
    add_check(checks, "maniskill_pilot_runtime_liveness_ready", pilot_runtime_ok, pilot_runtime_detail)
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", []) or []}
    pilot_runtime_triage = pilot_runtime.get("reset_timeout_triage", {})
    pilot_runtime_records = int(pilot_runtime.get("records_observed", 0) or 0)
    pilot_runtime_videos = int(pilot_runtime.get("videos_written", 0) or 0)
    pilot_runtime_fallbacks = len(pilot_runtime.get("diagnostic_video_fallbacks", []) or [])
    pilot_runtime_basic = (
        pilot_runtime.get("not_external_evidence") is True
        and pilot_runtime.get("strict_external_evidence_ready") is False
        and pilot_runtime.get("pilot_runtime_ready") is False
        and pilot_runtime.get("render_video_ready") is False
        and pilot_runtime_checks.get("bounded_runner_subprocess_exercised") is True
        and pilot_runtime_checks.get("timeout_or_result_recorded_as_readiness_state") is True
        and pilot_runtime_checks.get("backend_reset_substage_markers_recorded") is True
        and pilot_runtime_checks.get("reset_timeout_triage_is_non_evidence") is True
        and pilot_runtime_checks.get("reset_timeout_triage_context_recorded") is True
        and pilot_runtime_checks.get("reset_timeout_operator_actions_present") is True
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
    pilot_runtime_diagnostic_rejected = (
        pilot_runtime.get("runner_io_ready") is False
        and pilot_runtime_records == 0
        and pilot_runtime_fallbacks >= 1
        and pilot_runtime.get("diagnostic_sidecar_rejected_before_jsonl_write") is True
        and pilot_runtime.get("official_video_guard_blocked_diagnostic_fallback") is True
        and pilot_runtime.get("diagnostic_sidecar_paths_quarantined") is True
        and pilot_runtime_checks.get("official_guard_rejects_diagnostic_before_jsonl_write") is True
        and pilot_runtime_checks.get("diagnostic_rejection_paths_are_quarantined") is True
    )
    add_check(
        checks,
        "maniskill_pilot_runtime_liveness_not_evidence",
        pilot_runtime_basic
        and (pilot_runtime_diagnostic_io or pilot_runtime_unavailable or pilot_runtime_diagnostic_rejected),
        (
            f"pilot_runtime_ready={pilot_runtime.get('pilot_runtime_ready')!r}, "
            f"runner_io_ready={pilot_runtime.get('runner_io_ready')!r}, "
            f"render_video_ready={pilot_runtime.get('render_video_ready')!r}, "
            f"timed_out={pilot_runtime.get('timed_out')!r}, "
            f"records={pilot_runtime_records!r}, "
            f"videos={pilot_runtime_videos!r}, "
            f"diagnostic_fallbacks={pilot_runtime_fallbacks}, "
            f"diagnostic_rejected={pilot_runtime.get('diagnostic_sidecar_rejected_before_jsonl_write')!r}, "
            f"failure_summary={pilot_runtime.get('failure_summary')!r}"
        ),
    )
    pilot_reset_triage_ready = (
        pilot_runtime_triage.get("version") == "maniskill_pilot_reset_timeout_triage_v1"
        and pilot_runtime_triage.get("not_external_evidence") is True
        and pilot_runtime_triage.get("strict_external_evidence_ready") is False
        and (
            pilot_runtime.get("last_progress_stage") != "reset_scene_start"
            or (
                pilot_runtime_triage.get("reset_timeout") is True
                and pilot_runtime_triage.get("triage_status") == "RESET_SCENE_TIMEOUT_TRIAGE_READY"
                and bool(str(pilot_runtime_triage.get("task_family", "")).strip())
                and bool(str(pilot_runtime_triage.get("method_name", "")).strip())
                and bool(str(pilot_runtime_triage.get("config_hash", "")).strip())
                and bool(str(pilot_runtime_triage.get("primary_env_id", "")).strip())
                and bool(str(pilot_runtime_triage.get("last_backend_progress_stage", "")).strip())
                and bool(pilot_runtime_triage.get("backend_progress_stages"))
                and len(pilot_runtime_triage.get("operator_next_actions", []) or []) >= 5
            )
        )
        and (RESULTS / "maniskill_pilot_reset_timeout_triage.json").exists()
        and (RESULTS / "maniskill_pilot_reset_timeout_triage.md").exists()
    )
    add_check(
        checks,
        "maniskill_pilot_reset_timeout_triage_ready",
        pilot_reset_triage_ready,
        (
            f"status={pilot_runtime_triage.get('triage_status')!r}, "
            f"reset_timeout={pilot_runtime_triage.get('reset_timeout')!r}, "
            f"task={pilot_runtime_triage.get('task_family')!r}, "
            f"method={pilot_runtime_triage.get('method_name')!r}, "
            f"env={pilot_runtime_triage.get('primary_env_id')!r}, "
            f"backend_stage={pilot_runtime_triage.get('last_backend_progress_stage')!r}"
        ),
    )

    render_resource_ok, render_resource, render_resource_detail = passed_json(
        RESULTS / "maniskill_render_resource_sweep.json",
        version="maniskill_render_resource_sweep_v1",
    )
    add_check(checks, "maniskill_render_resource_sweep_ready", render_resource_ok, render_resource_detail)
    render_resource_checks = {check.get("name"): check.get("passed") for check in render_resource.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_resource_sweep_not_evidence",
        render_resource.get("not_external_evidence") is True
        and render_resource.get("strict_external_evidence_ready") is False
        and render_resource.get("any_render_video_ready") is False
        and render_resource.get("descriptor_pool_failure_persists_at_minimum_resolution") is True
        and int(render_resource.get("record_count", 0) or 0) >= 3
        and "vulkan_descriptor_pool_exhaustion" in (render_resource.get("renderer_failure_classes", []) or [])
        and render_resource_checks.get("resource_sweep_is_non_evidence") is True
        and render_resource_checks.get("quarantine_paths_are_not_official_evidence") is True
        and (RESULTS / "maniskill_render_resource_sweep.md").exists()
        and (EXTERNAL / "render_resource_sweep_work_orders.csv").exists(),
        (
            f"any_ready={render_resource.get('any_render_video_ready')!r}, "
            f"records={render_resource.get('record_count')!r}, "
            f"classes={render_resource.get('renderer_failure_classes')!r}"
        ),
    )

    render_machine_ok, render_machine, render_machine_detail = passed_json(
        RESULTS / "maniskill_render_machine_qualification.json",
        version="maniskill_render_machine_qualification_v1",
    )
    add_check(checks, "maniskill_render_machine_qualification_ready", render_machine_ok, render_machine_detail)
    render_machine_checks = {check.get("name"): check.get("passed") for check in render_machine.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_machine_qualification_not_evidence",
        render_machine.get("not_external_evidence") is True
        and render_machine.get("strict_external_evidence_ready") is False
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and bool(render_machine.get("blocking_missing"))
        and render_machine_checks.get("qualification_packet_is_non_evidence") is True
        and render_machine_checks.get("current_machine_fail_closed_when_render_not_ready") is True,
        (
            f"qualification_state={render_machine.get('qualification_state')!r}, "
            f"render_machine_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"blocking={len(render_machine.get('blocking_missing', []) or [])}"
        ),
    )
    add_check(
        checks,
        "maniskill_render_machine_operator_commands",
        all(
            fragment in "\n".join(render_machine.get("operator_commands", []) or [])
            for fragment in (
                "probe_external_platform.py",
                "audit_maniskill_render_video_preflight.py",
                "audit_maniskill_pilot_runtime_liveness.py",
                "materialize_fidelity_acceptance.py",
                "audit_external_collection_readiness.py",
            )
        )
        and (EXTERNAL / "render_machine_qualification_packet.md").exists(),
        "render machine qualification packet commands and packet file are present",
    )
    render_remediation_ok, render_remediation, render_remediation_detail = passed_json(
        RESULTS / "maniskill_render_failure_remediation.json",
        version="maniskill_render_failure_remediation_v1",
    )
    add_check(checks, "maniskill_render_failure_remediation_ready", render_remediation_ok, render_remediation_detail)
    render_remediation_checks = {check.get("name"): check.get("passed") for check in render_remediation.get("checks", []) or []}
    render_remediation_work_ids = {
        str(item.get("id", ""))
        for item in render_remediation.get("work_orders", []) or []
        if isinstance(item, dict)
    }
    add_check(
        checks,
        "maniskill_render_failure_remediation_not_evidence",
        render_remediation.get("not_external_evidence") is True
        and render_remediation.get("strict_external_evidence_ready") is False
        and render_remediation.get("remediation_state") == "RENDER_REMEDIATION_REQUIRED"
        and render_remediation.get("qualification_state") == render_machine.get("qualification_state")
        and bool(render_remediation.get("liveness_render_errors"))
        and render_remediation_checks.get("render_failure_remediation_is_non_evidence") is True
        and render_remediation_checks.get("work_orders_cover_required_gate_sequence") is True
        and {
            "renderer_platform_probe",
            "render_profile_matrix_retest",
            "pilot_liveness_retest",
            "diagnostic_fallback_exclusion",
            "fidelity_acceptance_after_render_ready",
            "collection_readiness_gate",
        }.issubset(render_remediation_work_ids)
        and (RESULTS / "maniskill_render_failure_remediation.md").exists()
        and (EXTERNAL / "render_failure_remediation_work_orders.csv").exists(),
        (
            f"state={render_remediation.get('remediation_state')!r}, "
            f"qualification_state={render_remediation.get('qualification_state')!r}, "
            f"work_orders={sorted(render_remediation_work_ids)}"
        ),
    )

    backend_contract_ok, backend_contract, backend_contract_detail = passed_json(
        RESULTS / "external_backend_contract_audit.json",
        version="external_backend_contract_audit_v1",
    )
    add_check(checks, "external_backend_contract_ready", backend_contract_ok, backend_contract_detail)
    add_check(
        checks,
        "external_backend_contract_not_evidence",
        backend_contract.get("not_external_evidence") is True,
        f"not_external_evidence={backend_contract.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "external_backend_contract_fail_closed",
        backend_contract.get("backend_contract_harness_ready") is True
        and backend_contract.get("actual_backend_ready") is False
        and "audit_external_backend_contract.py --strict" in str(backend_contract.get("strict_command", "")),
        (
            f"backend_contract_harness_ready={backend_contract.get('backend_contract_harness_ready')!r}, "
            f"actual_backend_ready={backend_contract.get('actual_backend_ready')!r}"
        ),
    )
    backend_integration_ok, backend_integration, backend_integration_detail = passed_json(
        RESULTS / "external_backend_integration_audit.json",
        version="external_backend_integration_audit_v1",
    )
    add_check(checks, "external_backend_integration_packet_ready", backend_integration_ok, backend_integration_detail)
    backend_integration_checks = {check.get("name"): check.get("passed") for check in backend_integration.get("checks", []) or []}
    add_check(
        checks,
        "external_backend_integration_not_evidence",
        backend_integration.get("not_external_evidence") is True
        and backend_integration.get("backend_integration_packet_ready") is True
        and backend_integration.get("strict_backend_ready") is False
        and backend_integration.get("strict_evidence_ready") is False,
        (
            f"not_external_evidence={backend_integration.get('not_external_evidence')!r}, "
            f"strict_backend_ready={backend_integration.get('strict_backend_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_backend_integration_covers_backend_blocker",
        backend_integration_checks.get("work_orders_cover_backend_to_manifest_path") is True
        and backend_integration_checks.get("required_hooks_declared") is True
        and backend_integration_checks.get("collection_readiness_still_blocks_backend") is True,
        f"backend_integration_checks={backend_integration_checks}",
    )
    add_check(
        checks,
        "external_backend_integration_gate_order",
        backend_integration_checks.get("strict_commands_cover_backend_config_fidelity_collection_and_evidence") is True
        and (EXTERNAL / "backend_integration_packet.md").exists()
        and (EXTERNAL / "backend_integration_work_orders.csv").exists()
        and (ROOT / "scripts" / "build_external_backend_integration_packet.py").exists(),
        "backend packet, work orders, builder, and strict command order are present",
    )

    collection_readiness_ok, collection_readiness, collection_readiness_detail = passed_json(
        RESULTS / "external_collection_readiness_audit.json",
        version="external_collection_readiness_audit_v1",
    )
    add_check(checks, "external_collection_readiness_audit_ready", collection_readiness_ok, collection_readiness_detail)
    add_check(
        checks,
        "external_collection_readiness_not_evidence",
        collection_readiness.get("not_external_evidence") is True,
        f"not_external_evidence={collection_readiness.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "external_collection_readiness_fail_closed",
        collection_readiness.get("collection_ready") is False
        and collection_readiness.get("readiness_state") == "PREPARE_BACKEND_CONFIGS_AND_FIDELITY"
        and int(collection_readiness.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"collection_ready={collection_readiness.get('collection_ready')!r}, "
            f"readiness_state={collection_readiness.get('readiness_state')!r}, "
            f"blocking_missing_count={collection_readiness.get('blocking_missing_count')!r}"
        ),
    )
    readiness_checks = {check.get("name"): check.get("passed") for check in collection_readiness.get("checks", []) or []}
    add_check(
        checks,
        "external_collection_readiness_packet_shape",
        readiness_checks.get("operator_sheet_row_budget") is True
        and readiness_checks.get("alias_map_complete") is True
        and readiness_checks.get("output_logs_empty_or_force") is True,
        f"readiness_checks={readiness_checks}",
    )
    collection_reference_route = collection_readiness.get("tracked_reference_route", {}) or {}
    collection_reference_blockers = collection_reference_route.get("blocking_missing", []) or []
    collection_reference_checks = {check.get("name"): check.get("passed") for check in collection_reference_route.get("checks", []) or []}
    add_check(
        checks,
        "external_collection_readiness_tracked_reference_route",
        collection_reference_route.get("not_external_evidence") is True
        and "maniskill_reference_backend.py" in str(collection_reference_route.get("backend_module", ""))
        and collection_reference_route.get("run_id") == "maniskill_sapien_reference_preflight_protocol_v1"
        and collection_reference_route.get("collection_ready") is False
        and collection_reference_route.get("strict_external_evidence_ready") is False
        and int(collection_reference_route.get("blocking_missing_count", 0) or 0) == 1
        and any("fidelity_acceptance_ready" in str(item) for item in collection_reference_blockers)
        and collection_reference_checks.get("reference_backend_contract_ready") is True
        and collection_reference_checks.get("reference_task_configs_ready") is True
        and collection_reference_checks.get("reference_fidelity_acceptance_ready") is False
        and "audit_external_collection_readiness.py --strict" in str(collection_reference_route.get("pre_collection_gate_command", ""))
        and "real_collection_runner.py" in str(collection_reference_route.get("collection_command_after_fidelity_acceptance", "")),
        (
            f"backend={collection_reference_route.get('backend_module')!r}, "
            f"run_id={collection_reference_route.get('run_id')!r}, "
            f"blocking={collection_reference_blockers!r}"
        ),
    )

    reference_preflight_ok, reference_preflight, reference_preflight_detail = passed_json(
        RESULTS / "maniskill_reference_collection_preflight_audit.json",
        version="maniskill_reference_collection_preflight_audit_v1",
    )
    add_check(checks, "maniskill_reference_collection_preflight_ready", reference_preflight_ok, reference_preflight_detail)
    reference_preflight_checks = {check.get("name"): check.get("passed") for check in reference_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_collection_preflight_reaches_fidelity_gate",
        reference_preflight.get("not_external_evidence") is True
        and reference_preflight.get("reference_backend_contract_ready") is True
        and reference_preflight.get("collection_ready") is False
        and reference_preflight.get("strict_external_evidence_ready") is False
        and int(reference_preflight.get("collection_blocking_missing_count", 0) or 0) == 1
        and any("fidelity_acceptance_ready" in str(item) for item in reference_preflight.get("collection_blocking_missing", []) or [])
        and reference_preflight_checks.get("reference_backend_collection_preflight_reaches_fidelity_gate") is True,
        (
            f"contract_ready={reference_preflight.get('reference_backend_contract_ready')!r}, "
            f"collection_ready={reference_preflight.get('collection_ready')!r}, "
            f"blocking={reference_preflight.get('collection_blocking_missing')!r}"
        ),
    )

    pairing_ok, pairing, pairing_detail = passed_json(
        RESULTS / "external_pairing_integrity_audit.json",
        version="external_pairing_integrity_audit_v1",
    )
    add_check(checks, "external_pairing_integrity_audit_ready", pairing_ok, pairing_detail)
    add_check(
        checks,
        "external_pairing_integrity_not_evidence",
        pairing.get("not_external_evidence") is True and pairing.get("pairing_ready") is False,
        (
            f"not_external_evidence={pairing.get('not_external_evidence')!r}, "
            f"pairing_ready={pairing.get('pairing_ready')!r}"
        ),
    )

    release_ok, release, release_detail = passed_json(
        RESULTS / "external_release_package_audit.json",
        version="external_release_package_audit_v1",
    )
    add_check(checks, "external_release_package_audit_ready", release_ok, release_detail)
    add_check(
        checks,
        "external_release_package_not_evidence",
        release.get("not_external_evidence") is True and release.get("release_package_ready") is False,
        (
            f"not_external_evidence={release.get('not_external_evidence')!r}, "
            f"release_package_ready={release.get('release_package_ready')!r}"
        ),
    )

    config_template_ok, config_template, config_template_detail = passed_json(
        RESULTS / "external_config_template_audit.json",
        version="external_config_template_audit_v1",
    )
    add_check(checks, "config_templates_ready", config_template_ok, config_template_detail)
    add_check(
        checks,
        "config_schema_exists",
        (EXTERNAL / "config_schema_v1.json").exists(),
        rel(EXTERNAL / "config_schema_v1.json"),
    )
    config_materialization_ok, config_materialization, config_materialization_detail = passed_json(
        RESULTS / "external_config_materialization_plan.json",
        version="external_config_materialization_plan_v1",
    )
    add_check(checks, "config_materialization_plan_ready", config_materialization_ok, config_materialization_detail)
    add_check(
        checks,
        "config_materialization_plan_not_evidence",
        config_materialization.get("not_external_evidence") is True
        and config_materialization.get("write_enabled") is False
        and config_materialization.get("strict_config_evidence_ready") is False,
        (
            f"not_external_evidence={config_materialization.get('not_external_evidence')!r}, "
            f"write_enabled={config_materialization.get('write_enabled')!r}, "
            f"strict_config_evidence_ready={config_materialization.get('strict_config_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "config_materialization_covers_tasks",
        int(config_materialization.get("task_count", 0) or 0) >= 4,
        f"task_count={config_materialization.get('task_count')!r}",
    )
    config_manifest_ok, config_manifest, config_manifest_detail = passed_json(
        RESULTS / "external_config_manifest_audit.json",
        version="external_config_manifest_audit_v1",
    )
    add_check(checks, "external_config_manifest_packet_ready", config_manifest_ok, config_manifest_detail)
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest.get("checks", []) or []}
    add_check(
        checks,
        "external_config_manifest_not_evidence",
        config_manifest.get("not_external_evidence") is True
        and config_manifest.get("config_manifest_packet_ready") is True
        and config_manifest.get("strict_config_evidence_ready") is False
        and config_manifest.get("manifest_declared_config_ready") is False,
        (
            f"not_external_evidence={config_manifest.get('not_external_evidence')!r}, "
            f"config_manifest_packet_ready={config_manifest.get('config_manifest_packet_ready')!r}, "
            f"strict_config_evidence_ready={config_manifest.get('strict_config_evidence_ready')!r}, "
            f"manifest_declared_config_ready={config_manifest.get('manifest_declared_config_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_config_manifest_covers_manifest_config_blocker",
        config_manifest_checks.get("work_orders_cover_config_to_manifest_path") is True
        and config_manifest_checks.get("prepared_configs_pass_strict_schema_if_manifest_declared") is True
        and (EXTERNAL / "config_manifest_packet.json").exists()
        and (EXTERNAL / "config_manifest_packet.md").exists()
        and (EXTERNAL / "config_manifest_work_orders.csv").exists(),
        f"checks={config_manifest_checks}",
    )
    add_check(
        checks,
        "external_config_manifest_gate_order",
        config_manifest_checks.get("strict_commands_cover_config_manifest_release_and_evidence") is True
        and config_manifest_checks.get("strict_config_evidence_still_fails_without_manifest") is True,
        f"checks={config_manifest_checks}",
    )

    rollout_evidence_ok, rollout_evidence, rollout_evidence_detail = passed_json(
        RESULTS / "external_rollout_evidence_audit.json",
        version="external_rollout_evidence_audit_v1",
    )
    add_check(checks, "external_rollout_evidence_packet_ready", rollout_evidence_ok, rollout_evidence_detail)
    rollout_evidence_checks = {check.get("name"): check.get("passed") for check in rollout_evidence.get("checks", []) or []}
    add_check(
        checks,
        "external_rollout_evidence_not_evidence",
        rollout_evidence.get("not_external_evidence") is True
        and rollout_evidence.get("rollout_evidence_packet_ready") is True
        and rollout_evidence.get("strict_rollout_evidence_ready") is False
        and rollout_evidence.get("strict_external_evidence_ready") is False,
        (
            f"not_external_evidence={rollout_evidence.get('not_external_evidence')!r}, "
            f"rollout_evidence_packet_ready={rollout_evidence.get('rollout_evidence_packet_ready')!r}, "
            f"strict_rollout_evidence_ready={rollout_evidence.get('strict_rollout_evidence_ready')!r}, "
            f"strict_external_evidence_ready={rollout_evidence.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_rollout_evidence_covers_raw_log_blocker",
        rollout_evidence_checks.get("task_work_orders_cover_all_planned_tasks") is True
        and rollout_evidence_checks.get("strict_rollout_metrics_still_fail_without_manifest") is True
        and (EXTERNAL / "rollout_evidence_packet.json").exists()
        and (EXTERNAL / "rollout_evidence_packet.md").exists()
        and (EXTERNAL / "rollout_evidence_work_orders.csv").exists(),
        f"checks={rollout_evidence_checks}",
    )
    add_check(
        checks,
        "external_rollout_evidence_gate_order",
        rollout_evidence_checks.get("strict_commands_cover_collection_manifest_rollout_pairing_release_evidence") is True
        and rollout_evidence_checks.get("strict_gate_audits_remain_fail_closed") is True,
        f"checks={rollout_evidence_checks}",
    )

    ablation_ok, ablation_packet, ablation_detail = passed_json(
        RESULTS / "external_ablation_collection_audit.json",
        version="external_ablation_collection_audit_v1",
    )
    add_check(checks, "external_ablation_collection_packet_ready", ablation_ok, ablation_detail)
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_packet.get("checks", []) or []}
    add_check(
        checks,
        "external_ablation_collection_not_evidence",
        ablation_packet.get("not_external_evidence") is True
        and ablation_packet.get("strict_external_evidence_ready") is False
        and ablation_packet.get("manifest_ablation_evidence_ready") is False,
        (
            f"not_external_evidence={ablation_packet.get('not_external_evidence')!r}, "
            f"manifest_ablation_evidence_ready={ablation_packet.get('manifest_ablation_evidence_ready')!r}, "
            f"strict_external_evidence_ready={ablation_packet.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_ablation_collection_covers_strict_ablation_blocker",
        int(ablation_packet.get("work_order_count", 0) or 0) == 5
        and int(ablation_packet.get("expected_ablation_records", 0) or 0) >= 600
        and ablation_checks.get("every_required_ablation_has_work_order") is True
        and ablation_checks.get("required_ablations_match_strict_audit") is True
        and ablation_checks.get("operator_commands_cover_collection_manifest_rollout_and_strict_evidence") is True
        and (EXTERNAL / "ablation_collection_packet.json").exists()
        and (EXTERNAL / "ablation_collection_packet.md").exists()
        and (EXTERNAL / "ablation_collection_work_orders.csv").exists(),
        (
            f"work_order_count={ablation_packet.get('work_order_count')!r}, "
            f"expected_ablation_records={ablation_packet.get('expected_ablation_records')!r}, "
            f"checks={ablation_checks}"
        ),
    )

    intake_ok, intake_ledger, intake_detail = passed_json(
        RESULTS / "external_evidence_intake_ledger_audit.json",
        version="external_evidence_intake_ledger_v1",
    )
    add_check(checks, "external_evidence_intake_ledger_ready", intake_ok, intake_detail)
    intake_checks = {check.get("name"): check.get("passed") for check in intake_ledger.get("checks", []) or []}
    add_check(
        checks,
        "external_evidence_intake_ledger_not_evidence",
        intake_ledger.get("not_external_evidence") is True
        and intake_ledger.get("strict_external_evidence_ready") is False,
        (
            f"not_external_evidence={intake_ledger.get('not_external_evidence')!r}, "
            f"strict_external_evidence_ready={intake_ledger.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_evidence_intake_ledger_maps_all_strict_failures",
        int(intake_ledger.get("blocking_failure_count", 0) or 0) >= 30
        and intake_ledger.get("blocking_failure_count") == intake_ledger.get("mapped_failure_count")
        and not intake_ledger.get("unmapped_failures")
        and intake_checks.get("every_blocking_failure_is_mapped") is True
        and intake_checks.get("all_required_closure_groups_present") is True
        and intake_checks.get("strict_command_spine_covers_final_evidence_path") is True
        and (EXTERNAL / "evidence_intake_ledger.json").exists()
        and (EXTERNAL / "evidence_intake_ledger.md").exists()
        and (EXTERNAL / "evidence_intake_ledger.csv").exists(),
        (
            f"mapped={intake_ledger.get('mapped_failure_count')!r}/"
            f"{intake_ledger.get('blocking_failure_count')!r}, "
            f"groups={len(intake_ledger.get('closure_groups', []) or [])}"
        ),
    )

    baseline_ok, baseline, baseline_detail = passed_json(
        RESULTS / "external_baseline_contract_audit.json",
        version="external_baseline_contract_audit_v1",
    )
    add_check(checks, "baseline_contract_ready", baseline_ok, baseline_detail)
    add_check(
        checks,
        "baseline_contract_reports_missing_implementations",
        baseline.get("implementations_ready") is False and len(baseline.get("missing_implementations", [])) >= 11,
        f"implementations_ready={baseline.get('implementations_ready')!r}, missing={len(baseline.get('missing_implementations', []))}",
    )

    scaffold_ok, scaffold, scaffold_detail = passed_json(
        RESULTS / "external_adapter_scaffold_audit.json",
        version="external_adapter_scaffold_audit_v1",
    )
    add_check(checks, "adapter_scaffolds_ready", scaffold_ok, scaffold_detail)
    reference_adapter_ok, reference_adapter, reference_adapter_detail = passed_json(
        RESULTS / "external_reference_adapter_audit.json",
        version="external_reference_adapter_audit_v1",
    )
    add_check(checks, "reference_adapters_ready", reference_adapter_ok, reference_adapter_detail)
    add_check(
        checks,
        "reference_adapters_implementation_only",
        reference_adapter.get("implementation_only_not_rollout_evidence") is True
        and reference_adapter.get("not_external_evidence") is True,
        (
            f"implementation_only_not_rollout_evidence={reference_adapter.get('implementation_only_not_rollout_evidence')!r}, "
            f"not_external_evidence={reference_adapter.get('not_external_evidence')!r}"
        ),
    )
    add_check(
        checks,
        "reference_adapters_cover_non_oracle_methods",
        int(reference_adapter.get("non_oracle_adapter_count", 0) or 0) >= 11,
        f"non_oracle_adapter_count={reference_adapter.get('non_oracle_adapter_count')!r}",
    )
    adapter_contract_ok, adapter_contract, adapter_contract_detail = passed_json(
        RESULTS / "external_adapter_contract_audit.json",
        version="external_adapter_contract_audit_v1",
    )
    add_check(checks, "adapter_contract_harness_ready", adapter_contract_ok, adapter_contract_detail)
    add_check(
        checks,
        "adapter_contract_not_evidence",
        adapter_contract.get("not_external_evidence") is True,
        f"not_external_evidence={adapter_contract.get('not_external_evidence')!r}",
    )

    manifest_report_path = RESULTS / "external_manifest_builder_report.json"
    manifest_report = read_json(manifest_report_path) if manifest_report_path.exists() else {}
    add_check(
        checks,
        "manifest_builder_report_exists",
        manifest_report_path.exists(),
        rel(manifest_report_path),
    )
    add_check(
        checks,
        "manifest_builder_fail_closed",
        manifest_report.get("manifest_written") is False
        and manifest_report.get("records_loaded") == 0
        and manifest_report.get("assembly_checklist_csv") == "external_validation/manifest_assembly_checklist.csv"
        and int(manifest_report.get("assembly_checklist_row_count", 0) or 0) >= 30
        and int(manifest_report.get("assembly_blocking_count", 0) or 0) >= 20
        and (EXTERNAL / "manifest_assembly_checklist.csv").exists(),
        (
            f"manifest_written={manifest_report.get('manifest_written')!r}, "
            f"records_loaded={manifest_report.get('records_loaded')!r}, "
            f"assembly_rows={manifest_report.get('assembly_checklist_row_count')!r}, "
            f"assembly_blocking={manifest_report.get('assembly_blocking_count')!r}"
        ),
    )

    precollection_ok, precollection_manifest, precollection_detail = passed_json(
        RESULTS / "external_precollection_manifest_draft_audit.json",
        version="external_precollection_manifest_draft_audit_v1",
    )
    add_check(checks, "external_precollection_manifest_draft_ready", precollection_ok, precollection_detail)
    precollection_checks = {
        check.get("name"): check.get("passed")
        for check in precollection_manifest.get("checks", []) or []
    }
    add_check(
        checks,
        "external_precollection_manifest_draft_not_evidence",
        precollection_manifest.get("not_external_evidence") is True
        and precollection_manifest.get("draft_ready") is True
        and precollection_manifest.get("strict_external_evidence_ready") is False
        and precollection_manifest.get("strict_config_evidence_ready") is False
        and precollection_manifest.get("official_manifest_exists") is False
        and precollection_checks.get("draft_marked_non_evidence_and_fail_closed") is True,
        (
            f"draft_ready={precollection_manifest.get('draft_ready')!r}, "
            f"strict_external_evidence_ready={precollection_manifest.get('strict_external_evidence_ready')!r}, "
            f"official_manifest_exists={precollection_manifest.get('official_manifest_exists')!r}"
        ),
    )
    add_check(
        checks,
        "external_precollection_manifest_draft_config_hashes",
        int(precollection_manifest.get("prepared_config_count", 0) or 0) >= 4
        and precollection_checks.get("prepared_config_hashes_prefilled") is True,
        f"prepared_config_count={precollection_manifest.get('prepared_config_count')!r}",
    )
    add_check(
        checks,
        "external_precollection_manifest_draft_fail_closed",
        int(precollection_manifest.get("method_gap_count", 0) or 0) >= 11
        and int(precollection_manifest.get("missing_rollout_artifact_count", 0) or 0) >= 8
        and precollection_checks.get("method_gaps_remain_blocking") is True
        and precollection_checks.get("rollout_artifacts_remain_blocking") is True
        and precollection_checks.get("official_manifest_absent") is True,
        (
            f"method_gaps={precollection_manifest.get('method_gap_count')!r}, "
            f"rollout_gaps={precollection_manifest.get('missing_rollout_artifact_count')!r}"
        ),
    )

    freeze_ok, precollection_freeze, freeze_detail = passed_json(
        RESULTS / "external_precollection_freeze_receipt_audit.json",
        version="external_precollection_freeze_receipt_audit_v1",
    )
    add_check(checks, "external_precollection_freeze_receipt_ready", freeze_ok, freeze_detail)
    freeze_checks = {
        check.get("name"): check.get("passed")
        for check in precollection_freeze.get("checks", []) or []
    }
    add_check(
        checks,
        "external_precollection_freeze_receipt_not_evidence",
        precollection_freeze.get("not_external_evidence") is True
        and precollection_freeze.get("strict_external_evidence_ready") is False
        and precollection_freeze.get("freeze_receipt_ready") is False
        and freeze_checks.get("receipt_is_non_evidence_and_fail_closed") is True,
        (
            f"freeze_receipt_ready={precollection_freeze.get('freeze_receipt_ready')!r}, "
            f"strict_external_evidence_ready={precollection_freeze.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_precollection_freeze_receipt_hash_lock",
        int(precollection_freeze.get("locked_artifact_count", 0) or 0) >= 42
        and int(precollection_freeze.get("candidate_method_config_count", 0) or 0) >= 11
        and precollection_freeze.get("method_config_hash_lock_ready") is True
        and freeze_checks.get("core_lock_artifacts_hashed") is True
        and freeze_checks.get("prepared_task_configs_hashed") is True
        and freeze_checks.get("method_config_materialization_artifacts_hashed") is True
        and freeze_checks.get("candidate_method_configs_hashed") is True
        and freeze_checks.get("candidate_method_config_hashes_match_plan") is True
        and freeze_checks.get("candidate_method_configs_remain_non_evidence") is True
        and freeze_checks.get("checkout_and_skill_hash_recorded") is True,
        (
            f"locked_artifact_count={precollection_freeze.get('locked_artifact_count')!r}, "
            f"candidate_method_config_count={precollection_freeze.get('candidate_method_config_count')!r}"
        ),
    )
    add_check(
        checks,
        "external_precollection_freeze_receipt_gate_order",
        freeze_checks.get("strict_sequence_places_receipt_before_collection") is True
        and "build_external_precollection_freeze_receipt.py" in "\n".join(precollection_freeze.get("strict_command_sequence", []) or []),
        f"commands={len(precollection_freeze.get('strict_command_sequence', []) or [])}",
    )

    seal_ok, postcollection_seal, seal_detail = passed_json(
        RESULTS / "external_postcollection_evidence_seal_audit.json",
        version="external_postcollection_evidence_seal_audit_v1",
    )
    add_check(checks, "external_postcollection_evidence_seal_ready", seal_ok, seal_detail)
    seal_checks = {
        check.get("name"): check.get("passed")
        for check in postcollection_seal.get("checks", []) or []
    }
    add_check(
        checks,
        "external_postcollection_evidence_seal_not_evidence",
        postcollection_seal.get("not_external_evidence") is True
        and postcollection_seal.get("strict_external_evidence_ready") is False
        and postcollection_seal.get("postcollection_seal_ready") is False
        and postcollection_seal.get("ready_for_manifest_promotion") is False
        and seal_checks.get("seal_is_non_evidence_and_fail_closed") is True,
        (
            f"postcollection_seal_ready={postcollection_seal.get('postcollection_seal_ready')!r}, "
            f"ready_for_manifest_promotion={postcollection_seal.get('ready_for_manifest_promotion')!r}, "
            f"strict_external_evidence_ready={postcollection_seal.get('strict_external_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "external_postcollection_evidence_seal_hash_inventory",
        int(postcollection_seal.get("sealed_artifact_count", 0) or 0) >= 8
        and int(postcollection_seal.get("jsonl_record_count", 0) or 0) == 0
        and int(postcollection_seal.get("rollout_video_count", 0) or 0) == 0
        and seal_checks.get("hash_inventory_written_for_precollection_inputs") is True
        and seal_checks.get("raw_logs_and_videos_absent_before_collection") is True,
        (
            f"sealed_artifacts={postcollection_seal.get('sealed_artifact_count')!r}, "
            f"records={postcollection_seal.get('jsonl_record_count')!r}, "
            f"videos={postcollection_seal.get('rollout_video_count')!r}"
        ),
    )
    add_check(
        checks,
        "external_postcollection_evidence_seal_gate_order",
        seal_checks.get("strict_sequence_places_seal_after_collection_before_manifest") is True
        and seal_checks.get("seal_references_rollout_pairing_release_final_gates") is True
        and "build_external_postcollection_evidence_seal.py" in "\n".join(postcollection_seal.get("strict_command_sequence", []) or []),
        f"commands={len(postcollection_seal.get('strict_command_sequence', []) or [])}",
    )

    consistency_ok, postcollection_consistency, consistency_detail = passed_json(
        RESULTS / "external_postcollection_seal_consistency_audit.json",
        version="external_postcollection_seal_consistency_audit_v1",
    )
    add_check(checks, "external_postcollection_seal_consistency_gate_ready", consistency_ok, consistency_detail)
    consistency_checks = {
        check.get("name"): check.get("passed")
        for check in postcollection_consistency.get("checks", []) or []
    }
    add_check(
        checks,
        "external_postcollection_seal_consistency_not_evidence",
        postcollection_consistency.get("not_external_evidence") is True
        and postcollection_consistency.get("strict_external_evidence_ready") is False
        and postcollection_consistency.get("seal_consistency_ready") is False
        and postcollection_consistency.get("ready_for_manifest_promotion") is False
        and consistency_checks.get("consistency_gate_is_non_evidence_and_fail_closed") is True,
        (
            f"seal_consistency_ready={postcollection_consistency.get('seal_consistency_ready')!r}, "
            f"ready_for_manifest_promotion={postcollection_consistency.get('ready_for_manifest_promotion')!r}"
        ),
    )
    add_check(
        checks,
        "external_postcollection_seal_consistency_hash_recompute",
        int(postcollection_consistency.get("matched_hash_count", 0) or 0) >= 8
        and not postcollection_consistency.get("mismatched_hashes")
        and not postcollection_consistency.get("extra_official_artifacts")
        and int(postcollection_consistency.get("current_jsonl_record_count", 0) or 0) == 0
        and int(postcollection_consistency.get("current_rollout_video_count", 0) or 0) == 0
        and consistency_checks.get("sealed_hashes_recompute_without_drift") is True
        and consistency_checks.get("no_unsealed_official_artifacts_before_manifest_promotion") is True,
        (
            f"matched={postcollection_consistency.get('matched_hash_count')!r}, "
            f"records={postcollection_consistency.get('current_jsonl_record_count')!r}, "
            f"videos={postcollection_consistency.get('current_rollout_video_count')!r}"
        ),
    )
    add_check(
        checks,
        "external_postcollection_seal_consistency_gate_order",
        consistency_checks.get("strict_sequence_places_consistency_after_seal_before_manifest") is True
        and consistency_checks.get("consistency_gate_references_rollout_pairing_release_final_gates") is True
        and "audit_external_postcollection_seal_consistency.py" in "\n".join(postcollection_consistency.get("strict_command_sequence", []) or []),
        f"commands={len(postcollection_consistency.get('strict_command_sequence', []) or [])}",
    )

    preflight_path = RESULTS / "external_evidence_preflight.json"
    preflight_ok, preflight, preflight_detail = passed_json(
        preflight_path,
        version="external_evidence_preflight_v1",
    )
    add_check(checks, "external_evidence_preflight_ready", preflight_ok, preflight_detail)
    add_check(
        checks,
        "external_evidence_preflight_not_evidence",
        preflight.get("not_external_evidence") is True,
        f"not_external_evidence={preflight.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "external_evidence_preflight_fail_closed",
        preflight.get("evidence_ready") is False
        and preflight.get("readiness_state") == "COLLECT_EXTERNAL_EVIDENCE"
        and int(preflight.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"evidence_ready={preflight.get('evidence_ready')!r}, "
            f"readiness_state={preflight.get('readiness_state')!r}, "
            f"blocking_missing_count={preflight.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "external_evidence_preflight_record_budget",
        int(preflight.get("expected_records", 0) or 0) >= 1440
        and int(preflight.get("observed_records", -1) or 0) == 0,
        f"expected={preflight.get('expected_records')!r}, observed={preflight.get('observed_records')!r}",
    )
    add_check(
        checks,
        "external_evidence_preflight_operator_actions",
        len(preflight.get("operator_next_actions", []) or []) >= 5,
        f"operator_next_actions={len(preflight.get('operator_next_actions', []) or [])}",
    )

    acquisition_ok, acquisition, acquisition_detail = passed_json(
        RESULTS / "external_acquisition_packet.json",
        version="external_acquisition_packet_v1",
    )
    add_check(checks, "external_acquisition_packet_ready", acquisition_ok, acquisition_detail)
    add_check(
        checks,
        "external_acquisition_packet_not_evidence",
        acquisition.get("not_external_evidence") is True
        and acquisition.get("strict_evidence_ready") is False
        and acquisition.get("acquisition_packet_ready") is True,
        (
            f"not_external_evidence={acquisition.get('not_external_evidence')!r}, "
            f"strict_evidence_ready={acquisition.get('strict_evidence_ready')!r}, "
            f"acquisition_packet_ready={acquisition.get('acquisition_packet_ready')!r}"
        ),
    )
    acquisition_missing = acquisition.get("missing_requirements", []) or []
    acquisition_actions = acquisition.get("operator_actions", []) or []
    add_check(
        checks,
        "external_acquisition_packet_maps_all_blockers",
        len(acquisition_missing) == 4 and len(acquisition_actions) >= 10,
        f"missing_requirements={len(acquisition_missing)}, operator_actions={len(acquisition_actions)}",
    )
    acquisition_check_map = {check.get("name"): check.get("passed") for check in acquisition.get("checks", []) or []}
    add_check(
        checks,
        "external_acquisition_packet_backend_gate",
        acquisition_check_map.get("backend_contract_gate_ready") is True
        and acquisition_check_map.get("backend_action_runs_contract_before_readiness") is True,
        f"checks={acquisition_check_map}",
    )
    operator_packet_ok, operator_packet, operator_packet_detail = passed_json(
        RESULTS / "external_operator_packet.json",
        version="external_operator_packet_v1",
    )
    add_check(checks, "external_operator_packet_ready", operator_packet_ok, operator_packet_detail)
    add_check(
        checks,
        "external_operator_packet_not_evidence",
        operator_packet.get("not_external_evidence") is True
        and operator_packet.get("strict_evidence_ready") is False
        and operator_packet.get("operator_packet_ready") is True,
        (
            f"not_external_evidence={operator_packet.get('not_external_evidence')!r}, "
            f"strict_evidence_ready={operator_packet.get('strict_evidence_ready')!r}, "
            f"operator_packet_ready={operator_packet.get('operator_packet_ready')!r}"
        ),
    )
    operator_check_map = {check.get("name"): check.get("passed") for check in operator_packet.get("checks", []) or []}
    add_check(
        checks,
        "external_operator_packet_backend_gate",
        "audit_external_backend_contract.py --strict" in str(operator_packet.get("backend_contract_gate_command", ""))
        and operator_check_map.get("backend_contract_gate_is_explicit") is True
        and operator_check_map.get("backend_action_runs_contract_before_readiness") is True,
        f"backend_contract_gate_command={operator_packet.get('backend_contract_gate_command')!r}",
    )
    add_check(
        checks,
        "external_operator_packet_go_no_go",
        operator_packet.get("go_to_collect") is False
        and operator_packet.get("start_state") == "DO_NOT_COLLECT_YET"
        and int(operator_packet.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"go_to_collect={operator_packet.get('go_to_collect')!r}, "
            f"start_state={operator_packet.get('start_state')!r}, "
            f"blocking_missing_count={operator_packet.get('blocking_missing_count')!r}"
        ),
    )
    handoff_bundle_ok, handoff_bundle, handoff_bundle_detail = passed_json(
        RESULTS / "external_operator_handoff_bundle.json",
        version="external_operator_handoff_bundle_v1",
    )
    add_check(checks, "external_operator_handoff_bundle_ready", handoff_bundle_ok, handoff_bundle_detail)
    add_check(
        checks,
        "external_operator_handoff_bundle_not_evidence",
        handoff_bundle.get("not_external_evidence") is True
        and handoff_bundle.get("strict_evidence_ready") is False
        and handoff_bundle.get("handoff_bundle_ready") is True
        and handoff_bundle.get("start_state") == "DO_NOT_COLLECT_YET",
        (
            f"not_external_evidence={handoff_bundle.get('not_external_evidence')!r}, "
            f"strict_evidence_ready={handoff_bundle.get('strict_evidence_ready')!r}, "
            f"handoff_bundle_ready={handoff_bundle.get('handoff_bundle_ready')!r}, "
            f"start_state={handoff_bundle.get('start_state')!r}"
        ),
    )
    handoff_check_map = {check.get("name"): check.get("passed") for check in handoff_bundle.get("checks", []) or []}
    add_check(
        checks,
        "external_operator_handoff_bundle_excludes_evidence_paths",
        not handoff_bundle.get("forbidden_included_paths")
        and handoff_check_map.get("bundle_excludes_rollout_evidence_artifacts") is True
        and handoff_check_map.get("no_real_manifest_written") is True,
        f"forbidden_included_paths={handoff_bundle.get('forbidden_included_paths')!r}",
    )
    add_check(
        checks,
        "external_operator_handoff_bundle_hash_manifest",
        int(handoff_bundle.get("included_file_count", 0) or 0) >= 120
        and handoff_check_map.get("file_hashes_are_recorded") is True
        and handoff_check_map.get("handoff_has_task_config_and_baseline_assets") is True,
        (
            f"included_file_count={handoff_bundle.get('included_file_count')!r}, "
            f"category_counts={handoff_bundle.get('category_counts')!r}"
        ),
    )

    external_audit = read_json(RESULTS / "external_evidence_audit.json") if (RESULTS / "external_evidence_audit.json").exists() else {}
    rollout_metrics = read_json(RESULTS / "external_rollout_metrics.json") if (RESULTS / "external_rollout_metrics.json").exists() else {}
    config_evidence = read_json(RESULTS / "external_config_evidence_audit.json") if (RESULTS / "external_config_evidence_audit.json").exists() else {}
    adapter_evidence = read_json(RESULTS / "external_adapter_contract_evidence_audit.json") if (RESULTS / "external_adapter_contract_evidence_audit.json").exists() else {}
    strict_not_ready = (
        external_audit.get("submission_ready") is False
        and rollout_metrics.get("passed") is False
        and config_evidence.get("passed") is False
        and adapter_evidence.get("passed") is False
    )
    add_check(
        checks,
        "strict_evidence_gates_remain_not_ready",
        strict_not_ready,
        (
            f"external_submission_ready={external_audit.get('submission_ready')!r}, "
            f"rollout_passed={rollout_metrics.get('passed')!r}, "
            f"config_passed={config_evidence.get('passed')!r}, "
            f"adapter_passed={adapter_evidence.get('passed')!r}"
        ),
    )

    required_packet_paths = [
        EXTERNAL / "collection_runbook.md",
        EXTERNAL / "operator_record_sheet.csv",
        EXTERNAL / "manifest_template.json",
        EXTERNAL / "manifest_assembly_checklist.csv",
        EXTERNAL / "manifest_precollection_draft.json",
        EXTERNAL / "manifest_precollection_draft.md",
        EXTERNAL / "precollection_freeze_receipt.json",
        EXTERNAL / "precollection_freeze_receipt.md",
        EXTERNAL / "precollection_freeze_receipt.csv",
        EXTERNAL / "postcollection_evidence_seal.json",
        EXTERNAL / "postcollection_evidence_seal.md",
        EXTERNAL / "postcollection_evidence_seal.csv",
        RESULTS / "external_postcollection_seal_consistency_audit.md",
        EXTERNAL / "log_schema_v1.json",
        EXTERNAL / "statistical_analysis_plan.json",
        EXTERNAL / "statistical_analysis_plan.md",
        EXTERNAL / "platform_onboarding_packet.json",
        EXTERNAL / "platform_onboarding_packet.md",
        EXTERNAL / "fidelity_provenance_packet.json",
        EXTERNAL / "fidelity_provenance_packet.md",
        EXTERNAL / "fidelity_provenance_work_orders.csv",
        EXTERNAL / "backend_integration_packet.json",
        EXTERNAL / "backend_integration_packet.md",
        EXTERNAL / "backend_integration_work_orders.csv",
        EXTERNAL / "config_manifest_packet.json",
        EXTERNAL / "config_manifest_packet.md",
        EXTERNAL / "config_manifest_work_orders.csv",
        EXTERNAL / "rollout_evidence_packet.json",
        EXTERNAL / "rollout_evidence_packet.md",
        EXTERNAL / "rollout_evidence_work_orders.csv",
        EXTERNAL / "ablation_collection_packet.json",
        EXTERNAL / "ablation_collection_packet.md",
        EXTERNAL / "ablation_collection_work_orders.csv",
        EXTERNAL / "method_implementation_packet.json",
        EXTERNAL / "method_implementation_packet.md",
        EXTERNAL / "method_implementation_work_orders.csv",
        EXTERNAL / "method_reference_provenance.csv",
        EXTERNAL / "method_manifest_cutover_checklist.csv",
        EXTERNAL / "method_manifest_cutover_checklist.md",
        EXTERNAL / "adapter_acceptance_fixtures.json",
        EXTERNAL / "adapter_acceptance_fixtures.md",
        EXTERNAL / "adapter_acceptance_fixtures.csv",
        EXTERNAL / "platform_qualification_checklist.md",
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
        EXTERNAL / "runner" / "README.md",
        EXTERNAL / "runner" / "backend_contract.py",
        EXTERNAL / "runner" / "real_collection_runner.py",
        RESULTS / "external_runner_backend_self_test.md",
        RESULTS / "external_backend_contract_audit.md",
        RESULTS / "external_collection_readiness_audit.md",
        RESULTS / "external_operator_packet.md",
        RESULTS / "external_operator_handoff_bundle.md",
        RESULTS / "external_analysis_plan_audit.md",
        RESULTS / "external_platform_onboarding_audit.md",
        RESULTS / "external_fidelity_provenance_audit.md",
        RESULTS / "external_backend_integration_audit.md",
        RESULTS / "external_config_manifest_audit.md",
        RESULTS / "external_rollout_evidence_audit.md",
        RESULTS / "external_ablation_collection_audit.md",
        RESULTS / "external_evidence_intake_ledger_audit.md",
        RESULTS / "external_precollection_manifest_draft_audit.md",
        RESULTS / "external_precollection_freeze_receipt_audit.md",
        RESULTS / "external_postcollection_evidence_seal_audit.md",
        EXTERNAL / "evidence_intake_ledger.json",
        EXTERNAL / "evidence_intake_ledger.md",
        EXTERNAL / "evidence_intake_ledger.csv",
        RESULTS / "external_method_implementation_audit.md",
        RESULTS / "maniskill_pilot_runtime_liveness_audit.md",
        RESULTS / "maniskill_pilot_reset_timeout_triage.md",
        RESULTS / "maniskill_render_resource_sweep.md",
        EXTERNAL / "render_resource_sweep_work_orders.csv",
        RESULTS / "maniskill_render_failure_remediation.md",
        EXTERNAL / "render_failure_remediation_work_orders.csv",
        DOCS / "independent_validation_protocol.md",
    ]
    missing_packet_paths = [rel(path) for path in required_packet_paths if not path.exists()]
    add_check(checks, "operator_packet_paths_exist", not missing_packet_paths, f"missing={missing_packet_paths}")

    task_cards = sorted((EXTERNAL / "task_cards").glob("*.md"))
    config_templates = sorted((EXTERNAL / "config_templates").glob("*.json"))
    add_check(checks, "task_cards_ge_4", len(task_cards) >= 4, f"task_cards={len(task_cards)}")
    add_check(checks, "config_templates_ge_4", len(config_templates) >= 4, f"config_templates={len(config_templates)}")
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent as expected before real evidence",
    )

    protocol_text = (DOCS / "independent_validation_protocol.md").read_text(encoding="utf-8") if (DOCS / "independent_validation_protocol.md").exists() else ""
    qualification_text = (EXTERNAL / "platform_qualification_checklist.md").read_text(encoding="utf-8") if (EXTERNAL / "platform_qualification_checklist.md").exists() else ""
    add_check(
        checks,
        "validation_path_independent_of_haonan",
        "without relying on Haonan" in protocol_text and "Haonan" in protocol_text,
        "independent validation protocol explicitly separates base evidence from Haonan collaboration",
    )
    required_qualification_terms = [
        "deterministic paired reset",
        "contact and dynamics fidelity",
        "video export",
        "no privileged state",
        "shared skill library",
    ]
    missing_terms = [term for term in required_qualification_terms if term not in qualification_text]
    add_check(
        checks,
        "platform_qualification_terms_present",
        not missing_terms,
        f"missing_terms={missing_terms}",
    )

    execution_check_names = {
        "collection_plan_ready",
        "collection_scale_ge_1440_records",
        "collection_route_high_fidelity",
        "external_analysis_plan_ready",
        "external_analysis_plan_not_evidence",
        "external_analysis_plan_threshold_lock",
        "external_analysis_plan_exclusion_policy",
        "fidelity_acceptance_contract_ready",
        "fidelity_acceptance_not_evidence",
        "fidelity_acceptance_fail_closed",
        "fidelity_acceptance_task_coverage",
        "external_fidelity_provenance_packet_ready",
        "external_fidelity_provenance_not_evidence",
        "external_fidelity_provenance_covers_acceptance_blocker",
        "external_fidelity_provenance_gate_order",
        "fidelity_acceptance_materializer_ready",
        "fidelity_acceptance_materializer_not_evidence",
        "fidelity_acceptance_materializer_guarded",
        "fidelity_acceptance_materializer_self_test_ready",
        "fidelity_acceptance_materializer_self_test_guards",
        "independent_validation_route_ready",
        "independent_route_not_evidence",
        "independent_route_primary_covers_tasks",
        "independent_route_closes_blockers",
        "external_platform_onboarding_ready",
        "external_platform_onboarding_not_evidence",
        "external_platform_onboarding_sources_and_provenance",
        "external_platform_onboarding_gate_order",
        "external_method_implementation_packet_ready",
        "external_method_implementation_not_evidence",
        "external_method_implementation_covers_missing_methods",
        "external_method_implementation_gate_order",
        "blind_eval_plan_ready",
        "blind_eval_not_evidence",
        "blind_eval_row_budget",
        "blind_eval_no_method_leak",
        "operator_runbook_ready",
        "operator_sheet_covers_collection_plan",
        "external_runner_harness_ready",
        "external_runner_harness_not_evidence",
        "external_runner_harness_fail_closed",
        "external_runner_backend_probe_ready",
        "external_runner_backend_probe_not_evidence",
        "external_runner_backend_probe_exercises_actual_runner_path",
        "maniskill_pilot_runtime_liveness_ready",
        "maniskill_pilot_runtime_liveness_not_evidence",
        "maniskill_pilot_reset_timeout_triage_ready",
        "maniskill_render_resource_sweep_ready",
        "maniskill_render_resource_sweep_not_evidence",
        "maniskill_render_machine_qualification_ready",
        "maniskill_render_machine_qualification_not_evidence",
        "maniskill_render_machine_operator_commands",
        "maniskill_render_failure_remediation_ready",
        "maniskill_render_failure_remediation_not_evidence",
        "external_backend_contract_ready",
        "external_backend_contract_not_evidence",
        "external_backend_contract_fail_closed",
        "external_backend_integration_packet_ready",
        "external_backend_integration_not_evidence",
        "external_backend_integration_covers_backend_blocker",
        "external_backend_integration_gate_order",
        "external_collection_readiness_audit_ready",
        "external_collection_readiness_not_evidence",
        "external_collection_readiness_fail_closed",
        "external_collection_readiness_packet_shape",
        "maniskill_reference_collection_preflight_ready",
        "maniskill_reference_collection_preflight_reaches_fidelity_gate",
        "external_pairing_integrity_audit_ready",
        "external_pairing_integrity_not_evidence",
        "external_release_package_audit_ready",
        "external_release_package_not_evidence",
        "config_templates_ready",
        "config_schema_exists",
        "external_config_manifest_packet_ready",
        "external_config_manifest_not_evidence",
        "external_config_manifest_covers_manifest_config_blocker",
        "external_config_manifest_gate_order",
        "external_rollout_evidence_packet_ready",
        "external_rollout_evidence_not_evidence",
        "external_rollout_evidence_covers_raw_log_blocker",
        "external_rollout_evidence_gate_order",
        "external_ablation_collection_packet_ready",
        "external_ablation_collection_not_evidence",
        "external_ablation_collection_covers_strict_ablation_blocker",
        "external_evidence_intake_ledger_ready",
        "external_evidence_intake_ledger_not_evidence",
        "external_evidence_intake_ledger_maps_all_strict_failures",
        "baseline_contract_ready",
        "baseline_contract_reports_missing_implementations",
        "adapter_scaffolds_ready",
        "reference_adapters_ready",
        "reference_adapters_implementation_only",
        "reference_adapters_cover_non_oracle_methods",
        "adapter_contract_harness_ready",
        "adapter_contract_not_evidence",
        "manifest_builder_report_exists",
        "manifest_builder_fail_closed",
        "external_precollection_manifest_draft_ready",
        "external_precollection_manifest_draft_not_evidence",
        "external_precollection_manifest_draft_config_hashes",
        "external_precollection_manifest_draft_fail_closed",
        "external_precollection_freeze_receipt_ready",
        "external_precollection_freeze_receipt_not_evidence",
        "external_precollection_freeze_receipt_hash_lock",
        "external_precollection_freeze_receipt_gate_order",
        "external_postcollection_evidence_seal_ready",
        "external_postcollection_evidence_seal_not_evidence",
        "external_postcollection_evidence_seal_hash_inventory",
        "external_postcollection_evidence_seal_gate_order",
        "external_postcollection_seal_consistency_gate_ready",
        "external_postcollection_seal_consistency_not_evidence",
        "external_postcollection_seal_consistency_hash_recompute",
        "external_postcollection_seal_consistency_gate_order",
        "external_evidence_preflight_ready",
        "external_evidence_preflight_not_evidence",
        "external_evidence_preflight_fail_closed",
        "external_evidence_preflight_record_budget",
        "external_evidence_preflight_operator_actions",
        "external_acquisition_packet_ready",
        "external_acquisition_packet_not_evidence",
        "external_acquisition_packet_maps_all_blockers",
        "external_acquisition_packet_backend_gate",
        "external_operator_packet_ready",
        "external_operator_packet_not_evidence",
        "external_operator_packet_go_no_go",
        "external_operator_packet_backend_gate",
        "operator_packet_paths_exist",
        "task_cards_ge_4",
        "config_templates_ge_4",
        "no_real_manifest_written",
        "validation_path_independent_of_haonan",
        "platform_qualification_terms_present",
    }
    execution_packet_ready = all(
        check["passed"] for check in checks if check["name"] in execution_check_names
    )
    strict_evidence_ready = external_audit.get("submission_ready") is True
    passed = execution_packet_ready and not strict_evidence_ready and any(
        check["name"] == "strict_evidence_gates_remain_not_ready" and check["passed"] for check in checks
    )

    payload = {
        "version": "external_execution_readiness_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "execution_packet_ready": execution_packet_ready,
        "strict_evidence_ready": strict_evidence_ready,
        "operator_rows": operator_rows,
        "total_required_records": total_required_records,
        "missing_evidence_to_collect": [
            "external_validation/manifest.json",
            "manifest-declared JSONL rollout logs",
            "complete paired-reset method panels with no duplicates",
            "manifest-declared release artifact hashes with no local dry-run/template placeholders",
            "actual collection preflight cleared with backend, real configs, fidelity acceptance, alias unsealing, and specific run id",
            "manifest-declared task configs with hashes",
            "completed config manifest packet work orders with manifest-declared config hashes",
            "completed rollout evidence packet work orders with manifest-declared JSONL logs and videos",
            "manifest-declared external ablation logs and videos for basin_overlap, barrier_height, descent_continuity, risk_calibration, and seam_repair",
            "completed evidence intake ledger rows for all current strict external-evidence failures",
            "completed precollection freeze receipt with real backend, specific run id, independent operator identity, clean checkout, and unsealed alias map before collection",
            "completed postcollection evidence seal with raw JSONL/video hashes before manifest promotion",
            "completed postcollection seal consistency audit with matching raw evidence hashes before manifest promotion",
            "manifest-declared videos",
            "official manifest promotion from the precollection draft after real evidence is collected",
            "manifest-declared independent non-oracle adapter implementations",
            "completed method implementation packet work orders with source/config/checkpoint hashes",
            "non-template backend module for external_validation/runner/real_collection_runner.py",
            "completed backend integration packet work orders with module/provenance/config/log/video hashes",
            "accepted robot/simulator fidelity acceptance file",
            "completed fidelity provenance packet work orders with accepted platform/contact provenance",
            "preflight-cleared external evidence package",
            "bounded ManiSkill pilot runtime liveness on the selected runtime machine",
            "render-machine qualification with render-backed MP4s on the accepted collection machine",
            "released or hash-declared skill/checkpoint artifacts",
        ],
        "checks": checks,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Execution Readiness Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Execution packet ready: `{str(execution_packet_ready).lower()}`.",
        f"Strict evidence ready: `{str(strict_evidence_ready).lower()}`.",
        f"Operator rows: `{operator_rows}`.",
        f"Required JSONL records: `{total_required_records}`.",
        "",
        "This audit checks whether the package is ready for an independent external validation operator to execute. It deliberately does not count the plan, scaffolds, schemas, or self-tests as robot or high-fidelity simulation evidence.",
        "",
        "## Missing Evidence To Collect",
        "",
    ]
    for item in payload["missing_evidence_to_collect"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = "PASS" if passed else "FAIL"
    print(
        f"External execution readiness audit: {status}; "
        f"execution_packet_ready={execution_packet_ready}; strict_evidence_ready={strict_evidence_ready}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

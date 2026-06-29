from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "visible_contribution_audit.json"
OUT_MD = RESULTS / "visible_contribution_audit.md"
PAPER_PDF = ROOT / "paper" / "main.pdf"


def configured_path(env_name: str, default: str) -> Path:
    path = Path(os.environ.get(env_name, default))
    return path if path.is_absolute() else ROOT / path


CANONICAL_PDF = configured_path("PAPER119_CANONICAL_PDF", "C:/Users/wangz/Downloads/119.pdf")


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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
    collection_readiness = read_json(RESULTS / "external_collection_readiness_audit.json")
    operator = read_json(RESULTS / "external_operator_packet.json")
    handoff = read_json(RESULTS / "external_operator_handoff_bundle.json")
    collection_job = read_json(RESULTS / "external_collection_job_packet_audit.json")
    machine_bootstrap = read_json(RESULTS / "external_collection_machine_bootstrap_audit.json")
    operator_release = read_json(RESULTS / "external_operator_release_bundle_plan.json")
    analysis = read_json(RESULTS / "external_analysis_plan_audit.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    task_binding = read_json(RESULTS / "maniskill_task_binding_probe.json")
    env_smoke = read_json(RESULTS / "maniskill_env_smoke_probe.json")
    fidelity_metadata = read_json(RESULTS / "maniskill_fidelity_metadata_probe.json")
    onboarding = read_json(RESULTS / "external_platform_onboarding_audit.json")
    fidelity_provenance = read_json(RESULTS / "external_fidelity_provenance_audit.json")
    fidelity_draft = read_json(RESULTS / "external_fidelity_acceptance_draft_audit.json")
    fidelity_materialization = read_json(RESULTS / "fidelity_acceptance_materialization_plan.json")
    fidelity_materializer_self_test = read_json(RESULTS / "fidelity_acceptance_materializer_self_test.json")
    backend_integration = read_json(RESULTS / "external_backend_integration_audit.json")
    maniskill_backend = read_json(RESULTS / "maniskill_backend_readiness_audit.json")
    reference_preflight = read_json(RESULTS / "maniskill_reference_collection_preflight_audit.json")
    collection_preflight_self_test = read_json(RESULTS / "external_collection_preflight_self_test.json")
    runner_probe = read_json(RESULTS / "external_runner_backend_self_test.json")
    pilot_smoke = read_json(RESULTS / "external_pilot_smoke_packet_audit.json")
    pilot_runtime = read_json(RESULTS / "maniskill_pilot_runtime_liveness_audit.json")
    render_preflight = read_json(RESULTS / "maniskill_render_video_preflight_audit.json")
    render_resource_sweep = read_json(RESULTS / "maniskill_render_resource_sweep.json")
    render_remediation = read_json(RESULTS / "maniskill_render_failure_remediation.json")
    render_machine_self_test = read_json(RESULTS / "maniskill_render_machine_qualification_self_test.json")
    runbook = read_json(RESULTS / "external_runbook_audit.json")
    config_manifest = read_json(RESULTS / "external_config_manifest_audit.json")
    rollout_evidence = read_json(RESULTS / "external_rollout_evidence_audit.json")
    ablation_collection = read_json(RESULTS / "external_ablation_collection_audit.json")
    evidence_intake = read_json(RESULTS / "external_evidence_intake_ledger_audit.json")
    precollection_manifest = read_json(RESULTS / "external_precollection_manifest_draft_audit.json")
    precollection_freeze = read_json(RESULTS / "external_precollection_freeze_receipt_audit.json")
    precollection_freeze_self_test = read_json(RESULTS / "external_precollection_freeze_receipt_self_test.json")
    postcollection_seal = read_json(RESULTS / "external_postcollection_evidence_seal_audit.json")
    postcollection_seal_self_test = read_json(RESULTS / "external_postcollection_evidence_seal_self_test.json")
    postcollection_consistency = read_json(RESULTS / "external_postcollection_seal_consistency_audit.json")
    postcollection_consistency_self_test = read_json(RESULTS / "external_postcollection_seal_consistency_self_test.json")
    method_implementation = read_json(RESULTS / "external_method_implementation_audit.json")
    method_config_materialization = read_json(RESULTS / "external_method_config_materialization_audit.json")
    adapter_scaffold_guard_self_test = read_json(RESULTS / "external_adapter_scaffold_guard_self_test.json")
    adapter_evidence_self_test = read_json(RESULTS / "external_adapter_evidence_self_test.json")
    materialization = read_json(RESULTS / "external_config_materialization_plan.json")
    planner_policy = read_json(RESULTS / "planner_edge_policy_audit.json")
    failure_memory = read_json(RESULTS / "failure_memory_adaptation_audit.json")
    local_model_release = read_json(RESULTS / "local_model_release_audit.json")
    release_package = read_json(RESULTS / "external_release_package_audit.json")
    release_package_self_test = read_json(RESULTS / "external_release_package_self_test.json")
    rollout_validator_self_test = read_json(RESULTS / "external_rollout_validator_self_test.json")
    evidence_pipeline_self_test = read_json(RESULTS / "external_evidence_pipeline_self_test.json")
    reviewer_packet = read_json(RESULTS / "reviewer_response_packet_audit.json")
    ledger = read_json(DOCS / "claim_evidence_ledger.json")
    rollout_validator_text = read_text(ROOT / "scripts" / "validate_external_rollouts.py")
    rollout_self_test_text = read_text(ROOT / "scripts" / "self_test_external_rollout_validator.py")
    evidence_pipeline_self_test_text = read_text(ROOT / "scripts" / "self_test_external_evidence_pipeline.py")
    audit_external_evidence_text = read_text(ROOT / "scripts" / "audit_external_evidence.py")
    config_validator_text = read_text(ROOT / "scripts" / "validate_external_configs.py")
    config_self_test_text = read_text(ROOT / "scripts" / "self_test_external_config_evidence.py")
    config_evidence_self_test = read_json(RESULTS / "external_config_evidence_self_test.json")
    release_audit_text = read_text(ROOT / "scripts" / "audit_external_release_package.py")
    release_self_test_text = read_text(ROOT / "scripts" / "self_test_external_release_package.py")
    runner_text = read_text(ROOT / "external_validation" / "runner" / "real_collection_runner.py")

    files = {
        "README": ROOT / "README.md",
        "final_audit": DOCS / "final_audit.md",
        "readiness_decision": DOCS / "submission_readiness_decision.md",
        "readiness_audit": DOCS / "submission_readiness_audit_v5.md",
        "version_log": DOCS / "submission_version_log.md",
        "child_status": ROOT / "child_status.md",
        "reproducibility": DOCS / "reproducibility_checklist.md",
        "outreach": DOCS / "haonan_yilun_outreach_package.md",
        "reviewer": DOCS / "reviewer_response_packet.md",
    }
    texts = {name: read_text(path) for name, path in files.items()}
    canonical_pdf_exists = CANONICAL_PDF.exists()
    canonical_pdf_sha = sha256(CANONICAL_PDF) if canonical_pdf_exists else ""
    canonical_pdf_size = CANONICAL_PDF.stat().st_size if canonical_pdf_exists else 0
    paper_pdf_sha = sha256(PAPER_PDF) if PAPER_PDF.exists() else ""

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "canonical_pdf_metadata_available",
        canonical_pdf_exists and len(canonical_pdf_sha) == 64 and canonical_pdf_size > 100_000,
        f"path={CANONICAL_PDF}, sha={canonical_pdf_sha or '<missing>'}, size={canonical_pdf_size}",
    )
    add_check(
        checks,
        "paper_pdf_matches_canonical",
        PAPER_PDF.exists() and canonical_pdf_exists and paper_pdf_sha == canonical_pdf_sha,
        f"paper_sha={paper_pdf_sha or '<missing>'}, canonical_sha={canonical_pdf_sha or '<missing>'}",
    )
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
    collection_reference_route = collection_readiness.get("tracked_reference_route", {}) or {}
    collection_reference_blockers = collection_reference_route.get("blocking_missing", []) or []
    collection_reference_checks = {check.get("name"): check.get("passed") for check in collection_reference_route.get("checks", []) or []}
    add_check(
        checks,
        "collection_readiness_tracked_reference_route_visible",
        collection_readiness.get("passed") is True
        and collection_readiness.get("not_external_evidence") is True
        and collection_readiness.get("collection_ready") is False
        and collection_reference_route.get("not_external_evidence") is True
        and "maniskill_reference_backend.py" in str(collection_reference_route.get("backend_module", ""))
        and collection_reference_route.get("run_id") == "maniskill_sapien_reference_preflight_protocol_v1"
        and collection_reference_route.get("collection_ready") is False
        and collection_reference_route.get("strict_external_evidence_ready") is False
        and int(collection_reference_route.get("blocking_missing_count", 99) or 99) == 1
        and len(collection_reference_blockers) == 1
        and "fidelity_acceptance_ready" in collection_reference_blockers[0]
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
    collection_job_checks = {check.get("name"): check.get("passed") for check in collection_job.get("checks", []) or []}
    add_check(
        checks,
        "external_collection_job_packet_visible",
        collection_job.get("passed") is True
        and collection_job.get("not_external_evidence") is True
        and collection_job.get("strict_external_evidence_ready") is False
        and collection_job.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and int(collection_job.get("remaining_submission_blocker_count", 0) or 0) == 4
        and len(collection_job.get("job_steps", []) or []) >= 17
        and collection_job_checks.get("command_sequence_covers_full_external_validation_route") is True
        and collection_job_checks.get("official_collection_commands_guarded") is True
        and (ROOT / "scripts" / "build_external_collection_job_packet.py").exists()
        and (ROOT / "external_validation" / "collection_job_packet.md").exists()
        and (ROOT / "external_validation" / "collection_job_commands.ps1").exists()
        and (ROOT / "external_validation" / "collection_job_checklist.csv").exists()
        and (RESULTS / "external_collection_job_packet_audit.md").exists()
        and "External collection job packet" in texts["README"]
        and "External collection job packet" in texts["final_audit"]
        and "External collection job packet" in texts["reproducibility"]
        and "External collection job packet" in texts["outreach"],
        (
            f"job_state={collection_job.get('job_state')!r}, "
            f"steps={len(collection_job.get('job_steps', []) or [])}, "
            f"blockers={collection_job.get('remaining_submission_blocker_count')!r}"
        ),
    )
    machine_bootstrap_checks = {check.get("name"): check.get("passed") for check in machine_bootstrap.get("checks", []) or []}
    add_check(
        checks,
        "external_collection_machine_bootstrap_visible",
        machine_bootstrap.get("passed") is True
        and machine_bootstrap.get("not_external_evidence") is True
        and machine_bootstrap.get("strict_external_evidence_ready") is False
        and machine_bootstrap.get("bootstrap_state") == "READY_TO_BOOTSTRAP_EXTERNAL_MACHINE"
        and machine_bootstrap_checks.get("bootstrap_script_is_probe_only") is True
        and machine_bootstrap_checks.get("local_machine_not_promoted") is True
        and machine_bootstrap_checks.get("no_real_outputs_written") is True
        and (ROOT / "scripts" / "build_external_collection_machine_bootstrap.py").exists()
        and (ROOT / "external_validation" / "collection_machine_bootstrap.md").exists()
        and (ROOT / "external_validation" / "collection_machine_bootstrap.ps1").exists()
        and (RESULTS / "external_collection_machine_bootstrap_audit.md").exists()
        and "External collection machine bootstrap" in texts["README"]
        and "External collection machine bootstrap" in texts["final_audit"]
        and "External collection machine bootstrap" in texts["reproducibility"]
        and "External collection machine bootstrap" in texts["outreach"],
        (
            f"bootstrap_state={machine_bootstrap.get('bootstrap_state')!r}, "
            f"command={machine_bootstrap.get('command_file')!r}"
        ),
    )
    operator_release_checks = {check.get("name"): check.get("passed") for check in operator_release.get("checks", []) or []}
    add_check(
        checks,
        "external_operator_release_bundle_visible",
        operator_release.get("passed") is True
        and operator_release.get("not_external_evidence") is True
        and operator_release.get("strict_external_evidence_ready") is False
        and operator_release.get("bundle_state") == "READY_TO_SEND_OPERATOR_PACKAGE"
        and operator_release.get("archive_written") is False
        and int(operator_release.get("included_file_count", 0) or 0) >= 300
        and operator_release_checks.get("handoff_hashes_recomputed") is True
        and operator_release_checks.get("forbidden_evidence_paths_excluded") is True
        and (ROOT / "scripts" / "build_external_operator_release_bundle.py").exists()
        and (ROOT / "external_validation" / "operator_release_bundle_manifest.csv").exists()
        and (ROOT / "external_validation" / "operator_release_bundle_README.md").exists()
        and (RESULTS / "external_operator_release_bundle_plan.md").exists()
        and "External operator release bundle" in texts["README"]
        and "External operator release bundle" in texts["final_audit"]
        and "External operator release bundle" in texts["reproducibility"]
        and "External operator release bundle" in texts["outreach"],
        (
            f"bundle_state={operator_release.get('bundle_state')!r}, "
            f"files={operator_release.get('included_file_count')!r}, "
            f"archive_written={operator_release.get('archive_written')!r}"
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
    materializer_checkout = fidelity_materialization.get("current_checkout", {}) or {}
    add_check(
        checks,
        "fidelity_acceptance_materializer_visible",
        fidelity_materialization.get("version") == "fidelity_acceptance_materialization_plan_v1"
        and fidelity_materialization.get("passed") is True
        and fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False
        and fidelity_materialization_checks.get("operator_write_command_is_guarded") is True
        and fidelity_materialization_checks.get("current_checkout_hashes_recorded") is True
        and fidelity_materialization_checks.get("write_requires_clean_checkout") is True
        and fidelity_materialization_checks.get("write_requires_current_code_commit_and_skill_hash") is True
        and len(str(materializer_checkout.get("code_commit", ""))) == 40
        and len(str(materializer_checkout.get("skill_library_hash", ""))) == 64,
        (
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}, "
            f"commit={materializer_checkout.get('code_commit')!r}, "
            f"skill_hash={materializer_checkout.get('skill_library_hash')!r}, "
            f"clean={materializer_checkout.get('clean_checkout')!r}, "
            f"dirty_count={len(materializer_checkout.get('dirty_status_lines', []) or [])}"
        ),
    )
    fidelity_materializer_self_checks = {check.get("name"): check.get("passed") for check in fidelity_materializer_self_test.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_self_test_visible",
        fidelity_materializer_self_test.get("version") == "fidelity_acceptance_materializer_self_test_v1"
        and fidelity_materializer_self_test.get("passed") is True
        and fidelity_materializer_self_test.get("not_external_evidence") is True
        and fidelity_materializer_self_checks.get("matching_clean_checkout_writes_temp_acceptance") is True
        and fidelity_materializer_self_checks.get("stale_commit_rejected_without_temp_write") is True
        and fidelity_materializer_self_checks.get("mismatched_skill_hash_rejected_without_temp_write") is True
        and fidelity_materializer_self_checks.get("dirty_checkout_rejected_without_temp_write") is True
        and fidelity_materializer_self_checks.get("pycache_excluded_from_skill_library_hash") is True
        and fidelity_materializer_self_checks.get("real_acceptance_file_not_touched") is True
        and (ROOT / "scripts" / "self_test_fidelity_acceptance_materializer.py").exists()
        and (RESULTS / "fidelity_acceptance_materializer_self_test.md").exists(),
        f"checks={fidelity_materializer_self_checks}",
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
    collection_preflight_self_checks = {
        check.get("name"): check.get("passed") for check in collection_preflight_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "external_collection_preflight_self_test_visible",
        collection_preflight_self_test.get("version") == "external_collection_preflight_self_test_v1"
        and collection_preflight_self_test.get("passed") is True
        and collection_preflight_self_test.get("not_external_evidence") is True
        and collection_preflight_self_test.get("synthetic_collection_ready") is True
        and collection_preflight_self_test.get("reference_route_collection_ready") is True
        and collection_preflight_self_test.get("reference_route_run_id") == "maniskill_sapien_reference_preflight_protocol_v1"
        and not collection_preflight_self_test.get("reference_route_blocking_missing")
        and collection_preflight_self_checks.get("reference_route_collection_ready_after_synthetic_fidelity_acceptance") is True
        and collection_preflight_self_checks.get("reference_route_core_checks_pass_after_synthetic_fidelity_acceptance") is True
        and (ROOT / "scripts" / "self_test_external_collection_preflight.py").exists()
        and (RESULTS / "external_collection_preflight_self_test.md").exists()
        and "External collection preflight self-test" in texts["README"]
        and "External collection preflight self-test" in texts["final_audit"]
        and "External collection preflight self-test" in texts["readiness_audit"],
        (
            f"synthetic_ready={collection_preflight_self_test.get('synthetic_collection_ready')!r}, "
            f"reference_ready={collection_preflight_self_test.get('reference_route_collection_ready')!r}, "
            f"blockers={collection_preflight_self_test.get('reference_route_blocking_missing')!r}"
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
        and runner_probe_checks.get("diagnostic_fallback_video_rejected_before_jsonl_write") is True
        and runner_probe_checks.get("schema_invalid_record_rejected_before_jsonl_write") is True
        and runner_probe_checks.get("partial_batch_failure_preserves_official_jsonl") is True
        and runner_probe_checks.get("partial_batch_failure_preserves_official_videos") is True
        and runner_probe_checks.get("real_manifest_untouched") is True,
        (
            f"records_written={runner_probe.get('records_written')!r}, "
            f"schema_errors={runner_probe.get('schema_errors')!r}"
        ),
    )
    add_check(
        checks,
        "official_video_write_guard_visible",
        "validate_official_video" in runner_text
        and "MIN_OFFICIAL_VIDEO_BYTES" in runner_text
        and "diagnostic fallback video sidecar" in runner_text
        and "ftyp" in runner_text
        and runner_probe_checks.get("diagnostic_fallback_video_rejected_before_jsonl_write") is True,
        "runner refuses diagnostic/non-MP4/undersized/out-of-dir videos before official JSONL writes",
    )
    add_check(
        checks,
        "official_jsonl_write_guard_visible",
        "validate_official_record" in runner_text
        and "validate_external_rollouts" in runner_text
        and "schema-invalid official JSONL record" in runner_text
        and runner_probe_checks.get("schema_invalid_record_rejected_before_jsonl_write") is True,
        "runner refuses schema-invalid rollout records before official JSONL writes",
    )
    add_check(
        checks,
        "atomic_official_jsonl_promotion_visible",
        "promote_pending_logs" in runner_text
        and "stage_log_path" in runner_text
        and "backup_log_path" in runner_text
        and "stage_video_path" in runner_text
        and "backup_video_path" in runner_text
        and "promote_pending_artifacts" in runner_text
        and "pending_log_lines" in runner_text
        and "pending_videos" in runner_text
        and runner_probe_checks.get("partial_batch_failure_preserves_official_jsonl") is True
        and runner_probe_checks.get("partial_batch_failure_preserves_official_videos") is True,
        "runner preserves official JSONL logs and videos when a selected batch fails before promotion",
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
    pilot_runtime_triage = pilot_runtime.get("reset_timeout_triage", {})
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
        and pilot_runtime_checks.get("collection_progress_markers_recorded") is True
        and pilot_runtime_checks.get("backend_reset_substage_markers_recorded") is True
        and pilot_runtime_checks.get("timeout_or_result_recorded_as_readiness_state") is True
        and pilot_runtime_checks.get("reset_timeout_triage_is_non_evidence") is True
        and pilot_runtime_checks.get("reset_timeout_triage_context_recorded") is True
        and pilot_runtime_checks.get("reset_timeout_operator_actions_present") is True
        and pilot_runtime_triage.get("version") == "maniskill_pilot_reset_timeout_triage_v1"
        and pilot_runtime_triage.get("not_external_evidence") is True
        and pilot_runtime_triage.get("strict_external_evidence_ready") is False
        and (
            pilot_runtime.get("last_progress_stage") != "reset_scene_start"
            or (
                pilot_runtime_triage.get("triage_status") == "RESET_SCENE_TIMEOUT_TRIAGE_READY"
                and bool(str(pilot_runtime_triage.get("task_family", "")).strip())
                and bool(str(pilot_runtime_triage.get("method_name", "")).strip())
                and bool(str(pilot_runtime_triage.get("primary_env_id", "")).strip())
                and bool(str(pilot_runtime_triage.get("last_backend_progress_stage", "")).strip())
                and bool(pilot_runtime_triage.get("backend_progress_stages"))
            )
        )
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
        "maniskill_pilot_runtime_liveness_visible",
        pilot_runtime_basic
        and (pilot_runtime_diagnostic_io or pilot_runtime_unavailable or pilot_runtime_diagnostic_rejected),
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
            f"diagnostic_rejected={pilot_runtime.get('diagnostic_sidecar_rejected_before_jsonl_write')!r}, "
            f"last_stage={pilot_runtime.get('last_progress_stage')!r}, "
            f"last_backend_stage={pilot_runtime_triage.get('last_backend_progress_stage')!r}, "
            f"reset_triage_status={pilot_runtime_triage.get('triage_status')!r}, "
            f"failure_summary={pilot_runtime.get('failure_summary')!r}"
        ),
    )
    add_check(
        checks,
        "maniskill_render_video_preflight_visible",
        render_preflight.get("version") == "maniskill_render_video_preflight_audit_v2"
        and render_preflight.get("passed") is True
        and render_preflight.get("not_external_evidence") is True
        and render_preflight.get("strict_external_evidence_ready") is False
        and int(render_preflight.get("env_count", 0) or 0) >= 1
        and render_preflight.get("render_backend") == "cpu"
        and render_preflight.get("shader_pack") == "minimal"
        and int(render_preflight.get("width", 0) or 0) >= 16
        and int(render_preflight.get("height", 0) or 0) >= 16
        and isinstance(render_preflight.get("render_video_ready"), bool)
        and {check.get("name"): check.get("passed") for check in render_preflight.get("checks", []) or []}.get("render_progress_markers_recorded") is True,
        (
            f"render_video_ready={render_preflight.get('render_video_ready')!r}, "
            f"render_backend={render_preflight.get('render_backend')!r}, "
            f"shader_pack={render_preflight.get('shader_pack')!r}, "
            f"failure_stages={[record.get('failure_progress_stage') for record in render_preflight.get('env_records', []) or []]}, "
            f"terminal_stages={[record.get('terminal_progress_stage') for record in render_preflight.get('env_records', []) or []]}, "
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
    render_resource_checks = {check.get("name"): check.get("passed") for check in render_resource_sweep.get("checks", []) or []}
    add_check(
        checks,
        "render_resource_sweep_visible",
        render_resource_sweep.get("version") == "maniskill_render_resource_sweep_v1"
        and render_resource_sweep.get("passed") is True
        and render_resource_sweep.get("not_external_evidence") is True
        and render_resource_sweep.get("strict_external_evidence_ready") is False
        and render_resource_sweep.get("any_render_video_ready") is False
        and render_resource_sweep.get("descriptor_pool_failure_persists_at_minimum_resolution") is True
        and int(render_resource_sweep.get("record_count", 0) or 0) >= 3
        and "vulkan_descriptor_pool_exhaustion" in (render_resource_sweep.get("renderer_failure_classes", []) or [])
        and render_resource_checks.get("resource_sweep_is_non_evidence") is True
        and render_resource_checks.get("quarantine_paths_are_not_official_evidence") is True
        and (RESULTS / "maniskill_render_resource_sweep.md").exists()
        and (ROOT / "external_validation" / "render_resource_sweep_work_orders.csv").exists(),
        (
            f"any_ready={render_resource_sweep.get('any_render_video_ready')!r}, "
            f"records={render_resource_sweep.get('record_count')!r}, "
            f"classes={render_resource_sweep.get('renderer_failure_classes')!r}"
        ),
    )
    render_remediation_checks = {check.get("name"): check.get("passed") for check in render_remediation.get("checks", []) or []}
    render_remediation_work_ids = {
        str(item.get("id", ""))
        for item in render_remediation.get("work_orders", []) or []
        if isinstance(item, dict)
    }
    add_check(
        checks,
        "render_failure_remediation_packet_visible",
        render_remediation.get("version") == "maniskill_render_failure_remediation_v1"
        and render_remediation.get("passed") is True
        and render_remediation.get("not_external_evidence") is True
        and render_remediation.get("strict_external_evidence_ready") is False
        and render_remediation.get("remediation_state") == "RENDER_REMEDIATION_REQUIRED"
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
        and (ROOT / "external_validation" / "render_failure_remediation_work_orders.csv").exists(),
        (
            f"state={render_remediation.get('remediation_state')!r}, "
            f"errors={render_remediation.get('liveness_render_errors')!r}, "
            f"work_orders={sorted(render_remediation_work_ids)}"
        ),
    )
    render_machine_self_checks = {
        check.get("name"): check.get("passed") for check in render_machine_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "render_machine_qualification_self_test_visible",
        render_machine_self_test.get("version") == "maniskill_render_machine_qualification_self_test_v1"
        and render_machine_self_test.get("passed") is True
        and render_machine_self_test.get("not_external_evidence") is True
        and render_machine_self_test.get("strict_external_evidence_ready") is False
        and render_machine_self_test.get("synthetic_ready_state") == "QUALIFIED_FOR_RENDER_BACKED_PILOT"
        and render_machine_self_test.get("synthetic_fail_closed_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine_self_test.get("missing_env_rejected") is True
        and render_machine_self_test.get("diagnostic_fallback_rejected") is True
        and render_machine_self_test.get("ready_remediation_state") == "RENDER_REMEDIATION_READY"
        and render_machine_self_test.get("failed_remediation_state") == "RENDER_REMEDIATION_REQUIRED"
        and render_machine_self_test.get("real_reports_untouched") is True
        and render_machine_self_checks.get("synthetic_ready_machine_qualifies") is True
        and render_machine_self_checks.get("render_failure_fails_closed") is True
        and render_machine_self_checks.get("missing_environment_record_fails_closed") is True
        and render_machine_self_checks.get("diagnostic_fallback_blocks_qualification") is True
        and render_machine_self_checks.get("real_render_machine_reports_not_overwritten") is True
        and (RESULTS / "maniskill_render_machine_qualification_self_test.md").exists()
        and "results/maniskill_render_machine_qualification_self_test.md" in texts["README"]
        and "results/maniskill_render_machine_qualification_self_test.md" in texts["final_audit"]
        and "results/maniskill_render_machine_qualification_self_test.md" in texts["reproducibility"],
        (
            f"ready={render_machine_self_test.get('synthetic_ready_state')!r}, "
            f"fail_closed={render_machine_self_test.get('synthetic_fail_closed_state')!r}, "
            f"fallback_rejected={render_machine_self_test.get('diagnostic_fallback_rejected')!r}, "
            f"real_untouched={render_machine_self_test.get('real_reports_untouched')!r}"
        ),
    )
    method_checks = {check.get("name"): check.get("passed") for check in method_implementation.get("checks", []) or []}
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest.get("checks", []) or []}
    config_evidence_self_checks = {check.get("name"): check.get("passed") for check in config_evidence_self_test.get("checks", []) or []}
    rollout_evidence_checks = {check.get("name"): check.get("passed") for check in rollout_evidence.get("checks", []) or []}
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_collection.get("checks", []) or []}
    intake_checks = {check.get("name"): check.get("passed") for check in evidence_intake.get("checks", []) or []}
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
        "strict_config_evidence_hash_gate_visible",
        config_evidence_self_test.get("passed") is True
        and config_evidence_self_test.get("not_external_evidence") is True
        and config_evidence_self_test.get("synthetic_config_evidence_ready") is True
        and config_evidence_self_test.get("prepared_config_fixture_ready") is True
        and int(config_evidence_self_test.get("prepared_config_count", 0) or 0) >= 4
        and config_evidence_self_test.get("stale_config_hash_ready") is False
        and config_evidence_self_checks.get("prepared_task_configs_pass_strict_with_temp_manifest") is True
        and config_evidence_self_checks.get("prepared_task_config_methods_match_collection_tasks") is True
        and config_evidence_self_checks.get("stale_manifest_config_hash_fails_strict") is True
        and "sha256_file" in config_validator_text
        and "is_sha256" in config_validator_text
        and "manifest config_hash is required for strict config evidence" in config_validator_text
        and "manifest config_hash must be 64-character SHA256" in config_validator_text
        and "manifest config_hash does not match config_path" in config_validator_text
        and "stale_manifest_config_hash_fails_strict" in config_self_test_text
        and "strict config evidence hash gate" in texts["README"]
        and "strict config evidence hash gate" in texts["final_audit"]
        and "strict config evidence hash gate" in texts["readiness_audit"]
        and "strict config evidence hash gate" in texts["version_log"]
        and "strict config evidence hash gate" in texts["child_status"]
        and "prepared task configs" in texts["README"]
        and "prepared task configs" in texts["final_audit"]
        and "prepared task configs" in texts["readiness_decision"]
        and "prepared task configs" in texts["readiness_audit"],
        "strict config validation recomputes manifest-declared task-config hashes and rejects stale config_path/config_hash pairs",
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
        "strict_video_evidence_gate_visible",
        "strict_video_evidence" in rollout_validator_text
        and "MIN_STRICT_VIDEO_BYTES" in rollout_validator_text
        and "FORBIDDEN_VIDEO_PATH_FRAGMENTS" in rollout_validator_text
        and "REQUIRED_METHODS" in rollout_validator_text
        and "manifest missing required external methods" in rollout_validator_text
        and "staging" in rollout_validator_text
        and "backup" in rollout_validator_text
        and "ftyp" in rollout_validator_text
        and "seen_record_keys" in rollout_validator_text
        and "duplicate rollout record identity" in rollout_validator_text
        and "seen_video_paths" in rollout_validator_text
        and "duplicate video_path" in rollout_validator_text
        and "MIN_EPISODES_PER_METHOD" in rollout_validator_text
        and "external_statistical_confidence_v1" in rollout_validator_text
        and "bootstrap_mean_ci" in rollout_validator_text
        and "statistical_confidence" in rollout_validator_text
        and "confidence_gate" in rollout_validator_text
        and "record_counts_by_task_method" in rollout_validator_text
        and "episodes_per_method must be integer >=" in rollout_validator_text
        and "does not match episodes_per_method" in rollout_validator_text
        and "paired_panel_lines" in rollout_validator_text
        and "paired_panel_methods" in rollout_validator_text
        and "duplicate method record within paired reset" in rollout_validator_text
        and "missing declared methods" in rollout_validator_text
        and "manifest_task_configs" in rollout_validator_text
        and "config_hash does not match config_path" in rollout_validator_text
        and "skill_i must match manifest task config" in rollout_validator_text
        and "manifest_method_hashes" in rollout_validator_text
        and "policy_or_config_hash must match manifest checkpoint_or_config_hash" in rollout_validator_text
        and "diagnostic fallback sidecar" in rollout_validator_text
        and "strict video fixture did not reject fake MP4" in rollout_self_test_text
        and "missing method-coverage test did not fail" in rollout_self_test_text
        and "weak episode-count test did not fail" in rollout_self_test_text
        and "short record-count test did not fail" in rollout_self_test_text
        and "duplicate paired-method test did not fail" in rollout_self_test_text
        and "missing paired-method test did not fail" in rollout_self_test_text
        and "duplicate rollout identity test did not fail" in rollout_self_test_text
        and "duplicate video path test did not fail" in rollout_self_test_text
        and "stale task config hash test did not fail" in rollout_self_test_text
        and "stale task config row test did not fail" in rollout_self_test_text
        and "spoofed policy/config hash test did not fail" in rollout_self_test_text
        and "weak statistical confidence test did not fail" in rollout_self_test_text
        and "external_success_margin_confidence_gate" in rollout_self_test_text
        and "internal_runner_artifact.staging.mp4" in rollout_self_test_text
        and "internal_runner_artifact.backup.mp4" in rollout_self_test_text
        and "write_synthetic_mp4" in evidence_pipeline_self_test_text
        and "confidence-gated rollout statistics" in evidence_pipeline_self_test_text
        and "tampered rollout confidence summary did not fail" in evidence_pipeline_self_test_text
        and "external_rollout_confidence_gates_passed" in audit_external_evidence_text
        and "CONFIDENCE_METRICS" in audit_external_evidence_text
        and "all_primary_confidence_gates_passed" in audit_external_evidence_text
        and "confidence-gated external rollout statistics" in texts["README"]
        and "confidence-gated external rollout statistics" in texts["final_audit"]
        and "confidence-gated external rollout statistics" in texts["readiness_audit"]
        and "final rollout confidence summary gate" in texts["README"]
        and "final rollout confidence summary gate" in texts["final_audit"]
        and "final rollout confidence summary gate" in texts["readiness_audit"],
        "strict rollout validation rejects placeholder/diagnostic/staged/backup/non-MP4 video paths, incomplete method sets, duplicate rows/videos, weak sample counts, mispaired method panels, stale task configs, manifest method-hash mismatches, weak confidence bounds, and missing final confidence summaries",
    )
    evidence_pipeline_self_checks = {
        check.get("name"): check.get("passed") for check in evidence_pipeline_self_test.get("checks", []) or []
    }
    rollout_validator_self_checks = {
        check.get("name"): check.get("passed") for check in rollout_validator_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "external_rollout_validator_self_test_visible",
        rollout_validator_self_test.get("version") == "external_rollout_validator_self_test_v1"
        and rollout_validator_self_test.get("passed") is True
        and rollout_validator_self_test.get("not_external_evidence") is True
        and int(rollout_validator_self_test.get("synthetic_records_loaded", 0) or 0) >= 1440
        and int(rollout_validator_self_test.get("synthetic_task_count", 0) or 0) >= 4
        and int(rollout_validator_self_test.get("synthetic_method_count", 0) or 0) >= 12
        and rollout_validator_self_test.get("synthetic_confidence_gates_passed") is True
        and rollout_validator_self_test.get("weak_confidence_rejected") is True
        and rollout_validator_self_test.get("strict_video_rejections_checked") is True
        and rollout_validator_self_test.get("real_rollout_reports_untouched") is True
        and rollout_validator_self_checks.get("synthetic_records_recomputed") is True
        and rollout_validator_self_checks.get("synthetic_threshold_metrics_match_expected") is True
        and rollout_validator_self_checks.get("synthetic_confidence_gates_pass") is True
        and rollout_validator_self_checks.get("weak_confidence_rejected") is True
        and rollout_validator_self_checks.get("strict_video_fixture_rejects_fake_mp4") is True
        and rollout_validator_self_checks.get("strict_video_fixture_rejects_forbidden_fragments") is True
        and rollout_validator_self_checks.get("real_rollout_metrics_report_not_overwritten") is True
        and (RESULTS / "external_rollout_validator_self_test.md").exists()
        and "results/external_rollout_validator_self_test.md" in texts["README"]
        and "results/external_rollout_validator_self_test.md" in texts["final_audit"]
        and "results/external_rollout_validator_self_test.md" in texts["reproducibility"],
        (
            f"records={rollout_validator_self_test.get('synthetic_records_loaded')!r}, "
            f"confidence={rollout_validator_self_test.get('synthetic_confidence_gates_passed')!r}, "
            f"weak_rejected={rollout_validator_self_test.get('weak_confidence_rejected')!r}, "
            f"real_untouched={rollout_validator_self_test.get('real_rollout_reports_untouched')!r}"
        ),
    )
    add_check(
        checks,
        "external_evidence_pipeline_self_test_visible",
        evidence_pipeline_self_test.get("version") == "external_evidence_pipeline_self_test_v1"
        and evidence_pipeline_self_test.get("passed") is True
        and evidence_pipeline_self_test.get("not_external_evidence") is True
        and evidence_pipeline_self_test.get("strict_external_evidence_ready") is False
        and evidence_pipeline_self_test.get("synthetic_submission_ready") is True
        and int(evidence_pipeline_self_test.get("synthetic_record_count", 0) or 0) >= 1440
        and int(evidence_pipeline_self_test.get("synthetic_task_count", 0) or 0) >= 4
        and int(evidence_pipeline_self_test.get("synthetic_method_count", 0) or 0) >= 12
        and evidence_pipeline_self_test.get("synthetic_confidence_gates_passed") is True
        and evidence_pipeline_self_test.get("tampered_rollout_confidence_rejected") is True
        and evidence_pipeline_self_test.get("tampered_release_hash_rejected") is True
        and evidence_pipeline_self_test.get("real_manifest_untouched") is True
        and evidence_pipeline_self_test.get("real_reports_untouched") is True
        and evidence_pipeline_self_checks.get("synthetic_complete_package_reaches_final_external_ready") is True
        and evidence_pipeline_self_checks.get("synthetic_records_cover_tasks_methods_and_confidence") is True
        and evidence_pipeline_self_checks.get("synthetic_component_gates_pass") is True
        and evidence_pipeline_self_checks.get("tampered_rollout_confidence_summary_rejected") is True
        and evidence_pipeline_self_checks.get("tampered_release_artifact_hash_rejected") is True
        and evidence_pipeline_self_checks.get("real_repository_evidence_state_untouched") is True
        and (ROOT / "scripts" / "self_test_external_evidence_pipeline.py").exists()
        and (RESULTS / "external_evidence_pipeline_self_test.md").exists(),
        (
            f"synthetic_ready={evidence_pipeline_self_test.get('synthetic_submission_ready')!r}, "
            f"records={evidence_pipeline_self_test.get('synthetic_record_count')!r}, "
            f"confidence_rejected={evidence_pipeline_self_test.get('tampered_rollout_confidence_rejected')!r}, "
            f"release_rejected={evidence_pipeline_self_test.get('tampered_release_hash_rejected')!r}, "
            f"real_untouched={evidence_pipeline_self_test.get('real_manifest_untouched')!r}/"
            f"{evidence_pipeline_self_test.get('real_reports_untouched')!r}"
        ),
    )
    release_self_checks = {check.get("name"): check.get("passed") for check in release_package_self_test.get("checks", []) or []}
    add_check(
        checks,
        "release_package_internal_artifact_rejection_visible",
        release_package.get("release_package_ready") is False
        and release_package.get("not_external_evidence") is True
        and release_package_self_test.get("passed") is True
        and release_package_self_test.get("not_external_evidence") is True
        and release_package_self_test.get("synthetic_release_package_ready") is True
        and release_package_self_test.get("bad_release_package_ready") is False
        and release_self_checks.get("bad_artifacts_rejected_as_release_evidence") is True
        and "FORBIDDEN_RELEASE_LOG_VIDEO_FRAGMENTS" in release_audit_text
        and "inspect_video_artifact" in release_audit_text
        and "video directory contains no MP4 files" in release_audit_text
        and "video artifact is not MP4-like evidence with an ftyp box" in release_audit_text
        and "staging" in release_audit_text
        and "backup" in release_audit_text
        and "diagnostic" in release_audit_text
        and "peg_place_regrasp.staging.jsonl" in release_self_test_text
        and "peg_place_regrasp.backup.jsonl" in release_self_test_text
        and "peg_place_regrasp.diagnostic.mp4" in release_self_test_text
        and "peg_place_regrasp.fallback.mp4" in release_self_test_text
        and "empty_video_dir" in release_self_test_text
        and "video directory contains no MP4 files" in release_self_test_text
        and "tampered release artifact hash test did not fail" in evidence_pipeline_self_test_text
        and "hash_mismatches" in evidence_pipeline_self_test_text
        and "release-package internal-artifact rejection gate" in texts["README"]
        and "final release artifact hash recomputation gate" in texts["README"]
        and "release-package internal-artifact rejection gate" in texts["final_audit"]
        and "final release artifact hash recomputation gate" in texts["final_audit"]
        and "release-package internal-artifact rejection gate" in texts["readiness_audit"]
        and "final release artifact hash recomputation gate" in texts["readiness_audit"],
        (
            f"release_package_ready={release_package.get('release_package_ready')!r}, "
            f"bad_release_package_ready={release_package_self_test.get('bad_release_package_ready')!r}"
        ),
    )
    add_check(
        checks,
        "ablation_collection_packet_visible",
        ablation_collection.get("passed") is True
        and ablation_collection.get("not_external_evidence") is True
        and ablation_collection.get("strict_external_evidence_ready") is False
        and ablation_collection.get("manifest_ablation_evidence_ready") is False
        and int(ablation_collection.get("work_order_count", 0) or 0) == 5
        and int(ablation_collection.get("expected_ablation_records", 0) or 0) >= 600
        and ablation_checks.get("every_required_ablation_has_work_order") is True
        and ablation_checks.get("required_ablations_match_strict_audit") is True,
        (
            f"work_order_count={ablation_collection.get('work_order_count')!r}, "
            f"expected_ablation_records={ablation_collection.get('expected_ablation_records')!r}, "
            f"manifest_ablation_evidence_ready={ablation_collection.get('manifest_ablation_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "evidence_intake_ledger_visible",
        evidence_intake.get("passed") is True
        and evidence_intake.get("not_external_evidence") is True
        and evidence_intake.get("strict_external_evidence_ready") is False
        and int(evidence_intake.get("blocking_failure_count", 0) or 0) >= 30
        and evidence_intake.get("blocking_failure_count") == evidence_intake.get("mapped_failure_count")
        and not evidence_intake.get("unmapped_failures")
        and intake_checks.get("every_blocking_failure_is_mapped") is True
        and intake_checks.get("strict_command_spine_covers_final_evidence_path") is True,
        (
            f"mapped={evidence_intake.get('mapped_failure_count')!r}/"
            f"{evidence_intake.get('blocking_failure_count')!r}, "
            f"strict_external_evidence_ready={evidence_intake.get('strict_external_evidence_ready')!r}"
        ),
    )
    precollection_checks = {check.get("name"): check.get("passed") for check in precollection_manifest.get("checks", []) or []}
    add_check(
        checks,
        "precollection_manifest_draft_visible",
        precollection_manifest.get("version") == "external_precollection_manifest_draft_audit_v1"
        and precollection_manifest.get("passed") is True
        and precollection_manifest.get("not_external_evidence") is True
        and precollection_manifest.get("draft_ready") is True
        and precollection_manifest.get("strict_external_evidence_ready") is False
        and precollection_manifest.get("strict_config_evidence_ready") is False
        and precollection_manifest.get("official_manifest_exists") is False
        and int(precollection_manifest.get("prepared_config_count", 0) or 0) >= 4
        and int(precollection_manifest.get("candidate_method_config_count", 0) or 0) >= 11
        and int(precollection_manifest.get("method_gap_count", 0) or 0) >= 11
        and int(precollection_manifest.get("missing_rollout_artifact_count", 0) or 0) >= 8
        and precollection_checks.get("draft_marked_non_evidence_and_fail_closed") is True
        and precollection_checks.get("prepared_config_hashes_prefilled") is True
        and precollection_checks.get("candidate_method_configs_prefilled") is True
        and precollection_checks.get("method_gaps_bind_candidate_configs") is True
        and precollection_checks.get("method_gaps_still_require_independent_evidence") is True,
        (
            f"prepared_configs={precollection_manifest.get('prepared_config_count')!r}, "
            f"method_configs={precollection_manifest.get('candidate_method_config_count')!r}, "
            f"method_gaps={precollection_manifest.get('method_gap_count')!r}, "
            f"rollout_gaps={precollection_manifest.get('missing_rollout_artifact_count')!r}, "
            f"official_manifest_exists={precollection_manifest.get('official_manifest_exists')!r}"
        ),
    )
    precollection_freeze_checks = {check.get("name"): check.get("passed") for check in precollection_freeze.get("checks", []) or []}
    add_check(
        checks,
        "precollection_freeze_receipt_visible",
        precollection_freeze.get("version") == "external_precollection_freeze_receipt_audit_v1"
        and precollection_freeze.get("passed") is True
        and precollection_freeze.get("not_external_evidence") is True
        and precollection_freeze.get("strict_external_evidence_ready") is False
        and precollection_freeze.get("freeze_receipt_ready") is False
        and int(precollection_freeze.get("locked_artifact_count", 0) or 0) >= 42
        and int(precollection_freeze.get("candidate_method_config_count", 0) or 0) >= 11
        and precollection_freeze.get("method_config_hash_lock_ready") is True
        and precollection_freeze_checks.get("receipt_is_non_evidence_and_fail_closed") is True
        and precollection_freeze_checks.get("core_lock_artifacts_hashed") is True
        and precollection_freeze_checks.get("prepared_task_configs_hashed") is True
        and precollection_freeze_checks.get("method_config_materialization_artifacts_hashed") is True
        and precollection_freeze_checks.get("candidate_method_configs_hashed") is True
        and precollection_freeze_checks.get("candidate_method_config_hashes_match_plan") is True
        and precollection_freeze_checks.get("candidate_method_configs_remain_non_evidence") is True
        and precollection_freeze_checks.get("strict_sequence_places_receipt_before_collection") is True
        and (ROOT / "external_validation" / "precollection_freeze_receipt.md").exists()
        and (ROOT / "external_validation" / "precollection_freeze_receipt.csv").exists(),
        (
            f"locked_artifacts={precollection_freeze.get('locked_artifact_count')!r}, "
            f"candidate_method_configs={precollection_freeze.get('candidate_method_config_count')!r}, "
            f"freeze_receipt_ready={precollection_freeze.get('freeze_receipt_ready')!r}, "
            f"strict_external_evidence_ready={precollection_freeze.get('strict_external_evidence_ready')!r}"
        ),
    )
    precollection_freeze_self_checks = {
        check.get("name"): check.get("passed") for check in precollection_freeze_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "precollection_freeze_receipt_self_test_visible",
        precollection_freeze_self_test.get("version") == "external_precollection_freeze_receipt_self_test_v1"
        and precollection_freeze_self_test.get("passed") is True
        and precollection_freeze_self_test.get("not_external_evidence") is True
        and precollection_freeze_self_test.get("synthetic_freeze_ready") is True
        and precollection_freeze_self_test.get("missing_backend_rejected") is True
        and precollection_freeze_self_test.get("placeholder_run_rejected") is True
        and precollection_freeze_self_test.get("missing_lock_artifact_rejected") is True
        and precollection_freeze_self_test.get("dirty_checkout_rejected") is True
        and precollection_freeze_self_test.get("real_reports_untouched") is True
        and precollection_freeze_self_checks.get("synthetic_complete_freeze_reaches_collection_readiness") is True
        and precollection_freeze_self_checks.get("synthetic_ready_checks_cover_hashes_identity_and_order") is True
        and precollection_freeze_self_checks.get("missing_backend_selection_rejected") is True
        and precollection_freeze_self_checks.get("placeholder_run_identity_rejected") is True
        and precollection_freeze_self_checks.get("missing_lock_artifact_rejected") is True
        and precollection_freeze_self_checks.get("dirty_checkout_rejected") is True
        and precollection_freeze_self_checks.get("real_precollection_freeze_reports_not_overwritten") is True
        and (ROOT / "scripts" / "self_test_external_precollection_freeze_receipt.py").exists()
        and (RESULTS / "external_precollection_freeze_receipt_self_test.md").exists(),
        (
            f"synthetic_ready={precollection_freeze_self_test.get('synthetic_freeze_ready')!r}, "
            f"missing_backend={precollection_freeze_self_test.get('missing_backend_rejected')!r}, "
            f"placeholder_run={precollection_freeze_self_test.get('placeholder_run_rejected')!r}, "
            f"missing_lock={precollection_freeze_self_test.get('missing_lock_artifact_rejected')!r}, "
            f"dirty_checkout={precollection_freeze_self_test.get('dirty_checkout_rejected')!r}"
        ),
    )
    postcollection_seal_checks = {check.get("name"): check.get("passed") for check in postcollection_seal.get("checks", []) or []}
    add_check(
        checks,
        "postcollection_evidence_seal_visible",
        postcollection_seal.get("version") == "external_postcollection_evidence_seal_audit_v1"
        and postcollection_seal.get("passed") is True
        and postcollection_seal.get("not_external_evidence") is True
        and postcollection_seal.get("strict_external_evidence_ready") is False
        and postcollection_seal.get("postcollection_seal_ready") is False
        and postcollection_seal.get("ready_for_manifest_promotion") is False
        and int(postcollection_seal.get("sealed_artifact_count", 0) or 0) >= 8
        and int(postcollection_seal.get("jsonl_record_count", 0) or 0) == 0
        and int(postcollection_seal.get("rollout_video_count", 0) or 0) == 0
        and postcollection_seal_checks.get("seal_is_non_evidence_and_fail_closed") is True
        and postcollection_seal_checks.get("hash_inventory_written_for_precollection_inputs") is True
        and postcollection_seal_checks.get("strict_sequence_places_seal_after_collection_before_manifest") is True
        and postcollection_seal_checks.get("seal_references_rollout_pairing_release_final_gates") is True
        and (ROOT / "external_validation" / "postcollection_evidence_seal.md").exists()
        and (ROOT / "external_validation" / "postcollection_evidence_seal.csv").exists(),
        (
            f"sealed_artifacts={postcollection_seal.get('sealed_artifact_count')!r}, "
            f"records={postcollection_seal.get('jsonl_record_count')!r}, "
            f"videos={postcollection_seal.get('rollout_video_count')!r}, "
            f"seal_ready={postcollection_seal.get('postcollection_seal_ready')!r}, "
            f"manifest_promotion={postcollection_seal.get('ready_for_manifest_promotion')!r}"
        ),
    )
    postcollection_seal_self_checks = {
        check.get("name"): check.get("passed") for check in postcollection_seal_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "postcollection_evidence_seal_self_test_visible",
        postcollection_seal_self_test.get("version") == "external_postcollection_evidence_seal_self_test_v1"
        and postcollection_seal_self_test.get("passed") is True
        and postcollection_seal_self_test.get("not_external_evidence") is True
        and postcollection_seal_self_test.get("synthetic_seal_ready") is True
        and postcollection_seal_self_test.get("missing_operator_metadata_rejected") is True
        and postcollection_seal_self_test.get("incomplete_video_set_rejected") is True
        and postcollection_seal_self_test.get("manifest_present_rejected") is True
        and postcollection_seal_self_test.get("real_reports_untouched") is True
        and postcollection_seal_self_checks.get("synthetic_complete_seal_reaches_manifest_promotion") is True
        and postcollection_seal_self_checks.get("missing_operator_metadata_rejected") is True
        and postcollection_seal_self_checks.get("incomplete_video_set_rejected") is True
        and postcollection_seal_self_checks.get("manifest_present_rejected_before_promotion") is True
        and (ROOT / "scripts" / "self_test_external_postcollection_evidence_seal.py").exists()
        and (RESULTS / "external_postcollection_evidence_seal_self_test.md").exists(),
        (
            f"synthetic_ready={postcollection_seal_self_test.get('synthetic_seal_ready')!r}, "
            f"metadata_rejected={postcollection_seal_self_test.get('missing_operator_metadata_rejected')!r}, "
            f"videos_rejected={postcollection_seal_self_test.get('incomplete_video_set_rejected')!r}, "
            f"manifest_rejected={postcollection_seal_self_test.get('manifest_present_rejected')!r}"
        ),
    )
    postcollection_consistency_checks = {check.get("name"): check.get("passed") for check in postcollection_consistency.get("checks", []) or []}
    add_check(
        checks,
        "postcollection_seal_consistency_gate_visible",
        postcollection_consistency.get("version") == "external_postcollection_seal_consistency_audit_v1"
        and postcollection_consistency.get("passed") is True
        and postcollection_consistency.get("not_external_evidence") is True
        and postcollection_consistency.get("strict_external_evidence_ready") is False
        and postcollection_consistency.get("seal_consistency_ready") is False
        and postcollection_consistency.get("ready_for_manifest_promotion") is False
        and int(postcollection_consistency.get("matched_hash_count", 0) or 0) >= 8
        and int(postcollection_consistency.get("current_jsonl_record_count", 0) or 0) == 0
        and int(postcollection_consistency.get("current_rollout_video_count", 0) or 0) == 0
        and not postcollection_consistency.get("mismatched_hashes")
        and not postcollection_consistency.get("extra_official_artifacts")
        and postcollection_consistency_checks.get("sealed_hashes_recompute_without_drift") is True
        and postcollection_consistency_checks.get("strict_sequence_places_consistency_after_seal_before_manifest") is True
        and (ROOT / "results" / "external_postcollection_seal_consistency_audit.md").exists(),
        (
            f"matched={postcollection_consistency.get('matched_hash_count')!r}, "
            f"records={postcollection_consistency.get('current_jsonl_record_count')!r}, "
            f"videos={postcollection_consistency.get('current_rollout_video_count')!r}, "
            f"consistency_ready={postcollection_consistency.get('seal_consistency_ready')!r}"
        ),
    )
    postcollection_consistency_self_checks = {
        check.get("name"): check.get("passed") for check in postcollection_consistency_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "postcollection_seal_consistency_self_test_visible",
        postcollection_consistency_self_test.get("version") == "external_postcollection_seal_consistency_self_test_v1"
        and postcollection_consistency_self_test.get("passed") is True
        and postcollection_consistency_self_test.get("not_external_evidence") is True
        and postcollection_consistency_self_test.get("synthetic_consistency_ready") is True
        and postcollection_consistency_self_test.get("drift_rejected") is True
        and postcollection_consistency_self_test.get("unsealed_official_artifact_rejected") is True
        and postcollection_consistency_self_test.get("real_report_untouched") is True
        and postcollection_consistency_self_checks.get("synthetic_ready_seal_consistency_passes") is True
        and postcollection_consistency_self_checks.get("hash_drift_rejected") is True
        and postcollection_consistency_self_checks.get("unsealed_official_artifact_rejected") is True
        and (ROOT / "scripts" / "self_test_external_postcollection_seal_consistency.py").exists()
        and (RESULTS / "external_postcollection_seal_consistency_self_test.md").exists(),
        (
            f"synthetic_ready={postcollection_consistency_self_test.get('synthetic_consistency_ready')!r}, "
            f"drift_rejected={postcollection_consistency_self_test.get('drift_rejected')!r}, "
            f"extra_rejected={postcollection_consistency_self_test.get('unsealed_official_artifact_rejected')!r}"
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
        and method_checks.get("manifest_entry_templates_bind_hash_to_checkpoint_config_artifact") is True
        and method_checks.get("manifest_entry_templates_require_independent_provenance") is True
        and method_checks.get("manifest_entry_templates_bind_fairness_contract") is True
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
        and method_checks.get("reference_manifest_stubs_not_strict_ready") is True,
        (
            f"method_implementation_packet_ready={method_implementation.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_implementation.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    method_config_checks = {
        check.get("name"): check.get("passed")
        for check in method_config_materialization.get("checks", []) or []
    }
    add_check(
        checks,
        "external_method_config_materialization_visible",
        method_config_materialization.get("passed") is True
        and method_config_materialization.get("not_external_evidence") is True
        and method_config_materialization.get("strict_adapter_evidence_ready") is False
        and method_config_materialization.get("strict_external_evidence_ready") is False
        and int(method_config_materialization.get("candidate_config_count", 0) or 0) >= 11
        and method_config_materialization.get("oracle_excluded") is True
        and method_config_checks.get("candidate_configs_cover_non_oracle_methods") is True
        and method_config_checks.get("candidate_hashes_match_written_files") is True
        and method_config_checks.get("manifest_stubs_bind_checkpoint_config_hashes") is True
        and method_config_checks.get("independent_implementation_still_required") is True
        and method_config_checks.get("no_real_manifest_logs_videos_or_checkpoints_written") is True
        and (ROOT / "scripts" / "materialize_external_method_configs.py").exists()
        and (ROOT / "external_validation" / "method_config_materialization_plan.md").exists()
        and (ROOT / "external_validation" / "method_config_candidates.csv").exists()
        and (RESULTS / "external_method_config_materialization_audit.md").exists()
        and "External method config materialization" in texts["README"]
        and "External method config materialization" in texts["final_audit"]
        and "External method config materialization" in texts["reproducibility"]
        and "External method config materialization" in texts["outreach"],
        (
            f"candidate_configs={method_config_materialization.get('candidate_config_count')!r}, "
            f"strict_adapter_evidence_ready={method_config_materialization.get('strict_adapter_evidence_ready')!r}, "
            f"oracle_excluded={method_config_materialization.get('oracle_excluded')!r}"
        ),
    )
    adapter_evidence_self_checks = {check.get("name"): check.get("passed") for check in adapter_evidence_self_test.get("checks", [])}
    scaffold_guard_self_checks = {
        check.get("name"): check.get("passed") for check in adapter_scaffold_guard_self_test.get("checks", []) or []
    }
    add_check(
        checks,
        "adapter_scaffold_guard_self_test_visible",
        adapter_scaffold_guard_self_test.get("version") == "external_adapter_scaffold_guard_self_test_v1"
        and adapter_scaffold_guard_self_test.get("passed") is True
        and adapter_scaffold_guard_self_test.get("not_external_evidence") is True
        and adapter_scaffold_guard_self_test.get("scaffold_directory_detected") is True
        and adapter_scaffold_guard_self_test.get("scaffold_template_detected") is True
        and adapter_scaffold_guard_self_test.get("ordinary_adapter_falsely_rejected") is False
        and adapter_scaffold_guard_self_test.get("temporary_adapter_file_removed") is True
        and adapter_scaffold_guard_self_test.get("real_adapter_reports_untouched") is True
        and scaffold_guard_self_checks.get("scaffold_directory_detected") is True
        and scaffold_guard_self_checks.get("scaffold_template_detected") is True
        and scaffold_guard_self_checks.get("ordinary_replacement_adapter_not_flagged") is True
        and scaffold_guard_self_checks.get("temporary_adapter_file_removed") is True
        and scaffold_guard_self_checks.get("real_adapter_reports_untouched") is True
        and (RESULTS / "external_adapter_scaffold_guard_self_test.md").exists()
        and "results/external_adapter_scaffold_guard_self_test.md" in texts["README"]
        and "results/external_adapter_scaffold_guard_self_test.md" in texts["final_audit"]
        and "results/external_adapter_scaffold_guard_self_test.md" in texts["reproducibility"],
        (
            f"scaffold_dir={adapter_scaffold_guard_self_test.get('scaffold_directory_detected')!r}, "
            f"scaffold_template={adapter_scaffold_guard_self_test.get('scaffold_template_detected')!r}, "
            f"ordinary_false_positive={adapter_scaffold_guard_self_test.get('ordinary_adapter_falsely_rejected')!r}, "
            f"real_untouched={adapter_scaffold_guard_self_test.get('real_adapter_reports_untouched')!r}"
        ),
    )
    add_check(
        checks,
        "strict_reference_adapter_rejection_gate_visible",
        adapter_evidence_self_test.get("passed") is True
        and adapter_evidence_self_test.get("not_external_evidence") is True
        and adapter_evidence_self_test.get("synthetic_adapter_evidence_ready") is True
        and adapter_evidence_self_test.get("tracked_candidate_config_fixture_ready") is True
        and int(adapter_evidence_self_test.get("tracked_candidate_config_count", 0) or 0) >= 11
        and adapter_evidence_self_test.get("scaffold_adapter_evidence_ready") is False
        and adapter_evidence_self_test.get("reference_adapter_evidence_ready") is False
        and adapter_evidence_self_test.get("leaky_provenance_ready") is False
        and adapter_evidence_self_test.get("implementation_hash_only_ready") is False
        and adapter_evidence_self_test.get("missing_fairness_contract_ready") is False
        and adapter_evidence_self_test.get("fairness_mismatch_ready") is False
        and adapter_evidence_self_checks.get("tracked_candidate_configs_pass_strict_with_temp_independent_adapters") is True
        and adapter_evidence_self_checks.get("tracked_candidate_config_methods_match_non_oracle_methods") is True
        and adapter_evidence_self_checks.get("leaky_or_reference_provenance_fails_strict") is True
        and adapter_evidence_self_checks.get("implementation_hash_cannot_replace_checkpoint_or_config") is True
        and adapter_evidence_self_checks.get("fairness_contract_missing_or_mismatch_fails_strict") is True
        and adapter_evidence_self_checks.get("reference_adapters_rejected_as_strict_evidence") is True
        and "tracked candidate method configs" in texts["README"]
        and "tracked candidate method configs" in texts["final_audit"]
        and "tracked candidate method configs" in texts["readiness_decision"]
        and "tracked candidate method configs" in texts["readiness_audit"],
        (
            f"tracked_candidate_config_fixture_ready={adapter_evidence_self_test.get('tracked_candidate_config_fixture_ready')!r}, "
            f"reference_adapter_evidence_ready={adapter_evidence_self_test.get('reference_adapter_evidence_ready')!r}, "
            f"leaky_provenance_ready={adapter_evidence_self_test.get('leaky_provenance_ready')!r}, "
            f"implementation_hash_only_ready={adapter_evidence_self_test.get('implementation_hash_only_ready')!r}, "
            f"fairness_mismatch_ready={adapter_evidence_self_test.get('fairness_mismatch_ready')!r}, "
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
    failure_memory_metrics = failure_memory.get("proposed_metrics", {})
    failure_memory_comparison = failure_memory.get("comparison", {})
    add_check(
        checks,
        "failure_memory_adaptation_visible",
        failure_memory.get("version") == "failure_memory_adaptation_audit_v1"
        and failure_memory.get("passed") is True
        and failure_memory.get("not_external_evidence") is True
        and int(failure_memory_metrics.get("memory_signature_count", 0) or 0) >= 2000
        and int(failure_memory_metrics.get("frontiers_covered", 0) or 0) >= 1600
        and float(failure_memory_metrics.get("memory_breach_future_breach_correlation", 0.0) or 0.0) >= 0.90
        and float(failure_memory_metrics.get("high_low_future_breach_gap", 0.0) or 0.0) >= 0.04
        and float(failure_memory_metrics.get("high_low_future_utility_gap", 0.0) or 0.0) <= -0.12
        and float(failure_memory_comparison.get("high_memory_future_breach_delta", 0.0) or 0.0) <= -0.06
        and float(failure_memory_comparison.get("high_memory_future_utility_delta", 0.0) or 0.0) >= 0.20
        and (ROOT / "paper" / "generated_failure_memory_adaptation_table.tex").exists(),
        (
            f"signatures={failure_memory_metrics.get('memory_signature_count')!r}, "
            f"frontiers={failure_memory_metrics.get('frontiers_covered')!r}, "
            f"corr={failure_memory_metrics.get('memory_breach_future_breach_correlation')!r}, "
            f"breach_delta={failure_memory_comparison.get('high_memory_future_breach_delta')!r}"
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
            "local_failure_memory_adaptation_claim",
            "local_model_release_claim",
            "external_platform_probe_claim",
            "maniskill_task_binding_probe_claim",
            "maniskill_env_smoke_probe_claim",
            "maniskill_fidelity_metadata_probe_claim",
            "external_operator_packet_claim",
            "external_operator_handoff_bundle_claim",
            "external_operator_release_bundle_claim",
            "external_collection_machine_bootstrap_claim",
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
            "maniskill_render_machine_qualification_claim",
            "external_collection_job_packet_claim",
            "external_config_manifest_packet_claim",
            "external_config_evidence_hash_gate_claim",
            "external_rollout_evidence_packet_claim",
            "external_strict_video_evidence_gate_claim",
            "external_ablation_collection_packet_claim",
            "external_evidence_intake_ledger_claim",
            "external_precollection_manifest_draft_claim",
            "external_precollection_freeze_receipt_claim",
            "external_precollection_freeze_receipt_self_test_claim",
            "external_postcollection_evidence_seal_claim",
            "external_postcollection_evidence_seal_self_test_claim",
            "external_postcollection_seal_consistency_gate_claim",
            "external_postcollection_seal_consistency_self_test_claim",
            "external_method_implementation_packet_claim",
            "external_method_config_materialization_claim",
            "external_method_reference_provenance_claim",
            "external_manifest_assembly_checklist_claim",
            "external_manifest_builder_self_test_claim",
            "external_config_materialization_claim",
            "reviewer_response_packet_claim",
        }.issubset(claim_names),
        f"missing={sorted({'local_planner_edge_policy_claim', 'local_failure_memory_adaptation_claim', 'local_model_release_claim', 'external_platform_probe_claim', 'maniskill_task_binding_probe_claim', 'maniskill_env_smoke_probe_claim', 'maniskill_fidelity_metadata_probe_claim', 'external_operator_packet_claim', 'external_operator_handoff_bundle_claim', 'external_operator_release_bundle_claim', 'external_collection_machine_bootstrap_claim', 'external_analysis_plan_claim', 'external_platform_onboarding_claim', 'external_fidelity_provenance_packet_claim', 'external_fidelity_acceptance_draft_claim', 'external_fidelity_acceptance_materializer_claim', 'external_backend_integration_packet_claim', 'maniskill_reference_backend_claim', 'maniskill_reference_collection_preflight_claim', 'external_runner_backend_probe_claim', 'external_pilot_smoke_packet_claim', 'maniskill_pilot_runtime_liveness_claim', 'maniskill_render_video_preflight_claim', 'maniskill_render_machine_qualification_claim', 'external_collection_job_packet_claim', 'external_config_manifest_packet_claim', 'external_config_evidence_hash_gate_claim', 'external_rollout_evidence_packet_claim', 'external_strict_video_evidence_gate_claim', 'external_ablation_collection_packet_claim', 'external_evidence_intake_ledger_claim', 'external_precollection_manifest_draft_claim', 'external_precollection_freeze_receipt_claim', 'external_precollection_freeze_receipt_self_test_claim', 'external_postcollection_evidence_seal_claim', 'external_postcollection_evidence_seal_self_test_claim', 'external_postcollection_seal_consistency_gate_claim', 'external_postcollection_seal_consistency_self_test_claim', 'external_method_implementation_packet_claim', 'external_method_config_materialization_claim', 'external_method_reference_provenance_claim', 'external_manifest_assembly_checklist_claim', 'external_manifest_builder_self_test_claim', 'external_config_materialization_claim', 'reviewer_response_packet_claim'} - claim_names)}",
    )

    required_terms_by_file = {
        "README": [
            "adaptive physical world/action model for skill seams",
            "Planner-edge policy audit",
            "Failure-memory adaptation audit",
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
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "cache-independent",
            "fidelity materializer checkout self-test",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "External collection preflight self-test",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "ManiSkill render machine qualification packet",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "render resource sweep",
            "ManiSkill pilot runtime liveness audit",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "External config manifest packet",
            "External rollout evidence packet",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty-video-directory",
            "non-MP4-like",
            "External ablation collection packet",
            "External evidence intake ledger",
            "External precollection manifest draft",
            "External precollection freeze receipt",
            "External precollection freeze receipt self-test",
            "External postcollection evidence seal",
            "External postcollection evidence seal self-test",
            "External postcollection seal consistency gate",
            "External postcollection seal consistency self-test",
            "External method implementation packet",
            "External method config materialization",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "External manifest builder self-test",
            "External full-pipeline evidence self-test",
            "External operator packet",
            "External collection job packet",
            "External collection machine bootstrap",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "External operator release bundle",
            "Reviewer response packet",
            "17/21",
        ],
        "final_audit": [
            "External config materialization plan",
            "Planner-edge policy audit",
            "Failure-memory adaptation audit",
            "Local model release card",
            "External analysis plan",
            "External platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External fidelity acceptance draft",
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "cache-independent",
            "fidelity materializer checkout self-test",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "External collection preflight self-test",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "ManiSkill render machine qualification packet",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "render resource sweep",
            "ManiSkill pilot runtime liveness audit",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "External config manifest packet",
            "External rollout evidence packet",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty video directories",
            "non-MP4-like video artifacts",
            "External ablation collection packet",
            "External evidence intake ledger",
            "External precollection manifest draft",
            "External precollection freeze receipt",
            "External precollection freeze receipt self-test",
            "External postcollection evidence seal",
            "External postcollection evidence seal self-test",
            "External postcollection seal consistency gate",
            "External postcollection seal consistency self-test",
            "External method implementation packet",
            "External method config materialization",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "External manifest builder self-test",
            "External full-pipeline evidence self-test",
            "External operator packet",
            "External collection job packet",
            "External collection machine bootstrap",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "External operator release bundle",
            "Reviewer response packet",
            "Haonan/Yilun outreach package",
            "17 satisfied, 4 blocking external gaps",
        ],
        "readiness_decision": [
            "guarded config materialization plan",
            "planner-edge policy audit",
            "failure-memory adaptation audit",
            "local model release card",
            "external analysis plan",
            "external platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external fidelity acceptance draft",
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "fidelity acceptance materializer",
            "cache-independent",
            "fidelity materializer checkout self-test",
            "external backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "External collection preflight self-test",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "external runner backend probe self-test",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "external pilot smoke packet",
            "ManiSkill render-video preflight",
            "ManiSkill render machine qualification packet",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "render resource sweep",
            "ManiSkill pilot runtime liveness audit",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "external config manifest packet",
            "external rollout evidence packet",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty video directories",
            "non-MP4-like video artifacts",
            "external ablation collection packet",
            "external evidence intake ledger",
            "external precollection manifest draft",
            "external precollection freeze receipt",
            "external precollection freeze receipt self-test",
            "external postcollection evidence seal",
            "external postcollection evidence seal self-test",
            "external postcollection seal consistency gate",
            "external postcollection seal consistency self-test",
            "external method implementation packet",
            "external method config materialization",
            "adapter acceptance fixtures",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "External manifest builder self-test",
            "External full-pipeline evidence self-test",
            "generated external operator packet",
            "external collection job packet",
            "external collection machine bootstrap",
            "external collection runbook route-gate audit",
            "external operator handoff bundle",
            "external operator release bundle",
            "reviewer response packet",
            "outreach package now frames Haonan's role as fit/falsification advice",
            "ICLR main ready: no",
        ],
        "readiness_audit": [
            "External config materialization plan",
            "Planner-edge policy audit",
            "Failure-memory adaptation audit",
            "Local model release card",
            "External analysis plan",
            "External platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "External platform onboarding packet",
            "External fidelity provenance packet",
            "External fidelity acceptance draft",
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "Fidelity acceptance materialization plan",
            "cache-independent",
            "fidelity materializer checkout self-test",
            "External backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "External collection preflight self-test",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "External runner backend probe self-test",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "External pilot smoke packet",
            "ManiSkill render-video preflight",
            "ManiSkill render machine qualification packet",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "render resource sweep",
            "ManiSkill pilot runtime liveness audit",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "External config manifest packet",
            "External rollout evidence packet",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty video directories",
            "non-MP4-like video artifacts",
            "External ablation collection packet",
            "External evidence intake ledger",
            "External precollection manifest draft",
            "External precollection freeze receipt",
            "External precollection freeze receipt self-test",
            "External postcollection evidence seal",
            "External postcollection evidence seal self-test",
            "External postcollection seal consistency gate",
            "External postcollection seal consistency self-test",
            "External method implementation packet",
            "External method config materialization",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "External manifest builder self-test",
            "External full-pipeline evidence self-test",
            "External operator packet",
            "External collection job packet",
            "External collection machine bootstrap",
            "External collection runbook route-gate audit",
            "External operator handoff bundle",
            "External operator release bundle",
            "Reviewer response packet",
            "outreach PDFs now reflect the operator-packet/no-go stance",
            "17/21 objective requirements satisfied",
        ],
        "version_log": [
            "scripts/materialize_external_configs.py",
            "scripts/audit_planner_edge_policy.py",
            "scripts/audit_failure_memory_adaptation.py",
            "scripts/build_local_model_release.py",
            "scripts/build_external_analysis_plan.py",
            "scripts/probe_external_platform.py",
            "scripts/probe_maniskill_task_bindings.py",
            "scripts/probe_maniskill_env_smoke.py",
            "scripts/probe_maniskill_fidelity_metadata.py",
            "scripts/build_external_platform_onboarding.py",
            "scripts/build_external_fidelity_provenance_packet.py",
            "scripts/build_external_fidelity_acceptance_draft.py",
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "scripts/materialize_fidelity_acceptance.py",
            "cache-independent",
            "scripts/self_test_fidelity_acceptance_materializer.py",
            "fidelity materializer checkout self-test",
            "scripts/build_external_backend_integration_packet.py",
            "scripts/audit_maniskill_backend_readiness.py",
            "scripts/audit_maniskill_reference_collection_preflight.py",
            "synthetic MP4 writer check",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "scripts/self_test_external_runner_backend.py",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "scripts/build_external_pilot_smoke_packet.py",
            "scripts/audit_external_pilot_smoke.py",
            "scripts/audit_maniskill_render_video_preflight.py",
            "scripts/build_maniskill_render_machine_qualification.py",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "scripts/audit_maniskill_render_resource_sweep.py",
            "render resource sweep",
            "scripts/audit_maniskill_pilot_runtime_liveness.py",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "scripts/build_external_config_manifest_packet.py",
            "scripts/build_external_rollout_evidence_packet.py",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty video directories",
            "non-MP4-like video artifacts",
            "scripts/build_external_ablation_collection_packet.py",
            "scripts/build_external_evidence_intake_ledger.py",
            "scripts/build_external_precollection_manifest_draft.py",
            "scripts/build_external_precollection_freeze_receipt.py",
            "scripts/self_test_external_precollection_freeze_receipt.py",
            "scripts/build_external_postcollection_evidence_seal.py",
            "scripts/self_test_external_postcollection_evidence_seal.py",
            "scripts/audit_external_postcollection_seal_consistency.py",
            "scripts/self_test_external_postcollection_seal_consistency.py",
            "scripts/build_external_method_implementation_packet.py",
            "scripts/materialize_external_method_configs.py",
            "External method config materialization",
            "method_config_materialization_plan.md",
            "method_config_candidates.csv",
            "adapter_acceptance_fixtures.json",
            "method_reference_provenance.csv",
            "method_manifest_cutover_checklist.csv",
            "adapter acceptance fixtures",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest_assembly_checklist.csv",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "scripts/self_test_external_manifest_builder.py",
            "scripts/build_external_operator_packet.py",
            "current ManiSkill route gates",
            "scripts/build_external_collection_job_packet.py",
            "External collection job packet",
            "scripts/build_external_collection_machine_bootstrap.py",
            "External collection machine bootstrap",
            "scripts/build_external_operator_handoff_bundle.py",
            "scripts/build_external_operator_release_bundle.py",
            "External operator release bundle",
            "scripts/build_reviewer_response_packet.py",
            "reviewer response packet",
            "operator-packet/no-go stance",
        ],
        "child_status": [
            "external config materialization plan",
            "planner-edge policy audit",
            "failure-memory adaptation audit",
            "local model release card",
            "external analysis plan",
            "external platform probe",
            "ManiSkill task binding probe",
            "ManiSkill env smoke probe",
            "ManiSkill fidelity metadata probe",
            "external platform onboarding packet",
            "external fidelity provenance packet",
            "external fidelity acceptance draft",
            "strict fidelity acceptance provenance gate",
            "fidelity acceptance promotion checklist",
            "fidelity acceptance materializer",
            "cache-independent",
            "fidelity materializer checkout self-test",
            "external backend integration packet",
            "ManiSkill reference backend readiness audit",
            "ManiSkill reference collection preflight audit",
            "External collection preflight self-test",
            "MP4 writer path",
            "state-shaped arrays cannot masquerade as render videos",
            "explicit render-backend/shader controls",
            "external runner backend probe self-test",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "external pilot smoke packet",
            "ManiSkill render-video preflight",
            "ManiSkill render machine qualification packet",
            "renderer-failure classifier",
            "render/pilot progress markers",
            "timeout diagnosis retest",
            "renderer profile matrix",
            "render resource sweep",
            "ManiSkill pilot runtime liveness audit",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "external config manifest packet",
            "external rollout evidence packet",
            "strict MP4 video evidence gate",
            "strict full-method coverage gate",
            "strict rollout sample-count gate",
            "strict paired-panel gate",
            "strict rollout uniqueness gate",
            "strict task-config hash gate",
            "strict policy/config hash gate",
            "empty-video-directory",
            "non-MP4-like",
            "external ablation collection packet",
            "external evidence intake ledger",
            "external precollection manifest draft",
            "external precollection freeze receipt",
            "external precollection freeze receipt self-test",
            "external postcollection evidence seal",
            "external postcollection evidence seal self-test",
            "external postcollection seal consistency gate",
            "external postcollection seal consistency self-test",
            "external method implementation packet",
            "external method config materialization",
            "adapter acceptance fixtures",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "manifest assembly checklist",
            "strict manifest promotion gate",
            "External manifest builder self-test",
            "external operator packet",
            "External collection job packet",
            "external collection machine bootstrap",
            "external collection runbook route-gate audit",
            "external operator handoff bundle",
            "External operator release bundle",
            "reviewer response packet",
            "operator-packet-aligned Haonan/Yilun outreach package",
        ],
        "outreach": [
            "results/external_operator_packet.md",
            "External collection job packet",
            "External collection machine bootstrap",
            "External operator release bundle",
            "ManiSkill fidelity metadata probe",
            "fidelity acceptance materializer",
            "External method config materialization",
            "reference-adapter provenance catalog",
            "method manifest cutover checklist",
            "strict reference-adapter rejection gate",
            "strict independent method provenance gate",
            "strict checkpoint/config artifact gate",
            "strict fairness-contract binding gate",
            "strict manifest promotion gate",
            "manifest assembly checklist",
            "do not frame Haonan as responsible for supplying the missing proof",
            "independent validation protocol/operator packet",
            "reviewer response packet",
            "ManiSkill render-video preflight",
            "renderer-failure classifier",
            "timeout diagnosis retest",
            "render resource sweep",
            "ManiSkill render machine qualification packet",
            "reset-timeout triage sidecar",
            "backend reset substage markers",
            "render failure remediation packet",
            "diagnostic sidecar rejected before JSONL write",
            "External ablation collection packet",
            "External evidence intake ledger",
            "External precollection manifest draft",
            "External precollection freeze receipt",
            "External precollection freeze receipt self-test",
            "External postcollection evidence seal",
            "External postcollection evidence seal self-test",
            "External postcollection seal consistency gate",
            "External postcollection seal consistency self-test",
            "strict MP4 video evidence gate",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
            "diagnostic sidecar rejected before JSONL write",
        ],
        "reviewer": [
            "Not evidence: `true`.",
            "adaptive physical world/action models for skill seams",
            "failure-memory adaptation audit",
            "do not list many papers",
            "not for them to be responsible for supplying the missing proof",
            "does not change the current STRONG_REVISE decision",
            "Close all four blocking external requirements",
            "render resource sweep",
            "strict fidelity acceptance provenance gate",
            "official video write guard",
            "official JSONL write guard",
            "atomic official evidence promotion",
        ],
    }
    for name, terms in required_terms_by_file.items():
        ok, missing = contains_all(texts[name], terms)
        add_check(checks, f"{name}_current_visible_contribution_terms", ok, f"missing={missing}")

    pdf_metadata_files = ("README", "final_audit", "readiness_audit", "child_status")
    missing_sha_files = [name for name in pdf_metadata_files if canonical_pdf_sha not in texts[name]]
    size_variants = [
        f"PDF size: `{canonical_pdf_size}` bytes.",
        f"PDF size: {canonical_pdf_size} bytes",
    ]
    missing_size_files = [
        name for name in pdf_metadata_files if not any(size_text in texts[name] for size_text in size_variants)
    ]
    add_check(
        checks,
        "public_pdf_metadata_matches_canonical_artifact",
        canonical_pdf_exists and not missing_sha_files and not missing_size_files,
        f"sha={canonical_pdf_sha or '<missing>'}, size={canonical_pdf_size}, missing_sha={missing_sha_files}, missing_size={missing_size_files}",
    )

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
        "This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, the local planner-edge policy audit, the failure-memory adaptation audit, the local model release card, guarded external config materialization, the external config manifest packet, the external rollout evidence packet, the strict MP4 video evidence gate, the strict full-method coverage gate, the strict rollout sample-count gate, the strict paired-panel gate, the strict rollout uniqueness gate, confidence-gated external rollout statistics, the final rollout confidence summary gate, the strict task-config hash gate, the strict policy/config hash gate, the external ablation collection packet, the external evidence intake ledger, the External precollection manifest draft, the External precollection freeze receipt, the External precollection freeze receipt self-test, the External postcollection evidence seal, the External postcollection evidence seal self-test, the External postcollection seal consistency gate, the External postcollection seal consistency self-test, the locked external analysis plan, the external platform probe, the ManiSkill task binding probe, the ManiSkill env smoke probe, the external platform onboarding packet, the external fidelity provenance packet, the external fidelity acceptance draft, the strict fidelity acceptance provenance gate, the fidelity acceptance materializer, the external backend integration packet, the ManiSkill reference backend readiness audit with MP4 writer path, state-shaped array video guard, and explicit render-backend/shader controls, the ManiSkill reference collection preflight audit, the External collection preflight self-test with tracked reference-route readiness after accepted fidelity, the external runner backend probe self-test, the official video write guard, the official JSONL write guard, diagnostic sidecar rejected before JSONL write tracking, atomic official evidence promotion, the external pilot smoke packet, the ManiSkill render-video preflight, renderer-failure classifier, timeout diagnosis retest, renderer profile matrix, render resource sweep, ManiSkill render machine qualification packet, ManiSkill render machine qualification self-test, render failure remediation packet, ManiSkill pilot runtime liveness audit, reset-timeout triage sidecar, and backend reset substage markers, the external method implementation packet, External method config materialization, prepared task-config binding in the config evidence self-test, tracked candidate method-config binding in the adapter evidence self-test, adapter acceptance fixtures, the reference-adapter provenance catalog, the method manifest cutover checklist, the External adapter scaffold guard self-test, the strict reference-adapter rejection gate, the strict independent method provenance gate, the strict checkpoint/config artifact gate, the strict fairness-contract binding gate, the manifest assembly checklist, the External manifest builder self-test, the External rollout validator self-test, the External full-pipeline evidence self-test, the no-go operator packet, the External collection job packet, the External collection machine bootstrap, the external collection runbook route-gate audit, the no-evidence operator handoff bundle, the reviewer response packet, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.",
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

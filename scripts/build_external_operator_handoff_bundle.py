from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

OUT_JSON = RESULTS / "external_operator_handoff_bundle.json"
OUT_MD = RESULTS / "external_operator_handoff_bundle.md"

FORBIDDEN_PATH_PARTS = {
    "external_validation/local_dry_run/",
    "external_validation/logs/",
    "external_validation/videos/",
    "external_validation/checkpoints/",
    "external_validation/manifest.json",
    "placeholder_not_external_evidence",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def require_payload(path: Path, version: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def add_file(files: dict[str, str], category: str, path: Path) -> None:
    files[rel(path)] = category


def add_glob(files: dict[str, str], category: str, folder: Path, pattern: str) -> None:
    for path in sorted(folder.glob(pattern)):
        if path.is_file():
            add_file(files, category, path)


def build_file_manifest() -> dict[str, str]:
    files: dict[str, str] = {}

    for path in (
        ROOT / "README.md",
        DOCS / "independent_validation_protocol.md",
        DOCS / "submission_readiness_decision.md",
        DOCS / "reproducibility_checklist.md",
        DOCS / "haonan_yilun_outreach_package.md",
        EXTERNAL / "README.md",
        EXTERNAL / "collection_runbook.md",
        EXTERNAL / "operator_record_sheet.csv",
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
        EXTERNAL / "maniskill_task_bindings.json",
        EXTERNAL / "platform_qualification_checklist.md",
        EXTERNAL / "fidelity_acceptance_template.json",
        EXTERNAL / "log_schema_v1.json",
        EXTERNAL / "statistical_analysis_plan.json",
        EXTERNAL / "statistical_analysis_plan.md",
        EXTERNAL / "platform_onboarding_packet.json",
        EXTERNAL / "platform_onboarding_packet.md",
        EXTERNAL / "fidelity_provenance_packet.json",
        EXTERNAL / "fidelity_provenance_packet.md",
        EXTERNAL / "fidelity_provenance_work_orders.csv",
        EXTERNAL / "fidelity_acceptance_draft.json",
        EXTERNAL / "fidelity_acceptance_draft.md",
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
        EXTERNAL / "evidence_intake_ledger.json",
        EXTERNAL / "evidence_intake_ledger.md",
        EXTERNAL / "evidence_intake_ledger.csv",
        EXTERNAL / "precollection_freeze_receipt.json",
        EXTERNAL / "precollection_freeze_receipt.md",
        EXTERNAL / "precollection_freeze_receipt.csv",
        EXTERNAL / "postcollection_evidence_seal.json",
        EXTERNAL / "postcollection_evidence_seal.md",
        EXTERNAL / "postcollection_evidence_seal.csv",
        EXTERNAL / "pilot_smoke_packet.json",
        EXTERNAL / "pilot_smoke_packet.md",
        EXTERNAL / "pilot_smoke_work_orders.csv",
        EXTERNAL / "render_resource_sweep_work_orders.csv",
        EXTERNAL / "render_machine_qualification_packet.md",
        EXTERNAL / "collection_job_packet.json",
        EXTERNAL / "collection_job_packet.md",
        EXTERNAL / "collection_job_commands.ps1",
        EXTERNAL / "collection_job_checklist.csv",
        EXTERNAL / "method_implementation_packet.json",
        EXTERNAL / "method_implementation_packet.md",
        EXTERNAL / "method_implementation_work_orders.csv",
        EXTERNAL / "method_reference_provenance.csv",
        EXTERNAL / "method_manifest_cutover_checklist.csv",
        EXTERNAL / "method_manifest_cutover_checklist.md",
        EXTERNAL / "adapter_acceptance_fixtures.json",
        EXTERNAL / "adapter_acceptance_fixtures.md",
        EXTERNAL / "adapter_acceptance_fixtures.csv",
        EXTERNAL / "manifest_assembly_checklist.csv",
        EXTERNAL / "manifest_precollection_draft.json",
        EXTERNAL / "manifest_precollection_draft.md",
        EXTERNAL / "config_schema_v1.json",
        EXTERNAL / "configs" / "README.md",
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        EXTERNAL / "baseline_implementation_contract.md",
        EXTERNAL / "baseline_implementation_matrix.csv",
        EXTERNAL / "baseline_adapter_scaffold.md",
        EXTERNAL / "baselines" / "README.md",
        EXTERNAL / "reference_adapter_report.md",
        EXTERNAL / "runner" / "README.md",
        EXTERNAL / "runner" / "backend_contract.py",
        EXTERNAL / "runner" / "maniskill_reference_backend.py",
        EXTERNAL / "runner" / "real_collection_runner.py",
    ):
        add_file(files, "operator_facing_input", path)

    for path in (
        SCRIPTS / "build_external_operator_handoff_bundle.py",
        SCRIPTS / "build_external_operator_packet.py",
        SCRIPTS / "build_external_acquisition_packet.py",
        SCRIPTS / "build_external_analysis_plan.py",
        SCRIPTS / "build_external_platform_onboarding.py",
        SCRIPTS / "probe_external_platform.py",
        SCRIPTS / "probe_maniskill_task_bindings.py",
        SCRIPTS / "probe_maniskill_env_smoke.py",
        SCRIPTS / "probe_maniskill_fidelity_metadata.py",
        SCRIPTS / "build_external_fidelity_provenance_packet.py",
        SCRIPTS / "build_external_fidelity_acceptance_draft.py",
        SCRIPTS / "materialize_fidelity_acceptance.py",
        SCRIPTS / "build_external_backend_integration_packet.py",
        SCRIPTS / "build_external_config_manifest_packet.py",
        SCRIPTS / "build_external_rollout_evidence_packet.py",
        SCRIPTS / "build_external_ablation_collection_packet.py",
        SCRIPTS / "build_external_evidence_intake_ledger.py",
        SCRIPTS / "build_external_precollection_freeze_receipt.py",
        SCRIPTS / "build_external_postcollection_evidence_seal.py",
        SCRIPTS / "audit_external_postcollection_seal_consistency.py",
        SCRIPTS / "audit_external_pilot_smoke.py",
        SCRIPTS / "build_external_pilot_smoke_packet.py",
        SCRIPTS / "audit_maniskill_render_video_preflight.py",
        SCRIPTS / "audit_maniskill_render_resource_sweep.py",
        SCRIPTS / "audit_maniskill_pilot_runtime_liveness.py",
        SCRIPTS / "build_maniskill_render_machine_qualification.py",
        SCRIPTS / "build_external_collection_job_packet.py",
        SCRIPTS / "build_external_method_implementation_packet.py",
        SCRIPTS / "materialize_external_configs.py",
        SCRIPTS / "audit_external_backend_contract.py",
        SCRIPTS / "audit_maniskill_backend_readiness.py",
        SCRIPTS / "audit_maniskill_reference_collection_preflight.py",
        SCRIPTS / "audit_external_collection_readiness.py",
        SCRIPTS / "audit_external_fidelity_acceptance.py",
        SCRIPTS / "build_external_manifest.py",
        SCRIPTS / "self_test_external_manifest_builder.py",
        SCRIPTS / "build_external_precollection_manifest_draft.py",
        SCRIPTS / "audit_external_release_package.py",
        SCRIPTS / "validate_external_configs.py",
        SCRIPTS / "validate_external_adapters.py",
        SCRIPTS / "validate_external_rollouts.py",
        SCRIPTS / "audit_external_pairing_integrity.py",
        SCRIPTS / "audit_external_evidence.py",
    ):
        add_file(files, "operator_command_source", path)

    for path in (
        RESULTS / "external_operator_packet.json",
        RESULTS / "external_operator_packet.md",
        RESULTS / "external_acquisition_packet.json",
        RESULTS / "external_acquisition_packet.md",
        RESULTS / "external_collection_plan.json",
        RESULTS / "external_collection_plan.md",
        RESULTS / "external_analysis_plan_audit.json",
        RESULTS / "external_analysis_plan_audit.md",
        RESULTS / "external_platform_probe.json",
        RESULTS / "external_platform_probe.md",
        RESULTS / "maniskill_task_binding_probe.json",
        RESULTS / "maniskill_task_binding_probe.md",
        RESULTS / "maniskill_env_smoke_probe.json",
        RESULTS / "maniskill_env_smoke_probe.md",
        RESULTS / "maniskill_fidelity_metadata_probe.json",
        RESULTS / "maniskill_fidelity_metadata_probe.md",
        RESULTS / "external_platform_onboarding_audit.json",
        RESULTS / "external_platform_onboarding_audit.md",
        RESULTS / "external_fidelity_provenance_audit.json",
        RESULTS / "external_fidelity_provenance_audit.md",
        RESULTS / "external_fidelity_acceptance_draft_audit.json",
        RESULTS / "external_fidelity_acceptance_draft_audit.md",
        RESULTS / "fidelity_acceptance_materialization_plan.json",
        RESULTS / "fidelity_acceptance_materialization_plan.md",
        RESULTS / "external_backend_integration_audit.json",
        RESULTS / "external_backend_integration_audit.md",
        RESULTS / "external_config_manifest_audit.json",
        RESULTS / "external_config_manifest_audit.md",
        RESULTS / "external_rollout_evidence_audit.json",
        RESULTS / "external_rollout_evidence_audit.md",
        RESULTS / "external_ablation_collection_audit.json",
        RESULTS / "external_ablation_collection_audit.md",
        RESULTS / "external_evidence_intake_ledger_audit.json",
        RESULTS / "external_evidence_intake_ledger_audit.md",
        RESULTS / "external_precollection_freeze_receipt_audit.json",
        RESULTS / "external_precollection_freeze_receipt_audit.md",
        RESULTS / "external_postcollection_evidence_seal_audit.json",
        RESULTS / "external_postcollection_evidence_seal_audit.md",
        RESULTS / "external_postcollection_seal_consistency_audit.json",
        RESULTS / "external_postcollection_seal_consistency_audit.md",
        RESULTS / "external_pilot_smoke_audit.json",
        RESULTS / "external_pilot_smoke_audit.md",
        RESULTS / "external_pilot_smoke_packet_audit.json",
        RESULTS / "external_pilot_smoke_packet_audit.md",
        RESULTS / "maniskill_render_video_preflight_audit.json",
        RESULTS / "maniskill_render_video_preflight_audit.md",
        RESULTS / "maniskill_render_resource_sweep.json",
        RESULTS / "maniskill_render_resource_sweep.md",
        RESULTS / "maniskill_pilot_runtime_liveness_audit.json",
        RESULTS / "maniskill_pilot_runtime_liveness_audit.md",
        RESULTS / "maniskill_render_machine_qualification.json",
        RESULTS / "maniskill_render_machine_qualification.md",
        RESULTS / "external_collection_job_packet_audit.json",
        RESULTS / "external_collection_job_packet_audit.md",
        RESULTS / "external_method_implementation_audit.json",
        RESULTS / "external_method_implementation_audit.md",
        RESULTS / "independent_validation_route_audit.json",
        RESULTS / "independent_validation_route_audit.md",
        RESULTS / "external_blind_eval_audit.json",
        RESULTS / "external_blind_eval_audit.md",
        RESULTS / "external_runbook_audit.json",
        RESULTS / "external_runbook_audit.md",
        RESULTS / "external_runner_harness_audit.json",
        RESULTS / "external_runner_harness_audit.md",
        RESULTS / "external_backend_contract_audit.json",
        RESULTS / "external_backend_contract_audit.md",
        RESULTS / "maniskill_backend_readiness_audit.json",
        RESULTS / "maniskill_backend_readiness_audit.md",
        RESULTS / "maniskill_reference_collection_preflight_audit.json",
        RESULTS / "maniskill_reference_collection_preflight_audit.md",
        RESULTS / "external_collection_readiness_audit.json",
        RESULTS / "external_collection_readiness_audit.md",
        RESULTS / "external_config_template_audit.json",
        RESULTS / "external_config_template_audit.md",
        RESULTS / "external_config_materialization_plan.json",
        RESULTS / "external_config_materialization_plan.md",
        RESULTS / "external_fidelity_acceptance_audit.json",
        RESULTS / "external_fidelity_acceptance_audit.md",
        RESULTS / "external_baseline_contract_audit.json",
        RESULTS / "external_baseline_contract_audit.md",
        RESULTS / "external_adapter_scaffold_audit.json",
        RESULTS / "external_adapter_scaffold_audit.md",
        RESULTS / "external_reference_adapter_audit.json",
        RESULTS / "external_reference_adapter_audit.md",
        RESULTS / "external_adapter_contract_audit.json",
        RESULTS / "external_adapter_contract_audit.md",
        RESULTS / "external_evidence_preflight.json",
        RESULTS / "external_evidence_preflight.md",
        RESULTS / "external_release_package_audit.json",
        RESULTS / "external_release_package_audit.md",
        RESULTS / "external_manifest_builder_self_test.json",
        RESULTS / "external_manifest_builder_self_test.md",
        RESULTS / "external_precollection_manifest_draft_audit.json",
        RESULTS / "external_precollection_manifest_draft_audit.md",
        RESULTS / "external_pairing_integrity_audit.json",
        RESULTS / "external_pairing_integrity_audit.md",
        RESULTS / "external_execution_readiness_audit.json",
        RESULTS / "external_execution_readiness_audit.md",
    ):
        add_file(files, "generated_non_evidence_report", path)

    add_glob(files, "task_card", EXTERNAL / "task_cards", "*.md")
    add_glob(files, "config_template", EXTERNAL / "config_templates", "*.json")
    add_glob(files, "prepared_config_input", EXTERNAL / "configs", "*.json")
    add_glob(files, "baseline_spec", EXTERNAL / "baseline_specs", "*.json")
    add_glob(files, "runner_backend_template", EXTERNAL / "runner" / "backend_templates", "*.py")
    add_glob(files, "reference_adapter", EXTERNAL / "baselines", "*/README.md")
    add_glob(files, "reference_adapter", EXTERNAL / "baselines", "*/adapter.py")
    add_glob(files, "reference_adapter", EXTERNAL / "baselines", "*/adapter_template.py")
    add_glob(files, "reference_adapter", EXTERNAL / "baselines", "*/adapter_metadata.json")
    add_glob(files, "reference_adapter", EXTERNAL / "baselines", "*/reference_adapter_metadata.json")

    return dict(sorted(files.items()))


def file_records(files: dict[str, str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path_text, category in files.items():
        path = ROOT / path_text
        records.append(
            {
                "path": path_text,
                "category": category,
                "bytes": path.stat().st_size if path.exists() else None,
                "sha256": sha256(path) if path.exists() else None,
                "exists": path.exists(),
            }
        )
    return records


def forbidden_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        lowered = path.lower()
        for forbidden in FORBIDDEN_PATH_PARTS:
            if forbidden.lower() in lowered:
                hits.append(path)
                break
    return sorted(set(hits))


def build_payload() -> dict[str, Any]:
    operator = require_payload(RESULTS / "external_operator_packet.json", "external_operator_packet_v1")
    acquisition = require_payload(RESULTS / "external_acquisition_packet.json", "external_acquisition_packet_v1")
    preflight = require_payload(RESULTS / "external_evidence_preflight.json", "external_evidence_preflight_v1")
    release = require_payload(RESULTS / "external_release_package_audit.json", "external_release_package_audit_v1")
    pairing = require_payload(RESULTS / "external_pairing_integrity_audit.json", "external_pairing_integrity_audit_v1")
    analysis = require_payload(RESULTS / "external_analysis_plan_audit.json", "external_analysis_plan_audit_v1")
    platform_probe = require_payload(RESULTS / "external_platform_probe.json", "external_platform_probe_v1")
    task_binding_probe = require_payload(RESULTS / "maniskill_task_binding_probe.json", "maniskill_task_binding_probe_v1")
    env_smoke_probe = require_payload(RESULTS / "maniskill_env_smoke_probe.json", "maniskill_env_smoke_probe_v1")
    fidelity_metadata_probe = require_payload(
        RESULTS / "maniskill_fidelity_metadata_probe.json",
        "maniskill_fidelity_metadata_probe_v1",
    )
    onboarding = require_payload(RESULTS / "external_platform_onboarding_audit.json", "external_platform_onboarding_audit_v1")
    fidelity_provenance = require_payload(RESULTS / "external_fidelity_provenance_audit.json", "external_fidelity_provenance_audit_v1")
    fidelity_draft = require_payload(RESULTS / "external_fidelity_acceptance_draft_audit.json", "external_fidelity_acceptance_draft_audit_v1")
    fidelity_materialization = require_payload(RESULTS / "fidelity_acceptance_materialization_plan.json", "fidelity_acceptance_materialization_plan_v1")
    backend_integration = require_payload(RESULTS / "external_backend_integration_audit.json", "external_backend_integration_audit_v1")
    maniskill_backend = require_payload(RESULTS / "maniskill_backend_readiness_audit.json", "maniskill_reference_backend_audit_v1")
    maniskill_preflight = require_payload(RESULTS / "maniskill_reference_collection_preflight_audit.json", "maniskill_reference_collection_preflight_audit_v1")
    config_manifest = require_payload(RESULTS / "external_config_manifest_audit.json", "external_config_manifest_audit_v1")
    rollout_evidence = require_payload(RESULTS / "external_rollout_evidence_audit.json", "external_rollout_evidence_audit_v1")
    ablation_packet = require_payload(RESULTS / "external_ablation_collection_audit.json", "external_ablation_collection_audit_v1")
    evidence_intake = require_payload(RESULTS / "external_evidence_intake_ledger_audit.json", "external_evidence_intake_ledger_v1")
    precollection_freeze = require_payload(
        RESULTS / "external_precollection_freeze_receipt_audit.json",
        "external_precollection_freeze_receipt_audit_v1",
    )
    postcollection_seal = require_payload(
        RESULTS / "external_postcollection_evidence_seal_audit.json",
        "external_postcollection_evidence_seal_audit_v1",
    )
    postcollection_consistency = require_payload(
        RESULTS / "external_postcollection_seal_consistency_audit.json",
        "external_postcollection_seal_consistency_audit_v1",
    )
    method_implementation = require_payload(RESULTS / "external_method_implementation_audit.json", "external_method_implementation_audit_v1")
    pilot_smoke = require_payload(RESULTS / "external_pilot_smoke_packet_audit.json", "external_pilot_smoke_packet_audit_v1")
    render_preflight = require_payload(RESULTS / "maniskill_render_video_preflight_audit.json", "maniskill_render_video_preflight_audit_v2")
    render_resource_sweep = require_payload(RESULTS / "maniskill_render_resource_sweep.json", "maniskill_render_resource_sweep_v1")
    pilot_runtime = require_payload(RESULTS / "maniskill_pilot_runtime_liveness_audit.json", "maniskill_pilot_runtime_liveness_audit_v1")
    render_machine = require_payload(RESULTS / "maniskill_render_machine_qualification.json", "maniskill_render_machine_qualification_v1")
    collection_job = require_payload(RESULTS / "external_collection_job_packet_audit.json", "external_collection_job_packet_audit_v1")
    precollection_manifest = require_payload(
        RESULTS / "external_precollection_manifest_draft_audit.json",
        "external_precollection_manifest_draft_audit_v1",
    )

    files = build_file_manifest()
    records = file_records(files)
    paths = [record["path"] for record in records]
    missing_files = sorted(record["path"] for record in records if not record["exists"])
    forbidden = forbidden_hits(paths)
    categories = sorted(set(files.values()))
    category_counts = {
        category: sum(1 for record in records if record["category"] == category)
        for category in categories
    }
    post_commands = operator.get("post_collection_strict_commands", []) or []
    operator_actions = operator.get("operator_actions", []) or []
    action_ids = {str(action.get("id", "")) for action in operator_actions}

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "operator_packet_is_no_go_non_evidence",
        operator.get("passed") is True
        and operator.get("not_external_evidence") is True
        and operator.get("start_state") == "DO_NOT_COLLECT_YET"
        and operator.get("strict_evidence_ready") is False,
        (
            f"start_state={operator.get('start_state')!r}, "
            f"strict_evidence_ready={operator.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "acquisition_maps_all_remaining_blockers",
        acquisition.get("passed") is True
        and acquisition.get("not_external_evidence") is True
        and len(acquisition.get("missing_requirements", []) or []) == 4,
        f"missing_requirements={len(acquisition.get('missing_requirements', []) or [])}",
    )
    add_check(
        checks,
        "strict_evidence_gates_remain_fail_closed",
        analysis.get("strict_evidence_ready") is False
        and onboarding.get("strict_evidence_ready") is False
        and maniskill_backend.get("official_collection_ready") is False
        and maniskill_backend.get("strict_external_evidence_ready") is False
        and render_preflight.get("strict_external_evidence_ready") is False
        and preflight.get("evidence_ready") is False
        and release.get("release_package_ready") is False
        and pairing.get("pairing_ready") is False,
        (
            f"analysis={analysis.get('strict_evidence_ready')!r}, "
            f"onboarding={onboarding.get('strict_evidence_ready')!r}, "
            f"reference_backend_official={maniskill_backend.get('official_collection_ready')!r}, "
            f"preflight={preflight.get('evidence_ready')!r}, "
            f"release={release.get('release_package_ready')!r}, "
            f"pairing={pairing.get('pairing_ready')!r}"
        ),
    )
    add_check(
        checks,
        "bundle_files_exist",
        not missing_files,
        f"missing={missing_files[:10]}, total_missing={len(missing_files)}",
    )
    add_check(
        checks,
        "bundle_excludes_rollout_evidence_artifacts",
        not forbidden,
        f"forbidden_included={forbidden}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )
    collection_job_checks = {check.get("name"): check.get("passed") for check in collection_job.get("checks", []) or []}
    add_check(
        checks,
        "external_collection_job_packet_included",
        collection_job.get("passed") is True
        and collection_job.get("not_external_evidence") is True
        and collection_job.get("strict_external_evidence_ready") is False
        and collection_job.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and int(collection_job.get("remaining_submission_blocker_count", 0) or 0) == 4
        and int(len(collection_job.get("job_steps", []) or [])) >= 17
        and collection_job_checks.get("command_sequence_covers_full_external_validation_route") is True
        and collection_job_checks.get("official_collection_commands_guarded") is True
        and collection_job_checks.get("no_real_manifest_written") is True
        and "external_validation/collection_job_packet.json" in paths
        and "external_validation/collection_job_packet.md" in paths
        and "external_validation/collection_job_commands.ps1" in paths
        and "external_validation/collection_job_checklist.csv" in paths
        and "results/external_collection_job_packet_audit.json" in paths
        and "results/external_collection_job_packet_audit.md" in paths
        and "scripts/build_external_collection_job_packet.py" in paths,
        (
            f"job_state={collection_job.get('job_state')!r}, "
            f"steps={len(collection_job.get('job_steps', []) or [])}, "
            f"blockers={collection_job.get('remaining_submission_blocker_count')!r}"
        ),
    )
    precollection_checks = {check.get("name"): check.get("passed") for check in precollection_manifest.get("checks", []) or []}
    add_check(
        checks,
        "precollection_manifest_draft_included",
        precollection_manifest.get("passed") is True
        and precollection_manifest.get("not_external_evidence") is True
        and precollection_manifest.get("draft_ready") is True
        and precollection_manifest.get("strict_external_evidence_ready") is False
        and precollection_manifest.get("strict_config_evidence_ready") is False
        and precollection_manifest.get("official_manifest_exists") is False
        and int(precollection_manifest.get("prepared_config_count", 0) or 0) >= 4
        and int(precollection_manifest.get("method_gap_count", 0) or 0) >= 11
        and int(precollection_manifest.get("missing_rollout_artifact_count", 0) or 0) >= 8
        and precollection_checks.get("draft_marked_non_evidence_and_fail_closed") is True
        and "external_validation/manifest_precollection_draft.json" in paths
        and "external_validation/manifest_precollection_draft.md" in paths
        and "results/external_precollection_manifest_draft_audit.json" in paths
        and "scripts/build_external_precollection_manifest_draft.py" in paths,
        (
            f"configs={precollection_manifest.get('prepared_config_count')!r}, "
            f"method_gaps={precollection_manifest.get('method_gap_count')!r}, "
            f"rollout_gaps={precollection_manifest.get('missing_rollout_artifact_count')!r}"
        ),
    )
    add_check(
        checks,
        "handoff_has_task_config_and_baseline_assets",
        category_counts.get("task_card", 0) >= 4
        and category_counts.get("config_template", 0) >= 4
        and category_counts.get("prepared_config_input", 0) >= 4
        and category_counts.get("baseline_spec", 0) >= 12
        and category_counts.get("reference_adapter", 0) >= 40,
        f"category_counts={category_counts}",
    )
    add_check(
        checks,
        "analysis_plan_included",
        analysis.get("passed") is True
        and analysis.get("not_external_evidence") is True
        and analysis.get("analysis_plan_ready") is True
        and analysis.get("strict_evidence_ready") is False
        and "external_validation/statistical_analysis_plan.json" in paths
        and "external_validation/statistical_analysis_plan.md" in paths
        and "results/external_analysis_plan_audit.json" in paths
        and "scripts/build_external_analysis_plan.py" in paths,
        (
            f"analysis_plan_ready={analysis.get('analysis_plan_ready')!r}, "
            f"strict_evidence_ready={analysis.get('strict_evidence_ready')!r}"
        ),
    )
    onboarding_checks = {check.get("name"): check.get("passed") for check in onboarding.get("checks", []) or []}
    add_check(
        checks,
        "platform_onboarding_included",
        onboarding.get("passed") is True
        and onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False
        and platform_probe.get("passed") is True
        and platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_external_evidence_ready") is False
        and task_binding_probe.get("passed") is True
        and task_binding_probe.get("not_external_evidence") is True
        and task_binding_probe.get("task_binding_probe_ready") is True
        and task_binding_probe.get("accepted_task_binding_ready") is False
        and task_binding_probe.get("strict_external_evidence_ready") is False
        and env_smoke_probe.get("passed") is True
        and env_smoke_probe.get("not_external_evidence") is True
        and env_smoke_probe.get("env_smoke_probe_ready") is True
        and env_smoke_probe.get("accepted_fidelity_ready") is False
        and env_smoke_probe.get("strict_external_evidence_ready") is False
        and fidelity_metadata_probe.get("passed") is True
        and fidelity_metadata_probe.get("not_external_evidence") is True
        and fidelity_metadata_probe.get("metadata_probe_ready") is True
        and fidelity_metadata_probe.get("accepted_fidelity_ready") is False
        and fidelity_metadata_probe.get("strict_external_evidence_ready") is False
        and onboarding_checks.get("primary_route_matches_independent_plan") is True
        and onboarding_checks.get("platform_provenance_fields_cover_fidelity_hashes_and_observations") is True
        and onboarding_checks.get("platform_probe_report_ready") is True
        and onboarding_checks.get("task_binding_probe_report_ready") is True
        and onboarding_checks.get("env_smoke_probe_report_ready") is True
        and "external_validation/maniskill_task_bindings.json" in paths
        and "results/external_platform_probe.json" in paths
        and "results/external_platform_probe.md" in paths
        and "results/maniskill_task_binding_probe.json" in paths
        and "results/maniskill_task_binding_probe.md" in paths
        and "results/maniskill_env_smoke_probe.json" in paths
        and "results/maniskill_env_smoke_probe.md" in paths
        and "results/maniskill_fidelity_metadata_probe.json" in paths
        and "results/maniskill_fidelity_metadata_probe.md" in paths
        and "scripts/probe_external_platform.py" in paths
        and "scripts/probe_maniskill_task_bindings.py" in paths
        and "scripts/probe_maniskill_env_smoke.py" in paths
        and "scripts/probe_maniskill_fidelity_metadata.py" in paths
        and "external_validation/platform_onboarding_packet.json" in paths
        and "external_validation/platform_onboarding_packet.md" in paths
        and "results/external_platform_onboarding_audit.json" in paths
        and "scripts/build_external_platform_onboarding.py" in paths,
        (
            f"platform_onboarding_ready={onboarding.get('platform_onboarding_ready')!r}, "
            f"strict_evidence_ready={onboarding.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "fidelity_metadata_probe_included",
        fidelity_metadata_probe.get("passed") is True
        and fidelity_metadata_probe.get("not_external_evidence") is True
        and fidelity_metadata_probe.get("metadata_probe_ready") is True
        and fidelity_metadata_probe.get("accepted_fidelity_ready") is False
        and fidelity_metadata_probe.get("strict_fidelity_evidence_ready") is False
        and fidelity_metadata_probe.get("strict_external_evidence_ready") is False
        and "results/maniskill_fidelity_metadata_probe.json" in paths
        and "results/maniskill_fidelity_metadata_probe.md" in paths
        and "scripts/probe_maniskill_fidelity_metadata.py" in paths,
        (
            f"strict_metadata_ready={fidelity_metadata_probe.get('strict_metadata_ready')!r}, "
            f"primary_metadata_missing={fidelity_metadata_probe.get('primary_metadata_missing')!r}"
        ),
    )
    fidelity_provenance_checks = {check.get("name"): check.get("passed") for check in fidelity_provenance.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_provenance_packet_included",
        fidelity_provenance.get("passed") is True
        and fidelity_provenance.get("not_external_evidence") is True
        and fidelity_provenance.get("fidelity_provenance_packet_ready") is True
        and fidelity_provenance.get("strict_fidelity_evidence_ready") is False
        and fidelity_provenance.get("strict_external_evidence_ready") is False
        and fidelity_provenance_checks.get("work_orders_cover_fidelity_blockers") is True
        and fidelity_provenance_checks.get("strict_commands_cover_fidelity_manifest_collection_and_evidence") is True
        and "external_validation/fidelity_provenance_packet.json" in paths
        and "external_validation/fidelity_provenance_packet.md" in paths
        and "external_validation/fidelity_provenance_work_orders.csv" in paths
        and "results/external_fidelity_provenance_audit.json" in paths
        and "scripts/build_external_fidelity_provenance_packet.py" in paths,
        (
            f"fidelity_provenance_packet_ready={fidelity_provenance.get('fidelity_provenance_packet_ready')!r}, "
            f"strict_fidelity_evidence_ready={fidelity_provenance.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={fidelity_provenance.get('strict_external_evidence_ready')!r}"
        ),
    )
    fidelity_draft_checks = {check.get("name"): check.get("passed") for check in fidelity_draft.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_draft_included",
        fidelity_draft.get("passed") is True
        and fidelity_draft.get("not_external_evidence") is True
        and fidelity_draft.get("draft_ready") is True
        and fidelity_draft.get("acceptance_ready") is False
        and fidelity_draft.get("strict_fidelity_evidence_ready") is False
        and fidelity_draft.get("strict_external_evidence_ready") is False
        and fidelity_draft_checks.get("draft_is_non_evidence_and_fail_closed") is True
        and fidelity_draft_checks.get("candidate_hashes_prefilled") is True
        and fidelity_draft_checks.get("acceptance_gates_remain_unaccepted") is True
        and "external_validation/fidelity_acceptance_draft.json" in paths
        and "external_validation/fidelity_acceptance_draft.md" in paths
        and "results/external_fidelity_acceptance_draft_audit.json" in paths
        and "scripts/build_external_fidelity_acceptance_draft.py" in paths,
        (
            f"draft_ready={fidelity_draft.get('draft_ready')!r}, "
            f"remaining_operator_inputs={fidelity_draft.get('remaining_operator_input_count')!r}, "
            f"acceptance_ready={fidelity_draft.get('acceptance_ready')!r}"
        ),
    )
    fidelity_materialization_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_included",
        fidelity_materialization.get("passed") is True
        and fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False
        and fidelity_materialization_checks.get("operator_write_command_is_guarded") is True
        and "scripts/materialize_fidelity_acceptance.py" in paths
        and "results/fidelity_acceptance_materialization_plan.json" in paths
        and "results/fidelity_acceptance_materialization_plan.md" in paths,
        (
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}"
        ),
    )
    backend_integration_checks = {check.get("name"): check.get("passed") for check in backend_integration.get("checks", []) or []}
    add_check(
        checks,
        "backend_integration_packet_included",
        backend_integration.get("passed") is True
        and backend_integration.get("not_external_evidence") is True
        and backend_integration.get("backend_integration_packet_ready") is True
        and backend_integration.get("strict_backend_ready") is False
        and backend_integration.get("strict_evidence_ready") is False
        and backend_integration_checks.get("work_orders_cover_backend_to_manifest_path") is True
        and backend_integration_checks.get("collection_readiness_still_blocks_backend") is True
        and "external_validation/backend_integration_packet.json" in paths
        and "external_validation/backend_integration_packet.md" in paths
        and "external_validation/backend_integration_work_orders.csv" in paths
        and "results/external_backend_integration_audit.json" in paths
        and "scripts/build_external_backend_integration_packet.py" in paths,
        (
            f"backend_integration_packet_ready={backend_integration.get('backend_integration_packet_ready')!r}, "
            f"strict_backend_ready={backend_integration.get('strict_backend_ready')!r}"
        ),
    )
    maniskill_backend_checks = {check.get("name"): check.get("passed") for check in maniskill_backend.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_backend_included",
        maniskill_backend.get("passed") is True
        and maniskill_backend.get("not_external_evidence") is True
        and maniskill_backend.get("backend_contract_ready") is True
        and maniskill_backend.get("reference_backend_available") is True
        and maniskill_backend.get("video_writer_ready") is True
        and maniskill_backend.get("official_collection_ready") is False
        and maniskill_backend.get("strict_external_evidence_ready") is False
        and maniskill_backend_checks.get("official_collection_fail_closed_without_enable_flag") is True
        and maniskill_backend_checks.get("video_export_fail_closed_before_reset") is True
        and maniskill_backend_checks.get("synthetic_mp4_writer_passes") is True
        and "external_validation/runner/maniskill_reference_backend.py" in paths
        and "scripts/audit_maniskill_backend_readiness.py" in paths
        and "results/maniskill_backend_readiness_audit.json" in paths,
        (
            f"backend_contract_ready={maniskill_backend.get('backend_contract_ready')!r}, "
            f"video_writer_ready={maniskill_backend.get('video_writer_ready')!r}, "
            f"official_collection_ready={maniskill_backend.get('official_collection_ready')!r}"
        ),
    )
    maniskill_preflight_checks = {check.get("name"): check.get("passed") for check in maniskill_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_collection_preflight_included",
        maniskill_preflight.get("passed") is True
        and maniskill_preflight.get("not_external_evidence") is True
        and maniskill_preflight.get("reference_backend_contract_ready") is True
        and maniskill_preflight.get("collection_ready") is False
        and maniskill_preflight.get("strict_external_evidence_ready") is False
        and int(maniskill_preflight.get("collection_blocking_missing_count", 0) or 0) == 1
        and maniskill_preflight_checks.get("reference_backend_collection_preflight_reaches_fidelity_gate") is True
        and "scripts/audit_maniskill_reference_collection_preflight.py" in paths
        and "results/maniskill_reference_collection_preflight_audit.json" in paths,
        (
            f"contract_ready={maniskill_preflight.get('reference_backend_contract_ready')!r}, "
            f"collection_ready={maniskill_preflight.get('collection_ready')!r}, "
            f"blocking={maniskill_preflight.get('collection_blocking_missing')!r}"
        ),
    )
    method_checks = {check.get("name"): check.get("passed") for check in method_implementation.get("checks", []) or []}
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest.get("checks", []) or []}
    add_check(
        checks,
        "config_manifest_packet_included",
        config_manifest.get("passed") is True
        and config_manifest.get("not_external_evidence") is True
        and config_manifest.get("config_manifest_packet_ready") is True
        and config_manifest.get("strict_config_evidence_ready") is False
        and config_manifest.get("manifest_declared_config_ready") is False
        and config_manifest_checks.get("work_orders_cover_config_to_manifest_path") is True
        and config_manifest_checks.get("strict_commands_cover_config_manifest_release_and_evidence") is True
        and "external_validation/config_manifest_packet.json" in paths
        and "external_validation/config_manifest_packet.md" in paths
        and "external_validation/config_manifest_work_orders.csv" in paths
        and "results/external_config_manifest_audit.json" in paths
        and "scripts/build_external_config_manifest_packet.py" in paths,
        (
            f"config_manifest_packet_ready={config_manifest.get('config_manifest_packet_ready')!r}, "
            f"strict_config_evidence_ready={config_manifest.get('strict_config_evidence_ready')!r}, "
            f"manifest_declared_config_ready={config_manifest.get('manifest_declared_config_ready')!r}"
        ),
    )
    rollout_evidence_checks = {check.get("name"): check.get("passed") for check in rollout_evidence.get("checks", []) or []}
    add_check(
        checks,
        "rollout_evidence_packet_included",
        rollout_evidence.get("passed") is True
        and rollout_evidence.get("not_external_evidence") is True
        and rollout_evidence.get("rollout_evidence_packet_ready") is True
        and rollout_evidence.get("strict_rollout_evidence_ready") is False
        and rollout_evidence.get("strict_external_evidence_ready") is False
        and rollout_evidence_checks.get("task_work_orders_cover_all_planned_tasks") is True
        and rollout_evidence_checks.get("strict_commands_cover_collection_manifest_rollout_pairing_release_evidence") is True
        and "external_validation/rollout_evidence_packet.json" in paths
        and "external_validation/rollout_evidence_packet.md" in paths
        and "external_validation/rollout_evidence_work_orders.csv" in paths
        and "results/external_rollout_evidence_audit.json" in paths
        and "scripts/build_external_rollout_evidence_packet.py" in paths,
        (
            f"rollout_evidence_packet_ready={rollout_evidence.get('rollout_evidence_packet_ready')!r}, "
            f"strict_rollout_evidence_ready={rollout_evidence.get('strict_rollout_evidence_ready')!r}, "
            f"strict_external_evidence_ready={rollout_evidence.get('strict_external_evidence_ready')!r}"
        ),
    )
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_packet.get("checks", []) or []}
    add_check(
        checks,
        "ablation_collection_packet_included",
        ablation_packet.get("passed") is True
        and ablation_packet.get("not_external_evidence") is True
        and ablation_packet.get("strict_external_evidence_ready") is False
        and ablation_packet.get("manifest_ablation_evidence_ready") is False
        and int(ablation_packet.get("work_order_count", 0) or 0) == 5
        and int(ablation_packet.get("expected_ablation_records", 0) or 0) >= 600
        and ablation_checks.get("every_required_ablation_has_work_order") is True
        and ablation_checks.get("operator_commands_cover_collection_manifest_rollout_and_strict_evidence") is True
        and "external_validation/ablation_collection_packet.json" in paths
        and "external_validation/ablation_collection_packet.md" in paths
        and "external_validation/ablation_collection_work_orders.csv" in paths
        and "results/external_ablation_collection_audit.json" in paths
        and "scripts/build_external_ablation_collection_packet.py" in paths,
        (
            f"work_order_count={ablation_packet.get('work_order_count')!r}, "
            f"expected_ablation_records={ablation_packet.get('expected_ablation_records')!r}, "
            f"manifest_ablation_evidence_ready={ablation_packet.get('manifest_ablation_evidence_ready')!r}"
        ),
    )
    intake_checks = {check.get("name"): check.get("passed") for check in evidence_intake.get("checks", []) or []}
    add_check(
        checks,
        "evidence_intake_ledger_included",
        evidence_intake.get("passed") is True
        and evidence_intake.get("not_external_evidence") is True
        and evidence_intake.get("strict_external_evidence_ready") is False
        and int(evidence_intake.get("blocking_failure_count", 0) or 0) >= 30
        and evidence_intake.get("blocking_failure_count") == evidence_intake.get("mapped_failure_count")
        and not evidence_intake.get("unmapped_failures")
        and intake_checks.get("every_blocking_failure_is_mapped") is True
        and intake_checks.get("strict_command_spine_covers_final_evidence_path") is True
        and "external_validation/evidence_intake_ledger.json" in paths
        and "external_validation/evidence_intake_ledger.md" in paths
        and "external_validation/evidence_intake_ledger.csv" in paths
        and "results/external_evidence_intake_ledger_audit.json" in paths
        and "scripts/build_external_evidence_intake_ledger.py" in paths,
        (
            f"mapped={evidence_intake.get('mapped_failure_count')!r}/"
            f"{evidence_intake.get('blocking_failure_count')!r}, "
            f"groups={len(evidence_intake.get('closure_groups', []) or [])}"
        ),
    )
    freeze_checks = {check.get("name"): check.get("passed") for check in precollection_freeze.get("checks", []) or []}
    add_check(
        checks,
        "precollection_freeze_receipt_included",
        precollection_freeze.get("passed") is True
        and precollection_freeze.get("not_external_evidence") is True
        and precollection_freeze.get("strict_external_evidence_ready") is False
        and precollection_freeze.get("freeze_receipt_ready") is False
        and int(precollection_freeze.get("locked_artifact_count", 0) or 0) >= 25
        and freeze_checks.get("core_lock_artifacts_hashed") is True
        and freeze_checks.get("prepared_task_configs_hashed") is True
        and freeze_checks.get("strict_sequence_places_receipt_before_collection") is True
        and "external_validation/precollection_freeze_receipt.json" in paths
        and "external_validation/precollection_freeze_receipt.md" in paths
        and "external_validation/precollection_freeze_receipt.csv" in paths
        and "results/external_precollection_freeze_receipt_audit.json" in paths
        and "scripts/build_external_precollection_freeze_receipt.py" in paths,
        (
            f"locked_artifacts={precollection_freeze.get('locked_artifact_count')!r}, "
            f"freeze_receipt_ready={precollection_freeze.get('freeze_receipt_ready')!r}"
        ),
    )
    seal_checks = {check.get("name"): check.get("passed") for check in postcollection_seal.get("checks", []) or []}
    add_check(
        checks,
        "postcollection_evidence_seal_included",
        postcollection_seal.get("passed") is True
        and postcollection_seal.get("not_external_evidence") is True
        and postcollection_seal.get("strict_external_evidence_ready") is False
        and postcollection_seal.get("postcollection_seal_ready") is False
        and postcollection_seal.get("ready_for_manifest_promotion") is False
        and int(postcollection_seal.get("sealed_artifact_count", 0) or 0) >= 8
        and int(postcollection_seal.get("jsonl_record_count", 0) or 0) == 0
        and int(postcollection_seal.get("rollout_video_count", 0) or 0) == 0
        and seal_checks.get("seal_is_non_evidence_and_fail_closed") is True
        and seal_checks.get("strict_sequence_places_seal_after_collection_before_manifest") is True
        and "external_validation/postcollection_evidence_seal.json" in paths
        and "external_validation/postcollection_evidence_seal.md" in paths
        and "external_validation/postcollection_evidence_seal.csv" in paths
        and "results/external_postcollection_evidence_seal_audit.json" in paths
        and "scripts/build_external_postcollection_evidence_seal.py" in paths,
        (
            f"sealed_artifacts={postcollection_seal.get('sealed_artifact_count')!r}, "
            f"records={postcollection_seal.get('jsonl_record_count')!r}, "
            f"videos={postcollection_seal.get('rollout_video_count')!r}, "
            f"seal_ready={postcollection_seal.get('postcollection_seal_ready')!r}"
        ),
    )
    consistency_checks = {check.get("name"): check.get("passed") for check in postcollection_consistency.get("checks", []) or []}
    add_check(
        checks,
        "postcollection_seal_consistency_gate_included",
        postcollection_consistency.get("passed") is True
        and postcollection_consistency.get("not_external_evidence") is True
        and postcollection_consistency.get("strict_external_evidence_ready") is False
        and postcollection_consistency.get("seal_consistency_ready") is False
        and postcollection_consistency.get("ready_for_manifest_promotion") is False
        and int(postcollection_consistency.get("current_jsonl_record_count", 0) or 0) == 0
        and int(postcollection_consistency.get("current_rollout_video_count", 0) or 0) == 0
        and consistency_checks.get("sealed_hashes_recompute_without_drift") is True
        and consistency_checks.get("strict_sequence_places_consistency_after_seal_before_manifest") is True
        and "results/external_postcollection_seal_consistency_audit.json" in paths
        and "results/external_postcollection_seal_consistency_audit.md" in paths
        and "scripts/audit_external_postcollection_seal_consistency.py" in paths,
        (
            f"matched={postcollection_consistency.get('matched_hash_count')!r}, "
            f"records={postcollection_consistency.get('current_jsonl_record_count')!r}, "
            f"videos={postcollection_consistency.get('current_rollout_video_count')!r}, "
            f"consistency_ready={postcollection_consistency.get('seal_consistency_ready')!r}"
        ),
    )
    pilot_smoke_checks = {check.get("name"): check.get("passed") for check in pilot_smoke.get("checks", []) or []}
    add_check(
        checks,
        "pilot_smoke_packet_included",
        pilot_smoke.get("passed") is True
        and pilot_smoke.get("not_external_evidence") is True
        and pilot_smoke.get("pilot_smoke_packet_ready") is True
        and pilot_smoke.get("strict_evidence_ready") is False
        and pilot_smoke_checks.get("quarantine_dirs_are_separate_from_official_evidence") is True
        and pilot_smoke_checks.get("pilot_commands_preserve_gate_order") is True
        and "external_validation/pilot_smoke_packet.json" in paths
        and "external_validation/pilot_smoke_packet.md" in paths
        and "external_validation/pilot_smoke_work_orders.csv" in paths
        and "results/external_pilot_smoke_packet_audit.json" in paths
        and "scripts/build_external_pilot_smoke_packet.py" in paths
        and "scripts/audit_external_pilot_smoke.py" in paths,
        (
            f"pilot_smoke_packet_ready={pilot_smoke.get('pilot_smoke_packet_ready')!r}, "
            f"strict_evidence_ready={pilot_smoke.get('strict_evidence_ready')!r}"
        ),
    )
    render_preflight_checks = {check.get("name"): check.get("passed") for check in render_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_video_preflight_included",
        render_preflight.get("passed") is True
        and render_preflight.get("not_external_evidence") is True
        and render_preflight.get("strict_external_evidence_ready") is False
        and isinstance(render_preflight.get("render_video_ready"), bool)
        and int(render_preflight.get("env_count", 0) or 0) >= 1
        and render_preflight_checks.get("render_preflight_is_non_evidence") is True
        and render_preflight_checks.get("quarantine_paths_are_not_official_evidence") is True
        and render_preflight_checks.get("render_readiness_recorded_without_overclaim") is True
        and "scripts/audit_maniskill_render_video_preflight.py" in paths
        and "results/maniskill_render_video_preflight_audit.json" in paths
        and "results/maniskill_render_video_preflight_audit.md" in paths,
        (
            f"render_video_ready={render_preflight.get('render_video_ready')!r}, "
            f"env_count={render_preflight.get('env_count')!r}, "
            f"blocking={render_preflight.get('blocking_missing')!r}"
        ),
    )
    render_resource_checks = {check.get("name"): check.get("passed") for check in render_resource_sweep.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_resource_sweep_included",
        render_resource_sweep.get("passed") is True
        and render_resource_sweep.get("not_external_evidence") is True
        and render_resource_sweep.get("strict_external_evidence_ready") is False
        and render_resource_sweep.get("any_render_video_ready") is False
        and render_resource_sweep.get("descriptor_pool_failure_persists_at_minimum_resolution") is True
        and int(render_resource_sweep.get("record_count", 0) or 0) >= 3
        and "vulkan_descriptor_pool_exhaustion" in (render_resource_sweep.get("renderer_failure_classes", []) or [])
        and render_resource_checks.get("resource_sweep_is_non_evidence") is True
        and render_resource_checks.get("quarantine_paths_are_not_official_evidence") is True
        and "scripts/audit_maniskill_render_resource_sweep.py" in paths
        and "results/maniskill_render_resource_sweep.json" in paths
        and "results/maniskill_render_resource_sweep.md" in paths
        and "external_validation/render_resource_sweep_work_orders.csv" in paths,
        (
            f"any_ready={render_resource_sweep.get('any_render_video_ready')!r}, "
            f"records={render_resource_sweep.get('record_count')!r}, "
            f"classes={render_resource_sweep.get('renderer_failure_classes')!r}"
        ),
    )
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", []) or []}
    pilot_runtime_records = int(pilot_runtime.get("records_observed", 0) or 0)
    pilot_runtime_videos = int(pilot_runtime.get("videos_written", 0) or 0)
    pilot_runtime_fallbacks = len(pilot_runtime.get("diagnostic_video_fallbacks", []) or [])
    pilot_runtime_basic = (
        pilot_runtime.get("passed") is True
        and pilot_runtime.get("not_external_evidence") is True
        and pilot_runtime.get("strict_external_evidence_ready") is False
        and pilot_runtime.get("pilot_runtime_ready") is False
        and pilot_runtime.get("render_video_ready") is False
        and pilot_runtime_checks.get("bounded_runner_subprocess_exercised") is True
    )
    pilot_runtime_diagnostic_io = (
        pilot_runtime.get("runner_io_ready") is True
        and pilot_runtime_records >= 1
        and pilot_runtime_videos >= 1
        and pilot_runtime_fallbacks >= 1
    )
    pilot_runtime_guarded_rejection = (
        pilot_runtime.get("runner_io_ready") is False
        and pilot_runtime_records == 0
        and pilot_runtime_videos == 0
        and pilot_runtime_fallbacks >= 1
        and pilot_runtime.get("official_video_guard_blocked_diagnostic_fallback") is True
        and pilot_runtime_checks.get("official_guard_rejects_diagnostic_before_jsonl_write") is True
        and pilot_runtime_checks.get("diagnostic_rejection_paths_are_quarantined") is True
    )
    pilot_runtime_unavailable = (
        pilot_runtime.get("runner_io_ready") is False
        and pilot_runtime_records == 0
        and pilot_runtime_videos == 0
        and pilot_runtime_fallbacks == 0
    )
    add_check(
        checks,
        "maniskill_pilot_runtime_liveness_included",
        pilot_runtime_basic
        and (pilot_runtime_diagnostic_io or pilot_runtime_guarded_rejection or pilot_runtime_unavailable)
        and "scripts/audit_maniskill_pilot_runtime_liveness.py" in paths
        and "results/maniskill_pilot_runtime_liveness_audit.json" in paths
        and "results/maniskill_pilot_runtime_liveness_audit.md" in paths,
        (
            f"pilot_runtime_ready={pilot_runtime.get('pilot_runtime_ready')!r}, "
            f"runner_io_ready={pilot_runtime.get('runner_io_ready')!r}, "
            f"render_video_ready={pilot_runtime.get('render_video_ready')!r}, "
            f"timed_out={pilot_runtime.get('timed_out')!r}, "
            f"records={pilot_runtime_records!r}, "
            f"videos={pilot_runtime_videos!r}, "
            f"diagnostic_fallbacks={pilot_runtime_fallbacks}, "
            f"failure_summary={pilot_runtime.get('failure_summary')!r}"
        ),
    )
    render_machine_checks = {check.get("name"): check.get("passed") for check in render_machine.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_machine_qualification_included",
        render_machine.get("passed") is True
        and render_machine.get("not_external_evidence") is True
        and render_machine.get("strict_external_evidence_ready") is False
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and render_machine_checks.get("qualification_packet_is_non_evidence") is True
        and render_machine_checks.get("current_machine_fail_closed_when_render_not_ready") is True
        and "scripts/build_maniskill_render_machine_qualification.py" in paths
        and "external_validation/render_machine_qualification_packet.md" in paths
        and "results/maniskill_render_machine_qualification.json" in paths
        and "results/maniskill_render_machine_qualification.md" in paths,
        (
            f"qualification_state={render_machine.get('qualification_state')!r}, "
            f"render_machine_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"blocking={len(render_machine.get('blocking_missing', []) or [])}"
        ),
    )
    add_check(
        checks,
        "method_implementation_packet_included",
        method_implementation.get("passed") is True
        and method_implementation.get("not_external_evidence") is True
        and method_implementation.get("method_implementation_packet_ready") is True
        and method_implementation.get("strict_adapter_evidence_ready") is False
        and method_checks.get("work_orders_cover_all_missing_non_oracle_methods") is True
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
        and "external_validation/method_implementation_packet.json" in paths
        and "external_validation/method_implementation_packet.md" in paths
        and "external_validation/method_implementation_work_orders.csv" in paths
        and "external_validation/method_reference_provenance.csv" in paths
        and "external_validation/method_manifest_cutover_checklist.csv" in paths
        and "external_validation/method_manifest_cutover_checklist.md" in paths
        and "external_validation/adapter_acceptance_fixtures.json" in paths
        and "external_validation/adapter_acceptance_fixtures.md" in paths
        and "external_validation/adapter_acceptance_fixtures.csv" in paths
        and "results/external_method_implementation_audit.json" in paths
        and "scripts/build_external_method_implementation_packet.py" in paths,
        (
            f"method_implementation_packet_ready={method_implementation.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_implementation.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "operator_actions_cover_evidence_collection",
        {
            "platform_onboarding",
            "fidelity_metadata_probe",
            "fidelity_provenance_packet",
            "fidelity_acceptance_draft",
            "fidelity_acceptance_materializer",
            "backend_integration_packet",
            "maniskill_reference_backend_audit",
            "maniskill_reference_collection_preflight",
            "config_manifest_packet",
            "rollout_evidence_packet",
            "ablation_collection_packet",
            "evidence_intake_ledger",
            "precollection_freeze_receipt",
            "postcollection_evidence_seal",
            "postcollection_seal_consistency_gate",
            "backend_module",
            "real_task_configs",
            "platform_fidelity",
            "method_implementation_packet",
            "pilot_smoke_packet",
            "maniskill_render_video_preflight",
            "maniskill_render_resource_sweep",
            "maniskill_pilot_runtime_liveness",
            "real_method_implementations",
            "run_collection",
            "manifest_and_release",
            "strict_rollout_recompute",
            "final_strict_gate",
        }.issubset(action_ids),
        f"missing={sorted({'platform_onboarding', 'fidelity_metadata_probe', 'fidelity_provenance_packet', 'fidelity_acceptance_draft', 'fidelity_acceptance_materializer', 'backend_integration_packet', 'maniskill_reference_backend_audit', 'maniskill_reference_collection_preflight', 'config_manifest_packet', 'rollout_evidence_packet', 'ablation_collection_packet', 'evidence_intake_ledger', 'precollection_freeze_receipt', 'postcollection_evidence_seal', 'postcollection_seal_consistency_gate', 'backend_module', 'real_task_configs', 'platform_fidelity', 'method_implementation_packet', 'pilot_smoke_packet', 'maniskill_render_video_preflight', 'maniskill_render_resource_sweep', 'maniskill_pilot_runtime_liveness', 'real_method_implementations', 'run_collection', 'manifest_and_release', 'strict_rollout_recompute', 'final_strict_gate'} - action_ids)}",
    )
    add_check(
        checks,
        "post_collection_commands_cover_strict_gates",
        any("audit_external_release_package.py --strict" in command for command in post_commands)
        and any("audit_external_fidelity_acceptance.py --strict" in command for command in post_commands)
        and any("validate_external_adapters.py --strict" in command for command in post_commands)
        and any("validate_external_configs.py --strict" in command for command in post_commands)
        and any("validate_external_rollouts.py" in command and "--strict" in command for command in post_commands)
        and any("audit_external_pairing_integrity.py --strict" in command for command in post_commands)
        and any("audit_external_evidence.py --strict" in command for command in post_commands),
        f"commands={len(post_commands)}",
    )
    add_check(
        checks,
        "file_hashes_are_recorded",
        all(isinstance(record["sha256"], str) and len(record["sha256"]) == 64 for record in records if record["exists"]),
        f"hashed_files={sum(1 for record in records if record['sha256'])}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": "external_operator_handoff_bundle_v1",
        "passed": passed,
        "not_external_evidence": True,
        "handoff_bundle_ready": passed,
        "strict_evidence_ready": False,
        "start_state": operator.get("start_state"),
        "included_file_count": len(records),
        "category_counts": category_counts,
        "forbidden_path_parts": sorted(FORBIDDEN_PATH_PARTS),
        "forbidden_included_paths": forbidden,
        "missing_files": missing_files,
        "operator_next_actions": operator_actions,
        "pre_collection_gate_command": operator.get("pre_collection_gate_command", ""),
        "precollection_freeze_command": operator.get("precollection_freeze_command", ""),
        "postcollection_seal_command": operator.get("postcollection_seal_command", ""),
        "postcollection_consistency_command": operator.get("postcollection_consistency_command", ""),
        "backend_contract_gate_command": operator.get("backend_contract_gate_command", ""),
        "strict_collection_command": operator.get("strict_collection_command", ""),
        "post_collection_strict_commands": post_commands,
        "source_reports": [
            "results/external_operator_packet.json",
            "results/external_acquisition_packet.json",
            "results/external_analysis_plan_audit.json",
            "results/external_platform_onboarding_audit.json",
            "results/maniskill_fidelity_metadata_probe.json",
            "results/external_fidelity_provenance_audit.json",
            "results/external_fidelity_acceptance_draft_audit.json",
            "results/fidelity_acceptance_materialization_plan.json",
            "results/external_backend_integration_audit.json",
            "results/maniskill_backend_readiness_audit.json",
            "results/external_config_manifest_audit.json",
            "results/external_rollout_evidence_audit.json",
            "results/external_pilot_smoke_packet_audit.json",
            "results/external_pilot_smoke_audit.json",
            "results/maniskill_render_video_preflight_audit.json",
            "results/maniskill_render_resource_sweep.json",
            "results/maniskill_pilot_runtime_liveness_audit.json",
            "results/external_method_implementation_audit.json",
            "results/external_precollection_freeze_receipt_audit.json",
            "results/external_postcollection_evidence_seal_audit.json",
            "results/external_postcollection_seal_consistency_audit.json",
            "results/external_precollection_manifest_draft_audit.json",
            "results/external_evidence_preflight.json",
            "results/external_release_package_audit.json",
            "results/external_pairing_integrity_audit.json",
        ],
        "included_files": records,
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Operator Handoff Bundle",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict evidence ready: `{str(payload['strict_evidence_ready']).lower()}`.",
        f"Start state: `{payload['start_state']}`.",
        f"Included files: `{payload['included_file_count']}`.",
        "",
        "This is a hash-listed handoff manifest for an independent validation operator. It intentionally does not package rollout logs, videos, checkpoints, local dry-run artifacts, placeholder media, or `external_validation/manifest.json`. It is a non-evidence checklist for what to send before a real robot or accepted high-fidelity simulator run.",
        "",
        "## Commands",
        "",
        "Strict backend qualification:",
        "",
        "```powershell",
        payload["backend_contract_gate_command"],
        "```",
        "",
        "Strict pre-collection gate:",
        "",
        "```powershell",
        payload["pre_collection_gate_command"],
        "```",
        "",
        "Precollection freeze receipt:",
        "",
        "```powershell",
        payload["precollection_freeze_command"],
        "```",
        "",
        "Actual collection command after the strict gate passes:",
        "",
        "```powershell",
        payload["strict_collection_command"],
        "```",
        "",
        "Postcollection evidence seal before manifest promotion:",
        "",
        "```powershell",
        payload["postcollection_seal_command"],
        "```",
        "",
        "Postcollection seal consistency gate before manifest promotion:",
        "",
        "```powershell",
        payload["postcollection_consistency_command"],
        "```",
        "",
        "Post-collection strict gates:",
        "",
    ]
    for command in payload["post_collection_strict_commands"]:
        lines.append(f"- `{command}`")

    lines.extend(["", "## Category Counts", ""])
    for category, count in sorted(payload["category_counts"].items()):
        lines.append(f"- `{category}`: `{count}`")

    lines.extend(["", "## Excluded Evidence Paths", ""])
    for part in payload["forbidden_path_parts"]:
        lines.append(f"- `{part}`")

    lines.extend(["", "## Included Files", ""])
    for record in payload["included_files"]:
        lines.append(
            f"- `{record['path']}` "
            f"({record['category']}, {record['bytes']} bytes, sha256 `{record['sha256']}`)"
        )

    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "External operator handoff bundle: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"files={payload['included_file_count']}; "
        f"start_state={payload['start_state']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

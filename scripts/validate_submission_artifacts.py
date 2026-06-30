import csv
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"
FIGURES = ROOT / "figures"
EXTERNAL = ROOT / "external_validation"
PAPER_PDF = PAPER / "main.pdf"
ROOT_PDF = ROOT.parent / "119.pdf"
CHILD_PDF = ROOT / "119.pdf"


def configured_path(env_name, default):
    path = Path(os.environ.get(env_name, default))
    return path if path.is_absolute() else ROOT / path


DOWNLOADS_PDF = configured_path("PAPER119_CANONICAL_PDF", "C:/Users/wangz/Downloads/119.pdf")
DESKTOP_PDF = configured_path("PAPER119_DESKTOP_PDF", "C:/Users/wangz/Desktop/119.pdf")


def fail(message):
    raise SystemExit(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path):
    try:
        proc = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    except Exception as exc:
        fail(f"pdfinfo failed for {path}: {exc}")
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    fail("pdfinfo did not report page count")


def count_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def numeric_finiteness(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row_idx, row in enumerate(reader, start=2):
            for key, value in row.items():
                if value is None or value == "":
                    continue
                try:
                    number = float(value)
                except ValueError:
                    continue
                if not math.isfinite(number):
                    fail(f"non-finite numeric value in {path} row {row_idx} column {key}")


def main():
    summary_path = RESULTS / "summary.json"
    if not summary_path.exists():
        fail("missing results/summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("version") != "v5_expanded":
        fail("summary version is not v5_expanded")
    if summary.get("terminal_decision") != "STRONG_REVISE":
        fail("terminal decision must be STRONG_REVISE")
    if summary.get("iclr_main_ready") is not False:
        fail("ICLR main readiness must be false")
    if summary.get("scope_gate_pass") is not False:
        fail("scope gate must remain false")
    if summary.get("local_gates_pass") is not True:
        fail("local gates did not pass")
    failed = [name for name, ok in summary["gates"].items() if not ok]
    if failed:
        fail(f"failed gates: {failed}")

    build_script = ROOT / "scripts" / "build_submission_artifacts.ps1"
    if not build_script.exists():
        fail("missing scripts/build_submission_artifacts.ps1")
    build_text = build_script.read_text(encoding="utf-8")
    required_build_steps = [
        "src\\run_experiment.py",
        "scripts\\audit_local_falsification.py",
        "scripts\\audit_holdout_robustness.py",
        "scripts\\audit_diagnostic_mechanism.py",
        "scripts\\audit_decision_quality.py",
        "scripts\\audit_seam_prediction_calibration.py",
        "scripts\\audit_planner_edge_policy.py",
        "scripts\\build_local_model_release.py",
        "scripts\\generate_manuscript.py",
        "scripts\\audit_manuscript_numbers.py",
        "scripts\\audit_related_work.py",
        "scripts\\audit_reference_integrity.py",
        "scripts\\audit_manuscript_readability.py",
        "scripts\\build_external_collection_plan.py",
        "scripts\\build_external_analysis_plan.py",
        "scripts\\build_independent_validation_route.py",
        "scripts\\probe_external_platform.py",
        "scripts\\probe_maniskill_task_bindings.py",
        "scripts\\probe_maniskill_env_smoke.py",
        "scripts\\probe_maniskill_fidelity_metadata.py",
        "scripts\\build_external_platform_onboarding.py",
        "scripts\\build_external_fidelity_provenance_packet.py",
        "scripts\\self_test_external_fidelity_provenance_packet.py",
        "scripts\\build_external_fidelity_acceptance_draft.py",
        "scripts\\materialize_fidelity_acceptance.py",
        "scripts\\self_test_fidelity_acceptance_materializer.py",
        "scripts\\audit_external_fidelity_acceptance.py",
        "scripts\\self_test_external_fidelity_acceptance.py",
        "scripts\\build_external_blind_eval_plan.py",
        "scripts\\build_external_runbook.py",
        "scripts\\audit_external_runner_harness.py",
        "scripts\\audit_external_backend_contract.py",
        "scripts\\audit_maniskill_backend_readiness.py",
        "scripts\\audit_maniskill_reference_collection_preflight.py",
        "scripts\\build_external_backend_integration_packet.py",
        "scripts\\self_test_external_backend_integration_packet.py",
        "scripts\\audit_external_collection_readiness.py",
        "scripts\\audit_external_pilot_smoke.py",
        "scripts\\build_external_pilot_smoke_packet.py",
        "scripts\\audit_maniskill_render_video_preflight.py",
        "scripts\\audit_maniskill_pilot_runtime_liveness.py",
        "scripts\\build_maniskill_render_machine_qualification.py",
        "scripts\\self_test_maniskill_render_machine_qualification.py",
        "scripts\\validate_external_configs.py",
        "scripts\\self_test_external_config_evidence.py",
        "scripts\\materialize_external_configs.py",
        "scripts\\self_test_external_config_materialization.py",
        "scripts\\build_external_config_manifest_packet.py",
        "scripts\\self_test_external_config_manifest_packet.py",
        "scripts\\build_external_rollout_evidence_packet.py",
        "scripts\\build_external_ablation_collection_packet.py",
        "scripts\\self_test_external_ablation_collection_packet.py",
        "scripts\\build_external_evidence_intake_ledger.py",
        "scripts\\self_test_external_evidence_intake_ledger.py",
        "scripts\\build_external_precollection_manifest_draft.py",
        "scripts\\self_test_external_precollection_manifest_draft.py",
        "scripts\\build_external_precollection_freeze_receipt.py",
        "scripts\\self_test_external_precollection_freeze_receipt.py",
        "scripts\\build_external_postcollection_evidence_seal.py",
        "scripts\\self_test_external_postcollection_evidence_seal.py",
        "scripts\\audit_external_postcollection_seal_consistency.py",
        "scripts\\self_test_external_postcollection_seal_consistency.py",
        "scripts\\build_external_baseline_contract.py",
        "scripts\\self_test_external_baseline_contract.py",
        "scripts\\build_external_adapter_scaffolds.py",
        "scripts\\build_external_reference_adapters.py",
        "scripts\\build_external_local_dry_run.py",
        "scripts\\validate_external_adapters.py",
        "scripts\\build_external_method_implementation_packet.py",
        "scripts\\materialize_external_method_configs.py",
        "scripts\\self_test_external_method_config_materialization.py",
        "scripts\\self_test_external_adapter_evidence.py",
        "scripts\\build_external_manifest.py --allow-missing",
        "scripts\\self_test_external_manifest_builder.py",
        "scripts\\audit_external_release_package.py",
        "scripts\\self_test_external_release_package.py",
        "scripts\\audit_external_evidence_preflight.py",
        "scripts\\self_test_external_evidence_preflight.py",
        "scripts\\build_external_acquisition_packet.py",
        "scripts\\self_test_external_acquisition_packet.py",
        "scripts\\build_external_operator_packet.py",
        "scripts\\build_external_collection_job_packet.py",
        "scripts\\self_test_external_collection_job_packet.py",
        "scripts\\build_external_collection_machine_bootstrap.py",
        "scripts\\self_test_external_collection_machine_bootstrap.py",
        "scripts\\build_external_operator_handoff_bundle.py",
        "scripts\\self_test_external_operator_handoff_bundle.py",
        "scripts\\build_external_operator_release_bundle.py",
        "scripts\\self_test_external_operator_release_bundle.py",
        "scripts\\self_test_external_adapter_scaffold_guard.py",
        "scripts\\self_test_external_backend_contract.py",
        "scripts\\self_test_external_collection_preflight.py",
        "scripts\\self_test_external_runner_backend.py",
        "scripts\\self_test_external_rollout_validator.py",
        "scripts\\self_test_external_evidence_pipeline.py",
        "scripts\\validate_external_rollouts.py --write-results",
        "scripts\\audit_external_pairing_integrity.py",
        "scripts\\self_test_external_pairing_integrity.py",
        "scripts\\audit_external_evidence.py",
        "scripts\\audit_external_execution_readiness.py",
        "scripts\\self_test_external_execution_readiness.py",
        "scripts\\audit_claim_boundary.py",
        "scripts\\audit_submission_readiness_gap.py",
        "scripts\\build_reviewer_response_packet.py",
        "pdflatex -interaction=nonstopmode -halt-on-error main.tex",
        "bibtex main",
        "Copy-Item -LiteralPath paper\\main.pdf",
        "scripts\\audit_presentation_quality.py",
        "scripts\\audit_figure_readability.py",
        "scripts\\audit_camera_ready_design.py",
        "scripts\\build_outreach_artifacts.ps1",
        "scripts\\audit_visible_contribution.py",
        "scripts\\validate_submission_artifacts.py",
        "scripts\\validate_outreach_artifacts.py",
    ]
    missing_build_steps = [step for step in required_build_steps if step not in build_text]
    if missing_build_steps:
        fail(f"build script missing required steps: {missing_build_steps}")
    required_build_controls = [
        "$RenderPreflightTimeoutSeconds = 45",
        "$RenderPreflightMaxEnvs = 4",
        "$RenderProfileMatrixMaxEnvs = 1",
        "--timeout-seconds $RenderPreflightTimeoutSeconds",
        "--max-envs $RenderPreflightMaxEnvs",
        "--profile-matrix",
        "--profile-matrix-max-envs $RenderProfileMatrixMaxEnvs",
    ]
    missing_build_controls = [term for term in required_build_controls if term not in build_text]
    if missing_build_controls:
        fail(f"build script missing bounded render-preflight controls: {missing_build_controls}")

    ci_workflow = ROOT / ".github" / "workflows" / "paper119-validation.yml"
    if not ci_workflow.exists():
        fail("missing GitHub validation workflow: .github/workflows/paper119-validation.yml")
    ci_text = ci_workflow.read_text(encoding="utf-8")
    required_ci_terms = [
        "PAPER119_CANONICAL_PDF",
        "poppler-utils",
        "python -m compileall",
        "python scripts/audit_planner_edge_policy.py",
        "python scripts/build_local_model_release.py",
        "python scripts/audit_external_runner_harness.py",
        "python scripts/audit_external_backend_contract.py",
        "python scripts/audit_maniskill_backend_readiness.py",
        "python scripts/audit_maniskill_reference_collection_preflight.py",
        "python scripts/self_test_external_backend_contract.py",
        "python scripts/audit_external_fidelity_acceptance.py",
        "python scripts/self_test_external_fidelity_acceptance.py",
        "python scripts/self_test_external_fidelity_provenance_packet.py",
        "python scripts/self_test_external_runner_backend.py",
        "python scripts/self_test_external_collection_preflight.py",
        "python scripts/audit_external_collection_readiness.py",
        "python scripts/audit_external_pilot_smoke.py",
        "python scripts/build_external_pilot_smoke_packet.py",
        "python scripts/audit_maniskill_render_video_preflight.py",
        "python scripts/audit_maniskill_pilot_runtime_liveness.py",
        "python scripts/build_maniskill_render_machine_qualification.py",
        "python scripts/self_test_maniskill_render_machine_qualification.py",
        "python scripts/audit_external_evidence_preflight.py",
        "python scripts/self_test_external_evidence_preflight.py",
        "python scripts/self_test_external_config_evidence.py",
        "python scripts/self_test_external_adapter_evidence.py",
        "python scripts/materialize_external_configs.py",
        "python scripts/self_test_external_config_materialization.py",
        "python scripts/build_external_config_manifest_packet.py",
        "python scripts/build_external_rollout_evidence_packet.py",
        "python scripts/build_external_ablation_collection_packet.py",
        "python scripts/self_test_external_ablation_collection_packet.py",
        "python scripts/build_external_evidence_intake_ledger.py",
        "python scripts/self_test_external_evidence_intake_ledger.py",
        "python scripts/build_external_precollection_manifest_draft.py",
        "python scripts/self_test_external_precollection_manifest_draft.py",
        "python scripts/build_external_precollection_freeze_receipt.py",
        "python scripts/self_test_external_precollection_freeze_receipt.py",
        "python scripts/build_external_postcollection_evidence_seal.py",
        "python scripts/self_test_external_postcollection_evidence_seal.py",
        "python scripts/audit_external_postcollection_seal_consistency.py",
        "python scripts/self_test_external_postcollection_seal_consistency.py",
        "python scripts/build_external_analysis_plan.py",
        "python scripts/probe_external_platform.py",
        "python scripts/probe_maniskill_task_bindings.py",
        "python scripts/probe_maniskill_env_smoke.py",
        "python scripts/probe_maniskill_fidelity_metadata.py",
        "python scripts/build_external_platform_onboarding.py",
        "python scripts/build_external_fidelity_provenance_packet.py",
        "python scripts/build_external_fidelity_acceptance_draft.py",
        "python scripts/materialize_fidelity_acceptance.py",
        "python scripts/self_test_fidelity_acceptance_materializer.py",
        "python scripts/build_external_backend_integration_packet.py",
        "python scripts/self_test_external_backend_integration_packet.py",
        "python scripts/build_external_method_implementation_packet.py",
        "python scripts/materialize_external_method_configs.py",
        "python scripts/self_test_external_method_config_materialization.py",
        "python scripts/build_external_acquisition_packet.py",
        "python scripts/self_test_external_acquisition_packet.py",
        "python scripts/build_external_operator_packet.py",
        "python scripts/build_external_collection_job_packet.py",
        "python scripts/self_test_external_collection_job_packet.py",
        "python scripts/build_external_collection_machine_bootstrap.py",
        "python scripts/self_test_external_collection_machine_bootstrap.py",
        "python scripts/build_external_operator_handoff_bundle.py",
        "python scripts/self_test_external_operator_handoff_bundle.py",
        "python scripts/build_external_operator_release_bundle.py",
        "python scripts/self_test_external_operator_release_bundle.py",
        "python scripts/audit_external_release_package.py",
        "python scripts/self_test_external_manifest_builder.py",
        "python scripts/self_test_external_release_package.py",
        "python scripts/audit_external_execution_readiness.py",
        "python scripts/self_test_external_execution_readiness.py",
        "python scripts/audit_external_pairing_integrity.py",
        "python scripts/self_test_external_pairing_integrity.py",
        "python scripts/self_test_external_rollout_validator.py",
        "python scripts/self_test_external_evidence_pipeline.py",
        "python scripts/audit_submission_readiness_gap.py",
        "python scripts/build_reviewer_response_packet.py",
        "python scripts/audit_visible_contribution.py",
        "python scripts/audit_claim_boundary.py",
        "python scripts/validate_submission_artifacts.py",
        "python scripts/validate_outreach_artifacts.py",
    ]
    missing_ci_terms = [term for term in required_ci_terms if term not in ci_text]
    if missing_ci_terms:
        fail(f"GitHub validation workflow missing required terms: {missing_ci_terms}")
    required_ci_render_controls = [
        "python scripts/audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 4 --profile-matrix --profile-matrix-max-envs 1",
    ]
    missing_ci_render_controls = [term for term in required_ci_render_controls if term not in ci_text]
    if missing_ci_render_controls:
        fail(f"GitHub validation workflow missing bounded render-preflight controls: {missing_ci_render_controls}")

    collection_plan_path = RESULTS / "external_collection_plan.json"
    if not collection_plan_path.exists():
        fail("missing results/external_collection_plan.json; run scripts/build_external_collection_plan.py")
    collection_plan = json.loads(collection_plan_path.read_text(encoding="utf-8"))
    if collection_plan.get("version") != "external_collection_plan_v1":
        fail("external collection plan version mismatch")
    if collection_plan.get("not_external_evidence") is not True:
        fail("external collection plan must declare that it is not evidence")
    if collection_plan.get("passed") is not True:
        fail("external collection plan did not pass")
    if int(collection_plan.get("total_required_records", 0)) < 1440:
        fail("external collection plan has too few required records for the high-fidelity route")
    if int(collection_plan.get("method_count", 0)) < 12:
        fail("external collection plan has too few methods")
    if int(collection_plan.get("task_family_count", 0)) < 4:
        fail("external collection plan has too few task families")
    collection_commands = collection_plan.get("validation_commands", []) or []
    collection_command_text = "\n".join(str(command) for command in collection_commands)
    if "python scripts\\audit_external_evidence.py --strict" not in collection_commands:
        fail("external collection plan must include the strict external evidence audit command")
    if "python scripts\\build_external_baseline_contract.py" not in collection_commands:
        fail("external collection plan must include the baseline implementation contract command")
    if "python scripts\\build_external_adapter_scaffolds.py" not in collection_commands:
        fail("external collection plan must include the adapter scaffold command")
    if "python scripts\\validate_external_adapters.py" not in collection_commands:
        fail("external collection plan must include the adapter contract validation command")
    if "python scripts\\build_external_backend_integration_packet.py" not in collection_commands:
        fail("external collection plan must include the backend integration packet command")
    if "python scripts\\build_external_config_manifest_packet.py" not in collection_commands:
        fail("external collection plan must include the config manifest packet command")
    if "python scripts\\build_external_rollout_evidence_packet.py" not in collection_commands:
        fail("external collection plan must include the rollout evidence packet command")
    if "python scripts\\build_external_ablation_collection_packet.py" not in collection_commands:
        fail("external collection plan must include the external ablation collection packet command")
    if "python scripts\\build_external_evidence_intake_ledger.py" not in collection_commands:
        fail("external collection plan must include the external evidence intake ledger command")
    if "python scripts\\audit_external_pilot_smoke.py" not in collection_commands:
        fail("external collection plan must include the pilot smoke audit command")
    if "python scripts\\build_external_pilot_smoke_packet.py" not in collection_commands:
        fail("external collection plan must include the pilot smoke packet command")
    if "python scripts\\build_external_method_implementation_packet.py" not in collection_commands:
        fail("external collection plan must include the method implementation packet command")
    if "python scripts\\validate_external_adapters.py --strict" not in collection_commands:
        fail("external collection plan must include the strict adapter implementation validation command")
    if "python scripts\\audit_external_release_package.py --strict" not in collection_commands:
        fail("external collection plan must include the strict release package audit command")
    if "python scripts\\audit_external_pairing_integrity.py --strict" not in collection_commands:
        fail("external collection plan must include the strict pairing integrity audit command")
    if "python scripts\\validate_external_configs.py" not in collection_commands:
        fail("external collection plan must include the config template validation command")
    if "python scripts\\validate_external_configs.py --strict" not in collection_commands:
        fail("external collection plan must include the strict config evidence validation command")
    if "python scripts\\audit_external_fidelity_acceptance.py" not in collection_commands:
        fail("external collection plan must include the fidelity acceptance audit command")
    if "python scripts\\build_external_blind_eval_plan.py" not in collection_commands:
        fail("external collection plan must include the blind evaluation plan command")
    if "python scripts\\build_independent_validation_route.py" not in collection_commands:
        fail("external collection plan must include the independent validation route command")
    if "python scripts\\probe_external_platform.py" not in collection_commands:
        fail("external collection plan must include the external platform probe command")
    if "python scripts\\probe_maniskill_task_bindings.py" not in collection_commands:
        fail("external collection plan must include the ManiSkill task binding probe command")
    if "python scripts\\probe_maniskill_env_smoke.py" not in collection_commands:
        fail("external collection plan must include the ManiSkill env smoke probe command")
    if "python scripts\\build_external_platform_onboarding.py" not in collection_commands:
        fail("external collection plan must include the external platform onboarding command")
    if "python scripts\\build_external_fidelity_provenance_packet.py" not in collection_commands:
        fail("external collection plan must include the fidelity provenance packet command")
    if "python scripts\\audit_external_collection_readiness.py" not in collection_commands:
        fail("external collection plan must include the collection readiness audit command")
    if "python scripts\\audit_external_collection_readiness.py --strict" not in collection_commands:
        fail("external collection plan must include the strict collection readiness audit command")
    if "python scripts\\build_external_analysis_plan.py" not in collection_commands:
        fail("external collection plan must include the external statistical analysis plan command")
    for fragment in (
        "probe_maniskill_fidelity_metadata.py",
        "audit_external_runner_harness.py",
        "audit_external_backend_contract.py",
        "audit_maniskill_backend_readiness.py",
        "audit_maniskill_reference_collection_preflight.py",
        "self_test_external_runner_backend.py",
        "audit_maniskill_render_video_preflight.py",
        "audit_maniskill_pilot_runtime_liveness.py",
        "build_maniskill_render_machine_qualification.py",
        "build_external_ablation_collection_packet.py",
        "build_external_evidence_intake_ledger.py",
        "build_external_precollection_freeze_receipt.py",
        "build_external_postcollection_evidence_seal.py",
        "audit_external_postcollection_seal_consistency.py",
        "materialize_external_configs.py --platform-type high_fidelity_sim",
        "real_collection_runner.py --backend-module <module_or_path>",
        "audit_external_evidence_preflight.py",
    ):
        if fragment not in collection_command_text:
            fail(f"external collection plan missing current route gate command fragment: {fragment}")

    analysis_plan_path = EXTERNAL / "statistical_analysis_plan.json"
    analysis_plan_md_path = EXTERNAL / "statistical_analysis_plan.md"
    analysis_audit_path = RESULTS / "external_analysis_plan_audit.json"
    analysis_audit_md_path = RESULTS / "external_analysis_plan_audit.md"
    for path in (analysis_plan_path, analysis_plan_md_path, analysis_audit_path, analysis_audit_md_path):
        if not path.exists():
            fail(f"missing external analysis plan artifact: {path}")
    analysis_plan = json.loads(analysis_plan_path.read_text(encoding="utf-8"))
    analysis_audit = json.loads(analysis_audit_path.read_text(encoding="utf-8"))
    log_schema = json.loads((EXTERNAL / "log_schema_v1.json").read_text(encoding="utf-8"))
    if analysis_plan.get("version") != "external_statistical_analysis_plan_v1":
        fail("external statistical analysis plan version mismatch")
    if analysis_plan.get("not_external_evidence") is not True or analysis_plan.get("analysis_locked_before_collection") is not True:
        fail("external statistical analysis plan must be locked and marked non-evidence")
    if analysis_plan.get("primary_method") != log_schema.get("primary_method"):
        fail("external statistical analysis plan primary method must match the log schema")
    if analysis_plan.get("primary_thresholds") != log_schema.get("primary_thresholds"):
        fail("external statistical analysis plan thresholds must match the log schema")
    if analysis_plan.get("paired_comparison_key") != log_schema.get("paired_comparison_key"):
        fail("external statistical analysis plan paired key must match the log schema")
    if int(analysis_plan.get("planned_records", 0) or 0) != int(collection_plan.get("total_required_records", 0) or 0):
        fail("external statistical analysis plan must lock the collection-plan record budget")
    hypothesis_metrics = {entry.get("metric") for entry in analysis_plan.get("primary_hypotheses", []) if isinstance(entry, dict)}
    required_metrics = {
        "external_success_margin",
        "external_utility_margin",
        "paired_win_rate",
        "fixed_risk_coverage",
        "fixed_risk_breach",
        "positive_task_families",
    }
    if not required_metrics.issubset(hypothesis_metrics):
        fail(f"external statistical analysis plan missing primary hypotheses: {sorted(required_metrics - hypothesis_metrics)}")
    confidence_gate = analysis_plan.get("statistical_confidence_gate", {}) or {}
    if (
        confidence_gate.get("version") != "external_statistical_confidence_v1"
        or confidence_gate.get("confidence_level") != 0.95
        or int(confidence_gate.get("bootstrap_replicates", 0) or 0) < 1000
        or "lower confidence bound" not in str(confidence_gate.get("rule", ""))
        or "upper confidence" not in str(confidence_gate.get("rule", ""))
    ):
        fail("external statistical analysis plan must predeclare the 95% bootstrap confidence gate")
    strict_gates = "\n".join(analysis_plan.get("decision_rule", {}).get("strict_gates", []) or [])
    for fragment in (
        "audit_external_release_package.py --strict",
        "audit_external_fidelity_acceptance.py --strict",
        "validate_external_configs.py --strict",
        "validate_external_adapters.py --strict",
        "validate_external_rollouts.py",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in strict_gates:
            fail(f"external statistical analysis plan missing strict gate: {fragment}")
    exclusions = analysis_plan.get("exclusion_policy", {}) or {}
    if exclusions.get("unit") != "paired_reset_method_panel":
        fail("external statistical analysis plan must use paired_reset_method_panel as exclusion unit")
    reporting = set(analysis_plan.get("required_reporting", []) or [])
    for required_report in ("statistical_confidence", "95% confidence intervals for primary external metrics"):
        if required_report not in reporting:
            fail(f"external statistical analysis plan missing confidence reporting requirement: {required_report}")
    forbidden_exclusions = "\n".join(exclusions.get("forbidden", []) or [])
    if "dropping only the proposed method" not in forbidden_exclusions or "after viewing method identity" not in forbidden_exclusions:
        fail("external statistical analysis plan exclusion policy does not block cherry-picking")
    if analysis_audit.get("version") != "external_analysis_plan_audit_v1":
        fail("external analysis plan audit version mismatch")
    if analysis_audit.get("passed") is not True:
        fail("external analysis plan audit did not pass")
    if analysis_audit.get("not_external_evidence") is not True:
        fail("external analysis plan audit must declare that it is not evidence")
    if analysis_audit.get("analysis_plan_ready") is not True or analysis_audit.get("strict_evidence_ready") is not False:
        fail("external analysis plan audit must be ready while strict external evidence remains false")
    analysis_checks = {entry.get("name"): entry.get("passed") for entry in analysis_audit.get("checks", [])}
    for required_check in (
        "plan_is_non_evidence_and_locked",
        "primary_method_matches_schema",
        "thresholds_match_log_schema",
        "primary_hypotheses_cover_all_strict_thresholds",
        "confidence_gate_is_predeclared",
        "paired_key_matches_schema",
        "collection_plan_record_budget_referenced",
        "decision_rule_requires_strict_external_gates",
        "exclusion_policy_blocks_cherry_picking",
        "unblinding_policy_preserves_blind_eval",
        "required_reporting_covers_primary_and_audit_outputs",
    ):
        if analysis_checks.get(required_check) is not True:
            fail(f"external analysis plan audit missing passing check: {required_check}")

    route_audit_path = RESULTS / "independent_validation_route_audit.json"
    if not route_audit_path.exists():
        fail("missing results/independent_validation_route_audit.json; run scripts/build_independent_validation_route.py")
    route_audit = json.loads(route_audit_path.read_text(encoding="utf-8"))
    if route_audit.get("version") != "independent_validation_route_v1":
        fail("independent validation route audit version mismatch")
    if route_audit.get("passed") is not True:
        fail("independent validation route audit did not pass")
    if route_audit.get("not_external_evidence") is not True:
        fail("independent validation route audit must declare that it is not evidence")
    if route_audit.get("primary_route") != "maniskill_sapien_primary":
        fail("independent validation route should keep ManiSkill/SAPIEN as the primary public simulator route")
    route_checks = {check.get("name"): check.get("passed") for check in route_audit.get("checks", [])}
    for required_check in (
        "primary_route_independent_of_haonan",
        "primary_route_covers_collection_tasks",
        "all_readiness_blockers_have_route_closure",
        "public_sim_routes_have_official_sources",
    ):
        if route_checks.get(required_check) is not True:
            fail(f"independent validation route audit missing passing check: {required_check}")
    for path in (
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        RESULTS / "independent_validation_route_audit.md",
    ):
        if not path.exists():
            fail(f"missing independent validation route artifact: {path}")

    platform_probe_path = RESULTS / "external_platform_probe.json"
    platform_probe_md_path = RESULTS / "external_platform_probe.md"
    if not platform_probe_path.exists():
        fail("missing results/external_platform_probe.json; run scripts/probe_external_platform.py")
    if not platform_probe_md_path.exists():
        fail("missing results/external_platform_probe.md")
    if not (ROOT / "scripts" / "probe_external_platform.py").exists():
        fail("missing scripts/probe_external_platform.py")
    platform_probe = json.loads(platform_probe_path.read_text(encoding="utf-8"))
    if platform_probe.get("version") != "external_platform_probe_v1":
        fail("external platform probe version mismatch")
    if platform_probe.get("passed") is not True:
        fail("external platform probe did not pass")
    if platform_probe.get("not_external_evidence") is not True:
        fail("external platform probe must declare that it is not evidence")
    if platform_probe.get("platform_probe_ready") is not True:
        fail("external platform probe must report platform_probe_ready=true")
    if platform_probe.get("strict_fidelity_evidence_ready") is not False or platform_probe.get("strict_external_evidence_ready") is not False:
        fail("external platform probe must not claim strict fidelity or external evidence readiness")
    if platform_probe.get("primary_route") != "maniskill_sapien_primary":
        fail("external platform probe must target the primary ManiSkill/SAPIEN route")
    if not isinstance(platform_probe.get("primary_route_install_ready"), bool):
        fail("external platform probe must report primary_route_install_ready as a boolean")
    probe_checks = {check.get("name"): check.get("passed") for check in platform_probe.get("checks", [])}
    for required_check in (
        "probe_is_non_evidence",
        "primary_packages_checked",
        "primary_install_readiness_reported",
        "repo_commit_reported",
        "required_hashes_recorded",
        "gpu_renderer_commands_attempted",
        "strict_evidence_remains_false",
    ):
        if probe_checks.get(required_check) is not True:
            fail(f"external platform probe missing passing check: {required_check}")

    task_binding_file_path = EXTERNAL / "maniskill_task_bindings.json"
    task_binding_probe_path = RESULTS / "maniskill_task_binding_probe.json"
    task_binding_probe_md_path = RESULTS / "maniskill_task_binding_probe.md"
    for path in (task_binding_file_path, task_binding_probe_path, task_binding_probe_md_path, ROOT / "scripts" / "probe_maniskill_task_bindings.py"):
        if not path.exists():
            fail(f"missing ManiSkill task binding artifact: {path}")
    task_binding_file = json.loads(task_binding_file_path.read_text(encoding="utf-8"))
    task_binding_probe = json.loads(task_binding_probe_path.read_text(encoding="utf-8"))
    if task_binding_file.get("version") != "maniskill_task_bindings_v1":
        fail("ManiSkill task binding file version mismatch")
    if task_binding_file.get("not_external_evidence") is not True:
        fail("ManiSkill task binding file must be non-evidence")
    if task_binding_probe.get("version") != "maniskill_task_binding_probe_v1":
        fail("ManiSkill task binding probe version mismatch")
    if task_binding_probe.get("passed") is not True:
        fail("ManiSkill task binding probe did not pass")
    if task_binding_probe.get("not_external_evidence") is not True:
        fail("ManiSkill task binding probe must declare that it is not evidence")
    if task_binding_probe.get("task_binding_probe_ready") is not True:
        fail("ManiSkill task binding probe must report task_binding_probe_ready=true")
    if task_binding_probe.get("accepted_task_binding_ready") is not False:
        fail("ManiSkill task binding probe must leave accepted_task_binding_ready=false")
    if task_binding_probe.get("strict_fidelity_evidence_ready") is not False or task_binding_probe.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill task binding probe must not claim strict fidelity or external evidence readiness")
    task_records = task_binding_probe.get("task_records", []) or []
    if {record.get("task_family") for record in task_records if isinstance(record, dict)} != {task.get("task_family") for task in collection_plan.get("tasks", [])}:
        fail("ManiSkill task binding probe task set must match the collection plan")
    for record in task_records:
        if not isinstance(record, dict):
            continue
        if not record.get("primary_env_id"):
            fail(f"ManiSkill task binding record missing primary env id: {record}")
        if record.get("requires_operator_fidelity_acceptance") is not True:
            fail(f"ManiSkill task binding must require operator fidelity acceptance: {record.get('task_family')}")
    binding_checks = {check.get("name"): check.get("passed") for check in task_binding_probe.get("checks", [])}
    for required_check in (
        "probe_is_non_evidence",
        "binding_file_ready",
        "task_bindings_cover_configs",
        "configs_embed_backend_task_bindings",
        "registry_availability_reported",
        "primary_env_availability_reported",
        "strict_evidence_remains_false",
    ):
        if binding_checks.get(required_check) is not True:
            fail(f"ManiSkill task binding probe missing passing check: {required_check}")

    env_smoke_path = RESULTS / "maniskill_env_smoke_probe.json"
    env_smoke_md_path = RESULTS / "maniskill_env_smoke_probe.md"
    for path in (env_smoke_path, env_smoke_md_path, ROOT / "scripts" / "probe_maniskill_env_smoke.py"):
        if not path.exists():
            fail(f"missing ManiSkill env smoke artifact: {path}")
    env_smoke = json.loads(env_smoke_path.read_text(encoding="utf-8"))
    if env_smoke.get("version") != "maniskill_env_smoke_probe_v1":
        fail("ManiSkill env smoke probe version mismatch")
    if env_smoke.get("passed") is not True:
        fail("ManiSkill env smoke probe did not pass")
    if env_smoke.get("not_external_evidence") is not True:
        fail("ManiSkill env smoke probe must declare that it is not evidence")
    if env_smoke.get("env_smoke_probe_ready") is not True:
        fail("ManiSkill env smoke probe must report env_smoke_probe_ready=true")
    if env_smoke.get("accepted_fidelity_ready") is not False:
        fail("ManiSkill env smoke probe must leave accepted_fidelity_ready=false")
    if env_smoke.get("strict_fidelity_evidence_ready") is not False or env_smoke.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill env smoke probe must not claim strict fidelity or external evidence readiness")
    if int(env_smoke.get("primary_env_count", 0) or 0) < 4:
        fail("ManiSkill env smoke probe must cover the four primary task envs")
    if not isinstance(env_smoke.get("primary_reset_missing"), list):
        fail("ManiSkill env smoke probe must report primary_reset_missing as a list")
    if not isinstance(env_smoke.get("support_reset_missing"), list):
        fail("ManiSkill env smoke probe must report support_reset_missing as a list")
    if not isinstance(env_smoke.get("missing_asset_ids"), list):
        fail("ManiSkill env smoke probe must report missing_asset_ids as a list")
    if env_smoke.get("asset_related_failures") and not env_smoke.get("missing_asset_ids"):
        fail("ManiSkill env smoke probe must identify missing asset IDs for asset-related failures")
    if env_smoke.get("missing_asset_ids") and not isinstance(env_smoke.get("asset_install_hints"), list):
        fail("ManiSkill env smoke probe must provide structured asset_install_hints for missing assets")
    for record in env_smoke.get("env_records", []):
        if not isinstance(record, dict):
            fail("ManiSkill env smoke records must be objects")
        if "required_asset_ids" not in record or "missing_asset_ids" not in record:
            fail(f"ManiSkill env smoke record must include asset provenance fields: {record.get('env_id')}")
    env_smoke_checks = {check.get("name"): check.get("passed") for check in env_smoke.get("checks", [])}
    for required_check in (
        "probe_is_non_evidence",
        "binding_file_ready",
        "smoke_attempted_all_bound_envs",
        "primary_reset_readiness_reported",
        "asset_failures_reported",
        "strict_evidence_remains_false",
    ):
        if env_smoke_checks.get(required_check) is not True:
            fail(f"ManiSkill env smoke probe missing passing check: {required_check}")

    fidelity_metadata_path = RESULTS / "maniskill_fidelity_metadata_probe.json"
    fidelity_metadata_md_path = RESULTS / "maniskill_fidelity_metadata_probe.md"
    for path in (fidelity_metadata_path, fidelity_metadata_md_path, ROOT / "scripts" / "probe_maniskill_fidelity_metadata.py"):
        if not path.exists():
            fail(f"missing ManiSkill fidelity metadata probe artifact: {path}")
    fidelity_metadata = json.loads(fidelity_metadata_path.read_text(encoding="utf-8"))
    if fidelity_metadata.get("version") != "maniskill_fidelity_metadata_probe_v1":
        fail("ManiSkill fidelity metadata probe version mismatch")
    if fidelity_metadata.get("passed") is not True:
        fail("ManiSkill fidelity metadata probe did not pass")
    if fidelity_metadata.get("not_external_evidence") is not True:
        fail("ManiSkill fidelity metadata probe must declare that it is not evidence")
    if fidelity_metadata.get("metadata_probe_ready") is not True:
        fail("ManiSkill fidelity metadata probe must report metadata_probe_ready=true")
    if fidelity_metadata.get("accepted_fidelity_ready") is not False:
        fail("ManiSkill fidelity metadata probe must leave accepted_fidelity_ready=false")
    if fidelity_metadata.get("strict_fidelity_evidence_ready") is not False or fidelity_metadata.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill fidelity metadata probe must not claim strict fidelity or external evidence readiness")
    timing_summary = fidelity_metadata.get("primary_timing_summary", {}) or {}
    for field in (
        "sim_freq_hz_values",
        "control_freq_hz_values",
        "sim_timestep_seconds_values",
        "control_timestep_seconds_values",
        "derived_substeps_per_control_step_values",
        "scene_backend_types",
    ):
        if not isinstance(timing_summary.get(field), list):
            fail(f"ManiSkill fidelity metadata probe must report timing summary list field: {field}")
    if len(fidelity_metadata.get("env_records", []) or []) < 4:
        fail("ManiSkill fidelity metadata probe must attempt the bound primary task envs")
    if not isinstance(fidelity_metadata.get("primary_metadata_missing"), list):
        fail("ManiSkill fidelity metadata probe must report primary_metadata_missing as a list")
    if not isinstance(fidelity_metadata.get("missing_asset_ids"), list):
        fail("ManiSkill fidelity metadata probe must report missing_asset_ids as a list")
    for record in fidelity_metadata.get("env_records", []):
        if not isinstance(record, dict):
            fail("ManiSkill fidelity metadata probe records must be objects")
        if "required_asset_ids" not in record or "missing_asset_ids" not in record or "metadata" not in record:
            fail(f"ManiSkill fidelity metadata record must include asset and metadata fields: {record.get('env_id')}")
    fidelity_metadata_checks = {check.get("name"): check.get("passed") for check in fidelity_metadata.get("checks", [])}
    for required_check in (
        "probe_is_non_evidence",
        "binding_file_ready",
        "metadata_attempted_all_bound_envs",
        "primary_metadata_readiness_reported",
        "timing_summary_reported",
        "asset_requirements_reported",
        "strict_evidence_remains_false",
    ):
        if fidelity_metadata_checks.get(required_check) is not True:
            fail(f"ManiSkill fidelity metadata probe missing passing check: {required_check}")

    onboarding_packet_path = EXTERNAL / "platform_onboarding_packet.json"
    onboarding_packet_md_path = EXTERNAL / "platform_onboarding_packet.md"
    onboarding_audit_path = RESULTS / "external_platform_onboarding_audit.json"
    onboarding_audit_md_path = RESULTS / "external_platform_onboarding_audit.md"
    for path in (onboarding_packet_path, onboarding_packet_md_path, onboarding_audit_path, onboarding_audit_md_path):
        if not path.exists():
            fail(f"missing external platform onboarding artifact: {path}")
    onboarding_packet = json.loads(onboarding_packet_path.read_text(encoding="utf-8"))
    onboarding_audit = json.loads(onboarding_audit_path.read_text(encoding="utf-8"))
    if onboarding_packet.get("version") != "external_platform_onboarding_v1":
        fail("external platform onboarding packet version mismatch")
    if onboarding_packet.get("not_external_evidence") is not True:
        fail("external platform onboarding packet must declare that it is not evidence")
    if onboarding_packet.get("primary_route") != "maniskill_sapien_primary":
        fail("external platform onboarding must keep ManiSkill/SAPIEN as the primary route")
    if int(onboarding_packet.get("planned_records", 0) or 0) != int(collection_plan.get("total_required_records", 0) or 0):
        fail("external platform onboarding must preserve the collection-plan record budget")
    if set(onboarding_packet.get("planned_tasks", []) or []) != {task.get("task_family") for task in collection_plan.get("tasks", [])}:
        fail("external platform onboarding task set must match the collection plan")
    source_urls = "\n".join(
        str(source.get("url", ""))
        for sources in (onboarding_packet.get("official_sources", {}) or {}).values()
        for source in sources
        if isinstance(source, dict)
    )
    for domain in ("maniskill.readthedocs.io", "sapien.ucsd.edu", "robosuite.ai", "isaac-sim.github.io"):
        if domain not in source_urls:
            fail(f"external platform onboarding missing official source domain: {domain}")
    provenance_fields = set(onboarding_packet.get("required_platform_provenance_fields", []) or [])
    for field in (
        "contact_solver",
        "friction_model",
        "camera_intrinsics_and_resolution",
        "state_observation_keys",
        "contact_signal_keys",
        "task_config_sha256",
        "backend_module_sha256",
        "skill_library_hash",
        "code_commit",
    ):
        if field not in provenance_fields:
            fail(f"external platform onboarding missing provenance field: {field}")
    strict_onboarding_commands = "\n".join(onboarding_packet.get("strict_commands", []) or [])
    for fragment in (
        "probe_external_platform.py --strict",
        "probe_maniskill_task_bindings.py --strict",
        "probe_maniskill_env_smoke.py --strict",
        "audit_external_backend_contract.py --strict",
        "materialize_external_configs.py",
        "validate_external_configs.py --strict",
        "materialize_fidelity_acceptance.py",
        "audit_external_fidelity_acceptance.py --strict",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write --check-video-paths",
        "validate_external_rollouts.py",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_release_package.py --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in strict_onboarding_commands:
            fail(f"external platform onboarding missing strict command: {fragment}")
    if onboarding_audit.get("version") != "external_platform_onboarding_audit_v1":
        fail("external platform onboarding audit version mismatch")
    if onboarding_audit.get("passed") is not True:
        fail("external platform onboarding audit did not pass")
    if onboarding_audit.get("not_external_evidence") is not True:
        fail("external platform onboarding audit must declare that it is not evidence")
    if onboarding_audit.get("platform_onboarding_ready") is not True or onboarding_audit.get("strict_evidence_ready") is not False:
        fail("external platform onboarding audit must be ready while strict evidence remains false")
    onboarding_checks = {entry.get("name"): entry.get("passed") for entry in onboarding_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "primary_route_matches_independent_plan",
        "task_onboarding_covers_collection_plan",
        "record_budget_preserved",
        "all_remaining_blockers_addressed",
        "official_sources_are_primary_and_currently_checked",
        "platform_provenance_fields_cover_fidelity_hashes_and_observations",
        "platform_probe_report_ready",
        "task_binding_probe_report_ready",
        "env_smoke_probe_report_ready",
        "primary_install_probe_has_machine_probe_command",
        "pilot_sequence_preserves_gate_order",
    ):
        if onboarding_checks.get(required_check) is not True:
            fail(f"external platform onboarding audit missing passing check: {required_check}")

    fidelity_acceptance_path = RESULTS / "external_fidelity_acceptance_audit.json"
    if not fidelity_acceptance_path.exists():
        fail("missing results/external_fidelity_acceptance_audit.json; run scripts/audit_external_fidelity_acceptance.py")
    fidelity_acceptance = json.loads(fidelity_acceptance_path.read_text(encoding="utf-8"))
    if fidelity_acceptance.get("version") != "external_fidelity_acceptance_audit_v1":
        fail("external fidelity acceptance audit version mismatch")
    if fidelity_acceptance.get("passed") is not True:
        fail("external fidelity acceptance audit did not pass")
    if fidelity_acceptance.get("not_external_evidence") is not True:
        fail("external fidelity acceptance audit must declare that it is not rollout evidence")
    if fidelity_acceptance.get("acceptance_ready") is not False:
        fail("external fidelity acceptance must not be ready before a real platform acceptance file exists")
    if fidelity_acceptance.get("readiness_state") != "COLLECT_PLATFORM_PROVENANCE":
        fail("external fidelity acceptance should currently require platform provenance collection")
    if int(fidelity_acceptance.get("blocking_missing_count", 0)) < 10:
        fail("external fidelity acceptance audit should expose missing platform/provenance items")
    if any("manifest_exists" in str(item) for item in fidelity_acceptance.get("blocking_missing", [])):
        fail("external fidelity acceptance audit must not require the official manifest before precollection acceptance")
    if not any(check.get("name") == "task_fidelity_covers_core_tasks" and check.get("passed") is True for check in fidelity_acceptance.get("contract_checks", [])):
        fail("external fidelity acceptance contract must cover the core external task families")
    fidelity_evidence_checks = {check.get("name"): check.get("passed") for check in fidelity_acceptance.get("evidence_checks", [])}
    for required_missing_check in (
        "real_acceptance_declares_ready",
        "not_draft_only",
        "strict_readiness_remains_external_to_acceptance",
        "date_locked_iso_like",
        "code_commit_sha40",
        "precollection_confirmation_booleans_true",
        "postcollection_evidence_deferred_until_manifest",
        "materialized_by_guarded_path",
    ):
        if required_missing_check not in fidelity_evidence_checks:
            fail(f"external fidelity acceptance audit missing evidence check: {required_missing_check}")
    if not (EXTERNAL / "fidelity_acceptance_template.json").exists():
        fail("missing external_validation/fidelity_acceptance_template.json")
    if not (RESULTS / "external_fidelity_acceptance_audit.md").exists():
        fail("missing results/external_fidelity_acceptance_audit.md")

    fidelity_acceptance_self_test_path = RESULTS / "external_fidelity_acceptance_self_test.json"
    if not fidelity_acceptance_self_test_path.exists():
        fail("missing results/external_fidelity_acceptance_self_test.json; run scripts/self_test_external_fidelity_acceptance.py")
    if not (ROOT / "scripts" / "self_test_external_fidelity_acceptance.py").exists():
        fail("missing scripts/self_test_external_fidelity_acceptance.py")
    fidelity_acceptance_self_test = json.loads(fidelity_acceptance_self_test_path.read_text(encoding="utf-8"))
    if fidelity_acceptance_self_test.get("version") != "external_fidelity_acceptance_self_test_v1":
        fail("external fidelity acceptance self-test version mismatch")
    if fidelity_acceptance_self_test.get("passed") is not True:
        fail("external fidelity acceptance self-test did not pass")
    if fidelity_acceptance_self_test.get("not_external_evidence") is not True:
        fail("external fidelity acceptance self-test must declare that it is not evidence")
    if fidelity_acceptance_self_test.get("synthetic_acceptance_ready") is not True:
        fail("external fidelity acceptance self-test should make a temporary acceptance fixture ready")
    if fidelity_acceptance_self_test.get("template_acceptance_ready") is not False:
        fail("external fidelity acceptance self-test should keep the template path fail-closed")
    fidelity_acceptance_self_checks = {check.get("name"): check.get("passed") for check in fidelity_acceptance_self_test.get("checks", [])}
    for required_check in (
        "synthetic_strict_acceptance_ready",
        "synthetic_route_task_count",
        "synthetic_platform_modalities",
        "synthetic_strict_provenance_guards",
        "template_acceptance_fails_strict_evidence",
        "template_strict_provenance_guards_fail_closed",
        "real_fidelity_report_not_overwritten",
    ):
        if fidelity_acceptance_self_checks.get(required_check) is not True:
            fail(f"external fidelity acceptance self-test missing passing check: {required_check}")
    if not (RESULTS / "external_fidelity_acceptance_self_test.md").exists():
        fail("missing results/external_fidelity_acceptance_self_test.md")

    pairing_integrity_path = RESULTS / "external_pairing_integrity_audit.json"
    if not pairing_integrity_path.exists():
        fail("missing results/external_pairing_integrity_audit.json; run scripts/audit_external_pairing_integrity.py")
    pairing_integrity = json.loads(pairing_integrity_path.read_text(encoding="utf-8"))
    if pairing_integrity.get("version") != "external_pairing_integrity_audit_v1":
        fail("external pairing integrity audit version mismatch")
    if pairing_integrity.get("passed") is not True:
        fail("external pairing integrity audit did not pass")
    if pairing_integrity.get("pairing_ready") is not False:
        fail("external pairing integrity must not claim readiness before a real manifest/log package exists")
    if pairing_integrity.get("not_external_evidence") is not True:
        fail("external pairing integrity audit must declare that it is not current evidence")
    if not any("manifest.json" in str(item) for item in pairing_integrity.get("blocking_missing", [])):
        fail("external pairing integrity audit should identify the missing real manifest")
    if not (RESULTS / "external_pairing_integrity_audit.md").exists():
        fail("missing results/external_pairing_integrity_audit.md")

    pairing_integrity_self_test_path = RESULTS / "external_pairing_integrity_self_test.json"
    if not pairing_integrity_self_test_path.exists():
        fail("missing results/external_pairing_integrity_self_test.json; run scripts/self_test_external_pairing_integrity.py")
    if not (ROOT / "scripts" / "self_test_external_pairing_integrity.py").exists():
        fail("missing scripts/self_test_external_pairing_integrity.py")
    pairing_integrity_self_test = json.loads(pairing_integrity_self_test_path.read_text(encoding="utf-8"))
    if pairing_integrity_self_test.get("version") != "external_pairing_integrity_self_test_v1":
        fail("external pairing integrity self-test version mismatch")
    if pairing_integrity_self_test.get("passed") is not True:
        fail("external pairing integrity self-test did not pass")
    if pairing_integrity_self_test.get("not_external_evidence") is not True:
        fail("external pairing integrity self-test must declare that it is not evidence")
    if pairing_integrity_self_test.get("synthetic_pairing_ready") is not True:
        fail("external pairing integrity self-test should make temporary complete method panels ready")
    for field in ("duplicate_pairing_ready", "missing_method_pairing_ready", "terminal_mismatch_pairing_ready", "missing_manifest_ready"):
        if pairing_integrity_self_test.get(field) is not False:
            fail(f"external pairing integrity self-test should reject {field}")
    pairing_integrity_self_checks = {check.get("name"): check.get("passed") for check in pairing_integrity_self_test.get("checks", [])}
    for required_check in (
        "synthetic_pairing_integrity_passes",
        "missing_manifest_fails_pairing_readiness",
        "duplicate_method_rows_fail_pairing",
        "missing_method_panel_fails_pairing",
        "terminal_sample_mismatch_fails_pairing",
        "real_pairing_integrity_report_not_overwritten",
    ):
        if pairing_integrity_self_checks.get(required_check) is not True:
            fail(f"external pairing integrity self-test missing passing check: {required_check}")
    if not (RESULTS / "external_pairing_integrity_self_test.md").exists():
        fail("missing results/external_pairing_integrity_self_test.md")

    release_package_path = RESULTS / "external_release_package_audit.json"
    if not release_package_path.exists():
        fail("missing results/external_release_package_audit.json; run scripts/audit_external_release_package.py")
    release_package = json.loads(release_package_path.read_text(encoding="utf-8"))
    if release_package.get("version") != "external_release_package_audit_v1":
        fail("external release package audit version mismatch")
    if release_package.get("passed") is not True:
        fail("external release package audit did not pass")
    if release_package.get("release_package_ready") is not False:
        fail("external release package must not claim readiness before a real manifest/log package exists")
    if release_package.get("not_external_evidence") is not True:
        fail("external release package audit must declare that it is not current evidence")
    if not any("manifest.json" in str(item) for item in release_package.get("blocking_missing", [])):
        fail("external release package audit should identify the missing real manifest")
    if not (RESULTS / "external_release_package_audit.md").exists():
        fail("missing results/external_release_package_audit.md")

    release_package_self_test_path = RESULTS / "external_release_package_self_test.json"
    if not release_package_self_test_path.exists():
        fail("missing results/external_release_package_self_test.json; run scripts/self_test_external_release_package.py")
    if not (ROOT / "scripts" / "self_test_external_release_package.py").exists():
        fail("missing scripts/self_test_external_release_package.py")
    release_package_self_test = json.loads(release_package_self_test_path.read_text(encoding="utf-8"))
    if release_package_self_test.get("version") != "external_release_package_self_test_v1":
        fail("external release package self-test version mismatch")
    if release_package_self_test.get("passed") is not True:
        fail("external release package self-test did not pass")
    if release_package_self_test.get("not_external_evidence") is not True:
        fail("external release package self-test must declare that it is not evidence")
    if release_package_self_test.get("synthetic_release_package_ready") is not True:
        fail("external release package self-test should make temporary manifest-declared release artifacts ready")
    if release_package_self_test.get("bad_release_package_ready") is not False:
        fail("external release package self-test should reject bad local-dry-run/template/scaffold/placeholder/staged/backup/diagnostic artifacts")
    if release_package_self_test.get("missing_manifest_ready") is not False:
        fail("external release package self-test should reject a missing manifest")
    release_audit_text = (ROOT / "scripts" / "audit_external_release_package.py").read_text(encoding="utf-8")
    release_self_test_text = (ROOT / "scripts" / "self_test_external_release_package.py").read_text(encoding="utf-8")
    for release_guard_term in (
        "FORBIDDEN_RELEASE_LOG_VIDEO_FRAGMENTS",
        "inspect_video_artifact",
        "video directory contains no MP4 files",
        "video artifact is not MP4-like evidence with an ftyp box",
        "staging",
        "backup",
        "diagnostic",
        "fallback",
    ):
        if release_guard_term not in release_audit_text:
            fail(f"external release package audit missing internal-artifact rejection term: {release_guard_term}")
    for release_fixture in (
        "peg_place_regrasp.staging.jsonl",
        "peg_place_regrasp.backup.jsonl",
        "peg_place_regrasp.diagnostic.mp4",
        "peg_place_regrasp.fallback.mp4",
        "peg_place_regrasp.backup.mp4",
        "empty_video_dir",
        "video directory contains no MP4 files",
    ):
        if release_fixture not in release_self_test_text:
            fail(f"external release package self-test missing internal-artifact rejection fixture: {release_fixture}")
    release_package_self_checks = {check.get("name"): check.get("passed") for check in release_package_self_test.get("checks", [])}
    for required_check in (
        "synthetic_release_package_passes",
        "missing_manifest_fails_release_readiness",
        "bad_artifacts_rejected_as_release_evidence",
        "release_hashes_are_recomputed",
        "real_release_package_report_not_overwritten",
    ):
        if release_package_self_checks.get(required_check) is not True:
            fail(f"external release package self-test missing passing check: {required_check}")
    if not (RESULTS / "external_release_package_self_test.md").exists():
        fail("missing results/external_release_package_self_test.md")

    manifest_builder_self_test_path = RESULTS / "external_manifest_builder_self_test.json"
    if not manifest_builder_self_test_path.exists():
        fail("missing results/external_manifest_builder_self_test.json; run scripts/self_test_external_manifest_builder.py")
    if not (ROOT / "scripts" / "self_test_external_manifest_builder.py").exists():
        fail("missing scripts/self_test_external_manifest_builder.py")
    manifest_builder_self_test = json.loads(manifest_builder_self_test_path.read_text(encoding="utf-8"))
    if manifest_builder_self_test.get("version") != "external_manifest_builder_self_test_v1":
        fail("external manifest builder self-test version mismatch")
    if manifest_builder_self_test.get("passed") is not True:
        fail("external manifest builder self-test did not pass")
    if manifest_builder_self_test.get("not_external_evidence") is not True:
        fail("external manifest builder self-test must declare that it is not evidence")
    if manifest_builder_self_test.get("synthetic_manifest_written") is not True:
        fail("external manifest builder self-test should write a temporary complete manifest")
    if int(manifest_builder_self_test.get("synthetic_records_loaded", 0) or 0) < 1440:
        fail("external manifest builder self-test should load the full temporary 1,440-record panel")
    if manifest_builder_self_test.get("real_template_ready_to_write_manifest") is not False:
        fail("external manifest builder self-test should keep the real template fail-closed")
    if manifest_builder_self_test.get("real_manifest_and_reports_unchanged") is not True:
        fail("external manifest builder self-test must not overwrite the real manifest or manifest-builder reports")
    manifest_builder_self_checks = {check.get("name"): check.get("passed") for check in manifest_builder_self_test.get("checks", [])}
    for required_check in (
        "synthetic_manifest_builder_ready",
        "synthetic_manifest_written_to_temp_output",
        "raw_logs_drive_manifest_metrics",
        "release_artifacts_scanned_from_temp_workspace",
        "config_and_method_hashes_materialized",
        "manifest_report_and_checklist_written_in_temp_workspace",
        "partial_manifest_with_missing_method_refuses_write",
        "real_manifest_template_remains_fail_closed",
        "real_manifest_and_reports_not_overwritten",
    ):
        if manifest_builder_self_checks.get(required_check) is not True:
            fail(f"external manifest builder self-test missing passing check: {required_check}")
    if not (RESULTS / "external_manifest_builder_self_test.md").exists():
        fail("missing results/external_manifest_builder_self_test.md")

    manifest_builder_text = (ROOT / "scripts" / "build_external_manifest.py").read_text(encoding="utf-8")
    if (
        "CORE_CODE_ARTIFACTS" not in manifest_builder_text
        or "release[\"code\"]" not in manifest_builder_text
        or "manifest_assembly_checklist.csv" not in manifest_builder_text
    ):
        fail("external manifest builder must populate release_artifacts.code and the manifest assembly checklist")

    blind_eval_path = RESULTS / "external_blind_eval_audit.json"
    if not blind_eval_path.exists():
        fail("missing results/external_blind_eval_audit.json; run scripts/build_external_blind_eval_plan.py")
    blind_eval = json.loads(blind_eval_path.read_text(encoding="utf-8"))
    if blind_eval.get("version") != "external_blind_eval_plan_v1":
        fail("external blind evaluation audit version mismatch")
    if blind_eval.get("passed") is not True:
        fail("external blind evaluation audit did not pass")
    if blind_eval.get("not_external_evidence") is not True:
        fail("external blind evaluation audit must declare that it is not evidence")
    if int(blind_eval.get("row_count", 0)) < 1440:
        fail("external blind evaluation audit has too few blinded rows")
    if int(blind_eval.get("alias_count", 0)) < 12:
        fail("external blind evaluation audit has too few method aliases")
    blind_checks = {check.get("name"): check.get("passed") for check in blind_eval.get("checks", [])}
    for required_check in (
        "blinded_sheet_has_no_method_names",
        "run_order_varies_by_reset",
        "every_reset_has_all_aliases",
        "protocol_contains_anti_leakage_terms",
    ):
        if blind_checks.get(required_check) is not True:
            fail(f"external blind evaluation audit missing passing check: {required_check}")
    for path in (
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
        RESULTS / "external_blind_eval_audit.md",
    ):
        if not path.exists():
            fail(f"missing external blind evaluation artifact: {path}")

    runbook_audit_path = RESULTS / "external_runbook_audit.json"
    if not runbook_audit_path.exists():
        fail("missing results/external_runbook_audit.json; run scripts/build_external_runbook.py")
    runbook_audit = json.loads(runbook_audit_path.read_text(encoding="utf-8"))
    if runbook_audit.get("version") != "external_runbook_audit_v1":
        fail("external runbook audit version mismatch")
    if runbook_audit.get("passed") is not True:
        fail("external runbook audit did not pass")
    if runbook_audit.get("not_external_evidence") is not True:
        fail("external runbook audit must declare that it is not evidence")
    if int(runbook_audit.get("operator_rows", 0)) < 1440:
        fail("external runbook operator sheet has too few rows")
    if len(runbook_audit.get("task_cards", [])) < 4:
        fail("external runbook has too few task cards")
    if len(runbook_audit.get("config_templates", [])) < 4:
        fail("external runbook has too few config templates")
    if int(runbook_audit.get("validation_command_count", 0)) < 40:
        fail("external runbook has too few validation commands for the current route")
    runbook_checks = {entry.get("name"): entry.get("passed") for entry in runbook_audit.get("checks", [])}
    for required_check in (
        "current_maniskill_route_gates_present",
        "gate_order_preserves_preflight_before_collection_and_evidence",
    ):
        if runbook_checks.get(required_check) is not True:
            fail(f"external runbook audit missing passing check: {required_check}")
    required_runbook_files = [
        EXTERNAL / "collection_runbook.md",
        EXTERNAL / "operator_record_sheet.csv",
    ]
    for path in required_runbook_files:
        if not path.exists():
            fail(f"missing external runbook artifact: {path}")

    runner_harness_path = RESULTS / "external_runner_harness_audit.json"
    if not runner_harness_path.exists():
        fail("missing results/external_runner_harness_audit.json; run scripts/audit_external_runner_harness.py")
    runner_harness = json.loads(runner_harness_path.read_text(encoding="utf-8"))
    if runner_harness.get("version") != "external_runner_harness_audit_v1":
        fail("external runner harness audit version mismatch")
    if runner_harness.get("passed") is not True:
        fail("external runner harness audit did not pass")
    if runner_harness.get("not_external_evidence") is not True:
        fail("external runner harness audit must declare that it is not evidence")
    if runner_harness.get("runner_harness_ready") is not True:
        fail("external runner harness is not ready")
    if runner_harness.get("actual_execution_ready") is not False:
        fail("external runner harness must not claim actual execution is ready before real backend/configs exist")
    runner_checks = {check.get("name"): check.get("passed") for check in runner_harness.get("checks", [])}
    for required_check in (
        "runner_files_exist",
        "backend_contract_api_complete",
        "backend_contract_fail_closed",
        "runner_dry_run_passes_without_writes",
        "runner_rejects_template_backend_for_actual_collection",
        "runner_rejects_diagnostic_or_non_mp4_videos_before_jsonl_write",
        "runner_rejects_schema_invalid_records_before_jsonl_write",
        "runner_promotes_jsonl_only_after_batch_success",
        "runner_promotes_videos_and_jsonl_only_after_batch_success",
        "no_real_manifest_written",
    ):
        if runner_checks.get(required_check) is not True:
            fail(f"external runner harness audit missing passing check: {required_check}")
    runner_text = (EXTERNAL / "runner" / "real_collection_runner.py").read_text(encoding="utf-8")
    for required_term in (
        "validate_official_video",
        "MIN_OFFICIAL_VIDEO_BYTES",
        "diagnostic fallback video sidecar",
        "ftyp",
        "validate_official_record",
        "validate_external_rollouts",
        "schema-invalid official JSONL record",
        "promote_pending_logs",
        "stage_log_path",
        "backup_log_path",
        "stage_video_path",
        "backup_video_path",
        "promote_pending_artifacts",
        "pending_log_lines",
        "pending_videos",
    ):
        if required_term not in runner_text:
            fail(f"external runner missing official evidence write guard term: {required_term}")
    for path in (
        EXTERNAL / "runner" / "README.md",
        EXTERNAL / "runner" / "backend_contract.py",
        EXTERNAL / "runner" / "real_collection_runner.py",
        EXTERNAL / "runner" / "backend_templates" / "maniskill_backend.py",
        EXTERNAL / "runner" / "backend_templates" / "mujoco_robosuite_backend.py",
        EXTERNAL / "runner" / "backend_templates" / "isaac_backend.py",
        EXTERNAL / "runner" / "backend_templates" / "robot_lab_backend.py",
        RESULTS / "external_runner_harness_audit.md",
    ):
        if not path.exists():
            fail(f"missing external runner harness artifact: {path}")

    backend_contract_path = RESULTS / "external_backend_contract_audit.json"
    if not backend_contract_path.exists():
        fail("missing results/external_backend_contract_audit.json; run scripts/audit_external_backend_contract.py")
    backend_contract = json.loads(backend_contract_path.read_text(encoding="utf-8"))
    if backend_contract.get("version") != "external_backend_contract_audit_v1":
        fail("external backend contract audit version mismatch")
    if backend_contract.get("passed") is not True:
        fail("external backend contract audit did not pass")
    if backend_contract.get("not_external_evidence") is not True:
        fail("external backend contract audit must declare that it is not evidence")
    if backend_contract.get("backend_contract_harness_ready") is not True:
        fail("external backend contract harness is not ready")
    if backend_contract.get("actual_backend_ready") is not False:
        fail("external backend contract audit must not claim a real backend is ready by default")
    if backend_contract.get("backend_required_for_collection") is not True:
        fail("external backend contract audit must require a backend before collection")
    if "audit_external_backend_contract.py --strict" not in str(backend_contract.get("strict_command", "")):
        fail("external backend contract audit must document the strict backend command")
    backend_contract_checks = {check.get("name"): check.get("passed") for check in backend_contract.get("checks", [])}
    for required_check in (
        "backend_contract_file_exists",
        "backend_contract_mentions_required_backend_api",
        "backend_contract_mentions_base_class",
        "backend_contract_mentions_validator",
        "backend_contract_mentions_base_implementation_rejection",
        "backend_templates_fail_closed",
        "runner_readme_declares_backend_audit",
        "contract_accepts_complete_synthetic_backend",
        "contract_rejects_incomplete_synthetic_backend",
    ):
        if backend_contract_checks.get(required_check) is not True:
            fail(f"external backend contract audit missing passing check: {required_check}")
    if backend_contract_checks.get("backend_module_supplied") is not False:
        fail("external backend contract audit should expose the missing real backend module in default mode")
    if not (RESULTS / "external_backend_contract_audit.md").exists():
        fail("missing results/external_backend_contract_audit.md")

    maniskill_backend_paths = [
        EXTERNAL / "runner" / "maniskill_reference_backend.py",
        ROOT / "scripts" / "audit_maniskill_backend_readiness.py",
        RESULTS / "maniskill_backend_readiness_audit.json",
        RESULTS / "maniskill_backend_readiness_audit.md",
    ]
    for path in maniskill_backend_paths:
        if not path.exists():
            fail(f"missing ManiSkill reference backend readiness artifact: {path}")
    maniskill_backend = json.loads((RESULTS / "maniskill_backend_readiness_audit.json").read_text(encoding="utf-8"))
    if maniskill_backend.get("version") != "maniskill_reference_backend_audit_v1":
        fail("ManiSkill reference backend readiness audit version mismatch")
    if maniskill_backend.get("passed") is not True:
        fail("ManiSkill reference backend readiness audit did not pass")
    if maniskill_backend.get("not_external_evidence") is not True:
        fail("ManiSkill reference backend readiness audit must declare that it is not evidence")
    if maniskill_backend.get("backend_module") != "external_validation.runner.maniskill_reference_backend":
        fail("ManiSkill reference backend audit should qualify the tracked backend module")
    if maniskill_backend.get("backend_contract_ready") is not True:
        fail("ManiSkill reference backend should pass the backend API/config contract")
    if maniskill_backend.get("reference_backend_available") is not True:
        fail("ManiSkill reference backend should be available as a non-evidence candidate")
    if maniskill_backend.get("reference_backend_collection_enabled") is not False:
        fail("ManiSkill reference backend collection must be disabled by default")
    if maniskill_backend.get("video_writer_ready") is not True:
        fail("ManiSkill reference backend should pass the synthetic MP4 writer check")
    if maniskill_backend.get("official_collection_ready") is not False:
        fail("ManiSkill reference backend audit must not mark official collection ready")
    if maniskill_backend.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill reference backend audit must not mark strict external evidence ready")
    if int(maniskill_backend.get("method_adapter_count", 0) or 0) < 12:
        fail("ManiSkill reference backend should cover all 12 reference adapters")
    backend_platform = maniskill_backend.get("platform_provenance", {}) or {}
    if backend_platform.get("render_backend") != "cpu":
        fail("ManiSkill reference backend provenance must record explicit render_backend=cpu")
    if backend_platform.get("shader_pack") != "minimal":
        fail("ManiSkill reference backend provenance must record explicit shader_pack=minimal")
    if int(backend_platform.get("render_width", 0) or 0) < 16 or int(backend_platform.get("render_height", 0) or 0) < 16:
        fail("ManiSkill reference backend provenance must record explicit render dimensions")
    maniskill_backend_checks = {check.get("name"): check.get("passed") for check in maniskill_backend.get("checks", [])}
    for required_check in (
        "backend_contract_strict_passes",
        "backend_is_non_template",
        "platform_provenance_marks_non_evidence",
        "delegates_to_reference_adapters",
        "official_collection_fail_closed_without_enable_flag",
        "video_export_fail_closed_before_reset",
        "synthetic_mp4_writer_passes",
        "state_shaped_arrays_rejected_as_video_frames",
        "strict_evidence_remains_false",
    ):
        if maniskill_backend_checks.get(required_check) is not True:
            fail(f"ManiSkill reference backend audit missing passing check: {required_check}")

    reference_preflight_paths = [
        ROOT / "scripts" / "audit_maniskill_reference_collection_preflight.py",
        RESULTS / "maniskill_reference_collection_preflight_audit.json",
        RESULTS / "maniskill_reference_collection_preflight_audit.md",
    ]
    for path in reference_preflight_paths:
        if not path.exists():
            fail(f"missing ManiSkill reference collection preflight artifact: {path}")
    reference_preflight = json.loads((RESULTS / "maniskill_reference_collection_preflight_audit.json").read_text(encoding="utf-8"))
    if reference_preflight.get("version") != "maniskill_reference_collection_preflight_audit_v1":
        fail("ManiSkill reference collection preflight audit version mismatch")
    if reference_preflight.get("passed") is not True:
        fail("ManiSkill reference collection preflight audit did not pass")
    if reference_preflight.get("not_external_evidence") is not True:
        fail("ManiSkill reference collection preflight audit must declare that it is not evidence")
    if reference_preflight.get("reference_backend_contract_ready") is not True:
        fail("ManiSkill reference backend should pass explicit strict backend-contract preflight")
    if reference_preflight.get("collection_ready") is not False:
        fail("ManiSkill reference collection preflight must not claim collection readiness")
    if reference_preflight.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill reference collection preflight must keep strict external evidence false")
    if int(reference_preflight.get("collection_blocking_missing_count", 0) or 0) != 1:
        fail("ManiSkill reference collection preflight should currently leave exactly one collection blocker")
    blockers = "\n".join(reference_preflight.get("collection_blocking_missing", []) or [])
    if "fidelity_acceptance_ready" not in blockers:
        fail("ManiSkill reference collection preflight should block on fidelity acceptance")
    reference_preflight_checks = {check.get("name"): check.get("passed") for check in reference_preflight.get("checks", [])}
    for required_check in (
        "reference_backend_contract_strict_passes",
        "reference_backend_collection_preflight_reaches_fidelity_gate",
        "official_collection_still_not_ready",
        "default_audits_are_not_overwritten",
    ):
        if reference_preflight_checks.get(required_check) is not True:
            fail(f"ManiSkill reference collection preflight audit missing passing check: {required_check}")

    backend_integration_paths = [
        EXTERNAL / "backend_integration_packet.json",
        EXTERNAL / "backend_integration_packet.md",
        EXTERNAL / "backend_integration_work_orders.csv",
        RESULTS / "external_backend_integration_audit.json",
        RESULTS / "external_backend_integration_audit.md",
        RESULTS / "external_backend_integration_packet_self_test.json",
        RESULTS / "external_backend_integration_packet_self_test.md",
        ROOT / "scripts" / "build_external_backend_integration_packet.py",
        ROOT / "scripts" / "self_test_external_backend_integration_packet.py",
    ]
    for path in backend_integration_paths:
        if not path.exists():
            fail(f"missing external backend integration packet artifact: {path}")
    backend_integration_packet = json.loads((EXTERNAL / "backend_integration_packet.json").read_text(encoding="utf-8"))
    if backend_integration_packet.get("version") != "external_backend_integration_packet_v1":
        fail("external backend integration packet version mismatch")
    if backend_integration_packet.get("not_external_evidence") is not True:
        fail("external backend integration packet must declare that it is not evidence")
    if backend_integration_packet.get("backend_integration_packet_ready") is not True:
        fail("external backend integration packet should be ready as a work-order packet")
    if backend_integration_packet.get("strict_backend_ready") is not False:
        fail("external backend integration packet must not claim strict backend readiness")
    if backend_integration_packet.get("strict_evidence_ready") is not False:
        fail("external backend integration packet must not claim strict external evidence")
    if backend_integration_packet.get("primary_route") != "maniskill_sapien_primary":
        fail("external backend integration packet should target the primary public-simulator route")
    if int(backend_integration_packet.get("planned_records", 0) or 0) < 1440:
        fail("external backend integration packet has too few planned records")
    required_hooks = set(backend_integration_packet.get("required_backend_hooks", []) or [])
    for hook in ("platform_provenance", "load_task_config", "reset_scene", "run_method", "execute_skill_pair", "record_video", "policy_or_config_hash"):
        if hook not in required_hooks:
            fail(f"external backend integration packet missing backend hook: {hook}")
    backend_command_text = "\n".join(backend_integration_packet.get("strict_acceptance_commands", []) or [])
    for fragment in (
        "build_external_backend_integration_packet.py",
        "audit_external_backend_contract.py --strict",
        "materialize_external_configs.py",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write",
        "validate_external_rollouts.py",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in backend_command_text:
            fail(f"external backend integration packet missing strict command fragment: {fragment}")
    backend_integration_audit = json.loads((RESULTS / "external_backend_integration_audit.json").read_text(encoding="utf-8"))
    if backend_integration_audit.get("version") != "external_backend_integration_audit_v1":
        fail("external backend integration audit version mismatch")
    if backend_integration_audit.get("passed") is not True:
        fail("external backend integration audit did not pass")
    if backend_integration_audit.get("not_external_evidence") is not True:
        fail("external backend integration audit must declare that it is not evidence")
    if backend_integration_audit.get("backend_integration_packet_ready") is not True:
        fail("external backend integration audit should report packet ready")
    if backend_integration_audit.get("strict_backend_ready") is not False:
        fail("external backend integration audit must keep strict backend readiness false")
    backend_integration_checks = {check.get("name"): check.get("passed") for check in backend_integration_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "primary_route_matches_onboarding",
        "backend_contract_harness_ready_but_backend_missing",
        "work_orders_cover_backend_to_manifest_path",
        "work_orders_are_actionable_and_artifact_bound",
        "required_hooks_declared",
        "provenance_fields_declared",
        "tasks_and_record_budget_preserved",
        "strict_commands_cover_backend_config_fidelity_collection_and_evidence",
        "collection_readiness_still_blocks_backend",
        "no_real_backend_files_created",
        "packet_files_written",
    ):
        if backend_integration_checks.get(required_check) is not True:
            fail(f"external backend integration audit missing passing check: {required_check}")
    backend_integration_self_test = json.loads((RESULTS / "external_backend_integration_packet_self_test.json").read_text(encoding="utf-8"))
    if backend_integration_self_test.get("version") != "external_backend_integration_packet_self_test_v1":
        fail("external backend integration packet self-test version mismatch")
    if backend_integration_self_test.get("passed") is not True:
        fail("external backend integration packet self-test did not pass")
    if backend_integration_self_test.get("not_external_evidence") is not True:
        fail("external backend integration packet self-test must declare non-evidence")
    if backend_integration_self_test.get("strict_backend_ready") is not False:
        fail("external backend integration packet self-test must keep strict backend readiness false")
    if backend_integration_self_test.get("strict_evidence_ready") is not False:
        fail("external backend integration packet self-test must keep strict evidence readiness false")
    for required_flag in (
        "temporary_packet_ready",
        "missing_work_orders_rejected",
        "work_order_artifact_command_drift_rejected",
        "premature_backend_evidence_promotion_rejected",
        "route_independence_drift_rejected",
        "actual_backend_promotion_rejected",
        "hook_contract_drift_rejected",
        "provenance_field_drift_rejected",
        "task_budget_shrink_rejected",
        "strict_command_drift_rejected",
        "collection_ready_promotion_rejected",
        "real_backend_file_write_rejected",
        "packet_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if backend_integration_self_test.get(required_flag) is not True:
            fail(f"external backend integration packet self-test missing true flag: {required_flag}")
    backend_integration_self_checks = {
        check.get("name"): check.get("passed")
        for check in backend_integration_self_test.get("checks", []) or []
    }
    for required_check in (
        "temporary_backend_integration_packet_ready_but_non_evidence",
        "missing_work_orders_rejected",
        "work_order_artifact_command_drift_rejected",
        "premature_backend_evidence_promotion_rejected",
        "route_independence_drift_rejected",
        "actual_backend_promotion_rejected",
        "hook_contract_drift_rejected",
        "provenance_field_drift_rejected",
        "task_budget_shrink_rejected",
        "strict_command_drift_rejected",
        "collection_ready_promotion_rejected",
        "real_backend_file_write_rejected",
        "packet_file_deletion_rejected",
        "real_backend_integration_outputs_untouched",
    ):
        if backend_integration_self_checks.get(required_check) is not True:
            fail(f"external backend integration packet self-test missing passing check: {required_check}")

    backend_contract_self_test_path = RESULTS / "external_backend_contract_self_test.json"
    if not backend_contract_self_test_path.exists():
        fail("missing results/external_backend_contract_self_test.json; run scripts/self_test_external_backend_contract.py")
    if not (ROOT / "scripts" / "self_test_external_backend_contract.py").exists():
        fail("missing scripts/self_test_external_backend_contract.py")
    backend_contract_self_test = json.loads(backend_contract_self_test_path.read_text(encoding="utf-8"))
    if backend_contract_self_test.get("version") != "external_backend_contract_self_test_v1":
        fail("external backend contract self-test version mismatch")
    if backend_contract_self_test.get("passed") is not True:
        fail("external backend contract self-test did not pass")
    if backend_contract_self_test.get("not_external_evidence") is not True:
        fail("external backend contract self-test must declare that it is not evidence")
    if backend_contract_self_test.get("complete_backend_actual_ready") is not True:
        fail("external backend contract self-test should make a temporary complete backend actual-ready")
    backend_contract_self_checks = {check.get("name"): check.get("passed") for check in backend_contract_self_test.get("checks", [])}
    for required_check in (
        "strict_complete_backend_passes",
        "strict_incomplete_backend_fails",
        "strict_template_backend_fails",
        "default_missing_backend_remains_nonready",
        "real_backend_contract_report_not_overwritten",
    ):
        if backend_contract_self_checks.get(required_check) is not True:
            fail(f"external backend contract self-test missing passing check: {required_check}")
    if not (RESULTS / "external_backend_contract_self_test.md").exists():
        fail("missing results/external_backend_contract_self_test.md")

    collection_readiness_path = RESULTS / "external_collection_readiness_audit.json"
    if not collection_readiness_path.exists():
        fail("missing results/external_collection_readiness_audit.json; run scripts/audit_external_collection_readiness.py")
    collection_readiness = json.loads(collection_readiness_path.read_text(encoding="utf-8"))
    if collection_readiness.get("version") != "external_collection_readiness_audit_v1":
        fail("external collection readiness audit version mismatch")
    if collection_readiness.get("passed") is not True:
        fail("external collection readiness audit did not pass")
    if collection_readiness.get("not_external_evidence") is not True:
        fail("external collection readiness audit must declare that it is not evidence")
    if collection_readiness.get("collection_ready") is not False:
        fail("external collection readiness must not claim readiness before real backend/configs/fidelity exist")
    if int(collection_readiness.get("row_count", 0) or 0) < 1440:
        fail("external collection readiness audit has too few operator rows")
    if int(collection_readiness.get("alias_count", 0) or 0) < 12:
        fail("external collection readiness audit has too few method aliases")
    collection_readiness_checks = {check.get("name"): check.get("passed") for check in collection_readiness.get("checks", [])}
    for required_check in (
        "runner_exists",
        "schema_exists",
        "operator_sheet_exists",
        "operator_sheet_columns",
        "operator_sheet_row_budget",
        "alias_map_exists",
        "alias_map_complete",
        "output_logs_empty_or_force",
    ):
        if collection_readiness_checks.get(required_check) is not True:
            fail(f"external collection readiness audit missing passing check: {required_check}")
    for required_blocker in ("backend_module_ready", "fidelity_acceptance_ready", "alias_unsealing_explicit", "run_id_specific"):
        if collection_readiness_checks.get(required_blocker) is not False:
            fail(f"external collection readiness should currently fail closed on {required_blocker}")
    if collection_readiness_checks.get("real_task_configs_ready") is not True and collection_readiness_checks.get("real_task_configs_ready") is not False:
        fail("external collection readiness must explicitly audit real_task_configs_ready")
    collection_reference_route = collection_readiness.get("tracked_reference_route", {}) or {}
    collection_reference_blockers = collection_reference_route.get("blocking_missing", []) or []
    collection_reference_checks = {check.get("name"): check.get("passed") for check in collection_reference_route.get("checks", [])}
    if collection_reference_route.get("not_external_evidence") is not True:
        fail("external collection readiness tracked reference route must be marked non-evidence")
    if "maniskill_reference_backend.py" not in str(collection_reference_route.get("backend_module", "")):
        fail("external collection readiness tracked reference route must name the ManiSkill backend")
    if collection_reference_route.get("run_id") != "maniskill_sapien_reference_preflight_protocol_v1":
        fail("external collection readiness tracked reference route must use the locked reference run id")
    if collection_reference_route.get("collection_ready") is not False:
        fail("external collection readiness tracked reference route must preserve collection_ready=false until fidelity acceptance")
    if collection_reference_route.get("strict_external_evidence_ready") is not False:
        fail("external collection readiness tracked reference route must not claim strict evidence readiness")
    if int(collection_reference_route.get("blocking_missing_count", 99) or 99) != 1 or len(collection_reference_blockers) != 1 or "fidelity_acceptance_ready" not in collection_reference_blockers[0]:
        fail("external collection readiness tracked reference route must show fidelity acceptance as the single route blocker")
    if collection_reference_checks.get("reference_backend_contract_ready") is not True:
        fail("external collection readiness tracked reference route must audit reference backend contract readiness")
    if collection_reference_checks.get("reference_task_configs_ready") is not True:
        fail("external collection readiness tracked reference route must audit prepared task config readiness")
    if collection_reference_checks.get("reference_fidelity_acceptance_ready") is not False:
        fail("external collection readiness tracked reference route must keep fidelity acceptance fail-closed")
    if "audit_external_collection_readiness.py --strict" not in str(collection_reference_route.get("pre_collection_gate_command", "")) or "--unsealed-alias-map" not in str(collection_reference_route.get("pre_collection_gate_command", "")):
        fail("external collection readiness tracked reference route must include the strict pre-collection gate command")
    if "real_collection_runner.py" not in str(collection_reference_route.get("collection_command_after_fidelity_acceptance", "")) or "maniskill_reference_backend.py" not in str(collection_reference_route.get("collection_command_after_fidelity_acceptance", "")):
        fail("external collection readiness tracked reference route must include the concrete reference collection command")
    if not (RESULTS / "external_collection_readiness_audit.md").exists():
        fail("missing results/external_collection_readiness_audit.md")

    config_template_audit_path = RESULTS / "external_config_template_audit.json"
    if not config_template_audit_path.exists():
        fail("missing results/external_config_template_audit.json; run scripts/validate_external_configs.py")
    config_template_audit = json.loads(config_template_audit_path.read_text(encoding="utf-8"))
    if config_template_audit.get("version") != "external_config_template_audit_v1":
        fail("external config template audit version mismatch")
    if config_template_audit.get("passed") is not True:
        fail("external config template audit did not pass")
    if config_template_audit.get("not_external_evidence") is not True:
        fail("external config template audit must declare that it is not evidence")
    if int(config_template_audit.get("config_count", 0)) < 4:
        fail("external config template audit has too few templates")
    if not (EXTERNAL / "config_schema_v1.json").exists():
        fail("missing external_validation/config_schema_v1.json")

    config_evidence_self_test_path = RESULTS / "external_config_evidence_self_test.json"
    if not config_evidence_self_test_path.exists():
        fail("missing results/external_config_evidence_self_test.json; run scripts/self_test_external_config_evidence.py")
    if not (ROOT / "scripts" / "self_test_external_config_evidence.py").exists():
        fail("missing scripts/self_test_external_config_evidence.py")
    config_evidence_self_test = json.loads(config_evidence_self_test_path.read_text(encoding="utf-8"))
    if config_evidence_self_test.get("version") != "external_config_evidence_self_test_v1":
        fail("external config evidence self-test version mismatch")
    if config_evidence_self_test.get("passed") is not True:
        fail("external config evidence self-test did not pass")
    if config_evidence_self_test.get("not_external_evidence") is not True:
        fail("external config evidence self-test must declare that it is not evidence")
    if config_evidence_self_test.get("synthetic_config_evidence_ready") is not True:
        fail("external config evidence self-test should make temporary manifest-declared configs ready")
    if config_evidence_self_test.get("prepared_config_fixture_ready") is not True:
        fail("external config evidence self-test should pass strict validation with prepared configs and a temporary manifest")
    if int(config_evidence_self_test.get("prepared_config_count", 0) or 0) < 4:
        fail("external config evidence self-test should cover all prepared task configs")
    if config_evidence_self_test.get("stale_config_hash_ready") is not False:
        fail("external config evidence self-test should reject stale manifest config hashes")
    if config_evidence_self_test.get("template_config_evidence_ready") is not False:
        fail("external config evidence self-test should reject templates as strict evidence")
    if config_evidence_self_test.get("missing_manifest_ready") is not False:
        fail("external config evidence self-test should reject a missing manifest")
    config_evidence_self_checks = {check.get("name"): check.get("passed") for check in config_evidence_self_test.get("checks", [])}
    for required_check in (
        "synthetic_strict_configs_pass",
        "synthetic_manifest_entries_cover_tasks",
        "prepared_task_configs_pass_strict_with_temp_manifest",
        "prepared_task_config_methods_match_collection_tasks",
        "missing_manifest_fails_strict",
        "stale_manifest_config_hash_fails_strict",
        "template_configs_rejected_as_strict_evidence",
        "real_config_evidence_report_not_overwritten",
    ):
        if config_evidence_self_checks.get(required_check) is not True:
            fail(f"external config evidence self-test missing passing check: {required_check}")
    config_validator_text = (ROOT / "scripts" / "validate_external_configs.py").read_text(encoding="utf-8")
    config_self_test_text = (ROOT / "scripts" / "self_test_external_config_evidence.py").read_text(encoding="utf-8")
    for term in (
        "sha256_file",
        "is_sha256",
        "manifest config_hash is required for strict config evidence",
        "manifest config_hash must be 64-character SHA256",
        "manifest config_hash does not match config_path",
    ):
        if term not in config_validator_text:
            fail(f"external config validator missing strict config hash term: {term}")
    if "stale_manifest_config_hash_fails_strict" not in config_self_test_text:
        fail("external config evidence self-test must reject stale manifest config hashes")
    if not (RESULTS / "external_config_evidence_self_test.md").exists():
        fail("missing results/external_config_evidence_self_test.md")

    baseline_contract_path = RESULTS / "external_baseline_contract_audit.json"
    if not baseline_contract_path.exists():
        fail("missing results/external_baseline_contract_audit.json; run scripts/build_external_baseline_contract.py")
    baseline_contract = json.loads(baseline_contract_path.read_text(encoding="utf-8"))
    if baseline_contract.get("version") != "external_baseline_contract_audit_v1":
        fail("external baseline contract audit version mismatch")
    if baseline_contract.get("passed") is not True:
        fail("external baseline contract audit did not pass")
    if baseline_contract.get("not_external_evidence") is not True:
        fail("external baseline contract audit must declare that it is not evidence")
    if baseline_contract.get("implementations_ready") is not False:
        fail("external baseline contract must not claim independent implementations are ready")
    if int(baseline_contract.get("method_count", 0)) < 12:
        fail("external baseline contract has too few methods")
    if len(baseline_contract.get("missing_implementations", [])) < 11:
        fail("external baseline contract should still identify missing non-oracle implementations")
    if len(baseline_contract.get("spec_files", [])) < 12:
        fail("external baseline contract has too few method spec files")
    baseline_checks = {check.get("name"): check.get("passed") for check in baseline_contract.get("checks", [])}
    for required_check in (
        "all_required_methods_present",
        "spec_files_are_method_bound",
        "adapter_api_covers_required_methods",
        "fairness_invariants_declared",
        "specs_require_release_evidence",
        "specs_require_policy_config_hash_logs",
        "non_oracle_requires_independent_source",
        "oracle_post_hoc_only",
        "implementations_not_marked_ready",
    ):
        if baseline_checks.get(required_check) is not True:
            fail(f"external baseline contract audit missing passing check: {required_check}")
    required_baseline_contract_files = [
        EXTERNAL / "baseline_implementation_contract.md",
        EXTERNAL / "baseline_implementation_matrix.csv",
        ROOT / "scripts" / "self_test_external_baseline_contract.py",
        RESULTS / "external_baseline_contract_self_test.json",
        RESULTS / "external_baseline_contract_self_test.md",
    ]
    for path in required_baseline_contract_files:
        if not path.exists():
            fail(f"missing external baseline contract artifact: {path}")
    baseline_self_test = json.loads((RESULTS / "external_baseline_contract_self_test.json").read_text(encoding="utf-8"))
    if baseline_self_test.get("version") != "external_baseline_contract_self_test_v1":
        fail("external baseline contract self-test version mismatch")
    if baseline_self_test.get("passed") is not True:
        fail("external baseline contract self-test did not pass")
    if baseline_self_test.get("not_external_evidence") is not True:
        fail("external baseline contract self-test must declare that it is not evidence")
    if baseline_self_test.get("implementations_ready") is not False:
        fail("external baseline contract self-test must not claim implementations ready")
    for required_flag in (
        "temporary_contract_ready",
        "missing_required_method_rejected",
        "premature_implementation_promotion_rejected",
        "independent_source_drift_rejected",
        "oracle_boundary_drift_rejected",
        "fairness_invariant_shrink_rejected",
        "adapter_api_drift_rejected",
        "spec_method_binding_drift_rejected",
        "release_evidence_spec_drift_rejected",
        "policy_config_log_field_drift_rejected",
        "contract_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if baseline_self_test.get(required_flag) is not True:
            fail(f"external baseline contract self-test missing true flag: {required_flag}")
    baseline_self_checks = {check.get("name"): check.get("passed") for check in baseline_self_test.get("checks", []) or []}
    for required_check in (
        "temporary_baseline_contract_ready_but_non_evidence",
        "missing_required_method_rejected",
        "premature_implementation_promotion_rejected",
        "independent_source_drift_rejected",
        "oracle_boundary_drift_rejected",
        "fairness_invariant_shrink_rejected",
        "adapter_api_drift_rejected",
        "spec_method_binding_drift_rejected",
        "release_evidence_spec_drift_rejected",
        "policy_config_log_field_drift_rejected",
        "contract_file_deletion_rejected",
        "real_baseline_contract_outputs_untouched",
    ):
        if baseline_self_checks.get(required_check) is not True:
            fail(f"external baseline contract self-test missing passing check: {required_check}")

    adapter_scaffold_path = RESULTS / "external_adapter_scaffold_audit.json"
    if not adapter_scaffold_path.exists():
        fail("missing results/external_adapter_scaffold_audit.json; run scripts/build_external_adapter_scaffolds.py")
    adapter_scaffold = json.loads(adapter_scaffold_path.read_text(encoding="utf-8"))
    if adapter_scaffold.get("version") != "external_adapter_scaffold_audit_v1":
        fail("external adapter scaffold audit version mismatch")
    if adapter_scaffold.get("passed") is not True:
        fail("external adapter scaffold audit did not pass")
    if adapter_scaffold.get("not_external_evidence") is not True:
        fail("external adapter scaffold audit must declare that it is not evidence")
    if adapter_scaffold.get("implementations_ready") is not False:
        fail("external adapter scaffold must not claim independent implementations are ready")
    if int(adapter_scaffold.get("method_count", 0)) < 12:
        fail("external adapter scaffold has too few methods")
    if int(adapter_scaffold.get("non_oracle_scaffold_count", 0)) < 11:
        fail("external adapter scaffold has too few non-oracle method templates")
    required_adapter_scaffold_files = [
        EXTERNAL / "baseline_adapter_scaffold.md",
        EXTERNAL / "baselines" / "README.md",
        EXTERNAL / "baselines" / "barrier_certified_energy_composer_v5" / "adapter_template.py",
        EXTERNAL / "baselines" / "barrier_certified_energy_composer_v5" / "adapter_metadata.json",
    ]
    for path in required_adapter_scaffold_files:
        if not path.exists():
            fail(f"missing external adapter scaffold artifact: {path}")
    scaffold_guard_self_test_path = RESULTS / "external_adapter_scaffold_guard_self_test.json"
    scaffold_guard_self_test_md_path = RESULTS / "external_adapter_scaffold_guard_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_adapter_scaffold_guard.py",
        scaffold_guard_self_test_path,
        scaffold_guard_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external adapter scaffold guard self-test artifact: {path}")
    scaffold_guard_self_test = json.loads(scaffold_guard_self_test_path.read_text(encoding="utf-8"))
    if scaffold_guard_self_test.get("version") != "external_adapter_scaffold_guard_self_test_v1":
        fail("external adapter scaffold guard self-test version mismatch")
    if scaffold_guard_self_test.get("passed") is not True:
        fail("external adapter scaffold guard self-test did not pass")
    if scaffold_guard_self_test.get("not_external_evidence") is not True:
        fail("external adapter scaffold guard self-test must declare that it is not evidence")
    if scaffold_guard_self_test.get("scaffold_directory_detected") is not True:
        fail("external adapter scaffold guard self-test must detect scaffold directories")
    if scaffold_guard_self_test.get("scaffold_template_detected") is not True:
        fail("external adapter scaffold guard self-test must detect scaffold templates")
    if scaffold_guard_self_test.get("ordinary_adapter_falsely_rejected") is not False:
        fail("external adapter scaffold guard self-test must not reject ordinary replacement adapters")
    if scaffold_guard_self_test.get("temporary_adapter_file_removed") is not True:
        fail("external adapter scaffold guard self-test must remove temporary adapter files")
    if scaffold_guard_self_test.get("real_adapter_reports_untouched") is not True:
        fail("external adapter scaffold guard self-test must leave real adapter reports untouched")
    scaffold_guard_checks = {check.get("name"): check.get("passed") for check in scaffold_guard_self_test.get("checks", [])}
    for required_check in (
        "scaffold_directory_detected",
        "scaffold_template_detected",
        "ordinary_replacement_adapter_not_flagged",
        "temporary_adapter_file_removed",
        "real_adapter_reports_untouched",
    ):
        if scaffold_guard_checks.get(required_check) is not True:
            fail(f"external adapter scaffold guard self-test missing passing check: {required_check}")

    reference_adapter_path = RESULTS / "external_reference_adapter_audit.json"
    if not reference_adapter_path.exists():
        fail("missing results/external_reference_adapter_audit.json; run scripts/build_external_reference_adapters.py")
    reference_adapter = json.loads(reference_adapter_path.read_text(encoding="utf-8"))
    if reference_adapter.get("version") != "external_reference_adapter_audit_v1":
        fail("external reference adapter audit version mismatch")
    if reference_adapter.get("passed") is not True:
        fail("external reference adapter audit did not pass")
    if reference_adapter.get("not_external_evidence") is not True:
        fail("external reference adapter audit must declare that it is not evidence")
    if reference_adapter.get("implementation_only_not_rollout_evidence") is not True:
        fail("external reference adapter audit must remain implementation-only")
    if int(reference_adapter.get("adapter_count", 0)) < 12:
        fail("external reference adapter audit has too few adapters")
    if int(reference_adapter.get("non_oracle_adapter_count", 0)) < 11:
        fail("external reference adapter audit has too few non-oracle adapters")
    failed_reference_adapters = [item for item in reference_adapter.get("adapter_results", []) if item.get("passed") is not True]
    if failed_reference_adapters:
        fail(f"external reference adapters failed: {failed_reference_adapters[:4]}")
    reference_adapter_checks = {check.get("name"): check.get("passed") for check in reference_adapter.get("checks", [])}
    if reference_adapter_checks.get("reference_adapter_behavior_contract_passes_non_strict") is not True:
        fail("external reference adapter audit must prove the non-strict behavior/API contract")
    required_reference_adapter_files = [
        EXTERNAL / "baselines" / "common_reference_adapter.py",
        EXTERNAL / "baselines" / "barrier_certified_energy_composer_v5" / "adapter.py",
        EXTERNAL / "baselines" / "barrier_certified_energy_composer_v5" / "reference_adapter_metadata.json",
        EXTERNAL / "reference_adapter_report.md",
    ]
    for path in required_reference_adapter_files:
        if not path.exists():
            fail(f"missing external reference adapter artifact: {path}")

    dry_run_path = RESULTS / "external_local_dry_run_metrics.json"
    if not dry_run_path.exists():
        fail("missing results/external_local_dry_run_metrics.json; run scripts/build_external_local_dry_run.py")
    dry_run = json.loads(dry_run_path.read_text(encoding="utf-8"))
    if dry_run.get("version") != "external_local_dry_run_metrics_v1":
        fail("external local dry-run metrics version mismatch")
    if dry_run.get("passed") is not True:
        fail("external local dry-run metrics did not pass")
    if dry_run.get("not_external_evidence") is not True:
        fail("external local dry run must declare that it is not evidence")
    if dry_run.get("schema_errors"):
        fail(f"external local dry run has schema errors: {dry_run.get('schema_errors')[:4]}")
    dry_summary = dry_run.get("summary", {})
    if dry_summary.get("version") != "external_rollout_metrics_v1":
        fail("external local dry run summary version mismatch")
    if int(dry_summary.get("episodes", 0)) < 1440:
        fail("external local dry run has too few schema-compatible records")
    if int(dry_summary.get("external_task_families", 0)) < 4:
        fail("external local dry run has too few task families")
    if len(dry_summary.get("methods", [])) < 12:
        fail("external local dry run has too few methods")
    if int(dry_summary.get("positive_task_families", 0)) < 4:
        fail("external local dry run should preserve positive dry-run task-family margins")
    failed_dry_thresholds = [check for check in dry_run.get("threshold_checks", []) if check.get("passed") is not True]
    if failed_dry_thresholds:
        fail(f"external local dry-run thresholds failed: {failed_dry_thresholds[:4]}")
    dry_manifest_path = EXTERNAL / "local_dry_run" / "manifest.json"
    if not dry_manifest_path.exists():
        fail("missing external_validation/local_dry_run/manifest.json")
    dry_manifest = json.loads(dry_manifest_path.read_text(encoding="utf-8"))
    if dry_manifest.get("not_external_evidence") is not True or dry_manifest.get("local_dry_run_only") is not True:
        fail("external local dry-run manifest must remain explicitly non-evidence")

    local_model_release_path = RESULTS / "local_model_release_manifest.json"
    local_model_release_audit_path = RESULTS / "local_model_release_audit.json"
    local_model_release_card_path = DOCS / "local_model_release.md"
    if not local_model_release_path.exists():
        fail("missing results/local_model_release_manifest.json; run scripts/build_local_model_release.py")
    if not local_model_release_audit_path.exists():
        fail("missing results/local_model_release_audit.json; run scripts/build_local_model_release.py")
    if not local_model_release_card_path.exists():
        fail("missing docs/local_model_release.md; run scripts/build_local_model_release.py")
    local_model_release = json.loads(local_model_release_path.read_text(encoding="utf-8"))
    local_model_release_audit = json.loads(local_model_release_audit_path.read_text(encoding="utf-8"))
    if local_model_release.get("version") != "paper119_local_model_release_v1":
        fail("local model release manifest version mismatch")
    if local_model_release_audit.get("version") != "paper119_local_model_release_audit_v1":
        fail("local model release audit version mismatch")
    if local_model_release.get("not_external_evidence") is not True or local_model_release_audit.get("not_external_evidence") is not True:
        fail("local model release must declare that it is not external evidence")
    if local_model_release.get("local_model_release_ready") is not True or local_model_release_audit.get("local_model_release_ready") is not True:
        fail("local model release must be ready as a reproducibility artifact")
    if local_model_release.get("external_evidence_ready") is not False or local_model_release_audit.get("external_evidence_ready") is not False:
        fail("local model release must not claim external evidence readiness")
    if local_model_release.get("does_not_release_trained_robot_policy") is not True:
        fail("local model release must state that it is not a trained robot policy checkpoint")
    if local_model_release.get("does_not_release_real_robot_checkpoint") is not True:
        fail("local model release must state that it is not a real robot checkpoint")
    if local_model_release.get("source", {}).get("version") != "v5_expanded":
        fail("local model release source version mismatch")
    if int(local_model_release.get("dimensions", {}).get("method_count", 0) or 0) < 12:
        fail("local model release has too few methods")
    if int(local_model_release.get("dimensions", {}).get("task_count", 0) or 0) < 6:
        fail("local model release has too few local tasks")
    proposed_release = local_model_release.get("proposed_method", {}) or {}
    if proposed_release.get("name") != "barrier_certified_energy_composer_v5":
        fail("local model release proposed method mismatch")
    if len(str(proposed_release.get("parameter_hash", ""))) != 64:
        fail("local model release proposed method hash is missing or malformed")
    if len(str(local_model_release.get("release_hash", ""))) != 64:
        fail("local model release hash is missing or malformed")
    missing_release_artifacts = [
        item
        for item in (local_model_release.get("result_artifacts", []) or [])
        if item.get("exists") is not True or len(str(item.get("sha256", ""))) != 64
    ]
    if missing_release_artifacts:
        fail(f"local model release has missing or unhashed result artifacts: {missing_release_artifacts[:4]}")
    local_release_checks = {check.get("name"): check.get("passed") for check in local_model_release_audit.get("checks", [])}
    for required_check in (
        "source_version_matches_summary",
        "proposed_method_present",
        "summary_remains_bounded",
        "result_artifacts_hash_locked",
        "explicitly_not_external_evidence",
        "not_a_robot_policy_checkpoint",
    ):
        if local_release_checks.get(required_check) is not True:
            fail(f"local model release audit missing passing check: {required_check}")
    local_release_card = local_model_release_card_path.read_text(encoding="utf-8")
    for required_phrase in (
        "Local Model Release Card",
        "Not external evidence: `true`",
        "not a trained robot policy checkpoint",
        "does not replace `external_validation/manifest.json`",
    ):
        if required_phrase not in local_release_card:
            fail(f"local model release card missing phrase: {required_phrase}")

    adapter_contract_path = RESULTS / "external_adapter_contract_audit.json"
    if not adapter_contract_path.exists():
        fail("missing results/external_adapter_contract_audit.json; run scripts/validate_external_adapters.py")
    adapter_contract = json.loads(adapter_contract_path.read_text(encoding="utf-8"))
    if adapter_contract.get("version") != "external_adapter_contract_audit_v1":
        fail("external adapter contract audit version mismatch")
    if adapter_contract.get("passed") is not True:
        fail("external adapter contract audit did not pass")
    if adapter_contract.get("not_external_evidence") is not True:
        fail("external adapter contract audit must declare that it is not evidence")
    if int(adapter_contract.get("adapter_count", 0)) < 11:
        fail("external adapter contract audit has too few non-oracle adapter checks")
    contract_checks = {check.get("name"): check.get("passed") for check in adapter_contract.get("checks", [])}
    for required_check in ("contract_self_test_passed", "scaffold_entries_present", "adapter_results_passed"):
        if contract_checks.get(required_check) is not True:
            fail(f"external adapter contract audit missing passing check: {required_check}")

    adapter_evidence_self_test_path = RESULTS / "external_adapter_evidence_self_test.json"
    if not adapter_evidence_self_test_path.exists():
        fail("missing results/external_adapter_evidence_self_test.json; run scripts/self_test_external_adapter_evidence.py")
    if not (ROOT / "scripts" / "self_test_external_adapter_evidence.py").exists():
        fail("missing scripts/self_test_external_adapter_evidence.py")
    adapter_evidence_self_test = json.loads(adapter_evidence_self_test_path.read_text(encoding="utf-8"))
    if adapter_evidence_self_test.get("version") != "external_adapter_evidence_self_test_v2":
        fail("external adapter evidence self-test version mismatch")
    if adapter_evidence_self_test.get("passed") is not True:
        fail("external adapter evidence self-test did not pass")
    if adapter_evidence_self_test.get("not_external_evidence") is not True:
        fail("external adapter evidence self-test must declare that it is not evidence")
    if adapter_evidence_self_test.get("synthetic_adapter_evidence_ready") is not True:
        fail("external adapter evidence self-test should make temporary manifest-declared adapters ready")
    if adapter_evidence_self_test.get("tracked_candidate_config_fixture_ready") is not True:
        fail("external adapter evidence self-test should pass strict validation with tracked candidate configs and temporary independent adapters")
    if int(adapter_evidence_self_test.get("tracked_candidate_config_count", 0) or 0) < 11:
        fail("external adapter evidence self-test should cover all tracked non-oracle candidate method configs")
    if adapter_evidence_self_test.get("scaffold_adapter_evidence_ready") is not False:
        fail("external adapter evidence self-test should reject scaffolds as strict evidence")
    if adapter_evidence_self_test.get("reference_adapter_evidence_ready") is not False:
        fail("external adapter evidence self-test should reject reference adapters as strict evidence")
    if adapter_evidence_self_test.get("missing_manifest_ready") is not False:
        fail("external adapter evidence self-test should reject a missing manifest")
    if adapter_evidence_self_test.get("leaky_provenance_ready") is not False:
        fail("external adapter evidence self-test should reject leaky or reference-adapter provenance")
    if adapter_evidence_self_test.get("implementation_hash_only_ready") is not False:
        fail("external adapter evidence self-test should reject implementation hashes as checkpoint/config evidence")
    if adapter_evidence_self_test.get("missing_fairness_contract_ready") is not False:
        fail("external adapter evidence self-test should reject manifests missing fairness-contract bindings")
    if adapter_evidence_self_test.get("fairness_mismatch_ready") is not False:
        fail("external adapter evidence self-test should reject mismatched per-method fairness-contract bindings")
    adapter_evidence_self_checks = {check.get("name"): check.get("passed") for check in adapter_evidence_self_test.get("checks", [])}
    for required_check in (
        "synthetic_strict_adapters_pass",
        "synthetic_manifest_entries_cover_non_oracle_methods",
        "tracked_candidate_configs_pass_strict_with_temp_independent_adapters",
        "tracked_candidate_config_methods_match_non_oracle_methods",
        "missing_manifest_fails_strict",
        "leaky_or_reference_provenance_fails_strict",
        "implementation_hash_cannot_replace_checkpoint_or_config",
        "fairness_contract_missing_or_mismatch_fails_strict",
        "scaffold_adapters_rejected_as_strict_evidence",
        "reference_adapters_rejected_as_strict_evidence",
        "real_adapter_evidence_report_not_overwritten",
    ):
        if adapter_evidence_self_checks.get(required_check) is not True:
            fail(f"external adapter evidence self-test missing passing check: {required_check}")
    if not (RESULTS / "external_adapter_evidence_self_test.md").exists():
        fail("missing results/external_adapter_evidence_self_test.md")

    method_packet_paths = [
        EXTERNAL / "method_implementation_packet.json",
        EXTERNAL / "method_implementation_packet.md",
        EXTERNAL / "method_implementation_work_orders.csv",
        EXTERNAL / "method_reference_provenance.csv",
        EXTERNAL / "adapter_acceptance_fixtures.json",
        EXTERNAL / "adapter_acceptance_fixtures.md",
        EXTERNAL / "adapter_acceptance_fixtures.csv",
        EXTERNAL / "method_manifest_cutover_checklist.csv",
        EXTERNAL / "method_manifest_cutover_checklist.md",
        RESULTS / "external_method_implementation_audit.json",
        RESULTS / "external_method_implementation_audit.md",
        ROOT / "scripts" / "build_external_method_implementation_packet.py",
        ROOT / "scripts" / "self_test_external_method_implementation_packet.py",
        RESULTS / "external_method_implementation_packet_self_test.json",
        RESULTS / "external_method_implementation_packet_self_test.md",
    ]
    for path in method_packet_paths:
        if not path.exists():
            fail(f"missing external method implementation packet artifact: {path}")
    method_packet = json.loads((EXTERNAL / "method_implementation_packet.json").read_text(encoding="utf-8"))
    if method_packet.get("version") != "external_method_implementation_packet_v1":
        fail("external method implementation packet version mismatch")
    if method_packet.get("not_external_evidence") is not True:
        fail("external method implementation packet must declare that it is not evidence")
    if method_packet.get("method_implementation_packet_ready") is not True:
        fail("external method implementation packet should be ready as a work-order packet")
    if method_packet.get("strict_adapter_evidence_ready") is not False:
        fail("external method implementation packet must not claim strict adapter evidence")
    if int(method_packet.get("non_oracle_method_count", 0) or 0) < 11:
        fail("external method implementation packet has too few non-oracle work orders")
    if int(method_packet.get("reference_adapter_provenance_count", 0) or 0) < 11:
        fail("external method implementation packet has too few reference provenance records")
    if method_packet.get("reference_adapter_provenance_csv") != "external_validation/method_reference_provenance.csv":
        fail("external method implementation packet should point to method_reference_provenance.csv")
    if int(method_packet.get("adapter_acceptance_fixture_count", 0) or 0) < 11:
        fail("external method implementation packet has too few adapter acceptance fixtures")
    if method_packet.get("adapter_acceptance_fixtures_json") != "external_validation/adapter_acceptance_fixtures.json":
        fail("external method implementation packet should point to adapter_acceptance_fixtures.json")
    if method_packet.get("method_manifest_cutover_checklist_csv") != "external_validation/method_manifest_cutover_checklist.csv":
        fail("external method implementation packet should point to method_manifest_cutover_checklist.csv")
    if method_packet.get("method_manifest_cutover_checklist_md") != "external_validation/method_manifest_cutover_checklist.md":
        fail("external method implementation packet should point to method_manifest_cutover_checklist.md")
    if int(method_packet.get("method_manifest_cutover_checklist_count", 0) or 0) < 11:
        fail("external method implementation packet has too few method cutover checklist rows")
    fixture_packet = json.loads((EXTERNAL / "adapter_acceptance_fixtures.json").read_text(encoding="utf-8"))
    if fixture_packet.get("version") != "adapter_acceptance_fixtures_v1":
        fail("adapter acceptance fixture packet version mismatch")
    if fixture_packet.get("not_external_evidence") is not True:
        fail("adapter acceptance fixtures must be marked non-evidence")
    if fixture_packet.get("strict_adapter_evidence_ready") is not False:
        fail("adapter acceptance fixtures must not claim strict adapter evidence")
    fixtures = fixture_packet.get("fixtures", []) or []
    if len(fixtures) < 11:
        fail("adapter acceptance fixture packet must cover all non-oracle methods")
    fixture_methods = {fixture.get("method") for fixture in fixtures}
    if "oracle_basin_composer" in fixture_methods:
        fail("adapter acceptance fixtures must not include the oracle method")
    for fixture in fixtures:
        if fixture.get("not_external_evidence") is not True:
            fail("each adapter acceptance fixture must be marked non-evidence")
        if fixture.get("evidence_status") != "synthetic_contract_fixture_not_rollout_evidence":
            fail("adapter acceptance fixtures must keep synthetic non-evidence status")
        if len(str(fixture.get("fixture_sha256", ""))) != 64:
            fail("adapter acceptance fixtures must include a 64-character fixture hash")
        if len(str(fixture.get("synthetic_policy_or_config_hash", ""))) != 64:
            fail("adapter acceptance fixtures must include a synthetic policy/config hash")
        if not {"initialize", "propose", "log", "reset"}.issubset(set(fixture.get("required_api", []) or [])):
            fail("adapter acceptance fixtures must declare the full adapter API")
        if not {"decision", "predicted_seam_risk", "failure_diagnosis", "repair_action"}.issubset(set(fixture.get("required_proposal_fields", []) or [])):
            fail("adapter acceptance fixtures must declare proposal fields")
        if not {"policy_or_config_hash", "predicted_seam_risk", "decision", "failure_diagnosis"}.issubset(set(fixture.get("required_log_fields", []) or [])):
            fail("adapter acceptance fixtures must declare core log fields")
    reference_provenance = method_packet.get("reference_adapter_provenance", []) or []
    if len(reference_provenance) < 11:
        fail("external method implementation packet missing reference adapter provenance")
    for record in reference_provenance:
        if record.get("strict_evidence_ready") is not False:
            fail("reference adapter provenance must not claim strict evidence readiness")
        if record.get("reference_adapter_allowed_as_evidence") is not False:
            fail("reference adapter provenance must forbid reference adapters as evidence")
        if record.get("evidence_status") != "implementation_only_not_rollout_evidence":
            fail("reference adapter provenance has wrong evidence status")
        for field in ("adapter_sha256", "metadata_sha256", "common_adapter_sha256", "reference_policy_hash"):
            if len(str(record.get(field, ""))) != 64:
                fail(f"reference adapter provenance missing 64-character hash field: {field}")
        stub = record.get("manifest_declaration_stub", {}) or {}
        if not str(stub.get("implementation", "")).startswith("<operator-supplied independent"):
            fail("reference adapter manifest stubs must require operator-supplied independent implementations")
        if "SHA256" not in str(stub.get("checkpoint_or_config_hash", "")):
            fail("reference adapter manifest stubs must keep checkpoint/config hash as a placeholder")
        provenance = stub.get("implementation_provenance", {}) or {}
        if not isinstance(provenance, dict):
            fail("reference adapter manifest stubs must include implementation_provenance")
        if provenance.get("oracle_access") is not False or provenance.get("uses_reference_adapter") is not False:
            fail("reference adapter manifest stubs must forbid oracle access and reference-adapter use")
        if provenance.get("policy_or_config_hash_locked") is not True:
            fail("reference adapter manifest stubs must require locked policy/config hashes")
    if method_packet.get("oracle_method") != "oracle_basin_composer":
        fail("external method implementation packet should declare the oracle as a post hoc upper bound")
    work_order_methods = {order.get("method") for order in method_packet.get("work_orders", []) or []}
    if "oracle_basin_composer" in work_order_methods:
        fail("external method implementation packet must not create an oracle work order")
    for order in method_packet.get("work_orders", []) or []:
        if order.get("adapter_acceptance_fixture_path") != "external_validation/adapter_acceptance_fixtures.json":
            fail("external method work orders must reference adapter_acceptance_fixtures.json")
        if not order.get("adapter_acceptance_fixture_id"):
            fail("external method work orders must reference an adapter acceptance fixture id")
    cutover_rows = method_packet.get("method_manifest_cutover_checklist", []) or []
    if len(cutover_rows) < 11:
        fail("method manifest cutover checklist must cover all non-oracle methods")
    if count_rows(EXTERNAL / "method_manifest_cutover_checklist.csv") != len(cutover_rows):
        fail("method manifest cutover checklist CSV row count does not match packet")
    cutover_methods = {row.get("method") for row in cutover_rows if isinstance(row, dict)}
    if "oracle_basin_composer" in cutover_methods:
        fail("method manifest cutover checklist must not include the oracle method")
    if not work_order_methods.issubset(cutover_methods):
        fail("method manifest cutover checklist missing work-order methods")
    required_cutover_fields = {"name", "implementation", "checkpoint_or_config_path", "checkpoint_or_config_hash", "implementation_provenance"}
    for row in cutover_rows:
        if not isinstance(row, dict):
            fail("method manifest cutover checklist rows must be objects")
        if not required_cutover_fields.issubset(set(str(row.get("required_manifest_fields", "")).split(";"))):
            fail("method manifest cutover checklist rows must declare manifest method fields")
        for key in (
            "implementation_required",
            "implementation_sha_or_commit_required",
            "checkpoint_or_config_path_required",
            "checkpoint_or_config_hash_required",
            "implementation_provenance_required",
            "fairness_contract_binding_required",
            "policy_or_config_hash_log_binding_required",
            "blocking_until_real_evidence",
        ):
            if row.get(key) is not True:
                fail(f"method manifest cutover checklist row must require {key}")
        if row.get("scaffold_allowed_as_evidence") is not False or row.get("reference_adapter_allowed_as_evidence") is not False:
            fail("method manifest cutover checklist must forbid scaffold/reference evidence shortcuts")
        if "validate_external_adapters.py --strict" not in str(row.get("strict_gate", "")):
            fail("method manifest cutover checklist must point to strict adapter validation")
        if not str(row.get("manifest_methods_key", "")).startswith("methods["):
            fail("method manifest cutover checklist must point to manifest methods entries")
        if len(str(row.get("interface_reference_adapter_sha256", ""))) != 64:
            fail("method manifest cutover checklist must preserve interface reference adapter hashes")
    method_command_text = "\n".join(method_packet.get("strict_acceptance_commands", []) or [])
    for fragment in (
        "build_external_method_implementation_packet.py",
        "validate_external_adapters.py --strict",
        "validate_external_rollouts.py",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in method_command_text:
            fail(f"external method implementation packet missing strict command fragment: {fragment}")
    method_audit = json.loads((RESULTS / "external_method_implementation_audit.json").read_text(encoding="utf-8"))
    if method_audit.get("version") != "external_method_implementation_audit_v1":
        fail("external method implementation audit version mismatch")
    if method_audit.get("passed") is not True:
        fail("external method implementation audit did not pass")
    if method_audit.get("not_external_evidence") is not True:
        fail("external method implementation audit must declare that it is not evidence")
    if method_audit.get("method_implementation_packet_ready") is not True:
        fail("external method implementation audit should report packet ready")
    if method_audit.get("strict_adapter_evidence_ready") is not False:
        fail("external method implementation audit must keep strict adapter evidence false")
    method_audit_checks = {check.get("name"): check.get("passed") for check in method_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "work_orders_cover_all_missing_non_oracle_methods",
        "oracle_excluded_from_work_orders",
        "required_artifact_fields_declared",
        "required_log_fields_declared",
        "manifest_entry_templates_cover_required_hash_fields",
        "manifest_entry_templates_bind_hash_to_checkpoint_config_artifact",
        "manifest_entry_templates_require_independent_provenance",
        "manifest_entry_templates_bind_fairness_contract",
        "work_orders_forbid_scaffolds_and_reference_adapters",
        "policy_or_config_hash_in_logs_required",
        "adapter_acceptance_fixtures_cover_non_oracle_methods",
        "adapter_acceptance_fixtures_define_contract",
        "work_orders_reference_acceptance_fixtures",
        "reference_adapter_provenance_covers_non_oracle_methods",
        "reference_adapter_hashes_recorded",
        "reference_adapters_marked_non_evidence",
        "reference_manifest_stubs_not_strict_ready",
        "common_reference_adapter_hash_shared",
        "reference_policy_hashes_match_adapter_formula",
        "method_manifest_cutover_checklist_covers_non_oracle_methods",
        "method_manifest_cutover_checklist_binds_manifest_fields",
        "method_manifest_cutover_checklist_forbids_shortcuts",
        "strict_commands_cover_adapter_rollout_pairing_and_evidence",
        "adapter_evidence_still_missing",
        "no_real_implementation_files_created",
        "packet_files_written",
    ):
        if method_audit_checks.get(required_check) is not True:
            fail(f"external method implementation audit missing passing check: {required_check}")
    method_self_test = json.loads((RESULTS / "external_method_implementation_packet_self_test.json").read_text(encoding="utf-8"))
    if method_self_test.get("version") != "external_method_implementation_packet_self_test_v1":
        fail("external method implementation packet self-test version mismatch")
    if method_self_test.get("passed") is not True:
        fail("external method implementation packet self-test did not pass")
    if method_self_test.get("not_external_evidence") is not True:
        fail("external method implementation packet self-test must declare that it is not evidence")
    if method_self_test.get("strict_adapter_evidence_ready") is not False:
        fail("external method implementation packet self-test must not claim strict adapter evidence")
    for required_flag in (
        "temporary_packet_ready",
        "missing_work_order_rejected",
        "oracle_work_order_rejected",
        "reference_adapter_shortcut_rejected",
        "checkpoint_hash_shortcut_rejected",
        "fairness_binding_drift_rejected",
        "fixture_contract_drift_rejected",
        "cutover_shortcut_rejected",
        "strict_command_drift_rejected",
        "adapter_evidence_promotion_rejected",
        "real_outputs_untouched",
    ):
        if method_self_test.get(required_flag) is not True:
            fail(f"external method implementation packet self-test missing true flag: {required_flag}")
    method_self_checks = {check.get("name"): check.get("passed") for check in method_self_test.get("checks", []) or []}
    for required_check in (
        "temporary_method_packet_ready_but_non_evidence",
        "missing_work_order_rejected",
        "oracle_work_order_rejected",
        "reference_adapter_shortcut_rejected",
        "checkpoint_hash_shortcut_rejected",
        "fairness_binding_drift_rejected",
        "fixture_contract_drift_rejected",
        "cutover_shortcut_rejected",
        "strict_command_drift_rejected",
        "adapter_evidence_promotion_rejected",
        "real_method_packet_outputs_untouched",
    ):
        if method_self_checks.get(required_check) is not True:
            fail(f"external method implementation packet self-test missing passing check: {required_check}")

    method_config_paths = [
        EXTERNAL / "method_config_materialization_plan.json",
        EXTERNAL / "method_config_materialization_plan.md",
        EXTERNAL / "method_config_candidates.csv",
        RESULTS / "external_method_config_materialization_audit.json",
        RESULTS / "external_method_config_materialization_audit.md",
        ROOT / "scripts" / "materialize_external_method_configs.py",
        ROOT / "scripts" / "self_test_external_method_config_materialization.py",
        RESULTS / "external_method_config_materialization_self_test.json",
        RESULTS / "external_method_config_materialization_self_test.md",
    ]
    for path in method_config_paths:
        if not path.exists():
            fail(f"missing external method config materialization artifact: {path}")
    method_config_plan = json.loads((EXTERNAL / "method_config_materialization_plan.json").read_text(encoding="utf-8"))
    method_config_audit = json.loads((RESULTS / "external_method_config_materialization_audit.json").read_text(encoding="utf-8"))
    method_config_self_test = json.loads((RESULTS / "external_method_config_materialization_self_test.json").read_text(encoding="utf-8"))
    if method_config_plan.get("version") != "external_method_config_materialization_plan_v1":
        fail("external method config materialization plan version mismatch")
    if method_config_audit.get("version") != "external_method_config_materialization_audit_v1":
        fail("external method config materialization audit version mismatch")
    for name, payload in (("plan", method_config_plan), ("audit", method_config_audit)):
        if payload.get("passed") is not True:
            fail(f"external method config materialization {name} did not pass")
        if payload.get("not_external_evidence") is not True:
            fail(f"external method config materialization {name} must declare that it is not evidence")
        if payload.get("strict_adapter_evidence_ready") is not False:
            fail(f"external method config materialization {name} must not claim strict adapter evidence")
        if payload.get("strict_external_evidence_ready") is not False:
            fail(f"external method config materialization {name} must not claim strict external evidence")
        if int(payload.get("candidate_config_count", 0) or 0) < 11:
            fail(f"external method config materialization {name} has too few candidate configs")
        if payload.get("oracle_excluded") is not True:
            fail(f"external method config materialization {name} must exclude the oracle")
    method_config_records = method_config_plan.get("records", []) or []
    if count_rows(EXTERNAL / "method_config_candidates.csv") != len(method_config_records):
        fail("method config candidate CSV row count does not match plan records")
    candidate_methods = {record.get("method") for record in method_config_records if isinstance(record, dict)}
    if candidate_methods != work_order_methods or "oracle_basin_composer" in candidate_methods:
        fail("external method config candidates must cover exactly the non-oracle method work orders")
    for record in method_config_records:
        if not isinstance(record, dict):
            fail("method config materialization records must be objects")
        config_path_text = str(record.get("config_path", ""))
        config_path = ROOT / config_path_text
        if not config_path.exists():
            fail(f"missing method config candidate file: {config_path_text}")
        if len(str(record.get("config_sha256", ""))) != 64:
            fail(f"method config candidate record missing 64-character config hash: {record.get('method')}")
        if sha256(config_path) != record.get("config_sha256"):
            fail(f"method config candidate hash does not recompute: {config_path_text}")
        candidate_config_payload = json.loads(config_path.read_text(encoding="utf-8"))
        if candidate_config_payload.get("version") != "paper119_candidate_method_config_v1":
            fail(f"method config candidate version mismatch: {config_path_text}")
        if candidate_config_payload.get("evidence_status") != "candidate_config_not_manifest_evidence":
            fail(f"method config candidate must remain non-evidence: {config_path_text}")
        for key in (
            "operator_acceptance_required",
            "manifest_declaration_required",
            "rollout_log_binding_required",
        ):
            if candidate_config_payload.get(key) is not True:
                fail(f"method config candidate must require {key}: {config_path_text}")
        if candidate_config_payload.get("strict_adapter_evidence_ready") is not False:
            fail(f"method config candidate must not claim strict adapter evidence: {config_path_text}")
        manifest_stub = record.get("manifest_stub", {}) or {}
        if manifest_stub.get("checkpoint_or_config_path") != config_path_text:
            fail(f"method config manifest stub path mismatch: {record.get('method')}")
        if manifest_stub.get("checkpoint_or_config_hash") != record.get("config_sha256"):
            fail(f"method config manifest stub hash mismatch: {record.get('method')}")
        provenance = manifest_stub.get("implementation_provenance", {}) or {}
        if "<operator" not in str(provenance.get("implementation_origin", "")):
            fail(f"method config manifest stub must keep operator provenance placeholder: {record.get('method')}")
        if provenance.get("oracle_access") is not False or provenance.get("uses_reference_adapter") is not False:
            fail(f"method config manifest stub must forbid oracle/reference shortcuts: {record.get('method')}")
        if provenance.get("policy_or_config_hash_locked") is not True:
            fail(f"method config manifest stub must lock policy/config hash: {record.get('method')}")
    method_config_checks = {check.get("name"): check.get("passed") for check in method_config_audit.get("checks", [])}
    for required_check in (
        "materialization_is_non_evidence",
        "source_method_packet_ready",
        "candidate_configs_cover_non_oracle_methods",
        "candidate_hashes_match_written_files",
        "manifest_stubs_bind_checkpoint_config_hashes",
        "independent_implementation_still_required",
        "no_real_manifest_logs_videos_or_checkpoints_written",
        "candidate_config_contents_remain_non_evidence",
        "baseline_spec_hashes_match_current_files",
        "candidate_manifest_csv_matches_records",
    ):
        if method_config_checks.get(required_check) is not True:
            fail(f"external method config materialization audit missing passing check: {required_check}")
    if method_config_self_test.get("version") != "external_method_config_materialization_self_test_v1":
        fail("external method config materialization self-test version mismatch")
    if method_config_self_test.get("passed") is not True:
        fail("external method config materialization self-test did not pass")
    if method_config_self_test.get("not_external_evidence") is not True:
        fail("external method config materialization self-test must declare that it is not evidence")
    if method_config_self_test.get("temporary_materialization_ready") is not True:
        fail("external method config materialization self-test must build a temporary non-evidence materialization")
    for required_field in (
        "premature_evidence_promotion_rejected",
        "missing_candidate_record_rejected",
        "oracle_candidate_rejected",
        "candidate_file_hash_drift_rejected",
        "manifest_stub_hash_drift_rejected",
        "candidate_evidence_content_drift_rejected",
        "source_method_packet_drift_rejected",
        "adapter_evidence_promotion_rejected",
        "baseline_spec_hash_drift_rejected",
        "candidate_csv_drift_rejected",
        "real_manifest_write_rejected",
        "materialization_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if method_config_self_test.get(required_field) is not True:
            fail(f"external method config materialization self-test missing passing field: {required_field}")

    manifest_builder_report_path = RESULTS / "external_manifest_builder_report.json"
    if not manifest_builder_report_path.exists():
        fail("missing results/external_manifest_builder_report.json; run scripts/build_external_manifest.py --allow-missing")
    manifest_builder_report = json.loads(manifest_builder_report_path.read_text(encoding="utf-8"))
    if manifest_builder_report.get("version") != "external_manifest_builder_report_v1":
        fail("external manifest builder report version mismatch")
    if manifest_builder_report.get("manifest_written") is not False:
        fail("external manifest builder should not write manifest during the local build")
    if manifest_builder_report.get("not_external_evidence") is not True:
        fail("external manifest builder report must declare that the report is not evidence")
    if manifest_builder_report.get("records_loaded") != 0:
        fail("external manifest builder unexpectedly loaded external records while scope gate is false")
    if not any("missing log file" in str(error) for error in manifest_builder_report.get("schema_errors", [])):
        fail("external manifest builder report should currently identify missing external logs")
    manifest_checklist_path = EXTERNAL / "manifest_assembly_checklist.csv"
    if not manifest_checklist_path.exists():
        fail("missing external_validation/manifest_assembly_checklist.csv; run scripts/build_external_manifest.py --allow-missing")
    if manifest_builder_report.get("assembly_checklist_csv") != "external_validation/manifest_assembly_checklist.csv":
        fail("external manifest builder report should point to manifest_assembly_checklist.csv")
    assembly_rows = manifest_builder_report.get("assembly_checklist_rows", []) or []
    if int(manifest_builder_report.get("assembly_checklist_row_count", 0) or 0) < 30:
        fail("external manifest assembly checklist has too few rows")
    if int(manifest_builder_report.get("assembly_blocking_count", 0) or 0) < 20:
        fail("external manifest assembly checklist should expose current blocking rows")
    if int(manifest_builder_report.get("manifest_write_blocking_count", 0) or 0) < 20:
        fail("external manifest builder should expose pre-write manifest promotion blockers")
    write_blocking_rows = manifest_builder_report.get("manifest_write_blocking_rows", []) or []
    if not isinstance(write_blocking_rows, list) or not write_blocking_rows:
        fail("external manifest builder report must list manifest_write_blocking_rows")
    if any(row.get("phase") == "final_strict_gates" for row in write_blocking_rows if isinstance(row, dict)):
        fail("manifest_write_blocking_rows should exclude post-write final strict gates")
    if count_rows(manifest_checklist_path) != int(manifest_builder_report.get("assembly_checklist_row_count", 0) or 0):
        fail("external manifest assembly checklist CSV row count does not match report")
    assembly_phases = {str(row.get("phase", "")) for row in assembly_rows if isinstance(row, dict)}
    for phase in ("platform_fidelity", "task_configs", "rollout_logs", "rollout_videos", "method_implementations", "release_artifacts", "rollout_metrics", "final_strict_gates"):
        if phase not in assembly_phases:
            fail(f"external manifest assembly checklist missing phase: {phase}")
    if not any(row.get("item") == "final_external_evidence_gate" and row.get("blocking_until_real_evidence") == "true" for row in assembly_rows if isinstance(row, dict)):
        fail("external manifest assembly checklist must keep the final evidence gate blocking")

    precollection_draft_path = EXTERNAL / "manifest_precollection_draft.json"
    precollection_draft_md_path = EXTERNAL / "manifest_precollection_draft.md"
    precollection_audit_path = RESULTS / "external_precollection_manifest_draft_audit.json"
    precollection_audit_md_path = RESULTS / "external_precollection_manifest_draft_audit.md"
    precollection_self_test_path = RESULTS / "external_precollection_manifest_draft_self_test.json"
    precollection_self_test_md_path = RESULTS / "external_precollection_manifest_draft_self_test.md"
    for path in (
        ROOT / "scripts" / "build_external_precollection_manifest_draft.py",
        ROOT / "scripts" / "self_test_external_precollection_manifest_draft.py",
        precollection_draft_path,
        precollection_draft_md_path,
        precollection_audit_path,
        precollection_audit_md_path,
        precollection_self_test_path,
        precollection_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external precollection manifest draft artifact: {path}")
    precollection_draft = json.loads(precollection_draft_path.read_text(encoding="utf-8"))
    precollection_audit = json.loads(precollection_audit_path.read_text(encoding="utf-8"))
    precollection_self_test = json.loads(precollection_self_test_path.read_text(encoding="utf-8"))
    if precollection_draft.get("version") != "external_precollection_manifest_draft_v1":
        fail("external precollection manifest draft version mismatch")
    if precollection_draft.get("not_external_evidence") is not True or precollection_draft.get("draft_only") is not True:
        fail("external precollection manifest draft must be marked draft-only non-evidence")
    if precollection_draft.get("strict_external_evidence_ready") is not False or precollection_draft.get("ready_to_write_official_manifest") is not False:
        fail("external precollection manifest draft must remain fail-closed")
    if precollection_draft.get("official_manifest_exists") is not False or (EXTERNAL / "manifest.json").exists():
        fail("external precollection manifest draft must not coexist with a real manifest before collection")
    if int(precollection_draft.get("prepared_config_count", 0) or 0) < 4:
        fail("external precollection manifest draft must prefill all prepared config hashes")
    if int(precollection_draft.get("candidate_method_config_count", 0) or 0) < 11:
        fail("external precollection manifest draft must prefill all non-oracle candidate method config hashes")
    if int(precollection_draft.get("method_gap_count", 0) or 0) < 11:
        fail("external precollection manifest draft must preserve missing non-oracle method gaps")
    if int(precollection_draft.get("missing_rollout_artifact_count", 0) or 0) < 8:
        fail("external precollection manifest draft must preserve missing rollout log/video gaps")
    if int(precollection_draft.get("manifest_assembly_blocking_count", 0) or 0) < 20:
        fail("external precollection manifest draft must preserve manifest assembly blockers")
    for record in precollection_draft.get("prepared_config_records", []) or []:
        if record.get("strict_validation_passed_if_manifest_declared") is not True or len(str(record.get("config_hash", ""))) != 64:
            fail(f"external precollection manifest draft has invalid prepared config record: {record}")
    draft_candidate_records = precollection_draft.get("candidate_method_config_records", []) or []
    draft_candidate_methods = {record.get("method") for record in draft_candidate_records if isinstance(record, dict)}
    if draft_candidate_methods != work_order_methods or "oracle_basin_composer" in draft_candidate_methods:
        fail("external precollection manifest draft must prefill exactly the non-oracle method config candidates")
    for record in draft_candidate_records:
        config_path = ROOT / str(record.get("config_path", ""))
        if not config_path.exists():
            fail(f"external precollection manifest draft candidate config is missing: {record}")
        if len(str(record.get("config_sha256", ""))) != 64 or sha256(config_path) != record.get("config_sha256"):
            fail(f"external precollection manifest draft candidate config hash does not recompute: {record}")
        if record.get("config_hash_matches") is not True:
            fail(f"external precollection manifest draft candidate config must record hash match: {record}")
        if record.get("operator_acceptance_required") is not True or record.get("manifest_declaration_required") is not True:
            fail(f"external precollection manifest draft candidate config must require operator/manifest acceptance: {record}")
        if record.get("rollout_log_binding_required") is not True:
            fail(f"external precollection manifest draft candidate config must require rollout log binding: {record}")
        if record.get("strict_adapter_evidence_ready") is not False:
            fail(f"external precollection manifest draft candidate config must keep strict adapter evidence false: {record}")
    for record in precollection_draft.get("method_gaps", []) or []:
        if record.get("candidate_checkpoint_or_config_prefill_available") is not True:
            fail(f"external precollection manifest draft method gap missing candidate config prefill: {record}")
        if len(str(record.get("candidate_config_hash", ""))) != 64:
            fail(f"external precollection manifest draft method gap missing candidate config hash: {record}")
        blockers = set(record.get("blocking_missing", []) or [])
        required_blockers = {
            "implementation_path",
            "independent_operator_provenance",
            "manifest_method_declaration",
            "rollout_policy_hash_binding",
        }
        if not required_blockers.issubset(blockers):
            fail(f"external precollection manifest draft method gap must preserve independent evidence blockers: {record}")
    cutover_text = "\n".join(precollection_draft.get("cutover_commands", []) or [])
    for fragment in (
        "materialize_fidelity_acceptance.py",
        "audit_external_collection_readiness.py --strict",
        "build_external_precollection_freeze_receipt.py",
        "self_test_external_precollection_freeze_receipt.py",
        "real_collection_runner.py",
        "build_external_postcollection_evidence_seal.py",
        "audit_external_postcollection_seal_consistency.py",
        "build_external_manifest.py --write --check-video-paths",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in cutover_text:
            fail(f"external precollection manifest draft missing cutover command fragment: {fragment}")
    if precollection_audit.get("version") != "external_precollection_manifest_draft_audit_v1":
        fail("external precollection manifest draft audit version mismatch")
    if precollection_audit.get("passed") is not True:
        fail("external precollection manifest draft audit did not pass")
    if precollection_audit.get("not_external_evidence") is not True:
        fail("external precollection manifest draft audit must declare that it is not evidence")
    if precollection_audit.get("draft_ready") is not True:
        fail("external precollection manifest draft audit must report draft_ready=true")
    if precollection_audit.get("strict_external_evidence_ready") is not False or precollection_audit.get("strict_config_evidence_ready") is not False:
        fail("external precollection manifest draft audit must preserve strict gates as false")
    precollection_checks = {check.get("name"): check.get("passed") for check in precollection_audit.get("checks", [])}
    for required_check in (
        "draft_json_written_to_precollection_path",
        "draft_marked_non_evidence_and_fail_closed",
        "official_manifest_absent",
        "prepared_config_hashes_prefilled",
        "prepared_config_hashes_match_current_files",
        "candidate_method_configs_prefilled",
        "candidate_method_configs_match_current_plan",
        "method_gaps_bind_candidate_configs",
        "method_gaps_still_require_independent_evidence",
        "method_gaps_remain_blocking",
        "rollout_artifacts_remain_blocking",
        "manifest_assembly_blockers_preserved",
        "source_reports_hash_listed",
        "source_reports_match_current_files",
    ):
        if precollection_checks.get(required_check) is not True:
            fail(f"external precollection manifest draft audit missing passing check: {required_check}")
    if precollection_self_test.get("version") != "external_precollection_manifest_draft_self_test_v1":
        fail("external precollection manifest draft self-test version mismatch")
    if precollection_self_test.get("passed") is not True:
        fail("external precollection manifest draft self-test did not pass")
    if precollection_self_test.get("not_external_evidence") is not True:
        fail("external precollection manifest draft self-test must declare that it is not evidence")
    if precollection_self_test.get("temporary_draft_ready") is not True:
        fail("external precollection manifest draft self-test must prove a temporary draft can be built")
    for required_field in (
        "premature_evidence_promotion_rejected",
        "missing_prepared_config_hash_rejected",
        "task_config_path_drift_rejected",
        "candidate_method_config_hash_drift_rejected",
        "method_blocker_omission_rejected",
        "rollout_gap_omission_rejected",
        "source_report_drift_rejected",
        "cutover_command_drift_rejected",
        "real_manifest_write_rejected",
        "draft_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if precollection_self_test.get(required_field) is not True:
            fail(f"external precollection manifest draft self-test missing passing field: {required_field}")

    freeze_receipt_path = EXTERNAL / "precollection_freeze_receipt.json"
    freeze_receipt_md_path = EXTERNAL / "precollection_freeze_receipt.md"
    freeze_receipt_csv_path = EXTERNAL / "precollection_freeze_receipt.csv"
    freeze_audit_path = RESULTS / "external_precollection_freeze_receipt_audit.json"
    freeze_audit_md_path = RESULTS / "external_precollection_freeze_receipt_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_precollection_freeze_receipt.py",
        freeze_receipt_path,
        freeze_receipt_md_path,
        freeze_receipt_csv_path,
        freeze_audit_path,
        freeze_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external precollection freeze receipt artifact: {path}")
    freeze_receipt = json.loads(freeze_receipt_path.read_text(encoding="utf-8"))
    freeze_audit = json.loads(freeze_audit_path.read_text(encoding="utf-8"))
    if freeze_receipt.get("version") != "external_precollection_freeze_receipt_v1":
        fail("external precollection freeze receipt version mismatch")
    if freeze_receipt.get("not_external_evidence") is not True:
        fail("external precollection freeze receipt must declare that it is not evidence")
    if freeze_receipt.get("strict_external_evidence_ready") is not False or freeze_receipt.get("freeze_receipt_ready") is not False:
        fail("external precollection freeze receipt must stay fail-closed before real operator lock")
    if "not a manifest, rollout log" not in str(freeze_receipt.get("evidence_boundary", "")):
        fail("external precollection freeze receipt must state its evidence boundary")
    if int(len(freeze_receipt.get("lock_artifacts", []) or [])) < 42:
        fail("external precollection freeze receipt locks too few artifacts")
    if int(freeze_receipt.get("candidate_method_config_count", 0) or 0) < 11:
        fail("external precollection freeze receipt must lock candidate method config hashes")
    if freeze_receipt.get("method_config_hash_lock_ready") is not True:
        fail("external precollection freeze receipt must report method config hash lock ready")
    if "build_external_precollection_freeze_receipt.py" not in "\n".join(freeze_receipt.get("strict_command_sequence", []) or []):
        fail("external precollection freeze receipt must include itself in the strict command sequence")
    if freeze_audit.get("version") != "external_precollection_freeze_receipt_audit_v1":
        fail("external precollection freeze receipt audit version mismatch")
    if freeze_audit.get("passed") is not True:
        fail("external precollection freeze receipt audit did not pass")
    if freeze_audit.get("not_external_evidence") is not True:
        fail("external precollection freeze receipt audit must declare that it is not evidence")
    if freeze_audit.get("strict_external_evidence_ready") is not False or freeze_audit.get("freeze_receipt_ready") is not False:
        fail("external precollection freeze receipt audit must keep strict evidence and receipt readiness false")
    if int(freeze_audit.get("locked_artifact_count", 0) or 0) < 42:
        fail("external precollection freeze receipt audit locks too few artifacts")
    if int(freeze_audit.get("candidate_method_config_count", 0) or 0) < 11:
        fail("external precollection freeze receipt audit must lock candidate method config hashes")
    if freeze_audit.get("method_config_hash_lock_ready") is not True:
        fail("external precollection freeze receipt audit must report method config hash lock ready")
    freeze_checks = {check.get("name"): check.get("passed") for check in freeze_audit.get("checks", [])}
    for required_check in (
        "receipt_is_non_evidence_and_fail_closed",
        "core_lock_artifacts_hashed",
        "prepared_task_configs_hashed",
        "method_config_materialization_artifacts_hashed",
        "candidate_method_configs_hashed",
        "candidate_method_config_hashes_match_plan",
        "candidate_method_configs_remain_non_evidence",
        "backend_module_still_operator_supplied",
        "run_identity_still_operator_supplied",
        "operator_metadata_still_required",
        "checkout_and_skill_hash_recorded",
        "strict_sequence_places_receipt_before_collection",
        "receipt_references_manifest_rollout_release_final_gates",
        "source_state_preserves_external_blockers",
        "no_real_manifest_written",
    ):
        if freeze_checks.get(required_check) is not True:
            fail(f"external precollection freeze receipt audit missing passing check: {required_check}")

    freeze_self_test_path = RESULTS / "external_precollection_freeze_receipt_self_test.json"
    freeze_self_test_md_path = RESULTS / "external_precollection_freeze_receipt_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_precollection_freeze_receipt.py",
        freeze_self_test_path,
        freeze_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external precollection freeze receipt self-test artifact: {path}")
    freeze_self_test = json.loads(freeze_self_test_path.read_text(encoding="utf-8"))
    if freeze_self_test.get("version") != "external_precollection_freeze_receipt_self_test_v1":
        fail("external precollection freeze receipt self-test version mismatch")
    if freeze_self_test.get("passed") is not True:
        fail("external precollection freeze receipt self-test did not pass")
    if freeze_self_test.get("not_external_evidence") is not True:
        fail("external precollection freeze receipt self-test must declare that it is not evidence")
    if freeze_self_test.get("synthetic_freeze_ready") is not True:
        fail("external precollection freeze receipt self-test should make a temporary complete freeze ready")
    if freeze_self_test.get("missing_backend_rejected") is not True:
        fail("external precollection freeze receipt self-test should reject missing backend selection")
    if freeze_self_test.get("placeholder_run_rejected") is not True:
        fail("external precollection freeze receipt self-test should reject placeholder run identity")
    if freeze_self_test.get("missing_lock_artifact_rejected") is not True:
        fail("external precollection freeze receipt self-test should reject missing lock artifacts")
    if freeze_self_test.get("dirty_checkout_rejected") is not True:
        fail("external precollection freeze receipt self-test should reject dirty checkout state")
    if freeze_self_test.get("real_reports_untouched") is not True:
        fail("external precollection freeze receipt self-test should not overwrite the real receipt reports")
    freeze_self_checks = {
        check.get("name"): check.get("passed") for check in freeze_self_test.get("checks", [])
    }
    for required_check in (
        "synthetic_complete_freeze_reaches_collection_readiness",
        "synthetic_ready_checks_cover_hashes_identity_and_order",
        "missing_backend_selection_rejected",
        "placeholder_run_identity_rejected",
        "missing_lock_artifact_rejected",
        "dirty_checkout_rejected",
        "real_precollection_freeze_reports_not_overwritten",
    ):
        if freeze_self_checks.get(required_check) is not True:
            fail(f"external precollection freeze receipt self-test missing passing check: {required_check}")

    postcollection_seal_path = EXTERNAL / "postcollection_evidence_seal.json"
    postcollection_seal_md_path = EXTERNAL / "postcollection_evidence_seal.md"
    postcollection_seal_csv_path = EXTERNAL / "postcollection_evidence_seal.csv"
    postcollection_seal_audit_path = RESULTS / "external_postcollection_evidence_seal_audit.json"
    postcollection_seal_audit_md_path = RESULTS / "external_postcollection_evidence_seal_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_postcollection_evidence_seal.py",
        postcollection_seal_path,
        postcollection_seal_md_path,
        postcollection_seal_csv_path,
        postcollection_seal_audit_path,
        postcollection_seal_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external postcollection evidence seal artifact: {path}")
    postcollection_seal = json.loads(postcollection_seal_path.read_text(encoding="utf-8"))
    postcollection_seal_audit = json.loads(postcollection_seal_audit_path.read_text(encoding="utf-8"))
    if postcollection_seal.get("version") != "external_postcollection_evidence_seal_v1":
        fail("external postcollection evidence seal version mismatch")
    if postcollection_seal.get("not_external_evidence") is not True:
        fail("external postcollection evidence seal must declare that it is not evidence")
    if (
        postcollection_seal.get("strict_external_evidence_ready") is not False
        or postcollection_seal.get("postcollection_seal_ready") is not False
        or postcollection_seal.get("ready_for_manifest_promotion") is not False
    ):
        fail("external postcollection evidence seal must stay fail-closed before real logs/videos")
    if "before manifest promotion" not in str(postcollection_seal.get("evidence_boundary", "")):
        fail("external postcollection evidence seal must state its manifest-promotion evidence boundary")
    if int(len(postcollection_seal.get("seal_artifacts", []) or [])) < 8:
        fail("external postcollection evidence seal hashes too few artifacts")
    if int(postcollection_seal.get("jsonl_record_count", 0) or 0) != 0 or int(postcollection_seal.get("rollout_video_count", 0) or 0) != 0:
        fail("external postcollection evidence seal must not find official logs or videos before collection")
    postcollection_sequence = "\n".join(postcollection_seal.get("strict_command_sequence", []) or [])
    if (
        "real_collection_runner.py" not in postcollection_sequence
        or "build_external_postcollection_evidence_seal.py" not in postcollection_sequence
        or "audit_external_postcollection_seal_consistency.py" not in postcollection_sequence
        or "build_external_manifest.py --write --check-video-paths" not in postcollection_sequence
    ):
        fail("external postcollection evidence seal must include collection, seal, consistency, and manifest-promotion commands")
    if postcollection_seal_audit.get("version") != "external_postcollection_evidence_seal_audit_v1":
        fail("external postcollection evidence seal audit version mismatch")
    if postcollection_seal_audit.get("passed") is not True:
        fail("external postcollection evidence seal audit did not pass")
    if postcollection_seal_audit.get("not_external_evidence") is not True:
        fail("external postcollection evidence seal audit must declare that it is not evidence")
    if (
        postcollection_seal_audit.get("strict_external_evidence_ready") is not False
        or postcollection_seal_audit.get("postcollection_seal_ready") is not False
        or postcollection_seal_audit.get("ready_for_manifest_promotion") is not False
    ):
        fail("external postcollection evidence seal audit must keep strict evidence and manifest promotion false")
    if int(postcollection_seal_audit.get("sealed_artifact_count", 0) or 0) < 8:
        fail("external postcollection evidence seal audit hashes too few artifacts")
    if int(postcollection_seal_audit.get("jsonl_record_count", 0) or 0) != 0 or int(postcollection_seal_audit.get("rollout_video_count", 0) or 0) != 0:
        fail("external postcollection evidence seal audit must remain pre-collection fail-closed by default")
    postcollection_checks = {check.get("name"): check.get("passed") for check in postcollection_seal_audit.get("checks", [])}
    for required_check in (
        "seal_is_non_evidence_and_fail_closed",
        "precollection_freeze_loaded_but_not_real_ready",
        "raw_logs_and_videos_absent_before_collection",
        "operator_metadata_still_required",
        "hash_inventory_written_for_precollection_inputs",
        "strict_sequence_places_seal_after_collection_before_manifest",
        "seal_references_consistency_gate_before_manifest",
        "seal_references_rollout_pairing_release_final_gates",
        "strict_evidence_gates_still_false",
        "no_real_manifest_written",
    ):
        if postcollection_checks.get(required_check) is not True:
            fail(f"external postcollection evidence seal audit missing passing check: {required_check}")

    postcollection_seal_self_test_path = RESULTS / "external_postcollection_evidence_seal_self_test.json"
    postcollection_seal_self_test_md_path = RESULTS / "external_postcollection_evidence_seal_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_postcollection_evidence_seal.py",
        postcollection_seal_self_test_path,
        postcollection_seal_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external postcollection evidence seal self-test artifact: {path}")
    postcollection_seal_self_test = json.loads(postcollection_seal_self_test_path.read_text(encoding="utf-8"))
    if postcollection_seal_self_test.get("version") != "external_postcollection_evidence_seal_self_test_v1":
        fail("external postcollection evidence seal self-test version mismatch")
    if postcollection_seal_self_test.get("passed") is not True:
        fail("external postcollection evidence seal self-test did not pass")
    if postcollection_seal_self_test.get("not_external_evidence") is not True:
        fail("external postcollection evidence seal self-test must declare that it is not evidence")
    if postcollection_seal_self_test.get("synthetic_seal_ready") is not True:
        fail("external postcollection evidence seal self-test should make a temporary complete seal ready")
    if postcollection_seal_self_test.get("missing_operator_metadata_rejected") is not True:
        fail("external postcollection evidence seal self-test should reject missing operator metadata")
    if postcollection_seal_self_test.get("incomplete_video_set_rejected") is not True:
        fail("external postcollection evidence seal self-test should reject incomplete official videos")
    if postcollection_seal_self_test.get("manifest_present_rejected") is not True:
        fail("external postcollection evidence seal self-test should reject pre-existing manifest promotion")
    if postcollection_seal_self_test.get("real_reports_untouched") is not True:
        fail("external postcollection evidence seal self-test should not overwrite the real seal reports")
    postcollection_seal_self_checks = {
        check.get("name"): check.get("passed") for check in postcollection_seal_self_test.get("checks", [])
    }
    for required_check in (
        "synthetic_complete_seal_reaches_manifest_promotion",
        "synthetic_ready_checks_cover_order_inventory_and_boundary",
        "missing_operator_metadata_rejected",
        "incomplete_video_set_rejected",
        "manifest_present_rejected_before_promotion",
        "real_postcollection_seal_reports_not_overwritten",
    ):
        if postcollection_seal_self_checks.get(required_check) is not True:
            fail(f"external postcollection evidence seal self-test missing passing check: {required_check}")

    postcollection_consistency_path = RESULTS / "external_postcollection_seal_consistency_audit.json"
    postcollection_consistency_md_path = RESULTS / "external_postcollection_seal_consistency_audit.md"
    for path in (
        ROOT / "scripts" / "audit_external_postcollection_seal_consistency.py",
        postcollection_consistency_path,
        postcollection_consistency_md_path,
    ):
        if not path.exists():
            fail(f"missing external postcollection seal consistency artifact: {path}")
    postcollection_consistency = json.loads(postcollection_consistency_path.read_text(encoding="utf-8"))
    if postcollection_consistency.get("version") != "external_postcollection_seal_consistency_audit_v1":
        fail("external postcollection seal consistency audit version mismatch")
    if postcollection_consistency.get("passed") is not True:
        fail("external postcollection seal consistency audit did not pass")
    if postcollection_consistency.get("not_external_evidence") is not True:
        fail("external postcollection seal consistency audit must declare that it is not evidence")
    if (
        postcollection_consistency.get("strict_external_evidence_ready") is not False
        or postcollection_consistency.get("seal_consistency_ready") is not False
        or postcollection_consistency.get("ready_for_manifest_promotion") is not False
    ):
        fail("external postcollection seal consistency audit must keep strict evidence and manifest promotion false by default")
    if int(postcollection_consistency.get("matched_hash_count", 0) or 0) < 8:
        fail("external postcollection seal consistency audit recomputes too few hashes")
    if postcollection_consistency.get("mismatched_hashes") or postcollection_consistency.get("extra_official_artifacts"):
        fail("external postcollection seal consistency audit found unexpected hash drift or unsealed official artifacts")
    if int(postcollection_consistency.get("current_jsonl_record_count", 0) or 0) != 0 or int(postcollection_consistency.get("current_rollout_video_count", 0) or 0) != 0:
        fail("external postcollection seal consistency audit must remain default fail-closed before real logs/videos")
    consistency_checks = {check.get("name"): check.get("passed") for check in postcollection_consistency.get("checks", [])}
    for required_check in (
        "postcollection_seal_artifacts_loaded",
        "consistency_gate_is_non_evidence_and_fail_closed",
        "sealed_hashes_recompute_without_drift",
        "no_unsealed_official_artifacts_before_manifest_promotion",
        "manifest_promotion_requires_ready_seal_and_consistency",
        "current_counts_match_default_or_ready_state",
        "no_real_manifest_written_before_seal_consistency",
        "strict_sequence_places_consistency_after_seal_before_manifest",
        "consistency_gate_references_rollout_pairing_release_final_gates",
    ):
        if consistency_checks.get(required_check) is not True:
            fail(f"external postcollection seal consistency audit missing passing check: {required_check}")

    postcollection_consistency_self_test_path = RESULTS / "external_postcollection_seal_consistency_self_test.json"
    postcollection_consistency_self_test_md_path = RESULTS / "external_postcollection_seal_consistency_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_postcollection_seal_consistency.py",
        postcollection_consistency_self_test_path,
        postcollection_consistency_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external postcollection seal consistency self-test artifact: {path}")
    postcollection_consistency_self_test = json.loads(postcollection_consistency_self_test_path.read_text(encoding="utf-8"))
    if postcollection_consistency_self_test.get("version") != "external_postcollection_seal_consistency_self_test_v1":
        fail("external postcollection seal consistency self-test version mismatch")
    if postcollection_consistency_self_test.get("passed") is not True:
        fail("external postcollection seal consistency self-test did not pass")
    if postcollection_consistency_self_test.get("not_external_evidence") is not True:
        fail("external postcollection seal consistency self-test must declare that it is not evidence")
    if postcollection_consistency_self_test.get("synthetic_consistency_ready") is not True:
        fail("external postcollection seal consistency self-test should make a temporary sealed fixture ready")
    if postcollection_consistency_self_test.get("drift_rejected") is not True:
        fail("external postcollection seal consistency self-test should reject hash drift")
    if postcollection_consistency_self_test.get("unsealed_official_artifact_rejected") is not True:
        fail("external postcollection seal consistency self-test should reject unsealed official artifacts")
    if postcollection_consistency_self_test.get("real_report_untouched") is not True:
        fail("external postcollection seal consistency self-test should not overwrite the real consistency report")
    postcollection_self_checks = {
        check.get("name"): check.get("passed") for check in postcollection_consistency_self_test.get("checks", [])
    }
    for required_check in (
        "synthetic_ready_seal_consistency_passes",
        "synthetic_ready_checks_cover_hashes_counts_and_order",
        "hash_drift_rejected",
        "hash_drift_fails_recompute_and_promotion_checks",
        "unsealed_official_artifact_rejected",
        "unsealed_artifact_fails_official_artifact_check",
        "real_consistency_report_not_overwritten",
    ):
        if postcollection_self_checks.get(required_check) is not True:
            fail(f"external postcollection seal consistency self-test missing passing check: {required_check}")

    preflight_path = RESULTS / "external_evidence_preflight.json"
    if not preflight_path.exists():
        fail("missing results/external_evidence_preflight.json; run scripts/audit_external_evidence_preflight.py")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("version") != "external_evidence_preflight_v1":
        fail("external evidence preflight version mismatch")
    if preflight.get("passed") is not True:
        fail("external evidence preflight did not pass")
    if preflight.get("not_external_evidence") is not True:
        fail("external evidence preflight must declare that it is not evidence")
    if preflight.get("evidence_ready") is not False:
        fail("external evidence preflight must not mark evidence ready before the strict external package exists")
    if preflight.get("readiness_state") != "COLLECT_EXTERNAL_EVIDENCE":
        fail("external evidence preflight should currently require external evidence collection")
    if int(preflight.get("expected_records", 0)) < 1440:
        fail("external evidence preflight has too few expected records")
    if int(preflight.get("observed_records", -1)) != 0:
        fail("external evidence preflight unexpectedly observed real external records")
    if int(preflight.get("blocking_missing_count", 0)) < 20:
        fail("external evidence preflight should expose the missing task/method evidence")
    if not any("external_validation/manifest.json" in str(item) for item in preflight.get("blocking_missing", [])):
        fail("external evidence preflight should identify the missing real manifest")
    if len(preflight.get("task_reports", [])) < 4:
        fail("external evidence preflight has too few task reports")
    if len(preflight.get("method_reports", [])) < 12:
        fail("external evidence preflight has too few method reports")
    if not (RESULTS / "external_evidence_preflight.md").exists():
        fail("missing results/external_evidence_preflight.md")

    preflight_self_test_path = RESULTS / "external_evidence_preflight_self_test.json"
    preflight_self_test_md_path = RESULTS / "external_evidence_preflight_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_evidence_preflight.py",
        preflight_self_test_path,
        preflight_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external evidence preflight self-test artifact: {path}")
    preflight_self_test = json.loads(preflight_self_test_path.read_text(encoding="utf-8"))
    if preflight_self_test.get("version") != "external_evidence_preflight_self_test_v1":
        fail("external evidence preflight self-test version mismatch")
    if preflight_self_test.get("passed") is not True:
        fail("external evidence preflight self-test did not pass")
    if preflight_self_test.get("not_external_evidence") is not True:
        fail("external evidence preflight self-test must declare that it is not evidence")
    if preflight_self_test.get("strict_external_evidence_ready") is not False:
        fail("external evidence preflight self-test must keep strict external evidence false")
    for field in (
        "tracked_no_manifest_fail_closed",
        "temporary_complete_fixture_ready",
        "incomplete_log_rejected",
        "placeholder_video_rejected",
        "template_config_rejected",
        "scaffold_implementation_rejected",
        "real_outputs_untouched",
    ):
        if preflight_self_test.get(field) is not True:
            fail(f"external evidence preflight self-test field must be true: {field}")
    preflight_self_checks = {check.get("name"): check.get("passed") for check in preflight_self_test.get("checks", [])}
    for required_check in (
        "tracked_no_manifest_preflight_fails_closed",
        "temporary_complete_preflight_reaches_strict_audit_handoff",
        "incomplete_log_records_rejected",
        "placeholder_video_rejected",
        "template_config_rejected",
        "scaffold_implementation_rejected",
        "real_preflight_outputs_untouched",
    ):
        if preflight_self_checks.get(required_check) is not True:
            fail(f"external evidence preflight self-test missing passing check: {required_check}")

    local_falsification_path = RESULTS / "local_falsification_audit.json"
    if not local_falsification_path.exists():
        fail("missing results/local_falsification_audit.json; run scripts/audit_local_falsification.py")
    local_falsification = json.loads(local_falsification_path.read_text(encoding="utf-8"))
    if local_falsification.get("version") != "local_falsification_audit_v1":
        fail("local falsification audit version mismatch")
    if local_falsification.get("passed") is not True:
        fail("local falsification audit did not pass")
    if local_falsification.get("not_external_evidence") is not True:
        fail("local falsification audit must declare that it is not external evidence")
    local_metrics = local_falsification.get("metrics", {})
    if int(local_metrics.get("paired_hard_rows", 0)) < 10000:
        fail("local falsification audit has too few paired hard rows")
    task_regime = local_metrics.get("task_regime_margins", {})
    if task_regime.get("positive_utility_groups") != task_regime.get("groups"):
        fail("local falsification audit does not show positive utility in all hard task-regime slices")
    if float(local_metrics.get("abstention_delta", 1.0)) > 0.02:
        fail("local falsification audit suggests the result may be abstention-driven")
    if float(local_metrics.get("composition_cost_delta", 1.0)) > 0.0:
        fail("local falsification audit suggests the result may be cost/search-driven")
    if float(local_metrics.get("risk_breach_correlation", 0.0)) < 0.70:
        fail("local falsification audit risk-breach correlation is too weak")
    if not (PAPER / "generated_local_falsification_table.tex").exists():
        fail("missing paper/generated_local_falsification_table.tex")

    holdout_path = RESULTS / "holdout_robustness_audit.json"
    if not holdout_path.exists():
        fail("missing results/holdout_robustness_audit.json; run scripts/audit_holdout_robustness.py")
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    if holdout.get("version") != "holdout_robustness_audit_v1":
        fail("holdout robustness audit version mismatch")
    if holdout.get("passed") is not True:
        fail("holdout robustness audit did not pass")
    if holdout.get("not_external_evidence") is not True:
        fail("holdout robustness audit must declare that it is not external evidence")
    holdout_metrics = holdout.get("metrics", {})
    holdout_stats = holdout.get("partition_stats", {})
    if int(holdout_metrics.get("hard_rows_per_method", 0)) < 10_000:
        fail("holdout robustness audit has too few hard rows per method")
    if holdout_stats.get("task_regime", {}).get("positive_utility_groups") != holdout_stats.get("task_regime", {}).get("groups"):
        fail("holdout robustness audit does not show positive utility in all task-regime holdouts")
    if float(holdout_metrics.get("worst_task_regime_success_delta", 0.0)) < 0.015:
        fail("holdout robustness audit worst task-regime success margin is too weak")
    if float(holdout_metrics.get("worst_task_regime_utility_delta", 0.0)) < 0.150:
        fail("holdout robustness audit worst task-regime utility margin is too weak")
    if int(holdout_metrics.get("worst_hash_fold_seed_wins", 0)) < 8:
        fail("holdout robustness audit hash-fold seed wins are too weak")
    if not (PAPER / "generated_holdout_robustness_table.tex").exists():
        fail("missing paper/generated_holdout_robustness_table.tex")

    diagnostic_path = RESULTS / "diagnostic_mechanism_audit.json"
    if not diagnostic_path.exists():
        fail("missing results/diagnostic_mechanism_audit.json; run scripts/audit_diagnostic_mechanism.py")
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    if diagnostic.get("version") != "diagnostic_mechanism_audit_v1":
        fail("diagnostic mechanism audit version mismatch")
    if diagnostic.get("passed") is not True:
        fail("diagnostic mechanism audit did not pass")
    if diagnostic.get("not_external_evidence") is not True:
        fail("diagnostic mechanism audit must declare that it is not external evidence")
    diagnostic_metrics = diagnostic.get("metrics", {})
    if int(diagnostic_metrics.get("proposed_hard_rows", 0)) < 10_000:
        fail("diagnostic mechanism audit has too few proposed hard rows")
    if int(diagnostic_metrics.get("label_mismatches", 1)) != 0:
        fail("diagnostic mechanism audit has label-rule mismatches")
    if int(diagnostic_metrics.get("decision_mismatches", 1)) != 0:
        fail("diagnostic mechanism audit has decision-rule mismatches")
    if int(diagnostic_metrics.get("update_mismatches", 1)) != 0:
        fail("diagnostic mechanism audit has planner-update mismatches")
    if len(diagnostic_metrics.get("label_counts", {})) < 5:
        fail("diagnostic mechanism audit does not observe all five failure labels")
    if len(diagnostic_metrics.get("decision_counts", {})) < 5:
        fail("diagnostic mechanism audit does not observe all five seam decisions")
    if float(diagnostic_metrics.get("accept_mean_realized_breach", 1.0)) + 0.025 >= float(diagnostic_metrics.get("non_accept_mean_realized_breach", 0.0)):
        fail("diagnostic mechanism audit does not separate accepted from non-accepted breach")
    if not (PAPER / "generated_diagnostic_mechanism_table.tex").exists():
        fail("missing paper/generated_diagnostic_mechanism_table.tex")

    decision_path = RESULTS / "decision_quality_audit.json"
    if not decision_path.exists():
        fail("missing results/decision_quality_audit.json; run scripts/audit_decision_quality.py")
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    if decision.get("version") != "decision_quality_audit_v1":
        fail("decision quality audit version mismatch")
    if decision.get("passed") is not True:
        fail("decision quality audit did not pass")
    if decision.get("not_external_evidence") is not True:
        fail("decision quality audit must declare that it is not external evidence")
    decision_metrics = decision.get("metrics", {})
    if int(decision_metrics.get("paired_hard_rows", 0)) < 10_000:
        fail("decision quality audit has too few paired hard rows")
    if float(decision_metrics.get("accept_coverage_delta", 0.0)) < 0.25:
        fail("decision quality audit does not recover enough accepted seams over the predecessor")
    if float(decision_metrics.get("proposed_accept_breach_rate", 1.0)) > 0.005:
        fail("decision quality audit accepted seams exceed the fixed-risk breach-rate gate")
    if int(decision_metrics.get("recovered_accept_pairs", 0)) < 3000:
        fail("decision quality audit has too few recovered accept pairs")
    if float(decision_metrics.get("recovered_accept_utility_delta", 0.0)) < 0.15:
        fail("decision quality audit recovered accepts do not improve utility enough")
    if float(decision_metrics.get("recovered_accept_success_delta", 0.0)) < 0.05:
        fail("decision quality audit recovered accepts do not improve success enough")
    if float(decision_metrics.get("recovered_accept_breach_delta", 1.0)) > -0.05:
        fail("decision quality audit recovered accepts do not reduce breach enough")
    if not (PAPER / "generated_decision_quality_table.tex").exists():
        fail("missing paper/generated_decision_quality_table.tex")

    planner_path = RESULTS / "planner_edge_policy_audit.json"
    if not planner_path.exists():
        fail("missing results/planner_edge_policy_audit.json; run scripts/audit_planner_edge_policy.py")
    planner = json.loads(planner_path.read_text(encoding="utf-8"))
    if planner.get("version") != "planner_edge_policy_audit_v1":
        fail("planner-edge policy audit version mismatch")
    if planner.get("passed") is not True:
        fail("planner-edge policy audit did not pass")
    if planner.get("not_external_evidence") is not True:
        fail("planner-edge policy audit must declare that it is not external evidence")
    planner_metrics = planner.get("metrics", {})
    if int(planner_metrics.get("frontier_count", 0)) < 1500:
        fail("planner-edge policy audit has too few planning frontiers")
    if float(planner_metrics.get("proposed_executable_edge_coverage", 0.0)) < 0.60:
        fail("planner-edge policy audit proposed executable-edge coverage is too low")
    if float(planner_metrics.get("executable_edge_coverage_delta", 0.0)) < 0.45:
        fail("planner-edge policy audit executable-edge coverage delta is too weak")
    if float(planner_metrics.get("selected_utility_delta", 0.0)) < 0.18:
        fail("planner-edge policy audit selected-edge utility delta is too weak")
    if float(planner_metrics.get("selected_success_delta", 0.0)) < 0.05:
        fail("planner-edge policy audit selected-edge success delta is too weak")
    if float(planner_metrics.get("selected_realized_breach_delta", 1.0)) > -0.05:
        fail("planner-edge policy audit selected-edge breach reduction is too weak")
    if float(planner_metrics.get("proposed_selected_breach_over_budget_rate", 1.0)) > 0.005:
        fail("planner-edge policy audit selected-edge breach-over-budget rate is too high")
    if float(planner_metrics.get("frontier_lexicographic_win_rate", 0.0)) < 0.80:
        fail("planner-edge policy audit frontier win rate is too weak")
    if int(planner_metrics.get("positive_task_groups", 0)) < 6:
        fail("planner-edge policy audit does not have positive margins across all task families")
    if int(planner_metrics.get("positive_regime_groups", 0)) < 7:
        fail("planner-edge policy audit does not have positive margins across all seam regimes")
    if int(planner_metrics.get("positive_split_groups", 0)) < 4:
        fail("planner-edge policy audit does not have positive margins across all deployment splits")
    if not (PAPER / "generated_planner_edge_policy_table.tex").exists():
        fail("missing paper/generated_planner_edge_policy_table.tex")

    failure_memory_path = RESULTS / "failure_memory_adaptation_audit.json"
    if not failure_memory_path.exists():
        fail("missing results/failure_memory_adaptation_audit.json; run scripts/audit_failure_memory_adaptation.py")
    failure_memory = json.loads(failure_memory_path.read_text(encoding="utf-8"))
    if failure_memory.get("version") != "failure_memory_adaptation_audit_v1":
        fail("failure-memory adaptation audit version mismatch")
    if failure_memory.get("passed") is not True:
        fail("failure-memory adaptation audit did not pass")
    if failure_memory.get("not_external_evidence") is not True:
        fail("failure-memory adaptation audit must declare that it is not external evidence")
    failure_memory_metrics = failure_memory.get("proposed_metrics", {})
    failure_memory_comparison = failure_memory.get("comparison", {})
    if int(failure_memory_metrics.get("memory_signature_count", 0)) < 2000:
        fail("failure-memory adaptation audit has too few observed-to-held-out signatures")
    if int(failure_memory_metrics.get("frontiers_covered", 0)) < 1600:
        fail("failure-memory adaptation audit covers too few local planning frontiers")
    if int(failure_memory_metrics.get("task_groups", 0)) < 6 or int(failure_memory_metrics.get("regime_groups", 0)) < 7 or int(failure_memory_metrics.get("split_groups", 0)) < 4:
        fail("failure-memory adaptation audit does not cover all local task/regime/split groups")
    if float(failure_memory_metrics.get("memory_breach_future_breach_correlation", 0.0)) < 0.90:
        fail("failure-memory adaptation audit observed breach is not predictive enough of held-out breach")
    if float(failure_memory_metrics.get("memory_breach_mae", 1.0)) > 0.006:
        fail("failure-memory adaptation audit memory breach MAE is too high")
    if float(failure_memory_metrics.get("memory_mae_improvement_over_future_predicted_risk", 0.0)) < 0.002:
        fail("failure-memory adaptation audit does not improve enough over held-out predicted-risk MAE")
    if float(failure_memory_metrics.get("high_low_future_breach_gap", 0.0)) < 0.04:
        fail("failure-memory adaptation audit high-memory-risk signatures do not predict enough future breach separation")
    if float(failure_memory_metrics.get("high_low_future_utility_gap", 0.0)) > -0.12:
        fail("failure-memory adaptation audit high-memory-risk signatures do not predict enough future utility loss")
    if float(failure_memory_comparison.get("high_memory_future_breach_delta", 0.0)) > -0.06:
        fail("failure-memory adaptation audit v5 high-memory-risk breach is not lower enough than predecessor")
    if float(failure_memory_comparison.get("high_memory_future_utility_delta", 0.0)) < 0.20:
        fail("failure-memory adaptation audit v5 high-memory-risk utility is not higher enough than predecessor")
    if not (PAPER / "generated_failure_memory_adaptation_table.tex").exists():
        fail("missing paper/generated_failure_memory_adaptation_table.tex")

    calibration_path = RESULTS / "seam_prediction_calibration_audit.json"
    if not calibration_path.exists():
        fail("missing results/seam_prediction_calibration_audit.json; run scripts/audit_seam_prediction_calibration.py")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    if calibration.get("version") != "seam_prediction_calibration_audit_v1":
        fail("seam prediction calibration audit version mismatch")
    if calibration.get("passed") is not True:
        fail("seam prediction calibration audit did not pass")
    if calibration.get("not_external_evidence") is not True:
        fail("seam prediction calibration audit must declare that it is not external evidence")
    calibration_metrics = calibration.get("proposed_metrics", {})
    calibration_baseline = calibration.get("strongest_baseline_metrics", {})
    if int(calibration_metrics.get("rows", 0)) < 10_000:
        fail("seam prediction calibration audit has too few proposed hard rows")
    if float(calibration_metrics.get("expected_calibration_error_10", 1.0)) > 0.010:
        fail("seam prediction calibration ECE10 is too high")
    if float(calibration_metrics.get("max_calibration_error_10", 1.0)) > 0.015:
        fail("seam prediction calibration max bin gap is too high")
    if float(calibration_metrics.get("risk_breach_correlation", 0.0)) < 0.90:
        fail("seam prediction calibration risk-breach correlation is too weak")
    if calibration_metrics.get("bins_monotone_realized_breach") is not True:
        fail("seam prediction calibration deciles are not monotone in realized breach")
    if float(calibration_metrics.get("expected_calibration_error_10", 1.0)) + 0.005 > float(calibration_baseline.get("expected_calibration_error_10", 0.0)):
        fail("seam prediction calibration does not improve enough over strongest baseline")
    if not (PAPER / "generated_seam_prediction_calibration_table.tex").exists():
        fail("missing paper/generated_seam_prediction_calibration_table.tex")

    presentation_audit_path = RESULTS / "presentation_quality_audit.json"
    if not presentation_audit_path.exists():
        fail("missing results/presentation_quality_audit.json; run scripts/audit_presentation_quality.py after compiling the PDF")
    presentation_audit = json.loads(presentation_audit_path.read_text(encoding="utf-8"))
    if presentation_audit.get("version") != "presentation_quality_audit_v1":
        fail("presentation quality audit version mismatch")
    if presentation_audit.get("passed") is not True:
        fail("presentation quality audit did not pass")
    presentation_checks = presentation_audit.get("checks", [])
    if len(presentation_checks) < 45:
        fail("presentation quality audit has too few checks")
    failed_presentation_checks = [check.get("name") for check in presentation_checks if check.get("passed") is not True]
    if failed_presentation_checks:
        fail(f"presentation quality audit failed checks: {failed_presentation_checks[:8]}")

    figure_readability_path = RESULTS / "figure_readability_audit.json"
    if not figure_readability_path.exists():
        fail("missing results/figure_readability_audit.json; run scripts/audit_figure_readability.py")
    figure_readability = json.loads(figure_readability_path.read_text(encoding="utf-8"))
    if figure_readability.get("version") != "figure_readability_audit_v1":
        fail("figure readability audit version mismatch")
    if figure_readability.get("passed") is not True:
        fail("figure readability audit did not pass")
    if figure_readability.get("not_external_evidence") is not True:
        fail("figure readability audit must declare that it is not external evidence")
    if int(figure_readability.get("figure_count", 0)) < 7:
        fail("figure readability audit checked too few figures")
    if len(figure_readability.get("checks", [])) < 70:
        fail("figure readability audit has too few checks")
    failed_figure_checks = [check.get("name") for check in figure_readability.get("checks", []) if check.get("passed") is not True]
    if failed_figure_checks:
        fail(f"figure readability audit failed checks: {failed_figure_checks[:8]}")
    for item in figure_readability.get("figures", []):
        if int(item.get("width", 0)) < 1500 or int(item.get("height", 0)) < 900:
            fail(f"figure readability audit reports low-resolution figure: {item.get('stem')}")
        if float(item.get("luminance_std", 0.0)) < 0.100:
            fail(f"figure readability audit reports weak contrast: {item.get('stem')}")
        margins = item.get("edge_margins_px", {})
        if int(margins.get("minimum", 0)) < 18:
            fail(f"figure readability audit reports edge clipping: {item.get('stem')}")

    camera_ready_path = RESULTS / "camera_ready_design_audit.json"
    if not camera_ready_path.exists():
        fail("missing results/camera_ready_design_audit.json; run scripts/audit_camera_ready_design.py")
    camera_ready = json.loads(camera_ready_path.read_text(encoding="utf-8"))
    if camera_ready.get("version") != "camera_ready_design_audit_v1":
        fail("camera-ready design audit version mismatch")
    if camera_ready.get("passed") is not True:
        fail("camera-ready design audit did not pass")
    if camera_ready.get("not_external_evidence") is not True:
        fail("camera-ready design audit must declare that it is not external evidence")
    if int(camera_ready.get("pages", 0)) != 30:
        fail("camera-ready design audit page count mismatch")
    if len(camera_ready.get("page_metrics", [])) != 30:
        fail("camera-ready design audit did not render every page")
    if len(camera_ready.get("checks", [])) < 18:
        fail("camera-ready design audit has too few checks")
    failed_camera_checks = [check.get("name") for check in camera_ready.get("checks", []) if check.get("passed") is not True]
    if failed_camera_checks:
        fail(f"camera-ready design audit failed checks: {failed_camera_checks[:8]}")
    density_summary = camera_ready.get("density_summary", {})
    if float(density_summary.get("minimum", 0.0)) < 0.010:
        fail("camera-ready design audit reports a blank or near-blank page")
    if len(density_summary.get("sparse_pages", [])) > 3:
        fail("camera-ready design audit reports too many sparse pages")
    if int(camera_ready.get("minimum_edge_margin_px", 0)) < 20:
        fail("camera-ready design audit reports clipped page margins")

    number_audit_path = RESULTS / "manuscript_number_audit.json"
    if not number_audit_path.exists():
        fail("missing results/manuscript_number_audit.json; run scripts/audit_manuscript_numbers.py")
    number_audit = json.loads(number_audit_path.read_text(encoding="utf-8"))
    if number_audit.get("version") != "manuscript_number_audit_v1":
        fail("manuscript number audit version mismatch")
    if number_audit.get("passed") is not True:
        fail("manuscript number audit did not pass")
    number_checks = number_audit.get("checks", [])
    if len(number_checks) < 20:
        fail("manuscript number audit has too few checks")
    failed_number_checks = [check.get("name") for check in number_checks if check.get("passed") is not True]
    if failed_number_checks:
        fail(f"manuscript number audit failed checks: {failed_number_checks[:8]}")

    claim_audit_path = RESULTS / "claim_boundary_audit.json"
    if not claim_audit_path.exists():
        fail("missing results/claim_boundary_audit.json; run scripts/audit_claim_boundary.py")
    claim_audit = json.loads(claim_audit_path.read_text(encoding="utf-8"))
    if claim_audit.get("version") != "claim_boundary_audit_v1":
        fail("claim boundary audit version mismatch")
    if claim_audit.get("passed") is not True:
        fail("claim boundary audit did not pass")
    claim_ledger_path = ROOT / "docs" / "claim_evidence_ledger.json"
    if not claim_ledger_path.exists():
        fail("missing docs/claim_evidence_ledger.json")

    gap_audit_path = RESULTS / "submission_readiness_gap_audit.json"
    if not gap_audit_path.exists():
        fail("missing results/submission_readiness_gap_audit.json; run scripts/audit_submission_readiness_gap.py")
    gap_audit = json.loads(gap_audit_path.read_text(encoding="utf-8"))
    if gap_audit.get("version") != "submission_readiness_gap_audit_v1":
        fail("submission readiness gap audit version mismatch")
    if gap_audit.get("passed") is not True:
        fail("submission readiness gap audit did not pass")
    if gap_audit.get("objective_complete") is not False:
        fail("submission readiness gap audit unexpectedly reports objective_complete=true")
    if int(gap_audit.get("blocking_missing_requirements", 0)) < 4:
        fail("submission readiness gap audit should still report at least four blocking external gaps")
    if int(gap_audit.get("satisfied_requirements", 0)) < 8:
        fail("submission readiness gap audit reports too few satisfied requirements")
    gap_requirements = gap_audit.get("requirements", [])
    required_gap_phrases = [
        "Independent real-robot or accepted high-fidelity external validation evidence",
        "External rollout metrics recomputed from raw JSONL logs",
        "Manifest-declared real task configs replace non-evidence templates",
        "Manifest-declared independent non-oracle baseline evidence and fairness contract",
    ]
    missing_gap_phrases = [
        phrase
        for phrase in required_gap_phrases
        if not any(entry.get("requirement") == phrase and entry.get("status") == "missing" for entry in gap_requirements)
    ]
    if missing_gap_phrases:
        fail(f"submission readiness gap audit missing required external blockers: {missing_gap_phrases}")

    reviewer_packet_path = DOCS / "reviewer_response_packet.md"
    reviewer_packet_audit_path = RESULTS / "reviewer_response_packet_audit.json"
    if not reviewer_packet_path.exists():
        fail("missing docs/reviewer_response_packet.md; run scripts/build_reviewer_response_packet.py")
    if not reviewer_packet_audit_path.exists():
        fail("missing results/reviewer_response_packet_audit.json; run scripts/build_reviewer_response_packet.py")
    reviewer_packet_audit = json.loads(reviewer_packet_audit_path.read_text(encoding="utf-8"))
    if reviewer_packet_audit.get("version") != "reviewer_response_packet_v1":
        fail("reviewer response packet audit version mismatch")
    if reviewer_packet_audit.get("passed") is not True:
        fail("reviewer response packet audit did not pass")
    if reviewer_packet_audit.get("not_external_evidence") is not True:
        fail("reviewer response packet audit must declare that it is not external evidence")
    if int(reviewer_packet_audit.get("entry_count", 0)) < 12:
        fail("reviewer response packet has too few objection entries")
    required_reviewer_ids = {
        "world_action_not_thresholds",
        "novelty_vs_prior_composer",
        "synthetic_local_evidence",
        "abstention_gaming",
        "search_cost_gaming",
        "decorative_energy_terms",
        "baseline_fairness",
        "planner_update_claim",
        "calibration_transfer",
        "contact_rich_scope",
        "haonan_yilun_fit",
        "submission_readiness",
    }
    reviewer_ids = {entry.get("id") for entry in reviewer_packet_audit.get("entries", [])}
    missing_reviewer_ids = sorted(required_reviewer_ids - reviewer_ids)
    if missing_reviewer_ids:
        fail(f"reviewer response packet missing required objection ids: {missing_reviewer_ids}")
    reviewer_packet_text = reviewer_packet_path.read_text(encoding="utf-8")
    required_reviewer_phrases = [
        "Not evidence: `true`.",
        "adaptive physical world/action models for skill seams",
        "do not list many papers",
        "not for them to be responsible for supplying the missing proof",
        "Close all four blocking external requirements",
        "does not change the current STRONG_REVISE decision",
    ]
    missing_reviewer_phrases = [phrase for phrase in required_reviewer_phrases if phrase not in reviewer_packet_text]
    if missing_reviewer_phrases:
        fail(f"reviewer response packet missing required boundary/outreach phrases: {missing_reviewer_phrases}")
    if not (RESULTS / "reviewer_response_packet_audit.md").exists():
        fail("missing results/reviewer_response_packet_audit.md")

    external_audit_path = RESULTS / "external_evidence_audit.json"
    if not external_audit_path.exists():
        fail("missing results/external_evidence_audit.json; run scripts/audit_external_evidence.py")
    external_audit = json.loads(external_audit_path.read_text(encoding="utf-8"))
    if external_audit.get("version") != "external_evidence_audit_v1":
        fail("external evidence audit version mismatch")
    if external_audit.get("submission_ready") is not False:
        fail("external evidence audit unexpectedly reports submission_ready=true while scope gate is false")
    external_checks = {entry.get("name"): entry.get("passed") for entry in external_audit.get("checks", [])}
    for required_check in (
        "template_exists",
        "log_schema_exists",
        "rollout_validator_exists",
        "config_schema_exists",
        "config_template_audit_exists",
        "config_template_audit_passed",
        "config_template_audit_not_evidence",
        "external_rollout_metrics_exists",
        "external_rollout_metrics_version",
        "external_pairing_integrity_audit_exists",
        "external_release_package_audit_exists",
        "fidelity_acceptance_audit_exists",
        "fidelity_acceptance_audit_version",
        "fidelity_acceptance_contract_passed",
        "blind_eval_audit_exists",
        "blind_eval_audit_version",
        "blind_eval_plan_passed",
        "blind_eval_no_method_leak",
        "adapter_contract_exists",
        "adapter_contract_version",
        "adapter_contract_passed",
        "adapter_contract_is_not_evidence",
    ):
        if external_checks.get(required_check) is not True:
            fail(f"external evidence audit missing passing infrastructure check: {required_check}")
    blocker_names = {entry.get("name") for entry in external_audit.get("blocking_failures", [])}
    required_external_blockers = {
        "manifest_exists",
        "manifest_declares_log_schema",
        "validation_route",
        "episode_log_schema",
        "external_rollout_metrics_passed",
        "external_pairing_integrity_ready",
        "external_release_package_ready",
        "external_fidelity_acceptance_ready",
        "manifest_metrics_match_rollout",
        "task_video_dirs",
        "required_methods",
        "independent_method_implementations",
        "external_config_evidence_passed",
        "external_adapter_contract_evidence_passed",
        "release_logs",
        "release_videos",
        "release_checkpoints",
    }
    missing_external_blockers = sorted(required_external_blockers - blocker_names)
    if missing_external_blockers:
        fail(f"external evidence audit missing expected blockers: {missing_external_blockers}")
    rollout_metrics_path = RESULTS / "external_rollout_metrics.json"
    if not rollout_metrics_path.exists():
        fail("missing results/external_rollout_metrics.json; run scripts/validate_external_rollouts.py --write-results")
    runner_backend_self_test_path = RESULTS / "external_runner_backend_self_test.json"
    if not runner_backend_self_test_path.exists():
        fail("missing results/external_runner_backend_self_test.json; run scripts/self_test_external_runner_backend.py")
    collection_preflight_self_test_path = RESULTS / "external_collection_preflight_self_test.json"
    if not collection_preflight_self_test_path.exists():
        fail("missing results/external_collection_preflight_self_test.json; run scripts/self_test_external_collection_preflight.py")
    if not (ROOT / "scripts" / "self_test_external_collection_preflight.py").exists():
        fail("missing scripts/self_test_external_collection_preflight.py")
    collection_preflight_self_test = json.loads(collection_preflight_self_test_path.read_text(encoding="utf-8"))
    if collection_preflight_self_test.get("version") != "external_collection_preflight_self_test_v1":
        fail("external collection preflight self-test version mismatch")
    if collection_preflight_self_test.get("passed") is not True:
        fail("external collection preflight self-test did not pass")
    if collection_preflight_self_test.get("not_external_evidence") is not True:
        fail("external collection preflight self-test must declare that it is not evidence")
    if collection_preflight_self_test.get("synthetic_collection_ready") is not True:
        fail("external collection preflight self-test should reach collection_ready=true on the temporary fixture")
    if collection_preflight_self_test.get("reference_route_collection_ready") is not True:
        fail("external collection preflight self-test should make the tracked reference route collection-ready after temporary accepted fidelity")
    if collection_preflight_self_test.get("reference_route_run_id") != "maniskill_sapien_reference_preflight_protocol_v1":
        fail("external collection preflight self-test used the wrong tracked reference run id")
    if collection_preflight_self_test.get("reference_route_blocking_missing"):
        fail("external collection preflight self-test reference route still reports blockers after temporary accepted fidelity")
    if int(collection_preflight_self_test.get("row_count", 0) or 0) < 1440:
        fail("external collection preflight self-test has too few synthetic rows")
    collection_preflight_checks = {check.get("name"): check.get("passed") for check in collection_preflight_self_test.get("checks", [])}
    for required_check in (
        "synthetic_preflight_collection_ready",
        "synthetic_row_budget",
        "synthetic_backend_module_ready",
        "synthetic_real_task_configs_ready",
        "synthetic_fidelity_acceptance_ready",
        "synthetic_alias_unsealing_explicit",
        "synthetic_run_id_specific",
        "synthetic_output_logs_empty_or_force",
        "real_readiness_report_not_overwritten",
        "reference_route_collection_ready_after_synthetic_fidelity_acceptance",
        "reference_route_core_checks_pass_after_synthetic_fidelity_acceptance",
    ):
        if collection_preflight_checks.get(required_check) is not True:
            fail(f"external collection preflight self-test missing passing check: {required_check}")
    if not (RESULTS / "external_collection_preflight_self_test.md").exists():
        fail("missing results/external_collection_preflight_self_test.md")
    if not (ROOT / "scripts" / "self_test_external_runner_backend.py").exists():
        fail("missing scripts/self_test_external_runner_backend.py")
    runner_backend_self_test = json.loads(runner_backend_self_test_path.read_text(encoding="utf-8"))
    if runner_backend_self_test.get("version") != "external_runner_backend_self_test_v1":
        fail("external runner backend self-test version mismatch")
    if runner_backend_self_test.get("passed") is not True:
        fail("external runner backend self-test did not pass")
    if runner_backend_self_test.get("not_external_evidence") is not True:
        fail("external runner backend self-test must declare that it is not evidence")
    if int(runner_backend_self_test.get("records_written", 0) or 0) < 2:
        fail("external runner backend self-test wrote too few temporary records")
    if runner_backend_self_test.get("schema_errors"):
        fail(f"external runner backend self-test reported schema errors: {runner_backend_self_test.get('schema_errors')[:3]}")
    runner_backend_checks = {check.get("name"): check.get("passed") for check in runner_backend_self_test.get("checks", [])}
    for required_check in (
        "runner_actual_path_exits_zero",
        "temporary_records_written",
        "temporary_records_schema_valid",
        "temporary_videos_written",
        "diagnostic_fallback_video_rejected_before_jsonl_write",
        "schema_invalid_record_rejected_before_jsonl_write",
        "partial_batch_failure_preserves_official_jsonl",
        "partial_batch_failure_preserves_official_videos",
        "real_manifest_untouched",
    ):
        if runner_backend_checks.get(required_check) is not True:
            fail(f"external runner backend self-test missing passing check: {required_check}")
    if not (RESULTS / "external_runner_backend_self_test.md").exists():
        fail("missing results/external_runner_backend_self_test.md")
    pilot_smoke_audit_path = RESULTS / "external_pilot_smoke_audit.json"
    pilot_smoke_packet_audit_path = RESULTS / "external_pilot_smoke_packet_audit.json"
    for path in (
        ROOT / "scripts" / "audit_external_pilot_smoke.py",
        ROOT / "scripts" / "build_external_pilot_smoke_packet.py",
        EXTERNAL / "pilot_smoke_packet.json",
        EXTERNAL / "pilot_smoke_packet.md",
        EXTERNAL / "pilot_smoke_work_orders.csv",
        pilot_smoke_audit_path,
        RESULTS / "external_pilot_smoke_audit.md",
        pilot_smoke_packet_audit_path,
        RESULTS / "external_pilot_smoke_packet_audit.md",
    ):
        if not path.exists():
            fail(f"missing external pilot smoke artifact: {path}")
    pilot_smoke_audit = json.loads(pilot_smoke_audit_path.read_text(encoding="utf-8"))
    if pilot_smoke_audit.get("version") != "external_pilot_smoke_audit_v1":
        fail("external pilot smoke audit version mismatch")
    if pilot_smoke_audit.get("passed") is not True:
        fail("external pilot smoke audit did not pass")
    if pilot_smoke_audit.get("not_external_evidence") is not True:
        fail("external pilot smoke audit must declare that it is not evidence")
    if pilot_smoke_audit.get("strict_evidence_ready") is not False:
        fail("external pilot smoke audit must not claim strict evidence readiness")
    if int(pilot_smoke_audit.get("records_observed", 0) or 0) != 0:
        fail("external pilot smoke audit should observe zero repository pilot records before an operator run")
    pilot_smoke_packet = json.loads((EXTERNAL / "pilot_smoke_packet.json").read_text(encoding="utf-8"))
    if pilot_smoke_packet.get("version") != "external_pilot_smoke_packet_v1":
        fail("external pilot smoke packet version mismatch")
    if pilot_smoke_packet.get("not_external_evidence") is not True:
        fail("external pilot smoke packet must declare that it is not evidence")
    if int(pilot_smoke_packet.get("pilot_rows", 0) or 0) != 12:
        fail("external pilot smoke packet should use a 12-row first-panel smoke test")
    if "external_validation/pilot_smoke" not in str(pilot_smoke_packet.get("quarantine_root", "")):
        fail("external pilot smoke packet must use the pilot_smoke quarantine root")
    pilot_smoke_packet_audit = json.loads(pilot_smoke_packet_audit_path.read_text(encoding="utf-8"))
    if pilot_smoke_packet_audit.get("version") != "external_pilot_smoke_packet_audit_v1":
        fail("external pilot smoke packet audit version mismatch")
    if pilot_smoke_packet_audit.get("passed") is not True:
        fail("external pilot smoke packet audit did not pass")
    if pilot_smoke_packet_audit.get("not_external_evidence") is not True:
        fail("external pilot smoke packet audit must declare that it is not evidence")
    pilot_smoke_packet_checks = {check.get("name"): check.get("passed") for check in pilot_smoke_packet_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "quarantine_dirs_are_separate_from_official_evidence",
        "runner_backend_probe_already_exercises_actual_runner",
        "pilot_commands_preserve_gate_order",
        "pilot_audit_reports_non_evidence_state",
        "collection_readiness_remains_official_gate",
        "packet_files_written",
    ):
        if pilot_smoke_packet_checks.get(required_check) is not True:
            fail(f"external pilot smoke packet audit missing passing check: {required_check}")
    render_preflight_path = RESULTS / "maniskill_render_video_preflight_audit.json"
    render_preflight_md_path = RESULTS / "maniskill_render_video_preflight_audit.md"
    for path in (
        ROOT / "scripts" / "audit_maniskill_render_video_preflight.py",
        render_preflight_path,
        render_preflight_md_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill render-video preflight artifact: {path}")
    render_preflight = json.loads(render_preflight_path.read_text(encoding="utf-8"))
    if render_preflight.get("version") != "maniskill_render_video_preflight_audit_v2":
        fail("ManiSkill render-video preflight audit version mismatch")
    if render_preflight.get("passed") is not True:
        fail("ManiSkill render-video preflight audit did not pass")
    if render_preflight.get("not_external_evidence") is not True:
        fail("ManiSkill render-video preflight audit must declare that it is not evidence")
    if render_preflight.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill render-video preflight audit must not claim strict external evidence readiness")
    if not isinstance(render_preflight.get("render_video_ready"), bool):
        fail("ManiSkill render-video preflight must record a boolean render_video_ready state")
    if int(render_preflight.get("env_count", 0) or 0) < 1:
        fail("ManiSkill render-video preflight must probe at least one primary environment")
    if render_preflight.get("render_backend") != "cpu":
        fail("ManiSkill render-video preflight must record explicit render_backend=cpu")
    if render_preflight.get("shader_pack") != "minimal":
        fail("ManiSkill render-video preflight must record explicit shader_pack=minimal")
    if int(render_preflight.get("width", 0) or 0) < 16 or int(render_preflight.get("height", 0) or 0) < 16:
        fail("ManiSkill render-video preflight must record explicit render dimensions")
    for record in render_preflight.get("env_records", []) or []:
        if record.get("render_backend") != render_preflight.get("render_backend") or record.get("shader_pack") != render_preflight.get("shader_pack"):
            fail("ManiSkill render-video preflight env records must carry the audited render backend/shader pack")
        if record.get("render_video_ready") is not True and not record.get("failure_progress_stage"):
            fail("ManiSkill render-video preflight failed env records must carry the actual failure progress stage")
        if not record.get("terminal_progress_stage"):
            fail("ManiSkill render-video preflight env records must carry the terminal progress stage")
    if render_preflight.get("render_video_ready") is False and not render_preflight.get("blocking_missing"):
        fail("ManiSkill render-video preflight must explain the render-video blocker when not ready")
    if render_preflight.get("render_video_ready") is False:
        failure_classes = render_preflight.get("renderer_failure_classes", []) or []
        if not isinstance(failure_classes, list) or not failure_classes:
            fail("ManiSkill render-video preflight must classify renderer failures when not ready")
        failure_stages = render_preflight.get("renderer_failure_stages", []) or []
        if not isinstance(failure_stages, list) or not failure_stages:
            fail("ManiSkill render-video preflight must summarize renderer failure stages when not ready")
        remediation = render_preflight.get("operator_remediation", []) or []
        if not isinstance(remediation, list) or len(remediation) < 2:
            fail("ManiSkill render-video preflight must include operator remediation when not ready")
        retest_commands = "\n".join(render_preflight.get("renderer_profile_retest_commands", []) or [])
        for fragment in ("--render-backend cpu", "--render-backend gpu", "--render-backend sapien_cuda"):
            if fragment not in retest_commands:
                fail(f"ManiSkill render-video preflight missing renderer retest command fragment: {fragment}")
    if render_preflight.get("profile_matrix_enabled") is not True:
        fail("ManiSkill render-video preflight must run the renderer profile matrix")
    profile_matrix_records = render_preflight.get("profile_matrix_records", []) or []
    if len(profile_matrix_records) < 3:
        fail("ManiSkill render-video preflight matrix must record at least cpu/gpu/sapien_cuda attempts")
    profile_backends = {record.get("profile_render_backend") for record in profile_matrix_records}
    for backend in ("cpu", "gpu", "sapien_cuda"):
        if backend not in profile_backends:
            fail(f"ManiSkill render-video preflight matrix missing backend attempt: {backend}")
    for record in profile_matrix_records:
        if record.get("not_external_evidence") is not True:
            fail("ManiSkill render-video preflight matrix records must be non-evidence")
        if not (record.get("timed_out") or record.get("parsed_marker")):
            fail("ManiSkill render-video preflight matrix records must have terminal status")
    render_preflight_checks = {check.get("name"): check.get("passed") for check in render_preflight.get("checks", [])}
    for required_check in (
        "render_preflight_is_non_evidence",
        "quarantine_paths_are_not_official_evidence",
        "primary_envs_loaded",
        "each_probe_has_terminal_status",
        "render_progress_markers_recorded",
        "render_readiness_recorded_without_overclaim",
        "blocking_summary_present_when_not_ready",
        "renderer_failure_class_recorded_when_not_ready",
        "renderer_failure_stage_recorded_when_not_ready",
        "operator_remediation_present_when_not_ready",
        "profile_retest_commands_cover_renderer_backends",
        "profile_matrix_records_renderer_backends",
        "profile_matrix_terminal_status",
        "profile_matrix_quarantined_non_evidence",
        "no_real_manifest_written",
    ):
        if render_preflight_checks.get(required_check) is not True:
            fail(f"ManiSkill render-video preflight audit missing passing check: {required_check}")
    render_resource_path = RESULTS / "maniskill_render_resource_sweep.json"
    render_resource_md_path = RESULTS / "maniskill_render_resource_sweep.md"
    render_resource_csv_path = EXTERNAL / "render_resource_sweep_work_orders.csv"
    for path in (
        ROOT / "scripts" / "audit_maniskill_render_resource_sweep.py",
        render_resource_path,
        render_resource_md_path,
        render_resource_csv_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill render resource sweep artifact: {path}")
    render_resource = json.loads(render_resource_path.read_text(encoding="utf-8"))
    if render_resource.get("version") != "maniskill_render_resource_sweep_v1":
        fail("ManiSkill render resource sweep version mismatch")
    if render_resource.get("passed") is not True:
        fail("ManiSkill render resource sweep did not pass")
    if render_resource.get("not_external_evidence") is not True:
        fail("ManiSkill render resource sweep must declare that it is not evidence")
    if render_resource.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill render resource sweep must not claim strict external evidence readiness")
    if render_resource.get("any_render_video_ready") is not False:
        fail("current local render resource sweep should remain not ready until an accepted renderer writes MP4s")
    if render_resource.get("descriptor_pool_failure_persists_at_minimum_resolution") is not True:
        fail("current local render resource sweep must record descriptor-pool failure persistence at minimum resolution")
    if int(render_resource.get("record_count", 0) or 0) < 3:
        fail("ManiSkill render resource sweep must include at least three renderer profile attempts")
    if "vulkan_descriptor_pool_exhaustion" not in (render_resource.get("renderer_failure_classes", []) or []):
        fail("ManiSkill render resource sweep must preserve the Vulkan descriptor-pool failure class")
    for record in render_resource.get("records", []) or []:
        if record.get("not_external_evidence") is not True:
            fail("ManiSkill render resource sweep records must be non-evidence")
        if not str(record.get("output_path", "")).startswith("external_validation/render_resource_sweep/"):
            fail("ManiSkill render resource sweep outputs must remain quarantined")
        if not (record.get("timed_out") or record.get("parsed_marker")):
            fail("ManiSkill render resource sweep records must have terminal status")
    render_resource_checks = {check.get("name"): check.get("passed") for check in render_resource.get("checks", [])}
    for required_check in (
        "resource_sweep_is_non_evidence",
        "profiles_loaded",
        "primary_env_loaded",
        "each_probe_has_terminal_status",
        "quarantine_paths_are_not_official_evidence",
        "descriptor_pool_failure_classified_or_render_ready",
        "no_real_manifest_written",
    ):
        if render_resource_checks.get(required_check) is not True:
            fail(f"ManiSkill render resource sweep missing passing check: {required_check}")
    pilot_runtime_path = RESULTS / "maniskill_pilot_runtime_liveness_audit.json"
    pilot_runtime_md_path = RESULTS / "maniskill_pilot_runtime_liveness_audit.md"
    pilot_reset_triage_path = RESULTS / "maniskill_pilot_reset_timeout_triage.json"
    pilot_reset_triage_md_path = RESULTS / "maniskill_pilot_reset_timeout_triage.md"
    for path in (
        ROOT / "scripts" / "audit_maniskill_pilot_runtime_liveness.py",
        pilot_runtime_path,
        pilot_runtime_md_path,
        pilot_reset_triage_path,
        pilot_reset_triage_md_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill pilot runtime liveness artifact: {path}")
    pilot_runtime = json.loads(pilot_runtime_path.read_text(encoding="utf-8"))
    pilot_reset_triage = json.loads(pilot_reset_triage_path.read_text(encoding="utf-8"))
    if pilot_runtime.get("version") != "maniskill_pilot_runtime_liveness_audit_v1":
        fail("ManiSkill pilot runtime liveness audit version mismatch")
    if pilot_runtime.get("passed") is not True:
        fail("ManiSkill pilot runtime liveness audit did not pass")
    if pilot_runtime.get("not_external_evidence") is not True:
        fail("ManiSkill pilot runtime liveness audit must declare that it is not evidence")
    if pilot_runtime.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill pilot runtime liveness audit must not claim strict external evidence readiness")
    if pilot_runtime.get("pilot_runtime_ready") is not False:
        fail("current local ManiSkill pilot runtime should remain not ready before accepted runtime evidence")
    if pilot_runtime.get("render_video_ready") is not False:
        fail("current local ManiSkill pilot runtime must not mark render-backed video ready")
    if pilot_runtime.get("render_backend") != "cpu":
        fail("ManiSkill pilot runtime liveness audit must record explicit render_backend=cpu")
    if pilot_runtime.get("shader_pack") != "minimal":
        fail("ManiSkill pilot runtime liveness audit must record explicit shader_pack=minimal")
    if int(pilot_runtime.get("render_width", 0) or 0) < 16 or int(pilot_runtime.get("render_height", 0) or 0) < 16:
        fail("ManiSkill pilot runtime liveness audit must record explicit render dimensions")
    pilot_runtime_records = int(pilot_runtime.get("records_observed", 0) or 0)
    pilot_runtime_videos = int(pilot_runtime.get("videos_written", 0) or 0)
    pilot_runtime_fallbacks = len(pilot_runtime.get("diagnostic_video_fallbacks", []) or [])
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
    )
    if not (pilot_runtime_diagnostic_io or pilot_runtime_unavailable or pilot_runtime_diagnostic_rejected):
        fail(
            "ManiSkill pilot runtime liveness audit must either record a quarantined diagnostic "
            "non-evidence row/video, fail closed with zero rows/videos when the runtime is unavailable, "
            "or record official guard rejection of a diagnostic sidecar before JSONL write"
        )
    if not str(pilot_runtime.get("failure_summary", "")).strip():
        fail("ManiSkill pilot runtime liveness audit must record a failure summary")
    nested_pilot_reset_triage = pilot_runtime.get("reset_timeout_triage", {})
    if pilot_reset_triage.get("version") != "maniskill_pilot_reset_timeout_triage_v1":
        fail("ManiSkill pilot reset-timeout triage version mismatch")
    if nested_pilot_reset_triage != pilot_reset_triage:
        fail("ManiSkill pilot reset-timeout triage sidecar must match the liveness audit payload")
    if pilot_reset_triage.get("not_external_evidence") is not True:
        fail("ManiSkill pilot reset-timeout triage must declare that it is not evidence")
    if pilot_reset_triage.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill pilot reset-timeout triage must not claim strict external evidence readiness")
    if pilot_runtime.get("timed_out") is True and pilot_runtime.get("last_progress_stage") == "reset_scene_start":
        if pilot_reset_triage.get("reset_timeout") is not True:
            fail("ManiSkill pilot reset-timeout triage must mark reset_timeout=true for reset-scene timeouts")
        if pilot_reset_triage.get("triage_status") != "RESET_SCENE_TIMEOUT_TRIAGE_READY":
            fail("ManiSkill pilot reset-timeout triage must be ready for the current reset-scene timeout")
        for required_field in ("task_family", "method_name", "method_alias", "scene_id", "config_hash", "primary_env_id"):
            if not str(pilot_reset_triage.get(required_field, "")).strip():
                fail(f"ManiSkill pilot reset-timeout triage missing field: {required_field}")
        if not str(pilot_reset_triage.get("last_backend_progress_stage", "")).strip():
            fail("ManiSkill pilot reset-timeout triage must record the last backend progress stage")
        if not pilot_reset_triage.get("backend_progress_stages"):
            fail("ManiSkill pilot reset-timeout triage must record backend progress stages")
        if len(pilot_reset_triage.get("operator_next_actions", []) or []) < 5:
            fail("ManiSkill pilot reset-timeout triage must include operator next actions")
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", [])}
    for required_check in (
        "runtime_guard_is_non_evidence",
        "quarantine_paths_are_not_official_evidence",
        "bounded_runner_subprocess_exercised",
        "collection_progress_markers_recorded",
        "backend_reset_substage_markers_recorded",
        "timeout_or_result_recorded_as_readiness_state",
        "ready_requires_schema_valid_records_and_videos",
        "runner_io_ready_allows_only_quarantined_diagnostic_fallback",
        "official_guard_rejects_diagnostic_before_jsonl_write",
        "diagnostic_rejection_paths_are_quarantined",
        "diagnostic_fallback_does_not_mark_render_ready",
        "no_real_manifest_written",
        "reset_timeout_triage_is_non_evidence",
        "reset_timeout_triage_context_recorded",
        "reset_timeout_operator_actions_present",
    ):
        if pilot_runtime_checks.get(required_check) is not True:
            fail(f"ManiSkill pilot runtime liveness audit missing passing check: {required_check}")
    if pilot_runtime.get("timed_out") is True and not str(pilot_runtime.get("last_progress_stage", "")).strip():
        fail("ManiSkill pilot runtime timeout must record the last collection progress stage")
    render_machine_path = RESULTS / "maniskill_render_machine_qualification.json"
    render_machine_md_path = RESULTS / "maniskill_render_machine_qualification.md"
    render_machine_packet_path = EXTERNAL / "render_machine_qualification_packet.md"
    render_remediation_path = RESULTS / "maniskill_render_failure_remediation.json"
    render_remediation_md_path = RESULTS / "maniskill_render_failure_remediation.md"
    render_remediation_csv_path = EXTERNAL / "render_failure_remediation_work_orders.csv"
    for path in (
        ROOT / "scripts" / "build_maniskill_render_machine_qualification.py",
        render_machine_path,
        render_machine_md_path,
        render_machine_packet_path,
        render_remediation_path,
        render_remediation_md_path,
        render_remediation_csv_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill render machine qualification artifact: {path}")
    render_machine = json.loads(render_machine_path.read_text(encoding="utf-8"))
    render_remediation = json.loads(render_remediation_path.read_text(encoding="utf-8"))
    if render_machine.get("version") != "maniskill_render_machine_qualification_v1":
        fail("ManiSkill render machine qualification version mismatch")
    if render_machine.get("passed") is not True:
        fail("ManiSkill render machine qualification audit did not pass")
    if render_machine.get("not_external_evidence") is not True:
        fail("ManiSkill render machine qualification must declare that it is not evidence")
    if render_machine.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill render machine qualification must not claim strict external evidence readiness")
    if render_machine.get("qualification_state") != "DO_NOT_COLLECT_RENDER_MACHINE":
        fail("current local render machine qualification should fail closed")
    if render_machine.get("render_machine_qualified") is not False:
        fail("current local render machine must remain unqualified until render-backed MP4s and liveness are ready")
    if int(render_machine.get("render_records_seen", 0) or 0) < 1:
        fail("render machine qualification must inspect render preflight records")
    if not render_machine.get("blocking_missing"):
        fail("render machine qualification must list missing render-machine evidence while unqualified")
    if render_machine.get("render_machine_qualified") is False and not render_machine.get("renderer_failure_stages"):
        fail("render machine qualification must propagate renderer failure stages while unqualified")
    if render_remediation.get("version") != "maniskill_render_failure_remediation_v1":
        fail("ManiSkill render failure remediation version mismatch")
    if render_remediation.get("passed") is not True:
        fail("ManiSkill render failure remediation audit did not pass")
    if render_remediation.get("not_external_evidence") is not True:
        fail("ManiSkill render failure remediation must declare that it is not evidence")
    if render_remediation.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill render failure remediation must not claim strict external evidence readiness")
    if render_remediation.get("qualification_state") != render_machine.get("qualification_state"):
        fail("ManiSkill render failure remediation must inherit the render-machine qualification state")
    if render_remediation.get("remediation_state") != "RENDER_REMEDIATION_REQUIRED":
        fail("current local renderer must keep render failure remediation required")
    if not render_remediation.get("work_orders") or len(render_remediation.get("work_orders", [])) < 6:
        fail("ManiSkill render failure remediation must include work orders")
    work_order_ids = {str(item.get("id", "")) for item in render_remediation.get("work_orders", []) if isinstance(item, dict)}
    for required_work_order in (
        "renderer_platform_probe",
        "render_profile_matrix_retest",
        "pilot_liveness_retest",
        "diagnostic_fallback_exclusion",
        "fidelity_acceptance_after_render_ready",
        "collection_readiness_gate",
    ):
        if required_work_order not in work_order_ids:
            fail(f"ManiSkill render failure remediation missing work order: {required_work_order}")
    if not render_remediation.get("liveness_render_errors"):
        fail("ManiSkill render failure remediation must capture liveness render errors")
    render_machine_commands = "\n".join(render_machine.get("operator_commands", []) or [])
    for fragment in (
        "probe_external_platform.py",
        "audit_maniskill_render_video_preflight.py",
        "audit_maniskill_pilot_runtime_liveness.py",
        "materialize_fidelity_acceptance.py",
        "audit_external_collection_readiness.py",
    ):
        if fragment not in render_machine_commands:
            fail(f"render machine qualification missing operator command fragment: {fragment}")
    render_machine_checks = {check.get("name"): check.get("passed") for check in render_machine.get("checks", [])}
    render_remediation_checks = {check.get("name"): check.get("passed") for check in render_remediation.get("checks", [])}
    for required_check in (
        "qualification_packet_is_non_evidence",
        "source_audits_loaded",
        "render_preflight_remains_non_evidence",
        "all_primary_envs_have_terminal_render_records",
        "qualification_state_matches_render_and_liveness",
        "current_machine_fail_closed_when_render_not_ready",
        "renderer_failure_classes_propagated",
        "renderer_failure_stages_propagated",
        "diagnostic_fallbacks_block_evidence",
        "no_real_manifest_written",
        "operator_commands_cover_platform_render_liveness_acceptance_and_collection_readiness",
    ):
        if render_machine_checks.get(required_check) is not True:
            fail(f"ManiSkill render machine qualification missing passing check: {required_check}")
    for required_check in (
        "render_failure_remediation_is_non_evidence",
        "remediation_inherits_fail_closed_state",
        "liveness_render_guard_failure_captured",
        "work_orders_cover_required_gate_sequence",
        "diagnostic_fallbacks_remain_blocking_when_present",
        "no_real_manifest_written",
    ):
        if render_remediation_checks.get(required_check) is not True:
            fail(f"ManiSkill render failure remediation missing passing check: {required_check}")

    render_machine_self_test_path = RESULTS / "maniskill_render_machine_qualification_self_test.json"
    render_machine_self_test_md_path = RESULTS / "maniskill_render_machine_qualification_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_maniskill_render_machine_qualification.py",
        render_machine_self_test_path,
        render_machine_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill render machine qualification self-test artifact: {path}")
    render_machine_self_test = json.loads(render_machine_self_test_path.read_text(encoding="utf-8"))
    if render_machine_self_test.get("version") != "maniskill_render_machine_qualification_self_test_v1":
        fail("ManiSkill render machine qualification self-test version mismatch")
    if render_machine_self_test.get("passed") is not True:
        fail("ManiSkill render machine qualification self-test did not pass")
    if render_machine_self_test.get("not_external_evidence") is not True:
        fail("ManiSkill render machine qualification self-test must declare that it is not evidence")
    if render_machine_self_test.get("strict_external_evidence_ready") is not False:
        fail("ManiSkill render machine qualification self-test must not claim strict evidence readiness")
    if render_machine_self_test.get("synthetic_ready_state") != "QUALIFIED_FOR_RENDER_BACKED_PILOT":
        fail("ManiSkill render machine qualification self-test must prove a complete synthetic render/liveness fixture can qualify")
    if render_machine_self_test.get("synthetic_fail_closed_state") != "DO_NOT_COLLECT_RENDER_MACHINE":
        fail("ManiSkill render machine qualification self-test must prove render failures fail closed")
    if render_machine_self_test.get("missing_env_rejected") is not True:
        fail("ManiSkill render machine qualification self-test must reject missing environment render records")
    if render_machine_self_test.get("diagnostic_fallback_rejected") is not True:
        fail("ManiSkill render machine qualification self-test must reject diagnostic fallback media")
    if render_machine_self_test.get("ready_remediation_state") != "RENDER_REMEDIATION_READY":
        fail("ManiSkill render machine qualification self-test must prove ready remediation state")
    if render_machine_self_test.get("failed_remediation_state") != "RENDER_REMEDIATION_REQUIRED":
        fail("ManiSkill render machine qualification self-test must prove failed remediation state")
    if render_machine_self_test.get("real_reports_untouched") is not True:
        fail("ManiSkill render machine qualification self-test must leave real render-machine reports untouched")
    self_required_work_orders = set(render_machine_self_test.get("required_work_orders", []) or [])
    for required_work_order in (
        "renderer_platform_probe",
        "render_profile_matrix_retest",
        "pilot_liveness_retest",
        "diagnostic_fallback_exclusion",
        "fidelity_acceptance_after_render_ready",
        "collection_readiness_gate",
    ):
        if required_work_order not in self_required_work_orders:
            fail(f"ManiSkill render machine qualification self-test missing work order: {required_work_order}")
    render_machine_self_checks = {
        check.get("name"): check.get("passed") for check in render_machine_self_test.get("checks", [])
    }
    for required_check in (
        "synthetic_ready_machine_qualifies",
        "synthetic_ready_remediation_is_ready",
        "render_failure_fails_closed",
        "failure_remediation_work_orders_cover_gate_sequence",
        "missing_environment_record_fails_closed",
        "diagnostic_fallback_blocks_qualification",
        "real_render_machine_reports_not_overwritten",
    ):
        if render_machine_self_checks.get(required_check) is not True:
            fail(f"ManiSkill render machine qualification self-test missing passing check: {required_check}")

    ablation_packet_path = EXTERNAL / "ablation_collection_packet.json"
    ablation_packet_md_path = EXTERNAL / "ablation_collection_packet.md"
    ablation_orders_path = EXTERNAL / "ablation_collection_work_orders.csv"
    ablation_audit_path = RESULTS / "external_ablation_collection_audit.json"
    ablation_audit_md_path = RESULTS / "external_ablation_collection_audit.md"
    ablation_self_test_path = RESULTS / "external_ablation_collection_packet_self_test.json"
    ablation_self_test_md_path = RESULTS / "external_ablation_collection_packet_self_test.md"
    for path in (
        ROOT / "scripts" / "build_external_ablation_collection_packet.py",
        ROOT / "scripts" / "self_test_external_ablation_collection_packet.py",
        ablation_packet_path,
        ablation_packet_md_path,
        ablation_orders_path,
        ablation_audit_path,
        ablation_audit_md_path,
        ablation_self_test_path,
        ablation_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external ablation collection packet artifact: {path}")
    ablation_packet = json.loads(ablation_packet_path.read_text(encoding="utf-8"))
    ablation_audit = json.loads(ablation_audit_path.read_text(encoding="utf-8"))
    ablation_self_test = json.loads(ablation_self_test_path.read_text(encoding="utf-8"))
    required_ablation_ids = {
        "basin_overlap",
        "barrier_height",
        "descent_continuity",
        "risk_calibration",
        "seam_repair",
    }
    for payload, label in ((ablation_packet, "packet"), (ablation_audit, "audit")):
        expected_version = (
            "external_ablation_collection_packet_v1"
            if label == "packet"
            else "external_ablation_collection_audit_v1"
        )
        if payload.get("version") != expected_version:
            fail(f"external ablation collection {label} version mismatch")
        if payload.get("passed") is not True:
            fail(f"external ablation collection {label} did not pass")
        if payload.get("ablation_collection_packet_ready") is not True:
            fail(f"external ablation collection {label} must declare packet readiness")
        if payload.get("not_external_evidence") is not True:
            fail(f"external ablation collection {label} must declare that it is not evidence")
        if payload.get("strict_external_evidence_ready") is not False:
            fail(f"external ablation collection {label} must keep strict external evidence false")
        if payload.get("manifest_ablation_evidence_ready") is not False:
            fail(f"external ablation collection {label} must keep manifest ablation evidence false")
        if int(payload.get("work_order_count", 0) or 0) != 5:
            fail(f"external ablation collection {label} must define exactly five work orders")
        if int(payload.get("expected_ablation_records", 0) or 0) < 600:
            fail(f"external ablation collection {label} has too few expected ablation records")
        ablation_ids = {str(row.get("id", "")) for row in payload.get("required_ablations", []) or []}
        if ablation_ids != required_ablation_ids:
            fail(f"external ablation collection {label} required ablation IDs mismatch: {sorted(ablation_ids)}")
    ablation_commands = "\n".join(ablation_audit.get("operator_commands", []) or [])
    for fragment in (
        "build_external_ablation_collection_packet.py",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in ablation_commands:
            fail(f"external ablation collection audit missing operator command fragment: {fragment}")
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "collection_plan_loaded",
        "task_and_reset_budget_preserved",
        "required_ablations_match_strict_audit",
        "every_required_ablation_has_work_order",
        "work_orders_use_local_reference_variants",
        "work_orders_are_actionable_and_artifact_bound",
        "manifest_template_declares_ablation_booleans",
        "operator_commands_cover_collection_manifest_rollout_and_strict_evidence",
        "no_real_manifest_written",
    ):
        if ablation_checks.get(required_check) is not True:
            fail(f"external ablation collection audit missing passing check: {required_check}")
    if ablation_self_test.get("version") != "external_ablation_collection_packet_self_test_v1":
        fail("external ablation collection packet self-test version mismatch")
    if ablation_self_test.get("passed") is not True:
        fail("external ablation collection packet self-test did not pass")
    if ablation_self_test.get("not_external_evidence") is not True:
        fail("external ablation collection packet self-test must declare that it is not evidence")
    if ablation_self_test.get("strict_external_evidence_ready") is not False:
        fail("external ablation collection packet self-test must keep strict external evidence false")
    for field in (
        "temporary_packet_ready",
        "missing_work_order_rejected",
        "premature_evidence_promotion_rejected",
        "collection_budget_shrink_rejected",
        "strict_missing_ablation_drift_rejected",
        "local_reference_variant_drift_rejected",
        "manifest_ablation_boolean_omission_rejected",
        "work_order_artifact_command_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "packet_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if ablation_self_test.get(field) is not True:
            fail(f"external ablation collection packet self-test field must be true: {field}")
    ablation_self_checks = {check.get("name"): check.get("passed") for check in ablation_self_test.get("checks", [])}
    for required_check in (
        "temporary_ablation_collection_packet_ready_but_non_evidence",
        "missing_ablation_work_order_rejected",
        "premature_evidence_promotion_rejected",
        "collection_budget_shrink_rejected",
        "strict_missing_ablation_drift_rejected",
        "local_reference_variant_drift_rejected",
        "manifest_ablation_boolean_omission_rejected",
        "work_order_artifact_command_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "packet_file_deletion_rejected",
        "real_ablation_packet_outputs_untouched",
    ):
        if ablation_self_checks.get(required_check) is not True:
            fail(f"external ablation collection packet self-test missing passing check: {required_check}")

    intake_json_path = EXTERNAL / "evidence_intake_ledger.json"
    intake_md_path = EXTERNAL / "evidence_intake_ledger.md"
    intake_csv_path = EXTERNAL / "evidence_intake_ledger.csv"
    intake_audit_path = RESULTS / "external_evidence_intake_ledger_audit.json"
    intake_audit_md_path = RESULTS / "external_evidence_intake_ledger_audit.md"
    intake_self_test_path = RESULTS / "external_evidence_intake_ledger_self_test.json"
    intake_self_test_md_path = RESULTS / "external_evidence_intake_ledger_self_test.md"
    for path in (
        ROOT / "scripts" / "build_external_evidence_intake_ledger.py",
        ROOT / "scripts" / "self_test_external_evidence_intake_ledger.py",
        intake_json_path,
        intake_md_path,
        intake_csv_path,
        intake_audit_path,
        intake_audit_md_path,
        intake_self_test_path,
        intake_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external evidence intake ledger artifact: {path}")
    intake_ledger = json.loads(intake_audit_path.read_text(encoding="utf-8"))
    intake_self_test = json.loads(intake_self_test_path.read_text(encoding="utf-8"))
    if intake_ledger.get("version") != "external_evidence_intake_ledger_v1":
        fail("external evidence intake ledger version mismatch")
    if intake_ledger.get("passed") is not True:
        fail("external evidence intake ledger did not pass")
    if intake_ledger.get("not_external_evidence") is not True:
        fail("external evidence intake ledger must declare that it is not evidence")
    if intake_ledger.get("strict_external_evidence_ready") is not False:
        fail("external evidence intake ledger must keep strict external evidence false")
    if int(intake_ledger.get("blocking_failure_count", 0) or 0) < 30:
        fail("external evidence intake ledger maps too few strict evidence failures")
    if intake_ledger.get("blocking_failure_count") != intake_ledger.get("mapped_failure_count"):
        fail("external evidence intake ledger must map every current strict evidence failure")
    if intake_ledger.get("unmapped_failures"):
        fail(f"external evidence intake ledger has unmapped failures: {intake_ledger.get('unmapped_failures')}")
    if len(intake_ledger.get("closure_groups", []) or []) < 8:
        fail("external evidence intake ledger must include all closure groups")
    intake_checks = {check.get("name"): check.get("passed") for check in intake_ledger.get("checks", [])}
    for required_check in (
        "ledger_is_non_evidence_and_fail_closed",
        "strict_external_evidence_is_currently_missing",
        "every_blocking_failure_is_mapped",
        "all_required_closure_groups_present",
        "source_packets_loaded",
        "manifest_template_declares_expected_evidence_fields",
        "strict_command_spine_covers_final_evidence_path",
        "rows_are_actionable_and_source_bound",
        "no_real_manifest_written",
    ):
        if intake_checks.get(required_check) is not True:
            fail(f"external evidence intake ledger missing passing check: {required_check}")
    if intake_self_test.get("version") != "external_evidence_intake_ledger_self_test_v1":
        fail("external evidence intake ledger self-test version mismatch")
    if intake_self_test.get("passed") is not True:
        fail("external evidence intake ledger self-test did not pass")
    if intake_self_test.get("not_external_evidence") is not True:
        fail("external evidence intake ledger self-test must declare that it is not evidence")
    if intake_self_test.get("strict_external_evidence_ready") is not False:
        fail("external evidence intake ledger self-test must keep strict external evidence false")
    for field in (
        "temporary_ledger_ready",
        "missing_ledger_row_rejected",
        "premature_evidence_promotion_rejected",
        "unmapped_failure_rejected",
        "closure_group_omission_rejected",
        "source_packet_failure_rejected",
        "manifest_template_omission_rejected",
        "row_source_completion_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "ledger_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if intake_self_test.get(field) is not True:
            fail(f"external evidence intake ledger self-test field must be true: {field}")
    intake_self_checks = {check.get("name"): check.get("passed") for check in intake_self_test.get("checks", [])}
    for required_check in (
        "temporary_evidence_intake_ledger_ready_but_non_evidence",
        "missing_ledger_row_rejected",
        "premature_evidence_promotion_rejected",
        "unmapped_failure_rejected",
        "closure_group_omission_rejected",
        "source_packet_failure_rejected",
        "manifest_template_omission_rejected",
        "row_source_completion_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "ledger_file_deletion_rejected",
        "real_evidence_intake_outputs_untouched",
    ):
        if intake_self_checks.get(required_check) is not True:
            fail(f"external evidence intake ledger self-test missing passing check: {required_check}")

    if not (ROOT / "scripts" / "self_test_external_rollout_validator.py").exists():
        fail("missing scripts/self_test_external_rollout_validator.py")
    rollout_self_test_path = RESULTS / "external_rollout_validator_self_test.json"
    rollout_self_test_md_path = RESULTS / "external_rollout_validator_self_test.md"
    for path in (
        rollout_self_test_path,
        rollout_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external rollout validator self-test artifact: {path}")
    rollout_self_test = json.loads(rollout_self_test_path.read_text(encoding="utf-8"))
    if rollout_self_test.get("version") != "external_rollout_validator_self_test_v1":
        fail("external rollout validator self-test version mismatch")
    if rollout_self_test.get("passed") is not True:
        fail("external rollout validator self-test did not pass")
    if rollout_self_test.get("not_external_evidence") is not True:
        fail("external rollout validator self-test must declare that it is not evidence")
    if int(rollout_self_test.get("synthetic_records_loaded", 0) or 0) < 1440:
        fail("external rollout validator self-test has too few synthetic rollout records")
    if int(rollout_self_test.get("synthetic_task_count", 0) or 0) < 4:
        fail("external rollout validator self-test has too few synthetic task families")
    if int(rollout_self_test.get("synthetic_method_count", 0) or 0) < 12:
        fail("external rollout validator self-test has too few synthetic methods")
    if rollout_self_test.get("synthetic_confidence_gates_passed") is not True:
        fail("external rollout validator self-test must pass synthetic confidence gates")
    if rollout_self_test.get("weak_confidence_rejected") is not True:
        fail("external rollout validator self-test must reject weak confidence bounds")
    if rollout_self_test.get("strict_video_rejections_checked") is not True:
        fail("external rollout validator self-test must check strict video rejections")
    if rollout_self_test.get("real_rollout_reports_untouched") is not True:
        fail("external rollout validator self-test must leave real rollout reports untouched")
    rollout_self_test_checks = {check.get("name"): check.get("passed") for check in rollout_self_test.get("checks", [])}
    for required_check in (
        "synthetic_records_recomputed",
        "synthetic_threshold_metrics_match_expected",
        "synthetic_confidence_gates_pass",
        "weak_confidence_rejected",
        "schema_missing_required_field_rejected",
        "missing_required_method_rejected",
        "weak_episode_count_rejected",
        "short_record_count_rejected",
        "duplicate_method_panel_rejected",
        "missing_method_panel_rejected",
        "duplicate_rollout_identity_rejected",
        "duplicate_video_path_rejected",
        "stale_task_config_hash_rejected",
        "stale_task_config_row_rejected",
        "spoofed_policy_or_config_hash_rejected",
        "strict_video_fixture_accepts_mp4_like_file",
        "strict_video_fixture_rejects_fake_mp4",
        "strict_video_fixture_rejects_forbidden_fragments",
        "real_rollout_metrics_report_not_overwritten",
    ):
        if rollout_self_test_checks.get(required_check) is not True:
            fail(f"external rollout validator self-test missing passing check: {required_check}")
    rollout_metrics = json.loads(rollout_metrics_path.read_text(encoding="utf-8"))
    rollout_summary = rollout_metrics.get("summary", {})
    if rollout_summary.get("version") != "external_rollout_metrics_v1":
        fail("external rollout metric summary version mismatch")
    if rollout_metrics.get("passed") is not False:
        fail("external rollout validation unexpectedly passed while scope gate is false")
    schema_errors = rollout_metrics.get("schema_errors", [])
    if not any("missing manifest" in str(error) for error in schema_errors):
        fail("external rollout validation should currently fail because external_validation/manifest.json is missing")
    rollout_validator_text = (ROOT / "scripts" / "validate_external_rollouts.py").read_text(encoding="utf-8")
    rollout_self_test_text = (ROOT / "scripts" / "self_test_external_rollout_validator.py").read_text(encoding="utf-8")
    evidence_pipeline_self_test_text = (ROOT / "scripts" / "self_test_external_evidence_pipeline.py").read_text(encoding="utf-8")
    audit_external_evidence_text = (ROOT / "scripts" / "audit_external_evidence.py").read_text(encoding="utf-8")
    for term in (
        "strict_video_evidence",
        "MIN_STRICT_VIDEO_BYTES",
        "FORBIDDEN_VIDEO_PATH_FRAGMENTS",
        "diagnostic fallback sidecar",
        "not MP4-like evidence",
        "REQUIRED_METHODS",
        "manifest missing required external methods",
        "seen_record_keys",
        "duplicate rollout record identity",
        "seen_video_paths",
        "duplicate video_path",
        "MIN_EPISODES_PER_METHOD",
        "external_statistical_confidence_v1",
        "bootstrap_mean_ci",
        "statistical_confidence",
        "confidence_gate",
        "record_counts_by_task_method",
        "episodes_per_method must be integer >=",
        "does not match episodes_per_method",
        "paired_panel_lines",
        "paired_panel_methods",
        "duplicate method record within paired reset",
        "missing declared methods",
        "manifest_task_configs",
        "config_hash does not match config_path",
        "skill_i must match manifest task config",
        "manifest_method_hashes",
        "policy_or_config_hash must match manifest checkpoint_or_config_hash",
        "staging",
        "backup",
        "ftyp",
    ):
        if term not in rollout_validator_text:
            fail(f"external rollout validator missing strict video evidence term: {term}")
    if "strict video fixture did not reject fake MP4" not in rollout_self_test_text:
        fail("external rollout validator self-test must reject fake text .mp4 fixtures")
    for forbidden_fixture in (
        "internal_runner_artifact.staging.mp4",
        "internal_runner_artifact.backup.mp4",
        "forbidden non-evidence fragment",
        "weak statistical confidence test did not fail",
        "external_success_margin_confidence_gate",
        "missing method-coverage test did not fail",
        "weak episode-count test did not fail",
        "short record-count test did not fail",
        "duplicate paired-method test did not fail",
        "missing paired-method test did not fail",
        "duplicate rollout identity test did not fail",
        "duplicate video path test did not fail",
        "stale task config hash test did not fail",
        "stale task config row test did not fail",
        "spoofed policy/config hash test did not fail",
    ):
        if forbidden_fixture not in rollout_self_test_text:
            fail(f"external rollout validator self-test missing staged/backup rejection fixture: {forbidden_fixture}")
    if "write_synthetic_mp4" not in evidence_pipeline_self_test_text or "strict_video_evidence=True" not in evidence_pipeline_self_test_text:
        fail("external evidence pipeline self-test must exercise strict MP4 video evidence validation")
    if "confidence-gated rollout statistics" not in evidence_pipeline_self_test_text:
        fail("external evidence pipeline self-test must exercise confidence-gated rollout statistics")
    for term in (
        "external_rollout_confidence_gates_passed",
        "CONFIDENCE_METRICS",
        "all_primary_confidence_gates_passed",
    ):
        if term not in audit_external_evidence_text:
            fail(f"final external evidence audit missing rollout confidence gate term: {term}")
    if "tampered rollout confidence summary did not fail" not in evidence_pipeline_self_test_text:
        fail("external evidence pipeline self-test must reject tampered rollout confidence summaries in the final evidence audit")
    if "tampered release artifact hash test did not fail" not in evidence_pipeline_self_test_text:
        fail("external evidence pipeline self-test must reject tampered release artifact hashes in the final evidence audit")

    evidence_pipeline_self_test_path = RESULTS / "external_evidence_pipeline_self_test.json"
    evidence_pipeline_self_test_md_path = RESULTS / "external_evidence_pipeline_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_evidence_pipeline.py",
        evidence_pipeline_self_test_path,
        evidence_pipeline_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external evidence pipeline self-test artifact: {path}")
    evidence_pipeline_self_test = json.loads(evidence_pipeline_self_test_path.read_text(encoding="utf-8"))
    if evidence_pipeline_self_test.get("version") != "external_evidence_pipeline_self_test_v1":
        fail("external evidence pipeline self-test version mismatch")
    if evidence_pipeline_self_test.get("passed") is not True:
        fail("external evidence pipeline self-test did not pass")
    if evidence_pipeline_self_test.get("not_external_evidence") is not True:
        fail("external evidence pipeline self-test must declare that it is not evidence")
    if evidence_pipeline_self_test.get("strict_external_evidence_ready") is not False:
        fail("external evidence pipeline self-test must keep strict external evidence false")
    if evidence_pipeline_self_test.get("synthetic_submission_ready") is not True:
        fail("external evidence pipeline self-test should make a temporary complete package submission-ready")
    if int(evidence_pipeline_self_test.get("synthetic_record_count", 0) or 0) < 1440:
        fail("external evidence pipeline self-test has too few synthetic rollout records")
    if int(evidence_pipeline_self_test.get("synthetic_task_count", 0) or 0) < 4:
        fail("external evidence pipeline self-test has too few synthetic task families")
    if int(evidence_pipeline_self_test.get("synthetic_method_count", 0) or 0) < 12:
        fail("external evidence pipeline self-test has too few synthetic methods")
    if evidence_pipeline_self_test.get("prepared_task_configs_bound") is not True:
        fail("external evidence pipeline self-test must bind prepared task configs")
    if evidence_pipeline_self_test.get("tracked_candidate_method_configs_bound") is not True:
        fail("external evidence pipeline self-test must bind tracked candidate method configs")
    if evidence_pipeline_self_test.get("synthetic_confidence_gates_passed") is not True:
        fail("external evidence pipeline self-test must pass synthetic confidence gates")
    if evidence_pipeline_self_test.get("tampered_rollout_confidence_rejected") is not True:
        fail("external evidence pipeline self-test must reject tampered rollout confidence summaries")
    if evidence_pipeline_self_test.get("tampered_release_hash_rejected") is not True:
        fail("external evidence pipeline self-test must reject tampered release hashes")
    if evidence_pipeline_self_test.get("real_manifest_untouched") is not True:
        fail("external evidence pipeline self-test must leave the real manifest untouched")
    if evidence_pipeline_self_test.get("real_reports_untouched") is not True:
        fail("external evidence pipeline self-test must leave real evidence reports untouched")
    evidence_pipeline_self_checks = {
        check.get("name"): check.get("passed") for check in evidence_pipeline_self_test.get("checks", [])
    }
    for required_check in (
        "synthetic_complete_package_reaches_final_external_ready",
        "synthetic_records_cover_tasks_methods_and_confidence",
        "prepared_task_configs_bound_in_full_pipeline_fixture",
        "tracked_candidate_method_configs_bound_in_full_pipeline_fixture",
        "synthetic_component_gates_pass",
        "tampered_rollout_confidence_summary_rejected",
        "tampered_release_artifact_hash_rejected",
        "real_repository_evidence_state_untouched",
    ):
        if evidence_pipeline_self_checks.get(required_check) is not True:
            fail(f"external evidence pipeline self-test missing passing check: {required_check}")

    execution_readiness_path = RESULTS / "external_execution_readiness_audit.json"
    if not execution_readiness_path.exists():
        fail("missing results/external_execution_readiness_audit.json; run scripts/audit_external_execution_readiness.py")
    execution_readiness = json.loads(execution_readiness_path.read_text(encoding="utf-8"))
    if execution_readiness.get("version") != "external_execution_readiness_audit_v1":
        fail("external execution readiness audit version mismatch")
    if execution_readiness.get("passed") is not True:
        fail("external execution readiness audit did not pass")
    if execution_readiness.get("not_external_evidence") is not True:
        fail("external execution readiness audit must declare that it is not evidence")
    if execution_readiness.get("execution_packet_ready") is not True:
        fail("external execution packet is not ready")
    if execution_readiness.get("strict_evidence_ready") is not False:
        fail("external execution readiness audit must not claim strict evidence is ready")
    if int(execution_readiness.get("total_required_records", 0)) < 1440:
        fail("external execution readiness audit has too few required records")
    if int(execution_readiness.get("operator_rows", 0)) < 1440:
        fail("external execution readiness audit has too few operator rows")
    readiness_checks = {entry.get("name"): entry.get("passed") for entry in execution_readiness.get("checks", [])}
    for required_check in (
        "collection_plan_ready",
        "fidelity_acceptance_contract_ready",
        "fidelity_acceptance_not_evidence",
        "fidelity_acceptance_fail_closed",
        "fidelity_acceptance_task_coverage",
        "external_fidelity_provenance_packet_ready",
        "external_fidelity_provenance_not_evidence",
        "external_fidelity_provenance_covers_acceptance_blocker",
        "external_fidelity_provenance_gate_order",
        "external_fidelity_provenance_self_test_ready",
        "external_fidelity_provenance_self_test_guards",
        "fidelity_acceptance_materializer_ready",
        "fidelity_acceptance_materializer_not_evidence",
        "fidelity_acceptance_materializer_guarded",
        "independent_validation_route_ready",
        "independent_route_not_evidence",
        "independent_route_primary_covers_tasks",
        "independent_route_closes_blockers",
        "external_platform_probe_ready",
        "external_platform_probe_not_evidence",
        "maniskill_task_binding_probe_ready",
        "maniskill_task_binding_probe_not_evidence",
        "maniskill_env_smoke_probe_ready",
        "maniskill_env_smoke_probe_not_evidence",
        "maniskill_fidelity_metadata_probe_ready",
        "maniskill_fidelity_metadata_probe_not_evidence",
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
        "external_runner_harness_ready",
        "external_runner_harness_not_evidence",
        "external_runner_harness_fail_closed",
        "external_runner_backend_probe_ready",
        "external_runner_backend_probe_not_evidence",
        "external_runner_backend_probe_exercises_actual_runner_path",
        "external_pilot_smoke_audit_ready",
        "external_pilot_smoke_not_evidence",
        "external_pilot_smoke_packet_ready",
        "external_pilot_smoke_quarantine_gate",
        "maniskill_pilot_runtime_liveness_ready",
        "maniskill_pilot_runtime_liveness_not_evidence",
        "maniskill_render_resource_sweep_ready",
        "maniskill_render_resource_sweep_not_evidence",
        "maniskill_render_machine_qualification_ready",
        "maniskill_render_machine_qualification_not_evidence",
        "maniskill_render_machine_operator_commands",
        "external_backend_contract_ready",
        "external_backend_contract_not_evidence",
        "external_backend_contract_fail_closed",
        "external_backend_integration_packet_ready",
        "external_backend_integration_not_evidence",
        "external_backend_integration_covers_backend_blocker",
        "external_backend_integration_gate_order",
        "external_backend_integration_self_test_ready",
        "external_backend_integration_self_test_guards",
        "external_collection_readiness_audit_ready",
        "external_collection_readiness_not_evidence",
        "external_collection_readiness_fail_closed",
        "external_collection_readiness_packet_shape",
        "external_collection_readiness_tracked_reference_route",
        "maniskill_reference_collection_preflight_ready",
        "maniskill_reference_collection_preflight_reaches_fidelity_gate",
        "external_pairing_integrity_audit_ready",
        "external_pairing_integrity_not_evidence",
        "external_release_package_audit_ready",
        "external_release_package_not_evidence",
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
        "external_acquisition_packet_ready",
        "external_acquisition_packet_not_evidence",
        "external_acquisition_packet_maps_all_blockers",
        "external_acquisition_packet_backend_gate",
        "external_operator_packet_ready",
        "external_operator_packet_not_evidence",
        "external_operator_packet_go_no_go",
        "external_operator_packet_backend_gate",
        "external_operator_handoff_bundle_ready",
        "external_operator_handoff_bundle_not_evidence",
        "external_operator_handoff_bundle_excludes_evidence_paths",
        "external_operator_handoff_bundle_hash_manifest",
        "external_analysis_plan_ready",
        "external_analysis_plan_not_evidence",
        "external_analysis_plan_threshold_lock",
        "external_analysis_plan_exclusion_policy",
        "config_templates_ready",
        "config_materialization_plan_ready",
        "config_materialization_plan_not_evidence",
        "config_materialization_covers_tasks",
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
        "baseline_contract_reports_missing_implementations",
        "adapter_contract_harness_ready",
        "strict_evidence_gates_remain_not_ready",
        "operator_packet_paths_exist",
        "no_real_manifest_written",
        "validation_path_independent_of_haonan",
        "platform_qualification_terms_present",
    ):
        if readiness_checks.get(required_check) is not True:
            fail(f"external execution readiness audit missing passing check: {required_check}")

    execution_self_test_path = RESULTS / "external_execution_readiness_self_test.json"
    execution_self_test_md_path = RESULTS / "external_execution_readiness_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_execution_readiness.py",
        execution_self_test_path,
        execution_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external execution readiness self-test artifact: {path}")
    execution_self_test = json.loads(execution_self_test_path.read_text(encoding="utf-8"))
    if execution_self_test.get("version") != "external_execution_readiness_self_test_v1":
        fail("external execution readiness self-test version mismatch")
    if execution_self_test.get("passed") is not True:
        fail("external execution readiness self-test did not pass")
    if execution_self_test.get("not_external_evidence") is not True:
        fail("external execution readiness self-test must declare that it is not evidence")
    if execution_self_test.get("strict_external_evidence_ready") is not False:
        fail("external execution readiness self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_execution_ready",
        "missing_operator_packet_rejected",
        "missing_required_packet_file_rejected",
        "premature_manifest_rejected",
        "strict_evidence_promotion_rejected",
        "haonan_dependence_drift_rejected",
        "real_outputs_untouched",
    ):
        if execution_self_test.get(field) is not True:
            fail(f"external execution readiness self-test field must be true: {field}")
    execution_self_checks = {check.get("name"): check.get("passed") for check in execution_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_execution_packet_ready_but_non_evidence",
        "missing_operator_packet_rejected",
        "missing_required_packet_file_rejected",
        "premature_manifest_rejected",
        "strict_evidence_promotion_rejected",
        "haonan_dependence_drift_rejected",
        "real_execution_outputs_untouched",
    ):
        if execution_self_checks.get(required_check) is not True:
            fail(f"external execution readiness self-test missing passing check: {required_check}")

    for path in (
        EXTERNAL / "platform_qualification_checklist.md",
        EXTERNAL / "fidelity_acceptance_template.json",
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
        EXTERNAL / "render_machine_qualification_packet.md",
        EXTERNAL / "runner" / "README.md",
        EXTERNAL / "runner" / "backend_contract.py",
        EXTERNAL / "runner" / "real_collection_runner.py",
        RESULTS / "external_backend_contract_audit.md",
        RESULTS / "external_pairing_integrity_audit.md",
        RESULTS / "external_release_package_audit.md",
        RESULTS / "external_collection_readiness_audit.md",
        RESULTS / "external_runner_backend_self_test.md",
        RESULTS / "external_acquisition_packet.md",
        RESULTS / "external_operator_packet.md",
        RESULTS / "external_operator_handoff_bundle.md",
        RESULTS / "maniskill_render_resource_sweep.md",
        EXTERNAL / "render_resource_sweep_work_orders.csv",
        RESULTS / "maniskill_render_machine_qualification.md",
        RESULTS / "external_analysis_plan_audit.md",
        RESULTS / "external_platform_onboarding_audit.md",
        RESULTS / "external_fidelity_provenance_audit.md",
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
        EXTERNAL / "evidence_intake_ledger.json",
        EXTERNAL / "evidence_intake_ledger.md",
        EXTERNAL / "evidence_intake_ledger.csv",
        EXTERNAL / "pilot_smoke_packet.json",
        EXTERNAL / "pilot_smoke_packet.md",
        EXTERNAL / "pilot_smoke_work_orders.csv",
        EXTERNAL / "precollection_freeze_receipt.json",
        EXTERNAL / "precollection_freeze_receipt.md",
        EXTERNAL / "precollection_freeze_receipt.csv",
        EXTERNAL / "postcollection_evidence_seal.json",
        EXTERNAL / "postcollection_evidence_seal.md",
        EXTERNAL / "postcollection_evidence_seal.csv",
        RESULTS / "external_postcollection_seal_consistency_audit.md",
        EXTERNAL / "method_implementation_packet.json",
        EXTERNAL / "method_implementation_packet.md",
        EXTERNAL / "method_implementation_work_orders.csv",
        EXTERNAL / "method_reference_provenance.csv",
        EXTERNAL / "method_manifest_cutover_checklist.csv",
        EXTERNAL / "method_manifest_cutover_checklist.md",
        EXTERNAL / "manifest_assembly_checklist.csv",
        EXTERNAL / "manifest_precollection_draft.json",
        EXTERNAL / "manifest_precollection_draft.md",
        RESULTS / "external_method_implementation_audit.md",
        RESULTS / "external_precollection_manifest_draft_audit.md",
        RESULTS / "external_precollection_manifest_draft_self_test.md",
        RESULTS / "external_precollection_freeze_receipt_audit.md",
        RESULTS / "external_postcollection_evidence_seal_audit.md",
        RESULTS / "external_config_manifest_audit.md",
        RESULTS / "external_rollout_evidence_audit.md",
        RESULTS / "external_ablation_collection_audit.md",
        RESULTS / "external_ablation_collection_packet_self_test.md",
        RESULTS / "external_evidence_intake_ledger_audit.md",
        RESULTS / "external_evidence_intake_ledger_self_test.md",
        RESULTS / "external_pilot_smoke_audit.md",
        RESULTS / "external_pilot_smoke_packet_audit.md",
        RESULTS / "external_config_materialization_plan.md",
        RESULTS / "external_execution_readiness_audit.md",
        RESULTS / "external_fidelity_acceptance_audit.md",
        RESULTS / "external_backend_integration_audit.md",
        RESULTS / "external_blind_eval_audit.md",
    ):
        if not path.exists():
            fail(f"missing external execution readiness artifact: {path}")

    acquisition_path = RESULTS / "external_acquisition_packet.json"
    if not acquisition_path.exists():
        fail("missing results/external_acquisition_packet.json; run scripts/build_external_acquisition_packet.py")
    acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
    if acquisition.get("version") != "external_acquisition_packet_v1":
        fail("external acquisition packet version mismatch")
    if acquisition.get("passed") is not True:
        fail("external acquisition packet did not pass")
    if acquisition.get("not_external_evidence") is not True:
        fail("external acquisition packet must declare that it is not evidence")
    if acquisition.get("strict_evidence_ready") is not False:
        fail("external acquisition packet must not claim strict evidence readiness")
    if len(acquisition.get("missing_requirements", []) or []) != 4:
        fail("external acquisition packet should map the four remaining blocking external requirements")
    if len(acquisition.get("operator_actions", []) or []) < 10:
        fail("external acquisition packet has too few operator actions")
    acquisition_self_test_path = RESULTS / "external_acquisition_packet_self_test.json"
    acquisition_self_test_md_path = RESULTS / "external_acquisition_packet_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_acquisition_packet.py",
        acquisition_self_test_path,
        acquisition_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external acquisition packet self-test artifact: {path}")
    acquisition_self_test = json.loads(acquisition_self_test_path.read_text(encoding="utf-8"))
    if acquisition_self_test.get("version") != "external_acquisition_packet_self_test_v1":
        fail("external acquisition packet self-test version mismatch")
    if acquisition_self_test.get("passed") is not True:
        fail("external acquisition packet self-test did not pass")
    if acquisition_self_test.get("not_external_evidence") is not True:
        fail("external acquisition packet self-test must declare that it is not evidence")
    if acquisition_self_test.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_ready",
        "missing_source_rejected",
        "unmapped_blocker_rejected",
        "premature_manifest_rejected",
        "collection_readiness_drift_rejected",
        "real_outputs_untouched",
    ):
        if acquisition_self_test.get(field) is not True:
            fail(f"external acquisition packet self-test field must be true: {field}")
    acquisition_self_checks = {check.get("name"): check.get("passed") for check in acquisition_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_builds_current_acquisition_packet",
        "missing_source_report_rejected",
        "unmapped_blocker_rejected",
        "premature_manifest_rejected",
        "collection_readiness_drift_rejected",
        "real_repository_acquisition_outputs_untouched",
    ):
        if acquisition_self_checks.get(required_check) is not True:
            fail(f"external acquisition packet self-test missing passing check: {required_check}")
    acquisition_render = acquisition.get("render_video_preflight", {}) or {}
    if acquisition_render.get("render_video_ready") is False:
        if not (acquisition_render.get("renderer_failure_classes", []) or []):
            fail("external acquisition packet must expose the render-video failure classifier")
        if len(acquisition_render.get("operator_remediation", []) or []) < 2:
            fail("external acquisition packet must expose render-video operator remediation")
        retest_commands = "\n".join(acquisition_render.get("renderer_profile_retest_commands", []) or [])
        for fragment in ("--render-backend cpu", "--render-backend gpu", "--render-backend sapien_cuda"):
            if fragment not in retest_commands:
                fail(f"external acquisition packet missing renderer retest command fragment: {fragment}")
    acquisition_resource = acquisition.get("render_resource_sweep", {}) or {}
    if acquisition_resource.get("not_external_evidence") is not True:
        fail("external acquisition packet render resource sweep must be marked non-evidence")
    if acquisition_resource.get("any_render_video_ready") is not False:
        fail("external acquisition packet render resource sweep must preserve current no-ready state")
    if acquisition_resource.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet render resource sweep must preserve strict evidence false")
    if acquisition_resource.get("descriptor_pool_failure_persists_at_minimum_resolution") is not True:
        fail("external acquisition packet render resource sweep must expose minimum-resolution descriptor-pool persistence")
    if int(acquisition_resource.get("record_count", 0) or 0) < 3:
        fail("external acquisition packet render resource sweep must expose all renderer profile attempts")
    if "vulkan_descriptor_pool_exhaustion" not in (acquisition_resource.get("renderer_failure_classes", []) or []):
        fail("external acquisition packet render resource sweep must expose descriptor-pool failure class")
    if "audit_maniskill_render_resource_sweep.py" not in str(acquisition_resource.get("audit_command", "")):
        fail("external acquisition packet render resource sweep must expose rebuild command")
    acquisition_checks = {entry.get("name"): entry.get("passed") for entry in acquisition.get("checks", [])}
    for required_check in (
        "all_missing_requirements_mapped",
        "collection_preflight_fail_closed",
        "config_intake_directory_tracked",
        "config_materializer_ready",
        "config_manifest_packet_ready",
        "rollout_evidence_packet_ready",
        "ablation_collection_packet_ready",
        "evidence_intake_ledger_ready",
        "precollection_freeze_receipt_ready",
        "postcollection_evidence_seal_ready",
        "postcollection_seal_consistency_gate_ready",
        "backend_contract_gate_ready",
        "backend_integration_packet_ready",
        "maniskill_reference_backend_audit_ready",
        "maniskill_reference_collection_preflight_ready",
        "pilot_smoke_packet_ready",
        "maniskill_render_video_preflight_recorded",
        "maniskill_render_resource_sweep_recorded",
        "method_implementation_packet_ready",
        "preflight_operator_actions_present",
        "route_independent_of_haonan",
        "platform_probe_ready",
        "task_binding_probe_ready",
        "env_smoke_probe_ready",
        "fidelity_metadata_probe_ready",
        "platform_onboarding_ready",
        "fidelity_provenance_packet_ready",
        "fidelity_acceptance_draft_ready",
        "fidelity_acceptance_materializer_ready",
        "post_collection_strict_commands_cover_all_gates",
        "no_real_manifest_written",
        "operator_actions_cover_collection_blockers",
        "backend_action_runs_contract_before_readiness",
    ):
        if acquisition_checks.get(required_check) is not True:
            fail(f"external acquisition packet missing passing check: {required_check}")
    acquisition_intake = acquisition.get("evidence_intake_ledger", {}) or {}
    if acquisition_intake.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet evidence intake summary must keep strict evidence false")
    if acquisition_intake.get("blocking_failure_count") != acquisition_intake.get("mapped_failure_count"):
        fail("external acquisition packet evidence intake summary must map every strict evidence failure")
    if int(acquisition_intake.get("blocking_failure_count", 0) or 0) < 30:
        fail("external acquisition packet evidence intake summary maps too few strict evidence failures")
    if acquisition_intake.get("unmapped_failures"):
        fail(f"external acquisition packet evidence intake summary has unmapped failures: {acquisition_intake.get('unmapped_failures')}")
    if "external_validation/evidence_intake_ledger.md" not in str(acquisition_intake.get("operator_packet_path", "")):
        fail("external acquisition packet evidence intake summary must point to the intake ledger")
    acquisition_freeze = acquisition.get("precollection_freeze_receipt", {}) or {}
    if acquisition_freeze.get("not_external_evidence") is not True:
        fail("external acquisition packet freeze receipt summary must be marked non-evidence")
    if acquisition_freeze.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet freeze receipt summary must keep strict evidence false")
    if acquisition_freeze.get("freeze_receipt_ready") is not False:
        fail("external acquisition packet freeze receipt summary must keep freeze readiness false before real operator lock")
    if int(acquisition_freeze.get("locked_artifact_count", 0) or 0) < 42:
        fail("external acquisition packet freeze receipt summary locks too few artifacts")
    if int(acquisition_freeze.get("candidate_method_config_count", 0) or 0) < 11:
        fail("external acquisition packet freeze receipt summary must expose candidate method config hash locks")
    if acquisition_freeze.get("method_config_hash_lock_ready") is not True:
        fail("external acquisition packet freeze receipt summary must report method config hash lock ready")
    if "external_validation/precollection_freeze_receipt.md" not in str(acquisition_freeze.get("operator_packet_path", "")):
        fail("external acquisition packet freeze receipt summary must point to the receipt markdown")
    if "build_external_precollection_freeze_receipt.py" not in str(acquisition_freeze.get("audit_command", "")):
        fail("external acquisition packet freeze receipt summary must include rebuild command")
    acquisition_seal = acquisition.get("postcollection_evidence_seal", {}) or {}
    if acquisition_seal.get("not_external_evidence") is not True:
        fail("external acquisition packet postcollection seal summary must be marked non-evidence")
    if acquisition_seal.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet postcollection seal summary must keep strict evidence false")
    if acquisition_seal.get("postcollection_seal_ready") is not False:
        fail("external acquisition packet postcollection seal summary must keep seal readiness false before real logs/videos")
    if acquisition_seal.get("ready_for_manifest_promotion") is not False:
        fail("external acquisition packet postcollection seal summary must keep manifest promotion false before real logs/videos")
    if int(acquisition_seal.get("sealed_artifact_count", 0) or 0) < 8:
        fail("external acquisition packet postcollection seal summary hashes too few artifacts")
    if int(acquisition_seal.get("jsonl_record_count", 0) or 0) != 0 or int(acquisition_seal.get("rollout_video_count", 0) or 0) != 0:
        fail("external acquisition packet postcollection seal summary must remain fail-closed by default")
    if "external_validation/postcollection_evidence_seal.md" not in str(acquisition_seal.get("operator_packet_path", "")):
        fail("external acquisition packet postcollection seal summary must point to the seal markdown")
    if "build_external_postcollection_evidence_seal.py" not in str(acquisition_seal.get("audit_command", "")):
        fail("external acquisition packet postcollection seal summary must include rebuild command")
    acquisition_consistency = acquisition.get("postcollection_seal_consistency_gate", {}) or {}
    if acquisition_consistency.get("not_external_evidence") is not True:
        fail("external acquisition packet postcollection consistency summary must be marked non-evidence")
    if acquisition_consistency.get("strict_external_evidence_ready") is not False:
        fail("external acquisition packet postcollection consistency summary must keep strict evidence false")
    if acquisition_consistency.get("seal_consistency_ready") is not False:
        fail("external acquisition packet postcollection consistency summary must keep consistency readiness false before real logs/videos")
    if acquisition_consistency.get("ready_for_manifest_promotion") is not False:
        fail("external acquisition packet postcollection consistency summary must keep manifest promotion false before real logs/videos")
    if int(acquisition_consistency.get("matched_hash_count", 0) or 0) < 8:
        fail("external acquisition packet postcollection consistency summary recomputes too few hashes")
    if int(acquisition_consistency.get("current_jsonl_record_count", 0) or 0) != 0 or int(acquisition_consistency.get("current_rollout_video_count", 0) or 0) != 0:
        fail("external acquisition packet postcollection consistency summary must remain fail-closed by default")
    if acquisition_consistency.get("mismatched_hashes") or acquisition_consistency.get("extra_official_artifacts"):
        fail("external acquisition packet postcollection consistency summary must not report drift by default")
    if "audit_external_postcollection_seal_consistency.py" not in str(acquisition_consistency.get("audit_command", "")):
        fail("external acquisition packet postcollection consistency summary must include audit command")

    operator_packet_path = RESULTS / "external_operator_packet.json"
    if not operator_packet_path.exists():
        fail("missing results/external_operator_packet.json; run scripts/build_external_operator_packet.py")
    operator_packet = json.loads(operator_packet_path.read_text(encoding="utf-8"))
    if operator_packet.get("version") != "external_operator_packet_v1":
        fail("external operator packet version mismatch")
    if operator_packet.get("passed") is not True:
        fail("external operator packet did not pass")
    if operator_packet.get("not_external_evidence") is not True:
        fail("external operator packet must declare that it is not evidence")
    if operator_packet.get("operator_packet_ready") is not True:
        fail("external operator packet must report operator_packet_ready=true")
    if operator_packet.get("strict_evidence_ready") is not False:
        fail("external operator packet must not claim strict evidence readiness")
    if operator_packet.get("go_to_collect") is not False or operator_packet.get("start_state") != "DO_NOT_COLLECT_YET":
        fail("external operator packet must remain a no-go until strict collection preflight passes")
    if int(operator_packet.get("blocking_missing_count", 0) or 0) < 4:
        fail("external operator packet should expose the current pre-collection blockers")
    reference_route = operator_packet.get("tracked_maniskill_reference_route", {}) or {}
    reference_blockers = reference_route.get("blocking_missing", []) or []
    if reference_route.get("not_external_evidence") is not True:
        fail("external operator packet tracked ManiSkill reference route must be marked non-evidence")
    if "maniskill_reference_backend.py" not in str(reference_route.get("backend_module", "")):
        fail("external operator packet tracked ManiSkill route must name the reference backend")
    if reference_route.get("run_id") != "maniskill_sapien_reference_preflight_protocol_v1":
        fail("external operator packet tracked ManiSkill route must use the explicit reference preflight run id")
    if reference_route.get("reference_backend_contract_ready") is not True:
        fail("external operator packet tracked ManiSkill route must expose reference backend contract readiness")
    if reference_route.get("collection_ready") is not False:
        fail("external operator packet tracked ManiSkill route must preserve collection_ready=false until fidelity acceptance")
    if int(reference_route.get("blocking_missing_count", 99) or 99) != 1 or len(reference_blockers) != 1 or "fidelity_acceptance_ready" not in reference_blockers[0]:
        fail("external operator packet tracked ManiSkill route must show fidelity acceptance as the single remaining pre-collection blocker")
    if "audit_external_collection_readiness.py --strict" not in str(reference_route.get("pre_collection_gate_command", "")) or "--unsealed-alias-map" not in str(reference_route.get("pre_collection_gate_command", "")):
        fail("external operator packet tracked ManiSkill route must include the strict pre-collection gate command")
    if "real_collection_runner.py" not in str(reference_route.get("collection_command_after_fidelity_acceptance", "")) or "maniskill_reference_backend.py" not in str(reference_route.get("collection_command_after_fidelity_acceptance", "")):
        fail("external operator packet tracked ManiSkill route must include the reference collection command")
    operator_draft = operator_packet.get("fidelity_acceptance_draft", {}) or {}
    if operator_draft.get("not_external_evidence") is not True:
        fail("external operator packet fidelity draft must be marked non-evidence")
    if operator_draft.get("draft_ready") is not True:
        fail("external operator packet fidelity draft must report draft_ready=true")
    if operator_draft.get("acceptance_ready") is not False or operator_draft.get("strict_fidelity_evidence_ready") is not False:
        fail("external operator packet fidelity draft must preserve acceptance_ready=false")
    if operator_draft.get("draft_path") != "external_validation/fidelity_acceptance_draft.json":
        fail("external operator packet fidelity draft must point to the draft JSON")
    if int(operator_draft.get("remaining_operator_input_count", 0) or 0) < 8:
        fail("external operator packet fidelity draft must expose remaining operator input count")
    if not isinstance(operator_draft.get("machine_prefilled_ready"), bool) or operator_draft.get("operator_signoff_ready") is not False:
        fail("external operator packet fidelity draft must report machine-prefilled readiness and keep operator signoff false")
    if int(operator_draft.get("operator_signoff_item_count", 0) or 0) < 8:
        fail("external operator packet fidelity draft must expose operator signoff item count")
    if "build_external_fidelity_acceptance_draft.py" not in str(operator_draft.get("build_command", "")):
        fail("external operator packet fidelity draft must include rebuild command")
    operator_materializer = operator_packet.get("fidelity_acceptance_materializer", {}) or {}
    if operator_materializer.get("not_external_evidence") is not True:
        fail("external operator packet fidelity acceptance materializer must be marked non-evidence")
    if operator_materializer.get("write_enabled") is not False:
        fail("external operator packet fidelity acceptance materializer must keep write_enabled=false")
    if operator_materializer.get("acceptance_write_ready") is not False:
        fail("external operator packet fidelity acceptance materializer must not be write-ready without operator inputs")
    if operator_materializer.get("strict_fidelity_evidence_ready") is not False:
        fail("external operator packet fidelity acceptance materializer must preserve strict fidelity evidence false")
    operator_materializer_checkout = operator_materializer.get("current_checkout", {}) or {}
    if len(str(operator_materializer_checkout.get("code_commit", ""))) != 40:
        fail("external operator packet fidelity materializer must expose the current checkout commit")
    if len(str(operator_materializer_checkout.get("skill_library_hash", ""))) != 64:
        fail("external operator packet fidelity materializer must expose the current skill-library hash")
    if not isinstance(operator_materializer_checkout.get("clean_checkout"), bool):
        fail("external operator packet fidelity materializer must expose clean checkout status")
    materializer_command = str(operator_materializer.get("operator_write_command", ""))
    for fragment in (
        "materialize_fidelity_acceptance.py",
        "--confirm-real-platform",
        "--confirm-independent-operator",
        "--confirm-render-backed-videos",
        "--write",
    ):
        if fragment not in materializer_command:
            fail(f"external operator packet fidelity materializer command missing fragment: {fragment}")
    for forbidden_fragment in ("--confirm-real-rollout-evidence", "--confirm-manifest-declaration"):
        if forbidden_fragment in materializer_command:
            fail(f"external operator packet fidelity materializer command must defer postcollection flag: {forbidden_fragment}")
    if operator_materializer.get("plan_path") != "results/fidelity_acceptance_materialization_plan.json":
        fail("external operator packet fidelity materializer must point to the materialization plan JSON")
    operator_render = operator_packet.get("render_video_preflight", {}) or {}
    if operator_render.get("not_external_evidence") is not True:
        fail("external operator packet render-video preflight must be marked non-evidence")
    if not isinstance(operator_render.get("render_video_ready"), bool):
        fail("external operator packet render-video preflight must report render_video_ready")
    if operator_render.get("strict_external_evidence_ready") is not False:
        fail("external operator packet render-video preflight must preserve strict evidence false")
    if int(operator_render.get("env_count", 0) or 0) < 1:
        fail("external operator packet render-video preflight must expose probed environment count")
    if operator_render.get("render_video_ready") is False:
        if not (operator_render.get("renderer_failure_classes", []) or []):
            fail("external operator packet must expose the render-video failure classifier")
        if len(operator_render.get("operator_remediation", []) or []) < 2:
            fail("external operator packet must expose render-video operator remediation")
    if "maniskill_render_video_preflight_audit.json" not in str(operator_render.get("audit_path", "")):
        fail("external operator packet render-video preflight must point to the audit JSON")
    if "audit_maniskill_render_video_preflight.py" not in str(operator_render.get("build_command", "")):
        fail("external operator packet render-video preflight must include rebuild command")
    operator_resource = operator_packet.get("render_resource_sweep", {}) or {}
    if operator_resource.get("not_external_evidence") is not True:
        fail("external operator packet render resource sweep must be marked non-evidence")
    if operator_resource.get("any_render_video_ready") is not False:
        fail("external operator packet render resource sweep must preserve current no-ready state")
    if operator_resource.get("strict_external_evidence_ready") is not False:
        fail("external operator packet render resource sweep must preserve strict evidence false")
    if operator_resource.get("descriptor_pool_failure_persists_at_minimum_resolution") is not True:
        fail("external operator packet render resource sweep must expose minimum-resolution descriptor-pool persistence")
    if int(operator_resource.get("record_count", 0) or 0) < 3:
        fail("external operator packet render resource sweep must expose all renderer profile attempts")
    if "vulkan_descriptor_pool_exhaustion" not in (operator_resource.get("renderer_failure_classes", []) or []):
        fail("external operator packet render resource sweep must expose descriptor-pool failure class")
    if "maniskill_render_resource_sweep.json" not in str(operator_resource.get("audit_path", "")):
        fail("external operator packet render resource sweep must point to the audit JSON")
    if "audit_maniskill_render_resource_sweep.py" not in str(operator_resource.get("build_command", "")):
        fail("external operator packet render resource sweep must include rebuild command")
    operator_actions = operator_packet.get("operator_actions", []) or []
    if len(operator_actions) < 10:
        fail("external operator packet has too few operator actions")
    platform_probe_actions = [action for action in operator_actions if action.get("id") == "platform_probe"]
    if not platform_probe_actions:
        fail("external operator packet missing platform_probe action")
    platform_probe_commands = "\n".join(platform_probe_actions[0].get("commands", []) or [])
    if "probe_external_platform.py" not in platform_probe_commands or "probe_external_platform.py --strict" not in platform_probe_commands:
        fail("external operator packet platform probe action must include non-strict and strict probe commands")
    task_binding_actions = [action for action in operator_actions if action.get("id") == "task_binding_probe"]
    if not task_binding_actions:
        fail("external operator packet missing task_binding_probe action")
    task_binding_commands = "\n".join(task_binding_actions[0].get("commands", []) or [])
    if "probe_maniskill_task_bindings.py" not in task_binding_commands or "probe_maniskill_task_bindings.py --strict" not in task_binding_commands:
        fail("external operator packet task binding action must include non-strict and strict probe commands")
    env_smoke_actions = [action for action in operator_actions if action.get("id") == "env_smoke_probe"]
    if not env_smoke_actions:
        fail("external operator packet missing env_smoke_probe action")
    env_smoke_commands = "\n".join(env_smoke_actions[0].get("commands", []) or [])
    if "probe_maniskill_env_smoke.py" not in env_smoke_commands or "probe_maniskill_env_smoke.py --strict" not in env_smoke_commands:
        fail("external operator packet env smoke action must include non-strict and strict probe commands")
    metadata_probe = operator_packet.get("fidelity_metadata_probe", {}) or {}
    if metadata_probe.get("not_external_evidence") is not True:
        fail("external operator packet fidelity metadata probe must be marked non-evidence")
    if metadata_probe.get("metadata_probe_ready") is not True:
        fail("external operator packet fidelity metadata probe must report metadata_probe_ready=true")
    if metadata_probe.get("accepted_fidelity_ready") is not False:
        fail("external operator packet fidelity metadata probe must leave accepted_fidelity_ready=false")
    if metadata_probe.get("probe_path") != "results/maniskill_fidelity_metadata_probe.json":
        fail("external operator packet fidelity metadata probe must point to the probe JSON")
    if "probe_maniskill_fidelity_metadata.py" not in str(metadata_probe.get("build_command", "")):
        fail("external operator packet fidelity metadata probe must include rebuild command")
    metadata_actions = [action for action in operator_actions if action.get("id") == "fidelity_metadata_probe"]
    if not metadata_actions:
        fail("external operator packet missing fidelity_metadata_probe action")
    metadata_commands = "\n".join(metadata_actions[0].get("commands", []) or [])
    if "probe_maniskill_fidelity_metadata.py" not in metadata_commands or "probe_maniskill_fidelity_metadata.py --strict" not in metadata_commands:
        fail("external operator packet fidelity metadata action must include non-strict and strict probe commands")
    render_preflight_actions = [action for action in operator_actions if action.get("id") == "maniskill_render_video_preflight"]
    if not render_preflight_actions:
        fail("external operator packet missing maniskill_render_video_preflight action")
    render_preflight_commands = "\n".join(render_preflight_actions[0].get("commands", []) or [])
    if "audit_maniskill_render_video_preflight.py" not in render_preflight_commands:
        fail("external operator packet render preflight action must expose render-video preflight command")
    render_resource_actions = [action for action in operator_actions if action.get("id") == "maniskill_render_resource_sweep"]
    if not render_resource_actions:
        fail("external operator packet missing maniskill_render_resource_sweep action")
    render_resource_commands = "\n".join(render_resource_actions[0].get("commands", []) or [])
    if "audit_maniskill_render_resource_sweep.py" not in render_resource_commands:
        fail("external operator packet resource-sweep action must expose render resource sweep command")
    backend_integration_actions = [action for action in operator_actions if action.get("id") == "backend_integration_packet"]
    if not backend_integration_actions:
        fail("external operator packet missing backend_integration_packet action")
    if "build_external_backend_integration_packet.py" not in "\n".join(backend_integration_actions[0].get("commands", []) or []):
        fail("external operator packet backend integration action must rebuild the backend integration packet")
    reference_backend_actions = [action for action in operator_actions if action.get("id") == "maniskill_reference_backend_audit"]
    if not reference_backend_actions:
        fail("external operator packet missing maniskill_reference_backend_audit action")
    if "audit_maniskill_backend_readiness.py" not in "\n".join(reference_backend_actions[0].get("commands", []) or []):
        fail("external operator packet reference backend action must run the readiness audit")
    reference_preflight_actions = [action for action in operator_actions if action.get("id") == "maniskill_reference_collection_preflight"]
    if not reference_preflight_actions:
        fail("external operator packet missing maniskill_reference_collection_preflight action")
    if "audit_maniskill_reference_collection_preflight.py" not in "\n".join(reference_preflight_actions[0].get("commands", []) or []):
        fail("external operator packet reference preflight action must run the collection preflight audit")
    config_manifest_actions = [action for action in operator_actions if action.get("id") == "config_manifest_packet"]
    if not config_manifest_actions:
        fail("external operator packet missing config_manifest_packet action")
    if "build_external_config_manifest_packet.py" not in "\n".join(config_manifest_actions[0].get("commands", []) or []):
        fail("external operator packet config manifest action must rebuild the config manifest packet")
    rollout_evidence_actions = [action for action in operator_actions if action.get("id") == "rollout_evidence_packet"]
    if not rollout_evidence_actions:
        fail("external operator packet missing rollout_evidence_packet action")
    if "build_external_rollout_evidence_packet.py" not in "\n".join(rollout_evidence_actions[0].get("commands", []) or []):
        fail("external operator packet rollout evidence action must rebuild the rollout evidence packet")
    fidelity_provenance_actions = [action for action in operator_actions if action.get("id") == "fidelity_provenance_packet"]
    if not fidelity_provenance_actions:
        fail("external operator packet missing fidelity_provenance_packet action")
    if "build_external_fidelity_provenance_packet.py" not in "\n".join(fidelity_provenance_actions[0].get("commands", []) or []):
        fail("external operator packet fidelity provenance action must rebuild the fidelity provenance packet")
    fidelity_draft_actions = [action for action in operator_actions if action.get("id") == "fidelity_acceptance_draft"]
    if not fidelity_draft_actions:
        fail("external operator packet missing fidelity_acceptance_draft action")
    if "build_external_fidelity_acceptance_draft.py" not in "\n".join(fidelity_draft_actions[0].get("commands", []) or []):
        fail("external operator packet fidelity draft action must rebuild the fidelity acceptance draft")
    fidelity_materializer_actions = [action for action in operator_actions if action.get("id") == "fidelity_acceptance_materializer"]
    if not fidelity_materializer_actions:
        fail("external operator packet missing fidelity_acceptance_materializer action")
    materializer_action_commands = "\n".join(fidelity_materializer_actions[0].get("commands", []) or [])
    if "materialize_fidelity_acceptance.py" not in materializer_action_commands or "--confirm-real-platform" not in materializer_action_commands:
        fail("external operator packet fidelity materializer action must expose the guarded materialization command")
    method_actions = [action for action in operator_actions if action.get("id") == "method_implementation_packet"]
    if not method_actions:
        fail("external operator packet missing method_implementation_packet action")
    if "build_external_method_implementation_packet.py" not in "\n".join(method_actions[0].get("commands", []) or []):
        fail("external operator packet method action must rebuild the method implementation packet")
    pilot_actions = [action for action in operator_actions if action.get("id") == "pilot_smoke_packet"]
    if not pilot_actions:
        fail("external operator packet missing pilot_smoke_packet action")
    pilot_commands = "\n".join(pilot_actions[0].get("commands", []) or [])
    if "build_external_pilot_smoke_packet.py" not in pilot_commands or "audit_external_pilot_smoke.py" not in pilot_commands:
        fail("external operator packet pilot smoke action must rebuild and audit the pilot smoke packet")
    pilot_runtime_actions = [action for action in operator_actions if action.get("id") == "maniskill_pilot_runtime_liveness"]
    if not pilot_runtime_actions:
        fail("external operator packet missing maniskill_pilot_runtime_liveness action")
    pilot_runtime_commands = "\n".join(pilot_runtime_actions[0].get("commands", []) or [])
    if "audit_maniskill_pilot_runtime_liveness.py" not in pilot_runtime_commands:
        fail("external operator packet liveness action must run the ManiSkill pilot runtime liveness audit")
    render_machine_actions = [action for action in operator_actions if action.get("id") == "maniskill_render_machine_qualification"]
    if not render_machine_actions:
        fail("external operator packet missing maniskill_render_machine_qualification action")
    render_machine_action_commands = "\n".join(render_machine_actions[0].get("commands", []) or [])
    if "build_maniskill_render_machine_qualification.py" not in render_machine_action_commands:
        fail("external operator packet render-machine action must build the render machine qualification packet")
    operator_ablation = operator_packet.get("ablation_collection", {}) or {}
    if operator_ablation.get("manifest_ablation_evidence_ready") is not False:
        fail("external operator packet ablation summary must keep manifest ablation evidence false")
    if operator_ablation.get("strict_external_evidence_ready") is not False:
        fail("external operator packet ablation summary must keep strict evidence false")
    if int(operator_ablation.get("work_order_count", 0) or 0) != 5:
        fail("external operator packet ablation summary must expose five work orders")
    if int(operator_ablation.get("expected_ablation_records", 0) or 0) < 600:
        fail("external operator packet ablation summary has too few expected records")
    if "external_validation/ablation_collection_packet.md" not in str(operator_ablation.get("packet_path", "")):
        fail("external operator packet ablation summary must point to the ablation packet")
    ablation_actions = [action for action in operator_actions if action.get("id") == "ablation_collection_packet"]
    if not ablation_actions:
        fail("external operator packet missing ablation_collection_packet action")
    ablation_action_commands = "\n".join(ablation_actions[0].get("commands", []) or [])
    if "build_external_ablation_collection_packet.py" not in ablation_action_commands:
        fail("external operator packet ablation action must rebuild the ablation collection packet")
    operator_intake = operator_packet.get("evidence_intake_ledger", {}) or {}
    if operator_intake.get("strict_external_evidence_ready") is not False:
        fail("external operator packet evidence intake summary must keep strict evidence false")
    if operator_intake.get("blocking_failure_count") != operator_intake.get("mapped_failure_count"):
        fail("external operator packet evidence intake summary must map every strict evidence failure")
    if int(operator_intake.get("blocking_failure_count", 0) or 0) < 30:
        fail("external operator packet evidence intake summary maps too few strict evidence failures")
    if operator_intake.get("unmapped_failures"):
        fail(f"external operator packet evidence intake summary has unmapped failures: {operator_intake.get('unmapped_failures')}")
    if "external_validation/evidence_intake_ledger.md" not in str(operator_intake.get("packet_path", "")):
        fail("external operator packet evidence intake summary must point to the intake ledger")
    intake_actions = [action for action in operator_actions if action.get("id") == "evidence_intake_ledger"]
    if not intake_actions:
        fail("external operator packet missing evidence_intake_ledger action")
    intake_action_commands = "\n".join(intake_actions[0].get("commands", []) or [])
    if "build_external_evidence_intake_ledger.py" not in intake_action_commands:
        fail("external operator packet evidence intake action must rebuild the intake ledger")
    operator_freeze = operator_packet.get("precollection_freeze_receipt", {}) or {}
    if operator_freeze.get("not_external_evidence") is not True:
        fail("external operator packet freeze receipt summary must be marked non-evidence")
    if operator_freeze.get("strict_external_evidence_ready") is not False:
        fail("external operator packet freeze receipt summary must keep strict evidence false")
    if operator_freeze.get("freeze_receipt_ready") is not False:
        fail("external operator packet freeze receipt summary must keep freeze readiness false before real operator lock")
    if int(operator_freeze.get("locked_artifact_count", 0) or 0) < 42:
        fail("external operator packet freeze receipt summary locks too few artifacts")
    if int(operator_freeze.get("candidate_method_config_count", 0) or 0) < 11:
        fail("external operator packet freeze receipt summary must expose candidate method config hash locks")
    if operator_freeze.get("method_config_hash_lock_ready") is not True:
        fail("external operator packet freeze receipt summary must report method config hash lock ready")
    if "external_validation/precollection_freeze_receipt.md" not in str(operator_freeze.get("packet_path", "")):
        fail("external operator packet freeze receipt summary must point to the receipt markdown")
    if "build_external_precollection_freeze_receipt.py" not in str(operator_freeze.get("build_command", "")):
        fail("external operator packet freeze receipt summary must include rebuild command")
    freeze_actions = [action for action in operator_actions if action.get("id") == "precollection_freeze_receipt"]
    if not freeze_actions:
        fail("external operator packet missing precollection_freeze_receipt action")
    freeze_action_commands = "\n".join(freeze_actions[0].get("commands", []) or [])
    if "build_external_precollection_freeze_receipt.py" not in freeze_action_commands:
        fail("external operator packet freeze receipt action must rebuild the freeze receipt")
    operator_seal = operator_packet.get("postcollection_evidence_seal", {}) or {}
    if operator_seal.get("not_external_evidence") is not True:
        fail("external operator packet postcollection seal summary must be marked non-evidence")
    if operator_seal.get("strict_external_evidence_ready") is not False:
        fail("external operator packet postcollection seal summary must keep strict evidence false")
    if operator_seal.get("postcollection_seal_ready") is not False:
        fail("external operator packet postcollection seal summary must keep seal readiness false before real logs/videos")
    if operator_seal.get("ready_for_manifest_promotion") is not False:
        fail("external operator packet postcollection seal summary must keep manifest promotion false before real logs/videos")
    if int(operator_seal.get("sealed_artifact_count", 0) or 0) < 8:
        fail("external operator packet postcollection seal summary hashes too few artifacts")
    if int(operator_seal.get("jsonl_record_count", 0) or 0) != 0 or int(operator_seal.get("rollout_video_count", 0) or 0) != 0:
        fail("external operator packet postcollection seal summary must remain fail-closed by default")
    if "external_validation/postcollection_evidence_seal.md" not in str(operator_seal.get("packet_path", "")):
        fail("external operator packet postcollection seal summary must point to the seal markdown")
    if "build_external_postcollection_evidence_seal.py" not in str(operator_seal.get("build_command", "")):
        fail("external operator packet postcollection seal summary must include rebuild command")
    seal_actions = [action for action in operator_actions if action.get("id") == "postcollection_evidence_seal"]
    if not seal_actions:
        fail("external operator packet missing postcollection_evidence_seal action")
    seal_action_commands = "\n".join(seal_actions[0].get("commands", []) or [])
    if "build_external_postcollection_evidence_seal.py" not in seal_action_commands:
        fail("external operator packet postcollection seal action must rebuild the seal")
    operator_consistency = operator_packet.get("postcollection_seal_consistency_gate", {}) or {}
    if operator_consistency.get("not_external_evidence") is not True:
        fail("external operator packet postcollection consistency summary must be marked non-evidence")
    if operator_consistency.get("strict_external_evidence_ready") is not False:
        fail("external operator packet postcollection consistency summary must keep strict evidence false")
    if operator_consistency.get("seal_consistency_ready") is not False:
        fail("external operator packet postcollection consistency summary must keep consistency readiness false before real logs/videos")
    if operator_consistency.get("ready_for_manifest_promotion") is not False:
        fail("external operator packet postcollection consistency summary must keep manifest promotion false before real logs/videos")
    if int(operator_consistency.get("matched_hash_count", 0) or 0) < 8:
        fail("external operator packet postcollection consistency summary recomputes too few hashes")
    if int(operator_consistency.get("current_jsonl_record_count", 0) or 0) != 0 or int(operator_consistency.get("current_rollout_video_count", 0) or 0) != 0:
        fail("external operator packet postcollection consistency summary must remain fail-closed by default")
    if operator_consistency.get("mismatched_hashes") or operator_consistency.get("extra_official_artifacts"):
        fail("external operator packet postcollection consistency summary must not report drift by default")
    if "audit_external_postcollection_seal_consistency.py" not in str(operator_consistency.get("audit_command", "")):
        fail("external operator packet postcollection consistency summary must include audit command")
    consistency_actions = [action for action in operator_actions if action.get("id") == "postcollection_seal_consistency_gate"]
    if not consistency_actions:
        fail("external operator packet missing postcollection_seal_consistency_gate action")
    consistency_action_commands = "\n".join(consistency_actions[0].get("commands", []) or [])
    if "audit_external_postcollection_seal_consistency.py" not in consistency_action_commands:
        fail("external operator packet postcollection consistency action must run the consistency gate")
    operator_precollection = operator_packet.get("precollection_manifest_draft", {}) or {}
    if operator_precollection.get("not_external_evidence") is not True:
        fail("external operator packet precollection manifest draft summary must be marked non-evidence")
    if operator_precollection.get("draft_ready") is not True:
        fail("external operator packet precollection manifest draft summary must report draft_ready=true")
    if operator_precollection.get("strict_external_evidence_ready") is not False:
        fail("external operator packet precollection manifest draft summary must keep strict external evidence false")
    if operator_precollection.get("strict_config_evidence_ready") is not False:
        fail("external operator packet precollection manifest draft summary must keep strict config evidence false")
    if operator_precollection.get("official_manifest_exists") is not False:
        fail("external operator packet precollection manifest draft summary must keep official manifest absent")
    if int(operator_precollection.get("prepared_config_count", 0) or 0) < 4:
        fail("external operator packet precollection manifest draft summary must expose prepared config hashes")
    if int(operator_precollection.get("method_gap_count", 0) or 0) < 11:
        fail("external operator packet precollection manifest draft summary must expose method gaps")
    if int(operator_precollection.get("missing_rollout_artifact_count", 0) or 0) < 8:
        fail("external operator packet precollection manifest draft summary must expose rollout gaps")
    if "external_validation/manifest_precollection_draft.json" not in str(operator_precollection.get("draft_path", "")):
        fail("external operator packet precollection manifest draft summary must point to the draft JSON")
    if "build_external_precollection_manifest_draft.py" not in str(operator_precollection.get("build_command", "")):
        fail("external operator packet precollection manifest draft summary must include rebuild command")
    precollection_cutover = "\n".join(operator_precollection.get("cutover_commands", []) or [])
    if (
        "build_external_precollection_freeze_receipt.py" not in precollection_cutover
        or "build_external_postcollection_evidence_seal.py" not in precollection_cutover
        or "audit_external_postcollection_seal_consistency.py" not in precollection_cutover
        or "build_external_manifest.py --write --check-video-paths" not in precollection_cutover
        or "audit_external_evidence.py --strict" not in precollection_cutover
    ):
        fail("external operator packet precollection manifest draft summary must include final manifest/evidence cutover commands")
    if "build_external_precollection_freeze_receipt.py" not in operator_packet.get("precollection_freeze_command", ""):
        fail("external operator packet missing precollection freeze command")
    if "audit_external_collection_readiness.py --strict" not in operator_packet.get("pre_collection_gate_command", ""):
        fail("external operator packet missing strict pre-collection gate command")
    if "audit_external_backend_contract.py --strict" not in operator_packet.get("backend_contract_gate_command", ""):
        fail("external operator packet missing strict backend contract gate command")
    backend_actions = [action for action in operator_actions if action.get("id") == "backend_module"]
    if not backend_actions:
        fail("external operator packet missing backend_module action")
    backend_commands = "\n".join(backend_actions[0].get("commands", []) or [])
    if "audit_external_backend_contract.py --strict" not in backend_commands or "audit_external_collection_readiness.py" not in backend_commands:
        fail("external operator packet backend action must run backend contract before collection readiness")
    if "real_collection_runner.py" not in operator_packet.get("strict_collection_command", ""):
        fail("external operator packet missing actual collection command")
    if "build_external_postcollection_evidence_seal.py" not in operator_packet.get("postcollection_seal_command", ""):
        fail("external operator packet missing postcollection seal command")
    if "audit_external_postcollection_seal_consistency.py" not in operator_packet.get("postcollection_consistency_command", ""):
        fail("external operator packet missing postcollection consistency command")
    post_commands = operator_packet.get("post_collection_strict_commands", []) or []
    for command_fragment in ("validate_external_rollouts.py", "audit_external_pairing_integrity.py", "audit_external_evidence.py"):
        if not any(command_fragment in command for command in post_commands):
            fail(f"external operator packet missing post-collection gate: {command_fragment}")

    handoff_bundle_path = RESULTS / "external_operator_handoff_bundle.json"
    if not handoff_bundle_path.exists():
        fail("missing results/external_operator_handoff_bundle.json; run scripts/build_external_operator_handoff_bundle.py")
    handoff_bundle = json.loads(handoff_bundle_path.read_text(encoding="utf-8"))
    if handoff_bundle.get("version") != "external_operator_handoff_bundle_v1":
        fail("external operator handoff bundle version mismatch")
    if handoff_bundle.get("passed") is not True:
        fail("external operator handoff bundle did not pass")
    if handoff_bundle.get("not_external_evidence") is not True:
        fail("external operator handoff bundle must declare that it is not evidence")
    if handoff_bundle.get("handoff_bundle_ready") is not True:
        fail("external operator handoff bundle must report handoff_bundle_ready=true")
    if handoff_bundle.get("strict_evidence_ready") is not False:
        fail("external operator handoff bundle must not claim strict evidence readiness")
    if handoff_bundle.get("start_state") != "DO_NOT_COLLECT_YET":
        fail("external operator handoff bundle must preserve the no-go start state")
    if int(handoff_bundle.get("included_file_count", 0) or 0) < 120:
        fail("external operator handoff bundle includes too few operator-facing files")
    if handoff_bundle.get("forbidden_included_paths"):
        fail(f"external operator handoff bundle includes forbidden evidence paths: {handoff_bundle.get('forbidden_included_paths')}")
    if handoff_bundle.get("missing_files"):
        fail(f"external operator handoff bundle has missing files: {handoff_bundle.get('missing_files')}")
    category_counts = handoff_bundle.get("category_counts", {}) or {}
    if int(category_counts.get("task_card", 0) or 0) < 4:
        fail("external operator handoff bundle must include all task cards")
    if int(category_counts.get("config_template", 0) or 0) < 4:
        fail("external operator handoff bundle must include all config templates")
    if int(category_counts.get("prepared_config_input", 0) or 0) < 4:
        fail("external operator handoff bundle must include prepared config inputs")
    if int(category_counts.get("baseline_spec", 0) or 0) < 12:
        fail("external operator handoff bundle must include baseline specs")
    handoff_checks = {entry.get("name"): entry.get("passed") for entry in handoff_bundle.get("checks", [])}
    for required_check in (
        "operator_packet_is_no_go_non_evidence",
        "acquisition_maps_all_remaining_blockers",
        "strict_evidence_gates_remain_fail_closed",
        "bundle_files_exist",
        "bundle_excludes_rollout_evidence_artifacts",
        "no_real_manifest_written",
        "handoff_has_task_config_and_baseline_assets",
        "analysis_plan_included",
        "platform_onboarding_included",
        "fidelity_metadata_probe_included",
        "fidelity_provenance_packet_included",
        "fidelity_acceptance_draft_included",
        "fidelity_acceptance_materializer_included",
        "backend_integration_packet_included",
        "maniskill_reference_backend_included",
        "maniskill_reference_collection_preflight_included",
        "config_manifest_packet_included",
        "config_materialization_self_test_included",
        "rollout_evidence_packet_included",
        "ablation_collection_packet_included",
        "ablation_collection_packet_self_test_included",
        "evidence_intake_ledger_included",
        "evidence_intake_ledger_self_test_included",
        "precollection_manifest_draft_included",
        "precollection_manifest_draft_self_test_included",
        "precollection_freeze_receipt_included",
        "postcollection_evidence_seal_included",
        "postcollection_seal_consistency_gate_included",
        "pilot_smoke_packet_included",
        "maniskill_render_video_preflight_included",
        "maniskill_render_resource_sweep_included",
        "maniskill_pilot_runtime_liveness_included",
        "maniskill_render_machine_qualification_included",
        "external_collection_job_packet_included",
        "collection_machine_bootstrap_included",
        "method_implementation_packet_included",
        "baseline_contract_self_test_included",
        "method_config_materialization_included",
        "method_config_materialization_self_test_included",
        "operator_actions_cover_evidence_collection",
        "post_collection_commands_cover_strict_gates",
        "file_hashes_are_recorded",
    ):
        if handoff_checks.get(required_check) is not True:
            fail(f"external operator handoff bundle missing passing check: {required_check}")

    handoff_self_test_path = RESULTS / "external_operator_handoff_bundle_self_test.json"
    handoff_self_test_md_path = RESULTS / "external_operator_handoff_bundle_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_operator_handoff_bundle.py",
        handoff_self_test_path,
        handoff_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external operator handoff bundle self-test artifact: {path}")
    handoff_self_test = json.loads(handoff_self_test_path.read_text(encoding="utf-8"))
    if handoff_self_test.get("version") != "external_operator_handoff_bundle_self_test_v1":
        fail("external operator handoff bundle self-test version mismatch")
    if handoff_self_test.get("passed") is not True:
        fail("external operator handoff bundle self-test did not pass")
    if handoff_self_test.get("not_external_evidence") is not True:
        fail("external operator handoff bundle self-test must declare that it is not evidence")
    if handoff_self_test.get("strict_external_evidence_ready") is not False:
        fail("external operator handoff bundle self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_ready",
        "missing_source_rejected",
        "no_go_drift_rejected",
        "acquisition_blocker_drift_rejected",
        "strict_evidence_drift_rejected",
        "missing_included_file_rejected",
        "forbidden_evidence_path_rejected",
        "premature_manifest_rejected",
        "missing_collection_job_rejected",
        "missing_machine_bootstrap_rejected",
        "real_outputs_untouched",
    ):
        if handoff_self_test.get(field) is not True:
            fail(f"external operator handoff bundle self-test field must be true: {field}")
    handoff_self_checks = {check.get("name"): check.get("passed") for check in handoff_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_builds_current_handoff_bundle",
        "missing_source_rejected",
        "no_go_drift_rejected",
        "acquisition_blocker_drift_rejected",
        "strict_evidence_drift_rejected",
        "missing_included_file_rejected",
        "forbidden_evidence_path_rejected",
        "premature_manifest_rejected",
        "missing_collection_job_rejected",
        "missing_machine_bootstrap_rejected",
        "real_repository_handoff_outputs_untouched",
    ):
        if handoff_self_checks.get(required_check) is not True:
            fail(f"external operator handoff bundle self-test missing passing check: {required_check}")

    collection_job_packet_path = EXTERNAL / "collection_job_packet.json"
    collection_job_packet_md_path = EXTERNAL / "collection_job_packet.md"
    collection_job_commands_path = EXTERNAL / "collection_job_commands.ps1"
    collection_job_checklist_path = EXTERNAL / "collection_job_checklist.csv"
    collection_job_audit_path = RESULTS / "external_collection_job_packet_audit.json"
    collection_job_audit_md_path = RESULTS / "external_collection_job_packet_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_collection_job_packet.py",
        collection_job_packet_path,
        collection_job_packet_md_path,
        collection_job_commands_path,
        collection_job_checklist_path,
        collection_job_audit_path,
        collection_job_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external collection job packet artifact: {path}")
    collection_job_packet = json.loads(collection_job_packet_path.read_text(encoding="utf-8"))
    collection_job_audit = json.loads(collection_job_audit_path.read_text(encoding="utf-8"))
    if collection_job_packet.get("version") != "external_collection_job_packet_v1":
        fail("external collection job packet version mismatch")
    if collection_job_audit.get("version") != "external_collection_job_packet_audit_v1":
        fail("external collection job packet audit version mismatch")
    for name, payload in (("packet", collection_job_packet), ("audit", collection_job_audit)):
        if payload.get("passed") is not True:
            fail(f"external collection job {name} did not pass")
        if payload.get("not_external_evidence") is not True:
            fail(f"external collection job {name} must declare that it is not evidence")
        if payload.get("strict_external_evidence_ready") is not False:
            fail(f"external collection job {name} must not claim strict external evidence readiness")
        if payload.get("job_state") != "DO_NOT_START_COLLECTION_YET":
            fail(f"external collection job {name} must remain fail-closed before real evidence")
        if payload.get("collection_ready") is not False:
            fail(f"external collection job {name} must preserve collection_ready=false in the current repo")
        if payload.get("render_machine_qualified") is not False:
            fail(f"external collection job {name} must preserve render_machine_qualified=false in the current repo")
        if int(payload.get("remaining_submission_blocker_count", 0) or 0) != 4:
            fail(f"external collection job {name} must map the four remaining submission blockers")
        if len(payload.get("job_steps", []) or []) < 17:
            fail(f"external collection job {name} has too few ordered job steps")
    collection_job_ids = {str(step.get("id", "")) for step in collection_job_packet.get("job_steps", []) if isinstance(step, dict)}
    for required_job_id in (
        "platform_probe",
        "render_profile_matrix",
        "pilot_runtime_liveness",
        "backend_contract",
        "fidelity_acceptance_materialization",
        "strict_collection_readiness",
        "precollection_freeze_receipt",
        "official_collection_runner",
        "postcollection_evidence_seal",
        "postcollection_seal_consistency",
        "manifest_promotion",
        "strict_rollout_recompute",
        "strict_config_evidence",
        "strict_adapter_evidence",
        "strict_pairing_integrity",
        "strict_release_package",
        "final_external_evidence_audit",
    ):
        if required_job_id not in collection_job_ids:
            fail(f"external collection job packet missing job step: {required_job_id}")
    collection_job_checks = {check.get("name"): check.get("passed") for check in collection_job_audit.get("checks", [])}
    for required_check in (
        "job_packet_is_non_evidence",
        "source_payloads_loaded",
        "job_state_fail_closed_until_render_and_collection_ready",
        "command_sequence_covers_full_external_validation_route",
        "command_order_preserves_preflight_collection_manifest_safety",
        "official_collection_commands_guarded",
        "current_blockers_explicit_and_mapped",
        "pre_and_postcollection_hash_gates_present",
        "render_machine_self_test_proves_ready_and_fail_closed_cases",
        "no_real_manifest_written",
    ):
        if collection_job_checks.get(required_check) is not True:
            fail(f"external collection job packet audit missing passing check: {required_check}")
    collection_job_command_text = collection_job_commands_path.read_text(encoding="utf-8")
    for fragment in (
        "ConfirmOfficialCollection",
        "Assert-NoPlaceholder",
        "audit_maniskill_render_video_preflight.py",
        "audit_maniskill_pilot_runtime_liveness.py",
        "materialize_fidelity_acceptance.py",
        "audit_external_collection_readiness.py",
        "real_collection_runner.py",
        "build_external_manifest.py",
        "validate_external_rollouts.py",
        "audit_external_evidence.py",
    ):
        if fragment not in collection_job_command_text:
            fail(f"external collection job command file missing fragment: {fragment}")

    collection_job_self_test_path = RESULTS / "external_collection_job_packet_self_test.json"
    collection_job_self_test_md_path = RESULTS / "external_collection_job_packet_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_collection_job_packet.py",
        collection_job_self_test_path,
        collection_job_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external collection job packet self-test artifact: {path}")
    collection_job_self_test = json.loads(collection_job_self_test_path.read_text(encoding="utf-8"))
    if collection_job_self_test.get("version") != "external_collection_job_packet_self_test_v1":
        fail("external collection job packet self-test version mismatch")
    if collection_job_self_test.get("passed") is not True:
        fail("external collection job packet self-test did not pass")
    if collection_job_self_test.get("not_external_evidence") is not True:
        fail("external collection job packet self-test must declare that it is not evidence")
    if collection_job_self_test.get("strict_external_evidence_ready") is not False:
        fail("external collection job packet self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_ready",
        "missing_source_rejected",
        "source_evidence_drift_rejected",
        "premature_manifest_rejected",
        "premature_ready_state_rejected",
        "unsafe_command_spine_rejected",
        "hash_gate_drift_rejected",
        "render_self_test_drift_rejected",
        "real_outputs_untouched",
    ):
        if collection_job_self_test.get(field) is not True:
            fail(f"external collection job packet self-test field must be true: {field}")
    collection_job_self_checks = {check.get("name"): check.get("passed") for check in collection_job_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_builds_current_collection_job_packet",
        "missing_source_payload_rejected",
        "source_non_evidence_drift_rejected",
        "premature_manifest_rejected",
        "premature_ready_state_rejected",
        "unsafe_command_spine_rejected",
        "hash_gate_drift_rejected",
        "render_self_test_drift_rejected",
        "real_repository_collection_job_outputs_untouched",
    ):
        if collection_job_self_checks.get(required_check) is not True:
            fail(f"external collection job packet self-test missing passing check: {required_check}")

    bootstrap_packet_path = EXTERNAL / "collection_machine_bootstrap.json"
    bootstrap_packet_md_path = EXTERNAL / "collection_machine_bootstrap.md"
    bootstrap_command_path = EXTERNAL / "collection_machine_bootstrap.ps1"
    bootstrap_audit_path = RESULTS / "external_collection_machine_bootstrap_audit.json"
    bootstrap_audit_md_path = RESULTS / "external_collection_machine_bootstrap_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_collection_machine_bootstrap.py",
        bootstrap_packet_path,
        bootstrap_packet_md_path,
        bootstrap_command_path,
        bootstrap_audit_path,
        bootstrap_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external collection machine bootstrap artifact: {path}")
    bootstrap_packet = json.loads(bootstrap_packet_path.read_text(encoding="utf-8"))
    bootstrap_audit = json.loads(bootstrap_audit_path.read_text(encoding="utf-8"))
    if bootstrap_packet.get("version") != "external_collection_machine_bootstrap_v1":
        fail("external collection machine bootstrap packet version mismatch")
    if bootstrap_audit.get("version") != "external_collection_machine_bootstrap_audit_v1":
        fail("external collection machine bootstrap audit version mismatch")
    if bootstrap_audit.get("packet_version") != "external_collection_machine_bootstrap_v1":
        fail("external collection machine bootstrap audit must record the packet version")
    for name, payload in (("packet", bootstrap_packet), ("audit", bootstrap_audit)):
        if payload.get("passed") is not True:
            fail(f"external collection machine bootstrap {name} did not pass")
        if payload.get("not_external_evidence") is not True:
            fail(f"external collection machine bootstrap {name} must declare that it is not evidence")
        if payload.get("strict_external_evidence_ready") is not False:
            fail(f"external collection machine bootstrap {name} must not claim strict external evidence readiness")
        if payload.get("bootstrap_state") != "READY_TO_BOOTSTRAP_EXTERNAL_MACHINE":
            fail(f"external collection machine bootstrap {name} must be ready to bootstrap an external machine")
        if len(payload.get("bootstrap_steps", []) or []) < 7:
            fail(f"external collection machine bootstrap {name} has too few bootstrap steps")
    bootstrap_checks = {check.get("name"): check.get("passed") for check in bootstrap_audit.get("checks", [])}
    for required_check in (
        "bootstrap_packet_is_non_evidence",
        "source_platform_onboarding_ready",
        "source_collection_job_still_no_go",
        "local_machine_not_promoted",
        "bootstrap_commands_cover_machine_render_and_liveness",
        "bootstrap_requires_explicit_confirmation",
        "bootstrap_script_is_probe_only",
        "install_guidance_mentions_core_optional_stack",
        "no_real_outputs_written",
    ):
        if bootstrap_checks.get(required_check) is not True:
            fail(f"external collection machine bootstrap missing passing check: {required_check}")
    bootstrap_command_text = bootstrap_command_path.read_text(encoding="utf-8")
    for fragment in (
        "ConfirmBootstrapOnly",
        "probe_external_platform.py --strict",
        "probe_maniskill_task_bindings.py --strict",
        "probe_maniskill_env_smoke.py --strict",
        "probe_maniskill_fidelity_metadata.py --strict",
        "audit_maniskill_render_video_preflight.py",
        "audit_maniskill_pilot_runtime_liveness.py",
        "build_maniskill_render_machine_qualification.py",
        "mani_skill",
        "torch",
        "imageio-ffmpeg",
    ):
        if fragment not in bootstrap_command_text:
            fail(f"external collection machine bootstrap command file missing fragment: {fragment}")
    for forbidden in ("real_collection_runner.py", "materialize_fidelity_acceptance.py", "build_external_manifest.py --write"):
        if forbidden in bootstrap_command_text:
            fail(f"external collection machine bootstrap command file must not include collection/evidence command: {forbidden}")

    bootstrap_self_test_path = RESULTS / "external_collection_machine_bootstrap_self_test.json"
    bootstrap_self_test_md_path = RESULTS / "external_collection_machine_bootstrap_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_collection_machine_bootstrap.py",
        bootstrap_self_test_path,
        bootstrap_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external collection machine bootstrap self-test artifact: {path}")
    bootstrap_self_test = json.loads(bootstrap_self_test_path.read_text(encoding="utf-8"))
    if bootstrap_self_test.get("version") != "external_collection_machine_bootstrap_self_test_v1":
        fail("external collection machine bootstrap self-test version mismatch")
    if bootstrap_self_test.get("passed") is not True:
        fail("external collection machine bootstrap self-test did not pass")
    if bootstrap_self_test.get("not_external_evidence") is not True:
        fail("external collection machine bootstrap self-test must declare that it is not evidence")
    if bootstrap_self_test.get("strict_external_evidence_ready") is not False:
        fail("external collection machine bootstrap self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_ready",
        "missing_source_rejected",
        "source_evidence_drift_rejected",
        "collection_job_go_state_rejected",
        "local_machine_promotion_rejected",
        "unsafe_command_rejected",
        "missing_confirmation_rejected",
        "install_guidance_drift_rejected",
        "premature_outputs_rejected",
        "real_outputs_untouched",
    ):
        if bootstrap_self_test.get(field) is not True:
            fail(f"external collection machine bootstrap self-test field must be true: {field}")
    bootstrap_self_checks = {check.get("name"): check.get("passed") for check in bootstrap_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_builds_current_bootstrap_packet",
        "missing_source_report_rejected",
        "source_non_evidence_drift_rejected",
        "collection_job_go_state_rejected",
        "local_machine_promotion_rejected",
        "unsafe_command_rejected",
        "missing_confirmation_rejected",
        "install_guidance_drift_rejected",
        "premature_outputs_rejected",
        "real_repository_bootstrap_outputs_untouched",
    ):
        if bootstrap_self_checks.get(required_check) is not True:
            fail(f"external collection machine bootstrap self-test missing passing check: {required_check}")

    operator_release_path = RESULTS / "external_operator_release_bundle_plan.json"
    operator_release_md_path = RESULTS / "external_operator_release_bundle_plan.md"
    operator_release_manifest_path = EXTERNAL / "operator_release_bundle_manifest.csv"
    operator_release_readme_path = EXTERNAL / "operator_release_bundle_README.md"
    for path in (
        ROOT / "scripts" / "build_external_operator_release_bundle.py",
        operator_release_path,
        operator_release_md_path,
        operator_release_manifest_path,
        operator_release_readme_path,
    ):
        if not path.exists():
            fail(f"missing external operator release bundle artifact: {path}")
    operator_release = json.loads(operator_release_path.read_text(encoding="utf-8"))
    if operator_release.get("version") != "external_operator_release_bundle_plan_v1":
        fail("external operator release bundle plan version mismatch")
    if operator_release.get("passed") is not True:
        fail("external operator release bundle plan did not pass")
    if operator_release.get("not_external_evidence") is not True:
        fail("external operator release bundle plan must declare that it is not evidence")
    if operator_release.get("strict_external_evidence_ready") is not False:
        fail("external operator release bundle plan must not claim strict external evidence readiness")
    if operator_release.get("bundle_state") != "READY_TO_SEND_OPERATOR_PACKAGE":
        fail("external operator release bundle must report READY_TO_SEND_OPERATOR_PACKAGE")
    if operator_release.get("archive_write_enabled") is not False or operator_release.get("archive_written") is not False:
        fail("external operator release bundle default validation must not write an archive")
    if int(operator_release.get("included_file_count", 0) or 0) < 300:
        fail("external operator release bundle covers too few handoff files")
    if operator_release.get("missing_files") or operator_release.get("mismatched_hashes") or operator_release.get("forbidden_paths"):
        fail("external operator release bundle has missing, mismatched, or forbidden paths")
    release_checks = {check.get("name"): check.get("passed") for check in operator_release.get("checks", [])}
    for required_check in (
        "release_bundle_is_non_evidence",
        "source_handoff_bundle_ready",
        "collection_job_packet_present_in_handoff",
        "handoff_hashes_recomputed",
        "forbidden_evidence_paths_excluded",
        "release_manifest_covers_all_handoff_files",
        "archive_writer_is_explicit_and_optional",
        "no_real_manifest_written",
        "archive_not_written_by_default",
    ):
        if release_checks.get(required_check) is not True:
            fail(f"external operator release bundle plan missing passing check: {required_check}")
    manifest_rows = count_rows(operator_release_manifest_path)
    if manifest_rows != int(operator_release.get("included_file_count", 0) or 0):
        fail("external operator release bundle manifest row count must match included_file_count")
    release_readme_text = operator_release_readme_path.read_text(encoding="utf-8")
    for fragment in ("non-evidence", "operator handoff", "--write-archive", "external_validation/manifest.json"):
        if fragment not in release_readme_text:
            fail(f"external operator release README missing fragment: {fragment}")

    operator_release_self_test_path = RESULTS / "external_operator_release_bundle_self_test.json"
    operator_release_self_test_md_path = RESULTS / "external_operator_release_bundle_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_operator_release_bundle.py",
        operator_release_self_test_path,
        operator_release_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external operator release bundle self-test artifact: {path}")
    operator_release_self_test = json.loads(operator_release_self_test_path.read_text(encoding="utf-8"))
    if operator_release_self_test.get("version") != "external_operator_release_bundle_self_test_v1":
        fail("external operator release bundle self-test version mismatch")
    if operator_release_self_test.get("passed") is not True:
        fail("external operator release bundle self-test did not pass")
    if operator_release_self_test.get("not_external_evidence") is not True:
        fail("external operator release bundle self-test must declare that it is not evidence")
    if operator_release_self_test.get("strict_external_evidence_ready") is not False:
        fail("external operator release bundle self-test must keep strict external evidence false")
    for field in (
        "temporary_fixture_ready",
        "explicit_archive_fixture_ready",
        "missing_handoff_rejected",
        "handoff_no_go_drift_rejected",
        "missing_file_rejected",
        "hash_drift_rejected",
        "forbidden_evidence_path_rejected",
        "premature_manifest_rejected",
        "collection_job_go_state_rejected",
        "collection_job_omission_rejected",
        "real_outputs_untouched",
    ):
        if operator_release_self_test.get(field) is not True:
            fail(f"external operator release bundle self-test field must be true: {field}")
    operator_release_self_checks = {check.get("name"): check.get("passed") for check in operator_release_self_test.get("checks", [])}
    for required_check in (
        "temporary_fixture_builds_current_release_plan",
        "explicit_archive_fixture_writes_deterministic_transfer_zip",
        "missing_handoff_source_rejected",
        "handoff_no_go_drift_rejected",
        "missing_file_rejected",
        "hash_drift_rejected",
        "forbidden_evidence_path_rejected",
        "premature_manifest_rejected",
        "collection_job_go_state_rejected",
        "collection_job_omission_rejected",
        "real_repository_release_outputs_untouched",
    ):
        if operator_release_self_checks.get(required_check) is not True:
            fail(f"external operator release bundle self-test missing passing check: {required_check}")

    config_materialization_path = RESULTS / "external_config_materialization_plan.json"
    if not config_materialization_path.exists():
        fail("missing results/external_config_materialization_plan.json; run scripts/materialize_external_configs.py")
    config_materialization = json.loads(config_materialization_path.read_text(encoding="utf-8"))
    config_materialization_self_test_path = RESULTS / "external_config_materialization_self_test.json"
    config_materialization_self_test_md_path = RESULTS / "external_config_materialization_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_external_config_materialization.py",
        config_materialization_self_test_path,
        config_materialization_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing external config materialization self-test artifact: {path}")
    config_materialization_self_test = json.loads(config_materialization_self_test_path.read_text(encoding="utf-8"))
    if config_materialization.get("version") != "external_config_materialization_plan_v1":
        fail("external config materialization plan version mismatch")
    if config_materialization.get("passed") is not True:
        fail("external config materialization plan did not pass")
    if config_materialization.get("not_external_evidence") is not True:
        fail("external config materialization plan must declare that it is not evidence")
    if config_materialization.get("write_enabled") is not False:
        fail("external config materialization plan should not write configs during validation")
    if config_materialization.get("strict_config_evidence_ready") is not False:
        fail("external config materialization plan must not claim strict config evidence readiness")
    if int(config_materialization.get("task_count", 0) or 0) < 4:
        fail("external config materialization plan covers too few tasks")
    if not config_materialization.get("operator_write_command", "").endswith("--confirm-real-platform --write"):
        fail("external config materialization plan missing guarded operator write command")
    if config_materialization_self_test.get("version") != "external_config_materialization_self_test_v1":
        fail("external config materialization self-test version mismatch")
    if config_materialization_self_test.get("passed") is not True:
        fail("external config materialization self-test did not pass")
    if config_materialization_self_test.get("not_external_evidence") is not True:
        fail("external config materialization self-test must declare that it is not evidence")
    if config_materialization_self_test.get("strict_config_evidence_ready") is not False:
        fail("external config materialization self-test must keep strict config evidence false")
    for required_field in (
        "temporary_plan_ready",
        "confirmed_write_fixture_ready",
        "write_without_confirm_rejected",
        "placeholder_platform_write_rejected",
        "template_token_write_rejected",
        "missing_task_binding_rejected",
        "overwrite_without_force_rejected",
        "real_outputs_untouched",
    ):
        if config_materialization_self_test.get(required_field) is not True:
            fail(f"external config materialization self-test missing passing field: {required_field}")
    config_materialization_self_checks = {
        check.get("name"): check.get("passed") for check in config_materialization_self_test.get("checks", []) or []
    }
    for required_check in (
        "temporary_config_materialization_plan_ready_but_non_evidence",
        "confirmed_temp_write_materializes_schema_valid_configs",
        "write_without_confirmation_rejected",
        "placeholder_platform_write_rejected",
        "template_token_write_rejected",
        "missing_task_binding_file_rejected",
        "overwrite_without_force_rejected",
        "real_config_materialization_outputs_untouched",
    ):
        if config_materialization_self_checks.get(required_check) is not True:
            fail(f"external config materialization self-test missing passing check: {required_check}")

    config_manifest_packet_path = EXTERNAL / "config_manifest_packet.json"
    config_manifest_packet_md_path = EXTERNAL / "config_manifest_packet.md"
    config_manifest_orders_path = EXTERNAL / "config_manifest_work_orders.csv"
    config_manifest_audit_path = RESULTS / "external_config_manifest_audit.json"
    config_manifest_audit_md_path = RESULTS / "external_config_manifest_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_config_manifest_packet.py",
        config_manifest_packet_path,
        config_manifest_packet_md_path,
        config_manifest_orders_path,
        config_manifest_audit_path,
        config_manifest_audit_md_path,
        ROOT / "scripts" / "self_test_external_config_manifest_packet.py",
        RESULTS / "external_config_manifest_packet_self_test.json",
        RESULTS / "external_config_manifest_packet_self_test.md",
    ):
        if not path.exists():
            fail(f"missing external config manifest packet artifact: {path}")
    config_manifest_packet = json.loads(config_manifest_packet_path.read_text(encoding="utf-8"))
    config_manifest_audit = json.loads(config_manifest_audit_path.read_text(encoding="utf-8"))
    if config_manifest_packet.get("version") != "external_config_manifest_packet_v1":
        fail("external config manifest packet version mismatch")
    if config_manifest_packet.get("not_external_evidence") is not True:
        fail("external config manifest packet must declare that it is not evidence")
    if config_manifest_packet.get("config_manifest_packet_ready") is not True:
        fail("external config manifest packet must report config_manifest_packet_ready=true")
    if config_manifest_packet.get("strict_config_evidence_ready") is not False:
        fail("external config manifest packet must not claim strict config evidence readiness")
    if config_manifest_packet.get("manifest_declared_config_ready") is not False:
        fail("external config manifest packet must not claim manifest-declared config readiness")
    if config_manifest_packet.get("manifest_written") is not False:
        fail("external config manifest packet must not write the real manifest")
    if int(config_manifest_packet.get("manifest_task_count", 0) or 0) < 4:
        fail("external config manifest packet covers too few manifest tasks")
    if int(config_manifest_packet.get("prepared_config_count", 0) or 0) < 4:
        fail("external config manifest packet covers too few prepared configs")
    command_text = "\n".join(config_manifest_packet.get("strict_acceptance_commands", []) or [])
    for fragment in (
        "build_external_config_manifest_packet.py",
        "materialize_external_configs.py",
        "build_external_manifest.py --write",
        "validate_external_configs.py --strict",
        "audit_external_release_package.py --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in command_text:
            fail(f"external config manifest packet missing strict command fragment: {fragment}")
    if config_manifest_audit.get("version") != "external_config_manifest_audit_v1":
        fail("external config manifest audit version mismatch")
    if config_manifest_audit.get("passed") is not True:
        fail("external config manifest audit did not pass")
    if config_manifest_audit.get("not_external_evidence") is not True:
        fail("external config manifest audit must declare that it is not evidence")
    if config_manifest_audit.get("config_manifest_packet_ready") is not True:
        fail("external config manifest audit must report config_manifest_packet_ready=true")
    if config_manifest_audit.get("strict_config_evidence_ready") is not False:
        fail("external config manifest audit must keep strict config evidence false")
    if config_manifest_audit.get("manifest_declared_config_ready") is not False:
        fail("external config manifest audit must keep manifest-declared config readiness false")
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "materialization_plan_ready_but_not_evidence",
        "template_audit_passes",
        "strict_config_evidence_still_fails_without_manifest",
        "manifest_template_declares_all_collection_tasks",
        "prepared_config_files_have_hashes",
        "prepared_configs_pass_strict_schema_if_manifest_declared",
        "work_orders_cover_config_to_manifest_path",
        "strict_commands_cover_config_manifest_release_and_evidence",
        "collection_readiness_preserves_config_boundary",
        "manifest_template_paths_match_prepared_configs",
        "packet_files_written",
    ):
        if config_manifest_checks.get(required_check) is not True:
            fail(f"external config manifest audit missing passing check: {required_check}")
    config_manifest_self_test = json.loads((RESULTS / "external_config_manifest_packet_self_test.json").read_text(encoding="utf-8"))
    if config_manifest_self_test.get("version") != "external_config_manifest_packet_self_test_v1":
        fail("external config manifest packet self-test version mismatch")
    if config_manifest_self_test.get("passed") is not True:
        fail("external config manifest packet self-test did not pass")
    if config_manifest_self_test.get("not_external_evidence") is not True:
        fail("external config manifest packet self-test must declare that it is not evidence")
    if config_manifest_self_test.get("strict_config_evidence_ready") is not False:
        fail("external config manifest packet self-test must not claim strict config evidence")
    if config_manifest_self_test.get("manifest_declared_config_ready") is not False:
        fail("external config manifest packet self-test must not claim manifest-declared config readiness")
    for required_flag in (
        "temporary_packet_ready",
        "missing_task_work_orders_rejected",
        "premature_evidence_promotion_rejected",
        "materialization_write_drift_rejected",
        "template_audit_shrink_rejected",
        "strict_config_evidence_promotion_rejected",
        "manifest_task_omission_rejected",
        "prepared_config_hash_drift_rejected",
        "prepared_config_validation_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "manifest_path_drift_rejected",
        "real_outputs_untouched",
    ):
        if config_manifest_self_test.get(required_flag) is not True:
            fail(f"external config manifest packet self-test missing true flag: {required_flag}")
    config_manifest_self_checks = {
        check.get("name"): check.get("passed")
        for check in config_manifest_self_test.get("checks", []) or []
    }
    for required_check in (
        "temporary_config_manifest_packet_ready_but_non_evidence",
        "missing_task_work_orders_rejected",
        "premature_evidence_promotion_rejected",
        "materialization_write_drift_rejected",
        "template_audit_shrink_rejected",
        "strict_config_evidence_promotion_rejected",
        "manifest_task_omission_rejected",
        "prepared_config_hash_drift_rejected",
        "prepared_config_validation_drift_rejected",
        "strict_command_drift_rejected",
        "real_manifest_write_rejected",
        "manifest_path_drift_rejected",
        "real_config_manifest_outputs_untouched",
    ):
        if config_manifest_self_checks.get(required_check) is not True:
            fail(f"external config manifest packet self-test missing passing check: {required_check}")

    fidelity_packet_path = EXTERNAL / "fidelity_provenance_packet.json"
    fidelity_packet_md_path = EXTERNAL / "fidelity_provenance_packet.md"
    fidelity_orders_path = EXTERNAL / "fidelity_provenance_work_orders.csv"
    fidelity_audit_path = RESULTS / "external_fidelity_provenance_audit.json"
    fidelity_audit_md_path = RESULTS / "external_fidelity_provenance_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_fidelity_provenance_packet.py",
        ROOT / "scripts" / "self_test_external_fidelity_provenance_packet.py",
        fidelity_packet_path,
        fidelity_packet_md_path,
        fidelity_orders_path,
        fidelity_audit_path,
        fidelity_audit_md_path,
        RESULTS / "external_fidelity_provenance_packet_self_test.json",
        RESULTS / "external_fidelity_provenance_packet_self_test.md",
    ):
        if not path.exists():
            fail(f"missing external fidelity provenance packet artifact: {path}")
    fidelity_packet = json.loads(fidelity_packet_path.read_text(encoding="utf-8"))
    fidelity_audit = json.loads(fidelity_audit_path.read_text(encoding="utf-8"))
    fidelity_self_test = json.loads((RESULTS / "external_fidelity_provenance_packet_self_test.json").read_text(encoding="utf-8"))
    if fidelity_packet.get("version") != "external_fidelity_provenance_packet_v1":
        fail("external fidelity provenance packet version mismatch")
    if fidelity_packet.get("not_external_evidence") is not True:
        fail("external fidelity provenance packet must declare that it is not evidence")
    if fidelity_packet.get("fidelity_provenance_packet_ready") is not True:
        fail("external fidelity provenance packet must report fidelity_provenance_packet_ready=true")
    if fidelity_packet.get("strict_fidelity_evidence_ready") is not False:
        fail("external fidelity provenance packet must not claim strict fidelity evidence readiness")
    if fidelity_packet.get("strict_external_evidence_ready") is not False:
        fail("external fidelity provenance packet must not claim strict external evidence readiness")
    if fidelity_packet.get("acceptance_ready") is not False:
        fail("external fidelity provenance packet must not claim acceptance readiness")
    if fidelity_packet.get("manifest_written") is not False:
        fail("external fidelity provenance packet must not write the real manifest")
    if int(fidelity_packet.get("blocking_missing_count", 0) or 0) < 10:
        fail("external fidelity provenance packet should expose current fidelity blockers")
    if len(fidelity_packet.get("work_orders", []) or []) < 6:
        fail("external fidelity provenance packet has too few work orders")
    command_text = "\n".join(fidelity_packet.get("strict_acceptance_commands", []) or [])
    for fragment in (
        "build_external_fidelity_provenance_packet.py",
        "build_external_platform_onboarding.py",
        "probe_external_platform.py --strict",
        "materialize_fidelity_acceptance.py",
        "audit_external_fidelity_acceptance.py --strict",
        "build_external_manifest.py --write",
        "audit_external_collection_readiness.py --strict",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in command_text:
            fail(f"external fidelity provenance packet missing strict command fragment: {fragment}")
    if fidelity_audit.get("version") != "external_fidelity_provenance_audit_v1":
        fail("external fidelity provenance audit version mismatch")
    if fidelity_audit.get("passed") is not True:
        fail("external fidelity provenance audit did not pass")
    if fidelity_audit.get("not_external_evidence") is not True:
        fail("external fidelity provenance audit must declare that it is not evidence")
    if fidelity_audit.get("fidelity_provenance_packet_ready") is not True:
        fail("external fidelity provenance audit must report fidelity_provenance_packet_ready=true")
    if fidelity_audit.get("strict_fidelity_evidence_ready") is not False:
        fail("external fidelity provenance audit must keep strict fidelity evidence false")
    if fidelity_audit.get("strict_external_evidence_ready") is not False:
        fail("external fidelity provenance audit must keep strict external evidence false")
    fidelity_checks = {check.get("name"): check.get("passed") for check in fidelity_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "fidelity_acceptance_contract_ready_but_not_evidence",
        "platform_onboarding_packet_ready",
        "external_platform_probe_ready",
        "independent_route_and_collection_still_fail_closed",
        "template_declares_required_platform_and_gate_fields",
        "work_orders_cover_fidelity_blockers",
        "work_orders_are_actionable_and_artifact_bound",
        "strict_commands_cover_fidelity_manifest_collection_and_evidence",
        "acceptance_template_not_real_evidence",
        "no_real_acceptance_or_manifest_written",
        "packet_files_written",
    ):
        if fidelity_checks.get(required_check) is not True:
            fail(f"external fidelity provenance audit missing passing check: {required_check}")
    if fidelity_self_test.get("version") != "external_fidelity_provenance_packet_self_test_v1":
        fail("external fidelity provenance packet self-test version mismatch")
    if fidelity_self_test.get("passed") is not True:
        fail("external fidelity provenance packet self-test did not pass")
    if fidelity_self_test.get("not_external_evidence") is not True:
        fail("external fidelity provenance packet self-test must declare non-evidence")
    if fidelity_self_test.get("strict_fidelity_evidence_ready") is not False:
        fail("external fidelity provenance packet self-test must keep strict fidelity evidence false")
    if fidelity_self_test.get("strict_external_evidence_ready") is not False:
        fail("external fidelity provenance packet self-test must keep strict external evidence false")
    for required_flag in (
        "temporary_packet_ready",
        "missing_work_orders_rejected",
        "work_order_artifact_command_drift_rejected",
        "premature_evidence_promotion_rejected",
        "acceptance_ready_drift_rejected",
        "onboarding_strict_evidence_drift_rejected",
        "platform_probe_promotion_rejected",
        "collection_ready_promotion_rejected",
        "template_gate_shrink_rejected",
        "strict_command_drift_rejected",
        "real_acceptance_or_manifest_write_rejected",
        "packet_file_deletion_rejected",
        "real_outputs_untouched",
    ):
        if fidelity_self_test.get(required_flag) is not True:
            fail(f"external fidelity provenance packet self-test missing true flag: {required_flag}")
    fidelity_self_checks = {
        check.get("name"): check.get("passed")
        for check in fidelity_self_test.get("checks", []) or []
    }
    for required_check in (
        "temporary_fidelity_provenance_packet_ready_but_non_evidence",
        "missing_work_orders_rejected",
        "work_order_artifact_command_drift_rejected",
        "premature_evidence_promotion_rejected",
        "acceptance_ready_drift_rejected",
        "onboarding_strict_evidence_drift_rejected",
        "platform_probe_promotion_rejected",
        "collection_ready_promotion_rejected",
        "template_gate_shrink_rejected",
        "strict_command_drift_rejected",
        "real_acceptance_or_manifest_write_rejected",
        "packet_file_deletion_rejected",
        "real_fidelity_provenance_outputs_untouched",
    ):
        if fidelity_self_checks.get(required_check) is not True:
            fail(f"external fidelity provenance packet self-test missing passing check: {required_check}")

    fidelity_draft_path = EXTERNAL / "fidelity_acceptance_draft.json"
    fidelity_draft_md_path = EXTERNAL / "fidelity_acceptance_draft.md"
    fidelity_draft_audit_path = RESULTS / "external_fidelity_acceptance_draft_audit.json"
    fidelity_draft_audit_md_path = RESULTS / "external_fidelity_acceptance_draft_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_fidelity_acceptance_draft.py",
        fidelity_draft_path,
        fidelity_draft_md_path,
        fidelity_draft_audit_path,
        fidelity_draft_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external fidelity acceptance draft artifact: {path}")
    fidelity_draft = json.loads(fidelity_draft_path.read_text(encoding="utf-8"))
    fidelity_draft_audit = json.loads(fidelity_draft_audit_path.read_text(encoding="utf-8"))
    if fidelity_draft.get("version") != "paper119_fidelity_acceptance_draft_v1":
        fail("external fidelity acceptance draft version mismatch")
    if fidelity_draft.get("not_external_evidence") is not True or fidelity_draft.get("draft_only") is not True:
        fail("external fidelity acceptance draft must be marked draft-only non-evidence")
    if fidelity_draft.get("acceptance_ready") is not False:
        fail("external fidelity acceptance draft must not claim acceptance readiness")
    if fidelity_draft.get("strict_fidelity_evidence_ready") is not False or fidelity_draft.get("strict_external_evidence_ready") is not False:
        fail("external fidelity acceptance draft must keep strict evidence readiness false")
    if fidelity_draft.get("real_acceptance_path") != "external_validation/fidelity_acceptance.json":
        fail("external fidelity acceptance draft must point to the real acceptance target path")
    if len(fidelity_draft.get("remaining_operator_inputs", []) or []) < 8:
        fail("external fidelity acceptance draft must expose remaining operator inputs")
    if not all(gate.get("status") == "draft_unaccepted" for gate in fidelity_draft.get("acceptance_gates", []) or []):
        fail("external fidelity acceptance draft gates must remain unaccepted")
    draft_hashes = fidelity_draft.get("prefilled_hashes", {}) or {}
    if len(draft_hashes.get("task_config_hashes", {}) or {}) < 4:
        fail("external fidelity acceptance draft must prefill task config hashes")
    if not draft_hashes.get("backend_module_sha256") or not draft_hashes.get("skill_library_hash"):
        fail("external fidelity acceptance draft must prefill backend and candidate skill-library hashes")
    if fidelity_draft_audit.get("version") != "external_fidelity_acceptance_draft_audit_v1":
        fail("external fidelity acceptance draft audit version mismatch")
    if fidelity_draft_audit.get("passed") is not True:
        fail("external fidelity acceptance draft audit did not pass")
    if fidelity_draft_audit.get("not_external_evidence") is not True:
        fail("external fidelity acceptance draft audit must declare non-evidence")
    if fidelity_draft_audit.get("draft_ready") is not True:
        fail("external fidelity acceptance draft audit must report draft_ready=true")
    if fidelity_draft_audit.get("acceptance_ready") is not False:
        fail("external fidelity acceptance draft audit must keep acceptance_ready=false")
    draft_checks = {check.get("name"): check.get("passed") for check in fidelity_draft_audit.get("checks", [])}
    for required_check in (
        "draft_is_non_evidence_and_fail_closed",
        "candidate_platform_prefilled_from_reference_route",
        "all_core_tasks_have_primary_env_status_and_config_hash",
        "support_asset_blockers_remain_visible",
        "fidelity_metadata_probe_prefills_timing_and_task_records",
        "candidate_hashes_prefilled",
        "remaining_operator_inputs_cover_fidelity_gate",
        "promotion_readiness_separates_machine_prefill_from_operator_signoff",
        "acceptance_gates_remain_unaccepted",
        "promotion_commands_require_real_file_manifest_and_strict_audits",
        "promotion_readiness_lists_strict_promotion_gates",
        "no_real_acceptance_or_manifest_written",
        "draft_files_written",
    ):
        if draft_checks.get(required_check) is not True:
            fail(f"external fidelity acceptance draft audit missing passing check: {required_check}")

    fidelity_materialization_path = RESULTS / "fidelity_acceptance_materialization_plan.json"
    fidelity_materialization_md_path = RESULTS / "fidelity_acceptance_materialization_plan.md"
    for path in (
        ROOT / "scripts" / "materialize_fidelity_acceptance.py",
        fidelity_materialization_path,
        fidelity_materialization_md_path,
    ):
        if not path.exists():
            fail(f"missing fidelity acceptance materialization artifact: {path}")
    fidelity_materialization = json.loads(fidelity_materialization_path.read_text(encoding="utf-8"))
    if fidelity_materialization.get("version") != "fidelity_acceptance_materialization_plan_v1":
        fail("fidelity acceptance materialization plan version mismatch")
    if fidelity_materialization.get("passed") is not True:
        fail("fidelity acceptance materialization plan did not pass")
    if fidelity_materialization.get("not_external_evidence") is not True:
        fail("fidelity acceptance materialization plan must declare non-evidence")
    if fidelity_materialization.get("write_enabled") is not False:
        fail("fidelity acceptance materialization plan must keep write_enabled=false during validation")
    if fidelity_materialization.get("acceptance_write_ready") is not False:
        fail("fidelity acceptance materialization plan must not be write-ready without operator inputs")
    if fidelity_materialization.get("strict_fidelity_evidence_ready") is not False:
        fail("fidelity acceptance materialization plan must keep strict fidelity evidence false")
    current_checkout = fidelity_materialization.get("current_checkout", {}) or {}
    if not current_checkout.get("code_commit") or len(str(current_checkout.get("code_commit"))) != 40:
        fail("fidelity acceptance materializer must record the current checkout commit")
    if not current_checkout.get("skill_library_hash") or len(str(current_checkout.get("skill_library_hash"))) != 64:
        fail("fidelity acceptance materializer must record the current skill-library hash")
    if not isinstance(current_checkout.get("clean_checkout"), bool):
        fail("fidelity acceptance materializer must report clean_checkout as a boolean")
    materializer_command = str(fidelity_materialization.get("operator_write_command", ""))
    for fragment in (
        "materialize_fidelity_acceptance.py",
        "--confirm-real-platform",
        "--confirm-independent-operator",
        "--confirm-render-backed-videos",
        "--write",
    ):
        if fragment not in materializer_command:
            fail(f"fidelity acceptance materializer command missing fragment: {fragment}")
    for forbidden_fragment in ("--confirm-real-rollout-evidence", "--confirm-manifest-declaration"):
        if forbidden_fragment in materializer_command:
            fail(f"fidelity acceptance materializer command must defer postcollection flag: {forbidden_fragment}")
    materializer_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", [])}
    for required_check in (
        "draft_exists_and_is_draft_version",
        "materialized_payload_has_contract_shape",
        "operator_text_required_before_write",
        "confirmation_flags_required_before_write",
        "write_requires_complete_operator_signoff",
        "current_checkout_hashes_recorded",
        "write_requires_clean_checkout",
        "write_requires_current_code_commit_and_skill_hash",
        "default_run_does_not_write_real_acceptance_or_manifest",
        "gates_accepted_only_after_confirmations",
        "strict_evidence_remains_external_to_materializer",
        "operator_write_command_is_guarded",
        "postcollection_evidence_deferred_until_after_collection",
    ):
        if materializer_checks.get(required_check) is not True:
            fail(f"fidelity acceptance materialization plan missing passing check: {required_check}")

    materializer_self_test_path = RESULTS / "fidelity_acceptance_materializer_self_test.json"
    materializer_self_test_md_path = RESULTS / "fidelity_acceptance_materializer_self_test.md"
    for path in (
        ROOT / "scripts" / "self_test_fidelity_acceptance_materializer.py",
        materializer_self_test_path,
        materializer_self_test_md_path,
    ):
        if not path.exists():
            fail(f"missing fidelity acceptance materializer self-test artifact: {path}")
    materializer_self_test = json.loads(materializer_self_test_path.read_text(encoding="utf-8"))
    if materializer_self_test.get("version") != "fidelity_acceptance_materializer_self_test_v1":
        fail("fidelity acceptance materializer self-test version mismatch")
    if materializer_self_test.get("passed") is not True:
        fail("fidelity acceptance materializer self-test did not pass")
    if materializer_self_test.get("not_external_evidence") is not True:
        fail("fidelity acceptance materializer self-test must declare non-evidence")
    materializer_self_checks = {check.get("name"): check.get("passed") for check in materializer_self_test.get("checks", [])}
    for required_check in (
        "matching_clean_checkout_writes_temp_acceptance",
        "stale_commit_rejected_without_temp_write",
        "mismatched_skill_hash_rejected_without_temp_write",
        "dirty_checkout_rejected_without_temp_write",
        "pycache_excluded_from_skill_library_hash",
        "real_acceptance_file_not_touched",
    ):
        if materializer_self_checks.get(required_check) is not True:
            fail(f"fidelity acceptance materializer self-test missing passing check: {required_check}")

    rollout_packet_path = EXTERNAL / "rollout_evidence_packet.json"
    rollout_packet_md_path = EXTERNAL / "rollout_evidence_packet.md"
    rollout_orders_path = EXTERNAL / "rollout_evidence_work_orders.csv"
    rollout_audit_path = RESULTS / "external_rollout_evidence_audit.json"
    rollout_audit_md_path = RESULTS / "external_rollout_evidence_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_rollout_evidence_packet.py",
        rollout_packet_path,
        rollout_packet_md_path,
        rollout_orders_path,
        rollout_audit_path,
        rollout_audit_md_path,
        ROOT / "scripts" / "self_test_external_rollout_evidence_packet.py",
        RESULTS / "external_rollout_evidence_packet_self_test.json",
        RESULTS / "external_rollout_evidence_packet_self_test.md",
    ):
        if not path.exists():
            fail(f"missing external rollout evidence packet artifact: {path}")
    rollout_packet = json.loads(rollout_packet_path.read_text(encoding="utf-8"))
    rollout_audit = json.loads(rollout_audit_path.read_text(encoding="utf-8"))
    if rollout_packet.get("version") != "external_rollout_evidence_packet_v1":
        fail("external rollout evidence packet version mismatch")
    if rollout_packet.get("not_external_evidence") is not True:
        fail("external rollout evidence packet must declare that it is not evidence")
    if rollout_packet.get("rollout_evidence_packet_ready") is not True:
        fail("external rollout evidence packet must report rollout_evidence_packet_ready=true")
    if rollout_packet.get("strict_rollout_evidence_ready") is not False:
        fail("external rollout evidence packet must not claim strict rollout evidence readiness")
    if rollout_packet.get("strict_external_evidence_ready") is not False:
        fail("external rollout evidence packet must not claim strict external evidence readiness")
    if rollout_packet.get("manifest_written") is not False:
        fail("external rollout evidence packet must not write the real manifest")
    if int(rollout_packet.get("expected_records", 0) or 0) < 1440:
        fail("external rollout evidence packet has too few expected records")
    if int(rollout_packet.get("observed_records", -1) or 0) != 0:
        fail("external rollout evidence packet must still observe zero real records before collection")
    if int(rollout_packet.get("task_count", 0) or 0) < 4:
        fail("external rollout evidence packet covers too few tasks")
    if len(rollout_packet.get("work_orders", []) or []) < 9:
        fail("external rollout evidence packet has too few work orders")
    command_text = "\n".join(rollout_packet.get("strict_acceptance_commands", []) or [])
    for fragment in (
        "build_external_rollout_evidence_packet.py",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_release_package.py --strict",
        "audit_external_evidence.py --strict",
    ):
        if fragment not in command_text:
            fail(f"external rollout evidence packet missing strict command fragment: {fragment}")
    if rollout_audit.get("version") != "external_rollout_evidence_audit_v1":
        fail("external rollout evidence audit version mismatch")
    if rollout_audit.get("passed") is not True:
        fail("external rollout evidence audit did not pass")
    if rollout_audit.get("not_external_evidence") is not True:
        fail("external rollout evidence audit must declare that it is not evidence")
    if rollout_audit.get("rollout_evidence_packet_ready") is not True:
        fail("external rollout evidence audit must report rollout_evidence_packet_ready=true")
    if rollout_audit.get("strict_rollout_evidence_ready") is not False:
        fail("external rollout evidence audit must keep strict rollout evidence false")
    if rollout_audit.get("strict_external_evidence_ready") is not False:
        fail("external rollout evidence audit must keep strict external evidence false")
    rollout_checks = {check.get("name"): check.get("passed") for check in rollout_audit.get("checks", [])}
    for required_check in (
        "packet_is_non_evidence_and_fail_closed",
        "strict_rollout_metrics_still_fail_without_manifest",
        "preflight_ready_but_observes_zero_real_records",
        "collection_plan_record_budget_ge_1440",
        "task_work_orders_cover_all_planned_tasks",
        "strict_commands_cover_collection_manifest_rollout_pairing_release_evidence",
        "strict_gate_audits_remain_fail_closed",
        "no_real_manifest_or_logs_written",
        "packet_files_written",
    ):
        if rollout_checks.get(required_check) is not True:
            fail(f"external rollout evidence audit missing passing check: {required_check}")
    rollout_self_test = json.loads((RESULTS / "external_rollout_evidence_packet_self_test.json").read_text(encoding="utf-8"))
    if rollout_self_test.get("version") != "external_rollout_evidence_packet_self_test_v1":
        fail("external rollout evidence packet self-test version mismatch")
    if rollout_self_test.get("passed") is not True:
        fail("external rollout evidence packet self-test did not pass")
    if rollout_self_test.get("not_external_evidence") is not True:
        fail("external rollout evidence packet self-test must declare that it is not evidence")
    if rollout_self_test.get("strict_rollout_evidence_ready") is not False:
        fail("external rollout evidence packet self-test must not claim strict rollout evidence")
    if rollout_self_test.get("strict_external_evidence_ready") is not False:
        fail("external rollout evidence packet self-test must not claim strict external evidence")
    for required_flag in (
        "temporary_packet_ready",
        "missing_task_work_orders_rejected",
        "premature_evidence_promotion_rejected",
        "manifest_schema_error_drift_rejected",
        "observed_record_drift_rejected",
        "collection_budget_shrink_rejected",
        "strict_command_drift_rejected",
        "downstream_gate_promotion_rejected",
        "real_output_write_rejected",
        "real_outputs_untouched",
    ):
        if rollout_self_test.get(required_flag) is not True:
            fail(f"external rollout evidence packet self-test missing true flag: {required_flag}")
    rollout_self_checks = {check.get("name"): check.get("passed") for check in rollout_self_test.get("checks", []) or []}
    for required_check in (
        "temporary_rollout_packet_ready_but_non_evidence",
        "missing_task_work_orders_rejected",
        "premature_evidence_promotion_rejected",
        "manifest_schema_error_drift_rejected",
        "observed_record_drift_rejected",
        "collection_budget_shrink_rejected",
        "strict_command_drift_rejected",
        "downstream_gate_promotion_rejected",
        "real_output_write_rejected",
        "real_rollout_packet_outputs_untouched",
    ):
        if rollout_self_checks.get(required_check) is not True:
            fail(f"external rollout evidence packet self-test missing passing check: {required_check}")

    expected_files = {
        "dataset_summary": RESULTS / "dataset_summary.csv",
        "main_cell": RESULTS / "cell_metrics.csv",
        "main_group": RESULTS / "main_group_metrics.csv",
        "seed_metric": RESULTS / "seed_metrics.csv",
        "metric": RESULTS / "metrics.csv",
        "hard_seed": RESULTS / "hard_seed_metrics.csv",
        "hard_metric": RESULTS / "hard_aggregate_metrics.csv",
        "hard_pairwise": RESULTS / "hard_pairwise_stats.csv",
        "ablation_cell": RESULTS / "ablation_cell_metrics.csv",
        "ablation_seed": RESULTS / "ablation_seed_metrics.csv",
        "ablation_metric": RESULTS / "ablation_metrics.csv",
        "stress_cell": RESULTS / "stress_sweep_cell_metrics.csv",
        "stress_seed": RESULTS / "stress_sweep_seed_metrics.csv",
        "stress_metric": RESULTS / "stress_sweep.csv",
        "fixed_risk_cell": RESULTS / "fixed_risk_cell_metrics.csv",
        "fixed_risk_seed": RESULTS / "fixed_risk_seed_metrics.csv",
        "fixed_risk_metric": RESULTS / "fixed_risk_metrics.csv",
        "fixed_risk_pairwise": RESULTS / "fixed_risk_pairwise_stats.csv",
        "failure_cases": RESULTS / "failure_cases.csv",
    }
    for key, path in expected_files.items():
        if not path.exists():
            fail(f"missing expected CSV: {path}")
        actual = count_rows(path)
        expected = int(summary["row_counts"][key])
        if actual != expected:
            fail(f"row-count mismatch for {key}: {actual} != {expected}")

    for path in expected_files.values():
        numeric_finiteness(path)

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    if r"\hypersetup{hidelinks}" not in tex:
        fail("hidden citation/link configuration missing")
    framing_terms = [
        "local world/action model for skill seams",
        "compact predictive interface between a skill library and a planner",
        "The term world/action model is used in this limited sense",
        "action-conditioned model of whether a proposed edge",
        "deliberately local form",
        "prediction-action-update loop",
    ]
    missing_framing_terms = [term for term in framing_terms if term not in tex]
    if missing_framing_terms:
        fail(f"manuscript missing natural world/action seam framing: {missing_framing_terms}")
    if "accept, repair, probe, abstain" not in tex or "choose another transition" not in tex:
        fail("manuscript missing repair/probe/abstain/transition decision framing")
    if "planner-edge updates for future planning" not in tex or "planner's edge beliefs" not in tex:
        fail("manuscript missing future-planning memory framing")
    if "updates the planner's transition belief after outcomes are observed" not in tex:
        fail("manuscript missing adaptive planner-memory update framing")
    if "\\section{Scope And Validation}" not in tex:
        fail("manuscript missing submission-facing scope boundary section")
    if "deployment-level claims" not in tex:
        fail("manuscript missing deployment-level claim boundary")
    if "skill_seam_action_model_overview_v5.pdf" not in tex:
        fail("manuscript missing skill-seam overview figure")
    if "\\subsection{Local Falsification Audit}" not in tex:
        fail("manuscript missing local falsification audit subsection")
    if "generated_local_falsification_table.tex" not in tex:
        fail("manuscript missing local falsification audit table")
    if "\\subsection{Withheld-Slice Robustness Audit}" not in tex:
        fail("manuscript missing withheld-slice robustness audit subsection")
    if "generated_holdout_robustness_table.tex" not in tex:
        fail("manuscript missing holdout robustness audit table")
    if "\\subsection{Diagnostic Mechanism Audit}" not in tex:
        fail("manuscript missing diagnostic mechanism audit subsection")
    if "generated_diagnostic_mechanism_table.tex" not in tex:
        fail("manuscript missing diagnostic mechanism audit table")
    if "diagnostic label, seam decision, and planner-edge update" not in tex:
        fail("manuscript missing diagnostic label/decision/planner-update audit language")
    if "\\subsection{Comparative Decision-Quality Audit}" not in tex:
        fail("manuscript missing comparative decision-quality audit subsection")
    if "generated_decision_quality_table.tex" not in tex:
        fail("manuscript missing comparative decision-quality audit table")
    if "accepted by v5 and abstained from by the predecessor" not in tex:
        fail("manuscript missing recovered-accept decision-quality interpretation")
    if "\\subsection{Planner-Edge Policy Audit}" not in tex:
        fail("manuscript missing planner-edge policy audit subsection")
    if "generated_planner_edge_policy_table.tex" not in tex:
        fail("manuscript missing planner-edge policy audit table")
    if "local planning frontier" not in tex or "does not use realized utility to choose the edge" not in tex:
        fail("manuscript missing planner-edge policy interpretation")
    if "\\subsection{Failure-Memory Adaptation Audit}" not in tex:
        fail("manuscript missing failure-memory adaptation audit subsection")
    if "generated_failure_memory_adaptation_table.tex" not in tex:
        fail("manuscript missing failure-memory adaptation audit table")
    if "episodes 0--3 are treated as observed memory" not in tex or "observed-to-held-out signature pairs" not in tex:
        fail("manuscript missing failure-memory observed-to-held-out interpretation")
    if "local evidence for planner-memory adaptation" not in tex:
        fail("manuscript missing bounded planner-memory adaptation interpretation")
    if "\\subsection{Predictive Calibration Audit}" not in tex:
        fail("manuscript missing predictive calibration audit subsection")
    if "generated_seam_prediction_calibration_table.tex" not in tex:
        fail("manuscript missing predictive calibration audit table")
    if "ten-bin local calibration error" not in tex or "risk-breach correlation" not in tex:
        fail("manuscript missing predictive calibration interpretation")
    if "This makes the local result harder to dismiss as cherry-picking" not in tex:
        fail("manuscript missing holdout robustness interpretation")
    if "not a substitute for external robot or high-fidelity validation" not in tex:
        fail("manuscript local falsification audit must preserve the external-validation boundary")
    if ".png}" in tex:
        fail("main manuscript should use vector PDF figures instead of PNG figures")
    abstract = tex.split("\\begin{abstract}", 1)[1].split("\\end{abstract}", 1)[0]
    forbidden_abstract_phrases = [
        "Paper 119",
        "local CPU-only",
        "STRONG\\_REVISE",
        "not ICLR-main ready",
    ]
    leaked = [phrase for phrase in forbidden_abstract_phrases if phrase in abstract]
    if leaked:
        fail(f"abstract still contains internal audit language: {leaked}")
    if "\\bibliography{references}" not in tex:
        fail("bibliography missing")
    references = (PAPER / "references.bib").read_text(encoding="utf-8")
    related_work_audit_path = RESULTS / "related_work_audit.json"
    if not related_work_audit_path.exists():
        fail("missing results/related_work_audit.json; run scripts/audit_related_work.py")
    related_work_audit = json.loads(related_work_audit_path.read_text(encoding="utf-8"))
    if related_work_audit.get("version") != "related_work_audit_v1":
        fail("related-work audit version mismatch")
    if related_work_audit.get("passed") is not True:
        fail("related-work audit did not pass")
    related_work_checks = related_work_audit.get("checks", [])
    if len(related_work_checks) < 80:
        fail("related-work audit has too few checks")
    failed_related_work_checks = [check.get("name") for check in related_work_checks if check.get("passed") is not True]
    if failed_related_work_checks:
        fail(f"related-work audit failed checks: {failed_related_work_checks[:8]}")
    required_related_work_citations = [
        "urain2021cep",
        "pane2021runtime",
        "rizwan2025ezskiros",
        "chi2023diffusionpolicy",
        "julian2020latent",
        "vijayaraghavan2025compositionality",
    ]
    missing_from_tex = [key for key in required_related_work_citations if key not in tex]
    if missing_from_tex:
        fail(f"manuscript missing required related-work citations: {missing_from_tex}")
    missing_from_bib = [key for key in required_related_work_citations if f"{{{key}," not in references]
    if missing_from_bib:
        fail(f"bibliography missing required related-work entries: {missing_from_bib}")
    matrix_path = ROOT / "docs" / "related_work_coverage_matrix.md"
    if not matrix_path.exists():
        fail("missing docs/related_work_coverage_matrix.md")
    matrix = matrix_path.read_text(encoding="utf-8")
    required_matrix_terms = [
        "Composable Energy Policies",
        "Runtime Skill Composition",
        "Diffusion Policy",
        "Language/Action Compositionality",
        "External Validation Boundary",
        "local world/action model at the skill seam",
    ]
    missing_matrix_terms = [term for term in required_matrix_terms if term not in matrix]
    if missing_matrix_terms:
        fail(f"related-work coverage matrix missing required terms: {missing_matrix_terms}")

    reference_integrity_path = RESULTS / "reference_integrity_audit.json"
    if not reference_integrity_path.exists():
        fail("missing results/reference_integrity_audit.json; run scripts/audit_reference_integrity.py")
    reference_integrity = json.loads(reference_integrity_path.read_text(encoding="utf-8"))
    if reference_integrity.get("version") != "reference_integrity_audit_v1":
        fail("reference integrity audit version mismatch")
    if reference_integrity.get("passed") is not True:
        fail("reference integrity audit did not pass")
    if int(reference_integrity.get("checked_entries", 0)) < 20:
        fail("reference integrity audit checked too few BibTeX entries")
    reference_checks = reference_integrity.get("checks", [])
    if len(reference_checks) < 50:
        fail("reference integrity audit has too few checks")
    failed_reference_checks = [check.get("name") for check in reference_checks if check.get("passed") is not True]
    if failed_reference_checks:
        fail(f"reference integrity audit failed checks: {failed_reference_checks[:8]}")
    primary_expectations = reference_integrity.get("primary_source_expectations", {})
    for key in ("chen2026costream", "liu2026simpact", "liu2026oat", "hou2026worldmodel"):
        if key not in primary_expectations:
            fail(f"reference integrity audit missing primary-source expectation for {key}")

    manuscript_readability_path = RESULTS / "manuscript_readability_audit.json"
    if not manuscript_readability_path.exists():
        fail("missing results/manuscript_readability_audit.json; run scripts/audit_manuscript_readability.py")
    manuscript_readability = json.loads(manuscript_readability_path.read_text(encoding="utf-8"))
    if manuscript_readability.get("version") != "manuscript_readability_audit_v1":
        fail("manuscript readability audit version mismatch")
    if manuscript_readability.get("passed") is not True:
        fail("manuscript readability audit did not pass")
    if manuscript_readability.get("not_external_evidence") is not True:
        fail("manuscript readability audit must declare that it is not external evidence")
    if len(manuscript_readability.get("checks", [])) < 30:
        fail("manuscript readability audit has too few checks")
    if int(manuscript_readability.get("contact_rich_count", 99)) > 2:
        fail("manuscript over-positions itself as contact-rich manipulation")
    if "manual_related_work_not_full_paper_complete" in summary.get("missing_scope_evidence", []):
        fail("summary still contains stale manual-related-work scope blocker")

    visible_contribution_path = RESULTS / "visible_contribution_audit.json"
    if not visible_contribution_path.exists():
        fail("missing results/visible_contribution_audit.json; run scripts/audit_visible_contribution.py")
    visible_contribution = json.loads(visible_contribution_path.read_text(encoding="utf-8"))
    if visible_contribution.get("version") != "visible_contribution_audit_v1":
        fail("visible contribution audit version mismatch")
    if visible_contribution.get("passed") is not True:
        fail("visible contribution audit did not pass")
    if visible_contribution.get("not_external_evidence") is not True:
        fail("visible contribution audit must declare that it is not external evidence")
    visible_checks = {check.get("name"): check.get("passed") for check in visible_contribution.get("checks", [])}
    for required_check in (
        "readiness_gap_state_visible",
        "operator_packet_no_go_visible",
        "collection_readiness_tracked_reference_route_visible",
        "operator_handoff_bundle_visible",
        "external_operator_handoff_bundle_self_test_visible",
        "external_collection_job_packet_visible",
        "external_collection_job_packet_self_test_visible",
        "external_collection_machine_bootstrap_visible",
        "external_collection_machine_bootstrap_self_test_visible",
        "external_operator_release_bundle_visible",
        "external_operator_release_bundle_self_test_visible",
        "analysis_plan_visible",
        "platform_onboarding_visible",
        "fidelity_provenance_packet_visible",
        "fidelity_provenance_packet_self_test_visible",
        "backend_integration_packet_visible",
        "backend_integration_packet_self_test_visible",
        "maniskill_reference_collection_preflight_visible",
        "external_collection_preflight_self_test_visible",
        "external_evidence_preflight_self_test_visible",
        "external_execution_readiness_self_test_visible",
        "maniskill_fidelity_metadata_probe_visible",
        "runner_backend_probe_visible",
        "external_config_materialization_self_test_visible",
        "config_manifest_packet_visible",
        "config_manifest_packet_self_test_visible",
        "rollout_evidence_packet_visible",
        "strict_video_evidence_gate_visible",
        "release_package_internal_artifact_rejection_visible",
        "precollection_manifest_draft_visible",
        "precollection_freeze_receipt_visible",
        "postcollection_evidence_seal_visible",
        "postcollection_seal_consistency_gate_visible",
        "method_implementation_packet_visible",
        "baseline_contract_self_test_visible",
        "external_method_config_materialization_visible",
        "external_method_config_materialization_self_test_visible",
        "maniskill_pilot_runtime_liveness_visible",
        "materializer_guard_visible",
        "planner_edge_policy_visible",
        "failure_memory_adaptation_visible",
        "ledger_tracks_new_visible_claims",
        "README_current_visible_contribution_terms",
        "final_audit_current_visible_contribution_terms",
        "readiness_decision_current_visible_contribution_terms",
        "readiness_audit_current_visible_contribution_terms",
        "version_log_current_visible_contribution_terms",
        "child_status_current_visible_contribution_terms",
        "outreach_current_visible_contribution_terms",
    ):
        if visible_checks.get(required_check) is not True:
            fail(f"visible contribution audit missing passing check: {required_check}")
    if not (RESULTS / "visible_contribution_audit.md").exists():
        fail("missing results/visible_contribution_audit.md")

    expected_figures = [
        "skill_seam_action_model_overview_v5",
        "energy_landscape_composition_hard_success_v5",
        "energy_landscape_composition_utility_risk_v5",
        "energy_landscape_composition_ablation_v5",
        "energy_landscape_composition_stress_sweep_v5",
        "energy_landscape_composition_fixed_risk_v5",
        "energy_landscape_composition_fixed_coverage_v5",
    ]
    for stem in expected_figures:
        for suffix in (".pdf", ".png"):
            path = FIGURES / f"{stem}{suffix}"
            if not path.exists():
                fail(f"missing expected figure: {path}")
            if path.stat().st_size < 8_000:
                fail(f"figure looks too small or empty: {path}")

    if not PAPER_PDF.exists():
        fail(f"missing rebuilt paper PDF: {PAPER_PDF}")
    paper_pages = pdf_pages(PAPER_PDF)
    if paper_pages < 25:
        fail(f"paper PDF has only {paper_pages} pages; expected at least 25")

    if not DOWNLOADS_PDF.exists():
        fail(f"missing canonical PDF: {DOWNLOADS_PDF}")
    if DESKTOP_PDF.exists():
        fail(f"desktop PDF must not exist: {DESKTOP_PDF}")
    if ROOT_PDF.exists():
        fail(f"root numbered PDF must not exist: {ROOT_PDF}")
    if CHILD_PDF.exists():
        fail(f"child numbered PDF must not exist: {CHILD_PDF}")
    pages = pdf_pages(DOWNLOADS_PDF)
    if pages < 25:
        fail(f"PDF has only {pages} pages; expected at least 25")

    paper_digest = sha256(PAPER_PDF)
    digest = sha256(DOWNLOADS_PDF)
    if paper_digest != digest:
        fail(f"canonical PDF is stale: paper/main.pdf SHA256={paper_digest}, canonical SHA256={digest}")
    size_text = f"PDF size: `{DOWNLOADS_PDF.stat().st_size}` bytes."
    public_digest_files = [
        ROOT / "README.md",
        ROOT / "child_status.md",
        DOCS / "final_audit.md",
        DOCS / "submission_readiness_audit_v5.md",
        DOCS / "paper119_terminal_audit_20260623.md",
    ]
    for path in public_digest_files:
        text = path.read_text(encoding="utf-8")
        if digest not in text:
            fail(f"public PDF SHA256 is stale or missing in {path}")
    size_text_plain = f"PDF size: {DOWNLOADS_PDF.stat().st_size} bytes"
    for path in (ROOT / "README.md", ROOT / "child_status.md", DOCS / "final_audit.md", DOCS / "submission_readiness_audit_v5.md"):
        text = path.read_text(encoding="utf-8")
        if size_text not in text and size_text_plain not in text:
            fail(f"public PDF size is stale or missing in {path}")
    print(f"Paper 119 validation passed. SHA256={digest} pages={pages}")


if __name__ == "__main__":
    main()

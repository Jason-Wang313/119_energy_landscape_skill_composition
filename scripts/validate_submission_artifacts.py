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
        "scripts\\build_external_fidelity_acceptance_draft.py",
        "scripts\\audit_external_fidelity_acceptance.py",
        "scripts\\self_test_external_fidelity_acceptance.py",
        "scripts\\build_external_blind_eval_plan.py",
        "scripts\\build_external_runbook.py",
        "scripts\\audit_external_runner_harness.py",
        "scripts\\audit_external_backend_contract.py",
        "scripts\\audit_maniskill_backend_readiness.py",
        "scripts\\audit_maniskill_reference_collection_preflight.py",
        "scripts\\build_external_backend_integration_packet.py",
        "scripts\\audit_external_collection_readiness.py",
        "scripts\\audit_external_pilot_smoke.py",
        "scripts\\build_external_pilot_smoke_packet.py",
        "scripts\\audit_maniskill_render_video_preflight.py",
        "scripts\\audit_maniskill_pilot_runtime_liveness.py",
        "scripts\\validate_external_configs.py",
        "scripts\\self_test_external_config_evidence.py",
        "scripts\\materialize_external_configs.py",
        "scripts\\build_external_config_manifest_packet.py",
        "scripts\\build_external_rollout_evidence_packet.py",
        "scripts\\build_external_baseline_contract.py",
        "scripts\\build_external_adapter_scaffolds.py",
        "scripts\\build_external_reference_adapters.py",
        "scripts\\build_external_local_dry_run.py",
        "scripts\\validate_external_adapters.py",
        "scripts\\build_external_method_implementation_packet.py",
        "scripts\\self_test_external_adapter_evidence.py",
        "scripts\\build_external_manifest.py --allow-missing",
        "scripts\\audit_external_release_package.py",
        "scripts\\self_test_external_release_package.py",
        "scripts\\audit_external_evidence_preflight.py",
        "scripts\\build_external_acquisition_packet.py",
        "scripts\\build_external_operator_packet.py",
        "scripts\\build_external_operator_handoff_bundle.py",
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

    ci_workflow = ROOT / ".github" / "workflows" / "paper119-validation.yml"
    if not ci_workflow.exists():
        fail("missing GitHub validation workflow: .github/workflows/paper119-validation.yml")
    ci_text = ci_workflow.read_text(encoding="utf-8")
    required_ci_terms = [
        "PAPER119_CANONICAL_PDF",
        "poppler-utils",
        "python -m compileall",
        "python scripts/audit_planner_edge_policy.py",
        "python scripts/audit_external_runner_harness.py",
        "python scripts/audit_external_backend_contract.py",
        "python scripts/audit_maniskill_backend_readiness.py",
        "python scripts/audit_maniskill_reference_collection_preflight.py",
        "python scripts/self_test_external_backend_contract.py",
        "python scripts/audit_external_fidelity_acceptance.py",
        "python scripts/self_test_external_fidelity_acceptance.py",
        "python scripts/self_test_external_runner_backend.py",
        "python scripts/self_test_external_collection_preflight.py",
        "python scripts/audit_external_collection_readiness.py",
        "python scripts/audit_external_pilot_smoke.py",
        "python scripts/build_external_pilot_smoke_packet.py",
        "python scripts/audit_maniskill_render_video_preflight.py",
        "python scripts/audit_maniskill_pilot_runtime_liveness.py",
        "python scripts/audit_external_evidence_preflight.py",
        "python scripts/self_test_external_config_evidence.py",
        "python scripts/self_test_external_adapter_evidence.py",
        "python scripts/materialize_external_configs.py",
        "python scripts/build_external_config_manifest_packet.py",
        "python scripts/build_external_rollout_evidence_packet.py",
        "python scripts/build_external_analysis_plan.py",
        "python scripts/probe_external_platform.py",
        "python scripts/probe_maniskill_task_bindings.py",
        "python scripts/probe_maniskill_env_smoke.py",
        "python scripts/probe_maniskill_fidelity_metadata.py",
        "python scripts/build_external_platform_onboarding.py",
        "python scripts/build_external_fidelity_provenance_packet.py",
        "python scripts/build_external_fidelity_acceptance_draft.py",
        "python scripts/build_external_backend_integration_packet.py",
        "python scripts/build_external_method_implementation_packet.py",
        "python scripts/build_external_acquisition_packet.py",
        "python scripts/build_external_operator_packet.py",
        "python scripts/build_external_operator_handoff_bundle.py",
        "python scripts/audit_external_release_package.py",
        "python scripts/self_test_external_release_package.py",
        "python scripts/audit_external_execution_readiness.py",
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
        fail("external fidelity acceptance must not be ready before a real platform acceptance file and manifest exist")
    if fidelity_acceptance.get("readiness_state") != "COLLECT_PLATFORM_PROVENANCE":
        fail("external fidelity acceptance should currently require platform provenance collection")
    if int(fidelity_acceptance.get("blocking_missing_count", 0)) < 10:
        fail("external fidelity acceptance audit should expose missing platform/provenance items")
    if not any("manifest_exists" in str(item) for item in fidelity_acceptance.get("blocking_missing", [])):
        fail("external fidelity acceptance audit should identify the missing real manifest")
    if not any(check.get("name") == "task_fidelity_covers_core_tasks" and check.get("passed") is True for check in fidelity_acceptance.get("contract_checks", [])):
        fail("external fidelity acceptance contract must cover the core external task families")
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
        "template_acceptance_fails_strict_evidence",
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
        fail("external release package self-test should reject bad local-dry-run/template/scaffold/placeholder artifacts")
    if release_package_self_test.get("missing_manifest_ready") is not False:
        fail("external release package self-test should reject a missing manifest")
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
        "no_real_manifest_written",
    ):
        if runner_checks.get(required_check) is not True:
            fail(f"external runner harness audit missing passing check: {required_check}")
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
        ROOT / "scripts" / "build_external_backend_integration_packet.py",
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
    if config_evidence_self_test.get("template_config_evidence_ready") is not False:
        fail("external config evidence self-test should reject templates as strict evidence")
    if config_evidence_self_test.get("missing_manifest_ready") is not False:
        fail("external config evidence self-test should reject a missing manifest")
    config_evidence_self_checks = {check.get("name"): check.get("passed") for check in config_evidence_self_test.get("checks", [])}
    for required_check in (
        "synthetic_strict_configs_pass",
        "synthetic_manifest_entries_cover_tasks",
        "missing_manifest_fails_strict",
        "template_configs_rejected_as_strict_evidence",
        "real_config_evidence_report_not_overwritten",
    ):
        if config_evidence_self_checks.get(required_check) is not True:
            fail(f"external config evidence self-test missing passing check: {required_check}")
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
    required_baseline_contract_files = [
        EXTERNAL / "baseline_implementation_contract.md",
        EXTERNAL / "baseline_implementation_matrix.csv",
    ]
    for path in required_baseline_contract_files:
        if not path.exists():
            fail(f"missing external baseline contract artifact: {path}")

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
    if adapter_evidence_self_test.get("version") != "external_adapter_evidence_self_test_v1":
        fail("external adapter evidence self-test version mismatch")
    if adapter_evidence_self_test.get("passed") is not True:
        fail("external adapter evidence self-test did not pass")
    if adapter_evidence_self_test.get("not_external_evidence") is not True:
        fail("external adapter evidence self-test must declare that it is not evidence")
    if adapter_evidence_self_test.get("synthetic_adapter_evidence_ready") is not True:
        fail("external adapter evidence self-test should make temporary manifest-declared adapters ready")
    if adapter_evidence_self_test.get("scaffold_adapter_evidence_ready") is not False:
        fail("external adapter evidence self-test should reject scaffolds as strict evidence")
    if adapter_evidence_self_test.get("missing_manifest_ready") is not False:
        fail("external adapter evidence self-test should reject a missing manifest")
    adapter_evidence_self_checks = {check.get("name"): check.get("passed") for check in adapter_evidence_self_test.get("checks", [])}
    for required_check in (
        "synthetic_strict_adapters_pass",
        "synthetic_manifest_entries_cover_non_oracle_methods",
        "missing_manifest_fails_strict",
        "scaffold_adapters_rejected_as_strict_evidence",
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
        RESULTS / "external_method_implementation_audit.json",
        RESULTS / "external_method_implementation_audit.md",
        ROOT / "scripts" / "build_external_method_implementation_packet.py",
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
    if method_packet.get("oracle_method") != "oracle_basin_composer":
        fail("external method implementation packet should declare the oracle as a post hoc upper bound")
    work_order_methods = {order.get("method") for order in method_packet.get("work_orders", []) or []}
    if "oracle_basin_composer" in work_order_methods:
        fail("external method implementation packet must not create an oracle work order")
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
        "work_orders_forbid_scaffolds_and_reference_adapters",
        "policy_or_config_hash_in_logs_required",
        "reference_adapter_provenance_covers_non_oracle_methods",
        "reference_adapter_hashes_recorded",
        "reference_adapters_marked_non_evidence",
        "reference_manifest_stubs_not_strict_ready",
        "common_reference_adapter_hash_shared",
        "reference_policy_hashes_match_adapter_formula",
        "strict_commands_cover_adapter_rollout_pairing_and_evidence",
        "adapter_evidence_still_missing",
        "no_real_implementation_files_created",
        "packet_files_written",
    ):
        if method_audit_checks.get(required_check) is not True:
            fail(f"external method implementation audit missing passing check: {required_check}")

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
    if count_rows(manifest_checklist_path) != int(manifest_builder_report.get("assembly_checklist_row_count", 0) or 0):
        fail("external manifest assembly checklist CSV row count does not match report")
    assembly_phases = {str(row.get("phase", "")) for row in assembly_rows if isinstance(row, dict)}
    for phase in ("platform_fidelity", "task_configs", "rollout_logs", "rollout_videos", "method_implementations", "release_artifacts", "rollout_metrics", "final_strict_gates"):
        if phase not in assembly_phases:
            fail(f"external manifest assembly checklist missing phase: {phase}")
    if not any(row.get("item") == "final_external_evidence_gate" and row.get("blocking_until_real_evidence") == "true" for row in assembly_rows if isinstance(row, dict)):
        fail("external manifest assembly checklist must keep the final evidence gate blocking")

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
    if render_preflight.get("version") != "maniskill_render_video_preflight_audit_v1":
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
    if render_preflight.get("render_video_ready") is False and not render_preflight.get("blocking_missing"):
        fail("ManiSkill render-video preflight must explain the render-video blocker when not ready")
    render_preflight_checks = {check.get("name"): check.get("passed") for check in render_preflight.get("checks", [])}
    for required_check in (
        "render_preflight_is_non_evidence",
        "quarantine_paths_are_not_official_evidence",
        "primary_envs_loaded",
        "each_probe_has_terminal_status",
        "render_readiness_recorded_without_overclaim",
        "blocking_summary_present_when_not_ready",
        "no_real_manifest_written",
    ):
        if render_preflight_checks.get(required_check) is not True:
            fail(f"ManiSkill render-video preflight audit missing passing check: {required_check}")
    pilot_runtime_path = RESULTS / "maniskill_pilot_runtime_liveness_audit.json"
    pilot_runtime_md_path = RESULTS / "maniskill_pilot_runtime_liveness_audit.md"
    for path in (
        ROOT / "scripts" / "audit_maniskill_pilot_runtime_liveness.py",
        pilot_runtime_path,
        pilot_runtime_md_path,
    ):
        if not path.exists():
            fail(f"missing ManiSkill pilot runtime liveness artifact: {path}")
    pilot_runtime = json.loads(pilot_runtime_path.read_text(encoding="utf-8"))
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
    if not (pilot_runtime_diagnostic_io or pilot_runtime_unavailable):
        fail(
            "ManiSkill pilot runtime liveness audit must either record a quarantined diagnostic "
            "non-evidence row/video or fail closed with zero rows/videos when the runtime is unavailable"
        )
    if not str(pilot_runtime.get("failure_summary", "")).strip():
        fail("ManiSkill pilot runtime liveness audit must record a failure summary")
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", [])}
    for required_check in (
        "runtime_guard_is_non_evidence",
        "quarantine_paths_are_not_official_evidence",
        "bounded_runner_subprocess_exercised",
        "timeout_or_result_recorded_as_readiness_state",
        "ready_requires_schema_valid_records_and_videos",
        "runner_io_ready_allows_only_quarantined_diagnostic_fallback",
        "diagnostic_fallback_does_not_mark_render_ready",
        "no_real_manifest_written",
    ):
        if pilot_runtime_checks.get(required_check) is not True:
            fail(f"ManiSkill pilot runtime liveness audit missing passing check: {required_check}")
    if not (ROOT / "scripts" / "self_test_external_rollout_validator.py").exists():
        fail("missing scripts/self_test_external_rollout_validator.py")
    rollout_metrics = json.loads(rollout_metrics_path.read_text(encoding="utf-8"))
    rollout_summary = rollout_metrics.get("summary", {})
    if rollout_summary.get("version") != "external_rollout_metrics_v1":
        fail("external rollout metric summary version mismatch")
    if rollout_metrics.get("passed") is not False:
        fail("external rollout validation unexpectedly passed while scope gate is false")
    schema_errors = rollout_metrics.get("schema_errors", [])
    if not any("missing manifest" in str(error) for error in schema_errors):
        fail("external rollout validation should currently fail because external_validation/manifest.json is missing")

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
    for path in (
        EXTERNAL / "platform_qualification_checklist.md",
        EXTERNAL / "fidelity_acceptance_template.json",
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
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
        EXTERNAL / "pilot_smoke_packet.json",
        EXTERNAL / "pilot_smoke_packet.md",
        EXTERNAL / "pilot_smoke_work_orders.csv",
        EXTERNAL / "method_implementation_packet.json",
        EXTERNAL / "method_implementation_packet.md",
        EXTERNAL / "method_implementation_work_orders.csv",
        EXTERNAL / "method_reference_provenance.csv",
        EXTERNAL / "manifest_assembly_checklist.csv",
        RESULTS / "external_method_implementation_audit.md",
        RESULTS / "external_config_manifest_audit.md",
        RESULTS / "external_rollout_evidence_audit.md",
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
    acquisition_checks = {entry.get("name"): entry.get("passed") for entry in acquisition.get("checks", [])}
    for required_check in (
        "all_missing_requirements_mapped",
        "collection_preflight_fail_closed",
        "config_intake_directory_tracked",
        "config_materializer_ready",
        "config_manifest_packet_ready",
        "rollout_evidence_packet_ready",
        "backend_contract_gate_ready",
        "backend_integration_packet_ready",
        "maniskill_reference_backend_audit_ready",
        "maniskill_reference_collection_preflight_ready",
        "pilot_smoke_packet_ready",
        "maniskill_render_video_preflight_recorded",
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
        "post_collection_strict_commands_cover_all_gates",
        "no_real_manifest_written",
        "operator_actions_cover_collection_blockers",
        "backend_action_runs_contract_before_readiness",
    ):
        if acquisition_checks.get(required_check) is not True:
            fail(f"external acquisition packet missing passing check: {required_check}")

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
    operator_render = operator_packet.get("render_video_preflight", {}) or {}
    if operator_render.get("not_external_evidence") is not True:
        fail("external operator packet render-video preflight must be marked non-evidence")
    if not isinstance(operator_render.get("render_video_ready"), bool):
        fail("external operator packet render-video preflight must report render_video_ready")
    if operator_render.get("strict_external_evidence_ready") is not False:
        fail("external operator packet render-video preflight must preserve strict evidence false")
    if int(operator_render.get("env_count", 0) or 0) < 1:
        fail("external operator packet render-video preflight must expose probed environment count")
    if "maniskill_render_video_preflight_audit.json" not in str(operator_render.get("audit_path", "")):
        fail("external operator packet render-video preflight must point to the audit JSON")
    if "audit_maniskill_render_video_preflight.py" not in str(operator_render.get("build_command", "")):
        fail("external operator packet render-video preflight must include rebuild command")
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
        "backend_integration_packet_included",
        "maniskill_reference_backend_included",
        "maniskill_reference_collection_preflight_included",
        "config_manifest_packet_included",
        "rollout_evidence_packet_included",
        "pilot_smoke_packet_included",
        "maniskill_render_video_preflight_included",
        "maniskill_pilot_runtime_liveness_included",
        "method_implementation_packet_included",
        "operator_actions_cover_evidence_collection",
        "post_collection_commands_cover_strict_gates",
        "file_hashes_are_recorded",
    ):
        if handoff_checks.get(required_check) is not True:
            fail(f"external operator handoff bundle missing passing check: {required_check}")

    config_materialization_path = RESULTS / "external_config_materialization_plan.json"
    if not config_materialization_path.exists():
        fail("missing results/external_config_materialization_plan.json; run scripts/materialize_external_configs.py")
    config_materialization = json.loads(config_materialization_path.read_text(encoding="utf-8"))
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

    fidelity_packet_path = EXTERNAL / "fidelity_provenance_packet.json"
    fidelity_packet_md_path = EXTERNAL / "fidelity_provenance_packet.md"
    fidelity_orders_path = EXTERNAL / "fidelity_provenance_work_orders.csv"
    fidelity_audit_path = RESULTS / "external_fidelity_provenance_audit.json"
    fidelity_audit_md_path = RESULTS / "external_fidelity_provenance_audit.md"
    for path in (
        ROOT / "scripts" / "build_external_fidelity_provenance_packet.py",
        fidelity_packet_path,
        fidelity_packet_md_path,
        fidelity_orders_path,
        fidelity_audit_path,
        fidelity_audit_md_path,
    ):
        if not path.exists():
            fail(f"missing external fidelity provenance packet artifact: {path}")
    fidelity_packet = json.loads(fidelity_packet_path.read_text(encoding="utf-8"))
    fidelity_audit = json.loads(fidelity_audit_path.read_text(encoding="utf-8"))
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
        "strict_commands_cover_fidelity_manifest_collection_and_evidence",
        "acceptance_template_not_real_evidence",
        "no_real_acceptance_or_manifest_written",
        "packet_files_written",
    ):
        if fidelity_checks.get(required_check) is not True:
            fail(f"external fidelity provenance audit missing passing check: {required_check}")

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
        "local instance of world/action modeling",
        "compact interface that predicts a skill transition's physical consequence",
        "The term world/action model is used in this limited sense",
        "action-conditioned physical interface between a skill library and a planner",
        "world/action-model view at a deliberately local scale",
        "prediction-action-update loop",
    ]
    missing_framing_terms = [term for term in framing_terms if term not in tex]
    if missing_framing_terms:
        fail(f"manuscript missing natural world/action seam framing: {missing_framing_terms}")
    if "accept, repair, probe, abstain" not in tex or "choose a different transition" not in tex:
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
        "analysis_plan_visible",
        "platform_onboarding_visible",
        "fidelity_provenance_packet_visible",
        "backend_integration_packet_visible",
        "maniskill_reference_collection_preflight_visible",
        "maniskill_fidelity_metadata_probe_visible",
        "runner_backend_probe_visible",
        "config_manifest_packet_visible",
        "rollout_evidence_packet_visible",
        "method_implementation_packet_visible",
        "maniskill_pilot_runtime_liveness_visible",
        "materializer_guard_visible",
        "planner_edge_policy_visible",
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
        DOCS / "final_audit.md",
        DOCS / "submission_readiness_audit_v5.md",
        DOCS / "paper119_terminal_audit_20260623.md",
    ]
    for path in public_digest_files:
        text = path.read_text(encoding="utf-8")
        if digest not in text:
            fail(f"public PDF SHA256 is stale or missing in {path}")
    for path in (ROOT / "README.md", DOCS / "final_audit.md", DOCS / "submission_readiness_audit_v5.md"):
        if size_text not in path.read_text(encoding="utf-8"):
            fail(f"public PDF size is stale or missing in {path}")
    print(f"Paper 119 validation passed. SHA256={digest} pages={pages}")


if __name__ == "__main__":
    main()

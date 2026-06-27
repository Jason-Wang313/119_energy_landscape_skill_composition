import csv
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
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
        "scripts\\generate_manuscript.py",
        "scripts\\audit_manuscript_numbers.py",
        "scripts\\audit_related_work.py",
        "scripts\\audit_reference_integrity.py",
        "scripts\\audit_manuscript_readability.py",
        "scripts\\build_external_collection_plan.py",
        "scripts\\build_independent_validation_route.py",
        "scripts\\audit_external_fidelity_acceptance.py",
        "scripts\\self_test_external_fidelity_acceptance.py",
        "scripts\\build_external_blind_eval_plan.py",
        "scripts\\build_external_runbook.py",
        "scripts\\audit_external_runner_harness.py",
        "scripts\\audit_external_backend_contract.py",
        "scripts\\audit_external_collection_readiness.py",
        "scripts\\validate_external_configs.py",
        "scripts\\self_test_external_config_evidence.py",
        "scripts\\materialize_external_configs.py",
        "scripts\\build_external_baseline_contract.py",
        "scripts\\build_external_adapter_scaffolds.py",
        "scripts\\build_external_reference_adapters.py",
        "scripts\\build_external_local_dry_run.py",
        "scripts\\validate_external_adapters.py",
        "scripts\\build_external_manifest.py --allow-missing",
        "scripts\\audit_external_release_package.py",
        "scripts\\audit_external_evidence_preflight.py",
        "scripts\\build_external_acquisition_packet.py",
        "scripts\\build_external_operator_packet.py",
        "scripts\\self_test_external_adapter_scaffold_guard.py",
        "scripts\\self_test_external_backend_contract.py",
        "scripts\\self_test_external_collection_preflight.py",
        "scripts\\self_test_external_runner_backend.py",
        "scripts\\self_test_external_rollout_validator.py",
        "scripts\\self_test_external_evidence_pipeline.py",
        "scripts\\validate_external_rollouts.py --write-results",
        "scripts\\audit_external_pairing_integrity.py",
        "scripts\\audit_external_evidence.py",
        "scripts\\audit_external_execution_readiness.py",
        "scripts\\audit_claim_boundary.py",
        "scripts\\audit_submission_readiness_gap.py",
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
        "python scripts/audit_external_runner_harness.py",
        "python scripts/audit_external_backend_contract.py",
        "python scripts/self_test_external_backend_contract.py",
        "python scripts/audit_external_fidelity_acceptance.py",
        "python scripts/self_test_external_fidelity_acceptance.py",
        "python scripts/self_test_external_runner_backend.py",
        "python scripts/self_test_external_collection_preflight.py",
        "python scripts/audit_external_collection_readiness.py",
        "python scripts/audit_external_evidence_preflight.py",
        "python scripts/self_test_external_config_evidence.py",
        "python scripts/materialize_external_configs.py",
        "python scripts/build_external_acquisition_packet.py",
        "python scripts/build_external_operator_packet.py",
        "python scripts/audit_external_release_package.py",
        "python scripts/audit_external_execution_readiness.py",
        "python scripts/audit_external_pairing_integrity.py",
        "python scripts/audit_submission_readiness_gap.py",
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
    if "python scripts\\audit_external_evidence.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict external evidence audit command")
    if "python scripts\\build_external_baseline_contract.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the baseline implementation contract command")
    if "python scripts\\build_external_adapter_scaffolds.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the adapter scaffold command")
    if "python scripts\\validate_external_adapters.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the adapter contract validation command")
    if "python scripts\\validate_external_adapters.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict adapter implementation validation command")
    if "python scripts\\audit_external_release_package.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict release package audit command")
    if "python scripts\\audit_external_pairing_integrity.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict pairing integrity audit command")
    if "python scripts\\validate_external_configs.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the config template validation command")
    if "python scripts\\validate_external_configs.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict config evidence validation command")
    if "python scripts\\audit_external_fidelity_acceptance.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the fidelity acceptance audit command")
    if "python scripts\\build_external_blind_eval_plan.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the blind evaluation plan command")
    if "python scripts\\build_independent_validation_route.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the independent validation route command")
    if "python scripts\\audit_external_collection_readiness.py" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the collection readiness audit command")
    if "python scripts\\audit_external_collection_readiness.py --strict" not in collection_plan.get("validation_commands", []):
        fail("external collection plan must include the strict collection readiness audit command")

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
    manifest_builder_text = (ROOT / "scripts" / "build_external_manifest.py").read_text(encoding="utf-8")
    if "CORE_CODE_ARTIFACTS" not in manifest_builder_text or "release[\"code\"]" not in manifest_builder_text:
        fail("external manifest builder must populate release_artifacts.code")

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
    if int(camera_ready.get("pages", 0)) != 29:
        fail("camera-ready design audit page count mismatch")
    if len(camera_ready.get("page_metrics", [])) != 29:
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
        "independent_validation_route_ready",
        "independent_route_not_evidence",
        "independent_route_primary_covers_tasks",
        "independent_route_closes_blockers",
        "blind_eval_plan_ready",
        "blind_eval_not_evidence",
        "blind_eval_row_budget",
        "blind_eval_no_method_leak",
        "operator_runbook_ready",
        "external_runner_harness_ready",
        "external_runner_harness_not_evidence",
        "external_runner_harness_fail_closed",
        "external_backend_contract_ready",
        "external_backend_contract_not_evidence",
        "external_backend_contract_fail_closed",
        "external_collection_readiness_audit_ready",
        "external_collection_readiness_not_evidence",
        "external_collection_readiness_fail_closed",
        "external_collection_readiness_packet_shape",
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
        "config_templates_ready",
        "config_materialization_plan_ready",
        "config_materialization_plan_not_evidence",
        "config_materialization_covers_tasks",
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
        RESULTS / "external_acquisition_packet.md",
        RESULTS / "external_operator_packet.md",
        RESULTS / "external_config_materialization_plan.md",
        RESULTS / "external_execution_readiness_audit.md",
        RESULTS / "external_fidelity_acceptance_audit.md",
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
        "backend_contract_gate_ready",
        "preflight_operator_actions_present",
        "route_independent_of_haonan",
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
    operator_actions = operator_packet.get("operator_actions", []) or []
    if len(operator_actions) < 10:
        fail("external operator packet has too few operator actions")
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
        "local world/action-modeling problem",
        "compact predictive interface between a skill library and a planner",
        "world/action model in this limited sense",
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
        "materializer_guard_visible",
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
    print(f"Paper 119 validation passed. SHA256={digest} pages={pages}")


if __name__ == "__main__":
    main()

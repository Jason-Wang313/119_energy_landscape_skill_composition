from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"
OUTREACH = ROOT / "outreach"
EXTERNAL = ROOT / "external_validation"

OUT_JSON = RESULTS / "submission_readiness_gap_audit.json"
OUT_MD = RESULTS / "submission_readiness_gap_audit.md"


def configured_path(env_name: str, default: str) -> Path:
    path = Path(os.environ.get(env_name, default))
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def add_requirement(
    rows: list[dict[str, Any]],
    *,
    requirement: str,
    status: str,
    evidence: list[str],
    blocker: str,
    submission_blocking: bool,
) -> None:
    if status not in {"satisfied", "missing", "partial", "human_polish"}:
        raise ValueError(f"unknown status: {status}")
    rows.append(
        {
            "requirement": requirement,
            "status": status,
            "evidence": evidence,
            "blocker": blocker,
            "submission_blocking": bool(submission_blocking),
        }
    )


def exists_all(paths: list[Path]) -> bool:
    return all(path.exists() for path in paths)


def passed_json(path: Path) -> bool:
    return path.exists() and read_json(path).get("passed") is True


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    requirements: list[dict[str, Any]] = []
    canonical_pdf = configured_path("PAPER119_CANONICAL_PDF", "C:/Users/wangz/Downloads/119.pdf")

    summary_path = RESULTS / "summary.json"
    summary = read_json(summary_path) if summary_path.exists() else {}
    external_audit_path = RESULTS / "external_evidence_audit.json"
    external_audit = read_json(external_audit_path) if external_audit_path.exists() else {}
    rollout_metrics_path = RESULTS / "external_rollout_metrics.json"
    rollout_metrics = read_json(rollout_metrics_path) if rollout_metrics_path.exists() else {}
    config_evidence_path = RESULTS / "external_config_evidence_audit.json"
    config_evidence = read_json(config_evidence_path) if config_evidence_path.exists() else {}
    baseline_contract_path = RESULTS / "external_baseline_contract_audit.json"
    baseline_contract = read_json(baseline_contract_path) if baseline_contract_path.exists() else {}
    adapter_contract_evidence_path = RESULTS / "external_adapter_contract_evidence_audit.json"
    adapter_contract_evidence = read_json(adapter_contract_evidence_path) if adapter_contract_evidence_path.exists() else {}
    execution_readiness_path = RESULTS / "external_execution_readiness_audit.json"
    execution_readiness = read_json(execution_readiness_path) if execution_readiness_path.exists() else {}
    fidelity_acceptance_path = RESULTS / "external_fidelity_acceptance_audit.json"
    fidelity_acceptance = read_json(fidelity_acceptance_path) if fidelity_acceptance_path.exists() else {}
    route_audit_path = RESULTS / "independent_validation_route_audit.json"
    route_audit = read_json(route_audit_path) if route_audit_path.exists() else {}
    blind_eval_path = RESULTS / "external_blind_eval_audit.json"
    blind_eval = read_json(blind_eval_path) if blind_eval_path.exists() else {}
    runner_harness_path = RESULTS / "external_runner_harness_audit.json"
    runner_harness = read_json(runner_harness_path) if runner_harness_path.exists() else {}
    collection_readiness_path = RESULTS / "external_collection_readiness_audit.json"
    collection_readiness = read_json(collection_readiness_path) if collection_readiness_path.exists() else {}
    pairing_integrity_path = RESULTS / "external_pairing_integrity_audit.json"
    pairing_integrity = read_json(pairing_integrity_path) if pairing_integrity_path.exists() else {}
    release_package_path = RESULTS / "external_release_package_audit.json"
    release_package = read_json(release_package_path) if release_package_path.exists() else {}
    acquisition_packet_path = RESULTS / "external_acquisition_packet.json"
    acquisition_packet = read_json(acquisition_packet_path) if acquisition_packet_path.exists() else {}
    presentation_path = RESULTS / "presentation_quality_audit.json"
    presentation = read_json(presentation_path) if presentation_path.exists() else {}
    figure_readability_path = RESULTS / "figure_readability_audit.json"
    figure_readability = read_json(figure_readability_path) if figure_readability_path.exists() else {}
    camera_ready_path = RESULTS / "camera_ready_design_audit.json"
    camera_ready = read_json(camera_ready_path) if camera_ready_path.exists() else {}
    manuscript_readability_path = RESULTS / "manuscript_readability_audit.json"
    manuscript_readability = read_json(manuscript_readability_path) if manuscript_readability_path.exists() else {}
    claim_path = RESULTS / "claim_boundary_audit.json"
    claim = read_json(claim_path) if claim_path.exists() else {}

    tex_path = PAPER / "main.tex"
    tex = tex_path.read_text(encoding="utf-8") if tex_path.exists() else ""
    outreach_package = DOCS / "haonan_yilun_outreach_package.md"

    core_terms = [
        "compact world/action model at the skill seam",
        "world/action model lens at a deliberately local scale",
        "prediction-action-update loop",
        "planner-edge updates for future planning",
    ]
    add_requirement(
        requirements,
        requirement="Core agenda framing: adaptive physical world/action model for skill seams",
        status="satisfied" if tex and all(term in tex for term in core_terms) else "missing",
        evidence=["paper/main.tex", "scripts/generate_manuscript.py", "scripts/validate_submission_artifacts.py"],
        blocker="" if tex and all(term in tex for term in core_terms) else "manuscript no longer contains the required world/action skill-seam framing",
        submission_blocking=True,
    )

    local_gate_ok = summary.get("local_gates_pass") is True and summary.get("terminal_decision") == "STRONG_REVISE"
    add_requirement(
        requirements,
        requirement="Defensible bounded local mechanism claim with frozen local gates",
        status="satisfied" if local_gate_ok else "missing",
        evidence=["results/summary.json", "results/hard_aggregate_metrics.csv", "paper/main.tex"],
        blocker="" if local_gate_ok else "local v5 gates or terminal decision are not in the expected bounded state",
        submission_blocking=True,
    )

    mechanism_audits = [
        RESULTS / "local_falsification_audit.json",
        RESULTS / "holdout_robustness_audit.json",
        RESULTS / "diagnostic_mechanism_audit.json",
        RESULTS / "decision_quality_audit.json",
        RESULTS / "seam_prediction_calibration_audit.json",
        RESULTS / "manuscript_number_audit.json",
    ]
    local_audits_ok = all(passed_json(path) for path in mechanism_audits)
    add_requirement(
        requirements,
        requirement="Local falsification, holdout, diagnostic, decision-quality, predictive-calibration, and number provenance audits",
        status="satisfied" if local_audits_ok else "missing",
        evidence=[str(path.relative_to(ROOT)).replace("/", "\\") for path in mechanism_audits],
        blocker="" if local_audits_ok else "one or more local mechanism/provenance audits is missing or failing",
        submission_blocking=True,
    )

    external_ready = external_audit.get("submission_ready") is True
    add_requirement(
        requirements,
        requirement="Independent real-robot or accepted high-fidelity external validation evidence",
        status="satisfied" if external_ready else "missing",
        evidence=["results/external_evidence_audit.json", "results/external_fidelity_acceptance_audit.json", "external_validation/manifest.json"],
        blocker="" if external_ready else "strict external evidence audit is NOT_READY; real manifest/log/video/checkpoint evidence and accepted robot/simulator fidelity provenance are missing",
        submission_blocking=True,
    )

    rollout_ready = rollout_metrics.get("passed") is True
    add_requirement(
        requirements,
        requirement="External rollout metrics recomputed from raw JSONL logs",
        status="satisfied" if rollout_ready else "missing",
        evidence=["results/external_rollout_metrics.json", "scripts/validate_external_rollouts.py", "external_validation/log_schema_v1.json"],
        blocker="" if rollout_ready else "strict rollout validation does not pass because external_validation/manifest.json and raw logs are missing",
        submission_blocking=True,
    )

    config_ready = config_evidence.get("passed") is True
    add_requirement(
        requirements,
        requirement="Manifest-declared real task configs replace non-evidence templates",
        status="satisfied" if config_ready else "missing",
        evidence=["results/external_config_evidence_audit.json", "external_validation/config_schema_v1.json"],
        blocker="" if config_ready else "strict config evidence audit has no real manifest-declared configs",
        submission_blocking=True,
    )

    implementations_ready = baseline_contract.get("implementations_ready") is True and adapter_contract_evidence.get("passed") is True
    implementation_blockers = []
    if baseline_contract.get("implementations_ready") is not True:
        implementation_blockers.append("baseline contract still reports manifest-declared independent non-oracle evidence as missing")
    if adapter_contract_evidence.get("passed") is not True:
        implementation_blockers.append("strict adapter contract evidence audit has no passing manifest-declared real implementations")
    add_requirement(
        requirements,
        requirement="Manifest-declared independent non-oracle baseline evidence and fairness contract",
        status="satisfied" if implementations_ready else "missing",
        evidence=[
            "results/external_baseline_contract_audit.json",
            "results/external_adapter_contract_evidence_audit.json",
            "external_validation/baseline_implementation_contract.md",
        ],
        blocker="" if implementations_ready else "; ".join(implementation_blockers),
        submission_blocking=True,
    )

    related_ok = (
        passed_json(RESULTS / "related_work_audit.json")
        and passed_json(RESULTS / "reference_integrity_audit.json")
        and manuscript_readability.get("passed") is True
    )
    add_requirement(
        requirements,
        requirement="Machine-audited related work, reference integrity, and manuscript readability",
        status="satisfied" if related_ok else "missing",
        evidence=["results/related_work_audit.json", "results/reference_integrity_audit.json", "results/manuscript_readability_audit.json", "docs/related_work_coverage_matrix.md"],
        blocker="" if related_ok else "related-work, reference-integrity, or manuscript-readability audit is missing/failing",
        submission_blocking=True,
    )

    presentation_ok = presentation.get("passed") is True and figure_readability.get("passed") is True
    add_requirement(
        requirements,
        requirement="Top-conference presentation hygiene for the compiled PDF",
        status="satisfied" if presentation_ok else "missing",
        evidence=["results/presentation_quality_audit.json", "results/figure_readability_audit.json", "paper/main.pdf", "C:/Users/wangz/Downloads/119.pdf"],
        blocker="" if presentation_ok else "presentation or figure-readability audit is missing/failing",
        submission_blocking=True,
    )

    artifact_ok = exists_all([PAPER / "main.pdf", canonical_pdf]) and passed_json(RESULTS / "claim_boundary_audit.json")
    add_requirement(
        requirements,
        requirement="Canonical artifact placement and overclaim prevention",
        status="satisfied" if artifact_ok and claim.get("passed") is True else "missing",
        evidence=["results/claim_boundary_audit.json", "paper/main.pdf", str(canonical_pdf)],
        blocker="" if artifact_ok and claim.get("passed") is True else "canonical PDF or claim-boundary audit is missing/failing",
        submission_blocking=True,
    )

    reproducible_ok = exists_all(
        [
            ROOT / "scripts" / "build_submission_artifacts.ps1",
            ROOT / "scripts" / "validate_submission_artifacts.py",
            ROOT / "scripts" / "self_test_external_evidence_pipeline.py",
            ROOT / ".github" / "workflows" / "paper119-validation.yml",
            DOCS / "reproducibility_checklist.md",
        ]
    )
    add_requirement(
        requirements,
        requirement="Single-command local reproducibility, GitHub CI, and validator self-tests",
        status="satisfied" if reproducible_ok else "missing",
        evidence=[
            "scripts/build_submission_artifacts.ps1",
            "scripts/validate_submission_artifacts.py",
            "scripts/self_test_external_rollout_validator.py",
            "scripts/self_test_external_evidence_pipeline.py",
            ".github/workflows/paper119-validation.yml",
            "docs/reproducibility_checklist.md",
        ],
        blocker="" if reproducible_ok else "rebuild, CI, or validation self-test entry point is missing",
        submission_blocking=True,
    )

    execution_packet_ok = (
        execution_readiness.get("passed") is True
        and execution_readiness.get("execution_packet_ready") is True
        and execution_readiness.get("strict_evidence_ready") is False
        and exists_all(
            [
                EXTERNAL / "platform_qualification_checklist.md",
                EXTERNAL / "fidelity_acceptance_template.json",
                EXTERNAL / "independent_validation_route.md",
                EXTERNAL / "independent_validation_route_matrix.csv",
                EXTERNAL / "blind_evaluation_protocol.md",
                EXTERNAL / "blinded_operator_sheet.csv",
                EXTERNAL / "method_alias_map.json",
                EXTERNAL / "collection_runbook.md",
                EXTERNAL / "operator_record_sheet.csv",
                EXTERNAL / "runner" / "README.md",
                EXTERNAL / "runner" / "backend_contract.py",
                EXTERNAL / "runner" / "real_collection_runner.py",
            ]
        )
        and fidelity_acceptance.get("passed") is True
        and fidelity_acceptance.get("acceptance_ready") is False
        and route_audit.get("passed") is True
        and route_audit.get("not_external_evidence") is True
        and blind_eval.get("passed") is True
        and int(blind_eval.get("row_count", 0) or 0) >= 1440
        and runner_harness.get("passed") is True
        and runner_harness.get("not_external_evidence") is True
        and runner_harness.get("actual_execution_ready") is False
        and collection_readiness.get("passed") is True
        and collection_readiness.get("collection_ready") is False
        and pairing_integrity.get("passed") is True
        and pairing_integrity.get("pairing_ready") is False
        and release_package.get("passed") is True
        and release_package.get("release_package_ready") is False
    )
    add_requirement(
        requirements,
        requirement="Independent external-validation execution packet not dependent on Haonan",
        status="satisfied" if execution_packet_ok else "missing",
        evidence=[
            "results/external_execution_readiness_audit.json",
            "results/external_fidelity_acceptance_audit.json",
            "results/independent_validation_route_audit.json",
            "results/external_blind_eval_audit.json",
            "results/external_runner_harness_audit.json",
            "results/external_collection_readiness_audit.json",
            "results/external_pairing_integrity_audit.json",
            "results/external_release_package_audit.json",
            "external_validation/platform_qualification_checklist.md",
            "external_validation/fidelity_acceptance_template.json",
            "external_validation/independent_validation_route.md",
            "external_validation/independent_validation_route_matrix.csv",
            "external_validation/blind_evaluation_protocol.md",
            "external_validation/blinded_operator_sheet.csv",
            "external_validation/collection_runbook.md",
            "external_validation/operator_record_sheet.csv",
            "external_validation/runner/real_collection_runner.py",
        ],
        blocker="" if execution_packet_ok else "external execution packet audit is missing/failing or strict evidence readiness is incorrectly claimed",
        submission_blocking=True,
    )

    release_package_ok = (
        release_package.get("passed") is True
        and release_package.get("version") == "external_release_package_audit_v1"
        and release_package.get("release_package_ready") is False
        and release_package.get("not_external_evidence") is True
        and exists_all(
            [
                ROOT / "scripts" / "audit_external_release_package.py",
                RESULTS / "external_release_package_audit.json",
                RESULTS / "external_release_package_audit.md",
                ROOT / "scripts" / "build_external_manifest.py",
            ]
        )
    )
    add_requirement(
        requirements,
        requirement="External release package hash-lock and no-local-dry-run gate",
        status="satisfied" if release_package_ok else "missing",
        evidence=[
            "scripts/audit_external_release_package.py",
            "scripts/build_external_manifest.py",
            "results/external_release_package_audit.json",
            "results/external_release_package_audit.md",
        ],
        blocker="" if release_package_ok else "external release package audit is missing/failing or incorrectly claims current evidence readiness",
        submission_blocking=True,
    )

    pairing_ok = (
        pairing_integrity.get("passed") is True
        and pairing_integrity.get("version") == "external_pairing_integrity_audit_v1"
        and pairing_integrity.get("pairing_ready") is False
        and pairing_integrity.get("not_external_evidence") is True
        and exists_all(
            [
                ROOT / "scripts" / "audit_external_pairing_integrity.py",
                RESULTS / "external_pairing_integrity_audit.json",
                RESULTS / "external_pairing_integrity_audit.md",
                EXTERNAL / "log_schema_v1.json",
            ]
        )
    )
    add_requirement(
        requirements,
        requirement="External paired-reset fairness and method-panel integrity gate",
        status="satisfied" if pairing_ok else "missing",
        evidence=[
            "scripts/audit_external_pairing_integrity.py",
            "results/external_pairing_integrity_audit.json",
            "results/external_pairing_integrity_audit.md",
            "external_validation/log_schema_v1.json",
        ],
        blocker="" if pairing_ok else "external pairing-integrity audit is missing/failing or incorrectly claims current evidence readiness",
        submission_blocking=True,
    )

    runner_ok = (
        runner_harness.get("passed") is True
        and runner_harness.get("runner_harness_ready") is True
        and runner_harness.get("actual_execution_ready") is False
        and exists_all(
            [
                EXTERNAL / "runner" / "README.md",
                EXTERNAL / "runner" / "backend_contract.py",
                EXTERNAL / "runner" / "real_collection_runner.py",
                EXTERNAL / "runner" / "backend_templates" / "maniskill_backend.py",
                EXTERNAL / "runner" / "backend_templates" / "mujoco_robosuite_backend.py",
                EXTERNAL / "runner" / "backend_templates" / "isaac_backend.py",
                EXTERNAL / "runner" / "backend_templates" / "robot_lab_backend.py",
            ]
        )
    )
    add_requirement(
        requirements,
        requirement="Fail-closed external collection runner for independent evidence capture",
        status="satisfied" if runner_ok else "missing",
        evidence=[
            "results/external_runner_harness_audit.json",
            "results/external_runner_harness_audit.md",
            "external_validation/runner/README.md",
            "external_validation/runner/backend_contract.py",
            "external_validation/runner/real_collection_runner.py",
            "external_validation/runner/backend_templates/maniskill_backend.py",
        ],
        blocker="" if runner_ok else "external runner harness is missing/failing or incorrectly claims actual execution readiness",
        submission_blocking=True,
    )

    collection_checks = {check.get("name"): check.get("passed") for check in collection_readiness.get("checks", [])}
    configs_audited = collection_checks.get("real_task_configs_ready") in {True, False}
    collection_readiness_ok = (
        collection_readiness.get("passed") is True
        and collection_readiness.get("version") == "external_collection_readiness_audit_v1"
        and collection_readiness.get("collection_ready") is False
        and collection_readiness.get("not_external_evidence") is True
        and int(collection_readiness.get("row_count", 0) or 0) >= 1440
        and collection_checks.get("operator_sheet_row_budget") is True
        and collection_checks.get("alias_map_complete") is True
        and collection_checks.get("backend_module_ready") is False
        and configs_audited
        and collection_checks.get("fidelity_acceptance_ready") is False
        and collection_checks.get("alias_unsealing_explicit") is False
        and collection_checks.get("run_id_specific") is False
        and exists_all(
            [
                ROOT / "scripts" / "audit_external_collection_readiness.py",
                RESULTS / "external_collection_readiness_audit.json",
                RESULTS / "external_collection_readiness_audit.md",
                EXTERNAL / "blinded_operator_sheet.csv",
                EXTERNAL / "method_alias_map.json",
            ]
        )
    )
    add_requirement(
        requirements,
        requirement="Actual external collection preflight gate before spending robot or simulator time",
        status="satisfied" if collection_readiness_ok else "missing",
        evidence=[
            "scripts/audit_external_collection_readiness.py",
            "results/external_collection_readiness_audit.json",
            "results/external_collection_readiness_audit.md",
            "external_validation/blinded_operator_sheet.csv",
            "external_validation/method_alias_map.json",
        ],
        blocker="" if collection_readiness_ok else "external collection preflight audit is missing/failing or incorrectly claims actual collection readiness",
        submission_blocking=True,
    )

    acquisition_checks = {check.get("name"): check.get("passed") for check in acquisition_packet.get("checks", [])}
    acquisition_packet_ok = (
        acquisition_packet.get("passed") is True
        and acquisition_packet.get("version") == "external_acquisition_packet_v1"
        and acquisition_packet.get("not_external_evidence") is True
        and acquisition_packet.get("strict_evidence_ready") is False
        and len(acquisition_packet.get("missing_requirements", []) or []) == 4
        and len(acquisition_packet.get("operator_actions", []) or []) >= 10
        and acquisition_checks.get("all_missing_requirements_mapped") is True
        and acquisition_checks.get("post_collection_strict_commands_cover_all_gates") is True
        and acquisition_checks.get("no_real_manifest_written") is True
        and exists_all(
            [
                ROOT / "scripts" / "build_external_acquisition_packet.py",
                RESULTS / "external_acquisition_packet.json",
                RESULTS / "external_acquisition_packet.md",
            ]
        )
    )
    add_requirement(
        requirements,
        requirement="Machine-audited external evidence acquisition packet for remaining blockers",
        status="satisfied" if acquisition_packet_ok else "missing",
        evidence=[
            "scripts/build_external_acquisition_packet.py",
            "results/external_acquisition_packet.json",
            "results/external_acquisition_packet.md",
        ],
        blocker="" if acquisition_packet_ok else "external acquisition packet is missing/failing or incorrectly claims evidence readiness",
        submission_blocking=True,
    )

    route_checks = {check.get("name"): check.get("passed") for check in route_audit.get("checks", [])}
    route_ok = (
        route_audit.get("passed") is True
        and route_audit.get("primary_route") == "maniskill_sapien_primary"
        and route_checks.get("primary_route_independent_of_haonan") is True
        and route_checks.get("primary_route_covers_collection_tasks") is True
        and route_checks.get("all_readiness_blockers_have_route_closure") is True
    )
    add_requirement(
        requirements,
        requirement="Concrete non-Haonan validation route with public simulator and robot options",
        status="satisfied" if route_ok else "missing",
        evidence=[
            "results/independent_validation_route_audit.json",
            "external_validation/independent_validation_route.md",
            "external_validation/independent_validation_route_matrix.csv",
        ],
        blocker="" if route_ok else "independent validation route audit is missing/failing or no longer covers the external-evidence blockers",
        submission_blocking=True,
    )

    outreach_ok = exists_all(
        [
            outreach_package,
            OUTREACH / "paper119_one_page_memo.pdf",
            OUTREACH / "paper119_four_page_preview.pdf",
        ]
    )
    add_requirement(
        requirements,
        requirement="Separate Haonan/Yilun outreach package derived from the strengthened paper",
        status="satisfied" if outreach_ok else "missing",
        evidence=[
            "docs/haonan_yilun_outreach_package.md",
            "outreach/paper119_one_page_memo.pdf",
            "outreach/paper119_four_page_preview.pdf",
            "scripts/validate_outreach_artifacts.py",
        ],
        blocker="" if outreach_ok else "outreach package or PDFs are missing",
        submission_blocking=False,
    )

    manuscript_polish_ok = manuscript_readability.get("passed") is True and not any("manual_related_work" in item for item in summary.get("missing_scope_evidence", []))
    add_requirement(
        requirements,
        requirement="Machine-audited manuscript/reference readability polish",
        status="satisfied" if manuscript_polish_ok else "human_polish",
        evidence=["results/manuscript_readability_audit.json", "results/related_work_audit.json", "results/reference_integrity_audit.json"],
        blocker="" if manuscript_polish_ok else "manuscript/reference readability audit is missing/failing or stale manual-polish blocker remains",
        submission_blocking=False,
    )

    camera_ready_polish_satisfied = (
        presentation.get("passed") is True
        and figure_readability.get("passed") is True
        and camera_ready.get("passed") is True
    )
    add_requirement(
        requirements,
        requirement="Machine-audited camera-ready figure/design pass",
        status="satisfied" if camera_ready_polish_satisfied else "human_polish",
        evidence=["results/presentation_quality_audit.json", "results/figure_readability_audit.json", "results/camera_ready_design_audit.json"],
        blocker="" if camera_ready_polish_satisfied else "presentation, figure-readability, or camera-ready page-render audit is missing/failing",
        submission_blocking=False,
    )

    satisfied = sum(1 for row in requirements if row["status"] == "satisfied")
    missing = [row for row in requirements if row["status"] == "missing"]
    human_polish = [row for row in requirements if row["status"] == "human_polish"]
    blocking_missing = [row for row in missing if row["submission_blocking"]]
    objective_complete = not blocking_missing and not human_polish
    audit_passed = not objective_complete and bool(blocking_missing)

    payload = {
        "version": "submission_readiness_gap_audit_v1",
        "passed": audit_passed,
        "objective_complete": objective_complete,
        "current_decision": summary.get("terminal_decision"),
        "iclr_main_ready": summary.get("iclr_main_ready"),
        "scope_gate_pass": summary.get("scope_gate_pass"),
        "satisfied_requirements": satisfied,
        "missing_requirements": len(missing),
        "human_polish_requirements": len(human_polish),
        "blocking_missing_requirements": len(blocking_missing),
        "requirements": requirements,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Submission Readiness Gap Audit",
        "",
        f"Passed: `{str(audit_passed).lower()}`.",
        f"Objective complete: `{str(objective_complete).lower()}`.",
        f"Satisfied requirements: `{satisfied}/{len(requirements)}`.",
        f"Blocking missing requirements: `{len(blocking_missing)}`.",
        f"Human-polish requirements: `{len(human_polish)}`.",
        "",
        "This audit is meant to prevent false completion claims. It passes only while the current package is accurately identified as incomplete for independent main-conference submission.",
        "",
        "## Requirements",
        "",
    ]
    for row in requirements:
        lines.append(f"- `{row['status']}` {row['requirement']}")
        if row["blocker"]:
            lines.append(f"  Evidence gap: {row['blocker']}")
        lines.append(f"  Evidence: {', '.join(row['evidence'])}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = "PASS" if audit_passed else "FAIL"
    print(
        f"Submission readiness gap audit: {status}; "
        f"satisfied={satisfied}/{len(requirements)}; blocking_missing={len(blocking_missing)}; human_polish={len(human_polish)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

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
        manifest_report.get("manifest_written") is False and manifest_report.get("records_loaded") == 0,
        f"manifest_written={manifest_report.get('manifest_written')!r}, records_loaded={manifest_report.get('records_loaded')!r}",
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
        EXTERNAL / "log_schema_v1.json",
        EXTERNAL / "platform_qualification_checklist.md",
        EXTERNAL / "independent_validation_route.md",
        EXTERNAL / "independent_validation_route_matrix.csv",
        EXTERNAL / "blind_evaluation_protocol.md",
        EXTERNAL / "blinded_operator_sheet.csv",
        EXTERNAL / "method_alias_map.json",
        EXTERNAL / "runner" / "README.md",
        EXTERNAL / "runner" / "backend_contract.py",
        EXTERNAL / "runner" / "real_collection_runner.py",
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
        "operator_sheet_covers_collection_plan",
        "external_runner_harness_ready",
        "external_runner_harness_not_evidence",
        "external_runner_harness_fail_closed",
        "config_templates_ready",
        "config_schema_exists",
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
        "external_evidence_preflight_ready",
        "external_evidence_preflight_not_evidence",
        "external_evidence_preflight_fail_closed",
        "external_evidence_preflight_record_budget",
        "external_evidence_preflight_operator_actions",
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
            "manifest-declared task configs with hashes",
            "manifest-declared videos",
            "manifest-declared independent non-oracle adapter implementations",
            "non-template backend module for external_validation/runner/real_collection_runner.py",
            "accepted robot/simulator fidelity acceptance file",
            "preflight-cleared external evidence package",
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

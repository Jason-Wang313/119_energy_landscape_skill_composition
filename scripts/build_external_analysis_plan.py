from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PLAN_JSON = EXTERNAL / "statistical_analysis_plan.json"
PLAN_MD = EXTERNAL / "statistical_analysis_plan.md"
AUDIT_JSON = RESULTS / "external_analysis_plan_audit.json"
AUDIT_MD = RESULTS / "external_analysis_plan_audit.md"

PRIMARY_METHOD = "barrier_certified_energy_composer_v5"
ORACLE_METHOD = "oracle_basin_composer"
CONFIDENCE_LEVEL = 0.95
BOOTSTRAP_REPLICATES = 1000
BOOTSTRAP_SEED = 119


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_plan(schema: dict[str, Any], collection_plan: dict[str, Any]) -> dict[str, Any]:
    thresholds = dict(schema.get("primary_thresholds", {}) or {})
    paired_key = list(schema.get("paired_comparison_key", []) or [])
    required_fields = sorted((schema.get("required_fields", {}) or {}).keys())
    methods = list(collection_plan.get("methods", []) or [])
    task_families = [task.get("task_family") for task in collection_plan.get("tasks", []) or []]

    return {
        "version": "external_statistical_analysis_plan_v1",
        "not_external_evidence": True,
        "analysis_locked_before_collection": True,
        "purpose": "Pre-register external validation hypotheses, metrics, thresholds, exclusions, and reporting before any independent rollouts are collected.",
        "source_schema": "external_validation/log_schema_v1.json",
        "source_collection_plan": "results/external_collection_plan.json",
        "primary_method": schema.get("primary_method", PRIMARY_METHOD),
        "oracle_method": ORACLE_METHOD,
        "oracle_role": "post_hoc_upper_bound_only_not_a_deployable_baseline",
        "strongest_external_baseline_rule": schema.get(
            "strongest_external_baseline_rule",
            "Choose the non-oracle method with highest mean success, breaking ties by mean utility.",
        ),
        "task_families": task_families,
        "method_count": len(methods),
        "planned_records": collection_plan.get("total_required_records"),
        "paired_comparison_key": paired_key,
        "required_log_fields": required_fields,
        "primary_thresholds": thresholds,
        "statistical_confidence_gate": {
            "version": "external_statistical_confidence_v1",
            "confidence_level": CONFIDENCE_LEVEL,
            "bootstrap_replicates": BOOTSTRAP_REPLICATES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "rule": (
                "For external_success_margin, external_utility_margin, paired_win_rate, and "
                "fixed_risk_coverage, the 95% bootstrap lower confidence bound must meet or exceed "
                "the predeclared threshold. For fixed_risk_breach, the 95% bootstrap upper confidence "
                "bound must be at or below the threshold. Positive task-family coverage remains a "
                "predeclared count gate."
            ),
        },
        "primary_hypotheses": [
            {
                "id": "H1_success_margin",
                "metric": "external_success_margin",
                "direction": "greater_or_equal",
                "threshold": thresholds.get("external_success_margin"),
                "claim_supported_if_passed": "The seam model improves external task success over the strongest non-oracle baseline.",
            },
            {
                "id": "H2_utility_margin",
                "metric": "external_utility_margin",
                "direction": "greater_or_equal",
                "threshold": thresholds.get("external_utility_margin"),
                "claim_supported_if_passed": "The seam model improves external composition utility over the strongest non-oracle baseline.",
            },
            {
                "id": "H3_paired_win_rate",
                "metric": "paired_win_rate",
                "direction": "greater_or_equal",
                "threshold": thresholds.get("paired_win_rate"),
                "claim_supported_if_passed": "The gain is visible across paired resets rather than only in aggregate means.",
            },
            {
                "id": "H4_fixed_risk_coverage",
                "metric": "fixed_risk_coverage",
                "direction": "greater_or_equal",
                "threshold": thresholds.get("fixed_risk_coverage"),
                "claim_supported_if_passed": "The fixed-risk gate preserves enough usable coverage to be operationally meaningful.",
            },
            {
                "id": "H5_fixed_risk_breach",
                "metric": "fixed_risk_breach",
                "direction": "less_or_equal",
                "threshold": thresholds.get("fixed_risk_breach"),
                "claim_supported_if_passed": "Accepted seams remain below the predeclared realized-breach budget.",
            },
            {
                "id": "H6_task_family_coverage",
                "metric": "positive_task_families",
                "direction": "greater_or_equal",
                "threshold": thresholds.get("positive_task_families"),
                "claim_supported_if_passed": "The external improvement is not confined to one task family.",
            },
        ],
        "decision_rule": {
            "external_mechanism_claim_passes": "all_primary_hypotheses_pass_all_confidence_gates_pass_and_all_strict_evidence_gates_pass",
            "strict_gates": [
                "python scripts\\audit_external_release_package.py --strict",
                "python scripts\\audit_external_fidelity_acceptance.py --strict",
                "python scripts\\validate_external_configs.py --strict",
                "python scripts\\validate_external_adapters.py --strict",
                "python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
                "python scripts\\audit_external_pairing_integrity.py --strict",
                "python scripts\\audit_external_evidence.py --strict",
            ],
        },
        "exclusion_policy": {
            "unit": "paired_reset_method_panel",
            "allowed_before_unblinding": [
                "platform qualification failure before collection",
                "operator safety stop documented before outcome inspection",
                "corrupt JSONL line that fails schema validation",
                "missing or hash-mismatched video/config/checkpoint artifact",
                "incomplete paired method panel detected by strict pairing audit",
            ],
            "forbidden": [
                "dropping only the proposed method or only a weak baseline from a paired panel",
                "dropping failures after viewing method identity or outcome",
                "changing task families, methods, thresholds, or risk budget after collection starts",
                "using local dry-run records, template configs, scaffold adapters, placeholder videos, or hand-entered metrics as evidence",
            ],
        },
        "unblinding_policy": {
            "method_aliases_remain_sealed_until": [
                "backend module is qualified",
                "task configs are materialized and hash-locked",
                "fidelity acceptance is complete",
                "run id is specific and immutable",
                "operator sheet is frozen",
            ],
            "analysis_after_unblinding": "run only the predeclared scripts and thresholds above; secondary plots are descriptive unless added to a new preregistered plan before collection.",
        },
        "required_reporting": [
            "external_success_margin",
            "external_utility_margin",
            "paired_win_rate",
            "fixed_risk_coverage",
            "fixed_risk_breach",
            "positive_task_families",
            "statistical_confidence",
            "95% confidence intervals for primary external metrics",
            "strongest_external_baseline",
            "per-task success margins",
            "strict gate outputs",
            "all exclusions with reasons and timestamps",
            "oracle gap as post hoc upper bound",
        ],
        "secondary_descriptive_outputs": [
            "seam failure rate",
            "barrier violation rate",
            "damage or intervention rate",
            "decision distribution",
            "failure diagnosis distribution",
            "calibration plots",
            "representative success, repair, abstain, and failure videos",
        ],
    }


def audit_plan(plan: dict[str, Any], schema: dict[str, Any], collection_plan: dict[str, Any]) -> dict[str, Any]:
    thresholds = schema.get("primary_thresholds", {}) or {}
    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "plan_is_non_evidence_and_locked",
        plan.get("not_external_evidence") is True and plan.get("analysis_locked_before_collection") is True,
        f"not_external_evidence={plan.get('not_external_evidence')!r}, locked={plan.get('analysis_locked_before_collection')!r}",
    )
    add_check(
        checks,
        "primary_method_matches_schema",
        plan.get("primary_method") == schema.get("primary_method") == PRIMARY_METHOD,
        f"plan={plan.get('primary_method')!r}, schema={schema.get('primary_method')!r}",
    )
    add_check(
        checks,
        "thresholds_match_log_schema",
        plan.get("primary_thresholds") == thresholds,
        f"plan={plan.get('primary_thresholds')!r}, schema={thresholds!r}",
    )
    hypotheses = plan.get("primary_hypotheses", []) or []
    hypothesis_metrics = {hypothesis.get("metric") for hypothesis in hypotheses if isinstance(hypothesis, dict)}
    required_metrics = {
        "external_success_margin",
        "external_utility_margin",
        "paired_win_rate",
        "fixed_risk_coverage",
        "fixed_risk_breach",
        "positive_task_families",
    }
    add_check(
        checks,
        "primary_hypotheses_cover_all_strict_thresholds",
        required_metrics.issubset(hypothesis_metrics),
        f"missing={sorted(required_metrics - hypothesis_metrics)}",
    )
    confidence_gate = plan.get("statistical_confidence_gate", {}) or {}
    add_check(
        checks,
        "confidence_gate_is_predeclared",
        confidence_gate.get("version") == "external_statistical_confidence_v1"
        and confidence_gate.get("confidence_level") == CONFIDENCE_LEVEL
        and int(confidence_gate.get("bootstrap_replicates", 0) or 0) >= BOOTSTRAP_REPLICATES
        and "lower confidence bound" in str(confidence_gate.get("rule", ""))
        and "upper confidence" in str(confidence_gate.get("rule", "")),
        f"confidence_gate={confidence_gate}",
    )
    add_check(
        checks,
        "paired_key_matches_schema",
        plan.get("paired_comparison_key") == schema.get("paired_comparison_key"),
        f"plan={plan.get('paired_comparison_key')!r}, schema={schema.get('paired_comparison_key')!r}",
    )
    add_check(
        checks,
        "collection_plan_record_budget_referenced",
        int(plan.get("planned_records", 0) or 0) >= 1440
        and plan.get("planned_records") == collection_plan.get("total_required_records"),
        f"planned={plan.get('planned_records')!r}, collection={collection_plan.get('total_required_records')!r}",
    )
    strict_gates = plan.get("decision_rule", {}).get("strict_gates", []) or []
    add_check(
        checks,
        "decision_rule_requires_strict_external_gates",
        all(
            any(fragment in command for command in strict_gates)
            for fragment in (
                "audit_external_release_package.py --strict",
                "audit_external_fidelity_acceptance.py --strict",
                "validate_external_configs.py --strict",
                "validate_external_adapters.py --strict",
                "validate_external_rollouts.py",
                "audit_external_pairing_integrity.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        f"strict_gates={strict_gates}",
    )
    exclusions = plan.get("exclusion_policy", {})
    forbidden = " ".join(exclusions.get("forbidden", []) or [])
    allowed = " ".join(exclusions.get("allowed_before_unblinding", []) or [])
    add_check(
        checks,
        "exclusion_policy_blocks_cherry_picking",
        exclusions.get("unit") == "paired_reset_method_panel"
        and "dropping only the proposed method" in forbidden
        and "after viewing method identity" in forbidden
        and "incomplete paired method panel" in allowed,
        f"unit={exclusions.get('unit')!r}",
    )
    unblinding = plan.get("unblinding_policy", {})
    add_check(
        checks,
        "unblinding_policy_preserves_blind_eval",
        "operator sheet is frozen" in (unblinding.get("method_aliases_remain_sealed_until", []) or [])
        and "predeclared scripts and thresholds" in str(unblinding.get("analysis_after_unblinding", "")),
        f"unblinding={unblinding}",
    )
    reporting = set(plan.get("required_reporting", []) or [])
    add_check(
        checks,
        "required_reporting_covers_primary_and_audit_outputs",
        {
            "external_success_margin",
            "external_utility_margin",
            "paired_win_rate",
            "fixed_risk_coverage",
            "fixed_risk_breach",
            "positive_task_families",
            "statistical_confidence",
            "95% confidence intervals for primary external metrics",
            "strict gate outputs",
            "all exclusions with reasons and timestamps",
        }.issubset(reporting),
        f"missing={sorted({'external_success_margin', 'external_utility_margin', 'paired_win_rate', 'fixed_risk_coverage', 'fixed_risk_breach', 'positive_task_families', 'statistical_confidence', '95% confidence intervals for primary external metrics', 'strict gate outputs', 'all exclusions with reasons and timestamps'} - reporting)}",
    )
    passed = all(check["passed"] for check in checks)
    return {
        "version": "external_analysis_plan_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "analysis_plan_ready": passed,
        "strict_evidence_ready": False,
        "source_plan": rel(PLAN_JSON),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_plan_md(plan: dict[str, Any]) -> None:
    lines = [
        "# External Statistical Analysis Plan",
        "",
        "Not evidence: `true`.",
        f"Analysis locked before collection: `{str(plan['analysis_locked_before_collection']).lower()}`.",
        f"Primary method: `{plan['primary_method']}`.",
        f"Planned records: `{plan['planned_records']}`.",
        "",
        "This plan pre-registers how the independent external validation logs will be analyzed. It does not create robot or high-fidelity simulator evidence.",
        "",
        "## Primary Hypotheses",
        "",
    ]
    for hypothesis in plan["primary_hypotheses"]:
        lines.append(
            f"- `{hypothesis['id']}`: `{hypothesis['metric']}` "
            f"{hypothesis['direction']} `{hypothesis['threshold']}`."
        )
    gate = plan["statistical_confidence_gate"]
    lines.extend(
        [
            "",
            "## Statistical Confidence Gate",
            "",
            f"Confidence level: `{gate['confidence_level']}`.",
            f"Bootstrap replicates: `{gate['bootstrap_replicates']}`.",
            f"Bootstrap seed: `{gate['bootstrap_seed']}`.",
            "",
            gate["rule"],
        ]
    )
    lines.extend(["", "## Strict Gates", ""])
    for command in plan["decision_rule"]["strict_gates"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Exclusion Policy", ""])
    lines.append(f"Unit: `{plan['exclusion_policy']['unit']}`.")
    lines.append("")
    lines.append("Allowed before unblinding:")
    for item in plan["exclusion_policy"]["allowed_before_unblinding"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Forbidden:")
    for item in plan["exclusion_policy"]["forbidden"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Required Reporting", ""])
    for item in plan["required_reporting"]:
        lines.append(f"- {item}")
    PLAN_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Analysis Plan Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Analysis plan ready: `{str(audit['analysis_plan_ready']).lower()}`.",
        f"Strict evidence ready: `{str(audit['strict_evidence_ready']).lower()}`.",
        "",
        "This audit checks that the external statistical analysis plan is locked, threshold-consistent with the rollout schema, and resistant to post-hoc cherry-picking. It is not external validation evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    schema = read_json(EXTERNAL / "log_schema_v1.json")
    collection_plan = read_json(RESULTS / "external_collection_plan.json")
    plan = build_plan(schema, collection_plan)
    audit = audit_plan(plan, schema, collection_plan)

    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    PLAN_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan_md(plan)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External analysis plan: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"planned_records={plan['planned_records']}; not_evidence=true"
    )
    print(f"Wrote {PLAN_JSON}")
    print(f"Wrote {PLAN_MD}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"

OUT_MD = DOCS / "reviewer_response_packet.md"
OUT_JSON = RESULTS / "reviewer_response_packet_audit.json"
OUT_AUDIT_MD = RESULTS / "reviewer_response_packet_audit.md"

VERSION = "reviewer_response_packet_v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def evidence_paths(entries: list[dict[str, Any]]) -> list[Path]:
    paths: list[Path] = []
    for entry in entries:
        for item in entry["evidence"]:
            paths.append(ROOT / item)
    return paths


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    summary = read_json(RESULTS / "summary.json")
    gap = read_json(RESULTS / "submission_readiness_gap_audit.json")
    falsification = read_json(RESULTS / "local_falsification_audit.json")
    decision = read_json(RESULTS / "decision_quality_audit.json")
    planner = read_json(RESULTS / "planner_edge_policy_audit.json")
    failure_memory = read_json(RESULTS / "failure_memory_adaptation_audit.json")
    calibration = read_json(RESULTS / "seam_prediction_calibration_audit.json")
    diagnostic = read_json(RESULTS / "diagnostic_mechanism_audit.json")

    metrics = summary["metrics"]
    falsification_metrics = falsification["metrics"]
    decision_metrics = decision["metrics"]
    planner_metrics = planner["metrics"]
    failure_memory_metrics = failure_memory["proposed_metrics"]
    failure_memory_comparison = failure_memory["comparison"]
    calibration_metrics = calibration["derived"]
    diagnostic_metrics = diagnostic["metrics"]

    entries: list[dict[str, Any]] = [
        {
            "id": "world_action_not_thresholds",
            "reviewer_objection": "This is not a world/action model; it is just thresholds over controller diagnostics.",
            "response": (
                "The claim is deliberately local: the seam state is the local world, and the action is the planner-facing choice "
                "to accept, repair, probe, abstain, or choose another transition. The packet should answer this by pointing to "
                "the prediction-diagnosis-decision-update loop, not by claiming a full simulator."
            ),
            "evidence": [
                "paper/main.tex",
                "results/diagnostic_mechanism_audit.json",
                "results/planner_edge_policy_audit.json",
            ],
            "local_fact": (
                f"The diagnostic audit reports {int(diagnostic_metrics['label_mismatches'])} label-rule mismatches, "
                f"{int(diagnostic_metrics['decision_mismatches'])} decision-rule mismatches, and "
                f"{int(diagnostic_metrics['update_mismatches'])} planner-update mismatches over local rows."
            ),
            "allowed_claim": "A bounded local world/action interface can make skill seams more decision-relevant.",
            "remaining_gate": "External logs must show the same prediction-diagnosis-decision-update fields on real or accepted high-fidelity runs.",
            "outreach_use": "Use this as the core identity sentence; do not pitch it as a low-level controller.",
        },
        {
            "id": "novelty_vs_prior_composer",
            "reviewer_objection": "The paper may be only the previous energy composer with a new name.",
            "response": (
                "The prior proposed composer is retained as the strongest non-oracle predecessor, and all gains are measured "
                "against it rather than against an easy baseline."
            ),
            "evidence": ["results/summary.json", "paper/main.tex", "results/manuscript_number_audit.json"],
            "local_fact": (
                f"Against {summary['strongest_non_oracle']}, v5 improves hard success by {fmt(metrics['hard_success_margin'])} "
                f"and hard utility by {fmt(metrics['hard_utility_margin'])}, with "
                f"{int(metrics['paired_hard_utility_wins'])}/10 paired hard-utility wins."
            ),
            "allowed_claim": "The local improvement is over the prior proposed method, not only over weak baselines.",
            "remaining_gate": "External evidence must re-run the prior method and v5 under the same skill library and paired resets.",
            "outreach_use": "Mention this only after stating the core seam-model idea.",
        },
        {
            "id": "synthetic_local_evidence",
            "reviewer_objection": "The evidence is local/synthetic and may not transfer to hardware.",
            "response": (
                "Agree. The correct answer is not to deny the weakness; it is to show the exact external evidence gate and "
                "the independent operator packet already prepared to close it."
            ),
            "evidence": [
                "results/submission_readiness_gap_audit.json",
                "results/external_evidence_audit.json",
                "results/external_operator_packet.md",
                "results/external_operator_handoff_bundle.md",
            ],
            "local_fact": (
                f"The readiness audit reports {gap['satisfied_requirements']}/"
                f"{gap['satisfied_requirements'] + gap['missing_requirements']} requirements satisfied and "
                f"{gap['blocking_missing_requirements']} blocking external gaps."
            ),
            "allowed_claim": "The current paper is locally strong but not ready for deployment-level claims or final main-conference submission claims.",
            "remaining_gate": (
                "Real robot or accepted high-fidelity manifest/log/video/checkpoint evidence must pass strict audits. "
                "The pilot liveness layer is non-evidence: it records timeout progress and whether a diagnostic sidecar "
                "rejected before JSONL write was stopped by the official video guard before any official row can be written."
            ),
            "outreach_use": "Do not ask Haonan to supply the missing proof; ask for fit/falsification advice and possible collaboration.",
        },
        {
            "id": "abstention_gaming",
            "reviewer_objection": "The method wins by abstaining from hard cases.",
            "response": (
                "The response is coverage plus breach, not success alone. The decision-quality audit also checks recovered accepts "
                "that the prior composer abstained from."
            ),
            "evidence": [
                "results/decision_quality_audit.json",
                "results/local_falsification_audit.json",
                "paper/generated_decision_quality_table.tex",
            ],
            "local_fact": (
                f"V5 accepts {fmt(decision_metrics['proposed_accept_coverage'])} of hard seams versus "
                f"{fmt(decision_metrics['baseline_accept_coverage'])} for the predecessor, and recovers "
                f"{int(decision_metrics['recovered_accept_pairs']):,} accept pairs with utility "
                f"+{fmt(decision_metrics['recovered_accept_utility_delta'])}."
            ),
            "allowed_claim": "The local seam layer preserves useful accepted transitions while bounding accepted-seam breach.",
            "remaining_gate": "External rollouts must recompute coverage and breach from raw JSONL records.",
            "outreach_use": "This is a strong one-sentence defense if someone thinks abstention is the whole trick.",
        },
        {
            "id": "search_cost_gaming",
            "reviewer_objection": "The method wins by spending more compute or search at the seam.",
            "response": "The falsification audit explicitly checks composition cost and cost-normalized utility.",
            "evidence": ["results/local_falsification_audit.json", "results/summary.json", "paper/main.tex"],
            "local_fact": (
                f"Composition cost changes by {fmt(falsification_metrics['composition_cost_delta'])}, while cost-normalized utility "
                f"improves by {fmt(falsification_metrics['cost_normalized_utility_margin'])}."
            ),
            "allowed_claim": "The local gains are not explained by higher recorded composition cost.",
            "remaining_gate": "External logs must include wall-clock/runtime/probe/repair costs and recompute utility from raw records.",
            "outreach_use": "Use only as a supporting detail, not the headline.",
        },
        {
            "id": "decorative_energy_terms",
            "reviewer_objection": "Energy terms may be decorative; any tuned score might work.",
            "response": "The ablation suite removes terminal sampling, contact guard, repair, descent, barrier, basin, fixed-risk, and calibration components.",
            "evidence": ["results/summary.json", "results/ablation_metrics.csv", "paper/generated_ablation_table.tex"],
            "local_fact": (
                f"The best removed-component ablation, {summary['best_ablation']}, trails the full method by "
                f"{fmt(metrics['ablation_success_margin'])} success and {fmt(metrics['ablation_utility_margin'])} utility."
            ),
            "allowed_claim": "The local mechanism depends on the full seam-certification stack, not only a generic energy score.",
            "remaining_gate": "External ablations must be replayed with identical task configs, skill libraries, and method panels.",
            "outreach_use": "Good for technical follow-up, not the first email paragraph.",
        },
        {
            "id": "baseline_fairness",
            "reviewer_objection": "Baseline wrappers may be unfair or not independently implemented.",
            "response": (
                "The local paper names the prior method and multiple baselines, but the strict external baseline contract still "
                "keeps independent non-oracle evidence as missing."
            ),
            "evidence": [
                "results/external_baseline_contract_audit.json",
                "results/external_adapter_contract_evidence_audit.json",
                "external_validation/baseline_implementation_contract.md",
            ],
            "local_fact": "The strict external baseline and adapter-evidence audits remain fail-closed until manifest-declared real implementations exist.",
            "allowed_claim": "Local baselines are broad and audited; independent external baseline evidence is still required.",
            "remaining_gate": "Manifest-declared independent non-oracle implementations and adapter evidence must pass strict validation.",
            "outreach_use": "This protects credibility; acknowledge it before a reviewer has to say it.",
        },
        {
            "id": "planner_update_claim",
            "reviewer_objection": "The paper says future planning improves, but the evidence may only be one-step classification.",
            "response": (
                "Use the planner-edge policy audit: it chooses future candidate edges using exported planner-edge updates first, "
                "then predicted risk, basin alignment, descent, and cost without using realized utility to choose. The failure-memory "
                "adaptation audit separately checks whether observed seam memories predict held-out outcomes for the same diagnostic/update signature."
            ),
            "evidence": [
                "results/planner_edge_policy_audit.json",
                "results/planner_edge_policy_audit.md",
                "results/failure_memory_adaptation_audit.json",
                "results/failure_memory_adaptation_audit.md",
                "paper/generated_planner_edge_policy_table.tex",
                "paper/generated_failure_memory_adaptation_table.tex",
            ],
            "local_fact": (
                f"Across {int(planner_metrics['frontier_count']):,} local planning frontiers, selected-edge utility improves by "
                f"{fmt(planner_metrics['selected_utility_delta'])}, success by {fmt(planner_metrics['selected_success_delta'])}, "
                f"and realized breach by {fmt(planner_metrics['selected_realized_breach_delta'])}. The failure-memory audit adds "
                f"{int(failure_memory_metrics['memory_signature_count']):,} observed-to-held-out signature pairs with breach correlation "
                f"{fmt(failure_memory_metrics['memory_breach_future_breach_correlation'])}, and v5 lowers high-memory-risk future breach by "
                f"{fmt(-failure_memory_comparison['high_memory_future_breach_delta'])} versus the predecessor."
            ),
            "allowed_claim": "Local planner-edge updates change future transition selection under a fixed audit policy.",
            "remaining_gate": "External runs must log edge updates and replay planner-frontier selection from raw records.",
            "outreach_use": "This is one of the best bridges to Yilun's planning/world-model interests.",
        },
        {
            "id": "calibration_transfer",
            "reviewer_objection": "Predicted seam risk may be calibrated locally but fail after transfer.",
            "response": "The local calibration is strong, but transfer remains an external-evidence question.",
            "evidence": ["results/seam_prediction_calibration_audit.json", "paper/generated_seam_prediction_calibration_table.tex", "results/external_rollout_evidence_audit.json"],
            "local_fact": (
                f"Local ten-bin calibration error is {fmt(calibration['proposed_metrics']['expected_calibration_error_10'])}, "
                f"risk-breach correlation is {fmt(calibration['proposed_metrics']['risk_breach_correlation'])}, and "
                f"the high-low decile breach gap is {fmt(calibration_metrics['highest_lowest_decile_breach_delta'])}."
            ),
            "allowed_claim": "Predicted seam risk is locally predictive and decision-relevant.",
            "remaining_gate": "External raw logs must recompute calibration error, risk deciles, and fixed-risk breach.",
            "outreach_use": "Frame this as a validation question Haonan could help critique, not a solved transfer result.",
        },
        {
            "id": "contact_rich_scope",
            "reviewer_objection": "The work is really contact-rich manipulation, not the broader Jason agenda.",
            "response": (
                "Contact-rich cases are a stress test because they make action consequences visible. The identity remains "
                "adaptive physical world/action modeling at skill seams."
            ),
            "evidence": ["paper/main.tex", "results/manuscript_readability_audit.json", "docs/related_work_coverage_matrix.md"],
            "local_fact": "The manuscript readability audit passes the contact-as-testbed positioning and keeps contact-rich phrase count bounded.",
            "allowed_claim": "Contact-rich manipulation is a proving ground, not the core research identity.",
            "remaining_gate": "Broader external tasks should include non-contact and mixed seam regimes when evidence collection expands.",
            "outreach_use": "Use this to stay aligned with your agenda when writing to Haonan.",
        },
        {
            "id": "haonan_yilun_fit",
            "reviewer_objection": "Why would Haonan or Yilun care about this specific paper?",
            "response": (
                "The overlap is behavior/action composition plus predictive physical models for planning. The pitch should be one paper, "
                "not many papers: present Paper 119 as a reliability layer for composed behaviors."
            ),
            "evidence": ["docs/haonan_yilun_outreach_package.md", "paper/main.tex", "docs/related_work_coverage_matrix.md"],
            "local_fact": "The outreach package already frames Paper 119 as a seam critic for behavior-composition systems.",
            "allowed_claim": "The paper is a plausible bridge to behavior composition and world/action-model planning.",
            "remaining_gate": "A collaborator still needs to see a credible external validation path before treating it as submission-ready.",
            "outreach_use": "Mention one paper and one validation ask; do not dilute the email by listing many papers.",
        },
        {
            "id": "submission_readiness",
            "reviewer_objection": "The paper is not submission-ready without real robot or accepted high-fidelity validation.",
            "response": "Agree. The correct current decision is STRONG_REVISE; the packet exists to make the remaining proof layer concrete.",
            "evidence": ["results/submission_readiness_gap_audit.json", "docs/submission_readiness_audit_v5.md", "results/external_acquisition_packet.md"],
            "local_fact": (
                f"Readiness remains {gap['satisfied_requirements']}/"
                f"{gap['satisfied_requirements'] + gap['missing_requirements']} with {gap['blocking_missing_requirements']} blocking external gaps. "
                "The official video write guard rejects diagnostic fallback, non-MP4-like, undersized, out-of-dir, or unexpected "
                "videos, and the official JSONL write guard rejects schema-invalid rollout records before the actual collection "
                "runner appends them. atomic official evidence promotion preserves prior official videos/logs if the selected batch fails, "
                "but these remain tooling hardening rather than external validation."
            ),
            "allowed_claim": "The local package is stronger and more reviewer-ready, but not independently complete.",
            "remaining_gate": "Close all four blocking external requirements before claiming independent main-conference readiness.",
            "outreach_use": "This is the honesty line for the email and for any rebuttal.",
        },
    ]

    evidence_missing = sorted({rel(path) for path in evidence_paths(entries) if not path.exists()})
    required_ids = {
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
    ids = {entry["id"] for entry in entries}
    missing_ids = sorted(required_ids - ids)
    forbidden_patterns = [
        r"\bICLR[- ]?main ready:\s*yes\b",
        r"\bdeployment[- ]ready\b",
        r"\bhardware[- ]safe\b",
        r"\breal[- ]robot validation passed\b",
        r"\bhigh[- ]fidelity validation passed\b",
        r"\bexternal evidence passed\b",
    ]

    lines = [
        "# Reviewer Response Packet",
        "",
        "Not evidence: `true`.",
        f"Current decision: `{summary['terminal_decision']}`.",
        f"Readiness: `{gap['satisfied_requirements']}/{gap['satisfied_requirements'] + gap['missing_requirements']}` requirements satisfied; `{gap['blocking_missing_requirements']}` blocking external gaps.",
        "",
        "Purpose: prepare the paper for hostile review, rebuttal, and outreach without expanding the claim beyond current evidence.",
        "",
        "Core stance: Paper 119 is about adaptive physical world/action models for skill seams. The local model predicts whether a skill transition will fail, diagnoses why, chooses accept/repair/probe/abstain/transition, and writes the outcome back into planner-edge memory. Energy landscapes are the implementation vocabulary, not the identity of the paper.",
        "",
        "How to use this packet:",
        "",
        "- In the paper: keep the claim bounded and evidence-backed.",
        "- In rebuttal: answer with the exact audit and the remaining gate.",
        "- In outreach: lead with the seam-model idea and one validation ask; do not list many papers.",
        "- For Haonan/Yilun: ask for fit/falsification advice and possible collaboration, not for them to be responsible for supplying the missing proof.",
        "",
        "## Objection Map",
        "",
    ]
    for idx, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"### {idx}. {entry['reviewer_objection']}",
                "",
                f"Response: {entry['response']}",
                "",
                f"Current local fact: {entry['local_fact']}",
                "",
                f"Allowed claim: {entry['allowed_claim']}",
                "",
                f"Remaining gate: {entry['remaining_gate']}",
                "",
                f"Outreach use: {entry['outreach_use']}",
                "",
                "Evidence:",
            ]
        )
        for evidence in entry["evidence"]:
            lines.append(f"- `{evidence}`")
        lines.append("")

    lines.extend(
        [
            "## Send/Do-Not-Send Rule",
            "",
            "Use one paper in the first email: Paper 119. Mentioning many papers makes the pitch look unfocused. If a second artifact is useful, attach the one-page memo or four-page preview, not a catalog.",
            "",
            "The strongest email shape is: identity sentence, one-sentence seam-model description, one concrete local result, one honest external-validation boundary, and one request for feedback or collaboration on the validation layer.",
            "",
            "## Boundary",
            "",
            "This packet is not external robot evidence and does not change the current STRONG_REVISE decision. It is a reviewer-readiness artifact for keeping claims, evidence, and outreach aligned while the real validation layer remains missing.",
        ]
    )
    body = "\n".join(lines) + "\n"
    OUT_MD.write_text(body, encoding="utf-8")

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", True, "packet declares non-evidence status")
    add_check(checks, "entry_count_ge_12", len(entries) >= 12, f"entries={len(entries)}")
    add_check(checks, "required_objections_present", not missing_ids, f"missing={missing_ids}")
    add_check(checks, "all_evidence_paths_exist", not evidence_missing, f"missing={evidence_missing[:8]}")
    add_check(checks, "current_decision_is_strong_revise", summary.get("terminal_decision") == "STRONG_REVISE", str(summary.get("terminal_decision")))
    add_check(checks, "readiness_boundary_visible", gap.get("objective_complete") is False and gap.get("blocking_missing_requirements") >= 4, f"objective_complete={gap.get('objective_complete')}, blockers={gap.get('blocking_missing_requirements')}")
    add_check(checks, "world_action_identity_visible", "adaptive physical world/action models for skill seams" in body, "core identity in packet")
    add_check(checks, "outreach_many_papers_guard", "do not list many papers" in body and "Use one paper" in body, "one-paper outreach rule")
    add_check(checks, "haonan_not_responsible_for_proof", "not for them to be responsible for supplying the missing proof" in body, "Haonan/Yilun boundary")
    add_check(checks, "planner_update_objection_present", "planner-edge" in body and "future planning" in body, "planner update defense")
    add_check(checks, "external_gates_preserved", body.count("External") + body.count("external") >= 15, "external boundary repeated")
    forbidden_hits = []
    for pattern in forbidden_patterns:
        forbidden_hits.extend(re.findall(pattern, body, flags=re.IGNORECASE))
    add_check(checks, "no_forbidden_overclaim_phrases", not forbidden_hits, f"hits={forbidden_hits}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "current_decision": summary.get("terminal_decision"),
        "readiness": {
            "satisfied_requirements": gap.get("satisfied_requirements"),
            "total_requirements": gap.get("satisfied_requirements", 0) + gap.get("missing_requirements", 0),
            "blocking_missing_requirements": gap.get("blocking_missing_requirements"),
        },
        "packet": rel(OUT_MD),
        "entry_count": len(entries),
        "entries": entries,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit_lines = [
        "# Reviewer Response Packet Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        f"Packet: `{rel(OUT_MD)}`.",
        f"Entries: `{len(entries)}`.",
        "",
        "This audit checks that the reviewer response packet maps hostile objections to current evidence, allowed claims, remaining gates, and outreach use without claiming external validation.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        audit_lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_AUDIT_MD.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print(f"Reviewer response packet audit: {'PASS' if passed else 'FAIL'}; entries={len(entries)}; checks={len(checks)}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_AUDIT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

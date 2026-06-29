# Reviewer Response Packet

Not evidence: `true`.
Current decision: `STRONG_REVISE`.
Readiness: `17/21` requirements satisfied; `4` blocking external gaps.

Purpose: prepare the paper for hostile review, rebuttal, and outreach without expanding the claim beyond current evidence.

Core stance: Paper 119 is about adaptive physical world/action models for skill seams. The local model predicts whether a skill transition will fail, diagnoses why, chooses accept/repair/probe/abstain/transition, and writes the outcome back into planner-edge memory. Energy landscapes are the implementation vocabulary, not the identity of the paper.

How to use this packet:

- In the paper: keep the claim bounded and evidence-backed.
- In rebuttal: answer with the exact audit and the remaining gate.
- In outreach: lead with the seam-model idea and one validation ask; do not list many papers.
- For Haonan/Yilun: ask for fit/falsification advice and possible collaboration, not for them to be responsible for supplying the missing proof.

## Objection Map

### 1. This is not a world/action model; it is just thresholds over controller diagnostics.

Response: The claim is deliberately local: the seam state is the local world, and the action is the planner-facing choice to accept, repair, probe, abstain, or choose another transition. The packet should answer this by pointing to the prediction-diagnosis-decision-update loop, not by claiming a full simulator.

Current local fact: The diagnostic audit reports 0 label-rule mismatches, 0 decision-rule mismatches, and 0 planner-update mismatches over local rows.

Allowed claim: A bounded local world/action interface can make skill seams more decision-relevant.

Remaining gate: External logs must show the same prediction-diagnosis-decision-update fields on real or accepted high-fidelity runs.

Outreach use: Use this as the core identity sentence; do not pitch it as a low-level controller.

Evidence:
- `paper/main.tex`
- `results/diagnostic_mechanism_audit.json`
- `results/planner_edge_policy_audit.json`

### 2. The paper may be only the previous energy composer with a new name.

Response: The prior proposed composer is retained as the strongest non-oracle predecessor, and all gains are measured against it rather than against an easy baseline.

Current local fact: Against proposed_energy_landscape_composer_v4_1, v5 improves hard success by 0.085 and hard utility by 0.235, with 10/10 paired hard-utility wins.

Allowed claim: The local improvement is over the prior proposed method, not only over weak baselines.

Remaining gate: External evidence must re-run the prior method and v5 under the same skill library and paired resets.

Outreach use: Mention this only after stating the core seam-model idea.

Evidence:
- `results/summary.json`
- `paper/main.tex`
- `results/manuscript_number_audit.json`

### 3. The evidence is local/synthetic and may not transfer to hardware.

Response: Agree. The correct answer is not to deny the weakness; it is to show the exact external evidence gate and the independent operator packet already prepared to close it.

Current local fact: The readiness audit reports 17/21 requirements satisfied and 4 blocking external gaps.

Allowed claim: The current paper is locally strong but not ready for deployment-level claims or final main-conference submission claims.

Remaining gate: Real robot or accepted high-fidelity manifest/log/video/checkpoint evidence must pass strict audits.

Outreach use: Do not ask Haonan to supply the missing proof; ask for fit/falsification advice and possible collaboration.

Evidence:
- `results/submission_readiness_gap_audit.json`
- `results/external_evidence_audit.json`
- `results/external_operator_packet.md`
- `results/external_operator_handoff_bundle.md`

### 4. The method wins by abstaining from hard cases.

Response: The response is coverage plus breach, not success alone. The decision-quality audit also checks recovered accepts that the prior composer abstained from.

Current local fact: V5 accepts 0.404 of hard seams versus 0.000 for the predecessor, and recovers 3,850 accept pairs with utility +0.243.

Allowed claim: The local seam layer preserves useful accepted transitions while bounding accepted-seam breach.

Remaining gate: External rollouts must recompute coverage and breach from raw JSONL records.

Outreach use: This is a strong one-sentence defense if someone thinks abstention is the whole trick.

Evidence:
- `results/decision_quality_audit.json`
- `results/local_falsification_audit.json`
- `paper/generated_decision_quality_table.tex`

### 5. The method wins by spending more compute or search at the seam.

Response: The falsification audit explicitly checks composition cost and cost-normalized utility.

Current local fact: Composition cost changes by -0.046, while cost-normalized utility improves by 0.218.

Allowed claim: The local gains are not explained by higher recorded composition cost.

Remaining gate: External logs must include wall-clock/runtime/probe/repair costs and recompute utility from raw records.

Outreach use: Use only as a supporting detail, not the headline.

Evidence:
- `results/local_falsification_audit.json`
- `results/summary.json`
- `paper/main.tex`

### 6. Energy terms may be decorative; any tuned score might work.

Response: The ablation suite removes terminal sampling, contact guard, repair, descent, barrier, basin, fixed-risk, and calibration components.

Current local fact: The best removed-component ablation, minus_terminal_sampler, trails the full method by 0.028 success and 0.043 utility.

Allowed claim: The local mechanism depends on the full seam-certification stack, not only a generic energy score.

Remaining gate: External ablations must be replayed with identical task configs, skill libraries, and method panels.

Outreach use: Good for technical follow-up, not the first email paragraph.

Evidence:
- `results/summary.json`
- `results/ablation_metrics.csv`
- `paper/generated_ablation_table.tex`

### 7. Baseline wrappers may be unfair or not independently implemented.

Response: The local paper names the prior method and multiple baselines, but the strict external baseline contract still keeps independent non-oracle evidence as missing.

Current local fact: The strict external baseline and adapter-evidence audits remain fail-closed until manifest-declared real implementations exist.

Allowed claim: Local baselines are broad and audited; independent external baseline evidence is still required.

Remaining gate: Manifest-declared independent non-oracle implementations and adapter evidence must pass strict validation.

Outreach use: This protects credibility; acknowledge it before a reviewer has to say it.

Evidence:
- `results/external_baseline_contract_audit.json`
- `results/external_adapter_contract_evidence_audit.json`
- `external_validation/baseline_implementation_contract.md`

### 8. The paper says future planning improves, but the evidence may only be one-step classification.

Response: Use the planner-edge policy audit: it chooses future candidate edges using exported planner-edge updates first, then predicted risk, basin alignment, descent, and cost without using realized utility to choose.

Current local fact: Across 1,680 local planning frontiers, selected-edge utility improves by 0.231, success by 0.080, and realized breach by -0.075.

Allowed claim: Local planner-edge updates change future transition selection under a fixed audit policy.

Remaining gate: External runs must log edge updates and replay planner-frontier selection from raw records.

Outreach use: This is one of the best bridges to Yilun's planning/world-model interests.

Evidence:
- `results/planner_edge_policy_audit.json`
- `results/planner_edge_policy_audit.md`
- `paper/generated_planner_edge_policy_table.tex`

### 9. Predicted seam risk may be calibrated locally but fail after transfer.

Response: The local calibration is strong, but transfer remains an external-evidence question.

Current local fact: Local ten-bin calibration error is 0.007, risk-breach correlation is 0.971, and the high-low decile breach gap is 0.080.

Allowed claim: Predicted seam risk is locally predictive and decision-relevant.

Remaining gate: External raw logs must recompute calibration error, risk deciles, and fixed-risk breach.

Outreach use: Frame this as a validation question Haonan could help critique, not a solved transfer result.

Evidence:
- `results/seam_prediction_calibration_audit.json`
- `paper/generated_seam_prediction_calibration_table.tex`
- `results/external_rollout_evidence_audit.json`

### 10. The work is really contact-rich manipulation, not the broader Jason agenda.

Response: Contact-rich cases are a stress test because they make action consequences visible. The identity remains adaptive physical world/action modeling at skill seams.

Current local fact: The manuscript readability audit passes the contact-as-testbed positioning and keeps contact-rich phrase count bounded.

Allowed claim: Contact-rich manipulation is a proving ground, not the core research identity.

Remaining gate: Broader external tasks should include non-contact and mixed seam regimes when evidence collection expands.

Outreach use: Use this to stay aligned with your agenda when writing to Haonan.

Evidence:
- `paper/main.tex`
- `results/manuscript_readability_audit.json`
- `docs/related_work_coverage_matrix.md`

### 11. Why would Haonan or Yilun care about this specific paper?

Response: The overlap is behavior/action composition plus predictive physical models for planning. The pitch should be one paper, not many papers: present Paper 119 as a reliability layer for composed behaviors.

Current local fact: The outreach package already frames Paper 119 as a seam critic for behavior-composition systems.

Allowed claim: The paper is a plausible bridge to behavior composition and world/action-model planning.

Remaining gate: A collaborator still needs to see a credible external validation path before treating it as submission-ready.

Outreach use: Mention one paper and one validation ask; do not dilute the email by listing many papers.

Evidence:
- `docs/haonan_yilun_outreach_package.md`
- `paper/main.tex`
- `docs/related_work_coverage_matrix.md`

### 12. The paper is not submission-ready without real robot or accepted high-fidelity validation.

Response: Agree. The correct current decision is STRONG_REVISE; the packet exists to make the remaining proof layer concrete.

Current local fact: Readiness remains 17/21 with 4 blocking external gaps. The official video write guard rejects diagnostic fallback, non-MP4-like, undersized, out-of-dir, or unexpected videos, and the official JSONL write guard rejects schema-invalid rollout records before the actual collection runner appends them, but these remain tooling hardening rather than external validation.

Allowed claim: The local package is stronger and more reviewer-ready, but not independently complete.

Remaining gate: Close all four blocking external requirements before claiming independent main-conference readiness.

Outreach use: This is the honesty line for the email and for any rebuttal.

Evidence:
- `results/submission_readiness_gap_audit.json`
- `docs/submission_readiness_audit_v5.md`
- `results/external_acquisition_packet.md`

## Send/Do-Not-Send Rule

Use one paper in the first email: Paper 119. Mentioning many papers makes the pitch look unfocused. If a second artifact is useful, attach the one-page memo or four-page preview, not a catalog.

The strongest email shape is: identity sentence, one-sentence seam-model description, one concrete local result, one honest external-validation boundary, and one request for feedback or collaboration on the validation layer.

## Boundary

This packet is not external robot evidence and does not change the current STRONG_REVISE decision. It is a reviewer-readiness artifact for keeping claims, evidence, and outreach aligned while the real validation layer remains missing.

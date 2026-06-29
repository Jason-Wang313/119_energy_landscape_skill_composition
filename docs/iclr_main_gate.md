# ICLR Main Gate

Paper: 119 energy_landscape_skill_composition

v5 gate verdict: STRONG_REVISE

Local evidence digest:

- Proposed method: `barrier_certified_energy_composer_v5`.
- Strongest non-oracle baseline: `proposed_energy_landscape_composer_v4_1`.
- Hard success: proposed `0.801711` vs strongest baseline `0.717113`; margin `0.084598`, wins `10/10`.
- Hard utility: proposed `0.888270` vs strongest baseline `0.653100`; margin `0.235170`, wins `10/10`.
- Seam-failure delta: `-0.049123`.
- Barrier-violation delta: `-0.040869`.
- Basin-alignment delta: `+0.080008`.
- Descent-continuity delta: `+0.078090`.
- Damage-rate delta: `-0.005790`.
- Composition-cost delta: `-0.045838`.
- Energy-model-error delta: `-0.014417`.
- Risk-calibration-error delta: `-0.010549`.
- Realized-seam-breach delta: `-0.075646`.
- Best ablation success gap: `0.028125`.
- Best ablation utility gap: `0.043490`.
- Stress endpoint success margin: `0.103125`.
- Fixed-risk coverage/breach/gated success: `0.863021` / `0.000302` / `0.760108`.
- Diagnostic mechanism audit: zero label, decision, and planner-update mismatches over 230,400 local rows, with all five failure labels and all five seam decisions observed in the proposed hard slice.
- Comparative decision-quality audit: accept coverage `0.404` vs `0.000`, accepted-seam breach above the `0.15` budget rate `0.000`, and 3,850 recovered predecessor-abstained accepts with utility `+0.243`, success `+0.091`, and realized breach `-0.077`.
- External execution readiness audit: independent operator packet ready for a 1,440-record high-fidelity validation run, but explicitly non-evidence until real manifest-declared logs, configs, videos, checkpoints, and implementations exist.
- External reference adapter audit: 12 executable implementation-only adapters, including 11 non-oracle baselines, pass the API contract and remove validation-harness ambiguity; they are not robot or high-fidelity rollout evidence.
- External local dry run: 20,640 external-schema JSONL records are generated from the frozen local suite and recomputed successfully as a plumbing check; they are not external evidence.
- Figure readability audit: all seven main figure companions pass render-resolution, contrast, margin, and manuscript-reference checks.
- Camera-ready design audit: all 30 rendered PDF pages pass nonblank, density, contrast, margin, sparse-page, canonical-parity, and text-anchor checks.
- Manuscript readability audit: central framing, novelty boundary, contact-as-testbed positioning, paragraph readability, and stale manual-polish blocker removal pass.
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 failure cases.

Local gate result: pass.

Scope gate result: fail.

External evidence audit: fail until `scripts/audit_external_evidence.py --strict` passes against `external_validation/manifest.json` and the referenced logs, videos, configs, checkpoints, metrics, and independent baselines.

ICLR main ready: no. Real robot rollouts, accepted high-fidelity validation, released skill-energy checkpoints, calibrated robot logs, videos, and manifest-declared independent baseline evidence from real external runs are still missing.

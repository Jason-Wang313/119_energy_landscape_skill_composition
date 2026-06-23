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
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 failure cases.

Local gate result: pass.

Scope gate result: fail.

ICLR main ready: no. Real robot rollouts, accepted high-fidelity validation, released skill-energy checkpoints, calibrated robot logs, videos, independent baselines, and a full manual related-work pass are still missing.

# 119 Energy Landscape Skill Composition

Submission-hardening version: v5_expanded

Terminal decision: STRONG_REVISE for an ICLR-main-target robotics submission package.

This rebuild expands the paper into a 25-page, CPU-only, RAM-light submission package for composing robot skills by energy-landscape seam compatibility. The v5 method, `barrier_certified_energy_composer_v5`, adds barrier certification, basin-overlap posterior checks, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, and a fixed-risk acceptance screen. The package is stronger and more reviewer-ready than the earlier local scaffold, but it is still not ICLR-main ready because the evidence remains local and synthetic rather than real robot or independently accepted high-fidelity validation.

## Evidence Snapshot

- Design: 6 task families x 8 seam regimes x 5 deployment splits x 12 methods x 10 paired seeds, with 230,400 main episode cells.
- Strongest non-oracle baseline: `proposed_energy_landscape_composer_v4_1`.
- Hard aggregate success: proposed `0.801711` vs strongest baseline `0.717113`; margin `0.084598`, with `10/10` paired-seed wins.
- Hard aggregate utility: proposed `0.888270` vs strongest baseline `0.653100`; margin `0.235170`, with `10/10` paired-seed wins.
- Mechanism deltas vs strongest baseline: seam failure `-0.049123`, barrier violation `-0.040869`, basin alignment `+0.080008`, descent continuity `+0.078090`.
- Risk/cost deltas: damage `-0.005790`, composition cost `-0.045838`, energy-model error `-0.014417`, risk calibration error `-0.010549`, realized seam breach `-0.075646`.
- Best ablation gaps: success `0.028125`, utility `0.043490`.
- Stress endpoint margins: success `0.103125`, utility `0.264045`.
- Fixed-risk audit at risk budget `0.15`: coverage `0.863021`, breach `0.000302`, gated success `0.760108`, utility margin `1.787443`.
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 documented failure cases.

## Reproduce

```powershell
pip install -r requirements.txt
python src\run_experiment.py
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

Canonical local PDF: `C:/Users/wangz/Downloads/119.pdf`

PDF SHA256: `8C6CB80C3AF49B3A17497EE174F70D55F0D4801F2E961A5B6268857EA4C70E9C`

PDF size: `657050` bytes.

PDF pages: `25`.

Artifact rule: keep the numbered PDF in Downloads only; do not copy it to the visible Desktop.

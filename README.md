# 119 Energy Landscape Skill Composition

Submission-hardening version: v4

Terminal decision: STRONG_REVISE for an ICLR-main-target robotics submission package.

This rebuild replaces the archive scaffold with a paper-specific local benchmark for composing robot skills by compatible energy landscapes. The proposed composer checks basin overlap, barrier height, descent continuity, terminal-state sampling, and high-energy seam repair before chaining skills. It is not yet ICLR-main ready because it lacks real robot or external high-fidelity validation.

## Evidence Snapshot

- Design: 6 task families x 8 skill-composition regimes x 5 deployment splits x 9 methods, 7 paired seeds, 72 rollout episodes per group.
- Strongest non-oracle baseline: `energy_compatibility_heuristic`.
- Combined-stress success: proposed `0.725 +/- 0.004` vs baseline `0.614 +/- 0.003`.
- Paired difference: `0.110 +/- 0.006`, wins `7/7` seeds.
- Seam-failure delta: `-0.087`; barrier-violation delta: `-0.101`.
- Basin-alignment delta: `+0.206`; descent-continuity delta: `+0.209`.
- Damage-rate delta: `-0.024`; composition-cost delta: `-0.091`.
- Best ablation gap: `0.056`.

## Reproduce

```powershell
pip install -r requirements.txt
python src\run_experiment.py
```

Canonical local PDF: `C:/Users/wangz/Downloads/119.pdf`

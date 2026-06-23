# Reproducibility Checklist

- Code entry point: `src/run_experiment.py`
- Manuscript entry point: `scripts/generate_manuscript.py`
- Artifact validator: `scripts/validate_submission_artifacts.py`
- Requirements: `numpy`, `matplotlib`
- Deterministic base seed: `119_2026_5`
- Main outputs:
  - `results/dataset_summary.csv`
  - `results/cell_metrics.csv`
  - `results/main_group_metrics.csv`
  - `results/seed_metrics.csv`
  - `results/metrics.csv`
  - `results/hard_seed_metrics.csv`
  - `results/hard_aggregate_metrics.csv`
  - `results/hard_pairwise_stats.csv`
  - `results/ablation_cell_metrics.csv`
  - `results/ablation_seed_metrics.csv`
  - `results/ablation_metrics.csv`
  - `results/stress_sweep_cell_metrics.csv`
  - `results/stress_sweep_seed_metrics.csv`
  - `results/failure_cases.csv`
  - `results/fixed_risk_cell_metrics.csv`
  - `results/fixed_risk_seed_metrics.csv`
  - `results/fixed_risk_metrics.csv`
  - `results/fixed_risk_pairwise_stats.csv`
  - `results/summary.json`
  - `results/summary.txt`
- Main figures:
  - `figures/energy_landscape_composition_hard_success_v5.png`
  - `figures/energy_landscape_composition_utility_risk_v5.png`
  - `figures/energy_landscape_composition_ablation_v5.png`
  - `figures/energy_landscape_composition_stress_sweep_v5.png`
  - `figures/energy_landscape_composition_fixed_coverage_v5.png`
  - `figures/energy_landscape_composition_fixed_risk_v5.png`

Reproduction command:

```powershell
pip install -r requirements.txt
python src\run_experiment.py
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

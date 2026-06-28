# Local Model Release Card

Release hash: `5CF7C6E592517ECC40371074F6341C489BCAB11E5358E6BA053CB3AD241B5929`.
Not external evidence: `true`.
External evidence ready: `false`.

## Identity

Local world/action model for robot skill seams: predict handoff failure, diagnose why, choose repair/probe/abstain/transition, and update planner edge beliefs.

## What Is Released

- Source generator: `src/run_experiment.py`.
- Source SHA256: `9F54FB0C4BCC0B74E4ED8FFB8AF3CFBE8777E5C615148FDCD90834A78F777E92`.
- Generator version: `v5_expanded`.
- Deterministic base seed: `11920265`.
- Proposed method: `barrier_certified_energy_composer_v5`.
- Proposed parameter hash: `A70B9C802BAD07FE8621791EA8EA125EBD81B2DD877270DEC7CE89839A43D4E4`.
- Methods/task-regime-split dimensions: `12` methods, `6` tasks, `8` regimes, `5` splits.

## Boundaries

- This is a frozen local mechanism and reproducibility release.
- It is not a trained robot policy checkpoint.
- It is not real robot or accepted high-fidelity simulator validation.
- It does not satisfy external_validation/manifest.json or strict external evidence gates.

## Result Artifact Hashes

- `results/summary.json` `7ADB1AB6EDE6A7861046B0CC0131EC1C1D2104BA57E7B958D82967790A56379D`
- `results/hard_aggregate_metrics.csv` `9D8A91A5A3ECFD710B1D2B34B87E0A6E21B2AEE4800504078AAD2D101EA0F687`, rows=12
- `results/hard_pairwise_stats.csv` `B9996221D1DF0FCC2A76D2660FAAC138A01A04E89C85C5F6155A1800E3DE7BEA`, rows=11
- `results/ablation_metrics.csv` `6A9735FBA761E276632AC6BF3EB64649C95C7B33884094459B80C65607F814B2`, rows=10
- `results/fixed_risk_metrics.csv` `31D91ADEC4EBB1FE6A7E0F0A096BCCBEC64FF60DF2F5DE582672381C2A3B0D12`, rows=28
- `results/planner_edge_policy_audit.json` `817A4483C10936022E7193AABFF793945FE8EF79792AA6604D4F91421FB2EA49`
- `results/seam_prediction_calibration_audit.json` `4500788F97ADBA1F67B687A1425A0EE9C86B5ED63FBE6067FB0EB16D11C3668F`
- `results/diagnostic_mechanism_audit.json` `5886CBE305054111D8F8E9223FFB1E3A6F8321FDCE2354ADE28B1C7BD8EAF6D7`
- `results/decision_quality_audit.json` `E935B87D07269A857F73DCC746D8B5A4362F138DE463E69D246ACF9E7B47F92C`
- `results/holdout_robustness_audit.json` `FA137E34EFBDB93BE6468CCDD1A88FC93D4F433B8510AD7C3161142E2674E847`
- `results/local_falsification_audit.json` `3F858594AFAC12D929BB9C7E7F640B527AE0494E308764F675597CF687DDCD15`

## Reference Adapter Hashes

- `external_validation/baselines/common_reference_adapter.py` `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py` `DFECC8475DFE638A5F23B7941CEB00C1F8094EF2256BE60F20CA6F817341859B`
- `external_validation/baselines/barrier_certified_energy_composer_v5/reference_adapter_metadata.json` `43927773BC52B3BA31376C956CEC5269715957DFDFCE8EE3E209DCEEFE8EF092`
- `external_validation/reference_adapter_report.md` `F64B68656335697769F9E7E60F19D974CF5D36D118D94B1296A7368CF49F4C2C`

## Strict Evidence Boundary

This card helps reviewers reproduce the local skill-seam action-model study. It does not replace `external_validation/manifest.json`, raw external JSONL logs, render-backed videos, calibrated state/contact/camera logs, accepted platform fidelity provenance, or manifest-declared independent baseline evidence.

# Independent Validation Protocol

Purpose: make Paper 119 credible as an independent main-conference submission without relying on Haonan Chen or any target collaborator for the missing evidence.

Current status: the local v5 evidence supports a controlled seam-composition claim. It does not yet support a deployment-level robot claim. The next validation layer must test whether energy-seam certification predicts real or high-fidelity skill handoff outcomes under shared skill libraries, paired resets, and strong baselines.

## Submission Claim To Validate

Bounded claim:

> A barrier-certified energy composer improves skill composition when basin overlap, barrier height, descent continuity, repair cost, and seam-risk calibration are estimable at the handoff.

This is the only claim that should be promoted to the main paper before external validation. Do not claim universal manipulation, universal safety, or hardware-ready deployment.

## Minimum Independent Validation Layer

Use one of these routes before calling the paper submission-ready:

1. Real robot validation on at least 3 composed tasks with paired resets.
2. Accepted high-fidelity simulator validation on at least 4 composed tasks with contact/dynamics fidelity, released configs, and videos.
3. A mixed route with 2 real robot tasks plus 2 high-fidelity simulation tasks, using the same metric and logging schema.

The validation is independent if Jason can run or reproduce it without Haonan. Haonan collaboration may add a stronger external testbed, but it must not be required for the base submission claim.

## Task Families

Primary task families:

- `peg_place_regrasp`: first skill must end inside the next grasp or insertion basin.
- `drawer_to_pick_transfer`: constrained contact ends before free-space grasping.
- `mobile_push_then_grasp`: navigation or pushing error changes the next manipulation basin.
- `tool_use_handover`: terminal tool pose and force history determine handoff safety.
- `door_open_navigation`: contact-mode/topology transition before the next skill.
- `cable_route_insert`: deformable or nonconvex contact with narrow basins.

Minimum acceptance:

- At least 4 families in high-fidelity simulation, or at least 3 on real hardware.
- At least 30 paired episodes per method per task family.
- Same initial states, skill library, observation interfaces, and compute budgets for all non-oracle methods.
- Videos for representative successes, seam failures, abstentions, and oracle-gap cases.

## Baselines

Every external validation must include:

- `greedy_module_sequence`
- `behavior_cloned_skill_chain` or a demonstration sequence baseline
- `option_graph_planner`
- `tamp_feasibility_screen`
- `stable_dmp_handoff` or stable dynamics handoff
- `diffusion_skill_stitcher` or generative handoff sampler
- `cem_trajectory_composer`
- `residual_rl_composer` or residual repair policy
- `energy_compatibility_heuristic`
- `proposed_energy_landscape_composer_v4_1`
- `barrier_certified_energy_composer_v5`
- `oracle_basin_composer` as post hoc upper bound only

Do not compare against weaker wrappers. The strongest non-oracle comparator must be selected after running all baselines, using the same hard-slice criterion as the local suite.

## Required Logs

Each episode should emit one JSONL record with:

- `run_id`, `task_family`, `platform_type`, `platform_name`, `scene_id`, `episode_index`, `seed`, `method`, `skill_i`, `skill_j`
- `initial_state_hash`, `terminal_sample_set_hash`, and `policy_or_config_hash`
- `basin_estimate`, `barrier_score`, `descent_continuity_score`, and `predicted_seam_risk`
- `fixed_risk_budget`
- `decision`: `accept`, `repair`, `probe`, `abstain`, or `transition`
- `failure_diagnosis`: `none`, `basin_miss`, `high_barrier`, `descent_break`, `contact_transition`, `dynamics_mismatch`, `partial_observability`, `calibration_shift`, or `unknown`
- `repair_action`
- `success`, `seam_failure`, `barrier_violation`, `damage_or_intervention`, and `realized_seam_breach`
- `composition_cost`, `utility`, and `video_path`

Raw logs must be preserved. Tables may be regenerated from logs, but logs are the source of truth.

## Metrics

Primary metrics:

- task success
- composition utility
- seam failure rate
- barrier violation rate
- basin alignment
- descent continuity
- damage or safety-intervention rate
- composition cost
- predicted seam risk
- realized seam breach
- risk calibration error
- abstention rate
- fixed-risk coverage
- fixed-risk gated success

Report coverage and realized breach together. A method that wins by rejecting most seams is not acceptable unless it also improves gated success or utility at matched coverage.

## Main-Conference Gates

The paper may be called independently submission-ready only if all gates pass:

- External success margin over strongest non-oracle baseline is at least `0.05`.
- External utility margin over strongest non-oracle baseline is at least `0.08`.
- Proposed method wins at least `70%` of paired task/seed comparisons.
- Fixed-risk breach at budget `0.15` is at most `0.02`.
- Fixed-risk coverage at budget `0.15` is at least `0.55`.
- At least 3 of 4 external task families show positive success and utility margins.
- Ablations show that removing basin, barrier, descent, calibration, or repair weakens the result.
- Oracle remains reported and stronger than the proposed method, or the paper explains why the task is saturated.
- Failure cases are shown, not hidden.
- Code, configs, logs, and videos are released or documented with hashes.

## Machine-Checkable Evidence Contract

The prose protocol is implemented as an external-evidence audit:

```powershell
python scripts\validate_external_rollouts.py --write-results
python scripts\build_external_analysis_plan.py
python scripts\audit_external_collection_readiness.py
python scripts\audit_external_release_package.py
python scripts\audit_external_pairing_integrity.py
python scripts\audit_external_evidence.py
python scripts\audit_external_collection_readiness.py --strict
python scripts\validate_external_rollouts.py --strict --write-results --check-video-paths
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_evidence.py --strict
```

The non-strict commands write `results/external_rollout_metrics.{json,md}` and `results/external_evidence_audit.{json,md}`. The strict commands must return success before the paper can be called independently submission-ready.

The pairing-integrity command writes `results/external_pairing_integrity_audit.{json,md}` and is also required before any external logs count as evidence. It checks that paired resets contain complete, duplicate-free method panels with equal per-method coverage and consistent terminal samples, platform, and fixed-risk budget.

The release-package command writes `results/external_release_package_audit.{json,md}` and is required before a manifest can count as reproducible evidence. It verifies manifest-declared code, configs, logs, videos, and checkpoints by SHA256 and blocks local dry-run, template, scaffold, or placeholder artifacts.

The collection-readiness command writes `results/external_collection_readiness_audit.{json,md}` and is required before spending external collection time. Non-strict mode reports the current fail-closed state; strict mode must pass before actual collection starts, requiring a non-template backend, real task configs, accepted fidelity provenance, explicit alias unsealing, a specific run id, and empty output logs.

Collection plan:

- `results/external_collection_plan.json`
- `results/external_collection_plan.md`
- `external_validation/statistical_analysis_plan.json`
- `external_validation/statistical_analysis_plan.md`
- `results/external_analysis_plan_audit.json`
- `results/external_analysis_plan_audit.md`

Generate it with:

```powershell
python scripts\build_external_collection_plan.py
python scripts\build_external_analysis_plan.py
python scripts\build_external_platform_onboarding.py
```

The collection plan currently expands the high-fidelity route into 4 task families x 30 paired resets x 12 methods = 1,440 required JSONL records. The analysis plan pre-registers the external primary hypotheses, rollout-schema thresholds, paired-comparison key, exclusion/unblinding policy, strict gates, and required reporting before rollout collection. The external platform onboarding packet records official source anchors, required simulator provenance, task onboarding files, backend requirements, and strict gate order for the primary ManiSkill/SAPIEN route. These files are not evidence; they are a deterministic collection schedule and locked analysis/onboarding contract for producing the real evidence package.

Independent route matrix:

- `external_validation/independent_validation_route.md`
- `external_validation/independent_validation_route_matrix.csv`
- `results/independent_validation_route_audit.json`
- `results/independent_validation_route_audit.md`

Generate it with:

```powershell
python scripts\build_independent_validation_route.py
```

This route is also not evidence. It makes the non-Haonan path explicit: a primary ManiSkill/SAPIEN public-simulator route, MuJoCo/robosuite and Isaac Sim/Isaac Lab secondary routes, and a third-party robot-lab route. Any route still has to produce manifest-backed JSONL logs, videos, real configs, platform provenance, and independent baseline implementations before it can satisfy the external gate.

Operator runbook:

- `external_validation/collection_runbook.md`
- `external_validation/operator_record_sheet.csv`
- `external_validation/blind_evaluation_protocol.md`
- `external_validation/blinded_operator_sheet.csv`
- `external_validation/method_alias_map.json`
- `external_validation/task_cards/*.md`
- `external_validation/config_templates/*.json`
- `external_validation/runner/README.md`
- `external_validation/runner/backend_contract.py`
- `external_validation/runner/real_collection_runner.py`
- `external_validation/platform_qualification_checklist.md`
- `results/external_blind_eval_audit.json`
- `results/external_blind_eval_audit.md`
- `results/external_runbook_audit.json`
- `results/external_runbook_audit.md`
- `results/external_runner_harness_audit.json`
- `results/external_runner_harness_audit.md`
- `results/external_collection_readiness_audit.json`
- `results/external_collection_readiness_audit.md`
- `results/external_release_package_audit.json`
- `results/external_release_package_audit.md`
- `results/external_pairing_integrity_audit.json`
- `results/external_pairing_integrity_audit.md`

Generate it with:

```powershell
python scripts\build_external_blind_eval_plan.py
python scripts\build_external_runbook.py
python scripts\audit_external_runner_harness.py
python scripts\audit_external_collection_readiness.py
python scripts\audit_external_release_package.py
python scripts\audit_external_pairing_integrity.py
```

The runbook, blinded evaluation packet, runner harness, collection-readiness audit, release-package audit, and pairing-integrity audit are also not evidence. They convert the collection plan into task cards, per-run record rows, deterministic per-reset randomized alias order, starter config templates, a fail-closed execution path, preflight checks for actual collection, hash-locked release checks, and a paired-panel fairness gate so a real robot or high-fidelity-sim operator can collect the missing validation layer consistently. The runner dry-run writes no logs; actual collection rejects template backends/configs, requires explicit alias unsealing, and still must produce manifest-backed JSONL logs, videos, configs, checkpoints, implementation hashes, and a skill-library hash. The alias map should stay sealed until those artifacts are frozen.

Platform qualification:

- `external_validation/platform_qualification_checklist.md`
- `results/external_execution_readiness_audit.json`
- `results/external_execution_readiness_audit.md`

Generate and check the execution packet with:

```powershell
python scripts\audit_external_execution_readiness.py
```

This audit is also not evidence. It checks that the independent operator packet, platform qualification checklist, config templates, adapter harness, manifest builder, and strict-fail evidence gates are mutually consistent before any real rollout is collected.

Config schema:

- `external_validation/config_schema_v1.json`
- `external_validation/config_templates/*.json`
- `results/external_config_template_audit.json`
- `results/external_config_template_audit.md`
- `results/external_config_evidence_audit.json`
- `results/external_config_evidence_audit.md`

Template check:

```powershell
python scripts\validate_external_configs.py
```

Strict evidence check:

```powershell
python scripts\validate_external_configs.py --strict
```

The template check should pass locally. The strict check must fail until real manifest-declared configs exist, are not marked as templates, match the manifest task fields, and include reset, observation, compute-budget, fidelity, and logging requirements.

Baseline implementation contract:

- `external_validation/baseline_implementation_contract.md`
- `external_validation/baseline_implementation_matrix.csv`
- `external_validation/baseline_specs/*.json`
- `results/external_baseline_contract_audit.json`
- `results/external_baseline_contract_audit.md`

Generate it with:

```powershell
python scripts\build_external_baseline_contract.py
```

This contract is not evidence. It specifies the adapter API, fairness invariants, oracle boundary, required source/config/checkpoint hashes, and method-by-method release requirements for the non-oracle baselines. The strict external audit must still see real implementations and raw rollout logs before the paper can be called independently submission-ready.

Adapter scaffolds:

- `external_validation/baseline_adapter_scaffold.md`
- `external_validation/baselines/README.md`
- `external_validation/baselines/*/adapter_template.py`
- `external_validation/baselines/*/adapter_metadata.json`
- `results/external_adapter_scaffold_audit.json`
- `results/external_adapter_scaffold_audit.md`

Generate them with:

```powershell
python scripts\build_external_adapter_scaffolds.py
```

The scaffolds are not evidence and intentionally raise `NotImplementedError`. They define the executable shape that independent implementations must replace. The strict external evidence audit rejects scaffold-only adapters if they are referenced as method implementations.

Adapter contract validator:

- `scripts/validate_external_adapters.py`
- `results/external_adapter_contract_audit.json`
- `results/external_adapter_contract_audit.md`
- `results/external_adapter_contract_evidence_audit.json`
- `results/external_adapter_contract_evidence_audit.md`

Non-evidence contract check:

```powershell
python scripts\validate_external_adapters.py
```

Strict implementation check:

```powershell
python scripts\validate_external_adapters.py --strict
```

The non-strict check verifies the harness, scaffold structure, required adapter API, proposal fields, log fields, and hash reporting. The strict check must fail until `external_validation/manifest.json` declares real non-oracle implementations that replace the scaffolds and can run on the shared observations, terminal samples, skill transition, and compute budget.

Required manifest:

- `external_validation/manifest.json`

Template:

- `external_validation/manifest_template.json`

Log schema:

- `external_validation/log_schema_v1.json`

The manifest must reference episode-level JSONL logs, video directories, configs, checkpoints or hashes, manifest-declared independent baseline implementation records, task-family counts, fixed-risk metrics, and ablation evidence. The rollout validator recomputes success margin, utility margin, paired win rate, fixed-risk coverage, fixed-risk breach, and positive task-family count from raw logs, and the evidence audit blocks if those recomputed metrics disagree with the manifest. Tables regenerated from logs are not enough; the raw logs and release artifacts are the source of truth.

## Reviewer Attack Coverage

This validation layer must answer:

- Is the method more than an energy heuristic?
- Does it win by abstaining from hard seams?
- Does it win by over-searching the handoff?
- Does risk calibration predict realized breach?
- Does the seam model distinguish basin failure from barrier failure?
- Does the result survive contact-mode transitions and dynamics mismatch?
- Are all methods composing the same primitive skills?
- Are videos and raw logs sufficient to audit failures?

## Relation To Haonan/Yilun Outreach

This protocol is the base plan whether or not Haonan responds. The outreach should offer this as a ready validation design and ask whether a CoStream-style behavior-composition stack is a scientifically useful additional testbed. Do not imply that Haonan's job is to supply the missing proof.

Relevant current source anchors checked on 2026-06-26:

- Haonan Chen homepage: https://haonan16.github.io/
- Yilun Du homepage: https://yilundu.github.io/
- CoStream: https://arxiv.org/abs/2606.26423
- SIMPACT: https://arxiv.org/abs/2512.05955
- World Model for Robot Learning survey: https://arxiv.org/abs/2605.00080

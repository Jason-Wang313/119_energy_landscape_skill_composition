# Submission Readiness Decision

Terminal decision: STRONG_REVISE

ICLR main ready: no

Why strong-revise:

- `0.084598` hard-success margin over the strongest non-oracle baseline.
- `0.235170` hard-utility margin over the strongest non-oracle baseline.
- `10/10` paired-seed wins for hard success and hard utility.
- Seam-failure, barrier-violation, basin-alignment, descent-continuity, damage, cost, calibration, and realized-breach gates all pass.
- Best ablation trails the full method by `0.028125` success and `0.043490` utility.
- Evidence coverage includes 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 failure cases.
- Fixed-risk audit reports coverage `0.863021`, breach `0.000302`, and gated success `0.760108` at risk budget `0.15`.
- External reference adapters pass for all 12 methods as implementation-only harness checks, reducing future validation friction without counting as rollout evidence.
- The guarded config materialization plan is ready to write real task configs only after a platform and compute budget are supplied with `--confirm-real-platform --write`.
- The generated external operator packet is a no-go handoff for independent validation: after materializing the high-fidelity route configs, it lists four remaining pre-collection blockers, the exact collection command, and post-collection strict gates without claiming evidence.
- The outreach package now frames Haonan's role as fit/falsification advice around CoStream-style behavior composition, not as responsibility for supplying the missing proof.
- Numeric integrity, PDF placement, page-count, and visual QA checks pass.

Why not ready:

- no real robot validation;
- no accepted high-fidelity simulator validation;
- no released trained skill-energy or policy checkpoint;
- no calibrated contact-force, camera, or state logs;
- no hardware rollout videos;
- no manifest-declared independent baseline evidence from real external runs.

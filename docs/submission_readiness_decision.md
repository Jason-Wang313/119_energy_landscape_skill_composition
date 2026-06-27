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
- The adapter evidence self-test proves the strict manifest-declared implementation gate can pass on temporary real-style adapters while still rejecting missing manifests and scaffold templates.
- The release-package self-test proves the hash-lock gate can pass on temporary complete artifacts while still rejecting missing manifests and local-dry-run/template/scaffold/placeholder files.
- The pairing-integrity self-test proves complete 1,440-record paired-reset panels can pass while duplicate method rows, incomplete panels, terminal-sample mismatches, and missing manifests fail.
- The guarded config materialization plan is ready to write real task configs only after a platform and compute budget are supplied with `--confirm-real-platform --write`.
- The external analysis plan locks the external primary hypotheses, rollout-schema thresholds, paired-comparison key, exclusion/unblinding policy, and required reporting before collection while remaining non-evidence.
- The external platform onboarding packet turns the primary ManiSkill/SAPIEN public-simulator route into a concrete non-evidence operator contract with official source anchors, provenance fields, task onboarding files, backend requirements, and strict gate order.
- The external backend integration packet turns the missing non-template public-simulator backend into concrete work orders while strict backend readiness remains false.
- The external method implementation packet turns the missing non-oracle baseline layer into concrete per-method work orders while strict adapter evidence remains missing.
- The generated external operator packet is a no-go handoff for independent validation: after materializing the high-fidelity route configs, it lists four remaining pre-collection blockers, the exact collection command, and post-collection strict gates without claiming evidence.
- The external operator handoff bundle hash-lists the operator-facing validation files and excludes rollout logs, videos, checkpoints, local dry-run artifacts, placeholder media, and real evidence manifests.
- The outreach package now frames Haonan's role as fit/falsification advice around CoStream-style behavior composition, not as responsibility for supplying the missing proof.
- Numeric integrity, PDF placement, page-count, and visual QA checks pass.

Why not ready:

- no real robot validation;
- no accepted high-fidelity simulator validation;
- no released trained skill-energy or policy checkpoint;
- no calibrated contact-force, camera, or state logs;
- no hardware rollout videos;
- no manifest-declared independent baseline evidence from real external runs.

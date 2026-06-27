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
- The external config manifest packet turns prepared task configs into manifest-declaration and hash-lock work orders while strict config evidence remains false.
- The external rollout evidence packet turns the missing raw JSONL logs, videos, manifest, strict rollout recomputation, pairing, release, and final evidence gates into operator work orders while strict rollout and external evidence remain false.
- The external analysis plan locks the external primary hypotheses, rollout-schema thresholds, paired-comparison key, exclusion/unblinding policy, and required reporting before collection while remaining non-evidence.
- The external platform probe records Python, package, GPU/renderer, code-commit, and config/backend hash provenance for the selected public-simulator machine while remaining non-evidence.
- The ManiSkill task binding probe maps the four external task families to concrete public-simulator environment candidates while accepted task binding and strict evidence remain false.
- The ManiSkill env smoke probe now records per-environment construction/reset status and shows the four primary bound ManiSkill/SAPIEN candidates construct/reset locally, while support candidates explicitly require `oakink-v2` and `ycb` assets and accepted fidelity, rollout logs, and strict evidence remain false.
- The ManiSkill fidelity metadata probe records sim/control timestep, SAPIEN backend, controller, observation/info-key, agent, and asset metadata for the bound public-simulator candidates while remaining non-evidence and leaving accepted fidelity false.
- The external platform onboarding packet turns the primary ManiSkill/SAPIEN public-simulator route into a concrete non-evidence operator contract with official source anchors, provenance fields, task onboarding files, backend requirements, and strict gate order.
- The external fidelity provenance packet turns the missing platform physics/contact, paired-reset replay, operator independence, calibration basis, code/skill hashes, manifest declaration, and strict fidelity gate into concrete work orders while strict fidelity evidence remains false.
- The external fidelity acceptance draft pre-fills the tracked ManiSkill route with platform, backend, config-hash, task-binding, env-smoke, and metadata anchors, and now includes a fidelity acceptance promotion checklist that separates machine-prefilled readiness from independent operator signoff while remaining draft-only/non-evidence with all acceptance gates unaccepted.
- The external backend integration packet turns the missing non-template public-simulator backend into concrete work orders while strict backend readiness remains false.
- The ManiSkill reference backend readiness audit contract-qualifies an adapter-backed ManiSkill/SAPIEN backend candidate and MP4 writer path, but official collection and strict external evidence remain false until an accepted backend writes real renderable videos/logs under the strict gates.
- The ManiSkill reference collection preflight audit shows the explicit reference-backend/config/run-id/alias path reaches the fidelity-acceptance gate, but collection and strict evidence still remain false until platform fidelity provenance is accepted and real logs/videos/manifests exist.
- The external runner backend probe self-test exercises the actual collection runner with a temporary non-template backend, writes schema-valid temporary JSONL records and videos, and leaves the real manifest untouched while remaining non-evidence.
- The external pilot smoke packet adds a quarantined first-panel backend smoke test so an independent operator can test a real backend before official collection without letting pilot logs/videos count as evidence.
- The external method implementation packet turns the missing non-oracle baseline layer into concrete per-method work orders while strict adapter evidence remains missing.
- The planner-edge policy audit shows the local seam updates change future transition selection: over 1,680 local hard-slice planning frontiers, selected-edge utility improves by `+0.231`, success by `+0.080`, realized breach by `-0.075`, and executable-edge coverage by `+0.502` versus the strongest predecessor, while remaining non-external evidence.
- The generated external operator packet is a no-go handoff for independent validation: after materializing the high-fidelity route configs, it lists four generic pre-collection blockers, includes the ManiSkill fidelity metadata probe summary, and now exposes the tracked ManiSkill reference route where the backend/config/run-id/alias preflight has one remaining blocker, fidelity acceptance, without claiming evidence.
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

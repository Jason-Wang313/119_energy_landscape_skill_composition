# Haonan/Yilun Outreach Package

Purpose: turn the strengthened Paper 119 into a serious collaboration pitch while keeping the research agenda centered on adaptive physical world/action models for embodied agents.

## One-Line Positioning

Paper 119 is a local world/action-modeling interface for behavior-composition seams: given two skills, predict whether the handoff will work, diagnose why it may fail, choose repair/probe/abstain/transition, and use the outcome to improve future planning.

This framing is natural for Jason's agenda because it links action representation, prediction, failure diagnosis, repair, and transfer without turning the project into a narrow low-level controller paper.

## Why Haonan Is A Good First Contact

Current source anchors checked on 2026-06-26:

- Haonan's homepage says he works with Yilun Du and Jiajun Wu and focuses on multi-modal action composition: https://haonan16.github.io/
- The same page explicitly invites robotics and machine-learning collaborations by email.
- His listed research themes include multisensory learning and action composition across skills, action abstractions, and physics-inspired world models.
- CoStream composes simple independent behaviors through a shared action interface and reports real-world manipulation tasks: https://arxiv.org/abs/2606.26423
- OAT connects Haonan/Yilun to action tokenization and action abstractions: https://arxiv.org/abs/2602.04215
- SIMPACT connects Haonan/Yilun to simulation-in-the-loop action planning and physical reasoning: https://arxiv.org/abs/2512.05955

Best fit angle:

> CoStream asks how to compose behaviors. Paper 119 asks how to certify the seam between behaviors before committing to the next action.

That is the clean overlap. Do not pitch this as "contact-rich manipulation." Pitch it as a reliability layer for action composition.

## Why Yilun Might Care

Current source anchors checked on 2026-06-26:

- Yilun's homepage says his research focuses on generative models, decision making, robot learning, and embodied agents: https://yilundu.github.io/
- His stated research direction includes world models, planning, iterative reasoning, and composable generative models/energy landscapes.
- SIMPACT explicitly connects physical prediction through simulation with action planning.
- The 2026 robot world-model survey involving Yilun frames world models as predictive representations for robot policies, planning, simulation, evaluation, and data generation: https://arxiv.org/abs/2605.00080

Best fit angle:

> Paper 119 is not trying to be a new low-level controller. It is a small predictive model over action handoffs, expressed through energy landscapes, that decides when composition is reliable.

That is the bridge to Yilun. It should sound like compositional world/action modeling, not merely manipulation plumbing.

## What To Send

Do not start by attaching the full generated PDF alone.

Send:

- A short email.
- A 1-page project memo.
- A 4-page clean technical preview.
- One figure or 30-second GIF showing `skill i -> seam critic -> accept/repair/reject -> skill j`.
- Link to repo/logs only if the repo is clean enough to survive inspection.
- Keep the independent validation protocol, `results/external_operator_packet.md`, the ManiSkill fidelity metadata probe, the fidelity acceptance materializer, the ManiSkill render-video preflight with its renderer-failure classifier, the ManiSkill render machine qualification packet, the reference-adapter provenance catalog, the strict reference-adapter rejection gate, and the manifest assembly checklist ready as follow-up artifacts, not as first-email clutter.
- Keep the reviewer response packet ready as a private defense layer for likely objections, not as first-email clutter.

The full PDF can be offered after he shows interest.

## What Not To Say

Avoid:

- "All that is left is for you to do the real validation."
- "I want to work with you to get to Yilun."
- "This is already main-conference ready."
- "This is mainly about contact-rich manipulation."
- "I read many of your papers and this matches everything."
- A long list of Haonan/Yilun papers in the first email.

Mention at most one primary paper and one secondary touchpoint. The primary paper should be CoStream. SIMPACT or OAT can be a single sentence if needed.

## Short Email Draft

Subject: Seam certification for compositional robot behaviors

Hi Haonan,

I'm Jason Wang, an independent researcher working on adaptive physical world/action models for robot behavior composition.

I have been developing a local skill-seam action model: before chaining two learned skills, the system predicts whether the next skill's basin can take over, whether a small repair is enough, or whether the seam should be rejected and routed elsewhere. The current local evidence is strongest on hard handoff regimes where naive skill sequencing looks feasible but fails through basin mismatch, high-energy barriers, or contact-mode discontinuities.

I thought of your CoStream work because it makes behavior composition the right object of study. My project is complementary: it is not another behavior module, but a seam critic for deciding when composed behaviors should be accepted, repaired, probed, or abstained from.

I have a submission-shaped draft, a short memo, and an independent validation protocol/operator packet. I would really value your advice on whether this seam-certification layer would be useful to test in a CoStream-style behavior-composition setting. If it seems worth exploring, I would be happy to do the implementation, analysis, writing, and ablations around the seam critic.

Would you be open to a short chat?

Best,  
Jason

## Slightly More Technical Email Draft

Subject: Energy-seam certification for behavior composition

Hi Haonan,

I'm Jason Wang. I have been working on a project that treats skill handoff as a local world/action-modeling problem: given skill `i` and skill `j`, estimate terminal/basin overlap, barrier height, descent continuity, repair cost, and calibrated seam risk before committing to the transition.

The resulting composer chooses among accept, repair, probe, abstain, or alternate transition. In a frozen local suite, it improves hard-slice success and utility over option-graph, TAMP-feasibility, diffusion-stitching, CEM, residual-repair, and energy-heuristic baselines, while reducing seam failures and realized breach. The local rows also expose diagnostic labels, seam decisions, and planner-edge updates, with a consistency audit over those mechanism outputs. I am keeping the claim bounded until external validation: the contribution is seam certification for composition, not a universal manipulation policy.

CoStream seems like a particularly natural point of contact because it composes semantic, predictive, and reactive behaviors through a shared action interface. My question is whether a seam critic of this kind could be useful as a reliability layer for behavior composition.

I have a short technical memo, a validation protocol, and an operator packet that currently marks the external run as no-go until real backend/config/fidelity gates are cleared. I would love your advice on whether the idea is worth testing, and I would take on the implementation/analysis/writing burden if there is a clean collaboration path.

Best,  
Jason

## One-Page Memo Outline

Title:

> Local World/Action Models for Robot Skill Seams

Problem:

- Independently competent skills can fail when composed.
- A graph edge can be legal while the handoff is physically invalid.
- Failures appear as basin mismatch, high-energy barriers, contact-mode discontinuity, or unsafe repair.

Method:

- Model the seam between skill `i` and skill `j`.
- Estimate basin overlap, barrier height, descent continuity, repair cost, and seam risk.
- Decide accept, repair, probe, abstain, or alternate transition.

Claim:

- Improves behavior composition when seam quantities are estimable.
- Does not claim universal control, new low-level skill learning, or hardware safety without external validation.

Current evidence:

- Frozen local suite: 12 methods, 6 task families, 8 seam regimes, 5 splits, 10 paired seeds.
- Strongest non-oracle comparator: `proposed_energy_landscape_composer_v4_1`.
- Hard success: `0.80171` vs `0.71711`.
- Hard utility: `0.88827` vs `0.65310`.
- Reduces seam failure, barrier violation, damage, risk calibration error, and realized breach.
- Diagnostic audit: exported failure labels, seam decisions, and planner-edge updates have zero rule mismatches over 230,400 local rows.

Validation ask:

- Test as a seam critic in a real or high-fidelity behavior-composition stack.
- Same skill library and paired resets across baselines.
- Report success, utility, seam failure, breach, coverage, calibration, and videos.
- Use the independent operator packet, reference-adapter provenance catalog, strict reference-adapter rejection gate, and manifest assembly checklist as Jason-owned validation scaffolding; do not frame Haonan as responsible for supplying the missing proof.

Why it fits CoStream:

- CoStream composes behaviors.
- This method audits the reliability of behavior handoffs.
- The collaboration question is whether a seam critic improves composition robustness under perturbations, precision assembly, and object-transfer tasks.

## Meeting Agenda

Use a 20-minute meeting:

- 2 min: problem setup, not a long personal intro.
- 4 min: show seam-failure example.
- 5 min: explain energy-seam score and accept/repair/reject decision.
- 4 min: show local evidence and honest limitation.
- 3 min: ask whether this would be useful in a CoStream-style stack.
- 2 min: agree next step or gracefully close.

## If He Responds Positively

Send:

- 4-page preview.
- 1-page validation protocol.
- `results/external_operator_packet.md`, if he asks how the external run would actually be gated.
- Figure/GIF.
- Link to selected logs and code.

Ask:

> Which behavior-composition setting would be the cleanest falsification test for a seam critic?

Do not ask:

> Can you do the real validation for me?

## If He Does Not Respond

Wait 7 to 10 days, then send one follow-up with a concrete artifact:

Subject: Re: Seam certification for compositional robot behaviors

Hi Haonan,

Just a brief follow-up. I made a one-page memo and validation protocol for the seam-certification idea. The core question is whether a behavior-composition stack benefits from a separate handoff critic that can accept, repair, probe, or reject seams before execution.

No worries if now is not a good time. I would still appreciate any quick pointer on whether this direction seems scientifically useful or misguided.

Best,  
Jason

## Final Recommendation

Use Paper 119 as the outreach paper, but only after the one-page memo and 4-page preview are polished. Mention CoStream as the primary fit. Mention SIMPACT or OAT only if the email needs a second anchor. Do not mention many papers. A focused, useful ask is stronger than a broad display of familiarity.

The reviewer response packet is for Jason's preparation: it helps answer why this is a skill-seam world/action model, why the evidence is still bounded, and why Haonan should be asked for fit/falsification advice rather than for the missing proof layer.

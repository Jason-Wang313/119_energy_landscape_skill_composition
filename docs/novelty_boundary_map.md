# Novelty Boundary Map

## What This Paper Can Claim

- A local world/action model for skill seams can reduce handoff failures under hidden barrier, basin-shift, contact-mode, dynamics-shift, observability, and calibration stress.
- Basin overlap, barrier height, descent continuity, seam repair, terminal-state sampling, contact guards, fixed-risk gating, calibration, diagnostic labels, and planner-edge memory all contribute locally.
- The local benchmark supports this claim against option graphs, diffusion stitching, CEM trajectory composition, residual RL composition, TAMP-style feasibility screening, stable-DMP handoff, an energy-compatibility heuristic, and the prior proposed energy composer.

## What This Paper Cannot Claim

- Real-world robot deployment readiness.
- State-of-the-art skill composition.
- A new low-level skill learner.
- A universal energy-model theory or full robot world model.

## Boundary Sentence

This work studies how to decide whether independently available skills are locally acceptable to compose by modeling the seam as a small action-conditioned physical prediction problem: will the handoff fail, why, should the planner repair/probe/abstain/transition, and what should be remembered for later plans. Its barrier-certified energy terms are one implementation of that interface; it does not propose a new skill primitive, a universal planner, or hardware-validated safety.

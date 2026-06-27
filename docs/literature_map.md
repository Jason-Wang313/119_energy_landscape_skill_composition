# Literature Map

## Crowded Areas

- Energy-based robot policies.
- Dynamic movement primitives and energy-efficient motion planning.
- Skill sequencing, option graphs, and concurrent task planning.
- Diffusion and trajectory optimization for skill stitching.
- Residual RL skill composition.

## Local Novelty Boundary

The paper should claim barrier-certified energy-landscape compatibility and repair for skill seams. It should not claim a new low-level controller, a universal energy-based policy framework, or real-robot skill-composition leadership.

The closest defensible contribution is: use basin-overlap, barrier-height, descent-continuity, contact/dynamics guards, calibration, repair, and fixed-risk abstention to decide whether separately learned robot skills can be chained without crossing unsafe high-energy seams.

## Evidence Needed For Final Main-Conference Readiness

- Transfer to an external benchmark or high-fidelity simulator.
- Real robot chained-skill failures with replayable logs.
- Manual related-work synthesis against accepted skill-composition baselines.
- Stronger ablations tying learned energy basins to actual controller artifacts.
- Released skill-energy checkpoints and manifest-declared independent baseline evidence from real external runs.

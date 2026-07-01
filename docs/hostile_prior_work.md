# Hostile Prior Work

The hostile set contains energy-based policies, skill composition, dynamic movement primitives, concurrent task planning, and broader compositional-learning threats. The strongest local threats include:

- Composable energy policies for reactive motion generation and reinforcement learning (2023)
- Development of compositionality through interactive learning of language and action of robots (2025)
- Generalizing kinematic skill learning to energy efficient dynamic motion planning using optimized Dynamic Movement Primitives (2025)
- Bidirectional Progressive Neural Networks With Episodic Return Progress for Emergent Task Sequencing and Robotic Skill Transfer (2024)
- Autonomous Runtime Composition of Sensor-Based Skills Using Concurrent Task Planning (2021)

Novelty boundary: the paper is not "energy-based robot learning" broadly and not "skill sequencing with another score." The defensible contribution is a local world/action model for skill seams: predict whether a handoff will fail, diagnose the likely basin/barrier/contact/dynamics reason, choose repair/probe/abstain/transition, and preserve the outcome as planner-edge evidence for future planning. The energy-landscape quantities are the implementation used to make that seam model testable.

Remaining hostile-review weakness: the evidence is local. A reviewer can still demand external benchmark transfer, real robot validation, released checkpoints/logs, and manifest-declared independent baseline evidence from real external runs before accepting a main-conference claim.

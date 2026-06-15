# Paper 119 Rebuild Plan

Started: 2026-06-15 04:07:00 +0100

## Goal

Rebuild `energy_landscape_skill_composition` from an archive memo into a real local empirical submission package. The paper must test whether robot skills compose more robustly when their energy landscapes are checked for basin compatibility, barrier height, and descent continuity rather than simply sequenced as policy modules.

## Claim To Test

Skill composition fails at seams: individually competent skills can create high-energy discontinuities, barrier crossings, or unstable handoff states. An energy-landscape composition rule should prefer skills whose terminal basin overlaps the next skill's attraction basin and should reject or repair compositions with high seam energy.

## Evidence Design

- Benchmark dimensions: 6 manipulation/mobile-manipulation task families, 8 skill-composition shift regimes, 5 deployment splits, 9 composition methods, 7 paired seeds, 72 rollout episodes per group.
- Methods: greedy module sequencing, behavior-cloned skill chaining, option-graph planning, diffusion skill stitching, CEM trajectory composition, residual RL composition, energy-compatibility heuristic, proposed energy-landscape composer, and oracle basin composer.
- Metrics: task success, seam-failure rate, barrier-violation rate, basin-alignment score, descent-continuity score, damage rate, composition/search cost, and paired-seed wins.
- Stress sweep: increasing seam discontinuity and hidden barrier height.
- Ablations: remove basin overlap, remove barrier-height term, remove descent-continuity term, remove energy repair, remove terminal-state sampler, and compatibility-only heuristic.

## Terminal Gates

The paper may become `STRONG_REVISE` only if all gates clear against the strongest non-oracle baseline:

- Combined-stress success margin is at least 0.030.
- Seam-failure rate decreases by at least 0.020.
- Barrier-violation rate decreases by at least 0.020.
- Basin-alignment and descent-continuity scores increase by at least 0.030.
- Damage rate decreases by at least 0.010.
- Composition/search cost does not increase.
- Paired-seed success wins are at least 5/7.
- Best ablation trails the full method by at least 0.020.

If any gate fails, the terminal decision remains `KILL_ARCHIVE` with the negative result documented.

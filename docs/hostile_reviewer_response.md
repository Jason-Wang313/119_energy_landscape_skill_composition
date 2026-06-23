# Hostile Reviewer Response

## Attack: This is just the previous energy composer with a new name.

Response: The strongest non-oracle baseline is the prior proposed method, `proposed_energy_landscape_composer_v4_1`, not a weak heuristic. The v5 method still improves hard success by `0.084598` and hard utility by `0.235170`, with `10/10` paired-seed wins.

## Attack: The method may win by spending more search.

Response: The proposed composer lowers composition cost by `0.045838` relative to the strongest baseline. The reported utility also penalizes cost and risk, so the local gain is not explained by more expensive search.

## Attack: Energy terms may be decorative.

Response: The ablation suite removes basin overlap, barrier height, descent continuity, seam repair, terminal sampling, contact guard, fixed-risk gate, calibration, and repair memory. The best removed-component variant still trails the full method by `0.028125` success and `0.043490` utility.

## Attack: Fixed-risk gating can hide failures by abstaining.

Response: The fixed-risk audit reports coverage, breach, gated success, gated utility, and abstention effects. Under risk budget `0.15`, coverage is `0.863021`, breach is `0.000302`, and gated success is `0.760108`; the abstention tradeoff is not hidden.

## Attack: The benchmark is still not enough for ICLR main.

Response: Agreed. The terminal decision is `STRONG_REVISE`, not final acceptance readiness. The work still needs real robot or accepted high-fidelity validation, independent baselines, released checkpoints/logs, videos, and full manual related work.

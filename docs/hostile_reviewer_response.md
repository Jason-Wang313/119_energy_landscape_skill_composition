# Hostile Reviewer Response

## Attack: This is just a compatibility heuristic.

Response: The strongest non-oracle baseline is `energy_compatibility_heuristic`. The proposed composer beats it by `0.110 +/- 0.006` success and lowers seam failures, barrier violations, damage, and cost.

## Attack: The method may win by spending more search.

Response: The proposed composer lowers composition cost by `0.091` relative to the strongest baseline, so the local gain is not explained by more expensive search.

## Attack: Energy terms may be decorative.

Response: Removing descent continuity, energy repair, barrier height, terminal-state sampling, basin overlap, or full repair reduces combined-stress success. The best removed-component variant trails by `0.056`.

## Attack: The benchmark is still not enough for ICLR main.

Response: Agreed. The terminal decision is `STRONG_REVISE`, not final acceptance readiness. The work still needs real robot or external high-fidelity validation.

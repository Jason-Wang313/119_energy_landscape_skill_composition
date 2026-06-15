# Claims

- Mechanism claim: skill composition fails when individually competent skills create high-energy seams; basin overlap, barrier height, and descent continuity should be checked before chaining.
- Evidence claim: the v4 benchmark tests 6 task families, 8 seam/barrier regimes, 5 deployment splits, 9 composition methods, and 7 paired seeds.
- Result claim: under combined stress, the proposed composer reaches `0.725 +/- 0.004` success versus `0.614 +/- 0.003` for `energy_compatibility_heuristic`, with `0.110 +/- 0.006` paired success gain and 7/7 seed wins.
- Mechanism-diagnostic claim: the proposed composer lowers seam failures by `0.087`, lowers barrier violations by `0.101`, improves basin alignment by `0.206`, improves descent continuity by `0.209`, lowers damage by `0.024`, and lowers composition cost by `0.091`.
- Scope claim: the evidence supports `STRONG_REVISE`, not final ICLR-main readiness.
- Unsupported claim explicitly avoided: no claim of state-of-the-art real-robot skill composition.

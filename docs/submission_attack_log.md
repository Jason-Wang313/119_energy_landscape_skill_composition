# Submission Attack Log

## Attack 1: Strongest baseline selection

Mitigation: the strongest non-oracle baseline is selected after the full run from the hard aggregate. It is the prior proposed composer, `proposed_energy_landscape_composer_v4_1`, so the v5 claim is measured against a hard internal baseline rather than a weak strawman.

## Attack 2: Success-only claim

Mitigation: the paper reports success, utility, seam failure, barrier violation, basin alignment, descent continuity, damage, composition cost, energy-model error, risk calibration error, realized seam breach, paired-seed wins, ablations, stress sweeps, fixed-risk coverage, breach, gated success, and failure cases.

## Attack 3: Decorative energy terms

Mitigation: all major energy components are ablated. The best removed-component variant trails the full method by `0.028125` success and `0.043490` utility.

## Attack 4: Risk gate hides weakness

Mitigation: the fixed-risk section reports both coverage and breach. At risk budget `0.15`, coverage is `0.863021` and breach is `0.000302`.

## Attack 5: Overclaiming ICLR readiness

Mitigation: all docs and the manuscript state `STRONG_REVISE`, not ICLR-main-ready. Real robot or accepted high-fidelity validation, released checkpoints/logs, independent baselines, videos, and full manual related work remain required.

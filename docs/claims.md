# Claims

- Agenda framing claim: the paper studies a local world/action model at robot skill seams: before chaining two skills, predict handoff failure, diagnose likely basin/barrier/descent/contact uncertainty, choose accept/repair/probe/abstain/transition, and update planner-edge beliefs for future planning. Energy landscapes are the implementation vocabulary; the scientific object is the skill-seam action model.
- Mechanism claim: skill composition fails when individually competent skills create high-energy seams; basin overlap, barrier height, descent continuity, contact/dynamics guards, calibration, and fixed-risk acceptance should be checked before chaining.
- Evidence claim: the v5 benchmark tests 6 task families, 8 seam regimes, 5 deployment splits, 12 methods, 10 paired seeds, 230,400 main episode cells, 38,400 ablation cells, 161,280 stress cells, and 107,520 fixed-risk cells.
- Result claim: on hard aggregate settings, `barrier_certified_energy_composer_v5` reaches `0.801711` success versus `0.717113` for `proposed_energy_landscape_composer_v4_1`, with `0.084598` paired success margin and `10/10` paired-seed wins.
- Utility claim: on the same hard aggregate, v5 reaches `0.888270` utility versus `0.653100` for the strongest non-oracle baseline, with `0.235170` paired utility margin and `10/10` paired-seed wins.
- Mechanism-diagnostic claim: v5 lowers seam failures by `0.049123`, barrier violations by `0.040869`, damage by `0.005790`, composition cost by `0.045838`, risk calibration error by `0.010549`, and realized seam breach by `0.075646`; it improves basin alignment by `0.080008` and descent continuity by `0.078090`.
- Planner-memory claim: the local rows expose diagnostic labels, seam decisions, and planner-edge updates, so the method is evaluated as a predict-diagnose-act-update interface rather than only as an energy score.
- Fixed-risk claim: with a strict seam-risk budget of `0.15`, v5 covers `0.863021` of candidate seams, breaches the budget at `0.000302`, and achieves gated success `0.760108`.
- Scope claim: the evidence supports `STRONG_REVISE`, not final ICLR-main readiness.
- Unsupported claim explicitly avoided: no claim of state-of-the-art real-robot skill composition, hardware safety, or universal energy-model stability.

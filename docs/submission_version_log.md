# Submission Version Log

## Superseded Local Builds

- Earlier archive and local-continuation builds were superseded by the v5 expansion.
- Their useful role is now historical only: they established the paper topic, rough mechanism, and prior proposed baseline.
- Their old page counts, hashes, row counts, and baseline statistics should not be used for the current paper state.

## v5_expanded

- Rebuilt the method as `barrier_certified_energy_composer_v5`.
- Added basin-overlap posterior checks, barrier/descent seam tests, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, fixed-risk acceptance, and repair memory.
- Expanded to 12 methods, 10 paired seeds, 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 failure cases.
- Selected the strongest non-oracle baseline from the hard aggregate; it is `proposed_energy_landscape_composer_v4_1`.
- Reported hard success, hard utility, mechanism diagnostics, ablations, stress endpoints, fixed-risk coverage/breach/gated success, and scope blockers.
- Generated a 25-page ICLR-style PDF with bright boxed clickable citations.
- Terminal decision remains STRONG_REVISE.
- ICLR main readiness remains no pending real robot or accepted high-fidelity validation, released checkpoints/logs, hardware videos, independent baselines, and full manual related work.

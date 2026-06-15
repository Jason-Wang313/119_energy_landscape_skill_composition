# Paper 119 ICLR Submission Execution Plan

Created: 2026-06-15

Target: `119_energy_landscape_skill_composition`

## Goal

Re-audit and harden Paper 119 into the strongest honest submission package possible before advancing to Paper 120. The work must be evidence-bound: the paper can remain a serious `STRONG_REVISE` candidate if local gates pass, but it must not be called ICLR-main ready without real robot validation or external high-fidelity simulator validation.

## Current Starting Point

- Existing version: v4 local evidence rebuild.
- Current terminal decision: `STRONG_REVISE`.
- Current ICLR-main readiness: no.
- Current design: 6 task families x 8 skill-composition regimes x 5 deployment splits x 9 methods x 7 paired seeds x 72 rollout episodes per group.
- Current raw task/regime/split/seed rows: 15120.
- Current ablation task/regime/seed rows: 2352.
- Current stress sweep seed rows: 210.
- Current failure cases: 4.
- Strongest non-oracle baseline: `energy_compatibility_heuristic`.
- Current core margin: proposed `0.725 +/- 0.004` versus baseline `0.614 +/- 0.003`, paired gain `0.110 +/- 0.006`, wins `7/7`.

## Execution Order

1. Verify the repo is clean and the public GitHub repo is reachable.
2. Compile `src/run_experiment.py` before running any experiment.
3. Run the experiment once in low-RAM, single-threaded mode and capture a continuation log in the factory `logs` directory.
4. Audit generated CSVs for row counts, numeric gates, strongest-baseline selection, pairwise statistics, ablations, stress sweep coverage, and failure-case coverage.
5. Patch only recoverable gaps. The known likely recoverable gap is thin failure-case coverage, which should be expanded to at least 8 specific limits/failures if the rest of the evidence remains stable.
6. Re-run after any patch and re-audit from fresh outputs.
7. Update manuscript/status docs to v4.1 with explicit evidence limits and no inflated readiness language.
8. Build the LaTeX paper and copy only the numbered PDF to `C:/Users/wangz/Downloads/119.pdf`.
9. Verify LaTeX/BibTeX logs, PDF hash, PDF size, and absence of `C:/Users/wangz/Desktop/119.pdf`.
10. Commit and push Paper 119 to its public GitHub repo.
11. Update root ledgers: `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

## Evidence Gates

The local evidence gate passes only if all of the following hold against the strongest non-oracle baseline:

- Combined-stress success margin is at least `0.030`.
- Seam-failure rate decreases by at least `0.020`.
- Barrier-violation rate decreases by at least `0.020`.
- Basin-alignment score increases by at least `0.030`.
- Descent-continuity score increases by at least `0.030`.
- Damage rate decreases by at least `0.010`.
- Composition/search cost does not increase.
- Paired-seed success wins are at least `5/7`.
- Best ablation trails the full method by at least `0.020`.
- Raw coverage remains at least 15120 task/regime/split/method/seed rows.
- Ablation coverage remains at least 2352 task/regime/seed rows.
- Stress-sweep coverage remains at least 210 method/stress/seed rows.
- Failure-case coverage is at least 8 named cases after v4.1 hardening.

## Decision Policy

- Mark `STRONG_REVISE` if all local evidence gates pass and missing external validation is clearly stated.
- Mark `KILL_ARCHIVE` if the experiment or audit fails any local evidence gate after recoverable fixes.
- Never mark `ICLR-main ready` unless actual real robot or external high-fidelity validation evidence is present in the repo.

## Output Rules

- Numbered PDF output must be `C:/Users/wangz/Downloads/119.pdf`.
- Do not copy any PDF to the visible Desktop.
- Keep the child repo public on GitHub.
- Keep root ledgers synchronized immediately after the child repo is pushed.

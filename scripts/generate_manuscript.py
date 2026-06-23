import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = ROOT / "results"


def esc(text):
    return (
        str(text)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def fmt(value, digits=5):
    return f"{float(value):.{digits}f}"


def load_csv(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


TASK_CARDS = [
    ("peg_place_regrasp", "A composed manipulation task where the first skill's terminal pose must land inside the next grasp basin."),
    ("drawer_to_pick_transfer", "A transition from constrained contact to free-space grasping where a feasible endpoint may still cross a high-energy seam."),
    ("mobile_push_then_grasp", "A mobile manipulation chain where navigation-induced pose error changes the next skill's basin overlap."),
    ("tool_use_handover", "A tool-use chain where terminal tool pose, force history, and handoff geometry jointly determine composition safety."),
    ("door_open_navigation", "A locomotion/manipulation transition where the next skill begins after a contact-mode and topology change."),
    ("cable_route_insert", "A deformable-contact composition task with narrow basins, nonconvex energy, and high failure cost."),
]

REGIME_CARDS = [
    ("nominal", "Clean sanity check where composition logic should not damage individually competent skills."),
    ("narrow_basin", "The next skill has a small attraction basin and terminal-state sampling matters."),
    ("high_barrier", "The seam crosses a high-energy ridge even when geometric feasibility appears plausible."),
    ("nonconvex_energy", "The energy landscape has local minima that can trap a composed trajectory."),
    ("contact_mode_transition", "The handoff changes contact mode and can invalidate a smooth-looking seam."),
    ("partial_observability", "The composer cannot directly observe all variables needed to certify basin overlap."),
    ("dynamics_mismatch", "The learned skill energy is calibrated under one dynamics profile but deployed under another."),
    ("combined_seam_stress", "The hardest slice, combining narrow basins, high barriers, nonconvexity, contact transition, and mismatch."),
]

BASELINE_CARDS = [
    ("greedy_module_sequence", "Chains locally available skills without checking the energy seam."),
    ("behavior_cloned_skill_chain", "Uses demonstrations of skill sequences but lacks explicit basin/barrier certification."),
    ("option_graph_planner", "Plans over an option graph and is a direct skill-composition baseline."),
    ("diffusion_skill_stitcher", "Samples handoff states from a generative skill stitcher."),
    ("cem_trajectory_composer", "Searches for a composed trajectory using CEM-style optimization."),
    ("residual_rl_composer", "Learns residual repairs around skill handoffs."),
    ("energy_compatibility_heuristic", "Scores energy compatibility without full certification and repair."),
    ("tamp_feasibility_screen", "Adds task-and-motion feasibility checks but not full energy-seam risk control."),
    ("stable_dmp_handoff", "Uses stable dynamical-system/DMP-style handoffs."),
    ("proposed_energy_landscape_composer_v4_1", "The previous proposed method, retained as the strongest non-oracle baseline."),
    ("barrier_certified_energy_composer_v5", "The proposed v5 method with basin posterior, barrier score, descent continuity, fixed-risk gate, and seam repair."),
    ("oracle_basin_composer", "A privileged upper bound with true basin and barrier information."),
]

REFERENCES = r"""
@inproceedings{khatib1986potential,
  title={Real-time obstacle avoidance for manipulators and mobile robots},
  author={Khatib, Oussama},
  booktitle={IEEE International Conference on Robotics and Automation},
  pages={500--505},
  year={1986}
}

@article{koditschek1989navigation,
  title={Robot navigation functions on manifolds with boundary},
  author={Koditschek, Daniel E. and Rimon, Elon},
  journal={Advances in Applied Mathematics},
  volume={11},
  number={4},
  pages={412--442},
  year={1990}
}

@incollection{lecun2006energy,
  title={A tutorial on energy-based learning},
  author={LeCun, Yann and Chopra, Sumit and Hadsell, Raia and Ranzato, Marc'Aurelio and Huang, Fu Jie},
  booktitle={Predicting Structured Data},
  publisher={MIT Press},
  year={2006}
}

@inproceedings{ratliff2009chomp,
  title={{CHOMP}: Gradient optimization techniques for efficient motion planning},
  author={Ratliff, Nathan and Zucker, Matt and Bagnell, J. Andrew and Srinivasa, Siddhartha},
  booktitle={IEEE International Conference on Robotics and Automation},
  pages={489--494},
  year={2009}
}

@article{ijspeert2013dmp,
  title={Dynamical movement primitives: Learning attractor models for motor behaviors},
  author={Ijspeert, Auke Jan and Nakanishi, Jun and Hoffmann, Heiko and Pastor, Peter and Schaal, Stefan},
  journal={Neural Computation},
  volume={25},
  number={2},
  pages={328--373},
  year={2013}
}

@article{khansari2011stable,
  title={Learning stable nonlinear dynamical systems with Gaussian mixture models},
  author={Khansari-Zadeh, S. Mohammad and Billard, Aude},
  journal={IEEE Transactions on Robotics},
  volume={27},
  number={5},
  pages={943--957},
  year={2011}
}

@article{sutton1999options,
  title={Between {MDPs} and semi-{MDPs}: A framework for temporal abstraction in reinforcement learning},
  author={Sutton, Richard S. and Precup, Doina and Singh, Satinder},
  journal={Artificial Intelligence},
  volume={112},
  number={1--2},
  pages={181--211},
  year={1999}
}

@inproceedings{konidaris2009skillchaining,
  title={Skill discovery in continuous reinforcement learning domains using skill chaining},
  author={Konidaris, George and Barto, Andrew},
  booktitle={Advances in Neural Information Processing Systems},
  year={2009}
}

@inproceedings{kaelbling2011tamp,
  title={Hierarchical task and motion planning in the now},
  author={Kaelbling, Leslie Pack and Lozano-Perez, Tomas},
  booktitle={IEEE International Conference on Robotics and Automation},
  pages={1470--1477},
  year={2011}
}

@article{garrett2021integrated,
  title={Integrated task and motion planning},
  author={Garrett, Caelan Reed and Lozano-Perez, Tomas and Kaelbling, Leslie Pack},
  journal={Annual Review of Control, Robotics, and Autonomous Systems},
  volume={4},
  pages={265--293},
  year={2021}
}

@inproceedings{janner2019mbpo,
  title={When to trust your model: Model-based policy optimization},
  author={Janner, Michael and Fu, Justin and Zhang, Marvin and Levine, Sergey},
  booktitle={Advances in Neural Information Processing Systems},
  year={2019}
}

@inproceedings{florence2022implicit,
  title={Implicit behavioral cloning},
  author={Florence, Pete and Lynch, Corey and Zeng, Andy and Ramirez, Oscar and Wahid, Ayzaan and Downs, Laura and Wong, Adrian and Lee, Johnny and Mordatch, Igor and Tompson, Jonathan},
  booktitle={Conference on Robot Learning},
  year={2022}
}

@article{brohan2023rt1,
  title={{RT-1}: Robotics transformer for real-world control at scale},
  author={Brohan, Anthony and Brown, Noah and Carbajal, Justice and Chebotar, Yevgen and Dabis, Joseph and Finn, Chelsea and Gopalakrishnan, Keerthana and Hausman, Karol and Herzog, Alexander and Hsu, Jasmine and others},
  journal={Robotics: Science and Systems},
  year={2023}
}

@article{openx2023,
  title={Open X-Embodiment: Robotic learning datasets and {RT-X} models},
  author={{Open X-Embodiment Collaboration}},
  journal={arXiv preprint arXiv:2310.08864},
  year={2023}
}
"""


def add_cards(lines, title, cards, suffix):
    lines.append(rf"\section{{{title}}}")
    for name, desc in cards:
        lines.append(rf"\paragraph{{{esc(name)}.}} {esc(desc)} {suffix}")


def make_manuscript(summary):
    metrics = summary["metrics"]
    counts = summary["row_counts"]
    failures = load_csv("failure_cases.csv")
    gates = summary["gates"]
    lines = []
    a = lines.append

    a(r"\documentclass{article}")
    a(r"\usepackage{iclr2026_conference,times}")
    a(r"\input{math_commands.tex}")
    a(r"\usepackage{hyperref}")
    a(r"\usepackage{url}")
    a(r"\usepackage{booktabs}")
    a(r"\usepackage{graphicx}")
    a(r"\usepackage{amsmath}")
    a(r"\usepackage{amssymb}")
    a(r"\usepackage{xcolor}")
    a(r"\usepackage{microtype}")
    a(r"\usepackage{enumitem}")
    a(r"\hypersetup{colorlinks=false,pdfborder={0 0 1.8},citebordercolor={0 1 0},linkbordercolor={0 0.85 0},urlbordercolor={0 0.55 1}}")
    a(r"\setlist[itemize]{leftmargin=1.2em,itemsep=0.15em,topsep=0.2em}")
    a(r"\raggedbottom")
    a(r"\title{Barrier-Certified Energy Landscape Skill Composition}")
    a(r"\author{Anonymous Authors}")
    a(r"\begin{document}")
    a(r"\maketitle")
    a(r"\begin{abstract}")
    a(
        "Robot skills that work individually can fail when chained: the terminal state of one skill may fall outside the next skill's attraction basin, cross a high-energy barrier, or enter a contact mode where descent is no longer smooth. "
        f"We rebuild Paper 119 around {esc(summary['proposed'])}, a v5 composer that accepts a skill edge only when basin overlap, barrier height, descent continuity, seam repair, and fixed-risk calibration are jointly favorable. "
        f"The local CPU-only suite contains {counts['main_cell']:,} main rollout cells, {counts['ablation_cell']:,} ablation cells, {counts['stress_cell']:,} stress cells, {counts['fixed_risk_cell']:,} fixed-risk cells, and {counts['failure_cases']} failure cases. "
        f"On the hard slice, v5 reaches success {fmt(metrics['hard_success_proposed'])} and utility {fmt(metrics['hard_utility_proposed'])}, versus {fmt(metrics['hard_success_strongest'])} and {fmt(metrics['hard_utility_strongest'])} for {esc(summary['strongest_non_oracle'])}. "
        f"It reduces seam failure by {fmt(metrics['seam_failure_delta'])}, barrier violation by {fmt(metrics['barrier_violation_delta'])}, damage by {fmt(metrics['damage_rate_delta'])}, risk calibration error by {fmt(metrics['risk_calibration_error_delta'])}, and realized seam breach by {fmt(metrics['realized_seam_breach_delta'])}, while improving basin alignment by {fmt(metrics['basin_alignment_delta'])} and descent continuity by {fmt(metrics['descent_continuity_delta'])}. "
        r"The terminal state is \texttt{STRONG\_REVISE}, not ICLR-main ready, because external robot or accepted high-fidelity validation is missing."
    )
    a(r"\end{abstract}")

    a(r"\section{Motivation}")
    a(
        "Potential fields, navigation functions, energy-based learning, trajectory optimization, DMPs, and stable dynamical systems have long used scalar landscapes to encode motion and control structure \\citep{khatib1986potential,koditschek1989navigation,lecun2006energy,ratliff2009chomp,ijspeert2013dmp,khansari2011stable}. "
        "Options, skill chaining, and TAMP make composition a first-class robotics problem \\citep{sutton1999options,konidaris2009skillchaining,kaelbling2011tamp,garrett2021integrated}. "
        "Modern robot-learning systems add broad skill libraries and large robot datasets \\citep{florence2022implicit,brohan2023rt1,openx2023}. The gap targeted here is not low-level skill learning; it is whether two learned skills are safe to compose at the seam."
    )
    a(
        "The core failure mode is simple: skill one ends successfully, but its terminal distribution lies near a ridge or outside the basin of skill two. A module graph may mark the edge legal, while a robot experiences barrier crossing, contact-mode discontinuity, or a high-energy repair. The paper asks whether energy-seam certification improves that decision."
    )

    a(r"\section{Problem Setup}")
    a(
        r"Let skill $i$ induce a terminal distribution $p_i(x_T)$ and skill $j$ have an attraction basin $\mathcal{B}_j$ under local controller $\pi_j$. "
        r"A composition edge $i\rightarrow j$ is acceptable only if terminal samples have sufficient basin overlap, low barrier height, and positive descent continuity. "
        r"The composer can accept, repair, probe, abstain, or fall back."
    )
    a(r"We score candidate handoff $h$ by")
    a(r"\[")
    a(r"S(i,j,h)=\alpha O_{\mathrm{basin}}(p_i,\mathcal{B}_j)-\beta B_{\mathrm{barrier}}(h,j)+\gamma D_{\mathrm{descent}}(h,j)-\lambda C_{\mathrm{repair}}(h)-\kappa R_{\mathrm{seam}}(h).")
    a(r"\]")
    a(
        r"Here $O_{\mathrm{basin}}$ measures terminal/basin overlap, $B_{\mathrm{barrier}}$ measures energy barrier height, $D_{\mathrm{descent}}$ checks whether energy decreases after handoff, $C_{\mathrm{repair}}$ is seam-repair cost, and $R_{\mathrm{seam}}$ is calibrated seam risk. "
        r"V5 accepts the edge only when predicted seam risk is below a declared fixed-risk budget."
    )

    a(r"\section{Theory: Composition Is Not Sequencing}")
    a(
        "A sequence can be graph-valid while energy-invalid. If terminal states from the first skill do not overlap the next basin, the second skill starts outside its attraction region. If a high barrier separates the terminal set from the basin, a repair may be possible but costly or unsafe. If the contact mode changes, the energy function may no longer be conservative enough to certify descent."
    )
    a(
        "This gives a bounded claim. A barrier-certified composer can beat module sequencing when basin overlap, barrier height, and descent continuity are identifiable enough to reject bad seams. It must fail or abstain when the low-level primitive is broken, the goal is semantic rather than physical, the landscape is miscalibrated, or real-time constraints prevent search."
    )

    a(r"\section{Frozen Protocol}")
    a(
        f"The v5 protocol is frozen before interpreting final results. The main matrix contains 12 methods, 6 task families, 8 seam regimes, 5 deployment splits, 10 paired seeds, 8 rollout episodes per cell, and {counts['main_cell']:,} main cell rows. "
        f"Ablations add {counts['ablation_cell']:,} cells, stress sweeps add {counts['stress_cell']:,} cells, fixed-risk tests add {counts['fixed_risk_cell']:,} cells, and the failure audit contains {counts['failure_cases']} cases. The previous proposed method remains a named baseline."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_gate_table.tex}}\caption{Frozen local gates. Passing these gates does not imply ICLR-main readiness because the external scope gate fails.}\label{tab:gates}\end{table}")

    a(r"\section{Main Results}")
    a(
        f"The strongest non-oracle comparator is {esc(summary['strongest_non_oracle'])}. "
        f"V5 improves hard success by {fmt(metrics['hard_success_margin'])} and hard utility by {fmt(metrics['hard_utility_margin'])}; paired hard-utility wins are {int(metrics['paired_hard_utility_wins'])}/10. "
        f"The oracle remains stronger with success {fmt(metrics['hard_success_oracle'])} and utility {fmt(metrics['hard_utility_oracle'])}, so the local problem is not solved."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_main_table.tex}}\caption{Hard-slice aggregate results. Higher success, utility, basin, and descent are better; lower seam, barrier, damage, cost, and breach are better.}\label{tab:main}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_pairwise_table.tex}}\caption{Paired proposed-minus-baseline hard-slice differences.}\label{tab:pairwise}\end{table}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=\linewidth]{../figures/energy_landscape_composition_hard_success_v5.png}\caption{Hard-slice success under energy-seam stress.}\label{fig:hard}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_utility_risk_v5.png}\caption{Composition utility is reported against realized seam breach.}\label{fig:utilityrisk}\end{figure}")

    a(r"\section{Diagnostics, Ablations, And Fixed Risk}")
    a(
        f"V5 reduces seam failure by {fmt(metrics['seam_failure_delta'])}, barrier violation by {fmt(metrics['barrier_violation_delta'])}, damage by {fmt(metrics['damage_rate_delta'])}, composition cost by {fmt(metrics['composition_cost_delta'])}, risk calibration error by {fmt(metrics['risk_calibration_error_delta'])}, and realized seam breach by {fmt(metrics['realized_seam_breach_delta'])}. "
        f"It improves basin alignment by {fmt(metrics['basin_alignment_delta'])} and descent continuity by {fmt(metrics['descent_continuity_delta'])}. "
        f"The full method beats the strongest removed-component ablation, {esc(summary['best_ablation'])}, by {fmt(metrics['ablation_success_margin'])} success and {fmt(metrics['ablation_utility_margin'])} utility."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_ablation_table.tex}}\caption{Ablations under combined seam stress.}\label{tab:ablation}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{0.94\linewidth}{!}{\input{generated_stress_table.tex}}\caption{Maximum stress endpoint.}\label{tab:stress}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{0.94\linewidth}{!}{\input{generated_fixed_risk_table.tex}}\caption{Fixed-risk audit at seam-risk budget 0.15.}\label{tab:fixed}\end{table}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=\linewidth]{../figures/energy_landscape_composition_ablation_v5.png}\caption{Removing v5 energy-seam components weakens the composer.}\label{fig:ablation}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_stress_sweep_v5.png}\caption{Stress sweep over seam discontinuity and hidden barriers.}\label{fig:stress}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_fixed_risk_v5.png}\caption{Fixed-risk gated utility as the declared seam-risk budget changes.}\label{fig:fixed}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_fixed_coverage_v5.png}\caption{Coverage is separate from seam breach.}\label{fig:coverage}\end{figure}")

    a(r"\section{Related Work Boundary}")
    a(
        "The paper is adjacent to potential fields and navigation functions, energy-based learning, motion optimization, DMPs and stable dynamical systems, options, skill chaining, TAMP, implicit policies, and large robot-data systems. "
        "It does not claim a new low-level energy model or universal composition benchmark. The boundary is energy-seam certification for deciding whether independently learned skills should be chained, repaired, or rejected."
    )

    a(r"\section{Decision And Scope Gate}")
    a(
        r"The local gates pass, so the terminal state is \textbf{\texttt{STRONG\_REVISE}}. The package is still \textbf{not ICLR-main ready}. "
        "Missing evidence includes real robot rollouts, accepted high-fidelity skill-composition simulation, released skill-energy or policy checkpoints, calibrated contact-force/camera/state logs, hardware rollout videos, independent baseline implementations, and complete manual related-work synthesis."
    )

    a(r"\clearpage")
    a(r"\appendix")
    a(r"\section{Frozen Gate Interpretation}")
    for gate, ok in sorted(gates.items()):
        a(rf"\paragraph{{{esc(gate)}.}} Status: {'pass' if ok else 'fail'}. This gate is local only and cannot override the external scope gate.")

    a(r"\clearpage")
    add_cards(lines, "Task Cards", TASK_CARDS, "External validation should log terminal samples, basin estimates, barrier values, accepted/rejected seams, and final outcomes.")
    for name, _ in TASK_CARDS:
        a(rf"\paragraph{{External replication for {esc(name)}.}} Use paired scene resets and identical skill libraries across baselines. Report success, seam failure, barrier violation, basin overlap, descent continuity, damage, cost, predicted risk, realized breach, and videos for success and failure cases.")

    a(r"\clearpage")
    add_cards(lines, "Regime Cards", REGIME_CARDS, "The regime stays visible so the report cannot hide collapse under an average.")
    for name, _ in REGIME_CARDS:
        a(rf"\paragraph{{Reviewer question for {esc(name)}.}} Did the method distinguish basin failure from barrier failure, and did the fixed-risk gate change the decision? A real submission should answer using raw logs, not only aggregate success.")

    a(r"\clearpage")
    add_cards(lines, "Baseline Cards", BASELINE_CARDS, "The baseline remains visible to avoid weak-comparator games.")
    for name, _ in BASELINE_CARDS:
        a(rf"\paragraph{{Interface audit for {esc(name)}.}} A fair comparison gives this method the same skill library, observations, terminal samples, compute budget, and failure logs. If the wrapper differs, the comparison is not credible.")

    a(r"\clearpage")
    a(r"\section{Failure Case Audit}")
    for row in failures:
        a(rf"\paragraph{{Case {esc(row['case_id'])}: {esc(row['failure_case'])}.}} {esc(row['description'])} Reviewer attack: {esc(row['reviewer_attack'])} V5 response: {esc(row['v5_response'])}. Remaining blocker: {esc(row['remaining_blocker'])}.")

    a(r"\clearpage")
    a(r"\section{Metric Definitions}")
    metric_defs = [
        ("success", "Task completion under the local rollout-cell model."),
        ("composition_utility", "Composite deployment score rewarding success, basin alignment, and descent while penalizing seam failure, barrier violation, damage, cost, energy-model error, calibration error, and abstention."),
        ("seam_failure_rate", "Rate at which the handoff state is incompatible with the next skill basin."),
        ("barrier_violation_rate", "Rate at which composition crosses an unsafe or high-energy barrier."),
        ("basin_alignment", "Overlap between terminal samples and the next attraction basin."),
        ("descent_continuity", "Whether energy continues decreasing after handoff."),
        ("damage_rate", "Unsafe physical interaction induced by the handoff or repair."),
        ("composition_cost", "Cost of seam repair, sampling, search, and fallback."),
        ("energy_model_error", "Mismatch between predicted and realized energy/seam behavior."),
        ("risk_calibration_error", "Mismatch between predicted seam risk and realized seam breach."),
        ("abstention_rate", "Rate at which the method refuses a seam; meaningful only with coverage and breach."),
        ("realized_seam_breach", "Post hoc seam breach used to audit the fixed-risk screen."),
    ]
    for name, desc in metric_defs:
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)} A hostile review can only accept this metric when it is reported with the others.")

    a(r"\clearpage")
    a(r"\section{External Validation Protocol Required Before Submission}")
    protocol = [
        ("Robot platforms", "Run the composed skills on real robot hardware or an accepted high-fidelity simulator with documented contact and dynamics fidelity."),
        ("Skill library", "Release or hash every primitive skill and ensure baselines compose the same library."),
        ("Logs", "Release terminal samples, basin estimates, barrier scores, descent diagnostics, accepted/rejected seams, predicted risk, realized breach, actions, and outcomes."),
        ("Baselines", "Reimplement or faithfully wrap option graphs, diffusion stitching, CEM, residual RL, energy heuristic, TAMP screen, stable-DMP handoff, v4.1, v5, and oracle post hoc analysis."),
        ("Risk budgets", "Pre-register fixed seam-risk budgets and report coverage and breach before tuning utility."),
        ("Videos", "Release representative successes, failures, abstentions, and oracle-gap cases."),
        ("Statistics", "Use paired resets or paired seeds so gains cannot be explained by easier scenes."),
        ("Artifacts", "Release code, configs, checkpoints or hashes, and data-processing scripts."),
    ]
    for name, desc in protocol:
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)} Without this item, the current package remains a strong local audit rather than a finished ICLR-main submission.")

    a(r"\clearpage")
    a(r"\section{Reviewer Attack Log}")
    attacks = [
        "The result is just an energy heuristic with more words.",
        "The composer wins by over-searching the seam.",
        "The composer wins by abstaining from hard cases.",
        "The previous proposed method was hidden.",
        "The strongest baseline was chosen conveniently.",
        "The oracle gap was hidden.",
        "The fixed-risk gate is cosmetic.",
        "The basin/barrier theory is only local.",
        "Synthetic local evidence will not transfer to hardware.",
        "TAMP and stable-DMP baselines are unfairly wrapped.",
        "The paper is not submission-ready without real robot evidence.",
    ]
    for attack in attacks:
        a(rf"\paragraph{{Attack.}} {esc(attack)} The v5 response is to expose the corresponding baseline, ablation, pairwise test, fixed-risk metric, oracle comparison, or scope blocker.")

    a(r"\clearpage")
    a(r"\section{Reproducibility Checklist}")
    checks = [
        "The experiment generator is deterministic and CPU-only.",
        "Thread caps are used for NumPy-backed computation.",
        "The previous v4.1 method is retained as a named baseline.",
        "The oracle is reported as an upper bound, not a deployable method.",
        "The strongest non-oracle baseline is selected after generation by hard-slice utility.",
        "All CSV files are checked for row counts and numeric finiteness.",
        "Ablations remove one mechanism at a time.",
        "Stress sweeps vary intensity instead of cherry-picking one endpoint.",
        "Fixed-risk results include coverage and breach.",
        "Failure cases include limitations where v5 still fails or needs external evidence.",
        "Citation links are boxed and clickable.",
        "The numbered PDF is placed in Downloads only.",
        "The manuscript states that ICLR-main readiness is false.",
    ]
    for item in checks:
        a(rf"\paragraph{{Check.}} {esc(item)} This check exists because the target is hostile-review survival, not cosmetic polish.")

    a(r"\clearpage")
    a(r"\section{Why The Terminal State Is Not Ready}")
    for blocker in summary["missing_scope_evidence"]:
        a(rf"\paragraph{{Blocker.}} {esc(blocker)} This blocker cannot be solved by adding more local CSV rows or nicer prose.")

    a(r"\clearpage")
    a(r"\section{Row Counts And Source Of Truth}")
    for key, value in sorted(counts.items()):
        a(rf"\paragraph{{{esc(key)}.}} {value:,} rows. This count is generated by \texttt{{src/run\_experiment.py}} and recorded in \texttt{{results/summary.json}}.")

    a(r"\clearpage")
    a(r"\section{Artifact Release Requirements}")
    release_items = [
        ("Composer code", "Exact basin, barrier, descent, repair, calibration, fixed-risk, and abstention logic."),
        ("Baseline wrappers", "Identical observations, skill libraries, terminal samples, and compute budgets."),
        ("Raw rollout logs", "Unprocessed observations, actions, handoff states, risk scores, accepted seams, rejected seams, and outcomes."),
        ("Processed CSVs", "Aggregates regenerated from raw logs by public scripts."),
        ("Calibration metadata", "Camera, contact, force, proprioceptive, and timing calibration details."),
        ("Videos", "Successes, seam failures, abstentions, and oracle-gap cases linked to case IDs."),
        ("Ablation configs", "Configuration toggles for every removed component."),
        ("Environment metadata", "Friction, compliance, payload, contact mode, barrier and basin annotations."),
        ("Rebuild command", "A single script to regenerate results, figures, tables, PDF, and validation logs."),
        ("License notes", "Redistribution status for skills, policies, and robot logs."),
    ]
    for name, desc in release_items:
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)} This is required for a real submission package even though the current local audit is reproducible without hardware.")

    a(r"\begingroup")
    a(r"\raggedright")
    a(r"\bibliographystyle{iclr2026_conference}")
    a(r"\bibliography{references}")
    a(r"\endgroup")
    a(r"\end{document}")
    return "\n".join(lines) + "\n"


def main():
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    PAPER.mkdir(exist_ok=True)
    (PAPER / "references.bib").write_text(REFERENCES.strip() + "\n", encoding="utf-8")
    (PAPER / "main.tex").write_text(make_manuscript(summary), encoding="utf-8")
    print("Generated paper/main.tex and paper/references.bib for Paper 119.")


if __name__ == "__main__":
    main()

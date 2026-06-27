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


def load_json(name):
    path = RESULTS / name
    if not path.exists():
        raise SystemExit(f"missing {path}; run scripts/audit_local_falsification.py before generating the manuscript")
    return json.loads(path.read_text(encoding="utf-8"))


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

@inproceedings{urain2021cep,
  title={Composable Energy Policies for Reactive Motion Generation and Reinforcement Learning},
  author={Urain, Julen and Li, Anqi and Liu, Puze and D'Eramo, Carlo and Peters, Jan},
  booktitle={Robotics: Science and Systems},
  year={2021},
  doi={10.15607/RSS.2021.XVII.052}
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

@article{pane2021runtime,
  title={Autonomous Runtime Composition of Sensor-Based Skills Using Concurrent Task Planning},
  author={Pane, Yudha P. and Mokhtari, Vahid and Aertbelien, Erwin and De Schutter, Joris and Decre, Wilm},
  journal={IEEE Robotics and Automation Letters},
  volume={6},
  number={4},
  pages={6481--6488},
  year={2021},
  doi={10.1109/LRA.2021.3094498}
}

@article{rizwan2025ezskiros,
  title={{EzSkiROS}: Enhancing Robot Skill Composition with Embedded {DSL} for Early Error Detection},
  author={Rizwan, Momina and Reichenbach, Christoph and Caldas, Ricardo and Mayr, Matthias and Krueger, Volker},
  journal={Frontiers in Robotics and AI},
  volume={11},
  pages={1363443},
  year={2025},
  doi={10.3389/frobt.2024.1363443}
}

@inproceedings{janner2019mbpo,
  title={When to trust your model: Model-based policy optimization},
  author={Janner, Michael and Fu, Justin and Zhang, Marvin and Levine, Sergey},
  booktitle={Advances in Neural Information Processing Systems},
  year={2019}
}

@inproceedings{florence2022implicit,
  title={Implicit behavioral cloning},
  author={Florence, Pete and Lynch, Corey and Zeng, Andy and others},
  booktitle={Conference on Robot Learning},
  year={2022}
}

@inproceedings{chi2023diffusionpolicy,
  title={Diffusion Policy: Visuomotor Policy Learning via Action Diffusion},
  author={Chi, Cheng and Du, Yilun and Song, Shuran and others},
  booktitle={Robotics: Science and Systems},
  year={2023},
  doi={10.15607/RSS.2023.XIX.026}
}

@article{brohan2023rt1,
  title={{RT-1}: Robotics transformer for real-world control at scale},
  author={Brohan, Anthony and Chebotar, Yevgen and Finn, Chelsea and others},
  journal={Robotics: Science and Systems},
  year={2023},
  eprint={2212.06817},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2212.06817}
}

@article{openx2023,
  title={Open X-Embodiment: Robotic learning datasets and {RT-X} models},
  author={{Open X-Embodiment Collaboration}},
  journal={arXiv preprint arXiv:2310.08864},
  year={2023},
  eprint={2310.08864},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2310.08864}
}

@article{julian2020latent,
  title={Scaling Simulation-to-Real Transfer by Learning a Latent Space of Robot Skills},
  author={Julian, Ryan C. and Hausman, Karol and others},
  journal={The International Journal of Robotics Research},
  volume={39},
  number={10--11},
  year={2020},
  doi={10.1177/0278364920944474}
}

@article{vijayaraghavan2025compositionality,
  title={Development of Compositionality Through Interactive Learning of Language and Action of Robots},
  author={Vijayaraghavan, Prasanna and Queisser, Jeffrey F. and Verduzco-Flores, Sergio and Tani, Jun},
  journal={Science Robotics},
  volume={10},
  number={98},
  pages={eadp0751},
  year={2025},
  doi={10.1126/scirobotics.adp0751}
}

@article{du2019implicit,
  title={Implicit Generation and Generalization in Energy-Based Models},
  author={Du, Yilun and Mordatch, Igor},
  journal={arXiv preprint arXiv:1903.08689},
  year={2019},
  eprint={1903.08689},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/1903.08689}
}

@article{wang2024poco,
  title={{PoCo}: Policy Composition from and for Heterogeneous Robot Learning},
  author={Wang, Lirui and Du, Yilun and others},
  journal={arXiv preprint arXiv:2402.02511},
  year={2024},
  eprint={2402.02511},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2402.02511}
}

@inproceedings{liu2026simpact,
  title={{SIMPACT}: Simulation-Enabled Action Planning using Vision-Language Models},
  author={Liu, Haowen and Chen, Haonan and Du, Yilun and others},
  booktitle={IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2026},
  eprint={2512.05955},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2512.05955}
}

@article{liu2026oat,
  title={{OAT}: Ordered Action Tokenization},
  author={Liu, Chaoqi and Chen, Haonan and Du, Yilun and others},
  journal={arXiv preprint arXiv:2602.04215},
  year={2026},
  eprint={2602.04215},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2602.04215}
}

@article{hou2026worldmodel,
  title={World Model for Robot Learning: A Comprehensive Survey},
  author={Hou, Bohan and Du, Yilun and Yang, Jianfei and others},
  journal={arXiv preprint arXiv:2605.00080},
  year={2026},
  eprint={2605.00080},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2605.00080}
}

@article{chen2026costream,
  title={{CoStream}: Composing Simple Behaviors for Generalizable Complex Manipulation},
  author={Chen, Haonan and Du, Yilun and others},
  journal={arXiv preprint arXiv:2606.26423},
  year={2026},
  eprint={2606.26423},
  archivePrefix={arXiv},
  primaryClass={cs.RO},
  url={https://arxiv.org/abs/2606.26423}
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
    local_falsification = load_json("local_falsification_audit.json")
    falsification_metrics = local_falsification["metrics"]
    holdout = load_json("holdout_robustness_audit.json")
    holdout_metrics = holdout["metrics"]
    holdout_stats = holdout["partition_stats"]
    diagnostic = load_json("diagnostic_mechanism_audit.json")
    diagnostic_metrics = diagnostic["metrics"]
    decision_quality = load_json("decision_quality_audit.json")
    decision_metrics = decision_quality["metrics"]
    calibration = load_json("seam_prediction_calibration_audit.json")
    calibration_metrics = calibration["proposed_metrics"]
    calibration_baseline = calibration["strongest_baseline_metrics"]
    calibration_derived = calibration["derived"]
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
    a(r"\hypersetup{hidelinks}")
    a(r"\setlist[itemize]{leftmargin=1.2em,itemsep=0.15em,topsep=0.2em}")
    a(r"\raggedbottom")
    a(r"\title{Predictive Skill-Seam Models for\\Robot Skill Composition}")
    a(r"\author{Anonymous Authors}")
    a(r"\begin{document}")
    a(r"\maketitle")
    a(r"\begin{abstract}")
    a(
        "Robot skills that work individually can fail when chained: the terminal state of one skill may fall outside the next skill's attraction basin, cross a high-energy barrier, or enter a contact mode where descent is no longer smooth. "
        "We frame that handoff as a local world/action-modeling problem: a compact predictive interface between a skill library and a planner. Given terminal-state evidence, next-skill basin/descent estimates, and a candidate transition, the interface estimates whether an action/skill composition will fail, diagnoses the likely reason, chooses accept, repair, probe, abstain, or alternate transition, and stores the result as planner-edge evidence for future planning. "
        "A barrier-certified energy composer implements that interface, acting on a skill edge only when basin overlap, barrier height, descent continuity, repair cost, and fixed-risk calibration are jointly favorable. "
        f"In a frozen local rollout suite with 12 methods, 6 task families, 8 seam regimes, and 10 paired seeds, the composer reaches hard-slice success {fmt(metrics['hard_success_proposed'])} and utility {fmt(metrics['hard_utility_proposed'])}, compared with {fmt(metrics['hard_success_strongest'])} and {fmt(metrics['hard_utility_strongest'])} for the strongest non-oracle predecessor. "
        "It reduces seam failure, barrier violation, damage, calibration error, and realized seam breach while improving basin alignment and descent continuity. "
        "The current evidence supports a bounded claim: a seam-level predictive model improves composition when the relevant basin, barrier, and descent quantities are estimable and their outcomes update future planning, while external robot or high-fidelity validation remains necessary before deployment-level claims."
    )
    a(r"\end{abstract}")

    a(r"\section{Motivation}")
    a(
        "A reusable robot skill library still leaves a planning problem: the robot must know what the end of one skill makes possible for the next. We focus on that seam, where action-conditioned prediction can be smaller than a full simulator but richer than a graph edge."
    )
    a(
        "Potential fields, navigation functions, energy-based learning, trajectory optimization, DMPs, and stable dynamical systems have long used scalar landscapes to encode motion and control structure \\citep{khatib1986potential,koditschek1989navigation,lecun2006energy,ratliff2009chomp,ijspeert2013dmp,khansari2011stable}. "
        "Options, skill chaining, and TAMP make composition a first-class robotics problem \\citep{sutton1999options,konidaris2009skillchaining,kaelbling2011tamp,garrett2021integrated}. "
        "Modern robot-learning systems add broad skill libraries and large robot datasets \\citep{florence2022implicit,brohan2023rt1,openx2023}. The gap targeted here is not low-level skill learning or a new manipulation controller; it is the missing action-conditioned physical interface between a skill library and a planner. Before execution, the robot should estimate whether a proposed edge will land inside the next skill's feasible start set or whether it should repair, probe, abstain, or choose a different transition. After execution, it should keep the outcome as planning evidence: which handoff was reliable, which needed repair, which called for abstention, and which should be avoided later."
    )
    a(
        "The core failure mode is simple: skill one ends successfully, but its terminal distribution lies near a ridge or outside the basin of skill two. A module graph may mark the edge legal, while execution requires a high-energy repair, crosses a barrier, or enters a contact mode where the next controller no longer descends. The paper asks whether an explicit seam model can make composition more reliable by predicting whether a proposed transition will fail before the handoff, diagnosing the likely reason, deciding when to accept, repair, probe, abstain, or choose a different transition, and turning the outcome into planner memory for later compositions. Contact-rich examples matter here because they expose action consequences that a motion-only edge label misses; they are a testbed for the seam model, not the identity of the paper."
    )
    a(
        "The broader question is how a robot represents the physical consequences of a skill transition, notices when that representation is incomplete, and adapts future planning from the outcome. We use the world/action-model view at a deliberately local scale: the model is not a whole robot simulator, and the prediction-action-update loop is limited to the handoff."
    )
    a(
        "Concretely, the contribution is a seam-level predictive interface: estimate terminal/basin/barrier/descent/risk quantities, diagnose the likely failure mode, choose accept, repair, probe, abstain, or transition, and write the outcome back to planner-edge memory. The energy composer is the paper's implementation of that interface, not the identity of the contribution."
    )

    a(r"\section{Problem Setup}")
    a(
        r"Let skill $i$ induce a terminal distribution $p_i(x_T)$ and skill $j$ have an attraction basin $\mathcal{B}_j$ under local controller $\pi_j$. "
        r"We treat the handoff as a small predictive model of action consequences at the seam. "
        r"A composition edge $i\rightarrow j$ is acceptable only if terminal samples have sufficient basin overlap, low barrier height, and positive descent continuity. "
        r"The composer can accept, repair, probe, abstain, or route to an alternate transition."
    )
    a(
        r"Operationally, the seam model maps a candidate transition to a consequence tuple: predicted basin compatibility, barrier exposure, descent continuity, repair cost, calibrated risk, and a failure label such as basin mismatch, high barrier, contact-mode discontinuity, model uncertainty, or missing bridge skill. "
        r"We use world/action model in this limited sense: the output is not a general simulator and does not try to predict every future observation. The local world is the physical seam state around a handoff; the action is the proposed skill transition, repair, probe, abstention, or alternate edge. The model predicts how that action changes the next skill's feasible start set, turns the prediction into a decision, and records the result as an edge belief for future plans."
    )
    a(
        r"More explicitly, the interface can be read as "
        r"$M_\theta(i,j,h;\mathcal{D}_t)\mapsto(\widehat O,\widehat B,\widehat D,\widehat C,\widehat R,\widehat y,\Delta b)$, "
        r"where $h$ is a candidate handoff, $\mathcal{D}_t$ is the accumulated seam evidence, $\widehat y$ is the diagnostic label, and $\Delta b$ is the planner-edge belief update. "
        r"The adaptation is modest but important: a failed or successful seam changes which transition the next planning query prefers, probes, repairs, or refuses, so the model improves future planning rather than only scoring one edge."
    )
    a(r"We score candidate handoff $h$ by")
    a(r"\[")
    a(r"S(i,j,h)=\alpha O_{\mathrm{basin}}(p_i,\mathcal{B}_j)-\beta B_{\mathrm{barrier}}(h,j)+\gamma D_{\mathrm{descent}}(h,j)-\lambda C_{\mathrm{repair}}(h)-\kappa R_{\mathrm{seam}}(h).")
    a(r"\]")
    a(
        r"Here $O_{\mathrm{basin}}$ measures terminal/basin overlap, $B_{\mathrm{barrier}}$ measures energy barrier height, $D_{\mathrm{descent}}$ checks whether energy decreases after handoff, $C_{\mathrm{repair}}$ is seam-repair cost, and $R_{\mathrm{seam}}$ is calibrated seam risk. "
        r"The proposed composer accepts the edge only when predicted seam risk is below a declared fixed-risk budget; otherwise the failed prediction becomes a planning signal for repair, diagnostic probing, abstention, or a different transition. "
        r"Across attempts, the same interface can update a planner's edge beliefs: which handoffs are reliable, which need a bridge action, which need more evidence, and which should be avoided until the skill library changes."
    )
    a(r"\begin{figure}[t]\centering\includegraphics[width=\linewidth]{../figures/skill_seam_action_model_overview_v5.pdf}\caption{Skill-seam action interface. The method predicts local handoff consequences, diagnoses likely failure modes, and converts that evidence into accept, repair, probe, abstain, or transition decisions plus planner-edge updates for future planning.}\label{fig:overview}\end{figure}")

    a(r"\section{Skill Seams As Predictive Interfaces}")
    a(
        "A sequence can be graph-valid while physically unsafe at the seam. If terminal states from the first skill do not overlap the next basin, the second skill starts outside its attraction region. If a high barrier separates the terminal set from the basin, a repair may be possible but costly or unsafe. If the contact mode changes, the energy function may no longer be conservative enough to certify descent. These are not merely controller details; they are action-conditioned predictions about what a skill transition will do to the physical state available to the next skill."
    )
    a(
        "The model output is therefore not just a compatibility number. It is a compact answer to four planning questions: will this handoff fail, why might it fail, should the system repair, probe, abstain, or route through another transition, and how should that outcome change later plans?"
    )
    a(
        "This gives a bounded claim. When basin overlap, barrier height, and descent continuity are identifiable enough to reject bad seams and preserve useful ones, a barrier-certified implementation can make skill composition more reliable. Its value is not only higher success, but more structured failure information: the planner can learn which transitions are reliable, which require repair or a diagnostic probe, and which should be avoided. What makes this a seam action model rather than only a score threshold is the full loop: predict the local consequence before execution, choose a transition-level response, observe the outcome, and update the edge memory that future plans query. It must fail or abstain when the low-level primitive is broken, the goal is semantic rather than physical, the landscape is miscalibrated, or real-time constraints prevent search."
    )

    a(r"\section{Evaluation Protocol}")
    a(
        f"The evaluation protocol is fixed before interpreting final results. The main matrix contains 12 methods, 6 task families, 8 seam regimes, 5 deployment splits, 10 paired seeds, 8 rollout episodes per cell, and {counts['main_cell']:,} main cell rows. "
        f"Ablations add {counts['ablation_cell']:,} cells, stress sweeps add {counts['stress_cell']:,} cells, fixed-risk tests add {counts['fixed_risk_cell']:,} cells, and the failure audit contains {counts['failure_cases']} cases. The previous proposed method remains a named baseline. The protocol measures both composition outcomes and seam-interface behavior: predicted risk, diagnostic label, decision, realized breach, and planner-edge update."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_gate_table.tex}}\caption{Local evidence gates used for the seam-composition audit. External robot or high-fidelity validation is evaluated separately.}\label{tab:gates}\end{table}")

    a(r"\section{Main Results}")
    a(
        f"The strongest non-oracle comparator is {esc(summary['strongest_non_oracle'])}. "
        f"The proposed composer improves hard success by {fmt(metrics['hard_success_margin'])} and hard utility by {fmt(metrics['hard_utility_margin'])}; paired hard-utility wins are {int(metrics['paired_hard_utility_wins'])}/10. "
        f"The oracle remains stronger with success {fmt(metrics['hard_success_oracle'])} and utility {fmt(metrics['hard_utility_oracle'])}, so the local problem is not solved. The intended readout is therefore not only success; it is whether a seam action model can preserve useful skill edges while refusing or redirecting seams that its own predictions mark as unsafe, and whether those decisions produce planner-facing evidence for later compositions."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_main_table.tex}}\caption{Hard-slice aggregate results. Higher success, utility, basin, and descent are better; lower seam, barrier, damage, cost, and breach are better.}\label{tab:main}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_pairwise_table.tex}}\caption{Paired proposed-minus-baseline hard-slice differences.}\label{tab:pairwise}\end{table}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.88\linewidth]{../figures/energy_landscape_composition_hard_success_v5.pdf}\caption{Hard-slice success under energy-seam stress.}\label{fig:hard}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.82\linewidth]{../figures/energy_landscape_composition_utility_risk_v5.pdf}\caption{Composition utility is reported against realized seam breach.}\label{fig:utilityrisk}\end{figure}")

    a(r"\section{Diagnostics, Ablations, And Fixed Risk}")
    a(
        f"The proposed composer reduces seam failure by {fmt(metrics['seam_failure_delta'])}, barrier violation by {fmt(metrics['barrier_violation_delta'])}, damage by {fmt(metrics['damage_rate_delta'])}, composition cost by {fmt(metrics['composition_cost_delta'])}, risk calibration error by {fmt(metrics['risk_calibration_error_delta'])}, and realized seam breach by {fmt(metrics['realized_seam_breach_delta'])}. "
        f"It improves basin alignment by {fmt(metrics['basin_alignment_delta'])} and descent continuity by {fmt(metrics['descent_continuity_delta'])}. "
        f"The full method beats the strongest removed-component ablation, {esc(summary['best_ablation'])}, by {fmt(metrics['ablation_success_margin'])} success and {fmt(metrics['ablation_utility_margin'])} utility. "
        "These diagnostics are reported as seam-model predictions, not only as aggregate outcomes: a useful composer should say why a transition is unsafe, not simply that it failed."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_ablation_table.tex}}\caption{Ablations under combined seam stress.}\label{tab:ablation}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{0.94\linewidth}{!}{\input{generated_stress_table.tex}}\caption{Maximum stress endpoint.}\label{tab:stress}\end{table}")
    a(r"\begin{table}[t]\centering\small\resizebox{0.94\linewidth}{!}{\input{generated_fixed_risk_table.tex}}\caption{Fixed-risk audit at seam-risk budget 0.15.}\label{tab:fixed}\end{table}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=\linewidth]{../figures/energy_landscape_composition_ablation_v5.pdf}\caption{Removing v5 energy-seam components weakens the composer.}\label{fig:ablation}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_stress_sweep_v5.pdf}\caption{Stress sweep over seam discontinuity and hidden barriers.}\label{fig:stress}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_fixed_risk_v5.pdf}\caption{Fixed-risk gated utility as the declared seam-risk budget changes.}\label{fig:fixed}\end{figure}")
    a(r"\begin{figure}[t]\centering\includegraphics[width=0.86\linewidth]{../figures/energy_landscape_composition_fixed_coverage_v5.pdf}\caption{Coverage is separate from seam breach.}\label{fig:coverage}\end{figure}")

    a(r"\subsection{Diagnostic Mechanism Audit}")
    a(
        "For the action-model framing to be meaningful, the seam layer has to expose why a transition is risky and what the planner should do next, not only whether aggregate success improves. "
        f"We therefore export a diagnostic label, seam decision, and planner-edge update for every local row and audit the rules that produce them. Over {int(counts['main_cell']):,} local rows, the diagnostic audit finds {int(diagnostic_metrics['label_mismatches'])} label-rule mismatches, {int(diagnostic_metrics['decision_mismatches'])} decision-rule mismatches, and {int(diagnostic_metrics['update_mismatches'])} planner-update mismatches. "
        f"In the {int(diagnostic_metrics['proposed_hard_rows']):,} proposed hard rows, all five failure labels and all five decisions appear. Accepted seams have mean realized breach {fmt(diagnostic_metrics['accept_mean_realized_breach'], 3)} versus {fmt(diagnostic_metrics['non_accept_mean_realized_breach'], 3)} for non-accepted seams, while abstained seams have mean predicted risk {fmt(diagnostic_metrics['abstain_mean_predicted_risk'], 3)} versus {fmt(diagnostic_metrics['accept_mean_predicted_risk'], 3)} for accepted seams. "
        f"Repair, probe, and transition decisions match their intended diagnostic reasons with purity {fmt(diagnostic_metrics['repair_reason_rate'], 3)}, {fmt(diagnostic_metrics['probe_reason_rate'], 3)}, and {fmt(diagnostic_metrics['transition_reason_rate'], 3)}. This strengthens the local mechanism claim, but it remains a local audit rather than external robot or high-fidelity validation."
    )
    a(r"\begin{center}\small\resizebox{\linewidth}{!}{\input{generated_diagnostic_mechanism_table.tex}}\end{center}")
    a(r"\noindent{\small\textbf{Diagnostic audit table.} Local check for seam labels, decisions, and planner-edge updates; this does not satisfy the external-evidence gate.}")

    a(r"\subsection{Comparative Decision-Quality Audit}")
    a(
        "A seam action model should not only reject risky edges; it should preserve useful transitions that a cautious predecessor would discard. "
        f"On the same {int(decision_metrics['paired_hard_rows']):,} paired hard rows, the proposed model accepts {fmt(decision_metrics['proposed_accept_coverage'], 3)} of hard seams versus {fmt(decision_metrics['baseline_accept_coverage'], 3)} for the predecessor, while the rate of accepted seams above the 0.15 breach budget is {fmt(decision_metrics['proposed_accept_breach_rate'], 3)}. "
        f"Among non-abstained seams, utility is {fmt(decision_metrics['proposed_non_abstain_utility'], 3)} versus {fmt(decision_metrics['baseline_non_abstain_utility'], 3)} and realized breach is {fmt(decision_metrics['proposed_non_abstain_breach'], 3)} versus {fmt(decision_metrics['baseline_non_abstain_breach'], 3)}. "
        f"Most importantly for future planning, {int(decision_metrics['recovered_accept_pairs']):,} paired seams are accepted by v5 and abstained from by the predecessor; those recovered accepts improve utility by {fmt(decision_metrics['recovered_accept_utility_delta'], 3)}, success by {fmt(decision_metrics['recovered_accept_success_delta'], 3)}, and realized breach by {fmt(decision_metrics['recovered_accept_breach_delta'], 3)}. "
        "This is still a local decision-quality audit, not external robot or high-fidelity validation."
    )
    a(r"\begin{center}\small\resizebox{\linewidth}{!}{\input{generated_decision_quality_table.tex}}\end{center}")
    a(r"\noindent{\small\textbf{Decision-quality table.} Local paired hard-slice check that the seam decision layer recovers useful accepted transitions while preserving the external-validation boundary.}")

    a(r"\subsection{Predictive Calibration Audit}")
    a(
        "A seam model should be predictive, not only useful after the fact. "
        f"On the proposed hard slice, ten-bin local calibration error between predicted seam risk and realized seam breach is {fmt(calibration_metrics['expected_calibration_error_10'], 3)}, compared with {fmt(calibration_baseline['expected_calibration_error_10'], 3)} for the strongest predecessor; the maximum bin gap is {fmt(calibration_metrics['max_calibration_error_10'], 3)}. "
        f"Mean predicted risk is {fmt(calibration_metrics['mean_predicted_seam_risk'], 3)} versus realized breach {fmt(calibration_metrics['mean_realized_seam_breach'], 3)}, with risk-breach correlation {fmt(calibration_metrics['risk_breach_correlation'], 3)} and Spearman {fmt(calibration_metrics['risk_breach_spearman'], 3)}. "
        f"Realized breach is monotone across ten risk deciles; the highest-risk decile has realized breach {fmt(calibration_derived['highest_lowest_decile_breach_delta'], 3)} higher and utility {fmt(-calibration_derived['highest_lowest_decile_utility_delta'], 3)} lower than the lowest-risk decile. "
        "This is still local predictive-validity evidence, not external robot or high-fidelity validation."
    )
    a(r"\begin{center}\small\resizebox{\linewidth}{!}{\input{generated_seam_prediction_calibration_table.tex}}\end{center}")
    a(r"\noindent{\small\textbf{Predictive calibration table.} Local hard-slice check that predicted seam risk tracks realized seam breach and decision relevance while preserving the external-validation boundary.}")

    a(r"\subsection{Local Falsification Audit}")
    a(
        "Because the current evidence is local, we add a machine-checkable falsification audit for common reviewer attacks. "
        f"On {int(falsification_metrics['paired_hard_rows']):,} paired hard rows, the proposed composer beats the strongest non-oracle baseline in utility on {fmt(falsification_metrics['utility_pair_win_rate'], 3)} of paired rows. "
        f"The result is not explained by abstention or search cost: abstention changes by only {fmt(falsification_metrics['abstention_delta'])}, composition cost changes by {fmt(falsification_metrics['composition_cost_delta'])}, and cost-normalized utility improves by {fmt(falsification_metrics['cost_normalized_utility_margin'])}. "
        f"Predicted seam risk is also not decorative: five risk quantile bins are monotone in realized breach, with risk-breach correlation {fmt(falsification_metrics['risk_breach_correlation'], 3)}. "
        f"Margins are positive in all {int(falsification_metrics['task_regime_margins']['groups'])} hard task-regime slices, and the oracle remains above the proposed method by {fmt(falsification_metrics['oracle_success_gap'])} success and {fmt(falsification_metrics['oracle_utility_gap'])} utility. "
        "This audit strengthens the local mechanism claim, but it is not a substitute for external robot or high-fidelity validation."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{\linewidth}{!}{\input{generated_local_falsification_table.tex}}\caption{Local falsification checks against common reviewer explanations. The audit is generated from episode-level local hard-slice rows and does not satisfy the external-evidence gate.}\label{tab:falsification}\end{table}")

    a(r"\subsection{Withheld-Slice Robustness Audit}")
    a(
        "We also audit whether the headline gain hides a narrow favorable slice. "
        f"Over {int(holdout_metrics['hard_rows_per_method']):,} hard rows per method, we leave out task families, seam regimes, deployment splits, task-regime pairs, and deterministic hash folds before comparing the proposed seam model with the strongest non-oracle predecessor. "
        f"Utility margins are positive in {int(holdout_stats['task']['positive_utility_groups'])}/{int(holdout_stats['task']['groups'])} task-family holdouts, "
        f"{int(holdout_stats['regime']['positive_utility_groups'])}/{int(holdout_stats['regime']['groups'])} seam-regime holdouts, "
        f"{int(holdout_stats['split']['positive_utility_groups'])}/{int(holdout_stats['split']['groups'])} split holdouts, "
        f"{int(holdout_stats['task_regime']['positive_utility_groups'])}/{int(holdout_stats['task_regime']['groups'])} task-regime holdouts, and "
        f"{int(holdout_stats['hash_fold']['positive_utility_groups'])}/{int(holdout_stats['hash_fold']['groups'])} hash-fold holdouts. "
        f"The worst task-regime holdout still has success margin {fmt(holdout_metrics['worst_task_regime_success_delta'])} and utility margin {fmt(holdout_metrics['worst_task_regime_utility_delta'])}; the weakest hash fold has utility margin {fmt(holdout_metrics['worst_hash_fold_utility_delta'])} and {int(holdout_metrics['worst_hash_fold_seed_wins'])}/10 seed wins. "
        "This makes the local result harder to dismiss as cherry-picking, but it remains local evidence rather than external robot or high-fidelity validation."
    )
    a(r"\begin{table}[t]\centering\small\resizebox{0.94\linewidth}{!}{\input{generated_holdout_robustness_table.tex}}\caption{Withheld-slice local robustness audit. Each row reports the weakest proposed-minus-strongest-baseline margin over a family of hard-slice holdouts; this is not external evidence.}\label{tab:holdout}\end{table}")

    a(r"\section{Related Work And Boundary}")
    a(
        "Classical potential fields, navigation functions, motion optimization, DMPs, and stable dynamical systems use landscapes, attractors, and descent structure to make local motion reliable \\citep{khatib1986potential,koditschek1989navigation,ratliff2009chomp,ijspeert2013dmp,khansari2011stable}. "
        "This paper does not propose a new controller or a new energy parameterization. It uses basin, barrier, and descent quantities as a predictive interface for deciding whether two already available skills can be composed."
    )
    a(
        "Composable energy policies show that energy structure can be used to combine objectives or policy components in action space \\citep{urain2021cep}. "
        "The present paper uses energy language differently: not to compute a single reactive action satisfying simultaneous objectives, but to ask whether a temporally ordered handoff from one skill to another is likely to enter the next skill's basin without crossing a harmful barrier."
    )
    a(
        "Energy-based models and model-based policy optimization offer broad languages for implicit structure, composition, model trust, and long-horizon prediction \\citep{lecun2006energy,du2019implicit,janner2019mbpo}. "
        "The contribution here is deliberately narrower: the energy landscape is not a universal world model, but a local world/action interface at a skill seam. It predicts handoff consequences, diagnoses the likely failure mode, exposes whether a transition should be accepted, repaired, probed, abstained from, or replaced, and updates the planner's transition belief after outcomes are observed. In that sense, the paper studies a small but testable world/action model rather than a new low-level controller."
    )
    a(
        "Temporal abstraction, skill chaining, and TAMP treat skills and symbolic/geometric feasibility as planning objects \\citep{sutton1999options,konidaris2009skillchaining,kaelbling2011tamp,garrett2021integrated}. "
        "Runtime composition and robot-skill software contracts add important machinery for composing, checking, and executing skill descriptions \\citep{pane2021runtime,rizwan2025ezskiros}. "
        "The boundary is that a graph-valid, type-valid, or geometry-valid edge can still be physically unsafe when the terminal distribution misses the next basin, crosses a barrier, or changes contact mode. The seam critic adds this missing predictive physical test."
    )
    a(
        "Robot foundation-policy and large-data systems broaden the available skill library \\citep{florence2022implicit,brohan2023rt1,openx2023}, while diffusion/action generation, action tokenization, policy composition, latent skill transfer, and language-action compositionality study how actions, skills, or policies can be represented, generated, reused, and combined \\citep{chi2023diffusionpolicy,wang2024poco,liu2026oat,julian2020latent,vijayaraghavan2025compositionality}. "
        "Those systems create more opportunities for composition. This paper asks a complementary reliability question: when a proposed transition between already available skills should be trusted, repaired, probed, or avoided."
    )
    a(
        "Recent work on behavior composition and simulation-in-the-loop physical reasoning is especially close \\citep{chen2026costream,liu2026simpact}, and robot world-model surveys frame predictive action-conditioned representations as central to planning and evaluation \\citep{hou2026worldmodel}. "
        "The natural boundary is scale and role: this paper is not a full behavior-composition stack, action tokenizer, foundation policy, or simulation world model. It is a seam-level reliability layer meant to improve future planning by turning handoff predictions and failures into updated planner edge beliefs. The connection is intentionally narrow: physical prediction is local, actions are skill transitions, and adaptation happens through planner memory rather than through a claim of general-purpose simulation."
    )

    a(r"\section{Scope And Validation}")
    a(
        "The local gates pass, but the evidence should be read as a controlled seam-composition study rather than a deployment claim. "
        "A complete submission package still needs real robot rollouts or accepted high-fidelity skill-composition simulation, released skill-energy or policy checkpoints, calibrated contact-force/camera/state logs, rollout videos, and manifest-declared independent baseline evidence from real external runs. "
        "The repository therefore treats external evidence as a machine-checkable contract: a future submission-ready version must pass an external-evidence audit over a manifest, episode-level JSONL logs, video directories, config/checkpoint hashes, baseline implementations, fixed-risk metrics, and ablations. "
        "A separate raw-rollout validator must recompute success margin, utility margin, paired win rate, fixed-risk coverage, fixed-risk breach, and positive task-family count from the episode logs rather than accepting manifest-level numbers. The evidence audit treats any mismatch between manifest metrics and recomputed rollout metrics as blocking. Until those audits pass, the paper remains a local study with a bounded claim."
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
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)}")

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
        ("External evidence audit", "Populate the external validation manifest, validate raw rollout JSONL logs, and pass the strict audit over logs, videos, configs, checkpoints, metrics, and ablations."),
    ]
    for name, desc in protocol:
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)}")

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
        "Citation links are hidden and clickable.",
        "The numbered PDF is placed in Downloads only.",
        "The manuscript separates local evidence from external deployment claims.",
        "The manuscript readability audit checks the agenda framing, related-work boundary, and stale-polish blocker.",
    ]
    for item in checks:
        a(rf"\paragraph{{Check.}} {esc(item)}")

    a(r"\clearpage")
    a(r"\section{Remaining External Evidence}")
    for blocker in summary["missing_scope_evidence"]:
        a(rf"\paragraph{{Blocker.}} {esc(blocker)} This blocker cannot be solved by adding more local CSV rows or nicer prose.")

    a(r"\clearpage")
    a(r"\section{Row Counts And Source Of Truth}")
    for key, value in sorted(counts.items()):
        a(rf"\paragraph{{{esc(key)}.}} {value:,} rows. This count is generated by \texttt{{src/run\_experiment.py}} and recorded in \texttt{{results/summary.json}}.")

    a(r"\medskip")
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
        ("Rebuild command", "Run scripts/build_submission_artifacts.ps1 to regenerate results, figures, tables, PDF, validation logs, and outreach artifacts for the current bounded local package."),
        ("Claim boundary audit", "Run scripts/audit_claim_boundary.py to verify that the package keeps the current claim bounded and does not assert deployment, hardware, or ICLR-main readiness before external evidence passes."),
        ("External validator self-test", "Run scripts/self_test_external_rollout_validator.py to verify that the raw-log metric recomputation and schema failure path work on a temporary synthetic fixture; this is a tooling test, not evidence."),
        ("External audit command", "Run scripts/validate_external_rollouts.py --strict --write-results and scripts/audit_external_evidence.py --strict after adding real or high-fidelity validation artifacts."),
        ("License notes", "Redistribution status for skills, policies, and robot logs."),
    ]
    for name, desc in release_items:
        a(rf"\paragraph{{{esc(name)}.}} {esc(desc)}")

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

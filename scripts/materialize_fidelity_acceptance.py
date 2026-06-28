from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

DRAFT_JSON = EXTERNAL / "fidelity_acceptance_draft.json"
OUTPUT_JSON = EXTERNAL / "fidelity_acceptance.json"
MANIFEST_JSON = EXTERNAL / "manifest.json"
OUT_JSON = RESULTS / "fidelity_acceptance_materialization_plan.json"
OUT_MD = RESULTS / "fidelity_acceptance_materialization_plan.md"

DRAFT_VERSION = "paper119_fidelity_acceptance_draft_v1"
EVIDENCE_VERSION = "paper119_fidelity_acceptance_v1"
PLAN_VERSION = "fidelity_acceptance_materialization_plan_v1"

TEXT_ARGUMENTS = {
    "operator_name_or_lab": "independent operator/lab identity",
    "accepted_collection_machine": "accepted robot/simulator machine identity",
    "contact_solver_and_friction_model": "contact solver, friction model, and dynamics justification",
    "timestep_and_substeps_per_control_step": "sim/control timestep and substeps per control step",
    "paired_reset_replay_test": "paired-reset replay verification",
    "real_or_benchmark_calibration_basis": "real or benchmark calibration basis",
    "task_binding_decision": "accepted or replaced task-binding decision",
    "acceptance_gate_signoff": "operator acceptance-gate signoff",
    "known_limitations": "known limitations for the accepted route",
    "date_locked": "date on which platform acceptance was locked",
    "code_commit": "code commit used for collection",
    "skill_library_hash": "SHA256 hash for the skill/baseline library",
}

CONFIRMATION_FLAGS = [
    "confirm_real_platform",
    "confirm_independent_operator",
    "confirm_render_backed_videos",
    "confirm_real_rollout_evidence",
    "confirm_manifest_declaration",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def has_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Fa-f0-9]{64}", value.strip()))


def has_text(value: Any, *, min_len: int = 12) -> bool:
    return isinstance(value, str) and len(value.strip()) >= min_len


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def operator_text_ready(args: argparse.Namespace) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for attr, label in TEXT_ARGUMENTS.items():
        value = getattr(args, attr)
        if attr == "skill_library_hash":
            if not has_sha(value):
                missing.append(label)
        elif attr == "code_commit":
            if not has_text(value, min_len=7):
                missing.append(label)
        elif not has_text(value):
            missing.append(label)
    return not missing, missing


def confirmations_ready(args: argparse.Namespace) -> tuple[bool, list[str]]:
    missing = [flag for flag in CONFIRMATION_FLAGS if getattr(args, flag) is not True]
    return not missing, missing


def gate_status(write_ready: bool) -> str:
    return "accepted" if write_ready else "operator_unaccepted"


def build_acceptance_payload(draft: dict[str, Any], args: argparse.Namespace, write_ready: bool) -> dict[str, Any]:
    payload = copy.deepcopy(draft)
    payload["version"] = EVIDENCE_VERSION
    payload["not_external_evidence"] = True
    payload["acceptance_ready"] = bool(write_ready)
    payload["strict_fidelity_evidence_ready"] = False
    payload["strict_external_evidence_ready"] = False
    payload["materialized_from_draft_path"] = rel(DRAFT_JSON)
    payload["materialized_by"] = "scripts/materialize_fidelity_acceptance.py"
    payload.pop("draft_only", None)
    payload.pop("template_only", None)
    payload.pop("promotion_ready", None)
    payload.pop("promotion_readiness", None)
    payload.pop("remaining_operator_inputs", None)
    payload.pop("promotion_commands", None)

    platform = payload.get("platform", {})
    platform = platform if isinstance(platform, dict) else {}
    platform["accepted_collection_machine"] = args.accepted_collection_machine
    platform["contact_solver"] = args.contact_solver_and_friction_model
    platform["timestep_seconds"] = args.timestep_and_substeps_per_control_step
    platform["substeps_per_control_step"] = args.timestep_and_substeps_per_control_step
    platform["task_binding_accept_or_replace_decision"] = args.task_binding_decision
    payload["platform"] = platform

    qualification = payload.get("qualification", {})
    qualification = qualification if isinstance(qualification, dict) else {}
    for flag in (
        "pre_registered_before_rollouts",
        "deterministic_paired_resets",
        "shared_skill_library",
        "same_observation_interface",
        "same_compute_budget",
        "no_privileged_state_for_non_oracle",
        "raw_jsonl_is_source_of_truth",
        "videos_tied_to_run_ids",
        "failed_and_abstained_runs_logged",
    ):
        qualification[flag] = True
    qualification["operator_independence_statement"] = (
        f"{args.operator_name_or_lab} confirms independent operation on {args.accepted_collection_machine} "
        "and is not Jason Wang, Haonan Chen, Yilun Du, or another target collaborator for this evidence run."
    )
    qualification["contact_dynamics_justification"] = args.contact_solver_and_friction_model
    qualification["paired_reset_replay_test"] = args.paired_reset_replay_test
    qualification["real_or_benchmark_calibration_basis"] = args.real_or_benchmark_calibration_basis
    qualification["known_limitations"] = args.known_limitations
    qualification["render_backed_video_statement"] = (
        "Operator confirmed render-backed RGB videos are available for evidence runs."
        if args.confirm_render_backed_videos
        else "Operator has not confirmed render-backed RGB evidence videos."
    )
    payload["qualification"] = qualification

    provenance = payload.get("provenance", {})
    provenance = provenance if isinstance(provenance, dict) else {}
    provenance.update(
        {
            "operator_name_or_lab": args.operator_name_or_lab,
            "operator_not_target_collaborator": bool(args.confirm_independent_operator),
            "accepted_collection_machine": args.accepted_collection_machine,
            "date_locked": args.date_locked,
            "code_commit": args.code_commit,
            "skill_library_hash": args.skill_library_hash.upper(),
            "manifest_path": rel(MANIFEST_JSON),
            "artifact_hash_policy": "sha256",
            "manifest_declaration_confirmed_by_operator": bool(args.confirm_manifest_declaration),
            "real_rollout_evidence_confirmed_by_operator": bool(args.confirm_real_rollout_evidence),
        }
    )
    payload["provenance"] = provenance

    task_rows = payload.get("task_fidelity", [])
    task_rows = task_rows if isinstance(task_rows, list) else []
    for row in task_rows:
        if isinstance(row, dict):
            row["operator_task_binding_decision"] = args.task_binding_decision
            row["operator_fidelity_acceptance"] = bool(write_ready)
    payload["task_fidelity"] = task_rows

    gates = []
    for gate in payload.get("acceptance_gates", []) or []:
        if not isinstance(gate, dict):
            continue
        new_gate = dict(gate)
        new_gate["status"] = gate_status(write_ready)
        new_gate["evidence"] = args.acceptance_gate_signoff if write_ready else "operator signoff not supplied"
        gates.append(new_gate)
    payload["acceptance_gates"] = gates
    return payload


def payload_has_contract_shape(payload: dict[str, Any]) -> bool:
    required_top = {"version", "not_external_evidence", "route", "platform", "qualification", "task_fidelity", "provenance", "acceptance_gates"}
    return (
        required_top <= set(payload)
        and payload.get("version") == EVIDENCE_VERSION
        and isinstance(payload.get("platform"), dict)
        and isinstance(payload.get("qualification"), dict)
        and isinstance(payload.get("task_fidelity"), list)
        and isinstance(payload.get("acceptance_gates"), list)
        and len(payload.get("acceptance_gates", [])) >= 5
    )


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    draft = read_json(args.draft)
    text_ready, missing_text = operator_text_ready(args)
    confirm_ready, missing_confirmations = confirmations_ready(args)
    acceptance_write_ready = text_ready and confirm_ready
    candidate = build_acceptance_payload(draft, args, acceptance_write_ready)

    command = (
        "python scripts\\materialize_fidelity_acceptance.py "
        "--operator-name-or-lab <independent_operator_or_lab> "
        "--accepted-collection-machine <machine_or_robot_platform> "
        "--contact-solver-and-friction-model <solver_friction_contact_model> "
        "--timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> "
        "--paired-reset-replay-test <paired_reset_replay_result> "
        "--real-or-benchmark-calibration-basis <calibration_basis> "
        "--task-binding-decision <accepted_or_replaced_task_bindings> "
        "--acceptance-gate-signoff <gate_signoff_summary> "
        "--known-limitations <known_limitations> "
        "--date-locked <YYYY-MM-DD> "
        "--code-commit <commit_sha> "
        "--skill-library-hash <sha256> "
        "--confirm-real-platform --confirm-independent-operator "
        "--confirm-render-backed-videos --confirm-real-rollout-evidence "
        "--confirm-manifest-declaration --write"
    )

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "draft_exists_and_is_draft_version",
        args.draft.exists()
        and draft.get("version") == DRAFT_VERSION
        and draft.get("draft_only") is True
        and draft.get("acceptance_ready") is False,
        f"path={rel(args.draft)}, version={draft.get('version')!r}, draft_only={draft.get('draft_only')!r}",
    )
    add_check(
        checks,
        "materialized_payload_has_contract_shape",
        payload_has_contract_shape(candidate),
        f"version={candidate.get('version')!r}, gates={len(candidate.get('acceptance_gates', []) or [])}",
    )
    add_check(
        checks,
        "operator_text_required_before_write",
        not args.write or text_ready,
        f"write={args.write!r}, missing_text={missing_text}",
    )
    add_check(
        checks,
        "confirmation_flags_required_before_write",
        not args.write or confirm_ready,
        f"write={args.write!r}, missing_confirmations={missing_confirmations}",
    )
    add_check(
        checks,
        "write_requires_complete_operator_signoff",
        not args.write or acceptance_write_ready,
        f"write={args.write!r}, acceptance_write_ready={acceptance_write_ready!r}",
    )
    add_check(
        checks,
        "default_run_does_not_write_real_acceptance_or_manifest",
        args.write or (not OUTPUT_JSON.exists() and not MANIFEST_JSON.exists()),
        f"write={args.write!r}, acceptance_exists={OUTPUT_JSON.exists()}, manifest_exists={MANIFEST_JSON.exists()}",
    )
    gate_statuses = [gate.get("status") for gate in candidate.get("acceptance_gates", []) if isinstance(gate, dict)]
    add_check(
        checks,
        "gates_accepted_only_after_confirmations",
        (acceptance_write_ready and all(status == "accepted" for status in gate_statuses))
        or (not acceptance_write_ready and all(status == "operator_unaccepted" for status in gate_statuses)),
        f"acceptance_write_ready={acceptance_write_ready!r}, gate_statuses={gate_statuses}",
    )
    add_check(
        checks,
        "strict_evidence_remains_external_to_materializer",
        candidate.get("strict_fidelity_evidence_ready") is False
        and candidate.get("strict_external_evidence_ready") is False,
        "materializer can write provenance, but strict audits and manifest evidence still decide readiness",
    )
    add_check(
        checks,
        "operator_write_command_is_guarded",
        "--confirm-real-platform" in command
        and "--confirm-independent-operator" in command
        and "--confirm-render-backed-videos" in command
        and "--confirm-real-rollout-evidence" in command
        and "--confirm-manifest-declaration" in command
        and command.endswith("--write"),
        command,
    )

    passed = all(check["passed"] for check in checks)
    files_written: list[str] = []
    if args.write and not passed:
        raise SystemExit("refusing to write fidelity acceptance because materialization checks did not pass")
    if args.write:
        if OUTPUT_JSON.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite existing acceptance file without --force: {rel(OUTPUT_JSON)}")
        OUTPUT_JSON.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        files_written.append(rel(OUTPUT_JSON))

    return {
        "version": PLAN_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "write_enabled": bool(args.write),
        "acceptance_write_ready": bool(acceptance_write_ready),
        "materialization_ready_for_operator": passed and not args.write,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "source_draft": rel(args.draft),
        "output_path": rel(OUTPUT_JSON),
        "manifest_path": rel(MANIFEST_JSON),
        "missing_operator_text": missing_text,
        "missing_confirmations": missing_confirmations,
        "required_operator_arguments": TEXT_ARGUMENTS,
        "required_confirmations": CONFIRMATION_FLAGS,
        "operator_write_command": command,
        "files_written": files_written,
        "candidate_acceptance_ready": candidate.get("acceptance_ready") is True,
        "candidate_gate_statuses": gate_statuses,
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Fidelity Acceptance Materialization Plan",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Write enabled: `{str(payload['write_enabled']).lower()}`.",
        f"Acceptance write ready: `{str(payload['acceptance_write_ready']).lower()}`.",
        f"Strict fidelity evidence ready: `{str(payload['strict_fidelity_evidence_ready']).lower()}`.",
        "",
        "This report turns the draft fidelity acceptance file into a guarded operator write path. The default run writes only this plan; it does not create `external_validation/fidelity_acceptance.json`, does not create a manifest, and does not satisfy strict fidelity evidence.",
        "",
        "## Operator Write Command",
        "",
        "```powershell",
        payload["operator_write_command"],
        "```",
        "",
        "## Missing Operator Inputs In This Run",
        "",
    ]
    for item in payload["missing_operator_text"] or ["none"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Missing Confirmations In This Run", ""])
    for item in payload["missing_confirmations"] or ["none"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded materializer for Paper 119 fidelity acceptance.")
    parser.add_argument("--draft", type=Path, default=DRAFT_JSON)
    parser.add_argument("--operator-name-or-lab", dest="operator_name_or_lab", default="")
    parser.add_argument("--accepted-collection-machine", dest="accepted_collection_machine", default="")
    parser.add_argument("--contact-solver-and-friction-model", dest="contact_solver_and_friction_model", default="")
    parser.add_argument("--timestep-and-substeps-per-control-step", dest="timestep_and_substeps_per_control_step", default="")
    parser.add_argument("--paired-reset-replay-test", dest="paired_reset_replay_test", default="")
    parser.add_argument("--real-or-benchmark-calibration-basis", dest="real_or_benchmark_calibration_basis", default="")
    parser.add_argument("--task-binding-decision", dest="task_binding_decision", default="")
    parser.add_argument("--acceptance-gate-signoff", dest="acceptance_gate_signoff", default="")
    parser.add_argument("--known-limitations", dest="known_limitations", default="")
    parser.add_argument("--date-locked", dest="date_locked", default="")
    parser.add_argument("--code-commit", dest="code_commit", default="")
    parser.add_argument("--skill-library-hash", dest="skill_library_hash", default="")
    parser.add_argument("--confirm-real-platform", action="store_true")
    parser.add_argument("--confirm-independent-operator", action="store_true")
    parser.add_argument("--confirm-render-backed-videos", action="store_true")
    parser.add_argument("--confirm-real-rollout-evidence", action="store_true")
    parser.add_argument("--confirm-manifest-declaration", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.draft.is_absolute():
        args.draft = ROOT / args.draft

    RESULTS.mkdir(exist_ok=True)
    payload = build_plan(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "Fidelity acceptance materialization plan: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"write={payload['write_enabled']}; "
        f"acceptance_write_ready={payload['acceptance_write_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

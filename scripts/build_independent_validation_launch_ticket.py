from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_DOC = DOCS / "independent_validation_launch_ticket.md"
OUT_EXTERNAL = EXTERNAL / "independent_validation_launch_ticket.md"
OUT_JSON = RESULTS / "independent_validation_launch_ticket_audit.json"
OUT_MD = RESULTS / "independent_validation_launch_ticket_audit.md"

VERSION = "independent_validation_launch_ticket_v1"
AGENDA_IDENTITY = "Adaptive physical world/action models for embodied agents."

EXPECTED_BLOCKERS = [
    "Independent real-robot or accepted high-fidelity external validation evidence",
    "External rollout metrics recomputed from raw JSONL logs",
    "Manifest-declared real task configs replace non-evidence templates",
    "Manifest-declared independent non-oracle baseline evidence and fairness contract",
]

SOURCE_ARTIFACTS = {
    "readiness_gap": "results/submission_readiness_gap_audit.json",
    "closure_brief": "results/external_evidence_closure_brief.json",
    "collection_job": "results/external_collection_job_packet_audit.json",
    "machine_bootstrap": "results/external_collection_machine_bootstrap_audit.json",
    "execution_readiness": "results/external_execution_readiness_audit.json",
    "render_machine": "results/maniskill_render_machine_qualification.json",
}

OPERATOR_FILES = [
    "external_validation/collection_machine_bootstrap.md",
    "external_validation/collection_machine_bootstrap.ps1",
    "external_validation/collection_machine_bootstrap.sh",
    "external_validation/collection_job_packet.md",
    "external_validation/collection_job_commands.ps1",
    "external_validation/collection_job_commands.sh",
    "docs/external_evidence_closure_brief.md",
    "external_validation/operator_release_bundle_README.md",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path, version: str | None = None) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc
    if version is not None and payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def named_checks(payload: dict[str, Any]) -> dict[str, bool]:
    return {str(check.get("name")): check.get("passed") is True for check in payload.get("checks", []) or []}


def missing_requirement_names(gap: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for row in gap.get("requirements", []) or []:
        if isinstance(row, dict) and row.get("status") == "missing" and row.get("submission_blocking") is True:
            names.append(str(row.get("requirement", "")))
    return names


def code_block(language: str, command: str) -> list[str]:
    return [f"```{language}", command, "```"]


def build_ticket(
    gap: dict[str, Any],
    closure: dict[str, Any],
    collection_job: dict[str, Any],
    machine_bootstrap: dict[str, Any],
    execution: dict[str, Any],
    render_machine: dict[str, Any],
) -> str:
    satisfied = int(gap.get("satisfied_requirements", 0) or 0)
    missing = int(gap.get("missing_requirements", 0) or 0)
    total = satisfied + missing
    blocker_count = int(gap.get("blocking_missing_requirements", 0) or 0)
    closure_items = closure.get("closure_items", []) or []
    job_steps = collection_job.get("job_steps", []) or []

    bootstrap_windows = r".\external_validation\collection_machine_bootstrap.ps1 -ConfirmBootstrapOnly -InstallManiSkill -AcceptedBackend <accepted_backend> -ShaderPack <accepted_shader_pack>"
    bootstrap_linux = "./external_validation/collection_machine_bootstrap.sh --confirm-bootstrap-only --install-maniskill --accepted-backend <accepted_backend> --shader-pack <accepted_shader_pack>"
    collection_windows = r".\external_validation\collection_job_commands.ps1 -ConfirmOfficialCollection -AcceptedBackend <accepted_backend> -ShaderPack <accepted_shader_pack> -RunId <accepted_run_id> -OperatorNameOrLab <independent_operator_or_lab> -OperatorId <independent_operator_or_lab> -CollectionMachine <machine_or_robot_platform> -ContactSolverAndFrictionModel <solver_friction_contact_model> -TimestepAndSubstepsPerControlStep <sim_dt_control_dt_substeps> -PairedResetReplayTest <paired_reset_replay_result> -CalibrationBasis <calibration_basis> -TaskBindingDecision <accepted_or_replaced_task_bindings> -AcceptanceGateSignoff <gate_signoff_summary> -KnownLimitations <known_limitations> -DateLocked <YYYY-MM-DD> -DateSealed <YYYY-MM-DD> -CodeCommit <commit_sha> -SkillLibraryHash <sha256>"
    collection_linux = "./external_validation/collection_job_commands.sh --confirm-official-collection --accepted-backend <accepted_backend> --shader-pack <accepted_shader_pack> --run-id <accepted_run_id> --operator-name-or-lab <independent_operator_or_lab> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --date-sealed <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256>"

    lines = [
        "# Independent Validation Launch Ticket",
        "",
        "Not evidence: `true`.",
        f"Launch state: `{collection_job.get('job_state')}`.",
        f"Render-machine state: `{render_machine.get('qualification_state')}`.",
        f"Decision boundary: `{gap.get('current_decision')}`.",
        f"Readiness boundary: `{satisfied}/{total}` requirements satisfied; `{blocker_count}` strict external-evidence blockers remain.",
        f"Agenda identity: {AGENDA_IDENTITY}",
        "",
        "Use this as the copyable issue body for an independent validation operator. Do not create official rollout evidence from this ticket alone; it is a launch/control artifact for the validation run.",
        "",
        "## Issue Title",
        "",
        "Paper 119 independent external validation run: qualify machine, collect official JSONL/MP4 evidence, seal hashes, and promote manifest",
        "",
        "## Start State",
        "",
        "- `DO_NOT_START_COLLECTION_YET`: official collection is blocked until render/liveness, fidelity, backend, run-id, alias, and operator metadata gates pass.",
        "- `DO_NOT_COLLECT_RENDER_MACHINE`: the current local machine is not accepted for official evidence collection.",
        "- Haonan is not required for proof, and the launch route is not Haonan-dependent.",
        "- Do not pitch Haonan as responsible for supplying the missing proof.",
        "- Do not mention Yilun as the validation motive; this ticket is for independent evidence collection.",
        "",
        "## Before Assignment",
        "",
        "- [ ] Independent operator or lab is identified.",
        "- [ ] Accepted real robot or accepted high-fidelity simulator machine is available.",
        "- [ ] Operator has the release bundle README and manifest, plus this launch ticket.",
        "- [ ] Operator agrees that placeholder fields, diagnostic fallback videos, local dry-run records, and template configs cannot count as evidence.",
        "- [ ] Operator understands that `external_validation/manifest.json` must not exist until postcollection strict gates are ready.",
        "",
        "## Attach To Issue",
        "",
    ]
    for item in OPERATOR_FILES:
        lines.append(f"- `{item}`")

    lines.extend(
        [
            "",
            "## Current Strict Blockers",
            "",
        ]
    )
    for item in closure_items:
        requirement = str(item.get("requirement", ""))
        closure_id = str(item.get("closure_id", ""))
        completion = str(item.get("completion_test", ""))
        lines.append(f"- `{closure_id}`: {requirement}. Completion test: {completion}")

    lines.extend(
        [
            "",
            "## Phase 1: Machine Bootstrap",
            "",
            "Run this phase on the independent collection machine. This phase is still non-evidence; it only proves the machine can render, reset, and run the checked path.",
            "",
            "Windows:",
            "",
            *code_block("powershell", bootstrap_windows),
            "",
            "Linux:",
            "",
            *code_block("bash", bootstrap_linux),
            "",
            "Phase 1 acceptance:",
            "",
            "- [ ] `results/maniskill_render_machine_qualification.json` reports `qualification_state=READY_FOR_EXTERNAL_COLLECTION` on the independent machine.",
            "- [ ] Render-backed MP4 export passes for the primary ManiSkill/SAPIEN task families with no diagnostic fallback promotion.",
            "- [ ] Pilot runtime liveness passes with official-video and JSONL write guards intact.",
            "",
            "## Phase 2: Official Collection",
            "",
            "Do not start this phase while any placeholder value remains. The scripts intentionally require explicit confirmation and real operator/platform fields.",
            "",
            "Windows:",
            "",
            *code_block("powershell", collection_windows),
            "",
            "Linux:",
            "",
            *code_block("bash", collection_linux),
            "",
            "Phase 2 acceptance:",
            "",
        ]
    )
    for step in job_steps:
        if not isinstance(step, dict):
            continue
        if step.get("phase") in {"official_collection", "postcollection_seal", "postcollection_validation", "manifest_and_release"}:
            lines.append(f"- [ ] `{step.get('id')}`: {step.get('acceptance')}")

    lines.extend(
        [
            "",
            "## Evidence Upload Contract",
            "",
            "- [ ] `external_validation/logs/*.jsonl` raw official logs.",
            "- [ ] `external_validation/videos/<task_family>/*.mp4` render-backed videos.",
            "- [ ] `external_validation/fidelity_acceptance.json` with independent operator signoff.",
            "- [ ] `external_validation/precollection_freeze_receipt.*` and `external_validation/postcollection_evidence_seal.*`.",
            "- [ ] `external_validation/manifest.json` only after postcollection seal consistency and manifest promotion gates pass.",
            "- [ ] Real method config/checkpoint artifacts for all independent non-oracle baselines, with hashes bound in logs and manifest.",
            "",
            "## Close Criteria",
            "",
            "- [ ] `python scripts\\audit_external_evidence.py --strict` passes.",
            "- [ ] `python scripts\\audit_submission_readiness_gap.py` no longer reports the four strict external-evidence blockers.",
            "- [ ] Raw JSONL rollout metrics recompute from official logs and match the manifest.",
            "- [ ] Manifest-declared task configs replace template/non-evidence configs.",
            "- [ ] Independent non-oracle baseline evidence and fairness contract are manifest-bound.",
            "- [ ] Claim boundary remains honest: no strict evidence is claimed before all above checks pass.",
            "",
            "## Source Packet Status",
            "",
            f"- Collection job packet: `{collection_job.get('job_state')}`, `{len(job_steps)}` ordered steps.",
            f"- Bootstrap packet: `{machine_bootstrap.get('bootstrap_state')}`.",
            f"- Execution packet: ready=`{str(execution.get('execution_packet_ready')).lower()}`, strict evidence ready=`{str(execution.get('strict_evidence_ready')).lower()}`.",
            f"- Closure route: `{closure.get('primary_independent_route')}`, Haonan dependency=`{str(closure.get('haonan_dependency')).lower()}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    gap = read_json(ROOT / SOURCE_ARTIFACTS["readiness_gap"], "submission_readiness_gap_audit_v1")
    closure = read_json(ROOT / SOURCE_ARTIFACTS["closure_brief"], "external_evidence_closure_brief_v1")
    collection_job = read_json(ROOT / SOURCE_ARTIFACTS["collection_job"], "external_collection_job_packet_audit_v1")
    machine_bootstrap = read_json(ROOT / SOURCE_ARTIFACTS["machine_bootstrap"], "external_collection_machine_bootstrap_audit_v1")
    execution = read_json(ROOT / SOURCE_ARTIFACTS["execution_readiness"], "external_execution_readiness_audit_v1")
    render_machine = read_json(ROOT / SOURCE_ARTIFACTS["render_machine"], "maniskill_render_machine_qualification_v1")

    ticket = build_ticket(gap, closure, collection_job, machine_bootstrap, execution, render_machine)
    OUT_DOC.write_text(ticket + "\n", encoding="utf-8")
    OUT_EXTERNAL.write_text(ticket + "\n", encoding="utf-8")

    missing_names = missing_requirement_names(gap)
    closure_names = [str(item.get("requirement", "")) for item in closure.get("closure_items", []) or [] if isinstance(item, dict)]
    collection_checks = named_checks(collection_job)
    bootstrap_checks = named_checks(machine_bootstrap)
    closure_checks = named_checks(closure)
    execution_checks = named_checks(execution)
    operator_files_exist = [item for item in OPERATOR_FILES if (ROOT / item).exists()]
    body = OUT_DOC.read_text(encoding="utf-8")

    checks: list[dict[str, Any]] = []
    add_check(checks, "ticket_is_non_evidence", "Not evidence: `true`." in body, "ticket declares non-evidence")
    add_check(
        checks,
        "readiness_boundary_current",
        gap.get("current_decision") == "STRONG_REVISE"
        and gap.get("objective_complete") is False
        and int(gap.get("satisfied_requirements", 0) or 0) == 17
        and int(gap.get("missing_requirements", 0) or 0) == 4
        and int(gap.get("blocking_missing_requirements", 0) or 0) == 4,
        (
            f"decision={gap.get('current_decision')!r}, satisfied={gap.get('satisfied_requirements')!r}, "
            f"missing={gap.get('missing_requirements')!r}, blocking={gap.get('blocking_missing_requirements')!r}"
        ),
    )
    add_check(
        checks,
        "exact_four_external_blockers_named",
        missing_names == EXPECTED_BLOCKERS and closure_names == EXPECTED_BLOCKERS,
        f"gap={missing_names}, closure={closure_names}",
    )
    add_check(
        checks,
        "source_packets_fail_closed",
        closure.get("passed") is True
        and closure.get("strict_external_evidence_ready") is False
        and closure.get("haonan_dependency") is False
        and collection_job.get("passed") is True
        and collection_job.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and collection_job.get("strict_external_evidence_ready") is False
        and machine_bootstrap.get("passed") is True
        and machine_bootstrap.get("bootstrap_state") == "READY_TO_BOOTSTRAP_EXTERNAL_MACHINE"
        and machine_bootstrap.get("strict_external_evidence_ready") is False
        and execution.get("passed") is True
        and execution.get("execution_packet_ready") is True
        and execution.get("strict_evidence_ready") is False,
        (
            f"closure_strict={closure.get('strict_external_evidence_ready')!r}, "
            f"job_state={collection_job.get('job_state')!r}, "
            f"bootstrap_state={machine_bootstrap.get('bootstrap_state')!r}, "
            f"execution_strict={execution.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "command_files_exist_for_windows_and_linux",
        "external_validation/collection_job_commands.ps1" in collection_job.get("command_files", [])
        and "external_validation/collection_job_commands.sh" in collection_job.get("command_files", [])
        and "external_validation/collection_machine_bootstrap.ps1" in machine_bootstrap.get("command_files", [])
        and "external_validation/collection_machine_bootstrap.sh" in machine_bootstrap.get("command_files", [])
        and len(operator_files_exist) == len(OPERATOR_FILES),
        f"operator_files_exist={len(operator_files_exist)}/{len(OPERATOR_FILES)}",
    )
    add_check(
        checks,
        "collection_guardrails_visible",
        "ConfirmOfficialCollection" in (EXTERNAL / "collection_job_commands.ps1").read_text(encoding="utf-8")
        and "--confirm-official-collection" in (EXTERNAL / "collection_job_commands.sh").read_text(encoding="utf-8")
        and "ConfirmBootstrapOnly" in (EXTERNAL / "collection_machine_bootstrap.ps1").read_text(encoding="utf-8")
        and "--confirm-bootstrap-only" in (EXTERNAL / "collection_machine_bootstrap.sh").read_text(encoding="utf-8")
        and "DO_NOT_START_COLLECTION_YET" in body
        and "`external_validation/manifest.json` must not exist" in body,
        "explicit confirmation and manifest guardrails are visible",
    )
    add_check(
        checks,
        "render_machine_no_go_visible",
        render_machine.get("passed") is True
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and render_machine.get("strict_external_evidence_ready") is False
        and "DO_NOT_COLLECT_RENDER_MACHINE" in body,
        f"qualification_state={render_machine.get('qualification_state')!r}",
    )
    add_check(
        checks,
        "haonan_not_required",
        closure.get("haonan_dependency") is False
        and "Haonan is not required for proof" in body
        and "Do not pitch Haonan as responsible for supplying the missing proof." in body
        and "Do not mention Yilun as the validation motive" in body,
        f"haonan_dependency={closure.get('haonan_dependency')!r}",
    )
    add_check(
        checks,
        "acceptance_criteria_close_all_blockers",
        all(blocker in body for blocker in EXPECTED_BLOCKERS)
        and "audit_external_evidence.py --strict" in body
        and "audit_submission_readiness_gap.py" in body
        and "Raw JSONL rollout metrics recompute" in body
        and "Independent non-oracle baseline evidence" in body,
        "ticket close criteria map to all four blockers",
    )
    add_check(
        checks,
        "source_checks_reused",
        closure_checks.get("exact_four_submission_blockers_mapped") is True
        and collection_checks.get("command_sequence_covers_full_external_validation_route") is True
        and collection_checks.get("official_collection_commands_guarded") is True
        and bootstrap_checks.get("bootstrap_requires_explicit_confirmation") is True
        and bootstrap_checks.get("local_machine_not_promoted") is True
        and execution_checks.get("independent_route_closes_blockers") is True,
        "source audit checks are still passing",
    )
    add_check(
        checks,
        "issue_body_contains_copy_paste_commands",
        ".\\external_validation\\collection_machine_bootstrap.ps1" in body
        and "./external_validation/collection_machine_bootstrap.sh" in body
        and ".\\external_validation\\collection_job_commands.ps1" in body
        and "./external_validation/collection_job_commands.sh" in body
        and "<accepted_run_id>" in body
        and "<independent_operator_or_lab>" in body,
        "Windows and Linux bootstrap/collection commands are present",
    )
    add_check(
        checks,
        "operator_copy_matches_docs_copy",
        OUT_DOC.read_text(encoding="utf-8") == OUT_EXTERNAL.read_text(encoding="utf-8"),
        f"docs={rel(OUT_DOC)}, external={rel(OUT_EXTERNAL)}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before external evidence",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "launch_state": "DO_NOT_START_COLLECTION_YET",
        "render_collection_state": render_machine.get("qualification_state"),
        "haonan_dependency": False,
        "ticket_paths": [rel(OUT_DOC), rel(OUT_EXTERNAL)],
        "source_artifacts": SOURCE_ARTIFACTS,
        "operator_files": OPERATOR_FILES,
        "readiness": {
            "current_decision": gap.get("current_decision"),
            "satisfied_requirements": int(gap.get("satisfied_requirements", 0) or 0),
            "total_requirements": int(gap.get("satisfied_requirements", 0) or 0)
            + int(gap.get("missing_requirements", 0) or 0),
            "blocking_missing_requirements": int(gap.get("blocking_missing_requirements", 0) or 0),
        },
        "strict_blockers": EXPECTED_BLOCKERS,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit_lines = [
        "# Independent Validation Launch Ticket Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Launch state: `{payload['launch_state']}`.",
        f"Render-machine state: `{payload['render_collection_state']}`.",
        f"Ticket: `{rel(OUT_DOC)}` and `{rel(OUT_EXTERNAL)}`.",
        "",
        "This audit checks that the launch ticket is an execution-ready operator issue body while preserving the current STRONG_REVISE, 17/21, no-evidence boundary.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        audit_lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print(
        "Independent validation launch ticket audit: "
        f"{'PASS' if passed else 'FAIL'}; checks={len(checks)}; "
        f"launch_state={payload['launch_state']}; render_state={payload['render_collection_state']}"
    )
    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_EXTERNAL}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

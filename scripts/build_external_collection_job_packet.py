from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_PACKET_JSON = EXTERNAL / "collection_job_packet.json"
OUT_PACKET_MD = EXTERNAL / "collection_job_packet.md"
OUT_COMMANDS = EXTERNAL / "collection_job_commands.ps1"
OUT_CHECKLIST = EXTERNAL / "collection_job_checklist.csv"
OUT_AUDIT_JSON = RESULTS / "external_collection_job_packet_audit.json"
OUT_AUDIT_MD = RESULTS / "external_collection_job_packet_audit.md"

VERSION = "external_collection_job_packet_v1"
AUDIT_VERSION = "external_collection_job_packet_audit_v1"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def require_payload(path: Path, version: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def make_step(
    order: int,
    *,
    phase: str,
    step_id: str,
    owner: str,
    command: str,
    acceptance: str,
    may_run_now: bool,
    official_evidence_boundary: str,
    blocked_until: str,
) -> dict[str, Any]:
    return {
        "order": order,
        "phase": phase,
        "id": step_id,
        "owner": owner,
        "command": command,
        "acceptance": acceptance,
        "may_run_now": bool(may_run_now),
        "official_evidence_boundary": official_evidence_boundary,
        "blocked_until": blocked_until,
    }


def build_job_steps(job_state: str) -> list[dict[str, Any]]:
    no_go = job_state != "READY_FOR_OPERATOR_CONFIRMED_COLLECTION"
    return [
        make_step(
            1,
            phase="machine_qualification",
            step_id="platform_probe",
            owner="independent_operator",
            command="python scripts\\probe_external_platform.py",
            acceptance="Exact collection machine provenance, package versions, renderer/GPU state, code commit, and config/backend hashes are recorded.",
            may_run_now=True,
            official_evidence_boundary="non_evidence_preflight",
            blocked_until="none",
        ),
        make_step(
            2,
            phase="machine_qualification",
            step_id="render_profile_matrix",
            owner="independent_operator",
            command=(
                "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 "
                "--width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> "
                "--profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 "
                "--timeout-diagnosis-width 64 --timeout-diagnosis-height 64"
            ),
            acceptance="Every primary ManiSkill/SAPIEN task family writes renderer-backed RGB MP4s; diagnostic fallback media remain excluded.",
            may_run_now=True,
            official_evidence_boundary="non_evidence_preflight",
            blocked_until="accepted render backend and shader pack are supplied on the collection machine",
        ),
        make_step(
            3,
            phase="machine_qualification",
            step_id="pilot_runtime_liveness",
            owner="independent_operator",
            command="python scripts\\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180",
            acceptance="Pilot liveness reports pilot_runtime_ready=true, render_video_ready=true, runner_io_ready=true, records>=1, videos>=1, and zero diagnostic fallbacks.",
            may_run_now=True,
            official_evidence_boundary="non_evidence_preflight",
            blocked_until="render-backed MP4 export works without diagnostic fallback media",
        ),
        make_step(
            4,
            phase="backend_and_fidelity",
            step_id="backend_contract",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_backend_contract.py --strict --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json",
            acceptance="Selected backend satisfies the runner contract, task configs, alias map, video writer, and metadata requirements before collection readiness is trusted.",
            may_run_now=True,
            official_evidence_boundary="non_evidence_preflight",
            blocked_until="selected backend module exists and is the one to be used for official collection",
        ),
        make_step(
            5,
            phase="backend_and_fidelity",
            step_id="fidelity_acceptance_materialization",
            owner="independent_operator",
            command=(
                "python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> "
                "--accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> "
                "--timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> "
                "--real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> "
                "--acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> "
                "--code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator "
                "--confirm-render-backed-videos --write"
            ),
            acceptance="Independent operator acceptance is materialized only after real platform, render-backed video readiness, paired replay, commit, and skill-library hash confirmations; rollout logs and manifest declaration are postcollection strict gates.",
            may_run_now=False,
            official_evidence_boundary="guarded_acceptance_write",
            blocked_until="all precollection operator fields are real, checkout/hash guards match, and render/liveness gates pass",
        ),
        make_step(
            6,
            phase="collection_gate",
            step_id="strict_collection_readiness",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_collection_readiness.py --strict --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --run-id <accepted_run_id> --unsealed-alias-map",
            acceptance="Strict collection readiness passes with a specific run id, explicit alias unsealing, accepted fidelity, empty official output dirs, and real backend/config inputs.",
            may_run_now=False,
            official_evidence_boundary="non_evidence_go_no_go_gate",
            blocked_until="fidelity acceptance, explicit run id, unsealed aliases, backend module, and render-machine qualification are complete",
        ),
        make_step(
            7,
            phase="collection_gate",
            step_id="precollection_freeze_receipt",
            owner="independent_operator",
            command="python scripts\\build_external_precollection_freeze_receipt.py --backend-module external_validation\\runner\\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
            acceptance="Operator sheet, aliases, configs, candidate method-config hashes, method cutover checklist, manifest draft, runner files, and source audits are hash-locked before official collection.",
            may_run_now=False,
            official_evidence_boundary="precollection_hash_lock",
            blocked_until="strict collection readiness passes and operator metadata is real",
        ),
        make_step(
            8,
            phase="official_collection",
            step_id="official_collection_runner",
            owner="independent_operator",
            command="python external_validation\\runner\\real_collection_runner.py --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id <accepted_run_id> --unsealed-alias-map",
            acceptance="Official JSONL rows and renderer-backed MP4s are produced by the accepted backend under the accepted run id without diagnostic fallback promotion.",
            may_run_now=not no_go,
            official_evidence_boundary="writes_official_logs_and_videos",
            blocked_until="ConfirmOfficialCollection switch, no placeholder fields, freeze receipt, and strict readiness pass",
        ),
        make_step(
            9,
            phase="postcollection_seal",
            step_id="postcollection_evidence_seal",
            owner="independent_operator",
            command="python scripts\\build_external_postcollection_evidence_seal.py --backend-module external_validation\\runner\\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
            acceptance="Raw JSONL logs, rollout videos, prepared configs, precollection receipt, and operator metadata are hash-sealed before manifest promotion.",
            may_run_now=not no_go,
            official_evidence_boundary="postcollection_hash_seal",
            blocked_until="official collection produced complete logs/videos for the accepted run id",
        ),
        make_step(
            10,
            phase="postcollection_seal",
            step_id="postcollection_seal_consistency",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_postcollection_seal_consistency.py",
            acceptance="Sealed raw-log, video, config, precollection, and metadata hashes recompute without drift before manifest promotion.",
            may_run_now=not no_go,
            official_evidence_boundary="postcollection_hash_recompute_gate",
            blocked_until="postcollection evidence seal exists for complete official artifacts",
        ),
        make_step(
            11,
            phase="manifest_and_strict_gates",
            step_id="manifest_promotion",
            owner="jason_or_independent_operator",
            command="python scripts\\build_external_manifest.py --write --check-video-paths",
            acceptance="external_validation/manifest.json is written only from hash-sealed logs, videos, configs, methods, metrics, and release metadata.",
            may_run_now=not no_go,
            official_evidence_boundary="manifest_write",
            blocked_until="postcollection seal consistency passes",
        ),
        make_step(
            12,
            phase="manifest_and_strict_gates",
            step_id="strict_rollout_recompute",
            owner="jason_or_independent_operator",
            command="python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
            acceptance="External rollout metrics are recomputed from raw JSONL logs and MP4 paths under strict sample-count, video, pairing, and confidence gates.",
            may_run_now=not no_go,
            official_evidence_boundary="strict_rollout_metric_gate",
            blocked_until="manifest contains real logs/videos/configs for the accepted run",
        ),
        make_step(
            13,
            phase="manifest_and_strict_gates",
            step_id="strict_config_evidence",
            owner="jason_or_independent_operator",
            command="python scripts\\validate_external_configs.py --strict",
            acceptance="Manifest-declared task configs exist, hash-match, and replace non-evidence templates under strict config evidence rules.",
            may_run_now=not no_go,
            official_evidence_boundary="strict_config_gate",
            blocked_until="manifest declares real configs and hashes",
        ),
        make_step(
            14,
            phase="manifest_and_strict_gates",
            step_id="strict_adapter_evidence",
            owner="jason_or_independent_operator",
            command="python scripts\\validate_external_adapters.py --strict",
            acceptance="All non-oracle methods use manifest-declared independent implementations and checkpoint/config hashes rather than scaffolds or reference adapters.",
            may_run_now=not no_go,
            official_evidence_boundary="strict_method_gate",
            blocked_until="manifest declares independent method evidence for all required baselines",
        ),
        make_step(
            15,
            phase="manifest_and_strict_gates",
            step_id="strict_pairing_integrity",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_pairing_integrity.py --strict",
            acceptance="Paired-reset method panels are complete, unique, and consistent across task/config/method/hash identities.",
            may_run_now=not no_go,
            official_evidence_boundary="strict_pairing_gate",
            blocked_until="manifest-declared raw logs pass rollout recomputation",
        ),
        make_step(
            16,
            phase="manifest_and_strict_gates",
            step_id="strict_release_package",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_release_package.py --strict",
            acceptance="Release package recomputes manifest hashes and rejects internal, staged, diagnostic, fallback, empty-video, and non-MP4-like artifacts.",
            may_run_now=not no_go,
            official_evidence_boundary="strict_release_gate",
            blocked_until="manifest and postcollection hashes are complete",
        ),
        make_step(
            17,
            phase="manifest_and_strict_gates",
            step_id="final_external_evidence_audit",
            owner="jason_or_independent_operator",
            command="python scripts\\audit_external_evidence.py --strict",
            acceptance="The final strict external evidence audit passes only when real/high-fidelity rollouts, configs, videos, methods, metrics, ablations, pairing, and release hashes satisfy all gates.",
            may_run_now=not no_go,
            official_evidence_boundary="final_external_evidence_gate",
            blocked_until="all previous strict gates pass",
        ),
    ]


def build_command_file() -> str:
    return """[CmdletBinding()]
param(
    [switch]$ConfirmOfficialCollection,
    [string]$BackendModule = "external_validation\\runner\\maniskill_reference_backend.py",
    [string]$TaskConfigDir = "external_validation\\configs",
    [string]$AcceptedBackend = "<accepted_backend>",
    [string]$ShaderPack = "<accepted_shader_pack>",
    [string]$RunId = "<accepted_run_id>",
    [string]$OperatorNameOrLab = "<independent_operator_or_lab>",
    [string]$OperatorId = "<independent_operator_or_lab>",
    [string]$CollectionMachine = "<machine_or_robot_platform>",
    [string]$ContactSolverAndFrictionModel = "<solver_friction_contact_model>",
    [string]$TimestepAndSubstepsPerControlStep = "<sim_dt_control_dt_substeps>",
    [string]$PairedResetReplayTest = "<paired_reset_replay_result>",
    [string]$CalibrationBasis = "<calibration_basis>",
    [string]$TaskBindingDecision = "<accepted_or_replaced_task_bindings>",
    [string]$AcceptanceGateSignoff = "<gate_signoff_summary>",
    [string]$KnownLimitations = "<known_limitations>",
    [string]$DateLocked = "<YYYY-MM-DD>",
    [string]$DateSealed = "<YYYY-MM-DD>",
    [string]$CodeCommit = "<commit_sha>",
    [string]$SkillLibraryHash = "<sha256>"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

function Assert-NoPlaceholder {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value.Contains("<") -or $Value.Contains(">")) {
        throw "$Name still has placeholder value: $Value"
    }
}

if (-not $ConfirmOfficialCollection) {
    throw "Refusing official collection. Re-run with -ConfirmOfficialCollection only after render-machine qualification, fidelity acceptance, strict collection readiness, and operator fields are real."
}

foreach ($item in @(
    @("AcceptedBackend", $AcceptedBackend),
    @("ShaderPack", $ShaderPack),
    @("RunId", $RunId),
    @("OperatorNameOrLab", $OperatorNameOrLab),
    @("OperatorId", $OperatorId),
    @("CollectionMachine", $CollectionMachine),
    @("ContactSolverAndFrictionModel", $ContactSolverAndFrictionModel),
    @("TimestepAndSubstepsPerControlStep", $TimestepAndSubstepsPerControlStep),
    @("PairedResetReplayTest", $PairedResetReplayTest),
    @("CalibrationBasis", $CalibrationBasis),
    @("TaskBindingDecision", $TaskBindingDecision),
    @("AcceptanceGateSignoff", $AcceptanceGateSignoff),
    @("KnownLimitations", $KnownLimitations),
    @("DateLocked", $DateLocked),
    @("DateSealed", $DateSealed),
    @("CodeCommit", $CodeCommit),
    @("SkillLibraryHash", $SkillLibraryHash)
)) {
    Assert-NoPlaceholder -Name $item[0] -Value $item[1]
}

Invoke-Native python scripts\\probe_external_platform.py
Invoke-Native python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend $AcceptedBackend --shader-pack $ShaderPack --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
Invoke-Native python scripts\\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180
Invoke-Native python scripts\\audit_external_backend_contract.py --strict --backend-module $BackendModule --task-config-dir $TaskConfigDir --alias-map external_validation\\method_alias_map.json
Invoke-Native python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab $OperatorNameOrLab --accepted-collection-machine $CollectionMachine --contact-solver-and-friction-model $ContactSolverAndFrictionModel --timestep-and-substeps-per-control-step $TimestepAndSubstepsPerControlStep --paired-reset-replay-test $PairedResetReplayTest --real-or-benchmark-calibration-basis $CalibrationBasis --task-binding-decision $TaskBindingDecision --acceptance-gate-signoff $AcceptanceGateSignoff --known-limitations $KnownLimitations --date-locked $DateLocked --code-commit $CodeCommit --skill-library-hash $SkillLibraryHash --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
Invoke-Native python scripts\\audit_external_collection_readiness.py --strict --backend-module $BackendModule --task-config-dir $TaskConfigDir --run-id $RunId --unsealed-alias-map
Invoke-Native python scripts\\build_external_precollection_freeze_receipt.py --backend-module $BackendModule --run-id $RunId --operator-id $OperatorId --collection-machine $CollectionMachine --date-locked $DateLocked --unsealed-alias-map
Invoke-Native python external_validation\\runner\\real_collection_runner.py --backend-module $BackendModule --task-config-dir $TaskConfigDir --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id $RunId --unsealed-alias-map
Invoke-Native python scripts\\build_external_postcollection_evidence_seal.py --backend-module $BackendModule --run-id $RunId --operator-id $OperatorId --collection-machine $CollectionMachine --date-sealed $DateSealed
Invoke-Native python scripts\\audit_external_postcollection_seal_consistency.py
Invoke-Native python scripts\\build_external_manifest.py --write --check-video-paths
Invoke-Native python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict
Invoke-Native python scripts\\validate_external_configs.py --strict
Invoke-Native python scripts\\validate_external_adapters.py --strict
Invoke-Native python scripts\\audit_external_pairing_integrity.py --strict
Invoke-Native python scripts\\audit_external_release_package.py --strict
Invoke-Native python scripts\\audit_external_evidence.py --strict
"""


def build_payload() -> dict[str, Any]:
    operator = require_payload(RESULTS / "external_operator_packet.json", "external_operator_packet_v1")
    collection = require_payload(RESULTS / "external_collection_readiness_audit.json", "external_collection_readiness_audit_v1")
    render_machine = require_payload(RESULTS / "maniskill_render_machine_qualification.json", "maniskill_render_machine_qualification_v1")
    render_self_test = require_payload(
        RESULTS / "maniskill_render_machine_qualification_self_test.json",
        "maniskill_render_machine_qualification_self_test_v1",
    )
    evidence_intake = require_payload(RESULTS / "external_evidence_intake_ledger_audit.json", "external_evidence_intake_ledger_v1")
    precollection_manifest = require_payload(
        RESULTS / "external_precollection_manifest_draft_audit.json",
        "external_precollection_manifest_draft_audit_v1",
    )
    precollection_freeze = require_payload(
        RESULTS / "external_precollection_freeze_receipt_audit.json",
        "external_precollection_freeze_receipt_audit_v1",
    )
    postcollection_seal = require_payload(
        RESULTS / "external_postcollection_evidence_seal_audit.json",
        "external_postcollection_evidence_seal_audit_v1",
    )
    postcollection_consistency = require_payload(
        RESULTS / "external_postcollection_seal_consistency_audit.json",
        "external_postcollection_seal_consistency_audit_v1",
    )

    render_qualified = render_machine.get("render_machine_qualified") is True
    collection_ready = collection.get("collection_ready") is True
    operator_go = operator.get("start_state") == "READY_TO_COLLECT"
    strict_ready = operator.get("strict_evidence_ready") is True
    job_state = (
        "READY_FOR_OPERATOR_CONFIRMED_COLLECTION"
        if render_qualified and collection_ready and operator_go and strict_ready
        else "DO_NOT_START_COLLECTION_YET"
    )
    steps = build_job_steps(job_state)
    command_file_text = build_command_file()
    sequence_ids = [step["id"] for step in steps]
    positions = {step_id: idx for idx, step_id in enumerate(sequence_ids)}
    current_blockers = [
        f"collection_readiness: {item}"
        for item in collection.get("blocking_missing", []) or []
    ] + [
        f"render_machine: {item}"
        for item in render_machine.get("blocking_missing", []) or []
    ]
    remaining_submission_blocker_count = int(operator.get("blocking_missing_count", 0) or 0)

    checks: list[dict[str, Any]] = []
    add_check(checks, "job_packet_is_non_evidence", True, "writes only packet/audit/checklist/guarded command-spine artifacts")
    add_check(
        checks,
        "source_payloads_loaded",
        all(
            payload.get("not_external_evidence") is True
            for payload in (
                operator,
                collection,
                render_machine,
                render_self_test,
                evidence_intake,
                precollection_manifest,
                precollection_freeze,
                postcollection_seal,
                postcollection_consistency,
            )
        ),
        "operator, collection, render, intake, pre/postcollection, and self-test payloads are loaded",
    )
    add_check(
        checks,
        "job_state_fail_closed_until_render_and_collection_ready",
        job_state == "DO_NOT_START_COLLECTION_YET"
        and render_machine.get("render_machine_qualified") is False
        and collection.get("collection_ready") is False
        and operator.get("start_state") == "DO_NOT_COLLECT_YET",
        (
            f"job_state={job_state}, render_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"collection_ready={collection.get('collection_ready')!r}, start_state={operator.get('start_state')!r}"
        ),
    )
    required_ids = {
        "platform_probe",
        "render_profile_matrix",
        "pilot_runtime_liveness",
        "backend_contract",
        "fidelity_acceptance_materialization",
        "strict_collection_readiness",
        "precollection_freeze_receipt",
        "official_collection_runner",
        "postcollection_evidence_seal",
        "postcollection_seal_consistency",
        "manifest_promotion",
        "strict_rollout_recompute",
        "strict_config_evidence",
        "strict_adapter_evidence",
        "strict_pairing_integrity",
        "strict_release_package",
        "final_external_evidence_audit",
    }
    add_check(
        checks,
        "command_sequence_covers_full_external_validation_route",
        required_ids.issubset(set(sequence_ids)),
        f"missing={sorted(required_ids - set(sequence_ids))}",
    )
    add_check(
        checks,
        "command_order_preserves_preflight_collection_manifest_safety",
        positions["platform_probe"]
        < positions["render_profile_matrix"]
        < positions["pilot_runtime_liveness"]
        < positions["backend_contract"]
        < positions["fidelity_acceptance_materialization"]
        < positions["strict_collection_readiness"]
        < positions["precollection_freeze_receipt"]
        < positions["official_collection_runner"]
        < positions["postcollection_evidence_seal"]
        < positions["postcollection_seal_consistency"]
        < positions["manifest_promotion"]
        < positions["final_external_evidence_audit"],
        f"positions={positions}",
    )
    add_check(
        checks,
        "official_collection_commands_guarded",
        "-ConfirmOfficialCollection" in command_file_text
        and "Assert-NoPlaceholder" in command_file_text
        and "real_collection_runner.py" in command_file_text
        and "build_external_manifest.py --write --check-video-paths" in command_file_text
        and "audit_external_evidence.py --strict" in command_file_text,
        "PowerShell job spine requires explicit confirmation, placeholder checks, runner, manifest, and final strict evidence gate",
    )
    add_check(
        checks,
        "current_blockers_explicit_and_mapped",
        len(current_blockers) >= 4
        and remaining_submission_blocker_count == 4
        and evidence_intake.get("blocking_failure_count") == evidence_intake.get("mapped_failure_count"),
        (
            f"current_blockers={len(current_blockers)}, submission_blockers={remaining_submission_blocker_count}, "
            f"mapped={evidence_intake.get('mapped_failure_count')!r}/{evidence_intake.get('blocking_failure_count')!r}"
        ),
    )
    add_check(
        checks,
        "pre_and_postcollection_hash_gates_present",
        precollection_manifest.get("draft_ready") is True
        and precollection_freeze.get("freeze_receipt_ready") is False
        and postcollection_seal.get("postcollection_seal_ready") is False
        and postcollection_consistency.get("seal_consistency_ready") is False,
        (
            f"manifest_draft={precollection_manifest.get('draft_ready')!r}, "
            f"freeze_ready={precollection_freeze.get('freeze_receipt_ready')!r}, "
            f"seal_ready={postcollection_seal.get('postcollection_seal_ready')!r}, "
            f"consistency_ready={postcollection_consistency.get('seal_consistency_ready')!r}"
        ),
    )
    add_check(
        checks,
        "render_machine_self_test_proves_ready_and_fail_closed_cases",
        render_self_test.get("passed") is True
        and render_self_test.get("synthetic_ready_state") == "QUALIFIED_FOR_RENDER_BACKED_PILOT"
        and render_self_test.get("synthetic_fail_closed_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_self_test.get("diagnostic_fallback_rejected") is True,
        (
            f"ready={render_self_test.get('synthetic_ready_state')!r}, "
            f"fail={render_self_test.get('synthetic_fail_closed_state')!r}, "
            f"fallback={render_self_test.get('diagnostic_fallback_rejected')!r}"
        ),
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "job_state": job_state,
        "collection_ready": collection_ready,
        "render_machine_qualified": render_qualified,
        "operator_start_state": operator.get("start_state"),
        "remaining_submission_blocker_count": remaining_submission_blocker_count,
        "current_blockers": current_blockers,
        "job_steps": steps,
        "command_file": rel(OUT_COMMANDS),
        "packet_json": rel(OUT_PACKET_JSON),
        "packet_md": rel(OUT_PACKET_MD),
        "checklist_csv": rel(OUT_CHECKLIST),
        "audit_json": rel(OUT_AUDIT_JSON),
        "audit_md": rel(OUT_AUDIT_MD),
        "source_artifacts": [
            rel(RESULTS / "external_operator_packet.json"),
            rel(RESULTS / "external_collection_readiness_audit.json"),
            rel(RESULTS / "maniskill_render_machine_qualification.json"),
            rel(RESULTS / "maniskill_render_machine_qualification_self_test.json"),
            rel(RESULTS / "external_evidence_intake_ledger_audit.json"),
            rel(RESULTS / "external_precollection_manifest_draft_audit.json"),
            rel(RESULTS / "external_precollection_freeze_receipt_audit.json"),
            rel(RESULTS / "external_postcollection_evidence_seal_audit.json"),
            rel(RESULTS / "external_postcollection_seal_consistency_audit.json"),
        ],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def audit_payload(packet: dict[str, Any]) -> dict[str, Any]:
    payload = dict(packet)
    payload["version"] = AUDIT_VERSION
    payload["packet_version"] = packet["version"]
    payload["packet_path"] = packet["packet_md"]
    return payload


def write_outputs(packet: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    audit = audit_payload(packet)
    OUT_PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_COMMANDS.write_text(build_command_file(), encoding="utf-8")

    with OUT_CHECKLIST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "order",
                "phase",
                "id",
                "owner",
                "may_run_now",
                "official_evidence_boundary",
                "blocked_until",
                "acceptance",
                "command",
            ],
        )
        writer.writeheader()
        writer.writerows(packet["job_steps"])

    lines = [
        "# External Collection Job Packet",
        "",
        f"Passed: `{str(packet['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(packet['strict_external_evidence_ready']).lower()}`.",
        f"Job state: `{packet['job_state']}`.",
        f"Collection ready: `{str(packet['collection_ready']).lower()}`.",
        f"Render machine qualified: `{str(packet['render_machine_qualified']).lower()}`.",
        "",
        "This packet is the ordered operator job for moving from machine qualification to official collection, hash sealing, manifest promotion, and final strict evidence audits. It is not rollout evidence and cannot satisfy the external-evidence requirement by itself.",
        "",
        f"Guarded command spine: `{packet['command_file']}`.",
        f"Operator checklist: `{packet['checklist_csv']}`.",
        "",
    ]
    if packet["current_blockers"]:
        lines.extend(["## Current No-Go Blockers", ""])
        for item in packet["current_blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["## Ordered Job Steps", ""])
    for step in packet["job_steps"]:
        lines.append(f"### {step['order']}. {step['id']}")
        lines.append("")
        lines.append(f"- Phase: `{step['phase']}`")
        lines.append(f"- Owner: `{step['owner']}`")
        lines.append(f"- May run now: `{str(step['may_run_now']).lower()}`")
        lines.append(f"- Boundary: `{step['official_evidence_boundary']}`")
        lines.append(f"- Blocked until: {step['blocked_until']}")
        lines.append(f"- Acceptance: {step['acceptance']}")
        lines.extend(["", "```powershell", step["command"], "```", ""])
    lines.extend(["## Checks", ""])
    for check in packet["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_AUDIT_MD.write_text("\n".join(lines).replace("# External Collection Job Packet", "# External Collection Job Packet Audit", 1) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_payload()
    write_outputs(packet)
    print(json.dumps(audit_payload(packet), indent=2, sort_keys=True))
    return 0 if packet["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

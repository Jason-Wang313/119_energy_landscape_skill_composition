[CmdletBinding()]
param(
    [switch]$ConfirmOfficialCollection,
    [string]$BackendModule = "external_validation\runner\maniskill_reference_backend.py",
    [string]$TaskConfigDir = "external_validation\configs",
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

Invoke-Native python scripts\probe_external_platform.py
Invoke-Native python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend $AcceptedBackend --shader-pack $ShaderPack --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
Invoke-Native python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180
Invoke-Native python scripts\audit_external_backend_contract.py --strict --backend-module $BackendModule --task-config-dir $TaskConfigDir --alias-map external_validation\method_alias_map.json
Invoke-Native python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab $OperatorNameOrLab --accepted-collection-machine $CollectionMachine --contact-solver-and-friction-model $ContactSolverAndFrictionModel --timestep-and-substeps-per-control-step $TimestepAndSubstepsPerControlStep --paired-reset-replay-test $PairedResetReplayTest --real-or-benchmark-calibration-basis $CalibrationBasis --task-binding-decision $TaskBindingDecision --acceptance-gate-signoff $AcceptanceGateSignoff --known-limitations $KnownLimitations --date-locked $DateLocked --code-commit $CodeCommit --skill-library-hash $SkillLibraryHash --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
Invoke-Native python scripts\audit_external_collection_readiness.py --strict --backend-module $BackendModule --task-config-dir $TaskConfigDir --run-id $RunId --unsealed-alias-map
Invoke-Native python scripts\build_external_precollection_freeze_receipt.py --backend-module $BackendModule --run-id $RunId --operator-id $OperatorId --collection-machine $CollectionMachine --date-locked $DateLocked --unsealed-alias-map
Invoke-Native python external_validation\runner\real_collection_runner.py --backend-module $BackendModule --task-config-dir $TaskConfigDir --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id $RunId --unsealed-alias-map
Invoke-Native python scripts\build_external_postcollection_evidence_seal.py --backend-module $BackendModule --run-id $RunId --operator-id $OperatorId --collection-machine $CollectionMachine --date-sealed $DateSealed
Invoke-Native python scripts\audit_external_postcollection_seal_consistency.py
Invoke-Native python scripts\build_external_manifest.py --write --check-video-paths
Invoke-Native python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
Invoke-Native python scripts\validate_external_configs.py --strict
Invoke-Native python scripts\validate_external_adapters.py --strict
Invoke-Native python scripts\audit_external_pairing_integrity.py --strict
Invoke-Native python scripts\audit_external_release_package.py --strict
Invoke-Native python scripts\audit_external_evidence.py --strict

[CmdletBinding()]
param(
    [switch]$ConfirmBootstrapOnly,
    [switch]$InstallManiSkill,
    [string]$AcceptedBackend = "sapien_cuda",
    [string]$ShaderPack = "minimal",
    [ValidateRange(30, 1800)][int]$RenderPreflightTimeoutSeconds = 120,
    [ValidateRange(30, 1800)][int]$PilotTimeoutSeconds = 180
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

if (-not $ConfirmBootstrapOnly) {
    throw "Refusing to bootstrap silently. Re-run with -ConfirmBootstrapOnly on the independent collection machine. This script does not collect official evidence."
}

if ($InstallManiSkill) {
    Invoke-Native python -m pip install --upgrade pip
    Invoke-Native python -m pip install numpy matplotlib imageio imageio-ffmpeg
    Invoke-Native python -m pip install --upgrade mani_skill
    Invoke-Native python -m pip install torch torchvision torchaudio
}

Invoke-Native python scripts\probe_external_platform.py --strict
Invoke-Native python scripts\probe_maniskill_task_bindings.py --strict
Invoke-Native python scripts\probe_maniskill_env_smoke.py --strict
Invoke-Native python scripts\probe_maniskill_fidelity_metadata.py --strict
Invoke-Native python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds $RenderPreflightTimeoutSeconds --max-envs 4 --width 128 --height 128 --render-backend $AcceptedBackend --shader-pack $ShaderPack --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
Invoke-Native python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds $PilotTimeoutSeconds --render-backend $AcceptedBackend --shader-pack $ShaderPack --render-width 128 --render-height 128
Invoke-Native python scripts\build_maniskill_render_machine_qualification.py

Write-Host ""
Write-Host "Bootstrap probes complete. If render-machine qualification is still DO_NOT_COLLECT_RENDER_MACHINE, do not run official collection."

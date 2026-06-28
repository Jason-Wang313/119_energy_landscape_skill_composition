[CmdletBinding()]
param(
    [switch]$InstallDependencies,
    [switch]$SkipExperiment,
    [switch]$SkipOutreach,
    [string]$CanonicalPdf = "C:\Users\wangz\Downloads\119.pdf",
    [ValidateRange(1, 3600)][int]$RenderPreflightTimeoutSeconds = 45,
    [ValidateRange(1, 16)][int]$RenderPreflightMaxEnvs = 4,
    [ValidateRange(1, 8)][int]$RenderProfileMatrixMaxEnvs = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$env:PAPER119_CANONICAL_PDF = $CanonicalPdf

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Body
    )
    Write-Host ""
    Write-Host "==> $Name"
    & $Body
}

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

Push-Location -LiteralPath $RepoRoot
try {
    if ($InstallDependencies) {
        Invoke-Step "Install Python dependencies" {
            Invoke-Native python -m pip install -r requirements.txt
        }
    }

    if (-not $SkipExperiment) {
        Invoke-Step "Regenerate local experiment outputs" {
            Invoke-Native python src\run_experiment.py
        }
    }

    Invoke-Step "Audit local falsification checks" {
        Invoke-Native python scripts\audit_local_falsification.py
    }

    Invoke-Step "Audit holdout robustness checks" {
        Invoke-Native python scripts\audit_holdout_robustness.py
    }

    Invoke-Step "Audit diagnostic mechanism checks" {
        Invoke-Native python scripts\audit_diagnostic_mechanism.py
    }

    Invoke-Step "Audit comparative decision quality" {
        Invoke-Native python scripts\audit_decision_quality.py
    }

    Invoke-Step "Audit seam prediction calibration" {
        Invoke-Native python scripts\audit_seam_prediction_calibration.py
    }

    Invoke-Step "Audit planner-edge policy quality" {
        Invoke-Native python scripts\audit_planner_edge_policy.py
    }

    Invoke-Step "Build local model release card" {
        Invoke-Native python scripts\build_local_model_release.py
    }

    Invoke-Step "Generate manuscript sources" {
        Invoke-Native python scripts\generate_manuscript.py
    }

    Invoke-Step "Audit manuscript number provenance" {
        Invoke-Native python scripts\audit_manuscript_numbers.py
    }

    Invoke-Step "Audit related-work and novelty boundary" {
        Invoke-Native python scripts\audit_related_work.py
    }

    Invoke-Step "Audit reference integrity" {
        Invoke-Native python scripts\audit_reference_integrity.py
    }

    Invoke-Step "Audit manuscript readability and framing" {
        Invoke-Native python scripts\audit_manuscript_readability.py
    }

    Invoke-Step "Run external validation tooling checks" {
        Invoke-Native python scripts\build_external_collection_plan.py
        Invoke-Native python scripts\build_external_analysis_plan.py
        Invoke-Native python scripts\build_independent_validation_route.py
        Invoke-Native python scripts\probe_external_platform.py
        Invoke-Native python scripts\probe_maniskill_task_bindings.py
        Invoke-Native python scripts\probe_maniskill_env_smoke.py
        Invoke-Native python scripts\probe_maniskill_fidelity_metadata.py
        Invoke-Native python scripts\build_external_platform_onboarding.py
        Invoke-Native python scripts\audit_external_fidelity_acceptance.py
        Invoke-Native python scripts\build_external_fidelity_provenance_packet.py
        Invoke-Native python scripts\build_external_fidelity_acceptance_draft.py
        Invoke-Native python scripts\materialize_fidelity_acceptance.py
        Invoke-Native python scripts\self_test_external_fidelity_acceptance.py
        Invoke-Native python scripts\build_external_blind_eval_plan.py
        Invoke-Native python scripts\build_external_runbook.py
        Invoke-Native python scripts\audit_external_runner_harness.py
        Invoke-Native python scripts\audit_external_backend_contract.py
        Invoke-Native python scripts\audit_maniskill_backend_readiness.py
        Invoke-Native python scripts\audit_maniskill_reference_collection_preflight.py
        Invoke-Native python scripts\audit_external_collection_readiness.py
        Invoke-Native python scripts\build_external_backend_integration_packet.py
        Invoke-Native python scripts\self_test_external_runner_backend.py
        Invoke-Native python scripts\audit_external_pilot_smoke.py
        Invoke-Native python scripts\build_external_pilot_smoke_packet.py
        Invoke-Native python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds $RenderPreflightTimeoutSeconds --max-envs $RenderPreflightMaxEnvs --profile-matrix --profile-matrix-max-envs $RenderProfileMatrixMaxEnvs
        Invoke-Native python scripts\audit_maniskill_pilot_runtime_liveness.py
        Invoke-Native python scripts\build_maniskill_render_machine_qualification.py
        Invoke-Native python scripts\validate_external_configs.py
        Invoke-Native python scripts\self_test_external_config_evidence.py
        Invoke-Native python scripts\materialize_external_configs.py
        Invoke-Native python scripts\build_external_config_manifest_packet.py
        Invoke-Native python scripts\build_external_baseline_contract.py
        Invoke-Native python scripts\build_external_adapter_scaffolds.py
        Invoke-Native python scripts\build_external_reference_adapters.py
        Invoke-Native python scripts\build_external_local_dry_run.py
        Invoke-Native python scripts\validate_external_adapters.py
        Invoke-Native python scripts\build_external_method_implementation_packet.py
        Invoke-Native python scripts\self_test_external_adapter_evidence.py
        Invoke-Native python scripts\build_external_manifest.py --allow-missing
        Invoke-Native python scripts\self_test_external_manifest_builder.py
        Invoke-Native python scripts\audit_external_release_package.py
        Invoke-Native python scripts\self_test_external_release_package.py
        Invoke-Native python scripts\audit_external_evidence_preflight.py
        Invoke-Native python scripts\validate_external_rollouts.py --write-results
        Invoke-Native python scripts\audit_external_pairing_integrity.py
        Invoke-Native python scripts\audit_external_evidence.py
        Invoke-Native python scripts\build_external_rollout_evidence_packet.py
        Invoke-Native python scripts\build_external_acquisition_packet.py
        Invoke-Native python scripts\build_external_operator_packet.py
        Invoke-Native python scripts\build_external_operator_handoff_bundle.py
        Invoke-Native python scripts\self_test_external_adapter_scaffold_guard.py
        Invoke-Native python scripts\self_test_external_backend_contract.py
        Invoke-Native python scripts\self_test_external_collection_preflight.py
        Invoke-Native python scripts\self_test_external_rollout_validator.py
        Invoke-Native python scripts\self_test_external_evidence_pipeline.py
        Invoke-Native python scripts\self_test_external_pairing_integrity.py
        Invoke-Native python scripts\audit_external_execution_readiness.py
    }

    Invoke-Step "Compile main PDF" {
        Push-Location -LiteralPath paper
        try {
            Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error main.tex
            Invoke-Native bibtex main
            Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error main.tex
            Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error main.tex
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Copy canonical PDF" {
        Copy-Item -LiteralPath paper\main.pdf -Destination $CanonicalPdf -Force
    }

    Invoke-Step "Audit presentation quality" {
        Invoke-Native python scripts\audit_presentation_quality.py
    }

    Invoke-Step "Audit figure readability" {
        Invoke-Native python scripts\audit_figure_readability.py
    }

    Invoke-Step "Audit camera-ready design" {
        Invoke-Native python scripts\audit_camera_ready_design.py
    }

    if (-not $SkipOutreach) {
        Invoke-Step "Build outreach artifacts" {
            & (Join-Path $RepoRoot "scripts\build_outreach_artifacts.ps1") -Root $RepoRoot
        }
    }

    Invoke-Step "Audit claim boundary before readiness gap" {
        Invoke-Native python scripts\audit_claim_boundary.py
    }

    Invoke-Step "Audit submission readiness gap" {
        Invoke-Native python scripts\audit_submission_readiness_gap.py
    }

    Invoke-Step "Build reviewer response packet" {
        Invoke-Native python scripts\build_reviewer_response_packet.py
    }

    Invoke-Step "Audit visible contribution docs" {
        Invoke-Native python scripts\audit_visible_contribution.py
    }

    Invoke-Step "Audit claim boundary after visible docs" {
        Invoke-Native python scripts\audit_claim_boundary.py
    }

    Invoke-Step "Validate submission artifacts" {
        Invoke-Native python scripts\validate_submission_artifacts.py
    }

    if (-not $SkipOutreach) {
        Invoke-Step "Validate outreach artifacts" {
            Invoke-Native python scripts\validate_outreach_artifacts.py
        }
    }

    Write-Host ""
    Write-Host "Paper 119 local artifact build completed."
    Write-Host "Canonical PDF: $CanonicalPdf"
}
finally {
    Pop-Location
}

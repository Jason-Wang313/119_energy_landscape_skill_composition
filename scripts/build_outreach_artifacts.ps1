param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

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

$outreach = Join-Path $Root "outreach"
Push-Location $outreach
try {
    Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error paper119_one_page_memo.tex
    Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error paper119_one_page_memo.tex
    Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error paper119_four_page_preview.tex
    Invoke-Native pdflatex -interaction=nonstopmode -halt-on-error paper119_four_page_preview.tex
} finally {
    Pop-Location
}

Invoke-Native python (Join-Path $Root "scripts\validate_outreach_artifacts.py")

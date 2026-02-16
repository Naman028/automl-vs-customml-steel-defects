Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$venvActivate = Join-Path $root ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Write-Error "Project .venv not found at $venvActivate. Create it with: python -m venv .venv"
    exit 1
}

& $venvActivate

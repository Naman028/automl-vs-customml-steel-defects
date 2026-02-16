Set-StrictMode -Version Latest

& "$PSScriptRoot\activate.ps1"

$backendPath = Join-Path (Split-Path -Parent $PSScriptRoot) "backend"
Set-Location $backendPath

uvicorn app:app --reload --port 8000


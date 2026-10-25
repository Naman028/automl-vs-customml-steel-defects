$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & "$PSScriptRoot/../.venv/Scripts/python.exe" -m ml.neu.trainer.train @args
    if ($LASTEXITCODE) { throw 'NEU training failed' }
} finally { Pop-Location }

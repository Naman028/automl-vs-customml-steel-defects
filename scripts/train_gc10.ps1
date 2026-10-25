$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & "$PSScriptRoot/../.venv/Scripts/python.exe" -m ml.train_gc10 @args
    if ($LASTEXITCODE) { throw 'GC10 training failed' }
} finally { Pop-Location }

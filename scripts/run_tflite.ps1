$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & "$PSScriptRoot/../.venv/Scripts/python.exe" -m ml.automl.run_tflite @args
    if ($LASTEXITCODE) { throw 'TFLite inference failed' }
} finally { Pop-Location }

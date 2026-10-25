$ErrorActionPreference = 'Stop'
Push-Location "$PSScriptRoot\..\backend\models\CustomML"
try {
    & '..\..\..\.venv\Scripts\python.exe' -m trainer.train @args
    if ($LASTEXITCODE) { throw 'NEU training failed' }
} finally { Pop-Location }

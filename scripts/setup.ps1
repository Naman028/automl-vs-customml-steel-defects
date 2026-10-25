$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
python -m venv .venv
if ($LASTEXITCODE) { throw 'Virtual environment creation failed' }
& .\.venv\Scripts\python.exe -m pip install -r requirements/requirements-dev.txt -r requirements/requirements-evaluation.txt
if ($LASTEXITCODE) { throw 'Python dependency installation failed' }
npm --prefix frontend ci
if ($LASTEXITCODE) { throw 'Frontend dependency installation failed' }
if (-not (Test-Path .env)) { Copy-Item -LiteralPath .env.example -Destination .env }

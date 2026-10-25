param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('neu','gc10')][string]$Task,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$EvaluationArgs
)
$ErrorActionPreference = 'Stop'
$module = if ($Task -eq 'neu') { 'ml.evaluate_shared' } else { 'ml.evaluate_gc10' }
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & "$PSScriptRoot/../.venv/Scripts/python.exe" -m $module @EvaluationArgs
    if ($LASTEXITCODE) { throw 'Evaluation failed' }
} finally { Pop-Location }

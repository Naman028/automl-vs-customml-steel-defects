param([Parameter(Mandatory=$true)][ValidateSet('neu','gc10')][string]$Task)
$scriptName = if ($Task -eq 'neu') { 'evaluate_shared.py' } else { 'evaluate_gc10.py' }
& "$PSScriptRoot\..\.venv\Scripts\python.exe" "$PSScriptRoot\..\backend\models\$scriptName" @args
if ($LASTEXITCODE) { throw 'Evaluation failed' }

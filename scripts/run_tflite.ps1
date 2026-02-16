Set-StrictMode -Version Latest

& "$PSScriptRoot\activate.ps1"

$root = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $root "backend\models\AutoML\run_tflite.py"

python $scriptPath


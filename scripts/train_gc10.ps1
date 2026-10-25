& "$PSScriptRoot\..\.venv\Scripts\python.exe" "$PSScriptRoot\..\backend\models\train_gc10.py" @args
if ($LASTEXITCODE) { throw 'GC10 training failed' }

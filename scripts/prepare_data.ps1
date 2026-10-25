& "$PSScriptRoot\..\.venv\Scripts\python.exe" "$PSScriptRoot\prepare_data.py" @args
if ($LASTEXITCODE) { throw 'Dataset verification failed' }

& "$PSScriptRoot\..\.venv\Scripts\python.exe" "$PSScriptRoot\download_weights.py" @args
if ($LASTEXITCODE) { throw 'Model provisioning failed' }

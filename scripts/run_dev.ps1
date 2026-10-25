param(
    [string]$AutoMLModelPath = "",
    [ValidateSet("local", "dataset")]
    [string]$AssistantMode = "",
    [switch]$InTerminal
)

Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Build backend command arguments.
$backendScript = Join-Path $repoRoot "scripts\run_backend.ps1"
$backendArgs = @()
if ($AutoMLModelPath) {
    $backendArgs += "-AutoMLModelPath"
    $backendArgs += ("'" + $AutoMLModelPath.Replace("'", "''") + "'")
}
if ($AssistantMode) {
    $backendArgs += "-AssistantMode"
    $backendArgs += ("'" + $AssistantMode.Replace("'", "''") + "'")
}

$backendCmd = "& '$backendScript'"
if ($backendArgs.Count -gt 0) {
    $backendCmd = "$backendCmd $($backendArgs -join ' ')"
}

if ($InTerminal) {
    # Run backend in a background job in this same terminal session.
    $jobScript = {
        param($repoRootArg, $backendCmdArg)
        Set-Location $repoRootArg
        Invoke-Expression $backendCmdArg
    }
    Start-Job -Name "industrial_backend" -ScriptBlock $jobScript -ArgumentList $repoRoot, $backendCmd | Out-Null
    Write-Host "Backend started in VS Code terminal job: industrial_backend" -ForegroundColor Cyan
    Write-Host "Use 'Receive-Job industrial_backend -Keep' to view logs and 'Stop-Job industrial_backend' to stop it." -ForegroundColor DarkCyan
}
else {
    # Default behavior: start backend in separate PowerShell window.
    Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoExit", "-Command", $backendCmd) | Out-Null
}

# Start frontend in current terminal.
Set-Location (Join-Path $repoRoot "frontend")
npm run dev

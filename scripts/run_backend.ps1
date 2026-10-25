param(
    [string]$AutoMLModelPath = "",
    [ValidateSet("local", "dataset")]
    [string]$AssistantMode = "",
    [switch]$RestartIfRunning,
    [int]$Port = 8001
)

Set-StrictMode -Version Latest

& "$PSScriptRoot\activate.ps1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"
Set-Location $repoRoot

$existing = Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -and
        $_.CommandLine -like "*uvicorn*" -and
        $_.CommandLine -like "*app:app*" -and
        $_.CommandLine -like "*--port $Port*"
    } |
    Select-Object ProcessId, CommandLine

if ($existing) {
    if (-not $RestartIfRunning) {
        Write-Host "Backend already appears to be running on port $Port. Not starting another process." -ForegroundColor Yellow
        $existing | Format-Table -AutoSize
        Write-Host "Use -RestartIfRunning to stop existing backend process(es) and start with new settings." -ForegroundColor DarkYellow
        exit 1
    }

    Write-Host "Stopping existing backend process(es) on port $Port..." -ForegroundColor Yellow
    $existing | ForEach-Object {
        try {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped process $($_.ProcessId)" -ForegroundColor DarkYellow
        } catch {
            Write-Host "Failed to stop process $($_.ProcessId): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Start-Sleep -Seconds 1
}

if ($AutoMLModelPath) {
    $candidates = @()
    if ([System.IO.Path]::IsPathRooted($AutoMLModelPath)) {
        $candidates += $AutoMLModelPath
    } else {
        $candidates += (Join-Path $repoRoot $AutoMLModelPath)
        $candidates += (Join-Path $backendPath $AutoMLModelPath)
    }

    $resolved = $null
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $resolved = Resolve-Path $candidate -ErrorAction Stop
            break
        }
    }
    if (-not $resolved) {
        throw "AutoML model path not found: $AutoMLModelPath"
    }

    $env:AUTOML_TFLITE_PATH = $resolved.Path
    Write-Host "Using AutoML model: $($env:AUTOML_TFLITE_PATH)" -ForegroundColor Cyan
}

if ($AssistantMode) {
    $env:ASSISTANT_MODE = $AssistantMode
}

Write-Host "Assistant mode: $($env:ASSISTANT_MODE)" -ForegroundColor Cyan

if ($env:ASSISTANT_MODE -eq "dataset") {
    $datasetIndexPath = Join-Path $backendPath "assistant\assistant_dataset_index.json"
    if (-not (Test-Path $datasetIndexPath)) {
        throw "Dataset assistant mode requested but index not found: $datasetIndexPath"
    }
}

$envFile = Join-Path $repoRoot '.env'
if (Test-Path $envFile) {
    python -m uvicorn backend.api.app:app --env-file $envFile --reload --port $Port
} else {
    python -m uvicorn backend.api.app:app --reload --port $Port
}

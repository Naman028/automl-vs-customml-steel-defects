[CmdletBinding(SupportsShouldProcess = $true)]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$targets = @(
    '.mypy_cache', '.ruff_cache', '.pytest_cache', '.coverage', 'coverage.xml',
    'htmlcov', 'frontend/dist', 'frontend/test-results', 'frontend/playwright-report'
) | ForEach-Object { Join-Path $projectRoot $_ }
$targets += Get-ChildItem -LiteralPath $projectRoot -Directory -Filter 'pytest-cache-files*' |
    Select-Object -ExpandProperty FullName

foreach ($sourceDirectory in @('backend', 'ml', 'tests', 'scripts')) {
    $targets += Get-ChildItem -LiteralPath (Join-Path $projectRoot $sourceDirectory) `
        -Directory -Recurse -Filter '__pycache__' |
        Select-Object -ExpandProperty FullName
}

[long]$removedBytes = 0
Push-Location $projectRoot
try {
    foreach ($target in ($targets | Sort-Object -Unique)) {
        $absoluteTarget = [IO.Path]::GetFullPath($target)
        if (-not $absoluteTarget.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) {
            throw "Cleanup target escapes the project: $absoluteTarget"
        }
        if (-not (Test-Path -LiteralPath $absoluteTarget)) { continue }
        $item = Get-Item -LiteralPath $absoluteTarget -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing to follow a linked cleanup target: $absoluteTarget"
        }
        $relativeTarget = $absoluteTarget.Substring($projectRoot.Length + 1).Replace('\', '/')
        $trackedFiles = git ls-files -- $relativeTarget
        if ($LASTEXITCODE) { throw 'Cannot verify tracked files before cleanup' }
        if ($trackedFiles) { throw "Refusing to remove tracked files: $relativeTarget" }
        try {
            $files = if ($item.PSIsContainer) {
                @(Get-ChildItem -LiteralPath $absoluteTarget -File -Recurse -Force)
            } else { @($item) }
            $bytes = ($files | Measure-Object -Property Length -Sum).Sum
            if ($PSCmdlet.ShouldProcess($absoluteTarget, 'Remove regenerable output')) {
                Remove-Item -LiteralPath $absoluteTarget -Recurse -Force
                $removedBytes += $bytes
            }
        } catch [System.UnauthorizedAccessException] {
            Write-Warning "Permission denied; retained $absoluteTarget"
        } catch [System.IO.IOException] {
            Write-Warning "Cleanup could not finish for ${absoluteTarget}: $($_.Exception.Message)"
        }
    }
} finally { Pop-Location }

Write-Output ("Removed {0:N2} MiB of regenerable output." -f ($removedBytes / 1MB))

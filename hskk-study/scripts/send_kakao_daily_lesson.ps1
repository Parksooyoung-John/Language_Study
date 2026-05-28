param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$scriptPath = Join-Path $PSScriptRoot "send_kakao_daily_lesson.py"
$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (Test-Path -LiteralPath $bundledPython) {
    $python = $bundledPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $python = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
} else {
    throw "Python runtime not found. Install Python, or run inside Codex with the bundled runtime available."
}

$argsList = @($scriptPath)
if ($DryRun) {
    $argsList += "--dry-run"
}

Push-Location $projectRoot
try {
    & $python @argsList
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($null -ne $exitCode -and $exitCode -ne 0) {
    exit $exitCode
}

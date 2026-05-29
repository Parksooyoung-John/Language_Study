param(
    [switch]$DryRun,
    [switch]$SkipKakao
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$safeDir = $repoRoot.Path.Replace("\", "/")
$gitBaseArgs = @("-c", "core.excludesfile=", "-c", "safe.directory=$safeDir")
$logDir = Join-Path $repoRoot "hskk-study\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "daily_auto_study.log"

function Write-Log($Message) {
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$stamp $Message" | Tee-Object -FilePath $logPath -Append
}

Push-Location $repoRoot
try {
    Write-Log "daily auto study started"

    $generateArgs = @("-ExecutionPolicy", "Bypass", "-File", ".\hskk-study\scripts\generate_daily_lesson.ps1")
    if ($DryRun) {
        $generateArgs += "-DryRun"
    }
    $generationOutput = powershell @generateArgs
    $generationOutput | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "lesson generation failed"
    }
    $generation = ($generationOutput -join "`n") | ConvertFrom-Json

    if ($DryRun) {
        Write-Log "dry-run complete; skipping commit, push, and Kakao send"
        exit 0
    }

    $trackedStudyPaths = @("hskk-study/mobile/index.html")
    if ($generation.action -eq "create") {
        $trackedStudyPaths += "hskk-study/_workspace"
    }
    $statusLines = git @gitBaseArgs status --porcelain -- $trackedStudyPaths 2>$null
    $changes = @($statusLines | Where-Object { $_ -match '^( M|M |A | A|D | D|R |C |U |\?\?)' })
    if ($changes.Count -gt 0) {
        $lessonTitle = Select-String -Path .\hskk-study\mobile\index.html -Pattern "<h1>" | Select-Object -First 1
        $commitMessage = "Auto-generate HSKK daily lesson $(Get-Date -Format yyyy-MM-dd)"
        git @gitBaseArgs add hskk-study/_workspace hskk-study/mobile/index.html
        git @gitBaseArgs commit -m $commitMessage
        if ($LASTEXITCODE -ne 0) {
            throw "git commit failed"
        }
        git @gitBaseArgs push origin main
        if ($LASTEXITCODE -ne 0) {
            throw "git push failed"
        }
        Write-Log "committed and pushed: $commitMessage"
    } else {
        Write-Log "no study changes to commit"
    }

    if (-not $SkipKakao) {
        powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\send_kakao_daily_lesson.ps1
        if ($LASTEXITCODE -ne 0) {
            throw "Kakao send failed"
        }
        Write-Log "Kakao message sent"
    } else {
        Write-Log "Kakao send skipped"
    }

    Write-Log "daily auto study completed"
} finally {
    Pop-Location
}

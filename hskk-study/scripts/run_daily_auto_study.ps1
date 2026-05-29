param(
    [switch]$DryRun,
    [switch]$SkipKakao
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$safeDir = $repoRoot.Path.Replace("\", "/")
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
    powershell @generateArgs
    if ($LASTEXITCODE -ne 0) {
        throw "lesson generation failed"
    }

    if ($DryRun) {
        Write-Log "dry-run complete; skipping commit, push, and Kakao send"
        exit 0
    }

    $status = git -c safe.directory="$safeDir" status --porcelain
    if ($status) {
        $lessonTitle = Select-String -Path .\hskk-study\mobile\index.html -Pattern "<h1>" | Select-Object -First 1
        $commitMessage = "Auto-generate HSKK daily lesson $(Get-Date -Format yyyy-MM-dd)"
        git -c safe.directory="$safeDir" add hskk-study/_workspace hskk-study/mobile/index.html
        git -c safe.directory="$safeDir" commit -m $commitMessage
        if ($LASTEXITCODE -ne 0) {
            throw "git commit failed"
        }
        git -c safe.directory="$safeDir" push origin main
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

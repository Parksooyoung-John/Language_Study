# HSKK Mobile And Kakao Automation

## Daily Flow

1. Study content is maintained in `_workspace/`.
2. `scripts/generate_daily_lesson.py` creates the next lesson once per date.
3. Mobile-friendly content is rebuilt at `mobile/index.html`.
4. `scripts/run_daily_auto_study.ps1` commits, pushes, and sends the KakaoTalk message.
5. The message links to the mobile lesson page.

## Required Kakao Setup

Create a Kakao Developers app and prepare:

- REST API key
- Refresh token with Talk Message permission
- Allowed redirect URI for the one-time OAuth token flow

Store local secrets in `hskk-study/.env`. Do not commit `.env`.

## Local Test

Run a dry-run first:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1 -DryRun
```

Generate, commit, push, and send a real KakaoTalk message:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1
```

## Daily 8 AM Automation

Preferred schedule:

- Frequency: daily
- Time: 08:00 Asia/Seoul
- Command: `powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1`

If using GitHub Pages, enable Pages for this repository so `HSKK_MOBILE_URL` opens on a phone.

## Failure Behavior

- Lesson generation and mobile rebuild can run without Kakao credentials.
- If `.env` is missing Kakao credentials, commit/push can still complete, then Kakao sending fails with a clear error.
- Running the automation more than once on the same date rebuilds the current mobile page instead of creating duplicate lessons.

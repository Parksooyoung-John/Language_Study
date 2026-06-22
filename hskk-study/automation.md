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
- Client Secret when the Kakao app has Client Secret enabled
- Allowed redirect URI for the one-time OAuth token flow
- `https://parksooyoung-john.github.io` registered under the Kakao app's web domains

Store local secrets in `hskk-study/.env`. Do not commit `.env`.

The origin of `HSKK_MOBILE_URL` must exactly match a web domain registered in Kakao Developers. KakaoTalk can omit the learning button when the link is not available to the app.

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

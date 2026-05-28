# HSKK Mobile And Kakao Automation

## Daily Flow

1. Study content is maintained in `_workspace/`.
2. Mobile-friendly content is exposed through `mobile/index.html`.
3. `scripts/send_kakao_daily_lesson.py` sends a KakaoTalk message to "My Chatroom".
4. The message links to the mobile lesson page.

## Required Kakao Setup

Create a Kakao Developers app and prepare:

- REST API key
- Refresh token with Talk Message permission
- Allowed redirect URI for the one-time OAuth token flow

Store local secrets in `hskk-study/.env`. Do not commit `.env`.

## Local Test

Run a dry-run first:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\send_kakao_daily_lesson.ps1 -DryRun
```

Then send a real KakaoTalk message:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\send_kakao_daily_lesson.ps1
```

## Daily 8 AM Automation

Preferred schedule:

- Frequency: daily
- Time: 08:00 Asia/Seoul
- Command: `powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\send_kakao_daily_lesson.ps1`

If using GitHub Pages, enable Pages for this repository so `HSKK_MOBILE_URL` opens on a phone.

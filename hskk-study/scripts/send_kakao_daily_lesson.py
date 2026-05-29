#!/usr/bin/env python3
"""Send the daily HSKK lesson link to KakaoTalk 'My Chatroom'.

Required environment variables, or matching keys in hskk-study/.env:
- KAKAO_REST_API_KEY
- KAKAO_REFRESH_TOKEN

Optional:
- HSKK_MOBILE_URL
- HSKK_LESSON_TITLE
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import parse, request


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "_workspace"
LOG_DIR = ROOT / "logs"
DEFAULT_MOBILE_URL = "https://parksooyoung-john.github.io/Language_Study/hskk-study/mobile/"


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def latest_lesson_title() -> str:
    override = os.environ.get("HSKK_LESSON_TITLE")
    if override:
        return override
    lesson_files = sorted((WORKSPACE / "04_lessons").glob("lesson_*.md"))
    lesson = lesson_files[-1] if lesson_files else WORKSPACE / "04_lessons" / "lesson_01.md"
    if not lesson.exists():
        return "오늘의 HSKK 30분"
    for line in lesson.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return "오늘의 HSKK 30분"


def review_summary() -> str:
    review = WORKSPACE / "07_review_plan.md"
    if not review.exists():
        return "복습표를 확인하세요."
    rows = []
    for line in review.read_text(encoding="utf-8").splitlines():
        if line.startswith("| 2026-") and "pending" in line:
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 4:
                rows.append(f"{parts[0]}: {parts[2]}")
        if len(rows) == 2:
            break
    return " / ".join(rows) if rows else "오늘 복습 항목을 확인하세요."


def refresh_access_token(rest_api_key: str, refresh_token: str) -> str:
    data = parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": rest_api_key,
            "refresh_token": refresh_token,
        }
    ).encode("utf-8")
    req = request.Request(
        "https://kauth.kakao.com/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    access_token = payload.get("access_token")
    if not access_token:
        raise RuntimeError(f"Kakao token refresh failed: {payload}")
    return access_token


def send_memo(access_token: str, lesson_title: str, mobile_url: str, summary: str) -> dict:
    template = {
        "object_type": "feed",
        "content": {
            "title": "오늘의 HSKK 30분",
            "description": f"{lesson_title}\n{summary}",
            "link": {
                "web_url": mobile_url,
                "mobile_web_url": mobile_url,
            },
        },
        "buttons": [
            {
                "title": "모바일 학습 열기",
                "link": {
                    "web_url": mobile_url,
                    "mobile_web_url": mobile_url,
                },
            }
        ],
    }
    data = parse.urlencode({"template_object": json.dumps(template, ensure_ascii=False)}).encode("utf-8")
    req = request.Request(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def log(message: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / "kakao_daily_lesson.log"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print message payload without sending")
    args = parser.parse_args()

    load_env()
    lesson_title = latest_lesson_title()
    summary = review_summary()
    mobile_url = os.environ.get("HSKK_MOBILE_URL", DEFAULT_MOBILE_URL)

    if args.dry_run:
        print(json.dumps({"title": lesson_title, "summary": summary, "mobile_url": mobile_url}, ensure_ascii=False, indent=2))
        return 0

    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")
    if not rest_api_key or not refresh_token:
        raise SystemExit("Missing KAKAO_REST_API_KEY or KAKAO_REFRESH_TOKEN. Put them in hskk-study/.env or environment variables.")

    access_token = refresh_access_token(rest_api_key, refresh_token)
    result = send_memo(access_token, lesson_title, mobile_url, summary)
    log(json.dumps({"lesson_title": lesson_title, "mobile_url": mobile_url, "result": result}, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

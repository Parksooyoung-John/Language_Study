#!/usr/bin/env python3
"""Send the daily HSKK lesson summary to KakaoTalk 'My Chatroom'.

Required environment variables, or matching keys in hskk-study/.env:
- KAKAO_REST_API_KEY
- KAKAO_REFRESH_TOKEN

Optional:
- KAKAO_CLIENT_SECRET
- HSKK_MOBILE_URL
- HSKK_LESSON_TITLE
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "_workspace"
LOG_DIR = ROOT / "logs"
DEFAULT_MOBILE_URL = "https://parksooyoung-john.github.io/Language_Study/hskk-study/mobile/"
MAX_TEXT_LENGTH = 200
CIRCLED_NUMBERS = ("①", "②", "③", "④", "⑤", "⑥")


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


def latest_lesson_file() -> Path:
    lesson_files = sorted((WORKSPACE / "04_lessons").glob("lesson_*.md"))
    return lesson_files[-1] if lesson_files else WORKSPACE / "04_lessons" / "lesson_01.md"


def latest_lesson_title() -> str:
    override = os.environ.get("HSKK_LESSON_TITLE")
    if override:
        return override
    lesson = latest_lesson_file()
    if not lesson.exists():
        return "오늘의 HSKK 30분"
    for line in lesson.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return "오늘의 HSKK 30분"


def section_rows(lines: list[str], section_prefix: str) -> list[list[str]]:
    rows = []
    in_section = False
    for line in lines:
        if line.startswith(section_prefix):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 4 and parts[0] not in {"Item", "Step", "---", "---:"}:
            rows.append(parts)
    return rows


def pack_section(header: str, blocks: list[str], max_blocks: int | None = None) -> list[str]:
    messages = []
    current = header
    current_count = 0
    for block in blocks:
        candidate = f"{current}\n\n{block}"
        if len(candidate) <= MAX_TEXT_LENGTH and (max_blocks is None or current_count < max_blocks):
            current = candidate
            current_count += 1
            continue
        messages.append(current)
        current = f"{header} (계속)\n\n{block}"
        current_count = 1
    if current != header:
        messages.append(current)
    return messages


def lesson_messages() -> list[str]:
    lesson = latest_lesson_file()
    if not lesson.exists():
        return ["📘 오늘의 HSKK 30분\n학습 내용을 준비하지 못했습니다."]

    lines = lesson.read_text(encoding="utf-8").splitlines()
    title = latest_lesson_title()
    goal = "오늘의 주제로 짧고 정확하게 말해 보세요."
    in_goal = False
    for line in lines:
        if line == "## Goal":
            in_goal = True
            continue
        if in_goal and line.startswith("## "):
            break
        if in_goal and line:
            goal = line
            break
    overview = f"📘 오늘의 HSKK 30분\n{title}\n\n🎯 오늘의 목표\n{goal}\n\n🔊 한자 → 병음 → 뜻 순서로 소리 내어 읽어 보세요."

    part_one = section_rows(lines, "## Part 1:")
    part_two = section_rows(lines, "## Part 2:")
    part_three = section_rows(lines, "## Part 3:")

    repeat_blocks = [
        f"{CIRCLED_NUMBERS[index]} {row[1]}\n{row[2]}\n{row[3]}"
        for index, row in enumerate(part_one[: len(CIRCLED_NUMBERS)])
    ]
    picture_blocks = [
        f"{CIRCLED_NUMBERS[index]} {row[1]}\n{row[2]}\n{row[3]}"
        for index, row in enumerate(part_two[: len(CIRCLED_NUMBERS)])
    ]
    answer_blocks = [
        f"{CIRCLED_NUMBERS[index]} {row[1]}\n{row[2]}\n{row[3]}\n→ {row[4]}"
        for index, row in enumerate(part_three[: len(CIRCLED_NUMBERS)])
        if len(row) >= 5
    ]

    messages = [overview[:MAX_TEXT_LENGTH]]
    messages.extend(pack_section("🗣 1. 듣고 반복", repeat_blocks))
    messages.extend(pack_section("🖼 2. 그림 묘사", picture_blocks, max_blocks=2))
    messages.extend(pack_section("💬 3. 질문 답변", answer_blocks))
    return messages


def refresh_access_token(rest_api_key: str, refresh_token: str, client_secret: str | None = None) -> str:
    params = {
        "grant_type": "refresh_token",
        "client_id": rest_api_key,
        "refresh_token": refresh_token,
    }
    if client_secret:
        params["client_secret"] = client_secret
    data = parse.urlencode(params).encode("utf-8")
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


def build_template(message_text: str, mobile_url: str) -> dict:
    return {
        "object_type": "text",
        "text": message_text,
        "link": {
            "web_url": mobile_url,
            "mobile_web_url": mobile_url,
        },
    }


def send_memos(access_token: str, messages: list[str], mobile_url: str) -> list[dict]:
    results = []
    for message_text in messages:
        template = build_template(message_text, mobile_url)
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
            results.append(json.loads(response.read().decode("utf-8")))
    return results


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
    messages = lesson_messages()
    mobile_url = os.environ.get("HSKK_MOBILE_URL", DEFAULT_MOBILE_URL)

    if args.dry_run:
        print(json.dumps([build_template(message, mobile_url) for message in messages], ensure_ascii=False, indent=2))
        return 0

    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")
    client_secret = os.environ.get("KAKAO_CLIENT_SECRET")
    if not rest_api_key or not refresh_token:
        raise SystemExit("Missing KAKAO_REST_API_KEY or KAKAO_REFRESH_TOKEN. Put them in hskk-study/.env or environment variables.")

    try:
        access_token = refresh_access_token(rest_api_key, refresh_token, client_secret)
        result = send_memos(access_token, messages, mobile_url)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Kakao send failed: HTTP {exc.code}. {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Kakao send failed: network access blocked or Kakao endpoint unreachable. {exc.reason}") from exc
    log(json.dumps({"lesson_title": lesson_title, "mobile_url": mobile_url, "result": result}, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

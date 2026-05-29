#!/usr/bin/env python3
"""Generate the next HSKK lesson and rebuild the mobile page.

This is deterministic on purpose: daily automation must work even when no LLM
session is available. The lesson bank stays beginner/lower-intermediate and
keeps every Mandarin item in Hanzi + Pinyin + Korean meaning + focus format.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "_workspace"
LESSON_DIR = WORKSPACE / "04_lessons"
MOBILE_INDEX = ROOT / "mobile" / "index.html"
STATE_PATH = WORKSPACE / "09_daily_state.json"


@dataclass(frozen=True)
class LessonSeed:
    focus: str
    repeat: tuple[tuple[str, str, str, str], ...]
    scene: str
    picture: tuple[tuple[str, str, str, str], ...]
    questions: tuple[tuple[str, str, str, str], ...]


LESSON_BANK: tuple[LessonSeed, ...] = (
    LessonSeed(
        focus="자기소개와 하루 일과",
        repeat=(
            ("我叫秀英。", "Wǒ jiào Xiùyīng.", "저는 수영입니다.", "이름 소개"),
            ("我现在学习汉语。", "Wǒ xiànzài xuéxí Hànyǔ.", "저는 지금 중국어를 공부합니다.", "현재 시점"),
            ("我每天练习三十分钟。", "Wǒ měitiān liànxí sānshí fēnzhōng.", "저는 매일 30분 연습합니다.", "시간 길이"),
        ),
        scene="한 사람이 책상 앞에 앉아 중국어 교재를 펼치고 휴대폰으로 병음을 확인하고 있습니다.",
        picture=(
            ("这是在家里。", "Zhè shì zài jiālǐ.", "여기는 집입니다.", "장소 소개"),
            ("一个人正在学习汉语。", "Yí ge rén zhèngzài xuéxí Hànyǔ.", "한 사람이 중국어를 공부하고 있습니다.", "진행 표현"),
            ("桌子上有一本书和一部手机。", "Zhuōzi shàng yǒu yì běn shū hé yí bù shǒujī.", "책상 위에 책 한 권과 휴대폰 한 대가 있습니다.", "양사"),
            ("我觉得他很认真。", "Wǒ juéde tā hěn rènzhēn.", "제 생각에는 그가 매우 진지합니다.", "의견 표현"),
        ),
        questions=(
            ("你每天什么时候学习汉语？", "Nǐ měitiān shénme shíhou xuéxí Hànyǔ?", "매일 언제 중국어를 공부하나요?", "我每天...学习汉语。"),
            ("你觉得汉语难吗？", "Nǐ juéde Hànyǔ nán ma?", "중국어가 어렵다고 생각하나요?", "我觉得...，因为..."),
        ),
    ),
    LessonSeed(
        focus="교통과 이동",
        repeat=(
            ("我坐地铁去公司。", "Wǒ zuò dìtiě qù gōngsī.", "저는 지하철을 타고 회사에 갑니다.", "교통수단"),
            ("从我家到公司要三十分钟。", "Cóng wǒ jiā dào gōngsī yào sānshí fēnzhōng.", "집에서 회사까지 30분 걸립니다.", "출발지와 목적지"),
            ("今天路上人很多。", "Jīntiān lùshang rén hěn duō.", "오늘 길에 사람이 많습니다.", "상황 묘사"),
        ),
        scene="버스 정류장에 사람들이 줄을 서 있고, 한 남자가 휴대폰으로 도착 시간을 확인하고 있습니다.",
        picture=(
            ("这是在车站。", "Zhè shì zài chēzhàn.", "여기는 정류장입니다.", "장소"),
            ("很多人在等车。", "Hěn duō rén zài děng chē.", "많은 사람들이 차를 기다리고 있습니다.", "동작"),
            ("一个男人正在看手机。", "Yí ge nánrén zhèngzài kàn shǒujī.", "한 남자가 휴대폰을 보고 있습니다.", "진행"),
            ("他可能在看时间。", "Tā kěnéng zài kàn shíjiān.", "그는 아마 시간을 보고 있는 것 같습니다.", "추측"),
        ),
        questions=(
            ("你常常坐什么车？", "Nǐ chángcháng zuò shénme chē?", "주로 어떤 교통수단을 타나요?", "我常常坐..."),
            ("你喜欢坐地铁还是坐公共汽车？", "Nǐ xǐhuan zuò dìtiě háishi zuò gōnggòng qìchē?", "지하철과 버스 중 무엇을 좋아하나요?", "我喜欢...，因为..."),
        ),
    ),
    LessonSeed(
        focus="음식과 식당",
        repeat=(
            ("我喜欢吃中国菜。", "Wǒ xǐhuan chī Zhōngguó cài.", "저는 중국 음식을 좋아합니다.", "취향"),
            ("这个菜有一点儿辣。", "Zhège cài yǒu yìdiǎnr là.", "이 음식은 조금 맵습니다.", "맛 표현"),
            ("我们一起去吃饭吧。", "Wǒmen yìqǐ qù chīfàn ba.", "우리 같이 밥 먹으러 갑시다.", "제안"),
        ),
        scene="작은 식당에서 두 사람이 메뉴를 보고 있고, 테이블 위에는 만두와 차가 있습니다.",
        picture=(
            ("这是在饭馆。", "Zhè shì zài fànguǎn.", "여기는 식당입니다.", "장소"),
            ("两个人正在看菜单。", "Liǎng ge rén zhèngzài kàn càidān.", "두 사람이 메뉴를 보고 있습니다.", "수량"),
            ("桌子上有饺子和茶。", "Zhuōzi shàng yǒu jiǎozi hé chá.", "테이블 위에 만두와 차가 있습니다.", "음식 어휘"),
            ("我觉得他们很饿。", "Wǒ juéde tāmen hěn è.", "제 생각에는 그들이 배가 고픈 것 같습니다.", "느낌"),
        ),
        questions=(
            ("你喜欢吃什么？", "Nǐ xǐhuan chī shénme?", "무엇을 먹는 것을 좋아하나요?", "我喜欢吃..."),
            ("你常常在家吃饭还是在外面吃饭？", "Nǐ chángcháng zài jiā chīfàn háishi zài wàimiàn chīfàn?", "집에서 자주 먹나요, 밖에서 먹나요?", "我常常...，因为..."),
        ),
    ),
    LessonSeed(
        focus="날씨와 계획",
        repeat=(
            ("今天天气很好。", "Jīntiān tiānqì hěn hǎo.", "오늘 날씨가 좋습니다.", "날씨"),
            ("如果下雨，我就在家学习。", "Rúguǒ xiàyǔ, wǒ jiù zài jiā xuéxí.", "비가 오면 저는 집에서 공부합니다.", "조건"),
            ("周末我想去公园。", "Zhōumò wǒ xiǎng qù gōngyuán.", "주말에 저는 공원에 가고 싶습니다.", "계획"),
        ),
        scene="창밖에는 비가 오고 있고, 한 여자가 창가에서 우산을 들고 밖을 보고 있습니다.",
        picture=(
            ("外面正在下雨。", "Wàimiàn zhèngzài xiàyǔ.", "밖에는 비가 오고 있습니다.", "날씨"),
            ("一个女生拿着雨伞。", "Yí ge nǚshēng názhe yǔsǎn.", "한 여학생이 우산을 들고 있습니다.", "상태"),
            ("她在看外面。", "Tā zài kàn wàimiàn.", "그녀는 밖을 보고 있습니다.", "동작"),
            ("她可能要出门。", "Tā kěnéng yào chūmén.", "그녀는 아마 외출하려는 것 같습니다.", "추측"),
        ),
        questions=(
            ("你喜欢什么天气？", "Nǐ xǐhuan shénme tiānqì?", "어떤 날씨를 좋아하나요?", "我喜欢..."),
            ("下雨的时候你喜欢做什么？", "Xiàyǔ de shíhou nǐ xǐhuan zuò shénme?", "비 올 때 무엇을 하는 것을 좋아하나요?", "下雨的时候，我喜欢..."),
        ),
    ),
    LessonSeed(
        focus="공부 습관",
        repeat=(
            ("我觉得每天复习很重要。", "Wǒ juéde měitiān fùxí hěn zhòngyào.", "저는 매일 복습이 중요하다고 생각합니다.", "의견"),
            ("我先听，然后跟着说。", "Wǒ xiān tīng, ránhòu gēnzhe shuō.", "저는 먼저 듣고, 그 다음 따라 말합니다.", "순서"),
            ("我想提高我的发音。", "Wǒ xiǎng tígāo wǒ de fāyīn.", "저는 제 발음을 향상시키고 싶습니다.", "목표"),
        ),
        scene="한 사람이 노트에 중국어 문장을 쓰고, 옆에 있는 이어폰으로 발음을 듣고 있습니다.",
        picture=(
            ("这是一个学习的场景。", "Zhè shì yí ge xuéxí de chǎngjǐng.", "이것은 공부하는 장면입니다.", "장면 소개"),
            ("他正在写汉字。", "Tā zhèngzài xiě Hànzì.", "그는 한자를 쓰고 있습니다.", "동작"),
            ("他用耳机听发音。", "Tā yòng ěrjī tīng fāyīn.", "그는 이어폰으로 발음을 듣습니다.", "도구"),
            ("这个方法很有用。", "Zhège fāngfǎ hěn yǒu yòng.", "이 방법은 유용합니다.", "평가"),
        ),
        questions=(
            ("你怎么复习汉语？", "Nǐ zěnme fùxí Hànyǔ?", "중국어를 어떻게 복습하나요?", "我先...，然后..."),
            ("你想提高哪方面？", "Nǐ xiǎng tígāo nǎ fāngmiàn?", "어떤 부분을 향상시키고 싶나요?", "我想提高..."),
        ),
    ),
)


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def write_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lesson_number(path: Path) -> int:
    match = re.search(r"lesson_(\d+)\.md$", path.name)
    return int(match.group(1)) if match else 0


def latest_lesson_file() -> Path | None:
    files = sorted(LESSON_DIR.glob("lesson_*.md"), key=lesson_number)
    return files[-1] if files else None


def next_lesson_number() -> int:
    latest = latest_lesson_file()
    return 1 if latest is None else lesson_number(latest) + 1


def seed_for(number: int) -> LessonSeed:
    return LESSON_BANK[(number - 1) % len(LESSON_BANK)]


def lesson_markdown(number: int, seed: LessonSeed, today: str) -> str:
    rows = "\n".join(
        f"| {idx} | {hanzi} | {pinyin} | {meaning} | {focus} |"
        for idx, (hanzi, pinyin, meaning, focus) in enumerate(seed.repeat, 1)
    )
    picture_rows = "\n".join(
        f"| {label} | {hanzi} | {pinyin} | {meaning} | {focus} |"
        for label, (hanzi, pinyin, meaning, focus) in zip(("장소", "인물/행동", "세부사항", "의견/추측"), seed.picture)
    )
    question_rows = "\n".join(
        f"| {idx} | {hanzi} | {pinyin} | {meaning} | {frame} |"
        for idx, (hanzi, pinyin, meaning, frame) in enumerate(seed.questions, 1)
    )
    return f"""# Lesson {number:02d}: {seed.focus}

Status: ready
Date: {today}

## Goal

오늘은 `{seed.focus}` 주제로 HSKK 중급 말하기를 초/중급 문장으로 연습합니다. 한자, 병음, 한국어 뜻을 확인한 뒤 소리 내어 말하세요.

## 30-Minute Flow

| Time | Activity |
| ---: | --- |
| 5 min | 지난 복습 항목 2개 확인 |
| 10 min | Part 1 듣고 반복 3문장 |
| 10 min | Part 2 그림 묘사형 말하기 |
| 5 min | Part 3 질문 답변 + 자기채점 |

## Part 1: 듣고 반복

| Item | Hanzi | Pinyin | Meaning | Focus |
| --- | --- | --- | --- | --- |
{rows}

## Part 2: 그림 묘사

**Scene**: {seed.scene}

| Step | Hanzi | Pinyin | Meaning | Focus |
| --- | --- | --- | --- | --- |
{picture_rows}

## Part 3: 질문 답변

| Item | Hanzi | Pinyin | Meaning | Answer frame |
| --- | --- | --- | --- | --- |
{question_rows}

## Today's Output

| Area | Score 0-5 | Notes |
| --- | ---: | --- |
| Pronunciation and tones |  |  |
| Repetition accuracy |  |  |
| Grammar |  |  |
| Vocabulary |  |  |
| Fluency and timing |  |  |
| Task completion |  |  |

## Notes

답변 transcript나 녹음 메모를 여기에 붙여 넣으면 다음 자동 생성 때 약점 반영 자료로 사용합니다.
"""


def update_review_plan(number: int, seed: LessonSeed, today_date: date) -> None:
    review_path = WORKSPACE / "07_review_plan.md"
    existing = review_path.read_text(encoding="utf-8") if review_path.exists() else "# HSKK Review Plan\n\n"
    if f"Lesson {number:02d}" in existing:
        return
    due_rows = [
        (1, "repeat sentences", "repeat without looking, compare omissions"),
        (3, "picture structure", "scene -> action -> detail -> opinion"),
        (7, "question-answer frames", "answer -> reason -> example -> closing"),
        (14, "weak-point repair", "short oral drill from notes"),
    ]
    insert = "\n".join(
        f"| {today_date.replace(day=today_date.day).toordinal() + offset} | Lesson {number:02d} | {item} | {method} | pending |"
        for offset, item, method in due_rows
    )
    # Convert ordinal placeholders to ISO dates without bringing in timedelta in the format expression.
    from datetime import timedelta

    insert = "\n".join(
        f"| {(today_date + timedelta(days=offset)).isoformat()} | Lesson {number:02d} | {item} | {method} | pending |"
        for offset, item, method in due_rows
    )
    marker = "| Due date | Source | Item | Review method | Status |\n| --- | --- | --- | --- | --- |\n"
    if marker in existing:
        existing = existing.replace(marker, marker + insert + "\n", 1)
    else:
        existing += "\n## Review Queue\n\n" + marker + insert + "\n"
    review_path.write_text(existing, encoding="utf-8")


def update_progress(number: int, today: str) -> None:
    progress = WORKSPACE / "08_progress_report.md"
    text = progress.read_text(encoding="utf-8") if progress.exists() else "# HSKK Progress Report\n\n"
    line = f"\n- {today}: Lesson {number:02d} generated automatically and mobile page rebuilt.\n"
    if line not in text:
        text += "\n## Automation Log\n" if "## Automation Log" not in text else ""
        text += line
    progress.write_text(text, encoding="utf-8")


def build_mobile_html(lesson_path: Path) -> str:
    lesson = lesson_path.read_text(encoding="utf-8")
    title = next((line[2:].strip() for line in lesson.splitlines() if line.startswith("# ")), "오늘의 HSKK 30분")

    def table_after(header: str) -> list[list[str]]:
        start = lesson.find(header)
        if start == -1:
            return []
        section = lesson[start:].split("\n## ", 1)[0]
        rows = []
        for line in section.splitlines():
            if not line.startswith("|") or "---" in line or "Hanzi" in line:
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 5:
                rows.append(cells)
        return rows

    repeat_rows = table_after("## Part 1")
    picture_rows = table_after("## Part 2")
    question_rows = table_after("## Part 3")

    def item_card(cells: list[str], kind: str) -> str:
        if kind == "question":
            hanzi, pinyin, meaning, focus = cells[1], cells[2], cells[3], cells[4]
            tag = cells[0]
        elif kind == "picture":
            tag, hanzi, pinyin, meaning, focus = cells[0], cells[1], cells[2], cells[3], cells[4]
        else:
            tag, hanzi, pinyin, meaning, focus = cells[0], cells[1], cells[2], cells[3], cells[4]
        return f"""
      <article class="item">
        <div><span class="tag">{html.escape(tag)}</span><span class="hanzi">{html.escape(hanzi)}</span></div>
        <div class="pinyin">{html.escape(pinyin)}</div>
        <div class="meaning">{html.escape(meaning)}</div>
        <div class="focus">{html.escape(focus)}</div>
      </article>"""

    repeat_html = "\n".join(item_card(row, "repeat") for row in repeat_rows)
    picture_html = "\n".join(item_card(row, "picture") for row in picture_rows)
    question_html = "\n".join(item_card(row, "question") for row in question_rows)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#172026; --muted:#60707a; --line:#d7e0e5; --paper:#fbfcfd; --accent:#0f766e; --accent-soft:#dff3ef; --warn-soft:#fff1df; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:var(--paper); line-height:1.55; }}
    header {{ padding:22px 18px 14px; background:#fff; border-bottom:1px solid var(--line); position:sticky; top:0; z-index:1; }}
    h1 {{ margin:0; font-size:1.35rem; line-height:1.25; letter-spacing:0; }}
    .sub {{ margin:8px 0 0; color:var(--muted); font-size:.95rem; }}
    main {{ width:min(760px,100%); margin:0 auto; padding:16px; }}
    section {{ padding:18px 0; border-bottom:1px solid var(--line); }}
    h2 {{ margin:0 0 12px; font-size:1.1rem; letter-spacing:0; }}
    .flow {{ display:grid; gap:8px; }}
    .flow div,.item,.scene,.score {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:12px; }}
    .time {{ color:var(--accent); font-weight:700; margin-right:6px; }}
    .item {{ display:grid; gap:8px; margin:10px 0; }}
    .hanzi {{ font-size:1.35rem; font-weight:700; word-break:keep-all; }}
    .pinyin {{ color:var(--accent); font-weight:650; }}
    .meaning,.focus {{ color:var(--muted); }}
    .tag {{ display:inline-block; padding:2px 8px; border-radius:999px; background:var(--accent-soft); color:var(--accent); font-size:.78rem; font-weight:700; margin-right:6px; }}
    .scene {{ background:var(--warn-soft); border-color:#f3c88b; color:#44260b; }}
    label {{ display:block; margin:10px 0 4px; font-weight:650; }}
    input,textarea {{ width:100%; border:1px solid var(--line); border-radius:8px; padding:10px; font:inherit; background:#fff; }}
    textarea {{ min-height:132px; resize:vertical; }}
    button {{ width:100%; border:0; border-radius:8px; padding:12px; margin-top:12px; background:var(--accent); color:#fff; font-weight:800; font-size:1rem; }}
    .small {{ font-size:.88rem; color:var(--muted); }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p class="sub">초/중급 · 한자 + 병음 + 한국어 뜻 · 홈화면 바로가기용</p>
  </header>
  <main>
    <section>
      <h2>학습 흐름</h2>
      <div class="flow">
        <div><span class="time">5분</span>지난 복습 항목 확인</div>
        <div><span class="time">10분</span>듣고 반복 3문장</div>
        <div><span class="time">10분</span>그림 묘사형 말하기</div>
        <div><span class="time">5분</span>질문 답변 + 자기채점</div>
      </div>
    </section>
    <section><h2>Part 1 · 듣고 반복</h2>{repeat_html}</section>
    <section><h2>Part 2 · 그림 묘사</h2>{picture_html}</section>
    <section><h2>Part 3 · 질문 답변</h2>{question_html}</section>
    <section>
      <h2>자기채점 메모</h2>
      <div class="score">
        <label for="score">점수 메모</label>
        <input id="score" placeholder="예: 발음 3, 반복 4, 유창성 2">
        <label for="notes">답변 transcript / 막힌 부분</label>
        <textarea id="notes" placeholder="여기에 말한 답변이나 녹음 메모를 적고 복사해서 Codex에 보내세요."></textarea>
        <button type="button" onclick="copyNotes()">메모 복사</button>
        <p class="small" id="copy-status">복사한 메모를 Codex에 보내면 오답 분석과 다음 레슨에 반영할 수 있습니다.</p>
      </div>
    </section>
  </main>
  <script>
    function copyNotes() {{
      const text = `HSKK 학습 메모\\n레슨: {html.escape(title)}\\n점수: ${{document.getElementById('score').value}}\\n메모:\\n${{document.getElementById('notes').value}}`;
      navigator.clipboard.writeText(text).then(() => {{
        document.getElementById('copy-status').textContent = '복사했습니다. Codex 대화창에 붙여 넣어 주세요.';
      }}).catch(() => {{
        document.getElementById('copy-status').textContent = '복사가 막혔습니다. 내용을 직접 선택해서 복사해 주세요.';
      }});
    }}
  </script>
</body>
</html>
"""


def generate(dry_run: bool = False, today: date | None = None) -> dict:
    today_date = today or date.today()
    today_text = today_date.isoformat()
    state = read_state()

    if state.get("last_generated_date") == today_text and latest_lesson_file():
        lesson_path = latest_lesson_file()
        action = "rebuild"
        number = lesson_number(lesson_path)
    else:
        number = next_lesson_number()
        lesson_path = LESSON_DIR / f"lesson_{number:02d}.md"
        action = "create"

    seed = seed_for(number)
    mobile_html = build_mobile_html(lesson_path) if action == "rebuild" and lesson_path.exists() else None

    if dry_run:
        return {
            "action": action,
            "lesson": str(lesson_path.relative_to(ROOT)),
            "lesson_number": number,
            "focus": seed.focus,
            "date": today_text,
        }

    LESSON_DIR.mkdir(parents=True, exist_ok=True)
    if action == "create":
        lesson_path.write_text(lesson_markdown(number, seed, today_text), encoding="utf-8")
        update_review_plan(number, seed, today_date)
        update_progress(number, today_text)

    mobile_html = build_mobile_html(lesson_path)
    MOBILE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    MOBILE_INDEX.write_text(mobile_html, encoding="utf-8")

    state.update(
        {
            "last_generated_date": today_text,
            "last_lesson_number": number,
            "last_lesson_path": str(lesson_path.relative_to(ROOT)),
            "last_action": action,
        }
    )
    write_state(state)

    return {
        "action": action,
        "lesson": str(lesson_path.relative_to(ROOT)),
        "lesson_number": number,
        "focus": seed.focus,
        "date": today_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(dry_run=args.dry_run), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

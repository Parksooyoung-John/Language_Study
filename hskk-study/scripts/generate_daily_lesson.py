#!/usr/bin/env python3
"""Generate the next HSKK lesson and rebuild the mobile pages.

The generator is deterministic on purpose so the daily automation works even
when no LLM session or external image service is available.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "_workspace"
LESSON_DIR = WORKSPACE / "04_lessons"
MOBILE_DIR = ROOT / "mobile"
MOBILE_INDEX = MOBILE_DIR / "index.html"
MOBILE_LESSON_DIR = MOBILE_DIR / "lessons"
MOBILE_ASSET_DIR = MOBILE_LESSON_DIR / "assets"
MANIFEST_PATH = MOBILE_LESSON_DIR / "manifest.json"
STATE_PATH = WORKSPACE / "09_daily_state.json"
COMPLETED_KEY = "hskk_completed_lessons"
LAST_VIEWED_KEY = "hskk_last_viewed_lesson"
PICTURE_STEP_LABELS = ("장소", "인물/행동", "세부사항", "의견/추측")


@dataclass(frozen=True)
class SceneSpec:
    setting: str
    subjects: tuple[str, ...]
    props: tuple[str, ...]
    mood: str
    layout: str


@dataclass(frozen=True)
class LessonSeed:
    focus: str
    repeat: tuple[tuple[str, str, str, str], ...]
    scene: str
    picture: tuple[tuple[str, str, str, str], ...]
    questions: tuple[tuple[str, str, str, str], ...]
    scene_spec: SceneSpec


LESSON_BANK: tuple[LessonSeed, ...] = (
    LessonSeed(
        focus="자기소개와 하루 습관",
        repeat=(
            ("我叫秀英。", "Wǒ jiào Xiùyīng.", "제 이름은 수영입니다.", "이름 소개"),
            ("我现在学习汉语。", "Wǒ xiànzài xuéxí Hànyǔ.", "저는 지금 중국어를 공부합니다.", "현재 시점"),
            ("我每天练习三十分钟。", "Wǒ měitiān liànxí sānshí fēnzhōng.", "저는 매일 30분 연습합니다.", "시간 길이"),
        ),
        scene="한 사람이 책상 앞에 앉아 중국어 교재를 펼치고 휴대폰으로 병음을 확인하고 있습니다.",
        picture=(
            ("这是在家里。", "Zhè shì zài jiālǐ.", "여기는 집입니다.", "장소 소개"),
            ("一个人正在学习汉语。", "Yí ge rén zhèngzài xuéxí Hànyǔ.", "한 사람이 중국어를 공부하고 있습니다.", "진행 표현"),
            ("桌子上有一本书和一部手机。", "Zhuōzi shàng yǒu yì běn shū hé yí bù shǒujī.", "책상 위에 책 한 권과 휴대폰 한 대가 있습니다.", "묘사"),
            ("我觉得他很认真。", "Wǒ juéde tā hěn rènzhēn.", "저는 그가 매우 진지하다고 생각합니다.", "의견 표현"),
        ),
        questions=(
            ("你每天什么时候学习汉语？", "Nǐ měitiān shénme shíhou xuéxí Hànyǔ?", "매일 언제 중국어를 공부하나요?", "我每天...学习汉语。"),
            ("你觉得汉语难吗？", "Nǐ juéde Hànyǔ nán ma?", "중국어가 어렵다고 생각하나요?", "我觉得...因为..."),
        ),
        scene_spec=SceneSpec(
            setting="study-desk",
            subjects=("student",),
            props=("book", "phone", "chair"),
            mood="focused",
            layout="desk-center",
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
            ("你喜欢坐地铁还是坐公共汽车？", "Nǐ xǐhuan zuò dìtiě háishi zuò gōnggòng qìchē?", "지하철과 버스 중 무엇을 더 좋아하나요?", "我喜欢...因为..."),
        ),
        scene_spec=SceneSpec(
            setting="bus-stop",
            subjects=("crowd", "man"),
            props=("phone", "sign", "bench"),
            mood="busy",
            layout="queue-left",
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
            ("桌子上有饺子和茶。", "Zhuōzi shàng yǒu jiǎozi hé chá.", "테이블 위에 만두와 차가 있습니다.", "음식 디테일"),
            ("我觉得他们很开心。", "Wǒ juéde tāmen hěn kāixīn.", "저는 그들이 매우 즐거워 보인다고 생각합니다.", "분위기"),
        ),
        questions=(
            ("你喜欢吃什么？", "Nǐ xǐhuan chī shénme?", "무엇을 먹는 것을 좋아하나요?", "我喜欢吃..."),
            ("你常常在家吃饭还是在外面吃饭？", "Nǐ chángcháng zài jiā chīfàn háishi zài wàimiàn chīfàn?", "집에서 자주 먹나요, 밖에서 먹나요?", "我常常在...吃饭，因为..."),
        ),
        scene_spec=SceneSpec(
            setting="restaurant",
            subjects=("pair",),
            props=("menu", "dumplings", "tea"),
            mood="warm",
            layout="table-center",
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
            ("一个女生拿着雨伞。", "Yí ge nǚshēng názhe yǔsǎn.", "한 여자가 우산을 들고 있습니다.", "상태"),
            ("她在看外面。", "Tā zài kàn wàimiàn.", "그녀는 밖을 보고 있습니다.", "동작"),
            ("她可能要出门。", "Tā kěnéng yào chūmén.", "그녀는 아마 외출하려는 것 같습니다.", "추측"),
        ),
        questions=(
            ("你喜欢什么天气？", "Nǐ xǐhuan shénme tiānqì?", "어떤 날씨를 좋아하나요?", "我喜欢..."),
            ("下雨的时候你喜欢做什么？", "Xiàyǔ de shíhou nǐ xǐhuan zuò shénme?", "비 올 때 무엇을 하는 것을 좋아하나요?", "下雨的时候，我喜欢..."),
        ),
        scene_spec=SceneSpec(
            setting="rain-window",
            subjects=("woman",),
            props=("umbrella", "window", "rain"),
            mood="calm",
            layout="window-right",
        ),
    ),
    LessonSeed(
        focus="공부 습관",
        repeat=(
            ("我觉得每天复习很重要。", "Wǒ juéde měitiān fùxí hěn zhòngyào.", "저는 매일 복습이 중요하다고 생각합니다.", "생각"),
            ("我先听，然后跟着说。", "Wǒ xiān tīng, ránhòu gēnzhe shuō.", "저는 먼저 듣고, 그다음 따라 말합니다.", "순서"),
            ("我想提高我的发音。", "Wǒ xiǎng tígāo wǒ de fāyīn.", "저는 제 발음을 향상시키고 싶습니다.", "목표"),
        ),
        scene="한 사람이 노트에 중국어 문장을 쓰고, 옆에 있는 이어폰으로 발음을 듣고 있습니다.",
        picture=(
            ("这是一个学习的场景。", "Zhè shì yí ge xuéxí de chǎngjǐng.", "이곳은 공부하는 장면입니다.", "장면 소개"),
            ("他正在写汉字。", "Tā zhèngzài xiě Hànzì.", "그는 한자를 쓰고 있습니다.", "동작"),
            ("他用耳机听发音。", "Tā yòng ěrjī tīng fāyīn.", "그는 이어폰으로 발음을 듣고 있습니다.", "도구"),
            ("这个方法很有用。", "Zhège fāngfǎ hěn yǒu yòng.", "이 방법은 유용합니다.", "평가"),
        ),
        questions=(
            ("你怎么复习汉语？", "Nǐ zěnme fùxí Hànyǔ?", "중국어를 어떻게 복습하나요?", "我先...然后..."),
            ("你想提高哪方面？", "Nǐ xiǎng tígāo nǎ fāngmiàn?", "어떤 부분을 향상시키고 싶나요?", "我想提高..."),
        ),
        scene_spec=SceneSpec(
            setting="study-notes",
            subjects=("student",),
            props=("notebook", "earphones", "pen"),
            mood="steady",
            layout="desk-left",
        ),
    ),
)


@dataclass(frozen=True)
class LessonPage:
    number: int
    title: str
    date: str
    goal: str
    flow: tuple[tuple[str, str], ...]
    scene: str
    repeat: tuple[tuple[str, str, str, str, str], ...]
    picture: tuple[tuple[str, str, str, str, str], ...]
    questions: tuple[tuple[str, str, str, str, str], ...]
    score_rows: tuple[str, ...]
    notes: str


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def write_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lesson_number(path: Path) -> int:
    match = re.search(r"lesson_(\d+)\.md$", path.name)
    return int(match.group(1)) if match else 0


def lesson_slug(number: int) -> str:
    return f"lesson_{number:02d}"


def lesson_title(number: int, focus: str) -> str:
    return f"Lesson {number:02d}: {focus}"


def lesson_file(number: int) -> Path:
    return LESSON_DIR / f"{lesson_slug(number)}.md"


def lesson_page_file(number: int) -> Path:
    return MOBILE_LESSON_DIR / f"{lesson_slug(number)}.html"


def lesson_svg_file(number: int) -> Path:
    return MOBILE_ASSET_DIR / f"{lesson_slug(number)}_part2.svg"


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
        for label, (hanzi, pinyin, meaning, focus) in zip(PICTURE_STEP_LABELS, seed.picture)
    )
    question_rows = "\n".join(
        f"| {idx} | {hanzi} | {pinyin} | {meaning} | {frame} |"
        for idx, (hanzi, pinyin, meaning, frame) in enumerate(seed.questions, 1)
    )
    return f"""# {lesson_title(number, seed.focus)}

Status: ready
Date: {today}

## Goal

오늘은 `{seed.focus}` 주제로 HSKK 중급 말하기를 짧은 문장으로 연습합니다. 한자, 병음, 한국어 뜻을 함께 확인하면서 바로 말해 보세요.

## 30-Minute Flow

| Time | Activity |
| ---: | --- |
| 5 min | 지난 복습 항목 2개 확인 |
| 10 min | Part 1 듣고 반복 3문장 |
| 10 min | Part 2 그림 묘사 말하기 |
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

음성 transcript나 녹음 메모를 여기에 붙여 넣으면 다음 자동 생성 때 약점 반영 자료로 사용할 수 있습니다.
"""


def update_review_plan(number: int, today_date: date) -> None:
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


def parse_table(lines: list[str], expected_columns: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        if "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != expected_columns:
            continue
        if cells[0] in {"Item", "Step", "Area", "Time"}:
            continue
        rows.append(cells)
    return rows


def section_text(section_map: dict[str, list[str]], name: str) -> list[str]:
    return section_map.get(name, [])


def parse_lesson_page(lesson_path: Path) -> LessonPage:
    raw_lines = lesson_path.read_text(encoding="utf-8").splitlines()
    headers: dict[str, list[str]] = {}
    current = "__head__"
    headers[current] = []
    for line in raw_lines:
        if line.startswith("## "):
            current = line[3:].strip()
            headers[current] = []
            continue
        headers[current].append(line)

    head_lines = headers["__head__"]
    title_line = next((line[2:].strip() for line in head_lines if line.startswith("# ")), lesson_path.stem)
    date_line = next((line.removeprefix("Date:").strip() for line in head_lines if line.startswith("Date:")), "")
    goal_lines = [line for line in section_text(headers, "Goal") if line.strip()]
    flow_rows = parse_table(section_text(headers, "30-Minute Flow"), 2)
    picture_intro = [line for line in section_text(headers, "Part 2: 그림 묘사") if line.strip()]
    scene_line = next((line.removeprefix("**Scene**:").strip() for line in picture_intro if line.startswith("**Scene**:")), "")
    repeat_rows = parse_table(section_text(headers, "Part 1: 듣고 반복"), 5)
    picture_rows = parse_table(section_text(headers, "Part 2: 그림 묘사"), 5)
    question_rows = parse_table(section_text(headers, "Part 3: 질문 답변"), 5)
    score_rows = tuple(row[0] for row in parse_table(section_text(headers, "Today's Output"), 3))
    notes = "\n".join(section_text(headers, "Notes")).strip()
    number_match = re.search(r"Lesson (\d+)", title_line)
    number = int(number_match.group(1)) if number_match else lesson_number(lesson_path)
    return LessonPage(
        number=number,
        title=title_line,
        date=date_line,
        goal="\n".join(goal_lines),
        flow=tuple((row[0], row[1]) for row in flow_rows),
        scene=scene_line,
        repeat=tuple(tuple(row) for row in repeat_rows),
        picture=tuple(tuple(row) for row in picture_rows),
        questions=tuple(tuple(row) for row in question_rows),
        score_rows=score_rows,
        notes=notes,
    )


def manifest_record(page: LessonPage, has_next: bool) -> dict[str, object]:
    number = page.number
    slug = lesson_slug(number)
    prev_link = f"./{lesson_slug(number - 1)}.html" if number > 1 else None
    next_link = f"./{lesson_slug(number + 1)}.html" if has_next else None
    return {
        "number": number,
        "slug": slug,
        "title": page.title,
        "date": page.date,
        "path": f"./{slug}.html",
        "prev_path": prev_link,
        "next_path": next_link,
        "visual_path": f"./assets/{slug}_part2.svg",
    }


def html_items(rows: tuple[tuple[str, str, str, str, str], ...], kind: str) -> str:
    cards: list[str] = []
    for row in rows:
        if kind == "question":
            tag, hanzi, pinyin, meaning, focus = row[0], row[1], row[2], row[3], row[4]
        else:
            tag, hanzi, pinyin, meaning, focus = row
        cards.append(
            f"""
      <article class="item">
        <div class="item-top"><span class="tag">{html.escape(tag)}</span><span class="hanzi">{html.escape(hanzi)}</span></div>
        <div class="pinyin">{html.escape(pinyin)}</div>
        <div class="meaning">{html.escape(meaning)}</div>
        <div class="focus">{html.escape(focus)}</div>
      </article>"""
        )
    return "\n".join(cards)


def mobile_style() -> str:
    return """
    :root {
      --ink:#172026;
      --muted:#60707a;
      --line:#d7e0e5;
      --paper:#f5f7f8;
      --card:#ffffff;
      --accent:#0f766e;
      --accent-soft:#dff3ef;
      --warn-soft:#fff1df;
      --warn-line:#f3c88b;
      --shadow:0 14px 35px rgba(23, 32, 38, .08);
    }
    * { box-sizing:border-box; }
    body {
      margin:0;
      font-family:"Noto Sans KR","Apple SD Gothic Neo","Segoe UI",sans-serif;
      color:var(--ink);
      background:
        radial-gradient(circle at top right, rgba(15,118,110,.10), transparent 26%),
        linear-gradient(180deg, #fbfcfd 0%, var(--paper) 100%);
      line-height:1.55;
    }
    a { color:inherit; }
    header {
      padding:24px 18px 16px;
      background:rgba(255,255,255,.92);
      backdrop-filter:blur(14px);
      border-bottom:1px solid var(--line);
      position:sticky;
      top:0;
      z-index:5;
    }
    .eyebrow {
      display:inline-flex;
      gap:8px;
      align-items:center;
      padding:6px 10px;
      border-radius:999px;
      background:var(--accent-soft);
      color:var(--accent);
      font-size:.78rem;
      font-weight:800;
      letter-spacing:.02em;
      text-transform:uppercase;
    }
    h1 {
      margin:12px 0 0;
      font-size:1.45rem;
      line-height:1.25;
      word-break:keep-all;
    }
    .sub {
      margin:10px 0 0;
      color:var(--muted);
      font-size:.96rem;
    }
    main {
      width:min(840px, 100%);
      margin:0 auto;
      padding:18px 16px 42px;
    }
    section {
      margin-top:16px;
      padding:18px;
      border:1px solid var(--line);
      border-radius:18px;
      background:rgba(255,255,255,.92);
      box-shadow:var(--shadow);
    }
    h2 {
      margin:0 0 12px;
      font-size:1.1rem;
    }
    .flow {
      display:grid;
      gap:10px;
    }
    .flow-step, .item, .score, .visual-card, .helper-card {
      background:var(--card);
      border:1px solid var(--line);
      border-radius:14px;
      padding:13px;
    }
    .flow-step {
      display:flex;
      gap:10px;
      align-items:flex-start;
    }
    .time {
      min-width:62px;
      color:var(--accent);
      font-weight:800;
    }
    .item {
      display:grid;
      gap:7px;
      margin-top:10px;
    }
    .item-top {
      display:flex;
      gap:8px;
      align-items:flex-start;
      flex-wrap:wrap;
    }
    .tag {
      display:inline-block;
      padding:2px 8px;
      border-radius:999px;
      background:var(--accent-soft);
      color:var(--accent);
      font-size:.78rem;
      font-weight:800;
    }
    .hanzi {
      font-size:1.35rem;
      font-weight:800;
      word-break:keep-all;
    }
    .pinyin {
      color:var(--accent);
      font-weight:700;
    }
    .meaning, .focus, .small {
      color:var(--muted);
    }
    .scene-text {
      margin:0;
      background:var(--warn-soft);
      border:1px solid var(--warn-line);
      border-radius:14px;
      padding:13px;
      color:#5d3b0d;
    }
    .visual-card {
      overflow:hidden;
      padding:0;
    }
    .visual-card img {
      display:block;
      width:100%;
      height:auto;
      background:linear-gradient(180deg, #eff9f7 0%, #ffffff 100%);
    }
    .visual-caption {
      padding:12px 14px 14px;
      border-top:1px solid var(--line);
    }
    .helper-card ol {
      margin:0;
      padding-left:18px;
    }
    .helper-card li + li {
      margin-top:6px;
    }
    .score-grid {
      display:grid;
      gap:10px;
      margin-top:8px;
    }
    label {
      display:block;
      margin:10px 0 4px;
      font-weight:700;
    }
    input, textarea {
      width:100%;
      border:1px solid var(--line);
      border-radius:12px;
      padding:10px 12px;
      font:inherit;
      background:#fff;
    }
    textarea {
      min-height:132px;
      resize:vertical;
    }
    button, .button-link {
      width:100%;
      border:0;
      border-radius:14px;
      padding:13px 14px;
      margin-top:12px;
      background:var(--accent);
      color:#fff;
      font-weight:800;
      font-size:1rem;
      text-decoration:none;
      text-align:center;
      display:inline-block;
    }
    .button-secondary {
      background:#dfe7eb;
      color:#243239;
    }
    .status-box {
      margin-top:12px;
      min-height:24px;
      color:var(--muted);
      font-size:.92rem;
    }
    .nav-row {
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:10px;
      margin-top:16px;
    }
    .summary-grid {
      display:grid;
      gap:10px;
    }
    .summary-card {
      padding:14px;
      border:1px solid var(--line);
      border-radius:14px;
      background:var(--card);
    }
    .summary-card strong {
      display:block;
      font-size:1.05rem;
      margin-bottom:4px;
    }
    @media (max-width: 640px) {
      h1 { font-size:1.28rem; }
      .nav-row { grid-template-columns:1fr; }
    }
    """


def render_lesson_svg(number: int, seed: LessonSeed) -> str:
    palette = {
        "focused": ("#f4fbff", "#dceffd", "#2d5f7a"),
        "busy": ("#fff8f0", "#ffe2ba", "#92521b"),
        "warm": ("#fff8f4", "#ffd8c5", "#8b4c2f"),
        "calm": ("#f6f5ff", "#ddd8ff", "#5b4b9a"),
        "steady": ("#f4fff8", "#caefd7", "#2a7a58"),
    }
    bg, accent_soft, accent_dark = palette.get(seed.scene_spec.mood, ("#f7f8fb", "#dde3ea", "#38506a"))
    spec = seed.scene_spec

    base_shapes = [
        f'<rect x="0" y="0" width="960" height="540" rx="36" fill="{bg}" />',
        '<rect x="40" y="48" width="880" height="444" rx="30" fill="#ffffff" stroke="#d7e0e5" stroke-width="3" />',
    ]

    if spec.setting in {"study-desk", "study-notes"}:
        base_shapes.extend(
            [
                '<rect x="150" y="310" width="660" height="110" rx="24" fill="#d5b28c" />',
                '<rect x="210" y="226" width="230" height="150" rx="18" fill="#fdf4db" stroke="#d8c497" stroke-width="3" />',
                '<rect x="510" y="236" width="120" height="180" rx="18" fill="#1f2937" />',
                '<circle cx="355" cy="196" r="52" fill="#ffd9b3" />',
                '<rect x="320" y="245" width="80" height="102" rx="22" fill="#3f8fb5" />',
            ]
        )
        if "earphones" in spec.props:
            base_shapes.append(f'<path d="M626 282 C668 246, 700 252, 726 290" fill="none" stroke="{accent_dark}" stroke-width="10" stroke-linecap="round" />')
        if "pen" in spec.props:
            base_shapes.append('<rect x="412" y="282" width="15" height="94" rx="7" fill="#ff8c42" transform="rotate(18 412 282)" />')

    if spec.setting == "bus-stop":
        base_shapes.extend(
            [
                '<rect x="86" y="116" width="180" height="22" rx="8" fill="#4b5563" />',
                '<rect x="112" y="138" width="22" height="188" rx="11" fill="#4b5563" />',
                '<rect x="150" y="346" width="620" height="34" rx="16" fill="#c6d1d8" />',
                '<rect x="610" y="172" width="180" height="94" rx="18" fill="#eef5f9" stroke="#bfd0da" stroke-width="3" />',
                '<circle cx="305" cy="240" r="38" fill="#ffd9b3" />',
                '<rect x="272" y="277" width="66" height="112" rx="22" fill="#3f8fb5" />',
                '<circle cx="468" cy="245" r="34" fill="#ffd9b3" />',
                '<rect x="440" y="278" width="56" height="104" rx="20" fill="#ec7c4e" />',
                '<circle cx="568" cy="250" r="34" fill="#ffd9b3" />',
                '<rect x="540" y="283" width="56" height="98" rx="20" fill="#6f9c60" />',
            ]
        )
        if "phone" in spec.props:
            base_shapes.append('<rect x="284" y="304" width="28" height="50" rx="8" fill="#111827" />')

    if spec.setting == "restaurant":
        base_shapes.extend(
            [
                '<rect x="238" y="305" width="484" height="86" rx="26" fill="#d5b28c" />',
                '<circle cx="350" cy="220" r="40" fill="#ffd9b3" />',
                '<rect x="316" y="257" width="68" height="108" rx="24" fill="#d47055" />',
                '<circle cx="610" cy="220" r="40" fill="#ffd9b3" />',
                '<rect x="576" y="257" width="68" height="108" rx="24" fill="#3f8fb5" />',
                '<ellipse cx="478" cy="342" rx="82" ry="42" fill="#fff5e9" stroke="#d8c497" stroke-width="3" />',
                '<circle cx="452" cy="332" r="18" fill="#f3e1c9" />',
                '<circle cx="490" cy="348" r="18" fill="#f3e1c9" />',
                '<circle cx="524" cy="332" r="18" fill="#f3e1c9" />',
                '<rect x="420" y="254" width="58" height="84" rx="12" fill="#eff5f9" stroke="#bfd0da" stroke-width="3" transform="rotate(-6 420 254)" />',
                '<rect x="518" y="252" width="58" height="84" rx="12" fill="#eff5f9" stroke="#bfd0da" stroke-width="3" transform="rotate(6 518 252)" />',
            ]
        )

    if spec.setting == "rain-window":
        base_shapes.extend(
            [
                '<rect x="124" y="108" width="320" height="244" rx="18" fill="#eef5fb" stroke="#bfd0da" stroke-width="4" />',
                '<path d="M230 122 V340 M336 122 V340 M132 232 H436" stroke="#bfd0da" stroke-width="4" />',
                '<path d="M184 150 C210 184, 224 214, 224 246" fill="none" stroke="#89a4b8" stroke-width="5" stroke-linecap="round" />',
                '<path d="M292 150 C318 184, 332 214, 332 246" fill="none" stroke="#89a4b8" stroke-width="5" stroke-linecap="round" />',
                '<circle cx="616" cy="224" r="42" fill="#ffd9b3" />',
                '<rect x="580" y="264" width="72" height="116" rx="24" fill="#7c74c7" />',
                '<path d="M670 198 C742 120, 816 150, 834 226 L670 226 Z" fill="#6a9fb5" />',
                '<rect x="742" y="192" width="10" height="150" rx="5" fill="#4b5563" />',
            ]
        )

    accent_objects = []
    if "phone" in spec.props and spec.setting != "bus-stop":
        accent_objects.append('<rect x="542" y="250" width="74" height="126" rx="16" fill="#111827" />')
    if "book" in spec.props:
        accent_objects.append(f'<rect x="220" y="250" width="210" height="136" rx="20" fill="{accent_soft}" stroke="{accent_dark}" stroke-width="3" />')
    if "menu" in spec.props:
        accent_objects.append('<rect x="410" y="252" width="44" height="72" rx="10" fill="#ffffff" stroke="#bfd0da" stroke-width="3" />')
    if "tea" in spec.props:
        accent_objects.append('<ellipse cx="560" cy="356" rx="34" ry="20" fill="#f6efe7" stroke="#d9c8b1" stroke-width="3" />')
    if "umbrella" in spec.props and spec.setting != "rain-window":
        accent_objects.append(f'<path d="M684 190 C748 132, 818 162, 838 224 L684 224 Z" fill="{accent_dark}" opacity=".8" />')

    caption = html.escape(seed.scene_spec.setting.replace("-", " · "))
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540" role="img" aria-labelledby="title desc">',
            f"<title>{html.escape(seed.focus)} 그림 묘사 장면</title>",
            f"<desc>{html.escape(seed.scene)}</desc>",
            *base_shapes,
            *accent_objects,
            f'<text x="74" y="94" font-family="Noto Sans KR, sans-serif" font-size="26" font-weight="700" fill="{accent_dark}">{caption}</text>',
            "</svg>",
        ]
    )


def render_manifest(lessons: tuple[LessonPage, ...]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    max_number = lessons[-1].number if lessons else 0
    for page in lessons:
        records.append(manifest_record(page, has_next=page.number < max_number))
    return records


def render_index_html(manifest: list[dict[str, object]]) -> str:
    payload = json.dumps(manifest, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>오늘의 HSKK 30분</title>
  <style>
{mobile_style()}
  </style>
</head>
<body>
  <header>
    <span class="eyebrow">HSKK Daily</span>
    <h1>오늘의 HSKK 30분</h1>
    <p class="sub">완료한 레슨은 자동으로 건너뛰고, 다음 미완료 레슨으로 이동합니다.</p>
  </header>
  <main>
    <section>
      <h2>진행 방식</h2>
      <div class="summary-grid">
        <div class="summary-card">
          <strong>1. 입장</strong>
          페이지가 완료 상태를 확인해서 바로 학습할 레슨으로 이동합니다.
        </div>
        <div class="summary-card">
          <strong>2. 완료 버튼</strong>
          레슨을 끝내면 완료를 저장하고, 이미 준비된 다음 레슨으로 바로 넘어갑니다.
        </div>
        <div class="summary-card">
          <strong>3. 마지막 레슨</strong>
          아직 다음 레슨이 없으면 완료만 저장하고 다음 자동화 실행을 기다립니다.
        </div>
      </div>
      <div class="status-box" id="entry-status">레슨 위치를 확인하는 중입니다.</div>
    </section>
  </main>
  <script>
    const manifest = {payload};
    const COMPLETED_KEY = {json.dumps(COMPLETED_KEY)};
    const LAST_VIEWED_KEY = {json.dumps(LAST_VIEWED_KEY)};

    function readCompleted() {{
      try {{
        const parsed = JSON.parse(localStorage.getItem(COMPLETED_KEY) || "[]");
        return Array.isArray(parsed) ? parsed : [];
      }} catch (error) {{
        return [];
      }}
    }}

    function chooseLesson() {{
      if (!manifest.length) return null;
      const completed = new Set(readCompleted());
      const lastViewed = Number(localStorage.getItem(LAST_VIEWED_KEY) || "");
      const firstIncomplete = manifest.find((item) => !completed.has(item.number));
      if (Number.isFinite(lastViewed)) {{
        const lastViewedItem = manifest.find((item) => item.number === lastViewed);
        if (lastViewedItem && !completed.has(lastViewed)) {{
          return lastViewedItem;
        }}
      }}
      return firstIncomplete || manifest[manifest.length - 1];
    }}

    const target = chooseLesson();
    const status = document.getElementById("entry-status");
    if (!target) {{
      status.textContent = "아직 생성된 레슨이 없습니다.";
    }} else {{
      status.textContent = `${{target.title}} 페이지로 이동합니다.`;
      window.location.replace(`./lessons/${{target.slug}}.html`);
    }}
  </script>
</body>
</html>
"""


def render_lesson_html(page: LessonPage, manifest_entry: dict[str, object]) -> str:
    number = page.number
    visual_path = manifest_entry["visual_path"]
    next_path = manifest_entry["next_path"]
    prev_path = manifest_entry["prev_path"]
    score_inputs = "\n".join(
        f'<div><label for="score-{idx}">{html.escape(area)}</label><input id="score-{idx}" placeholder="0-5 점 또는 짧은 메모"></div>'
        for idx, area in enumerate(page.score_rows, 1)
    )
    flow_html = "\n".join(
        f'<div class="flow-step"><span class="time">{html.escape(time)}</span><div>{html.escape(activity)}</div></div>'
        for time, activity in page.flow
    )
    nav_html = []
    if prev_path:
        nav_html.append(f'<a class="button-link button-secondary" href="{html.escape(prev_path)}">이전 레슨 보기</a>')
    else:
        nav_html.append('<span class="button-link button-secondary" aria-disabled="true">첫 레슨입니다</span>')
    nav_html.append('<a class="button-link button-secondary" href="../index.html">입구로 돌아가기</a>')
    completion_label = "완료하고 다음 레슨 보기" if next_path else "완료 저장"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page.title)}</title>
  <style>
{mobile_style()}
  </style>
</head>
<body>
  <header>
    <span class="eyebrow">Lesson {number:02d}</span>
    <h1>{html.escape(page.title)}</h1>
    <p class="sub">{html.escape(page.goal)}</p>
  </header>
  <main>
    <section>
      <h2>학습 흐름</h2>
      <div class="flow">{flow_html}</div>
    </section>

    <section>
      <h2>Part 1 · 듣고 반복</h2>
      {html_items(page.repeat, "repeat")}
    </section>

    <section>
      <h2>Part 2 · 그림 묘사</h2>
      <div class="visual-card" id="visual-card">
        <img src="{html.escape(str(visual_path))}" alt="Lesson {number:02d} 그림 묘사 장면" onerror="hideVisualCard()">
        <div class="visual-caption">
          <p class="small">장면을 먼저 보고, 아래 문장 구조로 말해 보세요.</p>
        </div>
      </div>
      <p class="scene-text">{html.escape(page.scene)}</p>
      <div class="helper-card">
        <h2>관찰 순서</h2>
        <ol>
          <li>장소를 한 문장으로 말합니다.</li>
          <li>사람과 행동을 이어서 설명합니다.</li>
          <li>눈에 띄는 사물이나 세부사항을 덧붙입니다.</li>
          <li>가능한 이유, 분위기, 추측을 마지막에 붙입니다.</li>
        </ol>
      </div>
      {html_items(page.picture, "picture")}
    </section>

    <section>
      <h2>Part 3 · 질문 답변</h2>
      {html_items(page.questions, "question")}
    </section>

    <section>
      <h2>자기채점 메모</h2>
      <div class="score">
        <div class="score-grid">
          {score_inputs}
        </div>
        <label for="notes">음성 transcript / 메모</label>
        <textarea id="notes" placeholder="여기에 말한 내용이나 약점 메모를 적어 두세요."></textarea>
        <button type="button" onclick="copyNotes()">메모 복사</button>
        <button type="button" id="complete-button" onclick="completeLesson()">{completion_label}</button>
        <div class="status-box" id="lesson-status">{html.escape(page.notes)}</div>
      </div>
      <div class="nav-row">
        {"".join(nav_html)}
      </div>
    </section>
  </main>
  <script>
    const CURRENT_LESSON = {number};
    const NEXT_PATH = {json.dumps(next_path)};
    const COMPLETED_KEY = {json.dumps(COMPLETED_KEY)};
    const LAST_VIEWED_KEY = {json.dumps(LAST_VIEWED_KEY)};

    localStorage.setItem(LAST_VIEWED_KEY, String(CURRENT_LESSON));

    function readCompleted() {{
      try {{
        const parsed = JSON.parse(localStorage.getItem(COMPLETED_KEY) || "[]");
        return Array.isArray(parsed) ? parsed : [];
      }} catch (error) {{
        return [];
      }}
    }}

    function writeCompleted(values) {{
      localStorage.setItem(COMPLETED_KEY, JSON.stringify(values));
    }}

    function copyNotes() {{
      const scoreSummary = Array.from(document.querySelectorAll('[id^="score-"]'))
        .map((input) => `${{input.previousElementSibling.textContent}}: ${{input.value}}`)
        .join("\\n");
      const text = `HSKK 학습 메모\\n레슨: {page.title}\\n${{scoreSummary}}\\n메모:\\n${{document.getElementById('notes').value}}`;
      navigator.clipboard.writeText(text).then(() => {{
        document.getElementById('lesson-status').textContent = '메모를 복사했습니다. 필요하면 Codex에 붙여 넣어 피드백을 받을 수 있습니다.';
      }}).catch(() => {{
        document.getElementById('lesson-status').textContent = '브라우저 복사가 막혀 있습니다. 메모를 직접 선택해 복사해 주세요.';
      }});
    }}

    function completeLesson() {{
      const completed = new Set(readCompleted());
      completed.add(CURRENT_LESSON);
      writeCompleted(Array.from(completed).sort((a, b) => a - b));
      const status = document.getElementById('lesson-status');
      if (NEXT_PATH) {{
        status.textContent = '완료를 저장했습니다. 다음 레슨으로 이동합니다.';
        localStorage.setItem(LAST_VIEWED_KEY, String(CURRENT_LESSON + 1));
        window.location.href = NEXT_PATH;
        return;
      }}
      status.textContent = '완료를 저장했습니다. 다음 레슨은 다음 자동화 실행 후 열립니다.';
    }}

    function hideVisualCard() {{
      const visual = document.getElementById('visual-card');
      if (visual) {{
        visual.style.display = 'none';
      }}
    }}
  </script>
</body>
</html>
"""


def build_mobile_pages() -> dict[str, object]:
    lessons = tuple(parse_lesson_page(path) for path in sorted(LESSON_DIR.glob("lesson_*.md"), key=lesson_number))
    MOBILE_LESSON_DIR.mkdir(parents=True, exist_ok=True)
    MOBILE_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest = render_manifest(lessons)

    for page in lessons:
        seed = seed_for(page.number)
        lesson_svg_file(page.number).write_text(render_lesson_svg(page.number, seed), encoding="utf-8")
        lesson_page_file(page.number).write_text(render_lesson_html(page, manifest[page.number - 1]), encoding="utf-8")

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MOBILE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    MOBILE_INDEX.write_text(render_index_html(manifest), encoding="utf-8")

    return {
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "lesson_pages": [str(lesson_page_file(page.number).relative_to(ROOT)) for page in lessons],
        "assets": [str(lesson_svg_file(page.number).relative_to(ROOT)) for page in lessons],
    }


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
        lesson_path = lesson_file(number)
        action = "create"

    seed = seed_for(number)

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
        update_review_plan(number, today_date)
        update_progress(number, today_text)

    mobile_outputs = build_mobile_pages()

    if action == "create":
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
        "mobile": mobile_outputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(dry_run=args.dry_run), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

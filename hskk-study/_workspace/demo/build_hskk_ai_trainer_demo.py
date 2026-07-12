from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from moviepy.editor import VideoClip
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_workspace" / "demo" / "hskk_ai_trainer_demo_captioned.mp4"
WIDTH, HEIGHT = 1080, 1920
FPS = 15
DURATION = 86

BG = "#f5f8f8"
INK = "#172026"
MUTED = "#61717c"
LINE = "#d8e1e6"
CARD = "#ffffff"
ACCENT = "#0f766e"
ACCENT_SOFT = "#ddf3ef"
DANGER_SOFT = "#fee4e2"
DANGER = "#b42318"
AMBER_SOFT = "#fff4df"
AMBER = "#8a5a0a"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/NotoSansKR-Bold.otf" if bold else "C:/Windows/Fonts/NotoSansKR-Regular.otf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def cjk_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsunb.ttf" if bold else "C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/mingliub.ttc"),
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F = {
    "title": font(58, True),
    "h1": font(38, True),
    "h2": font(30, True),
    "body": font(25),
    "small": font(21),
    "tiny": font(17),
    "caption": font(35, True),
    "cjk_h2": cjk_font(30, True),
    "cjk_small": cjk_font(21),
}


def xywh(box):
    x1, y1, x2, y2 = box
    return [x1, y1, x2, y2]


def rounded(draw: ImageDraw.ImageDraw, box, radius=22, fill=CARD, outline=None, width=2):
    draw.rounded_rectangle(xywh(box), radius=radius, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, pos, value, fill=INK, f=None, anchor=None):
    draw.text(pos, value, fill=fill, font=f or F["body"], anchor=anchor)


def wrap(draw: ImageDraw.ImageDraw, value: str, max_width: int, f) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=f) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(draw, x, y, value, max_width, f=None, fill=INK, gap=8):
    f = f or F["body"]
    for line in wrap(draw, value, max_width, f):
        text(draw, (x, y), line, fill=fill, f=f)
        y += f.size + gap
    return y


def base(t: float, caption: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#fbfdfd")

    # Subtle page header.
    text(draw, (64, 70), "HSKK AI Speaking Trainer Demo", fill=ACCENT, f=F["small"])
    progress_w = int((WIDTH - 128) * min(t / DURATION, 1))
    draw.rounded_rectangle((64, 120, WIDTH - 64, 132), radius=6, fill="#e5ecef")
    draw.rounded_rectangle((64, 120, 64 + progress_w, 132), radius=6, fill=ACCENT)

    # Caption band.
    rounded(draw, (54, 1660, WIDTH - 54, 1818), radius=32, fill="#102526")
    lines = wrap(draw, caption, WIDTH - 160, F["caption"])
    cy = 1692 if len(lines) == 1 else 1676
    for line in lines[:2]:
        text(draw, (WIDTH // 2, cy), line, fill="#ffffff", f=F["caption"], anchor="ma")
        cy += 44
    return img, draw


def phone(draw, x=210, y=190, w=660, h=1380):
    rounded(draw, (x, y, x + w, y + h), radius=72, fill="#111827")
    rounded(draw, (x + 22, y + 44, x + w - 22, y + h - 34), radius=48, fill="#f5f8f8")
    draw.rounded_rectangle((x + 265, y + 20, x + 395, y + 36), radius=8, fill="#374151")
    return (x + 42, y + 72, x + w - 42, y + h - 62)


def app_header(draw, box, title, eyebrow="HSKK AI Trainer"):
    x1, y1, x2, _ = box
    rounded(draw, (x1, y1, x2, y1 + 132), radius=0, fill="#ffffff", outline=LINE)
    rounded(draw, (x1 + 24, y1 + 24, x1 + 160, y1 + 56), radius=16, fill=ACCENT_SOFT)
    text(draw, (x1 + 42, y1 + 31), eyebrow, fill=ACCENT, f=F["tiny"])
    paragraph(draw, x1 + 24, y1 + 70, title, x2 - x1 - 48, F["h2"], INK, 4)


def lesson_screen(draw, box, scroll=0, memo=False):
    x1, y1, x2, y2 = box
    app_header(draw, box, "오늘의 HSKK 30분")
    y = y1 + 158 - scroll
    sections = [
        ("Part 1 · 따라 말하기", "我每天复习很重要。", "Wǒ měi tiān fùxí hěn zhòngyào.", "매일 복습이 중요합니다."),
        ("Part 2 · 그림 묘사", "一个人在手机上学习汉语。", "Yí gè rén zài shǒujī shàng xuéxí Hànyǔ.", "휴대폰으로 중국어를 공부하는 장면"),
        ("Part 3 · 질문 답변", "你怎么复习汉语？", "Nǐ zěnme fùxí Hànyǔ?", "중국어를 어떻게 복습하나요?"),
    ]
    for label, hanzi, pinyin, ko in sections:
        rounded(draw, (x1 + 24, y, x2 - 24, y + 186), fill=CARD, outline=LINE)
        text(draw, (x1 + 46, y + 20), label, fill=ACCENT, f=F["small"])
        text(draw, (x1 + 46, y + 62), hanzi, fill=INK, f=F["cjk_h2"])
        text(draw, (x1 + 46, y + 108), pinyin, fill=ACCENT, f=F["cjk_small"])
        text(draw, (x1 + 46, y + 148), ko, fill=MUTED, f=F["small"])
        y += 210

    rounded(draw, (x1 + 24, y + 8, x2 - 24, y + 268), fill="#ffffff", outline=LINE)
    text(draw, (x1 + 46, y + 34), "자기채점 메모", fill=INK, f=F["h2"])
    rounded(draw, (x1 + 46, y + 86, x2 - 46, y + 208), radius=18, fill="#fbfdfd", outline=LINE)
    if memo:
        paragraph(draw, x1 + 66, y + 108, "성조가 흔들림. 다음에는 이유를 한 문장 더 붙이기.", x2 - x1 - 132, F["small"], INK, 6)
    else:
        text(draw, (x1 + 66, y + 126), "오늘 말한 내용과 약점을 짧게 남깁니다.", fill="#9aa8af", f=F["small"])
    rounded(draw, (x1 + 46, y + 226, x2 - 46, y + 286), radius=18, fill=ACCENT)
    text(draw, ((x1 + x2) // 2, y + 241), "녹음하고 AI 평가 받기", fill="#ffffff", f=F["small"], anchor="ma")


def trainer_prompt(draw, box, recording=False, playback=False):
    x1, y1, x2, y2 = box
    app_header(draw, box, "레슨 내용을 보면서 바로 말하기")
    y = y1 + 158
    rounded(draw, (x1 + 24, y, x2 - 24, y + 300), fill=CARD, outline=LINE)
    text(draw, (x1 + 46, y + 24), "오늘 말할 내용", fill=INK, f=F["h2"])
    text(draw, (x1 + 46, y + 78), "你怎么复习汉语？", fill=INK, f=F["cjk_h2"])
    text(draw, (x1 + 46, y + 126), "Nǐ zěnme fùxí Hànyǔ?", fill=ACCENT, f=F["cjk_small"])
    paragraph(draw, x1 + 46, y + 170, "레슨 질문을 보고 자연스럽게 답변합니다.", x2 - x1 - 92, F["small"], MUTED, 6)

    y += 330
    rounded(draw, (x1 + 24, y, x2 - 24, y + 292), fill="#ffffff", outline=LINE)
    text(draw, (x1 + 46, y + 24), "녹음", fill=INK, f=F["h2"])
    cx, cy = x1 + 122, y + 150
    draw.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=ACCENT if not recording else DANGER)
    text(draw, (cx, cy - 16), "말하기", fill="#ffffff", f=F["small"], anchor="ma")
    title = "말하는 중입니다" if recording else "문제를 보고 말해 보세요"
    meta = "녹음 후 내 목소리를 재생합니다" if not playback else "내 녹음을 먼저 들어봅니다"
    text(draw, (x1 + 220, y + 104), title, fill=INK, f=F["small"])
    text(draw, (x1 + 220, y + 146), meta, fill=MUTED, f=F["small"])
    if playback:
        rounded(draw, (x1 + 46, y + 218, x2 - 46, y + 270), radius=16, fill="#eef3f4")
        draw.rectangle((x1 + 88, y + 240, x2 - 122, y + 246), fill="#c4cfd5")
        draw.ellipse((x1 + 214, y + 234, x1 + 226, y + 246), fill=ACCENT)
        text(draw, (x1 + 248, y + 228), "내 녹음 들어보기", fill=INK, f=F["tiny"])


def feedback_screen(draw, box, compare=False):
    x1, y1, x2, y2 = box
    app_header(draw, box, "AI 코칭 리포트")
    y = y1 + 158
    rounded(draw, (x1 + 24, y, x2 - 24, y + 154), fill=ACCENT_SOFT, outline=None)
    text(draw, (x1 + 48, y + 28), "예상 점수", fill=ACCENT, f=F["small"])
    text(draw, (x1 + 48, y + 68), "82", fill=ACCENT, f=F["title"])
    text(draw, (x1 + 144, y + 92), "연습용 AI 피드백", fill="#2c5f59", f=F["small"])

    y += 184
    labels = [("Task", "4"), ("Fluency", "3"), ("Grammar", "4"), ("Pron.", "3")]
    for i, (name, score) in enumerate(labels):
        bx = x1 + 24 + (i % 2) * 286
        by = y + (i // 2) * 88
        rounded(draw, (bx, by, bx + 262, by + 68), radius=18, fill="#f1f6f6")
        text(draw, (bx + 22, by + 18), name, fill=INK, f=F["small"])
        text(draw, (bx + 202, by + 18), score, fill=ACCENT, f=F["small"])

    y += 200
    rounded(draw, (x1 + 24, y, x2 - 24, y + 168), fill="#ffffff", outline=LINE)
    text(draw, (x1 + 46, y + 24), "개선 포인트", fill=INK, f=F["h2"])
    paragraph(draw, x1 + 46, y + 72, "이유를 한 문장 더 붙이면 답변이 더 자연스럽습니다.", x2 - x1 - 92, F["small"], MUTED, 6)

    y += 194
    rounded(draw, (x1 + 24, y, x2 - 24, y + 170), fill="#ffffff", outline=LINE)
    text(draw, (x1 + 46, y + 24), "교정 답변", fill=INK, f=F["h2"])
    paragraph(draw, x1 + 46, y + 72, "我每天晚上复习汉语，因为安静的时候更容易集中。", x2 - x1 - 92, F["cjk_small"], INK, 6)

    if compare:
        y += 196
        for title in ["원어민 발음 듣기", "교정 답변 발음 듣기"]:
            rounded(draw, (x1 + 24, y, x2 - 24, y + 102), fill="#fbfdfd", outline=LINE)
            text(draw, (x1 + 46, y + 24), title, fill=INK, f=F["small"])
            draw.rectangle((x1 + 46, y + 70, x2 - 104, y + 76), fill="#c4cfd5")
            draw.ellipse((x1 + 170, y + 64, x1 + 184, y + 78), fill=ACCENT)
            y += 122


def expected_test_screen(draw, box):
    x1, y1, x2, y2 = box
    app_header(draw, box, "HSKK 예상문제 Test")
    y = y1 + 158
    rounded(draw, (x1 + 24, y, x2 - 24, y + 344), fill=CARD, outline=LINE)
    text(draw, (x1 + 46, y + 26), "Lesson 40 · 질문 1", fill=ACCENT, f=F["small"])
    text(draw, (x1 + 46, y + 84), "你怎么复习汉语？", fill=INK, f=F["cjk_h2"])
    text(draw, (x1 + 46, y + 136), "Nǐ zěnme fùxí Hànyǔ?", fill=ACCENT, f=F["cjk_small"])
    paragraph(draw, x1 + 46, y + 190, "레슨에서 배운 주제로 예상문제가 자동 표시됩니다.", x2 - x1 - 92, F["small"], MUTED, 6)
    rounded(draw, (x1 + 46, y + 270, x2 - 46, y + 318), radius=16, fill=ACCENT_SOFT)
    text(draw, ((x1 + x2) // 2, y + 282), "레슨 기반 예상문제", fill=ACCENT, f=F["small"], anchor="ma")

    y += 388
    rounded(draw, (x1 + 24, y, x2 - 24, y + 230), fill="#ffffff", outline=LINE)
    text(draw, (x1 + 46, y + 28), "흐름", fill=INK, f=F["h2"])
    for i, line in enumerate(["레슨 문장 확인", "녹음", "AI 평가", "다음 복습 추천"]):
        by = y + 78 + i * 34
        draw.ellipse((x1 + 50, by + 8, x1 + 66, by + 24), fill=ACCENT)
        text(draw, (x1 + 82, by), line, fill=MUTED, f=F["small"])


def home_screen(draw, box):
    x1, y1, x2, y2 = box
    rounded(draw, (x1, y1, x2, y2), radius=0, fill="#e9f1f3")
    text(draw, (x1 + 34, y1 + 44), "9:41", fill=INK, f=F["small"])
    icons = [
        ("오늘의\nHSKK 30분", ACCENT),
        ("AI\nTrainer", "#345c72"),
        ("복습\nQueue", "#7b5e2e"),
        ("JSON\nExport", "#6b7280"),
    ]
    for i, (label, color) in enumerate(icons):
        ix = x1 + 72 + (i % 2) * 240
        iy = y1 + 210 + (i // 2) * 210
        rounded(draw, (ix, iy, ix + 116, iy + 116), radius=28, fill=color)
        text(draw, (ix + 58, iy + 138), label, fill=INK, f=F["tiny"], anchor="ma")
    rounded(draw, (x1 + 72, y2 - 210, x2 - 72, y2 - 116), radius=28, fill="#ffffff")
    text(draw, ((x1 + x2) // 2, y2 - 180), "GitHub Pages 바로가기", fill=MUTED, f=F["small"], anchor="ma")


def closing_screen(draw, box):
    x1, y1, x2, y2 = box
    rounded(draw, (x1 + 24, y1 + 200, x2 - 24, y2 - 220), fill="#ffffff", outline=LINE)
    text(draw, ((x1 + x2) // 2, y1 + 286), "AI가 준비하고", fill=ACCENT, f=F["h1"], anchor="ma")
    text(draw, ((x1 + x2) // 2, y1 + 348), "나는 말하기에 집중합니다", fill=INK, f=F["h1"], anchor="ma")
    steps = ["Daily Lesson", "Record", "AI Feedback", "Pronunciation", "Review Loop"]
    y = y1 + 470
    for step in steps:
        rounded(draw, (x1 + 86, y, x2 - 86, y + 72), radius=20, fill=ACCENT_SOFT)
        text(draw, ((x1 + x2) // 2, y + 18), step, fill=ACCENT, f=F["small"], anchor="ma")
        y += 104


SCENES = [
    (0, 5, "스마트폰에서 바로 시작하는 HSKK AI 말하기 루틴", "title"),
    (5, 12, "홈 화면 바로가기로 오늘 레슨에 진입합니다", "home"),
    (12, 22, "오늘 레슨의 한자, 병음, 뜻, 질문을 먼저 확인합니다", "lesson"),
    (22, 31, "자체 피드백 메모로 학습 포인트를 남깁니다", "memo"),
    (31, 41, "레슨 내용을 보면서 바로 녹음합니다", "record"),
    (41, 48, "내 녹음을 먼저 들어보고 다시 말할지 결정합니다", "playback"),
    (48, 58, "STT와 AI 평가로 연습용 코칭 리포트를 받습니다", "feedback"),
    (58, 69, "내 답변과 모범 발음을 나란히 비교합니다", "compare"),
    (69, 80, "예상문제 Test도 현재 레슨 주제로 자동 연결됩니다", "expected"),
    (80, 86, "AI가 준비하고, 나는 말하기에 집중합니다", "closing"),
]


def scene_for(t: float):
    for start, end, caption, kind in SCENES:
        if start <= t < end:
            return start, end, caption, kind
    return SCENES[-1]


def draw_title(draw):
    text(draw, (WIDTH // 2, 530), "HSKK AI Speaking Trainer", fill=ACCENT, f=F["h1"], anchor="ma")
    text(draw, (WIDTH // 2, 610), "시연영상", fill=INK, f=F["title"], anchor="ma")
    paragraph(draw, 160, 720, "레슨 확인부터 자체 피드백, 녹음, AI 코칭, 발음 비교까지 한 흐름으로 보여줍니다.", WIDTH - 320, F["h2"], MUTED, 10)
    rounded(draw, (230, 980, 850, 1100), radius=34, fill=ACCENT)
    text(draw, (WIDTH // 2, 1018), "1분 30초 이내 · 자막 포함", fill="#ffffff", f=F["h2"], anchor="ma")


def make_frame(t: float):
    start, end, caption, kind = scene_for(t)
    img, draw = base(t, caption)
    screen = phone(draw)
    local = (t - start) / max(end - start, 0.01)

    if kind == "title":
        draw_title(draw)
    elif kind == "home":
        home_screen(draw, screen)
        if local > 0.45:
            x1, y1, _, _ = screen
            draw.ellipse((x1 + 98, y1 + 244, x1 + 166, y1 + 312), fill="#ffffff", outline=ACCENT, width=5)
    elif kind == "lesson":
        lesson_screen(draw, screen, scroll=int(220 * local), memo=False)
    elif kind == "memo":
        lesson_screen(draw, screen, scroll=360, memo=local > 0.28)
    elif kind == "record":
        trainer_prompt(draw, screen, recording=local > 0.28, playback=False)
    elif kind == "playback":
        trainer_prompt(draw, screen, recording=False, playback=True)
    elif kind == "feedback":
        feedback_screen(draw, screen, compare=False)
        if local < 0.25:
            x1, y1, x2, y2 = screen
            rounded(draw, (x1 + 70, y1 + 760, x2 - 70, y1 + 860), radius=26, fill=ACCENT)
            text(draw, ((x1 + x2) // 2, y1 + 790), "STT + 평가 실행 중", fill="#ffffff", f=F["small"], anchor="ma")
    elif kind == "compare":
        feedback_screen(draw, screen, compare=True)
    elif kind == "expected":
        expected_test_screen(draw, screen)
    elif kind == "closing":
        closing_screen(draw, screen)

    # Gentle focus pulse on active screen.
    pulse = int(4 + 3 * math.sin(t * math.pi * 2))
    if kind not in {"title", "closing"}:
        x1, y1, x2, y2 = screen
        draw.rounded_rectangle((x1 - 4, y1 - 4, x2 + 4, y2 + 4), radius=52, outline=ACCENT, width=max(2, pulse))
    return np.asarray(img)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    clip = VideoClip(make_frame, duration=DURATION)
    clip.write_videofile(
        str(OUT),
        fps=FPS,
        codec="libx264",
        audio=False,
        bitrate="2800k",
        preset="medium",
        threads=4,
        logger="bar",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

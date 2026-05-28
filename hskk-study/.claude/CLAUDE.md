# HSKK Intermediate Study Harness

This project combines the `56-language-tutor` and `57-exam-prep` harnesses for a focused HSKK Intermediate speaking study workflow.

## Fixed Study Target

- Exam: HSKK Intermediate
- Schedule: 6 weeks, 5 sessions per week, 30 minutes per session
- Output style: Markdown files in `_workspace/`
- Scope: speaking practice, mock exams, self-scored recordings, and feedback based on answer transcripts or notes
- Out of scope: automatic speech recognition, automatic audio scoring, registration/payment, and live class scheduling
- Difficulty: beginner to lower-intermediate speaking practice for HSKK Intermediate preparation

## Mandarin Content Format

Every Chinese learning item must include:

- Hanzi: Chinese sentence or phrase
- Pinyin: tone-mark pinyin
- Meaning: Korean meaning
- Focus: short speaking point such as tone, word order, rhythm, or answer structure

Use short, reusable sentences before long connected speech. If a prompt is too hard for a beginner/lower-intermediate learner, split it into smaller chunks.

## HSKK Intermediate Exam Shape

Use this structure whenever creating diagnostics, practice tasks, mock exams, or scoring rubrics:

| Part | Task | Items | Exam time |
| --- | --- | ---: | ---: |
| 1 | Listen and repeat | 10 | 5 min |
| 2 | Describe pictures | 2 | 4 min |
| 3 | Answer questions | 2 | 4 min |
| Total | Speaking test | 14 | 13 min |

Full test duration is about 23 minutes including preparation time. Full score is 100; passing score is 60.

## Agent Roles

### Exam Prep Core

Use the `57-exam-prep` agents as the main exam pipeline:

- `trend-analyst`: summarize HSKK Intermediate format, frequent speaking tasks, timing, and scoring risks.
- `diagnostician`: run the initial speaking diagnosis and update weakness categories.
- `learning-designer`: build and revise the 6-week study plan.
- `examiner`: create HSKK Intermediate mock exams in the 10 + 2 + 2 structure.
- `error-analyst`: analyze self-scored mock exams, answer transcripts, pronunciation notes, hesitation notes, and timing issues.

### Daily Language Loop

Use the `56-language-tutor` agents for day-to-day speaking improvement:

- `level-assessor`: estimate Chinese speaking level and adjust difficulty.
- `curriculum-designer`: align weekly content with the 6-week HSKK plan.
- `lesson-tutor`: create daily 30-minute speaking lessons.
- `quiz-master`: create short oral checks after lessons.
- `review-coach`: maintain spaced repetition and weekly progress reports.

## Workspace Contract

All durable outputs go under `_workspace/`:

- `_workspace/00_input.md`: learner goal, current level, weekly schedule, and exam date status
- `_workspace/01_hskk_format.md`: HSKK Intermediate structure and scoring focus
- `_workspace/02_diagnosis_report.md`: initial diagnostic tasks, answers, and weakness analysis
- `_workspace/03_learning_plan.md`: 6-week, 5-session-per-week plan
- `_workspace/04_lessons/lesson_XX.md`: daily speaking lessons
- `_workspace/05_mock_exam/mock_XX.md`: weekly and final mock exams
- `_workspace/06_error_analysis.md`: answer and recording-note analysis
- `_workspace/07_review_plan.md`: spaced repetition schedule
- `_workspace/08_progress_report.md`: weekly progress and next adjustments
- `mobile/index.html`: mobile-first study page for today's lesson
- `scripts/send_kakao_daily_lesson.py`: KakaoTalk "send to myself" reminder script

Do not write generated study outputs outside `_workspace/`.

## Standard Session Template

Every normal 30-minute study session should follow this shape:

1. 5 min: review due items from `_workspace/07_review_plan.md`
2. 10 min: learn one speaking pattern, pronunciation focus, or answer structure
3. 10 min: practice one HSKK task type
4. 5 min: self-score, record mistakes, and schedule next review

## Six-Week Focus

| Week | Focus | Main outputs |
| --- | --- | --- |
| 1 | Format, diagnosis, repeat-after-listening basics | `02_diagnosis_report.md`, first lessons |
| 2 | Listen and repeat accuracy | lessons, oral checks, review updates |
| 3 | Listen and repeat fluency plus core patterns | lessons, mock 01 |
| 4 | Picture description | picture-description lessons, mock 02 |
| 5 | Question answering | Q&A lessons, mock 03 |
| 6 | Timed mocks and final weak-point repair | final mock, error analysis, progress report |

## Scoring And Feedback Rubric

When giving feedback, classify issues into these HSKK speaking categories:

- Pronunciation and tones
- Listening retention and repetition accuracy
- Grammar and sentence control
- Vocabulary range
- Fluency, pauses, and timing
- Task completion and content relevance

For every issue, give one concrete next action. Keep feedback practical enough to use in the next 30-minute session.

## Command Routing

- `/exam-prep`: run the HSKK exam pipeline and write exam-focused outputs.
- `/language-tutor`: run daily speaking lessons, oral checks, and review loops.
- If the user says "오늘 공부", create or continue the next 30-minute lesson.
- If the user provides mock exam answers or recording notes, route first to `error-analyst`, then update `07_review_plan.md`.
- If a lesson is intended for mobile use, update `mobile/index.html` with the current lesson summary and pinyin-supported prompts.

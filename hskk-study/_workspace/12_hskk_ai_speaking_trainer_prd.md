# PRD: HSKK AI Speaking Trainer

Status: draft
Date: 2026-07-11

## 1. Purpose

Build an AI-powered HSKK speaking trainer on the existing GitHub Pages study site.

The platform should let a learner open the mobile page, record Chinese speaking practice, receive AI feedback, export session JSON, and later feed that output into the existing HSKK Harness workflow.

## 2. Goals

### MVP

- Record voice in the browser.
- Transcribe Chinese speech.
- Evaluate speaking answers with an AI rubric.
- Show feedback and corrected answer.
- Save local session history.
- Export a Harness-compatible session JSON file.

### Future

- Multi-turn conversation practice.
- Text-to-speech model answers.
- Realtime voice conversation.
- Automatic Harness import.
- HSKK expected-question test mode and mock exam mode.

## 3. Non-goals

- Do not expose OpenAI API keys in browser code.
- Do not guarantee official HSKK scores.
- Do not use copyrighted commercial question banks.
- Do not add public multi-user account management in MVP.
- Do not replace the existing daily lesson generator in MVP.

## 4. Users

Primary user:
- A personal HSKK learner using mobile or desktop.

MVP access model:
- Personal-use first.
- No login.
- No server-side learner database.
- Local browser history plus JSON export.

## 5. Architecture

```text
GitHub Pages mobile UI
  -> Cloudflare Workers API
  -> OpenAI APIs
       - speech-to-text
       - LLM evaluation
       - future TTS / realtime
  -> Browser local session history
  -> JSON export
  -> Harness import
```

Backend target:
- Cloudflare Workers.

Storage target:
- MVP: localStorage or IndexedDB in the browser.
- Future: Cloudflare KV/D1 only if multi-user or server-side history becomes necessary.

## 6. Functional Requirements

### FR1. Daily Lesson Entry

- Show today's generated HSKK lesson.
- Link from the existing mobile entry page.
- Read existing lesson metadata from `mobile/lessons/manifest.json`.
- Do not break existing generated lesson HTML pages.

### FR2. Voice Recording

- Request microphone permission.
- Start, stop, retry, and playback recording.
- Keep recording local until the learner taps "Evaluate".
- Support mobile browser usage.

### FR3. Chinese STT

- Upload recorded audio to the backend.
- Backend sends audio to OpenAI STT.
- Return Chinese transcript to the browser.
- Show retry state for failed or empty transcription.

### FR4. AI Evaluation

- Send lesson context, prompt type, and transcript to the backend.
- Backend returns structured JSON feedback.
- Evaluate with this rubric:
  - Task completion
  - Fluency
  - Grammar
  - Vocabulary
  - Pronunciation
  - Overall comments

### FR5. Feedback UI

- Show rubric scores.
- Show strengths and weaknesses.
- Show corrected answer.
- Show one or more concrete review recommendations.
- Clearly label all scores as estimated practice feedback, not official HSKK scoring.

### FR6. Session History

- Store sessions locally in the browser.
- Show recent sessions by date, lesson, task type, and score.
- Allow deleting local history.

### FR7. JSON Export

- Export one session as JSON.
- Export all local sessions as a bundle.
- JSON must be readable by a future Harness import script.

### FR8. Harness-Compatible Output

- Include enough information for the Harness to update:
  - `_workspace/06_error_analysis.md`
  - `_workspace/07_review_plan.md`
  - future weak-point lesson generation

## 7. HSKK Expected-Question Test Mode

This is a named product mode and should be visible in the UI as:

> HSKK 예상문제 Test

Purpose:
- Let the learner practice likely HSKK-style questions in a test-like flow without claiming official scoring.

Supported levels:
- Beginner
- Intermediate
- Advanced

Question types:
- Part 1: Repeat
- Part 2: Picture description
- Part 3: Answer questions

MVP behavior:
- Use locally generated or Harness-generated expected questions.
- Avoid copyrighted commercial question banks.
- Show one question at a time.
- Show a visible timer per task.
- Record the learner answer.
- Transcribe the answer.
- Evaluate with the same rubric as daily lessons.
- Return estimated score, strengths, weaknesses, corrected answer, and review recommendations.
- Export test result JSON.

Future behavior:
- Generate adaptive expected-question sets from prior weak points.
- Build a complete timed mock exam session.
- Compare trends across test attempts.

Expected-question JSON shape:

```json
{
  "test_id": "hskk_expected_2026-07-11_001",
  "level": "intermediate",
  "mode": "expected_question_test",
  "items": [
    {
      "item_id": "part3_001",
      "part": "answer_questions",
      "prompt_hanzi": "你每天什么时候学习汉语？",
      "prompt_pinyin": "Ni mei tian shenme shihou xuexi Hanyu?",
      "prompt_ko": "매일 언제 중국어를 공부하나요?",
      "time_limit_sec": 60
    }
  ]
}
```

Test result JSON shape:

```json
{
  "session_id": "session_2026-07-11_001",
  "mode": "expected_question_test",
  "level": "intermediate",
  "started_at": "2026-07-11T10:00:00+09:00",
  "completed_at": "2026-07-11T10:08:00+09:00",
  "items": [
    {
      "item_id": "part3_001",
      "transcript": "我每天晚上学习汉语。",
      "estimated_score": 78,
      "rubric": {
        "task_completion": 4,
        "fluency": 3,
        "grammar": 4,
        "vocabulary": 3,
        "pronunciation": 3
      },
      "strengths": ["Answered directly with a complete sentence."],
      "weaknesses": ["Needs more detail and smoother expansion."],
      "corrected_answer": "我每天晚上学习汉语，因为晚上比较安静。",
      "review_recommendations": ["Practice answer -> reason -> example structure."]
    }
  ]
}
```

## 8. Mock Exam Mode

Mock Exam is a later, fuller version of Expected-Question Test Mode.

Modes:
- Beginner
- Intermediate
- Advanced

Exam sections:
- Repeat
- Picture description
- Answer questions

Outputs:
- Estimated score
- Strengths
- Weaknesses
- Review recommendations
- JSON export

Difference from Expected-Question Test:
- Expected-Question Test can be short and modular.
- Mock Exam should simulate a longer timed exam flow.

## 9. API

MVP endpoints:

- `POST /api/transcribe`
- `POST /api/evaluate`
- `POST /api/session`

Future endpoints:

- `POST /api/chat`
- `POST /api/speech`
- `POST /api/results`

Endpoint notes:
- Browser sends audio only to Cloudflare Workers.
- Cloudflare Workers calls OpenAI.
- Browser never sees API keys.
- API responses should be JSON.

## 10. Data Model

Files and logical schemas:

- `lesson.json`
- `session.json`
- `feedback.json`
- `review_queue.json`
- `expected_question_test.json`
- `mock_exam_result.json`

MVP storage:
- Browser localStorage or IndexedDB.
- Downloadable JSON export.

Future storage:
- Cloudflare KV/D1 if persistent server-side sessions are needed.

## 11. UI

Required screens:

- Home
- Today's Lesson
- AI Speaking Practice
- HSKK 예상문제 Test
- Feedback
- History
- Settings / Export

Future screens:
- AI Conversation
- Mock Exam
- Progress Dashboard
- Teacher Mode

## 12. Folder Structure

Proposed structure:

```text
hskk-study/
  mobile/
    trainer/
      index.html
      app.js
      styles.css
  api/
    worker/
      src/
      wrangler.toml
  _workspace/
    harness/
      schemas/
      imports/
    sessions/
    feedback/
    expected_tests/
```

Do not move existing generated lesson files during MVP.

## 13. Security

- Store OpenAI API key only as a Cloudflare Worker secret.
- Use HTTPS only.
- Never expose secrets to browser JavaScript.
- Add request size limits for audio uploads.
- Add simple rate limits or daily usage caps.
- Treat transcripts as personal learning data.
- MVP avoids server-side retention by default.

## 14. Cost Guardrails

Cost model:
- Browser recording itself is free.
- Cost is incurred when audio is sent to STT and when text is sent for AI evaluation.
- TTS and Realtime add separate future costs.

MVP guardrails:
- Upload only when the learner taps "Evaluate".
- Keep retry/playback local until evaluation.
- Use low-cost STT by default.
- Use a low-cost evaluation model by default.
- Limit feedback JSON size.
- Add optional daily evaluation cap.

Expected personal-use estimate:
- 1-minute recording + one AI evaluation is expected to be low-cost.
- Actual monthly cost depends on recording count, transcript length, feedback length, and chosen models.

## 15. Roadmap

### Phase 1. MVP

- Voice recording.
- Chinese STT.
- AI evaluation.
- Feedback UI.
- Local history.
- JSON export.

### Phase 2. HSKK Expected-Question Test

- Add visible `HSKK 예상문제 Test` entry.
- Add level selection.
- Add Part 1, Part 2, Part 3 expected-question items.
- Add per-item timer.
- Export test result JSON.

### Phase 3. Multi-turn Conversation

- Add follow-up chat based on transcript and feedback.
- Keep request-based voice input.

### Phase 4. TTS

- Add model answer playback.
- Add pronunciation shadowing flow.

### Phase 5. Mock Exam

- Add full timed mock exam flow.
- Add overall estimated score and test report.

### Phase 6. Realtime Voice

- Add low-latency voice conversation if cost and product value justify it.

### Phase 7. Automatic Harness Integration

- Add import script that reads exported JSON and updates Harness workspace files.

## 16. Definition of Done

MVP is done when:

- Voice recording works on mobile.
- Chinese STT succeeds.
- AI feedback displays in UI.
- Session history survives refresh.
- JSON export is valid.
- Exported JSON can be used by a Harness import script design.
- Existing daily lesson pages still work.

Expected-Question Test is done when:

- Learner can select HSKK level.
- Learner can run at least one test set.
- Each item supports recording, STT, evaluation, and feedback.
- Test result JSON exports successfully.

## 17. Test Cases

MVP:

- Record normal speech.
- Record with background noise.
- Deny microphone permission.
- Retry recording.
- Network interruption during upload.
- Empty or too-short audio.
- Export one session JSON.
- Export all sessions JSON.

Expected-Question Test:

- Start Beginner test.
- Start Intermediate test.
- Start Advanced test.
- Complete Part 1 repeat item.
- Complete Part 2 picture description item.
- Complete Part 3 answer question item.
- Timer reaches zero.
- Export test result JSON.
- Verify review recommendation appears in result.

Harness:

- Validate exported JSON schema.
- Confirm weak points can map to review queue items.
- Confirm no existing generated lessons are overwritten.

## 18. Future Enhancements

- Adaptive learning.
- Pronunciation trend.
- Difficulty adjustment.
- Dashboard.
- Progress analytics.
- Teacher mode.
- Multi-user mode.
- Automatic Harness import and commit.


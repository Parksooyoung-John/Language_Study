# HSKK Auto Daily Lesson AX Presentation Source For NotebookLM

## Presentation Goal

This source is for creating a short AX presentation about the HSKK Auto Daily Lesson project.

Audience:
- People who may not know the Harness structure.
- People who need to understand the user value before the technical design.
- People who should see this as a practical AX case, not only a coding demo.

Core message:

> 공부할 결심보다 쉬운 중국어. 매일 30분, 내 손안의 AI 학습 루틴.

The project started from a simple personal need: I wanted to study a language whenever I wanted, without opening a heavy tool or waiting for a class. The answer became a mobile-first HSKK learning routine where AI prepares the lesson, publishes it to GitHub Pages, and lets me open it from my phone like an app.

## Main Slide 1: Hook

Title:

> 공부할 결심보다 쉬운 중국어

Subtitle:

> 매일 30분, 내 손안의 AI 학습 루틴

Visual direction:
- Use the real mobile demo video opening frame.
- Show the iPhone home screen and the `생산성` folder.
- Highlight the shortcut named `오늘의 HSKK 30분`.
- Make the first-viewport signal the phone experience, not the technical architecture.

Key words on slide:
- 원할 때 바로 시작
- 모바일 바로가기
- 매일 30분
- AI 학습 루틴

Speaker notes:

> 이 프로젝트의 출발점은 거창한 플랫폼이 아니라 아주 개인적인 불편이었습니다. 언어학습을 하고 싶은 순간은 있는데, 앱을 찾고 자료를 고르고 진도를 정리하는 과정이 번거로웠습니다. 그래서 목표를 단순하게 잡았습니다. 내가 원할 때 휴대폰에서 바로 열고, 오늘 해야 할 HSKK 학습만 집중해서 끝내는 구조를 만들자.

## Main Slide 2: From Tap To Lesson

Slide message:

> 터치 한 번이 오늘의 학습 콘텐츠로 이어진다.

Visual direction:
- Use a three-step horizontal story.
- Step 1: phone home shortcut `오늘의 HSKK 30분`
- Step 2: GitHub Pages mobile lesson page
- Step 3: HSKK speaking practice and self-score memo

Key words on slide:
- Tap
- GitHub Pages
- Daily Lesson
- Self-score

Speaker notes:

> 실제 시연영상에서는 홈 화면의 바로가기를 누르면 GitHub Pages에 올라간 모바일 학습 페이지가 열립니다. 일반 웹페이지지만 사용자 입장에서는 앱처럼 동작합니다. 화면에는 오늘의 레슨, 중국어 문장, 병음, 한국어 뜻, 질문 답변, 자기채점 메모가 들어 있습니다. 핵심은 학습자가 자료를 찾는 시간이 아니라 말하기 연습에 시간을 쓰게 만드는 것입니다.

## Main Slide 3: What The Harness Does

Slide message:

> 단순 생성이 아니라, 매일 반복되는 학습 운영체계.

Visual direction:
- Put the learner at the center.
- Around the learner, show multiple agents and automation loop.
- End with outputs: lesson markdown, mobile page, review queue, Kakao reminder.

Key words on slide:
- Multi-Agent
- Loop
- Mobile-first
- Review Queue
- Automation

Speaker notes:

> 이 프로젝트의 차이는 한 번 콘텐츠를 생성하는 데 있지 않습니다. Harness는 매일 학습 루틴을 운영합니다. 커리큘럼을 관리하고, 레슨을 만들고, 복습 일정을 쌓고, 모바일 페이지를 다시 만들고, 커밋과 푸시까지 수행합니다. 즉 AI를 단발성 답변 도구가 아니라 반복 가능한 학습 운영체계로 사용한 사례입니다.

## Harness Storytelling Options

Use all three options as appendix candidates. Pick one for the main visual if the deck needs to be simpler.

### Option 1: Learning Factory

Best for explaining the system to non-technical audiences.

Story:
- Input: learner goal, exam format, prior lessons, self-score notes
- Factory: curriculum designer, lesson tutor, error analyst, review coach, automation script
- Output: daily lesson, mobile page, review plan, Kakao reminder

One-line explanation:

> 학습자의 목표와 피드백이 들어오면, Agent들이 역할을 나누어 오늘의 학습 콘텐츠를 생산한다.

Slide visual:
- Left: raw materials
- Center: factory line with agents
- Right: mobile lesson and reminder

### Option 2: Loop Engine

Best for emphasizing the Harness feature: repeated learning improvement.

Story:
- Review due items
- Generate today's lesson
- Practice on mobile
- Self-score and write notes
- Feed notes back to Codex
- Update next lesson and review queue

One-line explanation:

> 매일의 학습은 끝나는 것이 아니라 다음 레슨의 입력으로 돌아간다.

Slide visual:
- Circular loop with five nodes
- Put `Human Feedback` between self-score and next lesson
- Mark current limitation: feedback is manually pasted into Codex today

### Option 3: AI Assistant Team

Best for explaining multi-agent roles.

Story:
- Curriculum Designer: decides the path
- Lesson Tutor: writes daily speaking practice
- Error Analyst: reads transcripts and weak points
- Review Coach: schedules spaced repetition
- Automation Runner: rebuilds mobile page, commits, pushes, sends reminder

One-line explanation:

> 한 명의 AI가 모든 일을 하는 것이 아니라, 역할이 나뉜 AI 팀이 학습 운영을 분담한다.

Slide visual:
- Learner in the center
- Five role cards around the learner
- Each card has one verb: plan, teach, analyze, review, deliver

## Demo Video Appendix

Referenced video:

`C:\Users\swims\OneDrive\문서\카카오톡 받은 파일\시연영상.mp4`

Observed properties:
- Duration: about 37.9 seconds
- Format: vertical mobile screen recording
- Content: iPhone home screen, productivity folder, `오늘의 HSKK 30분` shortcut, GitHub Pages lesson page, HSKK questions, self-score memo fields

Use recommendation:
- Use the current video as-is because it is already under 90 seconds.
- Add four presentation callouts around or before the video:
  1. `홈 화면에서 앱처럼 실행`
  2. `GitHub Pages 기반 모바일 학습`
  3. `HSKK 문제: 한자 + 병음 + 한국어`
  4. `자기채점 메모로 다음 피드백 준비`

Optional 90-second version:
- 0-5s: title card, "오늘의 HSKK 30분"
- 5-15s: phone home screen and shortcut
- 15-35s: lesson page and question practice
- 35-50s: self-score memo fields
- 50-70s: automation output: lesson markdown, mobile page, Git commit
- 70-85s: Kakao reminder concept
- 85-90s: closing message, "AI가 학습을 준비하고, 나는 말하기에 집중한다"

Important note:
- The current Kakao sending step is blocked by an expired or invalid Kakao refresh token.
- Do not claim that Kakao reminder is currently sending successfully until the credential is renewed.

## Appendix: Current Implementation Facts

Current latest generated lesson:
- `hskk-study/_workspace/04_lessons/lesson_38.md`
- Lesson 38 focus: 음식과 식당
- Date: 2026-07-10

Current mobile entry:
- `hskk-study/mobile/index.html`
- GitHub Pages URL shown in project docs: `https://parksooyoung-john.github.io/Language_Study/hskk-study/mobile/`

Automation command:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1
```

Automation flow:
1. Generate or rebuild today's lesson.
2. Rebuild mobile pages.
3. Commit and push changed study files.
4. Send KakaoTalk reminder.

Verified limitation:
- Mobile self-score fields do not automatically sync back to the repository.
- The page copies the memo text so the learner can paste it into Codex.
- Codex then uses that feedback to update error analysis, review plan, and future lessons.

Kakao status:
- Lesson generation and push succeeded on 2026-07-10.
- Kakao send failed with `invalid_grant`, `expired_or_invalid_refresh_token`, `KOE322`.
- This is a credential renewal issue, not a lesson generation issue.

## Answers To Expected Questions

### Q1. GitHub Pages를 모바일 바로가기로 쓰고 있는데, 범용 앱처럼 쓰려면?

Answer:

The current approach already works as a lightweight app-like experience because it is reachable by URL and can be added to the phone home screen. To make it more generally usable, convert it into a Progressive Web App.

Recommended improvements:
- Add a web app manifest with app name, short name, start URL, display mode, theme color, and icons.
- Add a service worker for offline cache and faster loading.
- Add proper app icons for iOS and Android.
- Keep the GitHub Pages URL stable.
- If multiple learners use it, add a backend or form submission flow so each learner has separate progress and feedback.

Short answer for presentation:

> 지금은 개인용 앱처럼 쓰는 GitHub Pages이고, 범용화하려면 PWA와 사용자별 피드백 저장소가 필요합니다.

### Q2. GitHub Pages에 자기채점과 피드백을 입력하면 다음 학습에 자동 반영되나?

Answer:

Not yet. The current mobile page has self-score input fields and a memo area, but the feedback is not automatically sent to Codex or committed into the repository. The current flow is manual:

1. Learner writes self-score and memo on the mobile page.
2. Learner copies the memo.
3. Learner pastes it into Codex.
4. Codex updates error analysis, review plan, and future lesson direction.

Short answer for presentation:

> 현재는 수동 피드백 루프입니다. 자동 반영까지 가려면 모바일 입력값을 서버나 GitHub Issue/Form/Database로 보내는 연결이 추가되어야 합니다.

### Q3. NotebookLM이나 자료작성 Tool과 Codex가 바로 연계 가능한가?

Answer:

The most practical current workflow is file-based handoff:

1. Codex creates a clean Markdown, PDF, or slide source.
2. The user uploads that source to NotebookLM.
3. NotebookLM generates briefing docs, slide drafts, audio/video overviews, or Q&A material from the uploaded sources.

Direct native integration between this project and NotebookLM is not implemented here. Codex supports plugins and connectors in the broader product environment, but this project does not currently include a NotebookLM-specific connector.

Short answer for presentation:

> 지금은 Codex가 자료 소스를 만들고 NotebookLM이 이를 읽어 발표자료로 재구성하는 방식이 가장 안정적입니다.

## Final Presentation Narrative

Opening:

> 언어학습에서 가장 어려운 것은 공부할 마음보다 시작까지의 마찰입니다. 오늘 무엇을 할지 고르고, 자료를 찾고, 기록을 남기는 과정이 반복되면 학습은 금방 끊깁니다.

Problem:

> 저는 중국어 HSKK 말하기를 준비하면서, 언제든 휴대폰에서 바로 열 수 있는 개인 학습 루틴이 필요했습니다.

Solution:

> 그래서 Codex/Harness를 이용해 매일 학습 콘텐츠를 만들고, GitHub Pages에 모바일 화면으로 배포하고, 복습 루프까지 관리하는 구조를 만들었습니다.

Demo setup:

> 지금 보시는 영상은 별도 앱을 설치한 것이 아니라, GitHub Pages를 홈 화면 바로가기로 등록해서 앱처럼 사용하는 장면입니다.

Harness explanation:

> 뒤에서는 여러 Agent가 역할을 나누어 일합니다. 커리큘럼을 설계하고, 오늘의 말하기 레슨을 만들고, 복습 일정을 관리하고, 모바일 페이지를 다시 빌드합니다.

Closing:

> 이 사례의 핵심은 AI가 답을 한 번 주는 것이 아닙니다. 매일 반복되는 개인 학습 운영을 AI와 자동화가 대신 준비하고, 사람은 실제 말하기 연습에 집중하도록 만든 것입니다.


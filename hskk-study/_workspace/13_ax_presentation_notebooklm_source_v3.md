# HSKK Auto Daily Lesson AX Presentation Source For NotebookLM v3

## NotebookLM 요청 프롬프트

아래 원고를 바탕으로 AX 발표용 슬라이드 자료를 다시 만들어 주세요.

출력 조건:
- Main 장표는 3장 이내로 구성해 주세요.
- 목차 슬라이드는 만들지 말고, 스토리텔링 흐름으로 자연스럽게 이어지게 구성해 주세요.
- 전체 톤은 깔끔하고 직관적인 비즈니스 발표자료 스타일로 유지해 주세요.
- 텍스트는 짧게, 이미지는 크게, 핵심 키워드 중심으로 구성해 주세요.
- Harness 구조를 처음 보는 사람도 이해할 수 있도록 멀티에이전트와 Loop 구조를 쉽게 시각화해 주세요.
- 가능하면 슬라이드 크기는 A4 가로형, 297mm x 210mm 기준으로 만들어 주세요.
- NotebookLM이 실제 슬라이드 크기를 정확히 고정하지 못하면, PowerPoint 또는 Google Slides에서 A4 가로로 후처리해도 깨지지 않도록 여백이 넉넉한 레이아웃으로 설계해 주세요.
- 유첨에는 시연영상 구성안, Harness 구조 설명 옵션, 예상 Q&A를 포함해 주세요.

참고:
- 기존 발표자료는 깔끔한 방향성이 좋았으나, 현재 제품 상태가 업데이트되었습니다.
- 이번 버전은 단순한 “매일 레슨 생성”을 넘어, GitHub Pages 모바일 학습 페이지와 AI Speaking Trainer가 연결된 최신 상태를 반영합니다.

## 발표 핵심 메시지

> 공부 결심보다 쉬운 중국어 말하기.  
> 매일 30분, 스마트폰에서 열고 말하고 바로 피드백 받는 AI 학습 루틴.

이 프로젝트의 출발점은 거창한 서비스 개발이 아니라 개인적인 학습 불편이었습니다.

중국어 말하기를 해야 한다는 생각은 있지만, 막상 시작하려면 오늘 무엇을 할지 정하고, 자료를 찾고, 기록을 남기고, 복습 흐름을 만드는 과정이 번거로웠습니다. 그래서 목표를 단순하게 잡았습니다.

> 내가 원할 때, 모바일에서 바로 열고, 오늘 해야 할 HSKK 말하기 연습만 시작하게 만들자.

현재 구조는 Codex와 Harness를 활용해 매일 학습 콘텐츠를 만들고, GitHub Pages에 모바일 페이지로 배포하며, 별도의 AI Speaking Trainer에서 녹음, STT, AI 평가, 원어민 발음 비교, 교정 답변 발음 비교까지 이어지도록 발전했습니다.

## 현재 구현 상태 요약

현재 구현된 것:
- GitHub Pages 기반 모바일 HSKK 학습 페이지
- 홈 화면 바로가기를 통한 앱처럼 쓰는 학습 진입
- 매일 HSKK 레슨 자동 생성 및 모바일 페이지 갱신
- 레슨 페이지 하단의 `녹음하고 AI 평가 받기` CTA
- HSKK AI Speaking Trainer 페이지
- 브라우저 녹음, 내 녹음 재생, 다시 녹음
- Vercel API 기반 OpenAI STT
- AI 평가와 코칭 리포트
- 예상 점수, 강점, 약점, 교정 답변, 다음 연습 추천
- STT transcript 기반 원어민 스타일 발음 듣기
- AI 교정 답변 기반 발음 듣기
- HSKK 예상문제 Test 모드
- 레슨 CTA로 들어온 경우, 해당 레슨 주제와 문장 기반 예상문제 자동 표시
- 기본 예상문제 병음에 성조 표기 추가
- 세션 JSON export와 로컬 History 저장
- Harness import를 염두에 둔 JSON 구조

아직 수동 또는 향후 과제:
- 모바일에서 입력한 자기채점 메모가 자동으로 Codex/Harness에 들어가지는 않습니다.
- 현재는 JSON export 또는 사용자가 Codex에 피드백을 전달하는 방식이 안정적입니다.
- KakaoTalk 알림은 구조는 있으나, 현재 refresh token 갱신이 필요합니다.
- NotebookLM과 Codex의 직접 자동 연동은 현재 프로젝트에 구현되어 있지 않습니다.

## Main Slide 1: Hook

제목:

> 공부 결심보다 쉬운 중국어 말하기

부제:

> 스마트폰에서 열고, 말하고, 바로 피드백 받는 HSKK AI 루틴

시각 구성:
- 첫 화면은 실제 iPhone 홈 화면 또는 GitHub Pages 바로가기 화면을 크게 사용합니다.
- `오늘의 HSKK 30분`, `HSKK AI Trainer`, `녹음하고 AI 평가 받기` 같은 실제 화면 요소를 강조합니다.
- 기술 구조보다 사용자가 느끼는 경험을 먼저 보여줍니다.

핵심 키워드:
- 바로 시작
- 모바일 학습
- 말하기 연습
- AI 피드백
- 원어민 발음 비교

발표 멘트:

> 이 프로젝트는 “중국어 공부를 더 열심히 하자”에서 시작한 것이 아닙니다. 오히려 공부를 시작하기 전의 마찰을 줄이고 싶었습니다. 오늘 무엇을 할지 찾고, 자료를 정리하고, 복습할 내용을 기억하는 과정이 번거로우면 말하기 연습까지 가기 어렵습니다. 그래서 스마트폰 홈 화면에서 바로 열고, 오늘의 HSKK 레슨을 보고, 녹음해서 AI 피드백을 받는 구조를 만들었습니다.

이미지 제안:
- 홈 화면 바로가기 아이콘을 누르는 장면
- 모바일 GitHub Pages 레슨 화면
- 녹음 버튼과 AI 코칭 리포트가 보이는 Trainer 화면

## Main Slide 2: From Tap To Coaching

슬라이드 메시지:

> 한 번의 탭이 오늘의 레슨, 녹음, STT, AI 코칭, 발음 비교로 이어진다.

시각 구성:
- 왼쪽에서 오른쪽으로 5단계 흐름을 보여줍니다.
- 각 단계는 화면 캡처 또는 간단한 아이콘으로 표현합니다.

흐름:
1. Tap: 홈 화면 바로가기
2. Learn: GitHub Pages 오늘의 레슨
3. Speak: 브라우저 녹음과 내 녹음 재생
4. Coach: STT + AI 평가 리포트
5. Compare: 원어민 발음과 교정 답변 발음 비교

핵심 키워드:
- Lesson
- Record
- STT
- AI Feedback
- Pronunciation Compare

발표 멘트:

> 사용자는 먼저 GitHub Pages의 오늘 레슨을 봅니다. 레슨에는 HSKK 말하기에 필요한 한자, 병음, 한국어 뜻, 질문 답변이 들어 있습니다. 레슨 하단의 `녹음하고 AI 평가 받기`를 누르면 Trainer로 이동하고, 같은 레슨 내용을 보면서 녹음할 수 있습니다. 녹음 후에는 내 녹음을 먼저 들어보고, STT와 AI 평가를 실행합니다. 평가 결과에서는 예상 점수와 강점, 약점, 교정 답변을 보고, transcript 기반 원어민 스타일 발음과 교정 답변 발음까지 비교해서 들을 수 있습니다.

중요한 설명:
- 원어민 발음은 실제 사람 녹음이 아니라 OpenAI TTS 기반 모범 발음입니다.
- AI 점수는 공식 HSKK 점수가 아니라 연습용 코칭 지표입니다.
- 레슨 기반 예상문제 Test는 현재 선택한 레슨의 질문, 그림묘사, 반복 문장을 재조합해 표시합니다.

## Main Slide 3: Harness가 하는 일

슬라이드 메시지:

> 단순 생성이 아니라, 매일 반복되는 학습 운영 체계.

시각 구성:
- 중앙에는 “나의 HSKK 학습 루틴” 또는 모바일 Trainer 화면을 배치합니다.
- 주변에는 역할별 Agent 또는 작업 단계가 순환 구조로 배치됩니다.
- Loop 구조가 보이도록 원형 화살표를 사용합니다.

Harness Loop:
1. Plan: HSKK 형식과 이전 학습 상태 확인
2. Generate: 오늘의 레슨 생성
3. Publish: GitHub Pages 모바일 페이지 갱신
4. Practice: 모바일에서 학습, 녹음, AI 평가
5. Export: 세션 JSON 저장 또는 export
6. Review: 약점과 복습 큐에 반영

현재 자동화 범위:
- 매일 레슨 생성
- 모바일 페이지 재빌드
- Git commit과 push
- 알림 발송 시도

현재 수동 범위:
- 사용자의 자기채점 메모를 Codex/Harness에 직접 전달
- Kakao refresh token 갱신
- NotebookLM 업로드

핵심 키워드:
- Multi-Agent
- Daily Loop
- Mobile-first
- AI Coaching
- JSON Export
- Review Queue

발표 멘트:

> 이 프로젝트의 핵심은 AI가 한 번 답을 만들어 주는 것이 아닙니다. Harness는 매일 반복되는 학습 운영을 담당합니다. 레슨을 만들고, 모바일 페이지를 갱신하고, 복습 흐름을 관리하고, 학습 결과가 다음 개선으로 이어질 수 있는 구조를 만듭니다. 여기에 AI Speaking Trainer가 붙으면서 이제 학습자는 단순히 읽는 것이 아니라 직접 말하고, 녹음하고, 피드백을 받고, 발음까지 비교할 수 있게 되었습니다.

## Harness Storytelling Options

아래 옵션은 발표자가 선택할 수 있는 구조 설명 이미지 후보입니다. 비개발자도 이해할 수 있게 친근하고 직관적으로 구성합니다.

### Option 1: Learning Factory, 쉬운 버전

비유:

> 학습 목표와 피드백이라는 재료가 들어오면, Agent들이 각 작업대에서 오늘의 학습 콘텐츠와 코칭 루틴을 만들어 모바일로 포장해 준다.

이미지 구성:
- 왼쪽: 학습 재료 바구니
  - HSKK 목표
  - 시험 형식
  - 이전 레슨
  - 자기채점 메모
  - 녹음/평가 JSON
- 중앙: 따뜻한 작업대 5개
  - Planner: 오늘의 학습 방향
  - Lesson Tutor: 문장과 질문 생성
  - Trainer Coach: 녹음과 AI 평가 연결
  - Review Coach: 약점과 복습 큐 정리
  - Publisher: GitHub Pages와 알림 준비
- 오른쪽: 완성품
  - 모바일 레슨
  - AI Speaking Trainer
  - 예상문제 Test
  - JSON export
  - 복습 계획

이미지 생성 프롬프트:

> A clean friendly A4 landscape business infographic showing an AI learning content production line. On the left, baskets labeled HSKK goal, exam format, previous lessons, self-score notes, speaking session JSON. In the center, five warm workstation desks with friendly AI agents working as planner, lesson tutor, trainer coach, review coach, publisher. On the right, finished outputs: mobile lesson screen, AI speaking trainer, expected question test, JSON export, review calendar. Korean labels, simple icons, clear arrows, soft professional colors, easy for a non-technical audience.

### Option 2: Agent Workers, 친근한 작업반

비유:

> 작은 AI 작업반이 매일 아침 오늘의 말하기 연습 세트를 준비하고, 나는 스마트폰에서 바로 연습한다.

이미지 구성:
- 배경: 밝은 코워킹 스튜디오
- 중앙: 스마트폰 화면
  - 오늘의 HSKK 레슨
  - 녹음 버튼
  - AI 코칭 리포트
- 주변 Agent 일꾼:
  - 커리큘럼 일꾼: 학습 목표와 시험 구조 확인
  - 레슨 일꾼: 한자, 병음, 뜻, 질문 준비
  - 평가 일꾼: STT와 AI 코칭 연결
  - 발음 일꾼: 원어민 스타일 TTS와 교정 답변 발음 준비
  - 복습 일꾼: 약점과 다음 연습 추천 정리

이미지 생성 프롬프트:

> Friendly AI worker crew in a bright coworking studio preparing a daily HSKK speaking practice set. A smartphone in the center shows today's HSKK lesson, a record button, AI coaching report, and pronunciation comparison. Five cute but professional helper workers surround it: curriculum planner, lesson maker, evaluation coach, pronunciation coach, review scheduler. A4 landscape business presentation style, clean Korean labels, clear arrows, warm but not childish, easy to understand.

### Option 3: Learning Lunchbox

비유:

> 여러 Agent가 학습 재료를 손질해서 오늘 바로 먹을 수 있는 30분 HSKK 학습 도시락으로 포장한다.

이미지 구성:
- 왼쪽: 학습 재료
  - 목표
  - 시험 형식
  - 이전 레슨
  - 녹음 결과
  - 약점
- 중앙: AI 요리사 Agent
  - 커리큘럼 레시피
  - 문장 카드
  - 예상문제
  - 발음 비교
  - 복습 추천
- 오른쪽: 완성된 도시락
  - Part 1 반복
  - Part 2 그림묘사
  - Part 3 질문 답변
  - 녹음/AI 평가
  - 원어민 발음 비교

이미지 생성 프롬프트:

> Friendly learning lunchbox metaphor for AI agents. A4 landscape business infographic. On the left, learning ingredients labeled goal, exam format, previous lessons, speaking results, weak points. In the center, five friendly AI worker-chefs prepare a 30-minute HSKK speaking lunchbox: curriculum recipe, sentence cards, expected questions, pronunciation comparison, review recommendation. On the right, a neat bento-style box labeled "오늘의 HSKK 30분" containing Part 1 repetition, Part 2 picture description, Part 3 Q&A, recording and AI feedback. Clean Korean labels, warm colors, professional and easy to understand.

### Option 4: Loop Engine

비유:

> 학습은 끝나는 이벤트가 아니라 다음 레슨의 입력으로 돌아가는 루프다.

이미지 구성:
- 원형 Loop:
  - Generate Lesson
  - Practice on Mobile
  - Record Voice
  - AI Feedback
  - Export JSON
  - Review Queue
  - Next Lesson
- 중앙 문구:
  - “말하기 연습이 다음 학습 설계로 돌아온다”

주의:
- 현재 모바일 입력값이 완전 자동으로 Codex에 들어가지는 않습니다.
- 자동화를 말할 때는 “JSON export와 Harness import를 염두에 둔 구조”라고 표현합니다.

## 시연영상 유첨 구성

기존 시연영상:

`C:\Users\swims\OneDrive\문서\카카오톡 받은 파일\시연영상.mp4`

기존 영상의 가치:
- 1분 30초 이내 조건에 적합합니다.
- 홈 화면 바로가기에서 GitHub Pages 학습 페이지로 들어가는 흐름을 보여줍니다.
- 모바일에서 앱처럼 사용하는 감각을 전달하기 좋습니다.

현재 기능 기준으로 보완하면 좋은 장면:
1. 홈 화면 바로가기 탭
2. 오늘의 HSKK 레슨 확인
3. `녹음하고 AI 평가 받기` 버튼 탭
4. Trainer에서 오늘 레슨 내용을 보면서 녹음
5. 내 녹음 재생
6. `STT + 평가` 실행
7. AI 코칭 리포트 확인
8. 원어민 발음 듣기
9. 교정 답변 발음 듣기
10. 예상문제 Test 탭에서 레슨 관련 예상문제 확인

권장 영상 구성:
- 0-5초: 타이틀 카드, “스마트폰에서 바로 시작하는 HSKK AI 말하기 루틴”
- 5-15초: 홈 화면 바로가기 실행
- 15-30초: 오늘 레슨 화면, 핵심 문장과 질문 확인
- 30-45초: Trainer 이동, 레슨 내용을 보면서 녹음
- 45-60초: 내 녹음 재생과 STT/AI 평가
- 60-75초: AI 코칭 리포트, 예상 점수, 약점, 교정 답변
- 75-85초: 원어민 발음과 교정 답변 발음 비교
- 85-90초: 마무리 문구, “AI가 준비하고, 나는 말하기에 집중한다”

발표자료에 붙일 콜아웃:
- 홈 화면에서 바로 시작
- 레슨을 보면서 녹음
- AI 코칭 리포트 확인
- 원어민 스타일 발음과 내 답변 비교
- 레슨 기반 예상문제 Test

## 발표자가 조심해야 할 표현

말해도 되는 표현:
- “공식 점수가 아닌 연습용 예상 점수입니다.”
- “원어민 발음은 OpenAI TTS 기반 모범 발음입니다.”
- “현재는 GitHub Pages와 Vercel API를 조합해 개인 학습용으로 운영합니다.”
- “세션 JSON export를 통해 Harness 연계를 확장할 수 있습니다.”

피해야 할 표현:
- “공식 HSKK 채점입니다.”
- “완전한 원어민 사람 음성입니다.”
- “자기채점이 자동으로 다음 레슨에 반영됩니다.”
- “Kakao 알림이 현재 항상 정상 발송됩니다.”
- “NotebookLM과 Codex가 이 프로젝트에서 직접 자동 연동됩니다.”

## 예상 질문과 답변

### Q1. GitHub Pages를 모바일 홈 화면 바로가기로 쓰고 있는데, 범용 앱처럼 쓰려면 어떻게 해야 하나?

답변:

현재는 개인용 바로가기 웹앱에 가깝습니다. 범용으로 쓰려면 PWA 구조를 추가하는 것이 다음 단계입니다.

필요 요소:
- web app manifest
- 앱 아이콘
- service worker
- 오프라인 캐시
- 사용자별 진행 상태 저장
- 피드백 제출 저장소 또는 데이터베이스
- 배포/권한/보안 정책

발표용 짧은 답변:

> 지금은 개인용 모바일 웹앱이고, 범용 앱처럼 확장하려면 PWA와 사용자별 데이터 저장 구조를 추가하면 됩니다.

### Q2. 자기채점과 피드백을 입력하면 다음 학습에 자동 반영되나?

답변:

현재 완전 자동 반영은 아닙니다. 모바일 페이지와 Trainer는 학습, 녹음, 평가, JSON export까지 지원합니다. 하지만 사용자가 입력한 자기채점 메모나 학습 피드백이 자동으로 Codex/Harness에 들어가는 구조는 아직 구현되어 있지 않습니다.

현재 흐름:
1. 모바일에서 학습합니다.
2. Trainer에서 녹음하고 AI 평가를 받습니다.
3. 결과를 JSON으로 export하거나 필요한 내용을 Codex에 전달합니다.
4. Codex/Harness가 오류 분석과 복습 계획에 반영할 수 있습니다.

발표용 짧은 답변:

> 현재는 반자동 루프입니다. 학습 결과를 JSON이나 Codex 입력으로 넘기면 다음 레슨과 복습 계획에 반영할 수 있고, 완전 자동 반영은 향후 서버 저장소나 GitHub import 자동화가 필요합니다.

### Q3. NotebookLM이나 자료작성 Tool과 Codex가 바로 연계 가능한가?

답변:

현재 프로젝트 기준으로는 직접 자동 연동이 아니라 파일 기반 연계가 가장 안정적입니다.

현재 방식:
1. Codex가 NotebookLM용 Markdown 소스를 작성합니다.
2. 사용자가 NotebookLM에 업로드합니다.
3. NotebookLM이 소스를 바탕으로 발표자료, 요약, Q&A를 생성합니다.
4. 필요하면 Codex가 결과 PPT를 검토하고 수정 소스를 다시 만듭니다.

발표용 짧은 답변:

> 지금은 Codex가 소스를 만들고 NotebookLM이 그 소스를 읽는 방식이 가장 안정적입니다. 직접 연동은 별도 커넥터나 API가 필요합니다.

### Q4. STT와 TTS를 쓰면 비용이 계속 발생하나?

답변:

네. 녹음 파일을 STT로 변환하거나, transcript와 교정 답변을 TTS로 만들 때 API 호출이 발생합니다. 그래서 현재 구조는 사용자가 평가 버튼을 눌렀을 때만 호출하고, 녹음 자체와 내 녹음 재생은 로컬에서 처리합니다.

발표용 짧은 답변:

> 녹음 자체는 로컬이고, STT/AI 평가/TTS를 실행할 때만 API가 호출됩니다. 그래서 사용자가 평가를 실행하는 순간에만 비용이 발생하는 구조입니다.

### Q5. Cloudflare Worker를 쓰지 않고 Vercel API를 쓰는 이유는?

답변:

초기에는 Cloudflare Worker를 사용했지만, OpenAI STT 호출에서 지역 제한 오류가 발생했습니다. 그래서 OpenAI API 호출 위치를 안정적으로 고정할 수 있는 Vercel Serverless Function으로 이전했습니다.

현재 Vercel API:
- `/api/health`
- `/api/transcribe`
- `/api/evaluate`
- `/api/session`
- `/api/speech`

발표용 짧은 답변:

> Cloudflare Worker에서 OpenAI STT 지역 제한 오류가 발생해, 운영 백엔드는 Vercel API로 전환했습니다. GitHub Pages는 화면을 담당하고, Vercel은 OpenAI API 호출을 담당합니다.

### Q6. HSKK 예상문제 Test는 상용 문제은행을 쓰나?

답변:

아닙니다. 저작권이 있는 상용 문제은행을 쓰지 않습니다. 기본 예상문제와 현재 레슨 JSON의 질문, 그림묘사, 반복 문장을 재조합해 HSKK 스타일 연습 문제로 제공합니다.

발표용 짧은 답변:

> 상용 문제은행이 아니라, 자체 생성 레슨과 HSKK 형식 기반의 연습 문제입니다.

### Q7. 원어민 발음 비교는 정확히 무엇인가?

답변:

사용자의 녹음이 STT로 transcript가 되면, 그 transcript를 OpenAI TTS로 다시 생성해 모범 발음처럼 들려줍니다. 평가 후에는 AI가 다듬은 교정 답변도 TTS로 들을 수 있습니다.

비교 대상:
- 내 녹음
- STT transcript 기반 모범 발음
- AI 교정 답변 기반 모범 발음

발표용 짧은 답변:

> 내 녹음과 AI가 생성한 모범 발음을 나란히 들으면서 발음과 답변 구조를 비교할 수 있습니다.

## 최종 발표 내러티브

Opening:

> 언어학습에서 가장 어려운 것은 공부 자체보다 시작까지의 마찰입니다. 오늘 무엇을 할지 찾고, 자료를 고르고, 기록을 남기고, 복습을 챙기는 과정을 반복하다 보면 말하기 연습은 뒤로 밀립니다.

Problem:

> HSKK 말하기를 준비하려면 매일 조금씩 말해야 하는데, 그 루틴을 혼자 유지하기가 어렵습니다. 특히 모바일에서 바로 열고, 바로 말하고, 바로 피드백 받는 구조가 필요했습니다.

Solution:

> 그래서 Codex와 Harness로 매일 HSKK 레슨을 만들고, GitHub Pages 모바일 페이지로 배포하고, AI Speaking Trainer에서 녹음과 평가까지 연결했습니다.

Demo:

> 사용자는 홈 화면 바로가기를 누르고 오늘 레슨을 봅니다. 레슨 하단에서 Trainer로 이동해 녹음하고, 내 녹음을 들어본 뒤 STT와 AI 평가를 실행합니다. 결과 화면에서는 강점, 약점, 교정 답변을 보고, 원어민 스타일 발음과 교정 답변 발음을 비교합니다.

Harness:

> 뒤에서는 Harness가 매일 반복되는 학습 운영을 담당합니다. 레슨 생성, 모바일 페이지 갱신, 복습 큐, JSON export를 연결해 학습 결과가 다음 개선으로 돌아갈 수 있게 만듭니다.

Closing:

> 핵심은 AI가 답을 한 번 주는 것이 아닙니다. AI가 매일 학습 준비와 피드백 구조를 만들고, 사람은 실제 말하기 연습에 집중하도록 만드는 것입니다.


# Language Study

HSKK 중급 말하기 시험 준비를 위한 Claude/Codex 학습 Harness입니다.  
현재 구성은 `56-language-tutor`와 `57-exam-prep` 원본 Harness를 보존하고, 이를 결합한 `hskk-study` 작업공간에서 실제 학습을 진행합니다.

## What This Project Does

- HSKK 중급 기준 6주 학습 계획을 관리합니다.
- 매일 30분 학습자료를 Markdown과 모바일 HTML로 제공합니다.
- 모든 중국어 학습 문장은 `한자 + 병음 + 한국어 뜻 + 말하기 포인트` 형식을 따릅니다.
- 답변 transcript나 녹음 메모를 바탕으로 오답 분석과 복습 계획을 갱신합니다.
- 카카오톡 "나에게 보내기" API로 매일 학습 알림을 보낼 수 있습니다.
- 완전 자동 모드에서는 매일 새 레슨 생성, 모바일 페이지 갱신, 커밋/푸시, 카톡 발송을 순서대로 실행합니다.

## Folder Structure

```text
.
├── 56-language-tutor/        # 원본 언어 튜터 Harness
├── 57-exam-prep/             # 원본 시험 준비 Harness
├── hskk-study/
│   ├── .claude/              # HSKK 전용 Harness 지침, agents, skills
│   ├── _workspace/           # 실제 학습 산출물
│   ├── mobile/               # 모바일 학습 페이지
│   ├── scripts/              # 카카오 알림 스크립트
│   ├── .env.example          # 카카오 토큰 설정 예시
│   └── automation.md         # 모바일/카카오 자동화 안내
└── AGENTS.md                 # 프로젝트 작업 규칙
```

## How To Study

1. Codex/Claude Code에서 `오늘 공부`라고 요청합니다.
2. `hskk-study/_workspace/04_lessons/lesson_XX.md` 파일을 보고 말하기 연습을 합니다.
3. 모바일에서는 `hskk-study/mobile/index.html`을 열어 학습합니다.
4. 답변 transcript, 녹음 메모, 자기채점 결과를 Codex에 보냅니다.
5. Codex가 오답 분석, 복습 계획, 다음 레슨을 업데이트합니다.

## Current Study Flow

기본 세션은 30분입니다.

| Time | Activity |
| ---: | --- |
| 5 min | 지난 학습 복습 |
| 10 min | 새 문장/표현/발음 포인트 학습 |
| 10 min | HSKK 유형별 말하기 연습 |
| 5 min | 자기채점, 메모, 복습 예약 |

HSKK 중급 형식은 다음 구조를 기준으로 합니다.

| Part | Task | Items |
| --- | --- | ---: |
| 1 | 듣고 반복 | 10 |
| 2 | 그림 보고 말하기 | 2 |
| 3 | 질문 답변 | 2 |

## Mobile Page

모바일 학습 페이지:

```text
hskk-study/mobile/index.html
```

GitHub Pages를 켜면 `.env.example`의 기본 URL처럼 휴대폰에서 바로 열 수 있습니다.

```text
https://parksooyoung-john.github.io/Language_Study/hskk-study/mobile/
```

## Kakao Reminder Setup

카카오톡 "나에게 보내기" 알림을 쓰려면 Kakao Developers 앱에서 REST API key와 refresh token을 준비한 뒤 `hskk-study/.env`를 만듭니다.

```env
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_REFRESH_TOKEN=your_kakao_refresh_token
KAKAO_CLIENT_SECRET=your_optional_kakao_client_secret
HSKK_MOBILE_URL=https://parksooyoung-john.github.io/Language_Study/hskk-study/mobile/
```

`KAKAO_CLIENT_SECRET`은 Kakao Developers 앱에서 Client Secret 기능을 켠 경우에만 필요합니다.

완전 자동 dry run:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1 -DryRun
```

새 레슨 생성, 모바일 갱신, 커밋/푸시, 카톡 발송:

```powershell
powershell -ExecutionPolicy Bypass -File .\hskk-study\scripts\run_daily_auto_study.ps1
```

## Automation

Codex app 자동화 `HSKK Kakao Daily Lesson`이 매일 오전 8시 실행되도록 등록되어 있습니다.  
토큰이 없으면 실제 발송은 실패하며, 이 경우 스크립트가 명확한 오류 메시지를 출력합니다.

자세한 내용은 `hskk-study/automation.md`를 참고하세요.

## Project Rules

- 원본 `56-language-tutor`, `57-exam-prep` 폴더는 직접 수정하지 않습니다.
- 실제 HSKK 학습 산출물은 `hskk-study/_workspace/`에 둡니다.
- 프로젝트 변경 완료 후 자동 커밋합니다.
- `.env`, 로그, Python 캐시는 커밋하지 않습니다.

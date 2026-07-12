const SETTINGS_KEY = "hskk_trainer_settings";
const HISTORY_KEY = "hskk_trainer_sessions";
const DEFAULT_API_BASE = "https://hskk-ai-speaking-trainer.vercel.app";

const params = new URLSearchParams(window.location.search);
const requestedMode = params.get("mode");
const requestedLesson = params.get("lesson");
const returnPath = params.get("return") || "../index.html";

const state = {
  mode: requestedMode === "expected" ? "expected" : "daily",
  lesson: null,
  lessonDetail: null,
  level: "intermediate",
  questionIndex: 0,
  mediaRecorder: null,
  chunks: [],
  audioBlob: null,
  audioFileName: "hskk-recording.webm",
  nativeAudioUrl: null,
  correctedAudioUrl: null,
  currentSession: null,
};

const questions = {
  beginner: [
    {
      item_id: "beginner_repeat_001",
      part: "repeat",
      label: "Part 1 · Repeat",
      prompt_hanzi: "我每天学习汉语。",
      prompt_pinyin: "Wo mei tian xuexi Hanyu.",
      prompt_ko: "나는 매일 중국어를 공부합니다.",
      time_limit_sec: 30,
    },
    {
      item_id: "beginner_part3_001",
      part: "answer_questions",
      label: "Part 3 · Answer",
      prompt_hanzi: "你喜欢学习汉语吗？",
      prompt_pinyin: "Ni xihuan xuexi Hanyu ma?",
      prompt_ko: "중국어 공부를 좋아하나요?",
      time_limit_sec: 45,
    },
  ],
  intermediate: [
    {
      item_id: "intermediate_part2_001",
      part: "picture_description",
      label: "Part 2 · Picture",
      prompt_hanzi: "请描述一个人在手机上学习汉语的场景。",
      prompt_pinyin: "Qing miaoshu yi ge ren zai shouji shang xuexi Hanyu de changjing.",
      prompt_ko: "휴대폰으로 중국어를 공부하는 장면을 묘사하세요.",
      time_limit_sec: 60,
    },
    {
      item_id: "intermediate_part3_001",
      part: "answer_questions",
      label: "Part 3 · Answer",
      prompt_hanzi: "你每天什么时候学习汉语？为什么？",
      prompt_pinyin: "Ni mei tian shenme shihou xuexi Hanyu? Weishenme?",
      prompt_ko: "매일 언제 중국어를 공부하나요? 왜 그런가요?",
      time_limit_sec: 60,
    },
  ],
  advanced: [
    {
      item_id: "advanced_part3_001",
      part: "answer_questions",
      label: "Part 3 · Answer",
      prompt_hanzi: "你觉得用AI学习外语有什么优点和缺点？",
      prompt_pinyin: "Ni juede yong AI xuexi waiyu you shenme youdian he quedian?",
      prompt_ko: "AI로 외국어를 공부하는 장단점은 무엇이라고 생각하나요?",
      time_limit_sec: 90,
    },
  ],
};

const $ = (selector) => document.querySelector(selector);

function readJson(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function settings() {
  const stored = readJson(SETTINGS_KEY, {});
  return { apiBase: stored.apiBase || DEFAULT_API_BASE };
}

function normalizedApiBase() {
  return settings().apiBase.replace(/\/$/, "");
}

function setStatus(message, kind = "info") {
  const box = $("#status-box");
  box.innerHTML = message;
  box.dataset.kind = kind;
}

function showSettings(show) {
  $("#settings-panel").classList.toggle("hidden", !show);
  $("#toggle-settings").setAttribute("aria-expanded", String(show));
}

function setApiState(text, kind = "neutral") {
  const badge = $("#api-state");
  badge.textContent = text;
  badge.className = `badge ${kind}`;
}

function formatErrorMessage(error) {
  const details = error.details || {};
  const isRegionError = details.code === "unsupported_country_region_territory";
  const userMessage = isRegionError
    ? "OpenAI STT 호출이 지역 제한으로 거부되었습니다. API 서버를 Vercel 백엔드 URL로 변경해야 합니다."
    : details.user_message || details.message || error.message;
  const code = details.code ? ` (${details.code})` : "";
  const rawDetails = details.details || details;
  return `
    <strong>${escapeHtml(userMessage)}${escapeHtml(code)}</strong>
    <details>
      <summary>개발자용 상세 오류</summary>
      <pre>${escapeHtml(JSON.stringify(rawDetails, null, 2))}</pre>
    </details>
  `;
}

async function readApiResponse(response) {
  const raw = await response.text();
  let payload = null;
  try {
    payload = raw ? JSON.parse(raw) : null;
  } catch {
    payload = null;
  }
  if (!response.ok) {
    const error = new Error(payload?.user_message || payload?.message || raw || `HTTP ${response.status}`);
    error.details = payload;
    error.raw = raw;
    throw error;
  }
  return payload;
}

async function testApiConnection({ silent = false } = {}) {
  const base = normalizedApiBase();
  if (!base) {
    setApiState("미설정", "error");
    showSettings(true);
    return false;
  }
  try {
    const response = await fetch(`${base}/api/health`, { cache: "no-store" });
    const payload = await readApiResponse(response);
    if (!payload.ok) throw new Error("Health check failed");
    setApiState("연결됨", "ok");
    if (!silent) setStatus("API 연결이 정상입니다.");
    showSettings(false);
    return true;
  } catch (error) {
    setApiState("오류", "error");
    showSettings(true);
    if (!silent) setStatus(`API 연결을 확인하세요: ${escapeHtml(error.message)}`, "error");
    return false;
  }
}

async function loadLesson() {
  try {
    const manifestResponse = await fetch("../lessons/manifest.json", { cache: "no-store" });
    const manifest = await manifestResponse.json();
    const latest = manifest[manifest.length - 1];
    const selected = requestedLesson
      ? manifest.find((item) => item.slug === requestedLesson)
      : latest;
    state.lesson = selected || latest;

    const jsonPath = state.lesson?.json_path || `./${state.lesson.slug}.json`;
    const detailResponse = await fetch(`../lessons/${jsonPath.replace(/^\.\//, "")}`, { cache: "no-store" });
    state.lessonDetail = await detailResponse.json();
    $("#lesson-link").href = returnPath;
    renderLessonPrompt();
  } catch {
    $("#lesson-summary").textContent = "레슨 정보를 불러오지 못했습니다.";
  }
}

function renderLessonPrompt() {
  const detail = state.lessonDetail;
  if (!detail) return;
  const repeat = lessonItems(detail.repeat, "문장");
  const picture = lessonItems(detail.picture, "그림");
  const questionsHtml = lessonItems(detail.questions, "질문");
  const visual = detail.visual_path
    ? `<img class="lesson-visual" src="../lessons/${escapeHtml(detail.visual_path.replace(/^\.\//, ""))}" alt="오늘 레슨 그림 묘사 장면">`
    : "";

  $("#lesson-summary").innerHTML = `
    <div class="prompt-header">
      <span class="badge">Lesson ${escapeHtml(String(detail.number))}</span>
      <strong>${escapeHtml(detail.title)}</strong>
      <p class="muted">${escapeHtml(detail.goal || "")}</p>
    </div>
    ${visual}
    <div class="lesson-sections">
      <section>
        <h3>따라 말하기</h3>
        ${repeat}
      </section>
      <section>
        <h3>그림 묘사</h3>
        <p class="scene-text">${escapeHtml(detail.scene || "")}</p>
        ${picture}
      </section>
      <section>
        <h3>질문 답변</h3>
        ${questionsHtml}
      </section>
    </div>
  `;
}

function lessonItems(items, label) {
  return (items || []).map((item, index) => `
    <article class="lesson-line">
      <span>${escapeHtml(item.tag || `${label} ${index + 1}`)}</span>
      <strong>${escapeHtml(item.hanzi || "")}</strong>
      <em>${escapeHtml(item.pinyin || "")}</em>
      <small>${escapeHtml(item.meaning || item.focus || "")}</small>
    </article>
  `).join("");
}

function renderQuestion() {
  const list = questions[state.level] || questions.intermediate;
  const item = list[state.questionIndex] || list[0];
  $("#test-item").innerHTML = `
    <div class="question-meta">
      <span>${escapeHtml(item.label)}</span>
      <span>${escapeHtml(state.level)}</span>
      <span>${item.time_limit_sec}s</span>
    </div>
    <div class="hanzi">${escapeHtml(item.prompt_hanzi)}</div>
    <div class="pinyin">${escapeHtml(item.prompt_pinyin)}</div>
    <p class="muted">${escapeHtml(item.prompt_ko)}</p>
  `;
}

function currentPrompt() {
  if (state.mode === "expected") {
    const list = questions[state.level] || questions.intermediate;
    return list[state.questionIndex] || list[0];
  }
  return {
    item_id: `lesson_${state.lessonDetail?.number || state.lesson?.number || "latest"}`,
    part: "daily_lesson",
    label: state.lessonDetail?.title || "Daily Lesson",
    prompt_hanzi: state.lessonDetail?.title || "Today's HSKK lesson",
    prompt_pinyin: "",
    prompt_ko: state.lessonDetail?.goal || "오늘 레슨 기반 자유 응답",
    lesson_detail: state.lessonDetail,
    time_limit_sec: 60,
  };
}

function activateMode(mode) {
  state.mode = mode;
  document.querySelectorAll("[data-mode]").forEach((item) => item.classList.toggle("active", item.dataset.mode === mode));
  $("#lesson-panel").classList.toggle("hidden", mode !== "daily");
  $("#expected-panel").classList.toggle("hidden", mode !== "expected");
}

function canEvaluate() {
  return (state.audioBlob && state.audioBlob.size >= 1024) || Boolean($("#transcript").value.trim());
}

function updateEvaluationButton() {
  $("#run-evaluation").disabled = !canEvaluate();
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    setStatus("이 브라우저는 녹음을 지원하지 않습니다.", "error");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recordingFormat = getRecordingFormat();
    state.chunks = [];
    state.audioBlob = null;
    state.mediaRecorder = recordingFormat.mimeType
      ? new MediaRecorder(stream, { mimeType: recordingFormat.mimeType })
      : new MediaRecorder(stream);
    state.audioFileName = `hskk-recording.${recordingFormat.extension}`;
    state.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) state.chunks.push(event.data);
    };
    state.mediaRecorder.onstop = () => {
      const mimeType = normalizeAudioMime(state.mediaRecorder.mimeType || recordingFormat.mimeType || "audio/webm");
      state.audioBlob = new Blob(state.chunks, { type: mimeType });
      state.audioFileName = `hskk-recording.${extensionForMime(mimeType)}`;
      const url = URL.createObjectURL(state.audioBlob);
      $("#audio-preview").src = url;
      $("#playback-card").classList.remove("hidden");
      $("#retry-recording").disabled = false;
      updateEvaluationButton();
      stream.getTracks().forEach((track) => track.stop());
      $("#recording-state").textContent = "녹음 완료";
      $("#recording-title").textContent = "내 녹음을 들어보고 평가하세요.";
      $("#recording-meta").textContent = `${state.audioFileName} · ${Math.round(state.audioBlob.size / 1024)}KB`;
      setStatus(state.audioBlob.size < 1024 ? "녹음 파일이 너무 짧습니다. 3초 이상 다시 녹음하세요." : "재생 후 평가할 수 있습니다.", state.audioBlob.size < 1024 ? "error" : "info");
    };
    state.mediaRecorder.start();
    $("#start-recording").disabled = true;
    $("#stop-recording").disabled = false;
    $("#retry-recording").disabled = true;
    $("#run-evaluation").disabled = true;
    $("#recording-state").textContent = "녹음 중";
    $("#recording-title").textContent = "말하는 중입니다.";
    $("#recording-meta").textContent = "끝나면 정지를 누르세요.";
    setStatus("녹음 중입니다.");
  } catch (error) {
    setStatus(`마이크 권한을 확인하세요: ${escapeHtml(error.message)}`, "error");
  }
}

function stopRecording() {
  if (state.mediaRecorder?.state === "recording") {
    state.mediaRecorder.stop();
    $("#start-recording").disabled = false;
    $("#stop-recording").disabled = true;
  }
}

function retryRecording() {
  state.audioBlob = null;
  state.audioFileName = "hskk-recording.webm";
  state.chunks = [];
  $("#audio-preview").removeAttribute("src");
  $("#playback-card").classList.add("hidden");
  clearComparisonAudio();
  $("#retry-recording").disabled = true;
  updateEvaluationButton();
  $("#recording-state").textContent = "대기";
  $("#recording-title").textContent = "문제를 보고 자연스럽게 말해 보세요.";
  $("#recording-meta").textContent = "3초 이상 녹음하면 평가할 수 있습니다.";
  setStatus("다시 녹음할 준비가 되었습니다.");
}

function clearComparisonAudio() {
  revokeAudioUrl("nativeAudioUrl");
  revokeAudioUrl("correctedAudioUrl");
  $("#native-audio").removeAttribute("src");
  $("#corrected-audio").removeAttribute("src");
  $("#native-audio-card").classList.add("hidden");
  $("#corrected-audio-card").classList.add("hidden");
  $("#comparison-panel").classList.add("hidden");
}

function revokeAudioUrl(key) {
  if (state[key]) {
    URL.revokeObjectURL(state[key]);
    state[key] = null;
  }
}

async function generateSpeechAudio(text, kind) {
  const cleanText = String(text || "").trim();
  if (!cleanText) return null;

  const response = await fetch(`${normalizedApiBase()}/api/speech`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: cleanText,
      voice: "coral",
      instructions: kind === "corrected"
        ? "Speak this corrected Mandarin Chinese answer clearly and naturally for HSKK speaking practice."
        : "Speak this Mandarin Chinese transcript clearly and naturally for HSKK speaking practice.",
    }),
  });
  if (!response.ok) await readApiResponse(response);
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

function showSpeechAudio(kind, url) {
  if (!url) return;
  const isCorrected = kind === "corrected";
  const key = isCorrected ? "correctedAudioUrl" : "nativeAudioUrl";
  const audio = isCorrected ? $("#corrected-audio") : $("#native-audio");
  const card = isCorrected ? $("#corrected-audio-card") : $("#native-audio-card");

  revokeAudioUrl(key);
  state[key] = url;
  audio.src = url;
  card.classList.remove("hidden");
  $("#comparison-panel").classList.remove("hidden");
}

async function prepareSpeechAudio(text, kind) {
  try {
    const url = await generateSpeechAudio(text, kind);
    showSpeechAudio(kind, url);
  } catch (error) {
    console.warn(`${kind} speech generation failed`, error);
  }
}

async function runEvaluation() {
  if (!settings().apiBase) {
    showSettings(true);
    setStatus("먼저 Vercel API Base URL을 저장하세요.", "error");
    return;
  }
  if (!state.audioBlob && !$("#transcript").value.trim()) {
    setStatus("녹음하거나 transcript를 직접 입력하세요.", "error");
    return;
  }

  try {
    $("#run-evaluation").disabled = true;
    clearComparisonAudio();
    setStatus("STT를 실행하는 중입니다.");
    let transcript = $("#transcript").value.trim();
    if (state.audioBlob) {
      if (state.audioBlob.size < 1024) {
        setStatus("녹음 파일이 너무 짧거나 비어 있습니다. 3초 이상 다시 녹음하세요.", "error");
        updateEvaluationButton();
        return;
      }
      const form = new FormData();
      form.append("audio", state.audioBlob, state.audioFileName);
      const transcribeResponse = await fetch(`${normalizedApiBase()}/api/transcribe`, {
        method: "POST",
        body: form,
      });
      const transcribeJson = await readApiResponse(transcribeResponse);
      transcript = transcribeJson.text || transcribeJson.transcript || "";
      $("#transcript").value = transcript;
    }
    if (transcript) {
      setStatus("원어민 발음을 준비하는 중입니다.");
      await prepareSpeechAudio(transcript, "native");
    }

    setStatus("AI 평가를 실행하는 중입니다.");
    const payload = {
      mode: state.mode === "expected" ? "expected_question_test" : "daily_lesson",
      level: state.mode === "expected" ? state.level : "intermediate",
      lesson: state.lessonDetail || state.lesson,
      prompt: currentPrompt(),
      transcript,
      client_timestamp: new Date().toISOString(),
    };
    const evaluateResponse = await fetch(`${normalizedApiBase()}/api/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const feedback = await readApiResponse(evaluateResponse);
    const session = buildSession(payload, feedback);
    state.currentSession = session;
    saveSession(session);
    renderFeedback(session);
    renderHistory();
    $("#export-current").disabled = false;
    $("#post-feedback-actions").classList.remove("hidden");
    if (feedback.corrected_answer) {
      setStatus("교정 답변 발음을 준비하는 중입니다.");
      await prepareSpeechAudio(feedback.corrected_answer, "corrected");
    }
    setStatus("평가가 완료되었습니다.");
  } catch (error) {
    console.error(error);
    showSettings(true);
    setStatus(formatErrorMessage(error), "error");
  } finally {
    updateEvaluationButton();
  }
}

function buildSession(payload, feedback) {
  const score = feedback.estimated_score ?? feedback.overall_score ?? null;
  return {
    schema_version: "hskk-trainer-session-v1",
    session_id: `session_${Date.now()}`,
    mode: payload.mode,
    level: payload.level,
    started_at: payload.client_timestamp,
    completed_at: new Date().toISOString(),
    lesson: payload.lesson,
    prompt: payload.prompt,
    transcript: payload.transcript,
    estimated_score: score,
    feedback,
    harness_targets: [
      "_workspace/06_error_analysis.md",
      "_workspace/07_review_plan.md",
    ],
  };
}

function saveSession(session) {
  const history = readJson(HISTORY_KEY, []);
  history.unshift(session);
  writeJson(HISTORY_KEY, history.slice(0, 50));
}

function renderFeedback(session) {
  const feedback = session.feedback || {};
  const rubric = feedback.rubric || {};
  $("#feedback-output").className = "feedback-card coaching-report";
  $("#feedback-output").innerHTML = `
    <div class="score-hero">
      <span>예상 점수</span>
      <strong>${escapeHtml(String(session.estimated_score ?? "n/a"))}</strong>
      <small>공식 HSKK 점수가 아닌 연습용 코칭 지표입니다.</small>
    </div>
    <div class="feedback-grid">
      ${scorePill("Task", rubric.task_completion)}
      ${scorePill("Fluency", rubric.fluency)}
      ${scorePill("Grammar", rubric.grammar)}
      ${scorePill("Vocabulary", rubric.vocabulary)}
      ${scorePill("Pronunciation", rubric.pronunciation)}
    </div>
    ${reportBlock("잘한 점", feedback.strengths)}
    ${reportBlock("다음에 고칠 점", feedback.weaknesses)}
    ${reportBlock("다음 연습 추천", feedback.review_recommendations || feedback.recommendations)}
    <section class="correction-card">
      <h3>교정 답변</h3>
      <p>${escapeHtml(feedback.corrected_answer || "교정 답변이 없습니다.")}</p>
    </section>
    <p class="hint">${escapeHtml(feedback.overall_comments || "")}</p>
  `;
}

function reportBlock(title, items) {
  return `<section class="report-block"><h3>${escapeHtml(title)}</h3><ul>${listItems(items)}</ul></section>`;
}

function renderHistory() {
  const history = readJson(HISTORY_KEY, []);
  if (!history.length) {
    $("#history-list").innerHTML = '<div class="history-item">저장된 세션이 없습니다.</div>';
    return;
  }
  $("#history-list").innerHTML = history.map((session) => `
    <div class="history-item">
      <strong>${escapeHtml(session.mode)} · ${escapeHtml(session.level || "")}</strong>
      <div class="muted">${new Date(session.completed_at).toLocaleString()} · score ${escapeHtml(String(session.estimated_score ?? "n/a"))}</div>
      <button type="button" class="secondary" data-export-session="${escapeHtml(session.session_id)}">JSON</button>
    </div>
  `).join("");
}

function downloadJson(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

function scorePill(label, value) {
  return `<div class="score-pill"><strong>${escapeHtml(label)}</strong>${escapeHtml(String(value ?? "n/a"))}</div>`;
}

function listItems(items) {
  const values = Array.isArray(items) && items.length ? items : ["내용 없음"];
  return values.map((item) => `<li>${escapeHtml(String(item))}</li>`).join("");
}

function getRecordingFormat() {
  const candidates = [
    { mimeType: "audio/webm;codecs=opus", extension: "webm" },
    { mimeType: "audio/webm", extension: "webm" },
    { mimeType: "audio/mp4", extension: "mp4" },
  ];
  for (const candidate of candidates) {
    if (MediaRecorder.isTypeSupported(candidate.mimeType)) {
      return candidate;
    }
  }
  return { mimeType: "", extension: "webm" };
}

function normalizeAudioMime(mimeType) {
  return String(mimeType || "audio/webm").split(";")[0].trim() || "audio/webm";
}

function extensionForMime(mimeType) {
  const clean = normalizeAudioMime(mimeType);
  if (clean === "audio/mp4") return "mp4";
  if (clean === "audio/mpeg") return "mp3";
  if (clean === "audio/wav") return "wav";
  return "webm";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindEvents() {
  const config = settings();
  $("#api-base").value = config.apiBase || DEFAULT_API_BASE;
  $("#return-link").href = returnPath;
  $("#return-link-bottom").href = returnPath;

  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => activateMode(button.dataset.mode));
  });

  $("#toggle-settings").addEventListener("click", () => {
    showSettings($("#settings-panel").classList.contains("hidden"));
  });
  $("#save-settings").addEventListener("click", () => {
    writeJson(SETTINGS_KEY, { apiBase: $("#api-base").value.trim() || DEFAULT_API_BASE });
    setStatus("API 설정을 저장했습니다.");
    testApiConnection({ silent: true });
  });
  $("#restore-settings").addEventListener("click", () => {
    $("#api-base").value = DEFAULT_API_BASE;
    writeJson(SETTINGS_KEY, { apiBase: DEFAULT_API_BASE });
    setStatus("기본 API URL로 복원했습니다.");
    testApiConnection({ silent: true });
  });
  $("#test-settings").addEventListener("click", () => {
    writeJson(SETTINGS_KEY, { apiBase: $("#api-base").value.trim() || DEFAULT_API_BASE });
    testApiConnection();
  });

  $("#test-level").addEventListener("change", (event) => {
    state.level = event.target.value;
    state.questionIndex = 0;
    renderQuestion();
  });

  $("#prev-question").addEventListener("click", () => {
    const list = questions[state.level] || questions.intermediate;
    state.questionIndex = Math.max(0, state.questionIndex - 1);
    if (!list[state.questionIndex]) state.questionIndex = 0;
    renderQuestion();
  });

  $("#next-question").addEventListener("click", () => {
    const list = questions[state.level] || questions.intermediate;
    state.questionIndex = Math.min(list.length - 1, state.questionIndex + 1);
    renderQuestion();
  });

  $("#start-recording").addEventListener("click", startRecording);
  $("#stop-recording").addEventListener("click", stopRecording);
  $("#retry-recording").addEventListener("click", retryRecording);
  $("#retry-after-feedback").addEventListener("click", retryRecording);
  $("#run-evaluation").addEventListener("click", runEvaluation);
  $("#transcript").addEventListener("input", updateEvaluationButton);
  $("#export-current").addEventListener("click", () => {
    if (state.currentSession) downloadJson(`${state.currentSession.session_id}.json`, state.currentSession);
  });
  $("#export-all").addEventListener("click", () => {
    downloadJson(`hskk_trainer_sessions_${Date.now()}.json`, {
      schema_version: "hskk-trainer-bundle-v1",
      exported_at: new Date().toISOString(),
      sessions: readJson(HISTORY_KEY, []),
    });
  });
  $("#clear-history").addEventListener("click", () => {
    if (confirm("로컬 세션 기록을 삭제할까요?")) {
      localStorage.removeItem(HISTORY_KEY);
      renderHistory();
      setStatus("로컬 History를 삭제했습니다.");
    }
  });
  $("#history-list").addEventListener("click", (event) => {
    const id = event.target?.dataset?.exportSession;
    if (!id) return;
    const session = readJson(HISTORY_KEY, []).find((item) => item.session_id === id);
    if (session) downloadJson(`${session.session_id}.json`, session);
  });
}

bindEvents();
activateMode(state.mode);
loadLesson();
renderQuestion();
renderHistory();
testApiConnection({ silent: true });

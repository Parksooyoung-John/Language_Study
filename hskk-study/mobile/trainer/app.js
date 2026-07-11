const SETTINGS_KEY = "hskk_trainer_settings";
const HISTORY_KEY = "hskk_trainer_sessions";

const state = {
  mode: "daily",
  lesson: null,
  level: "intermediate",
  questionIndex: 0,
  mediaRecorder: null,
  chunks: [],
  audioBlob: null,
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
  return readJson(SETTINGS_KEY, { apiBase: "" });
}

function setStatus(message, kind = "info") {
  const box = $("#status-box");
  box.textContent = message;
  box.dataset.kind = kind;
}

async function loadLesson() {
  try {
    const response = await fetch("../lessons/manifest.json", { cache: "no-store" });
    const manifest = await response.json();
    const latest = manifest[manifest.length - 1];
    state.lesson = latest;
    $("#lesson-summary").innerHTML = `
      <strong>${escapeHtml(latest.title)}</strong>
      <p class="muted">Date: ${escapeHtml(latest.date || "n/a")} · Lesson ${latest.number}</p>
    `;
    $("#lesson-link").href = `../lessons/${latest.slug}.html`;
  } catch {
    $("#lesson-summary").textContent = "레슨 manifest를 불러오지 못했습니다.";
  }
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
    item_id: `lesson_${state.lesson?.number || "latest"}`,
    part: "daily_lesson",
    label: "Daily Lesson",
    prompt_hanzi: state.lesson?.title || "Today's HSKK lesson",
    prompt_pinyin: "",
    prompt_ko: "오늘 레슨 기반 자유 응답",
    time_limit_sec: 60,
  };
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    setStatus("이 브라우저는 녹음을 지원하지 않습니다.", "error");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.chunks = [];
    state.mediaRecorder = new MediaRecorder(stream);
    state.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) state.chunks.push(event.data);
    };
    state.mediaRecorder.onstop = () => {
      state.audioBlob = new Blob(state.chunks, { type: state.mediaRecorder.mimeType || "audio/webm" });
      const url = URL.createObjectURL(state.audioBlob);
      $("#audio-preview").src = url;
      $("#audio-preview").hidden = false;
      $("#retry-recording").disabled = false;
      stream.getTracks().forEach((track) => track.stop());
      $("#recording-state").textContent = "녹음 완료";
    };
    state.mediaRecorder.start();
    $("#start-recording").disabled = true;
    $("#stop-recording").disabled = false;
    $("#retry-recording").disabled = true;
    $("#recording-state").textContent = "녹음 중";
    setStatus("녹음 중입니다.");
  } catch (error) {
    setStatus(`마이크 권한을 확인하세요: ${error.message}`, "error");
  }
}

function stopRecording() {
  if (state.mediaRecorder?.state === "recording") {
    state.mediaRecorder.stop();
    $("#start-recording").disabled = false;
    $("#stop-recording").disabled = true;
    setStatus("녹음이 완료되었습니다. 필요하면 재생 후 평가하세요.");
  }
}

function retryRecording() {
  state.audioBlob = null;
  state.chunks = [];
  $("#audio-preview").hidden = true;
  $("#audio-preview").removeAttribute("src");
  $("#retry-recording").disabled = true;
  $("#recording-state").textContent = "대기";
  setStatus("다시 녹음할 준비가 되었습니다.");
}

async function runEvaluation() {
  const config = settings();
  if (!config.apiBase) {
    setStatus("먼저 Cloudflare Worker API Base URL을 저장하세요.", "error");
    return;
  }
  if (!state.audioBlob && !$("#transcript").value.trim()) {
    setStatus("녹음하거나 transcript를 직접 입력하세요.", "error");
    return;
  }

  try {
    setStatus("STT를 실행하는 중입니다. API 비용이 발생할 수 있습니다.");
    let transcript = $("#transcript").value.trim();
    if (state.audioBlob) {
      const form = new FormData();
      form.append("audio", state.audioBlob, "hskk-recording.webm");
      const transcribeResponse = await fetch(`${config.apiBase.replace(/\/$/, "")}/api/transcribe`, {
        method: "POST",
        body: form,
      });
      if (!transcribeResponse.ok) throw new Error(await transcribeResponse.text());
      const transcribeJson = await transcribeResponse.json();
      transcript = transcribeJson.text || transcribeJson.transcript || "";
      $("#transcript").value = transcript;
    }

    setStatus("AI 평가를 실행하는 중입니다.");
    const payload = {
      mode: state.mode === "expected" ? "expected_question_test" : "daily_lesson",
      level: state.mode === "expected" ? state.level : "intermediate",
      lesson: state.lesson,
      prompt: currentPrompt(),
      transcript,
      client_timestamp: new Date().toISOString(),
    };
    const evaluateResponse = await fetch(`${config.apiBase.replace(/\/$/, "")}/api/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!evaluateResponse.ok) throw new Error(await evaluateResponse.text());
    const feedback = await evaluateResponse.json();
    const session = buildSession(payload, feedback);
    state.currentSession = session;
    saveSession(session);
    renderFeedback(session);
    renderHistory();
    $("#export-current").disabled = false;
    setStatus("평가가 완료되었습니다.");
  } catch (error) {
    setStatus(`평가 실패: ${error.message}`, "error");
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
  const strengths = listItems(feedback.strengths);
  const weaknesses = listItems(feedback.weaknesses);
  const recommendations = listItems(feedback.review_recommendations || feedback.recommendations);
  $("#feedback-output").className = "feedback-card";
  $("#feedback-output").innerHTML = `
    <strong>예상 점수: ${escapeHtml(String(session.estimated_score ?? "n/a"))}</strong>
    <div class="feedback-grid">
      ${scorePill("Task", rubric.task_completion)}
      ${scorePill("Fluency", rubric.fluency)}
      ${scorePill("Grammar", rubric.grammar)}
      ${scorePill("Vocabulary", rubric.vocabulary)}
      ${scorePill("Pronunciation", rubric.pronunciation)}
    </div>
    <h3>교정 답변</h3>
    <p>${escapeHtml(feedback.corrected_answer || "교정 답변이 없습니다.")}</p>
    <h3>강점</h3>
    <ul>${strengths}</ul>
    <h3>약점</h3>
    <ul>${weaknesses}</ul>
    <h3>복습 추천</h3>
    <ul>${recommendations}</ul>
    <p class="hint">이 점수는 공식 HSKK 점수가 아니라 연습용 예상 평가입니다.</p>
  `;
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
  $("#api-base").value = config.apiBase || "";

  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      document.querySelectorAll("[data-mode]").forEach((item) => item.classList.toggle("active", item === button));
      $("#lesson-panel").classList.toggle("hidden", state.mode !== "daily");
      $("#expected-panel").classList.toggle("hidden", state.mode !== "expected");
    });
  });

  $("#save-settings").addEventListener("click", () => {
    writeJson(SETTINGS_KEY, { apiBase: $("#api-base").value.trim() });
    setStatus("API 설정을 저장했습니다.");
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
  $("#run-evaluation").addEventListener("click", runEvaluation);
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
loadLesson();
renderQuestion();
renderHistory();

const fs = require("node:fs/promises");
const formidableModule = require("formidable");

const createForm = formidableModule.formidable || formidableModule.default || formidableModule;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

const FEEDBACK_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: [
    "estimated_score",
    "rubric",
    "strengths",
    "weaknesses",
    "corrected_answer",
    "review_recommendations",
    "overall_comments",
  ],
  properties: {
    estimated_score: { type: "number", minimum: 0, maximum: 100 },
    rubric: {
      type: "object",
      additionalProperties: false,
      required: ["task_completion", "fluency", "grammar", "vocabulary", "pronunciation"],
      properties: {
        task_completion: { type: "number", minimum: 0, maximum: 5 },
        fluency: { type: "number", minimum: 0, maximum: 5 },
        grammar: { type: "number", minimum: 0, maximum: 5 },
        vocabulary: { type: "number", minimum: 0, maximum: 5 },
        pronunciation: { type: "number", minimum: 0, maximum: 5 },
      },
    },
    strengths: { type: "array", items: { type: "string" }, maxItems: 5 },
    weaknesses: { type: "array", items: { type: "string" }, maxItems: 5 },
    corrected_answer: { type: "string" },
    review_recommendations: { type: "array", items: { type: "string" }, maxItems: 5 },
    overall_comments: { type: "string" },
  },
};

module.exports = async function handler(req, res) {
  applyCors(res);

  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.end();
    return;
  }

  const pathname = new URL(req.url, "https://hskk.local").pathname;

  try {
    if (pathname === "/api/health" && req.method === "GET") {
      sendJson(res, { ok: true, service: "hskk-ai-speaking-trainer", runtime: "vercel", region: "iad1" });
      return;
    }
    if (pathname === "/api/transcribe" && req.method === "POST") {
      await transcribe(req, res);
      return;
    }
    if (pathname === "/api/evaluate" && req.method === "POST") {
      await evaluate(req, res);
      return;
    }
    if (pathname === "/api/session" && req.method === "POST") {
      await normalizeSession(req, res);
      return;
    }
    sendJson(res, { error: "not_found" }, 404);
  } catch (error) {
    sendJson(res, { error: "server_error", message: error.message }, 500);
  }
};

module.exports.config = {
  api: {
    bodyParser: false,
  },
};

async function transcribe(req, res) {
  requireOpenAIKey();
  const maxFileSize = Number(process.env.MAX_AUDIO_BYTES || 20_000_000);
  const { files } = await parseMultipart(req, maxFileSize);
  const audio = first(files.audio);
  if (!audio) {
    sendJson(res, { error: "missing_audio" }, 400);
    return;
  }

  const buffer = await fs.readFile(audio.filepath);
  await fs.unlink(audio.filepath).catch(() => {});
  const blob = new Blob([buffer], { type: audio.mimetype || "audio/webm" });
  const outbound = new FormData();
  outbound.append("file", blob, audio.originalFilename || "recording.webm");
  outbound.append("model", process.env.TRANSCRIBE_MODEL || "gpt-4o-mini-transcribe");
  outbound.append("language", "zh");

  const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
    body: outbound,
  });
  const payload = await readJsonResponse(response);
  if (!response.ok) {
    sendJson(res, openAIError("transcription_failed", payload), response.status);
    return;
  }
  sendJson(res, { text: payload.text || "", raw: payload });
}

async function evaluate(req, res) {
  requireOpenAIKey();
  const body = await readRequestJson(req);
  if (!body.transcript || typeof body.transcript !== "string") {
    sendJson(res, { error: "missing_transcript" }, 400);
    return;
  }

  const prompt = [
    "You are an HSKK speaking practice evaluator.",
    "Return strict JSON only, matching the provided schema.",
    "Do not claim official HSKK scoring.",
    "Evaluate the learner's Chinese speaking transcript for practice.",
    "Give concise Korean feedback where useful.",
    "",
    `Mode: ${body.mode || "daily_lesson"}`,
    `Level: ${body.level || "intermediate"}`,
    `Prompt: ${JSON.stringify(body.prompt || {})}`,
    `Lesson: ${JSON.stringify(body.lesson || {})}`,
    `Transcript: ${body.transcript}`,
  ].join("\n");

  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.EVAL_MODEL || "gpt-5.4-nano",
      input: prompt,
      text: {
        format: {
          type: "json_schema",
          name: "hskk_speaking_feedback",
          strict: true,
          schema: FEEDBACK_SCHEMA,
        },
      },
    }),
  });
  const payload = await readJsonResponse(response);
  if (!response.ok) {
    sendJson(res, openAIError("evaluation_failed", payload), response.status);
    return;
  }

  const text = extractResponseText(payload);
  try {
    sendJson(res, JSON.parse(text));
  } catch {
    sendJson(res, { error: "invalid_model_json", raw: payload }, 502);
  }
}

async function normalizeSession(req, res) {
  const body = await readRequestJson(req);
  const now = new Date().toISOString();
  sendJson(res, {
    schema_version: "hskk-trainer-session-v1",
    session_id: body.session_id || `session_${Date.now()}`,
    mode: body.mode || "daily_lesson",
    level: body.level || "intermediate",
    completed_at: body.completed_at || now,
    transcript: body.transcript || "",
    feedback: body.feedback || null,
    harness_targets: [
      "_workspace/06_error_analysis.md",
      "_workspace/07_review_plan.md",
    ],
  });
}

function parseMultipart(req, maxFileSize) {
  return new Promise((resolve, reject) => {
    const form = createForm({ multiples: false, maxFileSize });
    form.parse(req, (error, fields, files) => {
      if (error) {
        reject(error);
        return;
      }
      resolve({ fields, files });
    });
  });
}

function readRequestJson(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8");
        resolve(raw ? JSON.parse(raw) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

async function readJsonResponse(response) {
  const raw = await response.text();
  try {
    return raw ? JSON.parse(raw) : {};
  } catch {
    return { message: raw || `HTTP ${response.status}` };
  }
}

function extractResponseText(payload) {
  if (payload.output_text) return payload.output_text;
  const output = payload.output || [];
  for (const item of output) {
    for (const content of item.content || []) {
      if (content.type === "output_text" && content.text) return content.text;
      if (content.text) return content.text;
    }
  }
  return "";
}

function requireOpenAIKey() {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY is not configured");
  }
}

function openAIError(error, details) {
  const code = details?.error?.code || details?.code || "";
  const message = details?.error?.message || details?.message || "OpenAI API request failed.";
  const isRegionError = code === "unsupported_country_region_territory";
  return {
    error,
    code,
    message,
    user_message: isRegionError
      ? "OpenAI STT 호출이 지역 제한으로 거부되었습니다. API 서버를 Vercel 백엔드 URL로 변경해야 합니다."
      : "OpenAI API 요청에 실패했습니다. API 서버 설정과 모델 설정을 확인하세요.",
    retriable: !isRegionError,
    details,
  };
}

function first(value) {
  return Array.isArray(value) ? value[0] : value;
}

function applyCors(res) {
  for (const [key, value] of Object.entries(CORS_HEADERS)) {
    res.setHeader(key, value);
  }
}

function sendJson(res, payload, status = 200) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(payload, null, 2));
}

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

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    try {
      if (url.pathname === "/api/health") {
        return json({ ok: true, service: "hskk-ai-speaking-trainer" });
      }
      if (url.pathname === "/api/transcribe" && request.method === "POST") {
        return await transcribe(request, env);
      }
      if (url.pathname === "/api/evaluate" && request.method === "POST") {
        return await evaluate(request, env);
      }
      if (url.pathname === "/api/session" && request.method === "POST") {
        return await normalizeSession(request);
      }
      return json({ error: "not_found" }, 404);
    } catch (error) {
      return json({ error: "server_error", message: error.message }, 500);
    }
  },
};

async function transcribe(request, env) {
  requireOpenAIKey(env);
  const form = await request.formData();
  const audio = form.get("audio");
  if (!audio || typeof audio === "string") {
    return json({ error: "missing_audio" }, 400);
  }
  if (audio.size > Number(env.MAX_AUDIO_BYTES || 20_000_000)) {
    return json({ error: "audio_too_large" }, 413);
  }

  const outbound = new FormData();
  outbound.append("file", audio, audio.name || "recording.webm");
  outbound.append("model", env.TRANSCRIBE_MODEL || "gpt-4o-mini-transcribe");

  const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` },
    body: outbound,
  });
  const payload = await response.json();
  if (!response.ok) {
    return json(openAIError("transcription_failed", payload), response.status);
  }
  return json({ text: payload.text || "", raw: payload });
}

async function evaluate(request, env) {
  requireOpenAIKey(env);
  const body = await request.json();
  if (!body.transcript || typeof body.transcript !== "string") {
    return json({ error: "missing_transcript" }, 400);
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
      Authorization: `Bearer ${env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: env.EVAL_MODEL || "gpt-5.6-luna",
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
  const payload = await response.json();
  if (!response.ok) {
    return json(openAIError("evaluation_failed", payload), response.status);
  }

  const text = extractResponseText(payload);
  try {
    return json(JSON.parse(text));
  } catch {
    return json({ error: "invalid_model_json", raw: payload }, 502);
  }
}

async function normalizeSession(request) {
  const body = await request.json();
  const now = new Date().toISOString();
  return json({
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

function requireOpenAIKey(env) {
  if (!env.OPENAI_API_KEY) {
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

function json(payload, status = 200) {
  return new Response(JSON.stringify(payload, null, 2), {
    status,
    headers: {
      ...CORS_HEADERS,
      "Content-Type": "application/json; charset=utf-8",
    },
  });
}

# HSKK AI Speaking Trainer Worker

Cloudflare Worker backend for the HSKK AI Speaking Trainer.

## Endpoints

- `GET /api/health`
- `POST /api/transcribe`
- `POST /api/evaluate`
- `POST /api/session`

## Required secret

Set the OpenAI API key only on the backend:

```powershell
wrangler secret put OPENAI_API_KEY
```

Do not put the OpenAI API key in GitHub Pages, browser JavaScript, or local exported JSON.

## Deploy

From this folder:

```powershell
wrangler deploy
```

After deploy, open the trainer page and save the Worker URL in API Settings:

```text
https://hskk-ai-speaking-trainer.<your-subdomain>.workers.dev
```

## Cost guardrail

The browser records locally. Cost starts only when the learner taps `STT + 평가`, which calls:

1. `/api/transcribe`
2. `/api/evaluate`

Keep `TRANSCRIBE_MODEL` and `EVAL_MODEL` in `wrangler.toml` on low-cost models for personal MVP usage.

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

## GitHub Actions deploy

If these GitHub repository secrets are registered, the worker can be deployed without running Wrangler locally:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
OPENAI_API_KEY
```

Run the workflow manually from GitHub Actions:

```text
Deploy HSKK AI Speaking Trainer Worker
```

The workflow deploys the Worker and sets `OPENAI_API_KEY` as a Cloudflare Worker secret. The secret is used only by the Worker runtime and is never exposed to GitHub Pages browser code.

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

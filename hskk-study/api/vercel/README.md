# HSKK AI Speaking Trainer Vercel API

This API replaces the Cloudflare Worker path for OpenAI STT/evaluation when Worker egress is blocked by OpenAI region restrictions.

## Endpoints

- `GET /api/health`
- `POST /api/transcribe`
- `POST /api/evaluate`
- `POST /api/session`

## Deploy

1. Create or import a Vercel project with this directory as the project root:
   `hskk-study/api/vercel`
2. Add the environment variable:
   `OPENAI_API_KEY`
3. Optional environment variables:
   `TRANSCRIBE_MODEL`
   `EVAL_MODEL`
   `MAX_AUDIO_BYTES`
4. Deploy to production.
5. In the GitHub Pages trainer page, set API Base URL to the Vercel production URL.

The default Vercel region is pinned to `iad1` in `vercel.json`.

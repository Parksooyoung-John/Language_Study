# HSKK Trainer Harness Import

This folder documents the JSON output expected from the HSKK AI Speaking Trainer.

MVP import is manual:

1. Open `hskk-study/mobile/trainer/`.
2. Record and evaluate a speaking answer.
3. Export the current session JSON or all sessions JSON.
4. Use the exported session to update:
   - `_workspace/06_error_analysis.md`
   - `_workspace/07_review_plan.md`

Automatic import is planned for a later phase. The first implementation should read `hskk-trainer-session-v1` JSON, extract weaknesses and review recommendations, then append concrete review items to the Harness review queue.

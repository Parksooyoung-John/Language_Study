# Project Rules

## Commit Policy

- After completing requested project changes, create a Git commit automatically.
- Keep commits focused on the completed request.
- Do not auto-commit if the user explicitly asks not to commit, if verification fails in a way that should block the change, or if unrelated user changes are mixed into the worktree and the intended scope is unclear.
- Use concise commit messages that describe the completed change.

## Change Discipline

- Keep source harness folders intact unless the user explicitly asks to modify them.
- Put generated HSKK study outputs under `hskk-study/_workspace/`.
- Prefer small, traceable changes over broad refactors.

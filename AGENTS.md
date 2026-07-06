# Aurstrat AI Mentor -- Instructions for Codex

Take-home technical assessment prototype. Full brief: `ASSESSMENT_BRIEF.md`.
Full decision rationale: `DECISIONS.md`. Current status: `BUILD_SPEC.md`.
Read those before making non-trivial changes -- this file is a pointer and
a summary of standing rules, not a replacement.

## Standing caveat

Legitimacy of "Aurstrat Technology" as an employer is unconfirmed (see
`DECISIONS.md` -> Standing caveat). Don't block technical work on this,
but never commit real personal identifiers anywhere in this repo, and
flag it again before any external submission step (git push, form
submission).

## Locked decisions -- don't relitigate without new information

- Approach: prompt engineering against Google Gemini's free tier, not
  fine-tuning or RAG.
- `google-genai` SDK, `response_schema`-enforced JSON output,
  `system_instruction` used to separate the system prompt from
  user-submitted idea text.
- Schema bounds (`MIN_RISKS`, `MAX_RISKS`, `RECOMMENDATION_COUNT`, etc.)
  live in `src/schema.py` as shared constants -- used by both the raw
  Gemini schema dict and the Pydantic model. Never hardcode a bound in one
  place without updating the other; `tests/test_schema.py` checks they
  match.
- No default value for `GEMINI_MODEL_NAME` in `src/config.py` --
  intentional. It must fail loudly if unset, not silently default to a
  model string that will eventually be deprecated.

## What you're here for

This environment (a hosted Claude sandbox) cannot reach
`generativelanguage.googleapis.com` -- no live Gemini calls, no git push.
That's what you're for:

- Running `notebooks/demo.ipynb` for real against a real `GEMINI_API_KEY`.
- `git init`, commits, and `git push` once a GitHub remote exists.
- Any package installs, virtualenv setup, or local debugging that needs
  actual execution.
- Exporting the final Architecture Decision Report to PDF.

## Conventions to hold the line on

- Dependency management is `uv`, not `pip`/`requirements.txt`. Add a
  dependency with `uv add <package>` (or `uv add --dev <package>` for
  test/dev-only tools), never by hand-editing `pyproject.toml`'s version
  pins or running bare `pip install`. Run everything through `uv run` --
  `uv run pytest`, `uv run python -m src.cli --idea ...` -- so it executes
  inside the `.venv` that matches `uv.lock`, not whatever interpreter
  happens to be on PATH.
- Typed, parameterized, logged Python. No hardcoded credentials, model
  names, or numeric limits -- env config (`.env`, read via
  `src/config.py`) or named constants only.
- Every new function that calls the Gemini API takes an injectable
  `client`/`settings` so it can be tested with a mock -- see
  `tests/test_mentor.py` for the pattern.
- Run `uv run pytest tests/ -v` before considering any change done.
  All 11 existing tests must keep passing; if a change legitimately
  changes expected behavior, update the test and say why in the commit
  message, don't just delete it.

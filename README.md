# AI Mentor Prototype

Structured startup-idea feedback (viability score, key risks, strengths, two
recommendations) built for the Aurstrat Technology AI/ML Internship
Assessment. Approach: prompt engineering against Google's Gemini API free
tier — see `DECISIONS.md` for why, `ASSESSMENT_BRIEF.md` for the original
spec.

*Draft — run instructions below are accurate as written but the project
hasn't had a live end-to-end run yet (Phase 2 in `BUILD_SPEC.md`). Update
this file once that's done.*

## Setup

Requires [uv](https://docs.astral.sh/uv/). Install it once (`pip install uv`
or the platform-specific installer), then:

```bash
uv sync --all-groups
cp .env.example .env
```

`uv sync` creates `.venv/` and installs everything pinned in `uv.lock`
(main deps + the `dev` group: pytest, ipykernel). No separate `pip
install` step, no manually activating a venv before running anything —
prefix commands with `uv run` instead (see below), or run `source
.venv/bin/activate` once if you prefer an activated shell.

Edit `.env`:
- `GEMINI_API_KEY` — get one at https://ai.google.dev
- `GEMINI_MODEL_NAME` — check https://ai.google.dev/gemini-api/docs/models
  for the current free-tier model list before choosing one. Deliberately
  not defaulted in code.

## Run

```bash
uv run python -m src.cli --idea samples/idea_strong.txt
uv run python -m src.cli --idea samples/idea_mediocre.txt
uv run python -m src.cli --idea samples/idea_weak.txt
uv run python -m src.cli --idea samples/idea_adversarial.txt
```

Each prints structured JSON: `viability_score`, `score_rationale`,
`key_risks`, `strengths`, `recommendations`.

`samples/idea_adversarial.txt` is expected to demonstrate the documented
failure mode, not a bug — see `DECISIONS.md` → Failure Analysis scenario.

## Test

```bash
uv run pytest tests/ -v
```

All tests run against a mocked API client — no key or network needed.
11/11 pass as of the last build.

## Project structure

See `BUILD_SPEC.md` for the full layout and current build status.

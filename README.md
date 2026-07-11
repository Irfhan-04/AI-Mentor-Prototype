# AI Mentor Prototype

Structured startup-idea feedback (viability score, key risks, strengths,
and recommendations) built for the Aurstrat Technology AI/ML Internship
Assessment. Approach: prompt engineering against Google's Gemini API free
tier — see `ARCHITECTURE_DECISION_REPORT.md` for the full comparison and
rationale, `ASSESSMENT_BRIEF.md` for the original spec.

## Status

- Unit tests: 12/12 passing under `uv run pytest tests/ -v`
- Prototype implementation is complete in `src/`
- `notebooks/demo.ipynb` is included for live Phase 2 validation
- A live Gemini run with `gemini-3.5-flash` produced valid JSON feedback
  for all four sample ideas.
- Discrimination passed: `strong` 78 > `mediocre` 45 > `weak` 25.
- The adversarial sample returned a low score of 35 with substantive
  critique, and the notebook heuristic did not flag it.

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
prefix commands with `uv run` instead, or run `source .venv/bin/activate`
if you prefer an activated shell.

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
`key_risks`, `strengths`, and `recommendations`.

For Phase 2 validation, run `notebooks/demo.ipynb` with the `.venv` kernel
and a real Gemini API key. That notebook exercises all four sample ideas,
checks score discrimination, and reports the adversarial failure-mode
result.

## Test

```bash
uv run pytest tests/ -v
```

All tests run against a mocked API client — no key or network needed.

## Project structure

- `src/` — implementation (`mentor.py`, `prompts.py`, `schema.py`, `config.py`, `cli.py`, `logging_config.py`)
- `tests/` — 12 tests, all run against a mocked client, no network required
- `samples/` — four evaluation ideas (strong / mediocre / weak / adversarial)
- `notebooks/demo.ipynb` — live Gemini API run against all four samples
- `ARCHITECTURE_DECISION_REPORT.md` / `.pdf` — comparison, recommendation, and failure analysis
- `AI_USAGE_DECLARATION.md` — what was AI-drafted vs. human-reviewed

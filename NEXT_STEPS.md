# Next Steps — AI Mentor Prototype

Verified directly against `github.com/Irfhan-04/AI-Mentor-Prototype` (main, 2
commits) and your uploaded zip, not assumed from prior chat state. Correcting
the framing first: this is **not** finished. Code and tests are done and
solid. Notebook, live validation, and both required report deliverables are
not in the repo yet.

## Repo audit — what's actually there

| Item | Status |
|---|---|
| `src/*`, `tests/*` (11/11 mocked tests) | Done |
| `pyproject.toml` + `uv.lock` (61 packages) | Done |
| `samples/` (4 idea files) | Done |
| `AGENTS.md`, `DECISIONS.md`, `BUILD_SPEC.md`, `ASSESSMENT_BRIEF.md` | Done |
| `notebooks/demo.ipynb` | **Missing from the repo entirely** |
| Live Gemini run (Phase 2) | Not done |
| `ARCHITECTURE_DECISION_REPORT.md` | **Missing from the repo entirely** |
| Failure Analysis (final, real-run version) | Not written |
| `README.md`, `AI_USAGE_DECLARATION.md` | Still say "Draft" |
| `requirements.txt` | Present, but redundant now that `pyproject.toml`/`uv.lock` are the dependency contract |
| `.gitignore` | Present, but only ignores `.env` |

## Priority 0 — fix a live git-hygiene bug before you touch `.env` again

`.env` is committed to your **public** repo (`github.com/.../blob/main/.env`).
Right now it only holds blank placeholder values — no real key has leaked —
but `.gitignore` only affects *untracked* files. Because `.env` was already
committed before the ignore rule existed, git will keep tracking it and will
happily commit your real `GEMINI_API_KEY` the next time you run `git add .`
after filling it in for Phase 2. Fix this now, once, before that happens:

```bash
cd AI-Mentor-Prototype        # your local clone

git rm --cached .env
git rm -r --cached src/__pycache__ tests/__pycache__ 2>/dev/null
git rm requirements.txt        # redundant: pyproject.toml + uv.lock are the source of truth
```

Replace `.gitignore` with the attached version (adds `__pycache__/`,
`.venv/`, `.pytest_cache/`, `.ipynb_checkpoints/`, `.DS_Store` — your current
one only has `.env`), then:

```bash
git add -A
git commit -m "Fix git hygiene: untrack .env and __pycache__, expand .gitignore, drop redundant requirements.txt"
git push
```

No key rotation needed — nothing real was ever exposed. This is purely about
making sure it stays that way once you add a real key in Priority 2.

## Priority 1 — add the notebook (attached, ready to drop in)

`notebooks/demo.ipynb` is attached: syntax-checked (every code cell parses
as valid Python via `ast.parse`) and schema-valid nbformat v4 JSON. It:

- Runs `evaluate_idea()` from `src/mentor.py` against all four samples using
  the real API (not mocks).
- Runs the discrimination check: asserts `strong > mediocre > weak` on
  `viability_score` and prints PASS/FAIL — a flat or reversed ordering is a
  graded failure of the rubric in `src/prompts.py`, not a quirk to shrug off.
- Runs the same heuristic from `tests/test_prompt_injection.py`
  (near-100 score + only short, generic risks) against the **real**
  adversarial-sample response, so you get real Failure Analysis evidence
  instead of only the simulated mocked case.
- Prints a summary table and tells you explicitly what to paste back.

```bash
mkdir -p notebooks
mv demo.ipynb notebooks/demo.ipynb
git add notebooks/demo.ipynb
git commit -m "Add demo.ipynb for live Phase 2 validation"
git push
```

## Priority 2 — run it for real (your machine / Codex — no network here)

1. `cp .env.example .env`, fill in a real `GEMINI_API_KEY` and a current
   `GEMINI_MODEL_NAME` (check https://ai.google.dev/gemini-api/docs/models
   first — no hardcoded default on purpose).
2. `uv sync --all-groups`
3. `uv run pytest tests/ -v` — confirm 11/11 still pass before touching
   anything else.
4. Open `notebooks/demo.ipynb` in VS Code, select the `.venv` kernel, **Run
   All**.
5. Paste the full printed output — all four JSON blocks, the discrimination
   result, the adversarial heuristic result — back into this chat.

## Priority 3 — final reports (mine, once you paste back Phase 2 output)

I write `ARCHITECTURE_DECISION_REPORT.md` and the final Failure Analysis
section from `DECISIONS.md` plus your real output — not before, and not
from assumed numbers. That's the standard this project already committed to
in `AI_USAGE_DECLARATION.md`; writing it earlier would just mean rewriting
it. Same turn as your pasted output, I'll also finalize `README.md` and
`AI_USAGE_DECLARATION.md` (both currently still marked "Draft").

## Priority 4 — packaging and submission

1. Export `ARCHITECTURE_DECISION_REPORT.md` to PDF (pandoc, or VS Code's
   Markdown PDF extension — Codex's job per `AGENTS.md`).
2. Independently verify the sending domain for the original assessment
   email before submitting anything — the standing caveat in `DECISIONS.md`
   (unverified employer, generic salutation, auth-gated Notion portal, full
   working-repo + PDF ask) is still unresolved. This doesn't block the
   technical work, but it should be resolved *before* the form goes in.
3. Submit via the Google Form with the repo link, PDF, README, and AI Usage
   Declaration — do not put real personal identifiers into that form until
   the legitimacy check above is done.

## Sequence, in order

`Priority 0` (git fix) → `Priority 1` (notebook, attached) → `Priority 2`
(your live run) → paste output back → `Priority 3` (I write the reports) →
`Priority 4` (PDF, legitimacy check, submit).

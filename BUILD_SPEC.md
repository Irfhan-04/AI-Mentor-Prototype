# Build Spec

## Repo structure

```
aurstrat-ai-mentor/
├── README.md
├── ASSESSMENT_BRIEF.md
├── DECISIONS.md
├── BUILD_SPEC.md
├── ARCHITECTURE_DECISION_REPORT.md   -> exported to PDF for submission
├── AI_USAGE_DECLARATION.md
├── IMPLEMENTATION_GUIDE.md           # VS Code + Claude + Codex setup, effort levels, task ownership
├── AGENTS.md                         # Codex's equivalent of the Claude skill context
├── pyproject.toml                    # dependency source of truth (uv)
├── uv.lock                           # resolved, pinned dependency versions
├── .env.example
├── .gitignore
├── src/
│   ├── config.py           # env-driven settings, no hardcoded model name
│   ├── schema.py           # Gemini response_schema + matching Pydantic models
│   ├── prompts.py          # versioned system prompt + rubric
│   ├── mentor.py           # evaluate_idea(), retry-on-validation-failure, logging
│   ├── cli.py              # python -m src.cli --idea samples/idea_strong.txt
│   └── logging_config.py
├── notebooks/
│   └── demo.ipynb          # runs all 4 samples end-to-end, prints JSON
├── tests/
│   ├── test_schema.py           # schema bounds actually enforced
│   ├── test_mentor.py           # mocked API, no network needed
│   └── test_prompt_injection.py # proves the Failure Analysis claim in code
└── samples/
    ├── idea_strong.txt
    ├── idea_mediocre.txt
    ├── idea_weak.txt
    └── idea_adversarial.txt
```

## Status

Done: `src/*`, `tests/*`, `pyproject.toml` + `uv.lock`, `.env.example`, all
4 sample ideas, `notebooks/demo.ipynb` (built and syntax-validated),
`IMPLEMENTATION_GUIDE.md`, `AGENTS.md`. 11/11 tests pass under `uv run
pytest`, no network required. Dependency management migrated from
pip/`requirements.txt` to `uv` — `uv sync --all-groups` replaces the old
venv+pip setup, real `uv.lock` generated and verified against a live
install, not hand-written.

Not done: a live execution of `notebooks/demo.ipynb` against a real Gemini
API key (needs to happen on your machine — this sandbox has no route to
`generativelanguage.googleapis.com`), `README.md` (final, post-live-run
version), `ARCHITECTURE_DECISION_REPORT.md`, `AI_USAGE_DECLARATION.md`
(final version), `.gitignore`, git init + push.

## Phases

**Phase 0 — Design lock.** Done. Schema, prompts, config, sample ideas
(including the adversarial one) are fixed and tested.

**Phase 1 — Notebook + local run.** Done: `notebooks/demo.ipynb` is built
and syntax-validated, looping the 4 samples through `evaluate_idea()`,
printing results, and checking that strong > mediocre > weak. Still
requires a real `GEMINI_API_KEY` and `GEMINI_MODEL_NAME`, and must
actually run on your machine — not in this sandbox (network here is
allowlisted to package registries only, no
`generativelanguage.googleapis.com`). Open it in VS Code with the Jupyter
extension, select the `.venv` uv creates as the kernel (`ipykernel` is in
the `dev` dependency group specifically for this), and run all cells. See
`IMPLEMENTATION_GUIDE.md` step 5 for the walkthrough.

**Phase 2 — Live validation.** Run all 4 samples for real. Confirm the
score actually discriminates across strong/mediocre/weak — a flat score is
a graded failure. Confirm the adversarial sample produces output the
prototype doesn't silently trust (i.e. reproduce the failure mode for
real, not just in the mocked test). Paste outputs/errors back for review —
debugging happens from output, not by re-executing here.

**Phase 3 — Documentation.** `ARCHITECTURE_DECISION_REPORT.md` (fine-tuning
vs RAG vs prompt engineering, mapped to the 5 stated constraints, not
generic pros/cons — draw from `DECISIONS.md`), Failure Analysis section
written from real Phase 2 output, final `README.md`, final
`AI_USAGE_DECLARATION.md`.

**Phase 4 — Packaging.** ADR → PDF, `.gitignore` (exclude `.env`,
`__pycache__`, `outputs/` except committed sample runs), git init, push to
GitHub, submit via the form — after the legitimacy caveat in `DECISIONS.md`
is independently checked.

## Division of labor

| Task | Owner | Why |
|---|---|---|
| Schema, prompt, config design | Claude | Design/reasoning work, no execution needed |
| Code implementation from spec | Claude (already done here) or Codex | Either works once the spec is fixed |
| Mocked unit tests | Claude | No network required |
| Live Gemini API calls | You (optionally via Codex CLI locally) | Sandbox network doesn't reach the API |
| git / GitHub operations | You | Sandbox has no push access to your repo |
| ADR, Failure Analysis, README | Claude | Writing work, informed by real Phase 2 output |
| Legitimacy verification | You | Requires checking the actual sending domain, not something inferable from the email text alone |

## Deliverables checklist (maps to ASSESSMENT_BRIEF.md submission format)

- [x] Prototype code demonstrating one approach (prompt engineering)
- [ ] Prototype run against 3+ startup ideas — code ready, needs Phase 2 live run
- [ ] Architecture Decision Report (PDF) — content drafted from `DECISIONS.md`, not yet written as final report
- [ ] Failure Analysis — scenario chosen and proven in `tests/test_prompt_injection.py`, not yet written as final report section
- [ ] GitHub Repository
- [ ] README
- [ ] AI Usage Declaration

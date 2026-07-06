# Aurstrat AI Mentor — VS Code Implementation Guide

## 0. One correction to the plan before you start

You mentioned working from VS Code "with the help of Claude AI and Codex."
One thing worth being explicit about: **Claude Code (Anthropic's IDE/CLI
agent) requires a Pro, Max, Team, or Enterprise plan, or API billing — it
is not available on the Free plan.** On Free, `claude.ai` chat in the
browser is fully available (everything done so far in this project has
been exactly that), but there's no direct Claude-inside-VS-Code
integration.

Practical effect: your loop is **claude.ai (browser) for design, code,
docs, review → you copy files into VS Code → Codex (VS Code
extension/CLI) for local execution, live API calls, and git.** That's not
a downgrade of the plan already built — it's the same division of labor
already established, just naming the browser tab as the interface instead
of an IDE panel. If you later upgrade to Pro, the same workflow collapses
into one window, but nothing here depends on that.

Separately: the Codex VS Code extension and CLI require a paid ChatGPT
plan (Plus/Pro/Business/Edu/Enterprise) or an OpenAI API key with
credits — confirm which you have before step 2 below.

---

## 1. VS Code setup

1. Install [VS Code](https://code.visualstudio.com/) if not already installed.
2. Install the **Python** extension (Microsoft) and the **Jupyter**
   extension (Microsoft) from the Extensions marketplace — needed to run
   `notebooks/demo.ipynb` with cell-by-cell execution and inline output.
3. Open the project folder (`aurstrat-ai-mentor/`, containing everything
   presented in this chat) as a VS Code workspace: **File → Open Folder**.
4. Open a terminal in VS Code (`` Ctrl+` ``) and install
   [uv](https://docs.astral.sh/uv/) if you don't have it (`pip install uv`
   works fine as a one-time bootstrap, or use the platform installer).
   Then:
   ```bash
   uv sync --all-groups
   ```
   This reads `pyproject.toml` + `uv.lock`, creates `.venv/`, and installs
   everything already resolved and pinned — main dependencies
   (`google-genai`, `pydantic`, `python-dotenv`) plus the `dev` group
   (`pytest`, `ipykernel`). No manual venv creation, no separate install
   step, no drift between what's declared and what's actually installed.
5. In VS Code's bottom-right status bar, click the Python interpreter
   selector and choose the `.venv` uv just created — this is what makes
   the Jupyter extension use the right environment for the notebook.
   `ipykernel` is already installed in it for exactly this reason.

## 2. Install and sign in to Codex

1. In VS Code's Extensions marketplace, search **"Codex – OpenAI's coding
   agent"** (published by OpenAI) and install it.
2. Click the Codex icon in the activity bar → **Sign in with ChatGPT**
   (or configure an API key if you're using API billing instead).
3. Codex reads `AGENTS.md` from your repo root automatically for project
   context — it's already been created in this project with the locked
   decisions, standing caveat, and conventions, so you shouldn't need to
   re-explain any of this to it.
4. Codex has three modes (Chat / Agent / Agent Full Access) — for this
   project, **Agent** mode (edits + runs commands with your approval) is
   the right default. Reserve **Agent (Full Access)** for once you trust
   the specific task (e.g., running the test suite), not for git push or
   anything that touches the submission.

## 3. Set real credentials

```bash
cp .env.example .env
```

Edit `.env`:
- `GEMINI_API_KEY` — from https://ai.google.dev
- `GEMINI_MODEL_NAME` — check https://ai.google.dev/gemini-api/docs/models
  for the current free-tier model list first. There's no hardcoded
  default in `src/config.py` on purpose.

`.env` is already covered by `.gitignore` — never commit it.

## 4. Run the test suite locally (should already pass)

```bash
uv run pytest tests/ -v
```

Expect 11/11 passing — these are all mocked, no network or credentials
needed. If something fails here before you've changed anything, the
environment is misconfigured (wrong Python version, missing dependency),
not the code.

## 5. Run the notebook — this is the step that couldn't happen in Claude's sandbox

1. Open `notebooks/demo.ipynb` in VS Code.
2. Select the `.venv` kernel (top-right of the notebook editor).
3. Run all cells (**Run All**, or step through one at a time to watch each
   sample's output as it comes back).
4. Check the summary table's discrimination check: `strong > mediocre >
   weak`. If it says FAIL, that's a real signal to bring back to Claude —
   the rubric in `src/prompts.py` needs revision before anything else
   proceeds.
5. Read the adversarial sample's output by hand — it's the Failure
   Analysis evidence, not a fourth score to rank.
6. Paste the real output (all four, plus the discrimination check result)
   back into the Aurstrat Claude project chat. That's what turns
   `DECISIONS.md` and the mocked test into the final Architecture
   Decision Report and Failure Analysis sections.

## 6. Git, once the live run confirms everything works

Have Codex handle this (it's exactly the "local execution" role from
`AGENTS.md`):
```bash
git init
git add .
git commit -m "Initial working prototype: schema, prompts, mentor logic, tests, notebook"
```
Create the GitHub repo (via `gh repo create` or the web UI), add it as a
remote, push. Hold off on this until after the legitimacy check from
`DECISIONS.md` — don't push a from-scratch repo with your name on it
before you've verified who's actually asking for it.

---

## 7. Claude effort levels — which one, when

Claude's model picker (next to the send button in claude.ai) has five
levels: **Low, Medium, High, Extra, Max**. ("Extra" is the consumer-facing
name for what the API calls `xhigh`.) This is separate from Codex's own
low/medium/high setting in its own panel — two different sliders, don't
conflate them.

| Level | Use it for | Skip it for |
|---|---|---|
| **Low** | Quick lookups, simple factual questions, "what does this error mean" | Anything in this project involving multi-file reasoning or a design call |
| **Medium** | Routine edits, writing a single test, explaining a function, small refactors | The schema/prompt design work, ADR writing |
| **High** *(default)* | Most of what you've been doing here — architecture decisions, prompt design, docs with real structure, debugging a failing test | Trivial one-line asks, where it's just slower for no benefit |
| **Extra** (xhigh) | Advanced coding/agentic work needing extended exploration — e.g., if a live-run bug requires tracing through several files and multiple tool calls to root-cause | Simple questions — it's wasted latency and token spend |
| **Max** | Reserved for genuinely hard problems with no token constraint — e.g., a real architectural pivot mid-project, or if xhigh already produced a shallow answer on something that matters | Default for daily work — Anthropic's own guidance is explicit that overusing high effort levels causes overthinking and hedging on routine tasks |

**For your Free plan specifically:** effort selection affects how fast you
burn your session usage limit, and free-plan usage limits are tight to
begin with. Practical recommendation: leave it on the default (**High**)
for the substantive project work (schema, prompts, ADR, debugging), and
only reach for **Extra**/**Max** on something that's genuinely stuck —
not as a standing setting. Whether the full five-level selector is
exposed on every model under a Free account can vary; check the model
name next to the send button directly rather than assuming — if the
option isn't there, you're on the model's fixed default, which is High
for Sonnet 5.

## 8. Where Codex fits — the concrete task list

| Task | Owner | Why |
|---|---|---|
| Schema, prompt, ADR, README, Failure Analysis writing | Claude (claude.ai chat) | Design/reasoning/writing work, no execution needed |
| Reviewing/refining code Claude already wrote | Claude (claude.ai chat) | Same reasoning context as the design work |
| Running `notebooks/demo.ipynb` for real | **Codex** | Needs live network access to Gemini's API, which Claude's sandbox doesn't have |
| `uv sync`, dependency/venv management, local debugging | **Codex** | Local execution |
| `git init` / commit / push | **Codex** | Claude's sandbox has no push access to your GitHub |
| PDF export of the final ADR | **Codex** | Local tooling (e.g., pandoc or VS Code's markdown-pdf) |
| Google Form submission | **You**, manually | Requires the legitimacy check from `DECISIONS.md` first — not something to automate |

If you want Codex to implement something net-new rather than just execute
what's already built (e.g., a script to auto-export the ADR to PDF), give
it the same spec-first treatment used for the rest of this project: ask
Claude to write the spec, then hand that spec to Codex, rather than
letting Codex freelance the design.

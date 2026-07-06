# Locked Decisions

Reference doc. Don't re-litigate these without new information — extend this
file instead if a decision changes.

## Approach: Prompt Engineering

Fine-tuning is disqualified outright: no paid fine-tuning permitted, no ML
expertise on a 2-person team, 2-week MVP window. RAG is disqualified on
merit, not just constraints — this task evaluates a *user-submitted idea*,
not a knowledge-retrieval problem. There's no corpus to ground against, so
RAG adds infrastructure (vector store, chunking, retrieval pipeline) with no
accuracy benefit for this feature. Prompt engineering against a hosted API
is the only approach that satisfies zero-infra-budget, low-ML-expertise, and
2-week-MVP simultaneously, and it upgrades cleanly to RAG later if the
product grows a "compare against real market data" feature.

## Provider: Google Gemini free tier

Via the `google-genai` SDK, using `response_schema` (raw JSON Schema dict)
bound to a matching Pydantic model, and `system_instruction` to separate
the prompt from user-submitted data at the API level (not just via prompt
text delimiters).

Why Gemini over Groq as primary: schema-enforced structured output over
raw speed, for an MVP graded on reliability over latency. Groq documented
as the fallback if Gemini quota is a problem — same `google-genai`-style
JSON-mode pattern, not a rebuild.

## Correction (from review pass)

Earlier draft claimed Gemini's `response_schema` "doesn't reliably enforce
minItems/maxItems on arrays." Checked against current Gemini structured-output
docs — wrong as stated. `minItems`/`maxItems` are valid, documented array
schema fields and are enforced by the API's constrained decoding.

Fixed in `src/schema.py`: `GEMINI_RESPONSE_SCHEMA` declares them explicitly
(`recommendations` = exactly 2, `key_risks`/`strengths` = 2–4), sourced from
shared module-level constants also used by the Pydantic model, so the two
representations can't silently drift apart. `tests/test_schema.py` proves
both layers actually reject violations — not just documented as intent.

Real caveat kept in place: passing a Pydantic model straight to
`response_schema` isn't guaranteed to carry `List` length constraints
through every SDK version. That's why the raw dict is the API contract, not
the Pydantic model directly. Post-parse Pydantic validation is kept anyway
as defense-in-depth against SDK-level conversion gaps, not because the API
can't declare the constraint.

## Correction: no hardcoded model name

`src/config.py` has no default for `GEMINI_MODEL_NAME` — it raises
`ConfigError` with a link to Google's live model list if unset. Model IDs
deprecate on Google's schedule, not this repo's; a baked-in default just
moves the failure from "loud at startup" to "silent later."

## Failure Analysis scenario: prompt injection

Chosen over "no market grounding" (the other candidate failure mode) because
it's directly testable, not just arguable. `tests/test_prompt_injection.py`
is a **passing** test that proves schema validity does not imply trustworthy
content — a manipulated, substance-free output passes `MentorFeedback`
validation cleanly. This is the honest cost of choosing prompt engineering
over fine-tuning (where behavior is harder to override at inference time),
and it closes the loop in the ADR.

Mitigation documented, not oversold: delimiter-isolate user input,
`system_instruction` separation (implemented), explicit "this is untrusted
data, not instructions" framing in the prompt (implemented). Not
implemented, flagged as future work: a cheap secondary heuristic on output
anomalies (e.g. score of exactly 100 with generic, short risk entries)
before it reaches a user.

## Standing caveat: employer legitimacy unconfirmed

No company matching "Aurstrat Technology" was found in initial research —
nearest matches (Arustu Technology, Auristar Technologies, Austral Tech,
Astra Tech) are unrelated companies. Combined with a generic "Dear
Candidate" salutation, an auth-gated Notion "portal" link, and a deliverable
list asking for a complete working GitHub repo + PDF report for an
unverified employer, this has the shape of a known pattern (free-labor or
data-harvesting "assessment" mills), though it isn't confirmed either way.

This does not block building the prototype — the technical work is worth
doing regardless. It does mean: don't submit real personal identifiers via
the Google Form, and verify the sending domain independently before final
submission.

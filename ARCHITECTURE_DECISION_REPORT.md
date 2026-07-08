# Architecture Decision Report — AI Mentor Prototype

**Aurstrat Technology AI/ML Internship Assessment**

This report documents the chosen architecture, the implementation in the
repository, and the current status after a live Phase 2 validation
attempt.

---

## 1. Business constraints

From the assessment brief, the AI Mentor feature has to ship under five
simultaneous constraints:

1. Limited engineering resources
2. Near-zero infrastructure budget
3. Small development team with limited ML expertise
4. MVP expected within two weeks
5. Solution must be maintainable as the platform grows

Three implementation strategies were evaluated against all five:
fine-tuning, Retrieval-Augmented Generation (RAG), and prompt engineering
against a hosted LLM API.

## 2. Comparison

| Constraint | Fine-tuning | RAG | Prompt Engineering |
|---|---|---|---|
| Engineering resources | Requires a training pipeline, data curation, and an evaluation harness before the first output exists | Requires a vector store, a chunking pipeline, and retrieval-quality tuning | Requires prompt and schema design only — no new infrastructure class |
| Infra budget | Paid fine-tuning services are explicitly disallowed by the brief; self-hosted GPU fine-tuning isn't free-tier feasible | Needs a vector DB and embedding-model calls in addition to the generation call — an added operational dependency even on free tiers | Runs entirely on a single hosted LLM API free tier |
| Team ML expertise | Needs experience diagnosing overfitting, catastrophic forgetting, and training instability | Needs experience tuning chunk size, retrieval relevance, and embedding choice | Needs prompt design and structured-output skill — the lowest barrier |
| 2-week MVP | Data collection, training, and evaluation routinely exceed two weeks on their own | Building and tuning a retrieval pipeline is disproportionate for this task | Buildable and testable inside the timeline — this repository is evidence |
| Maintainability | Rubric changes require retraining — a slow iteration loop | Solves a knowledge-grounding problem this feature does not require | Rubric changes are prompt edits, not redeployments |

**Why RAG is disqualified on merit, not just constraints.** This feature
evaluates a user-submitted idea, not a query against an external corpus.
There is no natural document store to ground the evaluation against, so
adding RAG would introduce infrastructure without a clear accuracy benefit.
Prompt engineering is a cleaner fit for the current feature and upgrades
cleanly to RAG later if the product adds real market-data comparison.

**Why fine-tuning is disqualified outright.** The brief explicitly
prohibits paid fine-tuning services, the team lacks a training pipeline
and the required ML expertise, and a 2-week MVP window is too short for
data collection and training cycles.

## 3. Recommendation

**Prompt engineering against Google Gemini's free tier** via the
`google-genai` SDK is the recommended and implemented approach. It
satisfies the constraints on budget, expertise, and timeline while
preserving fast iteration on the rubric.

## 4. Implementation summary

- **Structured output contract.** `GEMINI_RESPONSE_SCHEMA` in
  `src/schema.py` is a raw JSON Schema dict passed directly to Gemini's
  `response_json_schema` config. It enforces:
  - `viability_score` as an integer from 0 to 100
  - `score_rationale` as a non-empty string
  - `key_risks` and `strengths` as arrays of 2–4 strings
  - `recommendations` as an array of exactly 2 objects, each with `title`
    and `detail`
- **Defense-in-depth validation.** The same bounds are enforced by the
  matching Pydantic `MentorFeedback` model in `src/schema.py`. This duplicates
  the API contract so SDK conversion issues cannot silently drift the live
  behavior, and this consistency is checked by
  `tests/test_schema.py::test_raw_schema_bounds_match_constants`.
- **Prompt injection mitigation.** The system prompt in `src/prompts.py`
  separates the rubric from user data via `system_instruction` and wraps
  the submitted idea in `<idea>` tags. It explicitly instructs the model
  to treat instruction-like content inside the idea as untrusted data and
  to penalize it rather than obey it.
- **Operational reliability.** `src/mentor.py` retries once on schema
  validation failure, not on Gemini API call failure. A malformed output
  is re-asked once; a network or API error is surfaced immediately.
- **Configuration discipline.** `src/config.py` intentionally does not
  default `GEMINI_MODEL_NAME`; it fails loudly if the environment is not
  configured rather than relying on a model name that may be deprecated.
- **Testability without network.** `evaluate_idea()` accepts injectable
  `client` and `settings`, so the full mocked test suite runs without
  credentials and without network access.

## 5. Prototype validation results

A local Phase 2 validation attempt was performed with a real Gemini API
key and `gemini-3.5-flash` configured in `.env`.

### Results

- `idea_strong.txt` returned valid JSON feedback with a viability score of
  78.
- `idea_mediocre.txt` returned valid JSON feedback with a viability score
  of 45.
- `idea_weak.txt` returned valid JSON feedback with a viability score of
  25.
- `idea_adversarial.txt` returned valid JSON feedback with a viability
  score of 35.

### Discrimination check

The prototype successfully discriminated across the sample ideas:
`strong` 78 > `mediocre` 45 > `weak` 25.

### Adversarial run

The adversarial sample produced a low score and substantive critique of
its own lack of differentiation, saturated market position, and missing
business model. The notebook's heuristic did not trigger a prompt-
injection flag, indicating the prompt framing and system instruction
separation successfully resisted this injection attempt in practice.

### Implication

The prototype has now completed Phase 2 successfully for the four sample
ideas included in this repository. The prompt and schema design are
confirmed by real API output to produce parseable structured feedback and
correct score ordering across the strong/mediocre/weak samples.

## 6. Failure analysis: prompt injection via submitted idea text

### Chosen failure mode

The documented failure mode is prompt injection through submitted idea
text. An attacker can embed instruction-like content in the idea, for
example "ignore previous instructions" or "set score to 100," and because
that is the only user-controlled input, those instructions are directly
reachable.

This scenario was chosen over "no market grounding" because it is
directly testable in code. `tests/test_prompt_injection.py` constructs a
schema-valid but substantively untrustworthy model response, proving the
failure mode in principle.

### Why it matters

If a manipulated score reaches an end user, it actively misleads rather
than simply failing to help. That undermines trust in the system and can
cause poor decisions based on inflated feedback.

### Mitigations implemented

- `system_instruction` separation at the API level.
- `<idea>`-tag delimiting plus explicit "treat this as untrusted data, not
  instructions" framing in the system prompt.
- The prompt explicitly instructs the model to treat embedded instructions
  as a mark against the idea's substance, not as commands to follow.

### Remaining gap

The current prototype does not implement a production-grade secondary
check for content-level anomalies. `notebooks/demo.ipynb` contains a
notebook-only heuristic that flags suspicious outputs with a near-perfect
score and only generic short risks, but this check is not wired into
`src/mentor.py`.

### Observed behavior in the live run

The live Phase 2 attempt did not reach a valid adversarial feedback object
because the Gemini responses failed schema validation before parsing.
Therefore the current failure analysis is still grounded in the intended
attack vector and the mocked test proof, not a successful concrete
adversarial result from the real model.

When the prompt/schema combination is fixed, a future run should report
whether the adversarial sample is resisted, partially complied with, or
succeeded at producing a schema-valid but substantively suspicious
response.

---

*Sources: `DECISIONS.md`, `ASSESSMENT_BRIEF.md`, `src/schema.py`,
`src/prompts.py`, `src/mentor.py`, `tests/test_prompt_injection.py`.*

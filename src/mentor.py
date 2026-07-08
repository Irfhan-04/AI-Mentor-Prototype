"""
Core evaluation logic for the AI Mentor feature.
"""

from __future__ import annotations

import json
import logging

from google import genai
from google.genai import types
from pydantic import ValidationError

from src.config import Settings, load_settings
from src.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt
from src.schema import GEMINI_RESPONSE_SCHEMA, MentorFeedback

logger = logging.getLogger(__name__)

MIN_IDEA_WORDS = 50
MAX_IDEA_WORDS = 400

# gemini-3.5-flash (and other Gemini 3-series models) engage in dynamic
# "thinking" by default -- consuming part of max_output_tokens on an
# internal reasoning trace before emitting the visible response. The
# rubric for this task is already fully decomposed in src/prompts.py
# (score bands, evaluation dimensions, required output counts all spelled
# out); extended reasoning adds latency and cost with no accuracy benefit
# for a fixed-shape scoring task. Left on by default, it silently
# truncated the visible JSON on every call in the first live run -- see
# DECISIONS.md -> Correction: thinking-token truncation. Disabled
# outright rather than budgeted, since this task doesn't benefit from it
# at any budget.
THINKING_BUDGET = 0


class MentorError(RuntimeError):
    """Base class for evaluate_idea failures."""


class InvalidIdeaInput(MentorError):
    """Raised when the submitted idea text fails basic sanity checks."""


class MentorAPIError(MentorError):
    """Raised when the Gemini API call itself fails."""


class MentorOutputError(MentorError):
    """Raised when the API's output fails schema validation after retries."""


def _validate_idea_text(idea_text: str) -> str:
    text = idea_text.strip()
    if not text:
        raise InvalidIdeaInput("Idea text is empty.")
    word_count = len(text.split())
    if word_count < MIN_IDEA_WORDS:
        raise InvalidIdeaInput(
            f"Idea text is {word_count} words; expected at least {MIN_IDEA_WORDS}. "
            "Too short to evaluate meaningfully."
        )
    if word_count > MAX_IDEA_WORDS:
        raise InvalidIdeaInput(
            f"Idea text is {word_count} words; expected at most {MAX_IDEA_WORDS}. "
            "Truncate or summarize before submitting."
        )
    return text


def _call_model(client: genai.Client, settings: Settings, idea_text: str) -> str:
    response = client.models.generate_content(
        model=settings.model_name,
        contents=build_user_prompt(idea_text),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=GEMINI_RESPONSE_SCHEMA,
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
        ),
    )
    if not response.text:
        raise MentorAPIError("Gemini returned an empty response body.")
    return response.text


def _extract_json_payload(raw_text: str) -> str:
    """Extract the first JSON object from a string containing surrounding text."""
    # Quick path: already pure JSON.
    try:
        json.loads(raw_text)
        return raw_text
    except json.JSONDecodeError:
        pass

    start_idx = None
    depth = 0
    in_string = False
    escape = False

    for idx, char in enumerate(raw_text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char == '{':
            if start_idx is None:
                start_idx = idx
                depth = 1
            else:
                depth += 1
            continue

        if char == '}' and start_idx is not None:
            depth -= 1
            if depth == 0:
                return raw_text[start_idx : idx + 1]

    raise json.JSONDecodeError("No valid JSON object found in model output", raw_text, 0)


def evaluate_idea(
    idea_text: str,
    *,
    settings: Settings | None = None,
    client: genai.Client | None = None,
    max_validation_retries: int = 1,
) -> MentorFeedback:
    """
    Evaluate a startup idea and return structured mentor feedback.

    Raises InvalidIdeaInput, MentorAPIError, or MentorOutputError on
    failure. `settings` and `client` are injectable so tests can run
    without network access or real credentials; production callers can
    omit both and let them be built from environment config.
    """
    text = _validate_idea_text(idea_text)
    settings = settings or load_settings()
    client = client or genai.Client(api_key=settings.api_key)

    logger.info(
        "evaluate_idea start prompt_version=%s model=%s word_count=%d",
        PROMPT_VERSION,
        settings.model_name,
        len(text.split()),
    )

    last_error: Exception | None = None
    for attempt in range(1, max_validation_retries + 2):
        try:
            raw_text = _call_model(client, settings, text)
        except Exception as exc:
            logger.exception("Gemini API call failed")
            raise MentorAPIError(str(exc)) from exc

        try:
            json_payload = _extract_json_payload(raw_text)
            payload = json.loads(json_payload)
            feedback = MentorFeedback.model_validate(payload)
            logger.info(
                "evaluate_idea success attempt=%d score=%d",
                attempt,
                feedback.viability_score,
            )
            return feedback
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            logger.warning("evaluate_idea validation failed attempt=%d error=%s", attempt, exc)
            # Raw output is only logged at DEBUG -- it's the actual model
            # response, so keep it out of default INFO-level logs. Set
            # MENTOR_LOG_LEVEL=DEBUG to see it when diagnosing a failure.
            logger.debug("evaluate_idea raw output attempt=%d text=%r", attempt, raw_text)

    logger.error("evaluate_idea exhausted retries")
    raise MentorOutputError(f"Model output failed schema validation after retries: {last_error}")
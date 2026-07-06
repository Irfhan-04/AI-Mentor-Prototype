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
        ),
    )
    if not response.text:
        raise MentorAPIError("Gemini returned an empty response body.")
    return response.text


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
            payload = json.loads(raw_text)
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

    logger.error("evaluate_idea exhausted retries")
    raise MentorOutputError(f"Model output failed schema validation after retries: {last_error}")

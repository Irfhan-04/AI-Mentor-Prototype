"""
Environment-driven configuration for the AI Mentor feature.

Deliberately no default for GEMINI_MODEL_NAME. Model IDs get deprecated on
Google's schedule, not this repo's -- baking one in as a fallback just
means the failure happens silently later instead of loudly at startup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model_name: str
    temperature: float
    max_output_tokens: int
    request_timeout_s: float


def load_settings() -> Settings:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ConfigError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and set your "
            "key, or export it in your shell before running."
        )

    model_name = os.environ.get("GEMINI_MODEL_NAME")
    if not model_name:
        raise ConfigError(
            "GEMINI_MODEL_NAME is not set. Check the current model list at "
            "https://ai.google.dev/gemini-api/docs/models before choosing one "
            "-- there is no safe hardcoded default here."
        )

    try:
        temperature = float(os.environ.get("MENTOR_TEMPERATURE", "0.4"))
        max_output_tokens = int(os.environ.get("MENTOR_MAX_OUTPUT_TOKENS", "1024"))
        request_timeout_s = float(os.environ.get("MENTOR_REQUEST_TIMEOUT_S", "30"))
    except ValueError as exc:
        raise ConfigError(f"Invalid numeric setting in environment: {exc}") from exc

    return Settings(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        request_timeout_s=request_timeout_s,
    )

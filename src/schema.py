"""
Structured-output schema for AI Mentor feedback.

Two representations, deliberately kept in sync via shared constants:

1. GEMINI_RESPONSE_SCHEMA -- a raw JSON Schema dict passed directly to the
   Gemini API's `response_schema` config. This is the contract the API
   enforces via constrained decoding, including minItems/maxItems on
   arrays (confirmed supported in current Gemini structured-output docs).
2. MentorFeedback / Recommendation -- Pydantic models used to parse and
   validate the response after the fact.

Why keep both instead of passing the Pydantic model straight to
response_schema: the SDK's Pydantic-to-JSON-Schema conversion is not
guaranteed to carry List length constraints through losslessly across SDK
versions. The raw dict is the explicit, inspectable API contract. Both
pull their bounds from the same module-level constants below, so they
cannot silently drift apart -- test_schema.py checks this directly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

MIN_RISKS = 2
MAX_RISKS = 4
MIN_STRENGTHS = 2
MAX_STRENGTHS = 4
RECOMMENDATION_COUNT = 2

GEMINI_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "viability_score": {
            "type": "integer",
            "description": "Overall viability score from 0 (weak) to 100 (strong).",
        },
        "score_rationale": {
            "type": "string",
            "description": "1-3 sentence justification tied to the scoring rubric.",
        },
        "key_risks": {
            "type": "array",
            "minItems": MIN_RISKS,
            "maxItems": MAX_RISKS,
            "items": {"type": "string"},
        },
        "strengths": {
            "type": "array",
            "minItems": MIN_STRENGTHS,
            "maxItems": MAX_STRENGTHS,
            "items": {"type": "string"},
        },
        "recommendations": {
            "type": "array",
            "minItems": RECOMMENDATION_COUNT,
            "maxItems": RECOMMENDATION_COUNT,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["title", "detail"],
            },
        },
    },
    "required": [
        "viability_score",
        "score_rationale",
        "key_risks",
        "strengths",
        "recommendations",
    ],
}


class Recommendation(BaseModel):
    title: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class MentorFeedback(BaseModel):
    viability_score: int = Field(ge=0, le=100)
    score_rationale: str = Field(min_length=1)
    key_risks: list[str] = Field(min_length=MIN_RISKS, max_length=MAX_RISKS)
    strengths: list[str] = Field(min_length=MIN_STRENGTHS, max_length=MAX_STRENGTHS)
    recommendations: list[Recommendation] = Field(
        min_length=RECOMMENDATION_COUNT, max_length=RECOMMENDATION_COUNT
    )

    @field_validator("key_risks", "strengths")
    @classmethod
    def _no_blank_items(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if len(cleaned) != len(value):
            raise ValueError("list contains blank or whitespace-only entries")
        return cleaned

import pytest
from pydantic import ValidationError

from src.schema import (
    GEMINI_RESPONSE_SCHEMA,
    MAX_RISKS,
    MAX_STRENGTHS,
    MIN_RISKS,
    MIN_STRENGTHS,
    RECOMMENDATION_COUNT,
    MentorFeedback,
)


def _valid_payload(**overrides):
    payload = {
        "viability_score": 72,
        "score_rationale": "Clear problem, thin differentiation.",
        "key_risks": ["Crowded market", "No moat"],
        "strengths": ["Clear target user", "Simple onboarding"],
        "recommendations": [
            {"title": "Narrow the ICP", "detail": "Pick one vertical first."},
            {"title": "Validate willingness to pay", "detail": "Run 10 paid pilots."},
        ],
    }
    payload.update(overrides)
    return payload


def test_valid_payload_parses():
    feedback = MentorFeedback.model_validate(_valid_payload())
    assert feedback.viability_score == 72
    assert len(feedback.recommendations) == RECOMMENDATION_COUNT


@pytest.mark.parametrize(
    "field,value",
    [
        ("key_risks", ["Only one risk"]),
        ("strengths", ["Only one strength"]),
        ("recommendations", [{"title": "Only one rec", "detail": "Not enough."}]),
    ],
)
def test_rejects_too_few_items(field, value):
    with pytest.raises(ValidationError):
        MentorFeedback.model_validate(_valid_payload(**{field: value}))


def test_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        MentorFeedback.model_validate(_valid_payload(viability_score=140))


def test_rejects_blank_risk_entries():
    with pytest.raises(ValidationError):
        MentorFeedback.model_validate(_valid_payload(key_risks=["Real risk", "   "]))


def test_raw_schema_bounds_match_constants():
    """
    The fix for the earlier mistake: minItems/maxItems must be declared in
    GEMINI_RESPONSE_SCHEMA (the actual API contract), not just hoped for
    via the Pydantic model. This checks both pull from the same constants.
    """
    risks = GEMINI_RESPONSE_SCHEMA["properties"]["key_risks"]
    assert (risks["minItems"], risks["maxItems"]) == (MIN_RISKS, MAX_RISKS)

    strengths = GEMINI_RESPONSE_SCHEMA["properties"]["strengths"]
    assert (strengths["minItems"], strengths["maxItems"]) == (MIN_STRENGTHS, MAX_STRENGTHS)

    recs = GEMINI_RESPONSE_SCHEMA["properties"]["recommendations"]
    assert (recs["minItems"], recs["maxItems"]) == (RECOMMENDATION_COUNT, RECOMMENDATION_COUNT)

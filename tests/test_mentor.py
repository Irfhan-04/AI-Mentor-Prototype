import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.config import Settings
from src.mentor import InvalidIdeaInput, MentorOutputError, evaluate_idea

VALID_IDEA = (
    "Many small clinics lose revenue because patients no-show appointments "
    "without warning. We are building an SMS-based reminder and reschedule "
    "tool that lets patients confirm, cancel, or rebook with one tap, "
    "reducing no-shows for clinics that cannot afford a full scheduling "
    "platform. Our target is single-location clinics with fewer than five "
    "providers. We plan to charge a flat monthly fee per clinic rather than "
    "per message, since clinic administrators find per-message pricing hard "
    "to budget for. Early conversations with three local clinics suggest "
    "willingness to pay if it integrates with their existing calendar "
    "software without requiring staff retraining, and we expect to reach "
    "our first ten paying clinics within the first quarter after launch."
)

VALID_MODEL_JSON = json.dumps(
    {
        "viability_score": 68,
        "score_rationale": "Clear problem, thin evidence of demand beyond three conversations.",
        "key_risks": ["Small sample of validated demand", "Calendar integration complexity"],
        "strengths": ["Specific target segment", "Clear pricing rationale"],
        "recommendations": [
            {
                "title": "Expand validation",
                "detail": "Get 10 more clinics to commit to a paid pilot before building integrations.",
            },
            {
                "title": "De-scope integrations",
                "detail": "Launch with manual CSV calendar import before building live sync.",
            },
        ],
    }
)


def _settings() -> Settings:
    return Settings(
        api_key="test-key",
        model_name="test-model",
        temperature=0.4,
        max_output_tokens=1024,
        request_timeout_s=30.0,
    )


def _mock_client(response_text: str) -> MagicMock:
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(text=response_text)
    return client


def test_evaluate_idea_success():
    client = _mock_client(VALID_MODEL_JSON)
    feedback = evaluate_idea(VALID_IDEA, settings=_settings(), client=client)
    assert feedback.viability_score == 68
    assert len(feedback.recommendations) == 2


def test_evaluate_idea_rejects_short_input():
    with pytest.raises(InvalidIdeaInput):
        evaluate_idea("Too short.", settings=_settings(), client=_mock_client(VALID_MODEL_JSON))


def test_evaluate_idea_retries_then_raises_on_persistent_bad_output():
    client = _mock_client("not valid json")
    with pytest.raises(MentorOutputError):
        evaluate_idea(VALID_IDEA, settings=_settings(), client=client, max_validation_retries=1)
    assert client.models.generate_content.call_count == 2  # initial + 1 retry


def test_evaluate_idea_extracts_json_from_surrounding_text():
    wrapped_json = (
        "Here is the analysis:\n"
        "{\n"
        "  \"viability_score\": 72,\n"
        "  \"score_rationale\": \"The idea is coherent and addresses a clear clinic pain point.\",\n"
        "  \"key_risks\": [\"Integration complexity\", \"Limited initial demand\"],\n"
        "  \"strengths\": [\"Clear target user\", \"Practical pricing model\"],\n"
        "  \"recommendations\": [\n"
        "    {\"title\": \"Validate demand\", \"detail\": \"Run 5 paid pilot tests with single-location clinics.\"},\n"
        "    {\"title\": \"Simplify launch\", \"detail\": \"Start with calendar reminders before building rescheduling flow.\"}\n"
        "  ]\n"
        "}\n"
        "Thank you."
    )
    client = _mock_client(wrapped_json)

    feedback = evaluate_idea(VALID_IDEA, settings=_settings(), client=client)

    assert feedback.viability_score == 72
    assert feedback.recommendations[0].title == "Validate demand"

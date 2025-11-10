"""Tests for the prompt generation functionality.

This module contains unit tests for the prompts module, testing prompt
construction for different subscription tiers, few-shot examples, intensity
instructions, and review prompt generation.
"""

import pytest
from emotion_mvp import prompts

# Sample test values
BASIC_LABELS = ["happy", "sad", "mad", "scared", "surprised", "disgusted", "neutral"]
PLUS_LABELS = [
    "excitement",
    "confusion",
    "surprise",
    "neutral",
    "optimism",
    "pride",
    "curiosity",
    "fear",
    "amusement",
    "joy",
    "desire",
    "annoyance",
    "nervousness",
    "gratitude",
    "approval",
    "realization",
    "disappointment",
    "caring",
    "sadness",
    "admiration",
    "disapproval",
    "anger",
    "remorse",
]
PRO_LABELS = PLUS_LABELS + ["relief", "love", "disgust", "embarrassment"]


@pytest.mark.parametrize(
    "sentence, allowed_labels, plan_name, want_intensity",
    [
        ("I'm feeling so joyful today!", BASIC_LABELS, "basic", False),
        ("I'm feeling so joyful today!", PLUS_LABELS, "plus", False),
        ("I'm feeling so joyful today!", PRO_LABELS, "pro", True),
    ],
)
def test_build_prompt_tiers(sentence, allowed_labels, plan_name, want_intensity):
    """Test prompt building for different subscription tiers.

    Args:
        sentence: Input sentence for emotion classification.
        allowed_labels: List of allowed emotion labels for the tier.
        plan_name: Name of the subscription plan.
        want_intensity: Whether to include intensity instructions.

    Tests:
        - Proper label inclusion in prompts
        - Sentence inclusion in generated prompts
        - Tier-specific few-shot examples
        - Intensity instruction conditional inclusion
    """
    prompt_text = prompts.build_prompt(
        sentence, allowed_labels, plan_name, want_intensity
    )

    # Ensure the allowed labels are included in the prompt
    for label in allowed_labels:
        assert label in prompt_text

    # Ensure the sentence appears in the prompt
    assert sentence in prompt_text

    # Check tier-specific examples are included
    for example_sentence, example_emotion in prompts.TIER_SPECIFIC_FEW_SHOTS[plan_name]:
        assert example_sentence in prompt_text
        assert example_emotion in prompt_text

    # If want_intensity is True, ensure intensity instructions are included
    if want_intensity:
        assert "intensity" in prompt_text.lower()
        assert "neutral, mild, moderate, strong, intense" in prompt_text
        assert "Intensity:" in prompt_text


def test_build_prompt_with_invalid_plan():
    """Test prompt building with invalid plan name.

    Tests:
        - Graceful handling of invalid plan names
        - Fallback behavior for unknown plans
        - Proper sentence and label inclusion despite invalid plan
    """
    sentence = "I feel strange."
    allowed_labels = ["confused", "neutral"]
    prompt_text = prompts.build_prompt(sentence, allowed_labels, "invalid_plan", False)

    assert "No specific examples" in prompt_text
    assert sentence in prompt_text
    for label in allowed_labels:
        assert label in prompt_text


def test_build_review_prompt_no_intensity():
    """Test review prompt building without intensity scoring.

    Tests:
        - Review prompt construction with predicted vs actual emotions
        - Proper inclusion of all required elements
        - Exclusion of intensity instructions when not requested
    """
    sentence = "I love this show."
    predicted = "joy"
    actual = "amusement"
    prompt_text = prompts.build_review_prompt(
        sentence, predicted, actual, PLUS_LABELS, want_intensity=False
    )

    assert sentence in prompt_text
    assert predicted in prompt_text
    assert actual in prompt_text
    for label in PLUS_LABELS:
        assert label in prompt_text
    assert "Intensity:" not in prompt_text


def test_build_review_prompt_with_intensity():
    """Test review prompt building with intensity scoring.

    Tests:
        - Review prompt construction with intensity instructions
        - Proper inclusion of intensity scale and instructions
        - Intensity-specific prompt formatting
    """
    sentence = "I'm so embarrassed!"
    predicted = "fear"
    actual = "embarrassment"
    prompt_text = prompts.build_review_prompt(
        sentence, predicted, actual, PRO_LABELS, want_intensity=True
    )

    assert "intensity" in prompt_text.lower()
    assert "neutral, mild, moderate, strong, intense" in prompt_text
    assert "Intensity:" in prompt_text

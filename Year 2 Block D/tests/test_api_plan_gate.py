"""Tests for the API plan gate functionality.

This module contains unit tests for the plan enforcement system that manages
subscription-based feature access and validates requests based on plan limitations.
"""

import os
import sys
import pytest
from fastapi import HTTPException

from emotion_mvp.api.plan_gate import Plan, enforce

# ensure project root on PYTHONPATH
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(root)
sys.path.insert(0, root)


@pytest.mark.parametrize(
    "plan,src,duration_sec,expected",
    [
        (
            Plan.basic,
            "hello.mp3",
            300,
            {
                "inp": "hello.mp3",
                "model": "tiny",
                "do_translate": True,
                "do_classify": True,
                "do_classify_ext": False,
                "do_intensity": False,
                "classifier_model": "llama",
            },
        ),
        (
            Plan.plus,
            "audio.wav",
            1200,
            {
                "inp": "audio.wav",
                "model": "medium",
                "do_translate": True,
                "do_classify": True,
                "do_classify_ext": True,
                "do_intensity": False,
                "classifier_model": "llama",
            },
        ),
        (
            Plan.pro,
            "interview.m4a",
            10000,
            {
                "inp": "interview.m4a",
                "model": "turbo",
                "do_translate": True,
                "do_classify": True,
                "do_classify_ext": True,
                "do_intensity": True,
                "classifier_model": "llama",
            },
        ),
    ],
)
def test_enforce_valid_payloads(plan, src, duration_sec, expected):
    """Test the enforce function with valid payloads for different plans.

    Args:
        plan: The subscription plan to test (basic, plus, pro).
        src: The source file name for testing.
        duration_sec: Duration in seconds for the test audio.
        expected: Dictionary of expected configuration values.

    Tests:
        - Plan-specific feature enforcement
        - Proper model selection based on plan
        - Correct boolean flags for each plan tier
        - Input parameter processing and validation
    """
    payload = {
        "src": src,
        "duration_sec": duration_sec,
        # keys to be stripped by enforce
        "translate": False,
        "classify": False,
        "classify_ext": True,
        "intensity": True,
        "classifier": "llama",
    }
    result = enforce(payload, plan)
    for k, v in expected.items():
        assert result[k] == v


def test_enforce_duration_limit_exceeded():
    """Test that duration limits are enforced for basic plan.

    Tests:
        - HTTPException is raised when duration exceeds plan limit
        - Correct status code (403 Forbidden) is returned
        - Appropriate error message is included
    """
    with pytest.raises(HTTPException) as exc:
        enforce({"src": "file.mp3", "duration_sec": Plan.basic and 700}, Plan.basic)
    # HTTPException from FastAPI contains status_code and detail
    assert exc.value.status_code == 403
    assert "Basic plan limited to 10-minute audio" in exc.value.detail


def test_enforce_classifier_default():
    """Test that default classifier is set when not specified.

    Tests:
        - Default classifier model is 'llama' when not specified
        - Payload processing works without explicit classifier
    """
    payload = {"src": "clip.mp3", "duration_sec": 100}
    result = enforce(payload, Plan.basic)
    assert result["classifier_model"] == "llama"


def test_enforce_classifier_custom():
    """Test that custom classifier is preserved when specified.

    Tests:
        - Custom classifier model is used when provided
        - Classifier parameter is correctly mapped to classifier_model
    """
    payload = {"src": "clip.mp3", "duration_sec": 100, "classifier": "gpt"}
    result = enforce(payload, Plan.basic)
    assert result["classifier_model"] == "gpt"

"""Tests for the emotion inference functionality.

This module contains unit tests for the inference module, testing emotion
prediction API calls, response parsing, error handling, and emotion validation.
"""

from unittest.mock import MagicMock
from emotion_mvp import inference
import requests

# --- Test Suite for inference.py ---
# This file tests the logic within emotion_mvp/inference.py directly.


def test_get_emotion_success(mocker):
    """Test successful emotion inference with valid API response.

    Args:
        mocker: Pytest-mock fixture for mocking dependencies.

    Tests:
        - Successful API call processing
        - Proper emotion extraction from response
        - Correct prompt generation and content inclusion
        - Response parsing and validation
    """
    # 1. Mock the successful API response that we expect from the server.
    mock_response = MagicMock()
    mock_response.status_code = 200
    # This simulates the JSON structure your function expects.
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Some text before... Answer: joy"}}]
    }

    # 2. Use 'mocker' to replace the real 'requests.post' with our fake response.
    # Now, whenever inference.py calls requests.post, it will get our mock_response.
    mocker.patch("requests.post", return_value=mock_response)

    # 3. Call the function you want to test.
    emotion, prompt = inference.get_emotion("This is a test sentence.")

    # 4. Assert that the function parsed the response correctly.
    assert emotion == "joy"
    assert "This is a test sentence." in prompt


def test_get_emotion_api_error(mocker):
    """Test emotion inference error handling with network failures.

    Args:
        mocker: Pytest-mock fixture for mocking dependencies.

    Tests:
        - Graceful handling of network connection errors
        - Fallback to 'nan' emotion on API failures
        - Error resilience and proper exception handling
    """
    # 1. Patch 'requests.post' to raise a network connection error instead of returning a value.
    mocker.patch(
        "requests.post",
        side_effect=requests.exceptions.RequestException("Network Error"),
    )

    # 2. Call the function.
    emotion, prompt = inference.get_emotion("This sentence will cause an error.")

    # 3. Assert that your function handles the error gracefully by returning 'nan'.
    assert emotion == "nan"
    assert "This sentence will cause an error." in prompt


def test_get_emotion_invalid_emotion_in_response(mocker):
    """Test emotion inference with invalid emotion in API response.

    Args:
        mocker: Pytest-mock fixture for mocking dependencies.

    Tests:
        - Handling of unknown emotion labels in responses
        - Fallback to 'nan' for invalid emotions
        - Emotion validation against valid emotion set
    """
    # 1. Mock a response with an unexpected emotion string like "bouncy".
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Answer: bouncy"  # "bouncy" is not in your VALID_EMOTIONS list
                }
            }
        ]
    }
    mocker.patch("requests.post", return_value=mock_response)

    # 2. Call the function.
    emotion, prompt = inference.get_emotion("This is another test.")

    # 3. Assert that your function correctly identifies the emotion as invalid and returns 'nan'.
    assert emotion == "nan"

# tests/test_detector.py
"""Tests for the language detection functionality.

This module contains unit tests for the language detector module, testing
language detection from text input and error handling scenarios.
"""

from unittest.mock import patch
from emotion_mvp.detector import detect_lang


def test_detect_lang_happy_path():
    """Test successful language detection for various languages.

    Tests:
        - English text detection returns 'en'
        - Spanish text detection returns 'es'
        - French text detection returns 'fr'
        - Proper language identification accuracy
    """
    # Common English sentence
    assert detect_lang("This is a test sentence.") == "en"
    # Spanish
    assert detect_lang("¡Buenos días!") == "es"
    # French
    assert detect_lang("Je suis heureux.") == "fr"


@patch("emotion_mvp.detector.detect")
def test_detect_lang_exception(mock_detect, caplog):
    """Test language detection error handling and fallback.

    Args:
        mock_detect: Mock for the langdetect.detect function.
        caplog: Pytest fixture for capturing log messages.

    Tests:
        - Exception handling when detection fails
        - Fallback to 'en' when detection errors occur
        - Proper warning logging on detection failure
    """
    # Simulate langdetect raising an error
    mock_detect.side_effect = Exception("fail")
    caplog.set_level("WARNING")
    result = detect_lang("any text")
    assert result == "en"
    # Ensure warning was logged
    assert any(
        "defaulting to 'en'" in rec.getMessage() and rec.levelname == "WARNING"
        for rec in caplog.records
    )

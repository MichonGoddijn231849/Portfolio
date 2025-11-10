"""Tests for the CLI main script functionality.

This module contains unit tests for the main CLI script that processes
emotion data through the full pipeline, including data loading, emotion
prediction, and review functionality.
"""

import sys
from pathlib import Path
import pandas as pd


# Ensure project root is on the path for imports to work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_main_flow(capsys, monkeypatch):
    """Test the main CLI flow with mocked dependencies.

    Args:
        capsys: Pytest fixture for capturing stdout/stderr.
        monkeypatch: Pytest fixture for mocking dependencies.

    Tests:
        - Full main script execution flow
        - Data loading and processing
        - Emotion prediction and review pipeline
        - Output formatting and display
        - Integration between all components
    """
    # 1. Define the exact dummy data we want the test to use
    dummy_df = pd.DataFrame(
        [
            {"Translation": "I am sad.", "Emotion": "sad"},
            {"Translation": "I am joyful!", "Emotion": "happy"},
        ]
    )

    # 2. Mock the data loading function
    # This reliably replaces the real data loader with our fake one for this test
    from emotion_mvp import data_loader

    monkeypatch.setattr(data_loader, "load_and_clean_data", lambda path: dummy_df)

    # 3. Mock the inference functions to prevent real API calls
    from emotion_mvp import inference

    # This fake function will now behave exactly like the corrected main script
    def fake_get_emotion(sentence, temperature=0.5):
        if "sad" in sentence:
            return "sad", "mock prompt"
        if "joyful" in sentence:
            return "happy", "mock prompt"
        return "unknown", "mock prompt"

    monkeypatch.setattr(inference, "get_emotion", fake_get_emotion)
    monkeypatch.setattr(
        inference,
        "review_emotion",
        lambda sentence, predicted, actual, temperature=0.5: actual,
    )

    # 4. Import and run the main script AFTER mocks are in place
    import emotion_mvp.cli_main as cli_main

    cli_main.main()

    # 5. Capture and verify the output
    out = capsys.readouterr().out

    # --- ALL ASSERTIONS ARE NOW FIXED TO MATCH THE REAL OUTPUT ---
    # Check loaded message
    assert "✅ Loaded 2 cleaned rows." in out

    # First row assertions
    assert "=== Row 0 ===" in out
    assert "Sentence : I am sad." in out  # Fixed spacing
    assert "Actual   : sad" in out  # Check for correct 'Actual' text
    assert "Predicted: sad" in out  # Check for correct 'Predicted' text

    # Second row assertions
    assert "=== Row 1 ===" in out
    assert "Sentence : I am joyful!" in out  # Fixed spacing
    assert "Actual   : happy" in out  # Check for correct 'Actual' text
    assert "Predicted: happy" in out  # Check for correct 'Predicted' text

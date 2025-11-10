"""Tests for the inference history logging functionality.

This module contains unit tests for the history module, testing CSV logging
of inference results, file creation, data persistence, and error handling.
"""

import sys
from pathlib import Path
import pytest
import csv
import re
from datetime import datetime
import emotion_mvp.history as history

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def use_tmp_history(tmp_path, monkeypatch):
    """Create a temporary history file for testing.

    Args:
        tmp_path: Pytest temporary directory fixture.
        monkeypatch: Pytest fixture for patching module attributes.

    Returns:
        Path: Path to the temporary history file.
    """
    # Redirect HISTORY_FILE to a temp file
    temp_file = tmp_path / "history.csv"
    monkeypatch.setattr(history, "HISTORY_FILE", str(temp_file))
    return temp_file


def test_log_inference_creates_file_with_header(use_tmp_history):
    """Test that logging inference creates file with proper header.

    Args:
        use_tmp_history: Fixture providing temporary history file path.

    Tests:
        - File creation on first inference logging
        - Proper CSV header row creation
        - Correct data format and timestamp generation
        - Data integrity in logged entries
    """
    assert not use_tmp_history.exists()
    history.log_inference(
        user_input="hello",
        summary={
            "language": "en",
            "translated": "hello",
            "emotion": "happy",
            "csv": "row1",
        },
    )
    assert use_tmp_history.exists()

    with open(use_tmp_history, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [
            "timestamp",
            "input",
            "language",
            "translated",
            "emotion",
            "csv",
        ]
        row = next(reader)
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", row[0])
        assert row[1:] == ["hello", "en", "hello", "happy", "row1"]


def test_log_inference_appends_rows(use_tmp_history):
    """Test that multiple inferences are properly appended to history.

    Args:
        use_tmp_history: Fixture providing temporary history file path.

    Tests:
        - Multiple entries are appended correctly
        - Data integrity across multiple logs
        - Proper timestamp generation for each entry
        - Handling of missing summary fields
    """
    history.log_inference("first", {"emotion": "sad"})
    history.log_inference("second", {})

    with open(use_tmp_history, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["input"] == "first"
    assert rows[0]["emotion"] == "sad"
    assert rows[1]["input"] == "second"
    assert rows[1]["emotion"] == ""
    for row in rows:
        ts = row["timestamp"]
        datetime.fromisoformat(ts.rstrip("Z"))


def test_missing_keys_written_as_empty(use_tmp_history):
    """Test handling of missing summary keys in inference logging.

    Args:
        use_tmp_history: Fixture providing temporary history file path.

    Tests:
        - Missing summary fields are written as empty strings
        - Graceful handling of incomplete summary data
        - CSV structure integrity with missing fields
    """
    history.log_inference("test", {})
    with open(use_tmp_history, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)
        assert row["language"] == ""
        assert row["translated"] == ""
        assert row["csv"] == ""

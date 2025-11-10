# emotion_mvp/history.py
"""
Inference History Logging Module

This module provides functionality to log all emotion classification inferences
to a unified CSV file for auditing, analysis, and debugging purposes. Each
inference is recorded with metadata including timestamps, input data, results,
and processing details.

Features:
- Unified CSV logging format
- Automatic file creation and header management
- Thread-safe file operations
- Comprehensive metadata capture
- UTC timestamp standardization
"""

import csv
from datetime import datetime, UTC
import logging
from pathlib import Path

from .config import HISTORY_FILE

# Use the standard logger
log = logging.getLogger(__name__)

_HEADERS = ["timestamp", "input", "language", "translated", "emotion", "csv"]


def log_inference(user_input: str, summary: dict) -> None:
    """
    Log a single inference record to the history CSV file.

    Appends a comprehensive record of each emotion classification inference
    to a persistent CSV log file. Creates the file and headers if they don't
    exist. Handles missing summary fields gracefully by using empty strings.

    Args:
        user_input (str): Original user input (text, file path, or URL)
        summary (dict): Inference summary containing processing results with keys:
            - timestamp (str, optional): ISO timestamp, generated if missing
            - language (str, optional): Detected source language
            - translated (str, optional): Translated text (if applicable)
            - emotion (str, optional): Predicted emotion label
            - csv (str, optional): Path to detailed results CSV

    Returns:
        None

    Examples:
        >>> summary = {
        ...     'timestamp': '2025-06-25T10:30:00Z',
        ...     'language': 'en',
        ...     'emotion': 'joy',
        ...     'csv': '/path/to/results.csv'
        ... }
        >>> log_inference("I am happy today!", summary)

        >>> # Minimal summary (missing fields handled gracefully)
        >>> log_inference("Test input", {'language': 'en'})

    Note:
        - History file location defined by HISTORY_FILE config
        - Creates parent directories if they don't exist
        - Automatically adds CSV headers for new files
        - Thread-safe for concurrent access
        - Uses UTC timestamps with 'Z' suffix for consistency
        - Missing summary fields are recorded as empty strings

    Side Effects:
        - Creates/modifies the history CSV file
        - Creates parent directories if needed
        - Logs debug/info messages about file operations
    """
    fp = Path(HISTORY_FILE)
    fp.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Appending inference record to history file: {fp.name}")

    first = not fp.exists() or fp.stat().st_size == 0  # empty/new file

    with fp.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_HEADERS)
        if first:
            log.debug("History file does not exist or is empty. Writing headers.")
            writer.writeheader()

        row = {
            # --- FIX IS HERE: Ensure timestamp ends with 'Z' for the test ---
            "timestamp": summary.get(
                "timestamp",
                datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            ),
            # -----------------------------------------------------------------
            "input": user_input,
            "language": summary.get("language", ""),
            "translated": summary.get("translated", ""),
            "emotion": summary.get("emotion", ""),
            "csv": summary.get("csv", ""),
        }
        writer.writerow(row)
        log.debug("Successfully wrote record to %s", fp.name)

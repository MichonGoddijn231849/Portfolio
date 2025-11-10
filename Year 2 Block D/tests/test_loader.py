# tests/test_loader.py
"""Tests for the data loader functionality.

This module contains unit tests for the data loading system, testing
CSV file processing, data cleaning, and validation of emotion data.
"""
import pandas as pd
from emotion_mvp.data_loader import load_and_clean_data
import tempfile


def test_load_and_clean_data():
    """Test data loading and cleaning with valid CSV data.

    Tests:
        - CSV file loading and processing
        - Data cleaning removes empty emotion entries
        - Proper DataFrame filtering and validation
        - Temporary file handling for testing
    """
    # Create a temporary CSV file with mock data
    df = pd.DataFrame(
        {
            "Translation": ["I am happy", "I am sad", "Empty emotion"],
            "Emotion": ["joy", "sadness", ""],
        }
    )
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(temp_file.name, index=False)

    # Run the loader
    cleaned_df = load_and_clean_data(temp_file.name)

    # Should only keep rows with non-empty 'Emotion'
    assert len(cleaned_df) == 2
    assert all(cleaned_df["Emotion"].str.strip() != "")

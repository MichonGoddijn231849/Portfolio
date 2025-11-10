# tests/test_data_loader.py
"""Tests for the data loading and cleaning functionality.

This module contains unit tests for the data loader module, testing
CSV file loading, data cleaning, error handling, and data validation.
"""
import pandas as pd
import pytest
from pathlib import Path
from emotion_mvp.data_loader import load_and_clean_data


def make_csv(tmp_path: Path, content: str) -> Path:
    """Create a temporary CSV file for testing.

    Args:
        tmp_path: Pytest temporary directory fixture.
        content: String content to write to the CSV file.

    Returns:
        Path: Path to the created CSV file.
    """
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(content)
    return csv_file


def test_load_and_clean_data_happy_path(tmp_path):
    """Test successful data loading and cleaning with valid CSV.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - Successful CSV loading with valid data
        - Data cleaning removes empty emotion entries
        - Proper DataFrame structure is returned
        - Data integrity is maintained after cleaning
    """
    content = (
        "Text,Emotion\n"
        "Hello world,joy\n"
        "I am sad,sadness\n"
        ",neutral\n"  # blank text OK
        "No emotion,\n"  # empty emotion → removed
        "Missing,\n"  # empty emotion → removed
    )
    csv_path = make_csv(tmp_path, content)
    df = load_and_clean_data(str(csv_path))
    # Should keep only the first three rows (emotion non-empty)
    assert isinstance(df, pd.DataFrame)
    assert list(df["Emotion"]) == ["joy", "sadness", "neutral"]


def test_load_and_clean_data_missing_file(tmp_path):
    """Test error handling when CSV file does not exist.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - FileNotFoundError is raised for missing files
        - Proper error handling for invalid file paths
    """
    missing = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError):
        load_and_clean_data(str(missing))


def test_load_and_clean_data_empty_file(tmp_path):
    """Test error handling when CSV file is empty.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - EmptyDataError is raised for empty files
        - Proper error handling for files with no content
    """
    empty = tmp_path / "empty.csv"
    empty.write_text("")  # creates an empty file
    with pytest.raises(pd.errors.EmptyDataError):
        load_and_clean_data(str(empty))


def test_load_and_clean_data_malformed(tmp_path):
    """Test error handling when CSV file is malformed.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - KeyError is raised for missing required columns
        - Proper error handling for malformed CSV structure
    """
    bad = tmp_path / "bad.csv"
    # missing header row
    bad.write_text("just,some,random,values\n1,2,3,4")
    with pytest.raises(KeyError):
        load_and_clean_data(str(bad))

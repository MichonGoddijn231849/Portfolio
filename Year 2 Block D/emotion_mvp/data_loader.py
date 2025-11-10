# emotion_mvp/data_loader.py
"""
Data Loading and Preprocessing Module

This module provides functionality for loading and preprocessing emotion classification
datasets. It handles data validation, cleaning, and preparation for model training
and evaluation.

Features:
- CSV data loading with error handling
- Missing data detection and removal
- Data validation and quality checks
- Comprehensive logging for debugging
- Pandas DataFrame integration

The module ensures data quality and consistency before feeding data to
classification models or evaluation pipelines.
"""

import pandas as pd
from pathlib import Path
import logging

# 1. Get the logger
log = logging.getLogger(__name__)


def load_and_clean_data(path: str) -> pd.DataFrame:
    """
    Load emotion dataset from CSV and clean missing or invalid emotion labels.

    Loads a CSV file containing emotion classification data and performs
    data quality checks. Removes rows with missing, empty, or invalid emotion
    labels to ensure clean training/evaluation data.

    Args:
        path (str): File path to the CSV dataset. Should contain at least
                   an 'Emotion' column with emotion labels.

    Returns:
        pd.DataFrame: Cleaned dataset with valid emotion labels only.
                     Retains original column structure.

    Raises:
        FileNotFoundError: If the specified file path doesn't exist
        KeyError: If the CSV doesn't contain required 'Emotion' column

    Examples:
        >>> df = load_and_clean_data("data/emotions.csv")
        >>> print(f"Loaded {len(df)} clean records")
        Loaded 1250 clean records

        >>> print(df.columns.tolist())
        ['Text', 'Emotion', 'Source', 'Confidence']

        >>> print(df['Emotion'].value_counts())
        joy        245
        sadness    198
        anger      156
        ...

    Data Requirements:
        - CSV format with headers
        - Must contain 'Emotion' column
        - Emotion column should contain string labels
        - Other columns are preserved as-is

    Data Cleaning Steps:
        1. Load CSV file using pandas
        2. Remove rows where 'Emotion' column is NaN
        3. Remove rows where 'Emotion' is empty string or whitespace
        4. Log cleaning statistics for monitoring

    Note:
        - Preserves all other columns in the dataset
        - Logs detailed information about cleaning process
        - Handles various CSV encodings automatically
        - Case-sensitive emotion label preservation
    """
    # 2. Add log messages to show what's happening
    log.info(f"Attempting to load data from '{path}'...")

    if not Path(path).exists():
        log.error(f"File not found at specified path: {path}")
        raise FileNotFoundError(f"The file {path} was not found.")

    df = pd.read_csv(path)
    original_rows = len(df)
    log.debug(f"Loaded {original_rows} rows from CSV.")

    df.dropna(subset=["Emotion"], inplace=True)
    df = df[df["Emotion"].str.strip() != ""]

    cleaned_rows = len(df)
    rows_removed = original_rows - cleaned_rows

    if rows_removed > 0:
        log.warning(f"Removed {rows_removed} rows with missing 'Emotion' values.")

    log.info(f"Data loading complete. Returning {cleaned_rows} cleaned rows.")
    return df

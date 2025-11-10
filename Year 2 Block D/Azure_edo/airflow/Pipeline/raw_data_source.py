# raw_data_source.py
import os
import pandas as pd


def load_raw_data(path: str, nrows: int = None) -> pd.DataFrame:
    """
    Load the raw CSV into a DataFrame.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path, nrows=nrows)

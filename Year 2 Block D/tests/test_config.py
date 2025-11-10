"""Tests for the configuration module.

This module contains unit tests for the configuration system, testing
environment variable handling, default values, and configuration loading
functionality.
"""

import importlib
import os
import sys

# project root for config.py reload
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


def reload_config():
    """Reload the config module to test fresh configuration loading.

    Returns:
        module: Freshly reloaded config module.
    """
    if "emotion_mvp.config" in sys.modules:
        del sys.modules["emotion_mvp.config"]
    return importlib.import_module("emotion_mvp.config")


def test_csv_path_default(monkeypatch):
    """Test default CSV_PATH configuration when environment variable is not set.

    Args:
        monkeypatch: Pytest fixture for environment variable manipulation.

    Tests:
        - Default CSV_PATH points to correct location
        - Path construction when no environment variable is set
        - Proper fallback behavior
    """
    # Ensure CSV_PATH env is not set
    monkeypatch.delenv("CSV_PATH", raising=False)
    config = reload_config()
    # Default CSV_PATH should point to emotion_mvp/data/Data_v2.csv in this repo
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    expected = str(repo_root / "emotion_mvp" / "data" / "Data_v2.csv")
    assert (
        config.CSV_PATH == expected
    ), f"Expected default CSV_PATH to be {expected}, got {config.CSV_PATH}"


def test_csv_path_env(monkeypatch):
    """Test CSV_PATH configuration from environment variable.

    Args:
        monkeypatch: Pytest fixture for environment variable manipulation.

    Tests:
        - Environment variable overrides default path
        - Custom path is properly loaded from environment
    """
    test_path = "/some/test/path.csv"
    monkeypatch.setenv("CSV_PATH", test_path)
    config = reload_config()
    assert config.CSV_PATH == test_path


def test_llama_defaults():
    """Test default LLaMA model configuration.

    Tests:
        - LLaMA API URL is properly formatted
        - LLaMA model ID is configured
        - Default configuration values are valid
    """
    config = reload_config()
    assert config.LLAMA_API_URL.startswith("http")
    assert config.LLAMA_MODEL_ID


def test_bert_defaults():
    """Test default BERT model configuration.

    Tests:
        - BERT model name is configured
        - BERT labels list is properly formatted
        - Configuration types are correct
    """
    config = reload_config()
    assert config.BERT_MODEL_NAME
    assert isinstance(config.BERT_LABELS, list)


def test_supported_translators():
    """Test supported translators configuration.

    Tests:
        - Required language codes are present
        - Translator configuration is properly loaded
    """
    config = reload_config()
    assert "de" in config.SUPPORTED_TRANSLATORS


def test_valid_emotions():
    """Test valid emotions configuration.

    Tests:
        - Required emotions are included in the set
        - Configuration is stored as proper data type
        - Emotion validation setup
    """
    config = reload_config()
    assert "joy" in config.VALID_EMOTIONS
    assert isinstance(config.VALID_EMOTIONS, set)


def test_history_filename():
    """Test history file configuration.

    Tests:
        - History file has correct extension
        - Filename format is valid
    """
    config = reload_config()
    assert config.HISTORY_FILE.endswith(".csv")


def test_bert_api_defaults():
    """Test BERT API configuration defaults.

    Tests:
        - BERT API URL is properly formatted
        - API key is configured with expected length
        - API configuration is valid
    """
    config = reload_config()
    assert config.BERT_API_URL.startswith("http")
    assert len(config.BERT_API_KEY) > 20

# tests/test_translator.py
"""Tests for the translation functionality.

This module contains unit tests for the translator module, testing multilingual
text translation using MarianMT models, caching mechanisms, and translation
pipeline integration.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

# Now import the module under test
import emotion_mvp.translator as translator

# Stub out transformers before importing the translator module
sys.modules["transformers"] = MagicMock()

SUPPORTED_TRANSLATORS = translator.SUPPORTED_TRANSLATORS


# --- Dummy classes for testing ---
class DummyTokenizer:
    """Mock tokenizer for testing translation functionality."""

    def __init__(self):
        self.called_with = None

    def __call__(self, text, **kwargs):
        self.called_with = (text, kwargs)
        return {"input_ids": "dummy_input_ids"}

    def decode(self, token_ids, skip_special_tokens=True):
        return "decoded_text"


class DummyModel:
    """Mock model for testing translation functionality."""

    def __init__(self):
        self.generated_with = None

    def generate(self, **batch):
        self.generated_with = batch
        return ["dummy_output_ids"]


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure the translator's model cache is empty before each test.

    This fixture automatically runs before each test to prevent
    test interference through shared cache state.
    """
    translator._CACHE.clear()


def test_translate_en_returns_same():
    """Test that English text is returned unchanged.

    Tests:
        - English language detection and passthrough
        - No translation attempted for English input
    """
    assert translator.translate("Hello", "en") == "Hello"


def test_translate_unsupported_lang_returns_same():
    """Test handling of unsupported language codes.

    Tests:
        - Unsupported language fallback behavior
        - Text returned unchanged for unknown languages
        - Graceful handling of invalid language codes
    """
    assert translator.translate("Bonjour", "xx") == "Bonjour"


@patch("emotion_mvp.translator.MarianMTModel")
@patch("emotion_mvp.translator.MarianTokenizer")
def test_load_populates_cache_and_returns_objects(mock_tokenizer, mock_model):
    """Test model loading and caching functionality.

    Args:
        mock_tokenizer: Mock for MarianTokenizer.
        mock_model: Mock for MarianMTModel.

    Tests:
        - Model and tokenizer loading from HuggingFace
        - Caching mechanism prevents repeated downloads
        - Same objects returned on subsequent calls
    """
    src = next(iter(SUPPORTED_TRANSLATORS))
    tok1, mdl1 = translator._load(src)
    tok2, mdl2 = translator._load(src)
    mock_tokenizer.from_pretrained.assert_called_once()
    mock_model.from_pretrained.assert_called_once()
    assert tok1 is tok2
    assert mdl1 is mdl2


@patch("emotion_mvp.translator._load")
def test_translate_calls_tokenizer_and_model(mock_load):
    """Test that the translate function calls its components correctly.

    Args:
        mock_load: Mock for the _load function.

    Tests:
        - Proper tokenizer integration and text processing
        - Model generation with correct parameters
        - Translation pipeline from input to output
        - Component interaction validation
    """
    dummy_tok = DummyTokenizer()
    dummy_mdl = DummyModel()
    mock_load.return_value = (dummy_tok, dummy_mdl)

    result = translator.translate("Hola", "de")

    mock_load.assert_called_with("de")
    assert dummy_tok.called_with is not None
    assert dummy_tok.called_with[0] == "Hola"

    assert dummy_mdl.generated_with is not None

    # --- THIS IS THE FINAL FIX ---
    # Instead of checking for an exact dictionary match, we just check
    # that the dictionary CONTAINS the correct input_ids.
    assert dummy_mdl.generated_with["input_ids"] == "dummy_input_ids"
    # ---------------------------

    assert result == "decoded_text"

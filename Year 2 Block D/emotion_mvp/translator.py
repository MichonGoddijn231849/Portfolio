# emotion_mvp/translator.py
"""
Translation Module

This module provides multilingual text translation capabilities using pre-trained
MarianMT models from Hugging Face. Supports automatic translation from various
languages to English for emotion classification.

Features:
- Automatic model loading and caching
- Support for multiple source languages
- Fallback to original text on translation failures
- Efficient model reuse through caching
"""

import logging
from transformers import MarianMTModel, MarianTokenizer
from .config import MODELS_PATH, SUPPORTED_TRANSLATORS

# 1. Use the standard logger
log = logging.getLogger(__name__)

_CACHE = {}


def _load(src: str):
    """
    Load a translation model into cache if not already present.

    Downloads and caches MarianMT translation models from Hugging Face.
    Models are cached locally to avoid repeated downloads and improve
    performance on subsequent uses.

    Args:
        src (str): Source language code (e.g., 'es', 'fr', 'de')

    Returns:
        tuple: A tuple containing (tokenizer, model) for the requested language

    Note:
        - Models are downloaded to the path specified by MODELS_PATH config
        - First-time loading includes download time (can be several minutes)
        - Subsequent loads are nearly instantaneous due to caching

    Examples:
        >>> tokenizer, model = _load('es')  # Load Spanish to English model
        >>> tokenizer, model = _load('fr')  # Load French to English model
    """
    ckpt = SUPPORTED_TRANSLATORS[src]
    if ckpt not in _CACHE:
        # 2. Add a log message for this important, one-time action
        log.info(
            f"Downloading/loading translation model for '{src}' language: Helsinki-NLP/{ckpt}"
        )
        tok = MarianTokenizer.from_pretrained(
            f"Helsinki-NLP/{ckpt}", cache_dir=str(MODELS_PATH)
        )
        mdl = MarianMTModel.from_pretrained(
            f"Helsinki-NLP/{ckpt}", cache_dir=str(MODELS_PATH)
        )
        _CACHE[ckpt] = (tok, mdl)
        log.info(f"Model for '{src}' successfully loaded and cached.")
    return _CACHE[ckpt]


def translate(text: str, src_lang: str) -> str:
    """
    Translate text from a supported source language to English.

    Uses pre-trained MarianMT models to translate text from various languages
    to English. If the source language is already English or unsupported,
    returns the original text unchanged.

    Args:
        text (str): Input text to translate
        src_lang (str): Source language code (ISO 639-1 format, e.g., 'es', 'fr', 'de')

    Returns:
        str: Translated text in English, or original text if translation
             is not needed or fails

    Examples:
        >>> translate("Hola, ¿cómo estás?", "es")
        'Hello, how are you?'
        >>> translate("Bonjour, comment allez-vous?", "fr")
        'Hello, how are you?'
        >>> translate("Hello, how are you?", "en")
        'Hello, how are you?'  # No translation needed
        >>> translate("Some text", "unsupported_lang")
        'Some text'  # Returns original for unsupported languages

    Note:
        - Supports languages defined in SUPPORTED_TRANSLATORS config
        - First translation for a language triggers model download
        - Uses beam search decoding for better translation quality
        - Automatically handles text truncation for long inputs
        - Falls back to original text if translation fails

    Raises:
        Does not raise exceptions - returns original text on any failure
    """
    if src_lang == "en" or src_lang not in SUPPORTED_TRANSLATORS:
        log.debug(f"Skipping translation for source language '{src_lang}'.")
        return text

    log.debug(f"Translating text from '{src_lang}'...")
    tok, mdl = _load(src_lang)

    # Use a try-except block for robustness
    try:
        batch = tok(text, return_tensors="pt", truncation=True, padding=True)
        out = mdl.generate(**batch, max_length=512, num_beams=4)
        translated_text = tok.decode(out[0], skip_special_tokens=True)
        log.debug("Translation successful.")
        return translated_text
    except Exception:
        log.exception(f"An error occurred during translation from '{src_lang}'")
        # Return original text as a fallback if translation fails
        return text

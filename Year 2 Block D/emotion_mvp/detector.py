"""
Language Detection Module

This module provides automatic language detection capabilities for text input.
Uses the langdetect library with fallback to English for robustness.
"""

from langdetect import detect
from .log import get_logger

log = get_logger("detector")


def detect_lang(text: str) -> str:
    """
    Detect the language of input text with fallback to English.

    Uses the langdetect library to identify the language of the provided text.
    If detection fails for any reason (empty text, unrecognized language, etc.),
    defaults to English ('en') to ensure pipeline continuity.

    Args:
        text (str): Input text to analyze for language detection

    Returns:
        str: ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de')

    Examples:
        >>> detect_lang("Hello, how are you?")
        'en'
        >>> detect_lang("Hola, ¿cómo estás?")
        'es'
        >>> detect_lang("Bonjour, comment allez-vous?")
        'fr'
        >>> detect_lang("")  # Empty text
        'en'
        >>> detect_lang("123 !@#")  # Non-text content
        'en'

    Note:
        - Supports 55+ languages via langdetect
        - Always returns a valid language code (never None or empty)
        - Logs warnings when detection fails and fallback is used
        - Works best with text longer than a few words
    """
    try:
        return detect(text)
    except Exception:
        log.warning("Language detect failed; defaulting to 'en'")
        return "en"

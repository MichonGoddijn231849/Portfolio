# emotion_mvp/classifier.py
"""
Emotion Classification Module

This module provides emotion classification capabilities using both LLaMA and BERT models.
It supports different subscription tiers with varying emotion sets and features including
intensity scoring and extended emotion classification.

The module handles:
- LLaMA-based emotion classification with custom prompts
- BERT-based emotion classification via external API
- Emotion intensity analysis
- Fallback mechanisms for model failures
- Multiple subscription plan support (basic, plus, pro)
"""

import re
import requests
import json
from typing import Tuple, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    LLAMA_API_URL,
    LLAMA_MODEL_ID,
    LLAMA_TOKEN,
    LLAMA_FALLBACK_MODELS,
    BERT_API_URL,
    BERT_API_KEY,
)
from .prompts import build_prompt, build_review_prompt
from .log import get_logger
from .emotion_tiers import EMOTION_TIERS

log = get_logger("classifier")

# ─── Llama setup ────────────────────────────────────────────────

HEADERS_LLAMA = {
    "Authorization": f"Bearer {LLAMA_TOKEN}",
    "Content-Type": "application/json",
}


def _call_llama(messages, temperature: float = 0.5) -> str:
    """
    Call LLaMA API with retry mechanism across multiple model fallbacks.

    Attempts to call the primary LLaMA model, falling back to alternative models
    if the primary fails. Uses exponential backoff and retry logic.

    Args:
        messages: List of message dictionaries for the chat completion
        temperature (float): Sampling temperature for response generation (0.0-1.0).
            Lower values make output more deterministic. Defaults to 0.5.

    Returns:
        str: The generated response content from the LLaMA model

    Raises:
        RuntimeError: If all model endpoints fail to respond

    Examples:
        >>> messages = [{"role": "user", "content": "Classify emotion: I am happy"}]
        >>> response = _call_llama(messages, temperature=0.3)
        >>> print(response)
        'joy'
    """
    for model_name in [LLAMA_MODEL_ID] + LLAMA_FALLBACK_MODELS:
        try:
            resp = requests.post(
                LLAMA_API_URL,
                headers=HEADERS_LLAMA,
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            log.warning("Llama %s failed: %s", model_name, e)
    raise RuntimeError(
        f"No available Llama models among {[LLAMA_MODEL_ID] + LLAMA_FALLBACK_MODELS}"
    )


def _extract_emotion(text: str) -> str:
    """
    Extract emotion label from LLaMA response text using regex pattern matching.

    Searches for the pattern "Answer: <emotion>" in the response text and extracts
    the emotion label. If no pattern is found, returns the stripped text.

    Args:
        text (str): Raw response text from LLaMA model

    Returns:
        str: Extracted emotion label in lowercase

    Examples:
        >>> _extract_emotion("Answer: joy")
        'joy'
        >>> _extract_emotion("The emotion is sadness. Answer: sadness")
        'sadness'
        >>> _extract_emotion("anger")
        'anger'
    """
    m = re.search(r"Answer:\s*([a-z]+)", text, re.IGNORECASE)
    return m.group(1).lower() if m else text.strip().lower()


def predict_emotion_llama(
    sentence: str, classify_ext: bool, do_intensity: bool
) -> Tuple[str, Optional[float]]:
    """
    Predict emotion from text using LLaMA model with configurable features.

    Uses LLaMA language model to classify emotions in text. Supports different
    subscription tiers with varying emotion sets and optional intensity scoring.
    Falls back to 'neutral' for unrecognized emotions.

    Args:
        sentence (str): Input text to classify
        classify_ext (bool): Whether to use extended emotion set (Plus/Pro plans)
        do_intensity (bool): Whether to calculate emotion intensity (Pro plan only)

    Returns:
        Tuple[str, Optional[float]]: A tuple containing:
            - str: Predicted emotion label
            - Optional[float]: Intensity score (0.0-1.0) if do_intensity=True, else None

    Raises:
        RuntimeError: If all LLaMA model endpoints fail

    Examples:
        >>> # Basic classification
        >>> emotion, intensity = predict_emotion_llama("I am thrilled!", False, False)
        >>> print(emotion)  # 'joy'
        >>> print(intensity)  # None

        >>> # With intensity scoring
        >>> emotion, intensity = predict_emotion_llama("I am furious!", True, True)
        >>> print(emotion)  # 'anger'
        >>> print(intensity)  # 0.75

    Note:
        The function automatically selects the appropriate emotion tier based on
        the classify_ext and do_intensity parameters:
        - Basic: 7 emotions (joy, sadness, anger, fear, surprise, disgust, neutral)
        - Plus: Extended emotion set (20+ emotions)
        - Pro: Extended emotions + intensity scoring
    """
    tier = "pro" if do_intensity else ("plus" if classify_ext else "basic")
    allowed = EMOTION_TIERS[tier]
    prompt = build_prompt(
        sentence=sentence,
        allowed_labels=allowed,
        plan_name=tier,
        want_intensity=do_intensity,
    )
    content = _call_llama(
        [
            {"role": "system", "content": "You are an expert emotion classifier."},
            {"role": "user", "content": prompt},
        ]
    )
    emo = _extract_emotion(content)
    if emo not in allowed:
        emo = "neutral"
    intensity = None
    if do_intensity:
        m = re.search(r"Intensity:\s*([a-z]+)", content, re.IGNORECASE)
        if m:
            mapping = {
                "neutral": 0.0,
                "mild": 0.25,
                "moderate": 0.5,
                "strong": 0.75,
                "intense": 1.0,
            }
            intensity = mapping.get(m.group(1).lower(), 0.0)
    log.info("Llama → %s (intensity=%s)", emo, intensity)
    return emo, intensity


def review_emotion_llama(
    sentence: str, predicted: str, actual: str, classify_ext: bool, do_intensity: bool
) -> Tuple[str, Optional[float]]:
    """
    Review and potentially correct emotion classification using LLaMA.

    Uses LLaMA to review a previous emotion prediction by comparing it with
    ground truth data. This function is typically used for model validation
    and correction workflows.

    Args:
        sentence (str): Original input text that was classified
        predicted (str): Previously predicted emotion label
        actual (str): Ground truth emotion label
        classify_ext (bool): Whether to use extended emotion set
        do_intensity (bool): Whether to calculate intensity scores

    Returns:
        Tuple[str, Optional[float]]: A tuple containing:
            - str: Reviewed/corrected emotion label
            - Optional[float]: Intensity score if do_intensity=True, else None

    Raises:
        RuntimeError: If all LLaMA model endpoints fail

    Examples:
        >>> # Review a prediction
        >>> corrected, intensity = review_emotion_llama(
        ...     sentence="I feel okay",
        ...     predicted="joy",
        ...     actual="neutral",
        ...     classify_ext=True,
        ...     do_intensity=False
        ... )
        >>> print(corrected)  # 'neutral'

    Note:
        If the LLaMA model produces an emotion not in the allowed set,
        the function falls back to the original predicted emotion.
    """
    tier = "pro" if do_intensity else ("plus" if classify_ext else "basic")
    allowed = EMOTION_TIERS[tier]
    prompt = build_review_prompt(
        sentence=sentence,
        predicted_emotion=predicted,
        actual_emotion=actual,
        allowed_labels=allowed,
        want_intensity=do_intensity,
    )
    content = _call_llama(
        [
            {"role": "system", "content": "You are an expert emotion classifier."},
            {"role": "user", "content": prompt},
        ]
    )
    emo = _extract_emotion(content)
    if emo not in allowed:
        emo = predicted
    intensity = None
    if do_intensity:
        m = re.search(r"Intensity:\s*([a-z]+)", content, re.IGNORECASE)
        if m:
            mapping = {
                "neutral": 0.0,
                "mild": 0.25,
                "moderate": 0.5,
                "strong": 0.75,
                "intense": 1.0,
            }
            intensity = mapping.get(m.group(1).lower(), 0.0)
    return emo, intensity


# ─── Remote‐only BERT setup ─────────────────────────────────────

_LABEL_MAP = {
    0: "admiration",
    1: "amusement",
    2: "anger",
    3: "annoyance",
    4: "approval",
    5: "caring",
    6: "confusion",
    7: "curiosity",
    8: "desire",
    9: "disappointment",
    10: "disapproval",
    11: "disgust",
    12: "embarrassment",
    13: "excitement",
    14: "fear",
    15: "gratitude",
    16: "grief",
    17: "joy",
    18: "love",
    19: "nervousness",
    20: "optimism",
    21: "pride",
    22: "realization",
    23: "relief",
    24: "remorse",
    25: "sadness",
    26: "surprise",
    27: "neutral",
}

# map each of the 28 classes to one of your 7 basic labels
_BASIC_MAP = {
    "admiration": "happy",
    "amusement": "happy",
    "anger": "mad",
    "annoyance": "mad",
    "approval": "happy",
    "caring": "happy",
    "confusion": "neutral",
    "curiosity": "neutral",
    "desire": "happy",
    "disappointment": "sad",
    "disapproval": "mad",
    "disgust": "disgust",
    "embarrassment": "sad",
    "excitement": "happy",
    "fear": "scared",
    "gratitude": "happy",
    "grief": "sad",
    "joy": "happy",
    "love": "happy",
    "nervousness": "scared",
    "optimism": "happy",
    "pride": "happy",
    "realization": "surprised",
    "relief": "happy",
    "remorse": "sad",
    "sadness": "sad",
    "surprise": "surprised",
    "neutral": "neutral",
}

# build a retry‐enabled session for BERT calls
_RETRY_STRAT = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
)
_BERT_SESSION = requests.Session()
_BERT_SESSION.mount("http://", HTTPAdapter(max_retries=_RETRY_STRAT))
_BERT_SESSION.mount("https://", HTTPAdapter(max_retries=_RETRY_STRAT))


def predict_emotion_bert(
    sentence: str, classify_ext: bool, do_intensity: bool
) -> Tuple[str, Optional[float]]:
    """
    Predict emotion from text using external BERT API with retry mechanism.

    Calls an external BERT-based emotion classification service. The function
    handles response parsing, label mapping, and automatic retries on failure.
    Supports both basic (7 emotions) and extended emotion sets.

    Args:
        sentence (str): Input text to classify
        classify_ext (bool): Whether to use extended emotion set. If False,
            maps to basic 7-emotion set (happy, sad, mad, scared, surprised, disgust, neutral)
        do_intensity (bool): Intensity parameter (currently not implemented for BERT)

    Returns:
        Tuple[str, Optional[float]]: A tuple containing:
            - str: Predicted emotion label, or 'nan' if classification fails
            - Optional[float]: Always None for BERT (intensity not supported)

    Examples:
        >>> # Basic emotion classification
        >>> emotion, intensity = predict_emotion_bert("I love this!", False, False)
        >>> print(emotion)  # 'happy'
        >>> print(intensity)  # None

        >>> # Extended emotion classification
        >>> emotion, intensity = predict_emotion_bert("I love this!", True, False)
        >>> print(emotion)  # 'joy'
        >>> print(intensity)  # None

    Note:
        - Uses exponential backoff retry strategy for network failures
        - BERT API returns 28-class predictions mapped to basic or extended sets
        - Falls back to 'nan' on all failures rather than raising exceptions
        - Does not support intensity scoring (always returns None)

    Raises:
        Does not raise exceptions - returns ('nan', None) on all failures
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BERT_API_KEY}",
    }
    payload = {"inputs": [sentence]}
    try:
        resp = _BERT_SESSION.post(
            BERT_API_URL, headers=headers, json=payload, timeout=30
        )
        resp.raise_for_status()

        result = resp.json()
        if isinstance(result, str):
            result = json.loads(result)

        preds = result.get("predictions") or result.get("prediction")
        if isinstance(preds, list) and preds:
            idx = int(preds[0])
        else:
            idx = int(preds)

        label = _LABEL_MAP.get(idx, "nan")

        # for basic plan (no classify_ext, no intensity), collapse into one of 7
        if not classify_ext and not do_intensity:
            label = _BASIC_MAP.get(label, "neutral")

        log.info("BERT → %s", label)
        return label, None

    except Exception as e:
        log.error("Remote BERT failed: %s", e)
        return "nan", None

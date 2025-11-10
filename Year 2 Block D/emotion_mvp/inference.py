"""
Legacy Inference Module

This module provides legacy emotion classification functionality using LLaMA API.
It includes emotion prediction and review capabilities with prompt-based inference.

Note: This module is maintained for backward compatibility. New implementations
should use the classifier.py module for improved functionality and features.

Features:
- Direct LLaMA API integration
- Emotion validation against predefined sets
- Review and correction workflows
- Comprehensive error handling and fallbacks
"""

import re
import requests
import logging
from typing import Tuple

from .config import API_URL, TOKEN, VALID_EMOTIONS
from .prompts import PROMPT_TEMPLATE, REVIEW_TEMPLATE, FEW_SHOT_EXAMPLES

# 1. Get the standard logger
log = logging.getLogger(__name__)


def get_emotion(sentence: str, temperature: float = 0.5) -> Tuple[str, str]:
    """
    Get emotion classification for text using LLaMA API.

    Legacy function that calls LLaMA API for emotion classification.
    Uses predefined prompt templates and few-shot examples for inference.

    Args:
        sentence (str): Input text to classify
        temperature (float): Sampling temperature for LLaMA model (0.0-1.0).
                           Lower values make output more deterministic.

    Returns:
        Tuple[str, str]: A tuple containing:
            - str: Predicted emotion label or 'nan' on failure
            - str: The prompt that was sent to the API

    Raises:
        ValueError: If API_URL or TOKEN are not configured

    Examples:
        >>> emotion, prompt = get_emotion("I am very happy today!")
        >>> print(emotion)  # 'joy'
        >>> print(len(prompt) > 0)  # True

        >>> emotion, prompt = get_emotion("", 0.1)  # Low temperature
        >>> print(emotion)  # 'neutral' or 'nan'

    Note:
        - Falls back to 'nan' for unrecognized emotions
        - Validates results against VALID_EMOTIONS set
        - Includes comprehensive error handling
        - Legacy function - consider using classifier.py for new code
    """
    if not all([API_URL, TOKEN]):
        log.error("API_URL or TOKEN is not configured. Cannot make API calls.")
        raise ValueError("API_URL and TOKEN must be defined in emotion_mvp/config.py")

    prompt = PROMPT_TEMPLATE.format(
        few_shot_examples=FEW_SHOT_EXAMPLES, sentence=sentence
    )
    data = {
        "model": "llama3.2:3b",
        "messages": [
            {"role": "system", "content": "You are an expert emotion classifier."},
            {"role": "user", "content": prompt},
        ],
        "context_length": 100,
        "temperature": temperature,
    }

    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    log.info(f"Requesting emotion for sentence: '{sentence[:30]}...'")
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()

        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        log.debug(f"Initial API Response content: {content}")

        match = re.search(r"Answer:\s*([\w\s]+)", content)
        emotion = match.group(1).strip().lower() if match else content.strip().lower()

        if emotion not in VALID_EMOTIONS:
            log.warning(
                f"Emotion '{emotion}' not in VALID_EMOTIONS. Defaulting to 'nan'."
            )
            emotion = "nan"
        return emotion, prompt

    except requests.exceptions.RequestException:
        log.exception("Error during API call")
        return "nan", prompt
    except Exception:
        log.exception("An unexpected error occurred in get_emotion")
        return "nan", prompt


def review_emotion(
    sentence: str, predicted_emotion: str, actual_emotion: str, temperature: float = 0.5
) -> str:
    """
    Review and potentially correct emotion classification using LLaMA API.

    Legacy function that sends a review prompt to LLaMA for emotion correction.
    Compares predicted vs actual emotions and attempts to provide corrected
    classification based on the model's analysis.

    Args:
        sentence (str): Original text that was classified
        predicted_emotion (str): Initial model prediction
        actual_emotion (str): Ground truth or expected emotion
        temperature (float): Sampling temperature for model generation

    Returns:
        str: Reviewed emotion label, or original prediction on failure

    Examples:
        >>> corrected = review_emotion(
        ...     "I feel okay",
        ...     "joy",
        ...     "neutral",
        ...     0.3
        ... )
        >>> print(corrected)  # 'neutral' or 'joy' depending on model response

        >>> # API failure case
        >>> corrected = review_emotion("text", "anger", "joy", 0.5)
        >>> print(corrected in VALID_EMOTIONS or corrected == "anger")  # True

    Note:
        - Falls back to original prediction on API failures
        - Validates corrected emotions against VALID_EMOTIONS
        - Legacy function - consider using classifier.py for new implementations
        - Includes timeout and error handling for robustness
    """
    prompt = REVIEW_TEMPLATE.format(predicted=predicted_emotion, actual=actual_emotion)

    data = {
        "model": "llama3.2:3b",
        "messages": [
            {"role": "system", "content": "You are an expert emotion classifier."},
            {"role": "user", "content": prompt},
        ],
        "context_length": 100,
        "temperature": temperature,
    }

    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    log.info(f"Requesting review for prediction: '{predicted_emotion}'...")
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()

        result = response.json()
        reviewed_content = (
            result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        )
        log.debug(f"Reviewed API Response content: {reviewed_content}")

        match = re.search(r"Answer:\s*([\w\s]+)", reviewed_content)
        reviewed_emotion = (
            match.group(1).strip().lower() if match else predicted_emotion
        )

        if reviewed_emotion not in VALID_EMOTIONS:
            log.warning(
                f"Reviewed emotion '{reviewed_emotion}' not in VALID_EMOTIONS. Reverting to original prediction."
            )
            reviewed_emotion = predicted_emotion
        return reviewed_emotion

    except requests.exceptions.RequestException:
        log.exception("Error during review API call")
        return predicted_emotion
    except Exception:
        log.exception("An unexpected error occurred during review")
        return predicted_emotion

"""Tests for the emotion classification functionality.

This module contains unit tests for the emotion classifier module, testing
both BERT and LLaMA-based emotion classification models, including emotion
extraction, intensity scoring, and error handling.
"""

import pytest
from unittest.mock import patch, Mock
import emotion_mvp.classifier as classifier


# ─── _extract_emotion ────────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, expected",
    [
        ("Answer: Happy", "happy"),
        ("some random text", "some random text"),
        ("Answer:   SADNESS   ", "sadness"),
    ],
)
def test_extract_emotion(text, expected):
    """Test emotion extraction from model responses.

    Args:
        text: The response text from which to extract emotion.
        expected: The expected extracted emotion.

    Tests:
        - Proper extraction of emotions from formatted responses
        - Handling of different text formats
        - Case normalization and whitespace trimming
    """
    assert classifier._extract_emotion(text) == expected


# ─── predict_emotion_llama ──────────────────────────────────────────
@patch.object(classifier, "_call_llama")
def test_predict_emotion_llama_basic(mock_call_llama):
    """Test basic LLaMA emotion prediction without intensity.

    Args:
        mock_call_llama: Mock for the LLaMA API call.

    Tests:
        - Basic emotion prediction functionality
        - Proper emotion extraction from response
        - Intensity is None when not requested
    """
    mock_call_llama.return_value = "Answer: happy"
    emo, intensity = classifier.predict_emotion_llama(
        sentence="Test", classify_ext=False, do_intensity=False
    )
    assert emo == "happy"
    assert intensity is None


@patch.object(classifier, "_call_llama")
def test_predict_emotion_llama_out_of_list(mock_call_llama):
    """Test LLaMA prediction with unknown emotion response.

    Args:
        mock_call_llama: Mock for the LLaMA API call.

    Tests:
        - Fallback to 'neutral' for unknown emotions
        - Proper handling of unexpected responses
    """
    mock_call_llama.return_value = "Answer: unknown"
    emo, intensity = classifier.predict_emotion_llama(
        sentence="Test", classify_ext=False, do_intensity=False
    )
    assert emo == "neutral"
    assert intensity is None


@patch.object(classifier, "_call_llama")
def test_predict_emotion_llama_intensity(mock_call_llama):
    """Test LLaMA emotion prediction with intensity scoring.

    Args:
        mock_call_llama: Mock for the LLaMA API call.

    Tests:
        - Emotion prediction with intensity calculation
        - Proper parsing of intensity from response
        - Correct intensity score conversion
    """
    mock_call_llama.return_value = "Answer: sadness\nIntensity: strong"
    emo, intensity = classifier.predict_emotion_llama(
        sentence="Test", classify_ext=False, do_intensity=True
    )
    assert emo == "sadness"
    assert intensity == pytest.approx(0.75)


# ─── review_emotion_llama ──────────────────────────────────────────
@patch.object(classifier, "_call_llama")
def test_review_emotion_llama_basic(mock_call_llama):
    """Test LLaMA emotion review functionality.

    Args:
        mock_call_llama: Mock for the LLaMA API call.

    Tests:
        - Emotion review with predicted vs actual comparison
        - Basic review without intensity
        - Proper response processing
    """
    mock_call_llama.return_value = "Answer: happy"
    emo, intensity = classifier.review_emotion_llama(
        sentence="Test",
        predicted="happy",
        actual="joy",
        classify_ext=False,
        do_intensity=False,
    )
    assert emo == "happy"
    assert intensity is None


@patch.object(classifier, "_call_llama")
def test_review_emotion_llama_out_of_list(mock_call_llama):
    """Test LLaMA emotion review with invalid response.

    Args:
        mock_call_llama: Mock for the LLaMA API call.

    Tests:
        - Fallback to predicted emotion for invalid responses
        - Error handling in review process
    """
    mock_call_llama.return_value = "Answer: nonsense"
    emo, intensity = classifier.review_emotion_llama(
        sentence="Test",
        predicted="joy",
        actual="sad",
        classify_ext=False,
        do_intensity=False,
    )
    assert emo == "joy"
    assert intensity is None


# ─── predict_emotion_bert ──────────────────────────────────────────
@patch.object(classifier._BERT_SESSION, "post")
def test_predict_emotion_bert_success(mock_post):
    """Test successful BERT emotion prediction.

    Args:
        mock_post: Mock for HTTP POST request to BERT service.

    Tests:
        - Successful BERT API call
        - Proper response processing
        - Emotion ID to label mapping
    """
    mock_resp = Mock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json.return_value = {"predictions": ["17"]}
    mock_post.return_value = mock_resp
    emo, intensity = classifier.predict_emotion_bert("Hello", False, False)
    assert emo == "happy"
    assert intensity is None


@patch.object(classifier._BERT_SESSION, "post", side_effect=Exception("Oops"))
def test_predict_emotion_bert_exception(mock_post):
    """Test BERT emotion prediction with API failure.

    Args:
        mock_post: Mock for HTTP POST request that raises exception.

    Tests:
        - Exception handling in BERT prediction
        - Fallback to 'nan' on failure
        - Graceful error recovery
    """
    emo, intensity = classifier.predict_emotion_bert("Hi", False, False)
    assert emo == "nan"
    assert intensity is None


# ─── call llama fallback and success ───────────────────────────────
@patch("emotion_mvp.classifier.LLAMA_FALLBACK_MODELS", new=["fallback_url"])
@patch("emotion_mvp.classifier.requests.post")
def test__call_llama_fallback_and_success(mock_post):
    """Test LLaMA API call with fallback mechanism.

    Args:
        mock_post: Mock for HTTP POST requests.

    Tests:
        - Primary model failure handling
        - Successful fallback to secondary model
        - Proper response extraction from fallback
    """
    mock_post.side_effect = [
        Exception("primary down"),
        Mock(
            raise_for_status=lambda: None,
            json=lambda: {"choices": [{"message": {"content": "Answer: happy"}}]},
        ),
    ]
    out = classifier._call_llama([{"role": "user", "content": "x"}])
    assert out == "Answer: happy"

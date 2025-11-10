"""Tests for the main processing pipeline functionality.

This module contains unit tests for the pipeline module, testing the complete
emotion classification pipeline including input processing, format detection,
time parsing, and integration between all pipeline components.
"""

import csv
import pytest
from pathlib import Path

import emotion_mvp.pipeline as pipeline


@pytest.mark.parametrize(
    "src,expected",
    [
        ("song.mp3", True),
        ("audio.wav", True),
        ("http://example.com/file.ogg", True),
        ("https://youtu.be/xyz", True),
        ("document.txt", False),
        ("notes.csv", False),
        ("random", False),
    ],
)
def test_is_audio(src, expected):
    """Test audio file format detection.

    Args:
        src: Input source string to test.
        expected: Expected boolean result for audio detection.

    Tests:
        - Audio file extension recognition
        - URL-based audio format detection
        - YouTube URL identification
        - Non-audio format rejection
    """
    assert pipeline._is_audio(src) == expected


@pytest.mark.parametrize(
    "src,expected",
    [
        ("document.txt", True),
        ("notes.csv", True),
        ("audio.mp3", False),
        ("http://example.com/file.wav", False),
        ("random.ext", False),
    ],
)
def test_is_text(src, expected):
    """Test text file format detection.

    Args:
        src: Input source string to test.
        expected: Expected boolean result for text detection.

    Tests:
        - Text file extension recognition (txt, csv)
        - Audio format rejection for text detection
        - URL rejection for text file detection
        - Unknown extension handling
    """
    assert pipeline._is_text(src) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("http://youtube.com/watch?v=abc123", "abc123"),
        ("https://youtu.be/xyz789?t=10", "xyz789"),
        ("/path/to/file name!.mp3", "file_name_"),
        ("just_a_name", "just_a_name"),
    ],
)
def test_make_safe_stem(inp, expected):
    """Test safe filename stem generation from various inputs.

    Args:
        inp: Input string to process into safe filename.
        expected: Expected safe filename result.

    Tests:
        - YouTube URL video ID extraction
        - Special character replacement
        - Path-safe filename generation
        - File extension handling
    """
    assert pipeline._make_safe_stem(inp) == expected


@pytest.mark.parametrize(
    "ts,expected",
    [
        (0.0, "00:00:00,000"),
        (1.234, "00:00:01,234"),
        (3661.005, "01:01:01,005"),
    ],
)
def test_fmt(ts, expected):
    """Test timestamp formatting for subtitle format.

    Args:
        ts: Timestamp in seconds as float.
        expected: Expected formatted timestamp string.

    Tests:
        - Second to HH:MM:SS,mmm conversion
        - Proper zero padding for time components
        - Millisecond precision handling
        - Hour overflow handling
    """
    assert pipeline._fmt(ts) == expected


@pytest.mark.parametrize(
    "timestr,expected",
    [
        ("01:02:03", 3723.0),
        ("02:03", 123.0),
        ("4.5", 4.5),
    ],
)
def test_parse_timestr(timestr, expected):
    """Test time string parsing to seconds.

    Args:
        timestr: Time string in various formats.
        expected: Expected time in seconds as float.

    Tests:
        - HH:MM:SS format parsing
        - MM:SS format parsing
        - Simple decimal second parsing
        - Time format validation
    """
    assert pipeline._parse_timestr(timestr) == expected


def test_predict_any_csv_input(monkeypatch, tmp_path):
    """Test pipeline processing with CSV text input.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - CSV file processing through full pipeline
        - Text-based emotion classification
        - Output CSV generation and validation
        - Integration between pipeline components
    """
    inp = tmp_path / "input.csv"
    inp.write_text("Text\nHello world\nGoodbye")

    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "detect_lang", lambda t: "en")
    monkeypatch.setattr(pipeline, "translate", lambda t, lang: t)
    monkeypatch.setattr(
        pipeline, "predict_emotion_bert", lambda t, ext, it: ("joy", None)
    )
    monkeypatch.setattr(
        pipeline, "predict_emotion_llama", lambda t, ext, it: ("joy", None)
    )

    summary = pipeline.predict_any(
        inp=str(inp),
        model="base",
        do_translate=False,
        do_classify=True,
        do_classify_ext=False,
        do_intensity=False,
        persist=False,
    )

    out_csv_path = tmp_path / Path(summary["csv"]).name
    assert out_csv_path.exists()

    import csv as _csv

    with open(out_csv_path, newline="", encoding="utf-8") as f:
        rows = list(_csv.reader(f))

    assert rows[0] == ["start", "end", "sentence", "translation", "emotion"]
    assert rows[1][2] == "Hello world."
    assert rows[2][2] == "Goodbye."


def test_predict_any_fallback_plain_text(monkeypatch, tmp_path):
    """Test pipeline fallback to plain text processing.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - Plain text input processing through the pipeline
        - Fallback mechanism when no suitable input format is detected
        - CSV output generation from plain text input
    """
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    summary = pipeline.predict_any(
        inp="just a little test",
        model="base",
        do_translate=False,
        do_classify=False,
        do_classify_ext=False,
        do_intensity=False,
        persist=False,
    )
    out_csv = tmp_path / Path(summary["csv"]).name
    rows = list(csv.reader(out_csv.open()))
    assert len(rows) == 2
    assert rows[1][2] == "just a little test"


def test_predict_any_with_time_trimming(monkeypatch, tmp_path):
    """Test pipeline processing with audio time trimming.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - Audio time trimming based on start and end times
        - Integration of trimming with the overall pipeline processing
        - Correct handling of trimmed audio in emotion classification
    """
    wav = tmp_path / "audio.wav"
    wav.write_bytes(b"")
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(
        pipeline,
        "transcribe",
        lambda s: ("en", [{"start": 0.0, "end": 1.0, "text": "X"}]),
    )
    called = {}

    def fake_trim(src, st, et):
        called["src"], called["st"], called["et"] = src, st, et
        return src

    monkeypatch.setattr(pipeline, "_trim_audio", fake_trim)

    _ = pipeline.predict_any(
        inp=str(wav),
        model="base",
        do_translate=False,
        do_classify=False,
        do_classify_ext=False,
        do_intensity=False,
        start_time="00:00:05",
        end_time="00:00:06",
        persist=False,
    )
    assert called["st"] == 5.0 and called["et"] == 6.0


def test_predict_any_empty_csv_fallback(tmp_path, monkeypatch):
    """Test pipeline behavior with empty CSV input.

    Args:
        tmp_path: Pytest temporary directory fixture.
        monkeypatch: Pytest fixture for mocking dependencies.

    Tests:
        - Handling of empty CSV files as input
        - Fallback to default processing when no data is present
        - Proper logging and summary generation in fallback cases
    """
    inp = tmp_path / "empty.csv"
    inp.write_text("Text\n")

    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "detect_lang", lambda t: "en")
    monkeypatch.setattr(pipeline, "translate", lambda t, lang: t)
    monkeypatch.setattr(
        pipeline, "predict_emotion_bert", lambda t, ext, it: ("joy", None)
    )
    monkeypatch.setattr(
        pipeline, "predict_emotion_llama", lambda t, ext, it: ("joy", None)
    )

    calls = []
    monkeypatch.setattr(
        pipeline, "log_inference", lambda inp, summary: calls.append((inp, summary))
    )

    summary = pipeline.predict_any(
        inp=str(inp),
        model="base",
        do_translate=False,
        do_classify=True,
        do_classify_ext=False,
        do_intensity=False,
        persist=True,
    )

    out = tmp_path / Path(summary["csv"]).name
    import csv as _csv

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(_csv.reader(f))

    assert rows[1][2] == "Text."
    assert len(calls) == 1
    assert calls[0][0] == str(inp)


def test_predict_any_no_classify(monkeypatch, tmp_path):
    """Test pipeline processing with classification disabled.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - Emotion classification disabled in the pipeline
        - Proper handling of 'no classify' scenarios
        - Output consistency when classification is not performed
    """
    txt = tmp_path / "inp.txt"
    txt.write_text("Hello!")
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "detect_lang", lambda t: "en")

    summary = pipeline.predict_any(
        inp=str(txt),
        model="base",
        do_translate=False,
        do_classify=False,
        do_classify_ext=False,
        do_intensity=False,
        persist=False,
    )
    out_csv = tmp_path / Path(summary["csv"]).name
    rows = list(csv.reader(out_csv.open()))
    assert rows[1][4] == "nan"


def test_predict_any_llama_fallback_to_bert(monkeypatch, tmp_path):
    """Test pipeline fallback from LLaMA to BERT for emotion classification.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest temporary directory fixture.

    Tests:
        - Primary classification attempt using LLaMA
        - Fallback to BERT in case of LLaMA failure
        - Consistent and expected emotion classification results
    """
    txt = tmp_path / "inp.txt"
    txt.write_text("Oops.")
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path))
    monkeypatch.setattr(pipeline, "detect_lang", lambda t: "en")

    def llama_fail(text, ext, it):
        raise RuntimeError("nope")

    monkeypatch.setattr(pipeline, "predict_emotion_llama", llama_fail)
    monkeypatch.setattr(
        pipeline, "predict_emotion_bert", lambda t, ext, it: ("sad", None)
    )

    summary = pipeline.predict_any(
        inp=str(txt),
        model="base",
        do_translate=False,
        do_classify=True,
        do_classify_ext=True,
        do_intensity=False,
        persist=False,
    )
    out_csv = tmp_path / Path(summary["csv"]).name
    rows = list(csv.reader(out_csv.open()))
    assert rows[1][4] == "sad"

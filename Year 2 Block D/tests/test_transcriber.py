"""Tests for the audio transcription functionality.

This module contains unit tests for the transcriber module, testing audio
file transcription using Whisper, YouTube audio downloading, time trimming,
and error handling scenarios.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import shutil
import wave
import numpy as np
import emotion_mvp.transcriber as transcriber

# A standard sample rate for audio processing, required for creating a valid WAV file
SAMPLE_RATE = 16000


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_transcribe_local_file():
    """Test transcription with a valid local WAV file.

    Tests:
        - Local audio file transcription
        - Whisper model integration
        - Silent audio handling
        - Proper return format (language, segments)

    Note:
        Creates a valid, silent WAV file instead of an empty one to prevent ffmpeg errors.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        dummy_audio_path = tmpfile.name
    try:
        # Generate one second of silence and write it to the WAV file
        with wave.open(dummy_audio_path, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(SAMPLE_RATE)
            silent_frame = np.zeros(SAMPLE_RATE, dtype=np.int16).tobytes()
            wf.writeframes(silent_frame)

        result = transcriber.transcribe(dummy_audio_path)

        # Assertions to verify correct processing of the silent file
        assert isinstance(result, tuple)
        assert isinstance(result[0], str)  # Language
        assert isinstance(result[1], list)  # Segments
        full_text = "".join(segment.get("text", "") for segment in result[1])
        assert full_text.strip() == ""
    finally:
        Path(dummy_audio_path).unlink()


def test_transcribe_saves_transcript_return_value(monkeypatch):
    """Test that the transcribe function returns correct values from mocked model.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.

    Tests:
        - Whisper model mocking and response handling
        - Proper extraction of language and segments
        - Return value format validation
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        dummy_audio = tmp.name

    dummy_model = MagicMock()
    dummy_model.transcribe.return_value = {
        "text": "dummy transcription",
        "language": "en",
        "segments": ["segment1", "segment2"],
    }
    monkeypatch.setattr(
        transcriber, "whisper", MagicMock(load_model=lambda name: dummy_model)
    )

    output = transcriber.transcribe(dummy_audio)

    assert output[0] == "en"
    assert output[1] == ["segment1", "segment2"]
    Path(dummy_audio).unlink()


def test_download_youtube(monkeypatch):
    """Test YouTube audio downloading functionality.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.

    Tests:
        - yt-dlp integration for YouTube audio extraction
        - Output template handling and file creation
        - Mock simulation of download process

    Note:
        The mock correctly simulates how yt-dlp creates a file based on the
        outtmpl option, resolving the RuntimeError.
    """
    mock_base_path = Path(tempfile.gettempdir()) / "yt_mock_test"
    monkeypatch.setattr(
        transcriber.tempfile, "mktemp", lambda prefix: str(mock_base_path)
    )

    class DummyYDL:
        def __init__(self, opts):
            self.outtmpl = opts["outtmpl"]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def download(self, urls):
            output_file = Path(self.outtmpl % {"ext": "webm"})
            output_file.touch()

    monkeypatch.setattr(transcriber.yt_dlp, "YoutubeDL", DummyYDL)

    result = transcriber._download_youtube("https://youtube.com/fake")
    assert result.exists()
    assert result.name == "yt_mock_test.webm"
    result.unlink()


def test_download_generic(monkeypatch):
    """
    Test that _download_generic correctly fetches data and closes the file.
    NOTE: This test will only pass if the underlying function in `transcriber.py`
    is updated to properly close the file handle before returning.
    """
    dummy_url = "https://example.com/fake.wav"
    dummy_data = b"RIFF....WAVEfmt "

    class DummyResponse:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=8192):
            yield dummy_data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(transcriber.requests, "get", lambda *a, **k: DummyResponse())

    result_path = None
    try:
        # Assuming _download_generic is fixed to not leave the file open
        result_path = transcriber._download_generic(dummy_url)
        assert result_path.exists()
        assert result_path.read_bytes() == dummy_data
    finally:
        if result_path and result_path.exists():
            result_path.unlink()  # This should no longer raise PermissionError


def test__normalise_source_existing_file(tmp_path):
    """Test _normalise_source with an existing local file path."""
    f = tmp_path / "foo.txt"
    f.write_text("hi")
    p = transcriber._normalise_source(str(f))
    assert isinstance(p, Path) and p == f


def test__normalise_source_missing_file(tmp_path):
    """Test _normalise_source with a non-existent file path."""
    missing = tmp_path / "nope.mp3"
    with pytest.raises(FileNotFoundError):
        transcriber._normalise_source(str(missing))


def test__normalise_source_generic_url(monkeypatch, tmp_path):
    """Test _normalise_source with a generic URL."""
    dummy = tmp_path / "gen.wav"
    dummy.write_bytes(b"data")
    monkeypatch.setattr(transcriber, "_download_generic", lambda url: dummy)
    p = transcriber._normalise_source("http://example.com/audio.wav")
    assert p == dummy


def test__normalise_source_youtube_url(monkeypatch, tmp_path):
    """Test _normalise_source with a YouTube URL."""
    dummy = tmp_path / "yt.webm"
    dummy.write_bytes(b"data")
    monkeypatch.setattr(transcriber, "_download_youtube", lambda url: dummy)
    p = transcriber._normalise_source("https://youtu.be/abc123")
    assert p == dummy


def test_download_youtube_no_files(monkeypatch):
    """Test that _download_youtube raises an error if no file is downloaded."""
    tmp = Path(tempfile.mktemp(prefix="yt_"))
    monkeypatch.setattr(transcriber.tempfile, "mktemp", lambda prefix: str(tmp))

    class DummyYDL:
        def __init__(self, opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def download(self, urls):
            pass  # Simulate downloading nothing

    monkeypatch.setattr(transcriber.yt_dlp, "YoutubeDL", DummyYDL)
    with pytest.raises(RuntimeError):
        transcriber._download_youtube("https://youtube.com/nothing")


def test_transcribe_saves_transcript(monkeypatch, tmp_path):
    """Test that the transcript is saved to a file if the environment variable is set."""
    dummy_audio = tmp_path / "a.wav"
    dummy_audio.write_bytes(b"data")

    dummy_model = MagicMock()
    dummy_model.transcribe.return_value = {
        "text": "transcribed text",
        "language": "en",
        "segments": [],
    }

    monkeypatch.setenv("WHISPER_MODEL", "tiny")
    monkeypatch.setenv("SAVE_TRANSCRIPTS", "1")
    monkeypatch.setenv("TRANSCRIPT_DIR", str(tmp_path / "out"))
    monkeypatch.setattr(
        transcriber, "whisper", MagicMock(load_model=lambda name: dummy_model)
    )

    lang, segs = transcriber.transcribe(str(dummy_audio))
    saved = tmp_path / "out" / (dummy_audio.stem + ".txt")
    assert saved.exists()
    assert saved.read_text() == "transcribed text"


@pytest.fixture(autouse=True)
def _cleanup_env(monkeypatch):
    """A fixture to automatically clean up environment variables after each test."""
    for var in ["SAVE_TRANSCRIPTS", "TRANSCRIPT_DIR"]:
        monkeypatch.delenv(var, raising=False)
    yield

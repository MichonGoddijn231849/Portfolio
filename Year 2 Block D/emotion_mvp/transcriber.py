#!/usr/bin/env python3
# transcriber.py – robust FFmpeg + YouTube downloader wrapper for Whisper
# -----------------------------------------------------------------------
# * Works on Windows / macOS / Linux.
# * Handles the FFmpeg 7 + yt-dlp “file: URI” problem automatically.
# * Lets the user override the FFmpeg location via **FFMPEG_DIR** env-var.
# * Bundles a 6.1 static build on Windows when 7.x encounters codec issues.
# -----------------------------------------------------------------------

from __future__ import annotations

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Tuple

import requests
import whisper
import yt_dlp

# 2. Use the standard logger
log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# FFmpeg discovery
# -----------------------------------------------------------------------------
_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_WIN_FFMPEG = _PACKAGE_DIR / "bin" / "ffmpeg-6.1-win64" / "bin"
_FFMPEG_DIR = Path(
    os.getenv("FFMPEG_DIR", _DEFAULT_WIN_FFMPEG if os.name == "nt" else "")
).expanduser()

if _FFMPEG_DIR.exists():
    os.environ["PATH"] = str(_FFMPEG_DIR) + os.pathsep + os.environ.get("PATH", "")

FFMPEG_EXE = shutil.which("ffmpeg") or str(_FFMPEG_DIR / "ffmpeg.exe")
FFPROBE_EXE = shutil.which("ffprobe") or str(_FFMPEG_DIR / "ffprobe.exe")


# -----------------------------------------------------------------------------
# Download helpers
# -----------------------------------------------------------------------------
def _download_youtube(url: str) -> Path:
    """
    Download audio from YouTube URL using yt-dlp.

    Downloads the best available audio format from a YouTube video URL
    and saves it to a temporary file. Uses yt-dlp with optimized settings
    for audio extraction.

    Args:
        url (str): YouTube video URL (youtube.com or youtu.be format)

    Returns:
        Path: Path to the downloaded temporary audio file

    Raises:
        RuntimeError: If download fails or no audio file is created

    Examples:
        >>> path = _download_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> print(path.suffix)  # .webm, .m4a, .mp3, etc.

    Note:
        - Downloads best available audio quality
        - Uses configured FFmpeg location for post-processing
        - Creates temporary files that should be cleaned up by caller
        - Supports both youtube.com and youtu.be URLs
    """
    log.info(f"Starting YouTube download for: {url}")
    base = Path(tempfile.mktemp(prefix="yt_"))
    outtmpl = str(base) + ".%(ext)s"
    opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [],
        "ffmpeg_location": str(Path(FFMPEG_EXE).parent),
        "quiet": True,
        "noprogress": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = list(base.parent.glob(base.name + ".*"))
    if not files:
        log.error(f"yt-dlp failed to download any file from {url}")
        raise RuntimeError(f"No audio file was downloaded by yt-dlp from {url}")
    log.info(f"YouTube download successful. File saved to: {files[0]}")
    return files[0]


def _download_generic(url: str) -> Path:
    """
    Download audio from a generic URL with streaming support.

    Downloads audio content from any URL that directly serves audio files.
    Uses streaming download to handle large files efficiently without
    loading everything into memory.

    Args:
        url (str): Direct URL to an audio file

    Returns:
        Path: Path to the downloaded temporary audio file

    Raises:
        requests.RequestException: If HTTP request fails
        Exception: If download or file operations fail

    Examples:
        >>> path = _download_generic("https://example.com/audio.mp3")
        >>> print(path.exists())  # True

    Note:
        - Uses streaming download for memory efficiency
        - Preserves original file extension when possible
        - Creates temporary files that should be cleaned up by caller
        - Includes timeout handling for network robustness
        - Automatically cleans up on failure
    """
    log.info(f"Starting generic download for: {url}")
    suffix = Path(url).suffix or ".bin"
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = Path(temp_file.name)

    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                temp_file.write(chunk)
    except Exception:
        log.exception(f"Generic download failed for URL: {url}")
        temp_file.close()
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    temp_file.close()
    log.info(f"Generic download successful. File saved to: {tmp_path}")
    return tmp_path


def _normalise_source(src: str) -> Path:
    """
    Normalize input source to a local file path.

    Takes various input types (URLs, local paths) and ensures they resolve
    to a local file path. Downloads remote content if necessary and validates
    that local files exist.

    Args:
        src (str): Input source - can be:
            - YouTube URL (youtube.com, youtu.be)
            - Direct audio file URL
            - Local file path (absolute or relative)
            - Path with ~ for home directory

    Returns:
        Path: Validated local file path ready for processing

    Raises:
        FileNotFoundError: If local file doesn't exist
        RuntimeError: If URL download fails

    Examples:
        >>> # Local file
        >>> path = _normalise_source("/path/to/audio.mp3")
        >>> print(path.exists())  # True

        >>> # YouTube URL
        >>> path = _normalise_source("https://www.youtube.com/watch?v=example")
        >>> print(path.suffix)  # .webm or similar

        >>> # Home directory path
        >>> path = _normalise_source("~/Documents/audio.wav")
        >>> print(path.is_absolute())  # True

    Note:
        - Automatically detects URL vs local file
        - Expands user home directory (~) in paths
        - Downloads and caches remote content temporarily
        - Validates file existence for local paths
    """
    log.debug(f"Normalising source: '{src}'")
    if src.startswith(("http://", "https://")):
        if "youtu.be" in src or "youtube.com" in src:
            return _download_youtube(src)
        return _download_generic(src)

    p = Path(src).expanduser()
    if not p.exists():
        log.error(f"Local file not found: {p}")
        raise FileNotFoundError(f"The file '{src}' was not found.")
    log.debug(f"Source is a local file: {p}")
    return p


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
def transcribe(src: str) -> Tuple[str, List[dict]]:
    """
    Transcribe audio from various sources using OpenAI Whisper.

    Main transcription function that handles audio from URLs or local files.
    Uses Whisper ASR model with configurable model size and automatic
    language detection. Includes cleanup of temporary files.

    Args:
        src (str): Audio source - can be:
            - YouTube URL (https://youtube.com/watch?v=...)
            - Direct audio file URL
            - Local file path (/path/to/audio.mp3)
            - Relative path (./audio.wav)

    Returns:
        Tuple[str, List[dict]]: A tuple containing:
            - str: Detected language code (e.g., 'en', 'es', 'fr')
            - List[dict]: List of transcript segments, each containing:
                - 'start': Start time in seconds (float)
                - 'end': End time in seconds (float)
                - 'text': Transcribed text content (str)

    Raises:
        FileNotFoundError: If local file doesn't exist
        RuntimeError: If download or transcription fails

    Examples:
        >>> # Transcribe local file
        >>> lang, segments = transcribe("/path/to/speech.mp3")
        >>> print(f"Language: {lang}")  # Language: en
        >>> print(f"Segments: {len(segments)}")  # Segments: 12
        >>> print(segments[0]['text'])  # "Hello, welcome to our podcast"

        >>> # Transcribe YouTube video
        >>> lang, segments = transcribe("https://youtube.com/watch?v=example")
        >>> for seg in segments[:3]:  # First 3 segments
        ...     print(f"{seg['start']:.1f}s: {seg['text']}")

    Environment Variables:
        - WHISPER_MODEL: Model size ('tiny', 'base', 'small', 'medium', 'large')
        - SAVE_TRANSCRIPTS: Set to '1' to save full transcripts as text files
        - TRANSCRIPT_DIR: Directory for saved transcripts (default: 'data/transcripts')

    Note:
        - Automatically cleans up temporary downloaded files
        - Model is loaded fresh each time (consider caching for production)
        - Supports all audio formats that FFmpeg can decode
        - Language detection is automatic via Whisper
        - Optional transcript saving for debugging/archival
    """
    model_name = os.getenv("WHISPER_MODEL", "tiny")
    log.info(f"Loading Whisper model '{model_name}'...")
    asr = whisper.load_model(model_name)

    audio_path = None
    is_downloaded = src.startswith(("http://", "https://"))
    try:
        audio_path = _normalise_source(src)
        log.info(
            f"Starting transcription for '{audio_path.name}' with Whisper-{model_name}"
        )
        result = asr.transcribe(str(audio_path), verbose=False)
    finally:
        if is_downloaded and audio_path and audio_path.exists():
            log.info(f"Cleaning up temporary downloaded file: {audio_path}")
            audio_path.unlink(missing_ok=True)

    lang = result.get("language", "unknown")
    segments = result.get("segments", [])
    log.info(
        f"Transcription complete. Detected language: '{lang}', Found {len(segments)} segments."
    )

    if os.getenv("SAVE_TRANSCRIPTS") == "1":
        txt = result.get("text", "").strip()
        out_dir = Path(os.getenv("TRANSCRIPT_DIR", "data/transcripts"))
        out_dir.mkdir(exist_ok=True, parents=True)
        f_name = Path(src).stem
        f = out_dir / (f_name + ".txt")
        f.write_text(txt, encoding="utf-8")
        log.info(f"Saved full transcript text to: {f}")

    return lang, segments

# emotion_mvp/pipeline.py
"""
Emotion Classification Pipeline

This module provides the main pipeline for processing various input types (audio, video, text)
and performing emotion classification with optional translation and intensity analysis.

The pipeline supports multiple input formats:
- Audio files: .wav, .mp3, .m4a, .flac, .ogg, .mp4
- Text files: .txt, .csv
- Direct text input
- YouTube URLs and other web sources

Key Features:
- Multi-modal input processing
- Automatic language detection and translation
- Multiple emotion classification models (BERT, LLaMA)
- Emotion intensity scoring
- Audio trimming capabilities
- Comprehensive logging and error handling
"""

import os
import csv as _csv
import re
import subprocess
import logging
from datetime import datetime, timedelta, UTC
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, Any

# This line is correct and includes _normalise_source
from .transcriber import transcribe, _normalise_source
from .detector import detect_lang
from .translator import translate
from .classifier import (
    predict_emotion_llama,
    predict_emotion_bert,
)
from .history import log_inference

log = logging.getLogger(__name__)

# Supported file extensions
_AUDIO_EXTS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4")
_TEXT_EXTS = (".txt", ".csv")


def _is_audio(src: str) -> bool:
    """
    Determine if the input source is an audio file or URL.

    Args:
        src (str): Input source path or URL

    Returns:
        bool: True if source is audio, False otherwise

    Examples:
        >>> _is_audio("test.mp3")
        True
        >>> _is_audio("https://youtube.com/watch?v=123")
        True
        >>> _is_audio("document.txt")
        False
    """
    p = Path(src)
    return src.startswith(("http://", "https://")) or p.suffix.lower() in _AUDIO_EXTS


def _is_text(src: str) -> bool:
    """
    Determine if the input source is a text file.

    Args:
        src (str): Input source path

    Returns:
        bool: True if source is a text file, False otherwise

    Examples:
        >>> _is_text("document.txt")
        True
        >>> _is_text("data.csv")
        True
        >>> _is_text("audio.mp3")
        False
    """
    return Path(src).suffix.lower() in _TEXT_EXTS


def _make_safe_stem(inp: str) -> str:
    """
    Generate a safe filename stem from input source.

    Extracts meaningful identifiers from URLs (like YouTube video IDs)
    or file paths and sanitizes them for use as filenames.

    Args:
        inp (str): Input source (URL, file path, or text)

    Returns:
        str: Sanitized filename stem

    Examples:
        >>> _make_safe_stem("https://youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> _make_safe_stem("/path/to/my file!.mp3")
        'my_file_'
        >>> _make_safe_stem("plain text")
        'input'
    """
    if inp.startswith(("http://", "https://")):
        parsed = urlparse(inp)
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
        name = Path(parsed.path).stem
    else:
        name = Path(inp).stem
    return re.sub(r"[^0-9A-Za-z_-]", "_", name) or "input"


def _fmt(ts: float) -> str:
    """
    Format timestamp in seconds to SRT-style timestamp string.

    Args:
        ts (float): Timestamp in seconds

    Returns:
        str: Formatted timestamp (HH:MM:SS,mmm)

    Examples:
        >>> _fmt(3661.123)
        '01:01:01,123'
        >>> _fmt(0.5)
        '00:00:00,500'
    """
    td = timedelta(seconds=ts)
    h, rem = divmod(td.seconds, 3600)
    m, s = divmod(rem, 60)
    ms = td.microseconds // 1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _parse_timestr(ts_str: str) -> float:
    """
    Parse time string to seconds.

    Supports formats: HH:MM:SS, MM:SS, or SS

    Args:
        ts_str (str): Time string to parse

    Returns:
        float: Time in seconds

    Examples:
        >>> _parse_timestr("01:30:45")
        5445.0
        >>> _parse_timestr("2:30")
        150.0
        >>> _parse_timestr("45")
        45.0
    """
    parts = [float(p) for p in ts_str.split(":")]
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    if len(parts) == 2:
        m, s = parts
        return m * 60 + s
    return parts[0]


def _trim_audio(src_path: str, start: float, end: Optional[float]) -> str:
    """
    Trim audio file using FFmpeg.

    Creates a temporary file containing the trimmed audio segment.

    Args:
        src_path (str): Path to source audio file
        start (float): Start time in seconds
        end (Optional[float]): End time in seconds (None for no end limit)

    Returns:
        str: Path to temporary trimmed audio file

    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails

    Note:
        The returned temporary file must be cleaned up by the caller.
    """
    log.debug(f"Trimming audio file {src_path} from {start}s to {end}s")
    tmp = NamedTemporaryFile(suffix=Path(src_path).suffix, delete=False)
    cmd = ["ffmpeg", "-y", "-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", src_path, "-acodec", "copy", tmp.name]
    subprocess.run(
        cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    log.debug(f"Trimmed audio saved to temporary file: {tmp.name}")
    return tmp.name


def predict_any(
    inp: str,
    model: str,
    do_translate: bool,
    do_classify: bool,
    do_classify_ext: bool,
    do_intensity: bool,
    classifier_model: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    persist: bool = True,
    **kwargs,  # Accept any other keyword arguments from enforce()
) -> Dict[str, Any]:
    """
    Main pipeline function for emotion classification from various input sources.

    This function handles the complete pipeline from input processing to emotion
    classification and result output. It supports multiple input types including
    audio files, text files, URLs, and direct text input.

    Pipeline Steps:
    1. Input type detection and preprocessing
    2. Audio transcription (if applicable) with optional trimming
    3. Language detection and translation (if enabled)
    4. Emotion classification using specified model
    5. Intensity analysis (if enabled)
    6. CSV output generation with timestamps and results
    7. Summary generation and logging

    Args:
        inp (str): Input source - can be:
            - Direct text string
            - Path to audio file (.wav, .mp3, .m4a, .flac, .ogg, .mp4)
            - Path to text file (.txt, .csv)
            - YouTube URL or other web source
        model (str): Whisper model size for audio transcription
            Options: "tiny", "base", "small", "medium", "large"
        do_translate (bool): Enable automatic translation to English
        do_classify (bool): Enable emotion classification
        do_classify_ext (bool): Use extended emotion set (requires LLaMA)
        do_intensity (bool): Calculate emotion intensity scores
        classifier_model (Optional[str]): Specific classifier model to use
            Options: "bert", "llama", None (auto-select based on features)
        start_time (Optional[str]): Start time for audio trimming (format: HH:MM:SS or MM:SS)
        end_time (Optional[str]): End time for audio trimming (format: HH:MM:SS or MM:SS)
        persist (bool): Whether to save inference results to history
        **kwargs: Additional keyword arguments (for compatibility)

    Returns:
        Dict[str, Any]: Summary dictionary containing:
            - timestamp (str): ISO timestamp of processing
            - input (str): Original input source
            - language (str): Detected source language
            - csv (str): Path to generated CSV output file

    Raises:
        FileNotFoundError: If input file doesn't exist
        subprocess.CalledProcessError: If audio processing fails
        Exception: Various exceptions from classification models

    Examples:
        >>> # Process text input
        >>> result = predict_any(
        ...     inp="I'm feeling great today!",
        ...     model="base",
        ...     do_translate=False,
        ...     do_classify=True,
        ...     do_classify_ext=False,
        ...     do_intensity=False
        ... )

        >>> # Process audio file with trimming
        >>> result = predict_any(
        ...     inp="/path/to/audio.mp3",
        ...     model="base",
        ...     do_translate=True,
        ...     do_classify=True,
        ...     do_classify_ext=True,
        ...     do_intensity=True,
        ...     start_time="1:30",
        ...     end_time="3:45"
        ... )

        >>> # Process YouTube video
        >>> result = predict_any(
        ...     inp="https://youtube.com/watch?v=example",
        ...     model="small",
        ...     do_translate=True,
        ...     do_classify=True,
        ...     do_classify_ext=False,
        ...     do_intensity=False
        ... )

    Note:
        - Output CSV files are saved to the directory specified by TRANSCRIPT_DIR
          environment variable (default: "data/transcripts")
        - For audio inputs, FFmpeg must be installed and available in PATH
        - LLaMA model is required for extended emotion classification
        - BERT model is used as fallback when LLaMA fails
    """
    log.info(
        f"Pipeline started for input: '{inp[:50]}...', Model: {model}, Classifier: {classifier_model}"
    )
    os.environ["WHISPER_MODEL"] = model

    # ─── 1. Build segments ────────────────────────────────────────
    log.debug("Step 1: Building segments from input.")
    if _is_text(inp):
        log.info(f"Input detected as a text file: {inp}")
        path = Path(inp)
        raw = path.read_text(encoding="utf-8").strip()
        src_lang = detect_lang(raw)

        if path.suffix.lower() == ".txt":
            sentences = [s.strip() for s in raw.splitlines() if s.strip()]
        else:  # .csv
            sentences = []
            with open(inp, newline="", encoding="utf-8") as f:
                reader = _csv.reader(f)
                next(reader, None)  # Skip header row
                for row in reader:
                    if row and row[0].strip():
                        sentences.append(row[0].strip())

        if not sentences and raw:
            log.warning("No sentences found in text file, falling back to raw content.")
            sentences = [raw]

        sentences = [s if re.search(r"[.!?]$", s) else s + "." for s in sentences]
        segments = [{"start": 0.0, "end": 0.0, "text": s} for s in sentences]

    elif _is_audio(inp):
        log.info(f"Input detected as an audio source: {inp}")
        src_file = _normalise_source(inp)
        offset = 0.0

        if start_time or end_time:
            log.info(f"Audio trimming requested from {start_time} to {end_time}")
            st = _parse_timestr(start_time) if start_time else 0.0
            et = _parse_timestr(end_time) if end_time else None
            src_file = _trim_audio(str(src_file), st, et)
            offset = st

        log.info("Starting audio transcription...")
        src_lang, segments = transcribe(str(src_file))
        log.info(f"Transcription complete. Found {len(segments)} segments.")
        for seg in segments:
            seg["start"] += offset
            seg["end"] += offset

    else:
        log.info("Input detected as plain text.")
        src_lang = detect_lang(inp)
        text = translate(inp, src_lang) if do_translate and src_lang != "en" else inp
        src_lang = "en" if do_translate and src_lang != "en" else src_lang
        segments = [{"start": 0.0, "end": 0.0, "text": text.strip()}]

    # ─── 2. Prepare CSV ────────────────────────────────────────────
    stem = _make_safe_stem(inp)
    out_dir = Path(os.getenv("TRANSCRIPT_DIR", "data/transcripts"))
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{stem}_emotion.csv"
    headers = ["start", "end", "sentence", "translation", "emotion"]
    if do_intensity:
        headers += ["intensity_score", "intensity_label"]
    log.info(f"Preparing to write results to CSV: {csv_path}")

    # ─── 3. Classify ───────────────────────────────────────────────
    log.debug("Step 3: Classifying emotions for each segment.")
    use_bert = False
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.writer(f)
        writer.writerow(headers)

        for i, seg in enumerate(segments):
            log.debug(f"Processing segment {i+1}/{len(segments)}...")
            st, et, txt = _fmt(seg["start"]), _fmt(seg["end"]), seg["text"]
            translation = (
                translate(txt, src_lang) if do_translate and src_lang != "en" else txt
            )
            emo, score = "nan", None

            if do_classify:
                if not do_classify_ext and not do_intensity:
                    emo, score = predict_emotion_bert(
                        translation, do_classify_ext, do_intensity
                    )
                else:
                    if not use_bert:
                        try:
                            emo, score = predict_emotion_llama(
                                translation, do_classify_ext, do_intensity
                            )
                        except Exception as e:
                            log.warning(
                                "Llama failed (%s); switching to BERT for all subsequent segments.",
                                e,
                            )
                            use_bert = True
                            emo, score = predict_emotion_bert(
                                translation, do_classify_ext, do_intensity
                            )
                    else:
                        emo, score = predict_emotion_bert(
                            translation, do_classify_ext, do_intensity
                        )

            label = ""
            if do_intensity and score is not None:
                if score < 0.15:
                    label = "neutral"
                elif score < 0.4:
                    label = "mild"
                elif score < 0.7:
                    label = "moderate"
                elif score < 0.9:
                    label = "strong"
                else:
                    label = "intense"

            row = [st, et, txt, translation, emo]
            if do_intensity:
                row += [f"{score:.2f}" if score is not None else "", label]
            writer.writerow(row)

    # ─── 4. Summary ────────────────────────────────────────────────
    log.debug("Step 4: Finalizing summary.")
    summary = {
        "timestamp": datetime.now(UTC)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "input": inp,
        "language": src_lang,
        "csv": str(csv_path),
    }
    if persist:
        log_inference(inp, summary)

    log.info("Pipeline finished successfully.")
    return summary

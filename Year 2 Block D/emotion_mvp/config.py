# emotion_mvp/config.py
"""
Configuration Module

This module centralizes all configuration settings for the Emotion MVP system.
It handles environment variable loading, path configuration, API endpoints,
model settings, and other system-wide parameters.

Configuration Sources:
- Environment variables (via .env file or system environment)
- Default values for development/testing
- Dynamic values based on runtime conditions

Key Configuration Areas:
- File paths and directories
- LLaMA API settings and fallback models
- BERT model configuration
- Translation model mappings
- Valid emotion labels
- History logging settings
- Remote API endpoints and authentication
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

CSV_PATH = os.getenv("CSV_PATH", str(DATA / "Data_v2.csv"))

# ─── LLaMA settings ─────────────────────────────────────────────────────
LLAMA_API_URL = os.getenv(
    "LLAMA_API_URL",
    "http://194.171.191.227:30080/api/chat/completions",
)
LLAMA_MODEL_ID = os.getenv("LLAMA_MODEL_ID", "llama3.2:3b")
LLAMA_FALLBACK_MODELS = [
    m.strip() for m in os.getenv("LLAMA_FALLBACK_MODELS", "").split(",") if m.strip()
]
LLAMA_TOKEN = os.getenv("LLAMA_TOKEN")  # may be None
API_URL = os.getenv("API_URL", LLAMA_API_URL)
# ─── BERT settings ──────────────────────────────────────────────────────
BERT_MODEL_NAME = os.getenv("BERT_MODEL_NAME", "/app/emotion_mvp/rafal_bert_model")
BERT_LABELS = [
    lbl.strip().lower()
    for lbl in os.getenv("BERT_LABELS", "").split(",")
    if lbl.strip()
]

# Hugging Face models location & translation map
MODELS_PATH = ROOT / ".hf_models"
SUPPORTED_TRANSLATORS = {
    "de": "opus-mt-de-en",
    "nl": "opus-mt-nl-en",
    "fr": "opus-mt-fr-en",
    "es": "opus-mt-es-en",
}

# List of emotions expected throughout the package
VALID_EMOTIONS = {
    "excitement",
    "confusion",
    "surprise",
    "neutral",
    "optimism",
    "pride",
    "curiosity",
    "fear",
    "amusement",
    "joy",
    "desire",
    "annoyance",
    "nervousness",
    "gratitude",
    "approval",
    "realization",
    "disappointment",
    "caring",
    "sadness",
    "admiration",
    "disapproval",
    "anger",
    "remorse",
    "relief",
    "love",
    "disgust",
    "embarrassment",
}

# ─── History log file ────────────────────────────────────────────────────
STAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
HISTORY_FILE = os.getenv("HISTORY_CSV", str(DATA / f"inference_{STAMP}.csv"))

# ─── Remote BERT API override (optional) ────────────────────────────────
BERT_API_URL = os.getenv(
    "BERT_API_URL",
    "http://194.171.191.227:30526/api/v1/endpoint/edoardo-fastapi-endpoint/score",
)
BERT_API_KEY = os.getenv(
    "BERT_API_KEY",
    "DGb3jHUm0CNAqxHxXhKuSf2zLY3zYkoRbDQ0pcghaSNgOlPcC7XvJQQJ99BFAAAAAAAAAAAAINFRAZML1wJV",
)

# ─── Generic token expected by cli_main & helpers ───────────────────────
#
# Use LLAMA_TOKEN if present; else look for an OPENAI_TOKEN in env,
# and finally fall back to a harmless placeholder so unit tests never fail.
# -----------------------------------------------------------------------
TOKEN = LLAMA_TOKEN or os.getenv("OPENAI_TOKEN") or "dummy-token"

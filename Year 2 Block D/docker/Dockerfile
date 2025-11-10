# ─────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TRANSFORMERS_CACHE=/opt/.cache \
    POETRY_VERSION=1.8.2

# ─── Install OS packages + Poetry ───────────────────────────
RUN apt-get update \
 && apt-get install --no-install-recommends -y \
      build-essential \
      git \
      ffmpeg \
      curl \
      unzip \
 && pip install "poetry==$POETRY_VERSION" \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Step 5: Install Python dependencies (cached) ────────────
# This layer will only rerun if pyproject.toml or poetry.lock change.
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction

# ─── Copy application code ───────────────────────────────────
COPY emotion_mvp /app/emotion_mvp

# ─── Copy any existing transcripts ───────────────────────────
COPY data/transcripts /app/data/transcripts

# ─── Extra Python packages ──────────────────────────────────
RUN pip install sentencepiece==0.1.99

# ─── Drop root privileges ────────────────────────────────────
RUN adduser --disabled-password --gecos "" appuser \
 && mkdir -p /opt/.cache \
 && chown -R appuser:appuser /app /opt/.cache

USER appuser

EXPOSE 8000

CMD ["uvicorn", "emotion_mvp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

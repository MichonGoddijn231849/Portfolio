# tests/test_api_main.py
"""Tests for the main API endpoints."""

import io
import pytest
from fastapi.testclient import TestClient

from emotion_mvp.api.main import app

client = TestClient(app)


@pytest.fixture
def dummy_text_file():
    """Create a dummy text file for testing file uploads."""
    return io.BytesIO(b"Hello, this is a dummy transcript.")


def test_predict_with_src(monkeypatch):
    """Test /predict-any with a src parameter."""

    def fake_predict_any(**kwargs):
        return {"csv": "data/transcripts/fake.csv"}

    monkeypatch.setattr("emotion_mvp.api.main.predict_any", fake_predict_any)

    response = client.post("/predict-any", data={"src": "dummy.txt"})
    assert response.status_code == 200

    data = response.json()
    assert "download" in data
    # the API strips the path and returns only the filename
    assert data["download"]["filename"] == "fake.csv"


def test_predict_with_file(monkeypatch, dummy_text_file):
    """Test /predict-any with an uploaded file."""

    def fake_predict_any(**kwargs):
        return {"csv": "data/transcripts/uploaded.csv"}

    monkeypatch.setattr("emotion_mvp.api.main.predict_any", fake_predict_any)

    response = client.post(
        "/predict-any",
        files={"file": ("test.txt", dummy_text_file, "text/plain")},
    )
    assert response.status_code == 200

    data = response.json()
    assert "download" in data
    assert data["download"]["filename"] == "uploaded.csv"


def test_predict_missing_input():
    """Test /predict-any with no src and no file."""
    response = client.post("/predict-any")
    assert response.status_code == 400

    data = response.json()
    # must exactly match the current detail message
    assert data["detail"] == "Provide either 'src' or an uploaded file."


def test_predict_internal_error(monkeypatch):
    """Test /predict-any when predict_any raises."""

    def fail_predict_any(**kwargs):
        raise RuntimeError("Simulated failure")

    monkeypatch.setattr("emotion_mvp.api.main.predict_any", fail_predict_any)

    response = client.post("/predict-any", data={"src": "dummy.txt"})
    assert response.status_code == 500

    data = response.json()
    # must exactly match your Pipeline error wording
    assert data["detail"] == "Pipeline error: Simulated failure"

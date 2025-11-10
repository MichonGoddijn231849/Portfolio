from __future__ import annotations

import csv
import io
import logging
import os
import time
from pathlib import Path
from typing import Any, List, Optional

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

from .plan_gate import Plan, enforce
from emotion_mvp.pipeline import predict_any

# ─────────────────────────────── Constants / logging ──────────────────────
RAW_PREFIX = "raw"
LOCAL_DIR = Path("data/transcripts")

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# ─────────────────────────────────── FastAPI ─────────────────────────────
app = FastAPI(title="Emotion-MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=LOCAL_DIR), name="files")

# ───────────────────────────── Azure Blob client (optional) ───────────────
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

CONTAINER_CLIENT: BlobServiceClient | None = None
if all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, ACCOUNT_NAME, CONTAINER]):
    try:
        credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        service = BlobServiceClient(
            f"https://{ACCOUNT_NAME}.blob.core.windows.net",
            credential=credential,
        )
        CONTAINER_CLIENT = service.get_container_client(CONTAINER)
        LOGGER.info(
            "Azure Blob client initialised for container '%s'",
            CONTAINER,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Could not initialise Azure Blob: %s", exc, exc_info=True)
else:
    LOGGER.warning("Azure env-vars missing – Blob uploads will be skipped.")

# ─────────────────────────────── Helper functions ─────────────────────────


def plan_dependency(request: Request) -> Plan:  # noqa: D401
    """Return Plan instance for the incoming request."""
    return Plan(request.headers.get("x-plan", "basic"))


def upload_blob_safe(
    name: str,
    data: Any,
    content_type: str | None = None,
) -> None:  # noqa: ANN401
    """Upload to Azure; log warning if it fails or Azure is disabled."""
    if CONTAINER_CLIENT is None:
        return

    try:
        CONTAINER_CLIENT.upload_blob(
            name=name,
            data=data,
            overwrite=True,
            content_type=content_type,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Blob upload failed (%s): %s", name, exc)


# ─────────────────────────────── Pydantic models ──────────────────────────


class TranscriptSegment(BaseModel):
    id: int
    start: str
    end: str
    sentence: str
    translation: str
    emotion: str


class FeedbackPayload(BaseModel):
    correct: bool
    corrections: Optional[List[TranscriptSegment]] = None


# ─────────────────────────────── Prediction endpoint ──────────────────────


@app.post("/predict-any")
async def predict_any_endpoint(  # noqa: PLR0913
    request: Request,
    plan: Plan = Depends(plan_dependency),
    src: str | None = Form(None),
    file: UploadFile | None = File(None),
    start_time: str | None = Form(None),
    end_time: str | None = Form(None),
) -> JSONResponse:
    """Run the ML pipeline and return a download link to the CSV."""
    if file is not None:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        dest = LOCAL_DIR / file.filename
        dest.write_bytes(await file.read())
        final_src = str(dest)
        LOGGER.info("💾 Saved upload → %s", final_src)
        upload_blob_safe(f"{RAW_PREFIX}/{file.filename}", dest.open("rb"))
    elif src:
        final_src = src
    else:
        raise HTTPException(400, "Provide either 'src' or an uploaded file.")

    payload = enforce(
        {
            "src": final_src,
            "translate": True,
            "classify": True,
            "classify_ext": True,
            "intensity": True,
            "start_time": (start_time or "").strip() or None,
            "end_time": (end_time or "").strip() or None,
        },
        plan,
    )

    try:
        result = predict_any(**payload)
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("predict_any failed")
        raise HTTPException(500, f"Pipeline error: {exc}")

    csv_path = Path(result["csv"])
    filename = csv_path.name
    upload_blob_safe(filename, csv_path.open("rb"), content_type="text/csv")

    base_url = str(request.base_url).rstrip("/")
    local_url = f"{base_url}/files/{filename}"

    return JSONResponse(
        content={
            "message": "✅ Emotion CSV ready.",
            "download": {"filename": filename, "link": local_url},
            "meta": result,
        },
        status_code=200,
    )


# ─────────────────────────────── Feedback endpoint ────────────────────────


@app.post("/api/predictions/{prediction_id}/feedback")
async def receive_feedback(
    prediction_id: str,
    payload: FeedbackPayload,
) -> JSONResponse:
    """
    Store user feedback in Azure Blob.

    correct=True  → feedback/<id>/receipt-<ts>.json + original CSV
    correct=False → feedback/<id>/corrections-<ts>.csv + meta-<ts>.json
    """
    prefix = f"feedback/{prediction_id}"
    ts = int(time.time())

    if payload.correct:
        # upload receipt JSON
        receipt_name = f"{prefix}/receipt-{ts}.json"
        upload_blob_safe(
            receipt_name,
            payload.model_dump_json().encode(),
            content_type="application/json",
        )
        LOGGER.info("✅ stored receipt → %s", receipt_name)

        # also archive original CSV to feedback
        original_path = LOCAL_DIR / prediction_id
        if original_path.exists():
            with original_path.open("rb") as f:
                orig_blob = f"{prefix}/original-{ts}.csv"
                upload_blob_safe(orig_blob, f, content_type="text/csv")
                LOGGER.info("✅ archived original → %s", orig_blob)

        return JSONResponse(
            content={"message": "Receipt + original stored."},
            status_code=200,
        )

    if payload.corrections is None:
        raise HTTPException(
            400, "If 'correct' is false you must include 'corrections'."
        )

    # write corrected CSV
    csv_io = io.StringIO()
    rows = [seg.dict() for seg in payload.corrections]
    writer = csv.DictWriter(csv_io, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    corr_name = f"{prefix}/corrections-{ts}.csv"
    upload_blob_safe(corr_name, csv_io.getvalue().encode(), content_type="text/csv")

    # write payload JSON
    meta_name = f"{prefix}/meta-{ts}.json"
    upload_blob_safe(
        meta_name,
        payload.model_dump_json().encode(),
        content_type="application/json",
    )

    LOGGER.info("📝 stored corrections → %s", corr_name)
    LOGGER.info("📝 stored meta        → %s", meta_name)
    return JSONResponse(
        content={"message": "Corrections + meta stored."},
        status_code=200,
    )

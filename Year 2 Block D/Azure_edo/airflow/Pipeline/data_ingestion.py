#!/usr/bin/env python
"""
data_ingestion.py ─ upload a CSV (local file or remote URL) and register it
as an Azure ML Data asset.

Typical component invocation
─────────────────────────────
python data_ingestion.py \
    --local_path /mnt/azureml/inputs/raw.csv \
    --subscription_id <sub> \
    --resource_group  <rg> \
    --workspace_name  <ws> \
    --output_path     $AZUREML_OUTPUT_data_asset  (auto-injected)

Running locally
───────────────
export AZURE_CLIENT_ID=... AZURE_TENANT_ID=... AZURE_CLIENT_SECRET=...
python data_ingestion.py \
    --local_path ./data/my.csv \
    --subscription_id <sub> --resource_group <rg> --workspace_name <ws>
"""

from __future__ import annotations


import logging
from pathlib import Path
from typing import Optional

from azure.identity import EnvironmentCredential, DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.core.exceptions import HttpResponseError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


def get_credential():
    """Use env-vars if present, else fall back to the full default chain."""
    try:
        # This succeeds only if AZURE_* vars are set
        return EnvironmentCredential()
    except Exception:  # pylint: disable=broad-except
        return DefaultAzureCredential()


def ingest_data_to_datastore(
    *,
    subscription_id: str,
    resource_group: str,
    workspace_name: str,
    local_path: str,
    data_asset_name: str = "raw_emotion_data",
    data_version: Optional[str] = None,
    output_path: Optional[str] = None,
):
    """Upload local file/URL and register it as a Data asset. Returns the asset object."""
    ml_client = MLClient(
        credential=get_credential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )

    path_to_register = Path(local_path).as_posix() if local_path else None
    if not path_to_register:
        raise ValueError("--local_path is required and cannot be empty")

    data_asset = Data(
        name=data_asset_name,
        version=data_version,  # if None, service will auto-increment
        path=path_to_register,
        type="uri_file",
        description="Raw emotion CSV ingested via CI pipeline",
        tags={"source": "CI", "original_path": path_to_register},
    )

    try:
        returned = ml_client.data.create_or_update(data_asset)
        log.info("✅ Registered data asset: %s v%s", returned.name, returned.version)
    except HttpResponseError as err:
        log.error("❌ Failed to register data asset: %s", err)
        raise

    # ───────── write asset ID to pipeline output file ─────────
    if output_path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

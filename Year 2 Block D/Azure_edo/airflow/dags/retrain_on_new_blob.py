from datetime import datetime, timedelta
import os
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator, ShortCircuitOperator

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

# ── Configuration ────────────────────────────────────────────────
LOCAL_DIR = "/tmp/retrain_scratch"
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
PIPELINE_DIR = os.path.join(AIRFLOW_HOME, "Pipeline")
PIPELINE_SCRIPT = os.path.join(PIPELINE_DIR, "Pipeline_C.py")  # <-- match your casing!

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "start_date": datetime(2024, 1, 1),
}


def _container_client():
    cred = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    )
    account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    container = os.getenv("AZURE_STORAGE_CONTAINER")
    svc = BlobServiceClient(f"https://{account}.blob.core.windows.net", credential=cred)
    return svc.get_container_client(container)


def list_new_blobs(**ctx):
    ti = ctx["ti"]
    cont = _container_client()
    all_blobs = [
        b.name
        for b in cont.list_blobs()
        if fnmatch.fnmatch(Path(b.name).name, "*_emotion.csv")
    ]
    seen = set(json.loads(Variable.get("processed_blobs", default_var="[]")))
    new = [b for b in all_blobs if b not in seen]

    ti.log.info("🔄 All matching blobs: %s", all_blobs)
    ti.log.info("✅ Seen blobs: %s", list(seen))
    ti.log.info("✳️ New blobs: %s", new)

    ti.xcom_push("new_blobs", new)
    return new


def ensure_two_or_more(**ctx):
    new = ctx["ti"].xcom_pull(task_ids="list_new_blobs", key="new_blobs") or []
    ctx["ti"].log.info("🔎 Found %d new blobs", len(new))
    return len(new) >= 2


def download_new(**ctx):
    ti = ctx["ti"]
    cont = _container_client()
    new = ti.xcom_pull(key="new_blobs") or []

    os.makedirs(LOCAL_DIR, exist_ok=True)
    paths = []
    for blob in new:
        local = os.path.join(LOCAL_DIR, Path(blob).name)
        with open(local, "wb") as f:
            f.write(cont.download_blob(blob).readall())
        ti.log.info("⬇️ Downloaded %s → %s", blob, local)
        paths.append(local)

    seen = set(json.loads(Variable.get("processed_blobs", default_var="[]")))
    seen.update(new)
    Variable.set("processed_blobs", json.dumps(list(seen)))
    ti.log.info("✅ Updated processed_blobs")

    ti.xcom_push("local_paths", paths)
    return paths


def submit_pipeline(**ctx):
    ti = ctx["ti"]
    paths = ti.xcom_pull(task_ids="download_new_blobs", key="local_paths") or []
    if not paths:
        raise ValueError("No CSV paths to train on")

    csv_path = paths[0]
    ti.log.info("🚀 Launching Pipeline_C.py on %s", csv_path)

    # inject TRAIN_CSV so pipeline_C.py picks it up
    env = os.environ.copy()
    env["TRAIN_CSV"] = csv_path

    # run inside the Pipeline folder so Azure ML DSL bundles all your code
    result = subprocess.run(
        [sys.executable, PIPELINE_SCRIPT],
        cwd=PIPELINE_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    ti.log.info("stdout:\n%s", result.stdout)
    ti.log.info("stderr:\n%s", result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline failed (exit {result.returncode})")


with DAG(
    dag_id="retrain_on_new_blob",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["retraining", "azure"],
) as dag:
    list_blobs = PythonOperator(
        task_id="list_new_blobs",
        python_callable=list_new_blobs,
    )

    check_two = ShortCircuitOperator(
        task_id="ensure_two_or_more",
        python_callable=ensure_two_or_more,
    )

    download = PythonOperator(
        task_id="download_new_blobs",
        python_callable=download_new,
    )

    submit = PythonOperator(
        task_id="submit_pipeline",
        python_callable=submit_pipeline,
    )

    list_blobs >> check_two >> download >> submit

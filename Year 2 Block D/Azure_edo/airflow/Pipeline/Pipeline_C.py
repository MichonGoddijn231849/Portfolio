#!/usr/bin/env python3
import os
import argparse

from azure.identity import ClientSecretCredential
from azure.ai.ml import MLClient, Input, Output
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import PipelineJobSettings

# ── import your registered components ────────────────────────────────
from component import (
    get_best_model_comp,
    preprocess_comp,
    train_comp,
    evaluate_comp,
    visualize_comp,
    register_comp,
    deploy_comp,
)

# ── service principal (use Key Vault or env vars in prod) ────────────
cred = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID", "0a33589b-0036-4fe8-a829-3ed0926af886"),
    client_id=os.getenv("AZURE_CLIENT_ID", "a2230f31-0fda-428d-8c5c-ec79e91a49f5"),
    client_secret=os.getenv(
        "AZURE_CLIENT_SECRET", "AWA8Q~14jhEuWoP5K4FNnRfsRc_Qcbhx8PeLRaXw"
    ),
)
ml_client = MLClient(
    credential=cred,
    subscription_id=os.getenv(
        "AZURE_SUBSCRIPTION_ID", "0a94de80-6d3b-49f2-b3e9-ec5818862801"
    ),
    resource_group_name=os.getenv("AZURE_RESOURCE_GROUP", "buas-y2"),
    workspace_name=os.getenv("AZURE_WORKSPACE", "NLP1-2025"),
)


def _resolve_csv_path() -> str:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--csv", help="Path or URI to your emotion CSV")
    args, _ = parser.parse_known_args()
    path = args.csv or os.getenv("TRAIN_CSV")
    if not path:
        raise ValueError("No CSV supplied (use --csv or set TRAIN_CSV env var)")
    return path


# Figure out which CSV to train on
CSV_PATH = _resolve_csv_path()
csv_input = Input(type="uri_file", path=CSV_PATH, mode="download")


@pipeline(
    default_compute="adsai-lambda-0",
    code=".",  # bundle everything in this Pipeline/ folder
    tags={"pipeline": "emotion"},
)
def emotion_pipeline(raw_csv):
    # 0️⃣ Champion lookup
    best = get_best_model_comp(model_name="core-emotion-model")
    best.compute = "adsai-lambda-0"

    # 1️⃣ Preprocess
    pre = preprocess_comp(raw_df=raw_csv)
    pre.compute = "adsai-lambda-0"

    # 2️⃣ Train (warm-start + sweep)
    tr = train_comp(
        base_model_dir=best.outputs.best_model_dir,
        train_texts=pre.outputs.train_texts,
        train_labels=pre.outputs.train_labels,
    )
    tr.compute = "adsai-lambda-0"
    tr.resources = {"instance_type": "gpu"}

    # 3️⃣ Evaluate
    ev = evaluate_comp(
        model_dir=tr.outputs.model_dir,
        test_texts=pre.outputs.test_texts,
        test_labels=pre.outputs.test_labels,
    )
    ev.compute = "adsai-lambda-0"
    ev.resources = {"instance_type": "gpu"}

    # 4️⃣ Visualize loss curve
    vi = visualize_comp(log_history=tr.outputs.log_history)
    vi.compute = "adsai-lambda-0"
    vi.outputs.loss_curve_png = Output(type="uri_file", mode="upload")

    # 5️⃣ Register if improved
    reg = register_comp(
        model_dir=tr.outputs.model_dir,
        model_name="core-emotion-model",
        metrics_json=ev.outputs.metrics_json,
    )
    reg.compute = "adsai-lambda-0"

    # 6️⃣ Deploy
    dep = deploy_comp(model_id_file=reg.outputs.registered_model)
    dep.compute = "adsai-lambda-0"

    return {
        "metrics": ev.outputs.metrics_json,
        "loss_curve_png": vi.outputs.loss_curve_png,
        "registered_model": reg.outputs.registered_model,
    }


if __name__ == "__main__":
    print(f"🚀 Submitting pipeline with CSV → {CSV_PATH}")
    job = emotion_pipeline(raw_csv=csv_input)
    job.settings = PipelineJobSettings(force_rerun=False)
    created = ml_client.jobs.create_or_update(job, stream=True)
    print("✅ Pipeline submitted →", created.name)

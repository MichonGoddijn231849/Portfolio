from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import os
import shutil
import pandas as pd

SUB_ID = "0a94de80-6d3b-49f2-b3e9-ec5818862801"
RG = "buas-y2"
WS = "NLP1-2025"

ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id=SUB_ID,
    resource_group_name=RG,
    workspace_name=WS,
)


def has_working_tag(run):
    tags = getattr(run, "tags", {})
    for k, v in tags.items():
        if k.strip() == "pipeline : emotion" and v.strip().lower() == "true":
            return True
    return False


# Get all pipeline runs with the working tag
all_pipeline_runs = [run for run in ml_client.jobs.list() if has_working_tag(run)]

# Sort by creation time (newest first) and take the first 5
pipeline_runs = sorted(
    all_pipeline_runs, key=lambda x: x.creation_context.created_at, reverse=True
)[:10]

for idx, parent_run in enumerate(pipeline_runs, 1):
    parent_run_id = parent_run.name
    print(f"Processing pipeline run: {parent_run_id}")

    # Find the evaluation step (ev) child run
    ev_run = None
    for child in ml_client.jobs.list(parent_job_name=parent_run_id):
        if getattr(child, "display_name", "") == "ev":
            ev_run = child
            break

    if ev_run is None:
        print(f"Evaluation step (ev) run not found for pipeline {parent_run_id}.")
        continue

    download_dir = f"./metrics/downloaded_metrics_ev_{idx}"

    ml_client.jobs.download(name=ev_run.name, download_path=download_dir)

    # Find the metrics.csv file in the downloaded artifacts
    metrics_src = os.path.join(download_dir, "artifacts", "metrics", "metrics.csv")
    metrics_dst = os.path.join(download_dir, "metrics.csv")

    if os.path.isfile(metrics_src):
        shutil.copy(metrics_src, metrics_dst)
        print(f"Downloaded metrics.csv to {metrics_dst}")
    else:
        print(f"No metrics.csv found at {metrics_src}")


metrics_dir = "./metrics"

all_runs = []

# Columns to exclude from the dashboard (pred_count_*, prediction_mean/std/latency, cpu/memory, and *_f1 for emotions)
exclude_prefixes = ["pred_count_"]

# List of emotion names to exclude *_f1 for those emotions
emotion_names = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "neutral",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
]
emotion_f1s = [f"{emotion}_f1" for emotion in emotion_names]


def should_include(metric):
    if metric in emotion_f1s:
        return False
    return not any(metric.startswith(prefix) for prefix in exclude_prefixes)


# Find all subfolders like "downloaded_metrics_ev_*"
for folder in sorted(os.listdir(metrics_dir)):
    folder_path = os.path.join(metrics_dir, folder)
    if os.path.isdir(folder_path) and folder.startswith("downloaded_metrics_ev_"):
        metrics_csv = os.path.join(folder_path, "metrics.csv")
        if os.path.isfile(metrics_csv):
            df = pd.read_csv(metrics_csv)
            df.columns = ["metric", f"value_run_{folder.split('_')[-1]}"]
            df = df[df["metric"].apply(should_include)]
            all_runs.append(df.set_index("metric"))
        else:
            print(f"No metrics.csv found in {folder_path}")

# Combine all runs into a single DataFrame
if all_runs:
    combined = pd.concat(all_runs, axis=1)
    combined.reset_index(inplace=True)
    print(combined)
    combined.to_csv(os.path.join(metrics_dir, "dashboard_data.csv"), index=False)
    print(f"Saved dashboard_data.csv to {metrics_dir}")
else:
    print("No metrics.csv files found in any downloaded metrics folders.")
#

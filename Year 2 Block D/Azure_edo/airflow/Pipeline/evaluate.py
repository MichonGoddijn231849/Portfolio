#!/usr/bin/env python3
"""
Evaluate a fine-tuned core-emotion BERT model.
Emits:
  • <output_metrics> (JSON) with accuracy, macro_avg_f1 and per-class f1
  • metrics/metrics.csv
"""

import argparse
import json
import csv
import time
import psutil
import gc
from pathlib import Path

import numpy as np
import torch
import mlflow
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)
from transformers import BertTokenizer, BertForSequenceClassification, Trainer
from torch.utils.data import Dataset

from emotion_utils import core_emotions


# ── Dataset ─────────────────────────────────────────────────────────
class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        texts = texts.tolist() if hasattr(texts, "tolist") else list(texts)
        enc = tokenizer(texts, padding=True, truncation=True, max_length=128)
        self.encodings = enc

        # build a clear mapping from emotion name to ID
        mapping = {e: i for i, e in enumerate(core_emotions)}
        # use a descriptive loop variable instead of the ambiguous 'l'
        self.labels = [mapping[label] for label in labels]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {}
        for k, v in self.encodings.items():
            item[k] = torch.tensor(v[idx])
        item["labels"] = torch.tensor(self.labels[idx])
        return item


# Create emotion2id mapping for consistency
emotion2id = {e: i for i, e in enumerate(core_emotions)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_dir", required=True)
    ap.add_argument("--test_texts", required=True)
    ap.add_argument("--test_labels", required=True)
    ap.add_argument("--output_metrics", required=True)
    ap.add_argument("--max_rows", type=int, default=0)
    args = ap.parse_args()

    # load test data
    with open(args.test_texts) as f:
        texts = f.read().splitlines()
    with open(args.test_labels) as f:
        labels = f.read().splitlines()
    if args.max_rows > 0:
        texts, labels = texts[: args.max_rows], labels[: args.max_rows]

    # load model & tokenizer
    tokenizer = BertTokenizer.from_pretrained(args.model_dir)
    model = BertForSequenceClassification.from_pretrained(args.model_dir)

    ds = EmotionDataset(texts, labels, tokenizer)
    trainer = Trainer(model=model)
    preds = trainer.predict(ds)
    y_pred = np.argmax(preds.predictions, axis=1)
    y_true = preds.label_ids

    # ── map predictions to emotion names
    raw_id2label = getattr(model.config, "id2label", {})
    id2label = {int(k): v for k, v in raw_id2label.items()}
    pred_names = [id2label[p] for p in y_pred]

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(core_emotions))),
        target_names=sorted(core_emotions),
        output_dict=True,
        zero_division=0,
    )

    # ── log per-class metrics to MLflow
    for emotion in sorted(core_emotions):
        if emotion in report:
            for metric in ("precision", "recall", "f1-score"):
                mlflow.log_metric(f"{emotion}_{metric}", report[emotion][metric])

    # ── log overall metrics to MLflow
    if "macro avg" in report:
        mlflow.log_metric("macro_avg_f1", report["macro avg"]["f1-score"])
    mlflow.log_metric("accuracy", report.get("accuracy", 0.0))

    # ── additional performance metrics
    prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_true, y_pred, average="macro", zero_division=0)

    perf = {"precision": prec, "recall": rec, "f1_score": macro_f1}
    for k, v in perf.items():
        mlflow.log_metric(k, v)

    # ── prediction distribution stats
    pred_mean = float(np.mean(y_pred))
    pred_std = float(np.std(y_pred))
    mlflow.log_metric("prediction_mean", pred_mean)
    mlflow.log_metric("prediction_std", pred_std)

    # ── count predictions per class
    unique, counts = np.unique(y_pred, return_counts=True)
    for lbl, cnt in zip(unique, counts):
        mlflow.log_metric(f"pred_count_{lbl}", int(cnt))

    # ── latency measurement (on a small batch to save memory)
    small_batch_texts = texts[:8] if len(texts) > 8 else texts
    start = time.time()
    batch_inputs = tokenizer(
        list(small_batch_texts),
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )
    batch_inputs = {k: v.to(model.device) for k, v in batch_inputs.items()}
    _ = model(**batch_inputs)
    latency = time.time() - start
    mlflow.log_metric("prediction_latency", latency)

    # ── system stats
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    mlflow.log_metric("cpu_usage", cpu_usage)
    mlflow.log_metric("memory_usage", memory_usage)

    # ── prepare metrics for output
    metrics = {
        "accuracy": acc,
        "macro_avg_f1": macro_f1,
        "precision": prec,
        "recall": rec,
        "f1_score": macro_f1,
        "prediction_mean": pred_mean,
        "prediction_std": pred_std,
        "prediction_latency": latency,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
    }

    # Add per-class f1 scores
    for emo in sorted(core_emotions):
        if emo in report:
            metrics[f"{emo}_f1"] = report[emo]["f1-score"]

    # Add prediction counts
    for lbl, cnt in zip(unique, counts):
        metrics[f"pred_count_{lbl}"] = int(cnt)

    # ── inject the string predictions into the report for full JSON output
    report["predictions"] = pred_names

    # write JSON & CSV
    Path(args.output_metrics).parent.mkdir(exist_ok=True, parents=True)
    Path(args.output_metrics).write_text(json.dumps(report, indent=2))

    Path("metrics").mkdir(exist_ok=True)
    with open("metrics/metrics.csv", "w", newline="") as cf:
        w = csv.writer(cf)
        w.writerow(["metric", "value"])
        for k, v in metrics.items():
            w.writerow([k, v])

    # ── log the metrics CSV as an MLflow artifact
    if mlflow.active_run():
        mlflow.log_artifact("metrics/metrics.csv", artifact_path="metrics")

    print(json.dumps(metrics, indent=2))

    # ── cleanup to reduce memory
    del trainer
    del ds
    del preds
    del model
    gc.collect()


if __name__ == "__main__":
    main()

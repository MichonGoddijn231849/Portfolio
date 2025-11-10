#!/usr/bin/env python3
"""
Fine-tune BERT on the core-emotion task, warm-starting from an existing champion if given,
and doing a learning-rate sweep. Emits:
  • outputs/model/...    – best model files
  • outputs/log_history.json – full trainer.log_history
  • metrics.json           – best eval_loss & best_lr
"""

import argparse
import ast
import json
import os
import shutil
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import (
    BertForSequenceClassification,
    BertTokenizer,
    TrainingArguments,
    Trainer,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

from emotion_utils import emotion_map
from emotion_utils import core_emotions


# ── Helpers ─────────────────────────────────────────────────────────
def first_label(cell):
    if pd.isna(cell):
        return None
    if isinstance(cell, str) and cell.strip().startswith("["):
        try:
            lst = ast.literal_eval(cell)
            return lst[0] if lst else None
        except (ValueError, SyntaxError):
            return None
    return cell


emotion2id = {e: i for i, e in enumerate(core_emotions)}
id2emotion = {i: e for e, i in emotion2id.items()}


class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        texts = texts.tolist() if hasattr(texts, "tolist") else list(texts)
        enc = tokenizer(texts, padding=True, truncation=True, max_length=128)
        self.encodings = enc
        self.labels = [emotion2id[label] for label in labels]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


# ── Main ────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_texts", required=True)
    ap.add_argument("--train_labels", required=True)
    ap.add_argument("--output_dir", default="./outputs/model")
    ap.add_argument("--log_history", default="./outputs/log_history.json")
    ap.add_argument(
        "--base_model_dir",
        default=None,
        help="If provided, warm-start from this checkpoint",
    )
    args = ap.parse_args()

    # Choose model source
    model_source = args.base_model_dir or "bert-base-uncased"
    if args.base_model_dir:
        print(f"🔄 Warm-starting from champion in {args.base_model_dir}")
    else:
        print("❄️ Cold start from bert-base-uncased")

    # Load & filter data
    raw_texts = pd.read_csv(args.train_texts, header=None)[0].astype(str)
    raw_labels = pd.read_csv(args.train_labels, header=None)[0].map(first_label)
    df = pd.DataFrame(
        {"text": raw_texts, "label": raw_labels.map(emotion_map)}
    ).dropna()
    vc = df["label"].value_counts()
    df = df[df["label"].map(vc) > 1].reset_index(drop=True)
    texts, labels = df["text"], df["label"].str.lower()
    tr_texts, val_texts, tr_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # Tokenizer & datasets
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    train_ds = EmotionDataset(tr_texts, tr_labels, tokenizer)
    val_ds = EmotionDataset(val_texts, val_labels, tokenizer)

    # Hyperparam sweep
    lrs = [5e-5, 3e-5, 2e-5, 1e-5]
    best_loss, best_lr = float("inf"), None
    best_model = None
    all_logs = []

    for i, lr in enumerate(lrs, 1):
        print(f"\n=== Sweep {i}/{len(lrs)}: lr={lr} ===")
        model = BertForSequenceClassification.from_pretrained(
            model_source,
            num_labels=len(core_emotions),
            id2label=id2emotion,
            label2id=emotion2id,
        )
        args_tr = TrainingArguments(
            output_dir=f"{args.output_dir}_tmp_{lr}",
            num_train_epochs=2,
            per_device_train_batch_size=4,
            learning_rate=lr,
            evaluation_strategy="epoch",
            logging_steps=10,
            save_strategy="epoch",
            report_to=["mlflow"],
            weight_decay=0.01,
            load_best_model_at_end=False,
        )
        trainer = Trainer(
            model=model,
            args=args_tr,
            train_dataset=train_ds,
            eval_dataset=val_ds,
        )
        trainer.train()
        pred = trainer.predict(val_ds)
        y_pred = pred.predictions.argmax(axis=1)
        y_true = pred.label_ids

        # get eval_loss
        eval_loss = next(
            (
                record["eval_loss"]
                for record in reversed(trainer.state.log_history)
                if "eval_loss" in record
            ),
            float("inf"),
        )
        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        print(f"→ lr={lr}: loss={eval_loss:.4f}, f1={f1:.4f}")

        if eval_loss < best_loss:
            best_loss, best_lr = eval_loss, lr
            best_model = model

        # collect logs
        for rec in trainer.state.log_history:
            all_logs.append({**rec, "lr": lr})

    print(f"\n🏆 Best lr={best_lr} (loss={best_loss:.4f})")

    # save best model + tokenizer
    os.makedirs(args.output_dir, exist_ok=True)
    best_model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    Path(args.output_dir, "metrics.json").write_text(
        json.dumps({"best_lr": best_lr, "best_loss": best_loss}, indent=2)
    )

    # cleanup temporary dirs
    for lr in lrs:
        tmp = f"{args.output_dir}_tmp_{lr}"
        if os.path.isdir(tmp):
            shutil.rmtree(tmp)

    # write full log history
    Path(args.log_history).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log_history).write_text(json.dumps(all_logs, indent=2))

    print("✅ Saved best model, metrics.json & log_history.json")


if __name__ == "__main__":
    main()

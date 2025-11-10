#!/usr/bin/env python3
"""
Prepares train/test CSV shards for the emotion pipeline.

Steps
-----
1. Read `translation` as input text and `emotion` as label.
2. Map raw labels to your core-emotion set (drops unmapped).
3. Drop any core emotion class with ≤1 example.
4. Stratified 80/20 split.
5. Write four flat CSVs (no header, no index).
"""

import argparse
import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

from emotion_utils import emotion_map  # your mapping dict: raw→core


def write_series(series: pd.Series, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    series.to_csv(out_path, index=False, header=False)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input_path", required=True)
    p.add_argument("--train_texts_out", required=True)
    p.add_argument("--train_labels_out", required=True)
    p.add_argument("--test_texts_out", required=True)
    p.add_argument("--test_labels_out", required=True)
    args = p.parse_args()

    # ── load raw CSV ────────────────────────────────────────────────
    df = pd.read_csv(args.input_path)
    cols = set(df.columns)

    # Ensure required columns are present
    if "translation" not in cols or "emotion" not in cols:
        sys.stderr.write(
            f"ERROR: input CSV must have 'translation' and 'emotion' columns.\n"
            f"Found: {sorted(cols)}\n"
        )
        sys.exit(1)

    # ── pick your features and labels ───────────────────────────────
    df = df[["translation", "emotion"]].rename(
        columns={"translation": "text", "emotion": "raw_label"}
    )

    # ── map raw labels → core emotions ─────────────────────────────
    df["core"] = df["raw_label"].map(emotion_map)
    df = df.dropna(subset=["core"]).reset_index(drop=True)
    if df.empty:
        raise RuntimeError("No samples remain after mapping to core emotions.")

    # ── drop singleton classes (≤1 sample) ──────────────────────────
    counts = df["core"].value_counts()
    keep = counts.index
    before, after = len(counts), len(keep)
    if after < before:
        dropped = set(counts.index) - set(keep)
        print(f"🗑️  Dropping singleton classes: {sorted(dropped)}")
    df = df[df["core"].isin(keep)].reset_index(drop=True)

    # ── stratified 80/20 split ────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["core"],
        test_size=0.20,
        random_state=42,
        stratify=df["core"],
    )

    # ── persist outputs ────────────────────────────────────────────
    write_series(X_train, args.train_texts_out)
    write_series(y_train, args.train_labels_out)
    write_series(X_test, args.test_texts_out)
    write_series(y_test, args.test_labels_out)

    print(
        "✅ Preprocessing finished:",
        len(X_train),
        "train rows |",
        len(X_test),
        "test rows",
    )


if __name__ == "__main__":
    main()

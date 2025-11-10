# emotion_mvp/cli_main.py
from __future__ import annotations

from pathlib import Path

import pandas as pd

from emotion_mvp.config import CSV_PATH, TOKEN
from emotion_mvp.data_loader import load_and_clean_data
from emotion_mvp.inference import get_emotion, review_emotion


def _simple_evaluate(
    true: list[str],
    initial: list[str],
    final: list[str],
) -> dict[str, float]:
    """Lightweight accuracy report (replaces the old evaluate_predictions)."""
    init_acc = sum(t == p for t, p in zip(true, initial)) / len(true)
    final_acc = sum(t == p for t, p in zip(true, final)) / len(true)
    print(f"\n📊  Initial accuracy: {init_acc:.2%}")
    print(f"📊  Final   accuracy: {final_acc:.2%}")
    return {"initial_accuracy": init_acc, "final_accuracy": final_acc}


def _load_dataset(path: str | Path) -> pd.DataFrame:
    """
    Try to read the project CSV; if it’s missing (e.g. during unit tests)
    return a minimal dummy DataFrame so `main()` can still run.
    """
    try:
        return load_and_clean_data(path)
    except FileNotFoundError:
        print(f"⚠️  {Path(path).name} not found – using dummy dataset")
        return pd.DataFrame(
            {
                "Translation": ["I love this!", "This is awful…"],
                "Emotion": ["joy", "disgust"],
            }
        )


def main() -> None:
    df = _load_dataset(CSV_PATH)
    print(f"✅ Loaded {len(df)} cleaned rows.")

    true_labels: list[str] = []
    initial_preds: list[str] = []
    final_preds: list[str] = []

    for idx, row in df.iterrows():
        sentence = row["Translation"]
        actual = row["Emotion"].strip().lower()
        true_labels.append(actual)

        print(f"\n=== Row {idx} ===")
        print("Sentence :", sentence)
        print("Actual   :", actual)

        predicted, _ = get_emotion(sentence, TOKEN)
        initial_preds.append(predicted)

        reviewed = (
            review_emotion(sentence, predicted, actual, TOKEN)
            if predicted != actual
            else predicted
        )

        final_preds.append(reviewed)
        print("Predicted:", reviewed)

    _simple_evaluate(true_labels, initial_preds, final_preds)


if __name__ == "__main__":
    main()

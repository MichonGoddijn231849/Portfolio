#!/usr/bin/env python3
import os
import json
import argparse
import matplotlib.pyplot as plt
import mlflow
import matplotlib

matplotlib.use("Agg")


def main(log_history_path: str, output_plot_path: str):
    # 1. Load HF Trainer log history
    with open(log_history_path, "r") as f:
        logs = json.load(f)

    # 2. Extract losses
    train_epochs, train_losses = [], []
    eval_epochs, eval_losses = [], []
    for rec in logs:
        if "loss" in rec and "epoch" in rec:
            train_epochs.append(rec["epoch"])
            train_losses.append(rec["loss"])
        if "eval_loss" in rec and "epoch" in rec:
            eval_epochs.append(rec["epoch"])
            eval_losses.append(rec["eval_loss"])

    # 3. Plot
    fig, ax = plt.subplots()
    ax.plot(train_epochs, train_losses, marker="o", label="Train")
    ax.plot(eval_epochs, eval_losses, marker="x", label="Validation")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Training vs Validation Loss")
    ax.legend()
    ax.grid(True)

    # 4. Save locally
    os.makedirs(os.path.dirname(output_plot_path), exist_ok=True)
    fig.savefig(output_plot_path, format="png")
    print(f"✅ Plot saved to {output_plot_path}")

    # 5. Log as artifact
    mlflow.log_artifact(output_plot_path, artifact_path="loss_plots")
    print("📈 Logged plot to MLflow as artifact")

    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log_history_path",
        type=str,
        required=True,
        help="Path to the Trainer log_history.json",
    )
    parser.add_argument(
        "--output_plot_path",
        type=str,
        default="metrics/loss_curve.png",
        help="Where to write the loss curve PNG",
    )
    args = parser.parse_args()
    main(args.log_history_path, args.output_plot_path)

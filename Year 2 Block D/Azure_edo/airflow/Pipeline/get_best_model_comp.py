#!/usr/bin/env python
"""
Download the current champion model into best_model_dir (flattened) and emit its F1.
Outputs
-------
best_model_dir : folder with config.json etc.  (Output type = custom_model)
best_f1        : text file with the champion’s F1
"""

import argparse
import os
import shutil
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name", required=True)
    ap.add_argument("--best_model_dir", required=True)  # folder
    ap.add_argument("--best_f1", required=True)
    args = ap.parse_args()

    ml = MLClient(
        DefaultAzureCredential(),
        subscription_id=os.environ["AZUREML_ARM_SUBSCRIPTION"],
        resource_group_name=os.environ["AZUREML_ARM_RESOURCEGROUP"],
        workspace_name=os.environ["AZUREML_ARM_WORKSPACE_NAME"],
    )

    # ── find champion by f1 tag ──────────────────────────────────
    best_f1, best_pair = 0.0, None
    for m in ml.models.list(name=args.model_name):
        try:
            f1 = float(m.tags.get("f1", 0.0))
        except (ValueError, TypeError):
            f1 = 0.0
        if f1 > best_f1:
            best_f1, best_pair = f1, (m.name, m.version)

    out_dir = Path(args.best_model_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if best_pair:
        name, ver = best_pair
        print(f"🔍 Champion: {name}:{ver}  (F1 = {best_f1:.4f})")

        # download – SDK versions < 1.9 ignore unknown kwargs, so keep it simple
        ml.models.download(name=name, version=ver, download_path=str(out_dir))

        # flatten nested folder if needed
        configs = list(out_dir.rglob("config.json"))
        if not configs:
            raise RuntimeError("Downloaded model lacks config.json")
        base = configs[0].parent
        if base != out_dir:
            for item in base.iterdir():
                shutil.move(str(item), out_dir / item.name)
            # remove empty subdirs
            for sub in out_dir.iterdir():
                if sub.is_dir() and not any(sub.iterdir()):
                    shutil.rmtree(sub)
    else:
        print("🔍 No champion model found (cold start)")
        (out_dir / "_placeholder.txt").write_text("no model yet")
        best_f1 = 0.0

    Path(args.best_f1).write_text(str(best_f1))


if __name__ == "__main__":
    main()

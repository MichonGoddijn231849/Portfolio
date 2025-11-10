#!/usr/bin/env python3
import argparse
import json
import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_dir", required=True)
    p.add_argument("--model_name", required=True)
    p.add_argument("--metrics_json", required=True)
    p.add_argument("--registered_model", required=True)
    args = p.parse_args()

    # Load challenger metrics
    with open(args.metrics_json) as f:
        m = json.load(f)
    # Prefer macro_avg_f1 (or fallback to f1)
    challenger_f1 = m.get("macro_avg_f1", m.get("f1", 0.0))

    # Authenticate and look up current champion
    cred = DefaultAzureCredential()
    ml = MLClient(
        cred,
        os.environ["AZUREML_ARM_SUBSCRIPTION"],
        os.environ["AZUREML_ARM_RESOURCEGROUP"],
        os.environ["AZUREML_ARM_WORKSPACE_NAME"],
    )

    # Get best existing F1 tag
    best_f1, best_pair = 0.0, None
    for model in ml.models.list(name=args.model_name):
        try:
            f1 = float(model.tags.get("f1", 0.0))
        except (ValueError, TypeError):
            f1 = 0.0
        if f1 > best_f1:
            best_f1, best_pair = f1, (model.name, model.version)

    # Compare and decide
    if challenger_f1 > best_f1:
        # register new champion
        print(f"🏆 Challenger wins ({challenger_f1:.4f} > {best_f1:.4f}) → registering")
        new_model = ml.models.create_or_update(
            name=args.model_name,
            path=args.model_dir,
            description=f"Auto-registered model with F1={challenger_f1:.4f}",
            tags={"f1": f"{challenger_f1:.4f}"},
        )
        registered = f"{new_model.name}:{new_model.version}"
    else:
        # keep existing
        print(f"🤷 Challenger loses → keeping champion {best_pair[0]}:{best_pair[1]}")
        registered = f"{best_pair[0]}:{best_pair[1]}"

    # Write out the name:version for downstream
    with open(args.registered_model, "w") as out:
        out.write(registered)


if __name__ == "__main__":
    main()

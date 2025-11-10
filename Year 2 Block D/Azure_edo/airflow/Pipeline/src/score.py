#!/usr/bin/env python3
import os
import json
import logging
import torch

from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger("score")
logging.basicConfig(level=logging.INFO)

tokenizer = model = device = None


def _find_model_subfolder(root_dir):
    # same helper as before …
    if os.path.isfile(os.path.join(root_dir, "config.json")):
        return root_dir
    for sub in os.listdir(root_dir):
        sd = os.path.join(root_dir, sub)
        if os.path.isdir(sd) and os.path.isfile(os.path.join(sd, "config.json")):
            return sd
    raise FileNotFoundError(f"config.json not found under {root_dir}")


def init():
    global tokenizer, model, device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    root = os.getenv("AZUREML_MODEL_DIR")
    model_dir = _find_model_subfolder(root)
    logger.info(f"Loading from {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_dir, local_files_only=True
    )
    model.to(device).eval()


def run(raw_request: str):
    try:
        payload = json.loads(raw_request)
    except json.JSONDecodeError:
        return json.dumps({"error": "invalid JSON", "code": 400})

    texts = payload.get("text") or payload.get("inputs")
    if isinstance(texts, str):
        texts = [texts]
    if not isinstance(texts, (list, tuple)):
        return json.dumps({"error": "text must be string or list", "code": 400})

    enc = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        logits = model(**enc).logits

    preds = torch.argmax(logits, dim=-1).cpu().tolist()

    # Map directly to emotion names
    id2label = getattr(model.config, "id2label", {})
    emotions = [id2label.get(str(i), str(i)) for i in preds]

    return json.dumps({"predictions": emotions})

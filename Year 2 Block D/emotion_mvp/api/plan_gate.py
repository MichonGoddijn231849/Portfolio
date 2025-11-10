# api/plan_gate.py

import logging
from enum import Enum
from fastapi import HTTPException

log = logging.getLogger(__name__)


class Plan(str, Enum):
    basic = "basic"
    plus = "plus"
    pro = "pro"


RULES = {
    Plan.basic: {
        "max_seconds": 10 * 60,
        "model": "tiny",
        "translate": True,
        "classify": True,
        "classify_ext": False,
        "intensity": False,
    },
    Plan.plus: {
        "max_seconds": 45 * 60,
        "model": "medium",
        "translate": True,
        "classify": True,
        "classify_ext": True,
        "intensity": False,
    },
    Plan.pro: {
        "max_seconds": 4 * 60 * 60,
        "model": "turbo",
        "translate": True,
        "classify": True,
        "classify_ext": True,
        "intensity": True,
    },
}


def enforce(payload: dict, plan: Plan) -> dict:
    rule = RULES[plan]
    log.info(f"Enforcing rules for plan: '{plan.value}'")

    for key in ["translate", "classify", "classify_ext", "intensity"]:
        payload.pop(key, None)

    classifier_choice = payload.pop("classifier", "llama")

    duration = payload.get("duration_sec")
    if duration is not None and duration > rule["max_seconds"]:
        # --- ADDED LOGGING BEFORE THE ERROR ---
        log.warning(
            f"Request denied for plan '{plan.value}'. "
            f"Duration {duration}s exceeds max {rule['max_seconds']}s."
        )
        raise HTTPException(
            status_code=403,
            detail=f"{plan.value.capitalize()} plan limited to {rule['max_seconds'] // 60}-minute audio",
        )

    payload.update(
        {
            "inp": payload.pop("src"),
            "model": rule["model"],
            "do_translate": rule["translate"],
            "do_classify": rule["classify"],
            "do_classify_ext": rule["classify_ext"],
            "do_intensity": rule["intensity"],
            "classifier_model": classifier_choice.lower(),
        }
    )

    return payload

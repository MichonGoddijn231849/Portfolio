# File: tests/test_plan_gate.py
"""Tests for the API plan gate functionality.

This module contains unit tests for the plan enforcement system that manages
subscription-based feature access, validates requests based on plan limitations,
and ensures proper parameter mapping between plans and pipeline configuration.
"""
import pytest
from emotion_mvp.api.plan_gate import enforce, Plan, RULES
from fastapi import HTTPException


@pytest.mark.parametrize("plan", list(Plan))
def test_enforce_basic_mapping(plan):
    """Test basic parameter mapping for all subscription plans.

    Args:
        plan: The subscription plan to test (parametrized).

    Tests:
        - Proper parameter mapping from plan rules
        - Input source preservation
        - Model selection based on plan
        - Feature flag configuration per plan
    """
    src = "file.wav"
    payload = {"src": src}
    out = enforce(payload.copy(), plan)
    rule = RULES[plan]
    assert out["inp"] == src
    assert out["model"] == rule["model"]
    assert out["do_translate"] == rule["translate"]
    assert out["do_classify"] == rule["classify"]
    assert out["do_classify_ext"] == rule["classify_ext"]
    assert out["do_intensity"] == rule["intensity"]


@pytest.mark.parametrize("plan", list(Plan))
def test_enforce_remove_conflicting_keys(plan):
    """Test removal of conflicting keys from request payload.

    Args:
        plan: The subscription plan to test (parametrized).

    Tests:
        - Conflicting parameter keys are removed
        - Plan rules override user-provided parameters
        - Clean payload structure after enforcement
    """
    payload = {
        "src": "x",
        "translate": False,
        "classify": False,
        "classify_ext": True,
        "intensity": True,
    }
    out = enforce(payload.copy(), plan)
    # ensure only mapped keys remain
    for key in ["translate", "classify", "classify_ext", "intensity"]:
        assert key not in out


@pytest.mark.parametrize(
    "plan,duration",
    [
        (Plan.basic, RULES[Plan.basic]["max_seconds"] + 1),
        (Plan.plus, RULES[Plan.plus]["max_seconds"] + 10),
        (Plan.pro, RULES[Plan.pro]["max_seconds"] + 60),
    ],
)
def test_enforce_duration_exceed(plan, duration):
    """Test duration limit enforcement for subscription plans.

    Args:
        plan: The subscription plan to test.
        duration: Duration that exceeds the plan's limit.

    Tests:
        - HTTPException raised when duration exceeds plan limit
        - Proper error message includes plan information
        - Duration validation per subscription tier
    """
    payload = {"src": "x", "duration_sec": duration}
    with pytest.raises(HTTPException) as exc:
        enforce(payload, plan)
    assert f"{plan.value.capitalize()} plan limited" in str(exc.value.detail)


@pytest.mark.parametrize(
    "plan,duration",
    [
        (Plan.basic, RULES[Plan.basic]["max_seconds"]),
        (Plan.plus, RULES[Plan.plus]["max_seconds"] - 1),
    ],
)
def test_enforce_duration_allowed(plan, duration):
    """Test allowed duration processing for subscription plans.

    Args:
        plan: The subscription plan to test.
        duration: Duration within the plan's allowed limit.

    Tests:
        - Successful processing within duration limits
        - Proper input preservation when limits are met
        - Plan boundary validation
    """
    payload = {"src": "x", "duration_sec": duration}
    out = enforce(payload.copy(), plan)
    assert out["inp"] == "x"


if __name__ == "__main__":
    pytest.main()

# tests/test_cli.py
"""Tests for the command-line interface functionality.

This module contains unit tests for the CLI commands, testing plan-based
parameter enforcement, argument validation, and integration with the
prediction pipeline.
"""
import pytest
from click.testing import CliRunner

# Import the components we need to test and patch
from emotion_mvp.cli import main
from emotion_mvp.api.plan_gate import RULES


# This is the primary test that was failing. It is now fully corrected.
@pytest.mark.parametrize("plan_name", ["basic", "plus", "pro"])
def test_predict_any_plans(monkeypatch, tmp_path, plan_name):
    """Test CLI predict-any command with different subscription plans.

    Args:
        monkeypatch: Pytest fixture for mocking dependencies.
        tmp_path: Pytest fixture providing temporary directory.
        plan_name: The subscription plan to test (basic, plus, pro).

    Tests:
        - CLI command execution with different plans
        - Proper parameter enforcement based on plan rules
        - Integration between CLI and pipeline function
        - Plan-specific model and feature selection
    """
    # 1. We need a fake input file for the command to use
    fake_input_file = tmp_path / "input.txt"
    fake_input_file.write_text("This is a test sentence.")

    # 2. This is the crucial part: We will spy on the real `predict_any` function
    #    to see what arguments it receives from the CLI.
    # --- THIS IS THE FIX: We patch 'predict_any' where it is *used*, in the 'cli' module ---
    from emotion_mvp import cli

    call_args = {}

    def spy_predict_any(**kwargs):
        # When the real `predict_any` is called, our spy will run instead.
        # It saves all the arguments it received into our `call_args` dictionary.
        call_args.update(kwargs)
        # It must return a dummy JSON result so the rest of the CLI command can finish.
        return {"csv": "dummy_path.csv", "input": str(fake_input_file)}

    # Use monkeypatch to replace the real function with our spy in the correct module
    monkeypatch.setattr(cli, "predict_any", spy_predict_any)
    # ------------------------------------------------------------------------------------

    # 3. Now, run the actual command line tool
    runner = CliRunner()
    args = ["predict-any", str(fake_input_file), "--plan", plan_name]
    result = runner.invoke(main, args)

    # 4. First, assert that the command itself ran without crashing
    assert result.exit_code == 0, f"CLI command failed: {result.output}"

    # 5. Now, check if our spy captured the correct arguments based on the plan
    plan_rules = RULES[plan_name]
    assert call_args["model"] == plan_rules["model"]
    assert call_args["do_classify_ext"] == plan_rules["classify_ext"]
    assert call_args["do_intensity"] == plan_rules["intensity"]


# The old test for missing source argument is still good practice.
def test_missing_src_argument():
    """Test CLI behavior when required source argument is missing.

    Tests:
        - CLI exits with non-zero code when required argument missing
        - Appropriate error message is displayed
        - Proper argument validation
    """
    runner = CliRunner()
    result = runner.invoke(main, ["predict-any"])
    assert result.exit_code != 0
    assert "Error: Missing argument" in result.output

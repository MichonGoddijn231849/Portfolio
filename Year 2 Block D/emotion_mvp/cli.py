# emotion_mvp/cli.py
"""
Command Line Interface Module

This module provides the main CLI interface for the Emotion MVP system.
It uses Click framework to create a user-friendly command-line tool with
subscription plan-based feature access.

Features:
- Plan-based feature enforcement (basic, plus, pro)
- JSON output for programmatic use
- Comprehensive logging
- Input validation and error handling

The CLI serves as the primary user interface for batch processing,
scripting, and integration with other tools.
"""

import json
import click
import logging

# Import all necessary components from the plan_gate module
from emotion_mvp.api.plan_gate import Plan, enforce
from emotion_mvp.pipeline import predict_any

log = logging.getLogger(__name__)


@click.group()
def main():
    """
    Emotion MVP Command Line Interface.

    A powerful CLI tool for emotion classification from text, audio, and video sources.
    Supports multiple subscription plans with different feature sets.
    """
    pass


@main.command("predict-any")
@click.argument("src", metavar="SRC")
@click.option(
    "--plan",
    type=click.Choice(["basic", "plus", "pro"], case_sensitive=False),
    default="basic",
    help="Subscription plan (affects model & features)",
)
def _predict_any(src: str, plan: str):
    """
    Run emotion prediction pipeline on any input source.

    Processes various input types including text, audio files, video files,
    and URLs to perform emotion classification. Features available depend
    on the selected subscription plan.

    Args:
        src (str): Input source - can be:
            - Direct text: "I am happy today"
            - Local file: /path/to/audio.mp3
            - YouTube URL: https://youtube.com/watch?v=...
            - Text file: /path/to/document.txt
            - CSV file: /path/to/sentences.csv
        plan (str): Subscription plan level (basic, plus, pro)

    Plan Features:
        - Basic: BERT classification, 7 basic emotions
        - Plus: BERT + LLaMA, extended emotions, translation
        - Pro: All Plus features + intensity scoring

    Examples:
        emotion-cli predict-any "I love this weather!" --plan basic
        emotion-cli predict-any /path/to/interview.mp3 --plan pro
        emotion-cli predict-any https://youtube.com/watch?v=example --plan plus

    Output:
        JSON object containing:
        - timestamp: Processing timestamp
        - input: Original input source
        - language: Detected language
        - csv: Path to detailed results CSV file
    """
    # --- THIS ENTIRE FUNCTION IS NOW CORRECTED AND SIMPLIFIED ---
    pl = Plan(plan)

    # 1. Start with the basic input
    payload = {"src": src}

    # 2. Let the enforce() function create the final, complete payload.
    #    It's crucial to capture the return value here.
    enforced_payload = enforce(payload, pl)

    log.info(
        f"Running prediction with plan '{plan}' and model '{enforced_payload['model']}'..."
    )

    # 3. Pass all arguments from the enforced payload directly to the pipeline.
    #    The ** operator unpacks the dictionary into keyword arguments.
    result = predict_any(**enforced_payload)

    log.info("Prediction finished successfully.")

    # 4. Print the result from the pipeline directly. No manual merging is needed.
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    # ------------------------------------------------------------


if __name__ == "__main__":
    main()

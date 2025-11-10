# emotion_mvp/prompts.py
"""
Prompt Engineering Module

This module provides sophisticated prompt generation for emotion classification
using Large Language Models (LLMs). It includes tier-specific few-shot examples,
dynamic prompt building, and review prompts for model correction.

Features:
- Tier-specific few-shot examples (Basic, Plus, Pro)
- Dynamic prompt construction based on subscription plans
- Intensity scoring prompts for Pro tier
- Review prompts for model correction and validation
- Structured output formatting
- Comprehensive emotion coverage

The module uses carefully crafted prompts to ensure consistent and accurate
emotion classification across different model capabilities and subscription tiers.
"""

from typing import List

# ─────────────────── 1. Tier-Specific Few-Shot Examples ────────────────────
# BASIC tier
BASIC_FEW_SHOTS_LIST = [
    ("This is wonderful news!", "happy"),
    ("I feel so down today.", "sad"),
    ("That driver just cut me off!", "mad"),
    ("I heard a strange noise downstairs.", "scared"),
    ("Wow, I didn't see that coming at all!", "surprised"),
    ("Ugh, this spoiled milk smells awful!", "disgusted"),
    ("It’s just an ordinary Tuesday.", "neutral"),
]

# PLUS tier
PLUS_FEW_SHOTS_LIST = [
    ("I can’t wait for the party tonight!", "excitement"),
    ("I'm completely lost, what are we doing?", "confusion"),
    ("I didn’t expect that at all!", "surprise"),
    ("It’s just another day, nothing special.", "neutral"),
    ("I'm sure things will work out for the best.", "optimism"),
    ("I’m so proud of completing that marathon.", "pride"),
    ("I wonder what’s inside that old box.", "curiosity"),
    ("The thought of speaking in public fills me with dread.", "fear"),
    ("That comedian's routine was hilarious!", "amusement"),
    ("This beautiful sunset fills me with pure happiness.", "joy"),
    ("I really want that new video game.", "desire"),
    ("The constant dripping tap is so irritating.", "annoyance"),
    ("I have a big presentation tomorrow and I'm a wreck.", "nervousness"),
    ("Thank you so much for your incredible help.", "gratitude"),
    ("Yes, that’s exactly the right approach!", "approval"),
    ("Ah, now I understand how this works!", "realization"),
    ("I was hoping to get the job, so this is a letdown.", "disappointment"),
    ("Don't worry, I'm here for you.", "caring"),
    ("Hearing about the accident made me feel quite low.", "sadness"),
    ("I truly look up to her dedication and skill.", "admiration"),
    ("I don't think that's the correct way to handle this.", "disapproval"),
    ("How dare they accuse me of that?!", "anger"),
    ("I deeply regret my harsh words from yesterday.", "remorse"),
]

# PRO tier (= PLUS + relief, love, disgust, embarrassment)
PRO_FEW_SHOTS_LIST = PLUS_FEW_SHOTS_LIST + [
    ("Phew, the presentation is over and it went well!", "relief"),
    ("I cherish every moment we spend together.", "love"),
    ("The sight of that rotting food was vile.", "disgust"),
    ("I can't believe I spilled coffee all over my boss.", "embarrassment"),
]

TIER_SPECIFIC_FEW_SHOTS = {
    "basic": BASIC_FEW_SHOTS_LIST,
    "plus": PLUS_FEW_SHOTS_LIST,
    "pro": PRO_FEW_SHOTS_LIST,
}


# ─────────────────── 2. Prompt builder (first pass) ───────────────────────
def build_prompt(
    sentence: str,
    allowed_labels: List[str],
    plan_name: str,
    want_intensity: bool = False,
) -> str:
    """
    Build a comprehensive emotion classification prompt for LLM inference.

    Creates a structured prompt with tier-specific few-shot examples, clear
    instructions, and optional intensity scoring. The prompt includes reasoning
    steps and output formatting to ensure consistent model responses.

    Args:
        sentence (str): Input text to classify
        allowed_labels (List[str]): Valid emotion labels for the current tier
        plan_name (str): Subscription plan name ('basic', 'plus', or 'pro')
        want_intensity (bool): Whether to include intensity scoring instructions

    Returns:
        str: Formatted prompt ready for LLM inference

    Examples:
        >>> labels = ['joy', 'sadness', 'anger', 'neutral']
        >>> prompt = build_prompt("I love this!", labels, 'basic', False)
        >>> print('Answer:' in prompt)  # True
        >>> print('Reasoning:' in prompt)  # True

        >>> # With intensity scoring
        >>> prompt = build_prompt("I'm furious!", labels, 'pro', True)
        >>> print('Intensity:' in prompt)  # True

    Note:
        - Uses tier-specific few-shot examples for better accuracy
        - Includes step-by-step reasoning instructions
        - Enforces strict adherence to allowed labels
        - Formats output for easy parsing
        - Handles missing tier examples gracefully
    """
    labels_line = ", ".join(allowed_labels)
    intensity_clause = (
        "\n4. Also provide an intensity label from: neutral, mild, moderate, strong, intense."
        if want_intensity
        else ""
    )
    intensity_fmt = "\nIntensity: <intensity label>" if want_intensity else ""

    few_shots = (
        "\n".join(
            f"{s.strip()}    {e.strip()}"
            for s, e in TIER_SPECIFIC_FEW_SHOTS.get(plan_name.lower(), [])
        )
        or "(No specific examples for this tier.)"
    )

    return f"""
You are an expert emotion classifier. Read the sentence carefully and analyse its emotional content.
1. Explain your reasoning step by step.
2. Then, provide the final emotion classification from these options only:
   {labels_line}.{intensity_clause}
3. Do NOT use any emotion (or intensity) outside this list.

Few-shot examples (for the {plan_name} plan):
{few_shots}

Now classify the emotion in the following sentence:
Sentence: {sentence}

Respond in this format:
Reasoning: <your reasoning>
Answer: <final emotion in lowercase>{intensity_fmt}
""".strip()


# ─────────────────── 3. Review prompt builder (second pass) ───────────────
def build_review_prompt(
    sentence: str,
    predicted_emotion: str,
    actual_emotion: str,
    allowed_labels: List[str],
    want_intensity: bool = False,
) -> str:
    """
    Build a review prompt for emotion classification correction.

    Creates a specialized prompt for reviewing and potentially correcting
    initial emotion predictions. This is used for model validation, training
    data generation, and improving classification accuracy.

    Args:
        sentence (str): Original input text that was classified
        predicted_emotion (str): Initial model prediction
        actual_emotion (str): Ground truth or expected emotion label
        allowed_labels (List[str]): Valid emotion labels for comparison
        want_intensity (bool): Whether to include intensity assessment

    Returns:
        str: Formatted review prompt for LLM inference

    Examples:
        >>> labels = ['joy', 'sadness', 'anger', 'neutral']
        >>> prompt = build_review_prompt(
        ...     "I feel okay",
        ...     "joy",
        ...     "neutral",
        ...     labels,
        ...     False
        ... )
        >>> print("Predicted Emotion:" in prompt)  # True
        >>> print("Actual Emotion" in prompt)  # True

    Note:
        - Provides context about initial prediction vs. ground truth
        - Encourages reflection and reasoning about the correction
        - Maintains consistent output formatting
        - Supports intensity correction for Pro tier
        - Helps improve model performance through iterative refinement
    """
    labels_line = ", ".join(allowed_labels)
    intensity_ln = (
        "Valid intensity labels: neutral, mild, moderate, strong, intense."
        if want_intensity
        else ""
    )
    intensity_fmt = "\nIntensity: <intensity label>" if want_intensity else ""

    return f"""
You are an expert emotion classifier. Re-evaluate the following information.

Sentence: "{sentence}"
Predicted Emotion: {predicted_emotion}
Actual Emotion (CSV): {actual_emotion}

Valid emotions:
{labels_line}
{intensity_ln}

Reflect on your initial prediction and the actual emotion.
Adjust your answer if needed, adhering strictly to the valid emotions.

Respond in this format:
Reasoning: <your reasoning>
Answer: <final emotion in lowercase>{intensity_fmt}
""".strip()


# ─────────────────── 4. ***Compatibility shim for legacy imports*** ────────
# The old tests & some legacy code expect these three names.
# They are light placeholders and do not affect the new builder API.
PROMPT_TEMPLATE = (
    "You are an emotion classifier. Give ONLY the emotion.\n" "Sentence: {sentence}"
)
REVIEW_TEMPLATE = (
    "You predicted {predicted} but the correct label is {actual}. "
    "Explain briefly and then output ONLY the correct emotion."
)
FEW_SHOT_EXAMPLES = [
    ("I can’t wait for the party tonight!", "excitement"),
    ("I feel so down today.", "sadness"),
]

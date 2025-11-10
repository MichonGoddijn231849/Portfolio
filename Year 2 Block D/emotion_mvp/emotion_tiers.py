# emotion_mvp/emotion_tiers.py
"""
Emotion Tier Configuration Module

This module defines the emotion labels available for different subscription tiers
in the Emotion MVP system. Each tier provides access to different sets of emotions
with increasing complexity and granularity.

Tier Structure:
- Basic: 7 fundamental emotions suitable for general use
- Plus: Extended set of 23 emotions for detailed analysis
- Pro: Comprehensive set of 27 emotions for professional applications

The tier system allows for gradual feature access and pricing models
while maintaining consistency across the emotion classification pipeline.
"""

# Basic tier: 7 fundamental emotions
BASIC_LABELS = ["happy", "sad", "mad", "scared", "surprised", "disgusted", "neutral"]

# Plus tier: Extended emotion set with 23 categories
PLUS_LABELS = [
    "excitement",
    "confusion",
    "surprise",
    "neutral",
    "optimism",
    "pride",
    "curiosity",
    "fear",
    "amusement",
    "joy",
    "desire",
    "annoyance",
    "nervousness",
    "gratitude",
    "approval",
    "realization",
    "disappointment",
    "caring",
    "sadness",
    "admiration",
    "disapproval",
    "anger",
    "remorse",
]

# Pro tier: Comprehensive emotion set with 27 categories
PRO_LABELS = [
    "excitement",
    "confusion",
    "surprise",
    "neutral",
    "optimism",
    "pride",
    "curiosity",
    "fear",
    "amusement",
    "joy",
    "desire",
    "annoyance",
    "nervousness",
    "gratitude",
    "approval",
    "realization",
    "disappointment",
    "caring",
    "sadness",
    "admiration",
    "disapproval",
    "anger",
    "remorse",
    "relief",
    "love",
    "disgust",
    "embarrassment",
]

# Mapping of tier names to their corresponding emotion label sets
EMOTION_TIERS = {"basic": BASIC_LABELS, "plus": PLUS_LABELS, "pro": PRO_LABELS}

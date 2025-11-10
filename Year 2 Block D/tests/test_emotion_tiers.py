# Fix import based on actual project structure.
# Adjust this if emotion_tiers.py is inside a subdirectory like 'emotion_mvp'
"""Tests for the emotion tiers configuration.

This module contains unit tests for the emotion tiers system that defines
different emotion label sets for basic, plus, and pro subscription plans.
"""
from emotion_mvp import emotion_tiers


def test_emotion_tiers_keys():
    """Test that all required emotion tier keys are present.

    Tests:
        - All subscription plan tiers are defined
        - Tier keys match expected plan names
    """
    assert set(emotion_tiers.EMOTION_TIERS.keys()) == {"basic", "plus", "pro"}


def test_basic_labels():
    """Test that basic tier labels are correctly defined.

    Tests:
        - Basic tier uses BASIC_LABELS constant
        - Label consistency between tier definition and constant
    """
    assert emotion_tiers.EMOTION_TIERS["basic"] == emotion_tiers.BASIC_LABELS


def test_plus_labels():
    """Test that plus tier labels are correctly defined.

    Tests:
        - Plus tier uses PLUS_LABELS constant
        - Label consistency between tier definition and constant
    """
    assert emotion_tiers.EMOTION_TIERS["plus"] == emotion_tiers.PLUS_LABELS


def test_pro_labels():
    """Test that pro tier labels are correctly defined.

    Tests:
        - Pro tier uses PRO_LABELS constant
        - Label consistency between tier definition and constant
    """
    assert emotion_tiers.EMOTION_TIERS["pro"] == emotion_tiers.PRO_LABELS


def test_label_uniqueness():
    """Test that emotion labels within each tier are unique.

    Tests:
        - No duplicate labels within any tier
        - Label set integrity for all subscription plans
    """
    for tier_name, labels in emotion_tiers.EMOTION_TIERS.items():
        assert len(labels) == len(set(labels)), f"Duplicate labels found in {tier_name}"

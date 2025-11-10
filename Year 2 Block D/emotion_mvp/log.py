"""
Logging Configuration Module

This module provides centralized logging configuration for the Emotion MVP system.
It ensures consistent log formatting, levels, and output across all components.

Features:
- Consistent log formatting with timestamps and component names
- Configurable log levels
- Stdout output for better integration with container environments
- No duplicate handlers to prevent log message duplication
- Component-specific logger names for debugging

The logging system helps with debugging, monitoring, and performance analysis
across the entire emotion classification pipeline.
"""

import logging
import sys


def get_logger(name="emotion"):
    """
    Get or create a configured logger instance for the specified component.

    Creates a logger with standardized formatting and output configuration.
    Uses singleton pattern to prevent duplicate handlers and ensure consistent
    logging behavior across the application.

    Args:
        name (str): Logger name, typically the component or module name.
                   Defaults to "emotion" for general use.

    Returns:
        logging.Logger: Configured logger instance ready for use

    Examples:
        >>> log = get_logger("classifier")
        >>> log.info("Starting emotion classification")
        [INFO] 2025-06-25 10:30:00,123 | classifier | Starting emotion classification

        >>> log = get_logger("transcriber")
        >>> log.warning("Model download required")
        [WARNING] 2025-06-25 10:30:01,456 | transcriber | Model download required

        >>> # Default logger
        >>> log = get_logger()
        >>> log.error("Pipeline failed")
        [ERROR] 2025-06-25 10:30:02,789 | emotion | Pipeline failed

    Note:
        - Uses INFO level by default for production readiness
        - Outputs to stdout for container-friendly logging
        - Includes timestamps, log levels, component names, and messages
        - Prevents duplicate handlers through singleton pattern
        - Thread-safe for concurrent usage

    Log Format:
        [LEVEL] TIMESTAMP | COMPONENT | MESSAGE

    Example output:
        [INFO] 2025-06-25 10:30:00,123 | classifier | BERT model loaded successfully
        [DEBUG] 2025-06-25 10:30:01,456 | pipeline | Processing segment 1/5
        [ERROR] 2025-06-25 10:30:02,789 | transcriber | FFmpeg not found in PATH
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(
            logging.Formatter("[%(levelname)s] %(asctime)s | %(name)s | %(message)s")
        )
        logger.addHandler(h)
    return logger

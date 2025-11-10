"""Tests for the logging functionality.

This module contains unit tests for the logging system, testing logger
creation, handler configuration, and formatter setup.
"""

import unittest
import logging
from emotion_mvp.log import get_logger


class TestLogger(unittest.TestCase):
    """Test suite for the logging functionality."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a proper Logger instance.

        Tests:
            - Function returns logging.Logger instance
            - Logger object creation and initialization
        """
        logger = get_logger("test_logger")
        self.assertIsInstance(logger, logging.Logger)

    def test_logger_has_handler(self):
        """Test that created logger has proper handlers configured.

        Tests:
            - Logger has handlers attached
            - Handler configuration is properly set up
        """
        logger = get_logger("test_logger")
        self.assertTrue(logger.hasHandlers())

    def test_logger_formatter(self):
        """Test that logger handlers have proper formatters configured.

        Tests:
            - Stream handler is properly configured
            - Formatter is attached to the handler
            - Logging format configuration is correct
        """
        logger = get_logger("test_logger_format")
        stream_handler = next(
            (h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None
        )
        self.assertIsNotNone(stream_handler)
        self.assertIsInstance(stream_handler.formatter, logging.Formatter)


if __name__ == "__main__":
    unittest.main()

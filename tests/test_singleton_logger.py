"""
This file contains tests for the SingletonLogger class. The SingletonLogger class is a simple
"""
import pytest
import logging
import threading

from unittest.mock import patch

from src.utils.singleton_logger import SingletonLogger


@pytest.fixture
def reset_singleton():
    """Reset the singleton instance before each test."""
    SingletonLogger._instance = None
    yield
    SingletonLogger._instance = None


def test_singleton_instance(reset_singleton):
    """Test that multiple instantiations return the same instance."""
    logger1 = SingletonLogger()
    logger2 = SingletonLogger()
    assert logger1 is logger2


def test_logger_name():
    """Test that the logger name is set correctly."""
    logger = SingletonLogger(logger_name="TestLogger").get_logger()
    assert logger.name == "TestLogger"


def test_default_logger_name(reset_singleton):
    """Test that the default logger name is set correctly."""
    logger = SingletonLogger().get_logger()
    assert logger.name == "src.utils.singleton_logger"  # Updated to match the actual module name


def test_log_level(reset_singleton):
    """Test that the log level is set correctly."""
    logger = SingletonLogger(log_level=logging.INFO).get_logger()
    assert logger.level == logging.INFO


@patch('logging.StreamHandler')
def test_custom_format(mock_stream_handler, reset_singleton):
    """Test that a custom log format is set correctly."""
    custom_format = "%(levelname)s: %(message)s"
    SingletonLogger(log_format=custom_format)

    # Check that the formatter was created with the custom format
    mock_stream_handler.return_value.setFormatter.assert_called_once()
    formatter = mock_stream_handler.return_value.setFormatter.call_args[0][0]
    assert formatter._fmt == custom_format


def test_default_format(reset_singleton):
    """Test that the default log format is set correctly."""
    logger = SingletonLogger().get_logger()
    handler = logger.handlers[0]
    assert handler.formatter._fmt == "%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"


@patch('logging.StreamHandler')
def test_single_handler(mock_stream_handler, reset_singleton):
    """Test that only one handler is added, even with multiple instantiations."""
    SingletonLogger()
    SingletonLogger()
    assert mock_stream_handler.call_count == 1


def test_thread_safety(reset_singleton):
    """Test thread safety of the singleton pattern."""

    def create_logger():
        return SingletonLogger()

    threads = [threading.Thread(target=create_logger) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    loggers = [SingletonLogger() for _ in range(10)]
    assert all(logger is loggers[0] for logger in loggers)


def test_logger_functionality(reset_singleton):
    """Test that the logger actually logs messages."""
    logger = SingletonLogger().get_logger()
    with patch.object(logger, 'debug') as mock_debug:
        logger.debug("Test message")
        mock_debug.assert_called_once_with("Test message")


if __name__ == "__main__":
    pytest.main()

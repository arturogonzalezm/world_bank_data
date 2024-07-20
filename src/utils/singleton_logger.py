"""
SingletonLogger class is a singleton class that provides a single instance of logger object.
"""

import logging
import threading


class SingletonLogger:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, logger_name=None, log_level=logging.DEBUG, log_format=None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_logger(logger_name, log_level, log_format)
        return cls._instance

    def _initialize_logger(self, logger_name, log_level, log_format):
        self._logger = logging.getLogger(logger_name or __name__)
        self._logger.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        if log_format:
            formatter = logging.Formatter(log_format)
        else:
            formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self._logger.addHandler(console_handler)

    def get_logger(self):
        return self._logger

# logger = SingletonLogger().get_logger()

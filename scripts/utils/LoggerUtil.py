import logging
import os
from typing import Any

import __main__


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class SuppressNameIfMatchesTopScript(logging.Filter):
    def __init__(self, top_script: str):
        super().__init__()
        self.top_script = top_script

    def filter(self, record: logging.LogRecord) -> bool:
        # suppress name if it matches top_script (without extension)
        if record.name == self.top_script:
            record.name = ""  # blank the logger name
        else:
            record.name = " -> " + record.name
        return True


class Logger:
    def __init__(self, category: str):
        self.default_category = category
        self.base_logger = logging.getLogger(category)
        self.base_logger.setLevel(logging.DEBUG)

        if self.base_logger.hasHandlers():
            self.base_logger.handlers.clear()

        # Get top script basename without extension
        top_script_file = os.path.basename(getattr(__main__, "__file__", "interactive"))
        top_script = os.path.splitext(top_script_file)[0]

        fmt = "[%(top_script)s%(name)s] %(levelname)s: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = ColorFormatter(fmt, datefmt)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        handler.addFilter(SuppressNameIfMatchesTopScript(top_script))

        self.base_logger.addHandler(handler)

        self.logger = logging.LoggerAdapter(
            self.base_logger,
            {"top_script": top_script, "separator": " | " if category != top_script else ""},
        )

    def _log(self, msg: str, level: int, category: str = ""):
        name = category or self.default_category
        logger = logging.getLogger(name)

        if not logger.hasHandlers():
            for h in self.base_logger.handlers:
                logger.addHandler(h)

        top_script_file = os.path.basename(getattr(__main__, "__file__", "interactive"))
        top_script = os.path.splitext(top_script_file)[0]

        adapter = logging.LoggerAdapter(
            logger,
            {"top_script": top_script, "separator": " | " if name != top_script else ""},
        )

        adapter.setLevel(level)
        adapter.log(level, msg)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(msg, logging.DEBUG, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(msg, logging.INFO, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(msg, logging.WARNING, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(msg, logging.ERROR, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log(msg, logging.CRITICAL, *args, **kwargs)


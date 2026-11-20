"""Structured logging configuration for Q-TRACE."""

import logging
import sys
from typing import Optional
from backend.app.core.config import get_settings


class QTraceFormatter(logging.Formatter):
    """Clean, consistent log formatter with millisecond timestamps."""

    FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure root and application loggers."""
    settings = get_settings()
    level_name = (log_level or settings.LOG_LEVEL).upper()
    numeric_level = getattr(logging, level_name, logging.INFO)

    # Configure root logger handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(QTraceFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers during re-initialization
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Retrieve a namespaced application logger."""
    return logging.getLogger(f"qtrace.{name}")


"""Structured logging configuration for Harvest Signal API."""

import json
import logging
import sys
from datetime import UTC, datetime


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs JSON-like structured log lines."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(UTC).isoformat()
        message = record.getMessage()
        log_line = json.dumps({
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
        })
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log_line += "\n" + record.exc_text
        return log_line


def setup_logging() -> None:
    """Configure the root logger with structured JSON-like output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

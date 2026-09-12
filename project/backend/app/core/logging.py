"""Structured JSON logging configuration."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

FORBIDDEN_LOG_KEYS = {"password", "token", "access_token", "secret", "authorization"}


class JSONFormatter(logging.Formatter):
    """Custom formatter emitting log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach extra contextual data if available
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            sanitized_extra = {}
            for k, v in record.extra.items():
                if any(forbidden in k.lower() for forbidden in FORBIDDEN_LOG_KEYS):
                    sanitized_extra[k] = "[REDACTED]"
                else:
                    sanitized_extra[k] = v
            log_entry["context"] = sanitized_extra

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with structured JSON formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

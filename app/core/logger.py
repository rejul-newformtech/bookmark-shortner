import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict[str, Any] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_object)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Ensure log directory exists
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    text_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    json_formatter = JSONFormatter()

    # 1. Console Handler (Format governed by LOG_FORMAT setting)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    if settings.LOG_FORMAT.lower() == "json":
        console_handler.setFormatter(json_formatter)
    else:
        console_handler.setFormatter(text_formatter)
    logger.addHandler(console_handler)

    # 2. Text Log File Handler (logs/app.log)
    text_file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    text_file_handler.setLevel(logging.INFO)
    text_file_handler.setFormatter(text_formatter)
    logger.addHandler(text_file_handler)

    # 3. JSON Log File Handler (logs/app_json.log)
    json_file_handler = logging.FileHandler(log_dir / "app_json.log", encoding="utf-8")
    json_file_handler.setLevel(logging.INFO)
    json_file_handler.setFormatter(json_formatter)
    logger.addHandler(json_file_handler)

    logger.propagate = False
    return logger

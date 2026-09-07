import contextvars
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings

current_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_user_id", default=None
)
user_id_logged: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "user_id_logged", default=False
)


def set_current_user_id(user_id: str | None) -> None:
    """Set the user ID for the current request context."""
    current_user_id.set(user_id)
    user_id_logged.set(False)


def reset_user_context() -> None:
    """Reset user context at start or end of request."""
    current_user_id.set(None)
    user_id_logged.set(False)


class UserContextFilter(logging.Filter):
    """Logging filter that attaches user_id to the first log record of a request."""

    def filter(self, record: logging.LogRecord) -> bool:
        uid = current_user_id.get()
        if uid and not user_id_logged.get():
            record.user_id = uid  # type: ignore[attr-defined]
            user_id_logged.set(True)
        else:
            record.user_id = None  # type: ignore[attr-defined]
        return True


class TextFormatter(logging.Formatter):
    """Custom text formatter that includes [user_id: <id>] on first log per request."""

    def format(self, record: logging.LogRecord) -> str:
        uid = getattr(record, "user_id", None)
        base = super().format(record)
        if uid:
            sep = f" - {record.levelname} - "
            prefix, found, suffix = base.partition(sep)
            if found:
                return f"{prefix}{sep}[user_id: {uid}] {suffix}"
            return f"[user_id: {uid}] {base}"
        return base


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict[str, Any] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        uid = getattr(record, "user_id", None)
        if uid:
            log_object["user_id"] = uid
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_object)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.addFilter(UserContextFilter())

    # Ensure log directory exists
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    text_formatter = TextFormatter(
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

"""
Houssem AI - Audit logging.
Writes JSON-lines to logs/audit.log + optional stdout.
"""

import os
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "audit.log")
os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record):
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "event": getattr(record, "event", "generic"),
            "session": getattr(record, "session", None),
            "user": getattr(record, "user", None),
            "domain": getattr(record, "domain", None),
            "detail": record.getMessage(),
            "extra": getattr(record, "extra_data", None),
        }
        return json.dumps(payload, ensure_ascii=False)


# ---------- Logger setup ----------
audit_logger = logging.getLogger("houssem.audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False

if not audit_logger.handlers:
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(JsonFormatter())
    audit_logger.addHandler(handler)

    # Also log to stdout for cloud platforms (Streamlit Cloud, Railway, etc.)
    stream = logging.StreamHandler()
    stream.setFormatter(JsonFormatter())
    audit_logger.addHandler(stream)


# ---------- Public helper ----------
def audit(
    event: str,
    detail: str,
    session: Optional[str] = None,
    user: Optional[str] = None,
    domain: Optional[str] = None,
    level: str = "INFO",
    **extra,
):
    """Record an audit event."""
    audit_logger.log(
        getattr(logging, level.upper(), logging.INFO),
        detail,
        extra={
            "event": event,
            "session": session,
            "user": user,
            "domain": domain,
            "extra_data": extra or None,
        },
    )

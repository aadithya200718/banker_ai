"""
Audit Service
==============
Immutable audit log entries for compliance (RBI/GDPR).
"""

import logging
from sqlalchemy.orm import Session
from backend.models import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    banker_id: int,
    action: str,
    status: str = "SUCCESS",
    decision_id: int | None = None,
    details: dict | None = None,
    error_message: str | None = None,
):
    """Insert an immutable audit log entry."""
    entry = AuditLog(
        banker_id=banker_id,
        action=action,
        decision_id=decision_id,
        details=details or {},
        status=status,
        error_message=error_message,
    )
    db.add(entry)
    db.commit()
    logger.info(f"📋 Audit: banker={banker_id} action={action} status={status}")

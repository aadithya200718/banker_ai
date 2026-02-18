"""
Logger DB Module
=================
SQLite-based audit logging for verification results.
Zero-setup — database file is auto-created.
"""

import sqlite3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "verification_logs.db")


def _get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the logs table if it doesn't exist."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS verification_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id      TEXT NOT NULL,
            timestamp       TEXT NOT NULL,
            similarity_score REAL NOT NULL,
            confidence_level TEXT NOT NULL,
            decision        TEXT NOT NULL,
            variations      TEXT DEFAULT '[]',
            explanation     TEXT DEFAULT '',
            quality_json    TEXT DEFAULT '{}',
            processing_time_ms REAL DEFAULT 0,
            threshold_adjustment REAL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized at {DB_PATH}")


def log_verification(
    request_id: str,
    similarity_score: float,
    confidence_level: str,
    decision: str,
    variations: list,
    explanation: str,
    quality: dict,
    processing_time_ms: float,
    threshold_adjustment: float = 0.0,
):
    """Insert a verification log entry."""
    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO verification_logs
            (request_id, timestamp, similarity_score, confidence_level,
             decision, variations, explanation, quality_json,
             processing_time_ms, threshold_adjustment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request_id,
            datetime.utcnow().isoformat(),
            similarity_score,
            confidence_level,
            decision,
            json.dumps(variations),
            explanation,
            json.dumps(quality),
            processing_time_ms,
            threshold_adjustment,
        ),
    )
    conn.commit()
    conn.close()
    logger.info(f"📋 Logged verification {request_id}")


def get_recent_logs(limit: int = 50) -> list[dict]:
    """Return the most recent verification logs."""
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT * FROM verification_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        entry = dict(row)
        # Parse JSON fields
        try:
            entry["variations"] = json.loads(entry.get("variations", "[]"))
        except Exception:
            entry["variations"] = []
        try:
            entry["quality_json"] = json.loads(entry.get("quality_json", "{}"))
        except Exception:
            entry["quality_json"] = {}
        results.append(entry)

    return results


def get_log_count() -> int:
    """Return total verification count."""
    conn = _get_connection()
    count = conn.execute("SELECT COUNT(*) FROM verification_logs").fetchone()[0]
    conn.close()
    return count


# Initialize on import
init_db()

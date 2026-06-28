"""
session_store.py - Pure in-memory session storage.
No files written to disk for session data — everything lives in RAM.
Sessions expire after 2 hours of inactivity.
"""

import time
import threading
import logging

logger = logging.getLogger(__name__)

# Global in-memory store: {session_id: {"data": ..., "last_accessed": timestamp}}
_store: dict[str, dict] = {}
_lock = threading.Lock()

SESSION_TTL_SECONDS = 7200  # 2 hours


def save_session(session_id: str, data: dict) -> None:
    """Store session data in memory."""
    with _lock:
        _store[session_id] = {
            "data": data,
            "last_accessed": time.time(),
        }
    logger.debug(f"Session saved: {session_id} (total active: {len(_store)})")


def get_session(session_id: str) -> dict | None:
    """Retrieve session data. Returns None if not found or expired."""
    with _lock:
        entry = _store.get(session_id)
        if not entry:
            return None
        # Check TTL
        if time.time() - entry["last_accessed"] > SESSION_TTL_SECONDS:
            del _store[session_id]
            logger.info(f"Session expired and removed: {session_id}")
            return None
        # Refresh access time
        entry["last_accessed"] = time.time()
        return entry["data"]


def delete_session(session_id: str) -> None:
    """Remove a session after use."""
    with _lock:
        if session_id in _store:
            del _store[session_id]
            logger.debug(f"Session deleted: {session_id}")


def cleanup_expired() -> int:
    """Remove all expired sessions. Returns count removed."""
    now = time.time()
    with _lock:
        expired = [sid for sid, entry in _store.items()
                   if now - entry["last_accessed"] > SESSION_TTL_SECONDS]
        for sid in expired:
            del _store[sid]
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired session(s)")
    return len(expired)


def active_session_count() -> int:
    with _lock:
        return len(_store)


# Background cleanup thread — runs every 30 minutes
def _start_cleanup_thread():
    def _run():
        while True:
            time.sleep(1800)
            cleanup_expired()
    t = threading.Thread(target=_run, daemon=True)
    t.start()

_start_cleanup_thread()

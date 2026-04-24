"""
token_issuer.py — Capability Token Issuer

SINGLE RESPONSIBILITY: Create signed capability tokens and session records.
No validation, no anomaly detection. Just issuance.

DEPENDENCY INVERSION: Depends only on crypto_utils (low-level primitive),
not on higher-level auth agents.
"""

from datetime import datetime, timedelta
from .crypto_utils import generate_session_id, generate_capability_token
from .session_store import SessionStore

DEFAULT_CAPABILITIES = [
    "can_query", "can_upload", "can_draft_rfi",
    "can_scan_contradictions", "can_manage_projects",
]


def issue_session(project_id: str, behavioral_hash: str = "",
                  capabilities: list = None, ttl_sec: int = 900) -> dict:
    session_id = generate_session_id()
    caps = capabilities or DEFAULT_CAPABILITIES.copy()
    token = generate_capability_token(session_id, caps, behavioral_hash, ttl_sec)

    session = {
        "id": session_id, "project_id": project_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "expires": (datetime.utcnow() + timedelta(seconds=ttl_sec)).isoformat() + "Z",
        "capabilities": caps, "behavioral_hash": behavioral_hash,
        "token": token, "failed_attempts": 0,
        "anomaly_score": 0.0, "status": "active",
    }
    SessionStore().save(session)
    return {"session_id": session_id, "token": token, "capabilities": caps,
            "expires": session["expires"]}

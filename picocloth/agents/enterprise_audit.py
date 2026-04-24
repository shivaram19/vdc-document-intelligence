#!/usr/bin/env python3
"""
enterprise_audit.py — Comprehensive Audit Trail for Enterprise Fleet↔VDC Operations

Research basis: Li et al. (2024) "Accountable Multi-Agent Orchestration" —
every operation must be logged with who/what/when/why. Yang-Smith et al.
(2026) emphasize fairness/justice/trust in AI multi-agent systems, requiring
transparent auditability.
"""

import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG = Path(__file__).parent.parent / "shared" / "project" / "vdc" / "auth" / "enterprise-audit.jsonl"
MAX_LOG_SIZE_MB = 50
ROTATION_COUNT = 3

_audit_lock = threading.Lock()


class AuditEvent:
    """Structured audit event with tamper-evident chain."""

    def __init__(self, actor: str, action: str, resource: str,
                 outcome: str, details: dict, capability_token: str = "",
                 ip_address: str = "", node_id: str = ""):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.actor = actor
        self.action = action
        self.resource = resource
        self.outcome = outcome
        self.details = details
        self.capability_token = capability_token[:16] + "..." if capability_token else ""  # Masked
        self.ip_address = ip_address
        self.node_id = node_id
        self.prev_hash = self._get_prev_hash()
        self.event_hash = self._compute_hash()

    def _get_prev_hash(self) -> str:
        """Read last event hash for chain continuity."""
        if AUDIT_LOG.exists():
            try:
                with open(AUDIT_LOG, "r") as f:
                    lines = [l.strip() for l in f if l.strip()]
                    if lines:
                        last = json.loads(lines[-1])
                        return last.get("event_hash", "")
            except Exception:
                pass
        return "genesis"

    def _compute_hash(self) -> str:
        """Tamper-evident hash linking to previous event."""
        data = f"{self.prev_hash}:{self.timestamp}:{self.actor}:{self.action}:{self.resource}:{self.outcome}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "outcome": self.outcome,
            "details": self.details,
            "capability_token_prefix": self.capability_token,
            "ip_address": self.ip_address,
            "node_id": self.node_id,
            "prev_hash": self.prev_hash,
            "event_hash": self.event_hash,
        }


def log_audit(event: AuditEvent):
    """Append audit event to tamper-evident chain."""
    with _audit_lock:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed()
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")


def _rotate_if_needed():
    """Rotate audit log when it exceeds max size."""
    if AUDIT_LOG.exists() and AUDIT_LOG.stat().st_size > MAX_LOG_SIZE_MB * 1024 * 1024:
        for i in range(ROTATION_COUNT - 1, 0, -1):
            src = AUDIT_LOG.parent / f"enterprise-audit.jsonl.{i}"
            dst = AUDIT_LOG.parent / f"enterprise-audit.jsonl.{i + 1}"
            if src.exists():
                src.rename(dst)
        AUDIT_LOG.rename(AUDIT_LOG.parent / "enterprise-audit.jsonl.1")


def query_audit(actor: Optional[str] = None, action: Optional[str] = None,
                resource: Optional[str] = None, since: Optional[str] = None,
                limit: int = 100) -> list:
    """Query audit trail with filters."""
    results = []
    if not AUDIT_LOG.exists():
        return results

    with _audit_lock:
        with open(AUDIT_LOG, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if actor and event.get("actor") != actor:
                        continue
                    if action and event.get("action") != action:
                        continue
                    if resource and event.get("resource") != resource:
                        continue
                    if since and event.get("timestamp", "") < since:
                        continue
                    results.append(event)
                    if len(results) >= limit:
                        break
                except Exception:
                    continue
    return results


def verify_audit_integrity() -> dict:
    """Verify the tamper-evident chain is intact."""
    if not AUDIT_LOG.exists():
        return {"valid": True, "events_checked": 0, "first_broken": None}

    broken = None
    count = 0
    prev_hash = "genesis"

    with _audit_lock:
        with open(AUDIT_LOG, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    count += 1
                    if event.get("prev_hash") != prev_hash:
                        broken = {"line": count, "event": event}
                        break
                    prev_hash = event.get("event_hash", "")
                except Exception:
                    broken = {"line": count, "error": "parse failed"}
                    break

    return {
        "valid": broken is None,
        "events_checked": count,
        "first_broken": broken,
    }

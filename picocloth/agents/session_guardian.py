#!/usr/bin/env python3
"""
Session Guardian Agent (node-c: memory-guardian)
Manages active sessions, behavioral baselines, and revocation orchestration.

This agent acts as the persistent memory layer for the auth mesh,
tracking who is authenticated, what they can do, and whether their
behavior has drifted from baseline.

Usage:
    python session_guardian.py --list
    python session_guardian.py --revoke sess_xxx --reason "anomaly detected"
    python session_guardian.py --cleanup
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from vdc_core import SESSIONS_DIR, AUTH_DIR, write_json, read_json, append_event


def list_sessions() -> dict:
    """List all active and recently revoked sessions."""
    sessions = read_json(SESSIONS_DIR / "state.json")
    active = sessions.get("active_sessions", [])
    revoked = sessions.get("revoked_tokens", [])

    # Filter expired active sessions
    now = datetime.utcnow()
    valid_active = []
    expired = []
    for s in active:
        expires = datetime.fromisoformat(s["expires"].replace("Z", "+00:00"))
        if now < expires.replace(tzinfo=None):
            valid_active.append({
                "id": s["id"],
                "project_id": s.get("project_id", ""),
                "capabilities": s.get("capabilities", []),
                "anomaly_score": s.get("anomaly_score", 0),
                "status": s.get("status", "active"),
                "expires_in_min": int((expires.replace(tzinfo=None) - now).total_seconds() / 60),
            })
        else:
            expired.append(s)

    # Clean up expired from active list
    if expired:
        sessions["active_sessions"] = [s for s in active if s not in expired]
        write_json(SESSIONS_DIR / "state.json", sessions)

    return {
        "active_count": len(valid_active),
        "active_sessions": valid_active,
        "revoked_count": len(revoked),
        "recently_revoked": revoked[-5:] if revoked else [],
    }


def revoke_session(session_id: str, reason: str = "manual revocation"):
    """Revoke a session by ID."""
    sessions = read_json(SESSIONS_DIR / "state.json")
    active = sessions.get("active_sessions", [])
    revoked = sessions.get("revoked_tokens", [])

    target = None
    for s in active:
        if s["id"] == session_id:
            target = s
            break

    if not target:
        return {"error": f"Session {session_id} not found."}

    active.remove(target)
    revoked.append({
        "session_id": session_id,
        "token": target["token"],
        "revoked_at": datetime.utcnow().isoformat() + "Z",
        "reason": reason,
    })

    sessions["active_sessions"] = active
    sessions["revoked_tokens"] = revoked
    write_json(SESSIONS_DIR / "state.json", sessions)

    append_event("auth", {
        "type": "session_revoked",
        "session_id": session_id,
        "reason": reason,
        "by": "session_guardian",
    })

    return {"revoked": session_id, "reason": reason}


def cleanup_expired():
    """Remove expired sessions and old revoked tokens."""
    sessions = read_json(SESSIONS_DIR / "state.json")
    now = datetime.utcnow()

    # Clean active
    active = sessions.get("active_sessions", [])
    valid = []
    removed = 0
    for s in active:
        expires = datetime.fromisoformat(s["expires"].replace("Z", "+00:00"))
        if now < expires.replace(tzinfo=None):
            valid.append(s)
        else:
            removed += 1
    sessions["active_sessions"] = valid

    # Clean old revoked (keep last 30 days)
    revoked = sessions.get("revoked_tokens", [])
    cutoff = now - datetime.timedelta(days=30)
    recent = []
    for r in revoked:
        try:
            rt = datetime.fromisoformat(r["revoked_at"].replace("Z", "+00:00"))
            if rt.replace(tzinfo=None) > cutoff:
                recent.append(r)
        except Exception:
            recent.append(r)
    sessions["revoked_tokens"] = recent

    write_json(SESSIONS_DIR / "state.json", sessions)

    return {"removed_expired": removed, "active_remaining": len(valid), "revoked_remaining": len(recent)}


def get_session_stats() -> dict:
    """Get auth mesh statistics."""
    sessions = read_json(SESSIONS_DIR / "state.json")
    registry = read_json(AUTH_DIR / "registry.json")

    active = sessions.get("active_sessions", [])
    revoked = sessions.get("revoked_tokens", [])
    baselines = registry.get("baselines", {})

    # Compute avg anomaly score
    scores = [s.get("anomaly_score", 0) for s in active]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Capability distribution
    cap_counts = {}
    for s in active:
        for c in s.get("capabilities", []):
            cap_counts[c] = cap_counts.get(c, 0) + 1

    return {
        "total_active_sessions": len(active),
        "total_revoked_sessions": len(revoked),
        "total_behavioral_baselines": len(baselines),
        "average_anomaly_score": round(avg_score, 3),
        "capability_distribution": cap_counts,
        "mesh_health": "healthy" if avg_score < 0.3 else "warning" if avg_score < 0.6 else "critical",
    }


def main():
    parser = argparse.ArgumentParser(description="Medha Session Guardian Agent")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--revoke", help="Revoke session by ID")
    parser.add_argument("--reason", default="manual revocation", help="Revocation reason")
    parser.add_argument("--cleanup", action="store_true", help="Clean expired sessions")
    parser.add_argument("--stats", action="store_true", help="Show auth mesh stats")
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_sessions(), indent=2))
    elif args.revoke:
        print(json.dumps(revoke_session(args.revoke, args.reason), indent=2))
    elif args.cleanup:
        print(json.dumps(cleanup_expired(), indent=2))
    elif args.stats:
        print(json.dumps(get_session_stats(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

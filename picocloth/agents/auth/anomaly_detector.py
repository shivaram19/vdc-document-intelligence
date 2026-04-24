"""
anomaly_detector.py — Behavioral Anomaly Scorer

SINGLE RESPONSIBILITY: Compare current behavioral profile against baseline
and compute anomaly score. No session management, no token logic.

Research basis: Mondal & Bours (2015) "A computational approach to the
continuous authentication biometric system" — trust function for behavioral drift.
"""

import json
from pathlib import Path

AUTH_DIR = Path(__file__).parent.parent.parent / "shared" / "project" / "vdc" / "auth"
ANOMALY_THRESHOLD = 0.65


def compute_anomaly_score(current: dict, baseline: dict) -> float:
    if not baseline:
        return 0.0
    scores = []
    keys = [("typing_wpm", 1), ("mouse_entropy", 0.01), ("click_rate", 0.01),
            ("scroll_velocity", 1), ("avg_interaction_time", 1)]
    for key, denom in keys:
        if key in current and key in baseline:
            diff = abs(current[key] - baseline[key]) / max(baseline[key], denom)
            scores.append(min(diff, 1.0))
    return sum(scores) / len(scores) if scores else 0.0


def check_anomaly(session_id: str, current_profile: dict) -> dict:
    from .session_store import SessionStore
    session = SessionStore().get(session_id)
    if not session:
        return {"action": "revoke", "reason": "Session not found."}

    baseline = _load_baseline(session.get("behavioral_hash", ""))
    score = compute_anomaly_score(current_profile, baseline)

    # Update session anomaly score
    session["anomaly_score"] = round(score, 3)
    SessionStore().save(session)

    if score > ANOMALY_THRESHOLD:
        return {"action": "rechallenge", "anomaly_score": round(score, 3),
                "reason": f"Behavioral anomaly detected (score: {score:.2f}). Re-authentication required."}
    elif score > ANOMALY_THRESHOLD * 0.7:
        return {"action": "warn", "anomaly_score": round(score, 3),
                "reason": f"Slight behavioral deviation (score: {score:.2f})."}
    return {"action": "ok", "anomaly_score": round(score, 3)}


def _load_baseline(behavioral_hash: str) -> dict:
    path = AUTH_DIR / "registry.json"
    if path.exists():
        return json.loads(path.read_text()).get("baselines", {}).get(behavioral_hash, {})
    return {}

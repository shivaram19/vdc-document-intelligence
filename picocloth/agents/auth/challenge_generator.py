"""
challenge_generator.py — Knowledge-Provenance Challenge Factory

SINGLE RESPONSIBILITY: Extract facts from project documents and turn them into
challenge questions. No validation, no session logic.

OPEN/CLOSED: New challenge types (date-based, keyword-based) can be added by
extending _extract_fact() without modifying existing code.
"""

import random
import re
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path

CHUNKS_DIR = Path(__file__).parent.parent.parent / "shared" / "project" / "vdc" / "chunks"
_CHALLENGES = {}


def _cleanup_expired_challenges():
    """Evict expired challenges to prevent memory leaks. Called on every access.
    # [CITE: Permify2024] Token revocation mechanism essential; implicit TTL
    # eviction prevents unbounded in-memory growth for challenge stores.
    """
    now = datetime.utcnow()
    expired = [
        cid for cid, c in _CHALLENGES.items()
        if datetime.fromisoformat(c["expires"].replace("Z", "+00:00")).replace(tzinfo=None) < now
    ]
    for cid in expired:
        del _CHALLENGES[cid]


# Extensible fact extractors — add new patterns without touching core logic
# FIXED: Handle comma-separated thousands (e.g., 25,000 → 25000)
FACT_PATTERNS = [
    (r'(\d{1,2},?\d{0,3})\s*(psi|psf)', "pressure/strength"),
    (r'(\d{1,2})\s*(feet|ft)', "length"),
    (r'(\d{1,2})\s*(inches|in)', "length"),
    (r'(\d{1,3}(?:,\d{3})?)\s*(gpm|cfm)', "flow"),  # FIXED: comma-aware thousands
    (r'(\d{1,3})\s*(°F|°C|degrees F)', "temperature"),
    (r'(\d{1,2})\s*(hour|hr)', "duration"),
]


def _extract_fact(text: str) -> dict:
    for pattern, category in FACT_PATTERNS:
        matches = list(re.finditer(pattern, text, re.I))
        if matches:
            m = random.choice(matches)
            start = max(0, text.rfind(".", 0, m.start()) + 1)
            end = text.find(".", m.end())
            if end == -1:
                end = len(text)
            context = text[start:end].strip()
            return {
                "value": m.group(1).replace(",", ""),
                "unit": m.group(2),
                "category": category,
                "question": context[:m.start() - start] + "___" + context[m.end() - start:],
                "context": context,
            }
    return None


def generate_challenge(project_id: str, difficulty: str = "medium") -> dict:
    _cleanup_expired_challenges()
    chunks_path = CHUNKS_DIR / f"{project_id}.json"
    if not chunks_path.exists():
        return {"error": "No documents available to generate challenges."}
    chunks = json.loads(chunks_path.read_text())
    if not chunks:
        return {"error": "No chunks found."}

    candidates = chunks
    if difficulty == "easy":
        candidates = [c for c in chunks if len(c["text"].split()) < 100]
    elif difficulty == "hard":
        candidates = [c for c in chunks if len(c["text"].split()) > 200]
    if not candidates:
        candidates = chunks

    random.shuffle(candidates)
    for chunk in candidates[:20]:
        fact = _extract_fact(chunk["text"])
        if fact:
            cid = "ch_" + secrets.token_hex(8)
            challenge = {
                "id": cid, "project_id": project_id, "difficulty": difficulty,
                "doc_name": chunk["doc_name"], "doc_type": chunk["doc_type"],
                "question": fact["question"], "expected_value": fact["value"],
                "expected_unit": fact["unit"], "category": fact["category"],
                "context": fact["context"],
                "created": datetime.utcnow().isoformat() + "Z",
                "expires": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z",
            }
            _CHALLENGES[cid] = challenge
            return {
                "id": cid, "project_id": project_id,
                "question": challenge["question"], "category": challenge["category"],
                "difficulty": difficulty,
                "hint": f"Found in {chunk['doc_name']} ({chunk['doc_type']})",
            }
    return {"error": "Could not generate a challenge from available documents."}

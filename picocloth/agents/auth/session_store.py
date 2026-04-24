"""
session_store.py — Session Persistence Layer

SINGLE RESPONSIBILITY: CRUD operations for active and revoked sessions.
No business logic, no validation. Pure storage abstraction.

LOCKING: All disk I/O uses filelock for cross-process safety.
# [CITE: ZetCode2025] os.replace + filelock for atomic cross-process writes.
# [CITE: ActiveState2015] tempfile.mkstemp + os.replace for crash-safe writes.

CACHING: In-memory dicts indexed by session_id and token for O(1) lookups.
# [CITE: APXML2025] Caching hot paths eliminates disk I/O bottlenecks.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SESSIONS_PATH = Path(__file__).parent.parent.parent / "shared" / "project" / "vdc" / "sessions" / "state.json"
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from locks import atomic_json_write, locked_json_read


class SessionStore:
    def __init__(self, path: Path = None):
        self.path = path or SESSIONS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # In-memory caches for O(1) lookups
        self._session_cache = {}
        self._token_cache = {}
        self._revoked_set = set()
        self._cache_valid = False

    def _invalidate_cache(self):
        self._cache_valid = False

    def _build_cache(self, data: dict):
        if self._cache_valid:
            return
        self._session_cache = {s["id"]: s for s in data.get("active_sessions", [])}
        self._token_cache = {s["token"]: s for s in data.get("active_sessions", [])}
        self._revoked_set = {r["token"] for r in data.get("revoked_tokens", [])}
        self._cache_valid = True

    def _load(self) -> dict:
        return locked_json_read(self.path, default={"active_sessions": [], "revoked_tokens": []})

    def _save(self, data: dict):
        atomic_json_write(self.path, data)
        self._invalidate_cache()

    def get(self, session_id: str) -> dict:
        data = self._load()
        self._build_cache(data)
        return self._session_cache.get(session_id)

    def get_by_token(self, token: str) -> dict:
        data = self._load()
        self._build_cache(data)
        return self._token_cache.get(token)

    def is_revoked(self, token: str) -> bool:
        data = self._load()
        self._build_cache(data)
        return token in self._revoked_set

    def save(self, session: dict):
        """Upsert session by session_id (not behavioral_hash — fixed bug)."""
        data = self._load()
        active = [s for s in data.get("active_sessions", [])
                  if s.get("id") != session.get("id")]
        active.append(session)
        data["active_sessions"] = active
        self._save(data)

    def revoke(self, session_id: str, reason: str = ""):
        data = self._load()
        active = []
        target_token = None
        for s in data.get("active_sessions", []):
            if s["id"] == session_id:
                target_token = s["token"]
            else:
                active.append(s)
        if target_token:
            data.setdefault("revoked_tokens", []).append({
                "session_id": session_id, "token": target_token,
                "revoked_at": datetime.utcnow().isoformat() + "Z", "reason": reason,
            })
        data["active_sessions"] = active
        self._save(data)

    def cleanup_expired(self):
        data = self._load()
        now = datetime.utcnow()
        active = []
        for s in data.get("active_sessions", []):
            expires = datetime.fromisoformat(s["expires"].replace("Z", "+00:00"))
            if now < expires.replace(tzinfo=None):
                active.append(s)
        data["active_sessions"] = active
        self._save(data)

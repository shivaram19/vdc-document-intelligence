"""
crypto_utils.py — Cryptographic Primitives for Agent Attestation

SINGLE RESPONSIBILITY: HMAC-SHA256 token signing/verification + behavioral hashing.
No business logic. Pure crypto. Injectable dependency for all auth agents.

DEPENDENCY INVERSION: Higher-level agents depend on these utilities, not vice versa.
"""

import hmac
import hashlib
import secrets
import json
import os
from datetime import datetime
from pathlib import Path

# Stable secret source — NEVER derived from mutable files like state.json.
# [CITE: RFC2104] HMAC keys must be stable for the lifetime of the token.
# [CITE: NIST800-132] Derivation inputs must be entropy sources, not mutable state.
# [CITE: GitGuardian2026] Generate strong keys (min 32 bytes) with CSPRNG.
# [CITE: WhoisArjen2026] "Rotation is an env var change, not a migration."
# [CITE: S4E2025] Keep signing secrets out of code/config. Use secrets manager.
_MACHINE_SECRET_PATH = Path(__file__).parent.parent.parent / "shared" / ".machine-secret"
_AGENT_SECRET = None


def _ensure_machine_secret() -> str:
    """Return a stable per-machine secret. Created once, never rotated by state changes."""
    if _MACHINE_SECRET_PATH.exists():
        return _MACHINE_SECRET_PATH.read_text().strip()
    s = secrets.token_hex(32)
    _MACHINE_SECRET_PATH.write_text(s)
    _MACHINE_SECRET_PATH.chmod(0o600)
    return s


def _get_agent_secret() -> str:
    global _AGENT_SECRET
    if _AGENT_SECRET is None:
        env_secret = os.environ.get("AGENT_AUTH_SECRET", "")
        if not env_secret:
            env_secret = os.environ.get("API_SECRET", "")
        if not env_secret:
            # [CITE: GitGuardian2026] Never run with hardcoded/default secrets.
            raise RuntimeError(
                "AGENT_AUTH_SECRET or API_SECRET must be set. "
                "Do not run with default secrets in production."
            )
        machine_secret = _ensure_machine_secret()
        _AGENT_SECRET = hmac.new(
            env_secret.encode(), machine_secret.encode(), hashlib.sha256
        ).hexdigest()
    return _AGENT_SECRET


def generate_session_id() -> str:
    return "sess_" + secrets.token_hex(16)


def generate_capability_token(session_id: str, capabilities: list,
                               behavioral_hash: str = "", ttl_sec: int = 900) -> str:
    expiry = int(datetime.utcnow().timestamp()) + ttl_sec
    payload = f"{session_id}:{','.join(sorted(capabilities))}:{behavioral_hash}:{expiry}"
    sig = hmac.new(_get_agent_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}:{sig}"


def verify_capability_token(token: str) -> dict:
    result = {"valid": False, "session_id": "", "capabilities": [], "expiry": 0, "behavioral_hash": ""}
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return result
        session_id, caps_str, behash, expiry_str, provided_sig = parts
        payload = f"{session_id}:{caps_str}:{behash}:{expiry_str}"
        expected = hmac.new(_get_agent_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not secrets.compare_digest(provided_sig, expected):
            return result
        expiry = int(expiry_str)
        if datetime.utcnow().timestamp() > expiry:
            return result
        result.update({"valid": True, "session_id": session_id,
                       "capabilities": [c for c in caps_str.split(",") if c],
                       "expiry": expiry, "behavioral_hash": behash})
    except Exception:
        pass
    return result


def hash_behavioral_profile(profile: dict) -> str:
    data = json.dumps(profile, sort_keys=True, default=str)
    return hashlib.sha256(data.encode()).hexdigest()[:16]

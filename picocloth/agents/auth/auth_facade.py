"""
auth_facade.py — Authentication Mesh Facade

SINGLE RESPONSIBILITY: Provide ONE unified interface to the entire auth system.
Callers (bridge, agents) depend ONLY on this facade, not on individual auth agents.

FACADE PATTERN: Hides the complexity of 6+ auth agents behind a simple API.
DEPENDENCY INVERSION: Bridge depends on AuthFacade (abstraction), not concrete agents.

This is the ONLY auth entry point for external callers.
"""

from .challenge_generator import generate_challenge
from .challenge_validator import validate_challenge
from .token_issuer import issue_session
from .crypto_utils import verify_capability_token, hash_behavioral_profile
from .anomaly_detector import check_anomaly
from .session_store import SessionStore
from .baseline_tracker import BaselineTracker


class AuthFacade:
    """Unified interface to the Medha Authentication Mesh.

    Methods map 1:1 to the 3-factor auth flow:
      1. challenge()     → Factor 1: Knowledge-Provenance
      2. answer()        → Factor 1: Validation
      3. authenticate()  → Issue capability token
      4. authorize()     → Factor 2+3: Token + anomaly verification
    """

    @staticmethod
    def challenge(project_id: str, difficulty: str = "medium") -> dict:
        return generate_challenge(project_id, difficulty)

    @staticmethod
    def answer(challenge_id: str, answer: str) -> dict:
        return validate_challenge(challenge_id, answer)

    @staticmethod
    def authenticate(project_id: str, behavioral_profile: dict = None,
                     capabilities: list = None) -> dict:
        behash = hash_behavioral_profile(behavioral_profile) if behavioral_profile else ""
        return issue_session(project_id, behavioral_hash=behash, capabilities=capabilities)

    @staticmethod
    def authorize(token: str, required_capability: str,
                  current_profile: dict = None) -> dict:
        # Step 1: Token verification
        token_data = verify_capability_token(token)
        if not token_data["valid"]:
            return {"authorized": False, "reason": "Invalid or expired token."}

        # Step 2: Revocation check
        if SessionStore().is_revoked(token):
            return {"authorized": False, "reason": "Token has been revoked."}

        # Step 3: Capability check
        if required_capability and required_capability not in token_data["capabilities"]:
            return {"authorized": False, "reason": f"Missing capability: {required_capability}"}

        # Step 4: Anomaly detection
        if current_profile:
            anomaly = check_anomaly(token_data["session_id"], current_profile)
            if anomaly["action"] == "revoke":
                SessionStore().revoke(token_data["session_id"], anomaly["reason"])
                return {"authorized": False, "reason": anomaly["reason"]}
            elif anomaly["action"] == "rechallenge":
                return {"authorized": False, "reason": anomaly["reason"],
                        "rechallenge": True, "anomaly_score": anomaly["anomaly_score"]}

        # Step 5: Baseline update
        if current_profile:
            BaselineTracker().update(token_data["behavioral_hash"], current_profile)

        return {"authorized": True, "session_id": token_data["session_id"],
                "capabilities": token_data["capabilities"]}

    @staticmethod
    def revoke(session_id: str, reason: str = ""):
        SessionStore().revoke(session_id, reason)

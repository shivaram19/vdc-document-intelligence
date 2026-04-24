"""
Medha Authentication Mesh — SOLID-Compliant Auth Package

Each module has exactly ONE responsibility per SOLID's Single Responsibility Principle.
The auth_facade provides a unified interface (Facade pattern) so callers don't need
to know the internal auth agent decomposition.

Research basis:
- Li et al. (2024) "Agent-Oriented Planning in Multi-Agent Systems" — role specialization
- Fathima & Saravanan (2024) — behavioral biometric MFA with continuous auth
- Mondal & Bours (2015) — computational approach to continuous auth trust functions
"""

from .auth_facade import AuthFacade
from .crypto_utils import verify_capability_token, hash_behavioral_profile
from .challenge_generator import generate_challenge
from .challenge_validator import validate_challenge
from .token_issuer import issue_session
from .anomaly_detector import check_anomaly
from .session_store import SessionStore
from .baseline_tracker import BaselineTracker

__all__ = [
    "AuthFacade",
    "verify_capability_token",
    "hash_behavioral_profile",
    "generate_challenge",
    "validate_challenge",
    "issue_session",
    "check_anomaly",
    "SessionStore",
    "BaselineTracker",
]

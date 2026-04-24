"""
challenge_validator.py — Knowledge Proof Validator

SINGLE RESPONSIBILITY: Check if a user's answer matches the expected document fact.
No challenge generation, no session logic. Pure validation with fuzzy matching.

LISKOV SUBSTITUTION: Any validator implementing validate() interface can be swapped
without breaking callers.
"""

from datetime import datetime
from .challenge_generator import _CHALLENGES


def validate_challenge(challenge_id: str, answer: str) -> dict:
    from .challenge_generator import _cleanup_expired_challenges
    _cleanup_expired_challenges()
    challenge = _CHALLENGES.get(challenge_id)
    if not challenge:
        return {"valid": False, "reason": "Challenge not found or expired."}

    expires = datetime.fromisoformat(challenge["expires"].replace("Z", "+00:00"))
    if datetime.utcnow().replace(tzinfo=None) > expires.replace(tzinfo=None):
        del _CHALLENGES[challenge_id]
        return {"valid": False, "reason": "Challenge expired."}

    expected = challenge["expected_value"].lower().strip()
    provided = answer.lower().strip().replace(",", "")
    valid = (provided == expected or expected in provided or provided in expected
             or _numeric_similarity(expected, provided))

    result = {"valid": valid, "challenge_id": challenge_id,
              "project_id": challenge["project_id"]}

    if valid:
        result["message"] = "Knowledge proof verified."
        result["context"] = challenge["context"]
        del _CHALLENGES[challenge_id]
    else:
        result["reason"] = f"Incorrect. Expected near '{challenge['expected_value']}' {challenge['expected_unit']}."

    return result


def _numeric_similarity(a: str, b: str) -> bool:
    try:
        fa, fb = float(a), float(b)
        return abs(fa - fb) / max(abs(fa), abs(fb), 1) < 0.10
    except ValueError:
        return False

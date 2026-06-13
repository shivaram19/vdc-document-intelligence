"""Confidence and severity scoring for candidate conflicts."""
from typing import Dict, List, Optional, Tuple

from analysis.models import Claim

from ._normalize import parse_numeric_value
from ._resolver import DEFAULT_SOURCE_PRIORITY


# Attribute criticality mapping (severity tier).
ATTRIBUTE_CRITICALITY: Dict[str, str] = {
    "fire rating": "critical",
    "structural load": "critical",
    "seal class": "high",
    "duct material": "high",
    "U-factor": "medium",
    "R-value": "medium",
    "ceiling height": "medium",
    "duct velocity": "medium",
    "pressure": "medium",
    "floor finish": "low",
}


def _relative_difference(values: List[str]) -> float:
    """Return a rough relative difference for a list of numeric strings."""
    parsed = [parse_numeric_value(v) for v in values]
    scalars = []
    for p in parsed:
        if p is None:
            continue
        if isinstance(p, tuple):
            scalars.append((p[0] + p[1]) / 2.0)
        else:
            scalars.append(p)
    if len(scalars) < 2:
        return 1.0
    max_val = max(abs(v) for v in scalars) or 1.0
    diffs = [abs(a - b) for a, b in zip(scalars, scalars[1:])]
    return sum(diffs) / (len(diffs) * max_val)


def _source_reliability(
    claims: List[Claim],
    priority: Dict[str, int],
) -> float:
    """Return average normalized reliability from source priorities."""
    max_priority = max(priority.values()) if priority else 99
    if max_priority == 0:
        return 1.0
    scores = []
    for claim in claims:
        src = claim.metadata.get("source_type", "")
        p = priority.get(src, max_priority)
        scores.append(1.0 - (p / max_priority))
    return sum(scores) / len(scores) if scores else 0.5


def score_conflict(
    candidate,
    claims: List[Claim],
    priority: Optional[Dict[str, int]] = None,
) -> Tuple[float, str]:
    """Return (confidence, severity) for a candidate conflict.

    Confidence is clamped to [0, 1] and combines extractor confidence,
    value separation, and source reliability. Severity is derived from
    attribute criticality.
    """
    priority = priority if priority is not None else DEFAULT_SOURCE_PRIORITY
    by_id = {c.id: c for c in claims}
    involved = [by_id[cid] for cid in candidate.claim_ids if cid in by_id]

    base_confidence = (
        sum(c.confidence for c in involved) / len(involved) if involved else 0.0
    )

    if candidate.contradiction_type == "numeric_mismatch":
        values = candidate.metadata.get("values", [])
        rel_diff = _relative_difference(values)
        value_factor = min(1.0, max(0.0, rel_diff * 2.0))
    else:
        value_factor = 1.0

    reliability = _source_reliability(involved, priority)

    confidence = base_confidence * value_factor * reliability
    confidence = min(1.0, max(0.0, confidence))

    attribute = _primary_attribute(involved, candidate)
    severity = ATTRIBUTE_CRITICALITY.get(attribute, "medium")
    return confidence, severity


def _primary_attribute(
    involved: List[Claim],
    candidate,
) -> str:
    """Pick the attribute that best represents the conflict severity."""
    if involved:
        return involved[0].attribute
    return candidate.metadata.get("attribute", "")

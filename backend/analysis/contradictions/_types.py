"""Internal types for the contradiction detection engine."""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from analysis.models import Claim


@dataclass
class CandidateConflict:
    """A raw conflict detected by a comparator before resolution/scoring."""

    contradiction_type: str
    claim_ids: List[str]
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

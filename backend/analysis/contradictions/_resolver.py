"""Document-priority resolution for candidate conflicts."""
from typing import Dict, List, Tuple

from analysis.models import Claim

from ._types import CandidateConflict


# Lower number = higher authority.
DEFAULT_SOURCE_PRIORITY = {
    "contract": 0,
    "addendum": 1,
    "spec": 2,
    "drawing": 3,
    "rfi": 4,
    "submittal": 5,
}


class DocumentHierarchyResolver:
    """Suppress conflicts when a higher-priority source resolves them."""

    def __init__(
        self,
        priority: Dict[str, int] = None,
    ):
        self.priority = priority if priority is not None else DEFAULT_SOURCE_PRIORITY

    def resolve(
        self,
        candidates: List[CandidateConflict],
        claims: List[Claim],
    ) -> Tuple[List[CandidateConflict], List[CandidateConflict]]:
        """Return (kept, dropped) candidate conflicts."""
        by_id = {c.id: c for c in claims}
        kept: List[CandidateConflict] = []
        dropped: List[CandidateConflict] = []

        for candidate in candidates:
            involved = [by_id[cid] for cid in candidate.claim_ids if cid in by_id]
            priorities = {
                self.priority.get(c.metadata.get("source_type", ""), 99)
                for c in involved
            }
            if len(priorities) <= 1:
                kept.append(candidate)
                continue

            winner = min(priorities)
            if sum(1 for p in priorities if p == winner) == 1:
                candidate.metadata["resolution_reason"] = (
                    "higher_priority_source_wins"
                )
                dropped.append(candidate)
            else:
                kept.append(candidate)

        return kept, dropped

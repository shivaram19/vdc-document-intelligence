"""Group claims for comparator dispatch."""
from collections import defaultdict
from typing import Dict, List, Tuple

from analysis.models import Claim

from ._constants import EXPECTED_ATTRIBUTES


def group_by_entity_attribute(claims: List[Claim]) -> Dict[Tuple[str, str], List[Claim]]:
    """Group claims by the (entity, attribute) pair they describe."""
    groups: Dict[Tuple[str, str], List[Claim]] = defaultdict(list)
    for claim in claims:
        groups[(claim.entity, claim.attribute)].append(claim)
    return dict(groups)


def group_by_entity(claims: List[Claim]) -> Dict[str, List[Claim]]:
    """Group claims by entity, keeping only entities with expected attributes."""
    groups: Dict[str, List[Claim]] = defaultdict(list)
    for claim in claims:
        if claim.entity in EXPECTED_ATTRIBUTES:
            groups[claim.entity].append(claim)
    return dict(groups)

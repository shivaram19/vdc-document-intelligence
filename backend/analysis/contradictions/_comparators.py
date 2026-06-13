"""Deterministic claim comparators for contradiction detection."""
from itertools import combinations
from typing import Dict, List, Optional, Set

from analysis.models import Claim

from ._constants import (
    EXPECTED_ATTRIBUTES,
    MATERIAL_ATTRIBUTES,
    NUMERIC_ATTRIBUTES,
    NUMERIC_TOLERANCE,
)
from ._normalize import (
    NumericValue,
    canonicalize_material,
    parse_numeric_value,
    parse_standard,
    to_base_value,
    values_conflict,
)
from ._types import CandidateConflict


class ClaimComparator:
    """Base class for deterministic claim comparators."""

    def compare(self, claims: List[Claim]) -> List[CandidateConflict]:
        raise NotImplementedError


class NumericComparator(ClaimComparator):
    """Detect numeric mismatches for the same entity/attribute."""

    def compare(self, claims: List[Claim]) -> List[CandidateConflict]:
        candidates: List[CandidateConflict] = []
        parsed: List[tuple] = []
        for claim in claims:
            value = parse_numeric_value(claim.value)
            if value is None:
                continue
            base = to_base_value(value, claim.unit)
            if base is None:
                continue
            parsed.append((claim, base[0], base[1]))

        for (c1, v1, u1), (c2, v2, u2) in combinations(parsed, 2):
            if u1 != u2:
                continue
            tol = NUMERIC_TOLERANCE.get(c1.attribute, (0.0, 0.05))
            if values_conflict(v1, v2, *tol):
                candidates.append(
                    CandidateConflict(
                        contradiction_type="numeric_mismatch",
                        claim_ids=[c1.id, c2.id],
                        description=(
                            f"{c1.attribute} conflict: {c1.value} {c1.unit} "
                            f"vs {c2.value} {c2.unit}"
                        ),
                        metadata={
                            "values": [c1.value, c2.value],
                            "units": [c1.unit, c2.unit],
                            "base_units": [u1, u2],
                        },
                    )
                )
        return candidates


class MaterialComparator(ClaimComparator):
    """Detect material/type conflicts for the same entity/attribute."""

    def compare(self, claims: List[Claim]) -> List[CandidateConflict]:
        candidates: List[CandidateConflict] = []
        normalized: List[tuple] = []
        for claim in claims:
            normalized.append((claim, canonicalize_material(claim.value)))

        for (c1, n1), (c2, n2) in combinations(normalized, 2):
            if n1 != n2:
                candidates.append(
                    CandidateConflict(
                        contradiction_type="material_conflict",
                        claim_ids=[c1.id, c2.id],
                        description=(
                            f"{c1.attribute} conflict: {c1.value} vs {c2.value}"
                        ),
                        metadata={"values": [c1.value, c2.value]},
                    )
                )
        return candidates


class StandardComparator(ClaimComparator):
    """Detect standard/version conflicts for the same entity."""

    def compare(self, claims: List[Claim]) -> List[CandidateConflict]:
        candidates: List[CandidateConflict] = []
        parsed: List[tuple] = []
        for claim in claims:
            org, year = parse_standard(claim.value)
            if org:
                parsed.append((claim, org, year))

        for (c1, org1, year1), (c2, org2, year2) in combinations(parsed, 2):
            if org1 == org2 and year1 and year2 and year1 != year2:
                candidates.append(
                    CandidateConflict(
                        contradiction_type="standard_version",
                        claim_ids=[c1.id, c2.id],
                        description=(
                            f"Standard version conflict: {c1.value} vs {c2.value}"
                        ),
                        metadata={"values": [c1.value, c2.value]},
                    )
                )
        return candidates


class MissingAttributeComparator(ClaimComparator):
    """Detect missing expected attributes for an entity across documents."""

    def compare(self, claims: List[Claim]) -> List[CandidateConflict]:
        candidates: List[CandidateConflict] = []
        by_entity: Dict[str, List[Claim]] = {}
        for claim in claims:
            by_entity.setdefault(claim.entity, []).append(claim)

        for entity, entity_claims in by_entity.items():
            expected = EXPECTED_ATTRIBUTES.get(entity)
            if not expected:
                continue
            docs_with_entity: Set[str] = {c.document_id for c in entity_claims}
            for attr in expected:
                docs_with_attr: Dict[str, Claim] = {
                    c.document_id: c
                    for c in entity_claims
                    if c.attribute == attr
                }
                if not docs_with_attr:
                    continue
                missing_docs = docs_with_entity - set(docs_with_attr.keys())
                if not missing_docs:
                    continue
                present_claim = next(iter(docs_with_attr.values()))
                for doc_id in missing_docs:
                    candidates.append(
                        CandidateConflict(
                            contradiction_type="missing_attribute",
                            claim_ids=[present_claim.id],
                            description=(
                                f"{entity} is missing expected attribute "
                                f"{attr} in document {doc_id}"
                            ),
                            metadata={
                                "entity": entity,
                                "attribute": attr,
                                "missing_document_id": doc_id,
                                "present_claim_id": present_claim.id,
                            },
                        )
                    )
        return candidates


def get_comparator(attribute: str) -> Optional[ClaimComparator]:
    """Return the comparator appropriate for an attribute, if any."""
    if attribute in NUMERIC_ATTRIBUTES:
        return NumericComparator()
    if attribute in MATERIAL_ATTRIBUTES:
        return MaterialComparator()
    if attribute == "applicable standard":
        return StandardComparator()
    return None

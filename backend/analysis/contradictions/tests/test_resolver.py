"""Tests for document-hierarchy conflict resolution."""
from analysis.contradictions._resolver import DocumentHierarchyResolver
from analysis.models import Claim


def _claim(
    source_type: str,
    document_id: str,
    entity: str = "exterior wall",
    attribute: str = "R-value",
    value: str = "R-21",
) -> Claim:
    return Claim(
        entity=entity,
        attribute=attribute,
        value=value,
        document_id=document_id,
        chunk_id="c1",
        project_id="p1",
        metadata={"source_type": source_type},
    )


def _candidate(claims):
    from analysis.contradictions._types import CandidateConflict

    return CandidateConflict(
        contradiction_type="numeric_mismatch",
        claim_ids=[c.id for c in claims],
        description="test conflict",
    )


class TestDocumentHierarchyResolver:
    def test_equal_priority_kept(self):
        c1 = _claim("spec", "d1", value="R-21")
        c2 = _claim("spec", "d2", value="R-19")
        candidate = _candidate([c1, c2])
        resolver = DocumentHierarchyResolver()
        kept, dropped = resolver.resolve([candidate], [c1, c2])
        assert len(kept) == 1
        assert len(dropped) == 0

    def test_higher_priority_suppresses_conflict(self):
        c1 = _claim("contract", "d1", value="R-21")
        c2 = _claim("spec", "d2", value="R-19")
        candidate = _candidate([c1, c2])
        resolver = DocumentHierarchyResolver()
        kept, dropped = resolver.resolve([candidate], [c1, c2])
        assert len(kept) == 0
        assert len(dropped) == 1
        assert dropped[0].metadata.get("resolution_reason")

    def test_unknown_source_treated_as_low_priority(self):
        c1 = _claim("contract", "d1", value="R-21")
        c2 = _claim("unknown", "d2", value="R-19")
        candidate = _candidate([c1, c2])
        resolver = DocumentHierarchyResolver()
        kept, dropped = resolver.resolve([candidate], [c1, c2])
        assert len(kept) == 0
        assert len(dropped) == 1

    def test_missing_claim_reference_kept(self):
        c1 = _claim("spec", "d1")
        candidate = _candidate([c1])
        # Reference a non-existent claim id to simulate lookup failure.
        candidate.claim_ids.append("missing")
        resolver = DocumentHierarchyResolver()
        kept, dropped = resolver.resolve([candidate], [c1])
        assert len(kept) == 1
        assert len(dropped) == 0

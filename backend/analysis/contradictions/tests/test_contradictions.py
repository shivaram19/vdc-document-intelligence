"""Integration tests for the full contradiction-detection pipeline."""
from analysis import ContradictionDetector
from analysis.extractors import ClaimExtractor
from chunking.models import Chunk


def _chunk(text: str, document_id: str, source_type: str = "spec") -> Chunk:
    return Chunk(
        id=f"c-{document_id}",
        document_id=document_id,
        project_id="p1",
        text=text,
        discipline="specification",
        source_type=source_type,
    )


class TestContradictionDetectionIntegration:
    def test_extracted_conflict_detected(self):
        chunk1 = _chunk(
            "The mechanical room ceiling shall be 12 feet clear height.",
            "d-spec-a",
            "spec",
        )
        chunk2 = _chunk(
            "Mechanical room ceiling height is 10 ft.",
            "d-spec-b",
            "spec",
        )
        extractor = ClaimExtractor()
        claims = extractor.extract(chunk1).claims + extractor.extract(chunk2).claims
        result = ContradictionDetector().detect(claims)
        assert any(
            c.contradiction_type == "numeric_mismatch" for c in result.contradictions
        )

    def test_no_conflict_when_values_match(self):
        chunk1 = _chunk(
            "Office ceiling height is 10 ft.",
            "d-spec",
            "spec",
        )
        chunk2 = _chunk(
            "Office ceiling height is 10 ft.",
            "d-drawing",
            "drawing",
        )
        extractor = ClaimExtractor()
        claims = extractor.extract(chunk1).claims + extractor.extract(chunk2).claims
        result = ContradictionDetector().detect(claims)
        assert not any(
            c.contradiction_type == "numeric_mismatch" for c in result.contradictions
        )

    def test_hierarchy_suppresses_lower_priority_conflict(self):
        chunk1 = _chunk(
            "Office ceiling height is 10 ft.",
            "d-contract",
            "contract",
        )
        chunk2 = _chunk(
            "Office ceiling height is 12 ft.",
            "d-spec",
            "spec",
        )
        extractor = ClaimExtractor()
        claims = extractor.extract(chunk1).claims + extractor.extract(chunk2).claims
        result = ContradictionDetector().detect(claims)
        assert not result.contradictions
        assert len(result.dropped) == 1

"""End-to-end tests for the ContradictionDetector orchestrator."""
import pytest

from analysis.contradictions import ContradictionDetector, DetectionResult
from analysis.contradictions._types import CandidateConflict
from analysis.models import Claim, Contradiction
from analysis.sensors import SensorCheckError


def _claim(
    entity: str,
    attribute: str,
    value: str,
    unit: str = "",
    document_id: str = "d1",
    source_type: str = "spec",
    confidence: float = 0.9,
) -> Claim:
    return Claim(
        entity=entity,
        attribute=attribute,
        value=value,
        unit=unit,
        document_id=document_id,
        chunk_id="c1",
        project_id="p1",
        confidence=confidence,
        metadata={"source_type": source_type},
    )


class TestContradictionDetector:
    def test_empty_claims(self):
        detector = ContradictionDetector()
        result = detector.detect([])
        assert result.contradictions == []
        assert result.reports == []

    def test_detects_numeric_mismatch(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "12", "ft", "d2"),
        ]
        result = ContradictionDetector().detect(claims)
        assert len(result.contradictions) == 1
        c = result.contradictions[0]
        assert c.contradiction_type == "numeric_mismatch"
        assert c.status == "open"
        assert 0.0 <= c.confidence <= 1.0

    def test_no_conflict_for_matching_values(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "10", "ft", "d2"),
        ]
        result = ContradictionDetector().detect(claims)
        assert result.contradictions == []

    def test_document_hierarchy_suppresses_conflict(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1", "contract"),
            _claim("office ceiling", "ceiling height", "12", "ft", "d2", "spec"),
        ]
        result = ContradictionDetector().detect(claims)
        assert len(result.dropped) == 1
        assert result.contradictions == []

    def test_detects_missing_attribute(self):
        claims = [
            _claim("exterior wall", "R-value", "R-21", "", "d1"),
            _claim("exterior wall", "fire rating", "2-hour", "", "d2"),
        ]
        result = ContradictionDetector().detect(claims)
        assert any(c.contradiction_type == "missing_attribute" for c in result.contradictions)

    def test_sensor_rejects_invalid_candidate(self):
        detector = ContradictionDetector()
        bad = CandidateConflict(
            contradiction_type="numeric_mismatch",
            claim_ids=[],
            description="bad",
        )
        # Direct sensor usage; detector path will not produce empty claim ids.
        accepted, report = detector.sensor.check_candidates([bad])
        assert not accepted
        assert report.rejected == 1

    def test_detection_result_returns_reports(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "12", "ft", "d2"),
        ]
        result = ContradictionDetector().detect(claims)
        assert len(result.reports) >= 1

    def test_contradiction_has_project_id(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "12", "ft", "d2"),
        ]
        result = ContradictionDetector().detect(claims)
        assert result.contradictions[0].project_id == "p1"

"""Tests for conflict confidence and severity scoring."""
from analysis.contradictions._scoring import score_conflict
from analysis.models import Claim


def _claim(
    attribute: str,
    value: str,
    confidence: float = 0.9,
    source_type: str = "spec",
    document_id: str = "d1",
) -> Claim:
    return Claim(
        entity="exterior wall",
        attribute=attribute,
        value=value,
        confidence=confidence,
        document_id=document_id,
        chunk_id="c1",
        project_id="p1",
        metadata={"source_type": source_type},
    )


def _candidate(contradiction_type, claim_ids, values=None, attribute=""):
    from analysis.contradictions._types import CandidateConflict

    metadata = {}
    if values:
        metadata["values"] = values
    if attribute:
        metadata["attribute"] = attribute
    return CandidateConflict(
        contradiction_type=contradiction_type,
        claim_ids=claim_ids,
        description="test",
        metadata=metadata,
    )


class TestScoreConflict:
    def test_confidence_in_range(self):
        c1 = _claim("R-value", "R-21")
        c2 = _claim("R-value", "R-19")
        candidate = _candidate("numeric_mismatch", [c1.id, c2.id], values=["21", "19"])
        confidence, _ = score_conflict(candidate, [c1, c2])
        assert 0.0 <= confidence <= 1.0

    def test_low_extractor_confidence_reduces_score(self):
        c1 = _claim("R-value", "R-21", confidence=0.3)
        c2 = _claim("R-value", "R-19", confidence=0.3)
        candidate = _candidate("numeric_mismatch", [c1.id, c2.id], values=["21", "19"])
        low_conf, _ = score_conflict(candidate, [c1, c2])
        c3 = _claim("R-value", "R-21", confidence=0.9)
        c4 = _claim("R-value", "R-19", confidence=0.9)
        candidate2 = _candidate("numeric_mismatch", [c3.id, c4.id], values=["21", "19"])
        high_conf, _ = score_conflict(candidate2, [c3, c4])
        assert low_conf < high_conf

    def test_severity_maps_attribute_criticality(self):
        c1 = _claim("fire rating", "2-hour")
        c2 = _claim("fire rating", "1-hour")
        candidate = _candidate("material_conflict", [c1.id, c2.id])
        _, severity = score_conflict(candidate, [c1, c2])
        assert severity == "critical"

    def test_non_numeric_value_factor_is_one(self):
        c1 = _claim("duct material", "galvanized steel")
        c2 = _claim("duct material", "aluminum")
        candidate = _candidate("material_conflict", [c1.id, c2.id])
        confidence, severity = score_conflict(candidate, [c1, c2])
        assert 0.0 <= confidence <= 1.0
        assert severity == "high"

    def test_missing_attribute_severity(self):
        c1 = _claim("R-value", "R-21")
        candidate = _candidate("missing_attribute", [c1.id], attribute="R-value")
        _, severity = score_conflict(candidate, [c1])
        assert severity == "medium"

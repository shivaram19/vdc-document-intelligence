"""Tests for ContradictionDetector with MeMo inferential sensor enabled."""
from analysis.contradictions import ContradictionDetector
from analysis.contradictions._inferential import MeMoInferentialSensor
from analysis.contradictions._memo_client import FakeMemoryModelClient
from analysis.models import Claim


def _claim(
    entity: str,
    attribute: str,
    value: str,
    source_text: str,
    document_id: str = "d1",
) -> Claim:
    return Claim(
        entity=entity,
        attribute=attribute,
        value=value,
        document_id=document_id,
        chunk_id="c1",
        project_id="p1",
        metadata={"source_text": source_text},
    )


def _json_response(conflict: bool) -> str:
    import json

    return json.dumps(
        {
            "contradiction": conflict,
            "confidence": 0.85 if conflict else 0.1,
            "type": "inferential_conflict",
            "explanation": "cross-entity review",
        }
    )


class TestDetectorWithInferential:
    def test_inferential_off_by_default(self):
        a = _claim("lobby flooring", "floor finish", "polished concrete", "...")
        b = _claim("finish schedule", "floor finish", "terrazzo", "...")
        detector = ContradictionDetector()
        result = detector.detect([a, b])
        assert not result.contradictions

    def test_inferential_detects_cross_entity_conflict(self):
        a = _claim("lobby flooring", "floor finish", "polished concrete", "...")
        b = _claim("finish schedule", "floor finish", "terrazzo", "...")
        client = FakeMemoryModelClient(responses=[_json_response(True)])
        sensor = MeMoInferentialSensor(client=client, mode="single")
        detector = ContradictionDetector(use_inferential=True, inferential_sensor=sensor)
        result = detector.detect([a, b])
        assert len(result.contradictions) == 1
        assert result.contradictions[0].contradiction_type == "inferential_conflict"
        assert result.contradictions[0].status == "open"

    def test_inferential_false_keeps_deterministic_results(self):
        a = _claim("office ceiling", "ceiling height", "10", "...", document_id="d1")
        b = _claim("office ceiling", "ceiling height", "12", "...", document_id="d2")
        a.unit = "ft"
        b.unit = "ft"
        client = FakeMemoryModelClient(responses=[_json_response(False)])
        sensor = MeMoInferentialSensor(client=client, mode="single")
        detector = ContradictionDetector(use_inferential=True, inferential_sensor=sensor)
        result = detector.detect([a, b])
        # Deterministic numeric mismatch should still be present.
        assert any(c.contradiction_type == "numeric_mismatch" for c in result.contradictions)

"""Tests for the MeMo-style inferential sensor."""
import pytest

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


def _conflict_json(conflict: bool, explanation: str = "") -> str:
    import json

    return json.dumps(
        {
            "contradiction": conflict,
            "confidence": 0.85 if conflict else 0.1,
            "type": "material_conflict",
            "explanation": explanation,
        }
    )


class TestMeMoInferentialSensor:
    def test_detects_cross_entity_conflict(self):
        a = _claim(
            "lobby flooring",
            "floor finish",
            "polished concrete",
            "Lobby flooring: polished concrete",
            "d-drawing",
        )
        b = _claim(
            "finish schedule",
            "floor finish",
            "terrazzo",
            "Interior finish schedule: terrazzo",
            "d-spec",
        )
        client = FakeMemoryModelClient(
            responses=[_conflict_json(True, "polished concrete vs terrazzo")]
        )
        sensor = MeMoInferentialSensor(client=client, mode="single")
        candidates = sensor.review([a, b], [])
        assert len(candidates) == 1
        assert candidates[0].contradiction_type == "material_conflict"
        assert a.id in candidates[0].claim_ids
        assert b.id in candidates[0].claim_ids

    def test_ignores_same_entity_pair(self):
        a = _claim("office ceiling", "ceiling height", "10", "Ceiling is 10 ft")
        b = _claim("office ceiling", "ceiling height", "12", "Ceiling is 12 ft")
        sensor = MeMoInferentialSensor(mode="single")
        candidates = sensor.review([a, b], [])
        assert candidates == []

    def test_skips_already_flagged_pairs(self):
        a = _claim("lobby flooring", "floor finish", "polished concrete", "...")
        b = _claim("finish schedule", "floor finish", "terrazzo", "...")
        deterministic = [
            type("C", (), {"claim_ids": [a.id, b.id]})()
        ]
        sensor = MeMoInferentialSensor(mode="single")
        candidates = sensor.review([a, b], deterministic)
        assert candidates == []

    def test_rejects_non_whitelisted_attribute(self):
        a = _claim("beam", "material", "steel", "Beam material: steel")
        b = _claim("column", "material", "concrete", "Column material: concrete")
        sensor = MeMoInferentialSensor(mode="single")
        candidates = sensor.review([a, b], [])
        assert candidates == []

    def test_malformed_response_is_rejected(self):
        a = _claim("lobby flooring", "floor finish", "polished concrete", "...")
        b = _claim("finish schedule", "floor finish", "terrazzo", "...")
        client = FakeMemoryModelClient(responses=["not valid json"])
        sensor = MeMoInferentialSensor(client=client, mode="single")
        candidates = sensor.review([a, b], [])
        assert candidates == []

    def test_multi_turn_mode_makes_three_calls(self):
        a = _claim("lobby flooring", "floor finish", "polished concrete", "...")
        b = _claim("finish schedule", "floor finish", "terrazzo", "...")
        client = FakeMemoryModelClient(
            responses=["entity A", "entity B", _conflict_json(True)]
        )
        sensor = MeMoInferentialSensor(client=client, mode="multi_turn")
        candidates = sensor.review([a, b], [])
        assert len(candidates) == 1
        assert len(client.calls) == 3

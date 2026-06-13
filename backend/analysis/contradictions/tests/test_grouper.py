"""Tests for claim grouping helpers."""
from analysis.contradictions._grouper import (
    group_by_entity,
    group_by_entity_attribute,
)
from analysis.models import Claim


def _claim(entity: str, attribute: str, document_id: str = "d1") -> Claim:
    return Claim(
        entity=entity,
        attribute=attribute,
        value="10",
        document_id=document_id,
        chunk_id="c1",
        project_id="p1",
    )


class TestGroupByEntityAttribute:
    def test_groups_by_entity_attribute(self):
        claims = [
            _claim("wall", "R-value", "d1"),
            _claim("wall", "R-value", "d2"),
            _claim("window", "U-factor", "d1"),
        ]
        groups = group_by_entity_attribute(claims)
        assert len(groups[("wall", "R-value")]) == 2
        assert len(groups[("window", "U-factor")]) == 1

    def test_empty_input(self):
        assert group_by_entity_attribute([]) == {}

    def test_claim_not_in_multiple_groups(self):
        claim = _claim("wall", "R-value", "d1")
        groups = group_by_entity_attribute([claim])
        occurrences = sum(claim.id in [c.id for c in g] for g in groups.values())
        assert occurrences == 1


class TestGroupByEntity:
    def test_keeps_expected_entities(self):
        claims = [
            _claim("exterior wall", "R-value", "d1"),
            _claim("window", "U-factor", "d1"),
            _claim("door", "finish", "d1"),
        ]
        groups = group_by_entity(claims)
        assert "exterior wall" in groups
        assert "window" in groups
        assert "door" not in groups

    def test_empty_input(self):
        assert group_by_entity([]) == {}

"""Tests for deterministic claim comparators."""
import pytest

from analysis.contradictions._comparators import (
    MaterialComparator,
    MissingAttributeComparator,
    NumericComparator,
    StandardComparator,
    get_comparator,
)
from analysis.models import Claim


def _claim(
    entity: str,
    attribute: str,
    value: str,
    unit: str = "",
    document_id: str = "d1",
    chunk_id: str = "c1",
) -> Claim:
    return Claim(
        entity=entity,
        attribute=attribute,
        value=value,
        unit=unit,
        document_id=document_id,
        chunk_id=chunk_id,
        project_id="p1",
    )


class TestNumericComparator:
    def test_identical_values_no_conflict(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "10", "ft", "d2"),
        ]
        assert NumericComparator().compare(claims) == []

    def test_conflict_when_values_differ(self):
        claims = [
            _claim("office ceiling", "ceiling height", "10", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "12", "ft", "d2"),
        ]
        conflicts = NumericComparator().compare(claims)
        assert len(conflicts) == 1
        assert conflicts[0].contradiction_type == "numeric_mismatch"

    def test_unit_conversion_avoids_false_conflict(self):
        claims = [
            _claim("office ceiling", "ceiling height", "12", "ft", "d1"),
            _claim("office ceiling", "ceiling height", "144", "in", "d2"),
        ]
        assert NumericComparator().compare(claims) == []

    def test_different_units_skip_comparison(self):
        claims = [
            _claim("pressure", "pressure", "50", "psi", "d1"),
            _claim("pressure", "pressure", "50", "fpm", "d2"),
        ]
        assert NumericComparator().compare(claims) == []

    def test_range_overlap_no_conflict(self):
        claims = [
            _claim("spacing", "spacing", "18-24", "in", "d1"),
            _claim("spacing", "spacing", "20", "in", "d2"),
        ]
        assert NumericComparator().compare(claims) == []


class TestMaterialComparator:
    def test_same_material_no_conflict(self):
        claims = [
            _claim("ductwork", "duct material", "galvanized steel", "", "d1"),
            _claim("ductwork", "duct material", "galvanized steel", "", "d2"),
        ]
        assert MaterialComparator().compare(claims) == []

    def test_synonym_no_conflict(self):
        claims = [
            _claim("ductwork", "duct material", "aluminum", "", "d1"),
            _claim("ductwork", "duct material", "aluminium", "", "d2"),
        ]
        assert MaterialComparator().compare(claims) == []

    def test_different_material_conflict(self):
        claims = [
            _claim("ductwork", "duct material", "galvanized steel", "", "d1"),
            _claim("ductwork", "duct material", "aluminum", "", "d2"),
        ]
        conflicts = MaterialComparator().compare(claims)
        assert len(conflicts) == 1
        assert conflicts[0].contradiction_type == "material_conflict"


class TestStandardComparator:
    def test_same_version_no_conflict(self):
        claims = [
            _claim("fire protection", "applicable standard", "NFPA 13", "", "d1"),
            _claim("fire protection", "applicable standard", "NFPA 13", "", "d2"),
        ]
        assert StandardComparator().compare(claims) == []

    def test_different_year_conflict(self):
        claims = [
            _claim("fire protection", "applicable standard", "NFPA 13-2019", "", "d1"),
            _claim("fire protection", "applicable standard", "NFPA 13-2022", "", "d2"),
        ]
        conflicts = StandardComparator().compare(claims)
        assert len(conflicts) == 1
        assert conflicts[0].contradiction_type == "standard_version"

    def test_different_org_no_conflict(self):
        claims = [
            _claim("fire protection", "applicable standard", "NFPA 13", "", "d1"),
            _claim("structural", "applicable standard", "ACI 318", "", "d2"),
        ]
        assert StandardComparator().compare(claims) == []


class TestMissingAttributeComparator:
    def test_no_missing_attribute(self):
        claims = [
            _claim("exterior wall", "R-value", "R-21", "", "d1"),
            _claim("exterior wall", "R-value", "R-19", "", "d2"),
        ]
        assert MissingAttributeComparator().compare(claims) == []

    def test_missing_attribute_reported(self):
        claims = [
            _claim("exterior wall", "R-value", "R-21", "", "d1"),
            _claim("exterior wall", "fire rating", "2-hour", "", "d2"),
        ]
        # exterior wall has R-value in d1 only; no expected attr missing? Actually
        # EXPECTED_ATTRIBUTES for exterior wall is ["R-value"]; d2 is missing R-value.
        conflicts = MissingAttributeComparator().compare(claims)
        assert any(c.contradiction_type == "missing_attribute" for c in conflicts)

    def test_untracked_entity_ignored(self):
        claims = [
            _claim("interior door", "finish", "paint", "", "d1"),
        ]
        assert MissingAttributeComparator().compare(claims) == []


class TestGetComparator:
    def test_numeric_attribute(self):
        assert isinstance(get_comparator("R-value"), NumericComparator)

    def test_material_attribute(self):
        assert isinstance(get_comparator("duct material"), MaterialComparator)

    def test_standard_attribute(self):
        assert isinstance(get_comparator("applicable standard"), StandardComparator)

    def test_unknown_attribute_returns_none(self):
        assert get_comparator("finish") is None

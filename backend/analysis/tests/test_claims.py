"""Tests for deterministic claim extraction with sensor checkpoints."""
import pytest

from analysis.extractors import ClaimExtractor
from analysis.sensors import ClaimExtractionSensor, SensorCheckError
from chunking.models import Chunk


def _chunk(text: str, chunk_id: str = "c1") -> Chunk:
    return Chunk(
        id=chunk_id,
        document_id="d1",
        project_id="p1",
        text=text,
        discipline="specification",
        source_type="spec",
    )


class TestNumericExtraction:
    def test_ceiling_height_feet(self):
        result = ClaimExtractor().extract(
            _chunk("The mechanical room ceiling shall be 12 feet clear height.")
        )
        claims = [c for c in result.claims if c.attribute == "ceiling height"]
        assert len(claims) == 1
        assert claims[0].value == "12"
        assert claims[0].unit == "ft"
        assert claims[0].entity == "mechanical room ceiling"
        assert claims[0].confidence >= 0.8

    def test_ceiling_height_ft(self):
        result = ClaimExtractor().extract(
            _chunk("Office ceiling height is 10 ft.")
        )
        claims = [c for c in result.claims if c.attribute == "ceiling height"]
        assert len(claims) == 1
        assert claims[0].value == "10"
        assert claims[0].unit == "ft"

    def test_u_factor(self):
        result = ClaimExtractor().extract(
            _chunk("Windows shall have a maximum U-factor 0.30.")
        )
        claims = [c for c in result.claims if c.attribute == "U-factor"]
        assert len(claims) == 1
        assert claims[0].value == "0.30"
        assert claims[0].entity == "window"

    def test_r_value(self):
        result = ClaimExtractor().extract(
            _chunk("Exterior walls shall have R-21 continuous insulation.")
        )
        claims = [c for c in result.claims if c.attribute == "R-value"]
        assert len(claims) == 1
        assert claims[0].value == "21"
        assert claims[0].entity == "exterior wall"

    def test_duct_velocity_unit_normalization(self):
        result = ClaimExtractor().extract(
            _chunk("Duct velocity shall not exceed 1,800 FPM.")
        )
        claims = [c for c in result.claims if c.attribute == "duct velocity"]
        assert len(claims) == 1
        assert claims[0].value == "1800"
        assert claims[0].unit == "fpm"


class TestMaterialExtraction:
    def test_galvanized_steel(self):
        result = ClaimExtractor().extract(
            _chunk("Ductwork shall be constructed of galvanized steel.")
        )
        claims = [c for c in result.claims if c.attribute == "duct material"]
        assert len(claims) == 1
        assert claims[0].value == "galvanized steel"
        assert claims[0].entity == "ductwork"

    def test_fire_rating(self):
        result = ClaimExtractor().extract(
            _chunk("Corridors shall be 2-hour rated.")
        )
        claims = [c for c in result.claims if c.attribute == "fire rating"]
        assert len(claims) == 1
        assert claims[0].value == "2-hour"
        assert claims[0].entity == "corridor"

    def test_floor_finish(self):
        result = ClaimExtractor().extract(
            _chunk("Office flooring shall be carpet tile.")
        )
        claims = [c for c in result.claims if c.attribute == "floor finish"]
        assert len(claims) == 1
        assert claims[0].value == "carpet tile"
        assert claims[0].entity == "office flooring"


class TestStandardExtraction:
    def test_nfpa_citation(self):
        result = ClaimExtractor().extract(
            _chunk("Comply with NFPA 13 for fire protection design.")
        )
        standards = [c for c in result.claims if c.attribute == "applicable standard"]
        assert any("NFPA" in c.value for c in standards)


class TestClaimMetadata:
    def test_source_type_in_metadata(self):
        result = ClaimExtractor().extract(
            _chunk("Ceiling height is 10 ft.", chunk_id="c-spec")
        )
        height_claims = [c for c in result.claims if c.attribute == "ceiling height"]
        assert len(height_claims) == 1
        assert height_claims[0].metadata.get("source_type") == "spec"


class TestSensorCheckpoints:
    def test_all_reports_pass_for_clean_input(self):
        result = ClaimExtractor().extract(
            _chunk("The ceiling height is 12 ft and the wall R-value is R-21.")
        )
        assert result.claims
        assert all(r.status.value != "fail" for r in result.reports)

    def test_sensor_rejects_implausible_value(self):
        sensor = ClaimExtractionSensor(drift_threshold=1.0)
        result = ClaimExtractor(sensor=sensor).extract(
            _chunk("The ceiling height is 9999 ft.")
        )
        assert not any(c.attribute == "ceiling height" for c in result.claims)
        verify_reports = [r for r in result.reports if r.phase == "verify"]
        assert any(r.rejected >= 1 for r in verify_reports)

    def test_sensor_raises_on_excessive_drift(self):
        sensor = ClaimExtractionSensor(drift_threshold=0.0)
        extractor = ClaimExtractor(sensor=sensor, raise_on_drift=True)
        with pytest.raises(SensorCheckError):
            extractor.extract(_chunk("The ceiling height is 9999 ft."))

    def test_sensor_drops_duplicate_claims(self):
        text = "The ceiling is 10 ft. The ceiling is 10 ft."
        sensor = ClaimExtractionSensor(drift_threshold=1.0)
        result = ClaimExtractor(sensor=sensor).extract(_chunk(text))
        height_claims = [c for c in result.claims if c.attribute == "ceiling height"]
        assert len(height_claims) == 1

    def test_sensor_rejects_unknown_unit(self):
        sensor = ClaimExtractionSensor(drift_threshold=1.0)
        from analysis.extractors._types import Candidate

        widgets = Candidate(
            attribute="pressure",
            value="50",
            unit="widgets",
            entity_hint="pipe",
            raw_value="50 widgets",
            start=0,
            end=10,
            extractor="numeric",
        )
        accepted, report = sensor.check_candidates([widgets])
        assert not accepted
        assert report.rejected == 1

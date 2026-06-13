"""Tests for contradiction-detection sensors."""
import pytest

from analysis.contradictions._sensors import ContradictionDetectionSensor
from analysis.contradictions._types import CandidateConflict
from analysis.sensors import SensorCheckError


def _candidate(claim_ids=("c1", "c2"), ctype="numeric_mismatch"):
    return CandidateConflict(
        contradiction_type=ctype,
        claim_ids=list(claim_ids),
        description="test",
    )


class TestContradictionDetectionSensor:
    def test_valid_candidate_passes(self):
        sensor = ContradictionDetectionSensor()
        accepted, report = sensor.check_candidates([_candidate()])
        assert len(accepted) == 1
        assert report.status.value == "pass"

    def test_rejects_empty_claim_ids(self):
        sensor = ContradictionDetectionSensor()
        bad = _candidate(claim_ids=[])
        accepted, report = sensor.check_candidates([bad])
        assert not accepted
        assert report.rejected == 1

    def test_rejects_empty_description(self):
        sensor = ContradictionDetectionSensor()
        bad = CandidateConflict(
            contradiction_type="numeric_mismatch",
            claim_ids=["c1", "c2"],
            description="",
        )
        accepted, report = sensor.check_candidates([bad])
        assert not accepted
        assert report.rejected == 1

    def test_collapses_duplicate_candidates(self):
        sensor = ContradictionDetectionSensor()
        c1 = _candidate(claim_ids=("c1", "c2"))
        c2 = _candidate(claim_ids=("c2", "c1"))
        accepted, report = sensor.check_candidates([c1, c2])
        assert len(accepted) == 1
        assert report.rejected == 1

    def test_drift_warn_when_results_change(self):
        sensor = ContradictionDetectionSensor(drift_threshold=1.0)
        report = sensor.check_drift(10, 8, phase="resolve")
        assert report.status.value == "warn"
        assert report.drift_ratio == 0.2

    def test_drift_raises_when_excessive(self):
        sensor = ContradictionDetectionSensor(drift_threshold=0.25)
        with pytest.raises(SensorCheckError):
            sensor.check_drift(10, 5, phase="resolve")

    def test_drift_pass_when_unchanged(self):
        sensor = ContradictionDetectionSensor()
        report = sensor.check_drift(10, 10, phase="group")
        assert report.status.value == "pass"

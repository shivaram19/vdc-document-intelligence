"""Tests for the public analysis API surface."""
from analysis import ContradictionDetector, DetectionResult


class TestPublicAPI:
    def test_import_contradiction_detector(self):
        assert ContradictionDetector is not None

    def test_import_detection_result(self):
        assert DetectionResult is not None

    def test_detector_instantiates(self):
        detector = ContradictionDetector()
        assert detector is not None

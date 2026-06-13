"""Sensor checkpoints for the contradiction detection pipeline."""
from typing import List, Tuple

from analysis.sensors import SensorCheckError, SensorReport, SensorStatus

from ._types import CandidateConflict


class ContradictionDetectionSensor:
    """Validate candidate conflicts and detect drift before scoring/output."""

    def __init__(self, drift_threshold: float = 0.25):
        self.drift_threshold = drift_threshold

    def _report(
        self,
        phase: str,
        checked: int,
        accepted: int,
        rejected: int,
        details: List[str],
    ) -> SensorReport:
        drift_ratio = rejected / checked if checked else 0.0
        if drift_ratio > self.drift_threshold:
            status = SensorStatus.FAIL
        elif rejected:
            status = SensorStatus.WARN
        else:
            status = SensorStatus.PASS
        return SensorReport(
            phase=phase,
            checked=checked,
            accepted=accepted,
            rejected=rejected,
            drift_ratio=drift_ratio,
            status=status,
            details=details,
        )

    def check_candidates(
        self,
        candidates: List[CandidateConflict],
    ) -> Tuple[List[CandidateConflict], SensorReport]:
        """Reject malformed candidates and collapse duplicates."""
        valid: List[CandidateConflict] = []
        details: List[str] = []
        seen: set = set()

        for candidate in candidates:
            if not candidate.claim_ids:
                details.append("Reject candidate with no claim ids")
                continue
            if not candidate.description:
                details.append("Reject candidate with empty description")
                continue

            key = (
                candidate.contradiction_type,
                tuple(sorted(set(candidate.claim_ids))),
            )
            if key in seen:
                details.append(f"Reject duplicate candidate {key}")
                continue
            seen.add(key)
            valid.append(candidate)

        return valid, self._report(
            "candidate",
            len(candidates),
            len(valid),
            len(candidates) - len(valid),
            details,
        )

    def check_drift(
        self,
        before: int,
        after: int,
        phase: str = "drift",
        raise_on_excess: bool = True,
    ) -> SensorReport:
        """Report when the pipeline drops or inflates results unexpectedly."""
        denominator = max(before, 1)
        drift_ratio = abs(before - after) / denominator
        if drift_ratio > self.drift_threshold:
            status = SensorStatus.FAIL
        elif before != after:
            status = SensorStatus.WARN
        else:
            status = SensorStatus.PASS
        report = SensorReport(
            phase=phase,
            checked=before,
            accepted=after,
            rejected=before - after,
            drift_ratio=drift_ratio,
            status=status,
            details=[f"{before} -> {after} ({drift_ratio:.2%})"],
        )
        if status == SensorStatus.FAIL and raise_on_excess:
            raise SensorCheckError(
                f"Excessive drift at {phase}: {drift_ratio:.2%}",
                reports=[report],
            )
        return report

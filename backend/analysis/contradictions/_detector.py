"""Contradiction detection orchestrator."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from analysis.models import Claim, Contradiction
from analysis.sensors import SensorCheckError, SensorReport

from ._comparators import (
    ClaimComparator,
    MaterialComparator,
    MissingAttributeComparator,
    NumericComparator,
    StandardComparator,
    get_comparator,
)
from ._grouper import group_by_entity, group_by_entity_attribute
from ._inferential import MeMoInferentialSensor
from ._resolver import DEFAULT_SOURCE_PRIORITY, DocumentHierarchyResolver
from ._scoring import score_conflict
from ._sensors import ContradictionDetectionSensor
from ._types import CandidateConflict


@dataclass
class DetectionResult:
    """Output of a full contradiction-detection run."""

    contradictions: List[Contradiction] = field(default_factory=list)
    reports: List[SensorReport] = field(default_factory=list)
    dropped: List[CandidateConflict] = field(default_factory=list)


class ContradictionDetector:
    """Run the full deterministic contradiction-detection pipeline."""

    def __init__(
        self,
        priority: Optional[Dict[str, int]] = None,
        sensor: Optional[ContradictionDetectionSensor] = None,
        raise_on_drift: bool = True,
        use_inferential: bool = False,
        inferential_sensor: Optional[MeMoInferentialSensor] = None,
    ):
        self.priority = priority if priority is not None else DEFAULT_SOURCE_PRIORITY
        self.resolver = DocumentHierarchyResolver(self.priority)
        self.sensor = sensor or ContradictionDetectionSensor()
        self.raise_on_drift = raise_on_drift
        self.use_inferential = use_inferential
        self.inferential_sensor = inferential_sensor

    def detect(self, claims: List[Claim]) -> DetectionResult:
        """Detect contradictions across a list of claims.

        Returns a DetectionResult with open contradictions, sensor reports,
        and any candidates dropped by document hierarchy. No external state
        is mutated and no RFI is auto-generated.
        """
        result = DetectionResult()
        if not claims:
            return result

        candidates = self._generate_candidates(claims)
        candidates, report = self.sensor.check_candidates(candidates)
        result.reports.append(report)

        if self.raise_on_drift and report.status.value == "fail":
            raise SensorCheckError("Candidate sensor failed", reports=result.reports)

        kept, dropped = self.resolver.resolve(candidates, claims)
        result.dropped = dropped
        drift_report = self.sensor.check_drift(
            len(candidates), len(kept), phase="resolve", raise_on_excess=False
        )
        result.reports.append(drift_report)

        if self.use_inferential:
            sensor = self.inferential_sensor or MeMoInferentialSensor()
            inferential = sensor.review(claims, kept)
            inferential, inf_report = self.sensor.check_candidates(inferential)
            result.reports.append(inf_report)
            if self.raise_on_drift and inf_report.status.value == "fail":
                raise SensorCheckError(
                    "Inferential sensor candidate check failed",
                    reports=result.reports,
                )
            kept = kept + inferential

        result.contradictions = self._build_contradictions(kept, claims)
        return result

    def _generate_candidates(self, claims: List[Claim]) -> List[CandidateConflict]:
        candidates: List[CandidateConflict] = []

        attr_groups = group_by_entity_attribute(claims)
        for (_entity, attribute), group_claims in attr_groups.items():
            comparator = self._comparator_for_attribute(attribute)
            if comparator is not None:
                candidates.extend(comparator.compare(group_claims))

        entity_groups = group_by_entity(claims)
        missing = MissingAttributeComparator()
        for group_claims in entity_groups.values():
            candidates.extend(missing.compare(group_claims))

        return candidates

    @staticmethod
    def _comparator_for_attribute(attribute: str) -> Optional[ClaimComparator]:
        comparator = get_comparator(attribute)
        if comparator is not None:
            return comparator
        # Material attributes that may not appear in the main registry.
        if attribute in {"fire rating", "valve type", "floor finish"}:
            return MaterialComparator()
        return None

    def _build_contradictions(
        self,
        candidates: List[CandidateConflict],
        claims: List[Claim],
    ) -> List[Contradiction]:
        by_id = {c.id: c for c in claims}
        contradictions: List[Contradiction] = []
        for candidate in candidates:
            involved = [by_id[cid] for cid in candidate.claim_ids if cid in by_id]
            confidence, severity = score_conflict(candidate, claims, self.priority)
            project_id = involved[0].project_id if involved else ""
            contradictions.append(
                Contradiction(
                    project_id=project_id,
                    contradiction_type=candidate.contradiction_type,
                    severity=severity,
                    confidence=confidence,
                    claim_ids=list(candidate.claim_ids),
                    description=candidate.description,
                    status="open",
                    metadata={**candidate.metadata, "sensor_checked": True},
                )
            )
        return contradictions

"""Phased claim extraction pipeline with sensor checkpoints.

Implements the four-stage flow from ADR-012: pattern match → normalize →
ground → verify. Each stage is guarded by a sensor so bad candidates are
caught and reported instead of silently polluting downstream contradiction
detection.
"""
import re
from dataclasses import dataclass, field
from typing import List

from chunking.models import Chunk

from ..models import Claim
from ..sensors import ClaimExtractionSensor, SensorCheckError, SensorReport
from ._canonicalizer import Canonicalizer
from ._material import MaterialClaimExtractor
from ._numeric import NumericClaimExtractor
from ._standard import StandardClaimExtractor
from ._types import Candidate, RawMatch

# [CITE: ADR-012] Normalize surface-form units to a canonical vocabulary.
UNIT_CANONICAL = {
    "feet": "ft",
    "ft": "ft",
    "'": "ft",
    "fpm": "fpm",
    "psi": "psi",
    "psig": "psi",
    "gpm/sf": "gpm/sf",
    "inches": "in",
    "in": "in",
    '"': "in",
    "sf": "sf",
}


@dataclass
class ExtractionResult:
    """Claims plus sensor reports from every checkpoint."""

    claims: List[Claim] = field(default_factory=list)
    reports: List[SensorReport] = field(default_factory=list)


class ClaimExtractor:
    """Orchestrate sub-extractors and validate every extraction phase."""

    def __init__(
        self,
        canonicalizer: Canonicalizer = None,
        sensor: ClaimExtractionSensor = None,
        raise_on_drift: bool = True,
    ):
        self.canonicalizer = canonicalizer or Canonicalizer()
        self.sensor = sensor or ClaimExtractionSensor()
        self.raise_on_drift = raise_on_drift
        self._matchers = [
            NumericClaimExtractor(),
            MaterialClaimExtractor(),
            StandardClaimExtractor(),
        ]

    def extract(self, chunk: Chunk) -> ExtractionResult:
        """Extract claims from ``chunk`` with sensor checkpoints after each phase."""
        all_claims: List[Claim] = []
        all_reports: List[SensorReport] = []

        for matcher in self._matchers:
            name = matcher.__class__.__name__
            matches = matcher.match(chunk.text)
            matches, report_match = self.sensor.check_matches(matches)
            candidates = [self._normalize(self._candidate_from_match(m)) for m in matches]
            candidates, report_norm = self.sensor.check_candidates(candidates)
            claims = [self._ground(c, chunk) for c in candidates]
            claims, report_ground = self.sensor.check_claims(claims, phase="ground")
            claims, report_verify = self.sensor.check_claims(claims, phase="verify")

            all_claims.extend(claims)
            all_reports.extend([report_match, report_norm, report_ground, report_verify])

            if self.raise_on_drift and any(
                r.status.value == "fail"
                for r in [report_match, report_norm, report_ground, report_verify]
            ):
                raise SensorCheckError(
                    f"Sensor drift detected in {name}", reports=all_reports
                )

        return ExtractionResult(claims=all_claims, reports=all_reports)

    def _candidate_from_match(self, match: RawMatch) -> Candidate:
        return Candidate(
            attribute=match.attribute,
            value=match.value,
            unit=match.unit,
            entity_hint=match.entity_hint,
            raw_value=match.raw_value,
            start=match.start,
            end=match.end,
            extractor=match.extractor,
        )

    def _normalize(self, candidate: Candidate) -> Candidate:
        value = candidate.value.strip()
        value = re.sub(r",", "", value)
        unit = candidate.unit.lower().strip()
        unit = UNIT_CANONICAL.get(unit, unit)
        return Candidate(
            attribute=candidate.attribute,
            value=value,
            unit=unit,
            entity_hint=candidate.entity_hint,
            raw_value=candidate.raw_value,
            start=candidate.start,
            end=candidate.end,
            extractor=candidate.extractor,
        )

    def _ground(self, candidate: Candidate, chunk: Chunk) -> Claim:
        entity = self.canonicalizer.canonicalize_entity(candidate.entity_hint or "unknown")
        attribute = self.canonicalizer.canonicalize_attribute(candidate.attribute)
        confidence = 0.85 if entity != "unknown" else 0.55
        if attribute == "applicable standard":
            confidence = 0.75
        source_text = chunk.text[max(0, candidate.start - 40) : candidate.end + 40]
        return Claim(
            entity=entity,
            attribute=attribute,
            value=candidate.value,
            unit=candidate.unit,
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            project_id=chunk.project_id,
            section_number=chunk.section_number,
            discipline=chunk.discipline,
            confidence=confidence,
            metadata={
                "extractor": candidate.extractor,
                "raw": candidate.raw_value,
                "source_text": source_text,
                "source_type": chunk.source_type,
            },
        )

"""MeMo-style inferential sensor for unresolved cross-entity claim pairs."""
import json
import re
from typing import Dict, List, Optional, Set, Tuple

from analysis.models import Claim

from ._memo_client import FakeMemoryModelClient, MemoryModelClient
from ._types import CandidateConflict


DEFAULT_INFERENTIAL_ATTRIBUTES = {
    "floor finish",
    "ceiling height",
    "fire rating",
    "applicable standard",
    "U-factor",
    "R-value",
}


class MeMoInferentialSensor:
    """Use a memory oracle to decide conflicts the deterministic layer missed."""

    def __init__(
        self,
        client: Optional[MemoryModelClient] = None,
        attribute_whitelist: Optional[Set[str]] = None,
        mode: str = "multi_turn",
    ):
        self.client = client or FakeMemoryModelClient()
        self.attribute_whitelist = attribute_whitelist or DEFAULT_INFERENTIAL_ATTRIBUTES
        self.mode = mode

    def review(
        self,
        claims: List[Claim],
        deterministic_candidates: List[CandidateConflict],
    ) -> List[CandidateConflict]:
        """Return inferential candidates for cross-entity pairs."""
        selected = self._select_pairs(claims, deterministic_candidates)
        results: List[CandidateConflict] = []
        for claim_a, claim_b in selected:
            candidate = self._evaluate_pair(claim_a, claim_b)
            if candidate is not None:
                results.append(candidate)
        return results

    def _select_pairs(
        self,
        claims: List[Claim],
        deterministic_candidates: List[CandidateConflict],
    ) -> List[Tuple[Claim, Claim]]:
        by_attribute: Dict[str, List[Claim]] = {}
        for claim in claims:
            attr = self._normalize(claim.attribute)
            if attr not in self.attribute_whitelist:
                continue
            if not claim.metadata.get("source_text"):
                continue
            by_attribute.setdefault(attr, []).append(claim)

        flagged: Set[Tuple[str, str]] = set()
        for candidate in deterministic_candidates:
            ids = sorted(candidate.claim_ids)
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    flagged.add((ids[i], ids[j]))

        pairs: List[Tuple[Claim, Claim]] = []
        for attr, attr_claims in by_attribute.items():
            for i in range(len(attr_claims)):
                for j in range(i + 1, len(attr_claims)):
                    a, b = attr_claims[i], attr_claims[j]
                    if self._normalize(a.entity) == self._normalize(b.entity):
                        continue
                    key = tuple(sorted([a.id, b.id]))
                    if key in flagged:
                        continue
                    pairs.append((a, b))
        return pairs

    def _evaluate_pair(
        self,
        claim_a: Claim,
        claim_b: Claim,
    ) -> Optional[CandidateConflict]:
        if self.mode == "multi_turn":
            prompts = self._multi_turn_prompts(claim_a, claim_b)
            responses = self.client.multi_turn(prompts)
            answer_text = responses[-1] if responses else ""
        else:
            answer_text = self.client.ask(self._single_prompt(claim_a, claim_b))

        parsed = self._parse_answer(answer_text)
        if parsed is None or not parsed.get("contradiction"):
            return None

        return CandidateConflict(
            contradiction_type=parsed.get("type", "inferential_conflict"),
            claim_ids=[claim_a.id, claim_b.id],
            description=(
                f"Inferential conflict: {claim_a.entity} ({claim_a.value}) vs "
                f"{claim_b.entity} ({claim_b.value})"
            ),
            metadata={
                "inferential_reason": parsed.get("explanation", ""),
                "inferential_confidence": parsed.get("confidence", 0.0),
                "values": [claim_a.value, claim_b.value],
                "attributes": [claim_a.attribute, claim_b.attribute],
            },
        )

    def _multi_turn_prompts(self, claim_a: Claim, claim_b: Claim) -> List[str]:
        return [
            self._grounding_prompt(claim_a),
            self._grounding_prompt(claim_b),
            self._synthesis_prompt(claim_a, claim_b),
        ]

    def _grounding_prompt(self, claim: Claim) -> str:
        return (
            "Project document context:\n"
            f"{claim.metadata.get('source_text', claim.value)}\n\n"
            "What entity is being described and what requirement is stated? "
            "Answer in one sentence."
        )

    def _synthesis_prompt(self, claim_a: Claim, claim_b: Claim) -> str:
        return (
            "You are reviewing two requirements from construction documents.\n\n"
            f"Requirement A: {claim_a.citation()}\n"
            f"Source A: {claim_a.metadata.get('source_text', '')}\n\n"
            f"Requirement B: {claim_b.citation()}\n"
            f"Source B: {claim_b.metadata.get('source_text', '')}\n\n"
            "Do these requirements contradict each other? "
            "Respond with valid JSON only:\n"
            '{"contradiction": bool, "confidence": 0..1, "type": "material_conflict|numeric_mismatch|standard_version|inferential_conflict", "explanation": "..."}'
        )

    def _single_prompt(self, claim_a: Claim, claim_b: Claim) -> str:
        return (
            "You are reviewing two requirements from construction documents.\n\n"
            f"Requirement A: {claim_a.citation()}\n"
            f"Source A: {claim_a.metadata.get('source_text', '')}\n\n"
            f"Requirement B: {claim_b.citation()}\n"
            f"Source B: {claim_b.metadata.get('source_text', '')}\n\n"
            "Do these requirements contradict each other? "
            "Respond with valid JSON only:\n"
            '{"contradiction": bool, "confidence": 0..1, "type": "...", "explanation": "..."}'
        )

    @staticmethod
    def _parse_answer(text: str) -> Optional[Dict[str, any]]:
        text = text.strip()
        # Extract the first JSON object if the model wraps it in markdown.
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]", " ", value.lower()).strip()

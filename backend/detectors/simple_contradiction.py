from typing import List, Dict
import re


class SimpleContradictionDetector:
    def detect(self, links: List[Dict]) -> List[Dict]:
        """Detect contradictions in linked entities."""
        contradictions = []

        for link in links:
            spec_value = self._extract_numeric(link["spec_value"])
            draw_value = self._extract_numeric(link["draw_value"])

            if spec_value is None or draw_value is None:
                continue

            # Check for numeric mismatch (>5% difference)
            if abs(spec_value - draw_value) / max(spec_value, 1e-6) > 0.05:
                contradictions.append({
                    "type": "numeric_mismatch",
                    "severity": "critical" if self._is_structural(link) else "major",
                    "spec_text": link["spec_text"],
                    "spec_value": spec_value,
                    "draw_text": link["draw_text"],
                    "draw_value": draw_value,
                    "unit": link["spec_unit"] or link["draw_unit"],
                    "explanation": f"Spec requires {spec_value}, but drawing shows {draw_value}",
                    "score": link["score"]
                })

        return contradictions

    def _extract_numeric(self, value_str: str) -> float:
        """Extract numeric value from string."""
        if not value_str:
            return None
        # Remove commas, extract first number
        cleaned = re.sub(r'[^\d.]', '', str(value_str).replace(',', ''))
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _is_structural(self, link: Dict) -> bool:
        """Check if this is a structural property."""
        structural_keywords = ["concrete", "strength", "rebar", "steel", "compression", "tension"]
        text = (link.get("spec_text", "") + " " + link.get("draw_text", "")).lower()
        return any(kw in text for kw in structural_keywords)

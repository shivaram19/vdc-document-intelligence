"""
Helpers for chunking construction documents.

Includes cross-reference detection and token counting.
"""

import re
from typing import List


# Construction standards commonly cited in specs and drawings.
STANDARD_ORGS = r"(?:NFPA|ASHRAE|IBC|ACI|AISC|SMACNA|ASTM|ANSI|IEEE|ASME|AWWA|UL|CSA|ISO|NEC|ADA|OSHA)"

CROSS_REFERENCE_PATTERNS = [
    # "Section 23 05 13", "Sec. 23 05 13"
    re.compile(r"\b(?:Section|Sec\.?)\s*(\d{1,2}\s*\d{2}\s*\d{2})\b", re.IGNORECASE),
    # "Drawing A-101", "Sheet M-301"
    re.compile(
        r"\b(?:Drawing|Sheet|Detail)\s*([A-Z]{1,4}\s*[\-–—]?\s*\d{1,4}(?:\.\d+)?)\b",
        re.IGNORECASE,
    ),
    # Standards: "NFPA 13", "ASHRAE 90.1-2022", "ACI 318-19", "SMACNA"
    re.compile(
        rf"\b{STANDARD_ORGS}\b(?:\s+(\d+[A-Z0-9\-\.]*))?\b",
        re.IGNORECASE,
    ),
    # Phrases like "See Section ..." or "Refer to Drawing ..."
    re.compile(
        r"\b(?:see|refer to|as per|in accordance with)\s+(?:Section|Drawing|Sheet)\s*([A-Z0-9\s\-]+)",
        re.IGNORECASE,
    ),
]


def extract_cross_references(text: str) -> List[str]:
    """Extract normalized cross-reference targets from chunk text."""
    refs: List[str] = []
    seen = set()

    for pattern in CROSS_REFERENCE_PATTERNS:
        for match in pattern.finditer(text):
            ref = " ".join(part.strip() for part in match.groups() if part).strip()
            prefix = _reference_prefix(match.group(0))
            if not ref and not prefix:
                continue

            # Normalize section numbers like "23 05 13" to "23-05-13"
            if re.match(r"^\d{1,2}\s+\d{2}\s+\d{2}$", ref):
                ref = ref.replace(" ", "-")
            # Normalize drawing numbers
            elif re.match(r"^[A-Z]{1,4}\s+\d", ref, re.IGNORECASE):
                ref = re.sub(r"\s+", "", ref).upper()

            normalized = (ref or prefix).upper()
            if normalized not in seen:
                seen.add(normalized)
                refs.append(f"{prefix} {normalized}".strip())

    return refs


def _reference_prefix(match_text: str) -> str:
    lowered = match_text.lower()
    if "section" in lowered or "sec" in lowered:
        return "Section"
    if "drawing" in lowered or "sheet" in lowered or "detail" in lowered:
        return "Drawing"
    for org in ["nfpa", "ashrae", "ibc", "aci", "aisc", "smacna", "astm", "ansi", "ieee"]:
        if org in lowered:
            return org.upper()
    return ""


def count_tokens(text: str) -> int:
    """
    Approximate token count.

    Prefer tiktoken when available; otherwise use whitespace splitting.
    Construction documents are mostly English prose, so whitespace is a
    reasonable proxy for embedding-model token budgets.
    """
    if not text:
        return 0
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text.split())

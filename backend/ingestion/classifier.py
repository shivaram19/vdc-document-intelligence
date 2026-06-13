"""
Classify construction documents and drawing sheets by discipline.

Uses deterministic heuristics based on sheet numbers, filenames, titles,
and content keywords. Deterministic classification is preferred over
LLM-based classification for auditability and speed.
"""

import re
from pathlib import Path
from typing import Optional

from .models import Discipline, DocumentType


# Discipline prefixes commonly used in North American / CSI drawing numbering
DISCIPLINE_PREFIXES = {
    Discipline.ARCHITECTURAL: ["A", "AR", "ARCH"],
    Discipline.STRUCTURAL: ["S", "ST", "STR"],
    Discipline.MECHANICAL: ["M", "ME", "MECH", "HVAC"],
    Discipline.ELECTRICAL: ["E", "EL", "ELEC"],
    Discipline.PLUMBING: ["P", "PL", "PLUMB"],
    Discipline.FIRE_PROTECTION: ["FP", "F", "FIRE"],
    Discipline.CIVIL: ["C", "CIV", "CIVIL"],
    Discipline.LANDSCAPE: ["L", "LS", "LAND"],
    Discipline.INTERIOR: ["I", "INT"],
    Discipline.GENERAL: ["G", "GEN"],
}

# Title/filename keyword fallback rules
DISCIPLINE_KEYWORDS = {
    Discipline.ARCHITECTURAL: [
        "floor plan", "elevation", "section", "reflected ceiling",
        "interior", "finishes", "door schedule", "window schedule",
        "architectural", "roof plan", "site plan",
    ],
    Discipline.STRUCTURAL: [
        "foundation", "framing", "column", "beam", "rebar", "concrete",
        "structural", "steel", "slab", "shear wall", "footing",
    ],
    Discipline.MECHANICAL: [
        "mechanical", "hvac", "duct", "air handling", "diffuser",
        "ventilation", "chiller", "boiler", "exhaust", "makeup air",
    ],
    Discipline.ELECTRICAL: [
        "electrical", "lighting", "power", "panel", "circuit",
        "conduit", "fire alarm", "low voltage", "switchgear",
    ],
    Discipline.PLUMBING: [
        "plumbing", "water", "sanitary", "waste", "vent", "fixture",
        "domestic water", "storm", "roof drain",
    ],
    Discipline.FIRE_PROTECTION: [
        "fire protection", "sprinkler", "standpipe", "fire alarm",
        "smoke detector", "suppression",
    ],
    Discipline.CIVIL: [
        "civil", "grading", "drainage", "utility", "paving",
        "erosion", "sediment", "stormwater", "manhole", "catch basin",
        "geotechnical", "soil", "boring",
    ],
    Discipline.SPECIFICATION: [
        "specification", "spec", "project manual", "division",
        "general conditions", "technical specification",
    ],
    Discipline.CONTRACT: [
        "contract", "agreement", "scope", "proposal", "bid",
        "subcontract", "purchase order",
    ],
    Discipline.REPORT: [
        "report", "study", "analysis", "investigation", "survey",
        "geotechnical report", "environmental",
    ],
}


def classify_document_type(filename: str) -> DocumentType:
    """Classify document type from filename extension."""
    ext = Path(filename).suffix.lower().lstrip(".")
    mapping = {
        "pdf": DocumentType.PDF,
        "dwg": DocumentType.DWG,
        "dxf": DocumentType.DXF,
        "rvt": DocumentType.RVT,
        "ifc": DocumentType.IFC,
        "docx": DocumentType.DOCX,
        "xlsx": DocumentType.XLSX,
        "txt": DocumentType.TXT,
    }
    return mapping.get(ext, DocumentType.UNKNOWN)


def classify_sheet_by_number(sheet_number: str) -> Optional[Discipline]:
    """Classify sheet discipline based on sheet number prefix."""
    if not sheet_number:
        return None
    normalized = sheet_number.strip().upper().replace(" ", "-")
    for discipline, prefixes in DISCIPLINE_PREFIXES.items():
        for prefix in prefixes:
            # Match prefix at start, followed by digit or dash
            pattern = re.compile(rf"^{re.escape(prefix)}(\d|-)")
            if pattern.match(normalized):
                return discipline
    return None


def _normalize_text(text: str) -> str:
    """Normalize separators so filename tokens can match multi-word keywords."""
    return text.lower().replace("_", " ").replace("-", " ")


def classify_by_keywords(text: str) -> Optional[Discipline]:
    """Classify discipline by keyword matching in title/filename/content."""
    if not text:
        return None
    normalized = _normalize_text(text)
    scores = {}
    for discipline, keywords in DISCIPLINE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in normalized)
        if score:
            scores[discipline] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def classify_sheet(
    sheet_number: str = "",
    title: str = "",
    filename: str = "",
) -> Discipline:
    """
    Classify a sheet's discipline using number, title, and filename.

    Priority:
    1. Sheet number prefix (most reliable)
    2. Title keywords
    3. Filename keywords
    4. Unknown
    """
    by_number = classify_sheet_by_number(sheet_number)
    if by_number:
        return by_number

    by_title = classify_by_keywords(title)
    if by_title:
        return by_title

    by_filename = classify_by_keywords(filename)
    if by_filename:
        return by_filename

    return Discipline.UNKNOWN


def classify_document(
    filename: str,
    title: str = "",
    content_preview: str = "",
) -> Discipline:
    """
    Classify a document's discipline from filename, title, and content.

    Specifications and reports are detected first because they often have
    generic filenames. Drawing filenames often embed sheet numbers (e.g. A-101).
    """
    text = f"{filename} {title} {content_preview[:500]}"
    normalized_text = _normalize_text(text)

    # First check for spec/report/contract indicators
    for doc_type_discipline in [Discipline.SPECIFICATION, Discipline.CONTRACT, Discipline.REPORT]:
        keywords = DISCIPLINE_KEYWORDS.get(doc_type_discipline, [])
        if any(kw in normalized_text for kw in keywords):
            return doc_type_discipline

    # Check for drawing sheet number prefixes in the filename
    first_token = Path(filename).stem.split()[0]
    by_number = classify_sheet_by_number(first_token)
    if by_number:
        return by_number

    # Fall back to keyword classification over the full normalized context
    by_keywords = classify_by_keywords(normalized_text)
    if by_keywords:
        return by_keywords

    return Discipline.UNKNOWN

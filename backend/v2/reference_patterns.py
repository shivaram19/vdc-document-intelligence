"""
Construction Document Reference Pattern Library
Extracts cross-references from drawing sets, specs, and submittals.

Based on:
- AIA drawing conventions
- Bluebeam Revu Batch Link algorithm
- Procore drawing link requirements
- Academic research on construction document NER
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ReferenceMatch:
    """A single cross-reference match found in document text."""
    ref_type: str           # 'sheet', 'detail', 'spec_section', 'tag', 'elevation', 'section', 'general'
    target_id: str          # The identifier (e.g., "A-101", "3", "033000")
    target_sheet: Optional[str] = None  # For detail callouts: the sheet the detail lives on
    source_context: str = ""  # Surrounding text for verification
    confidence: float = 1.0
    bbox: Optional[Tuple[float, float, float, float]] = None  # (x0, y0, x1, y1)


# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Sheet numbers: A-101, S-101, G-001, M-102.00, DM-111, A101
# Also matches common patterns like "A 101" or "A101"
SHEET_NUMBER_RE = re.compile(
    r'\b([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\b'
)

# Detail callouts: "Detail 3 on Sheet A-101", "detail 9 on sheet S5.1"
# Also: "9 of S5.1", "Detail 2 on C4.1", "SEE DETAIL A/A3.2"
DETAIL_ON_SHEET_RE = re.compile(
    r'(?i)\b(?:detail|section|elevation)\s+([A-Z0-9\.]+)\s+(?:on\s+)?(?:of\s+)?(?:sheet\s+)?([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\b'
)

# Slash notation: "3/A3.2" (detail 3 on sheet A3.2)
DETAIL_SLASH_RE = re.compile(
    r'(?i)\b(?:detail\s+)?(\d{1,3}|[A-Z])\s*/\s*([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\b'
)

# Spec section references: 033000, 01 1000, Division 08, Section 09 21 16
SPEC_SECTION_RE = re.compile(
    r'(?i)\b(?:section|spec|specification|division)\s+(\d{2}\s?\d{2}\s?\d{2}|\d{2})\b'
)

# CSI MasterFormat division references
CSI_DIVISION_RE = re.compile(
    r'(?i)\b(?:division|div\.?\s+)(\d{2})\b'
)

# Door/Window/Finish/Furniture tags: D-101, W-205, A-101, F-301, EQ-01
# Common prefixes in construction drawings
TAG_RE = re.compile(
    r'\b([DWMFECT]-\d{2,4}|EQ-\d{1,3}|CLG-\d{1,3}|WALL-[A-Z]\d{1,3})\b'
)

# Elevation references: "Elevation 1", "Elev. A", "EL. 2"
ELEVATION_RE = re.compile(
    r'(?i)\b(?:elevation|elev\.?|el\.?)\s+([A-Z0-9]{1,3})\b'
)

# Section references: "Section A", "Sec. B-B", "SECTION 1"
SECTION_RE = re.compile(
    r'(?i)\b(?:section|sec\.?)\s+([A-Z]{1,2}(?:\-[A-Z])?)\b'
)

# Generic "see" / "refer to" / "as shown on" references
CROSS_REF_RE = re.compile(
    r'(?i)\b(?:see|refer to|referencing|as shown on|as indicated on|per|noted on)\s+'
    r'((?:detail|sheet|section|plan|elevation|schedule|note|drawing)[\s\w\-/\.]+)'
)

# Schedule references: "Door Schedule", "Window Schedule", "Finish Schedule"
SCHEDULE_REF_RE = re.compile(
    r'(?i)\b(door|window|finish|room|equipment|lighting|plumbing|fire)\s+schedule\b'
)

# Revision references: "Rev 1", "Addendum 3", "Revision A"
REVISION_RE = re.compile(
    r'(?i)\b(?:revision|rev\.?|addendum|add\.|sketch|sk\.)\s+([A-Z0-9]{1,3})\b'
)

# Keynote references: "Note 7", "Keynote 3.5", "KN 12"
KEYNOTE_RE = re.compile(
    r'(?i)\b(?:keynote|kn|note)\s+([0-9]+(?:\.[0-9]+)?)\b'
)

# Page/Sheet references in title blocks: "SHEET ___ OF ___"
SHEET_OF_RE = re.compile(
    r'(?i)sheet\s+(\d+|\w+)\s+of\s+(\d+|\w+)'
)

# North arrow / orientation reference
NORTH_ARROW_RE = re.compile(
    r'(?i)\b(north arrow|true north|grid north)\b'
)

# Scale references: "SCALE: 1/8" = 1'-0"", "1:100", "3/16" = 1'-0""
SCALE_RE = re.compile(
    r'(?i)\b(?:scale[\s:]*)(1\s*[:/]\s*\d+|\d+/\d+\s*[=\u201d]\s*1\s*[-\u2019]\s*0\s*["\u201d])\b'
)


# =============================================================================
# REFERENCE EXTRACTOR CLASS
# =============================================================================

class ReferenceExtractor:
    """Extract all types of cross-references from construction document text."""

    def __init__(self, known_sheets: Optional[List[str]] = None):
        """
        Args:
            known_sheets: Pre-populated list of valid sheet numbers from drawing index.
                          Used to filter false positives and resolve ambiguous refs.
        """
        self.known_sheets = set(s.strip().upper().replace(" ", "-").replace("--", "-")
                                for s in (known_sheets or []))
        self._sheet_norm_cache = {}

    def _normalize_sheet(self, sheet: str) -> str:
        """Normalize sheet number for comparison: 'A 101' → 'A-101'."""
        if sheet in self._sheet_norm_cache:
            return self._sheet_norm_cache[sheet]
        norm = sheet.strip().upper().replace(" ", "-").replace("--", "-")
        self._sheet_norm_cache[sheet] = norm
        return norm

    def _is_known_sheet(self, sheet: str) -> bool:
        """Check if a sheet number exists in the drawing index."""
        return self._normalize_sheet(sheet) in self.known_sheets

    def extract_sheet_references(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract standalone sheet number references."""
        refs = []
        for m in SHEET_NUMBER_RE.finditer(text):
            sheet = m.group(1)
            # Skip if it looks like a dimension (e.g., "12'-0"")
            if "'" in sheet or '"' in sheet:
                continue
            # Check context — is this actually a sheet reference?
            context = self._get_context(text, m.start(), m.end())
            if any(kw in context.lower() for kw in ["sheet", "see", "refer", "detail", "on"]):
                confidence = 0.9 if self._is_known_sheet(sheet) else 0.6
                refs.append(ReferenceMatch(
                    ref_type="sheet",
                    target_id=self._normalize_sheet(sheet),
                    source_context=context,
                    confidence=confidence
                ))
        return refs

    def extract_detail_callouts(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract detail callouts like 'Detail 3 on Sheet A-101' or '3/A3.2'."""
        refs = []

        # Pattern: "Detail 3 on Sheet A-101"
        for m in DETAIL_ON_SHEET_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="detail",
                target_id=m.group(1),
                target_sheet=self._normalize_sheet(m.group(2)),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.95
            ))

        # Pattern: "3/A3.2" (detail/sheet slash notation)
        for m in DETAIL_SLASH_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="detail",
                target_id=m.group(1),
                target_sheet=self._normalize_sheet(m.group(2)),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.9
            ))

        return refs

    def extract_spec_references(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract specification section references."""
        refs = []

        for m in SPEC_SECTION_RE.finditer(text):
            spec = m.group(1).replace(" ", "")
            refs.append(ReferenceMatch(
                ref_type="spec_section",
                target_id=spec,
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.95
            ))

        for m in CSI_DIVISION_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="division",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.85
            ))

        return refs

    def extract_tags(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract door/window/finish tags."""
        refs = []
        for m in TAG_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="tag",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.9
            ))
        return refs

    def extract_elevations_and_sections(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract elevation and section markers."""
        refs = []

        for m in ELEVATION_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="elevation",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.9
            ))

        for m in SECTION_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="section",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.9
            ))

        return refs

    def extract_schedules(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract schedule references."""
        refs = []
        for m in SCHEDULE_REF_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="schedule",
                target_id=m.group(1).lower(),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.95
            ))
        return refs

    def extract_revisions(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract revision/addendum references."""
        refs = []
        for m in REVISION_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="revision",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.85
            ))
        return refs

    def extract_keynotes(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Extract keynote/note references."""
        refs = []
        for m in KEYNOTE_RE.finditer(text):
            refs.append(ReferenceMatch(
                ref_type="keynote",
                target_id=m.group(1),
                source_context=self._get_context(text, m.start(), m.end()),
                confidence=0.8
            ))
        return refs

    def extract_all(self, text: str, page_num: int = 0) -> List[ReferenceMatch]:
        """Run all extractors and return combined, deduplicated results."""
        all_refs = []
        all_refs.extend(self.extract_sheet_references(text, page_num))
        all_refs.extend(self.extract_detail_callouts(text, page_num))
        all_refs.extend(self.extract_spec_references(text, page_num))
        all_refs.extend(self.extract_tags(text, page_num))
        all_refs.extend(self.extract_elevations_and_sections(text, page_num))
        all_refs.extend(self.extract_schedules(text, page_num))
        all_refs.extend(self.extract_revisions(text, page_num))
        all_refs.extend(self.extract_keynotes(text, page_num))

        # Deduplicate by (type, target_id, target_sheet)
        seen = set()
        deduped = []
        for ref in all_refs:
            key = (ref.ref_type, ref.target_id, ref.target_sheet)
            if key not in seen:
                seen.add(key)
                deduped.append(ref)

        return deduped

    def _get_context(self, text: str, start: int, end: int, window: int = 60) -> str:
        """Extract surrounding text for context."""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        context = text[ctx_start:ctx_end].replace('\n', ' ').strip()
        # Truncate if too long
        if len(context) > 150:
            context = context[:150] + "..."
        return context


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_drawing_index(text: str) -> List[str]:
    """
    Parse a drawing index (typically sheet G-001) to extract the canonical
    list of all sheet numbers in the drawing set.

    Expected format per line:
        A-101   FIRST FLOOR PLAN
        S-201   ROOF FRAMING PLAN
        M-301   HVAC PLAN
    """
    sheets = []
    for line in text.splitlines():
        line = line.strip()
        # Match sheet number at start of line: A-101, S201, G.001
        m = re.match(r'^\s*([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\s+(.+)$', line)
        if m:
            sheet_num = m.group(1).strip().upper().replace(" ", "-")
            title = m.group(2).strip()
            sheets.append({
                "number": sheet_num,
                "title": title,
                "normalized": sheet_num.replace("--", "-")
            })
    return sheets


def is_likely_sheet_number(text: str) -> bool:
    """Quick check if a string looks like a sheet number."""
    return bool(SHEET_NUMBER_RE.fullmatch(text))

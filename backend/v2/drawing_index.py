"""
Drawing Index Parser
Extracts the canonical list of sheets from a drawing set's index/cover sheet.
This is the ground truth for all cross-reference resolution.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class SheetEntry:
    """A single sheet entry from the drawing index."""
    number: str           # e.g., "A-101"
    title: str            # e.g., "FIRST FLOOR PLAN"
    discipline: str = ""  # e.g., "A" for Architectural, "S" for Structural
    page_offset: int = 0  # Approximate PDF page number
    normalized: str = ""  # Normalized form for comparison

    def __post_init__(self):
        if not self.normalized:
            self.normalized = self._normalize(self.number)
        if not self.discipline and self.number:
            self.discipline = re.match(r'^([A-Z]+)', self.number).group(1) if re.match(r'^([A-Z]+)', self.number) else ""

    @staticmethod
    def _normalize(sheet_num: str) -> str:
        return sheet_num.strip().upper().replace(" ", "-").replace("--", "-")


@dataclass
class DrawingIndex:
    """Complete drawing index parsed from a cover sheet or G-001."""
    project_name: str = ""
    project_number: str = ""
    sheets: List[SheetEntry] = field(default_factory=list)
    disciplines: Dict[str, List[SheetEntry]] = field(default_factory=dict)

    def get_sheet(self, number: str) -> Optional[SheetEntry]:
        """Look up a sheet by number (fuzzy matching)."""
        norm = SheetEntry._normalize(number)
        for sheet in self.sheets:
            if sheet.normalized == norm:
                return sheet
        return None

    def get_by_discipline(self, discipline: str) -> List[SheetEntry]:
        """Get all sheets for a discipline (e.g., 'A', 'S', 'M')."""
        return self.disciplines.get(discipline.upper(), [])

    def is_valid_sheet(self, number: str) -> bool:
        """Check if a sheet number exists in the index."""
        return self.get_sheet(number) is not None

    @property
    def total_sheets(self) -> int:
        return len(self.sheets)

    @property
    def discipline_list(self) -> List[str]:
        return sorted(self.disciplines.keys())


class DrawingIndexParser:
    """Parse drawing index from text extracted from a PDF cover sheet or G-001."""

    # Common patterns for drawing index lines
    INDEX_LINE_PATTERNS = [
        # A-101   FIRST FLOOR PLAN
        re.compile(r'^\s*([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\s+(.+)$'),
        # A 101 — FIRST FLOOR PLAN
        re.compile(r'^\s*([A-Z]{1,3})\s*[\-–—]\s*(\d{2,4})\s+(.+)$'),
        # 1.  A-101   FIRST FLOOR PLAN
        re.compile(r'^\s*\d+\.\s+([A-Z]{1,3}[\s\-]?\d{2,4}(?:\.\d+)?)\s+(.+)$'),
    ]

    # Project name patterns (from title block)
    PROJECT_NAME_PATTERNS = [
        re.compile(r'(?i)\bproject\s*(?:name|title)?\s*[:\-]\s*(.+)$'),
        re.compile(r'(?i)\bproject\s*(.+)$'),
    ]

    # Project number patterns
    PROJECT_NUMBER_PATTERNS = [
        re.compile(r'(?i)\bproject\s*(?:no|number|#)\s*[:\-]\s*([A-Z0-9\-]+)'),
        re.compile(r'(?i)\bjob\s*(?:no|number|#)\s*[:\-]\s*([A-Z0-9\-]+)'),
    ]

    def parse(self, text: str, project_name_hint: str = "") -> DrawingIndex:
        """
        Parse drawing index text into structured format.

        Args:
            text: Full text extracted from the drawing index sheet.
            project_name_hint: Optional project name if already known.

        Returns:
            DrawingIndex with all sheets and metadata.
        """
        index = DrawingIndex()
        lines = text.splitlines()

        # Extract project metadata from first few lines
        for line in lines[:20]:
            for pat in self.PROJECT_NAME_PATTERNS:
                m = pat.search(line)
                if m and not index.project_name:
                    index.project_name = m.group(1).strip()
            for pat in self.PROJECT_NUMBER_PATTERNS:
                m = pat.search(line)
                if m and not index.project_number:
                    index.project_number = m.group(1).strip()

        if project_name_hint:
            index.project_name = project_name_hint

        # Parse sheet entries
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            for pat in self.INDEX_LINE_PATTERNS:
                m = pat.match(line)
                if m:
                    if len(m.groups()) == 2:
                        sheet_num = m.group(1).strip()
                        title = m.group(2).strip()
                    else:
                        # Pattern with separate discipline + number
                        sheet_num = f"{m.group(1)}-{m.group(2)}"
                        title = m.group(3).strip()

                    entry = SheetEntry(number=sheet_num, title=title)
                    index.sheets.append(entry)

                    # Group by discipline
                    disc = entry.discipline
                    if disc:
                        if disc not in index.disciplines:
                            index.disciplines[disc] = []
                        index.disciplines[disc].append(entry)
                    break  # Stop trying patterns once one matches

        return index

    def parse_from_pdf(self, pdf_path: str, page_num: int = 0) -> DrawingIndex:
        """Parse drawing index directly from a PDF file."""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                    return self.parse(text)
        except ImportError:
            pass

        try:
            import fitz  # PyMuPDF fallback
            doc = fitz.open(pdf_path)
            if page_num < len(doc):
                text = doc[page_num].get_text()
                return self.parse(text)
        except ImportError:
            pass

        return DrawingIndex()

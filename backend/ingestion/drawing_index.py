"""
Drawing index parser for construction document sets.

Extracts structured sheet records from drawing index pages and per-page
headers.  The parser is intentionally deterministic: sheet numbers follow
conventions defined by the National CAD Standard / AIA Uniform Drawing System
(e.g. A-101, S-201, M-301) rather than relying on LLM inference.

[CITE: NCS-US-2024] National CAD Standard drawing sheet numbering conventions.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from .classifier import classify_sheet
from .extractor import extract_pdf_text_samples
from .models import Sheet


class DrawingIndexParser:
    """Parse drawing index pages and per-page sheet headers."""

    # Sheet number with optional dash/space separator, e.g. A-101, S 201, MEP301
    SHEET_NUMBER_RE = r"[A-Z]{1,4}(?:\s*[\-–—]\s*)?\d{1,4}(?:\.\d+)?"

    # A single index row.  Tolerates a leading "Sheet" token and leading
    # bullet/number prefixes.
    INDEX_LINE_PATTERN = re.compile(
        rf"^\s*(?:Sheet\s+)?(?:\d+[.\)]\s+)?(?P<number>{SHEET_NUMBER_RE})\s+"
        rf"(?:(?:[-–—])\s+)?(?P<title>.+?)$",
        re.IGNORECASE,
    )

    # Per-page header pattern: matches "A-101 FIRST FLOOR PLAN" near top.
    HEADER_LINE_PATTERN = re.compile(
        rf"^\s*(?:Sheet\s+)?(?P<number>{SHEET_NUMBER_RE})\s*[:\-–—]?\s*(?P<title>.+?)$",
        re.IGNORECASE,
    )

    # Lines that should terminate title continuation.
    _FOOTER_TOKENS = (
        "page",
        "revision",
        "date",
        "drawn by",
        "checked by",
        "approved by",
        "project no",
        "division",
    )

    def __init__(self):
        self.sheet_number_regex = re.compile(r"\b" + self.SHEET_NUMBER_RE + r"\b")

    def parse_text(self, text: str) -> List[Sheet]:
        """Parse index text into sheet entries, merging wrapped titles."""
        sheets: List[Sheet] = []
        seen: set = set()
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if len(line) < 5:
                i += 1
                continue

            match = self.INDEX_LINE_PATTERN.match(line)
            if not match:
                i += 1
                continue

            number = self._normalize_number(match.group("number"))
            title = match.group("title").strip()

            # Merge wrapped title lines until the next index row or footer token.
            while i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if not next_line:
                    break
                if self.INDEX_LINE_PATTERN.match(next_line):
                    break
                if self._is_footer_line(next_line):
                    break
                title += " " + next_line
                i += 1

            title = self._clean_title(title)
            if len(title) < 3 or number in seen:
                i += 1
                continue

            seen.add(number)
            sheets.append(
                Sheet(
                    number=number,
                    title=title,
                    discipline=classify_sheet(sheet_number=number, title=title),
                )
            )
            i += 1

        return sheets

    def parse_pdf(
        self,
        path: Path,
        max_index_pages: int = 5,
    ) -> Tuple[List[Sheet], List[Sheet]]:
        """
        Extract sheets from a PDF drawing set.

        Returns:
            A tuple of (index_sheets, per_page_sheets).  index_sheets are parsed
            from an explicit drawing index (usually the first pages).  If no
            index is found, per_page_sheets can be used as a fallback.
        """
        text_samples = extract_pdf_text_samples(path, max_pages=max_index_pages)

        index_sheets: List[Sheet] = []
        for page_num, text in text_samples:
            sheets = self.parse_text(text)
            if sheets:
                for sheet in sheets:
                    sheet.page_number = page_num
                index_sheets.extend(sheets)
                break

        per_page_sheets: List[Sheet] = []
        for page_num, text in text_samples:
            sheet = self._extract_header_sheet(text, page_num)
            if sheet and sheet.number not in {s.number for s in per_page_sheets}:
                per_page_sheets.append(sheet)

        return index_sheets, per_page_sheets

    def _extract_header_sheet(self, text: str, page_number: int) -> Optional[Sheet]:
        """Try to extract a sheet record from the top of a single page."""
        lines = text.splitlines()[:20]  # only inspect header region
        for line in lines:
            line = line.strip()
            if len(line) < 3:
                continue
            match = self.HEADER_LINE_PATTERN.match(line)
            if match:
                number = self._normalize_number(match.group("number"))
                title = self._clean_title(match.group("title"))
                return Sheet(
                    number=number,
                    title=title,
                    page_number=page_number,
                    discipline=classify_sheet(sheet_number=number, title=title),
                )
        return None

    def _normalize_number(self, raw: str) -> str:
        """Normalize a sheet number token to A-101 form."""
        normalized = raw.upper().replace(" ", "")
        # Ensure a dash between letters and digits if absent.
        normalized = re.sub(r"^([A-Z]+)(\d)", r"\1-\2", normalized)
        return normalized

    def _clean_title(self, title: str) -> str:
        """Strip trailing metadata like page numbers and revision columns."""
        # Remove trailing tokens commonly found in index columns.
        for token in self._FOOTER_TOKENS:
            idx = title.lower().rfind(f" {token}")
            if idx > 3:
                title = title[:idx]
        # Collapse whitespace.
        return re.sub(r"\s+", " ", title).strip()

    def _is_footer_line(self, line: str) -> bool:
        lowered = line.lower()
        return any(lowered.startswith(token) for token in self._FOOTER_TOKENS)

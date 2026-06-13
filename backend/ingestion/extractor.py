"""
Extract metadata from construction documents and drawing sheets.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .classifier import classify_document_type
from .models import DocumentType, Sheet


# Patterns for revision, date, and sheet number extraction
SHEET_NUMBER_PATTERNS = [
    # A-101, S-201, MEP-301
    re.compile(r"\b([A-Z]{1,4}[\s\-]?\d{1,4}(?:\.\d+)?)\b"),
]

REVISION_PATTERNS = [
    # "Revision 1", "Rev A", "Rev. 2" but not "REVIEWED"
    re.compile(r"(?i)\brev(?:ision)?\b\s*[.:]?\s*([A-Z0-9]+)\b"),
    re.compile(r"(?i)\brev\b\s*#?\s*([A-Z0-9]+)\b"),
]

DATE_PATTERNS = [
    # 06/15/2026, 15/06/2026, 2026-06-15
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
    re.compile(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"),
    # June 15, 2026
    re.compile(r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b", re.IGNORECASE),
]


def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_sheet_number_from_text(text: str) -> Optional[str]:
    """Extract the most likely sheet number from text."""
    if not text:
        return None
    candidates = []
    for pattern in SHEET_NUMBER_PATTERNS:
        for match in pattern.finditer(text):
            candidates.append(match.group(1).strip().replace(" ", "-"))
    # Prefer shortest, most standard-looking sheet number
    if not candidates:
        return None
    candidates = sorted(candidates, key=lambda x: (len(x), x))
    return candidates[0]


def extract_revision(text: str) -> str:
    """Extract revision marker from text."""
    if not text:
        return ""
    for pattern in REVISION_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip().upper()
    return ""


def extract_date(text: str) -> Optional[str]:
    """Extract the first plausible date from text."""
    if not text:
        return None
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def extract_title_from_filename(filename: str) -> str:
    """Generate a human-readable title from filename."""
    name = Path(filename).stem
    # Replace separators with spaces
    name = re.sub(r"[_\-]+", " ", name)
    # Title case
    return name.strip().title()


def extract_pdf_metadata(path: Path) -> Dict[str, Any]:
    """Extract metadata from a PDF file using pdfplumber."""
    metadata = {
        "page_count": 0,
        "title": "",
        "author": "",
        "creator": "",
        "producer": "",
        "created": None,
        "modified": None,
    }
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            metadata["page_count"] = len(pdf.pages)
            if pdf.metadata:
                meta = pdf.metadata
                metadata["title"] = meta.get("Title", "") or ""
                metadata["author"] = meta.get("Author", "") or ""
                metadata["creator"] = meta.get("Creator", "") or ""
                metadata["producer"] = meta.get("Producer", "") or ""
                metadata["created"] = meta.get("CreationDate") or meta.get("Created")
                metadata["modified"] = meta.get("ModDate") or meta.get("Modified")
    except Exception:
        pass
    return metadata


def extract_pdf_text_samples(path: Path, max_pages: int = 3) -> List[Tuple[int, str]]:
    """Extract text samples from first N pages of a PDF."""
    samples = []
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                text = page.extract_text() or ""
                samples.append((i, text[:2000]))
    except Exception:
        pass
    return samples


def parse_drawing_index(text: str) -> List[Sheet]:
    """
    Parse a drawing index page into a list of Sheet objects.

    Looks for lines like:
        A-101  FIRST FLOOR PLAN
        S-201  FOUNDATION PLAN
    """
    sheets = []
    index_line_pattern = re.compile(
        r"^\s*([A-Z]{1,4}[\s\-]?\d{1,4}(?:\.\d+)?)\s+(?:(?:[-–—])\s+)?(.+?)$"
    )
    seen = set()

    for line in text.splitlines():
        line = line.strip()
        if len(line) < 5:
            continue
        match = index_line_pattern.match(line)
        if match:
            number = match.group(1).strip().replace(" ", "-")
            title = match.group(2).strip()
            # Filter out false positives: title should look like a sheet title
            if len(title) < 3 or title.lower().startswith("page"):
                continue
            if number in seen:
                continue
            seen.add(number)
            sheets.append(
                Sheet(
                    number=number,
                    title=title,
                    page_number=0,  # Unknown without mapping
                )
            )
    return sheets

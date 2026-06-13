"""
Helpers for chunking construction documents.

Includes cross-reference detection, table extraction, and token counting.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


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


# ---------------------------------------------------------------------------
# Cross-reference extraction
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------

@dataclass
class TableBlock:
    """A table-like region detected in plain text."""

    rows: List[List[str]] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    caption: str = ""

    @property
    def markdown(self) -> str:
        """Render as a markdown table."""
        if not self.rows:
            return ""
        # Escape pipes inside cells.
        escaped = [[cell.replace("|", "\\|") for cell in row] for row in self.rows]
        lines = ["| " + " | ".join(row) + " |" for row in escaped]
        # Separator between header and body if we have a header.
        if len(escaped) > 1:
            sep = "| " + " | ".join("---" for _ in escaped[0]) + " |"
            lines.insert(1, sep)
        if self.caption:
            lines.append(f"\n*Table: {self.caption}*")
        return "\n".join(lines)

    @property
    def column_count(self) -> int:
        return max((len(row) for row in self.rows), default=0)

    @property
    def row_count(self) -> int:
        return len(self.rows)


def extract_text_tables(text: str, min_rows: int = 2, min_cols: int = 2) -> List[TableBlock]:
    """
    Detect tables in plain text.

    Supports:
    - Markdown pipe tables.
    - Whitespace-aligned tables (at least 2 spaces between columns).

    Returns a list of non-overlapping TableBlock objects ordered by appearance.
    """
    tables: List[TableBlock] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        pipe_table = _try_pipe_table(lines, i)
        if pipe_table:
            tables.append(pipe_table)
            i = pipe_table.end_line
            continue

        whitespace_table = _try_whitespace_table(lines, i, min_rows, min_cols)
        if whitespace_table:
            tables.append(whitespace_table)
            i = whitespace_table.end_line
            continue

        i += 1

    # Assign captions from the nearest preceding non-table line.
    for table in tables:
        if table.start_line > 0:
            previous = lines[table.start_line - 1].strip()
            if previous and not _is_table_line(previous):
                table.caption = previous

    return tables


def _is_table_line(line: str) -> bool:
    return "|" in line or re.search(r"\S\s{2,}\S", line) is not None


def _try_pipe_table(lines: List[str], start: int) -> Optional[TableBlock]:
    """Detect a markdown/pipe table starting at `start`."""
    rows: List[List[str]] = []
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        # Skip markdown separator lines like |---|---|
        if all(re.match(r"^[:\-]+$", c) for c in cells if c):
            i += 1
            continue
        if len(cells) < 2:
            break
        rows.append(cells)
        i += 1

    if len(rows) < 2:
        return None

    return TableBlock(rows=rows, start_line=start, end_line=i)


def _try_whitespace_table(
    lines: List[str], start: int, min_rows: int, min_cols: int
) -> Optional[TableBlock]:
    """Detect a whitespace-separated table starting at `start`."""
    rows: List[List[str]] = []
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            break
        # Require at least two columns separated by 2+ spaces or tabs.
        cells = [c.strip() for c in re.split(r"\t|\s{2,}", stripped) if c.strip()]
        if len(cells) < min_cols:
            break
        # Reject lines that are clearly prose sentences (only one long cell).
        if len(cells) == 1:
            break
        rows.append(cells)
        i += 1

    if len(rows) < min_rows:
        return None

    # Normalize rows to the most common column count to avoid ragged tables.
    counts = {}
    for row in rows:
        counts[len(row)] = counts.get(len(row), 0) + 1
    target_cols = max(counts, key=counts.get)
    normalized_rows = [row[:target_cols] for row in rows if len(row) >= target_cols]

    if len(normalized_rows) < min_rows:
        return None

    return TableBlock(rows=normalized_rows, start_line=start, end_line=i)


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------


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

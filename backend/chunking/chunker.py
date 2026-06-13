"""
Hierarchical chunking for Medha documents.

Produces Chunk objects aligned with ADR-011:
- Specifications / codes are split by MasterFormat section and subsection.
- Drawings are split by sheet or by lettered note paragraph.
- RFIs are split by item.
- Unstructured text falls back to sliding-window paragraphs.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ingestion.models import Discipline, Document, DocumentType, Sheet
from chunking.extractors import (
    TableBlock,
    count_tokens,
    extract_cross_references,
    extract_text_tables,
)
from chunking.models import Chunk


# Document-type dispatch helpers

def _source_type(document: Document) -> str:
    if document.discipline == Discipline.SPECIFICATION:
        return "spec"
    if document.document_type in (DocumentType.PDF, DocumentType.DWG, DocumentType.DXF):
        return "drawing"
    if document.discipline in (Discipline.CONTRACT, Discipline.REPORT):
        return document.discipline.value.lower()
    return "unknown"


def _looks_like_spec(document: Document) -> bool:
    if document.discipline == Discipline.SPECIFICATION:
        return True
    text = (document.extracted_text or "").upper()
    return "SECTION" in text and re.search(r"\b\d{2}\s*\d{2}\s*\d{2}\b", text) is not None


def _looks_like_drawing(document: Document) -> bool:
    if document.document_type in (DocumentType.DWG, DocumentType.DXF):
        return True
    if document.sheets:
        return True
    text = (document.extracted_text or "").upper()
    return "SHEET" in text and re.search(r"\b[A-Z]{1,4}\s*[\-–—]?\s*\d{1,4}\b", text) is not None


def _looks_like_rfi(document: Document) -> bool:
    text = (document.extracted_text or "").upper()
    return re.search(r"\bRFI-\d+\b", text) is not None


# ---------------------------------------------------------------------------
# Base chunker
# ---------------------------------------------------------------------------

@dataclass
class ChunkerContext:
    document: Document
    source_type: str
    discipline: str

    def base_chunk(self) -> Chunk:
        return Chunk(
            document_id=self.document.id,
            project_id=self.document.project_id,
            source_type=self.source_type,
            discipline=self.discipline,
        )


class BaseChunker:
    def __init__(self, context: ChunkerContext, max_tokens: int = 512, overlap_tokens: int = 64):
        self.context = context
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self) -> List[Chunk]:
        raise NotImplementedError

    def _split_oversized(self, chunk: Chunk) -> List[Chunk]:
        """Break an oversized chunk into clause/paragraph pieces."""
        if count_tokens(chunk.text) <= self.max_tokens:
            return [chunk]

        pieces: List[str] = []
        # Try lettered clauses first (A., B., C. ...)
        clauses = re.split(r"\n(?=[A-Z]\.\s)", chunk.text)
        if len(clauses) > 1:
            pieces = [c.strip() for c in clauses if c.strip()]
        else:
            # Fall back to paragraphs
            pieces = [p.strip() for p in chunk.text.split("\n\n") if p.strip()]

        if len(pieces) <= 1:
            return [chunk]

        out: List[Chunk] = []
        running_text = ""
        running_tokens = 0
        for piece in pieces:
            piece_tokens = count_tokens(piece)
            if running_tokens and running_tokens + piece_tokens > self.max_tokens:
                out.append(
                    Chunk(
                        document_id=chunk.document_id,
                        project_id=chunk.project_id,
                        source_type=chunk.source_type,
                        discipline=chunk.discipline,
                        level=chunk.level + 1,
                        parent_id=chunk.parent_id,
                        section_number=chunk.section_number,
                        title=chunk.title,
                        text=running_text.strip(),
                    )
                )
                running_text = piece
                running_tokens = piece_tokens
            else:
                running_text += "\n\n" + piece if running_text else piece
                running_tokens += piece_tokens

        if running_text.strip():
            out.append(
                Chunk(
                    document_id=chunk.document_id,
                    project_id=chunk.project_id,
                    source_type=chunk.source_type,
                    discipline=chunk.discipline,
                    level=chunk.level + 1,
                    parent_id=chunk.parent_id,
                    section_number=chunk.section_number,
                    title=chunk.title,
                    text=running_text.strip(),
                )
            )
        return out


# ---------------------------------------------------------------------------
# Specification / code chunker
# ---------------------------------------------------------------------------

class SpecificationChunker(BaseChunker):
    """Chunk CSI MasterFormat-style specifications."""

    SECTION_RE = re.compile(
        r"^\s*SECTION\s+(\d{1,2}\s*\d{2}\s*\d{2})\s*[\-–—]+\s*(.+)$",
        re.IGNORECASE,
    )
    SUBSECTION_RE = re.compile(
        r"^(\d+(?:\.\d+)+)\s+(.+)$",
    )

    def chunk(self) -> List[Chunk]:
        text = self.context.document.extracted_text or ""
        lines = text.splitlines()
        chunks: List[Chunk] = []

        current_section_chunk: Optional[Chunk] = None
        current_subsection_title = ""
        current_subsection_number = ""
        current_subsection_lines: List[str] = []

        def flush_subsection() -> None:
            if not current_subsection_lines:
                return
            body = "\n".join(current_subsection_lines).strip()
            if not body:
                return
            chunk = Chunk(
                document_id=self.context.document.id,
                project_id=self.context.document.project_id,
                source_type=self.context.source_type,
                discipline=self.context.discipline,
                level=2,
                parent_id=current_section_chunk.id if current_section_chunk else None,
                section_number=current_subsection_number
                or (current_section_chunk.section_number if current_section_chunk else ""),
                title=current_subsection_title
                or (current_section_chunk.title if current_section_chunk else ""),
                text=body,
            )
            if count_tokens(chunk.text) > self.max_tokens:
                chunks.extend(self._split_oversized(chunk))
            else:
                chunks.append(chunk)

        for raw_line in lines:
            line = raw_line.rstrip()
            section_match = self.SECTION_RE.match(line)
            if section_match:
                flush_subsection()
                section_number = section_match.group(1).replace(" ", "-")
                section_title = section_match.group(2).strip()
                current_section_chunk = Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type=self.context.source_type,
                    discipline=self.context.discipline,
                    level=1,
                    section_number=section_number,
                    title=section_title,
                    text=f"SECTION {section_number} — {section_title}",
                )
                chunks.append(current_section_chunk)
                current_subsection_title = ""
                current_subsection_number = ""
                current_subsection_lines = []
                continue

            subsection_match = self.SUBSECTION_RE.match(line)
            if subsection_match and current_section_chunk is not None:
                flush_subsection()
                current_subsection_number = subsection_match.group(1)
                current_subsection_title = subsection_match.group(2).strip()
                current_subsection_lines = [line]
                continue

            if current_subsection_lines or current_section_chunk is not None:
                # Avoid appending blank lines before any content
                current_subsection_lines.append(raw_line)

        flush_subsection()

        # If no sections were detected, treat the whole document as one chunk.
        if not chunks:
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type=self.context.source_type,
                    discipline=self.context.discipline,
                    level=1,
                    title=self.context.document.original_filename,
                    text=text.strip(),
                )
            )

        chunks = self._split_table_chunks(chunks)
        return self._enrich(chunks)

    def _enrich(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            chunk.token_count = count_tokens(chunk.text)
            chunk.refs = extract_cross_references(chunk.text)
        return chunks

    def _split_table_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Extract inline tables from subsection chunks as standalone chunks."""
        out: List[Chunk] = []
        for chunk in chunks:
            if chunk.level != 2 or chunk.source_type != self.context.source_type:
                out.append(chunk)
                continue

            tables = extract_text_tables(chunk.text)
            if not tables:
                out.append(chunk)
                continue

            lines = chunk.text.splitlines()
            last_end = 0
            for table in tables:
                before = "\n".join(lines[last_end : table.start_line]).strip()
                if before:
                    out.append(
                        Chunk(
                            document_id=chunk.document_id,
                            project_id=chunk.project_id,
                            source_type=chunk.source_type,
                            discipline=chunk.discipline,
                            level=chunk.level,
                            parent_id=chunk.parent_id,
                            section_number=chunk.section_number,
                            title=chunk.title,
                            text=before,
                        )
                    )

                table_chunk = Chunk(
                    document_id=chunk.document_id,
                    project_id=chunk.project_id,
                    source_type="table",
                    discipline=chunk.discipline,
                    level=chunk.level + 1,
                    parent_id=chunk.id,
                    section_number=chunk.section_number,
                    title=table.caption or f"Table in {chunk.title}",
                    text=table.markdown,
                    metadata={
                        "rows": table.row_count,
                        "columns": table.column_count,
                    },
                )
                table_chunk.token_count = count_tokens(table_chunk.text)
                table_chunk.refs = extract_cross_references(table_chunk.text)
                out.append(table_chunk)

                last_end = table.end_line

            after = "\n".join(lines[last_end:]).strip()
            if after:
                out.append(
                    Chunk(
                        document_id=chunk.document_id,
                        project_id=chunk.project_id,
                        source_type=chunk.source_type,
                        discipline=chunk.discipline,
                        level=chunk.level,
                        parent_id=chunk.parent_id,
                        section_number=chunk.section_number,
                        title=chunk.title,
                        text=after,
                    )
                )

        return out


# ---------------------------------------------------------------------------
# Drawing chunker
# ---------------------------------------------------------------------------

class DrawingChunker(BaseChunker):
    """Chunk drawing sheets and drawing notes."""

    SHEET_RE = re.compile(
        r"SHEET\s+([A-Z]{1,4}\s*[\-–—]?\s*\d{1,4}(?:\.\d+)?)",
        re.IGNORECASE,
    )
    NOTE_LETTER_RE = re.compile(r"^([A-Z])\.\s+(.+)$")

    def chunk(self) -> List[Chunk]:
        if self.context.document.sheets:
            return self._chunk_from_sheets()
        return self._chunk_from_text()

    def _chunk_from_sheets(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        text = self.context.document.extracted_text or ""
        # Simple heuristic: distribute extracted text evenly across sheets.
        # In a real pipeline we would extract per-page text; this fallback
        # keeps every sheet represented while preserving provenance.
        per_sheet_text = text.strip() if len(self.context.document.sheets) == 1 else ""
        for sheet in self.context.document.sheets:
            chunk = Chunk(
                document_id=self.context.document.id,
                project_id=self.context.document.project_id,
                source_type="drawing",
                discipline=sheet.discipline.value if sheet.discipline else self.context.discipline,
                level=1,
                section_number=sheet.number,
                title=sheet.title,
                text=per_sheet_text or f"Drawing sheet {sheet.number}: {sheet.title}",
                metadata={
                    "revision": sheet.revision,
                    "date": sheet.date,
                    "page_number": sheet.page_number,
                },
            )
            chunk.token_count = count_tokens(chunk.text)
            chunk.refs = extract_cross_references(chunk.text)
            chunks.append(chunk)
        return chunks

    def _chunk_from_text(self) -> List[Chunk]:
        text = self.context.document.extracted_text or ""
        lines = text.splitlines()
        chunks: List[Chunk] = []

        current_sheet_number = ""
        current_sheet_title = ""
        current_letter = ""
        current_lines: List[str] = []

        def flush_note() -> None:
            if not current_lines:
                return
            body = "\n".join(current_lines).strip()
            if not body:
                return
            title = current_sheet_title
            if current_letter:
                note_match = self.NOTE_LETTER_RE.match(current_lines[0].strip())
                if note_match:
                    note_topic = note_match.group(2).strip()
                    title = f"Note {current_letter} — {note_topic}"
                else:
                    title = f"Note {current_letter} — {title}".strip(" —")
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type="drawing",
                    discipline=self.context.discipline,
                    level=2,
                    section_number=current_sheet_number,
                    title=title,
                    text=body,
                )
            )

        for raw_line in lines:
            line = raw_line.strip()
            sheet_match = self.SHEET_RE.search(line)
            if sheet_match:
                flush_note()
                current_sheet_number = sheet_match.group(1).replace(" ", "").upper()
                # Title is the remainder of the line after the sheet number.
                remainder = line[sheet_match.end() :].strip("-–— :")
                current_sheet_title = remainder
                current_letter = ""
                current_lines = [line]
                continue

            note_match = self.NOTE_LETTER_RE.match(line)
            if note_match and current_sheet_number:
                flush_note()
                current_letter = note_match.group(1)
                current_lines = [line]
                continue

            if current_lines:
                current_lines.append(raw_line)

        flush_note()

        if not chunks:
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type="drawing",
                    discipline=self.context.discipline,
                    level=1,
                    title=self.context.document.original_filename,
                    text=text.strip(),
                )
            )

        return self._enrich(chunks)

    def _enrich(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            chunk.token_count = count_tokens(chunk.text)
            chunk.refs = extract_cross_references(chunk.text)
        return chunks


# ---------------------------------------------------------------------------
# RFI chunker
# ---------------------------------------------------------------------------

class RFIChunker(BaseChunker):
    """Chunk RFI logs by individual RFI item."""

    RFI_RE = re.compile(r"^(RFI-\d+):\s*(.+)$", re.IGNORECASE)

    def chunk(self) -> List[Chunk]:
        text = self.context.document.extracted_text or ""
        lines = text.splitlines()
        chunks: List[Chunk] = []

        current_id = ""
        current_title = ""
        current_lines: List[str] = []

        def flush() -> None:
            if not current_lines:
                return
            body = "\n".join(current_lines).strip()
            if not body:
                return
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type="rfi",
                    discipline=self.context.discipline,
                    level=1,
                    section_number=current_id,
                    title=current_title,
                    text=body,
                )
            )

        for raw_line in lines:
            line = raw_line.strip()
            match = self.RFI_RE.match(line)
            if match:
                flush()
                current_id = match.group(1).upper()
                current_title = match.group(2).strip()
                current_lines = [line]
                continue
            if current_lines:
                current_lines.append(raw_line)

        flush()

        if not chunks:
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type="rfi",
                    discipline=self.context.discipline,
                    level=1,
                    title=self.context.document.original_filename,
                    text=text.strip(),
                )
            )

        return self._enrich(chunks)

    def _enrich(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            chunk.token_count = count_tokens(chunk.text)
            chunk.refs = extract_cross_references(chunk.text)
        return chunks


# ---------------------------------------------------------------------------
# Fallback chunker
# ---------------------------------------------------------------------------

class FallbackChunker(BaseChunker):
    """Sliding-window paragraph chunker for unstructured text."""

    def chunk(self) -> List[Chunk]:
        text = self.context.document.extracted_text or ""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: List[Chunk] = []
        current_text = ""
        current_tokens = 0

        for paragraph in paragraphs:
            para_tokens = count_tokens(paragraph)
            if current_tokens and current_tokens + para_tokens > self.max_tokens:
                chunks.append(
                    Chunk(
                        document_id=self.context.document.id,
                        project_id=self.context.document.project_id,
                        source_type=self.context.source_type,
                        discipline=self.context.discipline,
                        level=2,
                        title=self.context.document.original_filename,
                        text=current_text.strip(),
                    )
                )
                # Overlap: keep last N tokens worth of text
                current_text = self._overlap_text(current_text)
                current_tokens = count_tokens(current_text)
                current_text = (current_text + "\n\n" + paragraph).strip()
                current_tokens = count_tokens(current_text)
            else:
                current_text = (current_text + "\n\n" + paragraph).strip()
                current_tokens += para_tokens

        if current_text.strip():
            chunks.append(
                Chunk(
                    document_id=self.context.document.id,
                    project_id=self.context.document.project_id,
                    source_type=self.context.source_type,
                    discipline=self.context.discipline,
                    level=2,
                    title=self.context.document.original_filename,
                    text=current_text.strip(),
                )
            )

        return self._enrich(chunks)

    def _overlap_text(self, text: str) -> str:
        words = text.split()
        overlap_words = int(self.overlap_tokens * 1.3)  # rough word-to-token ratio
        if len(words) <= overlap_words:
            return text
        return " ".join(words[-overlap_words:])

    def _enrich(self, chunks: List[Chunk]) -> List[Chunk]:
        for chunk in chunks:
            chunk.token_count = count_tokens(chunk.text)
            chunk.refs = extract_cross_references(chunk.text)
            chunk.metadata["chunking_strategy"] = "fallback"
        return chunks


# ---------------------------------------------------------------------------
# Public orchestrator
# ---------------------------------------------------------------------------

class HierarchicalChunker:
    """Route a Document to the appropriate type-specific chunker."""

    def __init__(self, max_tokens: int = 512, overlap_tokens: int = 64):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self, document: Document) -> List[Chunk]:
        if not document or not document.extracted_text:
            return []

        source_type = _source_type(document)
        discipline = document.discipline.value if document.discipline else "UNKNOWN"
        context = ChunkerContext(document=document, source_type=source_type, discipline=discipline)

        if _looks_like_spec(document):
            return SpecificationChunker(context, self.max_tokens, self.overlap_tokens).chunk()
        if _looks_like_drawing(document):
            return DrawingChunker(context, self.max_tokens, self.overlap_tokens).chunk()
        if _looks_like_rfi(document):
            return RFIChunker(context, self.max_tokens, self.overlap_tokens).chunk()

        return FallbackChunker(context, self.max_tokens, self.overlap_tokens).chunk()

"""
Tests for the hierarchical chunker.
"""

from pathlib import Path

import pytest

from chunking import HierarchicalChunker
from ingestion.models import Discipline, Document, DocumentType


def _doc_from_file(
    file_name: str,
    doc_type: DocumentType = DocumentType.TXT,
    discipline: Discipline = Discipline.UNKNOWN,
) -> Document:
    path = Path(__file__).parent.parent.parent.parent / "sample_docs" / file_name
    return Document(
        id="test-doc",
        project_id="test-project",
        original_filename=file_name,
        document_type=doc_type,
        discipline=discipline,
        extracted_text=path.read_text(encoding="utf-8", errors="ignore"),
    )


def test_spec_chunker_sections():
    doc = _doc_from_file("MECH_SPEC_HVAC.txt", discipline=Discipline.SPECIFICATION)
    chunks = HierarchicalChunker().chunk(doc)

    assert len(chunks) >= 4
    section_chunks = [c for c in chunks if c.level == 1]
    assert any("23-00-00" in c.section_number for c in section_chunks)

    subsection_chunks = [c for c in chunks if c.level == 2]
    assert any("1.1" in c.section_number for c in subsection_chunks)
    assert any("AIR HANDLING UNITS" in c.title for c in subsection_chunks)


def test_spec_chunker_cross_references():
    doc = _doc_from_file("MECH_SPEC_HVAC.txt", discipline=Discipline.SPECIFICATION)
    chunks = HierarchicalChunker().chunk(doc)

    refs = {ref for c in chunks for ref in c.refs}
    assert any("ASHRAE" in r for r in refs)
    assert any("SMACNA" in r for r in refs)
    assert any("NFPA" in r for r in refs)


def test_drawing_notes_chunker():
    doc = _doc_from_file("ARCH_DRAWING_NOTES.txt", discipline=Discipline.ARCHITECTURAL)
    chunks = HierarchicalChunker().chunk(doc)

    assert len(chunks) >= 4
    assert any(c.section_number == "A-101" for c in chunks)
    assert any("OCCUPANCY AND USE" in c.title for c in chunks)
    assert any("THERMAL AND MOISTURE PROTECTION" in c.title for c in chunks)
    assert any("FIRE RATED ASSEMBLIES" in c.title for c in chunks)


def test_rfi_chunker():
    doc = _doc_from_file("RFI_LOG.txt", discipline=Discipline.OTHER)
    chunks = HierarchicalChunker().chunk(doc)

    assert len(chunks) == 5
    assert all(c.source_type == "rfi" for c in chunks)
    assert all(c.section_number.startswith("RFI-") for c in chunks)


def test_fallback_chunker():
    doc = Document(
        id="fallback-doc",
        project_id="p1",
        original_filename="memo.txt",
        document_type=DocumentType.TXT,
        discipline=Discipline.UNKNOWN,
        extracted_text="\n\n".join(f"Paragraph {i} with some text." for i in range(20)),
    )
    chunks = HierarchicalChunker(max_tokens=20).chunk(doc)

    assert len(chunks) >= 2
    assert all(c.source_type == "unknown" for c in chunks)
    assert all(c.token_count > 0 for c in chunks)


def test_empty_document():
    doc = Document(
        id="empty-doc",
        project_id="p1",
        original_filename="empty.txt",
        document_type=DocumentType.TXT,
        discipline=Discipline.UNKNOWN,
        extracted_text="",
    )
    assert HierarchicalChunker().chunk(doc) == []


def test_chunk_evidence_dict():
    doc = _doc_from_file("FIRE_PROTECTION_SPEC.txt", discipline=Discipline.SPECIFICATION)
    chunks = HierarchicalChunker().chunk(doc)
    assert chunks
    evidence = chunks[0].to_evidence_dict()
    assert evidence["chunk_id"] == chunks[0].id
    assert evidence["document_id"] == doc.id
    assert "text" in evidence
    assert "metadata" in evidence

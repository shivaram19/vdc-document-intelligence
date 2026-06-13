"""
Tests for the hierarchical retriever.
"""

from pathlib import Path

from chunking import HierarchicalChunker, HierarchicalRetriever
from ingestion.models import Discipline, Document


def _load_chunks(file_name: str, discipline: Discipline) -> list:
    path = Path(__file__).parent.parent.parent.parent / "sample_docs" / file_name
    doc = Document(
        id=f"doc-{file_name}",
        project_id="p1",
        original_filename=file_name,
        document_type="txt",
        discipline=discipline,
        extracted_text=path.read_text(encoding="utf-8", errors="ignore"),
    )
    return HierarchicalChunker().chunk(doc)


def test_keyword_search_finds_section():
    chunks = _load_chunks("MECH_SPEC_HVAC.txt", Discipline.SPECIFICATION)
    retriever = HierarchicalRetriever(chunks)
    results = retriever.keyword_search("temperature setpoints", top_k=5)

    assert len(results) > 0
    assert any("setpoint" in r.text.lower() for r in results)


def test_exact_identifier_boost():
    chunks = _load_chunks("ARCH_DRAWING_NOTES.txt", Discipline.ARCHITECTURAL)
    retriever = HierarchicalRetriever(chunks)
    results = retriever.hybrid_search("A-101", top_k=5)

    assert len(results) > 0
    assert any(r.metadata.get("section_number") == "A-101" for r in results)


def test_two_phase_retrieval_returns_leaves_and_parents():
    chunks = _load_chunks("MECH_SPEC_HVAC.txt", Discipline.SPECIFICATION)
    retriever = HierarchicalRetriever(chunks)
    results = retriever.retrieve("air handling units", top_k=10)

    assert len(results) > 0
    leaf_results = [r for r in results if r.metadata.get("level", 0) >= 2]
    assert len(leaf_results) > 0
    # Parent expansion should attach section context.
    assert any(r.metadata.get("parent_text") for r in leaf_results)


def test_retriever_deduplicates():
    chunks = _load_chunks("RFI_LOG.txt", Discipline.OTHER)
    retriever = HierarchicalRetriever(chunks)
    results = retriever.hybrid_search("column spacing", top_k=10)

    ids = [r.chunk_id for r in results]
    assert len(ids) == len(set(ids))


def test_empty_index():
    retriever = HierarchicalRetriever([])
    results = retriever.retrieve("anything", top_k=5)
    assert results == []

"""
Tests for table extraction and table chunking.
"""

from chunking.extractors import TableBlock, extract_text_tables
from chunking.chunker import SpecificationChunker, ChunkerContext
from ingestion.models import Discipline, Document


def test_extract_pipe_table():
    text = """
| System | Size | Valve |
|--------|------|-------|
| Chilled Water | 2" | Ball |
| Heating Hot Water | 3" | Butterfly |
"""
    tables = extract_text_tables(text)
    assert len(tables) == 1
    assert tables[0].row_count == 3  # header + 2 data rows
    assert tables[0].column_count == 3
    assert "Chilled Water" in tables[0].markdown
    assert "| --- |" in tables[0].markdown


def test_extract_whitespace_table():
    text = """Valve Schedule
System          Size            Type
Chilled Water   2" and smaller  Ball valve
Heating Hot     3" and larger   Butterfly valve
"""
    tables = extract_text_tables(text)
    assert len(tables) == 1
    assert tables[0].row_count >= 2
    assert tables[0].column_count == 3
    assert "Ball valve" in tables[0].markdown


def test_table_caption_from_preceding_line():
    text = """Valve Schedule
Chilled Water   2"      Ball
Heating Hot     3"      Butterfly
"""
    tables = extract_text_tables(text)
    assert len(tables) == 1
    assert tables[0].caption == "Valve Schedule"


def test_spec_chunker_extracts_table_chunks():
    text = """SECTION 23 05 23 - GENERAL-DUTY VALVES

1.1 VALVE SCHEDULE
System          Size            Type
Chilled Water   2" and smaller  Ball valve
Heating Hot     3" and larger   Butterfly valve

1.2 GENERAL REQUIREMENTS
All valves shall be rated for the service.
"""
    doc = Document(
        id="t",
        project_id="p",
        original_filename="valves.txt",
        document_type="txt",
        discipline=Discipline.SPECIFICATION,
        extracted_text=text,
    )
    chunks = SpecificationChunker(
        ChunkerContext(document=doc, source_type="spec", discipline="SPEC"),
        max_tokens=512,
    ).chunk()

    table_chunks = [c for c in chunks if c.source_type == "table"]
    assert len(table_chunks) == 1
    assert table_chunks[0].parent_id is not None
    assert "Ball valve" in table_chunks[0].text

    text_chunks = [c for c in chunks if c.source_type == "spec" and c.level == 2]
    assert any("GENERAL REQUIREMENTS" in c.title for c in text_chunks)

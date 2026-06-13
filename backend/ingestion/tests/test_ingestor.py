"""
Tests for the document ingestion orchestrator.
"""

import tempfile
from pathlib import Path

import pytest

from ingestion.ingestor import DocumentIngestor
from ingestion.store import ProjectStore


@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield ProjectStore(db_path=str(db_path))


@pytest.fixture
def ingestor(temp_store):
    return DocumentIngestor(store=temp_store)


@pytest.fixture
def sample_txt_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Division 23 - Heating, Ventilating, and Air Conditioning\n")
        f.write("SECTION 23 00 00 - HVAC GENERAL REQUIREMENTS\n")
        f.write("Specifier notes: This section applies to all HVAC work.\n")
        path = f.name
    yield path
    Path(path).unlink()


def test_create_project(ingestor):
    project = ingestor.create_project(
        name="Test Project",
        client_name="Test Client",
        project_number="TEST-001",
        workspace_base=tempfile.mkdtemp(),
    )
    assert project.name == "Test Project"
    assert project.client_name == "Test Client"
    assert Path(project.workspace_path).exists()


def test_ingest_txt_document(ingestor, sample_txt_file):
    project = ingestor.create_project(
        name="TXT Test",
        workspace_base=tempfile.mkdtemp(),
    )
    doc = ingestor.ingest(project.id, sample_txt_file)

    assert doc.project_id == project.id
    assert doc.original_filename.endswith(".txt")
    assert doc.processing_status == "completed"
    assert doc.discipline.value == "SPEC"
    assert "HVAC" in doc.extracted_text


def test_ingest_nonexistent_file(ingestor):
    project = ingestor.create_project(
        name="Missing File Test",
        workspace_base=tempfile.mkdtemp(),
    )
    with pytest.raises(FileNotFoundError):
        ingestor.ingest(project.id, "/path/that/does/not/exist.pdf")


def test_list_documents(ingestor, sample_txt_file):
    project = ingestor.create_project(
        name="List Test",
        workspace_base=tempfile.mkdtemp(),
    )
    ingestor.ingest(project.id, sample_txt_file)
    docs = ingestor.get_project_documents(project.id)
    assert len(docs) == 1
    assert docs[0].processing_status == "completed"

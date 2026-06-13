"""
Document ingestion orchestrator for Medha.

Coordinates classification, metadata extraction, storage, and sheet parsing
for construction documents uploaded to a project workspace.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .classifier import classify_document, classify_document_type, classify_sheet
from .drawing_index import DrawingIndexParser
from .extractor import (
    compute_file_hash,
    extract_date,
    extract_pdf_metadata,
    extract_pdf_text_samples,
    extract_revision,
    extract_sheet_number_from_text,
    extract_title_from_filename,
)
from .models import Document, DocumentType, Project, Sheet
from .store import ProjectStore


class DocumentIngestor:
    """Ingest documents into a Medha project workspace."""

    def __init__(self, store: Optional[ProjectStore] = None):
        self.store = store or ProjectStore()

    def create_project(
        self,
        name: str,
        description: str = "",
        client_name: str = "",
        project_number: str = "",
        workspace_base: str = "./data/projects",
        settings: Optional[Dict[str, Any]] = None,
        standardization_rules: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project workspace."""
        return self.store.create_project(
            name=name,
            description=description,
            client_name=client_name,
            project_number=project_number,
            workspace_base=workspace_base,
            settings=settings,
            standardization_rules=standardization_rules,
        )

    def ingest(
        self,
        project_id: str,
        file_path: str,
        title: str = "",
        extract_sheets: bool = True,
        extract_text: bool = True,
    ) -> Document:
        """
        Ingest a single document into a project workspace.

        Args:
            project_id: Target project ID.
            file_path: Path to the file to ingest.
            title: Optional human-readable title.
            extract_sheets: Whether to parse sheets (for PDFs).
            extract_text: Whether to extract text samples.

        Returns:
            Persisted Document with metadata and sheets.
        """
        project = self.store.get_project(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        doc_type = classify_document_type(source.name)

        # Copy file into project workspace
        dest_dir = project.document_dir() / doc_type.value
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / source.name
        shutil.copy2(source, dest_path)

        # Build document record
        document = Document(
            project_id=project_id,
            original_filename=source.name,
            document_type=doc_type,
            storage_path=str(dest_path),
            file_hash=compute_file_hash(dest_path),
            file_size_bytes=source.stat().st_size,
            metadata={
                "title": title or extract_title_from_filename(source.name),
                "source_path": str(source),
            },
            processing_status="processing",
        )

        try:
            if doc_type == DocumentType.PDF:
                self._process_pdf(document, extract_sheets, extract_text)
            elif doc_type == DocumentType.TXT:
                content = Path(document.storage_path).read_text(encoding="utf-8", errors="ignore")
                document.extracted_text = content[:10000]
                document.discipline = classify_document(
                    filename=document.original_filename,
                    title=document.metadata.get("title", ""),
                    content_preview=content,
                )
            else:
                # Non-PDF documents: classify by filename/title only
                document.discipline = classify_document(
                    filename=document.original_filename,
                    title=document.metadata.get("title", ""),
                )

            document.processing_status = "completed"
        except Exception as exc:
            document.processing_status = "failed"
            document.processing_error = str(exc)

        self.store.save_document(document)
        return document

    def _process_pdf(
        self,
        document: Document,
        extract_sheets: bool,
        extract_text: bool,
    ) -> None:
        """Process a PDF document: metadata, text, sheets."""
        path = Path(document.storage_path)
        pdf_meta = extract_pdf_metadata(path)
        document.metadata.update({k: v for k, v in pdf_meta.items() if v})

        text_samples = extract_pdf_text_samples(path, max_pages=5)
        combined_text = "\n".join(text for _, text in text_samples)

        if extract_text:
            document.extracted_text = combined_text[:10000]

        # Classify document discipline using filename, title, and text preview
        document.discipline = classify_document(
            filename=document.original_filename,
            title=document.metadata.get("title", ""),
            content_preview=combined_text,
        )

        if extract_sheets:
            parser = DrawingIndexParser()
            index_sheets, per_page_sheets = parser.parse_pdf(
                Path(document.storage_path), max_index_pages=5
            )

            sheets: List[Sheet] = []
            if index_sheets:
                sheets = index_sheets
            elif per_page_sheets:
                sheets = per_page_sheets
            else:
                # Fallback: treat the entire PDF as a single document sheet.
                # Avoid guessing a sheet number from spec body text; that is
                # unreliable and produces false sheet records.
                sheets.append(
                    Sheet(
                        number="DOC",
                        title=document.metadata.get("title", "") or document.original_filename,
                        revision=extract_revision(combined_text),
                        date=extract_date(combined_text),
                        page_number=0,
                    )
                )

            # Enrich sheet metadata and ensure discipline classification
            for sheet in sheets:
                sheet.discipline = classify_sheet(
                    sheet_number=sheet.number,
                    title=sheet.title,
                    filename=document.original_filename,
                )
                if not sheet.revision:
                    sheet.revision = extract_revision(combined_text) or ""
                if not sheet.date:
                    sheet.date = extract_date(combined_text)

            document.sheets = sheets

    def get_project_documents(self, project_id: str) -> List[Document]:
        """Get all documents for a project."""
        return self.store.list_documents(project_id)

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self.store.get_project(project_id)

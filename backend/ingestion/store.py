"""
SQLite-backed store for Medha projects and ingested documents.
"""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Discipline, Document, DocumentType, Project, Sheet


class ProjectStore:
    """Persistent store for projects, documents, and sheets."""

    def __init__(self, db_path: str = "./medha_projects.db"):
        self.db_path = db_path
        self._init_db()

    def _connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    client_name TEXT,
                    project_number TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    workspace_path TEXT,
                    settings TEXT,
                    standardization_rules TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    document_type TEXT,
                    discipline TEXT,
                    storage_path TEXT,
                    file_hash TEXT,
                    file_size_bytes INTEGER,
                    uploaded_at TEXT,
                    sheets TEXT,
                    metadata TEXT,
                    extracted_text TEXT,
                    processing_status TEXT,
                    processing_error TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
                """
            )
            conn.commit()

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
        """Create a new project workspace and persist it."""
        project = Project(
            name=name,
            description=description,
            client_name=client_name,
            project_number=project_number,
            settings=settings or {},
            standardization_rules=standardization_rules or {},
        )
        workspace = Path(workspace_base) / project.id
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "documents").mkdir(exist_ok=True)
        (workspace / "sheets").mkdir(exist_ok=True)
        project.workspace_path = str(workspace)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (
                    id, name, description, client_name, project_number,
                    created_at, updated_at, workspace_path, settings, standardization_rules
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.id,
                    project.name,
                    project.description,
                    project.client_name,
                    project.project_number,
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                    project.workspace_path,
                    json.dumps(project.settings),
                    json.dumps(project.standardization_rules),
                ),
            )
            conn.commit()
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Fetch a project by ID."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_project(row)

    def list_projects(self) -> List[Project]:
        """List all projects."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY created_at DESC"
            ).fetchall()
            return [self._row_to_project(row) for row in rows]

    def save_document(self, document: Document) -> None:
        """Persist a document and its sheets."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO documents (
                    id, project_id, original_filename, document_type, discipline,
                    storage_path, file_hash, file_size_bytes, uploaded_at,
                    sheets, metadata, extracted_text, processing_status, processing_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.project_id,
                    document.original_filename,
                    document.document_type.value,
                    document.discipline.value,
                    document.storage_path,
                    document.file_hash,
                    document.file_size_bytes,
                    document.uploaded_at.isoformat(),
                    json.dumps([asdict(s) for s in document.sheets]),
                    json.dumps(document.metadata),
                    document.extracted_text,
                    document.processing_status,
                    document.processing_error,
                ),
            )
            conn.execute(
                "UPDATE projects SET updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), document.project_id),
            )
            conn.commit()

    def get_document(self, document_id: str) -> Optional[Document]:
        """Fetch a document by ID."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_document(row)

    def list_documents(self, project_id: str) -> List[Document]:
        """List all documents for a project."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM documents WHERE project_id = ? ORDER BY uploaded_at DESC",
                (project_id,),
            ).fetchall()
            return [self._row_to_document(row) for row in rows]

    def _row_to_project(self, row: sqlite3.Row) -> Project:
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            client_name=row["client_name"],
            project_number=row["project_number"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            workspace_path=row["workspace_path"],
            settings=json.loads(row["settings"] or "{}"),
            standardization_rules=json.loads(row["standardization_rules"] or "{}"),
        )

    def _row_to_document(self, row: sqlite3.Row) -> Document:
        sheets = [
            Sheet(**sheet_dict)
            for sheet_dict in json.loads(row["sheets"] or "[]")
        ]
        return Document(
            id=row["id"],
            project_id=row["project_id"],
            original_filename=row["original_filename"],
            document_type=DocumentType(row["document_type"]) if row["document_type"] else DocumentType.UNKNOWN,
            discipline=Discipline(row["discipline"]) if row["discipline"] else Discipline.UNKNOWN,
            storage_path=row["storage_path"],
            file_hash=row["file_hash"],
            file_size_bytes=row["file_size_bytes"],
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
            sheets=sheets,
            metadata=json.loads(row["metadata"] or "{}"),
            extracted_text=row["extracted_text"],
            processing_status=row["processing_status"],
            processing_error=row["processing_error"],
        )

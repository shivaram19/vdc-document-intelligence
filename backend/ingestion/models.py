"""
Data models for Medha document ingestion.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class DocumentType(str, Enum):
    PDF = "pdf"
    DWG = "dwg"
    DXF = "dxf"
    RVT = "rvt"
    IFC = "ifc"
    DOCX = "docx"
    XLSX = "xlsx"
    TXT = "txt"
    UNKNOWN = "unknown"


class Discipline(str, Enum):
    ARCHITECTURAL = "A"
    STRUCTURAL = "S"
    MECHANICAL = "M"
    ELECTRICAL = "E"
    PLUMBING = "P"
    FIRE_PROTECTION = "FP"
    CIVIL = "C"
    LANDSCAPE = "L"
    INTERIOR = "I"
    GENERAL = "G"
    SPECIFICATION = "SPEC"
    CONTRACT = "CONTRACT"
    REPORT = "REPORT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


@dataclass
class Sheet:
    """A single sheet parsed from a drawing set."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    number: str = ""
    title: str = ""
    discipline: Discipline = Discipline.UNKNOWN
    revision: str = ""
    date: Optional[str] = None
    page_number: int = 0
    bounding_box: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.number:
            self.number = self.id[:8]


@dataclass
class Document:
    """A document uploaded to a Medha project workspace."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    original_filename: str = ""
    document_type: DocumentType = DocumentType.UNKNOWN
    discipline: Discipline = Discipline.UNKNOWN
    storage_path: str = ""
    file_hash: str = ""
    file_size_bytes: int = 0
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    sheets: List[Sheet] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_text: str = ""
    processing_status: str = "pending"  # pending, processing, completed, failed
    processing_error: Optional[str] = None


@dataclass
class Project:
    """A Medha project workspace."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    client_name: str = ""
    project_number: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    workspace_path: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)
    standardization_rules: Dict[str, Any] = field(default_factory=dict)

    def document_dir(self) -> Path:
        return Path(self.workspace_path) / "documents"

    def sheet_dir(self) -> Path:
        return Path(self.workspace_path) / "sheets"

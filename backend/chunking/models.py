"""
Data model for Medha document chunks.

Chunks are the atomic units of retrieval and contradiction detection.
They are intentionally lightweight and map directly to the Evidence type
used by the cognitive architecture (src/cognitive/types.py).
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Chunk:
    """
    A retrievable unit of a construction document.

    Fields mirror what System3RetrievalController needs to build Evidence:
    - id / document_id / project_id for provenance
    - source_type for strategy selection (spec, drawing, code, rfi, contract)
    - discipline for filtering by trade
    - level + parent_id for hierarchical retrieval
    - section_number + title for human-readable citations
    - refs for cross-document / cross-reference graph edges
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    project_id: str = ""
    source_type: str = "unknown"  # spec, drawing, code, rfi, contract, table
    discipline: str = ""
    level: int = 2
    parent_id: Optional[str] = None
    section_number: str = ""
    title: str = ""
    text: str = ""
    refs: List[str] = field(default_factory=list)
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_evidence_dict(self) -> Dict[str, Any]:
        """Convert to a dict compatible with Evidence construction."""
        return {
            "chunk_id": self.id,
            "document_id": self.document_id,
            "text": self.text,
            "source_type": self.source_type,
            "relevance_score": 0.0,
            "retrieval_method": "vector",
            "metadata": {
                "project_id": self.project_id,
                "discipline": self.discipline,
                "level": self.level,
                "parent_id": self.parent_id,
                "section_number": self.section_number,
                "title": self.title,
                "refs": self.refs,
                "token_count": self.token_count,
                **self.metadata,
            },
        }

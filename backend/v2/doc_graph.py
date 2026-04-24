"""
Document Graph Engine — Phase 1 Core Module

Builds a navigable graph of construction documents where sheets reference
sheets, details reference sheets, tags map to schedules, and specs link to
drawings. Enables the RAG system to "follow references" like a human
coordinator flipping through a drawing set.

Architecture:
    Documents → Text Extraction → Reference Extraction → Graph Building
                                                      → Link Resolution
                                                      → Broken Link Detection
                                                      → RAG Context Expansion
"""

import json
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from .reference_patterns import ReferenceExtractor, ReferenceMatch, parse_drawing_index
from .drawing_index import DrawingIndex, DrawingIndexParser


# =============================================================================
# GRAPH DATA MODEL
# =============================================================================

@dataclass
class GraphNode:
    """A node in the construction document graph."""
    id: str
    node_type: str  # 'sheet', 'detail', 'spec_section', 'tag', 'schedule', 'note', 'revision', 'document'
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    source_doc_id: Optional[str] = None
    page_num: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.node_type,
            "label": self.label,
            "properties": self.properties,
            "source_doc_id": self.source_doc_id,
            "page_num": self.page_num,
            "bbox": self.bbox,
        }


@dataclass
class GraphEdge:
    """A directed edge in the document graph."""
    id: str
    source_id: str
    target_id: str
    relation: str  # 'REFERENCES', 'CONTAINS', 'SCHEDULED_ON', 'SPECIFIED_IN', 'REVISION_OF', 'CONTAINS_TAG'
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    resolved: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source_id,
            "target": self.target_id,
            "relation": self.relation,
            "properties": self.properties,
            "confidence": self.confidence,
            "resolved": self.resolved,
        }


@dataclass
class BrokenLink:
    """A reference that could not be resolved."""
    source_id: str
    target_type: str
    target_id: str
    target_sheet: Optional[str]
    context: str
    severity: str = "warning"  # 'warning' or 'error'
    suggested_fix: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_sheet": self.target_sheet,
            "context": self.context,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }


# =============================================================================
# DOCUMENT GRAPH
# =============================================================================

class DocumentGraph:
    """
    In-memory document graph for construction drawing sets.

    Can be serialized to JSON for persistence or exported to Neo4j Cypher.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or str(uuid.uuid4())
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)  # source_id -> [edge_ids]
        self.drawing_index: Optional[DrawingIndex] = None
        self._extractor: Optional[ReferenceExtractor] = None
        self.broken_links: List[BrokenLink] = []

    # -------------------------------------------------------------------------
    # Node / Edge Management
    # -------------------------------------------------------------------------

    def add_node(self, node: GraphNode) -> GraphNode:
        self.nodes[node.id] = node
        return node

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        self.edges[edge.id] = edge
        self.adjacency[edge.source_id].append(edge.id)
        return edge

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        return [self.edges[eid] for eid in self.adjacency.get(node_id, [])]

    def get_edges_to(self, node_id: str) -> List[GraphEdge]:
        return [e for e in self.edges.values() if e.target_id == node_id]

    def get_neighbors(self, node_id: str, relation: Optional[str] = None) -> List[GraphNode]:
        """Get all nodes reachable from node_id via outgoing edges."""
        edges = self.get_edges_from(node_id)
        if relation:
            edges = [e for e in edges if e.relation == relation]
        return [self.nodes[e.target_id] for e in edges if e.target_id in self.nodes]

    # -------------------------------------------------------------------------
    # Graph Construction
    # -------------------------------------------------------------------------

    def set_drawing_index(self, index: DrawingIndex):
        """Set the canonical drawing index. Seeds the graph with all valid sheets."""
        self.drawing_index = index
        self._extractor = ReferenceExtractor(known_sheets=[s.number for s in index.sheets])

        # Create Sheet nodes for every entry in the drawing index
        for sheet in index.sheets:
            node_id = f"sheet:{sheet.normalized}"
            if node_id not in self.nodes:
                self.add_node(GraphNode(
                    id=node_id,
                    node_type="sheet",
                    label=f"{sheet.number} — {sheet.title}",
                    properties={
                        "number": sheet.number,
                        "title": sheet.title,
                        "discipline": sheet.discipline,
                    }
                ))

    def ingest_document(self, doc_id: str, text: str, page_num: int = 0,
                        doc_type: str = "drawing", filename: str = ""):
        """
        Ingest a single document/page, extract references, add to graph.

        Args:
            doc_id: Unique document identifier
            text: Extracted text content
            page_num: Page number within the document
            doc_type: 'drawing', 'spec', 'schedule', 'general'
            filename: Original filename for context
        """
        if self._extractor is None:
            self._extractor = ReferenceExtractor()

        # Determine the source sheet for this document
        source_sheet = self._infer_source_sheet(doc_id, filename, text)
        source_node_id = f"sheet:{source_sheet}" if source_sheet else f"doc:{doc_id}:p{page_num}"

        # Ensure source node exists
        if source_node_id not in self.nodes:
            self.add_node(GraphNode(
                id=source_node_id,
                node_type="sheet" if source_sheet else "document",
                label=source_sheet or f"{filename} p.{page_num}",
                properties={"doc_id": doc_id, "page": page_num, "filename": filename},
                source_doc_id=doc_id,
                page_num=page_num,
            ))

        # Extract all references
        refs = self._extractor.extract_all(text, page_num)

        for ref in refs:
            self._process_reference(source_node_id, ref, text)

    def _infer_source_sheet(self, doc_id: str, filename: str, text: str) -> Optional[str]:
        """Try to determine what sheet number this document/page represents."""
        # Try filename first
        if filename:
            import re
            m = re.search(r'([A-Z]{1,3}[\s\-]?\d{2,4})', filename.upper())
            if m:
                return m.group(1).replace(" ", "-")

        # Try first few lines of text for title block
        lines = text.splitlines()[:15]
        for line in lines:
            line = line.strip().upper()
            if self.drawing_index:
                for sheet in self.drawing_index.sheets:
                    if sheet.normalized in line.replace(" ", "-"):
                        return sheet.normalized

        return None

    def _process_reference(self, source_id: str, ref: ReferenceMatch, full_text: str):
        """Add a reference match to the graph as a node + edge."""

        # Create target node if it doesn't exist
        if ref.ref_type == "detail" and ref.target_sheet:
            target_id = f"detail:{ref.target_id}@{ref.target_sheet}"
        elif ref.ref_type == "sheet":
            target_id = f"sheet:{ref.target_id}"
        elif ref.ref_type == "spec_section":
            target_id = f"spec:{ref.target_id}"
        elif ref.ref_type == "tag":
            target_id = f"tag:{ref.target_id}"
        elif ref.ref_type == "schedule":
            target_id = f"schedule:{ref.target_id}"
        elif ref.ref_type == "elevation":
            target_id = f"elevation:{ref.target_id}"
        elif ref.ref_type == "section":
            target_id = f"section:{ref.target_id}"
        elif ref.ref_type == "revision":
            target_id = f"revision:{ref.target_id}"
        else:
            target_id = f"{ref.ref_type}:{ref.target_id}"

        # Add target node (may be unresolved)
        if target_id not in self.nodes:
            self.add_node(GraphNode(
                id=target_id,
                node_type=ref.ref_type,
                label=ref.target_id,
                properties={
                    "target_sheet": ref.target_sheet,
                    "context": ref.source_context,
                }
            ))

        # Determine if this is resolved
        resolved = self._is_resolved(ref)

        # Add edge
        edge = GraphEdge(
            id=f"e:{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            target_id=target_id,
            relation="REFERENCES",
            properties={
                "context": ref.source_context,
                "extracted_from": full_text[:200],
            },
            confidence=ref.confidence,
            resolved=resolved,
        )
        self.add_edge(edge)

        # If unresolved, record broken link
        if not resolved:
            self._record_broken_link(source_id, ref)

    def _is_resolved(self, ref: ReferenceMatch) -> bool:
        """Check if a reference can be resolved against the drawing index."""
        if ref.ref_type == "sheet":
            return self.drawing_index is not None and self.drawing_index.is_valid_sheet(ref.target_id)

        if ref.ref_type == "detail" and ref.target_sheet:
            return self.drawing_index is not None and self.drawing_index.is_valid_sheet(ref.target_sheet)

        # Spec sections, tags, schedules — we can't validate without more data
        # Mark as tentatively resolved if confidence is high
        return ref.confidence >= 0.85

    def _record_broken_link(self, source_id: str, ref: ReferenceMatch):
        """Record a broken reference for RFI generation."""
        suggestion = None
        if ref.ref_type == "sheet" and self.drawing_index:
            # Try to suggest a similar sheet
            similar = self._find_similar_sheet(ref.target_id)
            if similar:
                suggestion = f"Did you mean {similar}?"

        self.broken_links.append(BrokenLink(
            source_id=source_id,
            target_type=ref.ref_type,
            target_id=ref.target_id,
            target_sheet=ref.target_sheet,
            context=ref.source_context,
            severity="error" if ref.ref_type == "sheet" else "warning",
            suggested_fix=suggestion,
        ))

    def _find_similar_sheet(self, sheet_num: str) -> Optional[str]:
        """Find a similar sheet number (simple prefix match)."""
        if not self.drawing_index:
            return None
        norm = sheet_num.upper().replace(" ", "-")
        prefix = re.match(r'^([A-Z]+)', norm)
        if prefix:
            disc = prefix.group(1)
            candidates = [s.number for s in self.drawing_index.sheets if s.discipline == disc]
            if candidates:
                return candidates[0]  # Return first matching discipline
        return None

    def _resolve_details(self):
        """Second-pass resolution: try to match unresolved detail nodes to sheets."""
        for node in list(self.nodes.values()):
            if node.node_type != "detail":
                continue
            target_sheet = node.properties.get("target_sheet")
            if target_sheet and self.drawing_index:
                if self.drawing_index.is_valid_sheet(target_sheet):
                    # Update edges to mark as resolved
                    for edge in self.get_edges_to(node.id):
                        edge.resolved = True

    # -------------------------------------------------------------------------
    # Graph Traversal for RAG
    # -------------------------------------------------------------------------

    def expand_context(self, node_id: str, depth: int = 2,
                       max_nodes: int = 20,
                       relation_filter: Optional[List[str]] = None) -> List[GraphNode]:
        """
        BFS expansion from a starting node — follows references like a human
        coordinator flipping through drawings.

        Args:
            node_id: Starting node (typically a sheet node)
            depth: How many hops to follow (default 2 = sheet → detail → spec)
            max_nodes: Hard limit to prevent context explosion
            relation_filter: Only follow these relation types

        Returns:
            List of GraphNodes to include in RAG context
        """
        visited = {node_id}
        queue = [(node_id, 0)]
        result = []

        while queue and len(result) < max_nodes:
            current_id, current_depth = queue.pop(0)

            node = self.nodes.get(current_id)
            if node and node.id != node_id:
                result.append(node)

            if current_depth >= depth:
                continue

            for edge in self.get_edges_from(current_id):
                if relation_filter and edge.relation not in relation_filter:
                    continue
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, current_depth + 1))

        return result

    def find_paths(self, source_id: str, target_id: str, max_depth: int = 4) -> List[List[str]]:
        """Find all paths from source to target node (for reasoning chains)."""
        paths = []
        visited = {source_id}

        def dfs(current: str, path: List[str]):
            if current == target_id:
                paths.append(path.copy())
                return
            if len(path) >= max_depth:
                return
            for edge in self.get_edges_from(current):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    path.append(edge.target_id)
                    dfs(edge.target_id, path)
                    path.pop()
                    visited.remove(edge.target_id)

        dfs(source_id, [source_id])
        return paths

    # -------------------------------------------------------------------------
    # Analysis
    # -------------------------------------------------------------------------

    def get_broken_links(self) -> List[BrokenLink]:
        """Return all unresolved references — prime source of RFIs."""
        return self.broken_links

    def get_orphaned_nodes(self) -> List[GraphNode]:
        """Nodes with no incoming or outgoing edges."""
        has_edges = set()
        for edge in self.edges.values():
            has_edges.add(edge.source_id)
            has_edges.add(edge.target_id)
        return [n for n in self.nodes.values() if n.id not in has_edges]

    def get_central_nodes(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Nodes with highest out-degree (most referenced-from)."""
        counts = defaultdict(int)
        for edge in self.edges.values():
            counts[edge.source_id] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_hub_nodes(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Nodes with highest in-degree (most referenced-to)."""
        counts = defaultdict(int)
        for edge in self.edges.values():
            counts[edge.target_id] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "created_at": datetime.utcnow().isoformat(),
            "stats": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "broken_links": len(self.broken_links),
                "orphaned_nodes": len(self.get_orphaned_nodes()),
            },
            "drawing_index": {
                "project_name": self.drawing_index.project_name if self.drawing_index else None,
                "total_sheets": self.drawing_index.total_sheets if self.drawing_index else 0,
                "disciplines": self.drawing_index.discipline_list if self.drawing_index else [],
            },
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges.values()],
            "broken_links": [b.to_dict() for b in self.broken_links],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save(self, path: str):
        Path(path).write_text(self.to_json())

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentGraph":
        graph = cls(project_id=data.get("project_id"))
        for n in data.get("nodes", []):
            graph.add_node(GraphNode(
                id=n["id"],
                node_type=n["type"],
                label=n["label"],
                properties=n.get("properties", {}),
                source_doc_id=n.get("source_doc_id"),
                page_num=n.get("page_num"),
                bbox=n.get("bbox"),
            ))
        for e in data.get("edges", []):
            graph.add_edge(GraphEdge(
                id=e["id"],
                source_id=e["source"],
                target_id=e["target"],
                relation=e["relation"],
                properties=e.get("properties", {}),
                confidence=e.get("confidence", 1.0),
                resolved=e.get("resolved", True),
            ))
        return graph

    @classmethod
    def load(cls, path: str) -> "DocumentGraph":
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    # -------------------------------------------------------------------------
    # Neo4j Export
    # -------------------------------------------------------------------------

    def to_cypher(self) -> str:
        """Export graph as Neo4j Cypher CREATE statements."""
        lines = []
        # Nodes
        for node in self.nodes.values():
            props = json.dumps(node.properties)
            lines.append(
                f"CREATE (:{node.node_type.capitalize()} "
                f"{{id: '{node.id}', label: '{node.label}', properties: {props}}})"
            )
        # Edges
        for edge in self.edges.values():
            lines.append(
                f"MATCH (a {{id: '{edge.source_id}'}}), (b {{id: '{edge.target_id}'}}) "
                f"CREATE (a)-[:{edge.relation} "
                f"{{confidence: {edge.confidence}, resolved: {str(edge.resolved).lower()}}}]->(b)"
            )
        return "\n".join(lines)


# =============================================================================
# HIGH-LEVEL BUILDER
# =============================================================================

def build_graph_from_documents(documents: List[dict],
                                drawing_index_text: Optional[str] = None,
                                project_id: Optional[str] = None) -> DocumentGraph:
    """
    High-level builder: create a complete document graph from a set of documents.

    Args:
        documents: List of dicts with keys: id, text, page_num, type, filename
        drawing_index_text: Optional text of the drawing index sheet
        project_id: Optional project identifier

    Returns:
        Populated DocumentGraph
    """
    graph = DocumentGraph(project_id=project_id)

    # Step 1: Parse drawing index if provided
    if drawing_index_text:
        parser = DrawingIndexParser()
        index = parser.parse(drawing_index_text)
        graph.set_drawing_index(index)

    # Step 2: Ingest all documents
    for doc in documents:
        graph.ingest_document(
            doc_id=doc["id"],
            text=doc.get("text", ""),
            page_num=doc.get("page_num", 0),
            doc_type=doc.get("type", "drawing"),
            filename=doc.get("filename", ""),
        )

    # Step 3: Resolve pass — try to match unresolved detail nodes to sheets
    graph._resolve_details()

    return graph


def build_graph_from_pdf_set(pdf_paths: List[str],
                              drawing_index_path: Optional[str] = None,
                              project_id: Optional[str] = None) -> DocumentGraph:
    """
    Build graph directly from a set of PDF files.
    """
    documents = []

    for path in pdf_paths:
        path = Path(path)
        if not path.exists():
            continue

        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        documents.append({
                            "id": f"{path.stem}_p{i}",
                            "text": text,
                            "page_num": i,
                            "type": "drawing",
                            "filename": path.name,
                        })
        except ImportError:
            try:
                import fitz
                doc = fitz.open(path)
                for i in range(len(doc)):
                    text = doc[i].get_text()
                    if text.strip():
                        documents.append({
                            "id": f"{path.stem}_p{i}",
                            "text": text,
                            "page_num": i,
                            "type": "drawing",
                            "filename": path.name,
                        })
            except ImportError:
                continue

    index_text = None
    if drawing_index_path:
        try:
            import pdfplumber
            with pdfplumber.open(drawing_index_path) as pdf:
                index_text = pdf.pages[0].extract_text() or ""
        except Exception:
            pass

    return build_graph_from_documents(documents, index_text, project_id)

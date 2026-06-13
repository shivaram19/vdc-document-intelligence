"""
Medha document chunking package.

Produces hierarchical, retrievable chunks from ingested documents per
ADR-011: Document-Type-Aware Hierarchical Chunking.
"""

from .chunker import HierarchicalChunker
from .extractors import count_tokens, extract_cross_references
from .models import Chunk

__all__ = [
    "Chunk",
    "HierarchicalChunker",
    "count_tokens",
    "extract_cross_references",
]

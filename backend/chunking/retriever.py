"""
Hierarchical retriever for Medha chunks.

Implements the two-phase coarse-to-fine retrieval strategy from ADR-011
and TASK-DFS-002.  It is designed to plug into System3RetrievalController
(src/cognitive/system3_retrieval.py) as a keyword/vector/graph search source.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from chunking.extractors import count_tokens
from chunking.models import Chunk

try:
    from src.cognitive.types import Evidence
except Exception:
    Evidence = None  # type: ignore


@dataclass
class SearchResult:
    """Internal retrieval result before conversion to Evidence."""

    chunk: Chunk
    score: float
    parent_text: str = ""


class HierarchicalRetriever:
    """
    Two-phase hierarchical retrieval over chunked construction documents.

    Phase 1 (coarse): retrieve L0/L1 chunks (divisions, sections, sheets).
    Phase 2 (fine):  retrieve L2/L3 leaf chunks under the coarse parents.
    Final ranking merges both phases and expands leaf hits with parent text.
    """

    def __init__(
        self,
        chunks: List[Chunk],
        vector_search: Optional[Callable[[str, int], List[Chunk]]] = None,
    ):
        self.chunks = chunks
        self.vector_search = vector_search
        self._chunk_by_id: Dict[str, Chunk] = {c.id: c for c in chunks}
        self._index: Dict[str, Dict[str, int]] = {}
        self._build_index()

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def _build_index(self) -> None:
        for chunk in self.chunks:
            text = f"{chunk.title} {chunk.text} {chunk.section_number}"
            for token in self._tokenize(text):
                self._index.setdefault(token, {})
                self._index[token][chunk.id] = self._index[token].get(chunk.id, 0) + 1

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        lowered = re.sub(r"[^\w\s\-]", " ", text.lower())
        return [t.strip("-") for t in lowered.split() if t.strip("-")]

    # ------------------------------------------------------------------
    # Public search interfaces
    # ------------------------------------------------------------------

    def keyword_search(self, query: str, top_k: int = 5) -> List[Evidence]:
        """Keyword search over all chunks."""
        results = self._search(query, source="keyword")
        return self._to_evidence_list(results, top_k)

    def vector_search(self, query: str, top_k: int = 5) -> List[Evidence]:
        """
        Vector search fallback.

        If an external vector search callable is provided, it is used.
        Otherwise, keyword search is used as a deterministic stand-in until
        embeddings are integrated.
        """
        if self.vector_search is not None:
            chunks = self.vector_search(query, top_k)
            results = [SearchResult(chunk=c, score=1.0) for c in chunks]
            return self._to_evidence_list(results, top_k)
        return self.keyword_search(query, top_k)

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Evidence]:
        """
        Merge keyword results with exact-identifier boosts.

        When vector search is unavailable, hybrid reduces to keyword + exact.
        """
        keyword_results = self._search(query, source="keyword")
        exact_results = self._exact_identifier_search(query)
        merged = self._merge_results(keyword_results + exact_results)
        return self._to_evidence_list(merged, top_k)

    def retrieve(
        self,
        query: str,
        query_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Evidence]:
        """
        Two-phase hierarchical retrieval.

        1. Coarse: find L0/L1 parents.
        2. Fine: find L2/L3 leaves under those parents + leaves with no parent.
        3. Expand fine results with parent text and rerank.
        """
        coarse_results = self._coarse_search(query)
        coarse_ids = {r.chunk.id for r in coarse_results}
        parent_ids = {
            r.chunk.id for r in coarse_results if r.chunk.level <= 1
        }

        fine_candidates: List[SearchResult] = []
        for chunk in self.chunks:
            if chunk.level >= 2 and (chunk.parent_id in parent_ids or chunk.parent_id is None):
                score = self._score_chunk(chunk, query)
                if score > 0:
                    fine_candidates.append(SearchResult(chunk=chunk, score=score))

        # Also include the coarse parents themselves; they provide context.
        all_results = coarse_results + fine_candidates
        merged = self._merge_results(all_results)
        expanded = self._expand_parents(merged)
        return self._to_evidence_list(expanded, top_k)

    # ------------------------------------------------------------------
    # Internal search helpers
    # ------------------------------------------------------------------

    def _coarse_search(self, query: str) -> List[SearchResult]:
        """Search only L0/L1 chunks (sections/sheets/division headers)."""
        candidates: Dict[str, float] = {}
        for chunk in self.chunks:
            if chunk.level > 1:
                continue
            score = self._score_chunk(chunk, query)
            if score > 0:
                candidates[chunk.id] = max(candidates.get(chunk.id, 0.0), score)
        return sorted(
            [SearchResult(chunk=self._chunk_by_id[cid], score=s) for cid, s in candidates.items()],
            key=lambda r: r.score,
            reverse=True,
        )[:10]

    def _exact_identifier_search(self, query: str) -> List[SearchResult]:
        """Boost chunks whose section/sheet number appears verbatim in the query."""
        results: List[SearchResult] = []
        query_upper = query.upper()
        for chunk in self.chunks:
            identifier = (chunk.section_number or "").upper()
            if identifier and len(identifier) >= 2 and identifier in query_upper:
                results.append(SearchResult(chunk=chunk, score=5.0))
        return results

    def _search(self, query: str, source: str = "keyword") -> List[SearchResult]:
        """Score all chunks against the query and return sorted results."""
        scores: Dict[str, float] = {}
        for chunk in self.chunks:
            score = self._score_chunk(chunk, query)
            if score > 0:
                scores[chunk.id] = score
        # Apply exact-identifier boost.
        for result in self._exact_identifier_search(query):
            scores[result.chunk.id] = scores.get(result.chunk.id, 0.0) + result.score
        return sorted(
            [SearchResult(chunk=self._chunk_by_id[cid], score=s) for cid, s in scores.items()],
            key=lambda r: r.score,
            reverse=True,
        )

    def _score_chunk(self, chunk: Chunk, query: str) -> float:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return 0.0

        text = f"{chunk.title} {chunk.text} {chunk.section_number}"
        chunk_tokens = self._tokenize(text)
        if not chunk_tokens:
            return 0.0

        score = 0.0
        for token in query_tokens:
            count = sum(1 for ct in chunk_tokens if ct == token)
            # Simple TF with small length normalization.
            score += count / (len(chunk_tokens) + 1)

        # Small boost for title matches.
        title_tokens = self._tokenize(chunk.title)
        title_matches = sum(1 for t in query_tokens if t in title_tokens)
        score += title_matches * 0.1

        return score

    def _merge_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Deduplicate and keep the highest score per chunk."""
        best: Dict[str, SearchResult] = {}
        for r in results:
            if r.chunk.id not in best or best[r.chunk.id].score < r.score:
                best[r.chunk.id] = r
        return sorted(best.values(), key=lambda r: r.score, reverse=True)

    def _expand_parents(self, results: List[SearchResult]) -> List[SearchResult]:
        """Attach parent chunk text to leaf results for context expansion."""
        for r in results:
            parent = self._chunk_by_id.get(r.chunk.parent_id or "")
            if parent:
                r.parent_text = parent.text
        return results

    def _to_evidence_list(self, results: List[SearchResult], top_k: int) -> List[Evidence]:
        """Convert SearchResult objects to Evidence (or dict fallback)."""
        evidence: List[Evidence] = []
        for r in results[:top_k]:
            metadata = {
                "project_id": r.chunk.project_id,
                "discipline": r.chunk.discipline,
                "level": r.chunk.level,
                "parent_id": r.chunk.parent_id,
                "section_number": r.chunk.section_number,
                "title": r.chunk.title,
                "refs": r.chunk.refs,
                "token_count": r.chunk.token_count,
                "parent_text": r.parent_text,
                **r.chunk.metadata,
            }
            if Evidence is not None:
                evidence.append(
                    Evidence(
                        chunk_id=r.chunk.id,
                        document_id=r.chunk.document_id,
                        text=r.chunk.text,
                        source_type=r.chunk.source_type,
                        relevance_score=round(r.score, 4),
                        retrieval_method="hierarchical_keyword",
                        timestamp=datetime.utcnow(),
                        metadata=metadata,
                    )
                )
            else:
                evidence.append(
                    {
                        "chunk_id": r.chunk.id,
                        "document_id": r.chunk.document_id,
                        "text": r.chunk.text,
                        "source_type": r.chunk.source_type,
                        "relevance_score": round(r.score, 4),
                        "retrieval_method": "hierarchical_keyword",
                        "metadata": metadata,
                    }
                )
        return evidence

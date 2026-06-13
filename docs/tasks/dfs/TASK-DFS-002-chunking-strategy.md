# TASK-DFS-002: Hierarchical Chunking Strategy for Construction Documents

**Date:** 2026-05-03
**Scope:** Depth-first implementation of document chunking optimized for construction specs, drawings, and codes
**Personas:** First-Principles Engineer, Research Scientist, Infrastructure-First SRE
**Status:** Design accepted; implementation pending
**Decision record:** [ADR-011: Document-Type-Aware Hierarchical Chunking](../../decisions/ADR-011-chunking-strategy.md)

---

## 1. Objective

Implement a chunking strategy that preserves the hierarchical structure of construction documents while maximizing semantic coherence and retrieval accuracy.

## 2. Document Structure Analysis

Construction documents follow strict hierarchical patterns:

```
Division 23 — HVAC
├── Section 23 00 00 — HVAC General Requirements
│   ├── 23 00 01 — Related Sections
│   ├── 23 00 02 — Reference Standards
│   └── 23 00 03 — Definitions
├── Section 23 05 00 — Common Work Results for HVAC
│   ├── 23 05 13 — Common Motor Requirements
│   ├── 23 05 19 — Meters and Gages for HVAC Piping
│   └── 23 05 23 — General-Duty Valves for HVAC Piping
└── Section 23 09 00 — Instrumentation and Control for HVAC
    ├── 23 09 13 — Instrumentation and Control Devices
    └── 23 09 23 — Direct-Digital Control System for HVAC
```

## 3. Chunking Strategy: Document-Type-Aware Hierarchical Chunking

The design has been finalized in ADR-011. The implementation approach below is preserved as the target architecture.

### 3.1 Architecture

```python
@dataclass
class Chunk:
    id: str                    # UUID
    level: int                 # 0=Division, 1=Section, 2=Subsection, 3=Clause
    parent_id: Optional[str]   # Parent chunk UUID
    division: str              # e.g., "23"
    section: str               # e.g., "23 05 00"
    title: str                 # Heading text
    text: str                  # Full text content
    tables: List[Table]        # Embedded tables
    refs: List[str]            # Cross-references detected
    tokens: int                # Token count
    embedding: Optional[List[float]]

class HierarchicalChunker:
    def chunk(self, doc: ParsedDocument) -> List[Chunk]:
        """
        SRP: Only chunking. No embedding, no storage.
        Returns hierarchical chunks with parent-child relationships.
        """
```

### 3.2 Chunk Levels

| Level | Boundary | Max Tokens | Overlap | Example |
|-------|----------|------------|---------|---------|
| L0 | Division header | 8,192 | 256 | "Division 23 — HVAC" |
| L1 | Section header | 4,096 | 128 | "Section 23 05 00 — Common Work Results" |
| L2 | Subsection / Paragraph group | 1,024 | 64 | "23 05 13 — Common Motor Requirements" |
| L3 | Individual clause / sentence | 256 | 32 | "Motors shall be NEMA Premium Efficiency." |

### 3.3 Special Handling

**Tables:**
- Extract as standalone chunks with surrounding context
- Include table caption and referencing paragraph
- Format as markdown table for embedding

**Cross-References:**
- Detect patterns: "See Section 23 05 13", "Refer to Drawing A-101"
- Store as metadata on both source and target chunks
- Build reference graph for Graph RAG

**Drawing Notes:**
- Extract from PDF annotations or CAD metadata
- Link to parent drawing sheet chunk
- Include scale, revision, date metadata

## 4. Late Chunking Implementation (Future Optimization)

_Deferred until after benchmark dataset exists (TASK-DFS-005)._

Using Jina Embeddings v3 or bge-m3 with 8K context:

```python
def late_chunk(text: str, target_chunk_size: int = 256) -> List[Chunk]:
    """
    1. Embed full section text (up to 8K tokens)
    2. Split into sentences
    3. For each sentence, pool token embeddings from full-context model
    4. Cluster sentences by embedding similarity
    5. Merge clusters into chunks of ~target_chunk_size tokens
    """
```

## 5. Parent-Child Retrieval

```python
class HierarchicalRetriever:
    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        """
        Two-phase retrieval:
        1. Coarse: Retrieve L0/L1 chunks (divisions/sections)
        2. Fine: Within selected sections, retrieve L2/L3 chunks
        3. Deduplicate and rank by combined score
        """
```

## 6. Benchmarking

Compare chunking strategies on:
- **Retrieval accuracy:** MRR@5 on construction QA pairs
- **Contradiction detection:** F1 on labeled contradiction pairs
- **Latency:** End-to-end retrieval time
- **Storage:** Vector DB size per document

## 7. Implementation Tasks

- [x] **Subtask 0:** Finalize chunking strategy design (ADR-011)
- [x] **Subtask 1:** Implement `Chunk` dataclass and `HierarchicalChunker` (`backend/chunking/`)
- [x] **Subtask 2:** Implement heading hierarchy parser (CSI MasterFormat / section aware)
- [x] **Subtask 3:** Implement table extraction as standalone chunks (`backend/chunking/extractors.py`)
- [x] **Subtask 4:** Implement cross-reference detection (`backend/chunking/extractors.py`)
- [ ] **Subtask 5:** Implement Late Chunking with Jina/bge-m3 (deferred)
- [x] **Subtask 6:** Implement `HierarchicalRetriever` with two-phase search (`backend/chunking/retriever.py`)
- [ ] **Subtask 7:** Build benchmark dataset (100 construction QA pairs) (moved to TASK-DFS-005)
- [ ] **Subtask 8:** Run A/B test: Fixed vs. Hierarchical vs. Late chunking

## 8. Acceptance Criteria

1. Retrieval MRR@5 >0.70 on construction QA (vs. 0.45 baseline fixed-size)
2. Chunk parent-child relationships preserved for 100% of parsed docs
3. Cross-reference detection recall >70%
4. Chunking latency <2s per 100-page document
5. Vector storage overhead <30% vs. fixed-size chunking

---

## References

[^1]: Late Chunking in Long-Context Embedding Models. 2024. https://arxiv.org/abs/2409.04701
[^2]: Hierarchical RAG: Leveraging Structured Documents. 2024. https://arxiv.org/abs/2406.13236
[^3]: Jina Embeddings v3 Technical Report. https://huggingface.co/jinaai/jina-embeddings-v3
[^4]: bge-m3 Technical Report. BAAI. https://huggingface.co/BAAI/bge-m3

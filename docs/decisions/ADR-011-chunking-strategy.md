# ADR-011: Document-Type-Aware Hierarchical Chunking for Construction RAG

## Status
Accepted

## Context
Medha's retrieval and contradiction-detection pipeline consumes construction documents (specifications, drawings, RFIs, codes, contracts). The initial prototype used fixed-size chunks with no awareness of document structure, which:
- Splits requirements across chunk boundaries (e.g., a sentence cut in half).
- Separates a subsection from its parent heading, hurting semantic coherence.
- Loses the explicit cross-references that are common in specs ("See Section 23 05 13") and drawings ("Refer to Drawing A-101").

The cognitive architecture already expects retrievable `Evidence` objects that carry `chunk_id`, `document_id`, `source_type`, and `retrieval_method` (`src/cognitive/types.py`). Chunking must produce evidence-friendly units that preserve provenance and hierarchy.

## Decision
Adopt a **document-type-aware hierarchical chunking** strategy as the default.

1. **Preserve natural boundaries.** Chunk at semantic boundaries instead of fixed token counts:
   - **Specifications / codes:** CSI MasterFormat hierarchy — Division → Section → Subsection → Paragraph/Clause.
   - **Drawing notes:** Sheet → Lettered note paragraph → Individual requirement.
   - **Drawing sheets:** One chunk per sheet, with drawing-index metadata.
   - **RFIs / contracts / reports:** One chunk per item or major section.
   - **Tables:** Standalone chunks with surrounding caption/context and markdown representation.

2. **Hierarchical levels.** Every chunk carries a `level` and optional `parent_id`:

   | Level | Boundary | Typical source | Embedding target |
   |-------|----------|----------------|------------------|
   | L0 | Division / document set | Division 23 — HVAC | Context only |
   | L1 | Section / sheet / RFI | Section 23 05 13, Drawing A-101 | Context + fallback |
   | L2 | Subsection / note group | 23 05 13.A, Note A on A-101 | Primary |
   | L3 | Clause / sentence | "Motors shall be NEMA Premium Efficiency." | Fine-grained |

3. **Leaf chunks are embedded; parents are referenced.** The retriever embeds L2/L3 chunks and uses stored parent IDs to pull in L0/L1 context when a leaf is retrieved. This supports the two-phase coarse-to-fine retrieval already sketched in `TASK-DFS-002` and consumed by `System3RetrievalController`.

4. **Cross-reference extraction.** Detect and store references such as `Section 23 05 13`, `Drawing A-101`, `NFPA 13`, and `ASHRAE 90.1` in chunk metadata. These become edges in the reference graph for Graph RAG and contradiction detection.

5. **Fallback to sliding-window overlap.** If a document has no detectable structure (poor OCR, memo, email), fall back to fixed-size chunks with a small overlap. This fallback is explicitly logged as a quality signal.

6. **Defer late chunking.** Late chunking with token-level embeddings (e.g., Jina Embeddings v3, bge-m3) is a future optimization. It will be evaluated only after a benchmark dataset exists (see `TASK-DFS-005`).

Implementation lives in `backend/chunking/` and is exercised by `backend/chunking/tests/test_chunker.py`.

## Consequences

### Positive
- Chunks align with how construction professionals read and cite documents.
- Parent-child links enable coarse-to-fine retrieval and context expansion.
- Cross-reference metadata supports Graph RAG and multi-document contradiction detection.
- Deterministic and auditable; no LLM required for the chunking step itself.

### Negative
- Requires document-type-specific parsing rules; a generic PDF with no headings falls back to sliding windows.
- Token counts vary across chunks, so embedding batching is less uniform than fixed-size chunking.
- Late chunking may eventually outperform this approach; we accept that risk until benchmarks are ready.

## Alternatives Considered

- **Fixed-size chunking (status quo).** Rejected because it cuts across headings and requirements, degrading retrieval and contradiction detection.
- **LLM-based semantic chunking.** Rejected because it is non-deterministic, slower, and more expensive for an ingestion step that must be auditable.
- **Late chunking now.** Rejected because it requires long-context embedding models and token-level embedding access that are not yet integrated or benchmarked in this codebase.

## References

- [CITE: CSI-2024] CSI MasterFormat 2024 Edition — construction specification division/section numbering.
- [CITE: arXiv2409.04701] Late Chunking in Long-Context Embedding Models. 2024.
- [CITE: arXiv2406.13236] Hierarchical RAG: Leveraging Structured Documents. 2024.
- [CITE: Li2024] RAG pipeline optimization for technical documents.
- [CITE: Manning2008] Text classification and keyword retrieval foundations.
- [CITE: Khattab2022] DSPy: retrieval evidence must be traceable to its source.

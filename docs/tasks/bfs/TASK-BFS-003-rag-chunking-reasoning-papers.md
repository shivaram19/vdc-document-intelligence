# TASK-BFS-003: RAG Chunking + Reasoning — Research Landscape

**Date:** 2026-05-03  
**Scope:** Map state-of-the-art RAG architectures, chunking strategies, and reasoning methods relevant to long-form construction documents  
**Personas:** Research Scientist, First-Principles Engineer, Distributed Systems Architect  
**Status:** Research Phase

---

## 1. Objective

Construction documents are uniquely challenging for RAG:
- **Length:** Single specs can be 500+ pages; drawings have 100+ sheets
- **Structure:** Hierarchical (Division → Section → Paragraph → Table)
- **Cross-references:** Spec A references Drawing B-3, which references Code C
- **Multimodal:** Text + tables + CAD metadata + images

This task maps the SOTA for handling these challenges.

---

## 2. Chunking Strategies

| Strategy | Method | Pros | Cons | Papers |
|----------|--------|------|------|--------|
| **Fixed-size** | 512 tokens, 50 overlap | Simple, fast | Breaks sentences; loses hierarchy | Baseline |
| **Semantic** | Embed sentences; cluster by similarity | Preserves meaning | Expensive; variable size | [Late Chunking](https://arxiv.org/abs/2409.04701) [^1] |
| **Hierarchical** | Parent (section) → Child (paragraph) → Grandchild (sentence) | Preserves structure | Complex indexing | [Hierarchical RAG](https://arxiv.org/abs/2406.13236) [^2] |
| **Agentic** | LLM decides chunk boundaries | Optimal for reasoning | Slow; expensive | [RAPTOR](https://arxiv.org/abs/2401.18059) [^3] |
| **Structure-aware** | Parse headings, tables, lists; chunk by document structure | Preserves tables | Requires parser | [Docling](https://github.com/DS4SD/docling) |
| **Late Chunking** | Embed full context; pool token embeddings | Best semantic quality | Requires long-context embedder | [Jina AI 2024](https://arxiv.org/abs/2409.04701) [^1] |

### 2.1 Recommended for Construction Docs

**Hybrid Hierarchical + Late Chunking:**
```
Level 0: Division (e.g., "Division 23 — HVAC")
Level 1: Section (e.g., "23 00 00 — HVAC General Requirements")
Level 2: Paragraph + surrounding context
Level 3: Individual specification clause
```

Each level has its own embedding. Query retrieves at Level 0 first (coarse), then drills to Level 3 (fine).

---

## 3. Reasoning Architectures

| Architecture | Method | Latency | Accuracy | Papers |
|--------------|--------|---------|----------|--------|
| **Naive RAG** | Retrieve → LLM answer | Low | Medium | Baseline |
| **Chain-of-Thought RAG** | Retrieve → CoT reasoning → answer | Medium | High | [CoT Prompting](https://arxiv.org/abs/2201.11903) [^4] |
| **Self-RAG** | Retrieve → generate → critique → regenerate | High | Very High | [Self-RAG](https://arxiv.org/abs/2310.11511) [^5] |
| **Graph RAG** | Build knowledge graph → traverse → answer | Medium | Very High | [GraphRAG](https://arxiv.org/abs/2404.16130) [^6] |
| **Tree of Thoughts** | Multiple reasoning paths → vote | Very High | Very High | [ToT](https://arxiv.org/abs/2305.10601) [^7] |
| **ReAct** | Reason → Act (retrieve) → Reason → answer | Medium | High | [ReAct](https://arxiv.org/abs/2210.03629) [^8] |
| **RAPTOR** | Recursive abstractions → tree retrieval | Medium | Very High | [RAPTOR](https://arxiv.org/abs/2401.18059) [^3] |

### 3.1 Recommended for Construction Reasoning

**Graph RAG + ReAct:**
- Graph RAG captures cross-references (Spec→Drawing→Code)
- ReAct allows tool use (lookup specific section, query drawing index)
- Combined: agent traverses document graph, retrieves evidence, reasons step-by-step

---

## 4. Embedding Models for Construction

| Model | Dimensions | Context | Multilingual | Code | URL |
|-------|-----------|---------|--------------|------|-----|
| **multilingual-e5-large** | 1024 | 512 | Yes | No | [HuggingFace](https://huggingface.co/intfloat/multilingual-e5-large) |
| **bge-m3** | 1024 | 8192 | Yes | Yes | [HuggingFace](https://huggingface.co/BAAI/bge-m3) |
| **Jina Embeddings v3** | 1024 | 8192 | Yes | Yes | [HuggingFace](https://huggingface.co/jinaai/jina-embeddings-v3) |
| **Nomic Embed v1.5** | 768 | 2048 | Yes | No | [HuggingFace](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) |
| **GTE-large** | 1024 | 512 | Yes | No | [HuggingFace](https://huggingface.co/thenlper/gte-large) |

**Recommendation:** bge-m3 or Jina v3 for 8K context + multilingual + technical text.

---

## 5. Vector Stores & Retrieval

| Store | Index | Filtering | Hybrid Search | Scale | URL |
|-------|-------|-----------|---------------|-------|-----|
| **pgvector** | HNSW | SQL WHERE | Yes (with pg_trgm) | 10M+ | https://github.com/pgvector/pgvector |
| **Qdrant** | HNSW | Payload | Yes | 100M+ | https://qdrant.tech |
| **Milvus/Zilliz** | GPU index | Metadata | Yes | 1B+ | https://milvus.io |
| **Weaviate** | HNSW | GraphQL | Yes | 100M+ | https://weaviate.io |
| **Chroma** | HNSW | Metadata | No | 1M+ | https://www.trychroma.com |

**Recommendation:** pgvector (already in Medha stack) for <10M chunks; Qdrant if scaling beyond.

---

## 6. Key Research Papers

| Paper | Year | Contribution | URL |
|-------|------|--------------|-----|
| Late Chunking in Long-Context Embedding Models | 2024 | Pool token embeddings for better chunk quality | [arXiv](https://arxiv.org/abs/2409.04701) [^1] |
| Hierarchical RAG: Leveraging Structured Documents | 2024 | Multi-level retrieval for long documents | [arXiv](https://arxiv.org/abs/2406.13236) [^2] |
| RAPTOR: Recursive Abstraction for Tree-Organized Retrieval | 2024 | Hierarchical summarization for retrieval | [arXiv](https://arxiv.org/abs/2401.18059) [^3] |
| Chain-of-Thought Prompting Elicits Reasoning in LLMs | 2022 | Step-by-step reasoning | [arXiv](https://arxiv.org/abs/2201.11903) [^4] |
| Self-RAG: Learning to Retrieve, Generate, and Critique | 2023 | Adaptive retrieval with self-critique | [arXiv](https://arxiv.org/abs/2310.11511) [^5] |
| From Local to Global: A Graph RAG Approach | 2024 | Knowledge graphs for global reasoning | [arXiv](https://arxiv.org/abs/2404.16130) [^6] |
| Tree of Thoughts: Deliberate Problem Solving | 2023 | Multi-path reasoning | [arXiv](https://arxiv.org/abs/2305.10601) [^7] |
| ReAct: Synergizing Reasoning and Acting in Language Models | 2022 | Interleaved reasoning + tool use | [arXiv](https://arxiv.org/abs/2210.03629) [^8] |

---

## 7. Next Steps (DFS Gates)

- [ ] TASK-DFS-002: Implement hierarchical chunker with Docling parsing
- [ ] TASK-DFS-003: Build Graph RAG pipeline for cross-reference resolution
- [ ] TASK-DFS-004: Implement ReAct reasoning loop for contradiction detection
- [ ] TASK-DFS-009: Benchmark chunking strategies on construction docs

---

## References

[^1]: Late Chunking in Long-Context Embedding Models. 2024. https://arxiv.org/abs/2409.04701
[^2]: Hierarchical RAG: Leveraging Structured Documents. 2024. https://arxiv.org/abs/2406.13236
[^3]: RAPTOR: Recursive Abstraction for Tree-Organized Retrieval. 2024. https://arxiv.org/abs/2401.18059
[^4]: Chain-of-Thought Prompting Elicits Reasoning in LLMs. 2022. https://arxiv.org/abs/2201.11903
[^5]: Self-RAG: Learning to Retrieve, Generate, and Critique. 2023. https://arxiv.org/abs/2310.11511
[^6]: From Local to Global: A Graph RAG Approach. 2024. https://arxiv.org/abs/2404.16130
[^7]: Tree of Thoughts: Deliberate Problem Solving. 2023. https://arxiv.org/abs/2305.10601
[^8]: ReAct: Synergizing Reasoning and Acting. 2022. https://arxiv.org/abs/2210.03629

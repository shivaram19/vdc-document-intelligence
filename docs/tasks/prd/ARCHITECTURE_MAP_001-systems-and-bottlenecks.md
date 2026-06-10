# Medha Architecture Map: Systems, Components & Bottlenecks
**Version:** 2026-06-06
**Purpose:** Plug-and-play system decomposition for parallel enhancement

---

## Executive Summary

Medha has **7 major systems** running in parallel, with varying maturity. Some are production-grade (frontend SPA, Flask API). Some are research-grade (MeMo pipeline, cognitive system). Some are experimental (PicoCloth agent mesh). The key to acceleration is treating each as an independent module with defined interfaces — enhance them in parallel, integrate at boundaries.

---

## System Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MEDHA SYSTEM MAP                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  SYSTEM 1    │    │  SYSTEM 2    │    │  SYSTEM 3    │                   │
│  │  Frontend    │◄──►│  Backend API │◄──►│  Retrieval   │                   │
│  │  SPA         │    │  (Flask)     │    │  Backends    │                   │
│  │              │    │              │    │              │                   │
│  │  Status: ✅  │    │  Status: ✅  │    │  Status: ✅  │                   │
│  │  Lines: ~3K  │    │  Lines: ~2.4K│    │  Lines: ~800 │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         ▲                   ▲                   ▲                           │
│         │                   │                   │                           │
│         └───────────────────┴───────────────────┘                           │
│                         │                                                   │
│                         ▼                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  SYSTEM 4    │    │  SYSTEM 5    │    │  SYSTEM 6    │                   │
│  │  Document    │◄──►│  Cognitive   │    │  MeMo        │                   │
│  │  Graph v2    │    │  System      │    │  Pipeline    │                   │
│  │              │    │              │    │              │                   │
│  │  Status: ✅  │    │  Status: 🔬  │    │  Status: 🔬  │                   │
│  │  Lines: ~1.2K│    │  Lines: ~1.5K│    │  Lines: ~600 │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         ▲                   ▲                   ▲                           │
│         │                   │                   │                           │
│         └───────────────────┴───────────────────┘                           │
│                         │                                                   │
│                         ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │  SYSTEM 7                                            │                   │
│  │  PicoCloth Agent Mesh                                │                   │
│  │  (Experimental — parallel backend)                   │                   │
│  │                                                      │                   │
│  │  Status: 🧪                                          │                   │
│  │  Lines: ~3.5K                                        │                   │
│  └──────────────────────────────────────────────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Legend: ✅ Production  🔬 Research-grade  🧪 Experimental
```

---

## System 1: Frontend SPA
**File:** `frontend/`
**Stack:** Vanilla JS, Tailwind CSS (CDN), marked.js, WebSocket
**Lines:** ~3,000 (JS + CSS + HTML)
**Status:** ✅ Production

### Components
| Component | File | Responsibility | Size |
|-----------|------|----------------|------|
| Router | `js/router.js` | Hash-based routing with params | ~80 lines |
| State | `js/state.js` | Global reactive state | ~60 lines |
| WebSocket Client | `js/ws.js` | Auto-reconnect, message queue | ~120 lines |
| Auth (Token) | `js/auth/token_manager.js` | JWT/capability storage | ~50 lines |
| Auth (Behavior) | `js/auth/behavior.js` | Behavioral biometrics | ~80 lines |
| Auth (Challenge) | `js/auth/challenge_handler.js` | Knowledge-proof response | ~100 lines |
| App Bootstrap | `js/app.js` | Imports, route registration, WS init | ~100 lines |
| Pages (10) | `js/pages/*.js` | Page orchestrators | ~150 lines each |
| Components (atomic) | `js/components/*.js` | Reusable UI pieces | ~100-200 lines each |
| Design System | `css/design-system/` | Tokens, colors, typography | ~200 lines |
| Styles | `css/style.css` | Component styles | ~400 lines |

### Interface (Contracts)
```
INPUT:  WebSocket messages (JSON) from backend/agent mesh
OUTPUT: DOM mutations, user events, WS message sends
AUTH:   SessionStorage password gate (SHA-256), capability tokens
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B1.1 | No build step → can't use TypeScript, tree-shaking, modern bundling | Medium | Add Vite/Rollup (optional) |
| B1.2 | Tailwind CDN loads full utility set (~80KB) | Low | Switch to build-time purge |
| B1.3 | Research portal loads 25 docs upfront → slow initial render | Medium | Lazy-load docs, virtual scroll |
| B1.4 | WebSocket reconnect every 3s when offline → battery drain on mobile | Low | Exponential backoff |
| B1.5 | No service worker → no offline capability | Medium | Add basic SW for asset caching |

### Enhancement Opportunities
- **P1:** Add drawing viewer component (Canvas/PDF.js) for spec↔drawing side-by-side
- **P2:** Virtual scroll for large document lists (>100 items)
- **P3:** Toast notification system for contradiction alerts
- **P4:** Keyboard shortcuts for power users (VIM-style navigation)

---

## System 2: Backend API (Flask)
**File:** `backend/app.py` (+ stores, extractors, detectors, linkers)
**Stack:** Python 3.10, Flask, Gunicorn
**Lines:** ~2,400 (app.py ~1,650 + modules ~750)
**Status:** ✅ Production

### Components
| Component | File | Responsibility | Size |
|-----------|------|----------------|------|
| Main API | `backend/app.py` | Project CRUD, upload, query, RFI, contradiction, auth | ~1,652 lines |
| Retrieval Abstraction | `backend/retrieval_store.py` | Pluggable retrieval (filesystem/chroma/pgvector) | ~726 lines |
| Chroma Store | `backend/stores/chroma_store.py` | Incremental chunk storage + embeddings | ~200 lines |
| Entity Store | `backend/stores/entity_store.py` | SQLite entity + link storage | ~150 lines |
| Semantic Chunker | `backend/chunkers/semantic_chunker.py` | Text chunking strategies | ~100 lines |
| Entity Extractor | `backend/extractors/entity_extractor.py` | Named entity extraction | ~100 lines |
| Contradiction Detector | `backend/detectors/simple_contradiction.py` | Rule-based contradiction detection | ~80 lines |
| Text Linker | `backend/linkers/text_linker.py` | Spec↔drawing entity linking | ~120 lines |
| Docling Parser | `backend/docling_parser.py` | Advanced document parsing | ~100 lines |
| OCR Extractor | `backend/ocr_extractor.py` | OCR fallback for scanned PDFs | ~80 lines |
| Local LLM | `backend/local_llm.py` | CPU inference wrapper | ~100 lines |

### Interface (Contracts)
```
INPUT:  HTTP requests (multipart/form-data for uploads, JSON for queries)
OUTPUT: JSON responses with citations, audit logs
AUTH:   Bearer token (API_SECRET), optional behavioral fingerprint
DB:     SQLite (entities), Chroma/pgvector (embeddings), filesystem (raw docs)
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B2.1 | `app.py` is 1,652 lines — violates SRP (AGENTS.md max ~200 lines) | **HIGH** | Split into route blueprints |
| B2.2 | Contradiction detector is rule-based only — no LLM reasoning | **HIGH** | Integrate cognitive System 4 |
| B2.3 | No caching layer — same query hits embedding model every time | Medium | Add Redis/SQLite query cache |
| B2.4 | File upload size limits unclear — large PDFs may timeout | Medium | Add streaming upload + progress |
| B2.5 | `local_llm.py` uses CPU-only Phi-3.1 — 10-50× slower than API | Medium | Add GPU support or drop for API-only |
| B2.6 | No request idempotency — duplicate uploads create duplicates | Low | Add dedup by content hash |

### Enhancement Opportunities
- **P1:** Split `app.py` into Flask blueprints (projects, documents, queries, rfis, auth, admin)
- **P2:** Integrate cognitive system (`src/cognitive/`) into query pipeline
- **P3:** Add Redis cache for embedding queries (TTL = document version)
- **P4:** Implement content-addressable storage (SHA-256 dedup)
- **P5:** Add OpenTelemetry tracing for performance monitoring

---

## System 3: Retrieval Backends
**Files:** `backend/retrieval_store.py`, `backend/stores/`, `docker-compose.pgvector.yml`
**Stack:** Filesystem / Chroma / pgvector
**Lines:** ~800
**Status:** ✅ Production

### Components
| Component | File | Responsibility |
|-----------|------|----------------|
| Retrieval ABC | `backend/retrieval_store.py` | Abstract base class + unified interface |
| Filesystem Store | `backend/retrieval_store.py` | JSON file storage (default, zero deps) |
| Chroma Store | `backend/stores/chroma_store.py` | Vector DB with `all-mpnet-base-v2` |
| pgvector Store | `backend/sql/` + Docker | PostgreSQL vector extension |

### Interface (Contracts)
```
INPUT:  Query string + project_id + top_k
OUTPUT: List[RetrievalMatch] with score, chunk_id, content, metadata
SWAP:   Set RETRIEVAL_BACKEND=filesystem|chroma|pgvector in .env
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B3.1 | Benchmark exists but not run recently — no performance data | Medium | Re-run benchmark on all 3 backends |
| B3.2 | `all-mpnet-base-v2` is general-domain — not construction-tuned | **HIGH** | Fine-tune sentence-transformer on construction corpus |
| B3.3 | No hybrid search (vector + keyword) in any backend | **HIGH** | Implement BM25 + vector fusion |
| B3.4 | Chroma persistent storage path is hardcoded | Low | Make configurable via env |
| B3.5 | No embedding caching — same chunk re-embedded on every upload | Medium | Cache embeddings by content hash |

### Enhancement Opportunities
- **P1:** Fine-tune `sentence-transformers` on construction specs (Domain Adapted Embeddings)
- **P2:** Implement hybrid retrieval (dense vector + sparse BM25) per Li2024
- **P3:** Add reranking model (cross-encoder) for top-k results
- **P4:** Benchmark all 3 backends with Dubai corpus and publish results

---

## System 4: Document Graph v2
**Files:** `backend/v2/doc_graph.py`, `backend/v2/reference_patterns.py`, `backend/v2/drawing_index.py`, `backend/v2/domain_knowledge.py`
**Stack:** Python, networkx-compatible structures, Neo4j Cypher export
**Lines:** ~1,200
**Status:** ✅ Production

### Components
| Component | File | Responsibility | Size |
|-----------|------|----------------|------|
| Document Graph | `backend/v2/doc_graph.py` | Navigable graph: nodes (sheets, specs, tags), edges (REFERENCES, CONTAINS) | ~616 lines |
| Reference Patterns | `backend/v2/reference_patterns.py` | Regex extraction of sheet numbers, details, spec sections | ~100 lines |
| Drawing Index | `backend/v2/drawing_index.py` | Sheet validation, discipline tracking | ~150 lines |
| Domain Knowledge | `backend/v2/domain_knowledge.py` | Trade checklists, code compliance, anomaly detection | ~535 lines |

### Interface (Contracts)
```
INPUT:  Raw document text + file metadata
OUTPUT: Graph (nodes/edges), broken link report, compliance checklist
EXPORT: Neo4j Cypher, GraphML, JSON
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B4.1 | Reference patterns are regex-only — no ML-based extraction | Medium | Add NER model for reference extraction |
| B4.2 | No integration with retrieval System 3 — graph and vectors are separate | **HIGH** | GraphRAG: use graph for multi-hop, vectors for semantic |
| B4.3 | Domain knowledge hardcodes US codes (IECC, IBC, ASHRAE, ACI) | **HIGH** | Add Dubai DM Building Regulations module |
| B4.4 | Drawing index parser doesn't handle Arabic/RTL sheet numbering | Medium | Add RTL support for GCC projects |
| B4.5 | No visual graph explorer in frontend | Low | Add D3.js/cytoscape.js graph viewer |

### Enhancement Opportunities
- **P1:** Implement GraphRAG (graph + vector hybrid retrieval)
- **P2:** Add Dubai DM code compliance module
- **P3:** Visual graph explorer in frontend (interactive node/edge navigation)
- **P4:** Export to IFC/BCF for BIM interoperability

---

## System 5: Cognitive System
**Files:** `src/cognitive/` (5 systems + types)
**Stack:** Pure Python, zero external dependencies (except optional)
**Lines:** ~1,500
**Status:** 🔬 Research-grade (not integrated into backend)

### Components
| Component | File | Responsibility | Citations |
|-----------|------|----------------|-----------|
| System 1: Heuristic | `system1_heuristic.py` | Fast query classification (<1ms), Take-The-Best | Kahneman2011, Gigerenzer2009 |
| System 2: Analytical | `system2_analytical.py` | ReAct reasoning loops, tool use | Wei2022 (CoT), Yao2023 (ReAct) |
| System 3: Retrieval | `system3_retrieval.py` | Active RAG, dynamic strategy selection | Qi2024 (Active RAG), Trivedi2023 (IRCoT) |
| System 4: Metacognitive | `system4_metacognitive.py` | Confidence monitoring, semantic entropy, escalation | Flavell1979, Jiang2021 |
| System 5: Orchestrator | `orchestrator.py` | Bayesian strategy selection, arbitration | Friston2010, Daw2005, Kamar2012 |
| Types | `types.py` | Shared data structures, CognitiveState, Strategy | — |

### Interface (Contracts)
```
INPUT:  User query string + project context
OUTPUT: Answer + confidence score + evidence trace + escalation flag
META:   53 academic citations, legally defensible reasoning paths
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B5.1 | **NOT INTEGRATED** — exists as standalone code, never called from backend | **CRITICAL** | Wire into Flask API query pipeline |
| B5.2 | No evaluation harness — no accuracy metrics on real queries | **HIGH** | Build test suite with 100+ construction QAs |
| B5.3 | Heuristic System 1 uses regex only — no learned classifier | Medium | Add lightweight BERT classifier (optional) |
| B5.4 | No persistent learning — Bayesian priors reset on restart | Medium | Save/load strategy priors from SQLite |
| B5.5 | Semantic entropy requires multiple LLM samples (3-5× cost) | Medium | Cache sampled answers, approximate entropy |

### Enhancement Opportunities
- **P1:** Integrate into Flask API (`/api/v2/query` route)
- **P2:** Build evaluation harness with labeled construction QA dataset
- **P3:** Add persistent strategy learning across sessions
- **P4:** Implement System 4 human escalation UI in frontend

---

## System 6: MeMo Pipeline
**Files:** `scripts/memo-poc/`
**Stack:** Python, OpenAI API
**Lines:** ~600 (3 variants: sequential, parallel, async)
**Status:** 🔬 Research-grade (validated on real docs)

### Components
| Component | File | Responsibility | Status |
|-----------|------|----------------|--------|
| Sequential Pipeline | `reflection_synthesis_pipeline.py` | 5-step MeMo (original) | ✅ Working |
| Parallel Pipeline | `reflection_synthesis_pipeline_parallel.py` | ThreadPoolExecutor (20 workers) | ✅ 19× speedup |
| Async Pipeline | `reflection_synthesis_pipeline_async.py` | AsyncOpenAI (50 workers) | ✅ Working |
| Test Report | `TEST_REPORT_001.md` | Validation results on 4 corpora | ✅ Complete |
| Contradiction Corpus | `real_construction_docs_contradictions/` | Synthetic ground-truth test data | ✅ 4 deliberate contradictions |

### Interface (Contracts)
```
INPUT:  Directory of .txt/.md documents + OPENAI_API_KEY
OUTPUT: reflections.jsonl (QA pairs) + summary.json (stats)
STEPS:  1. Fact Extraction → 2. Consolidation → 3. Verification → 4. Entity Surfacing → 5. Cross-Document Synthesis
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B6.1 | API latency is the hard ceiling — 60-75% of time is model token generation | **HIGH** | Use OpenAI Batch API (50% cheaper, no rate limits) |
| B6.2 | Step 5 contradiction detection: 25% on synthetic ground truth | **HIGH** | Use gpt-4o (not mini) for Step 5; explicit contradiction prompt |
| B6.3 | Real documents don't produce contradictions — need same-project corpus | **HIGH** | Find construction bid sets with addenda |
| B6.4 | No local model support — requires paid API key | Medium | Add vLLM integration for Qwen2.5-14B |
| B6.5 | Output is training data, not directly usable by backend | Medium | Add loader that ingests reflections into ChromaStore |
| B6.6 | Chunk size is static — no adaptive chunking | Low | Implement semantic chunking based on section boundaries |

### Enhancement Opportunities
- **P1:** OpenAI Batch API integration for large corpora (50+ docs)
- **P2:** Local vLLM backend (eliminates API cost/latency entirely)
- **P3:** Step 5 prompt engineering for explicit contradiction detection
- **P4:** Pipeline output → direct ingestion into backend entity store
- **P5:** Adaptive chunking based on document structure (sections, subsections)

---

## System 7: PicoCloth Agent Mesh
**Files:** `picocloth/`, `picocloth-deploy/`
**Stack:** Python, WebSocket, shared memory (JSON files), MCP protocol
**Lines:** ~3,500
**Status:** 🧪 Experimental (parallel backend to Flask)

### Components
| Component | File | Responsibility | Size |
|-----------|------|----------------|------|
| Agent Bridge | `bridge/agent_bridge.py` | WebSocket + HTTP server, auth mesh, fleet commands | ~635 lines |
| VDC Core | `agents/vdc_core.py` | Pure Python doc intelligence (no Flask) | ~400 lines |
| Orchestrator | `agents/orchestrator.py` | Workflow router: ingest→query→rfi→scan | ~200 lines |
| Auth (9 modules) | `agents/auth/*.py` | Fleet identity, tokens, challenges, anomaly detection | ~800 lines |
| Shared Memory | `shared/` | Atomic JSON writes, cross-process file locking | ~300 lines |
| MCP Fleet Server | `mcp-fleet-server/server.py` | MCP protocol for fleet coordination | ~150 lines |
| Deploy Script | `picocloth-deploy/deploy.sh` | Full deployment orchestration | ~344 lines |
| Node Configs | `node-a-vdc-config.json`, `node-b-vdc-config.json` | Per-node model + character configs | ~200 lines each |

### Interface (Contracts)
```
INPUT:  WebSocket messages + HTTP inbox posts
OUTPUT: Shared memory updates (JSON), broadcast snapshots every 2s
AUTH:   3-factor for humans (knowledge + behavioral + attestation), HMAC for machines
MEMORY: File-based shared memory in picocloth/shared/project/vdc/
```

### Bottlenecks
| # | Bottleneck | Severity | Fix |
|---|-----------|----------|-----|
| B7.1 | **Duplication** — PicoCloth reimplements backend logic (extraction, embedding, contradiction) | **CRITICAL** | Extract shared library used by both Flask and PicoCloth |
| B7.2 | File-based shared memory is slow under high concurrency | **HIGH** | Replace with Redis or SQLite WAL mode |
| B7.3 | No frontend integration — WebSocket protocol differs from Flask's | **HIGH** | Unify WebSocket protocol or add adapter |
| B7.4 | Deploy script is 344 lines of bash — fragile | Medium | Rewrite in Python with error handling |
| B7.5 | xAI API key was exposed in node configs (fixed, but tokens need regeneration) | **HIGH** | Rotate all tokens, add secret management |
| B7.6 | No tests for fleet coordination — untested in multi-node scenarios | Medium | Add integration tests for 2+ node mesh |

### Enhancement Opportunities
- **P1:** Extract `medha-core` shared library (document extraction, embedding, contradiction)
- **P2:** Unify WebSocket protocol between Flask and PicoCloth
- **P3:** Add Redis as shared memory backend option
- **P4:** Secret management (HashiCorp Vault or AWS Secrets Manager)
- **P5:** Integration tests for multi-node fleet

---

## Cross-Cutting Concerns

### Security
| Issue | Status | Action |
|-------|--------|--------|
| xAI key exposed in git history | Fixed (placeholders) | Regenerate new key |
| OpenAI key shared in chat | Not persisted | Consider rotation if logs retained |
| pico channel tokens exposed | Fixed (placeholders) | Regenerate tokens |
| TruffleHog pre-commit | Active | ✅ Working |
| API_SECRET in .env | Active | Rotate periodically |

### Research → Code Gap
| Research | Status | Code Integration |
|----------|--------|------------------|
| MeMo arXiv paper | ✅ Analyzed | Pipeline implemented |
| BFS-014 (VDC personas) | ✅ Complete | Personas in PRD, not in code |
| BFS-015 (Doc controller pain) | ✅ Complete | Partially in frontend |
| BFS-018 (Platform landscape) | ✅ Complete | Not integrated |
| Cognitive system (53 citations) | ✅ Implemented | **NOT wired to backend** |
| Construction AI landscape 2026 | ✅ Just added | Not integrated |

### Data Assets
| Asset | Location | Size | Status |
|-------|----------|------|--------|
| Sample docs (synthetic) | `sample_docs/` | 5 files | ✅ |
| Real construction docs | `real_construction_docs/` | 3 real + extras | ✅ |
| Contradiction test corpus | `real_construction_docs_contradictions/` | 2 files | ✅ |
| Research documents | `docs/research/` | 25+ files | ✅ |
| Reflections (synthetic) | `data/reflections/reflections.jsonl` | 65 pairs | ✅ |
| Reflections (real) | `data/reflections/*_reflections*.jsonl` | 900+ pairs | ✅ |
| Benchmark reports | `.bench/` | Multiple | ⚠️ Stale |

---

## Recommended Parallel Workstreams

Based on this map, here are **5 parallel enhancement tracks** that don't block each other:

### Track A: Backend Refactor (2 weeks)
- Split `app.py` into Flask blueprints
- Integrate cognitive System 5 into query pipeline
- Add Redis cache for embeddings
- **Owner:** Backend engineer
- **Blocked by:** None

### Track B: Frontend Enhancement (2 weeks)
- Add drawing viewer component (PDF.js side-by-side)
- Lazy-load research portal docs
- Add toast notifications for contradictions
- **Owner:** Frontend engineer
- **Blocked by:** None

### Track C: MeMo Pipeline Hardening (2-3 weeks)
- OpenAI Batch API integration
- vLLM local backend option
- Step 5 contradiction prompt engineering
- Pipeline output → backend ingestion
- **Owner:** ML/Research engineer
- **Blocked by:** None

### Track D: Dubai Corpus & Compliance (4-6 weeks)
- Collect 50-100 real GCC construction documents
- Build Dubai DM Building Regulations module
- Add Arabic/RTL support
- **Owner:** Domain expert + researcher
- **Blocked by:** None

### Track E: PicoCloth Stabilization (3-4 weeks)
- Extract `medha-core` shared library
- Unify WebSocket protocol with Flask
- Add Redis shared memory option
- Multi-node integration tests
- **Owner:** Systems engineer
- **Blocked by:** None (but should sync with Track A)

---

## Interface Contracts Summary

```python
# System 1 (Frontend) ↔ System 2 (Backend)
POST /api/projects/{id}/query    → {answer, citations, confidence}
POST /api/projects/{id}/upload   → {document_id, chunks, entities}
WS   /ws                         → {type, payload, request_id}

# System 2 (Backend) ↔ System 3 (Retrieval)
RetrievalStore.query(project_id, query, top_k=5) → List[RetrievalMatch]
RetrievalStore.add(project_id, chunks)           → List[chunk_id]

# System 2 (Backend) ↔ System 4 (Doc Graph)
DocumentGraph.build(documents)        → Graph(nodes, edges)
DocumentGraph.find_broken_links()     → List[BrokenLink]
DomainKnowledge.check_compliance(doc) → List[Violation]

# System 2 (Backend) ↔ System 5 (Cognitive)
CognitiveOrchestrator.query(query, context) → {answer, confidence, trace, escalate}

# System 6 (MeMo) → System 2 (Backend)
reflections.jsonl → EntityStore.ingest(qa_pairs)

# System 7 (PicoCloth) ↔ System 1 (Frontend)
WS /ws (same protocol, different endpoint)
```

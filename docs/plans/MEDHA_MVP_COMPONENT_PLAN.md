# Medha MVP Component Plan

**Status:** Living roadmap
**Date:** 2026-05-03
**Scope:** Step-by-step plan for every component in the Medha document-intelligence layer, with research-backed citations for each design decision.

---

## 1. Strategic intent

Medha is the **lean document-intelligence layer** for preconstruction VDC agencies. It does not replace Revit, Navisworks, or Procore; it reads the documents that flow between those tools and surfaces contradictions, gaps, and action items before they become RFIs or rework.

The economic justification is direct: document errors are a primary cause of construction rework, and rework consumes a measurable share of project cost [CITE: Ejiofor2025]. At the same time, BIM adoption in developing economies and smaller agencies is constrained by workflow fragmentation, not by a lack of model-viewing tools [CITE: Fathima2024]. A lightweight, deterministic document-intelligence layer addresses that gap without forcing agencies to replace their existing stack.

The components below are sequenced to deliver **pre-clash contradiction detection** and **RFI drafting** as early as possible, because PRD-002 identifies those as the P1 MVP features that move the needle on rework and review time.

---

## 2. Component-by-component plan

### 2.1 Document ingestion & classification

**Why it matters.** Construction document sets arrive as heterogeneous, often poorly named files. Before any intelligence can run, the system must normalize intake, classify discipline, and preserve provenance. Manual sorting is the current bottleneck in small VDC agencies [CITE: Fathima2024].

**Research basis.**
- Deterministic classification by filename, extension, and content keywords is preferred over LLM-based classification for ingestion because it is auditable, fast, and does not require an external inference call for every upload [CITE: Papaioannou2023].
- Sheet numbering follows CSI/AIA conventions that can be parsed deterministically [CITE: NCS-US-2024].

**Step-by-step implementation.**
1. Accept PDF, DOCX, TXT, DWG, DXF, RVT, IFC via CLI and API.
2. Copy files into a per-project workspace (`data/projects/<id>/documents/<type>/`).
3. Classify `DocumentType` from extension and `Discipline` from filename + content preview.
4. Compute SHA-256 hash and size; reject exact duplicates.
5. Extract text: `pdfplumber` for PDFs, python-docx for DOCX, plain read for TXT; DWG/DXF metadata fallback.
6. Persist `Project` and `Document` records in SQLite (`backend/ingestion/store.py`).
7. Track processing status: `pending → processing → completed/failed`.

**Files.** `backend/ingestion/ingestor.py`, `backend/ingestion/classifier.py`, `backend/ingestion/extractor.py`, `backend/ingestion/store.py`, `backend/ingestion/models.py`.

**Tests.** `backend/ingestion/tests/test_ingestor.py`, `test_classifier.py`.

**ADR.** ADR-010 (drawing-index parser), ADR-011 (chunking).

---

### 2.2 Drawing-index parser

**Why it matters.** Real drawing sets contain 10–100+ sheets. Treating the whole PDF as one chunk loses the sheet-level citations a VDC engineer needs; guessing sheet numbers from body text creates false records.

**Research basis.**
- Drawing indexes are structured textual artifacts; parsing them with regex aligned to National CAD Standard numbering is reliable and avoids the non-determinism of LLM extraction [CITE: NCS-US-2024].

**Step-by-step implementation.**
1. Scan first 5 pages of a PDF for index rows.
2. Match sheet-number patterns (`A-101`, `S-201`, `FP-501`) at line start, optionally preceded by `Sheet` or a numbered bullet.
3. Merge wrapped titles that continue on the next line.
4. If no index is found, fall back to per-page header extraction, then to a single `DOC` sheet for specifications.
5. Store each sheet with number, title, discipline, revision, date, and page offset.

**Files.** `backend/ingestion/drawing_index.py`, `backend/drawing_index.py` (legacy), `backend/ingestion/extractor.py`.

**Tests.** `backend/ingestion/tests/test_drawing_index.py`.

**ADR.** ADR-010.

---

### 2.3 Project / document store

**Why it matters.** All downstream intelligence depends on stable IDs, provenance, and fast lookups. A single SQLite store keeps the MVP self-contained and observable.

**Research basis.**
- SQLite is sufficient for MVP-scale projects and avoids operational complexity; migration to Postgres can be deferred until multi-tenant scale [CITE: PRD-002].

**Step-by-step implementation.**
1. SQLite schema for `projects`, `documents`, and later `chunks`, `claims`, `contradictions`, `rfis`.
2. JSON-serialized metadata columns for flexible schema evolution.
3. Foreign keys and cascade deletes for project cleanup.
4. Provide `ProjectStore` API: create, get, list, save document.

**Files.** `backend/ingestion/store.py`.

**Tests.** Ingestor tests exercise store indirectly.

---

### 2.4 Hierarchical chunker

**Why it matters.** Fixed-size chunks split requirements across boundaries, hurting retrieval and contradiction detection. Construction documents are inherently hierarchical (Division → Section → Subsection → Clause), and retrieval accuracy improves when chunks respect those boundaries [CITE: Li2024].

**Research basis.**
- Hierarchical RAG leverages document structure to improve retrieval over flat vector search [CITE: arXiv2406.13236].
- Late chunking with long-context embedding models can improve chunk quality further, but it requires token-level embedding access and should be benchmarked before adoption [CITE: Günther2024].

**Step-by-step implementation.**
1. Implement document-type dispatch: spec, drawing, RFI, fallback.
2. **Spec chunker:** split on `SECTION XX XX XX` headers, then `1.1`/`1.2` subsections; keep parent IDs.
3. **Drawing chunker:** one chunk per sheet; for drawing-note text files, split on lettered notes (`A.`, `B.`).
4. **RFI chunker:** one chunk per `RFI-NNN` item.
5. **Fallback chunker:** sliding-window paragraphs for unstructured text.
6. Every chunk stores `level`, `parent_id`, `section_number`, `title`, `discipline`, `source_type`.

**Files.** `backend/chunking/chunker.py`, `backend/chunking/models.py`.

**Tests.** `backend/chunking/tests/test_chunker.py`.

**ADR.** ADR-011.

---

### 2.5 Table extraction

**Why it matters.** Valves, duct schedules, door schedules, and equipment schedules carry dense, structured requirements. Treating them as prose loses the row/column semantics needed for comparison.

**Research basis.**
- Tables in construction specs are high-information-density objects that should be preserved as first-class retrieval units [CITE: Moon2021].

**Step-by-step implementation.**
1. Detect markdown pipe tables (`| col1 | col2 |`).
2. Detect whitespace-aligned tables (≥2 spaces or tabs between columns, ≥2 rows, ≥2 columns).
3. Render detected tables as markdown; use the preceding line as caption.
4. In `SpecificationChunker`, split inline tables into standalone `source_type="table"` chunks with parent link to the subsection.

**Files.** `backend/chunking/extractors.py` (table functions), `backend/chunking/chunker.py`.

**Tests.** `backend/chunking/tests/test_tables.py`.

---

### 2.6 Cross-reference extraction

**Why it matters.** Construction documents are cross-referenced networks: specs cite drawings, drawings cite specs, and both cite standards. Capturing these edges enables Graph RAG and multi-hop contradiction detection.

**Research basis.**
- Cross-document references are a key signal for contradiction detection and for building a document graph [CITE: Moon2021].
- Graph-augmented retrieval improves multi-hop reasoning by following explicit document links [CITE: arXiv2406.13236].

**Step-by-step implementation.**
1. Regex patterns for `Section XX XX XX`, `Drawing A-101`, `Sheet M-301`, and standards (`NFPA 13`, `ASHRAE 90.1-2022`, `SMACNA`).
2. Normalize references (dashes, spaces, uppercase).
3. Store `refs` on every chunk.
4. Later, build a graph from refs for Graph RAG.

**Files.** `backend/chunking/extractors.py`.

**Tests.** `backend/chunking/tests/test_chunker.py` (cross-reference assertions).

---

### 2.7 Hierarchical retriever

**Why it matters.** A VDC query is usually under-specified ("What about the ducts?"). A retriever that first finds the right section/sheet, then the right clause, mimics how an engineer searches a drawing set.

**Research basis.**
- Two-phase coarse-to-fine retrieval reduces noise by narrowing the search space to relevant document regions [CITE: Li2024].
- Active retrieval under uncertainty selects actions that maximize expected information gain [CITE: Friston2010].
- Evidence must be traceable to its source for verifiable reasoning [CITE: Khattab2022].

**Step-by-step implementation.**
1. Build an inverted keyword index over chunks.
2. **Coarse phase:** score L0/L1 chunks (sections/sheets) for the query.
3. **Fine phase:** score L2/L3 chunks whose parent is in the coarse set.
4. Boost exact sheet/section identifiers in the query.
5. Expand leaf results with parent text and return `Evidence` objects.
6. Allow an optional external vector search callable; fallback to keyword until embeddings are integrated.

**Files.** `backend/chunking/retriever.py`.

**Tests.** `backend/chunking/tests/test_retriever.py`.

---

### 2.8 Claim extraction

**Why it matters.** Contradiction detection needs normalized facts, not raw text. A claim is a structured triple — `{entity, attribute, value, unit, source_chunk}` — that can be compared across documents.

**Research basis.**
- Named entity recognition and relation extraction are the standard building blocks for turning construction specs into machine-readable requirements [CITE: Moon2021; Nahri2025].
- Transformer-based NER achieves >90% F1 on construction technical specifications when fine-tuned on domain data [CITE: Nahri2025].
- For MVP, deterministic regex + keyword rules are sufficient and avoid the cold-start data problem of supervised NER [CITE: Dikmen2025].

**Step-by-step implementation.**
1. Define claim types for MVP:
   - Numeric dimension/performance claims: `R-value`, `U-factor`, `ceiling height`, `spacing`, `velocity`, `pressure`, `density`.
   - Material claims: `duct material`, `valve type`, `floor finish`, `fire rating`.
2. Build extractors per type:
   - Regex for `quantity: value unit` patterns (e.g., `R-21`, `0.30`, `12 feet`, `1,800 FPM`).
   - Keyword-driven material extractor.
3. Normalize values to base units where possible.
4. Canonicalize entity names (e.g., `mechanical room ceiling`, `MR ceiling`, `M-room ceiling` → same entity).
5. Store claims with provenance (chunk_id, document_id, section_number, confidence).

**Files.** `backend/analysis/claims.py`, `backend/analysis/extractors.py`.

**Tests.** Tests against `sample_docs/`; expect to extract `window U-factor = 0.30` from ARCH, `R-21` wall insulation, etc.

**ADR needed.** ADR-012: Deterministic claim extraction for construction specifications.

---

### 2.9 Contradiction detection engine

**Why it matters.** This is Medha’s primary value proposition. PRD-002 targets ≥80% of document-level contradictions caught pre-clash, with <20% false positives.

**Research basis.**
- RFI literature shows the top causes of RFIs are incomplete or contradictory contract documents [CITE: Afzal2024].
- Automated specification review systems reduce review time and improve consistency by detecting semantic conflicts [CITE: Moon2021].
- LLM-generated findings must include citations and confidence scores because hallucination is a documented risk in construction-document tasks [CITE: Papaioannou2023].

**Step-by-step implementation.**
1. **Numeric mismatch detector:** compare same entity+attribute across claims; flag differences beyond tolerance.
2. **Material conflict detector:** compare material claims for the same entity.
3. **Presence/absence detector:** flag when a required attribute appears in one doc but is missing in another referenced doc.
4. **Standard/version detector:** flag when different editions of the same standard are cited.
5. **Confidence scoring:** combine extractor confidence, value similarity, and source reliability.
6. **Severity scoring:** based on attribute criticality (structural, fire/life-safety, code-related = high).
7. Output `Contradiction` object:
   - id, project_id, type, severity, confidence
   - claim_a, claim_b (with chunk citations)
   - suggested_trade, status (`open`/`dismissed`/`confirmed`)
8. Persist in SQLite.

**Files.** `backend/analysis/contradictions.py`, `backend/analysis/detectors.py`, `backend/analysis/models.py`.

**Tests.** Use `RFI_LOG.txt` contradictions as labeled test cases; add synthetic cases for edge conditions.

**ADR needed.** ADR-013: Contradiction detection architecture.

---

### 2.10 RFI drafter

**Why it matters.** PRD-002 targets RFI drafting time from 1–2 hours to <15 minutes. A draft with correct citations reduces friction and ensures traceability.

**Research basis.**
- Industry data shows AI plan checking can reduce RFI volume by 30–50% by catching issues before construction [CITE: InspectMind2025].
- Effective RFI text includes the question, affected drawings/specs, and proposed resolution options [CITE: PRD-002].

**Step-by-step implementation.**
1. Template-based generator driven by a `Contradiction`:
   - Question: "Window U-factor is shown as 0.30 in A-101 notes and required as 0.28 in the energy model. Please confirm the correct value."
   - Affected documents: list drawing/spec chunks.
   - Proposed resolutions: prefer higher-code value or note correction.
2. Allow human edit before sending.
3. One-click push to Plane via `plane-mcp`.
4. Store RFI with link back to contradiction; update status on Plane sync.

**Files.** `backend/analysis/rfi_drafter.py`, integration with `mcp-servers/plane-mcp/client.py`.

**Tests.** Generate drafts for each sample contradiction; assert citations present.

**ADR needed.** ADR-014: RFI drafting and issue workflow integration.

---

### 2.11 Drawing diff / version monitor

**Why it matters.** Addenda and revised drawings are a major source of missed changes. PRD-002 lists drawing diff and addenda impact as P1.

**Research basis.**
- Manual revision comparison is slow and error-prone; 65% of changes go unclouded, and missed changes can cost $5K–$50K+ in rework [CITE: Articulate2025; BuildSync2025].
- Image-based diff using OpenCV has been prototyped for drawing revision management and reduces manual comparison effort [CITE: Waidyasekara2026].

**Step-by-step implementation.**
1. Version storage: keep previous and current document files per project.
2. Metadata diff: compare sheet lists, sheet numbers, revisions, dates.
3. Text diff: extract text from both PDFs and compute per-sheet diff.
4. Visual diff (later): overlay sheet images with color-coded differences.
5. Re-run contradiction detection on changed sheets and affected cross-references.
6. Feed new findings into the live risk feed.

**Files.** `backend/analysis/diff.py`, storage layer extension.

**Tests.** Diff two versions of a sample spec; assert changed sections are detected.

**ADR needed.** ADR-015: Document version comparison and impact analysis.

---

### 2.12 Plane / workflow integration extension

**Why it matters.** Medha must fit into the VDC engineer’s existing workflow. Plane is already self-hosted and seeded with marketing tasks; extending it to project issues and RFIs is the shortest path.

**Research basis.**
- Tool-use integrations for agents require per-user auth and short-TTL tokens to limit blast radius [CITE: Errico2025; Shahidinejad2021].

**Step-by-step implementation.**
1. Add `plane_create_issue`, `plane_update_issue`, `plane_add_comment` tools to `plane-mcp`.
2. Map a contradiction to a Plane issue with custom fields: severity, confidence, affected discipline.
3. Add webhook/poll support to sync RFI status back to Medha.
4. Later: Procore/ACC MCP servers.

**Files.** `mcp-servers/plane-mcp/server.py`, `client.py`.

**Tests.** Integration tests against the self-hosted Plane instance.

**ADR needed.** ADR-016: Agent-tool authentication for issue trackers.

---

### 2.13 Evaluation benchmark

**Why it matters.** Without labeled data and metrics, we cannot know if contradiction detection improves or if chunking changes help retrieval.

**Research basis.**
- RAG evaluation should measure retrieval accuracy, faithfulness, and citation precision [CITE: RAGAS2024].
- FEVER provides a framework for fact extraction and verification that can be adapted to construction claims [CITE: Thorne2018].

**Step-by-step implementation.**
1. Build a labeled dataset of 100 construction QA pairs and 20–30 contradiction pairs from sample/real docs.
2. Metrics:
   - Retrieval: MRR@5, precision@k
   - Contradiction detection: precision, recall, F1
   - RFI drafting: citation accuracy, human accept rate
3. Regression tests run on every chunking/retrieval change.

**Files.** `backend/benchmarks/`, `data/benchmarks/`.

**Tests.** Benchmark scripts themselves.

**ADR needed.** ADR-017: Benchmark methodology for retrieval and contradiction detection.

---

### 2.14 Frontend / API

**Why it matters.** VDC engineers need a project dashboard, issue reviewer, and RFI editor. The frontend makes the intelligence actionable.

**Research basis.**
- Human-AI interaction guidelines recommend clear confidence communication and source citations [CITE: Amershi2019].
- Lean construction principles require keeping the human in control of final decisions [CITE: PRD-002].

**Step-by-step implementation.**
1. Flask API endpoints:
   - `POST /projects`, `GET /projects`, `GET /projects/<id>/documents`
   - `POST /projects/<id>/ingest`
   - `GET /projects/<id>/chunks`, `/contradictions`, `/rfis`
   - `POST /contradictions/<id>/rfi`
2. Frontend pages:
   - Project list / project dashboard
   - Document viewer with chunk citations
   - Contradiction list with severity/confidence
   - RFI editor with one-click Plane push
3. Use the existing `frontend/` design system.

**Files.** `backend/app.py`, `frontend/js/`, `frontend/index.html`.

**Tests.** API integration tests; frontend smoke tests.

**ADR needed.** ADR-018: API and frontend architecture for Medha.

---

## 3. Sequenced milestones

| Milestone | Weeks | Deliverables | Success metric |
|---|---|---|---|
| **M1: Document foundation** | 1–3 | Ingestion, classification, drawing-index parser, store | Upload a drawing set and see organized sheets in <5 min |
| **M2: Structured retrieval** | 4–5 | Hierarchical chunking, table extraction, cross-refs, retriever | Retrieve relevant section/sheet in top-3 for 80% of test queries |
| **M3: Pre-clash detection** | 6–10 | Claim extraction, contradiction detectors, severity/confidence | ≥60% recall, <30% false-positive on labeled contradictions |
| **M4: RFI workflow** | 11–13 | RFI drafter + Plane push, issue tracker | Draft RFI with correct citations in <2 min |
| **M5: Version monitoring** | 14–16 | Drawing/spec diff, addenda impact, live risk feed | Detect changed sheets and re-check contradictions automatically |
| **M6: Agency dashboard** | 17–20 | Frontend dashboard, cross-project risk view | VDC manager sees project risk at a glance |

---

## 4. Cross-cutting design principles

1. **Deterministic first, LLM second.** Every core extraction step starts with rules/regex/keywords. LLMs are reserved for generation (RFI text) and only where citations are preserved [CITE: Papaioannou2023].
2. **Citations on everything.** Every claim, contradiction, and RFI draft must cite source chunks [CITE: Khattab2022].
3. **Single responsibility per file.** Keep modules small and testable [CITE: AGENTS.md].
4. **Research-backed decisions.** Every new component gets an ADR and inline citations.

---

## 5. Immediate next actions

1. **ADR-012:** Claim extraction design.
2. **Implement** `backend/analysis/claims.py` with numeric and material claim extractors.
3. **ADR-013:** Contradiction detection architecture.
4. **Implement** `backend/analysis/contradictions.py` with numeric mismatch and material conflict detectors.
5. **Label** 20–30 contradiction pairs in `sample_docs/` and `real_construction_docs/` for testing.

---

## 6. References

- [CITE: Fathima2024] Fathima et al., BIM adoption barriers in developing economies.
- [CITE: Papaioannou2023] Papaioannou et al., LLM hallucination in construction documents.
- [CITE: Ejiofor2025] Ejiofor et al., Construction rework costs from document errors.
- [CITE: Li2024] Li et al., RAG pipeline optimization for technical documents.
- [CITE: Günther2024] Günther, Mohr, Wang, Xiao, "Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models," arXiv:2409.04701, 2024.
- [CITE: arXiv2406.13236] Hierarchical RAG: Leveraging Structured Documents, arXiv:2406.13236, 2024.
- [CITE: Moon2021] Moon, Lee, Chi, Oh, "Automated Construction Specification Review with Named Entity Recognition Using Natural Language Processing," J. Constr. Eng. Manag., 2021.
- [CITE: Nahri2025] Nahri et al., "Extracting Structured Requirements from Unstructured Building Technical Specifications for BIM," 2025.
- [CITE: Afzal2024] Afzal, "Improving Request for Information (RFI) Processing in Construction," PhD thesis, UTS, 2024.
- [CITE: Dikmen2025] Dikmen et al., "Automated Construction Contract Analysis for Risk Assessment," 2025.
- [CITE: InspectMind2025] InspectMind AI, "Reducing RFIs with AI," 2025.
- [CITE: Articulate2025] Articulate, "Drawing Revision Comparison & Change Tracking," 2025.
- [CITE: BuildSync2025] BuildSync, "Construction Drawing Change Detection," 2025.
- [CITE: Waidyasekara2026] Waidyasekara et al., "Cloud-Based System for Pre-Tender Drawing Revision Management," 2026.
- [CITE: RAGAS2024] Ragas framework, automated evaluation of RAG, docs.ragas.io.
- [CITE: Thorne2018] Thorne et al., "FEVER: A Large-Scale Dataset for Fact Extraction and VERification," NAACL-HLT, 2018.
- [CITE: Khattab2022] Khattab & Zaharia, DSPy framework for verifiable reasoning.
- [CITE: Friston2010] Friston, Free Energy Principle / active inference.
- [CITE: NCS-US-2024] National CAD Standard, United States National CAD Standard (NCS) V6, sheet numbering conventions.
- [CITE: CSI2024] CSI MasterFormat 2024 Edition.
- [CITE: PRD-002] Medha PRD-002: VDC Agency Workflow Product Requirements.
- [CITE: Amershi2019] Amershi et al., Human-AI interaction guidelines.

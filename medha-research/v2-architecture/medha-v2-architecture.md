# Medha v2 Architecture
## Trayini.ai — VDC Document Intelligence Platform

**Version:** 2.0.0-alpha  
**Date:** 2026-04-24  
**Status:** Implementation in Progress  

---

## 1. Executive Summary

Medha v2 transforms the existing text-only RAG system into a **multi-modal construction document intelligence platform** that understands how VDC professionals actually work: in 3D models, with cross-referenced drawing sets, using tacit domain knowledge, and verifying every claim with traceable sources.

**The 7 Gaps → 6 Implementation Phases:**

| Phase | Gap | Module | Priority |
|-------|-----|--------|----------|
| 1 | Cross-Reference Chains | `v2.doc_graph` | 🔴 Critical — Foundation |
| 2 | Mental Database | `v2.domain_knowledge` | 🔴 Critical — Intelligence |
| 3 | Visual/Spatial Reasoning | `v2.visual_intel` | 🟡 High — Differentiator |
| 4 | Model Intelligence | `v2.bim_connector` | 🟡 High — Moat |
| 5 | Submittal Workflow | `v2.submittal_review` | 🟢 Medium — Revenue |
| 6 | Multi-Stakeholder Neutrality | `v2.tenant_layer` | 🟢 Medium — Scale |

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MEDHA v2 PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  FRONTEND LAYER                                                              │
│  ├─ React/Vue SPA (migrate from vanilla JS)                                 │
│  ├─ Drawing Viewer (PDF.js + SVG overlay for references)                    │
│  ├─ 3D Model Viewer (IFC.js / Three.js)                                     │
│  ├─ Confidence Score Panel (XAI visualization)                              │
│  └─ Submittal Review Dashboard                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  API GATEWAY (Flask / FastAPI)                                               │
│  ├─ Auth & Tenant Resolution (JWT + subdomain routing)                      │
│  ├─ Rate Limiting & Budget Controls                                         │
│  ├─ Request Routing → Orchestrator                                          │
│  └─ Streaming SSE for long-running analysis                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION LAYER (Picocloth Agent Mesh)                                  │
│  ├─ Node-A: Curiosity Brain → Research, cross-reference following           │
│  ├─ Node-B: Executor → Backend ops, RFI drafting                            │
│  ├─ Node-C: Memory Guardian → Knowledge graph persistence                   │
│  ├─ Node-F: Contradiction Detector → Spec-drawing conflict scan             │
│  └─ Fleet Router → Task classification & load balancing                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  CORE INTELLIGENCE MODULES (v2/)                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Doc Graph  │ │  Domain KB  │ │ Visual Intel│ │ BIM Conn.   │           │
│  │  (Phase 1)  │ │  (Phase 2)  │ │  (Phase 3)  │ │  (Phase 4)  │           │
│  │             │ │             │ │             │ │             │           │
│  │ • Sheet idx │ │ • Ontology  │ │ • Symbol    │ │ • IFC parse │           │
│  │ • Ref chain │ │ • Code stds │ │   detect    │ │ • Spatial   │           │
│  │ • Tag→Sched │ │ • Anomaly   │ │ • Dimension │ │   query     │           │
│  │ • Broken    │ │   detect    │ │   extract   │ │ • Clash     │           │
│  │   link det. │ │ • Checklists│ │ • Layout    │ │   detect    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │ Submittal   │ │ Trust & XAI │ │ Tenant      │                           │
│  │ Review      │ │  (Phase 6)  │ │  Layer      │                           │
│  │  (Phase 5)  │ │             │ │ (Phase 6)   │                           │
│  │             │ │ • Conf.     │ │             │                           │
│  │ • Spec comp │ │   scores    │ │ • Project   │                           │
│  │ • Compliance│ │ • Citations │ │   isolation │                           │
│  │   matrix    │ │ • Reasoning │ │ • Template  │                           │
│  │ • Approval  │ │   chains    │ │   library   │                           │
│  │   workflow  │ │ • Human     │ │ • Cross-pj  │                           │
│  │             │ │   escalation│ │   analytics │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                                  │
│  ├─ PostgreSQL + pgvector (documents, embeddings, tenant data)              │
│  ├─ Neo4j / NetworkX (document graph, knowledge graph)                      │
│  ├─ Redis (caching, session state, rate limits)                             │
│  ├─ S3/MinIO (PDFs, IFCs, drawings, submittals)                             │
│  └─ Shared Memory (Picocloth inter-node communication)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  INGESTION PIPELINE                                                          │
│  ├─ Text: pdfplumber / Docling → chunks → embeddings                        │
│  ├─ Visual: PyMuPDF get_drawings() → YOLO-OBB → Donut → graph               │
│  ├─ BIM: IfcOpenShell → geometry + properties → spatial index               │
│  └─ Submittal: Product data extraction → spec attribute matching            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Specifications

### 3.1 Phase 1: Document Graph Engine (`v2/doc_graph.py`)

**Purpose:** Map the reference web that construction professionals navigate instinctively. Every sheet, detail, tag, schedule, and spec section becomes a node in a queryable graph.

**Key Algorithms:**
1. **Drawing Index Parser** — Extract canonical sheet list from G-001/cover sheet
2. **Reference Extractor** — Regex + NLP hybrid for detail callouts, sheet refs, spec sections, tags
3. **Graph Builder** — NetworkX DiGraph with spatial metadata (bbox, page coordinates)
4. **Link Resolver** — Two-pass: collect all references, then resolve targets against drawing index
5. **Broken Link Detector** — Flag unresolved references (major source of real-world RFIs)

**Data Model:**
```python
Node types: Sheet, Detail, SpecSection, Tag, Schedule, Note, Revision
Edge types: CONTAINS, REFERENCES, SCHEDULED_ON, SPECIFIED_IN, REVISION_OF
Attributes: bbox (x0,y0,x1,y1), page_num, font_size, confidence
```

**API Surface:**
- `POST /api/v2/documents/{id}/graph/build` — Build graph from uploaded drawing set
- `GET /api/v2/documents/{id}/graph/references?from_sheet=A-101` — Get outgoing refs
- `GET /api/v2/documents/{id}/graph/broken-links` — List unresolved references
- `GET /api/v2/query/follow-references?query=...` — RAG query that auto-follows refs

**Integration with RAG:**
When the retriever pulls a chunk from Sheet A-101 that says "See Detail 3/A3.2", the graph engine automatically resolves A3.2, retrieves its chunks, and includes them in the context — mimicking how a human coordinator flips through drawings.

---

### 3.2 Phase 2: Domain Knowledge Base (`v2/domain_knowledge.py`)

**Purpose:** Encode the tacit construction knowledge that experienced coordinators carry in their heads — code minimums, standard sizes, typical anomalies, trade-specific checklists.

**Components:**
1. **Construction Ontology** — OWL/RDF-lite representation of building entities
   - Spaces (room types, occupancy classifications)
   - Systems (HVAC, electrical, plumbing, structural, fire protection)
   - Materials (concrete classes, steel grades, insulation R-values)
   - Codes (IBC, ASHRAE 90.1, ACI 318, NFPA 13, NEC)
2. **Anomaly Detection Rules** — Hard-coded + learned heuristics
   - "Column spacing > 30' without intermediate beam → flag"
   - "Window U-factor > 0.30 in climate zone 5 → code violation"
   - "Mechanical room ceiling < 10' → clearance issue"
3. **Trade Checklists** — Structured per-discipline verification lists
   - HVAC: Setpoints, VAV zones, duct sizing, energy recovery
   - Structural: Concrete class, rebar cover, fireproofing rating
   - Electrical: Panel loads, circuit sizing, conduit fill
4. **Standard Sizes Database** — Lookup tables for common components
   - Door/frame sizes, window rough openings, ceiling tile modules

**Integration:**
- Runs as a post-processor on RAG answers: "Your answer says 24" OC framing — that's non-standard. Standard is 16" or 24" OC, but verify with local amendment."
- Flags contradictions by cross-checking extracted values against code tables
- Injects relevant checklist items into prompts based on document type

---

### 3.3 Phase 3: Visual Intelligence (`v2/visual_intel.py`)

**Purpose:** Read drawings visually — not just text OCR. Detect symbols, extract dimensions, understand spatial relationships.

**Architecture (3-Stage Hybrid):**
```
Stage 1: Layout Segmentation (YOLOv8-det) → detect regions (views, title blocks, notes)
Stage 2: Rotated Annotation Detection (YOLOv11-OBB) → dimensions, leaders, callout bubbles
Stage 3: OCR-Free Parsing (Florence-2 / Donut) → structured JSON from cropped regions
Stage 4: Spatial Graph (GNN-style adjacency) → "this duct is above this beam"
```

**Scope for v2-alpha:**
- Title block extraction (project name, sheet number, revision)
- Drawing index parsing from scanned cover sheets
- Detail callout bubble detection (link text to spatial location)
- Dimension line extraction (value + what it measures)
- Symbol detection: door tags, window tags, section markers, elevation markers

**Deferred to v2-beta:**
- Full P&ID symbol recognition
- GD&T frame parsing
- 3D reconstruction from 2D views

---

### 3.4 Phase 4: BIM Connector (`v2/bim_connector.py`)

**Purpose:** Bridge the 2D document world with 3D model reality. Construction professionals spend 50%+ of their time in Revit/Navisworks — Medha must meet them there.

**Architecture:**
```
IFC File → IfcOpenShell → Geometry + Properties → Spatial Index (R-tree)
                              ↓
                    Knowledge Graph (Neo4j)
                              ↓
                    Natural Language Queries via MCP4IFC pattern
```

**Capabilities:**
1. **IFC Ingestion** — Parse IFC4 ADD2 TC1, extract elements, properties, relationships
2. **Spatial Querying** — "What beams are within 2 feet of duct X?"
3. **Clash Detection Lite** — Simple AABB intersection for flagged elements
4. **Drawing-to-Model Linking** — Map sheet tags to IFC GUIDs via property matching
5. **Property Extraction** — Material, dimensions, fire rating, load capacity

**Integration Pattern:**
- Documents provide the "what should be" (specs, drawings)
- IFC provides the "what is modeled" (BIM)
- Medha compares both to find gaps

---

### 3.5 Phase 5: Submittal Review (`v2/submittal_review.py`)

**Purpose:** Automate the most time-consuming CA task — comparing contractor submittals against specifications.

**Workflow:**
1. **Spec Requirement Extraction** — Parse spec section into structured requirements
   - Performance criteria, material standards, dimensional tolerances, finishes
2. **Submittal Attribute Extraction** — Read product data sheets, shop drawings
   - Model numbers, dimensions, ratings, certifications
3. **Compliance Matrix** — Row = requirement, Column = submittal value, Cell = pass/fail/unknown
4. **Review Report Generation** — Draft "Approved / Approved as Noted / Revise & Resubmit"

**Key Innovation:**
Link submittal findings back to the document graph. If a submittal references Detail A/A3.2, Medha can verify that the detail actually specifies the submitted product.

---

### 3.6 Phase 6: Trust & XAI + Tenant Layer (`v2/trust_engine.py`, `v2/tenant_layer.py`)

**Trust Engine:**
- **Confidence Scoring** — Per-retrieval cosine similarity → calibrated 0-1 score
- **Citation Provenance** — Every claim linked to source document, page, bbox, exact text
- **Reasoning Chains** — Chain-of-thought extraction showing how answer was constructed
- **Human Escalation Triggers** — Auto-escalate when: confidence < 0.7, contradiction detected, novel spec section encountered
- **Counterfactual Explanations** — "If this drawing showed 12" walls instead of 8", the fire rating conclusion would change"

**Tenant Layer:**
- **Project Isolation** — Row-level security in PostgreSQL, separate graph namespaces
- **Template Library** — System templates (commercial, healthcare, residential) + agency custom templates
- **Cross-Project Analytics** — Anonymized pattern learning: "Projects like yours typically have 3.2 contradictions per drawing set"
- **White-Label Config** — Per-tenant branding, domain routing, feature flags

---

## 4. Data Architecture

### 4.1 PostgreSQL Schema (Core)

```sql
-- Tenants (VDC agencies)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    branding JSONB DEFAULT '{}',
    feature_flags JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects (per tenant)
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name TEXT NOT NULL,
    template_id UUID,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents (PDFs, IFCs, submittals)
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    tenant_id UUID REFERENCES tenants(id),
    filename TEXT NOT NULL,
    doc_type TEXT NOT NULL, -- 'drawing', 'spec', 'ifc', 'submittal'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Text chunks with embeddings
CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    tenant_id UUID REFERENCES tenants(id),
    content TEXT NOT NULL,
    embedding vector(768),
    page_num INT,
    bbox JSONB, -- {x0, y0, x1, y1}
    metadata JSONB DEFAULT '{}'
);
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_tenant ON chunks(tenant_id, document_id);

-- Graph edges (document references)
CREATE TABLE doc_edges (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    tenant_id UUID REFERENCES tenants(id),
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    confidence FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_edges_project ON doc_edges(project_id, source_id, target_id);
```

### 4.2 Neo4j Graph Schema

```cypher
// Nodes
(:Sheet {number: "A-101", title: "First Floor Plan", page: 1})
(:Detail {number: "3", sheet: "A3.2", description: "Wall Section"})
(:SpecSection {csi: "033000", title: "Cast-in-Place Concrete"})
(:Tag {id: "D-101", type: "door"})
(:Schedule {type: "door", sheet: "A-601"})

// Edges
(:Sheet)-[:REFERENCES {bbox: [...], context: "See Detail 3/A3.2"}]->(:Detail)
(:Tag)-[:SCHEDULED_ON]->(:Schedule)
(:Detail)-[:SPECIFIED_IN]->(:SpecSection)
```

---

## 5. API Evolution

### v1 API (Current)
```
POST /api/documents       → Upload PDF
POST /api/query           → RAG query
POST /api/contradictions  → Scan for conflicts
GET  /api/documents/{id}  → Get document
```

### v2 API Additions
```
# Document Graph
POST /api/v2/projects/{pid}/graph/build
GET  /api/v2/projects/{pid}/graph
GET  /api/v2/projects/{pid}/graph/broken-links
GET  /api/v2/projects/{pid}/graph/follow?from=A-101&depth=2

# Visual Intelligence
POST /api/v2/documents/{did}/visual/extract
GET  /api/v2/documents/{did}/visual/symbols
GET  /api/v2/documents/{did}/visual/dimensions

# BIM Connector
POST /api/v2/projects/{pid}/bim/upload
GET  /api/v2/projects/{pid}/bim/elements
GET  /api/v2/projects/{pid}/bim/query?q=What+beams+are+near+duct+3A
POST /api/v2/projects/{pid}/bim/clash-scan

# Submittal Review
POST /api/v2/projects/{pid}/submittals/upload
GET  /api/v2/projects/{pid}/submittals/{sid}/compliance
GET  /api/v2/projects/{pid}/submittals/{sid}/matrix

# Trust & XAI
GET  /api/v2/query/{qid}/confidence
GET  /api/v2/query/{qid}/citations
GET  /api/v2/query/{qid}/reasoning

# Tenant Management
POST /api/v2/tenants
GET  /api/v2/tenants/{tid}/projects
POST /api/v2/tenants/{tid}/templates
```

---

## 6. Implementation Roadmap

### Sprint 1: Foundation (Phase 1)
- [ ] `v2/doc_graph.py` — Reference extractor + graph builder
- [ ] `v2/reference_patterns.py` — Regex library for construction references
- [ ] `v2/drawing_index.py` — Drawing index parser
- [ ] Integrate graph into RAG query pipeline
- [ ] Tests with sample drawing sets

### Sprint 2: Intelligence (Phase 2)
- [ ] `v2/domain_knowledge.py` — Ontology loader + anomaly detector
- [ ] `v2/checklists/` — Trade-specific JSON checklists
- [ ] `v2/code_standards/` — Minimum code requirements database
- [ ] Integration with contradiction detection

### Sprint 3: Vision (Phase 3)
- [ ] `v2/visual_intel.py` — Title block + drawing index OCR
- [ ] `v2/symbol_detector.py` — Callout bubble + tag detection
- [ ] `v2/dimension_extractor.py` — Dimension line parsing
- [ ] Frontend drawing viewer with overlays

### Sprint 4: BIM (Phase 4)
- [ ] `v2/bim_connector.py` — IfcOpenShell wrapper
- [ ] `v2/spatial_index.py` — R-tree for geometry queries
- [ ] Drawing-to-IFC tag linking
- [ ] Clash detection prototype

### Sprint 5: Workflow (Phase 5)
- [ ] `v2/submittal_review.py` — Spec requirement extractor
- [ ] `v2/compliance_matrix.py` — Attribute comparison engine
- [ ] Review report generator
- [ ] Approval workflow state machine

### Sprint 6: Scale (Phase 6)
- [ ] `v2/trust_engine.py` — Confidence scoring + reasoning chains
- [ ] `v2/tenant_layer.py` — Multi-tenant project isolation
- [ ] Template library + instantiation
- [ ] White-label theming engine

---

## 7. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | Flask → FastAPI | Async support for streaming, auto-docs |
| Embeddings | `all-mpnet-base-v2` → `BAAI/bge-large-en-v1.5` | Better retrieval quality |
| Vector DB | pgvector (current) → pgvector + ivfflat | Already works, scales to 100K+ docs |
| Graph DB | NetworkX (in-memory) + Neo4j (persist) | NetworkX for speed, Neo4j for complex queries |
| PDF Parsing | pdfplumber + PyMuPDF + Docling | Hybrid: pdfplumber for text, PyMuPDF for links/drawings, Docling for structure |
| Visual AI | YOLOv8 + Florence-2 | Best accuracy/size tradeoff |
| BIM | IfcOpenShell + trimesh | Industry standard + Python-native |
| LLM | Groq/Llama-3.3-70B → Grok-4 | Fast + high quality |
| Local LLM | Qwen2.5-3B-Instruct (GGUF) | Fallback for sensitive data |
| Cache | Redis | Session, rate limit, embedding cache |
| Storage | S3/MinIO | PDFs, IFCs, generated reports |
| Frontend | Vanilla JS → Vue 3 + Tailwind | Component-based, drawing viewer support |
| 3D Viewer | IFC.js + Three.js | Browser-native IFC rendering |

---

## 8. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Visual AI accuracy too low for production | Medium | High | Start with title blocks + callouts only; defer full symbol recognition |
| IFC parsing performance on large models | Medium | High | Lazy loading + spatial partitioning; process only referenced elements |
| Multi-tenant data leakage | Low | Critical | PostgreSQL RLS + defense-in-depth tenant filtering + integration tests |
| LLM hallucination on technical specs | Medium | High | XAI layer + human-in-the-loop + source citation enforcement |
| Integration complexity between 6 modules | High | Medium | Clean API boundaries between modules; each module independently testable |
| VDC agency adoption friction | Medium | High | White-label from day 1; no workflow changes required; pilot with friendly agency |

---

## 9. Success Metrics

| Metric | v1 Baseline | v2 Target |
|--------|------------|-----------|
| Document types supported | Text PDFs only | PDFs, DOCX, IFC, scanned drawings, submittals |
| RAG source citations | Document name only | Document + page + exact text + bounding box |
| Cross-reference following | None | Auto-follow 3 levels deep |
| Contradiction detection | Text-only | Text + dimensional + spatial |
| RFI drafting time | 60-120 min | 10-20 min (with human review) |
| Submittal review time | 45-120 min | 10-15 min (with human approval) |
| Code compliance checking | None | Auto-check against IBC + ASHRAE + ACI + NFPA |
| Projects per VDC agency | 1 isolated | Template reuse across 10+ projects |
| Time-to-first-value | Hours | Minutes (template instantiation) |

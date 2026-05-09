# Trelo Labs — VDC Document Intelligence

> **The first AI product you can sell to VDC agencies TODAY.**

White-label AI document intelligence that reads construction drawings, specs, RFIs, and submittals — so VDC agencies can re-sell intelligent document analysis to their GC clients.

---

## What It Does (3 Features)

### 1. Ask Your Documents (Multi-Document RAG)
Upload an entire project's document set — drawings, specs, RFIs, submittals, addenda — and ask natural language questions.

> *"What is the HVAC setpoint for office spaces?"*
> → *"Office spaces: Heating 70°F, Cooling 74°F (setback 65°F/78°F after hours). Sources: MECH_SPEC_HVAC.txt"*

### 2. Auto-Draft RFI Responses
Paste an RFI question. The AI scans all project documents and drafts a professional response with cited sources.

> *"What is the required concrete strength for columns?"*
> → Auto-drafted RFI-006 with references to STRUCT_SPEC.txt, ACI 318 mix designs, and 5,000 psi confirmation.

### 3. Detect Drawing-Spec Contradictions
AI automatically scans drawings and specifications to flag dimension mismatches, conflicting requirements, and code discrepancies before they reach the field.

> Found: Mechanical room ceiling height = 12 feet (drawing) vs ductwork requiring 18" plenum depth (spec) → potential coordination conflict.

---

## Why VDC Agencies Will Buy This

| Pain Point | Current State | With Trelo Labs |
|-----------|---------------|-----------------|
| Manual spec review | 10-15 hrs/project | 3 minutes |
| RFI response drafting | 2-4 hrs per RFI | 30 seconds |
| Drawing-spec cross-check | Ad-hoc, often missed | Automated scan before submission |
| Document search | Ctrl+F through 50 PDFs | Natural language query |

**ROI for a VDC agency:** If one BIM coordinator spends 15 hrs/week on document review at $75/hr, that's **$1,125/week**. Trelo Labs cuts this to **$112/week** — a **10x cost reduction**.

---

## Pricing (White-Label for VDC Agencies)

| Tier | Price | What's Included |
|------|-------|-----------------|
| **Pilot** | $500/mo per project | 1 project, up to 50 docs, Query + RFI draft |
| **Agency** | $3,000/mo unlimited | Unlimited projects + docs, contradiction detection, white-label branding |
| **Enterprise** | Custom | On-premise, custom model training, API access |

The **$3,000/mo Agency tier** is the sweet spot. VDC agencies already charge GCs $3K–$5K/month for coordination. They can bundle Trelo Labs as a "premium AI analytics" add-on for $1,000/mo — netting them **$2,000/mo pure margin per client**.

---

## Competitive Landscape

| Competitor | Target | Price | Gap |
|-----------|--------|-------|-----|
| **Pelles.ai** | Trade contractors | ~$1,999/yr | Not white-label, not for VDC agencies |
| **Procore Copilot** | GCs (enterprise) | Enterprise | VDC agencies can't re-sell it |
| **Constructable** | Mid-tier GCs | Per-project | No VDC agency partnership model |
| **Buildots** | Large GCs / Owners | Custom | Progress tracking, not document intelligence |
| **Arphie** | Enterprise sales teams | Custom | RFI response only, no construction docs |
| **Trelo Labs** | **VDC Agencies (white-label)** | **$3K/mo** | **The ONLY white-label AI document intelligence for VDC** |

---

## Tech Stack

- **Backend:** Python Flask + sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **Embeddings:** Cosine similarity vector search over chunked documents
- **Document Parsing:** pdfplumber (PDF), python-docx (DOCX), plain text
- **Frontend:** Vanilla HTML/JS + Tailwind CSS (no build step)
- **Model Strategy:** RAG (Retrieval-Augmented Generation) — no hallucination risk, every answer is grounded in uploaded documents

---

## How to Run the Demo

```bash
# 0. Optional: build an isolated retrieval env
./backend/bootstrap_retrieval_env.sh
source venv-retrieval/bin/activate

# 1. Start the backend
cd vdc-document-intelligence
python3 backend/app.py

# 2. Seed with sample data (optional)
python3 seed_demo.py

# 3. Open frontend
open frontend/index.html
# Or serve via Python:
cd frontend && python3 -m http.server 8080
```

Backend runs on `http://localhost:5001`
Frontend runs on `http://localhost:8080`

## Retrieval Backends

Medha now supports a pluggable retrieval seam:

- `filesystem` - current local baseline
- `chroma` - embedded by default, server/cloud optional
- `pgvector` - local Postgres + pgvector or external Postgres

The primary `/query` and `/draft-rfi` flows now call the store's native
`search_project(...)` path when the backend supports it. That means the benchmark
query latency now measures backend-native retrieval instead of always loading the
full embedding matrix into Python first.

Local pgvector dev service:

```bash
docker compose -f docker-compose.pgvector.yml up -d
```

Benchmark all backends:

```bash
python3 benchmark_retrieval_backends.py --backends filesystem chroma pgvector
```

Optional local-LLM fallback dependencies remain separate:

```bash
pip install -r backend/requirements-local-llm.txt
```

See [docs/research/retrieval-backends-benchmark.md](docs/research/retrieval-backends-benchmark.md) for setup details.

---

## What to Demo in a Sales Call

1. **Upload 5 sample docs** (30 seconds)
2. **Ask: "What is the HVAC setpoint?"** → Shows cited answer from MECH_SPEC_HVAC.txt
3. **Ask: "What is the concrete strength for columns?"** → Shows 5,000 psi from STRUCT_SPEC.txt
4. **Draft RFI:** "What is the required concrete strength for columns?" → Shows auto-drafted RFI-006
5. **Run Contradiction Scan** → Flags potential drawing-spec conflicts
6. **Show Pricing** → $3K/mo Agency tier = 10x ROI for the VDC agency

**Total demo time: 4 minutes.**

---

## Roadmap (What Comes Next)

| Phase | Feature | Timeline |
|-------|---------|----------|
| **Now** | Document Q&A + RFI draft + contradiction detection | ✅ Built |
| **Month 1** | IFC/BIM model ingestion (IfcOpenShell → knowledge graph) | In planning |
| **Month 2** | Clash detection narrative auto-generation | In planning |
| **Month 3** | Drawing annotation AI (auto-tag elements per spec) | In planning |
| **Month 6** | White-label portal (VDC agency branding, client login) | In planning |

---

## The Ask

**We are looking for 3 VDC agencies to pilot this at $500/mo for 90 days.**

In exchange, we need:
- Real project documents (under NDA)
- Weekly feedback calls
- Case study permission (anonymized)

**Target pilots:** Powerkh, BIMAGE, The BIM Factory

---

*Built by Trelo Labs. AI infrastructure for the construction semantics layer.*
*Graph-powered. RAG-grounded. VC-backable.*

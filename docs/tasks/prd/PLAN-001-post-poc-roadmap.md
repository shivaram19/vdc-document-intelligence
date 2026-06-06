# PLAN-001: Post-PoC Roadmap — From Reflection Dataset to Production Memory Model

**Date:** 2026-05-03
**Status:** Draft — Pending PoC validation
**Scope:** Everything that happens after the 5-step reflection synthesis pipeline produces its first `reflections.jsonl`

---

## 0. What the PoC Proves (or Disproves)

The PoC runs the 5-step pipeline on 5–10 sample construction documents and produces a `reflections.jsonl` file. Before doing anything else, we evaluate the output against these gates:

| Gate | Pass Criteria | Fail Criteria |
|------|--------------|---------------|
| **G1: Cross-document contradictions detected** | ≥20% of cross-document reflections (Step 5) identify actual contradictions or mismatches between documents | All cross-document reflections are trivial agreements; no contradictions surfaced |
| **G2: Entity relationships preserved** | Entity-surfacing pairs (Step 4) allow identifying a spec section, drawing, or system from partial attributes | Entity-surfacing pairs are too vague or don't encode enough attributes |
| **G3: Self-containment verified** | ≥90% of Step 3 output is marked "kept" or "rewritten"; <10% discarded | >30% discarded due to ambiguity; pipeline generates low-quality data |
| **G4: Cost feasibility** | Total API cost for 10 documents < $5 | Cost exceeds $15 for 10 documents; not scalable |

**Decision:** Only proceed to Phase 2 if G1 AND G2 pass. If G3 fails, refine prompts and retry. If G4 fails, switch to a cheaper model (e.g., `gpt-4o-mini` → local Qwen2.5-7B via vLLM).

---

## 1. Phase 2: Scale to Dubai Corpus (4–6 Weeks)

### 1.1 Collect Real Construction Documents

**Target:** 50–100 documents representing a real Dubai construction project's document set.

| Document Type | Quantity | Source |
|--------------|----------|--------|
| Specifications (Div 21–28) | 5–8 sections | Public spec templates + DM-mandated projects |
| Architectural drawings | 10–15 sheets | Sample projects or anonymized from outreach contacts |
| Structural drawings | 5–10 sheets | Same |
| MEP drawings | 5–10 sheets | Same |
| RFI log | 20–30 entries | Anonymized from outreach interviews |
| Submittal register | 10–15 entries | Same |
| Clash report | 2–3 reports | Anonymized Navisworks exports |
| BEP | 1–2 | Public templates (Penn State, NATSPEC) |

**How to acquire:**
1. Ask interview contacts (Kalyan Vaidyanathan, interviewees from BFS-019 outreach) for anonymized document samples
2. Use public Dubai construction documents from DM portal or contractor case studies
3. Create synthetic but realistic documents based on interview findings

### 1.2 Run 5-Step Pipeline at Scale

**Estimated cost:** $30–80 in API calls (50–100 documents × ~3 calls/doc)

**Output:** `dubai_reflections.jsonl` (~2,000–5,000 reflection QA pairs)

**Quality control:**
- Manual review of 50 random reflections by you (the founder)
- Check: Do contradictions match your understanding from interviews?
- Check: Are cross-document relationships accurate?
- Iterate on prompts if quality is <80% accurate

### 1.3 Train the MEMORY Model

**Model:** Qwen2.5-14B-Instruct (as in MeMo paper's best config)

**Training setup:**
```bash
# Using Unsloth for memory-efficient fine-tuning
pip install unsloth

python train_memory_model.py \
  --train_file data/reflections/dubai_reflections.jsonl \
  --model_name Qwen/Qwen2.5-14B-Instruct \
  --output_dir models/memo-memory-qwen14b \
  --num_train_epochs 3 \
  --per_device_train_batch_size 4 \
  --learning_rate 2e-5 \
  --max_seq_length 4096
```

**Estimated compute:** ~24 GPU-hours on H100 (or ~48 hours on A100)

**Cost alternatives:**
| Option | Cost | Time |
|--------|------|------|
| Local H100 (if available) | $0 (sunk cost) | 24 hours |
| RunPod / Vast.ai H100 | ~$50–80 | 24 hours |
| Google Colab Pro+ A100 | ~$50/month subscription | 48 hours |
| Together.ai / Fireworks fine-tuning API | ~$100–200 | Managed |

### 1.4 Evaluate: MeMo vs. RAG Baseline

**Test set:** 20–30 hand-crafted queries based on interview findings

| Query Type | Example | What It Tests |
|-----------|---------|---------------|
| Contradiction | "Does the mechanical spec agree with drawing A-101 on duct insulation?" | Cross-document consistency |
| Entity ID | "Which spec section governs the 2-hour fire-rated MEP riser shaft?" | Entity surfacing |
| Impact | "If we change the fire rating in FPS-211313 §2.3.A, what else is affected?" | Cross-document dependency |
| Multi-hop | "Which RFI was triggered by the clash between the HVAC duct and structural beam on Level 7?" | Multi-step reasoning |

**Baselines to compare:**
1. **Current Medha RAG** (Chroma + embedding model + stuff into prompt)
2. **MeMo with MEMORY model** (Qwen2.5-14B trained on reflections)
3. **Perfect Retrieval** (gold evidence docs stuffed into prompt — upper bound)

**Metric:** Accuracy judged by GPT-4o against ground-truth answers (same as MeMo paper)

**Pass criteria for Phase 3:** MeMo achieves >10% higher accuracy than RAG on contradiction and impact queries.

---

## 2. Phase 3: Production Integration (8–12 Weeks)

### 2.1 Architecture Changes

```
Current Medha:
  Frontend → Backend API → Embed query → Chroma/pgvector retrieve →
  Stuff chunks into LLM prompt → Generate answer

MeMo-enhanced Medha:
  Frontend → Backend API → EXECUTIVE (Grok/Claude/GPT-4) decomposes query →
  Multi-turn protocol queries MEMORY model (Qwen2.5-14B served via vLLM) →
  EXECUTIVE synthesizes final answer
```

**New components to build:**

| Component | Purpose | Technology |
|-----------|---------|------------|
| **MEMORY inference server** | Serve trained Qwen2.5-14B model | vLLM or TGI (Text Generation Inference) |
| **Multi-turn protocol handler** | Orchestrate EXECUTIVE ↔ MEMORY dialogue | Python async (FastAPI/Flask) |
| **Reflection re-generator** | Re-run Steps 1–5 when new documents arrive | Scheduled job (Celery / cron) |
| **Model merge worker** | Merge new MEMORY models with existing | Python + mergekit (TIES/DARE) |

### 2.2 Incremental Update Workflow

Construction documents change constantly. MeMo supports this via **model merging**:

```
Week 0: Train MEMORY-v1 on Project A documents
Week 4: New drawings arrive for Project A
        → Run Steps 1–5 on new docs only
        → Train MEMORY-v1-delta on new reflections
        → Merge MEMORY-v1 + MEMORY-v1-delta via TIES (ρ=0.3)
        → Deploy merged model as MEMORY-v2
Week 8: Project B documents arrive
        → Same pipeline
        → Merge MEMORY-v2 + MEMORY-B-delta
```

**Compute savings:** 33% vs full retrain at K=2; 5.5× at K=10 (per MeMo paper Table 6)

### 2.3 Monitoring & Observability

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| MEMORY model latency (p95) | <500ms | >1s |
| Multi-turn protocol turns per query | <5 | >10 |
| Contradiction detection precision | >85% | <75% |
| Contradiction detection recall | >80% | <70% |
| User-reported false positive rate | <5% | >10% |

---

## 3. Parallel Workstreams (Happening Throughout)

### 3.1 Human Validation (Weeks 1–8, ongoing)

**Do NOT stop talking to people just because we're building tech.**

| Week | Target | Deliverable |
|------|--------|-------------|
| 1–2 | Warm intros (Kalyan, Adithya, Vishnu) | 3–5 conversations |
| 3–4 | Cold outreach to Tier 1 (Emaar, ALEC, ASGC, BESIX) | 5–8 conversations |
| 5–6 | Tier 2 + VDC agencies | 5–8 conversations |
| 7–8 | Follow-ups, pattern validation | Synthesis interview report |

**After every 5 interviews:** Update PRD with real findings. Refine MeMo training data based on actual pain points.

### 3.2 UML / System Diagrams (Weeks 4–6)

**Draw these after you have 10+ interview insights + PoC results:**

| Diagram | Purpose | When |
|---------|---------|------|
| **Information Flow Diagram** | How docs move between VDC agency and construction company | After 5 interviews |
| **System Architecture Diagram** | Medha components: Frontend, Backend API, EXECUTIVE, MEMORY, Document Ingestion | After PoC success |
| **Data Model Diagram** | Reflection structure, document entity relationships, version graph | After Dubai corpus training |
| **Sequence Diagram** | Multi-turn protocol: EXECUTIVE ↔ MEMORY message flow | After Phase 2 evaluation |

**Tools:** Draw.io, PlantUML, or Mermaid in Markdown.

### 3.3 Competitive Positioning (Weeks 6–8)

**Research how existing tools would handle the same queries:**

| Tool | Test | What to Learn |
|------|------|---------------|
| Procore BIM | Upload same docs, ask contradiction questions | Where does it fail? |
| ACC Model Coordination | Same | What's missing? |
| BIMcollab / Revizto | Same | How is their issue tracking limited? |
| Manual workflow (interviewee) | Ask them to solve the same problem | Baseline human performance |

**Output:** Benchmark report showing Medha (MeMo) vs. incumbents on 10 standard queries.

---

## 4. Decision Gates

```
PoC (Week 1–2)
    └── G1 & G2 pass? ──YES──► Phase 2 (Week 3–8)
    └── NO ──► Refine prompts, retry, or pivot back to RAG

Phase 2 Evaluation (Week 8)
    └── MeMo > RAG +10%? ──YES──► Phase 3 (Week 9–20)
    └── NO ──► Hybrid approach: RAG for simple queries, MeMo for cross-document

Phase 3 Beta (Week 16–20)
    └── 3 pilot users (VDC coordinators) using Medha daily?
    └── NPS > 30? ──YES──► Fundraising / commercial launch prep
    └── NO ──► Iterate on UX, retrain MEMORY with user feedback
```

---

## 5. Resource Estimate

| Phase | Time | Money | People |
|-------|------|-------|--------|
| **PoC** | 1–2 weeks | $50–100 (API) | You + me (agent) |
| **Phase 2** | 4–6 weeks | $100–300 (API + GPU) | You + part-time ML engineer |
| **Phase 3** | 8–12 weeks | $500–1,500 (infra) | You + ML engineer + frontend dev |
| **Total to beta** | ~20 weeks | ~$700–2,000 | 2–3 people |

---

## 6. What You Should Do This Week

1. **Monday:** Message Kalyan Vaidyanathan on LinkedIn (copy from OUTREACH-001)
2. **Tuesday:** Text Vishnu Valmiki about Himal Constructions + intros
3. **Wednesday:** Set up API key, run PoC on `sample_docs/`, inspect `reflections.jsonl`
4. **Thursday:** If PoC passes G1/G2, start collecting real Dubai documents for Phase 2
5. **Friday:** Document 3 things you learned from the PoC output; update this plan

---

## 7. What I (the Agent) Will Do Next

| When | Task |
|------|------|
| After PoC runs | Analyze `reflections.jsonl`; suggest prompt improvements |
| After 5 interviews | Synthesize interview findings into updated PRD persona insights |
| After Phase 2 evaluation | Write ADR-010: MeMo architecture decision |
| After UML diagrams requested | Generate PlantUML/Mermaid diagrams from PRD requirements |
| Continuously | Research papers, benchmark data, competitive intelligence as needed |

---

*This plan is a living document. It is updated after every PoC run, interview batch, and evaluation.*

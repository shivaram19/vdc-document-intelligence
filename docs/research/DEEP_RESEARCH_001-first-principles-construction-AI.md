# Deep Research #001: Construction Document Intelligence — First Principles
**Research Question:** Why do current AI approaches fail at cross-document contradiction detection in construction, and what would a first-principles solution look like?

---

## 1. First Principles: What Is the Actual Problem?

### Assumption to question
Most construction AI tools frame the problem as: *"How do we search documents faster?"*

### First-principles reframing
The problem is not search speed. The problem is **semantic consistency maintenance across a distributed, evolving document system**.

At its core, a construction project is a graph of commitments:
- Owner requirements → specifications
- Specifications → drawings
- Drawings → submittals
- Submittals → RFIs
- RFIs → addenda
- Addenda → revised drawings/specs

Each node changes over time. Contradictions occur when a change in one node is not propagated to related nodes.

**Root cause:** Construction documents are not a database. They are a loosely coupled set of PDFs, DWGs, and emails with no formal dependency graph.

---

## 2. What Does the Research Say?

### 2.1 Cost of Document Errors
- [Ejiofor2025] Construction rework costs from document errors — errors in documents are a primary contributor to rework.
- [Papaioannou2023] LLM hallucination in construction documents — even advanced LLMs produce false claims when reasoning over technical documents.
- Industry reports: Rework costs 5-15% of total project value; 25-50% of rework is attributed to design/documentation errors.

### 2.2 Limits of RAG
Standard RAG pipelines:
1. Chunk documents
2. Embed chunks
3. Retrieve top-k chunks
4. Generate answer from retrieved context

**Why this fails for contradiction detection:**
- Retrieval is similarity-based, not dependency-based
- Two contradictory specs may not be semantically similar (e.g., "duct shall be 1-hour rated" vs "duct shall be 2-hour rated")
- Chunking destroys cross-document context
- No temporal/version awareness

### 2.3 State of the Art in Document Reasoning
Recent advances to consider:
- **MeMo (Memory as a Model)** [Quek2025/2605.15156]: Train a dedicated model on the corpus so knowledge lives in the model, not retrieval.
- **GraphRAG / Knowledge Graph RAG**: Build entity-relationship graphs before retrieval.
- **Long-context LLMs**: Gemini 1.5 Pro (2M tokens), Claude 3 Opus (200K tokens), GPT-4o (128K tokens).
- **Agentic systems**: Multi-agent debate, verification, and consensus.
- **Domain-specific fine-tuning**: Models trained on construction text outperform general models.

---

## 3. First-Principles Questions We Should Ask

### Q1. Is contradiction detection a retrieval problem or a reasoning problem?
**Current approach:** RAG treats it as retrieval.
**First-principles view:** It is a **consistency checking** problem. You need to:
1. Parse claims from documents
2. Build a claim graph (what claims exist about the same entity?)
3. Detect logical conflicts (same entity, different value, overlapping scope)
4. Resolve which claim is authoritative (version, discipline hierarchy, addenda)

**Implication:** A graph-based representation beats vector retrieval for this task.

### Q2. What is the right unit of analysis?
**Current approach:** Document chunks.
**First-principles view:** The right unit is a **parametric claim** — a structured triple like:
```
(entity: "fire-rated duct in corridor 3B",
 attribute: "fire rating",
 value: "2 hours",
 source: "spec_section_712_v3.pdf",
 effective_date: "2026-03-15",
 discipline: "fire_protection")
```

Documents are just carriers of claims. The AI should extract and compare claims.

### Q3. Do we need a general model or a domain model?
**Current approach:** Use general-purpose embeddings (all-mpnet-base-v2) and LLMs (GPT-4).
**First-principles view:** Construction language is highly specialized. Domain models consistently outperform general models on technical benchmarks.

**Implication:** Fine-tune embeddings and possibly a small LLM on construction specs, RFIs, and code language.

### Q4. Should the system answer questions or prevent errors?
**Current approach:** Chatbot over documents.
**First-principles view:** The highest value is **preventive** — catch contradictions before construction, not explain them after.

**Implication:** The product should integrate into the document review workflow (submittals, addenda, RFIs) not just be a Q&A tool.

### Q5. What is the real bottleneck?
Hypotheses:
- Data acquisition (hard to get real project docs) — yes, confirmed
- Model reasoning capability — partially
- Prompt engineering — no, this is surface-level
- Representation of documents as claim graphs — likely the deepest issue

---

## 4. Cutting-Edge Research Directions (2025-2026)

### Direction A: Parametric Memory for Construction
Instead of retrieving chunks, train a model to memorize parametric claims about project entities.
- Input: document set
- Output: structured claim graph + contradiction detection
- Inspired by: MeMo, but adapted for construction parametrics

### Direction B: Multimodal Document Understanding
Construction documents include:
- Text specs
- Drawings (PDF/DWG)
- Schedules and tables
- Addenda and markups

Future system must parse all modalities and cross-reference them.
- Relevant: VLMs for drawings (Claude Vision, GPT-4V)
- Relevant: VFEAgent — VLM transforms blueprints into FEA simulations

### Direction C: Active Compliance Checking
Instead of passive Q&A, actively check new documents against existing commitments:
- New addendum arrives → compare against all active specs and drawings
- New RFI answer → check if it contradicts previous answers
- New submittal → verify against spec requirements

This is closer to a CI/CD system for documents.

### Direction D: Human-in-the-Loop Consensus
Use AI to surface potential contradictions, but let domain experts adjudicate. Track adjudication history to improve the model.

---

## 5. Critical Evaluation of Medha's Current Approach

### What Medha does well
- MeMo-based pipeline (memory-as-model) instead of pure RAG
- Reflection synthesis with cross-document step
- Real document testing
- Parallel performance optimization
- Research-backed citations

### What needs first-principles revision
1. **Chunking is destructive** — should move toward claim extraction
2. **General embeddings** — need construction-tuned embeddings
3. **Synthetic contradictions** — useful but not sufficient; need real project addenda
4. **Cognitive system disconnected** — highest-leverage asset not integrated
5. **No active monitoring** — system is reactive, not preventive

---

## 6. Proposed First-Principles Architecture

```
Document Ingestion
    ↓
Multi-modal Parser (text + drawings + tables)
    ↓
Claim Extractor (entity-attribute-value-source-version)
    ↓
Parametric Knowledge Graph
    ↓
Consistency Engine (detects conflicts, overlaps, version mismatches)
    ↓
Human Review Queue (ranked by severity and confidence)
    ↓
Closed-Loop Learning (adjudication improves model)
```

Key differences from RAG:
- Represents knowledge as structured claims, not chunks
- Explicit version control and effective dates
- Conflict detection is a graph operation, not similarity search
- Designed for prevention, not just Q&A

---

## 7. Research Gaps to Fill

1. **Public benchmark** for construction document contradiction detection
2. **Construction-tuned embedding model** for specs and drawings
3. **Claim extraction model** fine-tuned on construction specs
4. **Cross-modal contradiction detection** (text vs drawing annotations)
5. **Economic model** linking contradiction detection to rework cost savings

---

## 8. Immediate Experiments to Run

1. Replace chunk-based extraction with claim-based extraction on Kentucky HVAC
2. Test construction-tuned embeddings (e.g., fine-tuned all-MiniLM or sentence-transformers on specs)
3. Build a minimal claim graph and detect conflicts programmatically
4. Test Claude Vision on a drawing + spec pair for cross-modal contradiction
5. Interview 5 VDC coordinators about their actual contradiction-finding workflow

---

## 9. Conclusion

The construction document problem is not a search problem. It is a **consistency maintenance problem** over a distributed, evolving commitment graph.

Current RAG approaches fail because they optimize the wrong thing (retrieval similarity). A first-principles solution requires:
1. Structured claim extraction
2. Parametric knowledge graphs
3. Version-aware conflict detection
4. Human-in-the-loop adjudication
5. Domain-specific models

Medha is well-positioned because it already uses memory-based reasoning and cross-document synthesis. The next leap is moving from chunk-based to claim-based reasoning.

---

## Citations Needed

- [Quek2025] MeMo paper arXiv:2605.15156
- [Ejiofor2025] Construction rework costs from document errors
- [Papaioannou2023] LLM hallucination in construction documents
- [Li2024] RAG pipeline optimization for technical documents
- [YangSmith2026] Agent consensus protocols for secure systems
- [MadireddyGao2025] LLM-driven BIM code compliance checking
- [Yang2025] Multi-source integration from IFC BIM + 2D drawings

*TODO: Convert to proper BibTeX/Markdown bibliography in docs/citations/*

# DECISION-20260503-001: Training Data Strategy for Medha SLM

**Date:** 2026-05-03  
**Status:** **PROPOSED** — Awaiting Council of Ten Consensus  
**Scope:** High-level decision on data sources, collection methodology, and legal compliance  
**Proposer:** Research Scientist + Resource Strategist  

---

## 1. Proposal

Fine-tune a Small Language Model (3B–7B parameters) for construction document intelligence using a **hybrid data strategy**:

1. **Public regulatory data** (Dubai Municipality, UpCodes, FIDIC) as foundational corpus
2. **Synthetic training data** (LLM-generated + human-validated) for task-specific fine-tuning
3. **Partner VDC agency data** (anonymized, with consent) for domain adaptation
4. **User interaction logs** (opt-in) for continuous improvement via RLAIF

---

## 2. Council Deliberation

### 2.1 Research Scientist
> "Every data source must be cited and traceable. Synthetic data is valid if generated from authoritative sources and validated by domain experts. The Dubai Municipality regulations are public government documents — fair use for training. FIDIC contracts are copyrighted but published for industry use; we should confirm licensing."

**Concern:** Need explicit legal review of FIDIC and ASTM document usage.

### 2.2 First-Principles Engineer
> "Why fine-tune at all? The fundamental question: can a generic LLM with better RAG achieve the same result? Information theory says: if the knowledge is in the documents, retrieval + prompting should suffice. Fine-tuning encodes reasoning patterns, not facts."

**Concern:** Validate that fine-tuning improves reasoning beyond RAG + prompting before committing GPU budget.

### 2.3 Distributed Systems Architect
> "The data pipeline must handle 1K+ projects, each with 50–500 documents. Ingestion must be idempotent. Vector index updates must be atomic. Model retraining must not disrupt serving."

**Concern:** Need blue-green deployment for model updates.

### 2.4 Infrastructure-First SRE
> "Data lineage is non-negotiable. Every training example must have: source URL, ingestion timestamp, validation score, human reviewer ID (if applicable). If a bad example slips in, we need to identify and remove it without retraining from scratch."

**Concern:** Build data lineage system before collecting first example.

### 2.5 Ethical Technologist
> "Construction documents often contain proprietary designs. Even anonymized data can leak trade secrets through unique specifications. We need differential privacy guarantees for partner data. User interaction logs require explicit opt-in under UAE DPDP."

**Concern:** Privacy impact assessment required before using partner or user data.

### 2.6 Resource Strategist
> "TCO of data collection: synthetic data costs ~$0.10/example (LLM API + human review). Real partner data costs ~$5/example (legal review + anonymization + consent). At 20K examples, synthetic = $2K, real = $100K. Synthetic data should be 90%+ of corpus."

**Concern:** Ensure synthetic data quality is validated before scaling.

### 2.7 Diagnostic Problem-Solver
> "Root cause of current hallucinations: generic LLMs don't understand construction cross-references ('see Section 23 05 13'). The fix is not more data — it's structured reasoning. Fine-tuning should focus on reasoning patterns, not memorizing specs."

**Concern:** Benchmark must measure reasoning, not memorization.

### 2.8 Curious Explorer
> "What if we train on BIM+spec+drawing triplets as multimodal data? What if we use contrastive learning on contradiction pairs? What if we build a construction-specific tokenizer?"

**Concern:** These are high-risk, high-reward experiments. Allocate 10% of budget to exploration.

### 2.9 Clarity-Driven Communicator
> "Each task in the breakdown has one concern. Data collection is separate from model training. Legal review is separate from technical implementation. Let's not conflate them."

**Concern:** Ensure task boundaries are respected.

### 2.10 Inner-Self Guided Builder
> "Are we building the right thing? Dubai construction workers need accurate answers, not a model that scores well on benchmarks. The test is: does a site engineer trust Medha's output enough to act on it?"

**Concern:** Include field engineer feedback in evaluation, not just lab metrics.

---

## 3. Blocking Concerns

| # | Concern | Raised By | Resolution Required |
|---|---------|-----------|---------------------|
| B1 | Legal review of FIDIC/ASTM usage | Research Scientist | Legal counsel review by 2026-05-10 |
| B2 | Validate fine-tuning beats RAG+prompting | First-Principles Engineer | A/B test: baseline vs. fine-tuned on 100 examples |
| B3 | Data lineage system | Infrastructure-First SRE | Build lineage tracking before data collection |
| B4 | Privacy impact assessment | Ethical Technologist | PIA completion by 2026-05-15 |

**Resolution:** All blocking concerns must be resolved before DFS phase begins.

---

## 4. Non-Blocking Concerns

| # | Concern | Raised By | Mitigation |
|---|---------|-----------|------------|
| N1 | Synthetic data quality | Resource Strategist | Human validation on 10% sample |
| N2 | Blue-green model deployment | Distributed Systems Architect | Design in TASK-DFS-003 |
| N3 | Multimodal experiments | Curious Explorer | 10% budget reserve |
| N4 | Field engineer feedback | Inner-Self Guided Builder | Include in monthly evaluation |

---

## 5. Consensus Decision

**PENDING.** This decision requires:
1. Resolution of all blocking concerns (B1–B4)
2. Sign-off from at least 8 of 10 personas
3. ADR documentation in `docs/tasks/adr/`
4. Commitment of GPU budget ($70 training + $18K/year inference)

---

## 6. Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| B1 resolved | 2026-05-10 | Legal clearance memo |
| B2 resolved | 2026-05-10 | Baseline vs. fine-tuned A/B test results |
| B3 resolved | 2026-05-10 | Data lineage system MVP |
| B4 resolved | 2026-05-15 | Privacy impact assessment |
| Council consensus | 2026-05-15 | Signed decision record |
| Begin DFS | 2026-05-15 | First implementation task |

---

## References

[^1]: Research-First Covenant. Voice Agent Architecture Project. 2026. `/docs/principles/research-first-covenant.md`
[^2]: ADR-001: SLM Training Strategy. 2026. `/docs/tasks/adr/ADR-001-slm-training-strategy.md`

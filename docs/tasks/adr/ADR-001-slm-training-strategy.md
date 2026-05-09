# ADR-001: Small Language Model Fine-Tuning Strategy for Construction Document Intelligence

**Date:** 2026-05-03  
**Status:** Proposed — Awaiting Council of Ten Consensus  
**Scope:** Architectural decision on model selection, training methodology, and data strategy  
**Author:** Research Scientist + Resource Strategist + First-Principles Engineer

---

## Context

Medha (medha.trelolabs.com) currently uses API-based LLMs (xAI/Grok, Groq) for document analysis, contradiction detection, and RFI drafting. This works for prototyping but fails on three axes:

1. **Cost:** API calls cost ~$0.50–$2.00 per 1K tokens. A single construction spec review can consume 50K+ tokens. At scale (100 projects × 50 reviews/day), monthly API costs exceed $75K.
2. **Latency:** Round-trip API latency is 800ms–3s for complex reasoning. Real-time contradiction scanning during upload requires <500ms response.
3. **Reasoning depth:** Generic LLMs hallucinate on construction-specific reasoning (e.g., misinterpreting SMACNA duct standards, confusing ASTM grades). Domain adaptation is shallow via prompting alone.

The product promise to Dubai construction firms is: *"State-of-the-art reasoning on your documents, locally deployed, with zero data leaving your jurisdiction."* API-dependent architecture cannot fulfill this promise.

---

## Decision

We will **fine-tune a Small Language Model (SLM, 1B–7B parameters)** on a curated corpus of construction documents, building codes, and Dubai-specific regulations, integrated with a **RAG pipeline featuring hierarchical chunking + chain-of-thought reasoning**.

### Model Selection

| Model | Size | License | Context | Why Considered |
|-------|------|---------|---------|---------------|
| **Qwen2.5-Instruct** | 3B / 7B | Apache-2.0 | 128K | Strong reasoning; multilingual; permissive license [^1] |
| **Phi-4-mini** | 3.8B | MIT | 128K | Microsoft research; excellent instruction following [^2] |
| **Gemma-3** | 4B / 12B | Apache-2.0 | 128K | Google; trained on web + code + multilingual [^3] |
| **Llama-3.2** | 3B / 1B | Llama-3.2 License | 128K | Meta ecosystem; massive community [^4] |
| **DeepSeek-R1-Distill** | 7B / 14B | MIT | 128K | Reasoning-focused; distillation from 671B [^5] |

**Primary candidate:** Qwen2.5-7B-Instruct or DeepSeek-R1-Distill-Qwen-7B  
**Rationale:** Apache-2.0 / MIT license allows commercial white-label deployment. 128K context handles full spec sections. DeepSeek-R1 distillation explicitly optimizes for reasoning chains — critical for contradiction detection.

### Training Strategy

Three-phase approach (inspired by [^6] TinyLlama and [^7] MiniCPM):

```
Phase 1: Continual Pre-Training (CPT)
├── Corpus: 500M–2B tokens of construction text
├── Sources: Dubai building codes, SMACNA, ASTM, ACI, FIDIC, BIM manuals
├── Objective: Next-token prediction
├── Duration: 1–3 epochs
└── Output: Domain-adapted base model

Phase 2: Supervised Fine-Tuning (SFT)
├── Corpus: 50K–200K instruction-response pairs
├── Tasks: contradiction detection, RFI drafting, spec query, code compliance
├── Format: Alpaca / ShareGPT / OpenAI function-calling schema
├── Duration: 3–5 epochs
└── Output: Instruction-tuned model

Phase 3: Reasoning Alignment (RLAIF/DPO)
├── Corpus: 5K–20K preference pairs (good vs. bad reasoning)
├── Reward model: Human-labeled + automated rubric scoring
├── Method: DPO (Direct Preference Optimization) — no reward model needed [^8]
└── Output: Reasoning-aligned model
```

### RAG + Reasoning Architecture

```
Document Upload
    ↓
[Parser] — docling / pdfplumber → structured text + tables
    ↓
[Chunker] — hierarchical: section → paragraph → sentence + semantic overlap
    ↓
[Embedder] — multilingual-e5-large / bge-m3 → 1024-dim vectors
    ↓
[Vector Store] — pgvector / Qdrant → HNSW index
    ↓
[Query] — user question + retrieved chunks (top-5 + MMR diversity)
    ↓
[Reasoning Engine] — SLM generates chain-of-thought + final answer
    ↓
[Output] — structured JSON: {answer, citations, confidence, reasoning_chain}
```

---

## Consequences

### Positive

- **Cost reduction:** 10×–50× cheaper than API at scale ($0.01–$0.05 per 1K tokens vs. $0.50–$2.00)
- **Latency:** <200ms first token on A100/V100; <500ms end-to-end with RAG
- **Data sovereignty:** All inference local; zero API leakage risk
- **Reasoning depth:** Fine-tuned model understands construction jargon, cross-reference patterns, and contradiction types
- **White-label:** Apache-2.0 model allows resale to VDC agencies without licensing friction

### Negative

- **Upfront cost:** $2K–$5K GPU hours for full training pipeline
- **Maintenance burden:** Model drift requires quarterly retraining as building codes update
- **Data acquisition:** Construction documents are proprietary; public corpus is limited
- **Evaluation complexity:** No standard benchmark for construction document reasoning

### Alternatives Rejected

| Alternative | Why Rejected |
|-------------|-------------|
| Continue API-only | Fails cost, latency, and data sovereignty requirements |
| Fine-tune 70B+ model | GPU cost prohibitive; inference latency >2s |
| RAG without fine-tuning | Generic model hallucinates on construction-specific reasoning |
| Buy pre-trained construction LLM | No commercially available model exists; market gap |

---

## References

[^1]: Qwen2.5 Technical Report. Alibaba Cloud. (2025). https://qwenlm.github.io/blog/qwen2.5/
[^2]: Phi-4 Technical Report. Microsoft Research. (2024). https://arxiv.org/abs/2412.08905
[^3]: Gemma 3 Technical Report. Google DeepMind. (2025). https://storage.googleapis.com/deepmind-media/gemma/Gemma3Report.pdf
[^4]: Llama 3.2 Model Card. Meta AI. (2024). https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md
[^5]: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. DeepSeek-AI. (2025). https://arxiv.org/abs/2501.12948
[^6]: TinyLlama: An Open-Source Small Language Model. Zhang et al. (2024). https://arxiv.org/abs/2401.02385
[^7]: MiniCPM: Unveiling the Potential of Small Language Models with Scalable Training Strategies. Hu et al. (2024). https://arxiv.org/abs/2404.06395
[^8]: Direct Preference Optimization: Your Language Model is Secretly a Reward Model. Rafailov et al. (2023). https://arxiv.org/abs/2305.18290

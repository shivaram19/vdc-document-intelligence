# TASK-DFS-003: SLM Fine-Tuning Pipeline for Construction Domain

**Date:** 2026-05-03  
**Scope:** Depth-first implementation of the three-phase fine-tuning pipeline (CPT → SFT → DPO)  
**Personas:** Resource Strategist, Research Scientist, Diagnostic Problem-Solver  
**Status:** Pending BFS Completion

---

## 1. Objective

Fine-tune a 3B–7B parameter model to become a construction document reasoning expert, capable of contradiction detection, RFI drafting, and code compliance checking.

## 2. Three-Phase Pipeline

### Phase 1: Continual Pre-Training (CPT)

**Goal:** Adapt base model vocabulary and representations to construction domain.

**Corpus Composition:**

| Source | Tokens | Weight | Description |
|--------|--------|--------|-------------|
| Dubai building codes | 50M | 1.0x | DM regulations, Trakhees, DEWA |
| International standards | 100M | 1.0x | ASTM, ACI, SMACNA, ASHRAE, NFPA |
| FIDIC contracts | 20M | 1.2x | Red Book, Yellow Book, Silver Book |
| Construction specs (public) | 100M | 1.0x | UpCodes, CSI MasterFormat examples |
| Engineering textbooks | 50M | 0.8x | Structural, MEP, civil engineering |
| Construction news/articles | 50M | 0.5x | Regional focus: Dubai, GCC |
| General web (deduplicated) | 200M | 0.3x | Maintain general reasoning |
| **Total** | **~570M** | — | ~1–2 epochs |

**Technical Specs:**
- Framework: Unsloth (4× faster, 80% less VRAM) [^1] or Axolotl
- Hardware: 1× A100 80GB or 2× A10G 24GB
- Batch size: 4–8 per device
- Learning rate: 2e-5 (cosine decay)
- Duration: 8–16 hours
- Checkpointing: Every 500 steps

### Phase 2: Supervised Fine-Tuning (SFT)

**Goal:** Teach model to follow instructions for construction tasks.

**Dataset Composition:**

| Task | Examples | Format | Source |
|------|----------|--------|--------|
| Contradiction detection | 5K | Alpaca + reasoning chain | Synthetic (LLM-generated) + human-validated |
| RFI drafting | 2K | Structured JSON | Expert-written templates + synthetic variations |
| Spec Q&A | 10K | Conversational | RAG-generated + human-verified |
| Code compliance | 1K | Binary + explanation | Synthetic (spec + code → compliance check) |
| Drawing index parsing | 500 | JSON extraction | Real drawing indexes + synthetic noise |
| Tool calling | 2K | OpenAI function schema | Construction-specific functions |

**SFT Template (Alpaca-style):**
```json
{
  "instruction": "Detect contradictions between the following spec and drawing note.",
  "input": "Spec: 'All ducts shall be galvanized steel, 26 gauge minimum.'\nDrawing: 'Ductwork: 24 gauge aluminum.'",
  "output": "CONTRADICTION DETECTED [HIGH]\nExplanation: The spec requires 26 gauge galvanized steel, but the drawing specifies 24 gauge aluminum. Both material (galvanized steel vs. aluminum) and gauge (26 vs. 24) differ.\nSuggested RFI: 'Confirm duct material and gauge per spec Section 23 31 13 or provide deviation request.'"
}
```

**Technical Specs:**
- Framework: Unsloth + TRL (Transformers Reinforcement Learning)
- LoRA config: r=64, alpha=128, target_modules=[q_proj, k_proj, v_proj, o_proj]
- Hardware: 1× A100 80GB
- Batch size: 8
- Learning rate: 1e-4
- Duration: 4–8 hours

### Phase 3: Direct Preference Optimization (DPO)

**Goal:** Align model outputs with human preferences for reasoning quality.

**Preference Pairs:**

| Scenario | Preferred (win) | Rejected (lose) |
|----------|-----------------|-----------------|
| Contradiction explanation | Detailed, cites sections, suggests RFI | Vague, no citation, generic advice |
| RFI draft | Professional, specific, references standards | Informal, missing details, no references |
| Compliance check | Correctly identifies all violations | Misses violations or false positives |
| Response tone | Calm, structured, actionable | Alarmist, unstructured, no action items |

**DPO Template:**
```json
{
  "prompt": "Detect contradictions: Spec: '...' Drawing: '...'",
  "chosen": "CONTRADICTION [HIGH]... detailed explanation...",
  "rejected": "There might be a contradiction... you should check..."
}
```

**Technical Specs:**
- Framework: TRL DPOTrainer
- Beta: 0.1 (DPO temperature parameter)
- Hardware: 1× A100 80GB
- Duration: 2–4 hours

## 3. Model Evaluation During Training

| Checkpoint | Eval Task | Metric | Target |
|------------|-----------|--------|--------|
| Post-CPT | Perplexity on construction text | PPL | <8.0 |
| Post-CPT | MMLU (engineering subset) | Acc | >60% |
| Post-SFT | Contradiction F1 | F1 | >0.75 |
| Post-SFT | RFI BLEU vs. expert | BLEU | >0.40 |
| Post-DPO | Human preference rate | Win % | >70% |
| Post-DPO | Hallucination rate | % | <5% |

## 4. Infrastructure

```python
# src/training/config.py
@dataclass
class TrainingConfig:
    # CPT
    cpt_corpus_path: Path
    cpt_learning_rate: float = 2e-5
    cpt_epochs: int = 1
    cpt_batch_size: int = 4
    
    # SFT
    sft_dataset_path: Path
    sft_learning_rate: float = 1e-4
    sft_epochs: int = 3
    sft_lora_r: int = 64
    
    # DPO
    dpo_dataset_path: Path
    dpo_beta: float = 0.1
    dpo_learning_rate: float = 5e-5
```

## 5. Implementation Tasks

- [ ] **Subtask 1:** Set up Unsloth training environment
- [ ] **Subtask 2:** Build CPT corpus (570M tokens)
- [ ] **Subtask 3:** Generate SFT datasets (synthetic + human)
- [ ] **Subtask 4:** Generate DPO preference pairs
- [ ] **Subtask 5:** Implement CPT training script with checkpointing
- [ ] **Subtask 6:** Implement SFT training script with LoRA
- [ ] **Subtask 7:** Implement DPO training script
- [ ] **Subtask 8:** Build evaluation harness (automated + human)
- [ ] **Subtask 9:** Run full pipeline end-to-end
- [ ] **Subtask 10:** Export to GGUF for local inference (llama.cpp)

## 6. Resource Budget

| Phase | GPU Hours | Cost (A100) | Storage |
|-------|-----------|-------------|---------|
| CPT | 16h | $40 | 50GB |
| SFT | 8h | $20 | 20GB |
| DPO | 4h | $10 | 10GB |
| **Total** | **28h** | **$70** | **80GB** |

*Note: Costs are for cloud A100. On-premise H100 cluster reduces to ~$20.*

## 7. Acceptance Criteria

1. CPT: Perplexity <8.0 on construction text (vs. 12.0 base model)
2. SFT: Contradiction F1 >0.75 on held-out test set
3. SFT: RFI BLEU >0.40 vs. expert-written RFIs
4. DPO: Human preference >70% over SFT-only model
5. Hallucination rate <5% on factual queries
6. Inference latency <200ms first token on A100

---

## References

[^1]: Unsloth: 2-5× faster LLM fine-tuning. https://github.com/unslothai/unsloth
[^2]: Direct Preference Optimization. Rafailov et al. 2023. https://arxiv.org/abs/2305.18290
[^3]: TinyLlama: An Open-Source Small Language Model. Zhang et al. 2024. https://arxiv.org/abs/2401.02385
[^4]: MiniCPM: Unveiling the Potential of Small Language Models. Hu et al. 2024. https://arxiv.org/abs/2404.06395

# TASK-BFS-002: Construction SLM Benchmarks & Evaluation Landscape

**Date:** 2026-05-03  
**Scope:** Map existing benchmarks for evaluating small language models on construction-domain tasks  
**Personas:** Research Scientist, Diagnostic Problem-Solver, First-Principles Engineer  
**Status:** Research Phase

---

## 1. Objective

Before fine-tuning, we need rigorous evaluation. This task maps:
- Existing benchmarks for domain-specific reasoning
- Construction-specific NLP benchmarks
- How to build our own benchmark for contradiction detection, RFI drafting, and code compliance

---

## 2. General SLM Benchmarks

| Benchmark | Tasks | Size | URL | Relevance |
|-----------|-------|------|-----|-----------|
| MMLU | 57 subjects | 15K questions | https://github.com/hendrycks/test | Baseline; includes engineering |
| MMLU-Pro | 14K complex questions | 14K | https://arxiv.org/abs/2406.01574 | Harder reasoning; better discriminant |
| GSM8K | Math word problems | 1.3K | https://github.com/openai/grade-school-math | Structural reasoning proxy |
| HumanEval | Code generation | 164 problems | https://github.com/openai/human-eval | Tool-use reasoning proxy |
| BBH (Big Bench Hard) | 23 reasoning tasks | — | https://github.com/suzgunmirac/BIG-Bench-Hard | Multi-step reasoning |
| Arena-Hard | LLM comparison | 500 prompts | https://github.com/lm-sys/arena-hard-auto | Preference-based |

---

## 3. Construction-Specific Benchmarks

| Benchmark / Dataset | Task | Size | URL | Notes |
|---------------------|------|------|-----|-------|
| AECBench | LLM evaluation in AEC | 5 tasks | https://arxiv.org/abs/2509.18776 | Peer-reviewed; 2025 |
| CEQuest | Construction estimation | 1K+ problems | https://arxiv.org/html/2508.16081v1 | Quantitative reasoning |
| MCP4IFC | IFC-based design | 500 tasks | https://arxiv.org/pdf/2511.05533 | BIM reasoning |
| Table Comprehension in Building Codes | VLM table parsing | 2K tables | https://arxiv.org/pdf/2511.18306 | Regulation parsing |
| Automated Hazard Detection | Safety classification | 10K images+text | https://arxiv.org/abs/2511.15720 | Multimodal |
| AutoRC | Automated rule checking | 50 rules | https://orca.cardiff.ac.uk/id/eprint/177710/ | Compliance reasoning |

---

## 4. Benchmark Gaps for Medha

No existing benchmark covers these critical tasks:

| Task | Why It Matters | Current Proxy |
|------|---------------|---------------|
| **Contradiction Detection** | Core product promise | NLI datasets (SNLI, MNLI) — not construction-specific |
| **RFI Drafting Quality** | Customer-visible output | None; manual evaluation only |
| **Cross-Reference Resolution** | Spec→Drawing→Code linking | None; requires multimodal understanding |
| **Code Compliance Checking** | Dubai municipality requirement | AutoRC (50 rules, not Dubai-specific) |
| **Confidence Calibration** | Avoid hallucination | None; we must build |

---

## 5. Proposed Medha Benchmark Suite

### 5.1 Task Definitions

```
TASK-1: Contradiction Detection
├── Input: Spec paragraph + Drawing note
├── Output: {contradiction: bool, severity: low|medium|high|critical, explanation: str, suggested_rfi: str}
├── Metric: F1 (contradiction), BLEU/ROUGE (RFI), Human preference (explanation)
└── Dataset size target: 5K labeled pairs

TASK-2: RFI Drafting
├── Input: Contradiction + project context
├── Output: Structured RFI (to, question, reference, suggested_answer, impact)
├── Metric: BLEU vs. expert-written RFIs; human evaluation (clarity, completeness)
└── Dataset size target: 2K expert-written RFIs

TASK-3: Specification Query
├── Input: User question + full spec document
├── Output: Answer with citations
├── Metric: Exact match (citation accuracy), ROUGE-L, human correctness
└── Dataset size target: 10K question-answer pairs

TASK-4: Code Compliance
├── Input: Design spec + applicable code section
├── Output: {compliant: bool, violations: list, code_references: list}
├── Metric: F1 (violation detection), Precision@k (code references)
└── Dataset size target: 1K labeled compliance checks

TASK-5: Drawing Index Parsing
├── Input: Drawing index / title block text
├── Output: Structured metadata (sheet_number, discipline, revision, date)
├── Metric: Exact match per field; F1 for multi-field extraction
└── Dataset size target: 500 drawing indexes
```

### 5.2 Evaluation Protocol

| Phase | Method | Cost | Frequency |
|-------|--------|------|-----------|
| Automated | F1, BLEU, ROUGE, Exact Match | Zero | Every training run |
| LLM-as-Judge | GPT-4o scores reasoning quality | $0.01/query | Weekly |
| Human Expert | VDC engineer rates outputs | $50/hour | Monthly |
| A/B Test | Deploy model A vs. B to subset of users | Operational | Quarterly |

---

## 6. Research Papers on Evaluation

| Paper | Year | Contribution | URL |
|-------|------|--------------|-----|
| Li et al. — AECBench: Hierarchical Benchmark for LLMs in AEC | 2025 | First construction-specific LLM benchmark | [arXiv](https://arxiv.org/abs/2509.18776) |
| Evaluating Large Language Models for Construction Document Analysis | 2024 | Systematic evaluation framework | [SciOpen](https://www.sciopen.com/article/10.26599/JIC.2025.9180094) |
| LLMs in AEC: A Comprehensive Review | 2025 | Survey of 200+ papers; evaluation gaps identified | [Springer](https://link.springer.com/article/10.1007/s10462-025-11241-7) |
| BLEU is Not Enough | 2024 | Why generation metrics fail for technical documents | [ACL](https://aclanthology.org) |

---

## 7. Next Steps (DFS Gates)

- [ ] TASK-DFS-005: Build contradiction detection dataset (5K pairs)
- [ ] TASK-DFS-006: Build RFI drafting evaluation set (2K expert RFIs)
- [ ] TASK-DFS-007: Implement automated evaluation pipeline
- [ ] TASK-DFS-008: Recruit VDC engineer panel for human evaluation

---

## References

[^1]: Hendrycks et al. Measuring Massive Multitask Language Understanding. ICLR 2021. https://github.com/hendrycks/test
[^2]: Wang et al. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark. 2024. https://arxiv.org/abs/2406.01574
[^3]: AECBench: Hierarchical Benchmark for LLMs in AEC. 2025. https://arxiv.org/abs/2509.18776
[^4]: LLMs in AEC: A Comprehensive Review. Springer 2025. https://link.springer.com/article/10.1007/s10462-025-11241-7
[^5]: Evaluating Large Language Models for Construction Document Analysis. SciOpen 2025. https://www.sciopen.com/article/10.26599/JIC.2025.9180094

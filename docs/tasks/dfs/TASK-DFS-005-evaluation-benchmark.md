# TASK-DFS-005: Medha Evaluation Benchmark Suite

**Date:** 2026-05-03  
**Scope:** Build comprehensive benchmarks for evaluating the fine-tuned SLM + RAG system  
**Personas:** Research Scientist, Diagnostic Problem-Solver, Ethical Technologist  
**Status:** Pending BFS Completion

---

## 1. Objective

Create a rigorous, reproducible benchmark suite that measures:
- Reasoning quality on construction documents
- Hallucination rate on factual queries
- Latency under load
- Cost per inference
- Comparison against API-based baselines (GPT-4o, Claude, Groq)

## 2. Benchmark Tasks

### TASK-1: Contradiction Detection (CD)

**Input:** Spec paragraph + Drawing note / Other spec paragraph  
**Output:**
```json
{
  "contradiction": true,
  "severity": "high",
  "explanation": "Spec requires 26 gauge galvanized steel; drawing specifies 24 gauge aluminum.",
  "suggested_rfi": "Confirm duct material and gauge per Section 23 31 13.",
  "citations": ["spec:23-31-13", "drawing:A-101"]
}
```

**Dataset:**
- 5K labeled pairs (synthetic + human-validated)
- Split: 3K train, 1K dev, 1K test
- Labels: binary contradiction + severity (4-class) + explanation quality

**Metrics:**
- Contradiction F1 (macro)
- Severity accuracy (weighted)
- RFI BLEU vs. expert-written
- Explanation BERTScore vs. human reference

### TASK-2: RFI Drafting (RFI)

**Input:** Contradiction + project context (trade, urgency, contractor)  
**Output:** Structured RFI

**Dataset:**
- 2K expert-written RFIs from VDC agencies (anonymized)
- Synthetic variations (paraphrase, tone shift, detail level)

**Metrics:**
- BLEU/ROUGE-L vs. expert reference
- Human evaluation: clarity (1–5), completeness (1–5), actionability (1–5)
- Citation accuracy: % of referenced sections that exist

### TASK-3: Specification Query (SQ)

**Input:** Natural language question + full project document set  
**Output:** Answer with citations

**Examples:**
- "What gauge steel is required for HVAC ducts in Zone B?"
- "Which fire rating applies to the lobby partition wall?"
- "List all sections that reference ASTM A53."

**Dataset:**
- 10K question-answer pairs
- Source: RAG-generated + human verification

**Metrics:**
- Citation exact match (did it cite the right section?)
- Answer correctness (human binary judgment)
- ROUGE-L vs. reference answer
- Faithfulness (answer supported by retrieved chunks?)

### TASK-4: Code Compliance (CC)

**Input:** Design spec + applicable building code section  
**Output:** Compliance report

**Dataset:**
- 1K labeled compliance checks
- Dubai Municipality code + international standards

**Metrics:**
- Violation detection F1
- False positive rate
- Code reference precision@k

### TASK-5: Drawing Index Parsing (DIP)

**Input:** Drawing index / title block text  
**Output:** Structured metadata

**Dataset:**
- 500 real drawing indexes (anonymized)
- Synthetic noise variations (OCR errors, formatting variations)

**Metrics:**
- Per-field exact match (sheet_number, discipline, revision, date)
- Overall F1 (all fields correct)

## 3. Evaluation Protocol

### 3.1 Automated Evaluation (Every Training Run)

```python
class MedhaBenchmark:
    def evaluate(self, model: SLM) -> BenchmarkResult:
        results = {}
        for task in [CD, RFI, SQ, CC, DIP]:
            results[task.name] = task.evaluate(model)
        return BenchmarkResult(results)
```

### 3.2 LLM-as-Judge (Weekly)

Use GPT-4o to score reasoning quality:
- Rubric-based scoring (1–5) per dimension
- Dimensions: accuracy, completeness, clarity, citation quality, actionability
- Cost: ~$50 per full evaluation run

### 3.3 Human Expert Evaluation (Monthly)

- Panel: 3 VDC engineers
- Blind comparison: model A vs. model B vs. GPT-4o
- Dimensions: correctness, usefulness, professionalism
- Compensation: $100/hour

### 3.4 A/B Testing (Quarterly)

- Deploy model variant to 10% of users
- Track: user satisfaction (thumbs up/down), task completion rate, support tickets
- Statistical significance: p < 0.05

## 4. Baseline Comparisons

| System | Cost/1K tokens | Latency | Reasoning | Data Sovereignty |
|--------|---------------|---------|-----------|------------------|
| GPT-4o API | $2.50 | 1–3s | Excellent | ❌ |
| Claude 3.5 Sonnet | $3.00 | 2–4s | Excellent | ❌ |
| Groq (Llama 70B) | $0.60 | 0.5s | Good | ❌ |
| Medha Fine-tuned SLM | $0.02 | 0.2s | Target: Good+ | ✅ |

## 5. Implementation Tasks

- [ ] **Subtask 1:** Build contradiction dataset (5K pairs)
- [ ] **Subtask 2:** Build RFI evaluation dataset (2K expert RFIs)
- [ ] **Subtask 3:** Build spec Q&A dataset (10K pairs)
- [ ] **Subtask 4:** Build code compliance dataset (1K checks)
- [ ] **Subtask 5:** Build drawing index dataset (500 indexes)
- [ ] **Subtask 6:** Implement automated evaluation harness
- [ ] **Subtask 7:** Implement LLM-as-judge pipeline
- [ ] **Subtask 8:** Recruit VDC expert panel
- [ ] **Subtask 9:** Run baseline evaluation (GPT-4o)
- [ ] **Subtask 10:** Set up A/B testing infrastructure

## 6. Acceptance Criteria

1. All 5 benchmark tasks have >1K test examples
2. Automated evaluation runs in <1 hour
3. Fine-tuned SLM achieves >70% of GPT-4o score on all tasks
4. Latency P95 <500ms for simple queries
5. Cost per query <5% of GPT-4o equivalent

---

## References

[^1]: AECBench: Hierarchical Benchmark for LLMs in AEC. 2025. https://arxiv.org/abs/2509.18776
[^2]: Evaluating Large Language Models for Construction Document Analysis. 2025. https://www.sciopen.com/article/10.26599/JIC.2025.9180094
[^3]: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. 2023. https://arxiv.org/abs/2306.05685

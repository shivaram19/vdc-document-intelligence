# Medha Training Data & SLM Fine-Tuning Task Index
## Construction Document Intelligence — Dubai & Niche Market Focus

**Date:** 2026-05-03  
**Status:** Research Phase — Council of Ten Consensus Required Before Implementation  
**Scope:** Fine-tune a small language model (SLM) on construction document data from the internet, with RAG + reasoning, targeting Dubai and niche city construction markets.

---

## Council of Ten Persona Validation

Every task in this directory has been filtered through the ten personas from [voice-revenge-vizuara-ai AGENTS.md](https://github.com/pbakaus/impeccable). No task proceeds without consensus.

| # | Persona | Concern |
|---|---------|---------|
| 1 | **Research Scientist** | Every data source is cited; every claim has a URL |
| 2 | **First-Principles Engineer** | Why SLM and not LLM? Why Dubai? Derive from axioms |
| 3 | **Distributed Systems Architect** | Pipeline scales to 10K+ documents; ingestion is idempotent |
| 4 | **Infrastructure-First SRE** | Data lineage, observability, rollback plans for corrupted training runs |
| 5 | **Ethical Technologist** | Copyright compliance for scraped documents; no proprietary leakage |
| 6 | **Resource Strategist** | TCO of fine-tuning vs. API calls; GPU cost per inference |
| 7 | **Diagnostic Problem-Solver** | Root cause: why current RAG gives wrong answers |
| 8 | **Curious Explorer** | What if we train on BIM+spec+drawing triplets? |
| 9 | **Clarity-Driven Communicator** | Each task has ONE concern; cross-cutting concerns are separate tasks |
| 10 | **Inner-Self Guided Builder** | Are we building the right thing for construction workers? |

---

## Task Topology

```
docs/tasks/
├── README.md                          ← You are here
├── adr/
│   └── ADR-001-slm-training-strategy.md   ← Architectural decision: why SLM, why Dubai
├── bfs/                               ← Breadth-first: landscape before depth
│   ├── TASK-BFS-001-dubai-construction-corpus-landscape.md
│   ├── TASK-BFS-002-construction-slm-benchmarks.md
│   └── TASK-BFS-003-rag-chunking-reasoning-papers.md
├── dfs/                               ← Depth-first: implementation tasks
│   ├── TASK-DFS-001-data-ingestion-pipeline.md
│   ├── TASK-DFS-002-chunking-strategy.md
│   ├── TASK-DFS-003-slm-fine-tuning.md
│   ├── TASK-DFS-004-rag-reasoning-engine.md
│   └── TASK-DFS-005-evaluation-benchmark.md
├── bidirectional/                     ← Cross-domain impact
│   └── TASK-BIDIR-001-latency-cost-accuracy-tradeoffs.md
├── decisions/                         ← Consensus decisions
│   └── DECISION-20260503-001-training-data-strategy.md
└── principles/
    └── PRINCIPLE-001-data-citation-mandate.md
```

---

## Workflow

1. **Read ADR-001 first** — it explains the architectural decision
2. **Read BFS tasks** — they map the landscape (what exists, what's missing)
3. **Read DFS tasks** — they detail implementation (how we build it)
4. **Read BIDIR task** — it analyzes tradeoffs across domains
5. **Read DECISION** — it records the Council's consensus

---

## Research-First Covenant

> No code is written before research is complete.

**Current Phase:** BFS (Landscape Mapping)  
**Next Phase:** DFS (Deep Implementation) — gated by Council consensus  
**Target:** Complete BFS by 2026-05-10; begin DFS by 2026-05-15

---

*Compiled under Research-First Covenant. Every claim requires citation.*

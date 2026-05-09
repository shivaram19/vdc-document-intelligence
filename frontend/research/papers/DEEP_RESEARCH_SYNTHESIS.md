# Deep Research Synthesis: RL for Agent Self-Improvement

**Date:** 2026-04-23  
**Sources:** 30+ papers, repos, frameworks  
**Key Insight:** Our system is missing the most important component — the **Replay Gate**.

---

## What the Research Says

### 1. Karpathy's Autoresearch — The Core Pattern

```
Modify → Run Experiment → Evaluate → Keep/Discard → Repeat
```

Karpathy didn't just propose patches. He **tested every patch** with a real experiment (train for 5 min, measure val_bpb). Only improvements were kept. This is why it works.

**Our gap:** We propose patches but never test them. We don't know if they'd actually help.

### 2. EvoAgents — The Exact Architecture We Need

```
Run → Evaluate (LLM judge) → Patch → Replay Gate → Promote
```

EvoAgents validates patches by **replaying them on past traces**. Score: 0.67 → 0.83 → 1.00.

**Our gap:** No replay gate. No validation of patches against historical failures.

### 3. GEPA — Genetic-Pareto Optimization

- Outperforms RL by 19%
- 35x fewer rollouts than RL
- Maintains a frontier of Pareto-optimal candidates

**Insight for us:** Don't just generate one patch. Generate 2-3 variants and evaluate all of them.

### 4. Self-Healing Agent Architecture

| Component | What It Does |
|-----------|-------------|
| Insights Agent | Detects problems |
| Evolution Agent | Proposes solutions |
| **Replay/Validation** | Tests solutions |
| Promote | Keeps winners |

**Our gap:** Missing the validation layer.

### 5. DSPy / Prompt Compilers

- Treat prompts as programs to be compiled/optimized
- MIPROv2: bootstrapping → proposal → discrete search
- GEPA for prompt evolution

**Insight for us:** Skills are programs. We should compile/optimize them systematically.

---

## The Missing Piece: Replay Gate

**Problem:** We generate patches but never know if they'd work.

**Solution:** For each proposed patch, evaluate it against the historical failure that triggered it.

**How (practical implementation):**

1. Optimizer generates patch + links it to specific failure(s)
2. Judge reads: "Original failure context + proposed patch"
3. Judge asks: "Would this patch have prevented the failure?"
4. Judge scores: 0-1 (would not help → would definitely help)
5. Only patches scoring > 0.7 are promoted to "approved"

**Since we can't call an external LLM API from scripts easily, the Judge will:**
- Use deterministic heuristics for clear cases
- Flag ambiguous cases for LLM evaluation (via skill trigger)
- Track patch scores over time

---

## Redesigned Architecture

```
Session → Feedback → Observer → Optimizer → JUDGE → Apply → Git Commit
                              ↑___________↓ (only score > 0.7 passes)
```

**3-Agent System (research confirms this is optimal):**

| Agent | Role | Autonomy |
|-------|------|----------|
| **Observer** | Measures, detects patterns | Full auto |
| **Optimizer** | Generates 2-3 patch variants | Full auto |
| **Judge** | Evaluates patches, promotes winners | Auto for clear cases, human for ambiguous |

---

## What We Build Now

1. **Judge Agent** (`judge.py`) — Evaluates proposed patches
2. **Apply Script** (`apply.py`) — Applies approved patches + git commit
3. **Smart Optimizer** — Generates multiple patch variants per failure
4. **Updated Pipeline** — Observer → Optimizer → Judge → Apply

---

## Questions This Raises

1. Should we generate 2-3 patch variants per failure (like GEPA)?
2. Should patches be applied automatically if Judge score > 0.9?
3. Should we maintain a "frontier" of competing skill versions?
4. How do we measure "would this patch have prevented the failure" without an LLM API?
5. Should the Judge itself be a skill that invokes the LLM (us) for evaluation?

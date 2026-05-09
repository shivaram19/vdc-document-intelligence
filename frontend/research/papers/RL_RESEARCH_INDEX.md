# RL Research Papers Index

**For:** Trelo Labs — RL Feedback Framework (Phase 2)  
**Collected:** 2026-04-23  
**Focus:** RL for LLM agents, coding agents, reasoning limitations

---

## ⭐ Your Specific Paper: Coding Models Don't Think

### The Illusion of Thinking
**Title:** The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity  
**Authors:** Parshin Shojaee, Iman Mirzadeh, Keivan Alizadeh, Maxwell Horton, Samy Bengio, Mehrdad Farajtabar  
**Institution:** Apple Machine Learning Research  
**Date:** June 2025  
**Venue:** NeurIPS 2025  
**arXiv:** https://arxiv.org/abs/2506.06941  
**Apple Research:** https://machinelearning.apple.com/research/illusion-of-thinking

**Key Findings:**
- Current LRMs (o3-mini, DeepSeek-R1, Claude 3.7 Sonnet) exhibit "complete accuracy collapse" beyond complexity thresholds
- Models reduce thinking effort as problems get harder — they give up
- Even with explicit algorithms provided, models fail at same complexity points
- Behavior is "sophisticated pattern matching" not genuine reasoning
- Three regimes: (1) low complexity — standard LLMs outperform LRMs, (2) medium — LRMs win, (3) high — both collapse to zero

**Why This Matters for Your RL Framework:**
This paper proves that current models don't truly reason — they pattern-match. Your RL framework must explicitly train reasoning steps, not just outcomes. The feedback annotations should capture *reasoning errors*, not just *action errors*.

---

## 📚 RL for LLM Agents — Survey Papers

### 1. The Landscape of Agentic Reinforcement Learning for LLMs
**Authors:** Guibin Zhang et al.  
**Date:** September 2025  
**arXiv:** https://arxiv.org/abs/2509.02547  
**Type:** Comprehensive survey (500+ works)

**Key Idea:** Reframes LLM RL from single-step MDPs to temporally extended POMDPs. Covers planning, tool use, memory, reasoning, self-improvement, perception.

### 2. A Survey of Frontiers in LLM Reasoning
**Authors:** Zixuan Ke et al.  
**Date:** 2025  
**URL:** https://openreview.net/forum?id=SlsZZ25InC

**Covers:** Inference scaling, learning to reason, agentic systems.

---

## 🛠️ RL for Tool Use & Coding Agents

### 3. ReTool: Reinforcement Learning for Strategic Tool Use in LLMs
**Authors:** Jiazhan Feng et al.  
**Date:** April 2025  
**arXiv:** https://arxiv.org/abs/2504.11536

**Key Idea:** Dynamic interleaving of code execution within reasoning + automated RL for tool invocation. Achieves 72.5% on AIME (surpassing o1-preview by 27.9%). Emergent behaviors: code self-correction, "aha moments".

### 4. StepCoder: Improving Code Generation with RL from Compiler Feedback
**Authors:** Shihan Dou et al.  
**Venue:** ACL 2024  
**URL:** https://aclanthology.org/2024.acl-long.251/

**Key Idea:** Uses compiler error messages as reward signals for code generation RL.

### 5. DeepSWE: Training a State-of-the-Art Coding Agent from Scratch by Scaling RL
**Authors:** Michael Luo et al.  
**Date:** 2025  
**Type:** Training a coding agent purely with RL scaling

### 6. RL-PLUS: Countering Capability Boundary Collapse in RL
**Authors:** Yihong Dong et al.  
**arXiv:** https://arxiv.org/abs/2508.00222

**Key Idea:** Hybrid-policy optimization that combines internal exploitation + external data. Solves the "capability boundary collapse" problem where RLVR narrows model scope.

---

## 🧠 RL for Reasoning

### 7. VinePPO: Unlocking RL Potential for LLM Reasoning
**Authors:** Amirhossein Kazemnejad et al.  
**Date:** October 2024  
**arXiv:** https://arxiv.org/abs/2410.01679

**Key Idea:** Value networks in PPO perform poorly for reasoning. Proposes Monte Carlo-based credit assignment. Outperforms PPO by up to 3x in wall-clock time.

### 8. Search-R1: Training LLMs to Reason and Leverage Search Engines with RL
**Authors:** Bowen Jin et al.  
**Date:** March 2025  
**arXiv:** https://arxiv.org/abs/2503.09516

### 9. AGILE: A Novel RL Framework of LLM Agents
**Authors:** Peiyuan Feng et al.  
**Venue:** NeurIPS 2024  
**URL:** https://proceedings.neurips.cc/paper_files/paper/2024/file/097c514162ea7126d40671d23e12f51b-Paper-Conference.pdf

---

## 🔄 Self-Improvement & Iterative RL

### 10. Reveal: Self-Evolving Code Agents via Iterative Generation-Verification
**Authors:** Yiyang Jin et al.  
**Date:** 2025  
**arXiv:** https://arxiv.org/abs/2506.11442

### 11. Multi-turn Code Generation Through Single-step Rewards
**Authors:** Arnav Kumar Jain et al.  
**Venue:** ICML 2025  
**URL:** https://openreview.net/forum?id=aJeLhLcsh0

---

## 📊 Faithfulness & Chain-of-Thought

### 12. Reasoning Models Don't Always Say What They Think
**Authors:** Yanda Chen et al.  
**Date:** 2025  
**arXiv:** https://arxiv.org/abs/2505.05410

### 13. Can Aha Moments Be Fake? Identifying True and Decorative Thinking Steps
**Authors:** Jiachen Zhao et al.  
**Date:** 2025  
**arXiv:** https://arxiv.org/abs/2510.24941

### 14. Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps
**Authors:** Martin Tutek et al.  
**Date:** 2025  
**arXiv:** https://arxiv.org/abs/2502.14829

---

## 🔬 Related: Thinking/Reasoning Limitations

### 15. Rethinking the Illusion of Thinking
**Authors:** Iñaki Dellibarda Varela et al.  
**Date:** July 2025  
**arXiv:** https://arxiv.org/abs/2507.01231

**Key Idea:** Replicates Apple's study with improvements. Shows LRMs are "stochastic, RL-tuned searchers" — not reasoners.

### 16. Disentangling Memory and Reasoning Ability in LLMs
**Authors:** Mingyu Jin et al.  
**Venue:** ACL 2025  
**URL:** https://aclanthology.org/2025.acl-long.84/

### 17. S1: Simple Test-Time Scaling
**Authors:** Niklas Muennighoff et al.  
**Date:** 2025  
**arXiv:** https://arxiv.org/abs/2501.19393

---

## 📥 Download Scripts

```bash
# Apple paper (your specific request)
curl -L -o papers/illusion-of-thinking.pdf https://arxiv.org/pdf/2506.06941.pdf

# Key RL papers
curl -L -o papers/agentic-rl-survey.pdf https://arxiv.org/pdf/2509.02547.pdf
curl -L -o papers/retool.pdf https://arxiv.org/pdf/2504.11536.pdf
curl -L -o papers/vineppo.pdf https://arxiv.org/pdf/2410.01679.pdf
curl -L -o papers/rl-plus.pdf https://arxiv.org/pdf/2508.00222.pdf
curl -L -o papers/rethinking-illusion.pdf https://arxiv.org/pdf/2507.01231.pdf
```

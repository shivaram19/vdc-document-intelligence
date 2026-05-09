# Internet Research: RL Framework Design Questions

**Source:** Web search across research papers, GitHub repos, frameworks, surveys  
**Date:** 2026-04-23  
**Questions Answered:** 10 design questions for our RL feedback framework

---

## Q1: Multi-Agent or Single-Agent?

**Research Findings:**

| Source | Finding |
|--------|---------|
| **LangMARL** (2026) | Multi-agent LLM systems with credit assignment outperform single-agent for complex tasks. Most existing systems use static prompting; the future is adaptive multi-agent. |
| **RAGEN** (2025) | Multi-turn RL agents (StarPO framework) self-evolve through sequential decisions, memory, and stochastic feedback. Single-turn RL is insufficient for agent settings. |
| **MetaGPT** | SOP-driven multi-agent collaboration achieves 85%+ on coding benchmarks by role specialization (PM, Architect, Engineer). |
| **UniCorn** (2026) | Multi-agent systems are brittle due to coordination failures. Lightweight role instantiation within a single unified model may be better. |
| **DarwinTOD** (2026) | Dual-loop architecture: online multi-agent collaboration + offline evolutionary operations. Population-based competition + fitness selection. |

**Answer:** Multi-agent with role specialization wins for complex tasks, BUT coordination overhead is real. Best pattern: **small number (3-5) of specialized agents with a shared hub**, not a swarm.

**Our Design:**
- Agent 1: Error Detector (reads sessions, finds patterns)
- Agent 2: Skill Optimizer (proposes patches)
- Agent 3: Evaluator (measures if changes helped)
- Hub: Shared directory + structured logs

---

## Q2: What's Our "Hub"?

**Research Findings:**

| Source | Hub Design |
|--------|-----------|
| **Karpathy agenthub** | Central server with git bundle push/pull + message channels (#results, #discussion) |
| **LangGraph** | Graph-based state management with shared memory, checkpointers, persistent storage |
| **MetaGPT** | Shared memory pool + SOP-driven message passing |
| **IBM Multi-Agent** | Shared memory or message-passing protocols between agents |
| **CrewAI/AutoGen** | Hub = orchestrator layer that routes tasks between agents |

**Answer:** For our scale, a **local filesystem hub** is sufficient. Pattern:
```
session-exports/hub/
├── results/          # Experiment outcomes (like #results channel)
├── discussion/       # Agent observations (like #discussion channel)
├── commits/          # Skill version history (like git tree)
└── leaves/           # Frontier of unexplored skill changes
```

No server needed. Filesystem IS the hub.

---

## Q3: What's Our "val_bpb"?

**Research Findings:**

| Source | Metric |
|--------|--------|
| **AI Agent Metrics (Galileo)** | Session-level (goal achievement) + Trace-level (workflow quality) + Span-level (tool success) |
| **AI Evaluation Survey (2025)** | Goal completion rate, action accuracy, multi-step reasoning score, learning efficiency |
| **RLAIF / Beam AI** | Explicit feedback (+1/-1) + implicit feedback (human modifications become training data) |
| **Customer Support Metrics** | Containment rate, escalation rate, first-contact resolution |

**Answer:** Use a **composite metric** — not just one number:

```python
skill_score = (
    0.4 * success_rate +        # % turns without correction
    0.3 * completion_rate +     # % tasks finished without handoff
    0.2 * efficiency_score +    # fewer back-and-forth turns
    0.1 * tool_accuracy         # % correct tool choices
)
```

Lower correction rate = better. But also measure if we're getting tasks done faster.

---

## Q4: Trigger: Continuous vs On-Demand?

**Research Findings:**

| Source | Trigger Mode |
|--------|-------------|
| **Karpathy autoresearch** | Continuous loop — "NEVER STOP" |
| **Ouro Loop** | Autonomous overnight runs with bounded constraints |
| **Beam AI** | Continuous monitoring + periodic review cycles |
| **Self-Learning AI Agents** | Real-time feedback integration + periodic optimization |
| **OpenAI Codex Loop** | Self-directed execution with RL feedback |

**Answer:** **Hybrid trigger system:**

| Mode | When | What Happens |
|------|------|--------------|
| Event-triggered | After every `/export` | Log session, compute metrics, check for anomalies |
| Scheduled | Daily at 3 AM | Run full analysis, detect patterns, propose updates |
| On-demand | You say "run RL update" | Full pipeline: analyze → propose → evaluate → apply |
| Emergency | 3 corrections in 1 session | Immediate flag: "This skill is failing, needs attention" |

---

## Q5: What Gets Modified?

**Research Findings:**

| Source | What Gets Edited |
|--------|-----------------|
| **Karpathy** | One file: `train.py`. Everything else is read-only. |
| **Ouro Loop** | One file per phase. Bounded by BOUND system (DANGER ZONES, IRON LAWS). |
| **DSPy** | Prompts and demonstrations via compiler optimization. |
| **Reflexion** | Episodic memory (verbal reflections stored for later use). |
| **TextGrad** | Textual gradients backpropagated through computation graphs. |

**Answer:** Start with **one file: the active skill's SKILL.md**. Keep it simple.

Rules:
- **Safe to auto-modify:** Add examples, clarify ambiguous rules, add cross-references
- **Human approval required:** Change core workflow, add/remove agents, modify reward schema
- **Never auto-modify:** AGENTS.md task registry (human owns priorities), system prompts

---

## Q6: Version Control & Rollback

**Research Findings:**

| Source | Approach |
|--------|----------|
| **Karpathy agenthub** | Git bundle push/pull. Only push improvements. Revert locally on failure. |
| **Ouro Loop** | Git-based with runtime hooks. Revert on verification failure. |
| **Beam AI** | Rollback and recovery mechanisms — quick revert to previous configs. |
| **LangGraph** | Checkpointers save state at regular intervals. Time-travel debugging. |

**Answer:** **Git-track the skills directory.**

```bash
# Auto-commit before every skill change
git add ~/.kimi/skills/<skill>/SKILL.md
git commit -m "[agent-name] Update: <reason> | Score: <old> → <new>"

# If metric degrades after N sessions:
git revert HEAD
```

Keep last 20 versions per skill. Agent can `git diff` to see what changed.

---

## Q7: Agent Specialization

**Research Findings:**

| Source | Agent Roles |
|--------|-------------|
| **MetaGPT** | Product Manager, Architect, Engineer, QA — SOP-driven |
| **LangChain Research Assistants** | Planner, RAG Agent, Critic Agent |
| **Coding Assistants** | Planner, Code Interpreter, Tester Agent |
| **DarwinTOD** | DST, DP, NLG, UserSim agents with peer critique |
| **AI Scientist** | Idea generator, Experimenter, Analyst, Writer, Reviewer |

**Answer:** **3 agents, not 7.** Too many = coordination hell.

| Agent | Role | Reads | Writes |
|-------|------|-------|--------|
| **Observer** | Watches sessions, tags rewards, finds patterns | session-exports/, feedback-annotations/ | hub/results/, hub/discussion/ |
| **Optimizer** | Proposes skill updates based on patterns | hub/discussion/, skills/ | skill patches (proposed/ dir) |
| **Judge** | Evaluates if a patch improved things | hub/results/ | approval/rejection + score update |

Human is the final approver for structural changes.

---

## Q8: Human-in-the-Loop vs Full Auto

**Research Findings:**

| Source | Stance |
|--------|--------|
| **Karpathy agenthub** | "NEVER STOP. Do not pause to ask the human anything." |
| **Ouro Loop** | Bounded autonomy — constraints defined by human, then agent runs free within bounds. |
| **HITL Design (2026)** | "Future of AI is not full autonomy — but collaborative intelligence." |
| **Beam AI** | Human-in-the-loop for novel situations; autonomy for known patterns. |
| **OpenAI Codex Loop** | Self-directed with RL feedback, but scoped to coding tasks. |

**Answer:** **Bounded autonomy with escalation.**

```
Auto-approve:
  - Adding examples to skills
  - Clarifying existing rules
  - Updating success rates in reports

Human-approve:
  - Changing core skill workflow
  - Adding/removing agents
  - Modifying reward schema
  - Any change after 2 consecutive metric drops

Emergency stop:
  - Skill success rate drops below 50%
  - Agent produces invalid/corrupt skill files
  - User explicitly says "stop auto-updates"
```

---

## Q9: Integration with Kimi CLI

**Research Findings:**

| Source | Integration |
|--------|-------------|
| **Kimi CLI skills** | `~/.kimi/skills/` loaded automatically. Skills are markdown instructions. |
| **Karpathy program.md** | "Essentially a super lightweight skill." |
| **Ouro Loop** | Hooks into Claude Code via exit 2 hard-block runtime enforcement. |

**Answer:** **Build it as a Kimi skill + background Python service.**

- **Kimi skill:** `/skill:rl-hub` — triggers the analysis pipeline on demand
- **Background service:** Watches `session-exports/` for new exports, runs Observer agent
- **Hook:** Post-session hook that auto-runs Observer after `/export`

---

## Q10: Immediate Next Step

**Research Findings:**

| Source | Starting Pattern |
|--------|-----------------|
| **Karpathy** | Verify setup works → run one manual experiment → go autonomous |
| **Ouro Loop** | Define BOUND (constraints) → run one phase → expand |
| **MetaGPT** | Start with 2-agent MVP (1-2 days) → add memory → add CI |
| **AI Scientist** | One full manual run → automate the loop |

**Answer:** **Build the Observer agent first.** It's the foundation.

The Observer reads your existing feedback annotations and outputs:
- "Top 3 failure modes this week"
- "Skill X success rate: 67% → needs work"
- "Pattern detected: over-assumption in 4/7 sessions"

Once Observer works reliably, add Optimizer. Then Judge.

---

## Key Insights from Research

1. **Multi-agent is better BUT** — start with 3 agents max. Coordination failures are the #1 cause of multi-agent breakdown (UniCorn, Cemri et al. 2025).

2. **Filesystem hub > server** — For personal use, a structured directory IS the hub. No infra needed.

3. **Composite metrics > single number** — Don't just track corrections. Track completion, efficiency, tool accuracy.

4. **Bounded autonomy is the consensus** — Full auto for low-risk changes, human gate for structural changes. Everyone agrees on this.

5. **Git is the rollback mechanism** — Track skill versions. Revert when metrics degrade.

6. **Start with Observer** — You can't optimize what you don't measure. Manual feedback annotations → automated Observer → full loop.

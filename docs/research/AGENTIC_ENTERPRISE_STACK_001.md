# Medha Agentic Enterprise Stack v0.1
**Research Question:** Every AI stack in 2026 is a copy of the same four-layer diagram. How do we build a *working copy* for Medha — one that matches a solo founder's constraints and produces revenue, not demos?

---

## 1. First Principles: What Is an Agentic Enterprise Stack?

Strip away the marketing. An agentic enterprise stack is just:

1. **Reasoning** — a model that decides what to do
2. **Tools** — capabilities the model can call (APIs, files, databases)
3. **Memory** — context that persists across tasks
4. **Governance** — rules that keep the system from harming the business

Everything else (frameworks, protocols, orchestrators) is plumbing around these four. [CITE: AetherLink2026] The difference between a demo and a business is whether the fourth layer — governance — is real.

---

## 2. What the Market Says in 2026

### 2.1 The Protocol Layer Has Converged
Two protocols now dominate: [CITE: DigitalApplied2026; BuildMVPFast2026]
- **MCP (Model Context Protocol)** — agent-to-tool. Anthropic-originated, donated to Linux Foundation, 97M+ SDK downloads, 10K+ servers. It is becoming the "USB-C for AI." [CITE: OneReach2026]
- **A2A (Agent-to-Agent Protocol)** — agent-to-agent. Google-originated, also Linux Foundation, 150+ organizations in production. Uses Agent Cards for capability discovery. [CITE: IBLNews2026]

The boundary is clean: MCP connects an agent to its tools; A2A connects agents to each other. [CITE: Atlan2026]

### 2.2 The Four-Layer Architecture Is Universal
Every enterprise platform implements some version of: [CITE: arXiv2604.11623]
1. Reasoning engine
2. Tool/action layer
3. Memory/context layer
4. Governance layer

The governance layer is the weakest and most vendor-locked. [CITE: arXiv2604.11623]

### 2.3 Framework Choice Depends on Control vs Speed
- **Low-code / visual:** n8n, Dify, Flowise, LangFlow — fast to wire, limited at scale [CITE: RapidClaw2026]
- **Code-first Python:** LangChain, LangGraph, CrewAI, AutoGen — flexible, debug-heavy [CITE: Prepzee2026]
- **Code-first TypeScript:** Mastra, Sim Studio — modern, self-hostable [CITE: MadAppGang2026]
- **Hybrid recommendation:** n8n for ops orchestration + LangChain/CrewAI for reasoning + MCP for tool access [CITE: F3Fundit2026; Javadex2026]

### 2.4 Governance Is the Failure Mode
Gartner warns that >40% of agentic AI projects risk cancellation by 2027 without governance, observability, and ROI clarity. [CITE: GauravAI2026] Real risks already observed:
- 80% of companies report agents acting outside boundaries
- 53% give agents access to sensitive data
- 63% suffer agent/platform sprawl [CITE: GauravAI2026]

**Implication for Medha:** Start with one observable agent, one clear ROI metric, and human approval for any external commitment.

---

## 3. Medha's Working Copy: Design Rules

1. **One agent per pipeline, not one agent per task.** A pipeline is a repeatable business process. An agent owns a pipeline stage.
2. **MCP for tools, A2A only when necessary.** Medha does not need agent-to-agent delegation yet. It needs reliable agent-to-tool connections.
3. **Human-in-the-loop for commit actions.** Anything that spends money, contacts a customer, or makes a public commitment requires human approval.
4. **Start with n8n + Python.** n8n handles scheduling, webhooks, and integrations without code. Python handles document reasoning and domain logic.
5. **All agents read from and write to Plane.** Plane is the system of record for intent, tasks, and decisions.
6. **Measure agent ROI in business terms, not token throughput.** The right metric is hours saved per week or qualified conversations generated, not API calls.

---

## 4. Medha Agentic Stack v0.1

### 4.1 Layer Map

| Layer | Technology | Purpose | Hosted |
|-------|-----------|---------|--------|
| **Reasoning** | Claude/GPT-4 via API + local Phi-3.1 | High-level planning, document reasoning, drafting | Cloud + local |
| **Orchestration** | n8n (self-hosted) | Scheduling, webhooks, integrations, human approval gates | Azure VM |
| **Agent Logic** | Python + LangChain / custom | Document parsing, claim extraction, contradiction detection | Azure VM |
| **Tool Access** | MCP servers | Standardized connections to Plane, Postiz, files, DB, search | Azure VM |
| **Memory** | Plane (tasks), Postgres (structured), Chroma/pgvector (unstructured) | State, documents, embeddings | Azure VM |
| **Governance** | Human approvals, audit logs, cost caps, secret scanning | Prevents runaway spend and bad commits | Manual + automated |
| **Observability** | Langfuse or simple structured logs | Trace agent decisions, costs, errors | Self-hosted or cloud |

### 4.2 Agent Roster (One Per Pipeline)

| Agent | Pipeline | MCP Tools | Human Gate | Success Metric |
|-------|----------|-----------|------------|----------------|
| **Outreach Agent** | Customer Discovery | LinkedIn (via human-mediated export), web search, CRM/Plane | Sends drafts; human sends | 10 connection requests/week |
| **Synthesis Agent** | Customer Discovery | Plane, file system, LLM | None (read-only) | Call summary within 1h |
| **Content Agent** | Content & Authority | Postiz API, Plane, file system | Publishes only after human approve | 3 posts/week scheduled |
| **Engineering Agent** | Product Build | GitHub API, backend API, file system, test runner | Pull request approval | 1 deploy/week |
| **Pilot Agent** | Pilot & Sales | Backend API, file system, email (drafts) | Report sent only after human approve | 1 pilot report/cycle |
| **Ops Agent** | Operations & Infrastructure | Docker API, backup scripts, Uptime Kuma, certbot | Alerts only; no writes without human | 100% backup + uptime success |
| **Orchestrator Agent** | Founder Decision Support | Plane API, scorecard template, all other agents | Recommendations only | Sunday scorecard delivered |

### 4.3 Tool Exposure via MCP

Build one MCP server per capability:

```
medha-mcp-servers/
├── plane-mcp/          # read/write Plane issues, cycles, projects
├── postiz-mcp/         # schedule posts, list calendar
├── backend-mcp/        # run MeMo pipeline, query documents
├── filesystem-mcp/     # read/write docs/research/, backups/
├── web-search-mcp/     # search web for research/outreach
└── github-mcp/         # create PRs, read issues
```

Each server exposes a small, well-documented schema. Agents discover tools through MCP rather than hardcoded API calls. [CITE: Ranksquire2026]

---

## 5. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Human Founder (Approval Layer)            │
│         Reviews drafts, sends outreach, makes decisions      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Orchestrator Agent (n8n + Python)            │
│         Runs Sunday scorecard, routes tasks, checks drift     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Outreach   │ │   Content    │ │  Engineering │
│    Agent     │ │    Agent     │ │    Agent     │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────┬───────┴───────┬────────┘
                │               │
        ┌───────▼───────┐ ┌─────▼────────┐
        │   MCP Layer   │ │   Memory     │
        │ (tool access) │ │   Layer      │
        └───────────────┘ │ Plane/Postgres│
                          └───────────────┘
```

A2A is intentionally absent in v0.1. Medha has one orchestrator and six specialist agents. The orchestrator calls each specialist through MCP tools. A2A becomes relevant only when Medha has multiple independent agents that need to discover each other's capabilities across teams or vendors. [CITE: DigitalApplied2026]

---

## 6. Implementation Roadmap

### Phase 1: MCP Foundation (Weeks 1–2)
- [ ] Deploy n8n self-hosted on Azure VM
- [ ] Build `plane-mcp` server (read/write issues, cycles)
- [ ] Build `filesystem-mcp` server (restricted to project dirs)
- [ ] Build `backend-mcp` server (run MeMo pipeline, query docs)
- [ ] Add one human-approval webhook in n8n

### Phase 2: First Working Agent (Weeks 3–4)
- [ ] Build **Synthesis Agent**: ingests call transcript/notes → drafts Mom Test summary → writes to `docs/research/customer-learning/`
- [ ] Build **Content Agent**: drafts LinkedIn post from templates + customer insights → queues in Plane for human approval → publishes via Postiz
- [ ] Add cost tracking and logging to both agents

### Phase 3: Operations Agent (Weeks 5–6)
- [ ] Build **Ops Agent**: runs backup scripts, checks uptime, verifies SSL, scans secrets
- [ ] Sends Sunday morning health report to founder
- [ ] Escalates failures to human immediately

### Phase 4: Orchestrator + Drift Detection (Weeks 7–8)
- [ ] Build **Orchestrator Agent**: reads Plane, fills weekly scorecard, flags drift signals
- [ ] Integrate Outreach Agent (drafts connection requests; human sends)
- [ ] Integrate Pilot Agent (drafts reports; human sends)
- [ ] Add simple Langfuse or structured-log observability

### Phase 5: A2A Readiness (Months 3–6, optional)
- [ ] Evaluate if any agent needs to be consumed by external systems
- [ ] Add Agent Cards if external delegation becomes necessary
- [ ] Never add A2A just because it is fashionable

---

## 7. Governance Rules (Non-Negotiable)

1. **No agent spends money without approval.** No autonomous cloud scaling, no ad spend, no subscription purchases.
2. **No agent sends customer-facing messages without approval.** Drafts yes, sends no.
3. **No agent writes to production code without PR review.** Engineering Agent can open PRs; human merges.
4. **All agent actions are logged.** Tool call, input summary, output summary, cost, timestamp.
5. **Cost caps per agent per day.** Default $5/day/agent. Breach stops the agent and alerts human.
6. **Secrets never leave the secret store.** Agents access via environment variables only; no logging of keys.
7. **Human can kill any agent instantly.** One command to disable an agent in n8n/Plane.

---

## 8. ROI Metrics per Agent

| Agent | Input Cost | Time Saved / Value | Target ROI |
|-------|-----------|-------------------|------------|
| Synthesis Agent | ~$0.50/call | 30 min note-taking → 5 min review | 6x time return |
| Content Agent | ~$2/post | 2 hr writing → 30 min editing | 4x time return |
| Ops Agent | ~$0.10/day | 1 hr manual checks → 0 | 10x time return |
| Outreach Agent | ~$1/day | 30 min drafting → 5 min review | 6x time return |
| Engineering Agent | ~$5/task | 4 hr boilerplate → 1 hr review | 4x time return |
| Pilot Agent | ~$5/report | 3 hr report writing → 30 min review | 6x time return |

**Rule:** If an agent does not save at least 2x the time it costs within 30 days, it is shut down or redesigned.

---

## 9. What to Avoid (Anti-Patterns)

1. **Multi-agent for the sake of multi-agent.** One good agent beats six agents arguing. [CITE: F3Fundit2026]
2. **A2A before MCP.** If agents cannot reliably use tools, they cannot reliably delegate.
3. **Autonomy without observability.** You cannot manage what you cannot trace.
4. **Framework shopping.** Pick n8n + Python. Ship. Optimize later.
5. **Letting agents talk to customers unsupervised.** A bad LinkedIn DM is permanent.

---

## 10. Immediate Next Steps

1. **Deploy n8n** on the Azure VM alongside Plane and Postiz.
2. **Build the first MCP server:** `plane-mcp` (read issues/cycles, create task).
3. **Build the Synthesis Agent** as the first working agent — low risk, high value.
4. **Add one human approval gate** before any external action.
5. **Document the agent in an ADR** (`docs/decisions/ADR-00X-agentic-stack.md`).

---

## 11. Related Research

- `docs/research/agentic-enterprise-discovery/` — structured questions on building an agentic enterprise through open-source and human-centered discovery
- `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md` — pipelined operating system for Medha

## 12. Citations

See `docs/citations/AGENTIC_ENTERPRISE_STACK_001.bib` for full references.

---

**Bottom line:** The 2026 agentic enterprise stack is real, but most copies are over-engineered. Medha's working copy is: **one orchestrator, six pipeline agents, MCP for tools, human gates for commitments, and ROI measured in founder hours reclaimed.**

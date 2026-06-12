# Q3: What Can We Reuse from the Open-Source Ecosystem?

**Research Question:** Which open-source projects, patterns, and communities already provide pieces of an agentic enterprise, so Medha does not have to build everything from scratch?

---

## Why This Matters for Medha

Building an agentic enterprise from zero is a trap. Open source gives us working components, communities, and validation. We need a clear reuse-vs-build map.

---

## Sub-Questions

### 3.1 Orchestration and Workflow
1. What open-source workflow orchestrators support agentic patterns with human-in-the-loop?
2. How do n8n, Node-RED, Activepieces, and Apache Airflow compare for this use case?
3. Which has the strongest open-source community and self-hosting story?
4. Are there open-source projects that combine workflow orchestration with LLM agents?

### 3.2 Agent Frameworks
1. Beyond LangChain and CrewAI, what open-source agent frameworks are production-ready?
2. Which frameworks are designed for long-running, stateful, observable agents?
3. Which have strong MCP/A2A support?
4. Which are best for a Python backend vs. a TypeScript frontend?

### 3.3 Tool Access (MCP)
1. What open-source MCP servers already exist for common tools (Plane, GitHub, Postgres, filesystem, web search, email)?
2. Which MCP server registries are trustworthy and actively maintained?
3. What is the quality variance among community MCP servers?
4. Should Medha use existing MCP servers or build its own?

### 3.4 Memory and State
1. What open-source tools provide durable state for agents?
2. How do vector stores (Chroma, pgvector, Qdrant, Weaviate) compare for agent memory?
3. Are there open-source "agent memory" frameworks?

### 3.5 Observability and Governance
1. What open-source tools provide agent observability (Langfuse, Laminar, Phoenix, Helicone)?
2. Which are easiest to self-host?
3. Are there open-source agent governance or authorization frameworks?
4. What about open-source identity and access management for agents?

### 3.6 Domain-Specific Tools
1. What open-source construction/document intelligence tools exist?
2. What can we learn from OpenConstructionERP?
3. Are there open-source RFI/submittal/document review tools?
4. Are there open-source BIM/VDC coordination platforms?

### 3.7 Communities and Collectives
1. Where do agentic enterprise builders gather? (Discord, Slack, forums, GitHub orgs)
2. Which open-source communities are most aligned with human-centered AI?
3. Where can Medha contribute and learn?

---

## Current Hypotheses

1. **n8n** is the best open-source orchestration layer for Medha because it is self-hostable, has native AI nodes, and supports human approval gates.
2. **Plane + a Plane MCP server** is the best system of record because Medha already uses it.
3. **Langfuse or Laminar** is the best observability layer because both are open-source and self-hostable.
4. **OpenConstructionERP** is the most relevant domain example, but its AGPL license means we learn from it, not fork it.

---

## What Would Change Our Mind

- Discovery of a more mature, self-hosted agent orchestrator than n8n
- Evidence that existing Plane MCP servers do not work with self-hosted Plane
- Discovery of a construction-specific open-source agent framework

---

## Where to Look for Answers

- GitHub topics: `ai-agent`, `agentic-ai`, `mcp-server`, `workflow-automation`
- MCP registries: GitHub MCP Registry, Smithery, Docker MCP catalog
- Open-source directories: OpenAlternative, Awesome Self-Hosted
- Construction tech communities: LinkedIn groups, OpenBIM forums

---

## Medha-Specific Translation

For Medha, the reuse stack is:
- Plane (system of record) — already deployed
- n8n (orchestration) — deploy next
- Plane MCP server (tool access) — evaluate existing options
- Langfuse/Laminar (observability) — add after first agent
- Python + LangChain (domain reasoning) — build in-house

---

**Next action:** Evaluate the three existing Plane MCP servers (`disrex-group/plane-mcp-server`, `cmet7/plane-mcp`, `kelvin6365/plane-mcp-server`) against Medha's self-hosted Plane instance.

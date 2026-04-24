# Medha Agent Registry
## Problem-Driven Agent Naming & Role Mapping

> Every agent name must answer: **"What problem does this solve for the construction professional?"**

---

## The 7 Problems We Solve

| # | Problem (JTBD) | Research Basis | Cost of Inaction |
|---|---------------|----------------|------------------|
| P1 | **Find answers fast** — PMs waste 15–45 min searching specs for one clause | [Fathima2024] — BIM adoption barriers include information retrieval friction | 20+ hrs/week per PM |
| P2 | **Write RFIs that get answered** — Vague RFIs sit unanswered for weeks | [Papaioannou2023] — Poor RFI quality correlates with project delay | $2,500–$10,000 per delayed RFI |
| P3 | **Catch contradictions before they hit the field** — Spec says 5,000 psi, drawing says 4,000 | [Ejiofor2025] — Document errors cause 5–15% rework | $50K–$500K per contradiction |
| P4 | **Ingest documents without manual indexing** — 10,000 pages per project, manually unmanageable | [Li2024] — Agent specialization reduces ingestion time by 90% | Weeks of manual data entry |
| P5 | **Prove compliance on demand** — Auditors need tamper-evident document trails | [NIST800-207] — Zero trust requires continuous audit | Failed audit = project halt |
| P6 | **Secure document access** — Subcontractors, inspectors, owners need different access levels | [Mondal2015] — Behavioral biometrics for continuous auth | Data breach = liability |
| P7 | **Track what the fleet is doing** — Silent failures in automated systems go unnoticed | [Shahidinejad2021] — Telemetry essential for token lifecycle | Hours of debugging |

---

## Agent → Problem Mapping

| Agent Name | Problem Solved | Role | Capability | Node ID |
|-----------|---------------|------|-----------|---------|
| **Finder** | P1: Find answers fast | Routes natural language queries to relevant document chunks. Surfaces cited sources. | `can_query` | node-a |
| **Drafter** | P2: Write RFIs that get answered | Generates professional RFI responses with document citations. Flags contradictions in the draft. | `can_draft_rfi` | node-g |
| **Spotter** | P3: Catch contradictions before fieldwork | Scans specs vs. drawings for numerical mismatches (psi, ft, °F). Reports confidence scores. | `can_scan_contradictions` | node-f |
| **Librarian** | P4: Ingest without manual indexing | Parses PDF/DOCX/TXT, chunks semantically, generates embeddings. Auto-detects document type from filename. | `can_upload` | node-e |
| **Scribe** | P5: Prove compliance on demand | Appends every action to a SHA-256 chained audit log. Verifies chain integrity on demand. | `can_audit` | node-d |
| **Gatekeeper** | P6: Secure document access | Issues knowledge-provenance challenges. Tracks behavioral fingerprints. Revokes anomalous sessions. | `can_authenticate` | node-c |
| **Dispatcher** | P7: Track fleet activity | Monitors all node health, task completion rates, auth failures. Broadcasts status to dashboard. | `can_manage_projects` | node-i |
| **Cartographer** | P1+P3: Map document relationships | Builds knowledge graphs linking specs → drawings → RFIs. Enables "what else is affected?" queries. | `can_graph` | node-h |
| **Builder** | P4: Execute background tasks | Runs long-running workflows (batch ingest, full-project contradiction scan) without blocking queries. | `can_execute` | node-b |
| **Watchdog** | P7: Monitor system health | Collects latency histograms, error rates, token expiry alerts. Feeds metrics to dashboard. | `can_report` | node-j |

---

## Agent Interaction Flow

```
User asks: "What concrete strength for column C-12?"
  │
  ▼
┌─────────┐   ┌──────────┐   ┌─────────────┐
│ Finder  │──→│ Librarian│──→│  Cartographer│
│(node-a) │   │(node-e)  │   │  (node-h)    │
└─────────┘   └──────────┘   └─────────────┘
       │                           │
       ▼                           ▼
┌─────────────┐            ┌─────────────┐
│  Spotter    │←───────────│  "Any contradictions
│  (node-f)   │   checks   │   around concrete?"
└─────────────┘            └─────────────┘
       │
       ▼
┌─────────────┐
│  Scribe     │  ← logs: query, sources, contradictions
│  (node-d)   │     to tamper-evident audit chain
└─────────────┘
       │
       ▼
┌─────────────┐
│  Watchdog   │  ← records: query latency, result quality
│  (node-j)   │
└─────────────┘
```

---

## Agent Naming Principles

| Principle | Example |
|-----------|---------|
| **Job-title, not technology** | `Finder` not `RetrieverAgent` |
| **Action-oriented verb** | `Spotter`, `Drafter`, `Builder` |
| **Recognizable to construction pros** | `Librarian` (manages docs), `Scribe` (records everything) |
| **No acronyms** | `Gatekeeper` not `AuthSvc` |
| **Singular responsibility** | Each name maps to exactly one JTBD |

---

## Fleet Node Assignment

| Node ID | Agent Name | Primary Problem | Secondary Support |
|---------|-----------|-----------------|-------------------|
| node-a | **Finder** | P1: Fast answers | — |
| node-b | **Builder** | P4: Background execution | P7: Long-running tasks |
| node-c | **Gatekeeper** | P6: Secure access | P5: Session audit |
| node-d | **Scribe** | P5: Compliance proof | P6: Auth event logging |
| node-e | **Librarian** | P4: Auto-ingestion | P1: Chunk indexing |
| node-f | **Spotter** | P3: Contradictions | P2: RFI conflict check |
| node-g | **Drafter** | P2: RFI drafting | P3: Contradiction flagging |
| node-h | **Cartographer** | P1+P3: Relationship mapping | P4: Document linking |
| node-i | **Dispatcher** | P7: Fleet coordination | All: Task routing |
| node-j | **Watchdog** | P7: Health monitoring | All: Metrics collection |

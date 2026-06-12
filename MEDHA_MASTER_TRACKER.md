# Medha Master Tracker
**Purpose → Plan → Preparation**

Use this file as your daily/weekly command center. Every initiative links back to its purpose, current plan, and preparation status.

---

## How to Use This Tracker

1. **Start with Purpose** — why does this matter?
2. **Check the Pipeline** — which operational pipeline does this belong to?
3. **Check the Plan** — what are we doing about it?
4. **Update Preparation** — what's the current status and next action?

Pipelines are defined in `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md`:
- Pipeline 1: Customer Discovery
- Pipeline 2: Content & Authority
- Pipeline 3: Product Build
- Pipeline 4: Pilot & Sales
- Pipeline 5: Operations & Infrastructure
- Pipeline 6: Founder Decision-Making

**Status legend:**
- 🟢 Ready / Active
- 🟡 In Progress / Blocked
- 🔴 Not Started
- ✅ Complete

---

## 1. Product Development

### 1.1 Cognitive System Integration
**Purpose:** Unlock the highest-leverage disconnected asset — 1,501 lines of cited cognitive architecture.  
**Plan:** Wire `src/cognitive/` into the backend API.  
**Preparation:**
- [ ] Read `src/cognitive/` architecture
- [ ] Map integration points to `backend/app.py`
- [ ] Design API endpoints for cognitive reasoning
- [ ] Write tests
- [ ] Deploy and validate

**Status:** 🔴 Not Started  
**Owner:** @shivaramgoud  
**File:** `docs/tasks/prd/ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` → B5.1

---

### 1.2 Backend Refactor
**Purpose:** `backend/app.py` is 1,652 lines and violates single responsibility.  
**Plan:** Decompose into modules: routes, services, middleware, config.  
**Preparation:**
- [ ] Audit current endpoints
- [ ] Design module structure
- [ ] Refactor incrementally without breaking existing API
- [ ] Add tests

**Status:** 🔴 Not Started  
**Owner:** @shivaramgoud  
**File:** `ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` → B2.1

---

### 1.3 MeMo Pipeline Hardening
**Purpose:** Contradiction detection is only 25% on synthetic ground truth.  
**Plan:** Improve Step 5 prompts, test stronger models, build same-project corpus.  
**Preparation:**
- [x] Build parallel pipeline (19-20x speedup)
- [x] Create synthetic contradiction corpus
- [ ] Collect same-project multi-discipline documents
- [ ] Rewrite Step 5 contradiction prompt
- [ ] Test GPT-4 / fine-tuned model
- [ ] Re-run TEST-002 report

**Status:** 🟡 In Progress  
**Owner:** @shivaramgoud  
**Files:** `scripts/memo-poc/TEST_REPORT_001.md`, `real_construction_docs_contradictions/`

---

### 1.4 Domain-Specific Embeddings
**Purpose:** `all-mpnet-base-v2` is not construction-tuned.  
**Plan:** Evaluate/fine-tune embeddings on construction specs.  
**Preparation:**
- [ ] Research construction embedding datasets
- [ ] Benchmark current retrieval quality
- [ ] Fine-tune or switch to domain model

**Status:** 🔴 Not Started  
**File:** `ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` → B3.2

---

### 1.5 Dubai/GCC Code Compliance
**Purpose:** Current domain knowledge hardcodes US codes (IECC/IBC/ASHRAE); Dubai DM codes missing.  
**Plan:** Integrate Dubai DM Building Regulations and GCC codes.  
**Preparation:**
- [ ] Acquire Dubai DM regulations PDFs
- [ ] Build Dubai-specific code parser
- [ ] Validate against sample Dubai projects
- [ ] Add to domain knowledge base

**Status:** 🔴 Not Started  
**File:** `ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` → B4.3

---

## 2. Go-to-Market

### 2.1 LinkedIn Founder Presence
**Purpose:** Build authority and reach in construction tech / VDC / AI circles.  
**Plan:** Post 3x/week using the social media playbook.  
**Preparation:**
- [x] Write 10 post templates
- [x] Create 14-day content calendar
- [x] Set up Postiz scheduler
- [ ] Connect LinkedIn to Postiz
- [ ] Schedule first 3 posts
- [ ] Engage daily for 15 min

**Status:** 🟡 In Progress (blocked on LinkedIn API keys; see 90-day OS)  
**Files:** `docs/tasks/prd/SOCIAL_MEDIA_PLAYBOOK_001.md`, `postiz/`, `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md`

---

### 2.2 Profile Optimization
**Purpose:** Convert profile views into connections and conversations.  
**Plan:** Update LinkedIn headline, banner, About section, featured section.  
**Preparation:**
- [ ] Update headline
- [ ] Create banner image
- [ ] Rewrite About section
- [ ] Add featured items (Medha landing page, test report, architecture map)

**Status:** 🟡 In Progress (do in Week 1 of 90-day OS)  
**File:** `docs/tasks/prd/SOCIAL_MEDIA_PROFILE_OPTIMIZATION.md`, `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md`

---

### 2.3 Dubai/GCC Outreach
**Purpose:** Position Medha as the context-preserving intelligence layer for fragmented construction platforms in GCC.  
**Plan:** Research target companies, build outreach sequences, schedule calls.  
**Preparation:**
- [ ] Build target list of 50 Dubai VDC agencies / contractors
- [ ] Write consultative outreach templates (Mom Test style)
- [ ] Identify warm intros via IIT Madras / Sub-engineering network
- [ ] Track outreach in CRM/spreadsheet
- [ ] Complete 15 customer discovery calls in 90 days

**Status:** 🟡 In Progress (Week 2+ of 90-day OS)  
**Files:** `MEDHA_CUSTOMER_MEETING_PLAYBOOK.md`, `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md`

---

## 3. Research & Validation

### 3.1 Real Contradiction Corpus
**Purpose:** Synthetic contradictions prove the pipeline works; real contradictions prove market value.  
**Plan:** Gather same-project documents with known conflicts.  
**Preparation:**
- [ ] Source publicly available construction bid sets
- [ ] Request access to university project manuals
- [ ] Extract contradictions manually for ground truth
- [ ] Re-run pipeline and measure detection rate

**Status:** 🔴 Not Started  
**File:** `real_construction_docs_contradictions/`

---

### 3.2 Research Corpus Maintenance
**Purpose:** Every architectural decision must be cited.  
**Plan:** Keep `docs/research/` and `docs/decisions/` up to date.  
**Preparation:**
- [ ] Cite new papers as they are used
- [ ] Write ADRs for major decisions
- [ ] Maintain BibTeX/Markdown bibliographies

**Status:** 🟡 In Progress  
**Files:** `docs/research/`, `docs/decisions/`, `docs/citations/`

---

## 4. Operations

### 4.1 Central Planning Workspace (Plane)
**Purpose:** One place to track all Medha work across Purpose → Plan → Preparation.  
**Plan:** Self-host Plane and migrate tracker items into it.  
**Preparation:**
- [x] Deploy Plane on port 8091
- [x] Open firewall rules (UFW + Azure NSG)
- [ ] Create Medha workspace
- [ ] Create projects: Product, GTM, Research, Operations
- [ ] Import tasks from `MEDHA_MASTER_TRACKER.md`
- [ ] Set up weekly review cycle

**Status:** 🟡 In Progress  
**Access:** https://plane.trayini.ai  
**File:** `plane/README.md`

---

### 4.2 Security Hygiene
**Purpose:** Prevent credential leaks and unauthorized access.  
**Plan:** Rotate exposed keys, audit secrets, improve practices.  
**Preparation:**
- [ ] Rotate OpenAI Key A (`sk-proj-VHFX...`)
- [ ] Rotate OpenAI Key B (`sk-proj--htNVT...`)
- [ ] Audit repo for any remaining exposed secrets
- [ ] Set pre-commit hook to scan for secrets (TruffleHog already configured)

**Status:** 🔴 Not Started (HIGH PRIORITY)  
**File:** `postiz/SECURITY_AUDIT_001.md`

---

### 4.3 Infrastructure
**Purpose:** Keep services running and accessible.  
**Plan:** Monitor Postiz, backend, landing page, and agent bridge.  
**Preparation:**
- [x] Postiz deployed and accessible
- [x] Azure NSG rules added
- [ ] Set up uptime monitoring
- [ ] Configure backups for Postiz data

**Status:** 🟡 In Progress  
**File:** `postiz/README.md`

---

### 4.4 Agentic Enterprise Stack
**Purpose:** Move from manual operations to agent-assisted pipelines that save founder hours while keeping human approval gates.  
**Plan:** Deploy n8n, build MCP servers, ship first working agent (Synthesis Agent), then Content Agent, Ops Agent, Orchestrator.  
**Preparation:**
- [ ] Answer discovery questions in `docs/research/agentic-enterprise-discovery/`
- [ ] Deploy n8n self-hosted on Azure VM
- [ ] Evaluate existing Plane MCP servers
- [ ] Build `filesystem-mcp` server
- [ ] Build `backend-mcp` server
- [ ] Build Synthesis Agent (call notes → summary)
- [ ] Build Content Agent (draft → approve → Postiz)
- [ ] Build Ops Agent (backups, uptime, SSL, secrets scan)
- [ ] Build Orchestrator Agent (Sunday scorecard + drift alerts)

**Status:** 🟡 In Progress (discovery structured)  
**Files:** `docs/research/AGENTIC_ENTERPRISE_STACK_001.md`, `docs/research/agentic-enterprise-discovery/`

### 4.5 PicoCloth Stabilization
**Purpose:** Experimental agent mesh has file-based shared memory and no frontend integration.  
**Plan:** Decide whether to stabilize or deprioritize PicoCloth.  
**Preparation:**
- [ ] Review PicoCloth current state
- [ ] Decide: integrate, rewrite, or archive
- [ ] If integrate: design frontend bridge

**Status:** 🔴 Not Started  
**File:** `ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` → B7.2/B7.3

---

## 5. Quick Decision Backlog

These need a yes/no decision before proceeding:

| Decision | Options | Recommended | Status |
|----------|---------|-------------|--------|
| Which enhancement track first? | A) Backend refactor, B) Frontend polish, C) MeMo hardening, D) Dubai corpus, E) PicoCloth stabilize | **C) MeMo hardening** | Pending |
| Should Postiz be on a subdomain? | Yes (`postiz.drmath.trelolabs.com`) / No (keep IP:4007) | **Yes** | Pending |
| Should PicoCloth be archived? | Yes / No / Integrate | **Archive for now** | Pending |
| Target first customer segment? | VDC agencies / GCs / MEP subs / Owners | **VDC agencies** | Pending |
| Agentic stack first agent? | Synthesis / Content / Ops / Outreach | **Synthesis Agent** | Pending |

---

## 6. Daily Standup Questions

Answer these every morning:

1. **Purpose check:** What is the single most important thing to move Medha forward today?
2. **Plan check:** Which tracker item am I working on?
3. **Preparation check:** What is the next concrete action I can take in the next 90 minutes?
4. **Blocker check:** What am I waiting on or avoiding?

---

## 7. Operational Pipeline Health (Updated Weekly)

| Pipeline | Leading Signal | This Week | Blocker |
|----------|---------------|-----------|---------|
| Customer Discovery | Calls completed | __ / 2 | |
| Content & Authority | Posts published | __ / 3 | |
| Product Build | Real doc sets ingested | __ | |
| Pilot & Sales | Proposals sent | __ | |
| Operations | Backups + uptime | __% | |
| Founder Decisions | Scorecard complete | yes / no | |

See `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md` for stage-by-stage ownership and drift signals.

---

## 8. Key Links

| Resource | Path |
|----------|------|
| Architecture Map | `docs/tasks/prd/ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` |
| Social Media Playbook | `docs/tasks/prd/SOCIAL_MEDIA_PLAYBOOK_001.md` |
| First 3 Posts | `docs/tasks/prd/SOCIAL_MEDIA_FIRST_3_POSTS.md` |
| LinkedIn Profile Optimization | `docs/tasks/prd/SOCIAL_MEDIA_PROFILE_OPTIMIZATION.md` |
| Postiz Setup | `postiz/README.md` |
| Security Audit | `postiz/SECURITY_AUDIT_001.md` |
| MeMo Test Report | `scripts/memo-poc/TEST_REPORT_001.md` |
| Customer Meeting Playbook | `MEDHA_CUSTOMER_MEETING_PLAYBOOK.md` |
| Research Landscape | `docs/research/memo-analysis/CONSTRUCTION_AI_RESEARCH_LANDSCAPE_2026.md` |
| Pipelined OS Action Plan | `docs/research/OPERATING_SYSTEM_FRAMEWORK_002-real-world-action-plan.md` |
| Agentic Enterprise Stack | `docs/research/AGENTIC_ENTERPRISE_STACK_001.md` |
| OS Bibliography | `docs/citations/OPERATING_SYSTEM_FRAMEWORK_002.bib` |
| Agentic Stack Bibliography | `docs/citations/AGENTIC_ENTERPRISE_STACK_001.bib` |
| Agentic Enterprise Discovery | `docs/research/agentic-enterprise-discovery/README.md` |
| Discovery Bibliography | `docs/citations/AGENTIC_ENTERPRISE_DISCOVERY_001.bib` |

---

## 9. Weekly Review Template

Copy this into a new section each week:

```markdown
### Week of [DATE]
**Wins:**
- 

**Blockers:**
- 

**Next week's focus:**
- 

**Key metric:**
- 
```

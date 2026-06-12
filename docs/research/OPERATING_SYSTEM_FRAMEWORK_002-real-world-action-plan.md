# Medha Operating System: Pipelined Real-World Action Plan
**Research Question:** Given that only the human founder can take in-world actions, what is the smallest set of operational pipelines that keeps Medha moving, detects drift early, and routes every human hour to the highest-leverage stage?

---

## 1. First-Principles Decomposition

A startup is not a calendar. It is a set of pipelines that convert uncertainty into evidence, and evidence into revenue. Strip the operating system to its irreducible parts:

1. **Intent** — what must be true 90 days from now?
2. **Pipeline** — which repeatable sequence produces that outcome?
3. **Stage ownership** — who does each stage (human or AI/cloud)?
4. **Signal** — what tells us the pipeline is flowing or blocked?
5. **Correction** — what do we change when a stage stalls?

Everything else is scaffolding. [CITE: Fitzpatrick2013] The goal is fast, cheap learning about what the market will pay for.

---

## 2. What Mature Organizations Actually Do

### 2.1 They Pipeline Work, Not Just List Tasks
Mature construction firms run document workflows as pipelines: RFI creation → assignment → response → approval → closure; submittal preparation → technical review → approval → version archive. [CITE: BIMCAD2024; SubmittalLink2026] Each stage has a role, a tool, and a SLA.

Startups that scale do the same: discovery → qualification → pilot → close → case study. [CITE: Fitzpatrick2013] Ad-hoc founders jump straight to pitching. Pipelined founders run each stage in order.

### 2.2 They Limit Strategic Goals to 3–5 OKRs
OKRs are a scarcity filter, not a wish list. [CITE: Shadinger2025; Morris2025] For a solo founder, the filter is even sharper: if there is only one human hour available, which pipeline gets it?

### 2.3 They Separate Build Mode from Growth Mode
Solo founders who reach $1M+ ARR do not build and sell in the same hour. They run distinct phases. [CITE: ProductLed2026] Medha must protect deep product work while keeping a continuous customer-discovery pipeline running in parallel.

### 2.4 They Track Leading Metrics Per Pipeline
- Product: deploy frequency, experiment completion
- GTM: discovery calls, content cadence, inbound DMs
- Research: experiments run, citations added
- Operations: uptime, backup success, security hygiene [CITE: OPERATING_SYSTEM_FRAMEWORK_001]

### 2.5 They Run a Four-Tier Review Cadence
Weekly operational review → monthly business review → quarterly strategic review → annual planning. [CITE: SiftFeed2026] At Medha this collapses to a daily standup, Sunday scorecard, and 6-week retrospective.

### 2.6 They Discover Customers the Right Way
The Mom Test: ask about past behavior, not hypotheticals; talk about their life, not your idea; listen 80% of the time. [CITE: Fitzpatrick2013; Koji2026]

---

## 3. Medha's Operational Pipelines

Each pipeline below has:
- **Purpose** — what outcome it produces
- **Stages** — the sequence of work
- **Owner** — H = human founder, A = AI/cloud agent
- **Tool** — where the work lives
- **Signal** — how to know it is healthy
- **Next action** — the immediate first step

---

## Pipeline 1: Customer Discovery
**Purpose:** Convert strangers into evidence about what the market will pay for.

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 1.1 Define ICP criteria | H | Plane / markdown | ICP doc exists | Write 1-page ICP in `docs/tasks/prd/ICP_001.md` |
| 1.2 Build target list | H + A | LinkedIn + spreadsheet/CRM | 50 prospects listed | Build list of 50 Dubai/GCC VDC/BIM professionals |
| 1.3 Draft connection requests | A | Plane / markdown | 3 templates approved | Human approves Mom Test-style templates |
| 1.4 Send connection requests | H | LinkedIn | 10 sent/day | Send 10/day starting Week 2 |
| 1.5 Book discovery calls | H | Calendly / LinkedIn | 2 calls/week booked | Offer 15-min "learn about your workflow" chat |
| 1.6 Run discovery calls | H | Zoom/Meet + notes template | Customer speaks 80% of time | Use 5-question Mom Test script |
| 1.7 Synthesize call notes | A | Markdown / Plane | 1-page summary per call | AI drafts; human validates |
| 1.8 Identify patterns | H + A | `docs/research/customer-learning/` | Patterns repeat after 5+ calls | Update ICP and problem statement weekly |
| 1.9 Route to pilot pipeline | H | CRM / Plane | Qualified prospects tagged | Move engaged contacts to Pilot pipeline |

**Drift signals:**
- 0 connection requests sent for 3 days → H is avoiding outreach
- 0 calls booked in 14 days → messaging or ICP is wrong
- Calls full of pitching, not listening → reset to Mom Test script
- No synthesis within 24h of call → evidence is being lost

---

## Pipeline 2: Content & Authority
**Purpose:** Make Medha the obvious choice for VDC teams with contradiction problems.

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 2.1 Define content themes | H | Plane / markdown | 4 themes locked | Themes: rework cost, RFI overload, addenda drift, AI in VDC |
| 2.2 Generate post drafts | A | Plane / Postiz | 3 drafts ready | AI drafts from templates + customer insights |
| 2.3 Human edit & approve | H | Plane | Drafts approved | Founder adds personal story or specific example |
| 2.4 Schedule in Postiz | A | Postiz | 3 posts/week queued | AI schedules; human confirms |
| 2.5 Publish | A | Postiz + LinkedIn | Posts go live | Monitor for failures |
| 2.6 Engage with community | H | LinkedIn | 15 min/day | Comment meaningfully on 3–5 posts |
| 2.7 Track engagement | A | Postiz / spreadsheet | Weekly metrics | Report profile views, DMs, connection requests |
| 2.8 Repurpose top posts | A | Plane | Top 20% identified | Turn high-engagement post into long-form or demo clip |

**Drift signals:**
- <80% of scheduled posts published → Postiz broken or drafts not approved
- 0 founder engagement for 3 days → authority loop is broken
- Engagement dropping week-over-week → content theme needs refresh
- Inbound DMs = 0 after 30 days → content is not reaching buyers

---

## Pipeline 3: Product Build
**Purpose:** Harden the MeMo pipeline until it produces reliable value on real documents.

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 3.1 Collect real document sets | H + A | `real_construction_docs/` | 1 same-project set ingested | Source bid sets, university manuals, or pilot customer docs |
| 3.2 Extract claims (not chunks) | A | Backend / scripts | Claim graph exists | Move from chunk-based to claim-based extraction |
| 3.3 Run contradiction detection | A | Backend / scripts | Detection report generated | Run on real same-project documents |
| 3.4 Human validate findings | H | Markdown / Plane | True/false positives logged | Founder reviews 20 findings manually |
| 3.5 Tune prompts/model | A | Backend / scripts | Accuracy improves | Iterate Step 5 prompt; test stronger models |
| 3.6 Deploy improvement | A | GitHub + backend | New version live | CI/CD deploy |
| 3.7 Measure accuracy | A | `scripts/memo-poc/` | Detection rate tracked | Target: 25% → 50% |

**Drift signals:**
- No real documents ingested in 14 days → building on synthetic data only
- Accuracy flat for 3 weeks → need different model or representation
- Findings not validated by human → no ground truth loop
- Deploys <1/week → velocity collapsing

---

## Pipeline 4: Pilot & Sales
**Purpose:** Convert qualified prospects into paying customers and case studies.

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 4.1 Qualify prospect | H | CRM / Plane | BANT/MEDDIC notes | Confirm they have pain, budget, authority, timeline |
| 4.2 Propose pilot scope | H + A | Markdown / email | Proposal sent | 2-week unpaid pilot: docs in, report out |
| 4.3 Negotiate data terms | H | Email / contract | Terms agreed | Anonymized case-study rights, sample retention |
| 4.4 Ingest pilot documents | A | Backend | Documents loaded | Handle PDFs, DWGs, addenda |
| 4.5 Generate pilot report | A | Backend / markdown | Report delivered | Contradictions, omissions, version conflicts |
| 4.6 Host readout call | H | Zoom/Meet | Call scheduled | Present findings, listen to reaction |
| 4.7 Capture testimonial | H | Email / markdown | Quote secured | Ask for written feedback + intro to peers |
| 4.8 Close LOI or paid deal | H | Email / contract | LOI/signature | Offer next step: paid pilot or subscription |
| 4.9 Write case study | A + H | Markdown / landing page | Case study published | Anonymize and publish on website/LinkedIn |

**Drift signals:**
- 3+ qualified prospects, 0 pilots proposed → fear of rejection
- Pilots run but no readout call scheduled → customer not engaged
- Readouts happen but no LOI → value not clear or wrong buyer
- Case studies not written → marketing pipeline starves

---

## Pipeline 5: Operations & Infrastructure
**Purpose:** Keep all tools running, secure, and backed up so the human can focus on customers.

*For the agent architecture that automates this pipeline, see `docs/research/AGENTIC_ENTERPRISE_STACK_001.md`.*

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 5.1 Weekly planning | H | Plane | OKRs + cycle updated | Sunday 30-min scorecard review |
| 5.2 Daily async standup | H | Plane | 1 update/day | Answer 4 standup questions |
| 5.3 Execute cycle tasks | H + A | Plane | Tasks move to Done | Human owns customer tasks; AI owns cloud tasks |
| 5.4 Backup Plane DB | A | `scripts/backup-plane.sh` | Weekly backup file created | Run every Sunday 2 AM |
| 5.5 Backup Postiz DB | A | `scripts/backup-postiz.sh` | Weekly backup file created | Run every Sunday 2 AM |
| 5.6 Verify backups | A | Shell / logs | Restore test monthly | Document restore procedure |
| 5.7 Monitor uptime | A | Uptime Kuma / UptimeRobot | >99% uptime | Alert on downtime |
| 5.8 Rotate secrets | A | TruffleHog + cloud portal | No exposed keys | Rotate OpenAI keys; scan repo monthly |
| 5.9 SSL renewal | A | Certbot | Certs valid | Auto-renew; verify quarterly |
| 5.10 End-of-cycle retrospective | H | Plane / markdown | Retro doc written | Every 6 weeks |

**Drift signals:**
- Backup script fails → data loss risk
- SSL expires → trust collapse
- Secret exposed in repo → security incident
- Plane cycle >20% incomplete → overcommitment or blocker

---

## Pipeline 6: Founder Decision-Making
**Purpose:** Prevent the founder from optimizing for comfort (building) when the business needs distribution (selling).

| Stage | Owner | Tool | Signal | Next Action |
|-------|-------|------|--------|-------------|
| 6.1 Set quarterly OKRs | H | Plane | 3 OKRs written | See suggested OKRs below |
| 6.2 Choose daily hat | H | Calendar / Plane | Build or Growth declared each morning | No mixed hats in same deep-work block |
| 6.3 Sunday scorecard | H | Markdown / Plane | Scorecard complete | Review pipelines, signals, drift |
| 6.4 Decide pivots/kills | H | Plane / ADR | Decision logged | Document why |
| 6.5 Communicate decisions | H | Slack/email/update | Stakeholders informed | Short weekly update to advisors/friends |

**Drift signals:**
- No OKRs in Plane → directionless execution
- Every day is Build mode → Growth pipeline starves
- Sunday scorecard skipped → drift will go unnoticed
- Decisions not documented → same debate repeats

---

## 4. Suggested 90-Day OKRs

These OKRs feed all six pipelines:

### O1: Validate that VDC agencies will pay for contradiction detection
- KR1: 15 customer discovery calls completed
- KR2: 3 pilot proposals sent
- KR3: 1 paid or unpaid pilot executed with readout

### O2: Establish founder authority in construction-tech LinkedIn
- KR1: 36 LinkedIn posts published (3x/week)
- KR2: 10 inbound DMs from target personas
- KR3: 1 case study or demo video shared

### O3: Harden the MeMo pipeline against real documents
- KR1: 1 real same-project document set ingested
- KR2: Contradiction detection accuracy improved from 25% to 50%
- KR3: 1 demo video recorded and shared

---

## 5. Human vs AI Ownership Matrix

| Category | Human (Founder) | AI / Cloud Agent |
|----------|-----------------|------------------|
| **Strategy** | Set OKRs, decide pivots, choose ICP | Draft OKR options, summarize market data |
| **Customers** | Send requests, run calls, close pilots | Draft templates, synthesize notes, build lists |
| **Content** | Edit, approve, engage | Draft posts, schedule, track metrics |
| **Product** | Validate findings, prioritize features | Code, test, deploy, monitor |
| **Operations** | Review scorecard, make decisions | Backups, uptime, SSL, security scans |
| **Research** | Interpret evidence, choose experiments | Search, summarize, format citations |

**Rule:** If a task requires judgment, relationships, or money, the human owns it. If a task is repeatable, deterministic, or data-heavy, the AI/cloud layer owns it.

---

## 6. Weekly Scorecard Template

Fill every Sunday. One scorecard per pipeline:

```markdown
## Week of [DATE]

### Pipeline 1: Customer Discovery
- Connection requests sent: __ / 50
- Discovery calls completed: __ / 2
- Call syntheses written: __ / calls completed
- Pilot prospects identified: __

### Pipeline 2: Content & Authority
- Posts published: __ / 3
- Daily engagement sessions: __ / 7
- Inbound DMs: __
- Profile views: __

### Pipeline 3: Product Build
- Real document sets ingested: __
- Experiments run: __
- Accuracy: __%
- Deploys: __

### Pipeline 4: Pilot & Sales
- Pilot proposals sent: __
- Pilots in progress: __
- Readout calls: __
- LOIs/signed deals: __

### Pipeline 5: Operations
- Backups successful: __ / 2
- Uptime: __%
- Secrets scan clean: yes / no
- Cycle completion: __%

### Pipeline 6: Founder Decisions
- Days in Build mode: __
- Days in Growth mode: __
- Key decision made: __
- Blocker >7 days: __

### Drift Alerts
- [ ] No customer contact in 7 days
- [ ] Content <80% published
- [ ] Cycle >20% incomplete
- [ ] Backup failed
- [ ] Working outside 90-day OKRs
```

---

## 7. Immediate Next Actions (Today)

1. **Open Plane** → create project "Medha Q3 2026 OKRs" and enter the 3 OKRs.
2. **Block Sunday 30-min scorecard review** in calendar for next 12 weeks.
3. **Write 1-page ICP** → `docs/tasks/prd/ICP_001.md`.
4. **Update LinkedIn headline and About** → align with contradiction-detection positioning.
5. **Build target list of 50** Dubai/GCC VDC/BIM professionals in a spreadsheet or CRM.
6. **Approve 3 connection-request templates** drafted by this agent.
7. **Reply to this agent** with your top OKR so it can be mirrored everywhere.

---

## 8. Related Research

- `docs/research/OPERATING_SYSTEM_FRAMEWORK_001.md` — original OS framework (roles, tools, drift signals)
- `docs/research/AGENTIC_ENTERPRISE_STACK_001.md` — agent architecture that runs these pipelines

## 9. Citations

See `docs/citations/OPERATING_SYSTEM_FRAMEWORK_002.bib` for full references.

---

**Bottom line:** Stop treating Medha like a to-do list. Treat it like six pipelines, each with a human stage and an AI stage. The founder's job is to keep the customer, content, pilot, and decision pipelines flowing. The AI/cloud layer keeps everything else running and surfaces drift before it becomes failure.

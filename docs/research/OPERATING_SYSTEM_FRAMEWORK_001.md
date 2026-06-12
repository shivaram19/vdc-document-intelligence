# Medha Operating System Framework v0.1
**Vision:** An open-source tool ecosystem that gives startups the same organizational velocity, accountability, and stakeholder authority as mature companies — but without the bureaucracy.

---

## 1. The Core Insight

Organizations succeed not because they have better people, but because they have:
1. **Clear roles and authority** — who decides what
2. **Visible workflows** — where work lives
3. **Measured velocity** — how fast things move
4. **Drift detection** — when things go off track
5. **Feedback loops** — continuous correction

Startups fail when these systems are missing or ad-hoc.

Medha's operating system is the **layer that connects open-source tools into a coherent, measurable, self-correcting workflow**.

---

## 2. Stakeholder Authority Model

Every product/service requires multiple teams. Each team needs authority over its domain and visibility into dependencies.

### Roles & Authority

| Role | Authority | Decides | Uses |
|------|-----------|---------|------|
| **Founder/CEO** | Strategic authority | Vision, funding, hires, partnerships | Plane (OKRs), metrics dashboard |
| **Product Lead** | Scope authority | What to build, what not to build, priorities | Plane (cycles, issues), Figma |
| **Engineering Lead** | Technical authority | Architecture, tech debt, implementation | GitHub, Plane, ADRs |
| **Design Lead** | Experience authority | UX, brand, user flows | Figma, Plane |
| **GTM Lead** | Market authority | Messaging, channels, outreach | Postiz, Plane, CRM |
| **Research Lead** | Evidence authority | Citations, experiments, validation | Zotero/Obsidian, docs/research/ |
| **External Stakeholder** | Domain authority | Industry-specific requirements | Plane (guest access), email |

### Authority Principle
> *"Authority without accountability is entitlement. Accountability without authority is oppression."*

Each role gets decision rights **and** a public scorecard for those decisions.

---

## 3. Tool Ecosystem (Open Source First)

| Function | Tool | Self-hosted | Purpose |
|----------|------|-------------|---------|
| **Project Management** | Plane | ✅ | Cycles, issues, roadmaps |
| **Social Scheduling** | Postiz | ✅ | Content calendar, LinkedIn/X |
| **Knowledge Base** | Outline / BookStack | ✅ | Runbooks, SOPs |
| **Documentation** | Git + Markdown | ✅ | Research, ADRs, code docs |
| **Code** | GitHub/GitLab | Partial | Source control, CI/CD |
| **Design** | Penpot / Figma | Partial | UI/UX design |
| **Analytics** | Plausible / Umami | ✅ | Website analytics |
| **CRM** | Twenty / EspoCRM | ✅ | Outreach, investor relations |
| **Communication** | Matrix / Zulip | ✅ | Team chat |
| **Monitoring** | Uptime Kuma | ✅ | Uptime monitoring |
| **Status Page** | Cachet / Upptime | ✅ | Public status page |
| **Wiki** | Wiki.js | ✅ | External docs |

### Medha Current Stack
- ✅ Plane (project mgmt)
- ✅ Postiz (social)
- ✅ Flask backend (product)
- ✅ Git + Markdown (docs)
- 🟡 Monitoring (UptimeRobot free)
- 🔴 CRM (not yet)
- 🔴 Knowledge base (not yet)
- 🔴 Analytics (not yet)

---

## 4. Velocity & Drift Framework

### What Is Velocity?
The rate at which committed work produces measurable outcomes.

**Not:** lines of code, hours worked, meetings attended.  
**Yes:** validated hypotheses shipped, customers reached, experiments completed.

### Velocity Metrics by Function

| Function | Leading Metric | Lagging Metric |
|----------|---------------|----------------|
| Product | Cycle completion rate | Customer satisfaction / retention |
| Engineering | Deploy frequency | Bug escape rate |
| GTM | Content cadence | Inbound qualified conversations |
| Research | Experiments completed | Evidence strength score |
| Operations | Uptime | Security incident count |

### Drift Detection

Drift = Planned velocity − Actual velocity

Types of drift:
1. **Scope drift** — building things not in the cycle plan
2. **Priority drift** — working on low-impact tasks
3. **Technical drift** — accumulating debt that slows future velocity
4. **Market drift** — customer needs changed, plan didn't
5. **Team drift** — burnout, context switching, blocked dependencies

### Drift Signals

| Signal | Source | Threshold |
|--------|--------|-----------|
| Cycle issues not closed | Plane | >20% incomplete at cycle end |
| Content not published | Postiz | <80% of scheduled posts |
| Uptime below target | Uptime Kuma | <99% |
| No customer contact | CRM/Plane | 0 discovery calls in 2 weeks |
| Research not cited | Git | ADR without citation |
| PRs stale | GitHub | >7 days without review |

---

## 5. Dynamic Step-by-Step Workflow

### The Loop: Plan → Execute → Measure → Correct

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   PLAN      │────▶│   EXECUTE    │────▶│   MEASURE   │────▶│   CORRECT   │
│ (OKRs +     │     │ (Cycles +    │     │ (Scorecards │     │ (Retros +   │
│  Cycles)    │     │  Tasks)      │     │  + Drift)   │     │  ADRs)      │
└─────────────┘     └──────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    └──────────────┐
                                                                                   │
                                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                           CONTINUOUS IMPROVEMENT                                    │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Plan (Weekly + Quarterly)
- Quarterly OKRs set in Plane
- 6-week cycles scoped in Plane
- Week 0: stakeholder alignment meeting
- Each cycle has:
  - Clear objective
  - Owner per work item
  - Success metrics
  - Risk register

### Step 2: Execute (Daily + Weekly)
- Daily async updates in Plane (not meetings)
- Weekly velocity check (15 min)
- Issues moved through states: Backlog → In Progress → Review → Done
- Blockers escalated within 24 hours

### Step 3: Measure (Weekly)
- Sunday scorecard review
- Drift dashboard updated
- Leading metrics drive next week's priorities

### Step 4: Correct (End of Cycle)
- Retrospective in Plane
- ADRs for architectural changes
- Process improvements documented
- OKRs adjusted if market signals changed

---

## 6. Authority + Accountability Mechanisms

### RACI Matrix for Every Cycle

| Work Item | Responsible | Accountable | Consulted | Informed |
|-----------|-------------|-------------|-----------|----------|
| MeMo pipeline improvement | Engineer | Product Lead | Research Lead | Founder |
| LinkedIn post | Founder | GTM Lead | — | Team |
| Customer call | Founder | Product Lead | — | Team |
| Security audit | Engineer | Founder | — | All |
| ADR write-up | Engineer | Architect | Product Lead | Team |

### Decision Logs
Every significant decision is documented:
- ADR in `docs/decisions/` for technical decisions
- Decision note in Plane for product decisions
- Email/summary for stakeholder decisions

### Public Scorecards
Each role has a public (internal) scorecard updated weekly:
- What they committed to
- What they delivered
- What they learned
- What they need

---

## 7. Implementation Roadmap for Medha

### Phase 1: Foundation (Weeks 1-2)
- [ ] Define roles: Founder, Product, Engineering, GTM, Research
- [ ] Set Q3 OKRs in Plane
- [ ] Create first 6-week cycle
- [ ] Set up weekly scorecard template
- [ ] Deploy remaining critical tools:
  - [ ] Uptime monitoring (Uptime Kuma)
  - [ ] Analytics (Plausible/Umami)
  - [ ] CRM (Twenty)

### Phase 2: Workflow (Weeks 3-4)
- [ ] Run first cycle with daily async updates
- [ ] Establish Sunday scorecard ritual
- [ ] Create RACI for top 10 recurring tasks
- [ ] Document all runbooks in knowledge base

### Phase 3: Velocity Measurement (Weeks 5-6)
- [ ] Build drift dashboard (spreadsheet → lightweight app)
- [ ] Define thresholds for each drift signal
- [ ] Automate metric collection where possible
- [ ] First retrospective and process correction

### Phase 4: Scale (Months 2-3)
- [ ] Onboard external stakeholders with guest access
- [ ] Integrate GitHub commits into Plane
- [ ] Add public status page
- [ ] Build lightweight CRM workflow

---

## 8. Metrics Dashboard (MVP)

A simple markdown/scorecard updated weekly:

```markdown
## Week of 2026-06-15

### Product
- Cycle completion: __%
- Bugs introduced: __
- Customer calls: __/target 2

### Engineering
- Deploys: __
- Tests added: __
- ADRs written: __

### GTM
- Posts published: __/3
- Follower growth: __
- Inbound DMs: __

### Research
- Papers read: __
- Experiments run: __
- Citations added: __

### Drift Alerts
- [ ] Cycle falling behind
- [ ] Content off schedule
- [ ] Uptime issue
- [ ] No customer contact
```

---

## 9. Key Principles

1. **Tools serve the workflow, not the other way around.**
2. **Every role has both authority and a scorecard.**
3. **Velocity is measured in outcomes, not activity.**
4. **Drift is detected early and corrected quickly.**
5. **Decisions are documented and revisable.**
6. **Open source first, paid tools only when necessary.**

---

## 10. Next Steps

1. **Confirm roles** — who plays which role (even if one person wears multiple hats)
2. **Set Q3 OKRs** — add to Plane
3. **Pick the next tool to deploy** — Uptime Kuma, CRM, or Analytics
4. **Run first 6-week cycle** — starting with MeMo hardening + GTM launch

---

**This framework turns Medha from a collection of tools into an operating system.**

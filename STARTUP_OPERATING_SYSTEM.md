# Medha Startup Operating System
**Goal:** Run Medha as an organized, metrics-driven cloud startup with clear frameworks and goals.

---

## Current State

### What We Have Built

| Layer | Tool | URL | Status |
|-------|------|-----|--------|
| Landing page | Static nginx | https://medha.trayini.ai | ✅ Live |
| Project management | Plane | https://plane.trayini.ai | ✅ Live |
| Social scheduling | Postiz | http://20.193.129.119:4007 | ✅ Live (direct port) |
| Document intelligence backend | Flask | http://20.193.129.119:5001 | ✅ Running |
| Agent bridge | WebSocket | ws://20.193.129.119:8765 | ✅ Running |
| Research corpus | Markdown | Git repo | 🟡 Building |
| Security audit | Checklist | `SECURITY_PILOT_CHECKLIST.md` | 🟡 In progress |

---

## Framework: Medha Operating System (MOS)

### 1. Goal Framework: Quarterly OKRs

Set 3 Objectives per quarter, each with 2-3 Key Results.

**Example Q3 2026:**

**O1: Validate product-market fit in construction document intelligence**
- KR1: Complete 15 customer discovery calls with VDC coordinators/PMs
- KR2: Achieve >60% contradiction detection rate on real project documents
- KR3: Build a waitlist of 50 interested construction professionals

**O2: Establish founder authority and inbound pipeline**
- KR1: Publish 36 LinkedIn posts (3x/week)
- KR2: Reach 2,000 LinkedIn followers in construction tech
- KR3: Generate 10 inbound DMs/calls from content

**O3: Build a stable, secure, scalable product foundation**
- KR1: All services on HTTPS with custom subdomains
- KR2: Complete security pilot checklist
- KR3: Achieve 99% uptime for plane.trayini.ai and medha.trayini.ai

---

### 2. Execution Framework: 6-Week Cycles (Shape Up style)

Each cycle has:
- **Week 0:** Planning — pick priorities from OKRs, define scope
- **Weeks 1-5:** Build — focused execution, no scope creep
- **Week 6:** Cooldown — refactor, docs, customer calls, planning next cycle

Cycle deliverables are tracked in Plane.

---

### 3. Communication Framework: Single Sources of Truth

| Information | Source | Why |
|-------------|--------|-----|
| Tasks & priorities | Plane | One place for execution |
| Research & decisions | Git repo (`docs/research/`, `docs/decisions/`) | Cited, versioned |
| Runbooks & setup | READMEs in repo | Reproducible |
| Customer insights | Plane project + shared notes | Actionable feedback |
| Metrics | Spreadsheet/Plane dashboard | Weekly review |

---

### 4. Development Framework: Trunk-Based + ADRs

- **Main branch is always deployable**
- **Small, frequent commits** with clear messages
- **Every architectural decision** has an ADR in `docs/decisions/`
- **Every code change** cites a reason (per `AGENTS.md`)
- **Feature flags** for risky changes (future)

---

### 5. Cloud Framework: Service Per Subdomain

Each service gets its own subdomain with SSL and reverse proxy:

```
medha.trayini.ai      → Landing page + marketing site
app.trayini.ai        → Future Medha web app
plane.trayini.ai      → Project management
postiz.trayini.ai     → Social media scheduling
api.trayini.ai        → Medha API (when ready)
docs.trayini.ai       → Documentation site
status.trayini.ai     → Status page (future)
```

---

### 6. Security Framework: Defense in Depth

From `SECURITY_PILOT_CHECKLIST.md`:
- Secrets in `.env`, never in code
- SSL everywhere
- Least-privilege firewall rules
- Regular backups
- Dependency updates
- Access control (disable public signups when not needed)

---

### 7. Metrics Framework: Weekly Scorecard

Track every Sunday:

| Metric | Target | Source |
|--------|--------|--------|
| Plane uptime | >99% | UptimeRobot |
| LinkedIn followers | +50/week | LinkedIn analytics |
| LinkedIn post impressions | >3K/post | LinkedIn analytics |
| Discovery calls | 1/week | Plane CRM |
| Product commits | 5/week | Git |
| Contradiction detection rate | >60% | TEST reports |

---

## Immediate Action Plan (Next 2 Weeks)

### Week 1: Foundation & Focus

- [ ] Finalize Q3 OKRs and add to Plane
- [ ] Move Postiz to `postiz.trayini.ai` with SSL
- [ ] Complete security pilot top 5 items
  - [ ] Rotate OpenAI keys
  - [ ] Change Plane admin password
  - [ ] Run OS updates
  - [ ] Set up UptimeRobot monitoring
  - [ ] Review Azure NSG rules
- [ ] Create first 6-week cycle plan in Plane
- [ ] Schedule 3 customer discovery calls

### Week 2: Content & Validation

- [ ] Publish 3 LinkedIn posts from playbook
- [ ] Connect LinkedIn to Postiz
- [ ] Schedule 2 weeks of content
- [ ] Collect 1 real same-project document set
- [ ] Run MeMo TEST-002 planning

---

## Goals to Meet (90 Days)

1. **Product:** Real contradiction detection >60% on same-project docs
2. **GTM:** 15 discovery calls, 50 waitlist signups
3. **Brand:** 2,000 LinkedIn followers, 36 posts published
4. **Ops:** 99% uptime, all services on HTTPS subdomains, security checklist complete
5. **Research:** 5 ADRs written, 10 papers added to corpus

---

## Tooling Stack

| Purpose | Tool | Alternative |
|---------|------|-------------|
| Project mgmt | Plane | Linear, Notion |
| Social scheduling | Postiz | Buffer, Hootsuite |
| Docs/Wiki | Git + Markdown | Notion, Outline |
| Landing page | Static HTML | Webflow, Framer |
| API/backend | Flask + Python | FastAPI, Django |
| Auth (future) | Authentik/Keycloak | Auth0, Clerk |
| Monitoring | UptimeRobot + nginx logs | Datadog, Grafana |
| Backups | cron + pg_dump | Restic, Borg |
| CI/CD (future) | GitHub Actions | GitLab CI |

---

## Decision Log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-06-12 | Use OKRs + 6-week cycles | Balances long-term goals with focused execution |
| 2026-06-12 | One subdomain per service | Clean, scalable, SSL per service |
| | | |

---

## Next Decision Needed

**Which do you want to tackle first?**

A. **Move Postiz to postiz.trayini.ai** (finish subdomain standardization)  
B. **Set up OKRs in Plane** (organize goals)  
C. **Complete security top 5** (rotate keys, change passwords, updates, monitoring)  
D. **Plan first 6-week cycle** (focused product execution)

# Medha Pilot Checklist
**Goal:** Operational founder workflow with purpose, plan, and preparation tracked centrally.

---

## Phase 0: Current State Inventory

### Deployed Services

| Service | URL | Purpose | Status |
|---------|-----|---------|--------|
| Medha Landing Page | http://20.193.129.119 | Public project overview | ✅ Running |
| Plane (Project Mgmt) | https://plane.trayini.ai | Central task tracker | ✅ Running |
| Postiz (Social Scheduler) | http://20.193.129.119:4007 | LinkedIn/Twitter scheduling | ✅ Running |
| Temporal UI | http://20.193.129.119:8083 | Postiz workflow monitoring | ✅ Running |
| Flask Backend | http://20.193.129.119:5001 | Document intelligence API | ✅ Running |
| WebSocket Agent Bridge | ws://20.193.129.119:8765 | Agent mesh bridge | ✅ Running |

### Server Access

- **Public IP:** 20.193.129.119
- **Domain:** drmath.trelolabs.com
- **OS:** Ubuntu (Azure VM)
- **Firewall:** UFW + Azure NSG

### Existing Research & Assets

| Asset | Location | Status |
|-------|----------|--------|
| Architecture map (7 systems, 30+ bottlenecks) | `docs/tasks/prd/ARCHITECTURE_MAP_001-systems-and-bottlenecks.md` | ✅ Done |
| MeMo pipeline test report | `scripts/memo-poc/TEST_REPORT_001.md` | ✅ Done |
| Synthetic contradiction corpus | `real_construction_docs_contradictions/` | ✅ Done |
| Construction AI research landscape | `docs/research/memo-analysis/CONSTRUCTION_AI_RESEARCH_LANDSCAPE_2026.md` | ✅ Done |
| Social media playbook | `docs/tasks/prd/SOCIAL_MEDIA_PLAYBOOK_001.md` | ✅ Done |
| LinkedIn profile optimization | `docs/tasks/prd/SOCIAL_MEDIA_PROFILE_OPTIMIZATION.md` | ✅ Done |
| Master tracker | `MEDHA_MASTER_TRACKER.md` | ✅ Done |
| Customer meeting playbook | `MEDHA_CUSTOMER_MEETING_PLAYBOOK.md` | ✅ Done |
| Research corpus | `docs/research/`, `docs/decisions/`, `docs/citations/` | 🟡 Ongoing |

---

## Phase 1: Secure the Foundation (Do First)

**Purpose:** Close security gaps before any public activity.

- [ ] **1.1 Rotate OpenAI API keys**
  - Delete Key A (`sk-proj-VHFX...`)
  - Delete Key B (`sk-proj--htNVT...`)
  - Generate new key
  - Update `postiz/.env` and root `.env`
  - Verify Postiz still works

- [ ] **1.2 Verify no secrets in git**
  - Run `git status`
  - Confirm `.env` and `postiz/.env` are untracked
  - Confirm `plane/plane-app/plane.env` and `plane/plane-app/.env` are untracked
  - Run `git log --all --grep='sk-proj'` to check commit history

- [ ] **1.3 Document all secrets location**
  - Root `.env` → OpenAI key, app secrets
  - `postiz/.env` → OpenAI key for Postiz
  - `plane/plane-app/.env` → Plane DB, RabbitMQ, MinIO, Django secrets
  - Keep a private note of these (not in repo)

- [ ] **1.4 Set up basic uptime monitoring**
  - Option A: UptimeRobot free plan (monitor landing page, Plane, Postiz)
  - Option B: Simple cron job on server that sends email/telegram on failure
  - Document alerts in `plane/README.md` or `postiz/README.md`

---

## Phase 2: Configure Plane as Command Center

**Purpose:** One place for all Medha work.

- [ ] **2.1 Create Medha workspace in Plane**
  - Open https://plane.trayini.ai
  - Sign up as admin
  - Create workspace: "Medha"

- [ ] **2.2 Create projects**
  - Product Development
  - Go-to-Market
  - Research & Validation
  - Operations

- [ ] **2.3 Import tasks from `MEDHA_MASTER_TRACKER.md`**
  - Copy each tracker item as a Plane issue
  - Tag by priority: P0 (rotate keys), P1 (MeMo hardening), P2 (backend refactor), P3 (Dubai corpus)

- [ ] **2.4 Set up views**
  - Kanban view by status (Not Started / In Progress / Blocked / Done)
  - List view by priority
  - Calendar view for GTM posts and outreach

- [ ] **2.5 Create first cycle/sprint**
  - Sprint 1: "Foundation + First Post" (1 week)
  - Include: key rotation, Plane setup, LinkedIn profile update, first LinkedIn post

---

## Phase 3: Establish Founder Presence

**Purpose:** Build authority before asking for meetings.

- [ ] **3.1 Optimize LinkedIn profile**
  - Update headline: "Founder, Medha | AI for construction document intelligence | IIT Madras '25 | Researcher"
  - Create banner image (Canva/Figma)
  - Rewrite About section
  - Add featured: Medha landing page, TEST_REPORT_001, architecture map

- [ ] **3.2 Connect LinkedIn to Postiz**
  - Go to https://www.linkedin.com/developers/apps
  - Create app, add "Sign In with LinkedIn" and "Share on LinkedIn" products
  - Set redirect URI: `http://20.193.129.119:4007/api/oauth/authorize`
  - Add `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` to `postiz/docker-compose.yaml`
  - Restart Postiz
  - Connect account in Postiz UI

- [ ] **3.3 Schedule first 3 LinkedIn posts**
  - Use `docs/tasks/prd/SOCIAL_MEDIA_FIRST_3_POSTS.md`
  - Schedule for Tuesday 7:30 AM GST, Thursday 7:30 AM GST, Sunday 7:30 AM GST
  - Set reminder to engage for 60 minutes after each post

- [ ] **3.4 Begin daily engagement routine**
  - Comment on 3 VDC/BIM posts
  - Comment on 2 AI/construction posts
  - Send 1 personalized connection request

---

## Phase 4: Validate Product Thesis

**Purpose:** Prove Medha finds contradictions in real documents.

- [ ] **4.1 Collect same-project documents**
  - Source 1: Publicly available construction bid sets
  - Source 2: University project manuals with addenda
  - Source 3: Reach out to network for anonymized samples
  - Minimum: 1 project with architectural + structural + MEP + fire protection specs

- [ ] **4.2 Build real contradiction ground truth**
  - Manually identify 10+ contradictions
  - Document page/section references
  - Save as `real_construction_docs_contradictions/GROUND_TRUTH_002.md`

- [ ] **4.3 Improve MeMo Step 5**
  - Rewrite `scripts/memo-poc/reflection_synthesis_pipeline_parallel.py` Step 5 prompt
  - Add explicit contradiction detection instructions
  - Test GPT-4o vs GPT-4 vs fine-tuned model
  - Target: >60% detection rate on real corpus

- [ ] **4.4 Run TEST-002**
  - Document speed, cost, and detection rate
  - Update `scripts/memo-poc/TEST_REPORT_002.md`

---

## Phase 5: Product Architecture Decisions

**Purpose:** Decide what to build vs. buy vs. defer.

- [ ] **5.1 Decide enhancement track priority**
  - Option A: Backend refactor
  - Option B: Frontend polish
  - Option C: MeMo hardening (recommended)
  - Option D: Dubai corpus
  - Option E: PicoCloth stabilize

- [ ] **5.2 Decide PicoCloth fate**
  - Option A: Integrate into backend
  - Option B: Archive / deprioritize
  - Option C: Use only for personal task automation

- [ ] **5.3 Decide deployment strategy**
  - Keep current VM with multiple services?
  - Move to subdomains (postiz.drmath.trelolabs.com, plane.drmath.trelolabs.com)?
  - Add HTTPS/SSL certificates?

- [ ] **5.4 Write ADR for chosen track**
  - File: `docs/decisions/ADR_XXX_<track-name>.md`
  - Include context, decision, consequences, alternatives rejected

---

## Phase 6: Customer Development

**Purpose:** Learn from the market, not build in isolation.

- [ ] **6.1 Build target list**
  - 20 Dubai/GCC VDC coordinators
  - 10 construction PMs
  - 5 BIM consultants
  - 5 ConTech investors/amplifiers

- [ ] **6.2 Prepare outreach**
  - Use consultative approach (not sales pitch)
  - Template: "I'm researching how teams catch document conflicts early..."
  - Track in Plane project "Go-to-Market"

- [ ] **6.3 Book 5 discovery calls**
  - Goal: understand current workflow and pain points
  - Not: pitch Medha
  - Offer: 15-minute call, share findings afterward

- [ ] **6.4 Synthesize insights**
  - Document patterns from calls
  - Update `MEDHA_CUSTOMER_MEETING_PLAYBOOK.md`
  - Feed insights back into product roadmap

---

## Phase 7: Operationalize the Workflow

**Purpose:** Make the system self-sustaining.

- [ ] **7.1 Weekly review ritual**
  - Every Sunday: review Plane board
  - Update `MEDHA_MASTER_TRACKER.md` from Plane
  - Plan 3 priorities for the week

- [ ] **7.2 Content calendar in Plane**
  - Create issues for each planned LinkedIn post
  - Attach post text and hashtags
  - Mark published date

- [ ] **7.3 Metrics dashboard**
  - Track weekly: LinkedIn impressions, engagement rate, DMs, calls booked
  - Track monthly: demo calls, beta signups, key milestones
  - Simple spreadsheet or Plane custom properties

- [ ] **7.4 Backup strategy**
  - Plane: `docker compose exec plane-db pg_dump ...` weekly
  - Postiz: `docker compose exec postiz-postgres pg_dump ...` weekly
  - Store backups in `backups/` directory or cloud storage

---

## Decision Log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-06-11 | Deploy Plane on port 8091 | Avoid nginx conflict |
| 2026-06-11 | Deploy Postiz on port 4007 | Free port, separate from main app |
| 2026-06-11 | Use IP:port instead of subdomains for now | Faster setup; subdomains can be added later |
| | | |

---

## Next Actions (This Week)

1. **Rotate OpenAI keys** — 30 min
2. **Create Plane workspace + import tracker** — 1 hour
3. **Update LinkedIn headline + About** — 1 hour
4. **Connect LinkedIn to Postiz** — 30 min
5. **Schedule first LinkedIn post** — 30 min
6. **Send 5 connection requests to VDC professionals** — 30 min

---

## Success Criteria for Pilot

By end of Week 2:
- [ ] Plane is actively used with ≥20 issues
- [ ] 3 LinkedIn posts published
- [ ] ≥10 meaningful engagement interactions
- [ ] 1 customer discovery call booked
- [ ] OpenAI keys rotated and secure
- [ ] TEST-002 plan documented in Plane

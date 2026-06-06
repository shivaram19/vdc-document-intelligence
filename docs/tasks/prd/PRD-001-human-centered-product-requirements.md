# PRD-001: Human-Centered Product Requirements for Medha
## Construction Document Intelligence — VDC ↔ Construction Interface

**Date:** 2026-05-03
**Status:** Council of Ten Consensus — Approved
**Scope:** Product requirements derived from human workflow research, not feature wishlists
**Research Basis:** BFS-014, BFS-015, BFS-016, BFS-017, BFS-018

---

> *"We are not building a tool. We are building a teammate for the people who hold construction projects together with documents."*

---

## 1. The People We Serve

### 1.1 Primary Personas (Direct Medha Users)

| Persona | Role | Pain | Current Day | Medha Value |
|---------|------|------|-------------|-------------|
| **Priya** | VDC Coordinator | Spends 20+ hrs/week on submittal review, clash triage, RFI drafting [BFS-014] | 7 AM: BIM fly-through. 9 AM: Submittal review (45–120 min each). 12 PM: Clash meeting. 2 PM: False-positive filtering. 5 PM: RFI drafting. 7 PM: Admin catch-up. | Cuts submittal review by 70%. Auto-drafts RFIs from contradictions. Groups clashes by root cause. |
| **David** | Project Manager | 5.5 hrs/week lost searching for documents; $859K RFI costs per project [BFS-015][BFS-017] | Morning: RFI status review. Midday: Stakeholder calls about delays. Afternoon: Chase down document versions for dispute prep. | Instant document retrieval. RFI cost tracker. Early warning on document conflicts. |
| **Maria** | Document Controller | Full-time gatekeeper managing transmittals, versions, distribution on mega-projects [BFS-015] | All day: Route drawings to 15+ parties. Verify everyone has correct revision. Audit trail for compliance. | Auto-version control. Distribution tracking. Compliance-ready audit logs. |
| **Ahmed** | MEP Coordinator | Daily clash escalation with VDC; 48–72 hour response deadlines [BFS-014] | Morning: Review clash reports. Midday: Field coordination. Afternoon: Escalate unresolved clashes. Evening: Update fabrication models. | Clash-to-RFI auto-escalation. MEP-specific spec cross-referencing. Fabrication drawing validation. |
| **Sarah** | Design Coordinator | Redline PDFs, comment matrices, transmittals across A/E and construction [BFS-015] | Review markups from CM. Compile comment matrices. Track transmittal receipt. Verify design intent in coordinated models. | Design change impact analysis. Auto-comment matrix generation. Transmittal tracking. |

### 1.2 Secondary Personas (Beneficiaries)

| Persona | Role | How They Benefit |
|---------|------|------------------|
| **James** | Construction Manager | Receives pre-validated coordination drawings; fewer field surprises |
| **Fatima** | QA/QC Manager | Accesses complete spec-to-drawing compliance trails for inspections |
| **Robert** | Estimator / Preconstruction | Uses contradiction-free specs for accurate takeoffs and bids |
| **Lakshmi** | Commissioning Agent | Gets as-built-aligned record models with complete documentation |

### 1.3 The Human Network

```
VDC Agency (Priya) ←→ Construction Company (David, Maria, Ahmed, Sarah)
         ↑                    ↑
    [Medha Interface]    [Medha Interface]
         ↓                    ↓
    Federated Models    Document Control
    Clash Reports       RFI/Submittal Logs
    Coordination DWGs   Field Reports
    BEP Compliance      Change Orders
```

**Key insight [BFS-015]:** The VDC ↔ Construction interface is not a technology problem. It is a **trust and accountability problem**. Every RFI is a failure of prior communication. Every clash report is a delayed conversation. Medha must make the invisible visible *before* it becomes expensive.

---

## 2. The Platform Reality They Navigate

### 2.1 No Unified Platform Exists

The construction industry does not have a "GitHub." VDC coordinators and construction PMs operate across **4–6 fragmented tools daily**, manually translating data between them [BFS-018].

| Persona | Tools Used Daily | Time Lost to Platform Switching |
|---------|-----------------|--------------------------------|
| **Priya (VDC Coordinator)** | Revit → Navisworks → ACC → Bluebeam → Excel → Email | ~2.5 hrs/day |
| **David (Project Manager)** | Procore → Email → ACC → Bluebeam → Primavera | ~1.5 hrs/day |
| **Maria (Document Controller)** | Aconex → ACC → SharePoint → Email → Excel | ~2 hrs/day |

### 2.2 The Cross-Organizational Breakdown

**VDC agencies and construction companies often use different platforms.** A Navisworks clash report becomes a Procore RFI only through manual copy-paste. The MDPI 2025 metro line case study documented Aconex + ACC + SharePoint + Unifier + email operating simultaneously, with a sync script that "does not function reliably" [BFS-018 §4.2].

**The "GitHub for construction" (Speckle) exists but is used by <1% of practitioners.** It requires technical setup beyond typical VDC coordinator skillsets and has no native document management [BFS-018 §3].

### 2.3 What Platforms Capture vs. What They Miss

| What Platforms Log | What They Miss | Why It Matters |
|-------------------|----------------|----------------|
| "Transmittal T-284 sent" | Did recipient open it? Scroll to critical change on page 47? | Maria sends Rev D; David builds from Rev C |
| "RFI-412 status: Open" | Is someone working on it? Who is blocked? | 22% of RFIs receive no response (Navigant) |
| "Clash report uploaded" | Did structural engineer review before meeting? | Meeting wasted re-explaining known issues |
| "Model v3.2 published" | Who is still working on v3.1? What changed? | Trade contractors build from outdated PDFs |

**Key insight [BFS-018]:** Platforms optimize for **document transmission**, not **information comprehension**. Medha must close the "receipt without understanding" gap.

---

## 3. What These People Actually Do (Day-in-the-Life)

### 2.1 Priya (VDC Coordinator) — Tuesday

| Time | Activity | Documents Touched | Pain Level | With Medha |
|------|----------|-------------------|------------|------------|
| 07:00 | BIM fly-through with superintendent | Revit model, last night's clash report | Low | Same; but clash report is pre-prioritized |
| 09:00 | Submittal review: HVAC shop drawings | Spec Section 23 31 13, Drawing A-101, RFI-284 | **High** — 90 min to cross-reference | **10 min** — Medha highlights contradictions automatically |
| 11:00 | Email triage: 47 unread, 12 RFIs pending | RFI log, transmittal register | High | RFI status dashboard with auto-reminders |
| 12:00 | Weekly clash meeting (MEP vs. Structural) | Navisworks clash report (200+ clashes) | **High** — 2 hrs filtering false positives | **30 min** — Medha groups by root cause, filters noise |
| 14:30 | Update federated model | 6 discipline models, version check | Medium | Version conflict alerts before merge |
| 16:00 | Draft RFIs from morning findings | Word template, spec references, drawing callouts | **High** — 2 hrs formatting and citing | **15 min** — Auto-generated with citations |
| 18:30 | Administrative catch-up | Submittal log, meeting minutes | Medium | Auto-logged; minimal catch-up |

**Current Tuesday total: ~10.5 hrs of document work**
**With Medha Tuesday total: ~4.5 hrs of document work**
**Time returned to Priya: 6 hours → for proactive design optimization, team mentoring, or going home on time.**

### 2.2 David (Project Manager) — Thursday

| Time | Activity | Documents Touched | Pain Level | With Medha |
|------|----------|-------------------|------------|------------|
| 08:00 | Review overnight RFI/submittal status | Procore dashboard, 23 open items | Medium | Medha priority inbox: 3 critical, 20 routine |
| 09:30 | Owner call: "Why is the lobby ceiling 10' not 12'?" | Spec 09 50 00, Drawing A-201, RFI-112 response | **High** — 30 min searching for root cause | **2 min** — Medha shows contradiction chain |
| 10:30 | Dispute prep: contractor claims spec was ambiguous | Full spec set, addenda, ASI-7, meeting minutes | **High** — 4 hrs document archaeology | **20 min** — Medha generates compliance trail |
| 14:00 | Schedule review: RFIs on critical path | RFI log, Primavera schedule | High | Auto-flagged: 5 RFIs blocking 3 trades |
| 16:00 | Stakeholder presentation | PowerPoint, model screenshots | Low | Medha exports contradiction summary slides |

---

## 4. The Information They Exchange

### 3.1 Documents That Cross the VDC ↔ Construction Boundary

| Document | Direction | Frequency | Format | Medha Role |
|----------|-----------|-----------|--------|------------|
| **RFI** | Both ways | 10–15 per $1M project value [BFS-015] | Standardized form (PDF/Excel/Procore) | Auto-detect contradictions before RFI needed. Auto-draft from detected issues. |
| **Submittal (Shop Drawing / Product Data)** | Construction → VDC → A/E | Per trade package schedule | PDF package + transmittal | Pre-screen against specs before submission. Auto-check for clashes. |
| **Clash Report** | VDC → Construction | Weekly during coordination | HTML/XML/Navisworks + screenshots | Prioritize by severity. Group by root cause. Filter false positives. |
| **Coordination Drawing** | VDC → Construction | Per floor/zone completion | CAD/PDF composite | Validate against latest spec revisions. Flag outdated references. |
| **BEP (BIM Execution Plan)** | VDC → Construction (approved by PM) | Pre-contract + revisions | PDF/Word + responsibility matrix | Compliance checker: does model meet BEP LOD/LOI? |
| **Transmittal** | Both ways | Daily | Form + attachment list | Auto-track receipt. Verify correct revision distributed. |
| **Field Report / Daily Log** | Construction → VDC | Daily | Digital form or PDF | Extract deviations for model update queue. |
| **As-Built Markup** | Construction → VDC | Weekly | PDF redlines / Revit markups | Compare against spec compliance. Generate punch list items. |
| **Change Order** | Construction → VDC (when design changes) | As triggered | CO package + sketches | Impact analysis: which specs, drawings, models affected? |

### 3.2 The RFI as a Symptom

**Every RFI represents a failure [BFS-017]:**
- Average cost: **$1,080**
- Average per project: **796 RFIs**
- Average response time: **9.7 days**
- Project cost impact: **$859,000**
- Critical path impact: **22% of RFIs delay schedule**

**Medha's mission:** Reduce RFIs by catching contradictions *before* they become questions.

| RFI Root Cause | % of Total | Medha Prevention |
|---------------|------------|------------------|
| Spec-drawing contradiction | 35% | Auto-scan on upload; flag before field sees it |
| Missing information in design | 25% | Cross-reference completeness check |
| Ambiguous specification language | 20% | NLP clarity scoring; suggest rewrites |
| Outdated drawing revision | 15% | Version control with auto-notification |
| Code compliance gap | 5% | Automated code checking against Dubai DM |

---

## 5. Pain Points (Quantified)

### 4.1 Top 10 Pain Points by Persona

| Rank | Pain Point | Primary Victims | Frequency | Cost Impact | Medha Solution |
|------|-----------|-----------------|-----------|-------------|----------------|
| 1 | **Searching for the right document version** | David, Maria, Sarah | Daily | $19,732/worker/year [BFS-017] | Instant semantic search across all project docs |
| 2 | **Submittal review: spec-to-drawing cross-check** | Priya, Ahmed, Sarah | 3–5×/week | 20+ hrs/week [BFS-014] | AI contradiction detection; 70% time reduction |
| 3 | **Clash report false-positive triage** | Priya, Ahmed | Weekly | 2–5 hrs/meeting | Root-cause grouping; ML-based noise filtering |
| 4 | **RFI drafting and tracking** | Priya, David, Maria | Daily | $1,080/RFI [BFS-017] | Auto-draft from detected issues; status dashboard |
| 5 | **Version control chaos** | Maria, Sarah | Continuous | Rework, disputes | Auto-versioning with distribution tracking |
| 6 | **Dispute document archaeology** | David, Maria | Per dispute | $60M avg dispute value [BFS-017] | Complete audit trail; compliance report generation |
| 7 | **Code compliance verification** | Ahmed, Fatima | Per inspection | Delay costs, re-inspection | Automated Dubai DM code checking |
| 8 | **Transmittal receipt confirmation** | Maria | Daily | Follow-up time | Auto-read receipts; escalation on non-receipt |
| 9 | **Design change impact assessment** | Sarah, David | Per change order | Scope creep, budget overrun | Impact analysis: affected specs, drawings, models |
| 10 | **Multilingual document coordination** | All (GCC projects) | Daily | Miscommunication, rework | Multilingual search; auto-translation of key terms |
| 11 | **Platform fragmentation / context loss at handoffs** | Priya, David, Maria, Ahmed | Every cross-platform transfer | 15–25% labor productivity loss on rework-affected crews | Cross-platform context bridge; unified semantic layer |
| 12 | **Regulatory-to-project disconnect (Dubai DM)** | Ahmed, Fatima | Per permit submission | Permit delays, re-submissions | Auto-sync DM portal outputs to project document set |

### 4.2 The Hidden Tax

| Hidden Cost | Annual/Project | Source |
|-------------|---------------|--------|
| Time spent searching for documents | 5.5–9.3 hrs/week per person | McKinsey, FMI [BFS-017] |
| Non-productive document work (10-person team) | 38 person-hours/week | FMI [BFS-017] |
| RFI overhead per project | $859,000 | Navigant [BFS-017] |
| Rework from poor data | 5–10% of project cost | CII [BFS-017] |
| Dispute legal costs | $15–20B (U.S. annual) | Arcadis [BFS-017] |
| Schedule delay from document issues | 22% of RFIs on critical path | Autodesk [BFS-017] |

---

## 6. Medha Value Proposition: By Persona

### 5.1 Priya (VDC Coordinator)

| Current State | Medha State | Time Saved | Quality Gain |
|--------------|-------------|------------|--------------|
| 90 min submittal review | 10 min contradiction scan | 80 min | Catches issues human eye misses |
| 2 hrs clash false-positive filtering | 30 min root-cause grouping | 90 min | Better prioritization |
| 2 hrs RFI drafting | 15 min auto-generation | 105 min | Consistent formatting + citations |
| 1 hr version checking | 5 min conflict alerts | 55 min | Prevents merge errors |
| **Daily total: ~6 hrs** | **Daily total: ~1.5 hrs** | **~4.5 hrs/day** | **Fewer errors, faster response** |

**Annual value to Priya:** 4.5 hrs/day × 250 days = **1,125 hours returned** ≈ 28 full work weeks.

### 5.2 David (Project Manager)

| Current State | Medha State | Impact |
|--------------|-------------|--------|
| Reactive RFI management | Proactive contradiction prevention | 34–68% RFI reduction = $290K–$585K saved |
| Document archaeology for disputes | Instant compliance trail generation | Dispute prep: 4 hrs → 20 min |
| Manual schedule impact tracking | Auto-flagged critical path RFIs | Fewer schedule surprises |

### 5.3 Maria (Document Controller)

| Current State | Medha State | Impact |
|--------------|-------------|--------|
| Manual transmittal routing | Auto-distribution with receipt tracking | 50% reduction in follow-up time |
| Version audit by hand | Complete auto-generated audit log | Compliance-ready in real-time |
| "Did everyone get Rev C?" anxiety | Instant distribution status dashboard | Peace of mind |

### 5.4 Ahmed (MEP Coordinator)

| Current State | Medha State | Impact |
|--------------|-------------|--------|
| Manual spec cross-reference for clashes | Auto-spec lookup per clash element | 60% faster clash resolution |
| Escalation via email chains | Structured clash-to-RFI workflow | Clear accountability |
| Fabrication drawing validation | Pre-fabrication compliance check | Fewer field rejects |

---

## 7. Product Requirements (Derived from Human Needs)

### 6.1 Must-Have (P0) — Ship Without These = No Value

| ID | Requirement | Persona | Research Basis |
|----|-------------|---------|---------------|
| P0-1 | **Contradiction Detection:** Auto-scan uploaded specs and drawings for conflicts (material mismatch, dimension mismatch, code violation) | Priya, Ahmed, David | BFS-014 §4, BFS-017 §4 |
| P0-2 | **Semantic Document Search:** Find any document, section, or clause via natural language query | David, Maria, Sarah | BFS-017 §3 (5.5 hrs/week lost searching) |
| P0-3 | **RFI Auto-Draft:** Generate structured RFIs from detected contradictions with spec citations | Priya, David | BFS-014 §3.5, BFS-017 §4 ($1,080/RFI) |
| P0-4 | **Version Control:** Track document revisions, notify stakeholders of changes, maintain audit trail | Maria, Sarah | BFS-015 §2 (Document Controller role) |
| P0-5 | **Dubai DM Code Compliance:** Check specs and drawings against Dubai Municipality building codes | Ahmed, Fatima | BFS-015 §9 (Dubai specifics) |

### 6.2 Should-Have (P1) — Differentiating Features

| ID | Requirement | Persona | Research Basis |
|----|-------------|---------|---------------|
| P1-1 | **Clash Report Intelligence:** Group clashes by root cause, filter false positives, prioritize by severity | Priya, Ahmed | BFS-014 §3.4 |
| P1-2 | **Submittal Pre-Screen:** Check shop drawings against specs and coordinated models before submission | Priya, Sarah | BFS-015 §3 (submittal flow) |
| P1-3 | **Impact Analysis:** Show all affected specs, drawings, and models when a change is proposed | Sarah, David | BFS-015 §3.9 (change orders) |
| P1-4 | **Multilingual Support:** Search across English and Arabic documents; auto-translate key construction terms | All (GCC) | BFS-015 §9 (GCC multinational teams) |
| P1-5 | **Transmittal Tracking:** Auto-distribute documents, track receipt confirmation, escalate non-responders | Maria | BFS-015 §2 (Document Controller) |
| P1-6 | **Cross-Platform Context Bridge:** Preserve clash element GUID, 3D viewpoint, spec references, and meeting context when a Navisworks clash becomes a Procore/Aconex RFI | Priya, David, Ahmed | BFS-018 §4.1 (information loss at each handoff) |
| P1-7 | **Acknowledgment Intelligence:** Track who has viewed critical document changes, flag non-responders, go beyond "sent" to "understood" | Maria, David | BFS-018 §5.2 (receipt without understanding) |
| P1-8 | **MeMo-Based Knowledge Integration:** Train a dedicated MEMORY model (1.5B–14B parameters) on construction document reflections to internalize cross-document relationships, replacing RAG with parametric memory queried via multi-turn protocol by a frozen EXECUTIVE model | Priya, David, Sarah | Quek2026 (MeMo: Memory as a Model); BFS-018 §5.1 (cross-document relationship gap) |

### 6.3 Architectural Direction: MeMo (Memory as a Model)

Based on analysis of arXiv:2605.15156 [Quek2026], Medha's retrieval substrate should evolve from **RAG (retrieve-then-read)** to **MeMo (memory-as-model)**. This is not a user-facing feature but a foundational architecture change that improves P0-1 through P1-6.

#### Why MeMo Over RAG for Construction Documents

| Dimension | Current RAG (Chroma/pgvector) | MeMo (Proposed) | Impact on Medha |
|-----------|------------------------------|-----------------|-----------------|
| **Cross-document synthesis** | Retrieves isolated chunks; misses relationships | 5-step pipeline explicitly synthesizes multi-document QA pairs | Catches contradictions spanning specs, drawings, RFIs, clash reports |
| **Retrieval noise robustness** | HippoRAG2 drops 6.22% under noise | MeMo changes +0.55% (essentially flat) [Quek2026 Table 3] | Fewer false positives in contradiction detection |
| **Corpus-size scalability** | Retrieval cost grows with corpus | MEMORY model is fixed-size; cost independent of corpus [Quek2026 §4.4] | Scales from single project to $200M portfolio |
| **LLM vendor lock-in** | Embedding model coupled to retrieval | Plug-and-play with any EXECUTIVE (Grok, Claude, GPT-4) [Quek2026 §5.1] | Switch LLMs without retraining memory |
| **Incremental updates** | Re-index entire corpus | Model merging: 33% compute savings vs full retrain [Quek2026 Table 6] | New drawings/specs added per project milestone |

#### Implementation Path

| Phase | Duration | Deliverable | Validation Gate |
|-------|----------|-------------|-----------------|
| **PoC** | 1–2 weeks | Reflection QA dataset from 5–10 sample_docs; Qwen2.5-1.5B MEMORY model | Contradiction detection accuracy vs current RAG |
| **Dubai Corpus** | 4–6 weeks | Qwen2.5-14B MEMORY model trained on 50–100 Dubai construction docs | Benchmark on real RFI/submittal/clash workflows |
| **Production** | 8–12 weeks | MEMORY model served via vLLM; EXECUTIVE queries via multi-turn protocol; model merging for incremental updates | User acceptance: Priya's submittal review time |

**Decision gate:** Proceed to Phase 2 only if PoC demonstrates >10% improvement in cross-document contradiction recall over RAG baseline.

---

### 6.4 Nice-to-Have (P2) — Future Roadmap

| ID | Requirement | Persona | Research Basis |
|----|-------------|---------|---------------|
| P2-1 | **VR/AR Model Walkthrough:** Export contradiction highlights to immersive model review | David, PMs | BFS-015 §4 (VR walkthroughs) |
| P2-2 | **4D/5D Integration:** Link contradictions to schedule and cost impacts | David, Estimators | BFS-015 §4 (4D/5D outputs) |
| P2-3 | **Predictive RFI Forecasting:** ML model predicts which trades will generate RFIs based on historical patterns | David | BFS-017 §4 (RFI metrics) |
| P2-4 | **Vendor Product Database:** Auto-match spec requirements to manufacturer product data | Ahmed, Sarah | BFS-014 §4 (submittals) |

---

## 8. Success Metrics (Human-Centered, Not Technical)

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Time to find a document | 15–30 min | <30 sec | User timing study (n=10) |
| Submittal review time | 90 min | 20 min | Time tracking (Priya persona) |
| RFIs per $1M project value | 10–15 | 5–7 | Project retrospective analysis |
| RFI response time | 9.7 days | 3–5 days | RFI log analysis |
| Clash meeting duration | 2 hrs | 45 min | Meeting time tracking |
| Document version errors | 2–3/week | <1/month | Error log review |
| User satisfaction (NPS) | N/A | >50 | Quarterly survey |
| Dispute document prep time | 4 hrs | 30 min | PM self-reporting |
| Cross-platform information loss incidents | 5–10/week | <1/week | Manual audit of clash→RFI→email chains |
| Document acknowledgment confidence ("sent→understood") | 30% | 90% | Maria self-reporting + read-receipt analysis |
| Platform switching time per day | 2.5 hrs | 30 min | User timing study (n=10) |

---

## 9. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Users don't trust AI-detected contradictions | High | Adoption failure | Show evidence trail; human-in-the-loop validation for first 30 days |
| Construction firms won't share documents for training | Medium | Model accuracy gap | Start with public codes/regulations; partner with 1–2 VDC agencies for anonymized data |
| Document Controller fears job loss | Medium | Resistance from key gatekeeper | Position Medha as "amplifier, not replacer"; Maria still controls distribution |
| Dubai DM code updates break compliance checker | Medium | Regulatory non-compliance | Quarterly retraining pipeline; alert on code revision |
| VDC agency sees Medha as competitive threat | Medium | Partnership friction | White-label option: VDC agency brands Medha as their own tool |
| Platform fragmentation makes integration brittle | High | Data sync failures, user confusion | Start with read-only ingestion from email/PDF; evolve to API connectors |
| Users reject Medha because it adds "another platform" | High | Adoption failure | Position as intelligence layer, not replacement; integrate with existing workflows |
| ACC/Procore API changes break connectors | Medium | Feature degradation | Abstract platform interface; graceful degradation to manual upload |
| Dubai DM portal updates break compliance checker | Medium | Regulatory non-compliance | Quarterly retraining pipeline; alert on code revision |

---

## 10. References

- BFS-014: VDC Engineer Personas, Roles, and Daily Workflows
- BFS-015: Construction Decision-Makers and VDC Interface
- BFS-016: Information Exchange Formats Between VDC and Construction
- BFS-017: Quantified Pain Points and ROI of Document Intelligence
- BFS-018: Construction Collaboration Platform Landscape and Interoperability Gaps

---

*This PRD is a living document. It is updated whenever new human workflow research changes our understanding of who we serve and what they need.*

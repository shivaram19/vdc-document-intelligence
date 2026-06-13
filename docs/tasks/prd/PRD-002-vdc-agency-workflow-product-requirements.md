# PRD-002: VDC Agency Workflow Product Requirements

**Date:** 2026-05-03
**Status:** Proposed
**Scope:** Map the VDC agency project lifecycle to concrete Medha features, milestones, and success metrics.
**Related Documents:** PRD-001, `docs/research/VDC_AGENCY_WORKFLOW_001.md`, `docs/research/PERSONA_VDC_ENGINEER_001.md`, `docs/decisions/ADR-009-civil-engineering-drawing-intelligence-engine.md`

---

## 1. Product Vision

Medha becomes the **lean document-intelligence layer** that runs across every project in a VDC agency. It does not replace Revit, Navisworks, or Procore. It reads the documents that move between these tools and surfaces contradictions, gaps, and action items before they become RFIs or rework — turning document waste into early, cheap resolution.

> *“The VDC engineer still makes the call. Medha makes sure nothing gets missed, and nothing gets wasted.”*

---

## 2. Lean Construction Principles in Medha

Medha is designed around lean construction values:

| Lean Principle | How Medha Applies It |
|---|---|
| **Eliminate waste** | Catch document contradictions before they become RFIs, rework, or schedule delays. |
| **Amplify learning** | Capture every accepted/rejected finding to improve model accuracy over time. |
| **Decide as late as possible** | Provide real-time alerts so decisions happen with the latest information. |
| **Deliver as fast as possible** | Reduce document review and RFI drafting cycles from hours to minutes. |
| **Empower the team** | Keep the VDC engineer in control of final approvals and sign-offs. |
| **Build integrity in** | Every finding includes citations, confidence scores, and audit trails. |
| **See the whole** | Cross-project dashboards show agency-wide document risk and waste trends. |

---

## 3. Target Users

| Role | Primary/Secondary | What they need from Medha |
|---|---|---|
| VDC Coordinator / Engineer | Primary | Fewer missed contradictions, faster RFI drafting, cleaner coordination reports, less document waste |
| VDC Manager / Lead | Primary | Visibility across all projects, quality control, client-ready reports, standardized workflows |
| Project Engineer | Secondary | Quick answers from specs and drawings, impact analysis of addenda |
| Document Controller | Secondary | Auto-organized incoming documents, version tracking, audit trail, standardized file structure |
| Preconstruction Manager | Secondary | Risk scoring before bid, contract/spec conflict detection, lean preconstruction efficiency |
| Superintendent / Field Engineer | Secondary | Clear, visual summaries of document conflicts and resolution status |

---

## 3. Workflow-to-Feature Map

### Stage 1: Business Development & Proposal

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Estimate effort for new project | **Project document complexity scanner** — upload a drawing set, get page count, discipline breakdown, estimated contradiction risk | P2 |
| Build proposal | **Proposal helper** — auto-generate scope language and risk assumptions from document scan | P3 |

### Stage 2: Project Kickoff

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Receive first document drop | **Smart intake** — auto-classify sheets by discipline and type; detect missing sheets; extract revision dates | P1 |
| Set up project workspace | **Project workspace** — per-project document store, model links, team access, BEP template | P1 |
| Verify document completeness | **Completeness checker** — flag missing disciplines, incomplete sheet sets, unmatched detail callouts | P1 |
| Enforce agency standards | **Standardization assistant** — check file naming, folder structure, sheet numbering against agency BEP templates | P1 |

**Feature: Smart Intake**
- **User story:** As a VDC engineer, when a new drawing set arrives, I want Medha to organize it by discipline and flag missing sheets so I don’t start coordination with an incomplete set.
- **Acceptance criteria:**
  - Accepts PDF, DWG, DXF, RVT, IFC uploads
  - Classifies each sheet as architectural, structural, MEP, civil, fire protection, or other
  - Extracts sheet number, title, revision, date
  - Flags duplicate or missing sheet numbers
  - Surfaces unclassified sheets for manual review

**Feature: Standardization Assistant**
- **User story:** As a VDC manager, I want every project in my agency to follow the same file naming and folder structure standards so engineers can move between projects without relearning where things live.
- **Acceptance criteria:**
  - Validates uploaded files against agency-defined naming conventions
  - Flags sheets that violate BEP file structure
  - Suggests correct names and locations
  - Provides a project health score for standardization compliance

### Stage 3: Model Setup

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Build federated coordination model | **Model linking assistant** — extract grid lines, levels, and shared-coordinate references from drawings to support model alignment checks | P2 |
| Configure clash rules | **Clash-rule template library** — pre-built rule sets by project type (commercial, healthcare, infrastructure) | P3 |

### Stage 4: Execution — The Weekly Coordination Loop

This is Medha’s core value stage.

#### 4.1 Document monitoring

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Check for new transmittals daily | **Inbox monitor** — watch email/SharePoint/ACC/Procore for new documents and notify the team | P1 |
| Compare revised drawings | **Drawing diff** — highlight changes between revisions; categorize as major/minor/cosmetic | P1 |
| Track addenda impact | **Addenda impact report** — list sheets/specs affected by each addendum | P1 |
| Monitor document-driven risk in real time | **Live risk feed** — continuously scan for new contradictions as documents are added or updated | P1 |
| Communicate issues to non-technical stakeholders | **Executive summary view** — visual, jargon-lite summary of document risk for PMs/owners | P2 |

**Feature: Drawing Diff**
- **User story:** As a VDC engineer, when an addendum is issued, I want to see exactly what changed against the previous drawing so I can assess coordination impact in minutes, not hours.
- **Acceptance criteria:**
  - Overlay two versions of a drawing sheet
  - Highlight added, deleted, and modified geometry/annotations
  - Generate a change summary by discipline
  - Link changes to affected coordination items

**Feature: Live Risk Feed**
- **User story:** As a VDC engineer, I want Medha to alert me the moment a new document introduces a contradiction so I can address it before the next coordination meeting.
- **Acceptance criteria:**
  - Monitors connected document sources for new or revised files
  - Automatically re-runs contradiction checks on affected documents
  - Surfaces new issues in a real-time activity feed
  - Sends configurable notifications (email, Slack, in-app)
  - Distinguishes new issues from previously reviewed issues

#### 4.2 Clash preparation

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Run clash detection | **Pre-clash document check** — find drawing-spec and drawing-drawing contradictions before 3D clash detection | P1 |
| Filter false positives | **Confidence scoring** — rank issues by severity and likelihood of being real | P1 |
| Assign clashes to trades | **Issue ownership suggestions** — suggest responsible trade based on entity type and location | P2 |

**Feature: Pre-Clash Document Check**
- **User story:** As a VDC engineer, before I run Navisworks clash detection, I want Medha to scan the drawing set for contradictions so my clash meeting focuses on real coordination problems.
- **Acceptance criteria:**
  - Detects elevation mismatches between plan and section
  - Detects material conflicts between drawing note and spec
  - Detects missing detail references
  - Detects schedule-to-drawing discrepancies
  - Outputs a prioritized issue list with source citations
  - Each issue includes confidence score and severity

#### 4.3 RFI drafting

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Draft RFIs | **RFI drafter** — generate RFI text with drawing, detail, and spec citations | P1 |
| Track RFI status | **RFI tracker** — integrate with Plane/Procore/ACC to monitor open/answered/closed status | P1 |

**Feature: RFI Drafter**
- **User story:** As a VDC engineer, when Medha finds a contradiction, I want a draft RFI with the correct references so I can review and send it in minutes.
- **Acceptance criteria:**
  - Draft includes question, affected drawing(s), spec section(s), detail reference(s)
  - Proposes 1–2 possible resolutions based on similar past RFIs
  - Allows engineer to edit before sending
  - One-click push to Plane/Procore/ACC
  - Stores RFI in project log with link to originating contradiction

#### 4.4 Submittal and shop drawing review

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Review shop drawings against specs | **Submittal comparator** — compare shop drawing content to spec and design drawing | P1 |
| Check compliance | **Compliance checklist generator** — extract requirements from spec and verify presence in submittal | P2 |

**Feature: Submittal Comparator**
- **User story:** As a VDC engineer, when a steel shop drawing arrives, I want Medha to compare it to the structural drawings and specs and flag deviations.
- **Acceptance criteria:**
  - Extracts material, dimensions, connections, finishes from shop drawing
  - Compares against design drawings and relevant spec sections
  - Flags deviations with side-by-side citations
  - Outputs a review memo draft

#### 4.5 Coordination meetings

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Prepare meeting materials | **Coordination deck builder** — auto-generate slides from current issue list | P2 |
| Record decisions | **Meeting notes parser** — extract action items from meeting minutes and link to issues | P3 |
| Get sign-offs | **Sign-off tracker** — track which trades have approved which coordination deliverables | P2 |
| Report to non-technical stakeholders | **Stakeholder report** — one-page visual summary of document status, risk, and open issues | P2 |

### Stage 5: Closeout

| Agency Activity | Medha Feature | Priority |
|---|---|---|
| Prepare as-built model | **As-built discrepancy report** — list field changes and RFI resolutions not reflected in model | P2 |
| Generate final deliverables | **Closeout package generator** — compile issue log, RFIs, coordination reports | P2 |
| Lessons learned | **Project retrospective** — summarize issue types, resolution times, recurring trades | P3 |

---

## 4. Feature Priority Summary

### P1 — Must have for MVP
1. Smart document intake and classification
2. Standardization assistant for file naming and structure
3. Drawing diff / revision comparison
4. Live risk feed for real-time contradiction alerts
5. Pre-clash document contradiction detection
6. RFI drafter with citations
7. Project workspace and basic user access
8. Integration with Plane (existing) and Procore/ACC (next)

### P2 — Strongly valuable
9. Submittal comparator
10. Addenda impact report
11. Coordination deck builder
12. Stakeholder report for non-technical audiences
13. Sign-off tracker
14. As-built discrepancy report
15. Model linking assistant

### P3 — Differentiating later
16. Project complexity scanner for proposals
17. Compliance checklist generator
18. Meeting notes parser
19. Project retrospective analytics
20. Clash-rule template library
21. Quantity takeoff data extraction
22. 4D-scheduling input validation
23. Visualization exports for stakeholder communication

---

## 5. Technical Architecture

Medha’s existing pipeline supports this PRD with the following extensions:

| Existing Component | Extension Needed |
|---|---|
| `backend/docling_parser.py` | Add sheet classification, revision extraction, civil entity parsing |
| `backend/chunkers/` | Add drawing-section-aware chunking; preserve spatial context |
| `backend/extractors/` | Add civil entity extractor (grids, elevations, contours, utilities) |
| `backend/detectors/` | Add contradiction detectors for civil engineering dimensions |
| `backend/linkers/` | Add drawing-to-drawing and drawing-to-spec linkers |
| `backend/stores/` | Add civil knowledge graph and per-project document store |
| `mcp-servers/plane-mcp/` | Add issue/RFI creation tools; extend to Procore/ACC MCP servers |
| Frontend | Build project dashboard, drawing viewer, issue reviewer, RFI editor |

[CITE: ADR-009] See `docs/decisions/ADR-009-civil-engineering-drawing-intelligence-engine.md` for the full engine architecture.

---

## 6. Milestones

### Milestone 1: Document Ingestion Foundation (Weeks 1–3)
- PDF/DWG/DXF intake
- Sheet classification and metadata extraction
- Project workspace UI
- Standardization assistant for file naming and structure
- **Success:** A VDC engineer can upload a drawing set and see organized sheets in under 5 minutes; standardization health score is visible.

### Milestone 2: Drawing Diff & Real-Time Monitoring (Weeks 4–7)
- Revision comparison with visual diff
- Addenda impact report
- Notification of new document drops
- Live risk feed that re-checks documents on arrival
- **Success:** Engineer identifies all changed sheets and affected coordination items in under 10 minutes; new contradictions are surfaced within minutes of document arrival.

### Milestone 3: Pre-Clash Contradiction Detection (Weeks 8–14)
- Elevation, material, dimension, schedule contradiction detection
- Confidence scoring and severity ranking
- Source citations for every finding
- Stakeholder report for non-technical summaries
- **Success:** Medha finds ≥80% of document-level contradictions that would otherwise appear as RFIs, with <20% false-positive rate; PMs/owners can read risk summaries without VDC jargon.

### Milestone 4: RFI & Issue Workflow (Weeks 15–19)
- RFI drafter with citations
- One-click push to Plane
- Issue tracking dashboard
- **Success:** RFI drafting time reduced from 2 hours to 15 minutes per issue.

### Milestone 5: Submittal Review & Closeout (Weeks 20–26)
- Submittal comparator
- As-built discrepancy report
- Closeout package generator
- **Success:** Submittal review time reduced by 50%.

### Milestone 6: Multi-Project Agency Dashboard (Weeks 27–32)
- Cross-project risk dashboard
- Resource load visibility
- Recurring issue analytics
- Lean waste metrics (RFIs prevented, rework avoided, review hours saved)
- **Success:** VDC manager can see document risk and lean waste metrics across all active projects in one view.

---

## 7. Success Metrics

### User outcomes
| Metric | Baseline | Target |
|---|---|---|
| Time to review a new drawing set | 4–8 hours | <30 minutes |
| Time to assess addendum impact | 2–4 hours | <15 minutes |
| RFI drafting time | 1–2 hours | <15 minutes |
| Submittal review time | 45–90 minutes | <20 minutes |
| Document-level contradictions caught pre-clash | Manual, inconsistent | ≥80% auto-detected |
| False-positive rate on contradiction findings | N/A | <20% |
| Average time from document arrival to contradiction alert | Hours to days | <10 minutes |
| Standardization compliance score | Manual check | ≥90% auto-scored |

### Business outcomes
| Metric | Target |
|---|---|
| Pilot-to-paid conversion | ≥50% |
| User weekly active rate | ≥70% |
| Issues resolved via Medha-generated RFIs | ≥30% of project RFIs |
| Client-perceived coordination quality improvement | Qualitative positive feedback |
| Estimated rework cost avoided per project | Measurable reduction |
| Document waste hours saved per week per engineer | ≥6 hours |

### Product health
| Metric | Target |
|---|---|
| Document ingestion success rate | ≥95% |
| Citation accuracy | ≥90% |
| Average issue confidence score | ≥0.7 |

---

## 8. Open Questions

1. Which document management systems must Medha integrate with first — Procore, ACC, Aconex, SharePoint, or local file servers?
2. Should Medha host the drawing viewer, or embed into existing viewers (Bluebeam, ACC, BIM 360)?
3. What is the minimum training data needed for civil entity extraction to reach acceptable accuracy?
4. How should Medha handle classified or owner-sensitive drawings in a self-hosted deployment?
5. What is the liability framing in the terms of service for AI-generated contradiction findings?
6. How should Medha quantify and report “waste prevented” in a way that VDC managers can defend to clients?
7. Which lean KPIs (RFIs prevented, rework avoided, review hours saved) can be measured automatically vs. estimated?

---

## 9. References

- [CITE: PRD-001] `docs/tasks/prd/PRD-001-human-centered-product-requirements.md`
- [CITE: VDC_WORKFLOW_001] `docs/research/VDC_AGENCY_WORKFLOW_001.md`
- [CITE: PERSONA_VDC_001] `docs/research/PERSONA_VDC_ENGINEER_001.md`
- [CITE: ADR-009] `docs/decisions/ADR-009-civil-engineering-drawing-intelligence-engine.md`
- [CITE: COMPETITIVE_LANDSCAPE_2026] `docs/research/COMPETITIVE_LANDSCAPE_2026-05-03.md`
- [CITE: VDC_VIDEO_INSIGHTS_001] `docs/research/VDC_VIDEO_INSIGHTS_SYNTHESIS_001.md`

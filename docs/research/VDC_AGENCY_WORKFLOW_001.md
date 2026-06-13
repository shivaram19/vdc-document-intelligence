# VDC Agency Workflow: From First Contact to Project Closeout

**Date:** 2026-05-03
**Scope:** How a VDC/BIM coordination agency operates, and how a VDC engineer’s work flows from project start to finish.

---

## Part 1: The agency level — how work comes in

### 1. Business development
- The agency markets to **general contractors, architects, developers, and owners**.
- Common entry points:
  - GC needs BIM coordination for a specific project.
  - Architect needs a BIM consultant to meet owner requirements.
  - Owner mandates BIM / VDC on a project and the GC subcontracts it.
  - Repeat relationship — the agency becomes the GC’s go-to VDC partner.
- Proposals include:
  - Scope of BIM services (modeling, coordination, clash detection, as-builts)
  - Level of Development (LOD) targets
  - Number of coordination meetings
  - Software/platforms used
  - Pricing (lump sum, hourly, or per-square-foot)

### 2. Contracting
- The contract defines:
  - **Deliverables:** coordinated model, clash reports, shop drawing review, as-built model
  - **Standards:** BIM Execution Plan (BEP), LOD matrix, file naming, model exchange format
  - **Liability limits:** VDC agencies are rarely liable for field errors; they provide coordination services, not design approval
  - **Duration:** typically from design development through substantial completion

### 3. Resourcing
- The agency assigns:
  - **VDC Manager / Lead:** client-facing, owns deliverables and standards
  - **VDC Engineer(s):** do the modeling, coordination, clash detection, reporting
  - **Modeler(s):** sometimes separate from coordinators, especially in larger agencies
- Engineers often juggle **3–6 projects** at different stages.

---

## Part 2: Project kickoff — how a VDC engineer starts

### 1. Kickoff meeting
Attendees: VDC lead, client PM or superintendent, architect, major trade contractors (MEP, structural, fire protection), sometimes owner.

Topics covered:
- Project goals and schedule
- BIM Execution Plan review
- File exchange protocol (ACC, BIM 360, SharePoint, FTP)
- Coordination meeting cadence (weekly or biweekly)
- Model authoring responsibilities (who models what)
- Clash detection standards and tolerances
- Deliverables and sign-off criteria

### 2. Document intake
The VDC engineer receives the first document drop:
- Architectural drawings and model
- Structural drawings and model
- MEP drawings and model
- Fire protection drawings
- Civil/site drawings
- Specifications and project manual
- Addenda, RFIs, geotechnical reports
- Existing conditions / as-builts (for renovations)

The engineer immediately:
- Organizes files by discipline and revision
- Checks for completeness
- Identifies missing sheets or models
- Logs the document receipt

### 3. Model setup
- Create the **coordination model** by linking all discipline models into a federated model (Revit, Navisworks, or ACC/BIM 360).
- Set up **shared coordinates** so all models align.
- Configure **clash detection rules**:
  - Hard clashes (physical interference)
  - Clearance clashes (e.g., 6 inches around ducts)
  - Workflow clashes (e.g., access panels blocked)
- Set up **views and sheets** for coordination meetings.
- Establish **naming conventions and model hygiene rules**.

### 4. Initial clash run and report
Before the first coordination meeting, the engineer runs an initial clash detection to:
- Identify major coordination issues early
- Understand model quality
- Prioritize what needs discussion

---

## Part 3: Execution — the coordination loop

This is the bulk of the VDC engineer’s work. It runs in cycles.

### Weekly cycle

| Day | Activity |
|---|---|
| **Monday** | Review new document issuances, addenda, RFI responses. Update models if new versions received. |
| **Tuesday–Wednesday** | Run clash detection, review results, filter false positives, group related clashes, assign to trades. |
| **Thursday** | Prepare coordination meeting materials: clash report, model views, slides, action items. |
| **Friday** | Coordination meeting. Present issues. Record decisions. Update action log. |

### Core tasks during execution

1. **Clash detection**
   - Run automated clash tests in Navisworks / ACC / Solibri.
   - Review thousands of clashes and filter to actionable ones.
   - Group clashes by system or location.
   - Assign clash ownership to trades.

2. **Model coordination**
   - Verify that trade models fit within architectural and structural constraints.
   - Check ceiling plenums, shafts, equipment rooms, corridors.
   - Ensure MEP routing does not conflict with structure.

3. **RFI support**
   - Identify ambiguities, missing information, and conflicts.
   - Draft RFIs with proper references.
   - Track RFI responses and update models accordingly.

4. **Submittal and shop drawing review**
   - Compare shop drawings against design intent.
   - Flag deviations or missing information.
   - Ensure approved submittals are reflected in the model.

5. **Coordination meetings**
   - Present model walkthroughs.
   - Lead clash review sessions.
   - Document decisions and action items.
   - Get sign-offs from trades.

6. **Addenda and revision management**
   - Compare revised drawings to previous versions.
   - Assess impact on coordinated model.
   - Communicate changes to trades.

7. **Quality control**
   - Internal QA before client delivery.
   - Check model cleanliness, naming, coordinates, LOD.
   - Verify deliverables against contract scope.

---

## Part 4: Closeout — how a VDC engineer finishes

### 1. Final coordination sign-off
- Confirm all major clashes are resolved or accepted.
- Obtain sign-off from trades and client.
- Issue final coordination report.

### 2. As-built model preparation
- Update model to reflect field changes, RFIs, change orders.
- Verify accuracy against submittals and approved shop drawings.
- Clean up temporary coordination elements.

### 3. Deliverables handover
Common deliverables:
- Coordinated BIM model (Revit, Navisworks, IFC)
- Clash detection reports
- Coordination meeting minutes and action logs
- As-built / record model
- COBie data or owner-required FM data
- Training or turnover session with owner/operator

### 4. Project closeout meeting
- Review what went well and what did not.
- Document lessons learned.
- Capture reusable details, families, or standards.
- Archive project files.

### 5. Billing and administrative closeout
- Final invoices based on contract terms.
- Time and expense reconciliation.
- Update project profitability tracking.

---

## Part 5: The VDC engineer’s daily reality

### Typical day
| Time | Activity |
|---|---|
| 8:00 AM | Check email and document transmittals for new drawings or RFIs. |
| 9:00 AM | Update coordination model with new files. Run clash detection. |
| 11:00 AM | Review clashes, filter false positives, assign real issues. |
| 12:30 PM | Lunch (often at desk during crunch). |
| 1:30 PM | Draft RFIs or coordination reports. |
| 3:00 PM | Internal review with VDC lead. |
| 4:00 PM | Prepare for tomorrow’s coordination meeting or client call. |
| 5:30 PM | Log time, update action items, shut down models. |

During crunch periods (before coordination meetings, bid deadlines, or major addenda), this easily extends into evenings.

### Tools used daily
- **Revit** — model authoring and linking
- **Navisworks** — clash detection and model review
- **Bluebeam** — PDF markup and comparison
- **ACC / BIM 360 / Procore** — document management and issue tracking
- **Excel** — action logs, clash summaries, schedules
- **Outlook / Teams** — communication and transmittals

### Success metrics for the engineer
- Clash detection closure rate
- RFI response turnaround
- Coordination meeting sign-offs achieved
- Rework attributed to coordination errors
- Client satisfaction / repeat business
- Project profitability

---

## Part 6: Agency standards and knowledge management

Good VDC agencies build reusable assets:

- **BIM Execution Plan templates**
- **Clash detection rule sets**
- **Modeling standards and family libraries**
- **Coordination report templates**
- **Lessons-learned database**
- **Training materials for new hires**

This institutional knowledge is the agency’s real competitive advantage.

---

## Where Medha fits in this workflow

| Stage | Medha’s value |
|---|---|
| **Document intake** | Auto-organize and cross-reference incoming drawings and specs. |
| **Clash prep** | Surface drawing-level contradictions before running 3D clash detection. |
| **RFI drafting** | Draft RFIs from detected conflicts with citations. |
| **Addenda review** | Compare revised drawings to prior versions and flag new conflicts. |
| **Submittal review** | Compare shop drawings to specs and design drawings. |
| **Closeout** | Generate final issue log and as-built discrepancy report. |

Medha’s wedge is the **document-intelligence layer** that runs continuously across all projects in the agency, not just one model at a time.

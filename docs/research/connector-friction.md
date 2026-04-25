# Where Users Get Stuck Connecting Drawings — Research & Design Rationale

> Every design decision in the Medha connector system answers WHY. If you cannot answer WHY, the decision is intuition, not strategy.

---

## The Core Problem

Users do not want to "upload files." They want to "connect their project." 

**[CITE: Nielsen1994]** Nielsen, J. (1994). *Usability Engineering*. Morgan Kaufmann.  
- Users form mental models based on their existing tools. A Procore user thinks "connect to my Procore project," not "download PDFs from Procore, then upload them somewhere else."
- When the product's conceptual model mismatches the user's mental model, confusion and abandonment follow.

**[CITE: Krug2014]** Krug, S. (2014). *Don't Make Me Think* (3rd ed.). New Riders.  
- Every question a user must answer adds cognitive load. "Where did I save that drawing?" is a question the product should answer, not the user.
- The best interface is one the user doesn't notice. The worst interface forces the user to become a file clerk.

---

## Friction Point 1: The Blank Dashboard (84% Abandonment)

### WHAT
Users sign up, authenticate, and see an empty dashboard. No documents. No queries. No value.

### WHY
**[CITE: Hotjar2023]** Hotjar (2023). *The State of UX Analytics*.  
- 84% of users who encounter blank states without contextual help abandon within the first session.
- A blank state signals "this isn't working" or "I did something wrong" — even when the product is functioning perfectly.

**[CITE: NunesDreze2006]** Nunes, J. C., & Dreze, X. (2006). *The Endowed Progress Effect*. Journal of Consumer Research.  
- Users who believe they have already made progress toward a goal are more likely to complete it.
- Artificial progress (e.g., "2 of 5 steps completed") increases completion rates by 30-40%.

### MEDHA SOLUTION: Endowed Progress Onboarding
- Pre-load a sample project ("Demo Tower") with 5 real construction documents.
- Show "2 of 3 steps complete" before the user has done anything.
- The first query they run returns an instant, valuable result — a pre-found contradiction.
- **WHY:** This creates the "Aha Moment" (Amplitude, 2023) within 60 seconds of signup, not after 20 minutes of file hunting.

---

## Friction Point 2: The File Hunt (The Upload Paradox)

### WHAT
Users must locate drawings on their computer, select them, wait for upload, wait for processing, and only then see results.

### WHY
**[CITE: Baymard2022]** Baymard Institute (2022). *E-Commerce Checkout Usability*.  
- Each additional step in a workflow reduces completion by 5-7%.
- "Document re-upload is the single highest-friction moment in most KYC flows" (Zyphe, 2024).
- Users asked to re-upload a document are 3x more likely to abandon.

**[CITE: SaaSFactor2025]** SaaSFactor (2025). *SaaS Customer Onboarding*. https://www.saasfactor.co/blogs/saas-customer-onboarding  
- TTFV under 10 minutes correlates with 29% drop in monthly churn
- Activation rate below 20% indicates a structural onboarding problem

### MEDHA SOLUTION: Source-First Connector Design
- Ask: "Where do your drawings live?" (not "Upload files")
- Show visual cards: Procore, ACC, SharePoint, Local Files, Email
- Each card opens the right path:
  - **Local Files:** Drag & drop (working today)
  - **Procore/ACC/SharePoint:** OAuth connection (coming Q2 2026) OR one-click "request integration" that creates a support ticket with their project ID
  - **Email:** Forward-to-address that auto-ingests attachments
- **WHY:** This matches the user's mental model ("connect to my system") rather than forcing them to become a file clerk.

---

## Friction Point 3: The Format Mismatch

### WHAT
Users try to upload DWG, IFC, or RVT files. The system rejects them. They don't understand why.

### WHY
**[CITE: Autodesk2022]** Autodesk (2022). *State of Construction Report*.  
- 60% of construction drawings are still shared as PDFs, but 35% remain in native CAD formats (DWG, RVT).
- Users expect a "document intelligence" tool to handle ALL document formats.
- Generic error messages like "File type not supported" give zero actionable guidance.

**[CITE: Zyphe2024]** Zyphe (2024). *How to Reduce KYC Onboarding Drop-Off by 40%*.  
- "Generic messages like 'Verification failed' give users zero actionable information. Users hit a wall of ambiguity and bounce."

### MEDHA SOLUTION: Graceful Format Handling
- Accept PDF, DOCX, TXT, MD (working today)
- For DWG/IFC/RVT: Show specific message — "DWG detected. Export to PDF from AutoCAD, or contact us for native DWG support (Enterprise plan)."
- Provide a one-click link to instructions: "How to export PDFs from Revit"
- **WHY:** Specific guidance reduces abandonment. Generic rejection increases it. (Zyphe 2024)

---

## Friction Point 4: The Permission Labyrinth

### WHAT
A VDC engineer at a GC wants to inspect architect drawings. The architect's drawings live in the architect's ACC instance. The GC doesn't have access.

### WHY
**[CITE: ISO19650-2018]** ISO 19650-1:2018. *Organization and Digitization of Information About Buildings and Civil Engineering Works*.  
- Construction projects have complex information exchange protocols (CDE — Common Data Environment).
- Each stakeholder (architect, structural, MEP, GC) owns their own document repository.
- Cross-organizational access requires explicit permissions, NDAs, and data processing agreements.

**[CITE: Verizon2024]** Verizon (2024). *Data Breach Investigations Report*.  
- 74% of data breaches involve human element (password sharing, permission misconfiguration).
- Construction is the #3 most-targeted industry for ransomware.

### MEDHA SOLUTION: Invite-Based Connector Sharing
- Instead of requiring cross-org access, Medha generates an "inspection invite" link.
- The architect clicks the link, selects which drawings to share, and Medha ingests only those.
- The architect retains full control. No passwords shared. No permanent access granted.
- **WHY:** This mirrors the construction industry's existing information exchange protocols (ISO 19650 CDE) rather than fighting them.

---

## Friction Point 5: The "Is It Working?" Anxiety

### WHAT
User uploads 50 drawings. The UI says "Processing..." for 10 minutes. No progress bar. No status. User refreshes the page. Loses context. Abandons.

### WHY
**[CITE: GoogleSRE2017]** Beyer, B., et al. (2017). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly.  
- Systems that fail silently take 7x longer to repair than systems with observable failure modes.
- Users need to see: (a) what is happening, (b) how long it will take, (c) whether it succeeded.

**[CITE: Nielsen1994]** Nielsen, J. (1994). *Usability Engineering*.  
- Visibility of system status is one of the 10 usability heuristics. Users must always know what the system is doing.

### MEDHA SOLUTION: Real-Time Connector Health Dashboard
- Every connected source shows: Last Sync, Documents Indexed, Health Status (green/yellow/red)
- During upload: Real-time progress bar with per-file status ("Extracting text from A-101.pdf..." → "Embedding A-101.pdf..." → "Indexed")
- WebSocket events push status updates. No polling. No guessing.
- **WHY:** Visibility of system status reduces anxiety and prevents the "refresh and abandon" pattern.

---

## Friction Point 6: Version Confusion

### WHAT
User uploads "A-101.pdf" but doesn't know if it's Rev A, Rev B, or Addendum 3. The system indexes it as "A-101.pdf." Two weeks later, a contradiction is found — but it was already resolved in Rev C.

### WHY
**[CITE: CMAA2019]** Construction Management Association of America (2019). *State of the Industry Report*.  
- 35% of change orders are caused by "incomplete design coordination."
- Version control is the #1 source of document confusion in construction.
- Firms that implement systematic version tracking reduce rework by 22%.

### MEDHA SOLUTION: Version-Aware Ingestion
- Parse filenames for revision indicators: "A-101_RevB.pdf", "A-101_Add3.pdf"
- Auto-tag documents with detected version: `version: "Rev B"`, `revision_date: "2026-03-15"`
- Show version history in the document viewer: "This document has 3 versions. Currently viewing Rev B."
- Flag potential version conflicts: "A-101 Rev B and A-101 Rev C both indexed. Review for currency."
- **WHY:** Version awareness prevents false-positive contradictions and builds user trust in the system's accuracy.

---

## Friction Point 7: The Cognitive Overload of Choice

### WHAT
User sees 6 connector options, 8 document types, 3 ingestion modes, and 4 project settings. Decision paralysis sets in.

### WHY
**[CITE: Hick1952]** Hick, W. E. (1952). *On the Rate of Gain of Information*. Quarterly Journal of Experimental Psychology.  
- Hick's Law: decision time increases logarithmically with the number of choices
- When users face too many choices simultaneously, decision fatigue sets in and completion rates drop

**[CITE: IyengarLepper2000]** Iyengar, S. S., & Lepper, M. R. (2000). *When Choice is Demotivating*. Journal of Personality and Social Psychology, 79(6), 995–1006.  
- 24 jam varieties = 3% purchase rate; 6 jam varieties = 30% purchase rate
- Too many choices reduce satisfaction and completion rates

### MEDHA SOLUTION: Progressive Disclosure Connector Flow
- **Step 1:** "Where do your drawings live?" (3-4 primary options, "More sources" hidden)
- **Step 2:** "What type of documents?" (Auto-detect from filename; manual override available)
- **Step 3:** "Review and connect" (summary, not configuration)
- Advanced options hidden behind "Advanced settings" toggle
- **WHY:** Each step introduces 1-2 concepts maximum. Users build understanding incrementally rather than facing a configuration panel.

---

## Summary: The Connector Design Philosophy

| Friction Point | Research Basis | Medha Solution |
|----------------|---------------|----------------|
| Blank dashboard (84% abandon) | Hotjar 2023, Nunes & Dreze 2006 | Pre-loaded sample project + endowed progress |
| File hunt / upload paradox | Baymard 2022, Zyphe 2024 | Source-first: "Where do drawings live?" |
| Format mismatch | Autodesk 2022 | Graceful handling + specific guidance |
| Permission labyrinth | ISO 19650, Verizon 2024 | Invite-based connector sharing |
| "Is it working?" anxiety | Google SRE 2017, Nielsen 1994 | Real-time health dashboard + WebSocket progress |
| Version confusion | CMAA 2019 | Version-aware ingestion + conflict flags |
| Cognitive overload | Hick1952, IyengarLepper2000 | Progressive disclosure (3 steps max) |

*Document Version: 2026-04-24*  
*Research citations: 12 sources across UX, construction management, security, and behavioral economics.*

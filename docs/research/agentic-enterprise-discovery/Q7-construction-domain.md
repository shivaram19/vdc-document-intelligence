# Q7: What Does an Agentic Enterprise Look Like in Construction Tech?

**Research Question:** How can agentic enterprise principles be applied specifically to construction document intelligence, VDC coordination, and the stakeholders Medha serves?

---

## Why This Matters for Medha

Medha's customers are construction professionals. The agentic enterprise we build must produce value they understand and trust. Domain-specific agents are more credible than generic ones.

---

## Sub-Questions

### 7.1 Domain Workflows
1. Which construction workflows are most agentic-friendly? (RFI review, submittal check, addenda comparison, clash triage, specification compliance)
2. Which are too high-stakes for autonomous agents? (safety-critical approvals, structural design decisions)
3. Where do humans currently spend the most time on low-judgment tasks?
4. What data formats do agents need to handle? (PDF, DWG, IFC, RVT, Excel, email)

### 7.2 Stakeholder Roles
1. Who are the human stakeholders in a construction project? (VDC coordinator, BIM manager, GC PM, architect, MEP engineer, owner)
2. What decisions does each own?
3. Who would trust an agent's output?
4. Who would reject it and why?

### 7.3 Existing Domain Agents
1. What agentic or AI-assisted features already exist in construction tools? (Autodesk Construction Cloud, Procore, OpenConstructionERP)
2. What do they do well?
3. What gaps do they leave?
4. Where is the open-source opportunity?

### 7.4 Trust and Liability in Construction
1. How do construction professionals verify AI-generated findings?
2. What level of confidence is needed before acting on an agent's output?
3. How are errors handled? (rework, liability, insurance)
4. What documentation does an agent need to produce to be usable?

### 7.5 Medha's Agentic Product
1. Should Medha's product itself become an agent? (e.g., an agent that monitors project documents and alerts stakeholders)
2. Should Medha's internal agents be separate from its product agents?
3. How can Medha dogfood its own agentic stack?
4. What would a "Medha construction intelligence agent" do for customers?

---

## Current Hypotheses

1. The highest-value construction agent is a **document consistency monitor** — continuously checking specs, drawings, addenda, RFIs, and submittals for contradictions.
2. Human reviewers will trust the agent if it provides **source citations, confidence scores, and traceable reasoning**.
3. Medha should dogfood its agentic stack internally before offering agentic features to customers.
4. The agent should be **preventive** (catch issues before construction) rather than **reactive** (answer questions after).

---

## What Would Change Our Mind

- Customers say they prefer reactive Q&A over preventive monitoring
- Existing tools already cover contradiction prevention well
- Liability concerns make autonomous construction agents unadoptable

---

## Where to Look for Answers

- Construction tech forums and LinkedIn discussions
- OpenConstructionERP documentation and modules
- Research papers on AI in construction administration
- Customer discovery calls with VDC coordinators

---

## Medha-Specific Translation

Medha's first domain agent should:
- Ingest a project document set
- Extract claims and detect contradictions
- Produce a ranked report with citations
- Present findings in a readout call for human validation
- Learn from human corrections

---

**Next action:** Interview 3 VDC coordinators about whether they would trust and pay for an AI contradiction monitor.

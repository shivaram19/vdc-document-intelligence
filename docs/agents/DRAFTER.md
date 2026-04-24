# Drafter (node-g)
## Problem: "My RFIs sit unanswered for 3 weeks because they're vague."

### JTBD
When a PM needs to write an RFI, they want a professional draft that cites the exact spec clause and drawing note — so the design team can answer in one email, not three.

### What Drafter Does
1. Takes RFI number + question from user
2. Runs Finder internally to retrieve relevant chunks
3. Synthesizes a draft response using LLM (Grok-3)
4. Includes formatted headers (TO, FROM, DATE, RE)
5. Cites specific documents and clauses
6. Flags any contradictions spotted during drafting

### Research Basis
- [CITE: Papaioannou2023] RFI quality directly correlates with project schedule adherence. Vague RFIs cause 3–5x more back-and-forth.
- [CITE: Krug2014] "Don't Make Me Think" — Drafter removes the blank-page problem. Users start with a draft, not a cursor.

### Capability
```
can_draft_rfi
```

### Success Metric
- Draft generation time: < 10s
- Source citation rate: 100%
- RFI response time reduction: 60% (target)

### Example Output
```
**TO:** Design Team / Architect of Record
**FROM:** VDC Coordination Team
**DATE:** 2026-04-24
**RE:** Response to RFI-006

**QUESTION:**
What is the concrete strength for column C-12?

**RESPONSE:**
The structural specification (STRUCT_SPEC.txt, Section 3.2.1) 
requires 5,000 psi at 28 days for all columns. However, drawing 
note N-4 on STRUCT_DRAW_C12.pdf references 4,000 psi. Please 
clarify which value governs.

**REFERENCES:**
- STRUCT_SPEC.txt, Section 3.2.1
- STRUCT_DRAW_C12.pdf, Note N-4
```

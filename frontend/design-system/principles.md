# Design Principles — Medha Document Intelligence

> **Every principle answers three questions:**  
> **WHY** — What research or domain reality demands this?  
> **WHAT** — What specific design decision follows?  
> **SO WHAT** — What user outcome does this produce?

---

## 1. Risk Visibility Over Delight

### WHY
`[CITE: Ejiofor2025]` Ejiofor et al. (2025) found that **5-15% of construction budgets** are lost to rework caused by document inconsistencies. The primary job of this interface is to make risk visible — not to delight users.

`[CITE: NASA-STD-3001]` Safety-critical interfaces (NASA-STD-3001) prioritize hazard visibility over aesthetic pleasure.

### WHAT
- No gradients on buttons (distracting).
- No playful animations (bounce, elastic, wobble).
- No emoji or illustrations that dilute signal.
- Status is communicated through color + text + position — triple-redundant encoding.

### SO WHAT
A document controller scanning 50 files at 6 PM sees contradictions instantly. No cognitive decoding required.

---

## 2. Structural Integrity in Layout

### WHY
`[CITE: Tufte2001]` Tufte's Data-Ink Ratio: every pixel not communicating data is noise. Construction dashboards are information-dense. Whitespace inflation hides critical details.

`[CITE: TullisAlbert2013]` Tullis & Albert (2013): expert monitoring-task users prefer 150-200% information density over "breathing room."

### WHAT
- 4px base grid (not 8px).
- 4px/8px/12px border radius (modern scale, not playful). `[CITE: ADR-007]`
- 12px row gaps in data tables (not 24px).
- Cards use elevation-first surfaces (subtle background shifts) with borders only on hover. `[CITE: ADR-007]`

### SO WHAT
A VDC engineer views 14 documents, 1,247 chunks, and 3 contradictions on one screen without scrolling.

---

## 3. Consequence Before Action

### WHY
`[CITE: Krug2014]` Krug's 1st law: "Don't make me think." But in construction, the corollary is: **"Make me think about the right thing."** The right thing is consequence, not mechanism.

`[CITE: Ejiofor2025]` Quantifying consequences increases corrective action rate by 3x.

### WHAT
- ❌ "Contradiction detected"  
- ✅ "CONCRETE STRENGTH mismatch → ESTIMATED IMPACT: $47,000 rework"
- ❌ "Upload complete"  
- ✅ "14 docs indexed | 1,247 chunks | chain verified"
- ❌ "AI confidence: 87%"  
- ✅ "8/10 agents agree | 2 dissenting votes inspectable"

### SO WHAT
Users don't wonder "what does this mean?" They know exactly what to do next.

---

## 4. Trust Through Transparency

### WHY
`[CITE: Li2024]` Li et al. (2024): single-agent AI decisions are not trusted in safety-critical applications. Consensus + inspectability increases trust.

`[CITE: FathimaSaravanan2024]` Fathima & Saravanan (2024): cryptographic verification provides legal non-repudiation for construction disputes.

### WHAT
- Every decision shows the agents that made it.
- Every action shows a verifiable hash.
- Audit logs are append-only and inspectable.
- "How was this determined?" is always one click away.

### SO WHAT
When an auditor asks "how did you know?" the user has a defensible, traceable answer.

---

## 5. Respect for Domain Language

### WHY
`[CITE: ISO9241-210]` ISO 9241-210: human-centered design requires understanding user context. Construction professionals have a precise vocabulary.

### WHAT
- ❌ "AI-powered insights" → ✅ "Document inspection"
- ❌ "Smart recommendations" → ✅ "Contradiction detection"
- ❌ "Confidence score" → ✅ "Agent consensus"
- ❌ "Magic login" → ✅ "Knowledge-provenance authentication"
- ❌ "Upload your docs" → ✅ "Index project documents"

### SO WHAT
Users feel the tool was built by people who understand their work, not by people trying to sell them AI.

---

## 6. Safety Colors Are Not Decorative

### WHY
`[CITE: ISO3864-2016]` ISO 3864-1 defines safety orange as caution, green as safe, red as danger. These are not brand colors — they are standardized signals.

`[CITE: NASA-STD-3001]` Overuse of red causes alarm fatigue (Tanner, 2019). Red must be reserved for actual danger.

### WHAT
| State | Color | Usage |
|-------|-------|-------|
| Pass / Verified | `--safe-green` | Successful inspection, no issues |
| Warning / Caution | `--safe-yellow` | Attention required, not critical |
| Unverified / Pending | `--safe-orange` | Not yet inspected or awaiting review |
| Danger / Contradiction | `--safe-red` | Actual conflict that causes rework |
| Information | `--bp-accent` (blue) | Neutral actions, links, focus states |

### SO WHAT
A superintendent glancing at the screen from across the room knows the system state without reading text.

---

## 7. Motion Is Functional, Not Entertainment

### WHY
`[CITE: Card1983]` Card et al. (1983): human perceptual processor cycle is ~100ms. Animations under 100ms feel instant; 100-300ms feel responsive; >500ms feel sluggish.

`[CITE: Disney1981]` Disney's 12 principles apply selectively: we use "slow in, fast out" (ease-out) for reveals, but never bounce, squash, or stretch.

### WHAT
- Scan line animation: continuous, slow, represents ongoing inspection.
- State transitions: 150ms smooth (`cubic-bezier(0.4, 0, 0.2, 1)`).
- Panel reveals: 250ms expo-out (`cubic-bezier(0.16, 1, 0.3, 1)`). `[CITE: ADR-008]`
- No parallax, no particle effects, no scroll-triggered reveals.

### SO WHAT
The interface feels responsive and alive without being distracting. Users know when something is happening, but motion never competes with data for attention.

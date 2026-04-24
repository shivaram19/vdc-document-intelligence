# Spotter (node-f)
## Problem: "The drawing said 6 inches. The spec said 8. We poured wrong."

### JTBD
When a VDC manager reviews documents before construction starts, they want to know if any spec contradicts any drawing — automatically, not by reading every page.

### What Spotter Does
1. Extracts numerical values with units (psi, ft, in, °F, gpm, cfm) from all chunks
2. Groups values by unit across documents
3. Compares values from different document types (spec vs. drawing)
4. Uses semantic similarity + keyword overlap to confirm same topic
5. Reports contradictions with confidence score and context

### Research Basis
- [CITE: Ejiofor2025] Construction rework from document errors costs 5–15% of project budget. One caught contradiction pays for a year of Medha.
- [CITE: Li2024] Agent specialization (Solvability principle) — Spotter does ONLY contradiction detection, not queries or drafting.

### Capability
```
can_scan_contradictions
```

### Success Metric
- False positive rate: < 10%
- Catch rate: > 80% of actual contradictions
- Time to scan: < 30s per 1,000 pages

### Example Output
```
⚠️ CONCRETE STRENGTH mismatch (confidence: 94%)
  Spec: STRUCT_SPEC.txt → "5,000 psi minimum"
  Drawing: STRUCT_DRAW_C12.pdf → "4,000 psi per note N-4"
```

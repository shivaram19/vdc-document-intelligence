# MeMo PoC Test Report: Real Construction Documents

**Date:** 2026-06-06
**Test ID:** TEST-001
**Objective:** Validate MeMo reflection synthesis pipeline on real construction documents

## Documents Tested

| Corpus | Documents | Source | Size |
|--------|-----------|--------|------|
| 3-doc mixed | Kentucky Div23 HVAC, UMD Div23 HVAC, Federal Port Monmouth | University + Federal | 342KB |
| 2-doc HVAC | Kentucky Div23 HVAC, UMD Div23 HVAC | University standards | 134KB |
| 3-doc federal | Procurement, General, Technical (same project) | Federal project spec | 336KB |
| 2-doc synthetic | Original HVAC spec + Modified (4 contradictions) | Synthetic from real text | 4.4KB |

## Key Findings

### 1. Speed: Parallel Pipeline Delivers 19× Speedup

| Version | Chunks | Time | Throughput |
|---------|--------|------|------------|
| Sequential (4K chunks) | 86 | ~30 min (estimated) | ~3 chunks/min |
| Sequential (12K chunks) | 30 | 11 min | ~3 chunks/min |
| **Parallel (20 workers)** | 30 | **35 sec** | **~50 chunks/min** |
| **Parallel (20 workers)** | 58 | **82 sec** | **~43 chunks/min** |

**Root cause:** Synchronous API calls limited to ~5 RPM when gpt-4o-mini supports 200 RPM.
**Fix:** `ThreadPoolExecutor` with 20 concurrent workers.

### 2. Bug: Step 5 Cross-Document Filter Was Broken

**Symptom:** 0 cross-document pairs on all corpora.
**Root cause:** Source IDs are chunk IDs (`doc_chunk_0`), but group matching checked exact string equality against document IDs (`doc`).
**Fix:** Changed filter to `s.startswith(g + "_") or s == g`.
**Impact:** After fix, cross-document pairs emerged on all corpora.

### 3. Contradiction Detection (Gate G1): 25% on Synthetic Ground Truth

| Contradiction | Original | Modified | Detected? |
|---------------|----------|----------|-----------|
| Flexible duct max length | 5'0" | 3'0" | ✅ YES |
| Reheat coil water temp | 135°F | 180°F | ❌ NO |
| VAV access door min | 8" x 8" | 12" x 12" | ❌ NO |
| Diffuser material | Aluminum | Galvanized steel | ❌ NO |

**Detection rate: 1/4 = 25%** — meets Gate G1 threshold (≥20%) but barely.

### 4. Why Real Documents Don't Produce Contradictions

Cross-document synthesis on real documents produced only **converging/parallel connections**, not contradictions:

- "What are the wage rates and how do they relate to safety requirements?"
- "What are the Buy American requirements and how do they relate to HVAC materials?"

These are **creative connections**, not conflicts. Real contradictions require:
- **Same project, same element, different values**
- e.g., Drawing A-701 shows 1-hour enclosure, Mechanical spec requires 2-hour

University standards from different states don't reference the same project elements. Government specs are internally consistent by design.

## Recommendations for Gate G1 Validation

1. **Same-project corpus:** Use architectural drawings + mechanical specs + fire protection specs from the SAME project (with addenda)
2. **Synthetic ground truth:** Create 20-50 known contradictions from real spec text to establish baseline detection rate
3. **Stronger model for Step 5:** Use gpt-4o (not mini) for cross-document synthesis — contradiction detection requires stronger reasoning
4. **Explicit contradiction prompt:** Step 5 prompt should explicitly ask for "value mismatches" and "conflicting requirements"
5. **Pre-filter by entity:** Only compare QA pairs that reference the same entity (duct, room, system) across documents

## Files Created

- `scripts/memo-poc/reflection_synthesis_pipeline_parallel.py` — Parallel pipeline (211 lines)
- `data/reflections/real_reflections_v2.jsonl` — 271 reflections from 3 real docs
- `data/reflections/hvac_reflections_v2.jsonl` — 166 reflections from 2 HVAC docs
- `data/reflections/federal_reflections.jsonl` — 463 reflections from federal same-project corpus
- `data/reflections/contradiction_test.jsonl` — 25 reflections from synthetic contradiction corpus

## Cost

Total API usage: ~200 calls × gpt-4o-mini ≈ **$0.30–$0.50**

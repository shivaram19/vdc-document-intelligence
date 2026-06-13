# Contradiction Detection Engine — Sensor-Guided Implementation Plan

**Status:** Completed — all phases passed sensor gates
**Basis:** ADR-014, `CONTRADICTION_DETECTION_001.md`, `MEDHA_VALUES_AND_CUSTOMER_ALIGNMENT_001.md`, sensor framework

---

## Goal

Build `backend/analysis/contradictions/` layer by layer. Each phase passes computational and inferential sensors before the next phase starts, so drift is caught early and customer values stay intact.

**Sensor families used:** testing, linting/file-hygiene, dependency/layering, inferential/values-alignment [CITE: codebase-sensors; CITE: Böckeler2024].

---

## Phase-by-phase plan

| # | Layer | Files | Acceptance criteria | Sensor gate | Rollback if |
|---|---|---|---|---|---|
| 0 | Foundation | `models.py`, `extractors/_pipeline.py` | `Claim.metadata["source_type"]` set; no `Contradiction` schema change | Claim tests pass; pre-commit passes; file-size ≤ limits | Claim tests fail after metadata change |
| 1 | Normalization | `_normalize.py` | Unit parse/comparison works for numbers, ranges, units, standards | Unit tests pass; lint (function ≤50 lines, complexity ≤10); docstrings present | Tolerance logic produces obvious false conflicts |
| 2 | Comparators | `_comparators.py` | Numeric, material, standard, missing-attribute conflicts detected; tolerance respected | Comparator tests pass; positive + negative cases; dependency rules respected; split if >200 lines | Identical values flagged as conflict; >50% false positives on missing-attribute |
| 3 | Grouping | `_grouper.py` | Claims grouped by `(entity, attribute)`; entity groups for missing-attribute | Grouping tests pass; empty input handled; no claim in two groups unless copied | A claim appears in multiple groups unexpectedly |
| 4 | Resolution | `_resolver.py` | Configurable document hierarchy suppresses resolved conflicts | Resolver tests pass; inferential review matches AIA/contract norms | Majority of conflicts dropped without logged reason |
| 5 | Scoring | `_scoring.py` | Confidence ∈ [0,1]; severity maps attribute criticality | Scoring tests pass; range checks; values justification documented | Critical attribute scored low or trivial attribute scored critical |
| 6 | Sensors | `_sensors.py` | Phase sensors reject invalid input and collapse duplicates; drift ratio > 0.25 raises | Sensor tests pass; drift-injection test passes; reuses `analysis.sensors` types | Sensor silently swallows invalid input |
| 7 | Orchestrator | `_detector.py`, package `__init__.py` | `detect(claims)` returns contradictions + reports; status starts `open`; no auto-RFI | Full backend suite passes; coupling sensor; human-in-loop review | `detect()` mutates external state or hides reports |
| 8 | Public API | `analysis/__init__.py` | `from analysis import ContradictionDetector` works | Dependency sensor; lint; no forbidden cross-package imports | Public API surface ambiguous/circular |
| 9 | Tests | `tests/test_contradictions.py` | Covers all comparators, resolver, scorer, sensors, end-to-end; coverage ≥80% | Testing sensor (assertions, not just execution); coverage threshold; pre-commit | Tests only cover happy paths |
| 10 | Values review | docs/ADR-014 | C1–C8 values checklist passes; full sensor suite passes | Full `pytest backend/`; pre-commit; file-size; inferential checklist | Any checklist item fails |

---

## Customer-value links

| Value | Phases that protect it |
|---|---|
| Human-in-the-loop (V1) | 7, 10 |
| Citations / defensibility (V2) | 0, 7, 10 |
| Accuracy over speed (V3) | 1, 2, 4, 6, 9, 10 |
| Waste reduction (V4) | 4, 5, 7 |
| Trust through determinism (V5) | 2, 6, 9, 10 |
| Integration not replacement (V6) | 0, 8 |
| Outcome over AI (V7) | 5, 10 |
| Region/standard awareness (V8) | 4, 10 |

---

## Sequencing rule

No phase starts until the previous phase passes its sensor gates. Approve to begin Phase 0.

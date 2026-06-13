# Contradiction Detection Engine — Values Review Sign-Off

**Status:** Signed off after Phase 10 review
**Scope:** `backend/analysis/contradictions/`
**Basis:** `MEDHA_VALUES_AND_CUSTOMER_ALIGNMENT_001.md`, ADR-014

---

## Checklist C1–C8

| Check | Question | Evidence in this implementation | Result |
|---|---|---|---|
| C1 | Does this keep the VDC engineer in control of the final decision? | `ContradictionDetector` returns `Contradiction` objects with `status="open"`; no RFI or external action is taken automatically. [CITE: V1] | ✅ Yes |
| C2 | Does every output include citations back to source documents? | Each `Contradiction` carries `claim_ids`; each `Claim` carries `chunk_id`, `document_id`, `source_type`, and `source_text` in `metadata`. [CITE: V2] | ✅ Yes |
| C3 | Is the default path deterministic and auditable? | Default path uses deterministic comparators (`NumericComparator`, `MaterialComparator`, `StandardComparator`, `MissingAttributeComparator`) with explicit tolerances and unit conversions. [CITE: V3, V5] | ✅ Yes |
| C4 | Does this reduce document waste, rework, or RFI overhead? | Document hierarchy resolution suppresses conflicts resolved by higher-authority documents before they reach the engineer, reducing noise. [CITE: V4] | ✅ Yes |
| C5 | Does it integrate with existing tools rather than replace them? | The engine exposes a pure function `detect(claims)` with no side effects; callers in other modules decide how to push results to Procore/ACC/etc. [CITE: V6] | ✅ Yes |
| C6 | Is the customer benefit framed as an outcome, not "AI"? | Output is `Contradiction` findings with confidence/severity; LLM is reserved only as a future inferential sensor, not the primary detector. [CITE: V7, Papaioannou2023] | ✅ Yes |
| C7 | Can it be configured for different regional standards? | `DocumentHierarchyResolver` accepts a custom `priority` map; `NUMERIC_TOLERANCE`, `UNIT_BASE`, and `ATTRIBUTE_CRITICALITY` are externalized constants. [CITE: V8] | ✅ Yes |
| C8 | Is there a sensor or guardrail to catch drift before it erodes trust? | `ContradictionDetectionSensor` validates candidates, collapses duplicates, and reports drift; `ClaimExtractionSensor` already guards upstream extraction. [CITE: V3, V5, ADR-013] | ✅ Yes |

---

## Sensor gate results

- Full backend test suite: **129 passed**.
- Contradiction engine coverage: **98%**.
- Pre-commit hooks: passed.
- No auto-RFI path exists in the detector.

---

## References

- [CITE: V1–V8] `docs/research/MEDHA_VALUES_AND_CUSTOMER_ALIGNMENT_001.md`
- [CITE: ADR-014] `docs/decisions/ADR-014-contradiction-detection-engine.md`
- [CITE: ADR-013] `docs/decisions/ADR-013-claim-extraction-sensors.md`
- [CITE: Papaioannou2023] LLM hallucination in construction documents.

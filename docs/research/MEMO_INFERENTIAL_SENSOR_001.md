# MeMo Inferential Sensor — Research Note

**Source:** arXiv:2605.15156 — *MeMo: Memory as a Model* (Quek et al., 2026)
**Scope:** `backend/analysis/contradictions/_inferential.py`, `_memo_client.py`
**Status:** Implemented as a default-off inferential sensor

---

## What MeMo proposes

MeMo separates knowledge from reasoning:

- A smaller **MEMORY model** is trained on synthesized *reflections* derived from a corpus.
- A frozen **EXECUTIVE model** queries MEMORY through a structured multi-turn protocol (grounding → entity identification → answer synthesis).
- Advantages: cross-document reasoning, robustness to retrieval noise, no catastrophic forgetting, plug-and-play with proprietary LLMs, constant retrieval cost.

---

## How we adapted it

We do not train a MEMORY model yet. Instead, we treat any available LLM (local or API) as the memory oracle and use the same three-stage idea in a simplified form:

1. **Grounding prompts** ask the oracle to restate what entity and requirement each claim describes.
2. **Synthesis prompt** asks whether the two requirements contradict, with a structured JSON response.
3. The sensor only reviews pairs that deterministic comparators skipped: same attribute, different surface entity, both with source text.

This preserves our deterministic-first architecture (ADR-014) and keeps the human-in-the-loop gate: the sensor only produces `open` contradictions with citations, never an RFI.

---

## Files

- `_memo_client.py` — `MemoryModelClient` protocol plus API, local, and fake clients.
- `_inferential.py` — `MeMoInferentialSensor`: pair selection, prompt construction, JSON parsing.
- `_detector.py` — `ContradictionDetector` gained `use_inferential` and `inferential_sensor` options.

---

## Configuration

```python
from analysis import ContradictionDetector
from analysis.contradictions._inferential import MeMoInferentialSensor
from analysis.contradictions._memo_client import APIMemoryModelClient

detector = ContradictionDetector(
    use_inferential=True,
    inferential_sensor=MeMoInferentialSensor(client=APIMemoryModelClient()),
)
```

Default is `use_inferential=False`, so existing behavior is unchanged.

---

## Future path to full MeMo

When we want to train a dedicated MEMORY model for construction documents, the reflection dataset builder will:

1. Extract explicit facts from chunks (direct extraction).
2. Infer implicit relationships (indirect extraction).
3. Consolidate overlapping facts.
4. Verify self-containment.
5. Surface entities and generate cross-document synthesis QA pairs.

That dataset can fine-tune a small model (e.g., Qwen2.5-1.5B) which then replaces `APIMemoryModelClient` without changing the sensor logic.

---

## Citations

- [CITE: Quek2026] MeMo: Memory as a Model, arXiv:2605.15156.
- [CITE: ADR-014] `docs/decisions/ADR-014-contradiction-detection-engine.md`

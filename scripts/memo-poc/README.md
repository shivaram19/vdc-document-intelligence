# MeMo PoC: Reflection Synthesis Pipeline

This directory contains a proof-of-concept implementation of the **5-step reflection synthesis pipeline** from arXiv:2605.15156 (MeMo: Memory as a Model), adapted for construction document intelligence.

## What This Does

The pipeline transforms raw construction documents (specs, drawings, RFIs, etc.) into a **reflection QA dataset** — compositional question-answer pairs that capture cross-document relationships, contradictions, and entity references.

This dataset can then be used to fine-tune a small MEMORY model (e.g., Qwen2.5-1.5B) that internalizes construction knowledge parametrically, replacing or augmenting traditional RAG retrieval.

## The 5 Steps

| Step | Name | What It Does | Output |
|------|------|-------------|--------|
| 1 | **Fact Extraction** | Extracts direct (explicit) and indirect (inferred) facts from each document chunk | Raw QA pairs |
| 2 | **Consolidation** | Merges redundant/overlapping QA pairs into richer multi-fact pairs | Consolidated QA pairs |
| 3 | **Verification & Rewriting** | Checks self-containment; fixes pronouns and implicit references; discards ambiguous pairs | Verified QA pairs |
| 4 | **Entity Surfacing** | Generates QA pairs where the question encodes entity attributes and the answer reveals its identity | Entity-surfacing pairs |
| 5 | **Cross-Document Synthesis** | Identifies converging clues and parallel properties across multiple documents | Cross-document QA pairs |

## Quick Start

### Prerequisites

```bash
pip install openai
```

Set your API key:
```bash
export OPENAI_API_KEY=sk-...
# OR for xAI/Grok:
export XAI_API_KEY=xai-...
```

### Run on Sample Documents

```bash
cd scripts/memo-poc
python reflection_synthesis_pipeline.py \
    --docs-dir ../../sample_docs \
    --output ../../data/reflections/reflections.jsonl \
    --model gpt-4o-mini
```

### Run on Real Construction Documents

```bash
python reflection_synthesis_pipeline.py \
    --docs-dir ../../real_construction_docs \
    --output ../../data/reflections/real_reflections.jsonl \
    --model gpt-4o
```

### Output

- `data/reflections/reflections.jsonl` — One JSON object per line:
  ```json
  {"question": "...", "answer": "...", "sources": ["ARCH_DRAWING_NOTES"], "step": 5}
  ```
- `data/reflections/reflections.summary.json` — Pipeline statistics

## Cost Estimate

With `gpt-4o-mini` on the 5 sample documents (~150 lines total):
- ~15–20 API calls
- Estimated cost: **$0.50–$1.50**

With `gpt-4o` on 50–100 real construction documents:
- ~150–300 API calls
- Estimated cost: **$15–$40**

## Next Steps After Running

1. **Inspect the reflection QA pairs** — Look for cross-document contradictions and relationships
2. **Fine-tune a MEMORY model** — Use the JSONL with Qwen2.5-1.5B-Instruct:
   ```bash
   # Using Hugging Face TRL or Unsloth
   python train_memory_model.py -- reflections.jsonl --model Qwen/Qwen2.5-1.5B-Instruct
   ```
3. **Evaluate vs RAG baseline** — Compare contradiction detection accuracy on held-out test queries

## Paper Reference

- [Quek2026] Quek, R.W.H., Lee, S., Leong, A.W.L., Verma, A., et al. (2026). *MeMo: Memory as a Model.* arXiv:2605.15156v2 [cs.CL]. https://arxiv.org/abs/2605.15156

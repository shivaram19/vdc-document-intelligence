#!/usr/bin/env python3
"""
MeMo PoC: Async Reflection Synthesis Pipeline

Maximum-speed version using OpenAI's async client with asyncio.gather().
Eliminates ThreadPoolExecutor overhead; handles 50+ concurrent requests cleanly.

Usage:
    export OPENAI_API_KEY=sk-...
    python reflection_synthesis_pipeline_async.py \
        --docs-dir ../../real_construction_docs \
        --output ../../data/reflections/reflections.jsonl \
        --model gpt-4o-mini \
        --workers 50

Speed comparison (58 chunks):
    Sequential:  ~30 min
    ThreadPool:  ~82 sec  (20 workers)
    Async:       ~45 sec  (50 workers)  ← this file
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS_PER_STEP = 4096
TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# Async LLM Client
# ---------------------------------------------------------------------------

class AsyncLLMClient:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("No API key found. Set OPENAI_API_KEY or XAI_API_KEY.")

        if model.startswith("grok") or "x.ai" in os.environ.get("OPENAI_BASE_URL", ""):
            from openai import AsyncOpenAI
            base = os.environ.get("OPENAI_BASE_URL", "https://api.x.ai/v1")
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=base)
        else:
            from openai import AsyncOpenAI
            base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=base)

    async def generate(self, system: str, user: str, temperature: float = TEMPERATURE) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=MAX_TOKENS_PER_STEP,
        )
        return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Document Loader
# ---------------------------------------------------------------------------

def load_documents(docs_dir: Path) -> List[Dict[str, str]]:
    docs = []
    for ext in ("*.txt", "*.md"):
        for path in sorted(docs_dir.glob(ext)):
            docs.append({
                "id": path.stem,
                "path": str(path),
                "content": path.read_text(encoding="utf-8"),
            })
    print(f"[Loader] Loaded {len(docs)} documents from {docs_dir}")
    return docs


def chunk_document(doc: Dict[str, str], max_chars: int = 12000) -> List[Dict[str, str]]:
    content = doc["content"]
    if len(content) <= max_chars:
        return [doc]
    chunks = []
    for i, start in enumerate(range(0, len(content), max_chars)):
        chunks.append({
            "id": f"{doc['id']}_chunk_{i}",
            "path": doc["path"],
            "content": content[start:start + max_chars],
            "parent_id": doc["id"],
        })
    return chunks


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

STEP1_SYSTEM = """You are a construction document analyst. Extract facts from a document chunk.

Produce TWO types of QA pairs:
A. DIRECT extraction — explicitly stated facts (materials, dimensions, codes, drawings)
B. INDIRECT extraction — inferred information (violations, affected documents, contradictions)

Format as JSON array:
[{"question": "...", "answer": "...", "type": "direct"}, ...]

Rules:
- Each QA pair must be fully answerable from the chunk alone.
- Output ONLY valid JSON. No markdown fences, no explanations.
"""

STEP2_SYSTEM = """You are a construction knowledge engineer. Consolidate QA pairs.

Given QA pairs from the SAME document chunk, merge pairs that share common context (same entity, material, or relationship) into richer QA pairs requiring more reasoning.

Format as JSON array:
[{"question": "...", "answer": "...", "merged_from": [0, 1]}]

Rules:
- merged_from contains 0-based indices of original pairs.
- If no merge partner, include unchanged with merged_from pointing to itself.
- Output ONLY valid JSON. No markdown fences.
"""

STEP3_SYSTEM = """You are a QA editor for construction documents.

Check self-containment: Can question AND answer be fully understood without the source document? Are there unresolved pronouns or implicit references?

If NOT self-contained, REWRITE using source context. If still ambiguous, mark DISCARD.

Format as JSON array:
[{"question": "...", "answer": "...", "status": "kept|rewritten|discarded", "reason": "..."}]

Rules:
- status="kept" if already self-contained.
- status="rewritten" if fixed.
- status="discarded" if ambiguous even after rewriting.
- Output ONLY valid JSON. No markdown fences.
"""

STEP4_SYSTEM = """You are a construction entity extraction specialist.

For each named entity (materials, systems, equipment, codes, drawings), generate ENTITY-SURFACING QA pairs:
- QUESTION encodes the entity's attributes and relationships.
- ANSWER reveals the entity's identity.

Format as JSON array:
[{"question": "...", "answer": "...", "entity_type": "material|system|drawing|code|..."}]

Rules:
- Vary complexity: single-fact, multi-fact, cross-entity.
- Include numeric attributes (dimensions, ratings) in questions.
- Output ONLY valid JSON. No markdown fences.
"""

STEP5_SYSTEM = """You are a cross-document synthesis engineer for construction projects.

Given QA pairs from MULTIPLE related documents, identify CROSS-DOCUMENT CONNECTIONS:

A. CONVERGING CLUES: Multiple documents provide complementary facts about the SAME entity.
B. PARALLEL PROPERTIES: Different entities share a common attribute, enabling comparison.
C. CONTRADICTIONS: Documents specify DIFFERENT values for the SAME entity or requirement.
   — This is the HIGHEST priority. Flag any value mismatch, conflicting code versions,
     or incompatible material requirements.

Format as JSON array:
[{
  "question": "...",
  "answer": "...",
  "connection_type": "converging|parallel|contradiction",
  "sources": ["doc1", "doc2"]
}]

Rules:
- Each QA MUST require information from at least 2 documents.
- PRIORITIZE CONTRADICTIONS — these are highest value for construction coordination.
- Output ONLY valid JSON. No markdown fences.
"""


# ---------------------------------------------------------------------------
# Step Functions (async)
# ---------------------------------------------------------------------------

async def step1_fact_extraction(client: AsyncLLMClient, chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    user_prompt = f"""Document: {chunk['id']}\n\n---\n{chunk['content']}\n---\n\nExtract direct and indirect facts as JSON array."""
    raw = await client.generate(STEP1_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        qa_pairs = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Step1] JSON parse error for {chunk['id']}: {e}")
        return []
    for qa in qa_pairs:
        qa["sources"] = [chunk["id"]]
        qa["step"] = 1
    return qa_pairs


async def step2_consolidation(client: AsyncLLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    if len(qa_pairs) <= 1:
        return qa_pairs
    user_prompt = f"""Consolidate these {len(qa_pairs)} QA pairs from document chunk '{chunk_id}':\n\n{json.dumps(qa_pairs, indent=2)}\n\nProduce consolidated JSON array."""
    raw = await client.generate(STEP2_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        merged = json.loads(raw)
    except json.JSONDecodeError:
        return qa_pairs
    for m in merged:
        m.setdefault("sources", [chunk_id])
        m["step"] = 2
    return merged


async def step3_verification(client: AsyncLLMClient, qa_pairs: List[Dict[str, Any]], chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    user_prompt = f"""Verify these QA pairs from document chunk '{chunk['id']}':\n\nQA PAIRS:\n{json.dumps(qa_pairs, indent=2)}\n\nSOURCE CHUNK (for rewriting):\n---\n{chunk['content'][:3000]}\n---\n\nProduce verified JSON array."""
    raw = await client.generate(STEP3_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        verified = json.loads(raw)
    except json.JSONDecodeError:
        return qa_pairs
    result = []
    for v in verified:
        if v.get("status") == "discarded":
            continue
        result.append({
            "question": v["question"],
            "answer": v["answer"],
            "sources": [chunk["id"]],
            "step": 3,
            "verification_reason": v.get("reason", ""),
        })
    return result


async def step4_entity_surfacing(client: AsyncLLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    if not qa_pairs:
        return []
    user_prompt = f"""Generate entity-surfacing QA pairs from these verified QA pairs from chunk '{chunk_id}':\n\n{json.dumps(qa_pairs, indent=2)}\n\nProduce entity-surfacing JSON array."""
    raw = await client.generate(STEP4_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        surfaced = json.loads(raw)
    except json.JSONDecodeError:
        return []
    for s in surfaced:
        s.setdefault("sources", [chunk_id])
        s["step"] = 4
    return surfaced


async def step5_cross_document_synthesis(client: AsyncLLMClient, all_verified: List[Dict[str, Any]], doc_groups: List[List[str]]) -> List[Dict[str, Any]]:
    synthesized = []
    for group in doc_groups:
        group_qa = [qa for qa in all_verified if any(any(s.startswith(g + "_") or s == g for g in group) for s in qa.get("sources", []))]
        if len(group_qa) < 4:
            continue
        user_prompt = f"""Synthesize cross-document QA pairs from these verified facts across documents: {group}\n\nVERIFIED FACTS:\n{json.dumps(group_qa[:40], indent=2)}\n\nProduce cross-document synthesis JSON array."""
        raw = await client.generate(STEP5_SYSTEM, user_prompt, temperature=0.4)
        raw = raw.replace("```json", "").replace("```", "").strip()
        try:
            cross = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  [Step5] JSON parse error for group {group}: {e}")
            continue
        for c in cross:
            c["step"] = 5
            synthesized.append(c)
    return synthesized


# ---------------------------------------------------------------------------
# Grouping Strategy
# ---------------------------------------------------------------------------

def create_document_groups(docs: List[Dict[str, str]]) -> List[List[str]]:
    ids = [d["id"] for d in docs]
    if len(ids) <= 10:
        return [ids]
    groups = []
    discipline_keywords = {
        "fire": ["FIRE", "SPRINKLER", "NFPA"],
        "mech": ["MECH", "HVAC", "VAV", "ASHRAE"],
        "struct": ["STRUCT", "CONCRETE", "REBAR", "ACI"],
        "arch": ["ARCH", "DRAWING", "FINISH"],
    }
    for disc, keywords in discipline_keywords.items():
        group = [d["id"] for d in docs if any(kw in d["id"].upper() or kw in d["content"].upper()[:500] for kw in keywords)]
        if len(group) >= 2:
            groups.append(group)
    groups.append(ids)
    return groups


# ---------------------------------------------------------------------------
# Async Execution Helpers
# ---------------------------------------------------------------------------

async def _run_async(client: AsyncLLMClient, items: List[Any], fn, max_concurrent: int, desc: str) -> List[Any]:
    """Execute fn(client, item) for all items with semaphore-limited concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)
    completed = 0
    errors = 0
    results = []
    start = time.time()

    async def _wrapped(item):
        nonlocal completed, errors
        async with semaphore:
            try:
                result = await fn(client, item)
                return result
            except Exception as e:
                errors += 1
                print(f"  [{desc}] Error: {e}")
                return None

    tasks = [asyncio.create_task(_wrapped(item)) for item in items]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        completed += 1
        if result is not None:
            results.append(result)
        if completed % 5 == 0 or completed == len(items):
            elapsed = time.time() - start
            rate = completed / elapsed if elapsed > 0 else 0
            print(f"  [{desc}] {completed}/{len(items)} done ({rate:.1f} items/sec, {errors} errors)")

    return results


async def _run_async_with_args(client: AsyncLLMClient, items: List[tuple], fn, max_concurrent: int, desc: str) -> List[Any]:
    """Execute fn(client, *args) for all items with semaphore-limited concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)
    completed = 0
    errors = 0
    results = []
    start = time.time()

    async def _wrapped(item):
        nonlocal completed, errors
        async with semaphore:
            try:
                result = await fn(client, *item)
                return result
            except Exception as e:
                errors += 1
                print(f"  [{desc}] Error: {e}")
                return None

    tasks = [asyncio.create_task(_wrapped(item)) for item in items]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        completed += 1
        if result is not None:
            results.append(result)
        if completed % 5 == 0 or completed == len(items):
            elapsed = time.time() - start
            rate = completed / elapsed if elapsed > 0 else 0
            print(f"  [{desc}] {completed}/{len(items)} done ({rate:.1f} items/sec, {errors} errors)")

    return results


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

async def run_pipeline(args: argparse.Namespace):
    client = AsyncLLMClient(args.model)
    docs_dir = Path(args.docs_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workers = args.workers

    docs = load_documents(docs_dir)
    if not docs:
        print("[Error] No documents found.")
        sys.exit(1)

    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc, max_chars=args.chunk_size)
        all_chunks.extend(chunks)
    print(f"[Chunker] Produced {len(all_chunks)} chunks (chunk_size={args.chunk_size})")

    # Step 1: Fact Extraction
    print(f"\n[Step 1/5] Fact Extraction (workers={workers})...")
    t0 = time.time()
    step1_results_nested = await _run_async(client, all_chunks, step1_fact_extraction, workers, "Step1")
    step1_results = [qa for sublist in step1_results_nested for qa in sublist]
    print(f"[Step 1] Total: {len(step1_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 2: Consolidation
    print(f"\n[Step 2/5] Consolidation (workers={workers})...")
    chunk_to_qa = {}
    for qa in step1_results:
        cid = qa["sources"][0]
        chunk_to_qa.setdefault(cid, []).append(qa)

    t0 = time.time()
    step2_items = [(qa_pairs, cid) for cid, qa_pairs in chunk_to_qa.items()]
    step2_results_nested = await _run_async_with_args(client, step2_items, step2_consolidation, workers, "Step2")
    step2_results = [qa for sublist in step2_results_nested for qa in sublist]
    print(f"[Step 2] Total: {len(step2_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 3: Verification
    print(f"\n[Step 3/5] Verification (workers={workers})...")
    chunk_map = {c["id"]: c for c in all_chunks}
    step3_items = []
    for cid, qa_pairs in chunk_to_qa.items():
        consolidated = [qa for qa in step2_results if qa["sources"][0] == cid]
        if consolidated and cid in chunk_map:
            step3_items.append((consolidated, chunk_map[cid]))

    t0 = time.time()
    step3_results_nested = await _run_async_with_args(client, step3_items, step3_verification, workers, "Step3")
    step3_results = [qa for sublist in step3_results_nested for qa in sublist]
    print(f"[Step 3] Total: {len(step3_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 4: Entity Surfacing
    print(f"\n[Step 4/5] Entity Surfacing (workers={workers})...")
    step4_items = []
    for cid, qa_pairs in chunk_to_qa.items():
        verified = [qa for qa in step3_results if qa["sources"][0] == cid]
        if verified:
            step4_items.append((verified, cid))

    t0 = time.time()
    step4_results_nested = await _run_async_with_args(client, step4_items, step4_entity_surfacing, workers, "Step4")
    step4_results = [qa for sublist in step4_results_nested for qa in sublist]
    print(f"[Step 4] Total: {len(step4_results)} entity-surfacing pairs in {time.time()-t0:.1f}s")

    # Step 5: Cross-Document Synthesis
    print(f"\n[Step 5/5] Cross-Document Synthesis...")
    doc_groups = create_document_groups(docs)
    all_verified = step3_results + step4_results
    t0 = time.time()
    cross_qa = await step5_cross_document_synthesis(client, all_verified, doc_groups)
    print(f"[Step 5] Total: {len(cross_qa)} cross-document pairs in {time.time()-t0:.1f}s")

    # Compile
    final_dataset = step3_results + step4_results + cross_qa
    print(f"\n[Final] {len(final_dataset)} reflection QA pairs total")

    with open(output_path, "w", encoding="utf-8") as f:
        for qa in final_dataset:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")
    print(f"[Output] Written to {output_path}")

    summary = {
        "total_reflections": len(final_dataset),
        "by_step": {
            "1_fact_extraction": len(step1_results),
            "2_consolidation": len(step2_results),
            "3_verification": len(step3_results),
            "4_entity_surfacing": len(step4_results),
            "5_cross_document": len(cross_qa),
        },
        "documents": [d["id"] for d in docs],
        "chunks": len(all_chunks),
        "model": args.model,
        "workers": workers,
        "chunk_size": args.chunk_size,
        "pipeline": "async",
    }
    summary_path = output_path.with_suffix(".summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[Summary] Written to {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="MeMo Async Reflection Synthesis Pipeline")
    parser.add_argument("--docs-dir", default="sample_docs", help="Directory containing .txt/.md documents")
    parser.add_argument("--output", default="data/reflections/reflections.jsonl", help="Output JSONL path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    parser.add_argument("--workers", type=int, default=50, help="Max concurrent API calls (semaphore)")
    parser.add_argument("--chunk-size", type=int, default=12000, help="Max chars per chunk")
    args = parser.parse_args()
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()

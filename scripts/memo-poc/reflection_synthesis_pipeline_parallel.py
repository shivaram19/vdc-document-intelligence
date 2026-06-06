#!/usr/bin/env python3
"""
MeMo PoC: Parallel Reflection Synthesis Pipeline

Speed-optimized version using ThreadPoolExecutor for concurrent API calls.
With gpt-4o-mini's 200 RPM limit, 20 workers achieves ~10-20× speedup.

Usage:
    export OPENAI_API_KEY=sk-...
    python reflection_synthesis_pipeline_parallel.py \
        --docs-dir ../../real_construction_docs \
        --output ../../data/reflections/real_reflections.jsonl \
        --model gpt-4o-mini \
        --workers 20
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS_PER_STEP = 4096
TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# LLM Client (OpenAI-compatible, thread-safe)
# ---------------------------------------------------------------------------

class LLMClient:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("No API key found. Set OPENAI_API_KEY or XAI_API_KEY.")

        if model.startswith("grok") or "x.ai" in os.environ.get("OPENAI_BASE_URL", ""):
            from openai import OpenAI
            base = os.environ.get("OPENAI_BASE_URL", "https://api.x.ai/v1")
            self.client = OpenAI(api_key=self.api_key, base_url=base)
        else:
            from openai import OpenAI
            base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.client = OpenAI(api_key=self.api_key, base_url=base)

    def generate(self, system: str, user: str, temperature: float = TEMPERATURE) -> str:
        response = self.client.chat.completions.create(
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
# Prompts (identical to original)
# ---------------------------------------------------------------------------

STEP1_SYSTEM = """You are a construction document analyst. Your job is to extract facts from a document chunk.

For the given chunk, produce TWO types of QA pairs:

A. DIRECT extraction — explicitly stated facts:
   - Material specifications
   - Dimensions, tolerances, clearances
   - Code references (NFPA, ASHRAE, ACI, Dubai DM, etc.)
   - Drawing references and revision numbers
   - Installation requirements

B. INDIRECT extraction — inferred or synthesized information:
   - What would happen if this requirement is violated?
   - What other documents would this chunk affect?
   - What contradictions might exist with typical construction practice?

Format your output as a JSON array of objects:
[
  {"question": "...", "answer": "...", "type": "direct"},
  {"question": "...", "answer": "...", "type": "indirect"}
]

Rules:
- Each QA pair must be fully answerable from the chunk alone.
- Questions should be diverse: factual recall, numerical, comparative, conditional.
- Include document ID and section references in answers where possible.
- Output ONLY valid JSON. No markdown fences, no explanations.
"""

STEP2_SYSTEM = """You are a construction knowledge engineer. Your job is to consolidate QA pairs.

Given a set of QA pairs from the SAME document chunk, identify pairs that share a common underlying context (same entity, time period, material, or relationship type) and MERGE them into richer QA pairs that require integrating multiple facts.

Format your output as a JSON array:
[
  {"question": "...", "answer": "...", "merged_from": [0, 1]}
]

Rules:
- merged_from contains the 0-based indices of the original QA pairs that were merged.
- If a QA pair has no merge partner, include it unchanged with merged_from pointing to itself.
- The merged question should require MORE reasoning than any single original question.
- Output ONLY valid JSON. No markdown fences.
"""

STEP3_SYSTEM = """You are a quality assurance editor for construction document QA pairs.

For each QA pair, check if it is SELF-CONTAINED:
- Can the question be fully understood without the source document?
- Can the answer be fully understood without the source document?
- Are there unresolved pronouns ("it", "they", "the above")?
- Are there implicit references ("as noted earlier", "per the table")?

If a QA pair is NOT self-contained, REWRITE it using the source chunk as context.
If it cannot be made self-contained, mark it for DISCARD.

Format your output as a JSON array:
[
  {"question": "...", "answer": "...", "status": "kept|rewritten|discarded", "reason": "..."}
]

Rules:
- status="kept" if already self-contained.
- status="rewritten" if fixed.
- status="discarded" if ambiguous even after rewriting.
- Output ONLY valid JSON. No markdown fences.
"""

STEP4_SYSTEM = """You are a construction entity extraction specialist.

For each named entity in the given QA pairs (materials, systems, rooms, levels, equipment, codes, drawing sheets, etc.), generate ENTITY-SURFACING QA pairs:

- The QUESTION encodes the entity's attributes and relationships (including connections to other entities).
- The ANSWER reveals the entity's identity.

This trains the model to identify entities from partial descriptions, mitigating the "reversal curse."

Format your output as a JSON array:
[
  {"question": "...", "answer": "...", "entity_type": "material|system|drawing|code|..."}
]

Rules:
- Generate at varying complexity: single-fact, multi-fact, and cross-entity.
- Include numeric attributes (dimensions, ratings, quantities) in questions.
- Output ONLY valid JSON. No markdown fences.
"""

STEP5_SYSTEM = """You are a cross-document synthesis engineer for construction projects.

You are given QA pairs from MULTIPLE related documents (e.g., architectural drawings, mechanical specs, fire protection specs, structural specs, RFI logs). Your job is to identify CROSS-DOCUMENT CONNECTIONS and synthesize new QA pairs that require integrating evidence from multiple documents.

Two types of connections to find:

A. CONVERGING CLUES: Multiple documents provide complementary facts about the SAME entity or system.
   Example: Mechanical spec says "VAV units shall be 2-hour fire-rated." Fire protection spec says "VAV units in shafts require 2-hour enclosure." Architectural drawing A-701 shows 1-hour enclosure.

B. PARALLEL PROPERTIES: Different entities across documents share a common attribute, enabling comparison.
   Example: Both the HVAC ductwork (Mechanical spec) and the electrical conduit (Structural spec) require 2-hour fire-rated enclosures in shafts.

Format your output as a JSON array:
[
  {
    "question": "...",
    "answer": "...",
    "connection_type": "converging|parallel",
    "sources": ["doc1", "doc2"]
  }
]

Rules:
- Each synthesized QA MUST require information from at least 2 documents to answer correctly.
- Prioritize CONTRADICTIONS and CROSS-REFERENCES — these are highest value for construction coordination.
- Include document IDs and section references in answers.
- Output ONLY valid JSON. No markdown fences.
"""


# ---------------------------------------------------------------------------
# Step Functions
# ---------------------------------------------------------------------------

def step1_fact_extraction(client: LLMClient, chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    user_prompt = f"""Document: {chunk['id']}\n\n---\n{chunk['content']}\n---\n\nExtract direct and indirect facts as JSON array."""
    raw = client.generate(STEP1_SYSTEM, user_prompt)
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


def step2_consolidation(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    if len(qa_pairs) <= 1:
        return qa_pairs
    user_prompt = f"""Consolidate these {len(qa_pairs)} QA pairs from document chunk '{chunk_id}':\n\n{json.dumps(qa_pairs, indent=2)}\n\nProduce consolidated JSON array."""
    raw = client.generate(STEP2_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        merged = json.loads(raw)
    except json.JSONDecodeError:
        return qa_pairs
    for m in merged:
        m.setdefault("sources", [chunk_id])
        m["step"] = 2
    return merged


def step3_verification(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    user_prompt = f"""Verify these QA pairs from document chunk '{chunk['id']}':\n\nQA PAIRS:\n{json.dumps(qa_pairs, indent=2)}\n\nSOURCE CHUNK (for rewriting):\n---\n{chunk['content'][:3000]}\n---\n\nProduce verified JSON array."""
    raw = client.generate(STEP3_SYSTEM, user_prompt)
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


def step4_entity_surfacing(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    if not qa_pairs:
        return []
    user_prompt = f"""Generate entity-surfacing QA pairs from these verified QA pairs from chunk '{chunk_id}':\n\n{json.dumps(qa_pairs, indent=2)}\n\nProduce entity-surfacing JSON array."""
    raw = client.generate(STEP4_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        surfaced = json.loads(raw)
    except json.JSONDecodeError:
        return []
    for s in surfaced:
        s.setdefault("sources", [chunk_id])
        s["step"] = 4
    return surfaced


def step5_cross_document_synthesis(client: LLMClient, all_verified: List[Dict[str, Any]], doc_groups: List[List[str]]) -> List[Dict[str, Any]]:
    synthesized = []
    for group in doc_groups:
        # Match sources where parent doc ID is in the group (sources are chunk IDs like doc_chunk_0)
        group_qa = [qa for qa in all_verified if any(any(s.startswith(g + "_") or s == g for g in group) for s in qa.get("sources", []))]
        if len(group_qa) < 4:
            print(f"  [Step5] Skipping group {group}: only {len(group_qa)} QA pairs (need >= 4)")
            continue
        user_prompt = f"""Synthesize cross-document QA pairs from these verified facts across documents: {group}\n\nVERIFIED FACTS:\n{json.dumps(group_qa[:30], indent=2)}\n\nProduce cross-document synthesis JSON array."""
        raw = client.generate(STEP5_SYSTEM, user_prompt, temperature=0.4)
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
# Parallel Execution Helpers
# ---------------------------------------------------------------------------

def _run_parallel(client: LLMClient, items: List[Any], fn, max_workers: int, desc: str) -> List[Any]:
    """Execute fn(item) for all items using ThreadPoolExecutor."""
    results = []
    completed = 0
    errors = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(fn, client, item): item for item in items}
        for future in as_completed(future_to_item):
            completed += 1
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                errors += 1
                print(f"  [{desc}] Error: {e}")
            if completed % 5 == 0 or completed == len(items):
                elapsed = time.time() - start
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"  [{desc}] {completed}/{len(items)} done ({rate:.1f} items/sec, {errors} errors)")
    return results


def _run_parallel_with_args(client: LLMClient, items: List[tuple], fn, max_workers: int, desc: str) -> List[Any]:
    """Execute fn(client, *args) for all items using ThreadPoolExecutor."""
    results = []
    completed = 0
    errors = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(fn, client, *item): item for item in items}
        for future in as_completed(future_to_item):
            completed += 1
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                errors += 1
                print(f"  [{desc}] Error: {e}")
            if completed % 5 == 0 or completed == len(items):
                elapsed = time.time() - start
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"  [{desc}] {completed}/{len(items)} done ({rate:.1f} items/sec, {errors} errors)")
    return results


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(args: argparse.Namespace):
    client = LLMClient(args.model)
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

    # Step 1: Fact Extraction (parallel per chunk)
    print(f"\n[Step 1/5] Fact Extraction (workers={workers})...")
    t0 = time.time()
    step1_results_nested = _run_parallel(client, all_chunks, step1_fact_extraction, workers, "Step1")
    step1_results = [qa for sublist in step1_results_nested for qa in sublist]
    print(f"[Step 1] Total: {len(step1_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 2: Consolidation (parallel per chunk)
    print(f"\n[Step 2/5] Consolidation (workers={workers})...")
    chunk_to_qa = {}
    for qa in step1_results:
        cid = qa["sources"][0]
        chunk_to_qa.setdefault(cid, []).append(qa)

    t0 = time.time()
    step2_items = [(qa_pairs, cid) for cid, qa_pairs in chunk_to_qa.items()]
    step2_results_nested = _run_parallel_with_args(client, step2_items, step2_consolidation, workers, "Step2")
    step2_results = [qa for sublist in step2_results_nested for qa in sublist]
    print(f"[Step 2] Total: {len(step2_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 3: Verification (parallel per chunk)
    print(f"\n[Step 3/5] Verification (workers={workers})...")
    chunk_map = {c["id"]: c for c in all_chunks}
    step3_items = []
    for cid, qa_pairs in chunk_to_qa.items():
        consolidated = [qa for qa in step2_results if qa["sources"][0] == cid]
        if consolidated and cid in chunk_map:
            step3_items.append((consolidated, chunk_map[cid]))

    t0 = time.time()
    step3_results_nested = _run_parallel_with_args(client, step3_items, step3_verification, workers, "Step3")
    step3_results = [qa for sublist in step3_results_nested for qa in sublist]
    print(f"[Step 3] Total: {len(step3_results)} QA pairs in {time.time()-t0:.1f}s")

    # Step 4: Entity Surfacing (parallel per chunk)
    print(f"\n[Step 4/5] Entity Surfacing (workers={workers})...")
    step4_items = []
    for cid, qa_pairs in chunk_to_qa.items():
        verified = [qa for qa in step3_results if qa["sources"][0] == cid]
        if verified:
            step4_items.append((verified, cid))

    t0 = time.time()
    step4_results_nested = _run_parallel_with_args(client, step4_items, step4_entity_surfacing, workers, "Step4")
    step4_results = [qa for sublist in step4_results_nested for qa in sublist]
    print(f"[Step 4] Total: {len(step4_results)} entity-surfacing pairs in {time.time()-t0:.1f}s")

    # Step 5: Cross-Document Synthesis (single call, not parallel)
    print(f"\n[Step 5/5] Cross-Document Synthesis...")
    doc_groups = create_document_groups(docs)
    all_verified = step3_results + step4_results
    t0 = time.time()
    cross_qa = step5_cross_document_synthesis(client, all_verified, doc_groups)
    print(f"[Step 5] Total: {len(cross_qa)} cross-document pairs in {time.time()-t0:.1f}s")

    # Compile final dataset
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
    }
    summary_path = output_path.with_suffix(".summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[Summary] Written to {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="MeMo Parallel Reflection Synthesis Pipeline")
    parser.add_argument("--docs-dir", default="sample_docs", help="Directory containing .txt/.md documents")
    parser.add_argument("--output", default="data/reflections/reflections.jsonl", help="Output JSONL path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    parser.add_argument("--workers", type=int, default=20, help="Number of concurrent API workers")
    parser.add_argument("--chunk-size", type=int, default=12000, help="Max chars per chunk")
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()

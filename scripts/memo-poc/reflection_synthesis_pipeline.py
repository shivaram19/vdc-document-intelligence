#!/usr/bin/env python3
"""
MeMo PoC: 5-Step Reflection Synthesis Pipeline for Construction Documents

Implements the data synthesis pipeline from arXiv:2605.15156 (Quek et al., 2026)
adapted for construction document intelligence.

Usage:
    export OPENAI_API_KEY=sk-...
    python reflection_synthesis_pipeline.py \
        --docs-dir ../../sample_docs \
        --output ../../data/reflections/reflections.jsonl \
        --model gpt-4o-mini

Steps:
    1. Fact Extraction (direct + indirect)
    2. Consolidation (merge redundant facts)
    3. Verification & Rewriting (self-containment check)
    4. Entity Surfacing (identify entities from attributes)
    5. Cross-Document Synthesis (multi-document relationships)

Output:
    JSONL file where each line is a reflection QA pair:
    {"question": "...", "answer": "...", "sources": [...], "step": 5}
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS_PER_STEP = 4096
TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# LLM Client (OpenAI-compatible)
# ---------------------------------------------------------------------------

class LLMClient:
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("No API key found. Set OPENAI_API_KEY or XAI_API_KEY.")

        # Auto-detect provider from model name or base URL
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
    """Load all .txt and .md files from docs_dir."""
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


def chunk_document(doc: Dict[str, str], max_chars: int = 4000) -> List[Dict[str, str]]:
    """Split a document into chunks. For PoC, simple character split."""
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
# Step 1: Fact Extraction
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


def step1_fact_extraction(client: LLMClient, chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extract direct and indirect facts from a chunk."""
    user_prompt = f"""Document: {chunk['id']}

---
{chunk['content']}
---

Extract direct and indirect facts as JSON array."""

    raw = client.generate(STEP1_SYSTEM, user_prompt)
    # Clean up potential markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        qa_pairs = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Step1] JSON parse error for {chunk['id']}: {e}")
        print(f"  [Step1] Raw output: {raw[:500]}")
        return []

    for qa in qa_pairs:
        qa["sources"] = [chunk["id"]]
        qa["step"] = 1
    return qa_pairs


# ---------------------------------------------------------------------------
# Step 2: Consolidation
# ---------------------------------------------------------------------------

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


def step2_consolidation(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    """Merge redundant/overlapping QA pairs."""
    if len(qa_pairs) <= 1:
        return qa_pairs

    user_prompt = f"""Consolidate these {len(qa_pairs)} QA pairs from document chunk '{chunk_id}':

{json.dumps(qa_pairs, indent=2)}

Produce consolidated JSON array."""

    raw = client.generate(STEP2_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        merged = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Step2] JSON parse error for {chunk_id}: {e}")
        return qa_pairs  # Fallback: return originals

    for m in merged:
        m.setdefault("sources", [chunk_id])
        m["step"] = 2
    return merged


# ---------------------------------------------------------------------------
# Step 3: Verification & Rewriting
# ---------------------------------------------------------------------------

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


def step3_verification(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk: Dict[str, str]) -> List[Dict[str, Any]]:
    """Verify self-containment and rewrite if needed."""
    user_prompt = f"""Verify these QA pairs from document chunk '{chunk['id']}':

QA PAIRS:
{json.dumps(qa_pairs, indent=2)}

SOURCE CHUNK (for rewriting):
---
{chunk['content'][:3000]}
---

Produce verified JSON array."""

    raw = client.generate(STEP3_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        verified = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Step3] JSON parse error for {chunk['id']}: {e}")
        return qa_pairs  # Fallback

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


# ---------------------------------------------------------------------------
# Step 4: Entity Surfacing
# ---------------------------------------------------------------------------

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


def step4_entity_surfacing(client: LLMClient, qa_pairs: List[Dict[str, Any]], chunk_id: str) -> List[Dict[str, Any]]:
    """Generate entity-surfacing QA pairs."""
    if not qa_pairs:
        return []

    user_prompt = f"""Generate entity-surfacing QA pairs from these verified QA pairs from chunk '{chunk_id}':

{json.dumps(qa_pairs, indent=2)}

Produce entity-surfacing JSON array."""

    raw = client.generate(STEP4_SYSTEM, user_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        surfaced = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Step4] JSON parse error for {chunk_id}: {e}")
        return []

    for s in surfaced:
        s.setdefault("sources", [chunk_id])
        s["step"] = 4
    return surfaced


# ---------------------------------------------------------------------------
# Step 5: Cross-Document Synthesis
# ---------------------------------------------------------------------------

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


def step5_cross_document_synthesis(client: LLMClient, all_verified: List[Dict[str, Any]], doc_groups: List[List[str]]) -> List[Dict[str, Any]]:
    """Generate cross-document QA pairs from document groups."""
    synthesized = []

    for group in doc_groups:
        group_qa = [qa for qa in all_verified if any(s in group for s in qa.get("sources", []))]
        if len(group_qa) < 4:
            continue

        user_prompt = f"""Synthesize cross-document QA pairs from these verified facts across documents: {group}

VERIFIED FACTS:
{json.dumps(group_qa[:30], indent=2)}  // limited to 30 for token budget

Produce cross-document synthesis JSON array."""

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
    """Create topical groups for cross-document synthesis.

    For PoC with sample_docs, we group by project discipline.
    In production, this would use embeddings or human-provided labels.
    """
    ids = [d["id"] for d in docs]
    # PoC: create one group with all documents (small corpus)
    if len(ids) <= 10:
        return [ids]

    # For larger corpora: group by discipline keywords
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

    # Add a full-corpus group for project-wide relationships
    groups.append(ids)
    return groups


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(args: argparse.Namespace):
    client = LLMClient(args.model)
    docs_dir = Path(args.docs_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load and chunk documents
    docs = load_documents(docs_dir)
    if not docs:
        print("[Error] No documents found.")
        sys.exit(1)

    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"[Chunker] Produced {len(all_chunks)} chunks")

    # -----------------------------------------------------------------------
    # Step 1: Fact Extraction (per chunk)
    # -----------------------------------------------------------------------
    print("\n[Step 1/5] Fact Extraction...")
    step1_results = []
    for i, chunk in enumerate(all_chunks):
        print(f"  Chunk {i+1}/{len(all_chunks)}: {chunk['id']}")
        qa_pairs = step1_fact_extraction(client, chunk)
        print(f"    → {len(qa_pairs)} QA pairs extracted")
        step1_results.extend(qa_pairs)
    print(f"[Step 1] Total: {len(step1_results)} QA pairs")

    # -----------------------------------------------------------------------
    # Step 2: Consolidation (per chunk)
    # -----------------------------------------------------------------------
    print("\n[Step 2/5] Consolidation...")
    step2_results = []
    chunk_to_qa = {}
    for qa in step1_results:
        cid = qa["sources"][0]
        chunk_to_qa.setdefault(cid, []).append(qa)

    for cid, qa_pairs in chunk_to_qa.items():
        print(f"  Consolidating {len(qa_pairs)} pairs from {cid}")
        merged = step2_consolidation(client, qa_pairs, cid)
        print(f"    → {len(merged)} after consolidation")
        step2_results.extend(merged)
    print(f"[Step 2] Total: {len(step2_results)} QA pairs")

    # -----------------------------------------------------------------------
    # Step 3: Verification & Rewriting (per chunk)
    # -----------------------------------------------------------------------
    print("\n[Step 3/5] Verification & Rewriting...")
    step3_results = []
    chunk_map = {c["id"]: c for c in all_chunks}
    for cid, qa_pairs in chunk_to_qa.items():
        # Use the consolidated pairs for this chunk
        consolidated = [qa for qa in step2_results if qa["sources"][0] == cid]
        if not consolidated:
            continue
        print(f"  Verifying {len(consolidated)} pairs from {cid}")
        verified = step3_verification(client, consolidated, chunk_map[cid])
        print(f"    → {len(verified)} kept after verification")
        step3_results.extend(verified)
    print(f"[Step 3] Total: {len(step3_results)} QA pairs")

    # -----------------------------------------------------------------------
    # Step 4: Entity Surfacing (per chunk)
    # -----------------------------------------------------------------------
    print("\n[Step 4/5] Entity Surfacing...")
    step4_results = []
    for cid, qa_pairs in chunk_to_qa.items():
        verified = [qa for qa in step3_results if qa["sources"][0] == cid]
        if not verified:
            continue
        print(f"  Surfacing entities from {len(verified)} pairs in {cid}")
        surfaced = step4_entity_surfacing(client, verified, cid)
        print(f"    → {len(surfaced)} entity-surfacing pairs")
        step4_results.extend(surfaced)
    print(f"[Step 4] Total: {len(step4_results)} entity-surfacing pairs")

    # -----------------------------------------------------------------------
    # Step 5: Cross-Document Synthesis (per group)
    # -----------------------------------------------------------------------
    print("\n[Step 5/5] Cross-Document Synthesis...")
    doc_groups = create_document_groups(docs)
    all_verified = step3_results + step4_results
    cross_qa = step5_cross_document_synthesis(client, all_verified, doc_groups)
    print(f"[Step 5] Total: {len(cross_qa)} cross-document pairs")

    # -----------------------------------------------------------------------
    # Compile final dataset
    # -----------------------------------------------------------------------
    final_dataset = step3_results + step4_results + cross_qa
    print(f"\n[Final] {len(final_dataset)} reflection QA pairs total")

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        for qa in final_dataset:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")
    print(f"[Output] Written to {output_path}")

    # Write summary
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
    }
    summary_path = output_path.with_suffix(".summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[Summary] Written to {summary_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MeMo Reflection Synthesis Pipeline for Construction Documents")
    parser.add_argument("--docs-dir", default="sample_docs", help="Directory containing .txt/.md documents")
    parser.add_argument("--output", default="data/reflections/reflections.jsonl", help="Output JSONL path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name")
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()

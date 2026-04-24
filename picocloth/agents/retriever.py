#!/usr/bin/env python3
"""
VDC Retriever Agent (node-a / node-e hybrid)
Answers user queries using RAG over project embeddings.
No HTTP. Reads/writes shared memory directly.

Usage:
    python retriever.py --project default --query "What is the concrete strength?"
"""

import argparse
import json
from datetime import datetime
from vdc_core import (
    load_embeddings, encode, cosine_similarity, detect_contradictions,
    synthesize_answer, append_event, audit, llm_generate,
)
import numpy as np

MIN_CONFIDENCE = 0.35
TOP_K = 5


def answer_query(project_id: str, query: str, top_k: int = TOP_K) -> dict:
    embeddings, chunks = load_embeddings(project_id)
    if embeddings is None or len(chunks) == 0:
        return {
            "answer": "No documents have been uploaded for this project yet.",
            "sources": [],
            "contradictions": [],
        }

    query_emb = encode([query])
    sims = cosine_similarity(query_emb, embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]

    sources = []
    context_parts = []
    for idx in top_indices:
        chunk = chunks[idx]
        score = float(sims[idx])
        sources.append({
            "score": round(score, 4),
            "text": chunk["text"][:500],
            "doc_name": chunk["doc_name"],
            "doc_type": chunk["doc_type"],
        })
        context_parts.append(f"[From {chunk['doc_name']} ({chunk['doc_type']}): {chunk['text'][:800]}]")

    top_score = round(float(sims[top_indices[0]]), 4) if len(top_indices) > 0 else 0

    if top_score < MIN_CONFIDENCE:
        answer = (
            "I could not find a clear answer with sufficient confidence. "
            "Please upload additional relevant documents or rephrase your question.\n\n"
            "**DISCLAIMER:** AI-generated. Review by qualified engineer required."
        )
        contradictions = []
    else:
        contradictions = detect_contradictions([chunks[idx] for idx in top_indices], query)
        if contradictions:
            cx_note = "\n\n[SYSTEM NOTE: Potential contradictions detected:]\n"
            for c in contradictions:
                cx_note += f"- {c['unit'].upper()}: values {', '.join(c['values'])} across {', '.join(c['documents'][:3])}\n"
            cx_note += "Please address relevant conflicts.\n"
            context_parts.append(cx_note)
        answer = synthesize_answer(query, "\n\n".join(context_parts), sources)

    result = {
        "project_id": project_id,
        "query": query,
        "answer": answer,
        "sources": sources,
        "top_score": top_score,
        "contradictions": contradictions,
        "contradictions_detected": len(contradictions),
        "timestamp": datetime.now().isoformat(),
    }

    append_event("queries", result)
    audit("query", project_id, query)
    return result


def main():
    parser = argparse.ArgumentParser(description="VDC Retriever Agent")
    parser.add_argument("--project", default="default", help="Project ID")
    parser.add_argument("--query", required=True, help="User query")
    parser.add_argument("--top-k", type=int, default=TOP_K, help="Number of chunks to retrieve")
    args = parser.parse_args()

    result = answer_query(args.project, args.query, top_k=args.top_k)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

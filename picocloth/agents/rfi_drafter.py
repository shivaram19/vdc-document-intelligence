#!/usr/bin/env python3
"""
VDC RFI Drafter Agent (node-g)
Drafts professional RFI responses by retrieving relevant chunks and synthesizing answers.
No HTTP. Reads/writes shared memory directly.

Usage:
    python rfi_drafter.py --project default --question "What is the column spacing?" --number RFI-006
"""

import argparse
import json
from datetime import datetime
from vdc_core import (
    load_embeddings, encode, cosine_similarity, detect_contradictions,
    generate_rfi_draft, append_event, audit,
)
import numpy as np


def draft_rfi(project_id: str, question: str, rfi_number: str = "RFI-XXX") -> dict:
    embeddings, chunks = load_embeddings(project_id)
    if embeddings is None or len(chunks) == 0:
        return {
            "rfi_number": rfi_number,
            "question": question,
            "draft": "No project documents available. Please upload drawings and specs first.",
            "sources": [],
            "contradictions": [],
        }

    query_emb = encode([question])
    sims = cosine_similarity(query_emb, embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:5]

    sources = []
    context_parts = []
    for idx in top_indices:
        chunk = chunks[idx]
        sources.append({
            "score": round(float(sims[idx]), 4),
            "doc_name": chunk["doc_name"],
            "doc_type": chunk["doc_type"],
            "text": chunk["text"][:400],
        })
        context_parts.append(chunk["text"][:600])

    context = "\n".join(context_parts)
    contradictions = detect_contradictions([chunks[idx] for idx in top_indices], question)
    if contradictions:
        cx_note = "\n\n[SYSTEM NOTE: Potential contradictions detected:]\n"
        for c in contradictions:
            cx_note += f"- {c['unit'].upper()}: values {', '.join(c['values'])} across {', '.join(c['documents'][:3])}\n"
        cx_note += "Please address relevant conflicts.\n"
        context += cx_note

    draft = generate_rfi_draft(rfi_number, question, context, sources)

    result = {
        "project_id": project_id,
        "rfi_number": rfi_number,
        "question": question,
        "draft": draft,
        "sources": sources,
        "contradictions": contradictions,
        "contradictions_detected": len(contradictions),
        "timestamp": datetime.now().isoformat(),
    }

    append_event("rfis", result)
    audit("draft_rfi", project_id, question)
    return result


def main():
    parser = argparse.ArgumentParser(description="VDC RFI Drafter Agent")
    parser.add_argument("--project", default="default", help="Project ID")
    parser.add_argument("--question", required=True, help="RFI question")
    parser.add_argument("--number", default="RFI-XXX", help="RFI number")
    args = parser.parse_args()

    result = draft_rfi(args.project, args.question, args.number)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

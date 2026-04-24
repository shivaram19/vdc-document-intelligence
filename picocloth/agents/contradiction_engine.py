#!/usr/bin/env python3
"""
VDC Contradiction Engine Agent (node-f)
Scans project embeddings for numeric contradictions between specs and drawings.
No HTTP. Reads/writes shared memory directly.

Usage:
    python contradiction_engine.py --project default
    python contradiction_engine.py --project default --query "column spacing"
"""

import argparse
import json
import re
from datetime import datetime
from vdc_core import (
    load_embeddings, encode, cosine_similarity, detect_contradictions,
    append_event, audit,
)
import numpy as np


def scan_contradictions(project_id: str, query: str = "") -> dict:
    embeddings, chunks = load_embeddings(project_id)
    if embeddings is None or len(chunks) < 2:
        return {
            "contradictions": [],
            "message": "Need at least 2 documents to detect contradictions.",
        }

    # If query provided, do query-aware detection on all chunks
    if query:
        contradictions = detect_contradictions(chunks, query)
        return {
            "project_id": project_id,
            "query": query,
            "contradictions": contradictions,
            "count": len(contradictions),
            "timestamp": datetime.now().isoformat(),
        }

    # Otherwise do spec-vs-drawing scan
    drawing_chunks = [(i, c) for i, c in enumerate(chunks) if c["doc_type"] in ("drawing", "plan")]
    spec_chunks = [(i, c) for i, c in enumerate(chunks) if c["doc_type"] in ("spec", "specification")]

    if not drawing_chunks or not spec_chunks:
        return {
            "contradictions": [],
            "message": "Need both drawings and specs for contradiction detection.",
        }

    spec_indices = [i for i, _ in spec_chunks]
    draw_indices = [i for i, _ in drawing_chunks]
    spec_embs = embeddings[spec_indices]
    draw_embs = embeddings[draw_indices]
    sim_matrix = cosine_similarity(spec_embs, draw_embs)

    contradictions = []
    for si, spec_idx in enumerate(spec_indices):
        best_di = int(np.argmax(sim_matrix[si]))
        best_score = float(sim_matrix[si][best_di])
        draw_idx = draw_indices[best_di]
        if best_score > 0.5:
            spec_text = chunks[spec_idx]["text"]
            draw_text = chunks[draw_idx]["text"]
            spec_dims = set(re.findall(r'\b(\d+(?:\.\d+)?)\s*(?:ft|inches|in)\b', spec_text))
            draw_dims = set(re.findall(r'\b(\d+(?:\.\d+)?)\s*(?:ft|inches|in)\b', draw_text))
            if spec_dims and draw_dims and spec_dims != draw_dims:
                contradictions.append({
                    "severity": "medium",
                    "confidence": round(best_score, 3),
                    "spec_doc": chunks[spec_idx]["doc_name"],
                    "drawing_doc": chunks[draw_idx]["doc_name"],
                    "spec_text": spec_text[:300],
                    "drawing_text": draw_text[:300],
                    "spec_dims_found": list(spec_dims)[:5],
                    "drawing_dims_found": list(draw_dims)[:5],
                    "issue": "Potential dimension mismatch between spec and drawing",
                })
    
    # Deduplicate by document pair, keeping highest confidence
    unique = {}
    for c in contradictions:
        key = (c["spec_doc"], c["drawing_doc"])
        if key not in unique or c["confidence"] > unique[key]["confidence"]:
            unique[key] = c
    contradictions = list(unique.values())

    result = {
        "project_id": project_id,
        "contradictions": contradictions[:10],
        "checked_pairs": len(spec_chunks) * len(drawing_chunks),
        "count": len(contradictions),
        "message": f"Found {len(contradictions)} potential contradictions." if contradictions else "No obvious contradictions detected.",
        "timestamp": datetime.now().isoformat(),
    }

    append_event("contradictions", result)
    audit("scan_contradictions", project_id, f"found {len(contradictions)}")
    return result


def main():
    parser = argparse.ArgumentParser(description="VDC Contradiction Engine")
    parser.add_argument("--project", default="default", help="Project ID")
    parser.add_argument("--query", default="", help="Optional query-aware scan")
    args = parser.parse_args()

    result = scan_contradictions(args.project, query=args.query)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

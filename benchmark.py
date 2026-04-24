#!/usr/bin/env python3
"""
VDC Document Intelligence — Benchmark Suite
Inspired by autoresearch: measure before you optimize.

This script runs a fixed set of queries against the local API and scores
answers on:
  - retrieval_quality: did we fetch the right chunks?
  - factual_accuracy: does the answer contain the expected fact?
  - citation_quality: does it cite the correct source document?
  - safety: is the disclaimer present?

Run: python3 benchmark.py
"""

import requests
import json
import sys
import os
from datetime import datetime

API_BASE = "http://localhost:5001"
API_SECRET = os.environ.get("API_SECRET", "")
if not API_SECRET:
    # Try reading from .env
    try:
        with open(".env") as f:
            for line in f:
                if line.startswith("API_SECRET="):
                    API_SECRET = line.strip().split("=", 1)[1]
                    break
    except Exception:
        pass

HEADERS = {}
if API_SECRET:
    HEADERS["Authorization"] = f"Bearer {API_SECRET}"

# Test cases: (project_id, query, expected_doc, expected_fact_contains, tags)
TEST_CASES = [
    # Downtown Office Tower — known facts
    ("c491acf20f40", "What is the HVAC temperature setpoint for office spaces?", "MECH_SPEC_HVAC.txt", "70°F", ["hvac", "setpoint"]),
    ("c491acf20f40", "What is the concrete strength for columns?", "STRUCT_SPEC.txt", "5,000 psi", ["structural", "concrete"]),
    ("c491acf20f40", "What are the live loads for mechanical rooms?", "STRUCT_SPEC.txt", "150 psf", ["loads", "mechanical"]),
    ("c491acf20f40", "What is NOT the HVAC temperature setpoint for office spaces?", "MECH_SPEC_HVAC.txt", "not", ["negation", "logic"]),
    # Construction Robotics — dynamic content (no hardcoded regex can pass this)
    ("34514bac709a", "What are the key findings of the construction robotics report?", "Construction_Robotics_Report_2026.pdf", "construction robotics", ["robotics", "dynamic"]),
    ("34514bac709a", "What is the purpose of the construction robotics report?", "Construction_Robotics_Report_2026.pdf", "robot", ["robotics", "intent"]),
]

def health_check():
    try:
        r = requests.get(f"{API_BASE}/api/health", headers=HEADERS, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def run_query(project_id: str, query: str, top_k: int = 5):
    try:
        r = requests.post(
            f"{API_BASE}/api/projects/{project_id}/query",
            headers=HEADERS,
            json={"query": query, "top_k": top_k},
            timeout=60,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def score_answer(result: dict, expected_doc: str, expected_fact: str) -> dict:
    score = {"retrieval_ok": False, "fact_ok": False, "citation_ok": False, "disclaimer_ok": False, "total": 0}
    sources = result.get("sources", [])
    answer = result.get("answer", "")

    # 1. Retrieval: expected doc must be in top sources
    doc_names = [s["doc_name"] for s in sources]
    score["retrieval_ok"] = expected_doc in doc_names

    # 2. Fact: answer must contain expected fact (case-insensitive)
    score["fact_ok"] = expected_fact.lower() in answer.lower()

    # 3. Citation: answer text must mention the expected doc name
    score["citation_ok"] = expected_doc in answer

    # 4. Safety: disclaimer must be present
    score["disclaimer_ok"] = "DISCLAIMER" in answer and "qualified engineer" in answer

    # Weighted total
    score["total"] = (
        (1.0 if score["retrieval_ok"] else 0.0) +
        (1.5 if score["fact_ok"] else 0.0) +
        (0.5 if score["citation_ok"] else 0.0) +
        (1.0 if score["disclaimer_ok"] else 0.0)
    )
    return score

def main():
    print("=" * 60)
    print("VDC Document Intelligence — Benchmark Suite")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    if not health_check():
        print("Backend is not running. Start it first: python3 backend/app.py")
        sys.exit(1)

    results = []
    total_score = 0
    max_score = 0

    for project_id, query, expected_doc, expected_fact, tags in TEST_CASES:
        print(f"\n[{' | '.join(tags)}]")
        print(f"Q: {query}")
        result = run_query(project_id, query)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            results.append({"query": query, "error": result["error"], "score": 0})
            max_score += 4.0
            continue

        score = score_answer(result, expected_doc, expected_fact)
        total_score += score["total"]
        max_score += 4.0

        print(f"  Retrieval: {'PASS' if score['retrieval_ok'] else 'FAIL'} (expected {expected_doc})")
        print(f"  Fact:      {'PASS' if score['fact_ok'] else 'FAIL'} (expected '{expected_fact}')")
        print(f"  Citation:  {'PASS' if score['citation_ok'] else 'FAIL'}")
        print(f"  Safety:    {'PASS' if score['disclaimer_ok'] else 'FAIL'}")
        print(f"  Score:     {score['total']:.1f} / 4.0")

        # Print first 200 chars of answer
        ans = result.get("answer", "")[:200].replace("\n", " ")
        print(f"  Answer:    {ans}...")

        results.append({
            "query": query,
            "tags": tags,
            "score": score,
            "top_score": result.get("top_score"),
        })

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_score:.1f} / {max_score:.1f}  ({100*total_score/max_score:.1f}%)")
    print("=" * 60)

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round(100 * total_score / max_score, 1),
        "results": results,
    }
    with open("benchmark_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Report saved to benchmark_report.json")

if __name__ == "__main__":
    main()

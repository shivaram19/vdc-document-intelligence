#!/usr/bin/env python3
"""
phd_interrogator.py — Two PhD-Level VDC Agents Interrogate Each Other

This is the battle arena. Two VDCPhDAgent instances face off:
- They ingest real construction documents
- They take turns asking deeply probing questions
- They answer using memory retrieval
- They critique each other's answers
- Benchmark scores are computed and reported

Usage (as CLI):
    python phd_interrogator.py --docs /path/to/docs --rounds 5 --project phd-battle

Think of it as two VDC PhDs in a conference room, specs spread across the table,
tearing into each other's analysis until the truth about the documents emerges.
"""

import argparse
import json
import sys
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent))
from vdc_phd_agent import VDCPhDAgent, Question, Answer, Critique
from vdc_core import (
    preload_model, save_embeddings, load_embeddings,
    CHUNKS_DIR, EMB_DIR, SHARED_DIR, append_event, audit,
)
from ingestor import process_file

# ---------------------------------------------------------------------------
# Battle Configuration
# ---------------------------------------------------------------------------
DEFAULT_ROUNDS = 5
DEFAULT_TOP_K = 8
SPECIALIZATIONS = ["structural-mep", "fire-architectural"]

BATTLE_HEADER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           VDC PHD BATTLE ARENA — Peer Review on Construction Docs            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Agent Alpha  (Specialist: {spec_a})  vs.  Agent Omega  (Specialist: {spec_b})  ║
║  Documents: {n_docs}  |  Rounds: {rounds}  |  Project: {project}                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ---------------------------------------------------------------------------
# Document Ingestion
# ---------------------------------------------------------------------------
def ingest_documents(doc_paths: List[Path], project_id: str) -> List[str]:
    """Ingest all documents into shared memory for the battle."""
    print(f"\n[INGEST] Loading {len(doc_paths)} documents into project '{project_id}'...")
    doc_names = []

    for dp in doc_paths:
        if not dp.exists():
            print(f"  ⚠️  Skipping missing file: {dp}")
            continue
        print(f"  📄 {dp.name} ...", end=" ", flush=True)
        t0 = time.time()
        result = process_file(dp, doc_type="specification", project_id=project_id, use_docling=False)
        if "error" in result:
            print(f"ERROR: {result['error']}")
            continue
        doc_names.append(dp.name)
        print(f"OK ({result.get('chunks', 0)} chunks, {time.time()-t0:.1f}s)")

    # Load total chunk count from shared memory
    _, all_chunks = load_embeddings(project_id)
    print(f"[INGEST] Complete. {len(doc_names)} docs, {len(all_chunks)} total chunks.\n")
    return doc_names


# ---------------------------------------------------------------------------
# Battle Round
# ---------------------------------------------------------------------------
def run_round(
    round_num: int,
    agent_asker: VDCPhDAgent,
    agent_answerer: VDCPhDAgent,
    agent_critiquer: VDCPhDAgent,
    project_id: str,
    doc_names: List[str],
    history: List[Dict],
) -> Dict:
    """One full round: ask → answer → critique."""
    print(f"\n{'─'*80}")
    print(f"  ROUND {round_num} | {agent_asker.agent_id} asks → {agent_answerer.agent_id} answers")
    print(f"{'─'*80}")

    # 1. ASK
    t0 = time.time()
    question = agent_asker.ask(project_id, history, doc_names)
    print(f"\n  ❓ QUESTION ({question.category})")
    print(f"     {question.text}")
    print(f"     [depth={question.expected_depth}, hint={question.target_doc_hint or 'none'}]")

    # 2. ANSWER
    t1 = time.time()
    answer = agent_answerer.answer(project_id, question)
    print(f"\n  💬 ANSWER (confidence={answer.confidence:.3f}, sources={len(answer.sources)})")
    # Print answer with line wrapping
    for line in answer.text.split("\n"):
        for sub in _wrap(line, 76):
            print(f"     {sub}")

    if answer.contradictions_found:
        print(f"\n  ⚠️  CONTRADICTIONS DETECTED ({len(answer.contradictions_found)}):")
        for c in answer.contradictions_found:
            print(f"     • {c['unit'].upper()}: {', '.join(c['values'])} across {', '.join(c['documents'][:2])}")

    # 3. CRITIQUE
    t2 = time.time()
    critique = agent_critiquer.critique(question, answer, project_id)
    print(f"\n  🎓 CRITIQUE by {agent_critiquer.agent_id} (score: {critique.score}/100)")
    if critique.strengths:
        print(f"     ✅ Strengths: {'; '.join(critique.strengths)}")
    if critique.weaknesses:
        print(f"     ❌ Weaknesses: {'; '.join(critique.weaknesses)}")
    if critique.missing_citations:
        print(f"     📌 Missing citations: {'; '.join(critique.missing_citations[:3])}")
    if critique.suggested_followups:
        print(f"     🔍 Suggested follow-ups:")
        for fu in critique.suggested_followups:
            print(f"       → {fu}")

    duration = time.time() - t0
    print(f"\n  ⏱️  Round duration: {duration:.1f}s")

    return {
        "round": round_num,
        "asker": agent_asker.agent_id,
        "answerer": agent_answerer.agent_id,
        "critiquer": agent_critiquer.agent_id,
        "question": {"text": question.text, "category": question.category},
        "answer": {"text": answer.text, "confidence": answer.confidence, "sources": len(answer.sources)},
        "critique": {"score": critique.score, "strengths": critique.strengths, "weaknesses": critique.weaknesses},
        "duration_sec": round(duration, 2),
    }


def _wrap(text: str, width: int) -> List[str]:
    """Simple text wrapper."""
    if len(text) <= width:
        return [text] if text.strip() else []
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines if lines else [text[:width]]


# ---------------------------------------------------------------------------
# Battle Orchestration
# ---------------------------------------------------------------------------
def run_battle(
    doc_paths: List[Path],
    project_id: str = "phd-battle",
    rounds: int = DEFAULT_ROUNDS,
    spec_a: str = SPECIALIZATIONS[0],
    spec_b: str = SPECIALIZATIONS[1],
) -> Dict:
    """Run the full PhD battle: ingest, then N rounds of Q&A."""
    # Preload model
    print("[INIT] Preloading embedding model...")
    preload_model()

    # Ingest documents
    doc_names = ingest_documents(doc_paths, project_id)
    if not doc_names:
        return {"error": "No documents ingested"}

    # Create agents
    agent_alpha = VDCPhDAgent("Alpha", specialization=spec_a)
    agent_omega = VDCPhDAgent("Omega", specialization=spec_b)

    print(BATTLE_HEADER.format(
        spec_a=spec_a, spec_b=spec_b,
        n_docs=len(doc_names), rounds=rounds, project=project_id,
    ))

    history: List[Dict] = []
    round_results: List[Dict] = []
    battle_start = time.time()

    for r in range(1, rounds + 1):
        # Alternate who asks
        if r % 2 == 1:
            result = run_round(r, agent_alpha, agent_omega, agent_alpha, project_id, doc_names, history)
        else:
            result = run_round(r, agent_omega, agent_alpha, agent_omega, project_id, doc_names, history)

        history.append({
            "question": result["question"]["text"],
            "answer": result["answer"]["text"],
            "category": result["question"]["category"],
        })
        round_results.append(result)

    battle_duration = time.time() - battle_start

    # Compute final scores
    alpha_stats = agent_alpha.stats()
    omega_stats = agent_omega.stats()

    # Winner determination: higher average critique score
    winner = "Alpha" if alpha_stats["average_critique_score"] > omega_stats["average_critique_score"] else "Omega"
    if abs(alpha_stats["average_critique_score"] - omega_stats["average_critique_score"]) < 5:
        winner = "TIE"

    report = {
        "project_id": project_id,
        "documents": doc_names,
        "rounds": rounds,
        "battle_duration_sec": round(battle_duration, 1),
        "agent_alpha": alpha_stats,
        "agent_omega": omega_stats,
        "winner": winner,
        "rounds_detail": round_results,
        "timestamp": datetime.now().isoformat(),
    }

    # Save report
    report_path = SHARED_DIR / "phd_battles" / f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str))

    print(f"\n{'='*80}")
    print(f"  BATTLE COMPLETE")
    print(f"{'='*80}")
    print(f"  Winner: {winner}")
    print(f"  Alpha avg critique score: {alpha_stats['average_critique_score']}")
    print(f"  Omega avg critique score: {omega_stats['average_critique_score']}")
    print(f"  Total duration: {battle_duration:.1f}s")
    print(f"  Report saved: {report_path}")
    print(f"{'='*80}\n")

    append_event("phd_battle", {
        "type": "battle_complete",
        "project": project_id,
        "winner": winner,
        "alpha_score": alpha_stats["average_critique_score"],
        "omega_score": omega_stats["average_critique_score"],
    })

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="VDC PhD Battle Arena — Two agents interrogate each other on construction docs"
    )
    parser.add_argument("--docs", required=True, help="Directory containing PDF/TXT/DOCX files")
    parser.add_argument("--project", default="phd-battle", help="Project ID")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS, help="Number of battle rounds")
    parser.add_argument("--spec-a", default=SPECIALIZATIONS[0], help="Alpha agent specialization")
    parser.add_argument("--spec-b", default=SPECIALIZATIONS[1], help="Omega agent specialization")
    parser.add_argument("--docling", action="store_true", help="Use Docling parser")
    args = parser.parse_args()

    doc_dir = Path(args.docs)
    if not doc_dir.exists():
        print(f"ERROR: Directory not found: {doc_dir}")
        sys.exit(1)

    doc_paths = sorted([f for f in doc_dir.iterdir() if f.suffix.lower() in {".pdf", ".txt", ".docx", ".md"}])
    if not doc_paths:
        print(f"ERROR: No supported documents found in {doc_dir}")
        sys.exit(1)

    report = run_battle(
        doc_paths=doc_paths,
        project_id=args.project,
        rounds=args.rounds,
        spec_a=args.spec_a,
        spec_b=args.spec_b,
    )

    # Also print raw JSON for piping
    print("\n--- RAW REPORT (JSON) ---")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()

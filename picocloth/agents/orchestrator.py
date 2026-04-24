#!/usr/bin/env python3
"""
VDC Agent Orchestrator
Coordinates workflows across the fleet by reading/writing shared memory.
Acts as the bridge between user intent and specialist agents.

Workflows:
  ingest   → ingestor agent
  query    → retriever agent  
  rfi      → rfi_drafter agent
  scan     → contradiction_engine agent

Usage:
    python orchestrator.py --workflow ingest --project default --file path.pdf
    python orchestrator.py --workflow query --project default --query "concrete strength?"
    python orchestrator.py --workflow rfi --project default --question "..." --number RFI-006
    python orchestrator.py --workflow scan --project default
    python orchestrator.py --daemon              # watch task queue forever
"""

import argparse
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from vdc_core import TASK_DIR, append_event, read_state, write_state

# Import agent functions directly (no HTTP)
from ingestor import process_file
from retriever import answer_query
from contradiction_engine import scan_contradictions
from rfi_drafter import draft_rfi


def run_workflow(workflow: str, params: dict) -> dict:
    """Execute a workflow by calling the appropriate agent function."""
    project_id = params.get("project", "default")
    t0 = time.time()

    append_event("tasks", {
        "type": "workflow_start",
        "workflow": workflow,
        "project_id": project_id,
        "params": params,
    })

    if workflow == "ingest":
        fpath = params.get("file")
        if not fpath:
            return {"error": "No file provided"}
        result = process_file(
            Path(fpath),
            doc_type=params.get("doc_type", "drawing"),
            project_id=project_id,
            use_docling=params.get("use_docling", False),
        )
        # Auto-trigger contradiction scan after ingest
        if "error" not in result:
            scan_contradictions(project_id)

    elif workflow == "query":
        query = params.get("query", "").strip()
        if not query:
            return {"error": "Empty query"}
        result = answer_query(project_id, query, top_k=params.get("top_k", 5))

    elif workflow == "rfi":
        question = params.get("question", "").strip()
        if not question:
            return {"error": "Empty question"}
        result = draft_rfi(project_id, question, params.get("number", "RFI-XXX"))

    elif workflow == "scan":
        result = scan_contradictions(project_id, query=params.get("query", ""))

    else:
        return {"error": f"Unknown workflow: {workflow}"}

    duration = round(time.time() - t0, 2)
    result["_workflow"] = workflow
    result["_duration_sec"] = duration
    result["_timestamp"] = datetime.now().isoformat()

    append_event("tasks", {
        "type": "workflow_complete",
        "workflow": workflow,
        "project_id": project_id,
        "duration_sec": duration,
        "success": "error" not in result,
    })

    return result


def watch_task_queue(poll_interval: float = 1.0):
    """Daemon mode: watch shared/task-queue.jsonl for new tasks."""
    queue_path = TASK_DIR / "queue.jsonl"
    processed = 0
    print("[orchestrator] Daemon mode. Watching task queue...")
    while True:
        if queue_path.exists():
            lines = queue_path.read_text().strip().split("\n")
            for i, line in enumerate(lines[processed:], start=processed):
                if not line.strip():
                    continue
                try:
                    task = json.loads(line)
                    print(f"[orchestrator] Executing task: {task.get('workflow')} for project {task.get('project')}")
                    result = run_workflow(task["workflow"], task.get("params", {}))
                    print(f"[orchestrator] Result: {json.dumps(result, indent=2, default=str)[:500]}")
                except Exception as e:
                    print(f"[orchestrator] Task error: {e}")
                processed = i + 1
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="VDC Agent Orchestrator")
    parser.add_argument("--workflow", choices=["ingest", "query", "rfi", "scan"], help="Workflow type")
    parser.add_argument("--project", default="default", help="Project ID")
    parser.add_argument("--file", help="File path (for ingest)")
    parser.add_argument("--doc-type", default="drawing", help="Document type")
    parser.add_argument("--query", help="Query text")
    parser.add_argument("--question", help="RFI question")
    parser.add_argument("--number", default="RFI-XXX", help="RFI number")
    parser.add_argument("--top-k", type=int, default=5, help="Retrieve top K chunks")
    parser.add_argument("--docling", action="store_true", help="Use Docling parser")
    parser.add_argument("--daemon", action="store_true", help="Watch task queue forever")
    args = parser.parse_args()

    if args.daemon:
        watch_task_queue()
    elif args.workflow:
        params = {
            "project": args.project,
            "file": args.file,
            "doc_type": args.doc_type,
            "query": args.query or args.question,
            "question": args.question,
            "number": args.number,
            "top_k": args.top_k,
            "use_docling": args.docling,
        }
        result = run_workflow(args.workflow, params)
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

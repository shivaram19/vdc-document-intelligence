#!/usr/bin/env python3
"""
VDC Ingestor Agent (node-e)
Watches the inbox/ directory for new documents, parses them,
chunks, embeds, and writes durable artifacts to shared memory.

Usage:
    python ingestor.py --watch              # daemon mode
    python ingestor.py --once               # process inbox once, exit
    python ingestor.py --file path.pdf      # process single file
"""

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from vdc_core import (
    INBOX_DIR, DOCS_DIR, SHARED_DIR,
    extract_text, detect_suspicious, chunk_text, encode,
    save_embeddings, load_embeddings, append_event, audit, read_state, write_state, write_json,
    ALLOWED_EXTS, MAX_FILE_MB,
)


def process_file(filepath: Path, doc_type: str = "drawing", project_id: str = "default",
                 use_docling: bool = False) -> dict:
    """Ingest a single file into the VDC shared memory."""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    if ext not in ALLOWED_EXTS:
        return {"error": f"Unsupported type: {ext}"}

    size_mb = filepath.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        return {"error": f"File too large: {size_mb:.1f} MB (max {MAX_FILE_MB})"}

    text = extract_text(str(filepath), use_docling=use_docling)
    susp = detect_suspicious(text)
    if susp:
        audit("upload_rejected", project_id, f"{filepath.name}: suspicious content")
        return {"error": "Suspicious content detected. Upload rejected.", "patterns": susp}

    chunks = chunk_text(text)
    embeddings = encode(chunks) if chunks else []

    doc_id = hashlib.md5(f"{filepath.name}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    chunk_records = [
        {
            "id": f"{doc_id}_chunk_{i}",
            "text": c,
            "doc_id": doc_id,
            "doc_name": filepath.name,
            "doc_type": doc_type,
            "index": i,
        }
        for i, c in enumerate(chunks)
    ]

    # Check for duplicate by filename
    existing_emb, existing_chunks = load_embeddings(project_id)
    if existing_chunks:
        existing_names = {c["doc_name"] for c in existing_chunks}
        if filepath.name in existing_names:
            return {"error": f"Document '{filepath.name}' already exists in project. Skipping duplicate."}

    # Merge with existing project embeddings
    if existing_emb is not None and len(existing_emb) > 0 and len(embeddings) > 0:
        all_emb = __import__('numpy').vstack([existing_emb, embeddings])
        all_chunks = existing_chunks + chunk_records
    elif len(embeddings) > 0:
        all_emb = embeddings
        all_chunks = chunk_records
    else:
        all_emb = existing_emb if existing_emb is not None else []
        all_chunks = existing_chunks

    save_embeddings(project_id, all_emb, all_chunks)

    # Save document metadata
    doc_meta = {
        "id": doc_id,
        "name": filepath.name,
        "type": doc_type,
        "project_id": project_id,
        "uploaded": datetime.now().isoformat(),
        "chunk_count": len(chunks),
        "word_count": len(text.split()),
        "size_mb": round(size_mb, 2),
    }
    write_json(DOCS_DIR / f"{doc_id}.json", doc_meta)

    # Update state
    state = read_state()
    proj = next((p for p in state.get("projects", []) if p["id"] == project_id), None)
    if not proj:
        proj = {"id": project_id, "name": project_id, "client": "", "created": datetime.now().isoformat(), "docs": []}
        state.setdefault("projects", []).append(proj)
    proj["docs"] = [d for d in proj.get("docs", []) if d["id"] != doc_id] + [doc_meta]
    write_state(state)

    # Emit event
    append_event("tasks", {
        "type": "document_ingested",
        "project_id": project_id,
        "doc_id": doc_id,
        "doc_name": filepath.name,
        "chunk_count": len(chunks),
    })
    audit("upload", project_id, filepath.name)

    return {"doc_id": doc_id, "chunks": len(chunks), "project_id": project_id}


def watch_inbox(poll_interval: float = 2.0):
    """Continuously watch inbox/ for new files."""
    print(f"[ingestor] Watching {INBOX_DIR} for new documents...")
    processed = set()
    while True:
        for fpath in INBOX_DIR.iterdir():
            if fpath.is_file() and fpath.name not in processed:
                print(f"[ingestor] New file detected: {fpath.name}")
                # Determine doc_type from filename hints
                name_lower = fpath.name.lower()
                if any(x in name_lower for x in ["spec", "specification"]):
                    doc_type = "spec"
                elif any(x in name_lower for x in ["draw", "plan", "arch", "struct"]):
                    doc_type = "drawing"
                elif "rfi" in name_lower:
                    doc_type = "rfi"
                else:
                    doc_type = "drawing"
                result = process_file(fpath, doc_type=doc_type)
                if "error" not in result:
                    processed.add(fpath.name)
                    # Optionally move processed file to archive
                    archive = INBOX_DIR / "archive"
                    archive.mkdir(exist_ok=True)
                    fpath.rename(archive / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fpath.name}")
                else:
                    print(f"[ingestor] Error processing {fpath.name}: {result['error']}")
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="VDC Document Ingestor Agent")
    parser.add_argument("--watch", action="store_true", help="Daemon mode: watch inbox forever")
    parser.add_argument("--once", action="store_true", help="Process inbox once and exit")
    parser.add_argument("--file", type=str, help="Process a single file")
    parser.add_argument("--type", default="drawing", help="Document type")
    parser.add_argument("--project", default="default", help="Project ID")
    parser.add_argument("--docling", action="store_true", help="Use Docling parser")
    args = parser.parse_args()

    if args.file:
        result = process_file(Path(args.file), doc_type=args.type, project_id=args.project, use_docling=args.docling)
        print(json.dumps(result, indent=2))
    elif args.watch:
        watch_inbox()
    elif args.once:
        for fpath in INBOX_DIR.iterdir():
            if fpath.is_file():
                result = process_file(fpath, project_id=args.project)
                print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

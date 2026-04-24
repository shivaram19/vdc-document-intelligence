#!/usr/bin/env python3
"""
VDC Inbox Watcher Daemon
Monitors the shared inbox/ directory and automatically triggers
document ingestion workflows when new files appear.

This daemon runs continuously and acts as the "document parser agent"
entry point for the fleet.

Usage:
    python inbox_watcher.py              # foreground
    python inbox_watcher.py --daemon     # background (detached)
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ingestor import process_file, INBOX_DIR
from vdc_core import append_event
from datetime import datetime


def watch(poll_interval: float = 2.0):
    print(f"[inbox_watcher] Monitoring {INBOX_DIR}")
    processed = set()
    archive = INBOX_DIR / "archive"
    archive.mkdir(exist_ok=True)

    while True:
        for fpath in INBOX_DIR.iterdir():
            if not fpath.is_file() or fpath.name in processed or fpath.name.endswith(".tmp"):
                continue

            print(f"[inbox_watcher] Detected: {fpath.name}")
            append_event("tasks", {
                "type": "inbox_detected",
                "filename": fpath.name,
                "size_bytes": fpath.stat().st_size,
            })

            # Auto-detect doc type from filename
            nl = fpath.name.lower()
            if any(x in nl for x in ["spec", "specification"]):
                doc_type = "spec"
            elif any(x in nl for x in ["draw", "plan", "arch", "struct", "elevation"]):
                doc_type = "drawing"
            elif "rfi" in nl:
                doc_type = "rfi"
            else:
                doc_type = "drawing"

            result = process_file(fpath, doc_type=doc_type)

            if "error" not in result:
                processed.add(fpath.name)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fpath.rename(archive / f"{ts}_{fpath.name}")
                print(f"[inbox_watcher] Ingested: {result.get('doc_id')} ({result.get('chunks', 0)} chunks)")
            else:
                print(f"[inbox_watcher] FAILED: {result['error']}")

        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0, help="Poll interval in seconds")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    args = parser.parse_args()

    if args.daemon:
        import os
        pid = os.fork()
        if pid > 0:
            print(f"[inbox_watcher] Daemon PID: {pid}")
            sys.exit(0)
        os.setsid()

    try:
        watch(args.interval)
    except KeyboardInterrupt:
        print("[inbox_watcher] Shutting down.")


if __name__ == "__main__":
    main()

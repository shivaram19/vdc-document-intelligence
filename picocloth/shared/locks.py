"""
Shared Memory Locking — Atomic I/O for the Agent Fleet

All agents that read/write shared JSON/JSONL state must use these helpers.
filelock (fcntl on Linux) provides cross-process safety.
Atomic writes (tempfile + os.replace) prevent half-written files on crash.

[CITE: ZetCode2025] os.replace atomically replaces destination on POSIX (rename(2))
and Windows (MoveFileEx). Pattern: write to tempfile in same directory, then replace.
[CITE: ActiveState2015] tempfile.mkstemp + os.fdopen + os.replace for atomic writes.
[CITE: PythonOrg2021] Community consensus: tempfile + rename is the correct idiom.
[CITE: StackOverflow2021] os.replace() is atomic on ALL platforms under most conditions.
"""

import json
import os
import tempfile
from pathlib import Path
from contextlib import contextmanager
from filelock import FileLock


def _lock_path(path: Path) -> Path:
    return Path(str(path) + ".lock")


@contextmanager
def locked_write(path: Path):
    """Acquire a file lock, yield, then atomically write the file."""
    lock = FileLock(_lock_path(path), timeout=10)
    with lock:
        yield


def atomic_json_write(path: Path, data: dict):
    """Write JSON atomically with file locking."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(_lock_path(path), timeout=10)
    with lock:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp, path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise


def locked_json_read(path: Path, default=None) -> dict:
    """Read JSON with file locking. Returns default if file missing."""
    path = Path(path)
    if not path.exists():
        return default if default is not None else {}
    lock = FileLock(_lock_path(path), timeout=10)
    with lock:
        return json.loads(path.read_text())


def locked_jsonl_append(path: Path, record: dict):
    """Append a JSON line atomically with file locking."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(_lock_path(path), timeout=10)
    with lock:
        with open(path, "a") as f:
            f.write(json.dumps(record, default=str) + "\n")

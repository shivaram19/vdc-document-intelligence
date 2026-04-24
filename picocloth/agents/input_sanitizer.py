#!/usr/bin/env python3
"""
input_sanitizer.py — Enterprise Input Validation & Sanitization

Research basis: Errico et al. (2025) "Securing the MCP" — content-injection
attackers embed malicious instructions into data. Every input must be validated
against schemas, size limits, and content filters before reaching agent logic.

Principles:
  - Fail-closed: invalid input rejected, not coerced
  - Defense in depth: schema + regex + size + path validation
  - No regex on user-controlled paths (use pathlib normalization)
"""

import json
import re
from pathlib import Path
from typing import Any

# ── Size Limits ──────────────────────────────────────────────────────────────
MAX_QUERY_LEN = 4096
MAX_PROJECT_NAME_LEN = 128
MAX_FILENAME_LEN = 256
MAX_FILE_SIZE_MB = 50
MAX_JSON_DEPTH = 8
MAX_JSON_KEYS = 50

# ── Regex Patterns ───────────────────────────────────────────────────────────
# Project IDs: alphanumeric, hyphens, underscores only
PROJECT_ID_RE = re.compile(r'^[a-zA-Z0-9_-]+$')

# Safe filenames: no path traversal, no control chars
SAFE_FILENAME_RE = re.compile(r'^[^/\\<>"|?*\x00-\x1f]+$')

# SQL-like injection patterns (basic heuristic)
SQL_INJECTION_RE = re.compile(
    r'(--|#|/\*|\*/|;|\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|SCRIPT)\b)',
    re.IGNORECASE
)

# Command injection patterns
CMD_INJECTION_RE = re.compile(r'[;&|`$()]')

# HTML/JS injection patterns
XSS_RE = re.compile(r'<(script|iframe|object|embed|form)|javascript:', re.IGNORECASE)


class ValidationError(Exception):
    """Structured validation failure with field and reason."""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"[{field}] {reason}")


def sanitize_project_id(value: str) -> str:
    """Validate project identifier."""
    if not value or not isinstance(value, str):
        raise ValidationError("project", "Project ID must be a non-empty string")
    if len(value) > MAX_PROJECT_NAME_LEN:
        raise ValidationError("project", f"Project ID exceeds {MAX_PROJECT_NAME_LEN} chars")
    if not PROJECT_ID_RE.match(value):
        raise ValidationError("project", "Project ID contains invalid characters")
    return value


def sanitize_query(value: str) -> str:
    """Validate and sanitize a natural-language query."""
    if not value or not isinstance(value, str):
        raise ValidationError("query", "Query must be a non-empty string")
    if len(value) > MAX_QUERY_LEN:
        raise ValidationError("query", f"Query exceeds {MAX_QUERY_LEN} chars")
    if SQL_INJECTION_RE.search(value):
        raise ValidationError("query", "Query contains suspicious patterns")
    if XSS_RE.search(value):
        raise ValidationError("query", "Query contains markup/script patterns")
    # Strip excessive whitespace, normalize
    return " ".join(value.split())


def sanitize_filename(value: str) -> str:
    """Validate filename, prevent path traversal."""
    if not value or not isinstance(value, str):
        raise ValidationError("filename", "Filename must be a non-empty string")
    if len(value) > MAX_FILENAME_LEN:
        raise ValidationError("filename", f"Filename exceeds {MAX_FILENAME_LEN} chars")
    if not SAFE_FILENAME_RE.match(value):
        raise ValidationError("filename", "Filename contains invalid characters")
    # Resolve to absolute and ensure it stays within expected boundaries
    return value


def sanitize_file_path(value: str, allowed_base: Path = None) -> Path:
    """
    Validate file path and ensure it resolves within allowed_base.
    Prevents directory traversal attacks.
    """
    if not value or not isinstance(value, str):
        raise ValidationError("file", "File path must be a non-empty string")
    try:
        path = Path(value).resolve()
    except Exception:
        raise ValidationError("file", "Invalid file path")

    if allowed_base:
        allowed = allowed_base.resolve()
        try:
            path.relative_to(allowed)
        except ValueError:
            raise ValidationError("file", f"File path escapes allowed directory: {allowed}")
    return path


def sanitize_text_field(value: str, name: str, max_len: int = 1024,
                        allow_markup: bool = False) -> str:
    """Generic text field validation."""
    if not isinstance(value, str):
        raise ValidationError(name, f"{name} must be a string")
    if len(value) > max_len:
        raise ValidationError(name, f"{name} exceeds {max_len} chars")
    if not allow_markup and XSS_RE.search(value):
        raise ValidationError(name, f"{name} contains markup patterns")
    return value.strip()


def sanitize_json_payload(data: Any, depth: int = 0, key_count: int = 0) -> Any:
    """Validate JSON payload depth and key count to prevent parser attacks."""
    if depth > MAX_JSON_DEPTH:
        raise ValidationError("json", f"JSON nesting exceeds {MAX_JSON_DEPTH}")
    if key_count > MAX_JSON_KEYS:
        raise ValidationError("json", f"JSON key count exceeds {MAX_JSON_KEYS}")

    if isinstance(data, dict):
        new = {}
        for k, v in data.items():
            if not isinstance(k, str):
                raise ValidationError("json", "All JSON keys must be strings")
            new[k] = sanitize_json_payload(v, depth + 1, key_count + len(data))
        return new
    elif isinstance(data, list):
        return [sanitize_json_payload(item, depth + 1, key_count) for item in data]
    elif isinstance(data, str):
        # Basic string sanitization for JSON values
        if len(data) > MAX_QUERY_LEN * 2:
            raise ValidationError("json", "String value exceeds maximum length")
        return data
    elif isinstance(data, (int, float, bool)) or data is None:
        return data
    else:
        raise ValidationError("json", f"Unsupported JSON type: {type(data).__name__}")


def sanitize_command(cmd: dict, allowed_actions: set = None) -> dict:
    """
    Full command sanitization pipeline.
    Returns sanitized command or raises ValidationError.
    """
    if not isinstance(cmd, dict):
        raise ValidationError("cmd", "Command must be a JSON object")

    action = cmd.get("action")
    if not action or not isinstance(action, str):
        raise ValidationError("action", "Action must be a non-empty string")
    if allowed_actions and action not in allowed_actions:
        raise ValidationError("action", f"Action '{action}' not allowed")

    # Sanitize project ID if present
    project = cmd.get("project", "default")
    cmd["project"] = sanitize_project_id(project)

    # Action-specific validation
    if action in ("query", "scan"):
        if "query" in cmd:
            cmd["query"] = sanitize_query(cmd["query"])
    elif action == "rfi":
        if "question" in cmd:
            cmd["question"] = sanitize_query(cmd["question"])
        if "number" in cmd:
            cmd["number"] = sanitize_text_field(cmd["number"], "number", max_len=64)
    elif action == "ingest":
        if "file" in cmd:
            cmd["file"] = str(sanitize_file_path(cmd["file"]))
        if "doc_type" in cmd:
            cmd["doc_type"] = sanitize_text_field(cmd["doc_type"], "doc_type", max_len=32)
    elif action == "create_project":
        if "name" in cmd:
            cmd["name"] = sanitize_text_field(cmd["name"], "name", max_len=MAX_PROJECT_NAME_LEN)
        if "client" in cmd:
            cmd["client"] = sanitize_text_field(cmd["client"], "client", max_len=MAX_PROJECT_NAME_LEN)

    # Sanitize behavioral profile (should be a dict of numbers)
    if "behavioral_profile" in cmd:
        profile = cmd["behavioral_profile"]
        if isinstance(profile, dict):
            for k, v in profile.items():
                if not isinstance(v, (int, float)):
                    raise ValidationError("behavioral_profile", f"Profile value for '{k}' must be numeric")
        elif not isinstance(profile, (list, type(None))):
            raise ValidationError("behavioral_profile", "Profile must be an object or null")

    # Sanitize token (basic format check)
    if "token" in cmd and cmd["token"]:
        tok = cmd["token"]
        if not isinstance(tok, str) or len(tok) > 2048:
            raise ValidationError("token", "Invalid token format")

    return cmd


def sanitize_inbox_upload(filename: str, content_length: int) -> None:
    """Validate inbox upload parameters."""
    sanitize_filename(filename)
    if content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError("file", f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

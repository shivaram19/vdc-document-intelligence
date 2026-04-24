#!/usr/bin/env python3
"""Seed the VDC Document Intelligence demo with sample data."""

import requests
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

API_BASE = "http://localhost:5001"
SAMPLE_DIR = Path("sample_docs")
API_SECRET = os.environ.get("API_SECRET", "")
HEADERS = {"Authorization": f"Bearer {API_SECRET}"} if API_SECRET else {}

def create_project(name, client):
    r = requests.post(f"{API_BASE}/api/projects", json={"name": name, "client": client}, headers=HEADERS)
    return r.json()["project"]["id"]

def upload_file(project_id, filepath, doc_type):
    with open(filepath, "rb") as f:
        files = {"file": (filepath.name, f, "text/plain")}
        data = {"type": doc_type}
        r = requests.post(f"{API_BASE}/api/projects/{project_id}/upload", files=files, data=data, headers=HEADERS)
    return r.json()

def main():
    print("Creating demo project...")
    pid = create_project("Downtown Office Tower", "ABC Development Corp")
    print(f"Project ID: {pid}")
    
    docs = [
        ("MECH_SPEC_HVAC.txt", "spec"),
        ("ARCH_DRAWING_NOTES.txt", "drawing"),
        ("STRUCT_SPEC.txt", "spec"),
        ("RFI_LOG.txt", "rfi"),
        ("FIRE_PROTECTION_SPEC.txt", "spec"),
    ]
    
    for filename, doc_type in docs:
        filepath = SAMPLE_DIR / filename
        if filepath.exists():
            print(f"Uploading {filename}...")
            result = upload_file(pid, filepath, doc_type)
            print(f"  → {result['document']['chunk_count']} chunks")
    
    print("\nDemo seeded! Open frontend/index.html in a browser.")
    print(f"API running at {API_BASE}")

if __name__ == "__main__":
    main()

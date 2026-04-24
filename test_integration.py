#!/usr/bin/env python3
"""VDC Document Intelligence - Integration Tests"""

import requests
import json
import os
import sys

BASE_URL = "http://localhost:5001"
API_SECRET = os.environ.get("API_SECRET", "9jZmSXM1fnWIluhXe9DCtRSYpgdx5NGCjXpgCa2PRSw")

def headers(ct=None):
    h = {"Authorization": f"Bearer {API_SECRET}"}
    if ct:
        h["Content-Type"] = ct
    return h

def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    data = r.json()
    assert data.get("status") == "ok"
    print("✅ Health check passed")
    return True

def test_create_project():
    r = requests.post(f"{BASE_URL}/api/projects", json={"name": "Integration Test Project", "client": "PicoCloth Fleet"}, headers=headers("application/json"), timeout=10)
    assert r.status_code in [200, 201], f"Create project failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "project" in data and "id" in data["project"]
    print(f"✅ Project created: {data['project']['id']}")
    return data["project"]["id"]

def test_list_projects():
    r = requests.get(f"{BASE_URL}/api/projects", headers=headers(), timeout=10)
    assert r.status_code == 200, f"List projects failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "projects" in data
    print(f"✅ List projects passed ({len(data['projects'])} projects)")
    return True

def test_upload_document(project_id):
    test_file = "/tmp/test_doc.txt"
    with open(test_file, "w") as f:
        f.write("CONCRETE SPECIFICATIONS\n")
        f.write("All concrete work shall comply with ACI 318-19.\n")
        f.write("Columns: 5,000 psi minimum at 28 days.\n")
        f.write("Floor slabs: 4,000 psi minimum at 28 days.\n")
    with open(test_file, "rb") as f:
        files = {"file": ("test_doc.txt", f, "text/plain")}
        data = {"type": "spec"}
        r = requests.post(f"{BASE_URL}/api/projects/{project_id}/upload", files=files, data=data, headers=headers(), timeout=30)
    os.remove(test_file)
    assert r.status_code in [200, 201], f"Upload failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "document" in data
    print(f"✅ Document upload passed: {data['document']['id']} ({data['document']['chunk_count']} chunks)")
    return data["document"]["id"]

def test_query(project_id):
    r = requests.post(f"{BASE_URL}/api/projects/{project_id}/query", json={"query": "What is the concrete strength for columns?", "top_k": 3}, headers=headers("application/json"), timeout=60)
    assert r.status_code == 200, f"Query failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "answer" in data
    print(f"✅ Query passed: {data['answer'][:120]}...")
    return True

def test_draft_rfi(project_id):
    r = requests.post(f"{BASE_URL}/api/projects/{project_id}/draft-rfi", json={"question": "What is the required concrete strength for columns?", "rfi_number": "RFI-TEST-001"}, headers=headers("application/json"), timeout=60)
    assert r.status_code == 200, f"Draft RFI failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "draft" in data
    print(f"✅ Draft RFI passed: {data['rfi_number']}")
    return True

def test_scan_contradictions(project_id):
    r = requests.get(f"{BASE_URL}/api/projects/{project_id}/contradictions", headers=headers(), timeout=60)
    assert r.status_code == 200, f"Contradictions failed: {r.status_code} - {r.text}"
    data = r.json()
    assert "contradictions" in data
    print(f"✅ Contradiction scan passed: {len(data['contradictions'])} found")
    return True

def test_list_documents(project_id):
    r = requests.get(f"{BASE_URL}/api/projects/{project_id}/documents", headers=headers(), timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "documents" in data
    print(f"✅ List documents passed ({len(data['documents'])} docs)")
    return True

def run_all_tests():
    print("🧪 VDC Document Intelligence - Integration Tests")
    print("=" * 50)
    try:
        test_health()
        test_list_projects()
        project_id = test_create_project()
        test_list_documents(project_id)
        doc_id = test_upload_document(project_id)
        test_query(project_id)
        test_draft_rfi(project_id)
        test_scan_contradictions(project_id)
        print("=" * 50)
        print("🎉 ALL TESTS PASSED")
        return 0
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

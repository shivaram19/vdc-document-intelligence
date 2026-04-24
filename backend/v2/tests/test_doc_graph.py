#!/usr/bin/env python3
"""
Test suite for Medha v2 Phase 1: Document Graph Engine
"""

import sys
from pathlib import Path

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v2.reference_patterns import ReferenceExtractor, ReferenceMatch, parse_drawing_index
from v2.drawing_index import DrawingIndexParser, DrawingIndex
from v2.doc_graph import DocumentGraph, build_graph_from_documents


# =============================================================================
# MOCK DRAWING SET
# =============================================================================

DRAWING_INDEX_TEXT = """
PROJECT: DOWNTOWN OFFICE TOWER
DRAWING INDEX

A-101   FIRST FLOOR PLAN
A-102   SECOND FLOOR PLAN
A-201   REFLECTED CEILING PLAN
A-301   BUILDING SECTIONS
A-302   WALL SECTIONS
A-401   INTERIOR ELEVATIONS
A-501   DOOR AND WINDOW SCHEDULES
A-601   FINISH SCHEDULE
S-101   FOUNDATION PLAN
S-201   ROOF FRAMING PLAN
S-301   STRUCTURAL DETAILS
M-101   HVAC PLAN
M-201   HVAC DETAILS
E-101   ELECTRICAL PLAN
E-201   ELECTRICAL DETAILS
FP-101  FIRE PROTECTION PLAN
"""

DOC_A101 = """
SHEET A-101 - FIRST FLOOR PLAN

General Notes:
- See Detail 3 on Sheet S-301 for column connection
- Refer to Section A-302 for typical wall section
- Door tags per schedule on A-501
- Finish schedule on A-601
- All dimensions per structural drawings S-101

Coordinate with electrical plan E-101 for outlet locations.
See HVAC plan M-101 for diffuser locations.
"""

DOC_S301 = """
SHEET S-301 - STRUCTURAL DETAILS

Detail 1: Column base plate connection
Detail 2: Beam-to-column moment connection
Detail 3: Column splice connection (referenced from A-101)

Refer to spec section 033000 for concrete requirements.
See also structural calc package.
"""

DOC_M101 = """
SHEET M-101 - HVAC PLAN

All ductwork sized per ASHRAE 90.1.
See mechanical spec section 230000 for equipment requirements.
VAV units per schedule on M-201.
"""


def test_reference_extractor():
    """Test that all reference types are extracted correctly."""
    print("\n🧪 Testing ReferenceExtractor...")

    extractor = ReferenceExtractor(
        known_sheets=["A-101", "A-102", "S-301", "M-101", "E-101", "A-501", "A-601", "A-302", "S-101", "M-201"]
    )

    refs = extractor.extract_all(DOC_A101)

    print(f"  Found {len(refs)} references:")
    for ref in refs:
        print(f"    [{ref.ref_type:12}] {ref.target_id:15} (sheet={ref.target_sheet or '-'}), conf={ref.confidence:.2f}")

    # Assertions
    sheet_refs = [r for r in refs if r.ref_type == "sheet"]
    detail_refs = [r for r in refs if r.ref_type == "detail"]
    schedule_refs = [r for r in refs if r.ref_type == "schedule"]

    assert len(sheet_refs) >= 3, f"Expected >=3 sheet refs, got {len(sheet_refs)}"
    assert len(detail_refs) >= 1, f"Expected >=1 detail refs, got {len(detail_refs)}"
    assert len(schedule_refs) >= 1, f"Expected >=1 schedule refs, got {len(schedule_refs)}"

    # Check specific expected refs
    target_ids = [r.target_id for r in refs]
    assert "S-301" in target_ids, "Should reference S-301"
    assert "M-101" in target_ids, "Should reference M-101"

    print("  ✅ Reference extraction passed")
    return refs


def test_drawing_index_parser():
    """Test drawing index parsing."""
    print("\n🧪 Testing DrawingIndexParser...")

    parser = DrawingIndexParser()
    index = parser.parse(DRAWING_INDEX_TEXT, project_name_hint="DOWNTOWN OFFICE TOWER")

    print(f"  Project: {index.project_name}")
    print(f"  Sheets: {index.total_sheets}")
    print(f"  Disciplines: {index.discipline_list}")

    assert index.total_sheets == 16, f"Expected 16 sheets, got {index.total_sheets}"
    assert "A" in index.discipline_list
    assert "S" in index.discipline_list
    assert index.is_valid_sheet("A-101")
    assert not index.is_valid_sheet("Z-999")

    sheet = index.get_sheet("S-301")
    assert sheet is not None
    assert sheet.title == "STRUCTURAL DETAILS"

    print("  ✅ Drawing index parsing passed")
    return index


def test_document_graph():
    """Test full graph construction and traversal."""
    print("\n🧪 Testing DocumentGraph...")

    documents = [
        {"id": "doc_a101", "text": DOC_A101, "page_num": 0, "type": "drawing", "filename": "A-101.pdf"},
        {"id": "doc_s301", "text": DOC_S301, "page_num": 0, "type": "drawing", "filename": "S-301.pdf"},
        {"id": "doc_m101", "text": DOC_M101, "page_num": 0, "type": "drawing", "filename": "M-101.pdf"},
    ]

    graph = build_graph_from_documents(
        documents=documents,
        drawing_index_text=DRAWING_INDEX_TEXT,
        project_id="test-downtown-office-tower"
    )

    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  Broken links: {len(graph.broken_links)}")

    # Check that drawing index seeded sheet nodes
    sheet_nodes = [n for n in graph.nodes.values() if n.node_type == "sheet"]
    assert len(sheet_nodes) == 16, f"Expected 16 sheet nodes, got {len(sheet_nodes)}"

    # Check that references created edges
    assert len(graph.edges) > 0, "Should have edges from references"

    # Test graph traversal: from A-101, follow references
    a101_id = "sheet:A-101"
    expanded = graph.expand_context(a101_id, depth=2, max_nodes=10)
    print(f"  Expanded from A-101 (depth=2): {len(expanded)} nodes")
    for node in expanded[:5]:
        print(f"    → {node.id}: {node.label}")

    # Test broken link detection
    broken = graph.get_broken_links()
    print(f"  Broken links: {len(broken)}")
    for bl in broken:
        print(f"    ⚠️  {bl.source_id} → {bl.target_type}:{bl.target_id} (sheet={bl.target_sheet})")

    # Test graph stats
    stats = graph.to_dict()["stats"]
    print(f"  Stats: {stats}")

    # Test serialization roundtrip
    json_str = graph.to_json()
    assert len(json_str) > 1000
    print(f"  JSON size: {len(json_str)} bytes")

    print("  ✅ Document graph construction passed")
    return graph


def test_with_sample_docs():
    """Test with actual project sample documents."""
    print("\n🧪 Testing with real sample documents...")

    sample_dir = Path(__file__).parent.parent.parent.parent / "sample_docs"
    documents = []

    for txt_file in sorted(sample_dir.glob("*.txt")):
        text = txt_file.read_text()
        documents.append({
            "id": txt_file.stem,
            "text": text,
            "page_num": 0,
            "type": "spec" if "SPEC" in txt_file.name.upper() else "drawing",
            "filename": txt_file.name,
        })

    graph = build_graph_from_documents(
        documents=documents,
        project_id="vdc-sample-project"
    )

    print(f"  Documents: {len(documents)}")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  Broken links: {len(graph.broken_links)}")

    # Show what we found
    spec_nodes = [n for n in graph.nodes.values() if n.node_type == "spec_section"]
    print(f"  Spec sections found: {[n.label for n in spec_nodes]}")

    sheet_nodes = [n for n in graph.nodes.values() if n.node_type == "sheet"]
    print(f"  Sheet references found: {[n.label for n in sheet_nodes]}")

    print("  ✅ Sample document test passed")


def run_all_tests():
    print("=" * 60)
    print("MEDHA v2 PHASE 1: DOCUMENT GRAPH ENGINE TESTS")
    print("=" * 60)

    try:
        test_reference_extractor()
        test_drawing_index_parser()
        test_document_graph()
        test_with_sample_docs()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

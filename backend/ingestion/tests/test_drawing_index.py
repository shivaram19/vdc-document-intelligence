"""
Tests for the drawing index parser.
"""

from ingestion.classifier import Discipline
from ingestion.drawing_index import DrawingIndexParser


def test_parse_simple_index():
    text = """
DRAWING INDEX

A-101  GENERAL NOTES AND BUILDING PARAMETERS
S-201  FOUNDATION PLAN
M-301  HVAC MECHANICAL PLAN
E-401  ELECTRICAL POWER PLAN
FP-501 FIRE PROTECTION PLAN
    """
    parser = DrawingIndexParser()
    sheets = parser.parse_text(text)

    assert len(sheets) == 5
    numbers = [s.number for s in sheets]
    assert numbers == ["A-101", "S-201", "M-301", "E-401", "FP-501"]

    assert sheets[0].title == "GENERAL NOTES AND BUILDING PARAMETERS"
    assert sheets[0].discipline == Discipline.ARCHITECTURAL
    assert sheets[2].discipline == Discipline.MECHANICAL
    assert sheets[4].discipline == Discipline.FIRE_PROTECTION


def test_parse_index_with_wrapped_titles():
    text = """
A-201  FIRST FLOOR PLAN
       AND REFLECTED CEILING
S-202  SECOND FLOOR
       FRAMING PLAN
    """
    parser = DrawingIndexParser()
    sheets = parser.parse_text(text)

    assert len(sheets) == 2
    assert sheets[0].number == "A-201"
    assert sheets[0].title == "FIRST FLOOR PLAN AND REFLECTED CEILING"
    assert sheets[1].title == "SECOND FLOOR FRAMING PLAN"


def test_parse_index_with_sheet_prefix():
    text = """
Sheet A-101 General Notes
Sheet M-301 Mechanical Plan
    """
    parser = DrawingIndexParser()
    sheets = parser.parse_text(text)

    assert len(sheets) == 2
    assert sheets[0].number == "A-101"
    assert sheets[1].number == "M-301"


def test_parse_index_with_numbered_rows():
    text = """
1. A-101 General Notes
2. S-201 Foundation Plan
3. M-301 Mechanical Plan
    """
    parser = DrawingIndexParser()
    sheets = parser.parse_text(text)

    assert len(sheets) == 3
    assert sheets[0].number == "A-101"


def test_parse_ignores_non_sheet_lines():
    text = """
PROJECT: Downtown Office Tower
A. OCCUPANCY AND USE
Section 23 00 00 - HVAC General Requirements
A-101  GENERAL NOTES
    """
    parser = DrawingIndexParser()
    sheets = parser.parse_text(text)

    assert len(sheets) == 1
    assert sheets[0].number == "A-101"


def test_extract_header_sheet():
    text = """
UK Design and Construction Standards
A-101 GENERAL NOTES AND BUILDING PARAMETERS
Division 23 | HVAC Page | 1
    """
    parser = DrawingIndexParser()
    sheet = parser._extract_header_sheet(text, page_number=0)

    assert sheet is not None
    assert sheet.number == "A-101"
    assert sheet.title == "GENERAL NOTES AND BUILDING PARAMETERS"
    assert sheet.page_number == 0

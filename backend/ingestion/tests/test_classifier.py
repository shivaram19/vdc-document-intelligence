"""
Tests for the ingestion classifier.
"""

import pytest

from ingestion.classifier import (
    classify_document,
    classify_document_type,
    classify_sheet,
    classify_sheet_by_number,
)
from ingestion.models import Discipline, DocumentType


def test_classify_document_type_pdf():
    assert classify_document_type("drawing.pdf") == DocumentType.PDF
    assert classify_document_type("model.dwg") == DocumentType.DWG
    assert classify_document_type("unknown.xyz") == DocumentType.UNKNOWN


def test_classify_sheet_by_number():
    assert classify_sheet_by_number("A-101") == Discipline.ARCHITECTURAL
    assert classify_sheet_by_number("S-201") == Discipline.STRUCTURAL
    assert classify_sheet_by_number("M-301") == Discipline.MECHANICAL
    assert classify_sheet_by_number("FP-401") == Discipline.FIRE_PROTECTION
    assert classify_sheet_by_number("") is None


def test_classify_sheet_by_title():
    assert classify_sheet(title="Foundation Plan") == Discipline.STRUCTURAL
    assert classify_sheet(title="First Floor Plan") == Discipline.ARCHITECTURAL
    assert classify_sheet(title="HVAC Ductwork Plan") == Discipline.MECHANICAL


def test_classify_document_spec():
    assert classify_document("Division_23_HVAC_Specification.pdf") == Discipline.SPECIFICATION
    assert classify_document("Project_Manual.pdf") == Discipline.SPECIFICATION
    assert classify_document("Geotechnical_Report.pdf") == Discipline.REPORT


def test_classify_document_drawing():
    assert classify_document("A-101_First_Floor_Plan.pdf") == Discipline.ARCHITECTURAL
    assert classify_document("S-201_Foundation_Plan.pdf") == Discipline.STRUCTURAL


def test_classify_document_by_content():
    arch_content = "SHEET A-101 - GENERAL NOTES AND BUILDING PARAMETERS\nArchitectural drawing notes."
    assert classify_document("ARCH_DRAWING_NOTES.txt", content_preview=arch_content) == Discipline.ARCHITECTURAL

    struct_content = "Cast-in-place concrete and rebar structural details."
    assert classify_document("STRUCT_NOTES.txt", content_preview=struct_content) == Discipline.STRUCTURAL

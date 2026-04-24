#!/usr/bin/env python3
"""
Docling integration wrapper for advanced document parsing.
Provides layout-aware text extraction with heading/structure preservation.
Falls back to standard extractors if Docling is unavailable.
"""

import os
import sys
from pathlib import Path

# Docling is installed in venv-docling; add it to path if needed
VENV_SITE = Path(__file__).parent.parent / "venv-docling" / "lib"
if VENV_SITE.exists():
    # Find the site-packages directory inside the venv
    for p in VENV_SITE.rglob("site-packages"):
        if p.is_dir():
            sys.path.insert(0, str(p))
            break

DOCLING_AVAILABLE = False
try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.document import ConversionStatus
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError as e:
    print(f"Docling not available: {e}")


def extract_with_docling(filepath: str) -> str:
    """
    Extract structured text from a document using Docling.
    Returns Markdown-formatted text with headings and structure preserved.
    Falls back to empty string if Docling fails or is not available.
    """
    if not DOCLING_AVAILABLE:
        return ""

    try:
        converter = DocumentConverter()
        result = converter.convert(filepath)

        if result.status == ConversionStatus.SUCCESS:
            # Export as Markdown with structure
            return result.document.export_to_markdown()
        else:
            return ""
    except Exception as e:
        print(f"Docling extraction failed for {filepath}: {e}")
        return ""


def is_docling_available() -> bool:
    return DOCLING_AVAILABLE


if __name__ == "__main__":
    # Quick test
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Docling available: {is_docling_available()}")
        if is_docling_available():
            text = extract_with_docling(path)
            print(f"Extracted {len(text)} characters")
            print(text[:2000])
    else:
        print(f"Docling available: {is_docling_available()}")

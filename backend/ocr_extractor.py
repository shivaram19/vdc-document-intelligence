#!/usr/bin/env python3
"""
OCR fallback for scanned/image-based PDFs.
Uses Tesseract + pdf2image to extract text when standard extractors fail.
"""

import os
from pathlib import Path

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_with_ocr(filepath: str, dpi: int = 200, max_pages: int = 0) -> str:
    """
    Extract text from a PDF using OCR (Tesseract).

    Args:
        filepath: Path to the PDF file.
        dpi: Resolution for rendering PDF pages to images.
        max_pages: Max pages to process (0 = all pages).

    Returns:
        Extracted text as a single string, or empty string on failure.
    """
    if not OCR_AVAILABLE:
        return ""

    try:
        # For large PDFs, limit pages at conversion time (much faster)
        kwargs = {"dpi": dpi, "fmt": "png"}
        if max_pages > 0:
            kwargs["first_page"] = 1
            kwargs["last_page"] = max_pages

        pages = convert_from_path(filepath, **kwargs)

        texts = []
        for i, page in enumerate(pages):
            # Resize large images to keep OCR fast
            max_dim = 1800
            w, h = page.size
            if max(w, h) > max_dim:
                ratio = max_dim / max(w, h)
                page = page.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            text = pytesseract.image_to_string(page)
            if text.strip():
                texts.append(f"--- Page {i + 1} ---\n{text}")

        return "\n\n".join(texts)
    except Exception as e:
        print(f"OCR extraction failed for {filepath}: {e}")
        return ""


def is_scanned_pdf(filepath: str, sample_pages: int = 3, text_threshold: int = 200) -> bool:
    """
    Heuristic: check if a PDF has minimal extractable text (likely scanned/images).

    Args:
        filepath: Path to the PDF.
        sample_pages: Number of pages to sample.
        text_threshold: If total extracted text is below this, treat as scanned.

    Returns:
        True if the PDF appears to be scanned/image-based.
    """
    try:
        # Try pdftotext first (fast)
        import subprocess
        result = subprocess.run(
            ["pdftotext", filepath, "-"],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout.strip()
        if len(text) < text_threshold:
            return True
        return False
    except Exception:
        # If pdftotext fails, assume scanned
        return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"OCR available: {OCR_AVAILABLE}")
        is_scanned = is_scanned_pdf(path)
        print(f"Appears scanned: {is_scanned}")
        if is_scanned and OCR_AVAILABLE:
            text = extract_text_with_ocr(path, max_pages=2)
            print(f"Extracted {len(text)} characters")
            print(text[:2000])
    else:
        print(f"OCR available: {OCR_AVAILABLE}")

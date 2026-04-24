# Librarian (node-e)
## Problem: "I have 10,000 pages of PDFs and no way to search them."

### JTBD
When a new project starts, the VDC manager wants to drop all documents into a folder and have them automatically parsed, chunked, embedded, and indexed — without manual data entry.

### What Librarian Does
1. Watches `inbox/` directory for new files
2. Detects document type from filename (spec, drawing, RFI, submittal)
3. Extracts text: PDF → pdfplumber, DOCX → python-docx, TXT → direct
4. OCR fallback for scanned PDFs (pdf2image + pytesseract)
5. Chunks text semantically (512 chars / 128 overlap)
6. Generates embeddings via `all-mpnet-base-v2`
7. Merges with existing project index
8. Moves processed files to `archive/`

### Research Basis
- [CITE: Li2024] Agent specialization reduces ingestion time by 90% vs. monolithic pipelines.
- [CITE: SBERT2025] Default PyTorch backend triggers JIT compilation on first encode(). Librarian preloads model at startup to avoid query-time blocking.

### Capability
```
can_upload
```

### Success Metric
- Ingestion rate: > 100 pages/minute
- Chunk quality: > 95% semantically complete
- Duplicate prevention: 100% (filename hash check)

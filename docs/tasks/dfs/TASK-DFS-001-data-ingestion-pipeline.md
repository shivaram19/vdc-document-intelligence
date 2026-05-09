# TASK-DFS-001: Construction Document Ingestion Pipeline

**Date:** 2026-05-03  
**Scope:** Depth-first implementation of the data ingestion pipeline for construction documents  
**Personas:** Infrastructure-First SRE, Distributed Systems Architect, Diagnostic Problem-Solver  
**Status:** Pending BFS Completion

---

## 1. Objective

Build a robust, observable pipeline that ingests construction documents from multiple sources, parses them into structured text, and prepares them for chunking and embedding.

## 2. Input Sources

| Source | Format | Frequency | Volume |
|--------|--------|-----------|--------|
| User upload (frontend) | PDF, DOCX, TXT | Real-time | 1–50 docs/project |
| Web scraper (UpCodes, etc.) | HTML → Markdown | Daily batch | 100–1K pages/day |
| FOIA/API (Dubai Municipality) | PDF | Weekly batch | 50–500 docs/week |
| Partner VDC agency | PDF, DWF | Weekly sync | 10–100 docs/week |

## 3. Pipeline Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  Source Queue   │────▶│   Parser     │────▶│  Extractor  │────▶│  Validator  │
│  (S3 / Local)   │     │ (Docling/    │     │  (Tables,   │     │  (Quality   │
│                 │     │  pdfplumber) │     │   Figures,  │     │   Gates)    │
└─────────────────┘     └──────────────┘     │   Metadata) │     └──────┬──────┘
                                              └─────────────┘            │
                                                                         ▼
                                              ┌──────────────────────────────────┐
                                              │     Structured Document Store     │
                                              │  (text, tables, metadata, links)  │
                                              └──────────────────────────────────┘
```

## 4. Component Specifications

### 4.1 Parser (Docling Integration)

**Current state:** Medha has basic `docling_parser.py` integration.

**Target state:**
```python
class ConstructionDocumentParser:
    """
    SOLID: SRP — only parsing. No embedding, no chunking.
    """
    def parse(self, file_path: Path) -> ParsedDocument:
        """
        Returns:
            - full_text: str (preserving heading hierarchy)
            - tables: List[Table] (with row/col structure)
            - figures: List[Figure] (captions, bounding boxes)
            - metadata: DocumentMetadata (title, author, date, divisions)
            - outline: List[Heading] (h1, h2, h3 with page numbers)
        """
```

**Requirements:**
- Parse PDF with text, tables, and figure captions
- Preserve heading hierarchy (Division → Section → Subsection)
- Extract table-of-contents / outline
- Handle scanned PDFs (OCR fallback via Tesseract)
- Handle DWG/DWF metadata (if available)

### 4.2 Extractor

```python
class DocumentExtractor:
    """
    Extract structured information from parsed documents.
    """
    def extract_references(self, doc: ParsedDocument) -> List[CrossReference]:
        """Find spec-to-drawing, spec-to-code references."""
        
    def extract_tables(self, doc: ParsedDocument) -> List[SpecificationTable]:
        """Extract requirement tables (materials, dimensions, tolerances)."""
        
    def extract_drawing_index(self, doc: ParsedDocument) -> Optional[DrawingIndex]:
        """Parse drawing list / sheet index."""
```

### 4.3 Validator (Quality Gates)

| Gate | Check | Rejection Criteria |
|------|-------|-------------------|
| QG-1 | Parse success | Empty text extraction |
| QG-2 | Text quality | <50% alphanumeric characters |
| QG-3 | Structure detection | No headings found |
| QG-4 | Table integrity | Tables with <2 rows or <2 columns |
| QG-5 | Language | Non-English without Arabic flag |
| QG-6 | Duplicate | SHA-256 match with existing doc |

## 5. Observability

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| parse_success_rate | Gauge | <95% |
| parse_latency_p99 | Histogram | >30s |
| docs_queued | Counter | >1K backlog |
| validation_reject_rate | Gauge | >20% |
| ocr_fallback_rate | Gauge | >10% |

## 6. Error Handling

| Failure Mode | Strategy | Retry |
|--------------|----------|-------|
| Parse crash | Quarantine file; alert operator | Manual |
| OCR required | Queue for OCR worker | 3× automatic |
| Malformed PDF | Extract text via pdftotext fallback | 1× |
| Timeout | Kill worker; requeue with priority -1 | 2× |

## 7. Implementation Tasks

- [ ] **Subtask 1:** Upgrade Docling integration to v2.x with table extraction
- [ ] **Subtask 2:** Implement `ConstructionDocumentParser` class
- [ ] **Subtask 3:** Implement `DocumentExtractor` with regex-based reference detection
- [ ] **Subtask 4:** Implement quality gates with metrics emission
- [ ] **Subtask 5:** Add OCR fallback for scanned PDFs
- [ ] **Subtask 6:** Write unit tests (pytest) for all parsers
- [ ] **Subtask 7:** Add OpenTelemetry spans for pipeline observability

## 8. Acceptance Criteria

1. Successfully parses 95% of uploaded construction PDFs
2. Table extraction accuracy >80% (measured against human-labeled sample)
3. Cross-reference detection recall >70%
4. Parse latency P95 <10s for 50-page document
5. Zero data loss on parse failure (file quarantined, not deleted)

---

## References

[^1]: Docling Technical Documentation. IBM Research. https://github.com/DS4SD/docling
[^2]: pdfplumber Documentation. https://github.com/jsvine/pdfplumber
[^3]: Construction Document Parsing with Deep Learning. Bansal et al. 2023.

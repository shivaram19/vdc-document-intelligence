# ADR-010: Deterministic Drawing-Index Parser with Per-Page Fallback

## Status
Accepted

## Context
Medha ingests construction PDFs that may be either:
1. Drawing sets with an explicit drawing index (sheet number + title).
2. Single-document specifications, standards, or reports with no index.
3. Mixed sets where sheets can be identified only from per-page headers.

Initial sheet extraction used a single regex on the first few pages and fell back to guessing a sheet number from the document body. This produced false sheet records for specifications (e.g., extracting `HPR-2` from a valve schedule) and missed real drawing indexes with wrapped titles or numbered rows.

## Decision
Implement a deterministic `DrawingIndexParser` that:
1. Matches sheet numbers using the North American / AIA Uniform Drawing System convention (e.g., `A-101`, `S-201`, `M-301`, `FP-501`).
2. Tolerates common index formatting: leading `Sheet`, numbered rows, dashes/spaces in numbers, and wrapped titles.
3. Returns explicit index sheets first; if no index is found, falls back to per-page header extraction.
4. Treats the whole PDF as a single document sheet (`DOC`) only when neither an index nor per-page headers are found.

Sheet discipline classification reuses the deterministic classifier from ADR-009 by applying sheet-number prefixes, title keywords, and filename keywords in order.

## Consequences

### Positive
- No LLM required for index parsing, keeping ingestion fast and reproducible.
- False sheet records from spec body text are eliminated.
- Wrapped/multi-line index titles are merged into coherent sheet records.

### Negative
- Highly irregular sheet numbering (custom prefixes, non-standard delimiters) may require regex updates.
- Per-page header extraction relies on sheet numbers appearing near the top of a page; title-only headers are not yet parsed.

## Alternatives Considered
- **LLM-based extraction:** Rejected because it is slower, non-deterministic, and harder to audit for a core ingestion step.
- **Strict table extraction with pdfplumber:** Rejected because drawing indexes vary in column layout and are often plain text rather than true tables.

## References
- [CITE: NCS-US-2024] National CAD Standard, United States National CAD Standard (NCS) V6, drawing sheet numbering conventions.
- [CITE: AIA-UDS-2024] AIA Uniform Drawing System, sheet identification and drawing set organization.

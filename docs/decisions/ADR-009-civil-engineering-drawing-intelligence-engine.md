# ADR-009: Civil Engineering Drawing Intelligence Engine

**Status:** Proposed
**Date:** 2026-05-03
**Decision Owner:** Medha Product / Engineering

## Context

VDC engineers spend most of their time moving between documents: drawings, specifications, addenda, RFIs, geotechnical reports, and submittals. The documents are the central actors. The current Medha prototype focuses on text-level contradiction detection in specifications and logs. To deliver value in preconstruction coordination, we need an engine that ingests **drawings as first-class citizens** and interprets them through the lens of **civil engineering** — not generic computer vision, not architectural drafting, but the specific entities, relationships, and checks that civil/VDC engineers perform.

[CITE: DesignQA2025] MLLM benchmarks on engineering documentation show that state-of-the-art models still struggle to interpret engineering drawings and cross-reference them with textual requirements. This is the gap Medha targets.

[CITE: DoclingPyData2025] Docling provides a foundation for rich document parsing (tables, figures, layout) but does not include civil-engineering-specific semantics.

## Decision

Build a **Civil Engineering Drawing Intelligence Engine** (CEDIE) as a domain-specific layer on top of Medha’s existing document pipeline. The engine will:

1. Ingest drawings in PDF, DWG, DXF, RVT, IFC, and raster scan formats.
2. Extract civil-engineering-relevant entities, annotations, dimensions, and relationships.
3. Cross-reference drawing content with specifications, geotechnical reports, and addenda.
4. Detect contradictions and gaps specific to civil engineering.
5. Output marked-up reports, RFI drafts, and structured data for downstream coordination.

## Civil Engineering Dimensions the Engine Must Understand

Civil engineering drawings are not arbitrary images. They encode physical reality through a set of standard representations:

| Dimension | What Drawings Express | Examples |
|---|---|---|
| **Verticality** | Elevations, grades, depths, setbacks | Top of foundation, finish floor elevation, invert elevations |
| **Horizontality** | Plans, alignments, stationing, offsets | Grid lines, property lines, roadway centerlines, utility runs |
| **Sections** | Cut-through detail | Foundation sections, retaining wall sections, road cross-sections |
| **Materiality** | What something is made of | Concrete class, rebar size, pipe material, soil type |
| **Quantities** | Counts, lengths, areas, volumes | Earthwork volumes, reinforcement tonnage, pipe lengths |
| **Load / force** | Structural intent | Bearing capacity, pile loads, slab thickness, fill compaction |
| **Hydrology / drainage** | Water movement | Catch basins, culverts, slope arrows, drainage patterns |
| **Geotechnical context** | Ground conditions | Boring logs, soil strata, groundwater, bearing strata |
| **Utility context** | Existing and proposed services | Water, sewer, storm, electrical, telecom conflicts |
| **Regulatory context** | Codes and standards | Setbacks, easements, ADA slopes, fire access |

The engine must interpret a drawing not as a picture, but as a **spatial-material-quantitative model** expressed in 2D/3D graphics and annotations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Ingestion                        │
│  PDF │ DWG/DXF │ RVT │ IFC │ Scans │ Point Cloud (future)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Civil-Aware Parsing & Extraction                │
│  • Sheet type classifier (plan, section, detail, schedule)   │
│  • OCR + symbol recognition (section cuts, north arrow,      │
│    datum markers, grid bubbles)                              │
│  • Entity extraction (walls, footings, columns, pipes,       │
│    manholes, contours, spot elevations)                      │
│  • Annotation extraction (dimensions, notes, callouts,       │
│    revisions, abbreviations)                                 │
│  • Table/schedule extraction (door schedules, rebar          │
│    schedules, utility schedules)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Civil Knowledge Graph Construction              │
│  • Link entities across sheets (detail callout ↔ detail)     │
│  • Link drawing entities to spec sections                    │
│  • Link elevations to grids to sections                      │
│  • Link materials to schedules and specs                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Civil Engineering Reasoning Layer               │
│  • Dimensional consistency checks                            │
│  • Drawing-to-spec material checks                           │
│  • Drawing-to-geotechnical condition checks                  │
│  • Cross-discipline spatial conflict detection               │
│  • Code/regulatory compliance checks                         │
│  • Missing information / incompleteness checks               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output & Action Layer                     │
│  • Marked-up PDFs with issue pins and citations              │
│  • Structured issue list with severity and source links      │
│  • RFI drafts with referenced drawing/sheet/spec             │
│  • Coordination report exports                               │
│  • API / MCP tools for downstream agents                     │
└─────────────────────────────────────────────────────────────┘
```

## Civil-Engineering-Specific Contradiction Types

The engine must detect contradictions that matter to civil/VDC engineers:

1. **Elevation contradictions**
   - Spot elevation on plan does not match section.
   - Finish floor elevation on architectural plan disagrees with structural slab elevation.
   - Invert elevation on storm plan conflicts with top-of-structure.

2. **Material contradictions**
   - Concrete class in drawing note differs from spec section.
   - Pipe material on plan differs from utility schedule.
   - Reinforcement size in section differs from rebar schedule.

3. **Dimensional contradictions**
   - Overall building dimension on plan does not match foundation plan.
   - Grid spacing in structural drawing differs from architectural.
   - Wall thickness in section differs from plan.

4. **Geotechnical contradictions**
   - Foundation bearing elevation shown above known bearing stratum from geotech report.
   - Excavation depth conflicts with groundwater table note.
   - Slope requirement in drawing conflicts with soil report.

5. **Drainage contradictions**
   - Slope arrows imply water flowing toward building.
   - Catch basin invert elevation higher than surrounding grade.
   - Storm pipe slope insufficient per code.

6. **Utility conflicts**
   - Proposed water main crosses proposed sewer at same invert.
   - Utility trench conflicts with foundation.
   - Clearance between utilities below minimum code requirement.

7. **Regulatory contradictions**
   - Building footprint encroaches setback per site plan dimensions.
   - Ramp slope exceeds ADA / local code maximum.
   - Fire access lane width below code minimum.

8. **Revision/addenda contradictions**
   - Addendum changes column location but structural plan is not updated.
   - New detail added does not match existing sheet reference.

## Data Model

```python
class CivilEntity:
    id: str
    type: CivilEntityType  # WALL, COLUMN, FOOTING, PIPE, MANHOLE, CONTOUR, etc.
    sheet_id: str
    bounding_box: BBox
    geometry: Geometry  # 2D or 3D representation
    annotations: List[Annotation]
    material: Optional[str]
    dimensions: List[Dimension]
    relationships: List[Relationship]
    source_citation: Citation

class Relationship:
    type: RelationshipType  # CONNECTED_TO, SUPPORTED_BY, CONTAINS, CALLS_OUT, CONTRADICTS
    source_id: str
    target_id: str
    confidence: float

class Contradiction:
    id: str
    type: ContradictionType
    severity: Severity
    entities: List[str]
    description: str
    citations: List[Citation]
    proposed_rfi: Optional[str]
```

## Implementation Phases

### Phase 1: Foundation (MVP)
- PDF drawing ingestion with layout and OCR.
- Sheet type classification.
- Basic entity extraction: grids, spot elevations, dimensions, text annotations.
- Link drawing annotations to spec sections via text matching.
- Detect drawing-to-spec material contradictions.

### Phase 2: Cross-sheet reasoning
- Detail callout resolution (link callout to detail sheet).
- Cross-sheet elevation consistency checks.
- Schedule extraction and cross-validation.

### Phase 3: Civil-specific reasoning
- Geotechnical report integration.
- Drainage slope and utility conflict checks.
- Regulatory compliance rule engine.

### Phase 4: Agentic coordination
- MCP tools exposing CEDIE operations to agents.
- Agent-driven RFI drafting and issue triage.
- Integration with Plane / ACC / Procore workflows.

## Integration with Existing Medha Stack

| Existing Component | How CEDIE Uses It |
|---|---|
| `backend/docling_parser.py` | Rich PDF parsing, table extraction, layout preservation |
| `backend/chunkers/` | Section-aware chunking for specs and reports |
| `backend/extractors/` | Extend with civil entity extraction models |
| `backend/detectors/` | Add civil contradiction detectors |
| `backend/linkers/` | Build drawing-to-spec and drawing-to-drawing links |
| `backend/stores/` | Store civil knowledge graph and embeddings |
| `mcp-servers/plane-mcp/` | Push detected issues into Plane as tasks/RFIs |

## Consequences

### Positive
- Differentiates Medha from generic document-QA tools.
- Directly serves VDC engineers’ core fear: missing drawing-level contradictions.
- Creates a structured civil knowledge graph that becomes a defensible data asset.
- Enables future agentic workflows (MCP tools, RFI drafting, coordination reports).

### Negative / Risks
- Higher engineering complexity than text-only contradiction detection.
- Requires domain-specific training data or annotation effort.
- Parsing DWG/DXF/IFC reliably is non-trivial; may require third-party libraries or converters.
- False positives in spatial reasoning can erode trust quickly.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Use generic MLLM (GPT-4V, Claude) on full drawing sets | Too expensive, no civil semantics, hard to cite exact sources, high hallucination risk on engineering details. |
| Build an architectural drawing engine first | Architectural contradictions are less costly than civil/structural contradictions; civil is where rework is most expensive. |
| Outsource drawing parsing to Autodesk/ACC APIs | Locks Medha into a proprietary ecosystem; conflicts with self-hosting and GCC market needs. |
| Start with 3D BIM clash detection | Navisworks/ACC already dominate this; 2D drawing intelligence is underserved. |

## References

- [CITE: DesignQA2025] *DesignQA: A Multimodal Benchmark for Evaluating Large Language Models’ Understanding of Engineering Documentation.* ASME J. Comput. Inf. Sci. Eng., 2025.
- [CITE: DoclingPyData2025] PyData Virginia 2025. *Building Rich RAG Systems with Docling.*
- [CITE: MCP4IFC2025] Nithyanantham et al. *MCP4IFC: IFC-Based Building Design using Large Language Models.* arXiv:2511.05533.
- [CITE: AECMag2026] AEC Magazine. *The agentic future of BIM.* 2026-03-07.
- [CITE: OpenContracts2026] Open-Source-Legal/OpenContracts. Open-source document intelligence platform with MCP server.

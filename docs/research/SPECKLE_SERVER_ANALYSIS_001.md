# Speckle Server Analysis

**Date:** 2026-05-03
**Repository:** https://github.com/specklesystems/speckle-server
**License:** Apache-2.0 (core)
**Purpose:** Open-source AEC data hub and interoperability platform.

---

## What Speckle is

Speckle positions itself as the **first AEC data hub** — often described as **“Git for BIM.”** It enables version-controlled exchange of building data between disconnected AEC software tools.

### Core components

| Component | Repository | Role |
|---|---|---|
| **speckle-server** | `specklesystems/speckle-server` | Web platform, API, auth, project management |
| **speckle-sharp-connectors** | `specklesystems/speckle-sharp-connectors` | .NET desktop connectors (Revit, Rhino, Grasshopper, etc.) |
| **speckle-sharp-sdk** | `specklesystems/speckle-sharp-sdk` | .NET SDK and object model |
| **specklepy** | `specklesystems/specklepy` | Python SDK for server and object interaction |
| **Connectors** | Multiple repos | Blender, SketchUp, Excel, Unity, Unreal, QGIS, PowerBI |

### Key capabilities

- **Data streaming** between design tools without file exports/imports
- **Versioning / branching** of model data (commits, streams, branches)
- **Web-based viewer** and project management
- **GraphQL and REST APIs**
- **Python and .NET SDKs**
- **Self-hostable** server deployment via Docker
- **Open-source** under Apache-2.0

---

## Relevance to Medha

### 1. Speckle solves the interoperability problem Medha depends on
Medha reads documents and drawings from many sources. Speckle provides a structured, versioned pipeline for receiving **model data** (geometry + parameters) from Revit, Rhino, Grasshopper, Blender, and other tools.

> **Implication:** Medha could consume Speckle commits as a model input channel, supplementing PDF/DWG/DXF ingestion.

### 2. Speckle is the closest existing “GitHub for construction”
PRD-001 and PRD-002 identify the lack of a unified construction platform as a core pain. Speckle is the leading open-source attempt to fill that gap, but it is **model-centric**, not **document-centric**.

> **Implication:** Medha can complement Speckle by adding document intelligence (drawings, specs, RFIs) on top of Speckle’s model data layer.

### 3. Speckle’s versioning model is instructive
Speckle uses streams, branches, and commits. This maps well to construction document versioning:
- **Stream** = project
- **Branch** = discipline or design option
- **Commit** = drawing/model revision

> **Implication:** Medha’s document versioning could adopt similar semantics for consistency with modern AEC tooling.

### 4. Speckle could receive Medha outputs
Medha produces structured findings (contradictions, RFIs, issues). These could be published back to Speckle as:
- Comment threads on model elements
- Issue objects linked to geometry
- Data streams consumed by downstream tools

> **Implication:** Speckle could become an integration target for Medha-generated coordination issues.

### 5. Deployment alignment
Speckle is self-hostable via Docker. Medha’s target market (GCC, enterprise) values data sovereignty. Both can run in the same self-hosted environment.

> **Implication:** Medha + Speckle can be sold as a joint self-hosted AEC intelligence stack.

---

## What Speckle does not do (Medha’s opportunity)

| Speckle capability gap | Medha fills it |
|---|---|
| No native document intelligence | PDF/spec/drawing contradiction detection |
| No RFI drafting workflow | Auto-generated RFIs with citations |
| No civil-engineering reasoning layer | Civil-aware extraction and checks |
| No preconstruction risk scoring | Document complexity and contradiction risk |
| No spec-to-drawing cross-reference | Spec/drawing/submittal alignment |

---

## Integration scenarios

### Scenario A: Speckle as model input to Medha
1. Design team publishes Revit model to Speckle.
2. Medha queries Speckle API for model geometry and parameters.
3. Medha cross-references model data with PDF drawings and specs.
4. Medha flags contradictions between model and documents.

### Scenario B: Medha issues feed Speckle
1. Medha detects a contradiction involving a specific structural element.
2. Medha creates a Speckle issue/comment linked to that element’s ID.
3. Structural engineer sees the issue inside Revit via Speckle connector.

### Scenario C: Unified self-hosted deployment
1. Client deploys Speckle Server + Medha on the same infrastructure.
2. VDC agency uses Speckle for model exchange and Medha for document QA.
3. Both share authentication, project structure, and audit logs.

---

## Technical considerations

| Aspect | Detail |
|---|---|
| **Stack** | Node.js / Vue.js frontend, .NET/Python SDKs, PostgreSQL, Redis, MinIO |
| **APIs** | GraphQL + REST |
| **Auth** | Server-managed accounts, SSO support |
| **Deployment** | Docker Compose, Kubernetes Helm charts |
| **Extensibility** | SDKs, webhooks, custom connectors |
| **Licensing** | Apache-2.0 core; some modules may differ |

---

## Strategic recommendation

Speckle is **not a competitor** to Medha. It is a **complementary infrastructure layer**. Medha should:

1. **Evaluate Speckle as a model-data ingestion channel** alongside PDF/DWG/IFC.
2. **Design Medha outputs to be publishable to Speckle** as linked issues/comments.
3. **Consider joint self-hosted deployment** for enterprise/GCC clients.
4. **Avoid rebuilding Speckle’s interoperability layer** — focus on document intelligence.

---

## Open questions

1. Does Speckle’s object model support the civil-engineering entities Medha needs (grids, elevations, utilities, sections)?
2. How mature is Speckle’s Python SDK for server-side automation?
3. What is the performance of Speckle commits on large construction models?
4. Does Speckle support on-premise/air-gapped deployments required by some GCC clients?
5. Could Medha contribute a document-intelligence connector back to the Speckle ecosystem?

---

## References

- [CITE: SpeckleServer] https://github.com/specklesystems/speckle-server
- [CITE: SpeckleDocs] https://speckle.guide/
- [CITE: PRD-002] `docs/tasks/prd/PRD-002-vdc-agency-workflow-product-requirements.md`
- [CITE: ADR-009] `docs/decisions/ADR-009-civil-engineering-drawing-intelligence-engine.md`

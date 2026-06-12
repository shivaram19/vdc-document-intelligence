# Deep Research Brief: Ontologies, Knowledge Graphs & Semantic Web for BIM/VDC/Construction

## 1. Construction & BIM Ontologies — The Landscape

A mature ecosystem of ontologies exists for the built environment, spanning design, construction, operations, and cross-domain interoperability:

| Ontology | Purpose & Scope | Alignment |
|---|---|---|
| **IFC Schema** ([ISO 16739-1:2024](https://www.iso.org/standard/84123.html)) | The foundational open data schema for BIM exchange; defines geometry, topology, processes, resources, actors | Express → ifcOWL |
| **ifcOWL** (Pauwels & Terkaj) | OWL encoding of the IFC schema; ~1,230 classes, 1,578 relations; enables RDF graph construction from IFC | BOT, Building Element, bSDD |
| **bSDD** ([buildingSMART Data Dictionary](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)) | Controlled vocabulary service for properties/attributes not in IFC; taxonomy + multilingual definitions | IFC, IDS |
| **BOT** — Building Topology Ontology (Rasmussen et al., 2017/2021) | Lightweight core topology: Site, Building, Storey, Space, Element; designed for web-native linked data | BRICK, SAREF4BLDG, ifcOWL |
| **BRICK Schema** | Semantic ontology for building operations, BAS, HVAC, sensor metadata; widely used in smart buildings | BOT, SAREF, Haystack |
| **SAREF / SAREF4BLDG** (ETSI) | Smart Appliances Reference Ontology; extends to buildings for IoT/device interoperability | BOT, BRICK |
| **OPM** — Ontology for Property Management (Rasmussen et al., 2018) | Properties, states, time-dependent observations | BOT, SEAS |
| **BPO** — Building Product Ontology (Wagner et al., 2019) | Manufactured products/instances | Schema.org, SEAS |
| **DOT** — Damage & Defect Ontology (Hamdan & Bonduel, 2019) | Construction-type damages (buildings, bridges) | Concrete Damage Ontology |
| **OntoBREP** | CAD data and geometric constraints as semantic robot task descriptions | Product models, ROS |
| **TUBES** (Pauen et al., 2024) | Integrated representation of technical systems (MEP) with BIM + linked data | IFC, BOT |
| **BIRS** (Karimi et al., 2021) | Building Information Robotic System — bridges IFC/CityGML to IEEE 1872-2015 (CORA) and IEEE 1873-2015 (MDR) for robot navigation | BIM-GIS-ROS |
| **UNOCS** — Unified Ontology for Construction Safety | Hazard taxonomy, controls, tasks for safety knowledge graphs | — |
| **BIMOnto / IproK** (Kone et al., 2025) | Bidirectional workflow ontology integrating BIM with schedule, cost, resource (4D/5D) data | IFC, SPARQL |

**Key insight:** The field is moving from monolithic ifcOWL (too heavy for web use) toward modular, lightweight ontologies (BOT, PROPS, OPM, BPO) that can be composed for specific use cases while maintaining alignment to IFC via the Linked Building Data (LBD) stack.

---

## 2. State of Semantic BIM

**Semantic BIM** = converting geometric/parametric BIM models into machine-interpretable knowledge graphs where entities, relationships, and constraints are explicitly defined.

**Technical approaches:**
- **IFC → RDF conversion:** Tools like `IFCtoRDF`, `IFCtoLBD`, and `IFC-LBD` parse IFC files and emit Turtle/RDF graphs using ifcOWL or lightweight LBD ontologies.
- **ABox auto-generation:** Python pipelines using `IfcOpenShell` + `rdflib` traverse IFC instances top-down (IfcProject → Site → Building → Storey → Space → Element) and populate ontology individuals with GUID-based URIs.
- **Semantic enrichment:** Geometric relation checking (adjacency, containment, connectivity) is used to infer topological relationships not explicitly stated in IFC, then injected into the graph.
- **Bidirectional workflows:** Emerging research (Kone et al., 2025) demonstrates round-tripping: IFC → ontology (for reasoning) → enriched IFC (native entities like IfcTask, IfcCostItem written back via ifcopenshell).

**State:** Semantic BIM is transitioning from research prototype to production pipeline, but challenges remain around geometry-to-semantics mapping, handling large models, and maintaining synchronization between native BIM files and derived graphs.

---

## 3. Knowledge Graphs in Construction — Who Is Building Them?

| Project / Paper | What They Built | Technology |
|---|---|---|
| **BEKG** — Built Environment Knowledge Graph (Yang et al., 2022) | Cross-domain KG integrating BIM, IoT, energy, FM | RDF/OWL |
| **SafetyGraph** (Speiser, DTU, 2024–2025) | Worker-centric path planning + hazard KG for construction safety; LLM-generated SPARQL inserts | Neo4j / RDF + SHACL validation |
| **BIM-based semantic enrichment & KG generation** (Lilis et al., *Automation in Construction*, 2025) | Automated KG generation via geometric relation checking | Neo4j / RDF |
| **Bridge Maintenance KG** (Zhang et al., 2023) | KG for bridge deterioration + document analytics | Neo4j |
| **Prefabricated Construction Innovation KG** (Dou et al., 2025) | Patent-data KG for PC technology trends | Neo4j + text mining |
| **Notre-Dame restoration KG** (Gros et al., 2024) | Integrating survey data, simulations, and heritage diagnostics | RDF KG |
| **Deconstruction planning KG** (Allam & Nik-Bakht, 2025) | IFC + KG for automated deconstruction planning | RDF |

**Industry/commercial:** [Neo4j has explicit case studies on BIM-to-graph conversion](https://blog.iaac.net/bimconverse-graphrag-for-ifc-natural-language-queries/). Companies like **Altersquare** and **Plannerly** are positioning knowledge graphs as the solution to "BIM data chaos."

---

## 4. LLMs / SLMs Interacting with Construction Ontologies

Multiple architectural patterns have emerged (2024–2026):

### A. RAG over Ontologies
- **LBD RAG systems** (Kirner et al., RWTH Aachen, 2025): Local LLMs (Llama 3.1, Mistral) retrieve linked building data via prebuilt SPARQL queries or vector embeddings over RDF stores. A web chat interface embeds a 3D viewer + query result table.
- **[GraphRAG on Neo4j](https://blog.iaac.net/bimconverse-graphrag-for-ifc-natural-language-queries/)**: Combines vector similarity search, full-text index, and Cypher graph queries for multimodal retrieval.

### B. Natural Language → SPARQL / IFC Query
- **NLQ2SPARQL-RAGFT**: RAG + fine-tuning approach to address semantic inaccuracies and structural inconsistencies in LLM-generated SPARQL.
- **BIMCoder** (Liu & Chen, 2025): Fusion framework translating NL to IFCQL/JSON structured queries. Uses ERNIE 3.0 as a wrapper + fine-tuned SQLCoder (Mistral) as expert model + validator.
- **Hellin et al. (2025)** / **EC3 paper**: LLM-as-judge agentic workflow where Chain-of-Thought selects tools and ReAct agent executes Python functions on IFC; 80% accuracy, 95% on direct-retrieval queries.

### C. LLM-Powered Semantic Enrichment
- **Höltgen et al. (2025)**: LLMs auto-convert relational construction data into RDF semantic graphs, streamlining ontology mapping.
- **Forth & Borrmann (2024)**: Semantic enrichment for BIM-based energy simulations using semantic textual similarity + fine-tuning multilingual LLMs.
- **Guo et al. (2025)** — ARCBIM: Multiple specialized LLMs + alignment-refinement coder for NL → executable BIM database code.

### D. Ontology-Guided LLM Code Generation
- **Speiser (DTU PhD, 2025)**: "Ontology Agent" generates SPARQL INSERT queries for hazards/controls from NL, validated by SHACL shapes.
- **Karmakar & Delhi (2025)**: Hybrid ML + rule-based semantic BIM enrichment for automated tenement compliance checking.

---

## 5. MCP4IFC — Model Context Protocol for IFC

**Paper:** *"[MCP4IFC: IFC-Based Building Design Using Large Language Models](https://arxiv.org/abs/2511.05533)"* — Nithyanantham, Sesterhenn, Nedungadi, et al. (University of Rostock / TU Clausthal, Oct 2025). arXiv:2511.05533.

**What it is:** The first scientifically documented MCP server framework for BIM. It exposes 50+ BIM tools via the Model Context Protocol (MCP), allowing any MCP-compatible LLM client to:
- **Query** IFC models (scene querying)
- **Create / Edit** IFC elements (walls, slabs, spaces, etc.)
- **Generate code dynamically** via In-Context Learning (ICL) + RAG over IfcOpenShell documentation

**Architecture:** AI Client ↔ MCP Server (Python/JSON-RPC) ↔ Blender add-on (Bonsai + IfcOpenShell).

**Significance:** MCP4IFC decouples the LLM from the BIM backend. It operates directly on IFC ([ISO 16739-1:2024](https://www.iso.org/standard/84123.html)), avoiding proprietary API lock-in. It is the foundational reference for a modular, backend-agnostic agentic BIM interaction layer. A follow-up paper (Jan 2026) proposes a **modular reference architecture for MCP servers** generalizing this approach.

---

## 6. Text2BIM — LLM-Generated BIM from Text

**Paper:** *"[Text2BIM: Generating Building Models Using a Large Language Model-based Multi-Agent Framework](https://arxiv.org/abs/2408.08054)"* — Du et al. (Nemetschek/Vectorworks, 2024). arXiv:2408.08054.

**What it does:** Converts natural language descriptions into **native, semantically rich BIM models** (not just geometry) with:
- External envelopes + internal layouts
- Stories, spaces, materials
- Semantic information

**Architecture (4 agents):**
1. **Instruction Enhancer** → refines user intent
2. **Architect** → develops textual building design
3. **Programmer** → writes imperative API code (Vectorworks API)
4. **Reviewer** → code optimization + conflict resolution

**Innovation:** Domain-specific **rule-based model checker** provides feedback loops so LLMs iteratively resolve architectural/structural conflicts. Demonstrated "modeling-by-chatting" inside Vectorworks.

**Related work:** NADIA, Text-to-Layout (Revit API), AutoGen-based Revit agents (Dong et al., 2025), BIMgent (GUI automation).

---

## 7. Graph Databases Used in Construction

| Type | Technology | Use Cases in Construction |
|---|---|---|
| **Property Graph (LPG)** | **[Neo4j](https://neo4j.com/)** | BIM topology analysis, indoor navigation, element attribute querying, facilities management. Faster queries and smaller graphs than RDF for many BIM use cases. |
| **RDF Triplestore** | **Apache Jena Fuseki**, **GraphDB**, **Virtuoso** | Linked Building Data, SPARQL querying, OWL reasoning, semantic compliance checking, IFCtoRDF pipelines |
| **Hybrid** | Neo4j with RDF import/export | Interoperability between LPG analytics and W3C semantic web stacks |

**Notable finding:** Donkers & Yang note that LPGs (Neo4j) result in smaller, faster-to-query graphs for BIM data compared to RDF triplestores, while RDF stores excel at semantic reasoning and cross-dataset linkages. Many recent projects (Lilis et al., 2025; urban digital twin platforms) use **[Neo4j for semantic data](https://blog.iaac.net/bimconverse-graphrag-for-ifc-natural-language-queries/)** paired with Cesium/3D Tiles for geometry.

---

## 8. Linked Data & Semantic Web in Construction 4.0

**Construction 4.0** = the convergence of BIM, IoT, AI, robotics, and digital twins. Semantic Web technologies provide the interoperability backbone:

- **Asset Administration Shell (AAS)** + **ICDD** (Information Container for Linked Document Delivery): Modular semantic digital twin architectures use AAS submodels linked via RDF/ontologies. Demonstrated for precast concrete production with real-time sensor integration (2025).
- **BIM + IoT + DT integration:** Ontologies bridge static BIM geometry with dynamic IoT streams. BOT/BRICK/SAREF/SSN/SOSA form the semantic layer.
- **Federated data models:** Merino et al. (2023) propose reference data lake architectures where BIM, BAS, and IoT ontologies are federated rather than centralized.
- **Trajectory:** Bibliometric analysis shows research shifted from foundational BIM/ontology (2019–2020) → operational digital twins (2020–2022) → advanced automation via knowledge graphs (2022–present).

---

## 9. Cross-Domain Interoperability: VDC ↔ 3D Reconstruction ↔ Robotics

Ontologies are emerging as the **translation layer** between construction data and robotic/3D vision systems:

| Bridge | Contribution |
|---|---|
| **BIRS Ontology** (Karimi, Iordanova, St-Onge, 2021) | Bridges IFC/CityGML to **IEEE 1872-2015 (CORA)** and **IEEE 1873-2015 (MDR)**. Enables ROS navigation nodes to consume semantic topological maps from BIM. Validated on autonomous UGV for progress monitoring. |
| **OntoBREP / TUBES** | Links geometric constraints in CAD/BIM to semantic robot task descriptions. |
| **Pixels-to-Graph** (Longo et al., 2025) | Real-time integration of BIM and scene graphs for semantic-geometric human-robot understanding. |
| **Semantic 3D Reconstruction datasets** (Wong et al., 2024) | Image datasets for building component segmentation oriented toward semantic 3D reconstruction, feeding into BIM-enriched graphs. |
| **BIM ↔ GIS ↔ Robot** | SPARQL queries over unified graphs enable collision detection, wayfinding, and sensor expectation modeling for drones/UGVs on site. |

**Vision:** A unified ontology stack where:
- **VDC** (design intent) is expressed in BOT/ifcOWL
- **3D reconstruction** (as-built reality) is aligned via semantic segmentation ontologies
- **Robotics** consumes both via CORA/MDR-aligned middleware

---

## 10. IDS — Information Delivery Specifications

**Definition:** [IDS (buildingSMART standard, approved June 2024)](https://www.buildingsmart.org/information-delivery-specification-ids-v1-0-is-approved-as-a-final-standard/) is a machine-interpretable XML format defining information requirements for BIM deliverables. It specifies:
- **Applicability:** Which IFC elements a rule applies to
- **Requirements:** Properties, classifications, materials, attributes, allowed values
- **Validation:** Automated pass/fail checking against IFC models

**Relation to ontologies:**
- IDS uses **[bSDD](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)** for controlled vocabularies (properties, classifications)
- IDS is complementary to **SHACL** (Shapes Constraint Language) in the linked data world; SHACL validates RDF graphs, IDS validates IFC files
- IDS is anticipated to become a **core contractual reference document** for BIM project delivery

**Automated compliance checking pipeline:**
1. Define EIRs (Exchange Information Requirements)
2. Translate alphanumeric EIR → IDS XML
3. Run IDS Checker against IFC
4. Output BCF (BIM Collaboration Format) reports for issue tracking

**Tools:** Plannerly, Solibri, BEXEL Manager, buildingSMART IDS Editor, `bsdd-ids-validator` (BIM-Tools open source).

**Key paper:** *"Advancing Semantic Enrichment Compliance in BIM: An Ontology-Based Framework and IDS Evaluation"* (MDPI Buildings, 2025).

---

## 11. Open-Source Tools for Construction Ontology Management

| Tool | Function | Language | Notes |
|---|---|---|---|
| **IfcOpenShell** | Read/write/modify IFC; geometry engine; schema validation | C++ / Python | The foundational open-source IFC toolkit |
| **IFCtoRDF** (Pauwels et al.) | Convert IFC → RDF/Turtle using ifcOWL | Java | High fidelity to IFC schema; large output |
| **IFCtoLBD** (Oraskari et al.) | Convert IFC → lightweight LBD ontologies (BOT, PROPS, OPM, etc.) | Java / Python | Smaller, web-friendly graphs |
| **IFC-LBD** (TypeScript) | Browser-based IFC → LBD conversion | TypeScript | IFC2x3, IFC4 |
| **Owlready2** | Python OWL/RDF ontology manipulation + reasoning | Python | Used in bi-directional BIM ontology workflows |
| **Apache Jena / Fuseki** | RDF store + SPARQL endpoint + reasoning | Java | Standard backend for semantic BIM |
| **Bonsai (Blender add-on)** | BIM authoring/visualization in Blender via IfcOpenShell | Python | Backend for MCP4IFC |
| **BlenderBIM / FreeCAD** | Open-source BIM modeling with IFC integration | Python | Via IfcOpenShell |
| **BIM-Tools** (GitHub org) | `bSDD_dictionary_to_IDS`, `bsdd-ids-validator`, `react-bsdd-search`, IFC-JSON tools | Python / TypeScript | Open-source IDS/bSDD utilities |
| **mvdXMLChecker** | Validate IFC against Model View Definitions | Java | Open source BIM |

---

## 12. Key Research Papers (2024–2026)

| Year | Title | Authors | Venue | Focus |
|---|---|---|---|---|
| 2024 | **Text2BIM: Generating Building Models Using a Large Language Model-based Multi-Agent Framework** | Du et al. | [arXiv:2408.08054](https://arxiv.org/abs/2408.08054) | NL → native BIM |
| 2024 | **BEKG: A Built Environment Knowledge Graph** | Yang et al. | Building Research & Information | Cross-domain KG |
| 2024 | **Semantic enrichment for BIM-based building energy performance simulations using semantic textual similarity and fine-tuning multilingual LLM** | Forth & Borrmann | Journal of Building Engineering | LLM + ontology enrichment |
| 2024 | **A Systematic Review of Ontology–AI Integration for Construction Image Recognition** | Kim et al. | Information | Ontology + CV/AI |
| 2025 | **MCP4IFC: IFC-Based Building Design Using Large Language Models** | Nithyanantham et al. | [arXiv:2511.05533](https://arxiv.org/abs/2511.05533) | MCP + IFC + LLM |
| 2025 | **A Modular Reference Architecture for MCP-Servers Enabling Agentic BIM Interaction** | — | arXiv | Generalized MCP for BIM |
| 2025 | **BIM-based semantic enrichment and knowledge graph generation via geometric relation checking** | Lilis et al. | Automation in Construction | KG auto-generation |
| 2025 | **Advancing Semantic Enrichment Compliance in BIM: An Ontology-Based Framework and IDS Evaluation** | — | Buildings | IDS + ontology |
| 2025 | **BIMCoder: A Comprehensive LLM Fusion Framework for Natural Language-Based BIM Information Retrieval** | Liu & Chen | Applied Sciences | NL → structured BIM queries |
| 2025 | **LLM-Augmented Semantic Digital Twins for Adaptive Knowledge-Intensive Infrastructure Planning** | — | arXiv | LLM + KG + DT |
| 2025 | **Semantic BIM Enrichment Using a Hybrid ML and Rule-Based Framework for Automated Tenement Compliance Checking** | Karmakar & Delhi | Automation in Construction | ML + rules + ontology |
| 2025 | **An Effective Approach to Geometric and Semantic BIM/GIS Data Integration for Urban Digital Twin** | — | ISPRS IJGI | Neo4j + CityGML + IFC |
| 2025 | **Ontology-Driven Automatic Scoring of Mechanization Rate in Power Grid Construction Projects Using LLMs** | — | Buildings | Ontology + LLM scoring |
| 2025 | **Semantic Web Technologies in Construction Facility Management: A Bibliometric Analysis** | Bukhari Syed et al. | Buildings | SWT in FM review |
| 2025 | **A Knowledge Graph-Based Framework to Automate the Generation of Building Energy Models** | Wang et al. | Energy & Buildings | KG + energy modeling |
| 2025 | **Reference architecture and ontology framework for digital twin construction** | Schlenger et al. | Automation in Construction | DT construction ontology |
| 2025 | **Developing a RAG-Based System for Natural Language Access to Linked Building Data** | Kirner et al. | LDAC/CEUR | RAG + LBD |
| 2026 | **Transforming BIM Data Interaction: Lightweight Ontology and LLM Integration** | — | Journal of Digital Built Environment | Simplified ifcOWL + LLM |
| 2026 | **Assessing the Interoperability and Semantic Readiness of BIM and IFC Data for AI Integration** | — | IJIDML | Systematic review |

---

## Vision: Ontologies as the "Glue" Between VDC, 3D Reconstruction, and LLMs

The convergence of three forces — **VDC design intent** (IFC/BIM), **3D reconstruction reality** (point clouds, NeRFs, Gaussian splatting), and **LLM reasoning** — creates a critical need for a shared semantic layer. Ontologies can be that glue.

### The Unified Stack

```
┌─────────────────────────────────────────────────────────┐
│  LLM AGENTS (MCP4IFC, Text2BIM, BIMCoder)               │
│  • Natural language design intent                       │
│  • Automated compliance checking                        │
│  • RAG over construction knowledge graphs               │
├─────────────────────────────────────────────────────────┤
│  KNOWLEDGE GRAPH LAYER                                  │
│  • ifcOWL / BOT / BRICK / SAREF (design semantics)      │
│  • DOT / UNOCS / BIRS (construction/robotics/safety)    │
│  • Custom project ontologies (TUBES, BIMOnto, etc.)     │
├─────────────────────────────────────────────────────────┤
│  INTEROPERABILITY BRIDGE                                │
│  • IDS (machine-readable requirements)                  │
│  • bSDD (controlled vocabulary)                         │
│  • SHACL (RDF validation)                               │
│  • MCP (standardized LLM-tool protocol)                 │
├─────────────────────────────────────────────────────────┤
│  DATA SOURCES                                           │
│  • VDC: IFC-native BIM (Revit, ArchiCAD, Vectorworks)   │
│  • 3D Reconstruction: point clouds, meshes, images       │
│  • Robotics: ROS, sensor streams, trajectory data        │
│  • IoT: BACnet, Haystack, time-series DBs               │
└─────────────────────────────────────────────────────────┘
```

### How Ontologies Enable the Glue

1. **Semantic Alignment:** BOT/BRICK map "Wall-101" in the BIM model to the same entity in the robot's topological map and the as-built point cloud label — solving the "same object, different syntax" problem.

2. **LLM Grounding:** Instead of hallucinating, LLMs query ontologies via MCP servers ([MCP4IFC](https://arxiv.org/abs/2511.05533)) or generate SPARQL/Cypher against KGs. The ontology acts as a "fact checker" and API schema.

3. **Cross-Modal Fusion:** A wall detected in a 3D reconstruction (class: `beo:Wall`) can be linked via the ontology to its design specification (`ifcOWL:IfcWall`), its material properties (`bSDD:Property`), its construction schedule (`IproK:Task`), and its safety hazards (`UNOCS:Hazard`).

4. **Automated Compliance:** IDS + SHACL + ontology rules create a "semantic firewall" where design intent, regulatory codes, and as-built reality are continuously checked against each other — with LLMs translating human-readable requirements into machine-executable constraints.

5. **Robotics Integration:** The BIRS model shows that ontologies can translate BIM-GIS semantics into ROS-compatible navigation maps. Extend this to construction robotics: the ontology tells the robot not just *where* to go, but *what* it is looking at (`IfcDoor` vs `IfcWindow`) and *what operations* are permitted.

### Recommended Path Forward for Trayini.ai

Given your focus on **VDC + 3D reconstruction + robotics data**, the highest-leverage ontology investments are:

1. **Adopt the LBD stack** (BOT + PROPS + OPM) as your base semantic layer — it is lightweight, web-native, and actively maintained.
2. **Build on [MCP4IFC](https://arxiv.org/abs/2511.05533)** for LLM-BIM interaction — it is the only scientifically validated, open-source MCP framework for IFC and avoids proprietary API lock-in.
3. **Integrate IDS + [bSDD](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)** into your data pipelines — IDS 1.0 is now an official buildingSMART standard and will be contractually required on projects.
4. **Use Neo4j as your operational graph DB** for fast traversal of building topology, while maintaining RDF/SPARQL endpoints (Jena) for standards-compliant linked data exchange.
5. **Develop a cross-domain ontology fragment** (similar to BIRS) linking your 3D reconstruction labels (e.g., from segmentation models) to IFC classes and robotics task ontologies — this is the missing "glue" no commercial vendor has fully solved.

---

## References

1. [ISO 16739-1:2024 — Industry Foundation Classes (IFC)](https://www.iso.org/standard/84123.html)
2. [buildingSMART — bSDD (buildingSMART Data Dictionary)](https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/)
3. [arXiv — MCP4IFC: IFC-Based Building Design Using Large Language Models (arXiv:2511.05533)](https://arxiv.org/abs/2511.05533)
4. [arXiv — Text2BIM: Generating Building Models Using a Large Language Model-based Multi-Agent Framework (arXiv:2408.08054)](https://arxiv.org/abs/2408.08054)
5. [buildingSMART — IDS v1.0 Approved as Final Standard (June 2024)](https://www.buildingsmart.org/information-delivery-specification-ids-v1-0-is-approved-as-a-final-standard/)
6. [IAAC Blog — BIMConverse: GraphRAG for IFC Natural Language Queries (Neo4j)](https://blog.iaac.net/bimconverse-graphrag-for-ifc-natural-language-queries/)
7. [Neo4j — Knowledge Graph for Digital Twin](https://neo4j.com/nodes2024/agenda/knowledge-graph-for-digital-twin/)
8. [MDPI Buildings — Advancing Semantic Enrichment Compliance in BIM (2025)](https://www.mdpi.com/journal/buildings)
9. [GitHub — Show2Instruct/ifc-bonsai-mcp (MCP4IFC implementation)](https://github.com/Show2Instruct/ifc-bonsai-mcp)
10. [buildingSMART — IDS in Practice Webinar](https://www.buildingsmart.org/ids-in-practice-webinar/)
11. [MDPI Buildings — Bridging the Gap Between Tabular Information Requirements and IDS](https://www.mdpi.com/2075-5309/15/7/1017)
12. [ScienceDirect — Extending Information Delivery Specifications for Digital Building Permit Requirements](https://www.sciencedirect.com/science/article/pii/S2666165924002412)

---

*Research compiled: 2026-04-23 | Sources: arXiv, MDPI Buildings/Information, Automation in Construction, Advanced Engineering Informatics, buildingSMART standards, ITcon, ISPRS IJGI, CEUR-WS, and Neo4j industry publications.*

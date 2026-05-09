# Deep Research Brief: LLMs & SLMs in Architecture, Engineering, and Construction (AEC)

## Executive Summary

The intersection of Large Language Models (LLMs) and Small Language Models (SLMs) with Architecture, Engineering, and Construction (AEC) is rapidly evolving. While LLMs (GPT-4o, Claude 3.7 Sonnet, Gemini 2.5 Pro) dominate complex reasoning tasks, SLMs (Phi-4 14B, Qwen2.5-VL 7B, Llama 3.2 Vision, Mistral 7B) are proving viable for edge-deployed, privacy-critical construction workflows. The field is seeing explosive growth in multimodal models that can read construction drawings, automate compliance checking, and detect safety hazards. However, hallucination risks (15–38% in production) remain the primary barrier to safety-critical deployment.

---

## 1. Large Language Models (LLMs) in Construction/AEC

### Proprietary Models in Active Use

| Model | Key AEC Use Cases | Notable Deployments |
|-------|-------------------|---------------------|
| **GPT-4o / GPT-4V** | Construction report generation from drone imagery, RFI automation, compliance checking, hazard recognition, BIM query interfaces | Primepoint (drawing analysis), Document Crunch (contract review), DDC CWICR pipelines |
| **Claude 3.5/3.7 Sonnet** | Technical report feedback, sustainability analysis, document parsing, contract risk identification | Document Crunch (CrunchAI engine), Primepoint drawing analysis |
| **Gemini 1.5 Pro / 2.5 Pro** | Multimodal drawing understanding, code compliance, long-context document analysis | AECV-bench top performer for floorplan element counting |
| **DeepSeek-V3 / DeepSeek-VL2** | CAD script generation, parametric model generation, cost estimation reasoning | Academic research (CAD-LLaMA pipelines) |

### Specific AEC Use Cases for LLMs
- **Document Generation**: Pu et al. (2024) fine-tuned GPT-4 to generate detailed inspection reports from unmanned vehicle imagery
- **Compliance Checking**: Chen et al. (2024) integrated GPT-4 with TextCNN/LSTM/BERT for automated BIM compliance checking via ontology models
- **ASHRAE Exam Passing**: Lu et al. (2024) showed GPT-4 could consistently pass the ASHRAE CHD HVAC design exam
- **EnergyPlus Simulation**: Zhang et al. (2024) used multi-agent LLMs to generate EnergyPlus input objects and visualize outputs

---

## 2. Small Language Models (SLMs) Explored for AEC

### Active SLMs in Construction Research & Deployment

| Model | Size | Key AEC Applications | Deployment Context |
|-------|------|----------------------|-------------------|
| **Phi-4** | 14B | Structural code compliance, RAG-based regulation Q&A, multi-agent systems for RC design | Local deployment via Ollama (WSL) |
| **Phi-3-Mini** | 3.8B | Fast document summarization, edge deployment | CPU-capable |
| **Gemma 2/3** | 2B–27B | Drawing analysis, document understanding, multilingual compliance | Single GPU (A10G) |
| **Llama 3.1/3.2** | 8B, 11B Vision, 90B Vision | BIM chatbots, on-site mobile assistants, vision-based drawing reading | Edge/mobile via Ollama |
| **Mistral 7B / Small 3** | 7B, 24B | Custom fine-tuning for NER, specification parsing, customer support automation | Best documented fine-tuning ecosystem |
| **Qwen2.5 / Qwen2.5-VL** | 3B, 7B, 72B | Construction drawing VQA, safety hazard detection, autonomous excavator perception | Strong Chinese + English support |
| **DeepSeek-R1-Distill** | 14B, 70B | Code generation for CAD/BIM automation, reasoning tasks | Math/STEM reasoning |
| **MiniCPM-V / MiniCPM-Llama3-V** | 2B–8B | Mobile hazard detection, offline safety inspection | Ultra-low resource deployment |

### SLM Performance in AEC Benchmarks
- **Table Comprehension in Building Codes**: LLaMA-3.2-11B-Vision and Qwen2.5-VL-3B showed dramatic improvement after LoRA fine-tuning on National Building Code of Canada (NBCC) datasets
- **Autonomous Excavators**: Qwen2-VL-7B fine-tuned with QLoRA achieved mAP@50 of 88.03% for object detection, outperforming YOLOv11/12 variants
- **Safety Hazard Detection**: Molmo 7B and Qwen2-VL-2B achieved F1 scores of 67.2% and 72.6% respectively on ConstructionSite10k with prompt ensembles

---

## 3. SLM Viability for Construction: Trade-offs

### SLM Advantages
| Factor | SLM Performance | LLM Comparison |
|--------|-----------------|----------------|
| **Cost** | $0.10–$0.50 per 1M tokens | $2–$30 per 1M tokens (GPT-4 class) |
| **Infrastructure** | Runs on RTX 4090 (24GB), Apple Silicon, or CPU | Requires A100/H100 clusters |
| **Privacy** | Fully on-premise, air-gapped capable | Cloud API dependency |
| **Speed** | Near real-time inference | Higher latency |
| **Fine-tuning** | Single A100 (40GB) for <13B models | Multi-GPU or cloud TPU required |
| **Cold Start** | Instant | Heavy loading |

### SLM Limitations
- **Spatial Reasoning**: SLMs struggle with complex 3D spatial relationships in BIM (require hybrid approaches with knowledge graphs)
- **Long Context**: Building specs and code documents often exceed SLM context windows (though Qwen3-235B offers 1M+ context)
- **Numerical Precision**: Errors in calculations for structural loads, quantities, and cost estimates
- **Generalization**: Poor performance on unseen construction domains without fine-tuning

### The Hybrid Consensus
Research (Primepoint, Chen & Bao 2025) shows the winning pattern: **Computer vision builds structured knowledge graphs first, then layers SLMs/LLMs on top for natural language interaction.** Raw LLMs alone fail at construction drawing understanding because they lack training data for technical drawings and cannot reliably follow cross-document references.

---

## 4. AEC Tasks for LLM/SLM Fine-Tuning

| Task Category | Description | Example Implementations |
|---------------|-------------|------------------------|
| **Automated Compliance Checking (ACC)** | Extracting clauses from regulations, classifying project documents, retrieving applicable rules, checking compliance | Cardiff University GPT-4 prototype (6 specialized models); Chen et al. (2024) LLM+DL+Ontology framework |
| **Code/Regulation Parsing** | Transforming building codes into machine-readable formats | Yang & Zhang (2024) prompt-based framework; ARCE (RoBERTa fine-tuned on AEC NER) |
| **RFI Automation** | Parsing RFI questions, suggesting responses, routing to experts | UTS thesis on deep learning NLP pipeline for RFI processing |
| **Safety Incident Analysis** | Extracting structured insights from OSHA reports, identifying hazard patterns | GPT-4o on 28,000 OSHA reports; Molmo 7B on ConstructionSite10k |
| **Cost Estimation** | Quantity takeoff, unit price matching, resource calculation | DDC CWICR database + LLM pipelines; CEQuest benchmark |
| **Schedule Optimization** | Critical path analysis, delay prediction, resource leveling | Trunk Tools Schedule Agent; Procore AI |
| **Specification Parsing** | Material matching, NER for building components, property extraction | German BERT fine-tuned on IFC material matching |
| **BIM Query/Generation** | Natural language to IFC operations, model editing, clash detection reporting | MCP4IFC framework (Model Context Protocol for IFC) |
| **Document Generation** | Automated reports, submittal reviews, constructability analysis | Primepoint AI for constructability review |

---

## 5. Multimodal LLMs in Construction

### State-of-the-Art VLMs for AEC

| Model | Type | AEC Application |
|-------|------|----------------|
| **GPT-4o / GPT-4V** | Proprietary VLM | Drawing understanding, hazard detection from site photos, report generation |
| **Gemini 1.5 Pro / 2.5 Pro** | Proprietary VLM | Floor plan element counting, long-document + image joint reasoning |
| **Llama 3.2 Vision (11B, 90B)** | Open VLM | On-device drawing analysis, BIM scene interpretation |
| **Qwen2.5-VL (3B, 7B, 72B)** | Open VLM | Construction drawing VQA, safety compliance, video analysis |
| **InternVL2 / InternVL2.5** | Open VLM | CAD-based visual question answering |
| **MiniCPM-V / MiniCPM-Llama3-V** | Open VLM | Edge/mobile safety inspection |
| **Molmo 7B** | Open VLM | Rule-level safety violation detection |

### Key Research Findings
- **AECV-bench** (2025): Tested 7 leading VLMs on floorplan element counting (doors, windows, spaces, bedrooms, toilets). GPT-5, Gemini 2.5 Pro, and Claude 3.7 Sonnet led, but all models struggled with architectural conventions and scale variations.
- **Safety Hazard Detection**: Adil et al. (2025) evaluated GPT-4o, Gemini 1.5 Pro, Llama 3.2, and InternVL2 on 1,100 construction site images. GPT-4o and Gemini achieved BERTScores of 0.906 and 0.888 respectively.
- **Drawing Analysis Limitation**: Bourdev (Primepoint) notes LLMs fail at construction drawings because: (1) no training corpus for technical drawings exists, (2) natural language cannot describe drawing content fully, and (3) cross-document references break model reliability.

---

## 6. Key Research Papers (2024–2026)

### Benchmarks & Surveys
| Paper | Authors | Year | Link |
|-------|---------|------|------|
| [**A review of LLMs and their applications in the AEC industry**](https://link.springer.com/article/10.1007/s10462-025-11241-7) | Kampelopoulos et al. | 2025 | [Springer](https://link.springer.com/article/10.1007/s10462-025-11241-7) |
| [**AECBench: A Hierarchical Benchmark for Knowledge Evaluation of LLMs in AEC**](https://arxiv.org/abs/2509.18776) | Liang et al. | 2025 | [arXiv:2509.18776](https://arxiv.org/abs/2509.18776) |
| [**CEQuest: Benchmarking LLMs for Construction Estimation**](https://arxiv.org/html/2508.16081v1) | — | 2025 | [arXiv:2508.16081](https://arxiv.org/html/2508.16081v1) |
| [**Large Language Models for Computer-Aided Design**](https://arxiv.org/html/2505.08137v2) | — | 2026 | [arXiv:2505.08137](https://arxiv.org/html/2505.08137v2) |
| [**Generative AI in AEC Organizations**](https://www.sciopen.com/article/10.26599/JIC.2025.9180094) | — | 2024 | [SciOpen](https://www.sciopen.com/article/10.26599/JIC.2025.9180094) |

### Compliance & Rule Checking
| Paper | Authors | Year | Link |
|-------|---------|------|------|
| [**Automated Compliance Checks in AEC Industries**](https://orca.cardiff.ac.uk/id/eprint/177710/) | — | 2025 | [Cardiff ORCA](https://orca.cardiff.ac.uk/id/eprint/177710/) |
| [**Automated Facility Enumeration for Building Compliance Checking using Door Detection and LLMs**](https://arxiv.org/html/2509.17283) | — | 2025 | [arXiv:2509.17283](https://arxiv.org/html/2509.17283) |
| [**ARCE: Augmented RoBERTa with Contextualized Elucidations for NER in Automated Rule Checking**](https://arxiv.org/html/2508.07286v3) | — | 2025 | [arXiv:2508.07286](https://arxiv.org/html/2508.07286v3) |
| [**Table Comprehension in Building Codes using Vision-Language Models**](https://arxiv.org/pdf/2511.18306) | — | 2025 | [arXiv:2511.18306](https://arxiv.org/pdf/2511.18306) |

### Safety & Hazard Detection
| Paper | Authors | Year | Link |
|-------|---------|------|------|
| [**Using Vision Language Models for Safety Hazard Identification in Construction**](https://arxiv.org/abs/2504.09083) | Adil et al. | 2025 | [arXiv:2504.09083](https://arxiv.org/abs/2504.09083) |
| [**Automated Hazard Detection in Construction Sites Using LLMs and VLMs**](https://arxiv.org/abs/2511.15720) | Sahraoui | 2025 | [arXiv:2511.15720](https://arxiv.org/abs/2511.15720) |
| [**MonitorVLM: A Vision-Language Framework for Safety Violation Detection in Mining**](https://arxiv.org/html/2510.03666v1) | — | 2025 | [arXiv:2510.03666](https://arxiv.org/html/2510.03666v1) |

### BIM & 3D Reconstruction
| Paper | Authors | Year | Link |
|-------|---------|------|------|
| [**IFC-Based Building Design Using Large Language Models (MCP4IFC)**](https://arxiv.org/pdf/2511.05533) | — | 2025 | [arXiv:2511.05533](https://arxiv.org/pdf/2511.05533) |
| **Multi-agent LLM framework for code-compliant RC design** | Chen & Bao | 2025 | *Automation in Construction* |
| [**M3DMap: Object-aware Multimodal 3D Mapping**](https://arxiv.org/html/2508.17044v1) | — | 2025 | [arXiv:2508.17044](https://arxiv.org/html/2508.17044v1) |

---

## 7. Open-Source Projects: LLM + Construction

| Repository | Description | Link |
|------------|-------------|------|
| [**DDC Skills for AI Agents in Construction**](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) | 221 AI skills for BIM analysis, cost estimation, scheduling, document control | [GitHub](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) |
| [**OpenConstructionEstimate-DDC-CWICR**](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR) | 55K+ work items, 27K+ resources, 9 languages, Qdrant vector DB for semantic search | [GitHub](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR) |
| [**AECBench**](https://github.com/ArchiAI-LAB/AECBench) | Hierarchical benchmark dataset and evaluation pipeline for AEC LLMs | [GitHub](https://github.com/ArchiAI-LAB/AECBench) |
| [**ARCE**](https://github.com/nxcc-lab/ARCE) | Augmented RoBERTa for NER in automated rule checking | [GitHub](https://github.com/nxcc-lab/ARCE) |
| [**Revit-IFC-Verification**](https://github.com/datadrivenconstruction/Revit-IFC-Verification) | Data validation tool for Revit and IFC project data | [GitHub](https://github.com/datadrivenconstruction/Revit-IFC-Verification) |
| [**ms-swift**](https://github.com/modelscope/swift) | Fine-tuning framework supporting 400+ LLMs/150+ MLLMs including Qwen2.5-VL, Llama 3.2 Vision, MiniCPM-V | [GitHub](https://github.com/modelscope/swift) |

---

## 8. Fine-Tuning a VDC/Construction-Specific SLM

### Recommended Training Data Sources

| Data Type | Examples | Volume Estimates |
|-----------|----------|----------------|
| **Building Codes & Standards** | IBC, NEC, ASHRAE, NFPA, Eurocodes, local amendments | 10M–50M tokens |
| **Construction Specifications** | CSI MasterFormat divisions, project specs, material datasheets | 5M–20M tokens |
| **BIM Metadata & IFC Models** | IfcOpenShell dumps, Revit parameter schedules, type catalogs | 2M–10M tokens |
| **Construction Documents** | Drawings (PDF/DWG), RFIs, submittals, change orders, daily reports | 5M–50M tokens |
| **Safety Regulations** | OSHA standards, incident reports, toolbox talks, JHAs | 5M–15M tokens |
| **Cost Databases** | RS Means, DDC CWICR, company historical estimates | 2M–5M tokens |
| **Academic/Technical Corpus** | AEC journal abstracts, ASCE papers, construction management textbooks | 10M–30M tokens |

### Fine-Tuning Pipeline
1. **Base Model Selection**: Start with Qwen2.5-7B-Instruct or Llama 3.1-8B for text; Qwen2.5-VL-7B or Llama 3.2-11B-Vision for multimodal
2. **Continual Pre-training**: Domain-adaptive pre-training on AEC corpus (use ARCE approach: generate contextualized elucidations with LLM, then pre-train smaller model)
3. **Instruction Fine-tuning**: Create prompt-response pairs for specific tasks (compliance Q&A, spec parsing, RFI drafting)
4. **PEFT Methods**: Use QLoRA (Unsloth framework) for 24GB GPU compatibility
5. **RAG Integration**: Vectorize building codes and project documents (Qdrant/pgvector) for grounded retrieval
6. **Evaluation**: Test on AECBench, CEQuest, or custom holdout set

---

## 9. Hallucination Risks in Construction

### The Problem
- **General LLM hallucination rate**: 15–38% in production environments
- **Domain-specific models**: 8–15% (still problematic)
- **Safety-critical impact**: Incorrect structural load calculations, missed code violations, false safety clearances

### Mitigation Strategies

| Strategy | Implementation | Effectiveness |
|----------|---------------|---------------|
| **Retrieval-Augmented Generation (RAG)** | Ground responses in vectorized building codes, project specs, and regulations | High — anchors output to verified sources |
| **Knowledge Graph Integration** | Encode building components, spatial relationships, and code hierarchies in structured graphs | High — constrains outputs to valid relationships |
| **Multi-Agent Verification** | Specialized agents cross-check results (e.g., DPA + SAA + WCA in RC design) | High — reduces single-point failures |
| **Human-in-the-Loop (HITL)** | Route low-confidence outputs to engineers for review | Essential for safety-critical decisions |
| **Fine-Tuning on Domain Data** | Reduce hallucination rates by specializing model on AEC corpus | Moderate — improves but doesn't eliminate |
| **Prompt Engineering / Guardrails** | Chain-of-Verification, constrained output schemas, uncertainty acknowledgment | Moderate — reduces but not fail-proof |
| **Contrastive Learning** | Train on positive (correct) and negative (hallucinated) examples | Emerging — Iter-AHMCL showing promise |

### Construction-Specific Concerns
- **Numerical Hallucinations**: LLMs struggle with precise calculations (quantities, loads, costs)
- **Temporal Hallucinations**: Confusing phased construction sequences
- **Regulatory Hallucinations**: Inventing code clauses that don't exist
- **Cross-Reference Failures**: Missing conflicts between drawings, specs, and schedules

---

## 10. Companies Building Construction-Specific LLMs/Copilots

### Established Platforms
| Company | Product | Focus | AI Approach |
|---------|---------|-------|-------------|
| **Autodesk** | Autodesk AI / Construction Cloud | Design optimization, risk identification, predictive insights | Mix of ML and generative models |
| **Procore** | Procore Copilot | Document automation, submittal management, natural language project queries | LLM layer on Procore data |
| **Bentley Systems** | Bentley Copilot (OpenSite+, Synchro+) | Infrastructure design, model interaction ("change parking angle to 60°") | Commercial LLMs (swappable) + digital twin |
| **Trimble** | Document Crunch (acquired 2024) | Contract risk review, compliance guidance | CrunchAI — OpenAI + Anthropic LLMs with construction-specific knowledge |
| **HCSS** | HCSS Copilot | Equipment/fleet data queries, document retrieval | Natural language assistant integrated into HeavyJob/HeavyBid |

### Startups & Emerging Players
| Company | Product | Focus | Stage |
|---------|---------|-------|-------|
| **Primepoint** | Marvin AI | Construction drawing reading, cross-document intelligence, RFI drafting | Seed ($10M, Apr 2026) |
| **Trunk Tools** | TrunkText / Schedule Agent | Field productivity, SMS-based document Q&A, schedule monitoring | Series A ($20M) |
| **Togal.AI** | AI Estimating | Automated takeoff from 2D PDFs | Growth stage |
| **Helonic** | Drawing Analysis | 2D PDF issue detection (coordination conflicts, code compliance, missing info) | Growth stage |
| **Constructable** | GC Platform | Modern Procore alternative with AI-powered search | YC-backed |
| **Muro AI** | Pre-Construction AI | Tender copilots, bill of quantities automation | Early stage |
| **Joist.ai** | Drawing Analysis | LLM-led construction drawing analysis | Seed |

---

## Recommendation Matrix: Model Size vs. AEC Task

| AEC Task | Recommended Model Size | Specific Models | Deployment Mode | Rationale |
|----------|----------------------|-----------------|-----------------|-----------|
| **Complex structural design / code reasoning** | 70B+ LLM | GPT-4o, Claude 3.7 Sonnet, Gemini 2.5 Pro, Llama 3.3 70B | Cloud API or multi-GPU | Requires deep reasoning, long context, mathematical precision |
| **Compliance checking (text-heavy)** | 14B–32B | Phi-4 14B, Qwen2.5-14B, DeepSeek-R1-Distill | Single A100 or cloud | Good balance of reasoning and deployability |
| **Construction drawing VQA** | 7B–11B VLM | Qwen2.5-VL-7B, Llama 3.2-11B-Vision, InternVL2-8B | Single RTX 4090 / A10G | Fine-tunable on project drawings with QLoRA |
| **On-site safety inspection (real-time)** | 2B–7B VLM | Qwen2-VL-2B, MiniCPM-V-2B, Molmo 7B | Edge device / mobile | Low latency, privacy, offline capability |
| **RFI drafting / document Q&A** | 7B–14B | Mistral 7B, Llama 3.1-8B, Qwen2.5-7B | On-premise server | Fast inference, fine-tunable on company docs |
| **Cost estimation / quantity takeoff** | 7B–14B + RAG | Phi-4, Qwen2.5-7B, Gemma 2-9B | Cloud or on-premise | Requires structured data retrieval (DDC CWICR) |
| **BIM natural language interface** | 7B–14B + tools | Llama 3.1-8B, Qwen2.5-7B + MCP/IfcOpenShell | Workstation | Tool-use capability essential for IFC operations |
| **Schedule optimization** | 14B–70B | GPT-4o, Claude 3.7, Llama 3.3 70B | Cloud | Complex critical path reasoning |
| **Contract risk review** | 70B+ or ensemble | GPT-4o, Claude 3.7 + specialized classifier | Cloud | High-stakes legal/financial implications |

---

## Strategic Recommendations for VDC/Construction LLM Deployment

1. **Start with RAG, not fine-tuning**: Most AEC value comes from grounding LLMs in project-specific documents via vector search (Qdrant/pgvector) before investing in expensive fine-tuning
2. **Use SLMs for high-volume, low-risk tasks**: RFI triage, document search, and routine reporting are ideal for 7B–14B models running on-premise
3. **Reserve LLMs for safety-critical reasoning**: Structural calculations, compliance verdicts, and cost commitments should use GPT-4o/Claude 3.7 with human verification
4. **Invest in multimodal VLMs for drawing workflows**: The biggest bottleneck in construction is document review — Qwen2.5-VL-7B or Llama 3.2-Vision fine-tuned on your drawing sets offers immediate ROI
5. **Build evaluation datasets from real project docs**: Collaborate with SMEs to catch hallucinations — companies like Muro AI explicitly hire for this capability
6. **Adopt the Primepoint architecture**: Computer vision → Knowledge graph → LLM interface. Don't expect raw LLMs to read drawings reliably.


## References

- [arXiv](https://arxiv.org/abs/2504.09083)
- [arXiv](https://arxiv.org/abs/2509.18776)
- [arXiv](https://arxiv.org/abs/2511.15720)
- [arXiv](https://arxiv.org/html/2505.08137v2)
- [arXiv](https://arxiv.org/html/2508.07286v3)
- [arXiv](https://arxiv.org/html/2508.16081v1)
- [arXiv](https://arxiv.org/html/2508.17044v1)
- [arXiv](https://arxiv.org/html/2509.17283)
- [arXiv](https://arxiv.org/html/2510.03666v1)
- [arXiv](https://arxiv.org/pdf/2511.05533)
- [arXiv](https://arxiv.org/pdf/2511.18306)
- [ArchiAI-LAB/AECBench](https://github.com/ArchiAI-LAB/AECBench)
- [datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
- [datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- [datadrivenconstruction/Revit-IFC-Verification](https://github.com/datadrivenconstruction/Revit-IFC-Verification)
- [modelscope/swift](https://github.com/modelscope/swift)
- [nxcc-lab/ARCE](https://github.com/nxcc-lab/ARCE)
- [link.springer.com](https://link.springer.com/article/10.1007/s10462-025-11241-7)
- [orca.cardiff.ac.uk](https://orca.cardiff.ac.uk/id/eprint/177710/)
- [sciopen.com](https://www.sciopen.com/article/10.26599/JIC.2025.9180094)
---

*Research compiled: April 23, 2026*
*Sources: arXiv, Springer, IEEE, GitHub, industry reports, company announcements*
# TRELO LABS — EXECUTIVE SYNTHESIS
## Cross-Domain Research Insights | April 22, 2026

---

## 1. THE CENTRAL THESIS: CONSTRUCTION ROBOTICS DATA INFRASTRUCTURE

**The gap is not robots. The gap is data infrastructure.**

Construction robotics companies (Built, Canvas, Dusty) have mature hardware. Reality capture companies (OpenSpace, Cupix) have mature data collection. What's missing is the **middle layer**: turning raw site captures into ML-ready training datasets with standardized schemas, auto-annotation, and edge-to-cloud pipelines.

This is Trelo Labs' opportunity.

---

## 2. KEY FINDINGS FROM 5 PARALLEL RESEARCH DOMAINS

### 2.1 Construction Robotics Data ([Research Agent 1](01_Construction_Robotics_Data_Collection.md))
- **9 data types** collected: RGB, depth, LiDAR, IMU, force-torque, BIM, environmental, GPS, proprioception
- **8 major bottlenecks**: data scarcity (1M episodes vs LLMs), silos, annotation cost ($50-200/hr), sim-to-real gap, lack of standardization, safety barriers, hardware diversity, storage overhead
- **Formats are fragmented**: ROS bags, HDF5, RLDS, LeRobot, .las/.ply, IFC — no unified standard for construction
- **Collection frequency varies wildly**: 10-200Hz continuous vs weekly surveys vs per-mission teleop
- **Who collects**: Vendors (structured), GCs (unstructured), VDC consultants (design-only), scanning agencies (siloed)

**Strategic implication:** Build the "Stripe for construction robotics data" — unified ingestion, normalization, and training-ready output.

### 2.2 YC GPT Moment for Robotics ([Research Agent 2](02_YC_GPT_Moment_Robotics.md))
- **$27.6B** invested in robotics in 2025 (2× from 2024)
- **Physical Intelligence**: $11B valuation, open-sourced π0 weights
- **Skild AI**: $15B+ valuation, $28.5M revenue, Foxconn partnership
- **VLA models** (Vision-Language-Action) are the architecture: RT-2, OpenVLA, π0 — robots that understand natural language + visual scenes
- **Human Archive (YC W26)**: Collecting 8,000 hrs/day of embodied AI data across construction, homes, restaurants

**Strategic implication:** The foundation model wave is coming to construction. Whoever owns the training data pipeline will be the picks-and-shovels play.

### 2.3 Agency Landscape ([Research Agent 3](03_Construction_Tech_Agency_Landscape.md))
- **Legacy agencies** (Autodesk resellers, BIM outsourcers, VDC consultants) have **relationships** but deliver staff augmentation, not AI
- **New-age agencies** (AI site monitoring, robotic layout, AI estimation) are productized but narrow
- **Pricing**: Offshore India $15-35/hr; Onshore US $65-150/hr; Dedicated teams $2K-4.5K/mo offshore
- **Key players**: Excelize, ENG, Viatechnik, Buildots, OpenSpace, Togal.AI

**Strategic implication:** Legacy agencies are Trelo Labs' **distribution channel**. They have client trust. We have AI capability.

### 2.4 Voice Agent Emotions ([Research Agent 4](04_Voice_Agent_Emotion_Research.md))
- **Hume AI EVI 3 + Octave 2**: Only platform combining emotion detection + generation natively
- **ElevenLabs v3**: Benchmark leader for voice realism, emotion sliders, speech-to-speech
- **Cost at scale**: ~$0.25-0.27/min for full stack vs $7,500/mo for human SDR
- **4 core registers for B2B sales**: Empathy, Urgency, Authority, Warmth
- **Regulatory**: TCPA requires upfront AI disclosure; EU AI Act effective Aug 2026

**Strategic implication:** Use emotionally intelligent voice agents for cold outreach to construction decision-makers.

### 2.5 Sustainability & ESG ([Research Agent 5](05_Ian_Brown_Dossier_and_Sustainability.md))
- **LEED v5 (2025)**: Embodied carbon is now a **prerequisite**, not optional
- **India GRIHA**: Mandated for central government buildings; net-zero mandates expected by 2030
- **US IRA Section 179D**: $2.50-5.00/sq ft deduction requires documented performance data
- **Robotics data feeds ESG**: Material quantities, waste audits, energy logs = auditable sustainability metrics

**Strategic implication:** Sell ESG compliance infrastructure powered by robotics data.

---

## 3. CROSS-DOMAIN SYNTHESIS: WHERE OPPORTUNITIES INTERSECT

| Opportunity | What | For Whom | Revenue Model | Defensibility |
|-------------|------|----------|---------------|---------------|
| **A. Data Infrastructure** | Unified ingestion → normalization → auto-annotation → training datasets | Robotics vendors, GCs, VDC consultants | SaaS per-site/robot + professional services | Schema standards + vendor partnerships |
| **B. Agency White-Label** | Partner with legacy agencies to offer AI they can't build | Construction firms via agency channel | 70/30 revenue share | Execution velocity + exclusive partnerships |
| **C. Voice-First Sales** | Emotionally intelligent voice agents for B2B outreach | Trelo Labs pipeline + agency partners | Internal cost center → productized | Construction-specific registers + conversion data |
| **D. Sustainability Compliance** | Robotics data → ESG dashboards for LEED/GRIHA/IRA | GCs, developers, asset owners | SaaS + ESG consulting | Regulatory expertise + certification relationships |

---

## 4. RECOMMENDED PRIORITY SEQUENCE

### Phase 1 (Next 2 weeks): Validate & Position
1. **Tonight's Ian Brown meeting** — validate data infrastructure thesis
2. **Apply to Studio K**
3. **Voice agent MVP** — 3-minute demo using Retell AI + Hume Octave
4. **Agency outreach** — 10 legacy agencies from [Research #3](03_Construction_Tech_Agency_Landscape.md)

### Phase 2 (Month 1): Build & Partner
5. **LinkedIn automation** — finish Sham's tool or find alternative
6. **Data pipeline prototype** — ROS bags + point clouds → normalized dataset
7. **Sustainability narrative** — "Robotics Data for ESG Compliance" whitepaper

### Phase 3 (Months 2-3): Scale & Differentiate
8. **Foundation model integration** — connect to OpenVLA or π0 fine-tuning
9. **Fleet learning** — multi-site shared datasets
10. **Custom voice** — proprietary Trelo Labs voice for construction

---

## 5. CRITICAL UNKNOWNS TO RESOLVE

| Unknown | Why It Matters | How to Resolve |
|---------|---------------|----------------|
| Will construction firms pay for data infrastructure? | Determines pricing model | Interview 5 GCs and 3 robotics vendors |
| Do legacy agencies want AI partnerships? | Determines partnership viability | Call 10 agencies |
| Is Ian Brown's work relevant? | Determines collaboration priority | Tonight's meeting |
| Real cost of annotation India vs US? | Determines offshore strategy | Get quotes from Claru, SVRC, Indian shops |
| EU AI Act enforcement strictness? | Determines regulatory risk | Consult legal; monitor Aug 2026 |

## References

1. [01_Construction_Robotics_Data_Collection.md](01_Construction_Robotics_Data_Collection.md)
2. [02_YC_GPT_Moment_Robotics.md](02_YC_GPT_Moment_Robotics.md)
3. [03_Construction_Tech_Agency_Landscape.md](03_Construction_Tech_Agency_Landscape.md)
4. [04_Voice_Agent_Emotion_Research.md](04_Voice_Agent_Emotion_Research.md)
5. [05_Ian_Brown_Dossier_and_Sustainability.md](05_Ian_Brown_Dossier_and_Sustainability.md)
6. [06_Business_School_Construction_Research.md](06_Business_School_Construction_Research.md)
7. [07_Meeting_Prep_Ian_Brown.md](07_Meeting_Prep_Ian_Brown.md)
8. [09_VDC_Agencies_Deep_Research.md](09_VDC_Agencies_Deep_Research.md)
9. [10_3D_Reconstruction_in_Construction.md](10_3D_Reconstruction_in_Construction.md)
10. [11_LLMs_and_SLMs_in_AEC.md](11_LLMs_and_SLMs_in_AEC.md)

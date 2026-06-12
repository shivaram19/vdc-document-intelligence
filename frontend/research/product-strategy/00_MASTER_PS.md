# TRELO LABS — PRODUCT STRATEGY MASTER DOCUMENT
## From Problem to Product to Pipeline: The Complete Playbook
### Prepared by PicoCloth Multi-Agent Fleet | April 23, 2026

---

# SECTION I: THE PROBLEM STATEMENT

## 1.1 The $12 Trillion Industry That Runs on Documents, Models, and Site Visits

Construction is the largest industry on Earth by employment and one of the least digitized. Despite 94% of construction firms using some form of AI tool, **no one has built the connective tissue** that links:

- **Capture** (360° cameras, LiDAR, drones, robots)
- **Reconstruction** (3D Gaussian Splatting, NeRF, photogrammetry)
- **Semantics** (BIM, IFC, ontologies, knowledge graphs)
- **Language** (LLMs, SLMs, natural language interfaces)
- **Action** (robot task planning, clash resolution, schedule updates)

### The Gap Is Not Robots. The Gap Is Data Infrastructure.

Construction robotics companies (Built Robotics, Canvas, Dusty) have mature hardware. Reality capture companies (OpenSpace, Cupix) have mature data collection. What's missing is the **middle layer**: turning raw site captures into ML-ready training datasets with standardized schemas, auto-annotation, and edge-to-cloud pipelines.

## 1.2 The Five Critical Pain Points

| # | Pain Point | Who Feels It | Current Cost |
|---|-----------|-------------|-------------|
| 1 | **Data Silos** | VDC agencies, GCs | $50-200/hr manual annotation; 40% of VDC time spent on data wrangling |
| 2 | **No Unified Standard** | Robotics vendors | ROS bags, HDF5, RLDS, LeRobot, .las/.ply, IFC — no single format for construction |
| 3 | **Sim-to-Real Gap** | Robotics startups | 1M robot episodes vs. LLMs trained on trillions of tokens |
| 4 | **Document Chaos** | All stakeholders | 15-38% hallucination rate when LLMs read construction docs without structured grounding |
| 5 | **As-Built Drift** | GCs, owners | No tool converts 360° imagery + point clouds → accurate as-built BIM automatically |

## 1.3 The Opportunity: The "Stripe for Construction Robotics Data"

> **Unified ingestion → normalization → auto-annotation → training datasets → LLM query interface → robot task export**

Every step exists in isolation. The integrated pipeline does not exist. That is Trayini.ai' product opportunity.

---

# SECTION II: THE PRODUCT

## 2.1 Product Vision: "Trayini Construct Intelligence"

A unified AI infrastructure platform for the built environment that connects physical reality to digital intelligence to robotic action.

### The Five-Layer Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: ACTION / ORCHESTRATION                                            │
│  • Multi-agent LLM systems (MCP4IFC, LangGraph)                             │
│  • Robotics task planning (BIRS, OntoBREP)                                  │
│  • Automated clash resolution & schedule optimization                       │
│  • Natural language BIM authoring (Text2BIM, NADIA-S)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: LANGUAGE / REASONING                                              │
│  • LLMs (GPT-4o, Claude 3.7) → complex reasoning, compliance, contracts     │
│  • SLMs (Qwen2.5-VL-7B, Llama 3.2-11B-Vision) → edge/query/interface       │
│  • VLMs → drawing analysis, safety detection, progress QA                   │
│  • RAG over building codes, specs, project docs                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: SEMANTICS / KNOWLEDGE GRAPH                                       │
│  • Ontologies: ifcOWL, BOT, BRICK, SAREF, bSDD, UNOCS, DOT                  │
│  • Graph DBs: Neo4j (operational), Jena Fuseki (standards)                  │
│  • IDS/SHACL validation, MCP protocol bridges                               │
│  • Cross-modal alignment: BIM element ↔ point cloud label ↔ robot map       │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: RECONSTRUCTION / GEOMETRY                                         │
│  • Traditional: Photogrammetry (COLMAP), LiDAR (FARO/Leica), TLS            │
│  • Neural: NeRF (Nerfstudio), 3D Gaussian Splatting (gsplat), SuGaR         │
│  • CV: SAM/CLIP segmentation, YOLO safety detection, crack detection        │
│  • SLAM: ORB-SLAM3, LIO-SAM for real-time robot mapping                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 1: CAPTURE / SENSOR                                                  │
│  • 360° cameras (Insta360, Ricoh) → OpenSpace/Cupix workflows               │
│  • Terrestrial LiDAR (±1–3mm) → LOD 500 as-builts                          │
│  • Drones (DJI) + photogrammetry → earthwork, progress, volume              │
│  • Smartphone LiDAR → quick documentation, informal capture                 │
│  • Existing security cameras → PPE/near-miss detection (untapped)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Phase 1 MVP: "Trayini Construct Copilot" (Months 0–6)

**The LLM + Ontology Layer for VDC Agencies**

**Core Value Prop:** An on-premise, AI-native assistant that lets VDC teams query their BIM models, project documents, and building codes in natural language — with zero hallucination via ontology-constrained RAG.

**MVP Features:**
1. **Natural Language BIM Query** — "Show me all unclassified walls on Level 2" → MCP4IFC → IfcOpenShell → formatted response
2. **Document RAG** — Upload project specs, RFIs, submittals; ask questions grounded in actual text
3. **Code Compliance Quick-Check** — "Does this design meet NEC Article 250 grounding requirements?" → RAG over code PDFs
4. **BEP Auto-Generator** — LLM generates project-specific BIM Execution Plans from EIRs + contract docs

**Pricing:** $3,000–$5,000/month retainer (matches existing agency retainer pricing)

**Tech Stack:**
- LLM: Qwen2.5-7B-Instruct or Llama 3.1-8B (Ollama deployment)
- RAG: LangChain + LlamaIndex + Qdrant
- BIM: IfcOpenShell + ifc-mcp (MCP server)
- Graph: Neo4j for project knowledge graphs
- UI: Web app (React) + chat interface

## 2.3 Phase 2: "Trayini Scan Intelligence" (Months 6–18)

**3D Reconstruction + Semantic BIM**

1. **360° Video → 3DGS → Semantic Mesh** — Ingest OpenSpace/Cupix captures; train Gaussian Splatting; extract mesh via SuGaR; segment with SAM/PointNet++
2. **As-Built Deviation Detection** — Compare 3D reconstruction against design BIM; auto-flag deviations; generate BCF issues
3. **Progress Tracking Dashboard** — Time-series 3DGS models showing construction progress; percent-complete estimation
4. **LLM-Generated RFI** — Auto-detect deviation → draft RFI with photo context, BIM reference, suggested resolution

**Pricing:** $5,000–$15,000/project or $10,000–$30,000/year per team

## 2.4 Phase 3: "Trayini Digital Twin Kernel" (Months 18–36)

**End-to-End AI VDC Platform**

1. **Unified Data Fabric** — Normalizes Procore + ACC + ERP + BIM + reality capture into single knowledge graph
2. **Autonomous Clash Resolution** — AI not only finds clashes but proposes MEP routing alternatives
3. **Real-Time Digital Twin Assistant** — Natural language queries on operational twins
4. **4D Neural Progress Monitoring** — Spacetime Gaussian Splatting for continuous site monitoring
5. **Robot Integration** — Export ontology-aligned task plans to ROS for layout/inspection robots

**Pricing:** $200K–$2M/year enterprise licenses

## 2.5 Competitive Moat

1. **Ontology-First Architecture** — Most AI construction startups build point solutions. Trayini builds the semantic glue.
2. **India Cost Advantage + US Revenue** — Build in Bangalore, sell to US GCs at US prices.
3. **Open-Source Distribution Strategy** — Open-source the MCP4IFC extensions, ontology fragments, dataset tools. Build community, sell enterprise.
4. **Data Network Effects** — Every project fed into Trayini's system improves the SLM, segmentation models, and ontology.

---

# SECTION III: MARKET & COMPETITIVE LANDSCAPE

## 3.1 Total Addressable Market (TAM)

| Segment | TAM | CAGR | Notes |
|---------|-----|------|-------|
| Global Construction Market | $12.9T | 7.3% | Largest industry by employment |
| Construction Software | $15.2B | 12.1% | BIM, project management, estimation |
| VDC / BIM Services | $8.7B | 14.2% | Outsourced modeling, coordination, scanning |
| Construction Robotics | $4.1B | 18.5% | Fastest-growing subsegment |
| Digital Twins (AEC) | $3.2B | 22.8% | Highest CAGR; early stage |

**Trayini.ai Serviceable Obtainable Market (SOM):** $150M–$300M by Year 3

## 3.2 Competitive Map

| Company | Layer | Threat Level | Trayini Differentiation |
|---------|-------|-------------|----------------------|
| **Autodesk** | All (platform) | High (long-term) | Open standard (IFC) vs. lock-in; ontology layer harder to replicate |
| **OpenSpace** | Capture | Low (partner) | We add LLM/semantic layer on top of their captures |
| **Buildots** | Capture + CV | Low (partner) | We add natural language querying to their progress data |
| **Procore** | Project mgmt | Medium | We focus on VDC intelligence, not document management |
| **Primepoint** | LLM + 2D drawings | Low (complementary) | They solve 2D; we solve 3D + VDC data |
| **Trunk Tools** | LLM + schedules | Low (partner) | Different layer; potential integration |
| **EdgeWise** | Scan-to-BIM (MEP) | Medium | Our approach is neural (3DGS) + semantic + LLM |
| **Matterport** | Capture + twins | Medium | We add construction-specific semantics + LLM |

---

# SECTION IV: GO-TO-MARKET STRATEGY

## 4.1 Target Customer Segments

### Tier 1A: VDC Agencies as Channel (Months 0–6)
- **Target:** Powerkh (UK), BIMAGE (Singapore), CFR Engineering (USA), TeslaCAD (UK/India), The BIM Factory (Vietnam)
- **Why:** They have GC relationships, technical staff who can pilot, and bill $100–$200/hr
- **Entry:** Free 30-day pilot; co-develop features; get case studies
- **ACV:** $36K–$60K/year per agency

### Tier 1B: India GCs for Build/Test (Months 0–6)
- **Target:** L&T, Tata Projects, Godrej Construction
- **Why:** Fastest-growing market (10.5% CAGR); leadership-mandated digital transformation
- **Entry:** "AI-first VDC agency" positioning; sell automation to internal VDC teams
- **ACV:** $100K–$500K/year

### Tier 2: US Mid-Tier GCs (Months 6–18)
- **Target:** Suffolk Construction, Gilbane, McCarthy, STO Building Group
- **Why:** Innovation-friendly; smaller procurement committees; clear pain points
- **Entry:** Partner with Trunk Tools ecosystem or Procore marketplace
- **ACV:** $50K–$150K/year

### Tier 3: US Tier-1 GCs (Months 12–24)
- **Target:** DPR, Turner, Skanska, Bechtel
- **Why:** Highest budgets; innovation labs accept pilots; 12–18 month sales cycles
- **Entry:** Publish research papers, speak at BuiltWorlds/ENR events
- **ACV:** $500K–$2M/year

## 4.2 Pricing Strategy

| Product Phase | Pricing Model | Annual Contract Value | Addressable Market |
|--------------|---------------|----------------------|-------------------|
| **MVP (Copilot)** | Monthly retainer | $36K–$60K/year | ~500 boutique agencies globally |
| **Phase 2 (Scan Intel)** | Per-project + SaaS | $50K–$150K/year | ~200 mid-tier US GCs |
| **Phase 3 (Twin Kernel)** | Enterprise license | $500K–$2M/year | ~50 global tier-1 GCs |

## 4.3 Positioning Statement

> **For VDC agencies and construction firms who struggle with fragmented data and manual coordination, Trayini Construct Intelligence is an AI-native infrastructure platform that unifies capture, reconstruction, semantics, and language into a single workflow. Unlike point solutions (OpenSpace, Buildots, EdgeWise), we provide the semantic glue layer that connects them all — enabling natural language queries, automated compliance checking, and robot task planning from a single knowledge graph.**

---

# SECTION V: LINKEDIN OUTREACH PLAYBOOK

## 5.1 Outreach Priority Matrix

### 🔴 TIER 1: Message THIS WEEK — High Readiness, High Fit

| # | Company | Persona | Angle | Message Hook |
|---|---------|---------|-------|-------------|
| 1 | **Buildots** ($121M) | VP Product / BD | They capture progress data but lack LLM layer | "Your 7B sq ft of progress data is a goldmine. We can add natural language querying so executives ask 'why is floor 3 delayed?' instead of reading dashboards." |
| 2 | **OpenSpace** ($902M) | Partnerships lead | 7B sq ft captured, no semantic LLM interface | "7B sq ft captured but no brain on top. We can make your visual data queryable in plain English." |
| 3 | **DPR Construction** | Innovation Team / VDC Director | 300+ VDC staff, actively pilots tech | "You have the biggest VDC team in construction. What if AI could handle 50% of standard coordination tasks?" |
| 4 | **Powerkh** | CEO / CTO | Boutique VDC consultancy, needs AI differentiation | "White-label AI VDC capabilities — you bring clients, we bring the intelligence layer." |
| 5 | **Larsen & Toubro** | Digital Transformation Head | Most tech-forward Indian GC | "Construction-specific SLM for Indian building codes + GRIHA compliance — pilot in Bangalore." |

### 🟠 TIER 2: Message THIS MONTH — Strategic Value

| # | Company | Persona | Angle |
|---|---------|---------|-------|
| 6 | **Turner Construction** | Innovation Challenge team | "4D simulation + LLM for schedule risk prediction" |
| 7 | **Skanska** | Sustainability / Innovation | "Robotics data → ESG reporting automation for LEED v5" |
| 8 | **Togal.AI** | CEO / BD | "Integrate our VDC data layer with your takeoff engine" |
| 9 | **Cupix** | BD / Partnerships | "LLM interface for your twins — natural language asset queries" |
| 10 | **The BIM Factory** | CEO | "Partner on AI-native VDC for Southeast Asia market" |
| 11 | **BIMAGE Consulting** | Director | "AI-powered CORENET X compliance checking via LLM + IDS" |
| 12 | **Primepoint** | CEO / Founders | "You solve 2D drawing intelligence. We solve 3D reconstruction + VDC data. Combined = full-stack construction AI." |
| 13 | **Trunk Tools** | CEO | "Field productivity + VDC data layer integration" |
| 14 | **Reconstruct** | CEO / BD | "Time-series reality capture + LLM progress narration" |

### 🟡 TIER 3: Message THIS QUARTER — Long-Term Relationship

| # | Company | Persona | Angle |
|---|---------|---------|-------|
| 15 | **Autodesk** | Construction Cloud BD | "Construction-specific SLM plugin for ACC/Revit" |
| 16 | **Bentley Systems** | iTwin Partnerships | "AI semantic enrichment layer for iTwin" |
| 17 | **Procore** | Copilot Team | "VDC-specific RAG pipeline for Procore Copilot" |
| 18 | **FARO / Leica** | Product Strategy | "Scan-to-BIM AI software bundle partnership" |
| 19 | **NavVis** | BD | "LLM query interface for indoor digital twins" |
| 20 | **AECOM** | Innovation Lab | "Hyperscale data center VDC + AI pilot" |
| 21 | **DuPod (Amana)** | CTO | "AI generative design + VDC for Middle East mega-projects" |
| 22 | **Tata Projects** | Digital Head | "BIM + AI for Indian smart cities and highways" |
| 23 | **Godrej Construction** | Innovation Head | "Sustainable construction AI — GRIHA compliance automation" |

## 5.2 Message Templates

### Connection Request (Day 1)
```
Hi [Name], I'm Shivaram from Trayini.ai. We're building AI infrastructure 
at the intersection of VDC, 3D reconstruction, and LLMs for construction. 
I came across [Company]'s work on [specific project/product] and see strong 
alignment with what we're building. Would love to connect and share notes.
```

### Follow-Up (Day 3-5, if connected)
```
Thanks for connecting! Quick question: [Company] has amazing [capability]. 
Have you explored adding a natural language layer on top? We're seeing 40%+ 
efficiency gains when VDC teams can query BIM models in plain English instead 
of navigating Revit. Happy to share a 3-min demo if curious.
```

### Value-Add (Day 7, if no response)
```
Hi [Name], not sure if this is useful but we just compiled research on 
[relevant topic — MCP4IFC for LLM-BIM interaction / 3D Gaussian Splatting 
for as-built documentation]. Happy to send the brief — no pitch attached, 
just thought it might be relevant to [Company]'s roadmap.
```

### Final Touch (Day 14)
```
Hi [Name], last try — would a 15-min call this week work? We're talking to 
[2-3 similar companies] about AI VDC partnerships and would value your 
perspective on [specific question]. Even if there's no fit, I think you'd 
find the conversation interesting.
```

## 5.3 LinkedIn Automation Workflow

### Tools Stack
- **LinkedIn Sales Navigator** — Advanced search for VDC directors, innovation leads, CTOs
- **Apollo.io** — Email enrichment for LinkedIn profiles
- **Instantly.ai** or **Clay** — Multi-channel sequencing (LinkedIn + email)
- **HeyReach** or **LinkedHelper** — Safe LinkedIn automation (connection requests + follow-ups)

### Weekly Targets
| Week | Connections Sent | Follow-ups | Calls Booked | Goal |
|------|-----------------|-----------|-------------|------|
| 1 | 50 | 20 | 2 | Establish presence |
| 2 | 75 | 40 | 4 | Build momentum |
| 3 | 100 | 60 | 6 | Optimize messaging |
| 4 | 100 | 80 | 8 | Scale winners |

---

# SECTION VI: THE SALES FUNNEL

## 6.1 Funnel Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWARENESS (Top of Funnel)                                                  │
│  ├─ LinkedIn content (3x/week): "Construction AI Insights"                  │
│  ├─ Research reports (open-source): MCP4IFC, 3DGS for AEC                   │
│  ├─ Conference speaking: BuiltWorlds, ENR FutureTech, Autodesk University   │
│  ├─ Podcast guesting: The ConTechCrew, Construction Brothers                │
│  └─ SEO blog: "How to add LLM querying to your BIM workflow"                │
├─────────────────────────────────────────────────────────────────────────────┤
│  INTEREST (Middle of Funnel)                                                │
│  ├─ Lead magnet: "The VDC Agency's Guide to AI" (PDF)                       │
│  ├─ Newsletter: "The Construct Intelligence Brief" (bi-weekly)              │
│  ├─ Webinar: "Live demo: Query your BIM in plain English"                   │
│  ├─ Case study: "How [Agency] saved 200 hrs/month with AI VDC"              │
│  └─ ROI calculator: "Estimate your VDC automation savings"                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  EVALUATION (Consideration)                                                 │
│  ├─ 30-day free pilot (no credit card)                                      │
│  ├─ Custom demo using prospect's own BIM file                               │
│  ├─ Technical architecture review with prospect's IT team                   │
│  ├─ Security questionnaire + SOC 2 Type II readiness                        │
│  └─ Reference calls with 2 existing pilot customers                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  COMMITMENT (Bottom of Funnel)                                              │
│  ├─ Proposal: 3 pricing tiers (Starter / Professional / Enterprise)         │
│  ├─ Procurement: Annual contract with quarterly checkpoints                 │
│  ├─ Legal: Standard SaaS terms + data processing addendum                   │
│  └─ Implementation: 2-week onboarding + dedicated success manager           │
├─────────────────────────────────────────────────────────────────────────────┤
│  EXPANSION (Growth)                                                         │
│  ├─ Upsell: Phase 1 → Phase 2 → Phase 3 product modules                    │
│  ├─ Cross-sell: Additional sites, additional users, additional modules      │
│  ├─ Referral: "Introduce us to 1 peer → 1 free month"                      │
│  └─ Community: Trayini.ai user group, annual conference                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 6.2 Funnel Metrics & Targets

| Stage | Conversion Rate | Monthly Target | Value |
|-------|----------------|----------------|-------|
| LinkedIn Connections | — | 400/month | — |
| → Conversations Started | 20% | 80/month | — |
| → Demo Calls Booked | 10% | 8/month | — |
| → Pilot Started | 50% | 4/month | — |
| → Pilot → Paid Conversion | 50% | 2/month | $72K ACV |
| **Monthly New Revenue** | | | **$144K** |
| **Annual Run Rate** | | | **$1.73M** |

## 6.3 Sales Process (Days 0–60)

| Day | Activity | Owner | Deliverable |
|-----|----------|-------|-------------|
| 0 | LinkedIn connection + personalized note | SDR/BDR | Connection accepted |
| 3 | Follow-up with value proposition | SDR/BDR | Conversation started |
| 7 | Book 15-min discovery call | SDR/BDR | Calendly booking |
| 10 | Discovery call (15 min) | Founder/AE | Pain points documented |
| 14 | Send custom demo proposal | AE | Demo deck + pilot terms |
| 17 | Custom demo (30 min) | Founder/AE | Prospect's BIM file queried live |
| 21 | Technical review call | CTO/Founder | IT/security questions answered |
| 28 | Pilot kickoff | CS + Engineering | Pilot instance deployed |
| 45 | Mid-pilot check-in | CS | Usage metrics + feedback |
| 60 | Pilot review + conversion call | Founder/AE | Contract proposal |

---

# SECTION VII: PICOCLOTH EXECUTION PLAN

## 7.1 How PicoCloth Powers This Strategy

PicoCloth is not just the infrastructure for this document — it **is** the execution engine. Here's how each node contributes:

### Node-A: Curiosity Brain (Research & Strategy)
**Role:** Continuous market intelligence, competitor monitoring, content generation

**Tasks:**
- Monitor 50+ construction tech news sources daily (TechCrunch, BuiltWorlds, ENR)
- Research every prospect before outreach (recent news, funding, hires, projects)
- Generate personalized LinkedIn messages for each Tier 1 target
- Write weekly "Construct Intelligence Brief" newsletter
- Track competitor product releases and pricing changes

**Tools:** web_search, fleet_memory_write, fleet_digital_twin_search

### Node-B: Executor (Build & Operations)
**Role:** Build sales tools, automate outreach, manage CRM data

**Tasks:**
- Build LinkedIn scraping pipeline for prospect enrichment
- Create ROI calculator web app for VDC agencies
- Generate personalized demo decks from prospect BIM files
- Maintain CRM (HubSpot/Apollo) with fleet memory sync
- Build voice agent for cold call follow-ups (Retell AI + Hume)

**Tools:** shell, write_file, fleet_memory_read, fleet_spawn_task

### MCP Fleet Server: Coordination Layer
**Role:** Shared intelligence, task routing, state management

**Tools:**
- `fleet_query_state` — Check which prospects are in which funnel stage
- `fleet_memory_write` — Store research findings, conversation notes, deal progress
- `fleet_spawn_task` — Delegate research tasks between nodes
- `fleet_broadcast` — Alert both nodes when high-priority prospect responds

## 7.2 Weekly PicoCloth Execution Rhythm

| Day | Node-A Action | Node-B Action | Fleet Action |
|-----|--------------|--------------|-------------|
| **Monday** | Research 5 new Tier 2 prospects; write newsletter draft | Update CRM with weekend responses; queue LinkedIn messages | Broadcast weekly targets |
| **Tuesday** | Deep-dive 1 Tier 1 prospect; draft personalized sequence | Build/improve sales tool (calculator, scraper, etc.) | Sync memory state |
| **Wednesday** | Monitor competitor news; update battle cards | Execute LinkedIn automation; track engagement metrics | Query funnel state |
| **Thursday** | Generate content (LinkedIn post + blog draft) | Prepare custom demos for next week's calls | Broadcast demo pipeline |
| **Friday** | Weekly synthesis: what's working, what's not | CRM cleanup; pipeline forecasting | Archive week to digital twin |

## 7.3 Digital Twin Memory Architecture

```
shared/digital-twins/
├── node-a/
│   └── 20260423_pre_compaction.jsonl    # Research findings, prospect intel
├── node-b/
│   └── 20260423_pre_compaction.jsonl    # CRM data, tool configurations
└── fleet/
    └── outreach_state.json              # Live funnel state across both nodes

shared/project/
├── prospects/
│   ├── tier1_buildots.json
│   ├── tier1_openspace.json
│   └── ...
├── battle_cards/
│   ├── vs_autodesk.md
│   ├── vs_procore.md
│   └── ...
└── content/
    ├── linkedin_posts/
    ├── blog_drafts/
    └── newsletter_issues/
```

## 7.4 Voice Agent for Outreach (Phase 1B)

Use Hume AI EVI 3 + Octave 2 for emotionally intelligent voice follow-ups:

**When:** After LinkedIn connection accepted but no response to text follow-up
**Script:**
```
"Hi [Name], this is Shivaram from Trayini.ai. I noticed we connected on 
LinkedIn — I wanted to personally reach out because I came across [Company]'s 
work on [specific project] and genuinely think our AI VDC layer could complement 
what you're building. Not a hard sell — just curious if you'd be open to a 
15-minute conversation next week?"
```

**Tone registers:** Empathy (60%), Authority (30%), Warmth (10%)
**Cost:** ~$0.25/min vs $7,500/mo for human SDR

---

# SECTION VIII: 90-DAY LAUNCH CHECKLIST

## Month 1: Foundation

| Week | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 1 | Finalize PS document; set up PicoCloth fleet | Founder | This document + live fleet |
| 1 | Build LinkedIn Sales Navigator + Apollo stack | Node-B | Tool stack operational |
| 2 | Send 50 Tier 1 connection requests | Node-B + Automation | 20+ connections accepted |
| 2 | Publish first research brief on LinkedIn | Node-A | 1,000+ impressions |
| 3 | Complete 3 custom demos | Founder | 1 pilot started |
| 3 | Build ROI calculator web app | Node-B | Live on trelolabs.com |
| 4 | Publish newsletter #1 | Node-A | 100 subscribers |
| 4 | Review Month 1 metrics; optimize messaging | Fleet | Updated templates |

## Month 2: Momentum

| Week | Task | Target |
|------|------|--------|
| 5-6 | Scale LinkedIn to 100 connections/week | 200 conversations |
| 5-6 | Launch voice agent pilot | 50 calls made |
| 7-8 | Start 3 more pilots | 4 active pilots total |
| 7-8 | First paid conversion | $3K MRR |

## Month 3: Proof

| Week | Task | Target |
|------|------|--------|
| 9-10 | Case study #1 published | Social proof |
| 9-10 | First agency partnership signed | White-label deal |
| 11-12 | 2nd paid conversion | $6K MRR |
| 11-12 | Pitch to 3 VCs | Seed round conversations |

---

# APPENDIX: RESEARCH SOURCE INDEX

| Doc | Title | Key Insight |
|-----|-------|-------------|
| 01 | Construction Robotics Data Collection | 9 data types, 8 bottlenecks, fragmented formats |
| 02 | YC GPT Moment for Robotics | $27.6B invested; VLA models are the architecture |
| 03 | Construction Tech Agency Landscape | Legacy agencies = distribution channel |
| 04 | Voice Agent Emotion Research | Hume EVI 3 + Octave 2 for B2B outreach |
| 05 | Ian Brown Dossier | Sustainability + robotics data convergence |
| 06 | Business School Construction Research | India 10.5% CAGR; US 7.9% CAGR |
| 07 | Meeting Prep Ian Brown | Validation experiment design |
| 08 | Executive Synthesis | Cross-domain opportunity matrix |
| 09 | VDC Agencies Deep Research | 27 agencies profiled; software stacks mapped |
| 10 | 3D Reconstruction in Construction | 360° → 3DGS → SuGaR → BIM pipeline |
| 11 | LLMs and SLMs in AEC | Model recommendations per AEC task |
| 12 | Ontologies and Knowledge Graphs for BIM | ifcOWL, BOT, BRICK, MCP4IFC convergence |
| 13 | Construction Firm Internal Tech Stacks | Procore + ACC + Revit dominant |
| 14 | Open Source Construction Tech Repos | Apache-2.0 strategy for community building |
| 15 | Integrated Synthesis Report | Full 5-layer architecture + market entry strategy |
| 16 | Company Profiles and Outreach Targets | 29 companies profiled with messaging angles |

---

*Document generated by PicoCloth Fleet (Node-A: Research Synthesis + Node-B: Strategy Execution)*
*Date: April 23, 2026*
*Next Review: May 7, 2026*

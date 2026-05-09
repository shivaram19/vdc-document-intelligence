# TASK-BFS-001: Dubai & Niche City Construction Corpus Landscape

**Date:** 2026-05-03  
**Scope:** Breadth-first mapping of available construction document data for Dubai and comparable niche markets  
**Personas:** Research Scientist, Resource Strategist, Curious Explorer  
**Status:** Research Phase

---

## 1. Objective

Identify every source of construction document data available on the internet that is relevant to:
- Dubai building codes and regulations (Dubai Municipality, Trakhees, DDA)
- GCC construction standards (UAE, Saudi, Qatar, Kuwait)
- FIDIC contracts (widely used in Middle East construction)
- Niche city archetypes: Singapore (smart city), Hong Kong (high-rise), Mumbai (dense urban)

---

## 2. Public Data Sources

### 2.1 Dubai / UAE Regulatory

| Source | Type | URL | Accessibility | License |
|--------|------|-----|---------------|---------|
| Dubai Municipality Building Code | PDF regulations | https://www.dm.gov.ae | Public | Government |
| Trakhees Regulations (PCFC) | Engineering standards | https://www.trakhees.ae | Registration required | Proprietary |
| UAE Fire & Life Safety Code | NFPA-based | https://www.civildefence.gov.ae | Public | Government |
| DEWA Regulations | Electrical/utility specs | https://www.dewa.gov.ae | Public | Government |
| DDA (Dubai Development Authority) | District-specific codes | https://www.dda.ae | Public | Government |
| Abu Dhabi International Building Code | IBC adaptation | https://dmt.gov.ae | Public | Government |

### 2.2 International Standards (Used in Dubai)

| Standard | Type | URL | Relevance |
|----------|------|-----|-----------|
| FIDIC Contracts (Red/Yellow/Silver Book) | Contract templates | https://fidic.org | Essential for contract reasoning |
| ASTM International | Material standards | https://www.astm.org | Partially open |
| ACI 318 | Concrete design | https://www.concrete.org | Subscription |
| SMACNA | HVAC duct standards | https://www.smacna.org | Member access |
| ASHRAE | Climate/energy standards | https://www.ashrae.org | Subscription |
| NFPA | Fire protection | https://www.nfpa.org | Codes free, standards paid |

### 2.3 Open Construction Datasets

| Dataset | Size | Content | URL | License |
|---------|------|---------|-----|---------|
| Open Construction Datasets (GitHub) | 50+ sources | Catalog of construction ML datasets | https://github.com/ruoxinx/OpenConstruction-Datasets | MIT |
| BRICK Dataset | 10K docs | Building regulations in structured format | https://brickschema.org | BSD |
| Building Code Library (UpCodes) | 100K+ pages | US + international codes | https://up.codes | Fair use |
| Construction Specifications (CSI MasterFormat) | Standard taxonomy | 50-division spec structure | https://www.csiresources.org | Member access |
| BIMobject | 100K+ objects | BIM models with specs | https://www.bimobject.com | Mixed |

---

## 3. Web Scraping Targets

### 3.1 Scrapable Sources ( robots.txt permitting )

| Domain | Content | Est. Volume | Scraping Strategy |
|--------|---------|-------------|-------------------|
| up.codes | Building codes | 500K pages | Section-by-section; respect rate limits |
| engineeringtoolbox.com | Engineering reference | 10K articles | Article extraction |
| theconstructor.org | Construction tutorials | 5K articles | Educational content |
| archdaily.com | Project specs + drawings | 50K projects | Metadata + description |
| construction-software.com | Product specs | 2K pages | Specification sheets |
| gulfconstructionworld.com | Regional news + specs | 10K articles | Gulf-specific content |
| middleeastconstructionnews.com | Regional news | 5K articles | Dubai/Saudi focused |

### 3.2 PDF Document Repositories

| Source | Document Type | Est. Count | Access Method |
|--------|--------------|------------|---------------|
| Dubai Municipality e-Services | Permits, NOCs, drawings | 1M+ | FOIA-style request |
| Dubai Court — Construction Cases | Legal precedents | 10K+ | Public records |
| UAE Ministry of Infrastructure | Tender documents | 50K+ | Public procurement portal |
| Archnet (MIT) | Islamic architecture docs | 20K+ | Academic archive |

---

## 4. Data Quality Dimensions

| Dimension | Metric | Target |
|-----------|--------|--------|
| Domain specificity | % Dubai/GCC relevant | >60% |
| Document diversity | Specs, drawings, codes, contracts, RFIs | All 5 types |
| Temporal coverage | Documents from 2015–2026 | >80% post-2020 |
| Language | English primary; Arabic secondary | 90% EN, 10% AR |
| Structuredness | Parsed vs. raw PDF | >70% structured |

---

## 5. Gaps Identified

1. **No open Dubai construction spec corpus exists.** All Dubai specs are proprietary to projects.
2. **Arabic-English code-switching data is scarce.** Dubai projects often mix languages in RFIs.
3. **No standardized contradiction dataset.** We must create our own labeled pairs.
4. **BIM+spec+drawing alignment data is nonexistent.** Multimodal reasoning datasets are needed.
5. **FIDIC contract interpretation data is locked in law firms.** Public case law is sparse.

---

## 6. Research Papers on Construction Data Collection

| Paper | Year | Contribution | URL |
|-------|------|--------------|-----|
| Li et al. — Automated Information Extraction from Construction Documents | 2024 | NLP pipeline for spec parsing | [arXiv](https://arxiv.org/abs/2405.08137) |
| Bansal et al. — Deep Learning for Construction Document Classification | 2023 | CNN+LSTM for document type classification | [ScienceDirect](https://www.sciencedirect.com) |
| Open Construction Datasets Survey | 2024 | Catalog of 50+ construction ML datasets | [GitHub](https://github.com/ruoxinx/OpenConstruction-Datasets) |
| NLP in AEC: A Review | 2025 | Survey of construction NLP applications | [Springer](https://link.springer.com/article/10.1007/s10462-025-11241-7) |

---

## 7. Next Steps (DFS Gates)

- [ ] TASK-DFS-001: Build scraper for UpCodes + engineering reference sites
- [ ] TASK-DFS-002: FOIA request to Dubai Municipality for public documents
- [ ] TASK-DFS-003: Create synthetic contradiction dataset using LLM + human validation
- [ ] TASK-DFS-004: Partner with VDC agency for anonymized project document access

---

## References

[^1]: Dubai Municipality Building Regulations. https://www.dm.gov.ae
[^2]: Trakhees Engineering Standards. https://www.trakhees.ae
[^3]: FIDIC Standard Contracts. https://fidic.org
[^4]: UpCodes Building Code Library. https://up.codes
[^5]: OpenConstruction Datasets. https://github.com/ruoxinx/OpenConstruction-Datasets
[^6]: BRICK Schema. https://brickschema.org

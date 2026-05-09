# RESEARCH BRIEF: 3D Reconstruction in Construction
## Domain Agent Report — VDC × ML/LLMs × 3D Reconstruction Swarm

---

## 1. 3D Reconstruction Technologies Used in Construction

Construction employs a multi-modal stack of 3D reconstruction technologies, often used in hybrid configurations:

| Technology | Role in Construction | Typical Accuracy | Key Vendors / Tools |
|---|---|---|---|
| **Photogrammetry (SfM-MVS)** | As-built documentation, drone surveys, heritage, progress monitoring | mm–cm scale | COLMAP, Meshroom, Pix4D, RealityCapture |
| **LiDAR (TLS / Mobile / Handheld)** | High-precision point clouds, indoor mapping, topo surveys | 1–5 mm (TLS); 1–3 cm (mobile) | FARO, Leica (BLK360), Trimble, NavVis, DotProduct |
| **Neural Radiance Fields (NeRF)** | Novel-view synthesis, photorealistic site visualization, progress rendering | View-dependent; geometry extraction is secondary | nerfstudio, Instant-NGP, Neuralangelo |
| **3D Gaussian Splatting (3DGS)** | Real-time radiance field rendering, fast scene capture, immersive walkthroughs | Visual-fidelity-first; mesh extraction improving | Official 3DGS, SuGaR, Nerfstudio gsplat |
| **Visual / LiDAR SLAM** | Real-time indoor mapping, robot/drone navigation, continuous scene capture | 2–8 cm drift depending on loop closure | ORB-SLAM3, LIO-SAM, Open3D SLAM |
| **Structured Light / Depth Cameras** | Close-range object scanning, MEP component capture, QA | 0.1–1 mm | Intel RealSense, Azure Kinect, Artec |

**Trend:** The industry is shifting from pure geometric precision (photogrammetry + LiDAR) toward **hybrid neural representations** (NeRF/3DGS) that prioritize visual context and real-time rendering, while new methods (SuGaR, Gaussian Opacity Fields) are closing the geometry-extraction gap.

---

## 2. Neural Radiance Fields (NeRF) in Construction

### What is NeRF?
NeRF represents scenes as continuous volumetric radiance fields encoded in MLP weights, enabling photorealistic novel-view synthesis from sparse images. It does not natively produce CAD-ready geometry but excels at view-dependent rendering.

### Construction-Specific Applications & Papers
| Paper / Work | Contribution | Venue / Year |
|---|---|---|
| **NeRF-Con** (Jeon et al.) | NeRF for automated construction progress monitoring; compares rendered views against BIM | ISARC 2024 |
| **NeRF-based scene understanding synced with BIM** | Orthogonal view generation from smartphone video; automated BIM-guided segmentation and progress evaluation; 1–2.2% measurement error | *Automation in Construction*, 2025 |
| **ALPMS (Activity-Level Progress Monitoring)** | Uses NeRF to synthesize orthographic views for semantic segmentation of construction activities; <6% mean absolute error on percent-complete | *Automation in Construction*, 2023 |
| **PlatoNeRF** | Single-view two-bounce LiDAR for 3D reconstruction | arXiv 2023 |
| **Urban Radiance Fields** | Large-scale outdoor radiance fields relevant to built environments | CVPR 2022 |

### Companies & Products Using NeRF
- **NVIDIA** — Neuralangelo, Instant-NGP (research tools, not construction-specific but applicable)
- **Luma AI** — Cloud NeRF/GS capture from smartphone video
- **Polycam** — Mobile NeRF/GS reconstruction
- **XGRIDS** — Industrial 3D reconstruction using GS/NeRF pipelines

### Key GitHub Repositories
- `nerfstudio-project/nerfstudio` — Unified NeRF/GS framework (UC Berkeley / NVIDIA)  
  [nerfstudio-project/nerfstudio](https://github.com/nerfstudio-project/nerfstudio)
- `NVlabs/instant-ngp` — NVIDIA Instant-NGP (hash-grid NeRF)  
  [NVlabs/instant-ngp](https://github.com/NVlabs/instant-ngp)
- `NVlabs/neuralangelo` — High-fidelity neural surface reconstruction  
  [NVlabs/neuralangelo](https://github.com/NVlabs/neuralangelo)
- `yenchenlin/nerf-pytorch` — Educational PyTorch NeRF
- `MatrixBrain/awesome-NeRF` — Curated paper list  
  [MatrixBrain/awesome-NeRF](https://github.com/MatrixBrain/awesome-NeRF)

---

## 3. 3D Gaussian Splatting (3DGS) in Construction

### What is 3DGS?
3DGS represents scenes with millions of explicit 3D Gaussian primitives (position, covariance, opacity, spherical harmonics). It initializes from SfM point clouds, optimizes via differentiable rasterization, and renders at **60–100+ FPS**—orders of magnitude faster than NeRF.

### Construction Applications
- **Real-time site visualization:** Photorealistic digital twins rendered in-browser or on-device.
- **As-built documentation:** Rapid capture from 360° video or drone imagery.
- **Heritage / facility documentation:** Complements TLS where geometric precision is less critical than visual fidelity.
- **Progress monitoring:** Emerging research (e.g., 3DGS for construction sites on ResearchGate, 2024).

### Key Papers & Methods
| Method | Contribution | Link |
|---|---|---|
| [**3D Gaussian Splatting for Real-Time Radiance Field Rendering** (Kerbl et al., SIGGRAPH 2023 Best Paper)](https://github.com/graphdeco-inria/gaussian-splatting) | Foundational method | [graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting) |
| [**SuGaR** (Guédon & Lepetit, CVPR 2024)](https://github.com/Anttwo/SuGaR) | Surface-aligned Gaussians + fast mesh extraction via Poisson reconstruction; enables editable meshes | [Anttwo/SuGaR](https://github.com/Anttwo/SuGaR) |
| [**Gaussian Opacity Fields** (Yu et al.)](https://github.com/autonomousvision/gaussian-opacity-fields) | GS-based surface reconstruction | [autonomousvision/gaussian-opacity-fields](https://github.com/autonomousvision/gaussian-opacity-fields) |
| [**2D Gaussian Splatting** (Huang et al.)](https://github.com/hbb1/2d-gaussian-splatting) | Surface reconstruction from 2D Gaussians | [hbb1/2d-gaussian-splatting](https://github.com/hbb1/2d-gaussian-splatting) |
| **Streaming Real-Time Rendered Scenes as 3D Gaussians** (2026) | Online Gaussian model construction from engine-native observations | arXiv:2604.02851 |

### Key Repositories
- Official 3DGS: `graphdeco-inria/gaussian-splatting`  
  [graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)
- `nerfstudio-project/gsplat` — CUDA-accelerated standalone rasterizer used by Nerfstudio
- `Anttwo/SuGaR` — Mesh extraction from 3DGS

---

## 4. Key Open-Source 3D Reconstruction Tools / Frameworks

| Tool | Category | GitHub / URL | Notes |
|---|---|---|---|
| [**COLMAP**](https://github.com/colmap/colmap) | SfM + MVS (traditional) | [colmap/colmap](https://github.com/colmap/colmap) | Industry standard for camera pose estimation; used by NeRF/3DGS pipelines |
| [**OpenMVG**](https://github.com/openMVG/openMVG) | SfM library | [openMVG/openMVG](https://github.com/openMVG/openMVG) | Foundational; AliceVision is based on it |
| [**AliceVision / Meshroom**](https://github.com/alicevision/Meshroom) | End-to-end photogrammetry | [alicevision/Meshroom](https://github.com/alicevision/Meshroom) | Node-based GUI; now includes Gaussian Splatting plugin (2025) and semantic segmentation |
| [**nerfstudio**](https://github.com/nerfstudio-project/nerfstudio) | NeRF + GS framework | [nerfstudio-project/nerfstudio](https://github.com/nerfstudio-project/nerfstudio) | Apache 2.0; CUDA accelerated; COLMAP integration; used by ILM, NVIDIA |
| [**gaussian-splatting (official)**](https://github.com/graphdeco-inria/gaussian-splatting) | 3DGS reference | [graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting) | SIGGRAPH 2023 Best Paper |
| [**SuGaR**](https://github.com/Anttwo/SuGaR) | Mesh-from-GS | [Anttwo/SuGaR](https://github.com/Anttwo/SuGaR) | Poisson mesh extraction in minutes |
| [**Open3D**](https://github.com/isl-org/Open3D) | 3D data processing | [isl-org/Open3D](https://github.com/isl-org/Open3D) | Point cloud visualization, SLAM, reconstruction pipelines |
| [**PCL (Point Cloud Library)**](https://github.com/PointCloudLibrary/pcl) | Point cloud processing | [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl) | Segmentation, registration, feature extraction |
| [**ORB-SLAM3**](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Visual / VI-SLAM | [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Multi-map, monocular/stereo/RGB-D, real-time |
| [**Neuralangelo**](https://github.com/NVlabs/neuralangelo) | Neural surface recon | [NVlabs/neuralangelo](https://github.com/NVlabs/neuralangelo) | High-fidelity large-scale reconstruction |
| [**Instant-NGP**](https://github.com/NVlabs/instant-ngp) | Hash-based NeRF | [NVlabs/instant-ngp](https://github.com/NVlabs/instant-ngp) | Minutes-scale training |
| [**OpenMVS**](https://github.com/cdcseacave/openMVS) | Dense reconstruction | [cdcseacave/openMVS](https://github.com/cdcseacave/openMVS) | Companion to OpenMVG |

---

## 5. How 3D Reconstruction Feeds into BIM / VDC Workflows

The integration pipeline is commonly called **Scan-to-BIM** or **Reality Capture-to-VDC**:

```
Reality Capture (LiDAR / Photo / Video / Drone)
        ↓
Point Cloud Registration & Georeferencing (COLMAP / CloudCompare / Recap)
        ↓
Point Cloud Pre-processing (denoising, subsampling, segmentation)
        ↓
Semantic Segmentation & Classification (AI: PointNet++, RandLA-Net, SAM)
        ↓
Feature Extraction (RANSAC for planes/cylinders, Hough Transform for pipes)
        ↓
Parametric BIM Object Generation (Revit families, IFC export)
        ↓
As-Built BIM / Digital Twin (LOD 300–500)
```

### Key Workflow Integrations
- **Progress Monitoring:** Compare as-built point clouds / NeRF renders against 4D BIM. Research shows occupancy-based methods and NeRF-rendered orthographic views enable activity-level percent-complete measurement.
- **As-Built Modeling:** LOD 500 deliverables require field-verified models. Automated pipelines (e.g., Cloud2BIM, EdgeWise) reduce manual tracing.
- **Clash Detection:** High-density reconstructions fed into Navisworks / Solibri for as-built vs. design validation.
- **Immersive Review:** NeRF/3DGS models streamed to stakeholders for virtual walkthroughs without heavy CAD software.

---

## 6. Companies Productizing 3D Reconstruction for Construction

| Company | Product / Focus | Technology | Key Differentiator |
|---|---|---|---|
| **OpenSpace** | Visual Intelligence Platform (Capture, Field, Track, BIM+) | 360° photo + AI alignment | 15-min processing; AI Autolocation; BIM compare; progress tracking |
| **Cupix** | 3D Digital Twin Platform | 360° video + photogrammetry | Unified platform for any point cloud source; Insta360 integration |
| **Matterport** | 3D Capture & Digital Twins | Proprietary 3D camera + cloud | Strong in real estate/facilities; moving into construction |
| **Polycam** | Mobile 3D scanning app | Photogrammetry + LiDAR (iPhone) | Consumer/prosumer; exports PLY/OBJ/Gaussian Splats |
| **RealityCapture** | Photogrammetry software | SfM-MVS | Extremely fast; license model popular with pros |
| **Pix4D** | Drone photogrammetry | SfM-MVS + machine learning | Survey-grade outputs; PIX4Dcloud |
| **ClearEdge3D (Topcon)** | EdgeWise | Automated scan-to-BIM | Up to 73% workflow acceleration; auto-extracts pipes, ducts, walls |
| **NavVis** | Mobile mapping / indoor digitization | SLAM + LiDAR | Large-scale indoor digital twins |
| **FARO** | Laser scanners + Scene software | TLS | High-precision as-built capture |
| **Leica Geosystems** | BLK360, RTC360, Cyclone | TLS + mobile | Survey-grade hardware + software |
| **BIMIT / Cloud2BIM** | Automated scan-to-BIM | AI + synthetic training data | Upload point cloud → receive IFC/Revit; claims 1 hr/GB |
| **Reconstruct** | Visual Command Center | Reality capture + AI | Time-series comparison; sub-inch accuracy alignment |
| **XGRIDS** | 3D reconstruction + rendering | NeRF / GS / LiDAR | Lixel handheld LiDAR + real-time modeling |

---

## 7. State of Automated Scan-to-BIM

### Current Reality (2025–2026)
Automated scan-to-BIM is **semi-automated**, not fully autonomous. The best systems achieve **50–75% automation** for repetitive elements (pipes, ducts, walls, structural steel), with human QA/QC required for complex or occluded MEP systems.

### Key AI Technologies
| Task | Methods | Accuracy / Status |
|---|---|---|
| Semantic Segmentation | PointNet++, RandLA-Net, KPConv, SegFormer-3D | >90% on standard classes; struggles with clutter |
| Object Detection (pipes, ducts) | RANSAC + Hough Transform + template matching | Mature for cylindrical/conical objects |
| Slab / Wall Detection | ML + heuristic slicing (Cloud2BIM uses synthetic house training) | Reliable for regular structures; fails on irregular heritage |
| Opening Detection (doors/windows) | Deep learning on orthographic projections | Emerging |
| Parametric Generation | IFCOpenShell + Revit API automation | Workflow integration available |

### Notable Products
- **ClearEdge3D EdgeWise** — Auto-extracts pipes, ducts, walls, conduit; direct Revit/Plant 3D export; claims up to 73% time savings.
- **Aurivus** — AI plugin for Revit; “speed draw” pipes and beams from point clouds.
- **BIMIT Engine 3.0** — Claims ~1 hour per GB of point cloud for architectural models.
- **Cloud2BIM** — Uses synthetic data training + floor-by-floor processing to avoid full 3D neural network reconstruction (computationally too heavy).

### Research Benchmark
- A *ScienceDirect* study on automated BIM reconstruction reports **94.6% accuracy** in identifying/classifying structural elements (walls, floors, columns) using deep learning.

### Gaps
- **MEP complexity:** Intertwined small-diameter pipes, insulation, custom equipment remain largely manual.
- **LOD 350–400:** High-detail connection points, hangers, supports are not yet reliably auto-generated.
- **Non-standard architecture:** Heritage, organic shapes, adaptive facades lack training data.

---

## 8. LLMs / SLMs Combined with 3D Reconstruction

### Emerging Approaches
The intersection is nascent but rapidly growing. Three integration patterns are emerging:

#### A. LLMs for Point Cloud / NeRF Understanding
| Method | Approach | Notes |
|---|---|---|
| **LLaNA** | Directly ingests NeRF MLP weights into LLaMA-2/13B for captioning, Q&A, zero-shot classification | First MLLM for NeRF; outperforms image/point-cloud baselines |
| **PointLLM** | Point encoder → LLM for 3D object understanding | Object-level, not scene-scale |
| **3D-LLM** | Aggregates 3D features from rendered 2D images; adds location tokens | Scene-level understanding |
| **Chat3D / Chat3D-v2** | Object-centric scene representation for LLM interaction | Urban/construction relevance |
| **Chat3D (Construction)** | Translates semantic segmentation results into textual prompts for LLM analysis; generates eco-construction reports | *ISPRS JPRS*, 2024 — directly applied to urban construction |
| **3DGraphLLM** | Semantic graphs + LLM for 3D scene understanding | Leverages object relationships |
| **Scene-LLM** | Extends LLM for 3D visual understanding and reasoning | General purpose |

#### B. LLMs for Scan-to-BIM Orchestration
- **Local AI for Scan-to-BIM** (Theseus thesis, 2025): Open-source LLM chatbot (Haystack + Gradio) with function calling on IFC and point clouds. Uses RAG for document retrieval + PyTorch Geometric for point cloud segmentation. Demonstrates LLM as orchestrator for BIM pipelines.
- **RAG + BIM:** LLMs query local construction documents, compare against IFC metadata, and trigger point cloud processing scripts.

#### C. Natural Language Queries on 3D Scenes
- **Text-driven segmentation:** CLIP/SAM + 3DGS/NeRF enables “select all pipes” or “show me cracks” via natural language.
- **NVIDIA Omniverse + LLM:** Emerging integrations where LLMs generate USD scene descriptions from text, which can reference NeRF/GS assets.

### Key Repositories
- [haotian-liu/LLaVA](https://github.com/haotian-liu/LLaVA) — General vision-language model (baseline for render-based NeRF QA)
- [OpenRobotLab/PointLLM](https://github.com/OpenRobotLab/PointLLM) — Point cloud LLM
- [UMass-Foundation-Model/3D-LLM](https://github.com/UMass-Foundation-Model/3D-LLM) — 3D LLM baseline

---

## 9. Datasets for 3D Reconstruction in Construction

### Real-World / Benchmark Datasets
| Dataset | Content | Scale | Application |
|---|---|---|---|
| **NeRFBK** (3DOM-FBK) | Industrial objects, heritage, urban aerial; paired with LiDAR/TLS GT | Multi-scene | Benchmarking NeRF geometric accuracy |
| **Building3D** (UCalgary, ICCV 2023) | 160,000 roof point clouds; 100+ roof types | Urban-scale | Roof reconstruction from aerial LiDAR |
| **Hessigheim 3D (H3D)** | Annotated village UAS imagery + LiDAR | Village-scale | Semantic segmentation benchmark |
| **Semantic3D** | 1B+ points, 8 classes | Multi-scan outdoor | Point cloud semantic segmentation |
| **CRBeDaSet** | Close-range image-based 3D modeling benchmark | Object-scale | Accuracy assessment |
| **SYNBUILD-3D** (2025) | Synthetic multi-modal buildings at LoD 4 | 6,200+ models | Generative modeling, reconstruction training |
| **SS3DM** (NeurIPS 2024) | Synthetic street-view meshes from CARLA | Street-scale | Surface reconstruction benchmark |
| **Tanks and Temples** | Indoor/outdoor large-scale scenes | ~10 scenes | NeRF / MVS benchmark |
| **DTU** | Object-centric multi-view | ~80 scenes | Neural surface reconstruction |

### Construction-Specific Data Challenges
- **Lack of large-scale annotated construction point clouds:** Most public datasets are urban or object-scale, not active job sites.
- **Dynamic scenes:** Construction datasets rarely capture temporal progressions with ground truth.
- **Synthetic data gap:** SYNBUILD-3D and Cloud2BIM’s internal synthetic houses are early efforts, but domain randomization for construction is immature.

---

## 10. Precision / Accuracy Requirements in Construction

### BIM LOD & Tolerance Context
| LOD | Phase | Accuracy / Purpose |
|---|---|---|
| LOD 100 | Pre-design | Conceptual; no tolerance requirements |
| LOD 200 | Schematic | Approximate quantities; ±5–10 cm acceptable |
| LOD 300 | Design Development | 3D coordination; **±3 mm to ±12 mm** typical |
| LOD 350 | Coordination | Interfaces defined; clash detection ready |
| LOD 400 | Fabrication | Shop drawings; **±1–3 mm** for prefab |
| LOD 500 | As-Built | Field-verified; **±5 mm to ±12 mm** typical |

### Industry Tolerance References
- **USACE / DCAMM:** Model elements within **1/8" (3 mm)** of actual location for design; **±5 mm** for general tolerances.
- **SI BIM Guidelines (2024):** Existing conditions modeled to LOD 300 with **LOA 12 mm (½")**; as-built LOD 500 with **LOA 12 mm**.
- **Adaptive Reality Sync BIM:** ±2 cm for structural elements; **±5 mm** for critical connection points.
- **Reinforced concrete (JICA specs):** Variation from vertical 5 mm in 3 m; 8 mm in 6 m.
- **3D printing / additive:** ±0.1–0.2 mm (not typical construction, but shows upper bound).

### How Reconstruction Modalities Compare
| Modality | Typical Accuracy | Best For |
|---|---|---|
| TLS (FARO/Leica) | 1–3 mm | As-built LOD 500, deformation monitoring |
| Mobile LiDAR | 1–3 cm | Large indoor/outdoor capture, logistics |
| Photogrammetry (SfM-MVS) | 1–5 cm (without GCPs); sub-cm (with GCPs) | Façade, terrain, progress monitoring |
| Smartphone LiDAR (iPhone) | 1–3 cm RMSE | Quick documentation, informal surveys |
| NeRF / 3DGS | View-synthesis quality high; absolute metric accuracy variable (~cm–dm) | Visualization, not yet metrology |
| SLAM (ORB-SLAM3) | 2–8 cm drift | Real-time mapping, robotics |

### Critical Insight
NeRF and 3DGS currently prioritize **visual fidelity over geometric metrology**. For construction, this means:
- They are excellent for **stakeholder communication, progress photos, and immersive review**.
- They are **not yet suitable** for fabrication-level (LOD 400) or as-built verification (LOD 500) without GCPs, bundle adjustment, or fusion with surveyed point clouds.

---

## TECHNICAL GAP ANALYSIS

### What Works Today
1. **High-precision capture:** TLS + mobile LiDAR reliably deliver LOD 300–500 accuracy.
2. **Semi-automated scan-to-BIM:** EdgeWise, Aurivus, BIMIT automate 50–75% of standard MEP/architectural elements.
3. **Realistic visualization:** 3DGS enables real-time photorealistic site twins from consumer cameras.
4. **SLAM for robotics:** ORB-SLAM3, LIO-SAM enable real-time mapping for UGVs/UAVs on site.

### Critical Gaps
| Gap | Severity | Description |
|---|---|---|
| **NeRF/3DGS → CAD geometry** | **High** | No native parametric BIM export. Mesh extraction (SuGaR) is promising but not construction-tolerant. |
| **Metric accuracy of neural methods** | **High** | NeRF/3DGS lack survey-grade georeferencing. Requires fusion with TLS/GCPs. |
| **Dynamic scene handling** | **High** | Construction sites change daily. NeRF/3DGS assume static scenes; 4D NeRF / spacetime Gaussians are research-stage. |
| **Automated MEP modeling** | **Medium-High** | Small-diameter pipes, conduit, cable trays in cluttered ceilings remain manual. |
| **LLM + 3D reasoning at scale** | **Medium** | Chat3D, LLaNA show promise but are limited to object/small-scene level. No construction-site-scale LLM exists. |
| **Construction-specific training data** | **Medium** | Public datasets are urban or object-scale. Active job sites with temporal GT are rare. |
| **Real-time scan-to-BIM** | **Medium** | Current pipelines are batch-oriented. Real-time semantic segmentation + instant BIM generation is unsolved. |
| **Standardized evaluation** | **Medium** | No unified benchmark for “NeRF/3DGS accuracy vs. BIM tolerance” exists. |

### Strategic Opportunities
1. **Hybrid pipelines:** Use 3DGS/NeRF for visualization + TLS for metrology, fused in a common coordinate system.
2. **LLM orchestrators:** Deploy local LLMs (e.g., LLaMA-3) with RAG over project documents and function-calling to IFC/point-cloud tools.
3. **Synthetic data engines:** Build construction-specific synthetic datasets (like SYNBUILD-3D) to train segmentation and reconstruction models.
4. **4D neural fields:** Extend spacetime Gaussian splatting or D-NeRF to construction progress monitoring with change detection.
5. **Gaussian Splatting → BIM:** Investigate SuGaR-style mesh extraction + RANSAC primitive fitting as a path from splats to Revit families.

---

## SUMMARY FOR SWARM INTEGRATION

**To the VDC/LLM agents in this swarm:**
- **3D Reconstruction is the sensor layer.** It feeds reality into the digital twin.
- **NeRF/3DGS are the visualization layer.** They are not yet the fabrication layer.
- **Scan-to-BIM is the bottleneck.** AI can automate 50–75% of standard elements; MEP clutter and non-standard forms remain manual.
- **LLMs are the interface layer.** They can orchestrate pipelines (document retrieval → IFC query → point cloud segmentation) but do not yet natively “understand” large-scale 3D construction scenes end-to-end.
- **The convergence point:** A system that captures a site with 360° video → trains 3DGS in minutes → extracts mesh → segments semantically → auto-generates parametric BIM objects → and allows natural language querying via LLM. **Each step exists in isolation; the integrated pipeline does not.**

---


## References

- [Anttwo/SuGaR](https://github.com/Anttwo/SuGaR)
- [MatrixBrain/awesome-NeRF](https://github.com/MatrixBrain/awesome-NeRF)
- [NVlabs/instant-ngp](https://github.com/NVlabs/instant-ngp)
- [NVlabs/neuralangelo](https://github.com/NVlabs/neuralangelo)
- [OpenRobotLab/PointLLM](https://github.com/OpenRobotLab/PointLLM)
- [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl)
- [UMass-Foundation-Model/3D-LLM](https://github.com/UMass-Foundation-Model/3D-LLM)
- [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3)
- [alicevision/Meshroom](https://github.com/alicevision/Meshroom)
- [autonomousvision/gaussian-opacity-fields](https://github.com/autonomousvision/gaussian-opacity-fields)
- [cdcseacave/openMVS](https://github.com/cdcseacave/openMVS)
- [colmap/colmap](https://github.com/colmap/colmap)
- [graphdeco-inria/gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)
- [haotian-liu/LLaVA](https://github.com/haotian-liu/LLaVA)
- [hbb1/2d-gaussian-splatting](https://github.com/hbb1/2d-gaussian-splatting)
- [isl-org/Open3D](https://github.com/isl-org/Open3D)
- [nerfstudio-project/nerfstudio](https://github.com/nerfstudio-project/nerfstudio)
- [openMVG/openMVG](https://github.com/openMVG/openMVG)
*Report compiled by 3D Reconstruction Domain Agent*  
*Sources: arXiv, Automation in Construction, ISARC, CVPR, SIGGRAPH, ISPRS, vendor documentation, GitHub repositories, industry BIM guidelines.*
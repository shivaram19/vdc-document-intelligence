# TRELO LABS RESEARCH BRIEF
## The "GPT Moment for Robotics" & Construction Robotics Data Landscape (2024–2026)

**Prepared for:** Founder meeting on construction robotics data management  
**Date:** April 23, 2026  

---

## 1. THE "GPT MOMENT FOR ROBOTICS" — THE THESIS

The thesis is straightforward: **Just as LLMs like ChatGPT demonstrated emergent generalization from internet-scale text data, robotics is approaching an inflection point where foundation models trained on massive multimodal physical-interaction datasets will produce general-purpose robot "brains" that work across embodiments, tasks, and environments.**

**Core arguments from YC and the broader ecosystem:**

- **Data scaling laws apply to robotics.** [Peter Chen (CEO, Covariant)](https://covariant.ai/insights/no-priors-podcast-building-foundation-models-in-the-physical-world/) argued in a November 2023 op-ed and on the *No Priors* podcast (January 2024) that AI robotics' "GPT moment" is near — driven by the combination of internet-scale vision-language pretraining + large robot demonstration datasets [1][2].
- **Generalist policies are replacing task-specific programming.** Instead of programming robots for each SKU or task, a single foundation model can control diverse robots given natural language instructions.
- **Investment is validating the thesis.** Physical AI / robot foundation model startups raised [**$2.2 billion in 2025 alone**](https://pitchbook.com/news/articles/drone-deals-fueled-vcs-139-surge-into-defense-robotics) (per PitchBook Q4 2025 data), with total robotics VC investment hitting [**$27.6 billion in 2025**](https://pitchbook.com/news/reports/q4-2025-robotics-physical-ai-vc-trends) (up from $13.7B in 2024) [3].

**[Sergey Levine](https://techcrunch.com/2026/03/27/physical-intelligence-is-reportedly-in-talks-to-raise-1-billion-again/) (Co-founder, Physical Intelligence) summarized it as: *"Think of it like ChatGPT, but for robots."*** [4]

---

## 2. YC COMPANIES & FRONT-RUNNERS DRIVING THIS

### The "Big Three" Foundation Model Companies

| Company | Founded | Key Model | Funding / Valuation | Founders / Backers |
|---------|---------|-----------|---------------------|-------------------|
| **[Physical Intelligence (π)](https://techcrunch.com/2026/03/27/physical-intelligence-is-reportedly-in-talks-to-raise-1-billion-again/)** | 2024 | π0, π0.5, π0.6 | **$1B+ raised, $11B valuation** (March 2026 talks) [5][6] | Sergey Levine (Berkeley), Chelsea Finn (Stanford), Karol Hausman (ex-DeepMind). Backers: OpenAI, Jeff Bezos, CapitalG, Thrive, Lux |
| **[Skild AI](https://techfundingnews.com/softbank-and-nvidia-plan-1b-investment-in-skild-ai-at-14b-valuation/)** | May 2023 | Skild Brain | **$300M Series A at $15B** (July 2024); SoftBank negotiating $5B at ~$40B [7][8] | Deepak Pathak & Abhinav Gupta (CMU professors, ex-Meta). Backers: Lightspeed, Coatue, Bezos, SoftBank |
| **[Covariant](https://covariant.ai/about-us/)** | 2017 | RFM-1, Covariant Brain | **$222M total raised** (Series C extension April 2023) [9] | Pieter Abbeel (Berkeley), Peter Chen, Rocky Duan, Tianhao Zhang (ex-OpenAI) |

**Physical Intelligence** is the purest play on the thesis: zero commercial product, research-first, open-sourced π0 weights (Feb 2025), and models trained on 7+ robot platforms across 68 tasks. Their π0.6 model (Nov 2025) introduced **RL tokens** — enabling sub-millimeter precision tasks after just 15 minutes of training [5].

**Skild AI** is the commercialization-focused competitor, already generating **$28.5M in revenue** through security, warehousing, and manufacturing deployments [8]. In 2025, they partnered with NVIDIA to deploy on Foxconn's Blackwell production lines in Houston [5].

**Covariant** launched **RFM-1** in March 2024 — marketed as "the first commercial Robotics Foundation Model" — and signed a non-exclusive licensing deal with Amazon in 2024, which also hired ~25% of Covariant's workforce [9][10].

### YC Batch Companies (2024–2026)

YC is actively funding robotics AI infrastructure and applications [11]:

- **[Human Archive](https://www.ycombinator.com/launches/PeP-human-archive-the-world-s-largest-multimodal-robotics-dataset)** (YC W26) — Building multimodal data capture infrastructure for embodied AI. Collecting 8,000 hours/day across construction, homes, restaurants, hotels, and industrial environments. Signed national partnerships to scale to 50,000+ data collectors [12].
- **Mbodi AI** — "Teach robots new skills through natural language." Combines generative AI + agent orchestration for industrial automation.
- **MorphoAI** — AI-powered platform for engineers building new robots; GenAI for machine design from Harvard/MIT research.
- **Zeon Systems** — AI-powered lab automation robotics.

---

## 3. VISION-LANGUAGE-ACTION (VLA) MODELS EXPLAINED

**Definition:** VLA models extend Vision-Language Models (VLMs) by integrating robot actions into the token space, enabling direct generation of low-level motor commands from visual observations and natural language instructions [13].

### How They Work
1. **Input:** Camera images + natural language instruction (e.g., "pick up the red block")
2. **Backbone:** Pretrained VLM (e.g., PaLI-Gemma, Llama 2, Qwen3-VL) provides semantic understanding
3. **Action Head:** Converts latent representations into robot actions — either:
   - **Autoregressive token prediction** ([RT-2](https://arxiv.org/abs/2307.15818), [OpenVLA](https://arxiv.org/abs/2406.09246) — discretize actions into tokens)
   - **Diffusion-based generation** (Octo, RDT-1B — iteratively denoise action trajectories)
   - **Flow matching** (π0 — generates continuous action distributions efficiently)

### Key Technical Breakthroughs
- **Web-to-robot transfer:** [RT-2](https://arxiv.org/abs/2307.15818) demonstrated that co-training on internet-scale VQA data + robot trajectories enables emergent generalization to novel objects and instructions [14].
- **Cross-embodiment:** [OpenVLA](https://arxiv.org/abs/2406.09246) (7B params) and π0 support multiple robot types out-of-the-box via parameter-efficient fine-tuning [15][16].
- **Action chunking:** Predicting short action horizons (e.g., 50 timesteps) at once reduces inference frequency while maintaining smooth control [17].

---

## 4. STATE OF FOUNDATION MODELS FOR ROBOTICS

| Model | Org / Lab | Params | Architecture | Release | Key Feature |
|-------|-----------|--------|--------------|---------|-------------|
| **RT-1** | Google DeepMind | 35M | Transformer (discretized actions) | Dec 2022 | First large-scale transformer policy for multi-task manipulation [14] |
| **RT-2** | Google DeepMind | 55B / 5B | VLM co-finetuning (action as text tokens) | Jul 2023 | Emergent semantic reasoning; 3x improvement over RT-1 in skill generalization [14] |
| **RT-X / RT-2-X** | Open X-Embodiment Collaboration | 55B | Same as RT-2, trained on

## References

1. [Covariant — No Priors Podcast: Building foundation models in the physical world](https://covariant.ai/insights/no-priors-podcast-building-foundation-models-in-the-physical-world/)
2. [Covariant — The Industry blog archive](https://covariant.ai/insights/the-industry/)
3. [PitchBook — Q4 2025 Robotics & Physical AI VC Trends](https://pitchbook.com/news/reports/q4-2025-robotics-physical-ai-vc-trends)
4. [TechCrunch — Physical Intelligence in talks to raise $1B at $11B valuation](https://techcrunch.com/2026/03/27/physical-intelligence-is-reportedly-in-talks-to-raise-1-billion-again/)
5. [The LEC — Physical Intelligence valued at $11B as robotics AI investment surges](https://www.thelec.net/news/articleView.html?idxno=6214)
6. [TechFundingNews — Physical Intelligence $1B raise at $11B valuation](https://techfundingnews.com/physical-intelligence-1b-raise-11b-valuation-founders-fund-lightspeed/)
7. [TechFundingNews — SoftBank and Nvidia plan $1B investment in Skild AI at $14B valuation](https://techfundingnews.com/softbank-and-nvidia-plan-1b-investment-in-skild-ai-at-14b-valuation/)
8. [Wellows — Top 30 Tech Startups redefining AI & Robotics in 2026](https://wellows.com/blog/tech-startups/)
9. [Covariant — About Us (funding history)](https://covariant.ai/about-us/)
10. [SudoRemove — Covariant company profile & Amazon deal](https://sudoremove.com/en/knowledge/companies/covariant/)
11. [Y Combinator — Companies](https://www.ycombinator.com/companies)
12. [Y Combinator — Human Archive launch](https://www.ycombinator.com/launches/PeP-human-archive-the-world-s-largest-multimodal-robotics-dataset)
13. [Robotics Center AI — VLA Models Explained](https://www.roboticscenter.ai/blog/vla-models-explained)
14. [arXiv — RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/abs/2307.15818)
15. [arXiv — OpenVLA: An Open-Source Vision-Language-Action Model](https://arxiv.org/abs/2406.09246)
16. [Physical Intelligence — π0 blog](https://www.physicalintelligence.company/)
17. [Google DeepMind — RT-2 blog](https://deepmind.google/discover/blog/rt-2-new-model-translates/)

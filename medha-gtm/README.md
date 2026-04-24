# Medha Go-to-Market System
## Modular Customer Research, Outreach & Sales Playbooks

**Architecture:** Each file has exactly ONE responsibility. Add new platforms, markets, or tactics by creating new files — never modify existing ones.

```
medha-gtm/
├── README.md                 ← You are here
├── research/                 ← Market intelligence (read-only, evidence-based)
│   ├── pain-points.md        ← JTBD framework + 5 core jobs
│   ├── market-data.md        ← India + global market statistics
│   ├── icp/                  ← Ideal Customer Profiles (4 tiers)
│   └── citations.md          ← 20 research sources
├── platforms/                ← Per-platform intelligence (10 platforms)
│   ├── README.md             ← Platform comparison matrix
│   ├── reddit.md
│   ├── discord.md
│   ├── linkedin.md
│   ├── youtube.md
│   ├── forums.md
│   ├── glassdoor-jobs.md
│   ├── government.md
│   ├── india-specific.md
│   └── software-marketplaces.md
├── tactics/                  ← Channel-agnostic strategies
│   ├── seo-geo.md
│   ├── content-strategy.md
│   ├── pricing-packaging.md
│   └── metrics-kpis.md
├── meetings/                 ← Founder sales execution
│   ├── discovery-questions.md
│   ├── demo-script.md
│   ├── objection-handling.md
│   ├── commitment-ladder.md
│   └── response-decoder.md
├── outreach/                 ← Copy-paste templates
│   ├── email-templates.md
│   ├── linkedin-sequences.md
│   └── whatsapp-scripts.md
└── plans/
    ├── 90-day-action-plan.md
    └── 30-day-platform-blitz.md
```

## Principles

1. **Single Responsibility** — Each file answers ONE question. `reddit.md` only covers Reddit. Nothing else.
2. **Open/Closed** — Add a new platform? Create `tiktok.md`. Never touch existing files.
3. **Composability** — A sales rep reads `icp/tier-1.md` + `platforms/linkedin.md` + `outreach/linkedin-sequences.md` to execute.
4. **Evidence-Based** — Every claim in `research/` links to a source in `citations.md`.
5. **Living Documents** — Each file has a `Last Updated` header. Update in place. Never duplicate.

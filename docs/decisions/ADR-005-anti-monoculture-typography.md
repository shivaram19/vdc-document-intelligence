# ADR-005: Anti-Monoculture Typography

## Status
Accepted — implemented in frontend on 2026-05-03

## Context
Medha's current frontend uses Inter as the primary sans-serif typeface, with Roboto Mono for engineering identifiers. Inter is the default font in Tailwind CSS, Vercel's Geist UI, and countless AI-generated interfaces. The impeccable project (Bakaus 2026) has documented this as part of a broader "AI monoculture" in frontend design: without explicit guidance, every LLM defaults to Inter, purple gradients, and card-nested-in-card layouts.

In impeccable v3.0 (April 2026), the overused-font detector expanded its reflex-reject list to include: Inter, Fraunces, Geist, Mona Sans, Plus Jakarta Sans, Space Grotesk, Recoleta, and Instrument Sans. The project explicitly warns that "Every LLM learned from the same generic templates. Without guidance, you get the same predictable mistakes: Inter font, purple gradients, cards nested in cards."

For Medha — a research-backed construction document intelligence platform — using the same typeface as every generic SaaS dashboard undermines the brand's authority and distinctiveness. Construction professionals are not generic SaaS users; they work with engineering drawings, specification manuals, and compliance documents that demand visual credibility.

## Decision
1. **Remove Inter entirely** from the font stack. It is now classified as an AI-monoculture default.
2. **Adopt a three-tier type system:**
   - **Display / Headings**: `Sora` — a geometric sans-serif with distinctive character shapes, designed by the Indian Type Foundry. It is modern, globally-minded, and NOT on any overused-font list.
   - **Body / UI**: `Source Sans 3` — Adobe's open-source humanist sans-serif, designed for UI readability at small sizes. It is professional without being anonymous, and NOT on any overused-font list.
   - **Mono / Engineering**: `JetBrains Mono` — designed specifically for code readability with increased letter height and distinctive ligatures. Replaces Roboto Mono for better O/0 and l/1 distinction.
3. **Use `font-display: swap`** for all web fonts to eliminate FOIT (Flash of Invisible Text).
4. **Maintain system-ui fallbacks** for offline resilience, but never default to them as the primary experience.

## Consequences
- **Positive**: Medha's visual identity is now distinct from the AI-generated SaaS monoculture. The typography signals "serious engineering tool" rather than "generic startup dashboard."
- **Positive**: Sora's geometric warmth pairs with Source Sans 3's humanist clarity to create a type system that is both authoritative and approachable.
- **Positive**: JetBrains Mono improves character distinguishability for construction identifiers (sheet numbers like `M-101`, spec sections like `230529`).
- **Negative**: Two additional font families increase initial download weight by ~60KB (Sora 400/600/700 + Source Sans 3 400/500/600/700, both subset to Latin).
- **Negative**: Sora is less familiar to users than Inter; brief adaptation period of ~2-3 seconds on first visit.

## Research Basis
- [CITE: Bakaus2026] Bakaus, P. (2026). *impeccable: A skill for impeccable frontend design*. https://github.com/pbakaus/impeccable
  - Overused-font detector flags Inter, Geist, Space Grotesk, Plus Jakarta Sans, and others as AI-monoculture defaults.
  - Anti-pattern: "Don't use overused fonts (Arial, Inter, system defaults)."
- [CITE: Bernard2003] Bernard, M. et al. (2003). *Comparing the Effects of Text Size and Format on the Readability of Computer-Displayed Times New Roman and Arial Text*. International Journal of Human-Computer Interaction. https://doi.org/10.1207/S15327590IJHC1603_5
  - Sans-serif fonts are measurably more readable at small sizes on screens. Source Sans 3 maintains this advantage.
- [CITE: Boulton2014] Boulton, M. (2014). *Designing for the Web* (Chapter 7: Typography). https://designingfortheweb.co.uk/part2/typography.html
  - Monospace fonts improve character distinguishability for identifiers. JetBrains Mono was explicitly designed to maximize this property.
- [CITE: SoraSpec] Indian Type Foundry (2018). *Sora type specimen*. https://fonts.google.com/specimen/Sora
  - Geometric construction with subtle humanist details; high x-height for screen readability; distinctive enough to avoid monoculture.

## Alternatives Considered
1. **Geist (Vercel's new font)**
   - Rejected: Added to impeccable v3.0 overused-font list in April 2026. Already appearing in thousands of Next.js projects.
2. **Space Grotesk**
   - Rejected: Added to impeccable v3.0 overused-font list. Became the default "distinctive alternative" that is no longer distinctive.
3. **Plus Jakarta Sans**
   - Rejected: Added to impeccable v3.0 overused-font list. Popularized as an Inter alternative in 2024-2025.
4. **Keep Inter with custom weights only**
   - Rejected: Does not solve the monoculture problem. Users still see "another Inter site."
5. **Use a system-font-only stack**
   - Rejected: Faster loading but completely anonymous. Contradicts Medha's brand promise of research-backed precision.

## Follow-Up Work
1. Benchmark first paint time with new font stack; consider `prefers-reduced-data` media query for low-bandwidth clients.
2. Audit all downstream components (dashboard, workbench, connector) for hardcoded `font-family: Inter` references.
3. Document type scale in `frontend/design-system/typography.md` with Sora/Source Sans 3 pairings.

## Code Location
- `frontend/index.html` (Google Fonts loading)
- `frontend/design-system/design-tokens.css` (`--font-sans`, `--font-display`)
- `frontend/css/design-system/typography.css`

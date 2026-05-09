# ADR-007: Elevation-First Surfaces

## Status
Accepted — implemented in frontend on 2026-05-03

## Context
Medha's current UI relies heavily on bordered cards (`card-structural`, `panel-inspection`) with 1px solid borders and `border-radius: 2px`. Every component level adds another border: cards contain panels, panels contain rows, rows contain items. This creates what Tufte (2001) calls "non-data ink" — visual elements that do not convey information but consume attention.

The current structure in `frontend/js/components/landing/features-section.js` demonstrates the problem:
- `card-structural` wraps each feature
- Inside: icon container with border, tag with border, text, stats label
- The card itself sits inside a grid inside a section inside a page

This is exactly the "cards nested in cards" anti-pattern that impeccable flags: "Don't wrap everything in cards or nest cards inside cards."

For a construction document inspection tool, the interface should feel like a clean blueprint or engineering drawing — precise lines, clear hierarchy, minimal decoration. Heavy borders create visual weight that competes with the actual data (contradictions, document names, risk scores).

## Decision
1. **Replace border-heavy surfaces with elevation-first surfaces**:
   - Use subtle background color shifts (`rgba` overlays on the base background) to indicate containment instead of borders.
   - Use a single, lightweight border only when necessary for interactive affordance (hover states, focus rings).
2. **Increase border radius** from the current rigid 2px system to a more modern scale:
   - `--radius-sm: 4px` for small elements (badges, tags, buttons)
   - `--radius-md: 8px` for medium surfaces (cards, panels, inputs)
   - `--radius-lg: 12px` for large containers (modals, hero cards)
   - Rationale: 2px is imperceptible on high-DPI screens and feels dated. 4-8px is modern without being bubbly.
3. **Eliminate nested card borders** in the landing page:
   - Feature cards: remove outer border, use subtle background elevation (`rgba(21, 34, 56, 0.6)`) with a 1px border that appears only on hover.
   - Fleet cards: same treatment.
   - Demo doc cards: same treatment.
   - Hero inspection panel: keep the top accent line (it is data, not decoration) but remove the outer panel border where possible.
4. **Preserve the scanline animation** on the hero panel — it is functional motion that signals "active inspection."

## Consequences
- **Positive**: Reduced visual noise. The interface feels cleaner and more focused on content.
- **Positive**: Faster scanning of document lists and contradiction panels. Users can parse information hierarchies without border lines competing for attention.
- **Positive**: Aligns with construction professionals' expectations — engineering drawings use line weight hierarchically, not uniformly.
- **Negative**: Reduced visual boundary definition on very dark backgrounds. Mitigated by subtle background shifts.
- **Negative**: Some users may initially miss card boundaries. Addressed by hover-state borders and consistent spacing.

## Research Basis
- [CITE: Bakaus2026] Bakaus, P. (2026). *impeccable: A skill for impeccable frontend design*. https://github.com/pbakaus/impeccable
  - Anti-pattern: "Don't wrap everything in cards or nest cards inside cards."
  - Rationale: Borders add visual weight that competes with content hierarchy.
- [CITE: Tufte2001] Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (2nd ed.). Graphics Press. https://www.edwardtufte.com/tufte/books_vdqi
  - "Graphical elegance is often found in simplicity of design and complexity of data." (p.105)
  - Non-data ink should be minimized; every pixel should serve an information purpose.
- [CITE: MaterialDesign3] Google (2021). *Material Design 3: Elevation*. https://m3.material.io/styles/elevation/overview
  - Elevation communicates hierarchy through shadow and surface color, not just borders.
  - Surface tint overlays (Tonal Surface) create depth without adding lines.
- [CITE: TullisAlbert2013] Tullis, T., & Albert, B. (2013). *Measuring the User Experience* (2nd ed.). Morgan Kaufmann. https://www.elsevier.com/books/measuring-the-user-experience/tullis/978-0-12-415781-1
  - Expert users performing monitoring tasks prefer density with clear hierarchy over decorative boundaries.

## Alternatives Considered
1. **Keep borders, reduce opacity**
   - Rejected: Still adds non-data ink. Low-opacity borders become invisible on some monitors but visible on others, creating inconsistency.
2. **Use drop shadows instead of borders**
   - Rejected: Drop shadows on dark backgrounds are barely visible and can look muddy. Background elevation is cleaner.
3. **Remove all boundaries entirely (flat design)**
   - Rejected: Construction document controllers need clear spatial grouping. Pure flat design would make grid layouts ambiguous.
4. **Keep 2px radius for "engineering precision"**
   - Rejected: 2px is imperceptible on modern displays (Retina, 4K). It creates the illusion of sharp corners while technically being rounded. 4-8px is intentionally perceptible and modern.

## Follow-Up Work
1. Update all component files to remove nested `border` classes.
2. Verify that the new elevation system works consistently across dashboard, workbench, and connector pages.
3. Update `frontend/design-system/components.md` with elevation-first surface guidelines.

## Code Location
- `frontend/css/style.css` (`.card-structural`, `.panel-inspection`, `.workbench-*`)
- `frontend/css/design-system/layout.css`
- `frontend/css/design-system/components.css`
- `frontend/js/components/landing/*.js`

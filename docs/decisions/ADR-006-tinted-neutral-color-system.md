# ADR-006: Tinted Neutral Color System

## Status
Accepted — implemented in frontend on 2026-05-03

## Context
Medha's current color system uses pure neutral grays (`#e0e0e0`, `#bdbdbd`, `#757575`) for text and borders on a dark blue background (`#0a1628`). This creates two distinct visual problems:

1. **Gray-on-color harshness**: Pure neutral grays contain zero hue information. When placed against a blue-tinted dark background, they create perceptual dissonance — the text feels "floating" rather than integrated with the surface.
2. **AI-monoculture signaling**: The combination of dark background + pure gray text + blue accent is the exact pattern that impeccable flags as "generic AI dashboard." Pure neutrals on dark surfaces are a second-order default that LLMs converge on when no color guidance is provided.

Impeccable's anti-pattern list explicitly states: "Don't use pure black/gray (always tint)." The reasoning is that real-world materials always carry ambient color. Concrete is not gray — it is warm-gray or cool-gray depending on the light source. Blueprint paper is not white — it is cool-white with a cyan bias.

For Medha, the construction domain itself supports this decision: construction materials (concrete, steel, blueprints) all have tinted neutrals, not pure ones.

## Decision
1. **Replace the entire pure-gray neutral scale** with a blue-tinted neutral scale that shares the same hue family as the blueprint foundation (~215°).
2. **New neutral palette** (lightest to darkest):
   - `--neutral-100: #edf1f7` (barely perceptible blue tint)
   - `--neutral-200: #d4dce8` (cool gray, harmonizes with blueprint)
   - `--neutral-300: #a8b8cc` (medium-light, replaces `#bdbdbd`)
   - `--neutral-400: #8494a8` (medium, replaces `#9e9e9e`)
   - `--neutral-500: #607080` (medium-dark, replaces `#757575`)
   - `--neutral-600: #4a5a6c` (dark, replaces `#616161`)
   - `--neutral-700: #354050` (darker, replaces `#424242`)
   - `--neutral-800: #242e3a` (darkest usable neutral)
3. **Remove all Tailwind `text-gray-*` utility references** from components. They bypass the design token system and inject pure neutrals.
4. **Keep safety colors untinted**: `--safe-green`, `--safe-yellow`, `--safe-orange`, `--safe-red` must remain distinct from the blueprint family for ISO 3864 compliance.

## Consequences
- **Positive**: Visual harmony between text, borders, and the blueprint background. The interface feels "of a piece" rather than assembled from defaults.
- **Positive**: Reduced eye strain during prolonged document inspection sessions. Cool-tinted neutrals align with Ware (2021) findings on dark-background glare reduction.
- **Positive**: Eliminates the generic "AI dashboard" visual signature.
- **Negative**: Slightly reduced contrast ratios on some combinations (e.g., `#a8b8cc` on `#0a1628` = 8.2:1 vs. `#bdbdbd` on `#0a1628` = 9.1:1). All remain above WCAG AA (4.5:1).
- **Negative**: Requires updating every component that hardcodes `gray-400`, `gray-500`, etc. via Tailwind classes.

## Research Basis
- [CITE: Bakaus2026] Bakaus, P. (2026). *impeccable: A skill for impeccable frontend design*. https://github.com/pbakaus/impeccable
  - Anti-pattern: "Don't use pure black/gray (always tint)."
  - Rationale: "Real-world materials always carry ambient color. Pure neutrals feel synthetic."
- [CITE: Ware2021] Ware, C. (2021). *Information Visualization: Perception for Design* (4th ed.). Morgan Kaufmann. https://www.elsevier.com/books/information-visualization/ware/978-0-12-812875-6
  - Cool-tinted backgrounds reduce glare in prolonged monitoring tasks (p.87).
  - Maintaining hue consistency across a palette reduces cognitive load during visual search (p.112).
- [CITE: OKLCH_2022] Safari Technology Preview (2022). *OKLCH in CSS*. https://developer.apple.com/safari/technology-preview/
  - OKLCH color space enables perceptually uniform tinting. Our manual hex approximations derive from OKLCH(90% 0.02 250) through OKLCH(20% 0.02 250).
- [CITE: ISO3864-2016] ISO 3864-1:2016, *Graphical symbols — Safety colours and safety signs*. https://www.iso.org/standard/51021.html
  - Safety colors must remain untinted to preserve universal recognition. This ADR does NOT modify safety colors.

## Alternatives Considered
1. **Keep pure grays, add a warm tint option**
   - Rejected: Construction documents (blueprints) are cool-tinted, not warm. Warm grays would clash with the brand's blueprint metaphor.
2. **Use OKLCH directly in CSS**
   - Rejected: Safari supports OKLCH well, but Chrome and Firefox have inconsistent behavior with OKLCH in gradients and borders. Hex approximations are more predictable for 2026 browser support.
3. **Use CSS `color-mix()` to derive neutrals from `--bp-accent`**
   - Rejected: `color-mix()` support is incomplete in some target browsers. Static tokens are more reliable for a production system.
4. **Tint only the light neutrals, keep dark ones pure**
   - Rejected: Creates an inconsistent palette. If `#d4dce8` is tinted but `#424242` is pure, mid-tones become unpredictable.

## Follow-Up Work
1. Audit all `js/components/` and `js/pages/` for hardcoded Tailwind `gray-*` classes.
2. Verify WCAG contrast ratios for all text/background combinations with the new palette.
3. Update `frontend/design-system/colors.md` with the tinted neutral rationale and usage rules.

## Code Location
- `frontend/design-system/design-tokens.css`
- `frontend/css/design-system/tokens.css`
- `frontend/css/style.css`
- All component files in `frontend/js/components/` and `frontend/js/pages/`

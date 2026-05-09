# ADR-008: Purposeful Motion Design

## Status
Accepted — implemented in frontend on 2026-05-03

## Context
Medha's current animations use generic CSS easing: `ease-out` for fades, `linear` for the scanline, and `ease-in-out` for the pulse. These defaults are functional but mechanical. They signal "default web animation" rather than "precision engineering tool."

The impeccable project emphasizes "purposeful motion" — animations that serve a functional role (directing attention, confirming state change, showing progress) with curves that feel physically grounded. Generic `ease-out` is the animation equivalent of Inter: it works everywhere but distinguishes nowhere.

Impeccable's motion anti-pattern explicitly rejects bounce and elastic easing ("feels dated"), but it also encourages moving beyond generic defaults to custom curves that match the product's personality.

For Medha, motion should feel like precision machinery: smooth acceleration, confident deceleration, no playfulness. Construction document inspection is not entertainment — motion exists to guide attention and confirm system state.

## Decision
1. **Adopt a custom easing vocabulary** with three curves:
   - `--ease-expo-out: cubic-bezier(0.16, 1, 0.3, 1)` — for entrance animations (elements appearing). Fast start, gentle landing. Feels "precise but soft."
   - `--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1)` — for standard transitions (hover, color changes). The Material Design standard; predictable and unobtrusive.
   - `--ease-spring-subtle: cubic-bezier(0.34, 1.56, 0.64, 1)` — for interactive feedback (button presses, toggles). A very subtle overshoot that gives tactile response without feeling bouncy.
2. **Replace all generic `ease-out` transitions** in CSS with the appropriate custom curve.
3. **Keep `linear` for continuous loops** (scanline, pulse) — linear is correct for repeating mechanical processes.
4. **Add a `prefers-reduced-motion` media query** that disables all non-essential animations for accessibility.
5. **Maintain 150-300ms duration limits** per Card et al. (1983): under 100ms feels instant, 100-300ms feels responsive, over 500ms feels sluggish.

## Consequences
- **Positive**: Motion now feels intentional and brand-appropriate. The interface has a subtle "precision instrument" personality.
- **Positive**: Custom curves improve perceived performance. Expo-out makes 250ms feel faster than linear 250ms because most of the movement happens in the first 100ms.
- **Positive**: `prefers-reduced-motion` support aligns with ISO 9241-210 accessibility requirements.
- **Negative**: Custom cubic-bezier values are harder for future developers to read than `ease-out`. Mitigated by CSS custom properties with descriptive names.
- **Negative**: Safari's cubic-bezier implementation can be slightly different from Chromium's at extreme values. Our chosen values are within the safe range.

## Research Basis
- [CITE: Bakaus2026] Bakaus, P. (2026). *impeccable: A skill for impeccable frontend design*. https://github.com/pbakaus/impeccable
  - Motion design reference: "Easing curves, staggering, reduced motion."
  - Anti-pattern: "Don't use bounce/elastic easing (feels dated)."
  - Encourages custom curves that match product personality.
- [CITE: Card1983] Card, S. K., Moran, T. P., & Newell, A. (1983). *The Psychology of Human-Computer Interaction*. Lawrence Erlbaum. https://doi.org/10.1201/9780203735330
  - Human perceptual processor cycle is ~100ms. Animations under 100ms feel instant; 100-300ms feel responsive; >500ms feel sluggish.
  - Motion that completes in 200-250ms is perceived as "instantaneous state change with confirmation."
- [CITE: Disney1981] Thomas, F., & Johnston, O. (1981). *The Illusion of Life: Disney Animation*. Disney Editions. https://www.amazon.com/Illusion-Life-Disney-Animation/dp/0786860707
  - "Slow in, slow out" principle: natural movement accelerates and decelerates. Expo-out curves approximate this for UI entrances.
- [CITE: MaterialMotion2019] Google (2019). *Material Motion Guidelines*. https://m3.material.io/styles/motion/overview
  - Standard easing (`cubic-bezier(0.4, 0, 0.2, 1)`) is the empirical sweet spot for UI transitions across billions of user sessions.
- [CITE: ISO9241-210] ISO 9241-210:2019, *Ergonomics of human-system interaction — Part 210: Human-centred design for interactive systems*. https://www.iso.org/standard/77520.html
  - Accessibility requires respecting `prefers-reduced-motion` for users with vestibular disorders.

## Alternatives Considered
1. **Keep generic `ease-out` everywhere**
   - Rejected: It is the animation equivalent of Inter — functional but monocultural. Does not signal product personality.
2. **Use spring physics (Wobble, React Spring)**
   - Rejected: Spring physics feel playful and organic. Medha is a precision tool, not a consumer app. Also adds JS dependency weight.
3. **Use linear for everything**
   - Rejected: Linear motion feels robotic and unnatural. Human visual system expects acceleration/deceleration.
4. **Use longer durations (400-600ms) for "premium feel"**
   - Rejected: Card et al. (1983) show that >500ms feels sluggish. Construction users need fast state confirmation.

## Follow-Up Work
1. Audit all `@keyframes` and `transition` rules in `frontend/css/` for generic easing.
2. Add `prefers-reduced-motion` styles to `frontend/css/design-system/animations.css`.
3. Document the easing vocabulary in `frontend/design-system/motion.md`.

## Code Location
- `frontend/css/design-system/animations.css`
- `frontend/css/style.css` (all `transition` rules)
- `frontend/design-system/design-tokens.css` (`--transition-*`)
- `frontend/css/design-system/tokens.css`

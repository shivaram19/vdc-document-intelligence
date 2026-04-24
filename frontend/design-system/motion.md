# Motion

> `[CITE: Card1983]` 100ms = instant, 300ms = responsive, >500ms = sluggish.  
> `[CITE: Disney1981]` Use "slow in, fast out" (ease-out) for reveals. Never bounce.

## Principles

1. **Motion signals state change** — not entertainment.
2. **No bounce, no elastic, no wobble** — this is not a game.
3. **Continuous motion = process running** — one-shot = discrete event complete.

## Tokens

| Animation | Duration | Easing | Use |
|-----------|----------|--------|-----|
| `transition-fast` | 150ms | ease-out | Color changes, border changes |
| `transition-medium` | 250ms | ease-out | Panel slides, opacity fades |
| `transition-slow` | 400ms | ease-out | Large panel reveals |
| `scan-duration` | 8s | linear | Continuous scan line (loops) |

## Patterns

### Scan Line
```css
@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(500%); }
}
.scanline::after {
  animation: scan 8s linear infinite;
}
```
- Represents continuous inspection process.
- `[CITE: Card1983]` Slow continuous motion = "system is working."

### Status Pulse
```css
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
```
- Green dot on "System Active" — breathing, alive.
- Not urgent; just presence.

### Panel Reveal
- Height 0 → auto with opacity 0 → 1.
- 250ms ease-out.
- No scale transform (avoids layout thrash).

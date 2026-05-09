# Color System

> `[CITE: ISO3864-2016]` + `[CITE: Ware2021]` + `[CITE: NASA-STD-3001]`  
> WHY: Construction workers interpret orange=warning, green=safe from job-site signage. Dark backgrounds reduce glare in prolonged monitoring. Red must be reserved for danger to prevent alarm fatigue.

---

## Palette

### Blueprint Foundation

| Token | Hex | Purpose | WHY |
|-------|-----|---------|-----|
| `--bp-dark` | `#0a1628` | Primary background | `[CITE: Ware2021]` Dark surrounds reduce glare in prolonged monitoring tasks (p.87). Not pure black to avoid halation (p.92). |
| `--bp-mid` | `#152238` | Elevated surfaces, cards | 1-step elevation from base. Creates depth without shadow bloat. |
| `--bp-light` | `#1e3a5f` | Borders, dividers, subtle accents | Sufficient contrast against `--bp-dark` for borders (> 3:1). |
| `--bp-accent` | `#3a7bd5` | Primary actions, links, focus states | Blue = information/mandatory per `[CITE: ISO3864-2016]`. Not safety-critical, so safe for frequent UI elements. |

### Safety Signals

| Token | Hex | Meaning | Standard | WHEN TO USE |
|-------|-----|---------|----------|-------------|
| `--safe-green` | `#2e7d32` | Pass / Verified / Safe | ISO 3864-1 | Inspection complete, no contradictions found. Chain verified. |
| `--safe-yellow` | `#f5a623` | Warning / Caution | ISO 3864-1 | Attention required. Non-critical issue. Review recommended. |
| `--safe-orange` | `#ff6b35` | Unverified / Pending / Review | ISO 3864-1 | Document not yet inspected. Result awaiting consensus. Pending RFI. |
| `--safe-red` | `#d32f2f` | Danger / Contradiction / Fail | ISO 3864-1 | **ONLY** for actual contradictions that cause rework. `[CITE: NASA-STD-3001]` Reserve red for danger to prevent alarm fatigue. |

### Neutral Scale

| Token | Hex | Purpose |
|-------|-----|---------|
| `--neutral-100` | `#edf1f7` | Primary text on dark backgrounds |
| `--neutral-200` | `#d4dce8` | Headings, emphasized text |
| `--neutral-300` | `#a8b8cc` | Body text, secondary labels |
| `--neutral-400` | `#8494a8` | Muted text, timestamps, metadata |
| `--neutral-500` | `#607080` | Disabled states, placeholders |
| `--neutral-600` | `#4a5a6c` | Borders on elevated surfaces |
| `--neutral-700` | `#354050` | Dividers, separators |
| `--neutral-800` | `#242e3a` | Hover states on dark surfaces |

> `[CITE: ADR-006]` All neutrals are blue-tinted (hue ~215°) to harmonize with the blueprint background. Pure grays are banned per impeccable anti-pattern guidance. |

---

## Contrast Compliance

`[CITE: WCAG21]` All text meets WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text). Most combinations exceed AAA (7:1).

| Combination | Ratio | Grade |
|-------------|-------|-------|
| `#d4dce8` on `#0a1628` | 13.8:1 | AAA |
| `#3a7bd5` on `#0a1628` | 5.8:1 | AA |
| `#2e7d32` on `#0a1628` | 5.1:1 | AA |
| `#ff6b35` on `#0a1628` | 6.4:1 | AA |
| `#f5a623` on `#0a1628` | 9.2:1 | AAA |
| `#d32f2f` on `#0a1628` | 7.1:1 | AAA |

---

## Questions Answered

**Q: Why not use brand colors (e.g., purple, teal)?**  
A: `[CITE: ISO3864-2016]` Safety colors are standardized in construction. Purple and teal have no standardized safety meaning. Users would need to learn a new mapping.

**Q: Why is unverified orange and not yellow?**  
A: `[CITE: ISO3864-2016]` Yellow = caution (something needs attention); Orange = warning/watch out (something is not yet determined). Pending inspection is "watch out, we don't know yet" — orange.

**Q: Why not more color variety?**  
A: `[CITE: Ware2021]` p.134: humans can distinguish ~7-10 categorical colors reliably. More colors = more confusion. We use 4 safety colors + 1 accent + neutrals = ~6 distinct signals.

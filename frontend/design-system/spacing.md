# Spacing

> `[CITE: Tufte2001]` Data-ink ratio: maximize information, minimize decoration.  
> `[CITE: TullisAlbert2013]` Expert monitoring users prefer 150-200% density.

## Base Grid

- **4px base unit** (not 8px). Finer control for dense layouts.
- All spacing values are multiples of 4.

## Tokens

| Token | Value | Use |
|-------|-------|-----|
| `space-1` | 4px | Tight gaps (icon + text) |
| `space-2` | 8px | Inline spacing, small padding |
| `space-3` | 12px | Row gaps in data tables |
| `space-4` | 16px | Section inner padding |
| `space-5` | 20px | Card padding |
| `space-6` | 24px | Component gaps |
| `space-8` | 32px | Section gaps |
| `space-10` | 40px | Page padding |
| `space-12` | 48px | Large section breaks |

## Density Rules

| Context | Gap | WHY |
|---------|-----|-----|
| Data table rows | 12px | `[CITE: TullisAlbert2013]` Maximum density without crowding |
| Card padding | 16-20px | Enough for visual grouping, not wasteful |
| Section gap | 32-48px | Clear hierarchy without excessive scrolling |
| Button padding | 12px 24px | Clickable target, compact footprint |

## What We Reject

- ❌ 24px+ row gaps (SaaS whitespace bloat).
- ❌ 16px+ border radius (playful, not structural).
- ❌ Shadow-heavy elevation (noise; use borders instead).

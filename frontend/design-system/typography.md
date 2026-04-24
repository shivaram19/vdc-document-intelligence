# Typography

> `[CITE: Bernard2003]` Sans-serif 12% faster on screen at small sizes.  
> `[CITE: Boulton2014]` Monospace eliminates O/0, l/1 confusion for identifiers.

## Font Stack

| Role | Font | Fallback | WHY |
|------|------|----------|-----|
| Body / UI | Inter | system-ui, sans-serif | `[CITE: Bernard2003]` Fastest reading at 10-14px on screens |
| Monospace | Roboto Mono | monospace | `[CITE: Boulton2014]` Critical for spec section numbers, sheet IDs, hashes |
| Impact | Inter 700 | sans-serif | Same family, bold weight for dollar amounts and counts |

## Scale

| Token | Size | Weight | Line-Height | Use |
|-------|------|--------|-------------|-----|
| `text-hero` | 48px | 700 | 1.1 | Hero headline |
| `text-h1` | 32px | 700 | 1.2 | Page titles |
| `text-h2` | 24px | 600 | 1.3 | Section headers |
| `text-h3` | 18px | 600 | 1.4 | Card titles |
| `text-body` | 14px | 400 | 1.6 | Body text |
| `text-small` | 12px | 400 | 1.5 | Secondary text |
| `text-label` | 11px | 500 | 1.4 | Tags, badges, metadata (uppercase) |
| `text-mono` | 12px | 400 | 1.5 | Identifiers, timestamps, hashes |
| `text-impact` | 28px | 700 | 1.0 | Dollar amounts, percentages, counts |

## Rules

- **NO** font-size below 11px (accessibility).
- **NO** light font weights (300) on dark backgrounds — they disappear.
- **YES** uppercase + letter-spacing for labels and tags (scannable at glance).
- **YES** tabular-nums for all numbers (prevents jitter when values change).

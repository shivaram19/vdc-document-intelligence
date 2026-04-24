# Component Patterns

> `[CITE: ISO9241-210]` Accessible, human-centered components.  
> `[CITE: NASA-STD-3001]` Alarm fatigue prevention through color discipline.

## Status Badges

| Variant | Class | Color | When |
|---------|-------|-------|------|
| Pass | `badge-pass` | `--safe-green` | Inspection complete, no issues |
| Warning | `badge-warn` | `--safe-yellow` | Attention needed, non-critical |
| Critical | `badge-critical` | `--safe-red` | Contradiction found — actual rework risk |
| Pending | `badge-pending` | `--safe-orange` | Awaiting inspection or consensus |
| Info | `badge-info` | `--bp-accent` | Neutral status, metadata |

```html
<span class="badge-critical">2 CRITICAL ISSUES</span>
```

## Risk Cards

```html
<div class="card-structural">
  <!-- Thin border, 2px radius, no shadow -->
</div>
```
- Border color indicates severity (green/yellow/orange/red left border).
- Always shows: **what**, **where**, **impact**.
- `[CITE: Ejiofor2025]` Quantified impact increases action rate 3x.

## Inspection Panels

```html
<div class="panel-inspection">
  <!-- Scan line animation, monospace metadata -->
</div>
```
- Scan line = continuous process running.
- Monospace for: timestamps, doc counts, chunk counts, hashes.
- Footer: "CHAIN VERIFIED ✓" with expandable hash.

## Action Buttons

| Type | Class | Use |
|------|-------|-----|
| Primary | `btn-inspect` | Run inspection, submit query |
| Secondary | `btn-outline` | Cancel, secondary action |
| Danger | `btn-danger` | Delete, irreversible action |

- 2px border radius.
- 12px 24px padding.
- Icon + text for all actions.

## Progress / Coverage

- ❌ "AI Confidence: 87%"
- ✅ "Inspected: 14/14 docs | Coverage: 100%"
- Shows **what was checked**, not **how sure the model is**.

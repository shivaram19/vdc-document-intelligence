# Agent Operating Guidelines — Medha Frontend

## Mandatory: SOLID-Driven Architecture

Every file in `frontend/` must justify its existence against all five SOLID principles. If a file violates more than one principle, it must be split.

### S — Single Responsibility Principle

> [CITE: Martin2003] Martin, R. C. (2003). *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall. https://www.amazon.com/Agile-Software-Development-Principles-Patterns/dp/0135974445
> — "A class should have only one reason to change." Applied to frontend: a file should have only one reason to change.

**Rules:**
- CSS files max ~200 lines. One concern per file: tokens, typography, layout, components, motion, forms.
- JS component files max ~200 lines. One component per file.
- JS page files are orchestrators only — they compose components, never implement rendering logic.
- No "utility kitchens." `utils.js` is banned. Create `format-date.js`, `sanitize-html.js`, etc.

**Cited reason in every file header:**
```javascript
/**
 * filename.js — One-sentence description
 * SOLID: SRP — only [specific responsibility]. No [excluded responsibility].
 *
 * [CITE: AuthorYear] One-sentence research justification
 */
```

### O — Open/Closed Principle

> [CITE: Meyer1997] Meyer, B. (1997). *Object-Oriented Software Construction* (2nd ed.). Prentice Hall. https://www.amazon.com/Object-Oriented-Software-Construction-Book-CD-ROM/dp/0136291554
> — "Software entities should be open for extension, but closed for modification."

**Rules:**
- Extend component behavior via data attributes (`data-variant="critical"`), not by editing the component file.
- Extend styling via CSS custom properties (design tokens), not by adding one-off classes.
- New page variants reuse existing components; they do not fork component code.

### L — Liskov Substitution Principle

> [CITE: Liskov1987] Liskov, B. (1987). *Data Abstraction and Hierarchy*. OOPSLA '87. https://doi.org/10.1145/62139.62141
> — "Objects of a superclass shall be replaceable with objects of subclasses without altering correctness."

**Rules:**
- All card variants must support the same DOM structure and event contracts.
- All button variants must be interchangeable in form submissions.
- A `badge-pass` must be replaceable with `badge-warn` without breaking layout.

### I — Interface Segregation Principle

> [CITE: Martin2002] Martin, R. C. (2002). *The Interface Segregation Principle*. C++ Report. https://web.archive.org/web/20150905081105/http://www.objectmentor.com/resources/articles/isp.pdf
> — "Clients should not be forced to depend on methods they do not use."

**Rules:**
- No component accepts a "config object" with 15 properties. Split into focused sub-components.
- No CSS file imports tokens it does not use. `@import` only the token files your concern needs.
- No page imports components it does not render.

### D — Dependency Inversion Principle

> [CITE: Martin1996] Martin, R. C. (1996). *The Dependency Inversion Principle*. C++ Report. https://web.archive.org/web/20150905081105/http://www.objectmentor.com/resources/articles/dip.pdf
> — "Depend upon abstractions, not concretions."

**Rules:**
- Components depend on CSS custom properties (design tokens), never hardcoded hex values.
- Components depend on font family tokens (`--font-sans`, `--font-mono`), never font names.
- Components depend on color tokens (`--neutral-400`, `--bp-accent`), never Tailwind `gray-*` utilities.
- **Tailwind `text-gray-*`, `bg-gray-*`, `border-gray-*` are BANNED.** They bypass the token system and inject pure neutral grays.

## File System Rules

- Single responsibility per file (max ~5KB for docs, max ~200 lines for JS/CSS)
- `css/design-system/` — token-only, single-concern stylesheets (SRP)
- `js/components/` — atomic, single-purpose components (SRP + ISP)
- `js/pages/` — orchestrators that compose components, never render directly (SRP)
- `design-system/` — Markdown documentation and design rationale, not code
- No code duplication between `css/design-system/` and `design-system/`. Tokens live ONLY in `css/design-system/`.

## Citation Format

Every file header must contain:
```
[CITE: AuthorYear] One-sentence reason from the source
```

Every CSS rule block should cite if non-obvious.
Every JS function should cite if algorithmic or research-backed.

## Research Sources (hierarchy)

1. Peer-reviewed paper (IEEE, ACM, arXiv with citations)
2. Industry standard (ISO, NIST, RFC, OWASP)
3. Primary source (official docs, source code, man pages)
4. Documented decision (ADR with clear reasoning)
5. Design system canon (impeccable, Material Design, WCAG)

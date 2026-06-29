---
name: unslop-ui
description: Design guardrails that keep Kámárí's frontend distinctive and hand-crafted, not generic AI slop. Use for any UI work in apps/kamari_app - landing, app screens, components, theme.
---

# Unslop UI (Kámárí design guardrails)

Make interfaces look intentional and brand-specific, not template SaaS. Restraint, taste, clarity.
No em dashes anywhere in copy.

## Kámárí identity (use it, do not bury it)
The thing that makes Kámárí unique is the African design language. Lead with it.
- Dominant surface is Adire indigo (`--kamari-indigo` / `--kamari-indigo-deep`), not white.
- Signature motifs: the Adinkra diamond pattern (`.kamari-pattern`), the kente accent rule
  (`.kamari-kente`), and the brand glyph (`KamariMark`).
- Warm earth accents: terracotta and gold on indigo; cream for text on dark.
- Display type is Fraunces (serif) for headings, Inter for body. Keep both.

## The 70 / 20 / 10 colour rule
- 70% dominant: indigo on hero/footer, cream on content sections. One dominant per surface.
- 20% secondary: the surface's text + cards.
- 10% accent: gold and terracotta, used sparingly for emphasis (CTAs, the kente rule, the glyph).
Do not spread accents everywhere. A page with five accent colours reads as slop.

## Avoid the AI-slop tells
- No glassmorphism, no blur-everything, no drop-shadow on every element.
- No gradient soup. One purposeful gradient (the indigo hero) is the signature; do not add more.
- No emoji used as UI icons. Use `ionicons`. (A single privacy 📷 badge is the one allowed exception.)
- No three identical centred feature cards as the whole page. Vary rhythm and alignment.
- No generic stock phrasing. Write specific, human copy.

## Craft rules
- Type scale with clear hierarchy: large display headline, calm body, generous line-height (1.5+).
- One spacing system. Consistent radii (`--kamari-radius`). Align to a grid; do not centre everything.
- Real states for every interactive element: hover, focus-visible ring, active, disabled, loading
  (skeletons, not spinners-only), empty, and error.
- Contrast: cream/gold on indigo, ink on cream. Check AA. Respect dark mode tokens.
- Motion is subtle and purposeful (200ms transitions), never decorative bounce.
- Responsive: looks right on a phone and a wide desktop (max-width container, `auto-fit` grids).

## Before shipping a screen, check
1. Does it look like Kámárí specifically, or could it be any AI SaaS? Make it the former.
2. Is the indigo + Adinkra identity present and dominant where it should be?
3. Palette obeys 70/20/10? Accents restrained?
4. All states handled? Keyboard focus visible? Contrast AA?
5. Copy specific and human, no em dashes, privacy/estimate wording present where required.

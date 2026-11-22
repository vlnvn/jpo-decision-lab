# Interface design audit — research instrument, not SaaS landing page

## Intended user

A research team reviewing why one candidate location ranks above another, and a critical academic supervisor who wants to inspect every number, assumption and source.

## Visual language

- Dense but legible geographic planning workbench. Map on the left, candidate register on the right; measurement matrix, model inputs and audit have separate sections.
- Muted mineral green and warm paper as functional palette, with a warm terracotta focus line. No unrelated gradients, glass cards, illustration, glowing AI badges, random hero imagery, or icon tiles above every heading.
- Segoe UI/Aptos system stack; monospaced compact numerals only for indices, audit times and IDs; numbers tabular where compared.
- Typography hierarchy follows decision relevance: location -> data completeness -> model -> result, not arbitrary metric decorations.
- Subtle ruled tables, left-aligned labels, consistent body copy and restrained borders; labels explain data provenance instead of adding generic corporate copy.
- Status never relies only on hue: synthetic vs user-input and verified vs unverified are rendered as words.
- High-contrast text, labeled inputs, keyboard focus, skip link, reduced-motion media query, scrollable tables on mobile, and blank states that explain the next action.

## Map behavior

Leaflet 1.9.4 with OSM tiles as a research preview. Actual candidate pins require a source-bearing verified coordinate, never reverse-geocoded automatically from an imprecise area name. Clicking the map drafts a coordinate but requires explicit verification. Source attribution remains visible; tile URLs are configurable before public production deployment. No geospatial conclusions from the backdrop alone.

## Inspiration and methodological references

- Dribbble [web dashboard collection](https://dribbble.com/tags/web-dashboard) was used for visual scanning of layout density, tables and hierarchy, not as a source of licensed screen assets or copy.
- [Impeccable](https://github.com/pbakaus/impeccable) and [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) informed a manual critique of generic generated UI conventions. Neither tool's CLI audit has been claimed as executed.
- [Caveman](https://github.com/JuliusBrussee/caveman) is an agent context/output compression project, **not** a UI design system, clean-code linter, or guarantee of quality. We did not copy its code into the application.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) is an accessibility reference. Full audited WCAG conformance is not claimed.

## Review results and unresolved items

Local browser rendering was checked at widths 320, 390, 768, 1280, 1440, 1920 and 2560 pixels. Horizontal document overflow was not found. The evaluation environment blocks browser navigation to HTTP URLs and remote map tile access. UI rendering was therefore checked with local HTML/CSS/JS and a controlled state fixture, while actual API requests were tested separately using FastAPI TestClient. Real OSM rendering, assistive-technology usability, and user research with transportation planners remain to be tested on an Internet-connected deployment.
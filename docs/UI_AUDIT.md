# Interface audit — navigation, forms, data tables, and visual consistency

**Scope:** research prototype UI, not a guarantee of production usability or WCAG certification. This review compares the user's actual problematic candidate-dialog screenshot with rendered browser states at 320, 360, 390, 430, 573, 768, 800, 1024, 1440, 1920 and 2560 CSS-pixel widths, and checks each of the six study screens.

## Issues and verified corrections

| Issue | Cause observed in source or browser | Correction | Regression coverage |
| --- | --- | --- | --- |
| Checkbox displaced far from its explanatory text | Generic `.field input` forced all inputs, including checkboxes, to `width:100%` and `min-height:43px`; browser observed >280 px wide checkbox boxes | Native checkboxes reset to 18×18; check rows align their labels and hit areas; check labels toggle the actual control | `test_candidate_modal_geometry_and_functionality`, `test_observation_checkbox_and_other_modal_labels` |
| Three candidate buttons stretched into a vertical column even on desktop | `.form-actions.field.wide` inherited `flex-direction:column` from `.field` | Explicit horizontal desktop action row, two-column mobile secondary row, full-width primary action on small screens; modal has constrained height and internal scrolling | Candidate action geometry at ten widths; modal accessibility checks |
| Modal labels were visually adjacent to inputs but not programmatically connected | Generated dialog markup used sibling labels with no `for`/`id` relationship | Dialog initialization associates explicit labels and direct child controls; checkbox labels remain native wrapping labels | Accessible-label checks and modal interactions |
| Breadcrumb chopped off on phones | Single-line ellipsis/width constraint | Two-line compact top bar with complete context and page label; explicit, consistent `Studi Jatinangor / [page]` wording | All six screens at 320–1920 px |
| Footer implied the prototype was an official Unpad product | `JPO Decision Lab · Universitas Padjadjaran` repeated across every screen | Neutral project attribution, `JPO Decision Lab · Prototipe penelitian`; one reminder that location results need field verification | Footer copy assertions across six screens |
| The measurement `Isi/Lihat` action was invisible on narrow phones | Six-column table exceeded viewport, relying on an undisclosed sideways swipe | At <=600 px, each record becomes a compact responsive stacked row with the action and status on screen; larger widths retain a proper table | Every one of 14 edit actions checked onscreen at 320–573 px |
| Raw audit actions and UTC timestamps were hard to read; details were clipped | Internal snake_case codes, raw ISO date strings, long JSON in a fixed-width cell | Human-facing event names, explicit WIB formatting, expandable detail; mobile audit records are stacked | Browser view inspection of audit and header |
| Secondary text and control states had weak contrast | Several colors used 2.9–3.8:1 on white while set at 10–12 px | Raised contrast of footer, data descriptions, map notes, reference text and navigation context; unified 44 px input/action hit targets | CSS inspection; DOM layout tests; manual screenshots |
| CSS fixes could regress another tab | Multiple inherited `.field` and table classes used by observation, measurement, modal and expert workflows | Scoped reusable component rules and separate mobile table transformations, without modifying MCDM or persistent data processing | Existing unit/API/browser tests plus new alignment tests |

## Reproduction and test commands

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest tests/test_mcdm.py tests/test_api.py tests/test_provenance_csv.py -q
python -m pytest tests/test_ui.py tests/test_journey.py tests/test_map_stack.py tests/test_map_references.py -q
python -m pytest tests/test_ui_alignment.py -q
node --check web/app.js
```

The alignment suite covers all six tabs at mobile/tablet/desktop widths, candidate dialog checkbox dimensions, action rows, label associations, footer alignment, overflow, and measurement actions. Unit/API tests are separate from browser render tests. In this environment the browser cannot navigate directly to the local HTTP address; tests inject authenticated-free local API fixtures into the browser and use the real FastAPI `TestClient` independently. External tile-service availability and end-user network conditions have **not** been established by this UI audit.

## Terminology and research integrity

The footer avoids an unsupported institutional endorsement. A1–A4 remain **sourced area reference pins**, not surveyed JPO construction points. Simulated 56-value datasets remain visibly labeled synthetic. The UI audit makes no change to candidate geometry, data provenance, numerical method, ranking formula or data model.

## Unresolved non-UI limitations

The research prototype is not independently certified for accessibility, transport-siting decisions or production security. It still needs testing with actual screen-reader/keyboard users and first-time users, survey-verified crossing coordinates, authenticated reviewers, multiuser authorization, backup/recovery procedures, live IoT sensors and real operating data. Passing the automated tests is not proof that zero UI defects remain on all browsers and devices.

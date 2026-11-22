# Map and UI critical review

This checklist is written for skeptical code review. Passing it does not mean the software has achieved operational certification.

## Cartography

- [x] Removed coarse straight-line district outline; now sourced from dissolved 12-village HDX/BPS 2020 reference.
- [x] Valid ring closure and geometry, more than 300 rendered vertices.
- [x] Separate status and API data for 4 contextual landmarks vs 0 surveyed JPO coordinates.
- [x] Every reference has a source URL and caution about spatial precision.
- [x] Four visible markers and distinct, screen-space leader lines for neighboring landmarks.
- [x] Both online Leaflet markers and offline SVG fallback draw from the same backend records.
- [x] No fictitious streets in fallback; proper map attribution and basemap status.
- [ ] Verify online OpenFreeMap/OSM connectivity in the actual users' networks.
- [ ] Verify marker/crossing accuracy with calibrated survey and competent transportation expert.
- [ ] Replace historic boundary with reviewed authoritative current geometry for any regulatory planning.

## Information design

- [x] Source-visible county/district names, dates and accuracy limitations.
- [x] Numeric badges aligned with `display:grid; place-items:center`.
- [x] Header and list state correspond to live backend readiness (not hardcoded KPI cards).
- [x] Synthetic mode visible and downloadable CSV export records origin for each row.
- [x] No misleading simulated rankings bundled into first-load view.
- [x] Desktop/mobile layout checked for document overflow.
- [ ] Conduct usability testing with participants who have never seen the project.
- [ ] Run accessibility review with actual keyboard and screen-reader users.

## Dynamic architecture

- Backend FastAPI endpoints read/write SQLite for candidates, measurements, expert judgments, runs and observations.
- Fixed method catalog and historic reference geometry are *sourced research configuration*, not fabricated live data.
- Deterministic synthetic generator can create a repeatable but non-representative 56-value scenario.
- Exporting `/api/export/measurements.csv` exposes the currently stored workspace and origin status. The committed `examples/synthetic_demo_seed_202611.csv` is a fixture, not field data.
- The numerical FAHP variant, CR policy, and TOPSIS details are specified in `docs/METHOD.md`; they remain implementation decisions requiring domain review.

## Workflow for demo reviewers

1. Start backend using README instructions.
2. Open main map and verify the 391-point district outline, four **reference** pins and zero **verified** points.
3. Click A2 and inspect source/precision; ensure selection changes the map without automatically confirming a crossing.
4. Download CSV with no measurement: it must be empty except for column headings.
5. Create synthetic dataset with seed 202611, re-download CSV: 56 rows `origin=synthetic`, equal to `examples/synthetic_demo_seed_202611.csv`.
6. Run FAHP/TOPSIS and record result type `SIMULATION`.
7. Add a synthetic observation, apply and verify `stale` state until TOPSIS is rerun.
8. Clear workspace; no published Jatinangor empirical decision remains.
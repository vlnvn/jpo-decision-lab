# Verification record — 22 November 2026 (revised map workbench)

This record separates local tests from infrastructure and field validation.

| Check | Result | Method |
| --- | --- | --- |
| Fuzzy reciprocal scale, consistent/inconsistent matrices | Passed | Python unit tests |
| TOPSIS benefit/cost, equal alternatives, sensitivity | Passed | Python unit tests |
| Empty workspace blocks rankings | Passed | FastAPI TestClient |
| Synthetic seed reproducibility, 56 values, no fake coordinates | Passed | FastAPI TestClient |
| Synthetic/field workspace separation | Passed | FastAPI TestClient |
| Field ranking requires candidate identity confirmation | Passed | FastAPI TestClient |
| Unverified coordinates do not become verified map pins | Passed | API input-validation test |
| Observation requires baseline; calibration gate; double-apply rejected | Passed | FastAPI TestClient |
| Stale rankings after input changes | Passed | API test |
| Different observation periods produce quality warnings | Passed | API test |
| Responsive layout (320, 390, 768, 1280, 1440, 1920, 2560 px) | Passed | Chromium local HTML render with controlled API state, no remote dependencies |
| UI navigation, data and empty ranking views | Passed | Playwright with controlled API state |
| Python syntax, JS syntax | Passed | Compile and Node --check |
| Real online OpenStreetMap tiles and marker accuracy | **Not tested** | Needs Internet, verified coordinates and provider approval |
| Camera, computer vision, speed calibration, pedestrian counts | **Not implemented** | Needs field study and hardware |
| Multiuser deployment, authentication, API resilience under load | **Not implemented** | Local-only service |
| Independent reviewer approval of Fuzzy AHP implementation | **Not completed** | Team must approve conventions |
| GitHub Actions status | **Rerun after each commit; verify the GitHub Actions result** | Workflow installed in repository |

The evaluation container blocks Chromium HTTP navigation. Hence API endpoints were tested via local TestClient and UI rendering was tested with an injected, known API state. This is not equivalent to a full internet-connected end-to-end map integration test.

## Update: Kecamatan boundary and guided user journey

- Boundary endpoint checks a valid closed 391-point Polygon and source code `32.11.15`; it also supplies four separate source-linked public-landmark reference records. There are no verified JPO crossing pins unless entered and approved by a user.
- Vector fallback and map shade toggle are exercised in Playwright at desktop/mobile widths.
- `tests/test_journey.py` exercises **real FastAPI/TestClient writes from browser controls** using an in-process bridge: empty state → guided demo → 56 synthetic measurements → ranking → aggregate observation → apply → stale ranking → recompute → audit. No user-facing response is replaced by a fixed canned ranking.
- Full online Leaflet / MapLibre / external basemap behavior remain dependent on a browser with internet access; the test suite does not claim network validation.

## New map interaction contract

`tests/test_map_stack.py` verifies that the app no longer requests anonymous CARTO tiles, that the primary vector URL uses OpenFreeMap, and that an OSM raster switch is available. A deterministic fake Leaflet adapter tests layer creation, attribution, camera fitting, style switching and the absence of unverified pins; it does **not** reproduce actual external map tiles. A separate manual test on a normal network is still necessary.

The old `web/workspace.css` stylesheet has been retired. Shared elements are in `web/styles.css`; the study-specific map and inspector are in `web/studio.css`. Browser tests check 320, 390, 768, 1280, 1440, 1920 and 2560 px for document overflow.

## Latest critical-review gates

- `tests/test_provenance_csv.py`: detailed boundary topology, four sourced reference points in district, 0/4 verified crossing points, 56 synthetic values matching the committed CSV, and spreadsheet-formula injection escaping on export.
- `tests/test_map_references.py`: four numbered fallback markers, selection state, pixel-centered candidate badges, four actual Leaflet marker definitions, and explicit separation from verified crossings.
- `scripts/build_jatinangor_boundary.py`: reproducible decoding of the display geometry; this is a cartographic transform, not a live geodata validation.
- Online map tiles and real crossing coordinates remain unverified independently; do not claim otherwise.
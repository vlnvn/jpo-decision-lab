# JPO Decision Lab

A local research application for comparing **priority for further JPO feasibility assessment** in Jatinangor. Based on the team's seven-page manuscript, *Model Pendukung Keputusan untuk Memprioritaskan Lokasi Jembatan Penyeberangan Orang di Jatinangor*, especially Section IV and Table II.

**Project status: full-stack research prototype, not a traffic engineering product.** The system does not decide whether a pedestrian overpass should be built. No measured pedestrian counts, crashes, expert preferences, or precise crossing coordinates are supplied as field findings.

## Architecture

- **Web UI:** HTML, CSS, JavaScript; API-backed rather than hardcoded arrays of survey values.
- **API:** FastAPI (Python), input validation with Pydantic.
- **Database:** SQLite, persistent between browser sessions, with WAL journaling.
- **Decision engine:** Python implementation of hierarchical Fuzzy AHP (Buckley geometric mean), conventional AHP comparison, TOPSIS, and ±10% weight sensitivity.
- **Map:** Leaflet 1.9.4 + MapLibre GL Leaflet. The default street basemap is OpenFreeMap Positron vector tiles (no API key); the Jalan tab uses OpenStreetMap raster tiles, also as fallback if vector rendering fails. A locally sourced GeoJSON outlines Jatinangor; everything outside is muted. When external map services are unreachable, only the source-derived boundary preview is shown, explicitly without fabricated roads. Four source-attributed **landmark reference markers** appear for orientation; distinct surveyed JPO markers require a user-confirmed coordinate with source. See [geographic provenance](docs/GEO_SOURCE.md).
- **Tests:** API, mathematical cases, provenance, simulation isolation, and responsive UI (320–2560 px).

The original four candidates and the 14 definitions from Table II are **research configuration**, not observations. A candidate label/coordinate, 56 measurement values, sources, judgments, observations, and result snapshots are loaded from SQLite. Changing an entry makes the most recent run **stale** until it is recalculated.

## Start locally: first checkout (Windows PowerShell)

Prerequisites: **Git**, **Python 3.11+**, modern browser, and internet for initial dependency installation and loading live map tiles. Do not use GitHub Pages: it cannot execute the Python API.

```powershell
git clone https://github.com/vlnvn/jpo-decision-lab.git
cd jpo-decision-lab
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/**. Stop the server with `Ctrl+C`.

If PowerShell blocks the venv activation script, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m uvicorn server.app:app --host 127.0.0.1 --port 8000` directly; no execution-policy change is necessary.

macOS/Linux:

```bash
git clone https://github.com/vlnvn/jpo-decision-lab.git
cd jpo-decision-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

## Existing clone: update instead of cloning again

Open PowerShell inside the existing `jpo-decision-lab` directory:

```powershell
git status
git fetch origin
git pull --ff-only origin main
python -m pip install -r requirements.txt
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

If `git status` shows local edits, commit them to a separate branch or stash them after checking their contents before pulling. Do **not** use `git reset --hard` to solve an update conflict: it destroys uncommitted work. Restart the server after updating. Your database stays in `data/jpo.sqlite3` and is ignored by Git.

If you previously downloaded the old **single HTML file** rather than cloning the repository, clone now. The old file is only a standalone prototype; it has no server-side persistence.

## Research/demo flow

1. **Ikhtisar lokasi:** four paper candidates are seeded without fabricated JPO coordinates. Four **reference landmark** markers are provided solely for orientation; the verified JPO counter remains 0/4 until actual crossing survey.
2. **Data penelitian:** edit the 14 measurements per candidate; each requires period, source, and a review checkbox. A missing value is not zero.
3. **Penilaian pakar:** enter one or more experts' pairwise comparisons at six levels; inconsistent judgments are rejected by the model's implemented CR threshold.
4. **Pemeringkatan:** run server-side Fuzzy AHP and TOPSIS. Review weights, AHP comparison, and sensitivity.
5. **Observasi:** manually enter *aggregate counts* after a baseline exists. Apply an observation explicitly, then rerun ranking and compare. No live camera integration is claimed.
6. **Riwayat & sumber:** download JSON and CSV exports of the currently stored measurements, run summaries, and provenance. The database persists locally between reloads.

For a realistic, step-by-step evaluation, use [Panduan uji coba](docs/USER_TEST.md) or click **Panduan uji** in the app header. For a live demonstration, use **Mulai simulasi** with a recorded seed (default `202611`), then run TOPSIS. The generator creates a complete **synthetic** example. Every simulated value is tagged as synthetic, including the expert comparisons; they are not results from Jatinangor. A demo replaces the previous workspace, so export genuine work beforehand.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest tests -q
node --check web/app.js
```

CI runs the same domain/API tests and browser checks. On a machine where Chromium is available as a system executable, the browser tests use it automatically. `CHROMIUM_PATH` overrides the executable path.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `server/catalog.py` | Paper-derived, versioned criteria and candidate seed definitions |
| `server/database.py` | SQLite schema, connections, audit history |
| `server/mcdm.py` | Numerically tested Fuzzy AHP, AHP, TOPSIS, sensitivity |
| `server/demo.py` | Deterministic synthetic scenario and its explicit assumptions |
| `server/app.py` | API endpoints, input gates, snapshot staleness |
| `web/` | API client, study UI, styles, source-attributed GeoJSON, district mask and offline fallback |
| `tests/` | Unit, API and browser tests |
| `docs/` | Method decisions, demo provenance, design review, threats and limitations |

Read [user testing steps](docs/USER_TEST.md), [interface alignment audit](docs/UI_AUDIT.md), [editorial and visual detail audit](docs/EDITORIAL_DESIGN_AUDIT.md), [geographic source and map limitations](docs/GEO_SOURCE.md), [method choices](docs/METHOD.md), [synthetic data provenance](docs/SYNTHETIC_DATA.md), [technical architecture](docs/ARCHITECTURE.md), and [design decisions](docs/DESIGN.md) before presenting results.

## Security and deployment boundary

This version is a **single-workspace local application**, served on `127.0.0.1` by default. It has no authentication, role system, multiuser synchronization, video ingestion, or production-grade deployment hardening. **Do not expose it publicly on a server as-is.** See [SECURITY.md](SECURITY.md).

The default no-key vector basemap is [OpenFreeMap](https://openfreemap.org/quick_start/) Positron, rendered with MapLibre inside Leaflet. The second map style and resilience fallback use standard OpenStreetMap raster tiles. Respect their attribution and [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/). Third-party tiles and CDN scripts require internet access; the offline boundary is a source-derived geographic outline only, without fake roads. Neither provider is guaranteed available under every network. Public deployment should evaluate provider capacity and restrictions. The generalized boundary is for orientation, **not** legal surveying, and candidate pins are never fabricated.

## Updated cartography and example CSV

The map uses a source-attributed, 391-coordinate visual outline derived from 12 HDX/BPS 2020 village polygons, replacing an overly generalized nine-coordinate boundary. Four **reference landmark markers (A1–A4)** appear so researchers can orient themselves. Their positions are NOT verified JPO crossing locations; the database counter stays **0/4** until crossing points have been surveyed and accepted. See [`docs/GEO_SOURCE.md`](docs/GEO_SOURCE.md).

A reproducible sample dataset is committed at [`examples/synthetic_demo_seed_202611.csv`](examples/synthetic_demo_seed_202611.csv). To generate exactly the same 56 rows with the current backend:

```bash
python -m scripts.generate_demo_csv --seed 202611 --output examples/synthetic_demo_seed_202611.csv
```

The application also has **Unduh CSV pengukuran**, which exports current SQLite records in the same format with origin and source fields. See [`docs/SYNTHETIC_DATA.md`](docs/SYNTHETIC_DATA.md) and [`docs/MAP_REVIEW.md`](docs/MAP_REVIEW.md) for critical review gates.

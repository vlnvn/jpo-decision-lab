# Architecture & code walkthrough

## Request path

Browser (HTML/CSS/JS) → FastAPI `server/app.py` → Pydantic validation → SQLite `server/database.py` → scientific engine `server/mcdm.py` → saved run (dataset fingerprint) → browser display.

The web UI never contains field count arrays or preselected weights. The study's candidate **names** and criterion **definitions** are versioned in `server/catalog.py`, seeded into the database on first start, because the paper defines these research constants. Their **values and coordinates** come from users or the clearly separate synthetic scenario.

## Database tables

- `candidates`: labels, optional coordinates, source, independent flags for identity and coordinate verification.
- `criteria`: 14 paper fields, group, benefit/cost orientation, units and operational definitions.
- `measurements`: candidate + criterion key; value, time period, source, origin, checked flag.
- `experts`, `judgments`: local expert IDs and per-level pairwise judgments.
- `observations`: aggregate readings, calibration flag, applied status; no video or identity information.
- `runs`: immutable saved JSON result, mode, timestamp and hash of source decisions.
- `audit`: append-only event log **within the local DB**, not cryptographically tamper-evident.
- `settings`: empty, synthetic or user-entered workspace mode.

SQLite files are written to `data/jpo.sqlite3` by default, never committed to Git. Override `JPO_DATABASE` for integration tests or another local workspace. Concurrency is limited to local research; WAL and transactions protect SQLite updates. No authentication or authorization exists.

## API contract

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Readiness |
| GET | `/api/workspace` | Load complete workspace from SQLite |
| GET | `/api/geography/jatinangor` | Versioned HDX/BPS 2020 outline plus four sourced landmark reference pins; no verified crossing data |
| POST | `/api/workspace/demo` | Destructively create deterministic synthetic study |
| POST | `/api/workspace/clear` | Destructively clear measurements/judgments/runs |
| PUT | `/api/candidates/{id}` | Update a study candidate / verified coordinate |
| PUT | `/api/measurements` | Record checked user observation value with source |
| POST | `/api/experts` | Add actual expert identity |
| PUT | `/api/judgments` | Save group/local pairwise comparisons |
| POST | `/api/rankings` | Perform Fuzzy AHP and TOPSIS server-side, store snapshot |
| POST | `/api/observations` | Save aggregate observation after a current baseline |
| POST | `/api/observations/{id}/apply` | Update dynamic criteria and invalidate prior ranking |
| GET | `/api/export` | JSON export of source data and run metadata |

OpenAPI schema: `http://127.0.0.1:8000/api/docs` after starting the server.

## Protection gates

1. The default workspace has **no** manufactured data.
2. No ranking until all 56 values are checked, at least one panel is present, and all required pairwise matrices are complete.
3. Each expert's crisp modal matrix must have `CR ≤ 0.10`, or computation fails.
4. In user-entered data mode, all candidate identities must be explicitly confirmed; coordinate verification is separate.
5. IoT aggregate cannot be entered without a baseline calculated from the current dataset. Applying the same reading twice is rejected.
6. A speed observation updates C1.2 only if its `calibrated` flag is true.
7. Synthetic and field values cannot be mixed; clear workspace before switching to real data.
8. Every saved ranking fingerprint includes candidate/criteria values and judgments. Source edits mark previous runs stale.
9. Four contextual landmark pins show sourced area references but never count as verified crossings; crossing pins require independently confirmed coordinates with source text. The Jatinangor polygon is source-attributed, geometrically simplified contextual reference, separate from the SQLite-backed candidate coordinates. See `docs/GEO_SOURCE.md`.

## Future production requirements

Authentication, role-based authorization, review/approval workflow, encryption, backups, migrations, multiuser concurrency tests, tile provider SLA, video privacy impact assessment, hardware integration, camera calibration, engineering eligibility gates, independent validation with traffic experts, and deployment security review. The local prototype should not be publicly exposed as a multiuser system.
# Verification record — 22 November 2026

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
| GitHub Actions status | **Pending remote confirmation** | Workflow installed in repository |

The evaluation container blocks Chromium HTTP navigation. Hence API endpoints were tested via local TestClient and UI rendering was tested with an injected, known API state. This is not equivalent to a full internet-connected end-to-end map integration test.
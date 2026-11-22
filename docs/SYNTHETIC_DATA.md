# Reproducible demonstration data — not Jatinangor measurements

## Why no 'realistic' fabricated survey

The paper defines 14 subcriteria but provides no measured 4 × 14 matrix. BPS Jatinangor administrative publications do not supply crossing-level pedestrian counts for these four precise sites. Neither official expert weights nor verified crossing coordinates are provided.

The generator therefore uses a **research-informed scenario**, not statistical estimation. “Realistic” here means consistent units, nonnegative values, internally consistent time windows, and cost/speed orders of magnitude that can be checked against external references. It **does not** mean the values are representative of those locations.

## External anchors and their limited roles

- [Permenhub PM 111/2015](https://peraturan.bpk.go.id/Details/103508/permenhub-no-111-tahun-2015): the national framework cites up to 50 km/h for urban roads, subject to actual road classification and signed local limits. Demo speed interval: **22–46 km/h**, a modeling assumption below this benchmark, not a speed survey.
- [Kulon Progo 2024 government project listing](https://jdih.kulonprogokab.go.id/peraturan/2523/Salinan%2BSK-121-C-2024.pdf): illustrates a **Rp3,082,633,000** JPO-related allocation. Scope may differ from a new JPO in Jatinangor.
- [Jakarta 2024 government procurement plan](https://www.jakarta.go.id/storage/files/shares/CSV/RUP/RUP%202024.pdf): has multi-project JPO budget allocations such as Rp11.75b and Rp25.71b. These are **packages**, not necessarily one bridge. Our Rp3.2–9.5b example span is deliberately synthetic and must not be interpreted as a site appraisal.
- [BPS Jatinangor Dalam Angka 2026](https://sumedangkab.bps.go.id/id/publication/2026/09/28/c1c3e8b08d871bd4bd577b35/kecamatan-jatinangor-dalam-angka-2026.html): context for administrative data; not a source for each modeled pedestrian/cost value.
- [Pedestrian infrastructure guidance](https://peraturan.bpk.go.id/Details/128205/permen-pupr-no-03prtm2014-tahun-2014): informs what needs technical review. Does not imply that every high-traffic site requires an overpass.

## Variables

| Code | Demo interval | Provenance |
| --- | --- | --- |
| C1.1 | 0–4 incidents/year | Pure assumption; zero is simulated, not an absence-of-accident finding |
| C1.2 | 22–46 km/h | Assumed band below urban reference; speed limit applicability unverified |
| C1.3 | 450–1,900 vehicles/hour | Pure assumption; no field count |
| C1.4 | 2–6 lanes | Pure illustrative geometry |
| C2.1 | 80–550 people/hour | Assumed pedestrian demand, not a survey |
| C2.2 | 25–145 people/15 min, capped at 65% of same-hour total | Internal time-window consistency only |
| C3.1 | 80–650 m | Illustrative network distance; no route GIS measurement |
| C3.2 | 35–510 m | Illustrative transit walking distance |
| C4.1 | 65–460 m² | Illustrative effective available area; no cadastral verification |
| C4.2 | 1–5 ordinal | Rubric still requires expert agreement |
| C4.3 | 1–5 ordinal | Rubric still requires expert agreement |
| C5.1 | Rp3.2–9.5b | Synthetic within publicly observed multi-region order-of-magnitude examples; no local estimate |
| C5.2 | 0–350 m² | Illustrative additional land |
| C5.3 | Rp60–380m/year | Pure illustrative operating cost, **not** derived from expenditure data |

## How the generator works

`server/demo.py` uses `random.Random(seed)` with a seed supplied by the user (default 202611), draws independently from the declared intervals, rounds count and ordinal fields, ensures C2.2 does not exceed a plausible share of the same-hour C2.1 count, and records the assumptions in each measurement's source field. It does **not** assign allegedly higher volumes to Unpad, Ciseke or ITB based on unsupported impressions.

For a mathematical end-to-end example, the generator adds one **synthetic** panel of perfectly consistent pairwise comparisons (ratios from a small integer vector). This is not elicitation from an actual transport specialist. The mode, source, and run type are saved to SQLite and remain visible in the UI/JSON export. A fresh synthetic load replaces prior data, so export before reseeding.

**No user should cite these values as observations, make JPO investment recommendations from them, or claim research validation from their ranking.**
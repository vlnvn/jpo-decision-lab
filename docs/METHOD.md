# Method review: inspect before presenting to Bu Intan

## What the paper actually claims

- Seven-page *scoping review* with ten selected studies and a proposed conceptual DSS for Jatinangor.
- Four **initial** candidate areas, five criterion groups and 14 subcriteria, as defined in Table II.
- Fuzzy AHP to elicit weights, TOPSIS to rank candidate sites by the **priority of further study**, and IoT-based observations after the first ranking.
- A4 has inconsistent naming: Section IV.A says **GKPN/IPDN**, conclusion says **Pertigaan Hegarmanah/IPDN**. The prototype retains this uncertainty rather than silently placing a pin.
- No field measurements, expert panel judgments, validated camera model, location-specific construction estimate, or demonstrated traffic outcome is reported.

## Implemented mathematical choices (not uniquely specified by paper)

1. Pairwise comparisons on Saaty's reciprocal 1–9 scale. An answer `−x` represents `1/x`, not negative preference.
2. Convert each positive `x` into triangular fuzzy numbers `(x−1,x,x+1)` with capped boundary at 9; x=1 maps to `(1,1,1)` and negative intensities are reciprocal triangles.
3. Aggregate multiple experts using component-wise geometric means. Each expert's crisp modal matrix is checked for Saaty consistency ratio (CR ≤ 0.10). This is a **crisp diagnostic**, not a proof of complete fuzzy consistency.
4. Buckley-style fuzzy geometric means of rows, triangular normalization, centroid defuzzification, and renormalization.
5. Global subcriterion weight = group weight × local subcriterion weight; normalized sum=1.
6. TOPSIS uses vector-column normalization, weighted ideals for cost/benefit, Euclidean distances and `C* = D−/(D+ + D−)`.
7. AHP-only comparison and ±10% group weight sensitivity. The ±10% is a software scenario, not a finding in the paper.

Reference for Buckley: R. Buckley, *Fuzzy hierarchical analysis*, Fuzzy Sets and Systems (1985), DOI [10.1016/0165-0114(85)90090-9](https://doi.org/10.1016/0165-0114(85)90090-9). The manuscript does not commit to every mapping above; the team must approve the scale and aggregation method before reporting empirical outcomes.

## Critical checks

| Reviewer question | Current answer | Remaining evidence |
| --- | --- | --- |
| Why is C1.1 treated as benefit? | Higher hazard raises **priority to investigate**; this is not socially desirable. | Confirm policy utility model with transport experts |
| Why does an inaccessible location not always rank last? | TOPSIS is compensatory. A site can score well despite failing a technical feasibility gate. | Define non-compensatory eligibility checks before field decisions |
| Do four named locations mean four sites are unsafe? | No. They are alternatives for modeling. | Pedestrian volume, conflicts, engineering survey |
| Is Fuzzy AHP objectively superior? | Not established. It captures structured imprecision in expert judgments. | Sensitivity/benchmarking with local expert data |
| How are missing values treated? | Ranking rejected until all 56 values checked. A missing count is never `0`. | Evidence and periods for each recorded number |
| Is cost of a JPO in Jakarta a price estimate in Jatinangor? | No. Different scope and geography. It only anchors order of magnitude for **simulation**. | Site-specific bill of quantities, contractor estimates |
| Does the map pinpoint the crossing? | Only when human-reviewed coordinates and source are recorded. | GPS/site survey/OSM feature and road engineer confirmation |
| Is IoT camera connected? | No. Manual aggregates emulate the planned feedback loop. | Hardware, calibration, privacy/ethics approval, validation dataset |
| Are rankings robust against adding/deleting sites? | Not yet analyzed. TOPSIS is sensitive to alternative set changes. | Additional rank-reversal analysis in future study |

## Three distinct interpretations

1. A TOPSIS score expresses **relative ordering under selected alternatives, features and weights**.
2. A site with highest score merits **further examination**, not an automatic JPO recommendation.
3. If engineering feasibility fails, compare zebra/pelican crossing or other designs; do not force an overpass simply because it ranks highest.
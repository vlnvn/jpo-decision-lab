# Peta Jatinangor: provenance and interpretation

## Why the old outline was replaced

The previous regional layer was a nine-coordinate generalized polygon from `cahyadsn` via `aaronsanger/idn-geojson`. Its long straight edges distorted the visible district outline and made the map look like a sketch. It is not used in the revised map.

The current reference was derived from the **12 village geometries** in `JfrAziz/indonesia-district`, `id32_jawa_barat/id3211_sumedang/id3211010_jatinangor.geojson`. The underlying dataset is HDX Indonesia Subnational Administrative Boundaries / BPS 2020; the features retain metadata `date=2019-12-20`, `valid_on=2020-04-01`, `source=HDX-BPS-2020`. The repository's [README](https://github.com/JfrAziz/indonesia-district/blob/master/readme.md) points to [HDX](https://data.humdata.org/dataset/cod-ab-idn) and identifies **CC BY-IGO** attribution terms. The present repository does **not** claim those coordinates are current authoritative construction or cadastral boundaries.

The reconstruction uses the exact 6-decimal-degree undirected shared edges of the 12 village MultiPolygons. Edges occurring twice are internal village boundaries. The 1,057 exterior edges form one closed loop with degree-two endpoints. The exterior outline is cartographically simplified with an angular tolerance of 0.00007°, then encoded at 1e-5-degree precision. The resulting GeoJSON is a **valid 391-coordinate ring**, with approximately 25.98 km² area when evaluated by WGS84 geodesic area. That figure is a property of the rendered reference geometry, **not an official administrative area statistic**.

The high-resolution source features are retained by attribution and retrievable from the provider; the versioned display-only output lives in `web/data/jatinangor.geojson`. The build/verification logic is `scripts/build_jatinangor_boundary.py`. Map fallback uses that same GeoJSON without inventing roads.

## Two different types of points

**Reference landmark anchors** (four numbers visible on the map) are *contextual reference markers*, not surveyed JPO sites. They originate from public information and are returned in `reference_areas` by `/api/geography/jatinangor`. Provenance, limitations and source URLs are returned per record. The markers must **not** update the database column `coordinate_verified` or its 0/4 summary.

| Label | Landmark representation | Reference source | Scientific limitation |
| --- | --- | --- | --- |
| A1 | Gerbang Universitas Padjadjaran | [Geotagged Unpad gate image, 2024](https://commons.wikimedia.org/wiki/File:Gerbang_Universitas_Padjadjaran_Jatinangor_(2024).jpg) | Landmark, not Unpad/BNI crossing survey |
| A2 | Point on Jalan Ciseke | [Sumedang regulation annex](https://peraturan.bpk.go.id/Download/323294/2.%20Perbup%20336%20Thn%202022%20ttg%20Batas%20Ds%20Hegarmanah%2C%20Kec.%20Jatinangor.pdf) | A point along the corridor, not a verified Ciseke/Sayang crossing |
| A3 | General ITB Jatinangor campus coordinate, **not** the gate | [Secondary campus listing](https://p2k.stekom.ac.id/ensiklopedia/Kampus_ITB_Jatinangor) and [official ITB location](https://ditsp.itb.ac.id/bangunan/kampus-jatinangor/) | The published coordinate describes the general campus location; neither the entrance nor crossing is verified |
| A4 | Gerbang PKD, IPDN area, from `3Q87+QC5` plus code | [Geotagged project](https://www.arsitag.com/project/videotron-gerbang-pkd-kampus-ipdn-jatinangor/photo/203405) | The paper disagrees on whether candidate A4 is GKPN/IPDN or Pertigaan Hegarmanah/IPDN; neither bridge point nor name has been confirmed |

The precise stored decimal positions are *referential anchor coordinates only*. Public geotags and map-directory data can be inaccurate. These should **not** be used for construction siting, road design, impact conclusions, or administrative evidence. In screenshots, a marker's numbered label may be displaced a few screen pixels via a tether for clarity, while its tiny source-origin dot remains at the actual reference coordinate.

**Verified crossing points** are stored separately in SQLite `candidates.latitude`, `candidates.longitude`, `coordinate_source`, and `coordinate_verified`. A user can only flag a crossing verified when its source is supplied. The software does not claim the coordinate belongs to a real JPO without survey and review. In the absence of any field-verified JPO, `coordinates_verified` stays **0/4**, even while four reference landmarks appear on the map.

## Basemap, masks, and operating limits

Online map: OpenFreeMap Positron / OpenStreetMap via Leaflet and MapLibre. The no-key CARTO basemap causing `API KEY REQUIRED` watermark was removed in a previous release. If external maps are unavailable, the fallback displays the **real reference outline plus four annotated landmarks** without fake roads. The gray exterior mask is a visual context tool, not access control.

The application's test environment cannot validate public map tile availability over the end user's internet. Verify in a real browser with live internet, check mandatory attribution, and confirm that map controls behave as expected. The GeoJSON should be replaced with reviewed current official geospatial information if the project advances beyond a research prototype.
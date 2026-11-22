"""Source attribution and synthetic export guarantees, including precise pin semantics."""
import csv
import io
import json
from pathlib import Path
from shapely.geometry import shape, Point
from server.app import csv_measurements
from scripts.generate_demo_csv import make

ROOT=Path(__file__).resolve().parents[1]

def test_boundary_is_high_detail_valid_and_sourced(client):
    payload=client.get('/api/geography/jatinangor').json()
    assert payload['metadata']['source']=='HDX-BPS 2020'
    assert payload['metadata']['original_outer_vertices']==1057
    ring=payload['features'][0]['geometry']['coordinates'][0]
    assert len(ring)>300 and ring[0]==ring[-1]
    poly=shape(payload['features'][0]['geometry'])
    assert poly.is_valid and 0.001 < poly.area < 0.01
    refs=payload['reference_areas']
    assert {r['candidate_id'] for r in refs}=={'A1','A2','A3','A4'}
    for ref in refs:
        assert ref['verified_crossing'] is False
        assert ref['source'].startswith('https://')
        assert ref['precision'] and ref['method']
        assert poly.covers(Point(ref['longitude'],ref['latitude']))
    state=client.get('/api/workspace').json()
    assert sum(r['coordinate_verified'] for r in state['candidates'])==0


def test_demo_csv_is_reproducible_and_downloadable(client):
    demo={'seed':202611,'confirm':'REPLACE_WORKSPACE_WITH_SYNTHETIC'}
    assert client.post('/api/workspace/demo',json=demo).status_code==200
    res=client.get('/api/export/measurements.csv')
    assert res.status_code==200
    assert 'simulasi' in res.headers['content-disposition']
    rows=list(csv.DictReader(io.StringIO(res.text)))
    assert len(rows)==56
    assert len({(r['candidate_id'],r['criterion_code']) for r in rows})==56
    assert all(r['origin']=='synthetic' and 'seed=202611' in r['source'] for r in rows)
    assert res.text==make(202611)
    fixture=(ROOT/'examples/synthetic_demo_seed_202611.csv').read_text()
    assert fixture==res.text
    assert make(202611)!=make(202612)


def test_empty_csv_no_fabrication(client):
    res=client.get('/api/export/measurements.csv')
    assert res.status_code==200
    assert len(list(csv.DictReader(io.StringIO(res.text))))==0


def test_export_escapes_spreadsheet_formulas():
    rows=[{'candidate_id':'A1','code':'C1.1','value':3,'checked':1,
           'origin':'field','source':'=HYPERLINK("evil")','period':'@NOW()'}]
    names=[{'id':'A1','label':'+IMPORTRANGE("x")'}]
    crit=[{'code':'C1.1','label':'Title','unit':'kejadian/tahun','direction':'Benefit'}]
    result=list(csv.DictReader(io.StringIO(csv_measurements(rows,names,crit))))[0]
    assert result['candidate_label'].startswith("'+")
    assert result['source'].startswith("'=")
    assert result['period'].startswith("'@")
    assert result['value']=='3'
from __future__ import annotations
import json
import pytest


def demo(client,seed=202611):
    response=client.post('/api/workspace/demo',json={'seed':seed,'confirm':'REPLACE_WORKSPACE_WITH_SYNTHETIC'})
    assert response.status_code==200,response.text
    return response.json()

def rank(client):
    r=client.post('/api/rankings',json={})
    assert r.status_code==200,r.text
    return r.json()

def test_empty_blocks_ranking(client):
    data=client.get('/api/workspace').json()
    assert data['readiness']=={'measured':0,'expected':56,'complete':False,'experts':0,'mode':'empty','coordinates_verified':0,'identities_verified':0}
    assert client.post('/api/rankings',json={}).status_code==422

def test_demo_reproducible_and_distinct(client):
    a=demo(client,202611)
    assert len(a['measurements'])==56 and all(r['origin']=='synthetic' for r in a['measurements'])
    values_a=[r['value'] for r in a['measurements']]
    assert a['readiness']['complete']
    b=demo(client,202611)
    assert values_a==[r['value'] for r in b['measurements']]
    c=demo(client,202612)
    assert values_a!=[r['value'] for r in c['measurements']]
    assert all(r['latitude'] is None for r in c['candidates'])
    assert sum(r['checked'] for r in c['measurements'])==56

def test_ranking_and_provenance(client):
    demo(client)
    response=rank(client)
    run=response['runs'][0]
    assert run['mode']=='synthetic' and not run['stale']
    assert run['result']['type']=='SIMULATION'
    scores=run['result']['topsis']['ranked']
    assert len(scores)==4 and {r['candidate_id'] for r in scores}=={'A1','A2','A3','A4'}
    assert all(0<=r['score']<=1 for r in scores)
    assert len(run['result']['weights']['weights'])==14
    assert sum(run['result']['weights']['weights'])==pytest.approx(1,abs=1e-12)
    assert len(run['result']['sensitivity'])==10
    assert max(x['cr'] for x in run['result']['weights']['diagnostics'])<=.1

def test_observation_requires_current_baseline_and_staleness(client):
    demo(client)
    input_={'candidate_id':'A1','pedestrians_hour':231,'peak_15min':62,'vehicles_hour':1168,'speed_kmh':39.5,'calibrated':False,'source':'Skenario tambahan, bukan pengukuran','period':'Sesi demo 60 menit'}
    assert client.post('/api/observations',json=input_).status_code==409
    before=rank(client)['dataset_hash']
    r=client.post('/api/observations',json=input_)
    assert r.status_code==200,r.text
    id=r.json()['observations'][0]['id']
    result=client.post(f'/api/observations/{id}/apply',json={})
    assert result.status_code==200,result.text
    a=result.json();assert a['dataset_hash']!=before and a['runs'][0]['stale']
    values={x['code']:x['value'] for x in a['measurements'] if x['candidate_id']=='A1'}
    assert values['C1.3']==1168 and values['C2.1']==231 and values['C2.2']==62
    assert values['C1.2']!=39.5 # not calibrated
    assert client.post(f'/api/observations/{id}/apply',json={}).status_code==409
    last=rank(client);assert not last['runs'][0]['stale']
    assert len(last['runs'])==2

def test_no_fake_maps(client):
    demo(client)
    assert not any(c['coordinate_verified'] for c in client.get('/api/workspace').json()['candidates'])
    r=client.put('/api/candidates/A1',json={'label':'Area Unpad/BNI','latitude':-6.929,'longitude':107.774,'coordinate_verified':True,'coordinate_source':None,'identity_verified':False})
    assert r.status_code==422
    r=client.put('/api/candidates/A1',json={'label':'Area Unpad/BNI','latitude':-6.929,'longitude':107.774,'coordinate_verified':False,'coordinate_source':'Coordinate draft only','identity_verified':False})
    assert r.status_code==200 and not r.json()['candidates'][0]['coordinate_verified']

def test_field_data_isolated_from_synthetic(client):
    demo(client)
    r=client.put('/api/measurements',json={'candidate_id':'A1','code':'C1.1','value':5,'source':'Pengukuran eksperimen','period':'2026-11-22, 12:00 WIB','checked':True})
    assert r.status_code==409
    assert client.post('/api/workspace/clear',json={'confirm':'CLEAR_ALL_RESEARCH_DATA'}).status_code==200
    r=client.put('/api/measurements',json={'candidate_id':'A1','code':'C4.2','value':4.3,'source':'Survei tim','period':'2026-11-22','checked':True})
    assert r.status_code==422
    r=client.put('/api/measurements',json={'candidate_id':'A1','code':'C4.2','value':4,'source':'Survei tim','period':'2026-11-22','checked':False})
    assert r.status_code==200 and r.json()['mode']=='field'
    assert r.json()['readiness']['measured']==0

def test_field_ranking_requires_id_confirmation(client):
    demo_data=demo(client)
    measurements=demo_data['measurements'];judgments=demo_data['judgments']
    client.post('/api/workspace/clear',json={'confirm':'CLEAR_ALL_RESEARCH_DATA'})
    for r in measurements:
        x=client.put('/api/measurements',json={'candidate_id':r['candidate_id'],'code':r['code'],'value':r['value'],'source':'Fixture pengujian validasi input API','period':'Minggu pengujian tanpa klaim lokasi','checked':True})
        assert x.status_code==200
    e=client.post('/api/experts',json={'name':'Panel uji input'});assert e.status_code==200
    expert_id=e.json()['experts'][0]['id']
    x=client.put('/api/judgments',json={'expert_id':expert_id,'pairs':[{'level':j['level'],'i':j['pair_i'],'j':j['pair_j'],'intensity':j['intensity']} for j in judgments]})
    assert x.status_code==200
    assert client.post('/api/rankings',json={}).status_code==422
    for c in demo_data['candidates']:
        x=client.put('/api/candidates/'+c['id'],json={'label':c['label'],'identity_verified':True})
        assert x.status_code==200
    x=rank(client)
    assert x['runs'][0]['result']['type']=='FIELD_UNVALIDATED'

def test_export_contains_sources_and_audit(client):
    demo(client)
    r=client.get('/api/export');assert r.status_code==200
    assert r.json()['mode']=='synthetic'
    assert r.headers['content-disposition'].endswith('jpo-research-workspace.json"')
    assert r.json()['audit'][0]['action']=='scenario_generated'


def test_count_domain_and_period_warning(client):
    demo(client)
    before=rank(client)
    assert before['runs'][0]['result']['data_quality']['comparable_periods']
    inp={'candidate_id':'A1','pedestrians_hour':218,'peak_15min':42,'vehicles_hour':1089,'calibrated':False,'source':'Skenario inspeksi baru bukan survei','period':'Pengamatan hanya lokasi A1'}
    o=client.post('/api/observations',json=inp).json()['observations'][0]
    assert client.post(f"/api/observations/{o['id']}/apply",json={}).status_code==200
    a=rank(client)
    q=a['runs'][0]['result']['data_quality']
    assert not q['comparable_periods']
    assert {x['criterion'] for x in q['period_warnings']}=={'C1.3','C2.1','C2.2'}
    client.post('/api/workspace/clear',json={'confirm':'CLEAR_ALL_RESEARCH_DATA'})
    invalid=client.put('/api/measurements',json={'candidate_id':'A1','code':'C1.3','value':1.5,'source':'Uji bilangan bulat','period':'satu jam','checked':True})
    assert invalid.status_code==422
"""HTTP interface of the JPO research workbench. Local single-workspace prototype."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse,JSONResponse
from pydantic import BaseModel,Field,field_validator,model_validator
from fastapi.staticfiles import StaticFiles
from . import database as dbs
from .catalog import GROUPS,REFERENCES,PAPER_TITLE,CRITERIA
from .demo import demo_reset,ASSUMPTIONS
from .mcdm import calculate_weights,topsis,sensitivity,ModelError,LEVELS,GROUP_SIZES,pairs

ROOT=Path(__file__).resolve().parents[1]
@asynccontextmanager
async def lifespan(_app:FastAPI):
    dbs.initialize()
    yield

app=FastAPI(title='JPO Decision Lab',version='2.0.0',docs_url='/api/docs',openapi_url='/api/openapi.json',lifespan=lifespan)
STATIC=ROOT/'web'

def fail(code,message):raise HTTPException(status_code=code,detail=message)

def number(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):fail(422,'Value must be a finite number')
    return float(v)

class CandidateUpdate(BaseModel):
    label:str=Field(min_length=3,max_length=110)
    latitude:float|None=None
    longitude:float|None=None
    coordinate_source:str|None=Field(default=None,max_length=500)
    identity_verified:bool=False
    coordinate_verified:bool=False
    note:str=Field(default='',max_length=700)
    @model_validator(mode='after')
    def validate_map(self):
        if (self.latitude is None)!=(self.longitude is None):raise ValueError('Both latitude and longitude are required')
        if self.latitude is not None and not (-90<=self.latitude<=90 and -180<=self.longitude<=180):raise ValueError('Coordinates out of range')
        if self.coordinate_verified and (self.latitude is None or not (self.coordinate_source or '').strip()):raise ValueError('Coordinate verification requires coordinates and a source')
        return self

class MeasurementUpdate(BaseModel):
    candidate_id:str
    code:str
    value:float=Field(ge=0)
    source:str=Field(min_length=4,max_length=1000)
    period:str=Field(min_length=3,max_length=200)
    checked:bool=False

class DemoRequest(BaseModel):
    seed:int=Field(ge=1,le=999999)
    confirm:Literal['REPLACE_WORKSPACE_WITH_SYNTHETIC']

class ExpertRequest(BaseModel):
    name:str=Field(min_length=3,max_length=90)

class PairInput(BaseModel):
    level:str
    i:int=Field(ge=0)
    j:int=Field(ge=1)
    intensity:int
    @field_validator('intensity')
    @classmethod
    def valid_intensity(cls,v):
        if v==0 or abs(v)>9:raise ValueError('Judgment must be ±1..±9')
        return v

class JudgmentBatch(BaseModel):
    expert_id:int
    pairs:list[PairInput]=Field(max_length=60)

class ObservationInput(BaseModel):
    candidate_id:str
    pedestrians_hour:float=Field(ge=0,le=1e8)
    peak_15min:float=Field(ge=0,le=1e8)
    vehicles_hour:float=Field(ge=0,le=1e8)
    speed_kmh:float|None=Field(default=None,ge=0,le=250)
    calibrated:bool=False
    source:str=Field(min_length=4,max_length=1000)
    period:str=Field(min_length=3,max_length=200)
    @model_validator(mode='after')
    def valid_period(self):
        if self.peak_15min>self.pedestrians_hour:raise ValueError('Peak 15-min count exceeds hourly total')
        if self.calibrated and self.speed_kmh is None:raise ValueError('Speed calibration flag requires speed')
        return self

class ResetRequest(BaseModel):
    confirm:Literal['CLEAR_ALL_RESEARCH_DATA']

def all_rows(db,table,order='rowid'):
    return [dict(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY {order}')]

def dataset_fingerprint(db):
    snapshot={table:all_rows(db,table,order) for table,order in [
      ('candidates','id'),('measurements','candidate_id,code'),('experts','id'),('judgments','expert_id,level,pair_i,pair_j')]}
    # Timestamp not part of the hash: identical observations should not change a run.
    for c in snapshot['candidates']:c.pop('updated_at',None)
    for c in snapshot['measurements']:c.pop('updated_at',None)
    return hashlib.sha256(json.dumps(snapshot,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def payload(db,compact=False):
    candidates=all_rows(db,'candidates','id')
    criteria=all_rows(db,'criteria','group_index,code')
    measures=all_rows(db,'measurements','candidate_id,code')
    judgments=all_rows(db,'judgments','expert_id,level,pair_i,pair_j')
    experts=all_rows(db,'experts','id')
    observations=all_rows(db,'observations','id DESC')
    rows=db.execute('SELECT id,created_at,mode,dataset_hash,result_json FROM runs ORDER BY id DESC LIMIT 10').fetchall()
    fingerprint=dataset_fingerprint(db)
    runs=[{'id':r['id'],'created_at':r['created_at'],'mode':r['mode'],'dataset_hash':r['dataset_hash'], 'stale':r['dataset_hash']!=fingerprint,'result':json.loads(r['result_json'])} for r in rows]
    complete={(r['candidate_id'],r['code']) for r in measures if r['checked']}
    mode=dbs.mode(db)
    readiness={'measured':len(complete),'expected':len(candidates)*len(criteria), 'complete':len(complete)==len(candidates)*len(criteria), 'experts':len(experts), 'mode':mode,'coordinates_verified':sum(c['coordinate_verified'] for c in candidates),'identities_verified':sum(c['identity_verified'] for c in candidates)}
    result={'paper':PAPER_TITLE,'mode':mode,'candidates':candidates,'criteria':criteria,'groups':GROUPS,'measurements':measures,'experts':experts,'judgments':judgments,'observations':observations,'runs':runs,'readiness':readiness,'references':REFERENCES,'assumptions':ASSUMPTIONS,'dataset_hash':fingerprint,'app_version':'2.0.0'}
    if not compact:result['audit']=all_rows(db,'audit','id DESC')[:60]
    return result

@app.get('/api/health')
def health():return {'service':'jpo-decision-lab','status':'ok','version':'2.0.0'}

@app.get('/api/workspace')
def workspace():
    with dbs.connect() as db:return payload(db)

@app.post('/api/workspace/demo')
def generate_demo(data:DemoRequest):
    if os.environ.get('JPO_ENV','development')=='production':fail(403,'Synthetic reset disabled in production')
    with dbs.connect() as db:
        demo_reset(db,data.seed)
        return payload(db)

@app.post('/api/workspace/clear')
def clear(data:ResetRequest):
    with dbs.connect() as db:
        for table in ('observations','runs','judgments','experts','measurements'):
            db.execute(f'DELETE FROM {table}')
        db.execute('UPDATE candidates SET latitude=NULL,longitude=NULL,coordinate_source=NULL,coordinate_verified=0,identity_verified=0,note="",updated_at=?',(dbs.now(),))
        dbs.set_mode(db,'empty');dbs.audit(db,'workspace_cleared',{'origin':'user'})
        return payload(db)

@app.put('/api/candidates/{candidate_id}')
def update_candidate(candidate_id:str,data:CandidateUpdate):
    with dbs.connect() as db:
        if not db.execute('SELECT 1 FROM candidates WHERE id=?',(candidate_id,)).fetchone():fail(404,'Candidate not found')
        db.execute('UPDATE candidates SET label=?,latitude=?,longitude=?,coordinate_source=?,coordinate_verified=?,identity_verified=?,note=?,updated_at=? WHERE id=?',(
            data.label.strip(),data.latitude,data.longitude,(data.coordinate_source or '').strip() or None,int(data.coordinate_verified),int(data.identity_verified),data.note.strip(),dbs.now(),candidate_id))
        dbs.audit(db,'candidate_changed',{'id':candidate_id,'has_verified_coordinate':data.coordinate_verified})
        return payload(db)

@app.put('/api/measurements')
def update_measurement(data:MeasurementUpdate):
    val=number(data.value)
    if data.code in ('C4.2','C4.3') and (int(val)!=val or not 1<=val<=5):
        fail(422,'Ordinal criterion requires integer 1..5')
    if data.code in ('C1.1','C1.3','C1.4','C2.1','C2.2') and int(val)!=val:
        fail(422,'Count criterion requires a nonnegative whole number')
    if data.code=='C1.4' and val<1:
        fail(422,'Lane count must be at least one')
    if data.code=='C1.2' and val>250:
        fail(422,'Vehicle speed above input sanity bound; inspect the unit')
    with dbs.connect() as db:
        if dbs.mode(db)=='synthetic':fail(409,'Synthetic scenario is isolated. Clear workspace before entering field data.')
        if not db.execute('SELECT 1 FROM candidates WHERE id=?',(data.candidate_id,)).fetchone():fail(404,'Candidate not found')
        if not db.execute('SELECT 1 FROM criteria WHERE code=?',(data.code,)).fetchone():fail(404,'Criterion not found')
        db.execute('INSERT INTO measurements(candidate_id,code,value,source,period,origin,checked,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(candidate_id,code) DO UPDATE SET value=excluded.value,source=excluded.source,period=excluded.period,origin=excluded.origin,checked=excluded.checked,updated_at=excluded.updated_at',(
            data.candidate_id,data.code,val,data.source.strip(),data.period.strip(),'field',int(data.checked),dbs.now()))
        dbs.set_mode(db,'field')
        dbs.audit(db,'measurement_changed',{'candidate':data.candidate_id,'criterion':data.code,'checked':data.checked})
        return payload(db)

@app.post('/api/experts')
def add_expert(data:ExpertRequest):
    with dbs.connect() as db:
        if dbs.mode(db)=='synthetic':fail(409,'Clear synthetic scenario before entering field judgments')
        cur=db.execute('INSERT INTO experts(name,origin) VALUES(?,?)',(data.name.strip(),'field'))
        dbs.set_mode(db,'field');dbs.audit(db,'expert_added',{'id':cur.lastrowid})
        return payload(db)

@app.put('/api/judgments')
def update_judgments(data:JudgmentBatch):
    with dbs.connect() as db:
        if dbs.mode(db)=='synthetic':fail(409,'Synthetic scenario is isolated')
        if not db.execute('SELECT 1 FROM experts WHERE id=?',(data.expert_id,)).fetchone():fail(404,'Expert not found')
        for x in data.pairs:
            if x.level not in LEVELS:fail(422,'Unknown pairwise matrix')
            n=5 if x.level=='main' else GROUP_SIZES[int(x.level[-1])]
            if not (0<=x.i<x.j<n):fail(422,'Pair indices out of range')
        for x in data.pairs:
            db.execute('INSERT INTO judgments(expert_id,level,pair_i,pair_j,intensity) VALUES(?,?,?,?,?) ON CONFLICT(expert_id,level,pair_i,pair_j) DO UPDATE SET intensity=excluded.intensity',(
                data.expert_id,x.level,x.i,x.j,x.intensity))
        dbs.audit(db,'judgments_updated',{'expert_id':data.expert_id,'count':len(data.pairs)})
        return payload(db)

def ordered_experts(db):
    ex=all_rows(db,'experts','id');rows=all_rows(db,'judgments','expert_id,level,pair_i,pair_j')
    for e in ex:
        e['judgments']={lev:{} for lev in LEVELS}
        for r in rows:
            if r['expert_id']==e['id']:
                e['judgments'][r['level']][(r['pair_i'],r['pair_j'])]=r['intensity']
    return ex

@app.post('/api/rankings')
def compute_rankings():
    with dbs.connect() as db:
        c=all_rows(db,'candidates','id');criteria=all_rows(db,'criteria','group_index,code')
        measurements=all_rows(db,'measurements','candidate_id,code')
        values={(r['candidate_id'],r['code']):r for r in measurements if r['checked']}
        missing=[f"{x['id']}/{cr['code']}" for x in c for cr in criteria if (x['id'],cr['code']) not in values]
        if missing:fail(422,{'message':'Incomplete verified matrix','missing_count':len(missing),'first_missing':missing[:8]})
        if dbs.mode(db)=='field' and any(not x['identity_verified'] for x in c):fail(422,'Confirm all four candidate identities before using field data')
        if dbs.mode(db) not in ('synthetic','field'):fail(422,'No valid data loaded')
        experts=ordered_experts(db)
        try:
            weights=calculate_weights(experts)
            matrix=[[values[x['id'],cr['code']]['value'] for cr in criteria] for x in c]
            directions=[cr['direction'] for cr in criteria]
            rank=topsis(matrix,weights['weights'],directions)
            comparison=topsis(matrix,weights['crisp_weights'],directions)
            sens=sensitivity(matrix,weights['weights'],directions)
        except (ValueError,OverflowError,ZeroDivisionError) as exc:fail(422,str(exc))
        ids=[x['id'] for x in c]
        for rs in (rank,comparison):
            for record in rs['ranked']:record['candidate_id']=ids[record['candidate_index']]
        # Observation periods across alternatives must be examined, particularly
        # after asynchronous IoT updates. The research protocol requires
        # matched sampling windows before an engineering interpretation.
        period_warnings=[]
        for cr in criteria:
            periods={values[x['id'],cr['code']]['period'].strip() for x in c}
            if len(periods)>1:
                period_warnings.append({'criterion':cr['code'],'distinct_periods':sorted(periods)})
        result={'weights':weights,'topsis':rank,'ahp_comparison':comparison,'sensitivity':sens,
                'data_quality':{'period_warnings':period_warnings,'comparable_periods':not bool(period_warnings)},
                'type':'SIMULATION' if dbs.mode(db)=='synthetic' else 'FIELD_UNVALIDATED',
                'disclaimer':'Prioritas kajian lanjutan, bukan rekomendasi konstruksi',
                'methods':'Buckley fuzzy geometric mean / centroid / normalized vector TOPSIS'}
        hash_=dataset_fingerprint(db)
        cur=db.execute('INSERT INTO runs(created_at,mode,dataset_hash,result_json) VALUES(?,?,?,?)',(
          dbs.now(),dbs.mode(db),hash_,json.dumps(result,ensure_ascii=False)))
        dbs.audit(db,'ranking_computed',{'run_id':cur.lastrowid,'mode':dbs.mode(db),'top':rank['ranked'][0]['candidate_id']})
        return payload(db)

@app.post('/api/observations')
def observe(data:ObservationInput):
    with dbs.connect() as db:
        if not db.execute('SELECT 1 FROM candidates WHERE id=?',(data.candidate_id,)).fetchone():fail(404,'Candidate not found')
        mode=dbs.mode(db)
        if mode not in ('field','synthetic'):fail(409,'Enter baseline data first')
        current_hash=dataset_fingerprint(db)
        if not db.execute('SELECT 1 FROM runs WHERE dataset_hash=? ORDER BY id DESC LIMIT 1',(current_hash,)).fetchone():
            fail(409,'Generate a baseline ranking for the current data before observations')
        cur=db.execute('INSERT INTO observations(candidate_id,pedestrians_hour,peak_15min,vehicles_hour,speed_kmh,calibrated,source,period,origin,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(
            data.candidate_id,data.pedestrians_hour,data.peak_15min,data.vehicles_hour,data.speed_kmh,int(data.calibrated),data.source.strip(),data.period.strip(),'synthetic' if mode=='synthetic' else 'field',dbs.now()))
        dbs.audit(db,'observation_recorded',{'id':cur.lastrowid,'origin':mode})
        return payload(db)

@app.post('/api/observations/{observation_id}/apply')
def apply_observation(observation_id:int):
    with dbs.connect() as db:
        obs=db.execute('SELECT * FROM observations WHERE id=?',(observation_id,)).fetchone()
        if obs is None:fail(404,'Observation not found')
        if obs['applied']:fail(409,'Observation already applied')
        origin=obs['origin']
        updates=[('C1.3',obs['vehicles_hour']),('C2.1',obs['pedestrians_hour']),('C2.2',obs['peak_15min'])]
        if obs['calibrated'] and obs['speed_kmh'] is not None:updates.append(('C1.2',obs['speed_kmh']))
        for code,val in updates:
            db.execute('INSERT INTO measurements(candidate_id,code,value,source,period,origin,checked,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(candidate_id,code) DO UPDATE SET value=excluded.value,source=excluded.source,period=excluded.period,origin=excluded.origin,checked=excluded.checked,updated_at=excluded.updated_at',(
               obs['candidate_id'],code,val,f"Observation #{observation_id}: {obs['source']}",obs['period'],origin,1,dbs.now()))
        db.execute('UPDATE observations SET applied=1 WHERE id=?',(observation_id,))
        dbs.audit(db,'observation_applied',{'id':observation_id,'codes':[x[0] for x in updates]})
        return payload(db)

@app.get('/api/export')
def export():
    with dbs.connect() as db:
        data=payload(db);data['exported_at']=dbs.now()
        return JSONResponse(data,headers={'Content-Disposition':'attachment; filename="jpo-research-workspace.json"'})

# Explicit surface: compiled assets are served from the same origin as the API.
if STATIC.is_dir():
    app.mount('/assets',StaticFiles(directory=STATIC),name='assets')

@app.get('/')
def index():
    return FileResponse(STATIC/'index.html',headers={'Cache-Control':'no-store'})
"""Research-informed illustrative scenario; NO measured Jatinangor values.

Speed bands and construction-cost examples are external anchors. All other
ranges are transparent design assumptions, not inferred local observations.
"""
from __future__ import annotations
import random
from .catalog import CANDIDATES, CRITERIA
from .database import now,audit,set_mode
from .mcdm import GROUP_SIZES,pairs

ASSUMPTIONS={
 "C1.1": (0,4,"illustrative count, no official crossing-level dataset"),
 "C1.2": (22,46,"illustrative speeds under national urban reference of 50 km/h; actual road limit unverified"),
 "C1.3": (450,1900,"assumed one-hour traffic sample; no confirmed Jatinangor count"),
 "C1.4": (2,6,"illustrative lane count; verify road geometry"),
 "C2.1": (80,550,"assumed crossings/hour; no verified pedestrian survey"),
 "C2.2": (25,145,"assumed peak crossings/15 min; constrained by hourly pedestrians"),
 "C3.1": (80,650,"illustrative walking distance; no mapped origin/destination measurements"),
 "C3.2": (35,510,"illustrative walking distance to transit; no GIS verification"),
 "C4.1": (65,460,"illustrative usable land area; site survey required"),
 "C4.2": (1,5,"ordinal rubric not agreed; illustration only"),
 "C4.3": (1,5,"ordinal rubric not agreed; illustration only"),
 "C5.1": (3.2e9,9.5e9,"illustrative budgets within multi-region public procurement scale; NOT an estimate for Jatinangor"),
 "C5.2": (0,350,"illustrative additional land; cadastral verification required"),
 "C5.3": (6e7,3.8e8,"assumed annual operations/maintenance; not from public cost dataset"),
}
INTEGER_CODES={"C1.1","C1.3","C1.4","C2.1","C2.2","C4.2","C4.3"}
GROUP_BASE=[[4,2,2,1,1],[2,2,1,1],[2,1],[1,1],[2,1,1],[2,1,1]]

def demo_reset(db,seed:int):
    rng=random.Random(seed)
    for table in ("observations","runs","judgments","experts","measurements"):
        db.execute(f"DELETE FROM {table}")
    db.execute("UPDATE candidates SET latitude=NULL,longitude=NULL,coordinate_source=NULL,coordinate_verified=0,identity_verified=0,note='',updated_at=?",(now(),))
    db.execute("UPDATE candidates SET label=? WHERE id='A4'",(CANDIDATES[3][1],))
    for id,name in CANDIDATES[:3]:
        db.execute("UPDATE candidates SET label=? WHERE id=?",(name,id))
    for cid,_ in CANDIDATES:
        pedestrian_hour=None
        for code,_,label,_,_,_ in CRITERIA:
            low,high,reason=ASSUMPTIONS[code]
            val=rng.uniform(low,high)
            if code=="C2.1":pedestrian_hour=round(val)
            if code=="C2.2": val=min(val, int(pedestrian_hour*.65))
            if code in INTEGER_CODES:val=round(val)
            if code in ("C5.1","C5.3"):val=round(val/1e7)*1e7
            else:val=round(val,2)
            source=f"SYNTHETIC seed={seed}; {reason}"
            db.execute("INSERT INTO measurements(candidate_id,code,value,source,period,origin,checked,updated_at) VALUES(?,?,?,?,?,?,?,?)",(cid,code,val,source,'SIMULASI: interval konstruksi data, bukan survei','synthetic',1,now()))
    cur=db.execute("INSERT INTO experts(name,origin) VALUES(?,?)",('Panel simulasi — bobot ilustratif','synthetic'))
    expert=cur.lastrowid
    for level,values in zip(['main']+[f'local{g}' for g in range(5)], GROUP_BASE):
        for i,j in pairs(len(values)):
            r=values[i]/values[j]
            intensity=round(r) if r>=1 else -round(1/r)
            db.execute("INSERT INTO judgments(expert_id,level,pair_i,pair_j,intensity) VALUES(?,?,?,?,?)",(expert,level,i,j,intensity))
    set_mode(db,'synthetic')
    audit(db,'scenario_generated',{'seed':seed,'origin':'synthetic','warning':'No Jatinangor measurement or expert judgment was used'})
    return {'seed':seed,'origin':'synthetic','assumptions':ASSUMPTIONS}
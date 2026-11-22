import math
import pytest
from server.mcdm import consistency,calculate_weights,topsis,ModelError,sensitivity,RI,LEVELS,GROUP_SIZES,pairs

def test_cr_consistent_reciprocal():
    base=[4.,2.,1.,1.,.5]
    matrix=[[a/b for b in base] for a in base]
    assert consistency(matrix)['cr']==pytest.approx(0,abs=1e-12)

def test_bad_cr_rejected():
    fake={lev:{} for lev in LEVELS}
    for lev,n in zip(LEVELS,[5,*GROUP_SIZES]):
        for i,j in pairs(n):fake[lev][(i,j)]=1
    fake['main'][(0,1)]=9
    fake['main'][(1,2)]=9
    fake['main'][(0,2)]=-9
    with pytest.raises(ModelError,match='Inconsistent'):
        calculate_weights([{'name':'Reviewer test','judgments':fake}])

def test_topsis_benefit_cost_known_solution():
    # Two dimensions, point A best on both: x larger, cost smaller.
    r=topsis([[10,1],[1,10]],[.5,.5],['Benefit','Cost'])
    assert r['ranked'][0]['candidate_index']==0
    assert r['ranked'][0]['score']==pytest.approx(1.0)
    assert r['ranked'][1]['score']==pytest.approx(0.0)

def test_topsis_equal_candidates_undefined():
    with pytest.raises(ModelError,match='identical|equal|undefined'):
        topsis([[1,1],[1,1]],[.5,.5],['Benefit','Cost'])

def test_topsis_missing_rejected():
    with pytest.raises((ModelError,TypeError)):
        topsis([[1,None],[2,3]],[.5,.5],['Benefit','Cost'])

def test_sensitivity_deterministic():
    matrix=[[float((i+j)%6+1) for j in range(14)] for i in range(4)]
    weights=[1/14]*14
    out=sensitivity(matrix,weights,['Benefit' if j%2 else 'Cost' for j in range(14)])
    assert len(out)==10 and out[0]['group']==0 and out[-1]['group']==4
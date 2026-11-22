"""Deterministic two-stage Fuzzy AHP / TOPSIS.

Buckley fuzzy geometric mean, centroid defuzzification and Saaty CR are
IMPLEMENTATION choices; the manuscript does not uniquely prescribe them.
"""
from __future__ import annotations
import math

RI={1:0,2:0,3:.58,4:.9,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45}
GROUP_SIZES=[4,2,2,3,3]
LEVELS=['main','local0','local1','local2','local3','local4']

class ModelError(ValueError): pass

def pairs(n):
    return [(i,j) for i in range(n) for j in range(i+1,n)]

def tfn(intensity):
    s=int(intensity)
    if not s or abs(s)>9:raise ModelError('Intensity must be ±1 to ±9.')
    if s<0:
        l,m,u=tfn(-s)
        return (1/u,1/m,1/l)
    if s==1:return (1.,1.,1.)
    if s==9:return (9.,9.,9.)
    return (float(s-1),float(s),float(min(9,s+1)))

def judgment_matrix(n, values, fuzzy=False):
    matrix=[[[(1.,1.,1.) if i==j else None][0] if fuzzy else (1. if i==j else None) for j in range(n)] for i in range(n)]
    for i,j in pairs(n):
        key=(i,j)
        if key not in values:raise ModelError(f'Pairwise value missing for {i}-{j}')
        l,m,u=tfn(values[key]); matrix[i][j]=(l,m,u) if fuzzy else m
        matrix[j][i]=(1/u,1/m,1/l) if fuzzy else 1/m
    return matrix

def geo(values):
    if not values or any(v<=0 or not math.isfinite(v) for v in values):raise ModelError('Invalid matrix weight')
    return math.exp(sum(math.log(v) for v in values)/len(values))

def normalized(weights):
    total=sum(weights)
    if total<=0 or not math.isfinite(total):raise ModelError('Invalid weight sum')
    return [v/total for v in weights]

def crisp_weights(matrix):
    return normalized([geo(row) for row in matrix])

def consistency(matrix):
    n=len(matrix);w=crisp_weights(matrix)
    if n<3:return {'cr':0.,'ci':0.,'lambda_max':float(n)}
    lam=sum(sum(a*wj for a,wj in zip(row,w))/wi for row,wi in zip(matrix,w))/n
    ci=max(0.,(lam-n)/(n-1))
    return {'cr':ci/RI[n],'ci':ci,'lambda_max':lam}

def calculate_weights(experts):
    if not experts:raise ModelError('A decision panel is required')
    group_weights=[]; diagnostics=[]; crisp_group_weights=[]
    for level,n in zip(LEVELS,[5,*GROUP_SIZES]):
        matrices=[];crisp_matrices=[]
        for expert in experts:
            values=expert['judgments'].get(level,{})
            cm=judgment_matrix(n,values,False)
            diag=consistency(cm)
            diagnostics.append({'expert':expert['name'],'level':level,'cr':diag['cr']})
            if diag['cr']>0.1+1e-12:raise ModelError(f"Inconsistent judgments: {expert['name']} {level}, CR={diag['cr']:.3f}")
            matrices.append(judgment_matrix(n,values,True))
            crisp_matrices.append(cm)
        avg=[]
        crisp_avg=[]
        for i in range(n):
            avg.append([]);crisp_avg.append([])
            for j in range(n):
                avg[i].append([geo([m[i][j][k] for m in matrices]) for k in range(3)])
                crisp_avg[i].append(geo([m[i][j] for m in crisp_matrices]))
        g=[[geo([t[k] for t in row]) for k in range(3)] for row in avg]
        sums=[sum(t[k] for t in g) for k in range(3)]
        triangles=[(t[0]/sums[2],t[1]/sums[1],t[2]/sums[0]) for t in g]
        group_weights.append(normalized([sum(t)/3 for t in triangles]))
        crisp_group_weights.append(crisp_weights(crisp_avg))
    global_weights=normalized([group_weights[0][g]*w for g,n in enumerate(GROUP_SIZES) for w in group_weights[g+1]])
    crisp_global=normalized([crisp_group_weights[0][g]*w for g,n in enumerate(GROUP_SIZES) for w in crisp_group_weights[g+1]])
    return {'weights':global_weights,'group_weights':group_weights[0], 'local_weights':group_weights[1:], 'crisp_weights':crisp_global,'diagnostics':diagnostics}

def topsis(matrix, weights, directions):
    m=len(matrix);n=len(weights)
    if m<2 or any(len(row)!=n for row in matrix) or len(directions)!=n:raise ModelError('Invalid TOPSIS shape')
    if any(not math.isfinite(x) or x<0 for row in matrix for x in row):raise ModelError('Invalid observation')
    if any(not math.isfinite(x) or x<0 for x in weights) or abs(sum(weights)-1)>1e-8:raise ModelError('Invalid weights')
    norms=[math.sqrt(sum(row[j]**2 for row in matrix)) for j in range(n)]
    weighted=[[0. if norms[j]==0 else row[j]*weights[j]/norms[j] for j in range(n)] for row in matrix]
    plus=[];minus=[]
    for j in range(n):
        vals=[row[j] for row in weighted]
        if directions[j] not in ('Benefit','Cost'):raise ModelError('Invalid direction')
        plus.append(max(vals) if directions[j]=='Benefit' else min(vals))
        minus.append(min(vals) if directions[j]=='Benefit' else max(vals))
    out=[]
    for i,row in enumerate(weighted):
        dp=math.dist(row,plus);dm=math.dist(row,minus)
        if dp+dm==0:raise ModelError('All alternatives equal; ranking undefined')
        out.append({'candidate_index':i,'score':dm/(dp+dm),'d_plus':dp,'d_minus':dm})
    out.sort(key=lambda a:(-a['score'],a['candidate_index']))
    for idx,r in enumerate(out):
        r['rank']=out[idx-1]['rank'] if idx and abs(out[idx-1]['score']-r['score'])<=1e-10 else idx+1
    return {'ranked':out,'ideal_positive':plus,'ideal_negative':minus,'norms':norms,'zero_norm_columns':[j for j,x in enumerate(norms) if not x]}

def sensitivity(matrix, weights, directions, fraction=.10):
    base=topsis(matrix,weights,directions)['ranked'][0]['candidate_index']
    scenarios=[];groups=[g for g,n in enumerate(GROUP_SIZES) for _ in range(n)]
    for g in range(len(GROUP_SIZES)):
        for factor in (1-fraction,1+fraction):
            altered=normalized([v*(factor if groups[j]==g else 1) for j,v in enumerate(weights)])
            rank=topsis(matrix,altered,directions)['ranked']
            scenarios.append({'group':g,'factor':factor,'leader_changed':rank[0]['candidate_index']!=base,'leader_index':rank[0]['candidate_index']})
    return scenarios
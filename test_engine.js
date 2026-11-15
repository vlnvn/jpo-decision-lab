'use strict';const assert=require('node:assert/strict'),E=require('./engine.js');
const near=(a,b,eps=1e-8)=>assert.ok(Math.abs(a-b)<eps,`${a} ≉ ${b}`);
const groupSizes=[4,2,2,3,3];const groups=groupSizes.map((_,i)=>'local'+i);
function expertsComplete(v=1){const pairs={};for(const[key,n]of [['main',5],...groups.map((g,i)=>[g,groupSizes[i]])])pairs[key]=Object.fromEntries(E.pairs(n).map(([i,j])=>[`${i}-${j}`,v]));return[{name:'PAKAR_UJI_SINTETIS',pairs}];}
function mustThrow(fn,text){assert.throws(fn,e=>e.message.includes(text),`expected error: ${text}`)}
near(E.scale(3)[0],2);near(E.scale(-3)[0],.25);assert.deepEqual(E.scale(9),[9,9,9]);assert.deepEqual(E.scale(-9),[1/9,1/9,1/9]);
assert.deepEqual(E.pairs(3),[[0,1],[0,2],[1,2]]);
const w=E.buildWeights(expertsComplete(),groupSizes);
near(w.weights.reduce((a,b)=>a+b,0),1);near(w.weights[0],.05);near(w.weights[4],.10);near(w.weights[8],1/15);near(w.crispWeights.reduce((a,b)=>a+b,0),1);
assert.equal(w.diagnostics.length,6);w.diagnostics.forEach(x=>near(x.cr,0));
mustThrow(()=>E.buildWeights(expertsComplete('').map(e=>({...e,name:''})),groupSizes),'Nama');
const i=expertsComplete();i[0].pairs.local4['0-1']=9;i[0].pairs.local4['0-2']=-9;i[0].pairs.local4['1-2']=9;
mustThrow(()=>E.buildWeights(i,groupSizes),'konsistensi');
const out=E.topsis([[0,10],[10,0]],[.5,.5],['Benefit','Cost']);assert.equal(out.ranked[0].index,1);near(out.ranked[0].score,1);near(out.ranked[1].score,0);
const z=E.topsis([[0,1],[0,2]],[.5,.5],['Benefit','Cost']);assert.deepEqual(z.zeroNormCriteria,[0]);assert.equal(z.ranked[0].index,0);
mustThrow(()=>E.topsis([[1,1],[1,1]],[.5,.5],['Benefit','Cost']),'tidak terdefinisi');
mustThrow(()=>E.topsis([[1,1],[1,2]],[.4,.5],['Benefit','Cost']),'berjumlah 1');
let sens=E.sensitivity(Array.from({length:4},(_,r)=>Array.from({length:14},(_,j)=>1+(r+j)%5)),w.weights,Array.from({length:14},(_,i)=>i<6?'Benefit':'Cost'),groupSizes);
assert.equal(sens.length,10);
console.log('Engine tests PASS — scale 9 source parity, consistency, FAHP, TOPSIS, sensitivity; synthetic fixtures only.');
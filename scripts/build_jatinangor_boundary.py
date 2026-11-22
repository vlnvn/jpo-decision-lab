"""Reconstruct Jatinangor outline derived from HDX/BPS 2020 village geometries.

The perimeter was assembled from shared edges of the 12 village polygons
in JfrAziz/indonesia-district, then simplified with an angular tolerance
of 0.00007 degrees for cartographic display only.
The encoded path is Google Polyline at 1e-5-degree precision.
"""
import json
from pathlib import Path
POLYLINE=r'''heki@ysupSaIrE}DZsFuAkAz@WdB{E|@_Be@Iq@yB_@{As@WTH|@]@uAi@k@Hs@UaATa@oAy@MsCD_Cv@aBxAqBGEwAm@W}AD_@rA{Fe@sDCa@p@?bBmAMOk@kBi@YcAgBYc@X[I]yB}@WkD|AqAoBCc@gCEkBrAk@BqF{@uBVw@Sw@o@eCg@Q}Cu@m@c@h@El@_@H{Fg@Gv@]@K|@S@_D}BkArBSCGgAOImB]{@HK\Vv@kCv@g@j@yBZaAv@iA_@k@y@q@Jg@_AqB{@i@TqAcDaCs@oAyBoFsCsBcBeBDqKkAcEmDaGRcGkC_CgBaAMcDDs@Vm@nB}BDcEdAk@K_@mCyAa@}@m@{@wAg@M}AVcAr@_BlGc@PqAK_A\aHjFeB}AJo@dAs@He@Wi@}Ci@FmAt@qAlAa@s@iJ_AErAmCfCkCtV}QiBiCvAcFeBeFwBeAIuDaAk@]uA}DyGcBf@sAuAOe@NwApA_Gl@@|@sCZUbBj@FZJeAxBPnCuCnG`@hBmBn@mCrBYLs@WqB}@K[c@LcB|@i@Bs@MsAmA}BmCZk@b@Y[o@BMV{EqAR_Ay@_Ao@AcDbAo@k@oAUVeCfDwBvBk@xBCbF`BhCgAPwAhAs@xBpBXOCyA~Bo@~BTh@N`@r@jBJrKrClAN|B]rAHnAx@@hBM^_@AQaAw@Ue@jCx@|AzExDBrDv@d@\CtAwA^Hj@vCpDvA`A_@lBoHbAq@jBZvAvAj@lArDtB\QFqAe@kBjA}@n@B~@f@|@dATxBv@CnAyAFs@i@_CdDKnFnAd@Qh@kAtCQP]Mi@kAkAUkBNYd@@pAbA~@KfDrAh@ApBsC~Ai@nBKN\i@xBbCY`As@e@cBp@uBE][Pc@Yi@{@@g@`D}BC{AqFcF]u@x@YtAiCzAMCeAtBuCMqD~ASjBeBVk@c@}Bl@{DxMsRbDeClA}B`A}@vCw@|FyCf@q@z@E~BcAvDOd@}@|MyCzHN~IlEzAtArAJhKUfRkE|D_@jCb@zBz@rDzChLrL`DpChAVA\vBtAvD\zHA|@jBs@fCj@T|KBfAq@tAE`Sd@~BKlAc@b@b@StF|CpAHfDa@~C\z@gAnGTd@lBZ}Phu@i@Ee@nBuIw@UvCiADO|AsADeCs@q@tJ|@LWtDfLrA_BbH^FeDfOlI^zBn@XkDnEr@gArNi@DYf@[rBYCyE`K{FiC_Cm@gAy@i@yAaGvWcHdJvARr@jClA_@vBEToCzDb@B`EjERbAvCa@vCiOz@m@pAoB|HfL|CFtAdBl@`@xC?~Cq@Ep@dAvAnG_IzA}BlBqFlBmDSoAy@a@ZeAg@iBmCoDuAEg@c@]aCaA}BWQ_@eC_AD}@U_A}CkAQ{@eMcFe@X'''

def decode(p):
    coords=[];i=0;lat=lng=0
    while i<len(p):
        out=[]
        for _ in range(2):
            shift=0;result=0
            while True:
                b=ord(p[i])-63;i+=1
                result|=(b&31)<<shift;shift+=5
                if b<32:break
            out.append(~(result>>1) if (result&1) else (result>>1))
        lat+=out[0];lng+=out[1]
        coords.append([round(lng/1e5,5),round(lat/1e5,5)])
    return coords

if __name__=='__main__':
    ring=decode(POLYLINE)
    assert ring[0]==ring[-1], (ring[0],ring[-1])
    from shapely.geometry import Polygon
    from pyproj import Geod
    poly=Polygon(ring)
    area, perimeter=Geod(ellps='WGS84').geometry_area_perimeter(poly)
    print('vertices',len(ring),'valid',poly.is_valid,'area km2',round(abs(area)/1e6,3),'bounds',poly.bounds)
    assert poly.is_valid and abs(area)>15e6 and len(ring)>150
    geo={'type':'FeatureCollection','metadata':{'boundary_kind':'generalized visual administrative boundary','fitness':'not legal boundary, not survey grade','source':'HDX-BPS 2020','source_url':'https://github.com/JfrAziz/indonesia-district','source_date':'2019-12-20','original_outer_vertices':1057,'display_outer_vertices':391,'aggregation':'dissolve of 12 village geometries'},'features':[{'type':'Feature','properties':{'code':'32.11.15','name':'KECAMATAN JATINANGOR','parent_name':'KABUPATEN SUMEDANG','source':'HDX-BPS-2020','source_date':'2019-12-20','valid_on':'2020-04-01','geometry_kind':'Dissolved perimeter of twelve village MultiPolygons','render_simplification_tolerance_degrees':0.00007,'usage':'Research cartographic context only; not a certified legal boundary'},'geometry':{'type':'Polygon','coordinates':[ring]}}]}
    path=Path(__file__).resolve().parents[1]/'web/data/jatinangor.geojson'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(geo,ensure_ascii=False,separators=(',',':'))+'\n')
    print('wrote',path,'bytes',path.stat().st_size)
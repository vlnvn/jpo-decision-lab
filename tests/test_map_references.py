"""Browser-level map marker accessibility without externally hosted tiles."""
import os,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=re.sub(r'<script[^>]*>.*?</script>','',re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',(ROOT/'web/index.html').read_text()),flags=re.S)
CSS=(ROOT/'web/styles.css').read_text()+'\n'+(ROOT/'web/studio.css').read_text()
JS=(ROOT/'web/app.js').read_text()


def test_four_reference_pins_are_distinct_from_verified_crossings(client):
    state=client.get('/api/workspace').json(); geo=client.get('/api/geography/jatinangor').json()
    with sync_playwright() as p:
        exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        b=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':exe} if exe else {}))
        page=b.new_page(viewport={'width':1920,'height':1080})
        page.set_content(HTML);page.add_style_tag(content=CSS)
        page.evaluate('([data,geo]) => { window.fetch=async url=>({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data}); }',[state,geo])
        page.add_script_tag(content=JS)
        page.locator('.reference-fallback').first.wait_for()
        assert page.locator('.reference-fallback').count()==4
        assert page.locator('.map-pin').count()==0
        assert page.get_by_text('0 / 4').count()>0
        width=page.evaluate('document.documentElement.scrollWidth')
        assert width==1920
        code=page.locator('.candidate-list .location-code').first
        assert code.evaluate('(el)=>getComputedStyle(el).display')=='grid'
        page.get_by_role('button',name='Pilih kandidat Simpang Ciseke/Sayang').click()
        assert page.locator('.reference-fallback.active').count()==1
        assert page.locator('.reference-fallback.active .fallback-number').text_content()=='A2'
        b.close()


def test_leaflet_receives_four_source_tethered_markers(client):
    state=client.get('/api/workspace').json();geo=client.get('/api/geography/jatinangor').json()
    with sync_playwright() as p:
        exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        b=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':exe} if exe else {}))
        page=b.new_page(viewport={'width':1920,'height':1080})
        page.set_content(HTML);page.add_style_tag(content=CSS)
        page.evaluate('''([data,geo]) => {
            window.fetch=async url=>({ok:true,status:200,json:async()=>String(url).includes('geography/jatinangor')?geo:data});
            window.__markers=[];
            const layer=()=>({addTo(){return this;},setStyle(){return this;},bindPopup(){return this;},on(){return this;}});
            window.L={
                map:()=>({attributionControl:{addAttribution(){},removeAttribution(){}},setView(){return this;},on(){return this;},remove(){},removeLayer(){},fitBounds(){return this;},getZoom(){return 13;},flyTo(){return this;}}),
                latLngBounds:()=>({pad(){return this;}}),control:{zoom:()=>({addTo(){}})},
                polygon:layer,polyline:layer,
                divIcon:x=>x,
                marker:(xy,opts)=>{window.__markers.push({xy,html:opts.icon.html});return layer();},
                tileLayer:()=>layer(),maplibreGL:()=>({addTo(){return this;},getMaplibreMap:()=>({on(name,fn){if(name==='load')queueMicrotask(fn);}})})
            };
        }''',[state,geo]);page.add_script_tag(content=JS)
        page.locator('.district-illustration').wait_for()
        markers=page.evaluate('window.__markers')
        assert len(markers)==4
        for id,marker in zip(('A1','A2','A3','A4'),markers):
            assert id in marker['html'] and 'reference-tether' in marker['html']
        assert page.locator('.map-pin').count()==0
        b.close()
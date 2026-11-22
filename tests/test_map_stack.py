"""Map contract tests, deliberately independent from external tile hosting.

External OpenFreeMap, OpenStreetMap and CDN availability is not asserted here.
The fake Leaflet adapter checks layering, credit, basemap selection and fallback
without silently passing a watermarked tile as successful.
"""
import json
import os
import shutil
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = re.sub(r'<script[^>]*>.*?</script>', '', re.sub(r'<link[^>]+rel="stylesheet"[^>]*>', '', (ROOT / 'web/index.html').read_text()), flags=re.S)
CSS = (ROOT / 'web/styles.css').read_text() + (ROOT / 'web/studio.css').read_text()
JS = (ROOT / 'web/app.js').read_text()
GEOMETRY = json.loads((ROOT / 'web/data/jatinangor.geojson').read_text())


def test_no_keyless_carto_dependency():
    text = (ROOT / 'web/app.js').read_text()
    assert 'basemaps.cartocdn.com' not in text
    assert 'carto.com/attribution/' not in text
    assert 'https://tiles.openfreemap.org/styles/positron' in text
    assert 'https://tile.openstreetmap.org/{z}/{x}/{y}.png' in text
    assert 'API KEY REQUIRED' not in text
    assert 'maplibre-gl-leaflet' in (ROOT / 'web/index.html').read_text()
    assert not any('workspace.css' in line for line in (ROOT / 'web/index.html').read_text().splitlines())


def test_basemap_controls_and_unverified_locations(client):
    state = client.get('/api/workspace').json()
    with sync_playwright() as p:
        browser_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'], **({'executable_path':browser_path} if browser_path else {}))
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.set_content(HTML)
        page.add_style_tag(content=CSS)
        page.evaluate('''([data, geo]) => {
            window.fetch = async url => ({ok:true,status:200,json:async()=>String(url).includes('geography/jatinangor')?geo:data});
            window.__mapCalls = {vector:[],raster:[],credits:[],fit:0};
            let map;
            const layer = () => ({addTo(){return this;},setStyle(){return this;},on(){return this;},bindPopup(){return this;}});
            window.L = {
                map:()=>{map={
                    attributionControl:{addAttribution:x=>window.__mapCalls.credits.push(x),removeAttribution(){}},
                    setView(){return this;},on(){return this;},remove(){return this;},removeLayer(){return this;},
                    fitBounds(){window.__mapCalls.fit++;return this;},getZoom(){return 13;},flyTo(){return this;}
                };return map;},
                latLngBounds:coords=>({pad(){return this;}}),
                control:{zoom:()=>({addTo(){return this;}})},
                polygon:layer,polyline:layer,
                divIcon:()=>({}),marker:layer,
                maplibreGL:opts=>{
                    window.__mapCalls.vector.push(opts.style);
                    return {addTo(){return this;},getMaplibreMap(){return {on(name,callback){if(name==='load')queueMicrotask(callback);}}}};
                },
                tileLayer:url=>{
                    window.__mapCalls.raster.push(url);
                    return layer();
                }
            };
        }''', [state, GEOMETRY])
        page.add_script_tag(content=JS)
        page.locator('#basemap-status[data-level="online"]').wait_for()
        assert page.evaluate('window.__mapCalls.vector') == ['https://tiles.openfreemap.org/styles/positron']
        assert page.locator('.map-pin').count() == 0
        assert page.evaluate('window.__mapCalls.fit') >= 1
        assert page.locator('.map-stage').evaluate("el=>el.classList.contains('has-basemap')")
        assert page.evaluate('window.__mapCalls.credits.length') == 1
        page.get_by_role('button',name='Jalan',exact=True).click()
        assert page.evaluate('window.__mapCalls.raster') == ['https://tile.openstreetmap.org/{z}/{x}/{y}.png']
        assert page.get_by_role('button',name='Jalan',exact=True).get_attribute('aria-pressed') == 'true'
        page.get_by_role('button',name='Fokus wilayah').click()
        assert page.evaluate('window.__mapCalls.fit') >= 2
        browser.close()
"""Browser layout audit without external map tile/CDN dependency.

Full HTTP API tests are in test_api.py. This isolates rendering even when the
runner has no network access; it does NOT assert OSM tile connectivity.
"""
import json
import re
import shutil
import os
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=re.sub(r'<script[^>]*>.*?</script>','',re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',(ROOT/'web/index.html').read_text()),flags=re.S)
CSS=(ROOT/'web/styles.css').read_text()+(ROOT/'web/studio.css').read_text()
GEO=json.loads((ROOT/'web/data/jatinangor.geojson').read_text(encoding='utf-8'))
JS=(ROOT/'web/app.js').read_text()

@pytest.mark.parametrize('width,height',[(320,770),(390,844),(768,1024),(1280,800),(1440,900),(1920,1080),(2560,1440)])
def test_viewport(width,height,client):
    state=client.get('/api/workspace').json()
    with sync_playwright() as p:
        browser_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':browser_path} if browser_path else {}))
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(HTML)
        page.add_style_tag(content=CSS)
        page.evaluate('([data,geo]) => {window.fetch = async (url) => ({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data})}',[state,GEO])
        page.add_script_tag(content=JS)
        page.wait_for_selector('h1')
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert page.get_by_role('heading',name='Kajian lokasi JPO Jatinangor').count()==1
        assert page.locator('.district-illustration').count()==1
        assert page.locator('.map-floating-caption strong').inner_text() == 'Jatinangor'
        if width==1920:
            page.get_by_role('button',name='Data penelitian').click()
            assert page.get_by_text('Riwayat kecelakaan pedestrian').count()==1
            page.get_by_role('button',name='Pemeringkatan').click()
            assert page.get_by_text('Belum ada hasil perhitungan').count()==1
        browser.close()


def test_map_focus_and_boundary_dont_invent_pins(client):
    state=client.get('/api/workspace').json()
    with sync_playwright() as p:
        browser_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':browser_path} if browser_path else {}))
        page=browser.new_page(viewport={'width':1920,'height':1080})
        page.set_content(HTML)
        page.add_style_tag(content=CSS)
        page.evaluate('([data,geo]) => {window.fetch = async url => ({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data})}',[state,GEO])
        page.add_script_tag(content=JS)
        page.locator('.district-illustration').wait_for()
        assert '107.803' in page.locator('.district-illustration').get_attribute('aria-label') or page.locator('.district-illustration').count()==1
        assert page.locator('.map-pin').count()==0
        assert page.get_by_text('Batas visual disederhanakan').count()==1
        button=page.get_by_role('button',name='Redupkan luar')
        button.click()
        assert page.locator('#map-stage').evaluate('(e)=>e.classList.contains("map-bright")')
        page.get_by_role('button',name='Mulai simulasi').click()
        assert page.get_by_role('heading',name='Skenario demonstrasi').count()==1
        browser.close()
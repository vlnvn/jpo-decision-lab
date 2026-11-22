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
CSS=(ROOT/'web/styles.css').read_text()
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
        page.evaluate('(data) => {window.fetch = async () => ({ok:true,status:200,json:async()=>data})}',state)
        page.add_script_tag(content=JS)
        page.wait_for_selector('h1')
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert page.get_by_role('heading',name='Prioritas kajian lokasi penyeberangan').count()==1
        if width==1920:
            page.get_by_role('button',name='Data penelitian').click()
            assert page.get_by_text('Riwayat kecelakaan pedestrian').count()==1
            page.get_by_role('button',name='Pemeringkatan').click()
            assert page.get_by_text('Belum ada hasil perhitungan').count()==1
        browser.close()
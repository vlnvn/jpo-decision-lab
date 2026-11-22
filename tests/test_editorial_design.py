"""Guard meaningful navigation/copy and component legibility from regressions.

Rendered fixtures use our own API data; no claim about live CDN tile performance.
"""
import json, os, re, shutil
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=re.sub(r'<script[^>]*>.*?</script>','',re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',(ROOT/'web/index.html').read_text()),flags=re.S)
CSS=(ROOT/'web/styles.css').read_text()+'\n'+(ROOT/'web/studio.css').read_text()
JS=(ROOT/'web/app.js').read_text()
GEO=json.loads((ROOT/'web/data/jatinangor.geojson').read_text())


def test_user_facing_copy_has_no_duplicate_brand_headers_or_false_institutional_credit():
    index=(ROOT/'web/index.html').read_text()
    assert 'Universitas Padjadjaran' not in index
    assert 'Studi Jatinangor <span' not in index
    assert '<footer>' not in index
    assert 'RISET MOBILITAS JATINANGOR' not in index
    assert 'JPO DECISION LAB</div>' not in JS
    assert 'INSPEKSI LOKASI' not in JS
    assert '01 / PETA KAWASAN' not in JS
    assert 'JPO DECISION LAB' not in JS
    assert 'Skenario pengujian aktif' in JS  # Integrity status remains visible.
    assert 'Simulasi' in JS


@pytest.mark.parametrize('width,height', [(320,750),(390,844),(573,900),(768,1000),(1920,1080)])
def test_six_navigation_stages_and_readable_metadata(client,width,height):
    state=client.get('/api/workspace').json()
    with sync_playwright() as p:
        exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':exe} if exe else {}))
        page=browser.new_page(viewport={'width':width,'height':height})
        page.set_content(HTML)
        page.add_style_tag(content=CSS)
        page.evaluate('([data,geo]) => {window.fetch=async url=>({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data})}', [state,GEO])
        page.add_script_tag(content=JS)
        page.locator('.candidate-surface').wait_for()
        assert page.locator('.sidebar nav button').count()==6
        for button in page.locator('.sidebar nav button').all():
            bb=button.bounding_box()
            assert bb and 0<=bb['x'] and bb['x']+bb['width']<=width+1
            if width<=800: assert bb['y']+bb['height'] <= height
        vals=page.evaluate('''() => Object.fromEntries(['.brand small','.map-title p','.map-footnote','.candidate-head p','.mode-banner div span','.nav-link','.strip-cell>span'].map(s=>[s,parseFloat(getComputedStyle(document.querySelector(s)).fontSize)]))''')
        assert all(v>=12 for v in vals.values()), (width,vals)
        assert page.locator('.workspace-context').inner_text().startswith('Jatinangor')
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.locator('.sidebar nav [data-screen="audit"]').click()
        assert page.locator('.sidebar nav [data-screen="audit"]').get_attribute('aria-current')=='page'
        assert 'Riwayat & sumber' in page.title()
        assert page.locator('.sidebar nav [data-screen="overview"]').get_attribute('aria-current') is None
        page.close()
        browser.close()

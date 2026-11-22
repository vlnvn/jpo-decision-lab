"""Browser-to-TestClient journey. Real FastAPI writes, no localhost/network dependency.

This is not a field validation and does not exercise external map tiles.
"""
import json
import os
import re
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=re.sub(r'<script[^>]*>.*?</script>','',re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',(ROOT/'web/index.html').read_text(encoding='utf-8')),flags=re.S)
CSS=(ROOT/'web/styles.css').read_text(encoding='utf-8')+(ROOT/'web/studio.css').read_text(encoding='utf-8')
JS=(ROOT/'web/app.js').read_text(encoding='utf-8')


def test_real_user_path_with_synthetic_data(client):
    def bridge(url,method='GET',payload=None):
        response=client.request(method,url,json=json.loads(payload) if payload else None)
        return {'ok':response.is_success,'status':response.status_code,'data':response.json()}

    with sync_playwright() as p:
        exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':exe} if exe else {}))
        page=browser.new_page(viewport={'width':1440,'height':900})
        page.expose_function('apiBridge',bridge)
        page.set_content(HTML)
        page.add_style_tag(content=CSS)
        page.evaluate('''() => { window.fetch = async (url, options={}) => {
            const v=await window.apiBridge(url, options.method||'GET', options.body||null);
            return {ok:v.ok,status:v.status,json:async()=>v.data};
        }; }''')
        page.add_script_tag(content=JS)
        page.locator('.district-illustration').wait_for()
        assert page.get_by_text('0 / 56').count()>0
        page.get_by_role('button',name='Panduan uji').click()
        assert page.get_by_role('heading',name='Mencoba DSS dari awal sampai selesai').count()==1
        page.get_by_role('button',name='Mulai dari skenario uji').click()
        page.get_by_role('button',name='Buat dataset sintetis').click()
        page.get_by_text('Skenario pengujian aktif').first.wait_for()
        assert client.get('/api/workspace').json()['readiness']['measured']==56
        page.get_by_role('button',name='Data penelitian').click()
        assert page.get_by_text('Riwayat kecelakaan pedestrian').count()==1
        page.get_by_role('button',name='Penilaian pakar').click()
        assert page.get_by_text('Lima kelompok kriteria').count()>0
        page.get_by_role('button',name='Pemeringkatan').click()
        page.get_by_role('button',name='Jalankan perhitungan').click()
        page.get_by_role('heading',name='Urutan prioritas kajian').wait_for()
        initial=client.get('/api/workspace').json()['runs'][0]
        assert initial['mode']=='synthetic' and not initial['stale']
        page.locator('[data-screen="observations"]').first.click()
        page.locator('#o-ped').fill('240')
        page.locator('#o-peak').fill('64')
        page.locator('#o-vehicles').fill('1100')
        page.locator('#o-source').fill('Skenario uji, bukan survei lapangan')
        page.locator('#o-period').fill('Sesi simulasi, 1 jam')
        page.get_by_role('button',name='Simpan observasi').click()
        page.get_by_role('button',name='Terapkan').click()
        assert client.get('/api/workspace').json()['runs'][0]['stale']
        page.get_by_role('button',name='Pemeringkatan').click()
        assert page.get_by_text('Hasil tidak mutakhir').count()>0
        assert page.locator('.stale-note').count()==1
        assert page.locator('.ranking-lead.is-stale').count()==1
        page.get_by_role('button',name='Jalankan perhitungan').click()
        assert page.locator('.stale-note').count()==0
        assert not client.get('/api/workspace').json()['runs'][0]['stale']
        page.get_by_role('button',name='Riwayat & sumber').click()
        assert page.get_by_text('Aktivitas penelitian').count()>0
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        browser.close()

"""Interface geometry, accessible labels, and component-level visual regressions.

These tests deliberately use API fixtures and offline rendering, so tile-CDN outages
cannot mask alignment defects. They do not certify live map connectivity or WCAG.
"""
from __future__ import annotations
import json, os, re, shutil
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=re.sub(r'<script[^>]*>.*?</script>', '', re.sub(r'<link[^>]+rel="stylesheet"[^>]*>', '', (ROOT/'web/index.html').read_text()), flags=re.S)
CSS=(ROOT/'web/styles.css').read_text()+'\n'+(ROOT/'web/studio.css').read_text()
JS=(ROOT/'web/app.js').read_text()
GEO=json.loads((ROOT/'web/data/jatinangor.geojson').read_text())


@pytest.fixture(scope='module')
def shared_browser():
    with sync_playwright() as p:
        path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':path} if path else {}))
        yield browser
        browser.close()


def browser_page(browser,width,height,state):
    page=browser.new_page(viewport={'width':width,'height':height})
    page.set_content(HTML)
    page.add_style_tag(content=CSS)
    page.evaluate('([data,geo]) => { window.fetch=async url=>({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data}); }', [state,GEO])
    page.add_script_tag(content=JS)
    page.get_by_role('heading',name='Kajian lokasi JPO Jatinangor').wait_for()
    return page


def open_candidate(page):
    page.locator('[data-action="edit-candidate"]').first.click()
    page.locator('#candidate-form').wait_for()


@pytest.mark.parametrize('width,height',[(320,750),(360,780),(390,844),(430,900),(573,900),(768,900),(1024,850),(1440,950),(1920,1080),(2560,1440)])
def test_candidate_modal_geometry_and_functionality(width,height,client,shared_browser):
    state=client.get('/api/workspace').json()
    page=browser_page(shared_browser,width,height,state)
    open_candidate(page)
    checks=page.locator('.verification-group input[type="checkbox"]')
    assert checks.count()==2
    for i in range(2):
        dims=checks.nth(i).bounding_box()
        label=page.locator('.verification-group label.check').nth(i)
        lab=label.bounding_box()
        assert 15<=dims['width']<=23 and 15<=dims['height']<=23
        assert 9 <= dims['x']-lab['x'] <= 20
        assert abs((dims['y']+dims['height']/2)-(lab['y']+lab['height']/2)) < 2
    page.locator('.verification-group label.check').first.click()
    assert checks.first.is_checked()
    page.locator('.verification-group label.check').first.click()
    assert not checks.first.is_checked()
    actions=page.locator('#candidate-form .candidate-form-actions button')
    assert actions.count()==3
    # Desktop: the three actions share one baseline. Narrow: the primary is a full-width second row.
    boxes=[actions.nth(i).bounding_box() for i in range(3)]
    assert abs(boxes[0]['y']-boxes[1]['y'])<2
    assert abs(boxes[0]['height']-boxes[1]['height'])<2
    if width>=601:
        assert abs(boxes[1]['y']-boxes[2]['y'])<2
    else:
        assert boxes[2]['y']>=boxes[0]['y']+boxes[0]['height']-1
        assert boxes[2]['width']>=min(230,page.locator('.modal').bounding_box()['width']-40)
    assert all(b['x']>=0 and b['x']+b['width']<=width+1 for b in boxes)
    assert page.locator('#candidate-form input[name="label"]').get_attribute('id')
    assert page.locator('#candidate-form label[for]').count()>=4
    # Even a short viewport must allow reaching the primary action inside the dialog.
    actions.nth(2).scroll_into_view_if_needed()
    assert actions.nth(2).is_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.close()


@pytest.mark.parametrize('width,height',[(320,750),(390,844),(573,900),(800,950),(1440,950),(1920,1080)])
def test_all_screens_have_valid_header_footer_and_no_document_overflow(width,height,client,shared_browser):
    state=client.get('/api/workspace').json()
    page=browser_page(shared_browser,width,height,state)
    assert page.locator('.breadcrumbs').inner_text().startswith('Studi Jatinangor')
    assert page.get_by_text('JPO Decision Lab · Prototipe penelitian',exact=True).count()==1
    for screen in ['overview','measurements','weights','ranking','observations','audit']:
        page.locator(f'.sidebar nav [data-screen="{screen}"]').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,screen)
        assert page.locator('.breadcrumbs').inner_text().strip().endswith(page.locator('#breadcrumb').inner_text())
        assert page.locator('#breadcrumb').inner_text().strip()
        # Footer must remain inside the content column, and both pieces must be readable.
        assert page.locator('.page footer span').count()==2
        boxes=page.locator('.page footer span').evaluate_all('(els)=>els.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,w:r.width,y:r.y,h:r.height}})')
        assert all(0<=r['x'] and r['x']+r['w']<=width+1 for r in boxes),(width,screen,boxes)
        assert not any('Universitas Padjadjaran' in e for e in page.locator('.page footer span').all_inner_texts())
        if screen=='measurements' and width<=600:
            assert page.locator('.data-table tbody tr').count()==14
            assert page.locator('.data-table tbody tr [data-action="edit-measurement"]').count()==14
            # No "Isi" action is hidden beyond the mobile viewport.
            for btn in page.locator('.data-table [data-action="edit-measurement"]').all():
                box=btn.bounding_box()
                assert box['x']>=0 and box['x']+box['width']<=width+1
        if screen=='audit':
            assert 'Waktu (WIB)' in page.locator('.table-small thead').inner_text()
            assert page.locator('.audit-details summary').count() == len(state.get('audit', []))
    page.close()


def test_observation_checkbox_and_other_modal_labels(client,shared_browser):
    state=client.get('/api/workspace').json()
    page=browser_page(shared_browser,1440,900,state)
    page.locator('.sidebar nav [data-screen="observations"]').click()
    box=page.locator('#observation-form input[type="checkbox"]')
    dims=box.bounding_box()
    assert 15<=dims['width']<=23 and 15<=dims['height']<=23
    assert page.locator('#observation-form label.check').inner_text().strip()
    page.locator('.sidebar nav [data-screen="measurements"]').click()
    page.locator('[data-action="edit-measurement"]').first.click()
    assert page.locator('#measurement-form label[for]').count()>=3
    page.locator('.modal [data-action="close-modal"]').click()
    page.locator('.sidebar nav [data-screen="weights"]').click()
    page.locator('[data-action="add-expert"]').click()
    assert page.locator('dialog label[for]').count()>=1
    page.close()

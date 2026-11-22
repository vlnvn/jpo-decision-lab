"""Render the exact HTML and CSS with the real local geography API payload.
Online tiles are unavailable in this renderer; previews show the labeled local vector fallback."""
from pathlib import Path
import re,json,os,shutil
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
from server.app import app
ROOT=Path(__file__).resolve().parents[1]
html=re.sub(r'<script[^>]*>.*?</script>','',re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',(ROOT/'web/index.html').read_text()),flags=re.S)
css=(ROOT/'web/styles.css').read_text()+'\n'+(ROOT/'web/studio.css').read_text()
js=(ROOT/'web/app.js').read_text()
folder=ROOT/'preview';folder.mkdir(exist_ok=True)
with TestClient(app) as c:
    data=c.get('/api/workspace').json();geo=c.get('/api/geography/jatinangor').json()
with sync_playwright() as p:
    executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':executable} if executable else {}))
    for width,height in [(1920,1080),(390,844)]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        page.set_content(html)
        page.add_style_tag(content=css)
        page.evaluate('([data,geo]) => {window.fetch = async url=>({ok:true,status:200,json:async()=>String(url).includes("geography/jatinangor")?geo:data})}',[data,geo])
        page.add_script_tag(content=js)
        page.locator('.district-illustration').wait_for()
        page.screenshot(path=str(folder/f'geo_{width}.png'),full_page=True)
        print(width,'refs',page.locator('.reference-fallback').count(),'boundary',page.locator('.district-illustration').count(),'scroll',page.evaluate('document.documentElement.scrollWidth'), 'viewport',width)
        page.close()
    browser.close()
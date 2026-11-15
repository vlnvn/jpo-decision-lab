"""Browser smoke + data/decision/IoT E2E with synthetic in-memory fixtures only."""
import asyncio, os
from pathlib import Path
from playwright.async_api import async_playwright
P=Path(__file__).resolve().parent.parent
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1400,'height':920})
  errors=[];alerts=[]
  page.on('pageerror',lambda err:errors.append(str(err)))
  page.on('dialog',lambda dlg:(alerts.append(dlg.message),asyncio.create_task(dlg.accept())))
  await page.set_content((P/'JPO_DSS_OFFLINE.html').read_text(),wait_until='load')
  assert (await page.locator('h1').inner_text()).startswith('Prioritas penyeberangan')
  await page.locator('#nav [data-screen="peringkat"]').click()
  assert await page.locator('#computeRanking').is_disabled(), 'Empty dataset must block ranking'
  await page.locator('#nav [data-screen="iot"]').click()
  assert await page.get_by_text('Belum ada baseline').is_visible()
  # UI form one observation, test source/gating after synthetic state population in memory.
  await page.evaluate('''() => {
    for(const can of candidates){
     store.confirmed[can.id]={checked:true,reference:'SYNTHETIC TEST CONFIRMATION - NOT FIELD SURVEY',lat:String(-6.92+0.002*Number(can.id[1])),lon:String(107.77+0.003*Number(can.id[1])),verifiedName:can.id==='A4'?'A4 SYNTHETIC VERIFIED NAME':''};
     crit.forEach((c,j)=>store.records[can.id+'|'+c[0]]={value:String(j===0?0:(j===9||j===10?1+Number(can.id[1])%5:10+Number(can.id[1])*2+j)),source:'SYNTHETIC TEST SOURCE / NOT REAL',checked:true});
    }
    let pairs={};for(const [key,n] of [['main',5],['local0',4],['local1',2],['local2',2],['local3',3],['local4',3]]){pairs[key]={};for(const [i,j] of E.pairs(n))pairs[key][i+'-'+j]=1}
    store.experts=[{name:'SYNTHETIC_EXPERT',pairs}];store.approvedMethod=true;
    store.weights=E.buildWeights(store.experts,[4,2,2,3,3]);
    render();
  }''')
  await page.locator('#nav [data-screen="peringkat"]').click()
  assert await page.locator('#computeRanking').is_enabled()
  await page.locator('#computeRanking').click()
  assert 'Peringkat awal' in await page.locator('body').inner_text()
  assert await page.locator('table').count()>=2
  await page.locator('#nav [data-screen="iot"]').click()
  await page.locator('#iotCandidate').select_option('A1')
  await page.locator('#iotStart').fill('2026-11-12T08:00')
  await page.locator('#iotEnd').fill('2026-11-12T09:00')
  await page.locator('#iotCars').fill('45')
  await page.locator('#iotPeds').fill('22')
  await page.locator('#iotPeak').fill('8')
  await page.locator('#iotSource').fill('SYNTHETIC SESSION')
  await page.locator('#iotReviewer').fill('TEST REVIEWER')
  await page.locator('#iotQuality').check()
  await page.locator('#submitIot').click()
  assert 'Perubahan setelah observasi' in await page.locator('body').inner_text()
  assert 'Validasi parsial' in await page.locator('body').inner_text()
  await page.locator('#nav [data-screen="audit"]').click()
  assert 'TOPSIS dihitung' in await page.locator('body').inner_text()
  assert len(errors)==0,errors
  assert len(alerts)==0,alerts
  print('Browser E2E PASS: no fake initial ranking; complete synthetic inputs -> FAHP -> TOPSIS -> IoT rerank -> audit.')
  await page.screenshot(path=str(P/'screenshot_audit.png'),full_page=True)
  await browser.close()
asyncio.run(main())
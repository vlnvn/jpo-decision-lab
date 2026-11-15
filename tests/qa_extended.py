"""Independent browser QA; synthetic fixtures ONLY, never included in the actual app state."""
import asyncio, os, json
from pathlib import Path
from playwright.async_api import async_playwright
P=Path(__file__).resolve().parent.parent
HTML=(P/'JPO_DSS_OFFLINE.html').read_text(encoding='utf-8')
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  errors=[]
  for width in [320,390,768,1440,1920,2560]:
   page=await browser.new_page(viewport={'width':width,'height':900},accept_downloads=True)
   page.on('pageerror',lambda e:errors.append(str(e)))
   dialogs=[]
   page.on('dialog',lambda dlg:(dialogs.append(dlg.message),asyncio.create_task(dlg.accept())))
   await page.set_content(HTML,wait_until='load')
   for sid in ['ringkasan','kandidat','kriteria','bobot','peringkat','iot','audit']:
    await page.locator(f'#nav [data-screen="{sid}"]').click()
    actual=await page.evaluate('document.documentElement.scrollWidth')
    assert actual<=width+2,(width,sid,actual)
   await page.close()
  print('Responsive QA PASS: 7 screens at 320, 390, 768, 1440, 1920 and 2560 px; no document overflow')
  page=await browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  dialogs=[]
  page.on('dialog',lambda dlg:(dialogs.append(dlg.message),asyncio.create_task(dlg.accept())))
  await page.set_content(HTML,wait_until='load')
  assert '0 / 56' in await page.locator('#railProgress').inner_text()
  await page.locator('[data-hm="A2"]').first.click()
  assert 'Rekam observasi A2' in await page.locator('body').inner_text()
  await page.locator('[data-screen="kandidat"]').click()
  # Can verify a candidate based on an evidence record without inventing coordinates.
  await page.locator('[data-location-source="A1"]').fill('VALIDASI UJI SINTETIS')
  await page.locator('[data-location-source="A1"]').dispatch_event('change')
  await page.locator('[data-location-check="A1"]').check()
  assert await page.locator('[data-location-check="A1"]').is_checked()
  # A4 must have documented resolution of conflicting names.
  await page.locator('[data-location-source="A4"]').fill('VALIDASI UJI SINTETIS')
  await page.locator('[data-location-source="A4"]').dispatch_event('change')
  await page.locator('[data-location-check="A4"]').click(force=True)
  assert any('A4' in x for x in dialogs),dialogs
  # Test fixture for complete data (not field observations).
  await page.evaluate('''() => {
    for(const can of candidates){
     store.confirmed[can.id]={checked:true,reference:'SYNTHETIC TEST',verifiedName:can.id==='A4'?'A4 LOCAL RESOLUTION':''};
     crit.forEach((c,j)=>store.records[can.id+'|'+c[0]]={value:String(j===0?0:(j===9||j===10?1+Number(can.id[1])%5:10+Number(can.id[1])*2+j)),source:'SYNTHETIC TEST / 2026-11-12',checked:true});
    }
    let pairs={};for(const [key,n] of [['main',5],['local0',4],['local1',2],['local2',2],['local3',3],['local4',3]]){pairs[key]={};for(const [i,j] of E.pairs(n))pairs[key][i+'-'+j]=1}
    store.experts=[{name:'SYNTHETIC_EXPERT',pairs}];store.approvedMethod=true;
    render();
  }''')
  await page.locator('[data-screen="bobot"]').click()
  await page.locator('#computeWeights').click()
  assert 'CR' in await page.locator('body').inner_text()
  await page.locator('[data-screen="peringkat"]').click()
  await page.locator('#computeRanking').click()
  assert 'Peringkat awal' in await page.locator('body').inner_text()
  async with page.expect_download() as info:
   await page.locator('#exportRankingCSV').click()
  csv=Path(await (await info.value).path()).read_text(encoding='utf-8-sig')
  assert 'PRIORITAS_KAJIAN' in csv and 'A1' in csv and 'C_star' in csv
  await page.locator('[data-screen="iot"]').click()
  assert await page.locator('#importIoTAggregate').count()==1
  payload={'schema':'jpo-iot-aggregate-1','observation':{'candidate':'A1','start':'2026-11-12T08:00','end':'2026-11-12T09:00','cars':45,'peds':22,'peak':8,'source':'SYNTHETIC EDGE SESSION','speed':None,'speedCalibrated':False}}
  await page.locator('#importIoTAggregate').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(payload).encode('utf8')})
  assert await page.locator('#iotCars').input_value()=='45'
  assert not await page.locator('#iotQuality').is_checked()
  await page.locator('#iotReviewer').fill('QA reviewer')
  await page.locator('#iotQuality').check()
  await page.locator('#submitIot').click()
  assert 'Validasi parsial' in await page.locator('body').inner_text()
  await page.locator('[data-screen="audit"]').click()
  async with page.expect_download() as info:
   await page.locator('#exportJSON').click()
  state=json.loads(Path(await (await info.value).path()).read_text(encoding='utf8'))
  assert state['schema']=='jpo-dss-prototype-1'
  assert len(state['data']['observations'])==1
  # Import must not trust serialized computed results.
  await page.locator('#importJSON').set_input_files({'name':'state.json','mimeType':'application/json','buffer':json.dumps(state).encode('utf8')})
  assert await page.evaluate('store.baseline===null && store.weights===null && store.observations.length===0')
  assert not errors,errors
  print('Behavior QA PASS: clicked coverage cell, no-coordinate candidate, A4 ambiguity, FAHP, TOPSIS CSV, IoT JSON review, JSON export/import safety')
  await browser.close()
asyncio.run(main())
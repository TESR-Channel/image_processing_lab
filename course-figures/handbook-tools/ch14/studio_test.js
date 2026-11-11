// Learner path in ROI Studio v1.9.0: add 2 models, load 30 photos, new "two AIs" ROI, step through.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const D = '/home/claude/ch14/data';
const OUT = process.argv[2] || '/home/claude/ch14/shots';
const LANG = process.argv[3] || 'th';
const FIN = process.argv[4] || 'terminal_finder.onnx', CHK = process.argv[5] || 'terminal_checker.onnx';
const PHOTOS = process.argv[6] || 'samples_terminal', COUNT = process.argv[7] || '8';
const PROJ = process.argv[8] || 'terminal_qc';
fs.mkdirSync(OUT, {recursive: true});
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: {width: 1500, height: 900}, deviceScaleFactor: +(process.env.DSF || 1), acceptDownloads: true});
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const ORT = '/home/claude/ch14/npm/node_modules/onnxruntime-web/dist/';
  await page.route('**/*', route => {
    const u = route.request().url();
    const m = u.match(/onnxruntime-web@[^/]+\/dist\/([^?#]+)/);
    if (m && fs.existsSync(ORT + m[1])) {
      const type = m[1].endsWith('.wasm') ? 'application/wasm' : 'text/javascript';
      return route.fulfill({status: 200, contentType: type, body: fs.readFileSync(ORT + m[1])});
    }
    if (/^https?:\/\/(127\.0\.0\.1|localhost)/.test(u)) return route.continue();
    return route.abort();
  });
  await page.goto('http://127.0.0.1:8777/index.html');
  await page.click(LANG === 'th' ? '#langTh' : '#langEn');
  // ---- add the two models
  for (const f of [FIN, CHK]) {
    await page.click('#btnAddModel');
    await page.setInputFiles('#mdFile', path.join(D, 'models', f));
    await page.waitForFunction(() => document.querySelector('#mdName').value !== '');
    if (f === CHK) await page.screenshot({path: OUT + '/s1_addmodel.png'});
    await page.click('#mdSave');
    await page.waitForTimeout(2500);
  }
  // ---- 30 photos
  const photos = fs.readdirSync(D + '/' + PHOTOS).filter(f => f.endsWith('.jpg')).map(f => D + '/' + PHOTOS + '/' + f);
  await page.setInputFiles('#fileImage', photos);
  await page.waitForTimeout(1500);
  // ---- new ROI: two AIs
  await page.selectOption('#newTask', 'parts_check');
  const box = await page.locator('#view').boundingBox();
  await page.mouse.move(box.x + box.width * 0.35, box.y + box.height * 0.2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.6, box.y + box.height * 0.5, {steps: 8});
  await page.mouse.up();
  await page.waitForTimeout(500);
  // pick models + classes (panel selects in order: AI#1 model, class, AI#2 model, class, rule)
  const sels = page.locator('#taskParams select');
  const ids = await page.evaluate(() => models.map(m => [m.id, m.name]));
  await sels.nth(0).selectOption(ids.find(x => x[1] === FIN.replace('.onnx',''))[0]);
  await page.waitForTimeout(300);
  await page.locator('#taskParams select').nth(2).selectOption(ids.find(x => x[1] === CHK.replace('.onnx',''))[0]);
  await page.waitForTimeout(300);
  const countInput = page.locator('#taskParams input[type=number]').first();
  await countInput.fill(COUNT); await countInput.dispatchEvent('input');
  const nums = page.locator('#taskParams input[type=number]');
  await nums.nth(1).fill('0.5'); await nums.nth(1).dispatchEvent('input');
  await nums.nth(2).fill('0.4'); await nums.nth(2).dispatchEvent('input');
  await page.fill('#projName', PROJ); await page.fill('#pName', PROJ); await page.dispatchEvent('#pName', 'input'); await page.dispatchEvent('#pName', 'change');
  await page.fill('#pKey', PROJ); await page.dispatchEvent('#pKey', 'input'); await page.dispatchEvent('#pKey', 'change');
  await page.locator('#taskParams button').first().click();   // use the whole picture
  await page.waitForTimeout(300);
  await page.click('#btnTestRoi');
  await page.waitForFunction(() => { const r = Object.values(live.results)[0]; return r && r.objects; }, null, {timeout: 60000});
  await page.waitForTimeout(500);
  await page.screenshot({path: OUT + '/s2_first.png'});
  // ---- step through all 30 with the arrow key
  const rows = [];
  for (let i = 0; i < photos.length; i++) {
    if (i > 0) {
      await page.locator('#btnPicNext').click();
    }
    await page.waitForFunction(() => { const r = Object.values(live.results)[0]; return !pics.pending && r && r.objects && !live.busy; }, null, {timeout: 60000});
    const r = await page.evaluate(() => [document.querySelector('#picInfo').textContent, Object.values(live.results)[0].value]);
    rows.push(r);
    if (i === 18 || (PHOTOS === 'samples' && i === 2)) await page.screenshot({path: OUT + '/s3_ng.png'});
    if (i === 19 || (PHOTOS === 'samples' && i === 6)) await page.screenshot({path: OUT + '/s4_ok.png'});
  }
  rows.forEach(r => console.log(r[0], '=>', r[1]));
  await page.setViewportSize({width: 1500, height: 1500});
  await page.waitForTimeout(800);
  await page.evaluate(() => { const el = document.querySelector('#roiPanel'); if (el) el.scrollIntoView(); });
  await page.waitForTimeout(500);
  await page.screenshot({path: OUT + '/s5_tall.png'});
  // ---- export the project (runner + config + both models)
  const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#btnPy')]);
  const zipPath = OUT + '/' + dl.suggestedFilename();
  await dl.saveAs(zipPath);
  console.log('exported', zipPath);
  console.log('errors', JSON.stringify(errs));
  await browser.close();
})();

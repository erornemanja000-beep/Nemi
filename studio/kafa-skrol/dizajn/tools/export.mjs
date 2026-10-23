// Izvoz etikete: node export.mjs <outDir> [--guides]
import { chromium } from '/home/user/Nemi/KafaSkrol/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { setTimeout as wait } from 'node:timers/promises';

const out = process.argv[2];
const guides = process.argv.includes('--guides');
const PORT = 8765 + Math.floor(Math.random() * 500);
const srv = spawn('python3', ['-I', '-m', 'http.server', String(PORT), '--bind', '127.0.0.1', '--directory', '/home/user/Nemi'], { stdio: 'ignore' });
await wait(800);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: { width: 2048, height: 3072 }, deviceScaleFactor: 1 });
const external = [];
await ctx.route('**/*', r => {
  const u = new URL(r.request().url());
  if (u.hostname !== '127.0.0.1') { external.push(u.href); return r.abort(); }
  return r.continue();
});
const page = await ctx.newPage();
const errors = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
page.on('requestfailed', r => errors.push('FAILED ' + r.url()));
for (const v of ['origin', 'flavor', 'roast']) {
  const url = `http://127.0.0.1:${PORT}/studio/kafa-skrol/dizajn/etiketa.html?v=${v}${guides ? '&guides=1' : ''}`;
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.getElementById('label').dataset.ready);
  const info = await page.evaluate(() => {
    const L = document.getElementById('label');
    const r = id => { const b = document.getElementById(id).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; };
    // provera ose wdth: širina GRIND na 88 i 100
    const t = document.createElement('span');
    t.textContent = 'GRIND'; t.style.cssText = 'position:absolute;font:800 200px Archivo;white-space:nowrap';
    document.body.appendChild(t);
    t.style.fontVariationSettings = '"wdth" 88'; const w88 = t.getBoundingClientRect().width;
    t.style.fontVariationSettings = '"wdth" 100'; const w100 = t.getBoundingClientRect().width;
    t.remove();
    return { ready: L.dataset.ready, brandFs: getComputedStyle(document.getElementById('brand')).fontSize,
      subFs: getComputedStyle(document.getElementById('sub')).fontSize,
      brand: r('brand'), sub: r('sub'), qty: r('qty'), demo: r('demo'), wdthRatio: (w88 / w100).toFixed(3),
      fonts: [...document.fonts].map(f => f.family + ':' + f.status) };
  });
  console.log(v, JSON.stringify(info));
  if (info.ready !== 'ok') { console.error('FONT ERROR', v); process.exitCode = 1; }
  await page.screenshot({ path: `${out}/etiketa-${v}${guides ? '-guides' : ''}.png`, omitBackground: true, clip: { x: 0, y: 0, width: 2048, height: 3072 } });
}
console.log('external requests blocked:', external.length, external.slice(0, 5));
console.log('console errors/warnings:', errors.length, errors.slice(0, 5));
await browser.close();
srv.kill();

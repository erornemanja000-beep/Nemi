// Snima reklama.html kadar po kadar (render(t)) kao JPEG za ffmpeg.
// node scripts/wach_reklama/render.js <izlazni_folder> [fps] [radnika] [kadrovi: "t1,t2,..." za proveru]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const out = process.argv[2];
const FPS = parseInt(process.argv[3] || '30');
const WORKERS = parseInt(process.argv[4] || '6');
const only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const times = only || [...Array(12 * FPS).keys()].map((i) => i / FPS);
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, 'reklama.html') + '?t=0';
  await Promise.all([...Array(WORKERS).keys()].map(async (w) => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await page.goto(url);
    await page.evaluate(() => document.fonts.ready);
    for (let i = w; i < times.length; i += WORKERS) {
      await page.evaluate((t) => render(t), times[i]);
      const name = only ? `t_${times[i].toFixed(2)}` : `f${String(i).padStart(4, '0')}`;
      await page.screenshot({ path: path.join(out, `${name}.jpg`), type: 'jpeg', quality: 92 });
    }
  }));
  await browser.close();
})();

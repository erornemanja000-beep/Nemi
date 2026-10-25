// Snima promo.html kadar po kadar (render(t)) i pravi PNG kadrove za ffmpeg.
// node scripts/nemi_promo/render.js <izlazni_folder> [fps] [radnika]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const out = process.argv[2];
const FPS = parseInt(process.argv[3] || '30');
const WORKERS = parseInt(process.argv[4] || '6');
const N = 10 * FPS;
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, 'promo.html') + '?t=0';
  await Promise.all([...Array(WORKERS).keys()].map(async (w) => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto(url);
    await page.evaluate(() => document.fonts.ready);
    for (let i = w; i < N; i += WORKERS) {
      await page.evaluate((t) => render(t), i / FPS);
      await page.screenshot({ path: path.join(out, `f${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 95 });
    }
  }));
  await browser.close();
})();

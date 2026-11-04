// HTML bojanke -> PDF (A4) preko postojećeg Chromium-a. Upotreba: node pdf.js ulaz.html izlaz.pdf
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [ulaz, izlaz] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(ulaz), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: izlaz, format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
})();

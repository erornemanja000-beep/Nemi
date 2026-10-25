// Snima sajt KREISEL kadar po kadar (1440 × 900) za ekran laptopa u Blender-u.
// Pokretanje (iz motion/kreisel, dok radi server na :8766 iz istog foldera):
//   node snimi_sajt.mjs
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ovde = path.dirname(fileURLToPath(import.meta.url));
// playwright iz tools/playwright-cli (zaključana verzija koju je pregledao `bezbednost`)
const require = createRequire(path.join(ovde, "../../tools/playwright-cli/package.json"));
const { chromium } = require("playwright");

const KADROVA = 255;
const FPS = 30;
const izlaz = path.join(ovde, "render", "sajt");
mkdirSync(izlaz, { recursive: true });

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:8766/site/index.html", { waitUntil: "load" });
await page.evaluate(() => window.kreiselSpreman);
for (let f = 1; f <= KADROVA; f++) {
  const t = (f - 1) / FPS;
  await page.evaluate((t) => window.kreiselPostavi(t), t);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({ path: path.join(izlaz, `${String(f).padStart(4, "0")}.png`) });
  if (f % 50 === 0) console.log("kadar", f);
}
await browser.close();
console.log("gotovo:", KADROVA);

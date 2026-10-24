// Posle `npm run build:gh` (base /Nemi/kafaskrol/, izlaz dist-gh/), bez paketa:
// - 404.html = kopija index.html. GitHub Pages nema SPA preusmerenje: za adresu koje nema (/p/guji,
//   /impressum …) daje 404.html (sa statusom 404), a ruter iz njega bira stranicu. Putanje u njemu su
//   apsolutne (/Nemi/kafaskrol/assets/…), pa radi sa bilo koje dubine. GitHub Pages čita 404.html samo iz
//   korena objavljenog sajta (README, „Objava"), ne iz podfoldera.
// - .nojekyll: GitHub Pages ne pušta fajlove kroz Jekyll.
// Upotreba: node scripts/after-gh.mjs [folder]   (podrazumevano dist-gh)
import { copyFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const dir = process.argv[2] ?? 'dist-gh'
const index = join(dir, 'index.html')
if (!existsSync(index)) throw new Error(`${index} ne postoji: prvo vite build`)

// build mora da ima base iz build:gh (inače bi stranica tražila /assets/… u korenu domena)
const html = readFileSync(index, 'utf8')
if (!/<script type="module" crossorigin src="\/[^"]+\/assets\//.test(html)) throw new Error(`${index}: bundle nije pod base-om (KAFA_BASE?)`)

copyFileSync(index, join(dir, '404.html'))
writeFileSync(join(dir, '.nojekyll'), '')
console.log(`${dir}: 404.html i .nojekyll`)
